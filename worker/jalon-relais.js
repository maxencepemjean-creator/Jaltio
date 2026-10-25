// Relais Jaltio (Cloudflare Worker)
//
// 1) Relais Claude : garde la clé Anthropic côté serveur ; le navigateur n'envoie qu'un code d'accès
//    (code testeur du secret CODES, ou code d'abonné créé automatiquement après un paiement Stripe).
// 2) Synchronisation entre appareils (routes /sync/*) : le serveur ne reçoit qu'un bloc CHIFFRÉ dans le
//    navigateur (AES-GCM, clé dérivée du mot de passe par PBKDF2) et un identifiant haché. Il ne voit jamais
//    l'e-mail, le mot de passe ni le contenu des CV.
//
// À créer dans Cloudflare :
//   Secrets (Settings > Variables and Secrets, type « Secret ») :
//     ANTHROPIC_KEY  = la clé sk-ant-... dédiée à Jaltio
//     CODES          = codes testeurs séparés par des virgules, ex. « maman-7k2, julien-p9x »
//     STRIPE_KEY            = clé RESTREINTE Stripe (rk_test_… puis rk_live_…), droit « Checkout Sessions : lecture » uniquement
//     STRIPE_WEBHOOK_SECRET = secret de signature du webhook Stripe (whsec_…)
//     STRIPE_KEY doit avoir les droits : Checkout Sessions (lecture), Customers (lecture), Subscriptions (écriture)
//     MAIL_SECRET           = secret partagé avec le workflow n8n des e-mails (en-tête x-jaltio-secret)
//     MAILS_WEBHOOK         = (facultatif) adresse du workflow n8n « [JLT] 05 - E-mails clients » ; par défaut MAILS_DEFAUT ci-dessous
//     (MAIL_WEBHOOK, ancien workflow « [JLT] 03 », n'est plus utilisé)
//   Base D1 liée au Worker (Settings > Bindings > Add > D1 database), nom de variable : DB
//   Tables : voir worker/schema.sql (à coller dans l'onglet Console de la base D1)
//   Stripe : webhook vers https://jalon-relais.jalon-emploi.workers.dev/stripe/webhook
//            (événements checkout.session.completed, customer.subscription.updated, customer.subscription.deleted)
//            Lien de paiement : redirection après paiement vers https://jaltio.fr/?paye={CHECKOUT_SESSION_ID}
//   Déclencheur planifié (Settings > Triggers > Cron) : « 0 3 * * * » (chaque nuit : avertissements et suppressions à 6 mois)
//   Base D1 : exécuter une fois worker/migration-2026-10-25.sql (colonnes fin, averti, accepte, code_h)

const ORIGINES = ["https://maxencepemjean-creator.github.io", "https://jaltio.fr", "https://www.jaltio.fr"];
const MODELES = ["claude-sonnet-5-5"];
const MAX_TOKENS = 16000;

const MAX_BODY = 1900000;              // octets : requête de synchro complète (D1 limite une ligne à 2 Mo)
const CONSERVATION_JOURS = 400;        // comptes sans abonnement (codes testeurs) : supprimés après ce délai sans aucune connexion
const APRES_FIN_JOURS = 183;           // comptes d'abonnés : supprimés 6 mois après la fin de l'abonnement
const PREAVIS_JOURS = 7;               // e-mail d'avertissement envoyé 7 jours avant la suppression
const MAILS_DEFAUT = "https://n8n.srv1136752.hstgr.cloud/webhook/jaltio-mails";
const LIMITES = {                      // [nombre max, fenêtre en secondes]
  ip:       [90, 60],                  // toutes routes /sync, par adresse (hachée)
  compte:   [30, 60],                  // toutes routes /sync, par identifiant
  echecs:   [8, 900],                  // mots de passe faux, par identifiant
  creation: [5, 3600],                 // créations de compte, par adresse (hachée)
  code_h:   [40, 3600],                // appels Claude par code d'accès et par heure
  code_j:   [150, 86400],              // appels Claude par code d'accès et par jour
  paiement: [20, 3600],                // récupérations de code après paiement, par adresse (hachée)
  compte_abo: [20, 3600],              // consultations et résiliations d'abonnement, par adresse (hachée)
};

// Quotas mensuels par offre (mois calendaire). Les codes testeurs (secret CODES) n'ont pas de quota mensuel.
// « generations » = création ou régénération d'un CV et d'une lettre (requêtes à plus de SEUIL_GENERATION jetons max) ;
// « autres » = petits appels (lecture d'offre, coach, analyse du parcours…) : garde-fou de coût.
const QUOTAS = {
  essentiel: { generations: 50, autres: 300 },
};
const SEUIL_GENERATION = 8000;
const OFFRE_PAR_DEFAUT = "essentiel";  // offre attribuée à un paiement (une seule offre en vente pour l'instant)
// Accès offert (proches, testeurs) : abonnement Stripe pris avec un code promo du coupon COUPON_OFFERT (100 %, à vie).
// L'offre « offert » n'a aucun quota mensuel et aura accès à toutes les fonctions, y compris celles de Pro.
const COUPON_OFFERT = "JALTIO_OFFERT";

const RE_ID = /^[0-9a-f]{64}$/;
const RE_B64 = /^[A-Za-z0-9+/]+={0,2}$/;

function cors(origin) {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, x-jalon-code",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function reponse(obj, status, origin) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json", "cache-control": "no-store", ...cors(origin) },
  });
}
const erreur = (status, message, origin, extra) => reponse({ error: { message }, ...(extra || {}) }, status, origin);

async function sha256hex(texte) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(texte));
  return [...new Uint8Array(buf)].map(x => x.toString(16).padStart(2, "0")).join("");
}
function egal(a, b) {                  // comparaison à temps constant
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}
const maintenant = () => Date.now();
const moisCourant = () => new Date().toISOString().slice(0, 7);   // « 2026-10 »

async function hmacHex(secret, texte) {
  const cle = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", cle, new TextEncoder().encode(texte));
  return [...new Uint8Array(sig)].map(x => x.toString(16).padStart(2, "0")).join("");
}

/* ---------- Codes d'accès : testeurs (secret CODES) et abonnés (table abonnes) ---------- */
function nouveauCode() {               // ex. « jal-7k2m-p9xq » (sans 0/o/1/l pour éviter les confusions)
  const alpha = "23456789abcdefghijkmnpqrstuvwxyz", r = crypto.getRandomValues(new Uint8Array(8));
  const c = [...r].map(x => alpha[x % alpha.length]).join("");
  return "jal-" + c.slice(0, 4) + "-" + c.slice(4);
}
async function verifierCode(env, code) {      // renvoie { offre } si le code est valable, sinon null
  if (!code) return null;
  const codes = String(env.CODES || "").split(",").map(c => c.trim()).filter(Boolean);
  if (codes.includes(code)) return { offre: "testeur" };
  if (!env.DB || !/^jal-[a-z0-9]{4}-[a-z0-9]{4}$/.test(code)) return null;
  const row = await env.DB.prepare("SELECT offre, actif FROM abonnes WHERE code = ?1").bind(code).first();
  return row && row.actif === 1 ? { offre: row.offre } : null;
}

// Empreinte d'un code d'abonné (table abonnes, actif ou non) ; null pour un code testeur ou inconnu
async function codeAbonneH(env, code) {
  if (!env.DB || !/^jal-[a-z0-9]{4}-[a-z0-9]{4}$/.test(code || "")) return null;
  const row = await env.DB.prepare("SELECT code FROM abonnes WHERE code = ?1").bind(code).first();
  return row ? await sha256hex("code|" + code) : null;
}

/* ---------- Limites de requêtes (compteurs atomiques dans D1) ---------- */
async function compter(env, cle, fenetre) {
  const s = Math.floor(Date.now() / 1000), w = Math.floor(s / fenetre);
  const row = await env.DB.prepare(
    "INSERT INTO rate (k, n, exp) VALUES (?1, 1, ?2) ON CONFLICT(k) DO UPDATE SET n = n + 1 RETURNING n"
  ).bind(cle + ":" + w, (w + 1) * fenetre + 60).first();
  return row ? row.n : 1;
}
async function lire(env, cle, fenetre) {
  const w = Math.floor(Math.floor(Date.now() / 1000) / fenetre);
  const row = await env.DB.prepare("SELECT n FROM rate WHERE k = ?1").bind(cle + ":" + w).first();
  return row ? row.n : 0;
}
async function sous_limite(env, cle, [max, fenetre]) { return (await compter(env, cle, fenetre)) <= max; }

/* ---------- Synchronisation ---------- */
async function verifierAuth(env, id, auth, row) {
  const [max, fenetre] = LIMITES.echecs;
  if ((await lire(env, "echec:" + id, fenetre)) >= max) return "bloque";
  if (!RE_ID.test(auth || "") || !egal(await sha256hex(auth), row.auth)) {
    await compter(env, "echec:" + id, fenetre);
    return "refuse";
  }
  return "ok";
}

async function synchro(request, env, origin, chemin) {
  if (request.method !== "POST") return erreur(405, "Méthode non autorisée.", origin);
  if (!env.DB) return erreur(503, "La synchronisation n'est pas encore configurée côté serveur.", origin);

  const declare = Number(request.headers.get("content-length") || 0);
  if (declare > MAX_BODY) return erreur(413, "Données trop volumineuses.", origin);
  const texte = await request.text();
  if (texte.length > MAX_BODY) return erreur(413, "Données trop volumineuses.", origin);
  let b; try { b = JSON.parse(texte); } catch (e) { return erreur(400, "Requête illisible.", origin); }
  if (!b || !RE_ID.test(b.id || "")) return erreur(400, "Identifiant invalide.", origin);

  const ip = await sha256hex("ip|" + (request.headers.get("CF-Connecting-IP") || "?"));
  if (!(await sous_limite(env, "ip:" + ip, LIMITES.ip)) || !(await sous_limite(env, "id:" + b.id, LIMITES.compte)))
    return erreur(429, "Trop de demandes. Patientez une minute.", origin);

  // Nettoyage opportuniste des compteurs périmés
  if (Math.random() < 0.02) await env.DB.prepare("DELETE FROM rate WHERE exp < ?1").bind(Math.floor(Date.now() / 1000)).run();

  const row = await env.DB.prepare("SELECT * FROM sync WHERE id = ?1").bind(b.id).first();

  if (chemin === "/sync/meta") {
    return reponse(row ? { exists: true, salt: row.salt, version: row.version, updated: row.updated } : { exists: false }, 200, origin);
  }

  if (chemin === "/sync/get") {
    if (!row) return erreur(404, "Aucune donnée en ligne pour cet identifiant.", origin);
    const a = await verifierAuth(env, b.id, b.auth, row);
    if (a === "bloque") return erreur(429, "Trop d'essais. Réessayez dans 15 minutes.", origin);
    if (a !== "ok") return erreur(401, "Identifiant ou mot de passe incorrect.", origin);
    await env.DB.prepare("UPDATE sync SET accessed = ?1 WHERE id = ?2").bind(maintenant(), b.id).run();
    return reponse({ salt: row.salt, iv: row.iv, ct: row.ct, version: row.version, updated: row.updated }, 200, origin);
  }

  if (chemin === "/sync/put") {
    if (!RE_B64.test(b.iv || "") || b.iv.length !== 16) return erreur(400, "Bloc invalide.", origin);
    if (!RE_B64.test(b.ct || "") || b.ct.length > MAX_BODY - 2000) return erreur(413, "Données trop volumineuses.", origin);
    const baseVersion = Number.isInteger(b.baseVersion) ? b.baseVersion : -1;

    if (!row) {                                              // création du compte
      const code = (request.headers.get("x-jalon-code") || "").trim();
      if (!(await verifierCode(env, code))) return erreur(403, "Un code d'accès valide est nécessaire pour créer la synchronisation.", origin);
      if (!RE_ID.test(b.auth || "")) return erreur(400, "Authentification invalide.", origin);
      if (!RE_B64.test(b.salt || "") || b.salt.length !== 24) return erreur(400, "Sel invalide.", origin);
      if (!(await sous_limite(env, "new:" + ip, LIMITES.creation))) return erreur(429, "Trop de créations de compte. Réessayez plus tard.", origin);
      const t = maintenant();
      const r = await env.DB.prepare(
        "INSERT INTO sync (id, auth, salt, iv, ct, version, updated, accessed, size, code_h) VALUES (?1, ?2, ?3, ?4, ?5, 1, ?6, ?6, ?7, ?8) ON CONFLICT(id) DO NOTHING"
      ).bind(b.id, await sha256hex(b.auth), b.salt, b.iv, b.ct, t, b.ct.length, await codeAbonneH(env, code)).run();
      if (!r.meta || r.meta.changes !== 1) return erreur(409, "Ce compte vient d'être créé ailleurs.", origin, { conflict: true });
      return reponse({ version: 1, updated: t }, 200, origin);
    }

    const a = await verifierAuth(env, b.id, b.auth, row);
    if (a === "bloque") return erreur(429, "Trop d'essais. Réessayez dans 15 minutes.", origin);
    if (a !== "ok") return erreur(401, "Identifiant ou mot de passe incorrect.", origin);
    if (baseVersion !== row.version) return erreur(409, "Une version plus récente existe en ligne.", origin, { conflict: true, version: row.version, updated: row.updated });
    const t = maintenant();
    const r = await env.DB.prepare(
      "UPDATE sync SET iv = ?1, ct = ?2, version = version + 1, updated = ?3, accessed = ?3, size = ?4 WHERE id = ?5 AND version = ?6"
    ).bind(b.iv, b.ct, t, b.ct.length, b.id, row.version).run();
    if (!r.meta || r.meta.changes !== 1) return erreur(409, "Une version plus récente existe en ligne.", origin, { conflict: true });
    // Lien entre le compte et l'abonnement (pour la suppression 6 mois après la fin) : posé dès que le site envoie un code d'abonné
    const ch = await codeAbonneH(env, (request.headers.get("x-jalon-code") || "").trim());
    if (ch && row.code_h !== ch) await env.DB.prepare("UPDATE sync SET code_h = ?1 WHERE id = ?2").bind(ch, b.id).run();
    return reponse({ version: row.version + 1, updated: t }, 200, origin);
  }

  if (chemin === "/sync/delete") {
    if (!row) return reponse({ deleted: false }, 200, origin);
    const a = await verifierAuth(env, b.id, b.auth, row);
    if (a === "bloque") return erreur(429, "Trop d'essais. Réessayez dans 15 minutes.", origin);
    if (a !== "ok") return erreur(401, "Identifiant ou mot de passe incorrect.", origin);
    await env.DB.prepare("DELETE FROM sync WHERE id = ?1").bind(b.id).run();
    return reponse({ deleted: true }, 200, origin);
  }

  return erreur(404, "Route inconnue.", origin);
}

/* ---------- Relais Claude ---------- */
async function relais(request, env, origin) {
  if (request.method !== "POST") return erreur(405, "Méthode non autorisée.", origin);

  const code = (request.headers.get("x-jalon-code") || "").trim();
  const acces = await verifierCode(env, code);
  if (!acces) return erreur(401, "Code d'accès refusé.", origin);

  if (Number(request.headers.get("content-length") || 0) > MAX_BODY) return erreur(413, "Données trop volumineuses.", origin);

  // Quota par code d'accès (le code est haché : il n'est jamais écrit dans les compteurs)
  const h = await sha256hex("code|" + code);
  if (env.DB) {
    const ok_h = await sous_limite(env, "ch:" + h, LIMITES.code_h);
    const ok_j = await sous_limite(env, "cj:" + h, LIMITES.code_j);
    if (!ok_h || !ok_j) return erreur(429, "Quota atteint pour ce code d'accès. Réessayez plus tard.", origin);
  }

  let recu;
  try { recu = await request.json(); } catch (e) { return erreur(400, "Requête illisible.", origin); }
  if (!recu || !MODELES.includes(recu.model)) return erreur(400, "Modèle non autorisé.", origin);
  if (!Array.isArray(recu.messages)) return erreur(400, "Requête invalide.", origin);

  // On ne transmet que les champs attendus ; seuls les outils de lecture d'annonce et de recherche web sont autorisés.
  const body = { model: recu.model, messages: recu.messages, max_tokens: Math.min(Number(recu.max_tokens) || 1024, MAX_TOKENS) };
  if (typeof recu.system === "string" || Array.isArray(recu.system)) body.system = recu.system;
  if (Array.isArray(recu.tools)) {
    const tools = [];
    const fetchTool = recu.tools.find(t => t && t.type === "web_fetch_20250910" && t.name === "web_fetch");
    const searchTool = recu.tools.find(t => t && t.type === "web_search_20250305" && t.name === "web_search");
    if (fetchTool) tools.push({ type: "web_fetch_20250910", name: "web_fetch", max_uses: Math.min(Number(fetchTool.max_uses) || 3, 3), max_content_tokens: Math.min(Number(fetchTool.max_content_tokens) || 20000, 20000) });
    if (searchTool) tools.push({ type: "web_search_20250305", name: "web_search", max_uses: Math.min(Number(searchTool.max_uses) || 2, 2) });
    if (tools.length) body.tools = tools;
  }

  // Quota mensuel de l'offre
  const generation = body.max_tokens > SEUIL_GENERATION, mois = moisCourant(), quota = QUOTAS[acces.offre];
  if (env.DB && quota) {
    const u = await env.DB.prepare("SELECT generations, autres FROM conso WHERE code_h = ?1 AND mois = ?2").bind(h, mois).first();
    if (generation && u && u.generations >= quota.generations)
      return erreur(402, "Vous avez utilisé vos " + quota.generations + " générations de CV de ce mois. Le compteur repart à zéro le 1er du mois prochain.", origin, { quota: true });
    if (!generation && u && u.autres >= quota.autres)
      return erreur(402, "Limite mensuelle d'utilisation atteinte. Le compteur repart à zéro le 1er du mois prochain.", origin, { quota: true });
  }

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": env.ANTHROPIC_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(body),
  });
  const texte = await res.text();

  // Consommation réelle (jetons, recherches web) par code et par mois : sert au quota et au calcul du coût
  if (env.DB && res.ok) {
    try {
      const u = (JSON.parse(texte) || {}).usage || {};
      const entree = (u.input_tokens || 0) + (u.cache_creation_input_tokens || 0) + (u.cache_read_input_tokens || 0);
      const recherches = (u.server_tool_use && u.server_tool_use.web_search_requests) || 0;
      await env.DB.prepare(
        "INSERT INTO conso (code_h, mois, offre, generations, autres, tokens_in, tokens_out, recherches) VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, ?8) " +
        "ON CONFLICT(code_h, mois) DO UPDATE SET generations = generations + excluded.generations, autres = autres + excluded.autres, " +
        "tokens_in = tokens_in + excluded.tokens_in, tokens_out = tokens_out + excluded.tokens_out, recherches = recherches + excluded.recherches"
      ).bind(h, mois, acces.offre, generation ? 1 : 0, generation ? 0 : 1, entree, u.output_tokens || 0, recherches).run();
    } catch (e) { /* le comptage ne doit jamais bloquer la réponse */ }
  }

  return new Response(texte, {
    status: res.status,
    headers: { "content-type": "application/json", ...cors(origin) },
  });
}

/* ---------- Paiement Stripe ---------- */
const idStripe = v => (typeof v === "string" ? v : (v && typeof v.id === "string" ? v.id : null));

// Identifiants des coupons appliqués à une session (lus sur la session, sinon sur l'abonnement créé)
async function couponsSession(env, s) {
  const ids = [];
  const lire = d => { if (!d) return; const c = d.coupon || (d.source && d.source.coupon); const id = idStripe(c); if (id) ids.push(id); };
  (Array.isArray(s.discounts) ? s.discounts : []).forEach(lire);
  const sub = idStripe(s.subscription);
  if (!ids.length && sub && env.STRIPE_KEY) {
    try {
      const r = await stripe(env, "GET", "/v1/subscriptions/" + encodeURIComponent(sub) + "?expand[]=discounts");
      if (r.ok && r.d) { (Array.isArray(r.d.discounts) ? r.d.discounts : []).forEach(lire); lire(r.d.discount); }
    } catch (e) { /* en cas d'échec : offre par défaut */ }
  }
  return ids;
}

// Enregistre une session de paiement payée et renvoie son code d'accès (toujours le même pour une même session)
async function enregistrerSession(env, s) {
  const paye = s && s.mode === "subscription" && s.status === "complete" &&
    (s.payment_status === "paid" || s.payment_status === "no_payment_required");
  if (!paye || typeof s.id !== "string") return null;
  // Preuve d'acceptation : versions des CGV et de la politique + horodatage, transmis par la page d'inscription
  const accepte = /^[A-Za-z0-9_-]{1,200}$/.test(s.client_reference_id || "") ? s.client_reference_id : null;
  const offre = (await couponsSession(env, s)).includes(COUPON_OFFERT) ? "offert" : OFFRE_PAR_DEFAUT;
  await env.DB.prepare(
    "INSERT INTO abonnes (code, session, client, abonnement, offre, actif, cree, accepte) VALUES (?1, ?2, ?3, ?4, ?5, 1, ?6, ?7) " +
    "ON CONFLICT(session) DO UPDATE SET client = COALESCE(excluded.client, client), abonnement = COALESCE(excluded.abonnement, abonnement), accepte = COALESCE(excluded.accepte, accepte)"
  ).bind(nouveauCode(), s.id, idStripe(s.customer), idStripe(s.subscription), offre, maintenant(), accepte).run();
  const row = await env.DB.prepare("SELECT code FROM abonnes WHERE session = ?1").bind(s.id).first();
  return row ? row.code : null;
}

// Envoie un e-mail client via le workflow n8n « [JLT] 05 » : bienvenue (code + CGV et politique en PDF),
// resiliation (date d'effet), avertissement (suppression dans 7 jours). Renvoie true si l'envoi a réussi.
const dateFr = ms => new Date(ms).toLocaleDateString("fr-FR", { day: "numeric", month: "long", year: "numeric", timeZone: "Europe/Paris" });
async function envoyerMail(env, donnees) {
  if (!env.MAIL_SECRET || !donnees || !donnees.email) return false;
  try {
    const r = await fetch(env.MAILS_WEBHOOK || MAILS_DEFAUT, {
      method: "POST",
      headers: { "content-type": "application/json", "x-jaltio-secret": env.MAIL_SECRET },
      body: JSON.stringify(donnees),
      signal: AbortSignal.timeout(20000),
    });
    return r.ok;
  } catch (e) { return false; }
}

// Envoie le mail de bienvenue une seule fois par paiement. Renvoie false si l'envoi a échoué.
async function envoyerCode(env, session, email, code) {
  if (!env.MAIL_SECRET || !email || !code) return true;
  const pris = await env.DB.prepare("UPDATE abonnes SET envoye = 1 WHERE session = ?1 AND envoye = 0").bind(session).run();
  if (!pris.meta || pris.meta.changes !== 1) return true;       // déjà envoyé (ou en cours d'envoi ailleurs)
  if (await envoyerMail(env, { type: "bienvenue", email, code })) return true;
  await env.DB.prepare("UPDATE abonnes SET envoye = 0 WHERE session = ?1").bind(session).run();
  return false;
}

/* ---------- Appels à l'API Stripe (clé restreinte) ---------- */
async function stripe(env, methode, chemin, form) {
  const res = await fetch((env.STRIPE_API || "https://api.stripe.com") + chemin, {
    method: methode,
    headers: { "Authorization": "Bearer " + env.STRIPE_KEY, ...(form ? { "content-type": "application/x-www-form-urlencoded" } : {}) },
    body: form ? new URLSearchParams(form).toString() : undefined,
  });
  let d = null; try { d = await res.json(); } catch (e) {}
  return { ok: res.ok, status: res.status, d };
}
// Fin de la période payée d'un abonnement (champ déplacé dans les éléments de l'abonnement depuis l'API 2025-03)
const finPeriode = sub => {
  const s = (sub && (sub.current_period_end || (sub.items && sub.items.data && sub.items.data[0] && sub.items.data[0].current_period_end))) || 0;
  return s ? s * 1000 : null;
};
async function emailClient(env, client) {
  if (!client) return "";
  const r = await stripe(env, "GET", "/v1/customers/" + encodeURIComponent(client));
  return (r.ok && r.d && typeof r.d.email === "string") ? r.d.email : "";
}

// Lit l'abonnement lié à un code d'accès (en-tête x-jalon-code)
async function abonnementDuCode(request, env, origin) {
  if (request.method !== "POST") return { err: erreur(405, "Méthode non autorisée.", origin) };
  if (!env.DB) return { err: erreur(503, "Service non configuré.", origin) };
  const ip = await sha256hex("ip|" + (request.headers.get("CF-Connecting-IP") || "?"));
  if (!(await sous_limite(env, "abo:" + ip, LIMITES.compte_abo))) return { err: erreur(429, "Trop de demandes. Patientez quelques minutes.", origin) };
  const code = (request.headers.get("x-jalon-code") || "").trim();
  const codes = String(env.CODES || "").split(",").map(c => c.trim()).filter(Boolean);
  if (code && codes.includes(code)) return { testeur: true };
  if (!/^jal-[a-z0-9]{4}-[a-z0-9]{4}$/.test(code)) return { err: erreur(401, "Code d'accès manquant ou invalide.", origin) };
  const row = await env.DB.prepare("SELECT code, client, abonnement, offre, actif, fin FROM abonnes WHERE code = ?1").bind(code).first();
  if (!row) return { err: erreur(404, "Aucun abonnement ne correspond à ce code.", origin) };
  return { row };
}

// État de l'abonnement, pour l'onglet Mon profil
async function statutAbonnement(request, env, origin) {
  const a = await abonnementDuCode(request, env, origin);
  if (a.err) return a.err;
  if (a.testeur) return reponse({ offre: "testeur", actif: true }, 200, origin);
  const r = a.row;
  return reponse({ offre: r.offre, actif: r.actif === 1, fin: r.fin || null, resiliation_prevue: r.actif === 1 && !!r.fin }, 200, origin);
}

// Résiliation depuis le site : fin de l'abonnement à la fin de la période payée, confirmation par e-mail
async function resilierAbonnement(request, env, origin, ctx) {
  const a = await abonnementDuCode(request, env, origin);
  if (a.err) return a.err;
  if (a.testeur) return erreur(400, "Ce code de test n'est lié à aucun abonnement payant.", origin);
  const r = a.row;
  if (!env.STRIPE_KEY || !r.abonnement) return erreur(503, "La résiliation en ligne n'est pas disponible pour l'instant. Écrivez à contact@jaltio.fr.", origin);
  if (r.actif !== 1) return reponse({ deja: true, fin: r.fin || null, actif: false }, 200, origin);
  if (r.fin) return reponse({ deja: true, fin: r.fin, actif: true }, 200, origin);
  const s = await stripe(env, "POST", "/v1/subscriptions/" + encodeURIComponent(r.abonnement), { cancel_at_period_end: "true" });
  if (!s.ok) return erreur(502, "Stripe n'a pas pu enregistrer la résiliation. Réessayez dans une minute ou écrivez à contact@jaltio.fr.", origin);
  const fin = finPeriode(s.d) || maintenant();
  await env.DB.prepare("UPDATE abonnes SET fin = ?1 WHERE code = ?2").bind(fin, r.code).run();
  const envoi = (async () => {
    const email = await emailClient(env, idStripe(s.d.customer) || r.client);
    if (email) await envoyerMail(env, { type: "resiliation", email, date: dateFr(fin) });
  })();
  if (ctx && ctx.waitUntil) ctx.waitUntil(envoi); else await envoi;
  return reponse({ ok: true, fin, actif: true }, 200, origin);
}
const emailSession = s => (s && ((s.customer_details && s.customer_details.email) || s.customer_email)) || "";

// Appelée par le site au retour du paiement (jaltio.fr/?paye=cs_…) : renvoie le code d'accès de l'acheteur
async function codeApresPaiement(request, env, origin, ctx) {
  if (request.method !== "POST") return erreur(405, "Méthode non autorisée.", origin);
  if (!env.DB || !env.STRIPE_KEY) return erreur(503, "Le paiement n'est pas encore configuré côté serveur.", origin);
  const ip = await sha256hex("ip|" + (request.headers.get("CF-Connecting-IP") || "?"));
  if (!(await sous_limite(env, "pay:" + ip, LIMITES.paiement))) return erreur(429, "Trop de demandes. Patientez une minute.", origin);
  let b; try { b = await request.json(); } catch (e) { return erreur(400, "Requête illisible.", origin); }
  const session = String((b && b.session) || "");
  if (!/^cs_(test|live)_[A-Za-z0-9]{10,200}$/.test(session)) return erreur(400, "Référence de paiement invalide.", origin);

  const deja = await env.DB.prepare("SELECT code FROM abonnes WHERE session = ?1").bind(session).first();
  if (deja) return reponse({ code: deja.code }, 200, origin);

  const res = await fetch((env.STRIPE_API || "https://api.stripe.com") + "/v1/checkout/sessions/" + session, {
    headers: { "Authorization": "Bearer " + env.STRIPE_KEY },
  });
  if (res.status === 404) return erreur(404, "Paiement introuvable.", origin);
  if (!res.ok) return erreur(502, "Stripe ne répond pas. Réessayez dans une minute.", origin);
  const s = await res.json();
  const code = await enregistrerSession(env, s);
  if (!code) return erreur(409, "Le paiement n'est pas encore confirmé. Réessayez dans une minute.", origin, { attente: true });
  const envoi = envoyerCode(env, session, emailSession(s), code);
  if (ctx && ctx.waitUntil) ctx.waitUntil(envoi); else await envoi;
  return reponse({ code }, 200, origin);
}

// Webhook Stripe (signature vérifiée) : enregistre les paiements et coupe les codes des abonnements terminés
async function webhookStripe(request, env) {
  const json = (obj, status) => new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json" } });
  if (request.method !== "POST") return json({ error: "Méthode non autorisée." }, 405);
  if (!env.DB || !env.STRIPE_WEBHOOK_SECRET) return json({ error: "Non configuré." }, 503);
  const brut = await request.text();
  if (brut.length > 500000) return json({ error: "Trop volumineux." }, 413);

  let t = "";
  const v1 = [];
  for (const morceau of (request.headers.get("Stripe-Signature") || "").split(",")) {
    const i = morceau.indexOf("="), k = morceau.slice(0, i).trim(), v = morceau.slice(i + 1).trim();
    if (k === "t") t = v; else if (k === "v1") v1.push(v);
  }
  if (!/^\d+$/.test(t) || !v1.length || Math.abs(Date.now() / 1000 - Number(t)) > 300) return json({ error: "Signature invalide." }, 400);
  const attendu = await hmacHex(env.STRIPE_WEBHOOK_SECRET, t + "." + brut);
  if (!v1.some(s => egal(s, attendu))) return json({ error: "Signature invalide." }, 400);

  let ev; try { ev = JSON.parse(brut); } catch (e) { return json({ error: "Illisible." }, 400); }
  const o = (ev && ev.data && ev.data.object) || {};
  if (ev.type === "checkout.session.completed") {
    const code = await enregistrerSession(env, o);
    if (code && !(await envoyerCode(env, o.id, emailSession(o), code)))
      return json({ error: "Envoi de l'e-mail impossible pour l'instant." }, 500);   // Stripe renverra l'événement plus tard
  } else if (ev.type === "customer.subscription.updated" || ev.type === "customer.subscription.deleted") {
    // past_due : Stripe retente le prélèvement, on laisse l'accès pendant les relances
    const actif = ev.type === "customer.subscription.updated" && ["active", "trialing", "past_due"].includes(o.status) ? 1 : 0;
    // fin = date de fin d'accès : prévue (résiliation en fin de période), réelle (abonnement terminé), ou vide (abonnement en cours)
    let fin = null;
    if (!actif) fin = (o.ended_at || o.canceled_at || Math.floor(Date.now() / 1000)) * 1000;
    else if (o.cancel_at_period_end) fin = finPeriode(o) || (o.cancel_at ? o.cancel_at * 1000 : null);
    else if (o.cancel_at) fin = o.cancel_at * 1000;
    if (typeof o.id === "string") await env.DB.prepare("UPDATE abonnes SET actif = ?1, fin = ?2, averti = CASE WHEN ?1 = 1 THEN 0 ELSE averti END WHERE abonnement = ?3").bind(actif, fin, o.id).run();
  }
  return json({ received: true }, 200);
}

export default {
  async fetch(request, env, ctx) {
    const chemin = new URL(request.url).pathname.replace(/\/+$/, "") || "/";
    if (chemin === "/stripe/webhook") {       // appelé par les serveurs de Stripe : pas d'en-tête Origin
      try { return await webhookStripe(request, env); }
      catch (e) { return new Response(JSON.stringify({ error: "Erreur du serveur." }), { status: 500, headers: { "content-type": "application/json" } }); }
    }
    const origin = request.headers.get("Origin") || "";
    if (!ORIGINES.includes(origin)) return erreur(403, "Origine non autorisée.", "null");
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    try {
      if (chemin === "/stripe/code") return await codeApresPaiement(request, env, origin, ctx);
      if (chemin === "/stripe/statut") return await statutAbonnement(request, env, origin);
      if (chemin === "/stripe/resilier") return await resilierAbonnement(request, env, origin, ctx);
      if (chemin.startsWith("/sync/")) return await synchro(request, env, origin, chemin);
      return await relais(request, env, origin);
    } catch (e) {
      return erreur(500, "Erreur du serveur. Réessayez dans un instant.", origin);
    }
  },

  // Chaque nuit : avertissement 7 jours avant, puis suppression des comptes 6 mois après la fin de l'abonnement ;
  // comptes sans abonnement (testeurs) sans connexion depuis CONSERVATION_JOURS ; compteurs périmés
  async scheduled(event, env) {
    if (!env.DB) return;
    const t = Date.now(), apres = APRES_FIN_JOURS * 864e5, preavis = PREAVIS_JOURS * 864e5;
    // 1. Avertissement : abonnement terminé, suppression dans 7 jours au plus, pas encore averti
    const aAvertir = await env.DB.prepare(
      "SELECT code, client, fin FROM abonnes WHERE actif = 0 AND fin IS NOT NULL AND averti = 0 AND fin + ?1 - ?2 <= ?3 LIMIT 50"
    ).bind(apres, preavis, t).all();
    for (const r of (aAvertir.results || [])) {
      const h = await sha256hex("code|" + r.code);
      const compte = await env.DB.prepare("SELECT id FROM sync WHERE code_h = ?1 LIMIT 1").bind(h).first();
      let ok = true;
      if (compte && env.STRIPE_KEY) {
        const email = await emailClient(env, r.client);
        ok = !email || await envoyerMail(env, { type: "avertissement", email, date: dateFr(Math.max(r.fin + apres, t + preavis)) });
      }
      if (ok) await env.DB.prepare("UPDATE abonnes SET averti = ?1 WHERE code = ?2").bind(t, r.code).run();
    }
    // 2. Suppression : 6 mois après la fin, et au moins 7 jours après l'avertissement
    const aSupprimer = await env.DB.prepare(
      "SELECT code FROM abonnes WHERE actif = 0 AND fin IS NOT NULL AND averti > 0 AND fin + ?1 <= ?2 AND averti + ?3 <= ?2 LIMIT 200"
    ).bind(apres, t, preavis).all();
    for (const r of (aSupprimer.results || [])) {
      await env.DB.prepare("DELETE FROM sync WHERE code_h = ?1").bind(await sha256hex("code|" + r.code)).run();
      await env.DB.prepare("UPDATE abonnes SET averti = -1 WHERE code = ?1").bind(r.code).run();   // -1 = données supprimées
    }
    // 3. Comptes non liés à un abonnement (codes testeurs) : 400 jours sans connexion
    await env.DB.prepare("DELETE FROM sync WHERE code_h IS NULL AND accessed < ?1").bind(t - CONSERVATION_JOURS * 864e5).run();
    await env.DB.prepare("DELETE FROM rate WHERE exp < ?1").bind(Math.floor(Date.now() / 1000)).run();
    try { await env.DB.prepare("DELETE FROM conso WHERE mois < ?1").bind(new Date(Date.now() - 400 * 864e5).toISOString().slice(0, 7)).run(); } catch (e) {}
  },
};
