-- Base D1 « jalon-sync » : à coller dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
-- Le serveur ne stocke que : un identifiant haché, l'empreinte du jeton d'authentification, le sel,
-- et le bloc chiffré dans le navigateur (il ne peut pas le lire).

CREATE TABLE IF NOT EXISTS sync (
  id       TEXT PRIMARY KEY,      -- SHA-256 de l'e-mail (jamais l'e-mail)
  auth     TEXT NOT NULL,         -- SHA-256 du jeton d'authentification (jamais le mot de passe)
  salt     TEXT NOT NULL,         -- sel aléatoire PBKDF2 (public par nature)
  iv       TEXT NOT NULL,         -- vecteur d'initialisation AES-GCM
  ct       TEXT NOT NULL,         -- données chiffrées
  version  INTEGER NOT NULL,      -- augmente à chaque envoi (détection de conflit)
  updated  INTEGER NOT NULL,      -- dernier envoi (ms)
  accessed INTEGER NOT NULL,      -- dernière connexion (ms), sert à la suppression automatique
  size     INTEGER NOT NULL,
  code_h   TEXT                   -- empreinte du code d'abonné lié (suppression 6 mois après la fin de l'abonnement)
);
CREATE INDEX IF NOT EXISTS sync_code_h ON sync (code_h);

CREATE TABLE IF NOT EXISTS rate (
  k   TEXT PRIMARY KEY,           -- compteur de limitation de requêtes
  n   INTEGER NOT NULL,
  exp INTEGER NOT NULL
);

-- Abonnés payants : un code d'accès par paiement Stripe (créé automatiquement par le Worker)
CREATE TABLE IF NOT EXISTS abonnes (
  code       TEXT PRIMARY KEY,      -- code d'accès donné à l'acheteur, ex. jal-7k2m-p9xq
  session    TEXT UNIQUE NOT NULL,  -- session de paiement Stripe (cs_...) ou inscription Free (fr_...)
  client     TEXT,                  -- client Stripe (cus_...)
  abonnement TEXT,                  -- abonnement Stripe (sub_...)
  offre      TEXT NOT NULL,         -- essentiel, offert, free (pro plus tard)
  actif      INTEGER NOT NULL,      -- 1 = abonnement en cours, 0 = terminé
  cree       INTEGER NOT NULL,      -- date de création (ms)
  envoye     INTEGER NOT NULL DEFAULT 0,  -- 1 = code envoyé par e-mail
  fin        INTEGER,                    -- date de fin d'accès (ms), prévue ou réelle
  averti     INTEGER NOT NULL DEFAULT 0, -- date de l'e-mail d'avertissement avant suppression ; -1 = données supprimées
  accepte    TEXT                        -- versions des CGV et de la politique acceptées + horodatage
);
-- Base créée avant le 25/10/2026 : exécuter une fois worker/migration-2026-10-25.sql
-- Base créée avant l'envoi par e-mail : exécuter UNE fois  ALTER TABLE abonnes ADD COLUMN envoye INTEGER NOT NULL DEFAULT 0;
CREATE INDEX IF NOT EXISTS abonnes_abonnement ON abonnes (abonnement);

-- Consommation par code et par mois (le code est haché) : quota mensuel et coût réel
CREATE TABLE IF NOT EXISTS conso (
  code_h      TEXT NOT NULL,        -- SHA-256 du code d'accès
  mois        TEXT NOT NULL,        -- ex. 2026-10
  offre       TEXT NOT NULL,        -- testeur, essentiel...
  generations INTEGER NOT NULL,     -- CV + lettres générés ou régénérés
  autres      INTEGER NOT NULL,     -- petits appels (lecture d'offre, coach...)
  tokens_in   INTEGER NOT NULL,
  tokens_out  INTEGER NOT NULL,
  recherches  INTEGER NOT NULL,     -- recherches web facturées
  PRIMARY KEY (code_h, mois)
);

-- Offre Free : une inscription par adresse e-mail (créée par le Worker, route /free/inscription)
CREATE TABLE IF NOT EXISTS gratuits (
  email_h TEXT PRIMARY KEY,        -- SHA-256 de l'adresse normalisée (une seule offre Free par adresse)
  session TEXT UNIQUE NOT NULL,    -- référence interne fr_… (lien du mail, code à 6 chiffres) ; le code d'accès est dans abonnes
  email   TEXT,                    -- adresse pour l'envoi du code ; effacée après 12 mois sans connexion
  cree    INTEGER NOT NULL         -- date d'inscription (ms)
);
-- Base créée avant le 02/11/2026 : exécuter une fois worker/migration-2026-11-02.sql
