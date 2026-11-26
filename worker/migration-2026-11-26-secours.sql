-- Migration du 26/11/2026 : code de secours (mot de passe oublié).
-- À coller UNE fois dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
-- Le serveur ne connaît ni le code de secours, ni la clé des données : seulement l'empreinte du jeton tiré du code
-- et une enveloppe chiffrée (la clé des données, chiffrée avec une clé tirée du code).
ALTER TABLE sync ADD COLUMN r_salt TEXT;   -- sel PBKDF2 du code de secours
ALTER TABLE sync ADD COLUMN r_auth TEXT;   -- SHA-256 du jeton tiré du code de secours
ALTER TABLE sync ADD COLUMN r_iv   TEXT;   -- vecteur d'initialisation de l'enveloppe
ALTER TABLE sync ADD COLUMN r_env  TEXT;   -- clé des données, chiffrée avec la clé tirée du code de secours
