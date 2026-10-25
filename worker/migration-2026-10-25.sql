-- Migration du 25/10/2026 : résiliation sur le site, preuve d'acceptation des CGV, suppression 6 mois après la fin.
-- À coller UNE fois dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
ALTER TABLE abonnes ADD COLUMN fin INTEGER;                       -- date de fin d'accès (ms) : prévue ou réelle
ALTER TABLE abonnes ADD COLUMN averti INTEGER NOT NULL DEFAULT 0; -- date de l'e-mail d'avertissement (ms) ; -1 = données supprimées
ALTER TABLE abonnes ADD COLUMN accepte TEXT;                      -- versions des CGV et de la politique acceptées + horodatage
ALTER TABLE sync ADD COLUMN code_h TEXT;                          -- empreinte du code d'abonné lié au compte (jamais le code)
CREATE INDEX IF NOT EXISTS sync_code_h ON sync (code_h);
