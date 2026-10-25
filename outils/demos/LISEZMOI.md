# Démos vidéo Jaltio

Chaque démo = un profil fictif avec son CV « avant » (texte brut) et son CV « après » (rendu par l'appli Jaltio).
Elles alimentent la production vidéo du dimanche ([JLT] 01), via l'onglet **Démos** du Google Sheet « Elanos ».

1. Écrire un lot `outils/demos/lots/lot-AAAAMMJJ.json` (même format que `lot-20261025.json`) :
   `id` (D35, D36…), `metier`, `profil`, `offre`, `score`, `couleur`, `ancien_cv` (texte brut, 1re ligne = nom),
   `cv` (JSON de l'appli, en respectant les règles du prompt de génération de `app/index.html` : rien d'inventé).
2. `node outils/demos/fabriquer.js outils/demos/lots/lot-AAAAMMJJ.json` → `demos/Dxx_avant.png` et `demos/Dxx_apres.png`.
3. Vérifier les images, puis commit + push (elles sont servies sur https://jaltio.fr/demos/).
4. Envoyer les lignes au workflow n8n « [JLT] 10 - Ajout de démos vidéo » (POST /webhook/jaltio-demos-ajout,
   en-tête `x-jaltio-secret`, corps `{ "demos": [ { id, metier, profil, ancien_cv, offre, score, nom } ] }`).

Règles : profils 100 % fictifs (06 00 00 00 00, adresses @exemple.fr), villes de Charente-Maritime, aucun nom
d'entreprise réelle, métiers différents de ceux déjà utilisés, score honnête (75 à 92).
