-- Migration du 27/11/2026 : lettre de motivation offerte dans l'offre Free (3 CV + 1 lettre).
-- À coller UNE fois dans Cloudflare > Storage & databases > D1 > jalon-sync > Console, puis « Execute ».
-- Sans cette colonne, le relais fonctionne comme avant (aucune lettre en Free).
ALTER TABLE conso ADD COLUMN lettres INTEGER NOT NULL DEFAULT 0;   -- lettres offertes utilisées (Free)
