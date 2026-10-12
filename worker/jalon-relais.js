// Relais Jalon (Cloudflare Worker)
// Garde la clé Anthropic côté serveur : le navigateur n'envoie qu'un code d'accès testeur.
// Secrets à créer dans Cloudflare (Settings > Variables and Secrets, type « Secret ») :
//   ANTHROPIC_KEY  = la clé sk-ant-... dédiée à Jalon
//   CODES          = codes testeurs séparés par des virgules, ex. « maman-7k2, julien-p9x »

const ORIGINES = ["https://maxencepemjean-creator.github.io"];
const MODELES = ["claude-sonnet-5-5", "claude-opus-5-5"];
const MAX_TOKENS = 16000;

function cors(origin) {
  return {
    "Access-Control-Allow-Origin": origin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "content-type, x-jalon-code",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function erreur(status, message, origin) {
  return new Response(JSON.stringify({ error: { message } }), {
    status,
    headers: { "content-type": "application/json", ...cors(origin) },
  });
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    if (!ORIGINES.includes(origin)) return erreur(403, "Origine non autorisée.", "null");
    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors(origin) });
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
  },
};
