-- Migration du 27/11/2026 : mot de passe oublié par lien e-mail (option B).
-- À coller UNE fois dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
-- La clé de chaque compte est gardée chiffrée avec le secret CLE_COMPTES du Worker : avec un lien reçu par e-mail,
-- la personne choisit un nouveau mot de passe et garde ses documents.
ALTER TABLE sync ADD COLUMN k_iv  TEXT;   -- vecteur d'initialisation
ALTER TABLE sync ADD COLUMN k_env TEXT;   -- clé des données du compte, chiffrée avec CLE_COMPTES
