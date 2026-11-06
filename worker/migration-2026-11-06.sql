-- Migration du 06/11/2026 : l'abonnement est rattaché au compte (e-mail + mot de passe), plus seulement au navigateur.
-- À coller UNE fois dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
ALTER TABLE abonnes ADD COLUMN compte TEXT;   -- identifiant du compte de synchronisation (SHA-256 de l'e-mail, jamais l'e-mail)
CREATE INDEX IF NOT EXISTS abonnes_compte ON abonnes (compte);
