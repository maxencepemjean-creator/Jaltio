-- Migration du 02/11/2026 : offre Free (inscription sans paiement, une seule fois par adresse e-mail).
-- À coller UNE fois dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
CREATE TABLE IF NOT EXISTS gratuits (
  email_h TEXT PRIMARY KEY,        -- SHA-256 de l'adresse normalisée (une seule offre Free par adresse)
  session TEXT UNIQUE NOT NULL,    -- référence interne fr_… (lien du mail, code à 6 chiffres) ; le code d'accès est dans abonnes
  email   TEXT,                    -- adresse pour l'envoi du code ; effacée après 12 mois sans connexion
  cree    INTEGER NOT NULL         -- date d'inscription (ms)
);
