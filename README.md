# Elanos — votre coach emploi IA

*Chaque étape, jusqu'au poste.*

Site qui adapte un CV et une lettre de motivation à chaque offre d'emploi, conseille comme un coach et suit les candidatures jusqu'à l'entretien. Il fonctionne avec Claude (Anthropic).

Le nom de la marque se change à un seul endroit : la constante `BRAND` au début du script de `index.html`.

## Architecture

- **Site** : un seul fichier `index.html` (+ `fonts.css` et `fonts/`, polices hébergées sur le site, aucune requête vers Google), publié sur GitHub Pages.
- **Relais** (`worker/jalon-relais.js`) : Cloudflare Worker. Il garde la clé API Anthropic côté serveur ; le navigateur n'envoie qu'un code d'accès. Le contenu du CV et de l'offre transite donc par Cloudflare puis Anthropic (États-Unis).
- **Synchronisation optionnelle** (routes `/sync/*`, base Cloudflare D1, schéma dans `worker/schema.sql`) : le navigateur chiffre les données (AES-GCM, clé dérivée du mot de passe) avant envoi. Le serveur ne stocke qu'un hash de l'e-mail, un hash du jeton d'authentification et le bloc chiffré. Purge automatique après 400 jours sans connexion.
- **Par défaut** : parcours, historique et réglages restent dans le navigateur (`localStorage`). Export et import de fichier disponibles.

## Ce que fait le site

1. **Parcours** : on dépose son ancien CV (PDF, Word .docx, texte) ou on décrit son parcours. On peut ajouter une photo.
2. **Offre** : on colle le lien de l'annonce, ou son texte.
3. **Génération** : Claude lit l'annonce, rédige un CV d'une page optimisé pour les logiciels de tri (ATS) et la lettre de motivation. Il cherche aussi la couleur de l'entreprise pour l'appliquer aux documents.
4. **Corrections** : on corrige un mot directement dans le document, ou on écrit ce qui ne plaît pas et Claude refait une version.
5. **Téléchargement** : bouton « Télécharger le CV (PDF) », puis « Enregistrer au format PDF ».

## Mise en ligne

1. Dépôt GitHub public, **Settings → Pages**, source `main`, dossier `/ (root)`.
2. Déposer `index.html`, `fonts.css` et le dossier `fonts/` (sans eux, le site s'affiche avec les polices du système).
3. Adresse : `https://<pseudo>.github.io/cv-express/`.

## Le relais Cloudflare

Voir l'en-tête de `worker/jalon-relais.js` : secrets `ANTHROPIC_KEY` (clé dédiée à Elanos) et `CODES` (un code d'accès par testeur, séparés par des virgules), base D1 liée sous le nom `DB`, déclencheur planifié `0 3 * * 0`.

- **Révoquer un testeur** : retirer son code de `CODES`.
- **Plafonner la dépense** : fixer une limite mensuelle dans la console Anthropic et ne pas activer la recharge automatique.
- **Aucune clé API n'est acceptée dans le navigateur.** Une clé `sk-ant-…` saisie à la place du code est refusée.

## Limites connues

- **LinkedIn et Indeed** bloquent souvent la lecture automatique de leurs annonces. Il suffit alors de coller le texte de l'annonce.
- **PDF scannés** : s'ils ne contiennent pas de texte, Claude les lit (quelques centimes de plus).
- **Anciens fichiers Word (.doc)** : non lus. Les réenregistrer en .docx ou en PDF.
- **Couleur de l'entreprise** : trouvée par recherche web. Si elle est fausse ou trop claire, choisir une autre pastille.
- **Bibliothèques externes** : la lecture des PDF et Word charge `pdf.js` et `mammoth` depuis `cdnjs.cloudflare.com` (à citer dans la politique de confidentialité, ou à héberger soi-même).
- **Mot de passe de synchronisation perdu** : les données en ligne sont irrécupérables.
