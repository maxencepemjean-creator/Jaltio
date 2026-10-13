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
  size     INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS rate (
  k   TEXT PRIMARY KEY,           -- compteur de limitation de requêtes
  n   INTEGER NOT NULL,
  exp INTEGER NOT NULL
);
