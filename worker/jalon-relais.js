// Relais Jalon (Cloudflare Worker)
//
// 1) Relais Claude : garde la clé Anthropic côté serveur ; le navigateur n'envoie qu'un code d'accès testeur.
// 2) Synchronisation entre appareils (routes /sync/*) : le serveur ne reçoit qu'un bloc CHIFFRÉ dans le
//    navigateur (AES-GCM, clé dérivée du mot de passe par PBKDF2) et un identifiant haché. Il ne voit jamais
//    l'e-mail, le mot de passe ni le contenu des CV.
//
// À créer dans Cloudflare :
//   Secrets (Settings > Variables and Secrets, type « Secret ») :
//     ANTHROPIC_KEY  = la clé sk-ant-... dédiée à Jalon
//     CODES          = codes testeurs séparés par des virgules, ex. « maman-7k2, julien-p9x »
//   Base D1 liée au Worker (Settings > Bindings > Add > D1 database), nom de variable : DB
//   Tables : voir worker/schema.sql (à coller dans l'onglet Console de la base D1)
//   Déclencheur planifié (Settings > Triggers > Cron) : « 0 3 * * 0 » (nettoyage hebdomadaire)

const ORIGINES = ["https://maxencepemjean-creator.github.io"];
const MODELES = ["claude-sonnet-5-5", "claude-opus-5-5"];
const MAX_TOKENS = 16000;

const MAX_BODY = 1900000;              // octets : requête de synchro complète (D1 limite une ligne à 2 Mo)
const CONSERVATION_JOURS = 400;        // données supprimées après ce délai sans aucune connexion
const LIMITES = {                      // [nombre max, fenêtre en secondes]
  ip:       [90, 60],                  // toutes routes /sync, par adresse (hachée)
  compte:   [30, 60],                  // toutes routes /sync, par identifiant
  echecs:   [8, 900],                  // mots de passe faux, par identifiant
  creation: [5, 3600],                 // créations de compte, par adresse (hachée)
};

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
      const codes = String(env.CODES || "").split(",").map(c => c.trim()).filter(Boolean);
      const code = (request.headers.get("x-jalon-code") || "").trim();
      if (!code || !codes.includes(code)) return erreur(403, "Un code d'accès valide est nécessaire pour créer la synchronisation.", origin);
      if (!RE_ID.test(b.auth || "")) return erreur(400, "Authentification invalide.", origin);
      if (!RE_B64.test(b.salt || "") || b.salt.length !== 24) return erreur(400, "Sel invalide.", origin);
      if (!(await sous_limite(env, "new:" + ip, LIMITES.creation))) return erreur(429, "Trop de créations de compte. Réessayez plus tard.", origin);
      const t = maintenant();
      const r = await env.DB.prepare(
        "INSERT INTO sync (id, auth, salt, iv, ct, version, updated, accessed, size) VALUES (?1, ?2, ?3, ?4, ?5, 1, ?6, ?6, ?7) ON CONFLICT(id) DO NOTHING"
      ).bind(b.id, await sha256hex(b.auth), b.salt, b.iv, b.ct, t, b.ct.length).run();
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

  const codes = String(env.CODES || "").split(",").map(c => c.trim()).filter(Boolean);
  const code = (request.headers.get("x-jalon-code") || "").trim();
  if (!code || !codes.includes(code)) return erreur(401, "Code d'accès refusé.", origin);

  let body;
  try { body = await request.json(); } catch (e) { return erreur(400, "Requête illisible.", origin); }
  if (!MODELES.includes(body.model)) return erreur(400, "Modèle non autorisé.", origin);
  body.max_tokens = Math.min(Number(body.max_tokens) || 1024, MAX_TOKENS);

  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": env.ANTHROPIC_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(body),
  });
  return new Response(res.body, {
    status: res.status,
    headers: { "content-type": "application/json", ...cors(origin) },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    if (!ORIGINES.includes(origin)) return erreur(403, "Origine non autorisée.", "null");
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
    const chemin = new URL(request.url).pathname.replace(/\/+$/, "") || "/";
    try {
      if (chemin.startsWith("/sync/")) return await synchro(request, env, origin, chemin);
      return await relais(request, env, origin);
    } catch (e) {
      return erreur(500, "Erreur du serveur. Réessayez dans un instant.", origin);
    }
  },

  // Nettoyage hebdomadaire : données sans aucune connexion depuis CONSERVATION_JOURS, compteurs périmés
  async scheduled(event, env) {
    if (!env.DB) return;
    await env.DB.prepare("DELETE FROM sync WHERE accessed < ?1").bind(Date.now() - CONSERVATION_JOURS * 864e5).run();
    await env.DB.prepare("DELETE FROM rate WHERE exp < ?1").bind(Math.floor(Date.now() / 1000)).run();
  },
};
