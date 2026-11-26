-- Migration du 26/11/2026 : fonction de rétractation en ligne (art. L221-21 du Code de la consommation).
-- À coller UNE fois dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
CREATE TABLE IF NOT EXISTS retractations (
  ref TEXT PRIMARY KEY,          -- numéro donné au client (R-AAAAMMJJ-XXXXXX)
  cree INTEGER NOT NULL,         -- date de la déclaration (ms)
  nom TEXT NOT NULL,
  email TEXT NOT NULL,           -- adresse donnée par le client, pour lui répondre et retrouver l'abonnement dans Stripe
  offre TEXT,
  souscription TEXT,             -- date de souscription indiquée par le client (facultative)
  message TEXT,
  ip_h TEXT,                     -- empreinte de l'adresse IP (lutte contre les abus)
  traite INTEGER NOT NULL DEFAULT 0  -- 1 quand le remboursement est fait (à mettre à jour à la main)
);
-- Conservation : 5 ans (preuve en cas de litige), comme les autres données contractuelles.
