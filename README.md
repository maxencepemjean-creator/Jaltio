# Jalon — votre coach emploi IA

*Chaque étape, jusqu'au poste.*

Site qui adapte un CV et une lettre de motivation à chaque offre d'emploi, conseille comme un coach et suit les candidatures jusqu'à l'entretien. Il fonctionne avec Claude (Anthropic).

Le nom de la marque se change à un seul endroit : la constante `BRAND` au début du script de `index.html`.
Pensé pour un usage familial : 2 ou 3 personnes, avec la clé API de Maxence.

## Ce que fait le site

1. **Parcours** : on dépose son ancien CV (PDF, Word .docx, texte) ou on décrit son parcours. On peut ajouter une photo.
2. **Offre** : on colle le lien de l'annonce, ou son texte.
3. **Génération** : Claude lit l'annonce, rédige un CV d'une page optimisé pour les logiciels de tri (ATS) et la lettre de motivation. Il cherche aussi la couleur de l'entreprise pour l'appliquer aux documents.
4. **Corrections** : on corrige un mot directement dans le document, ou on écrit ce qui ne plaît pas et Claude refait une version.
5. **Téléchargement** : bouton « Télécharger le CV (PDF) », puis « Enregistrer au format PDF ».

Tout reste dans le navigateur de la personne : parcours, historique et clé. Aucun serveur, aucune base de données.

## Mise en ligne sur GitHub Pages (une seule fois, 5 minutes)

1. Sur github.com, cliquer sur **New repository**. Nom : `cv-express`, visibilité **Public** (obligatoire pour GitHub Pages gratuit). Créer.
2. Dans le dépôt : **Add file → Upload files**, déposer `index.html` et `README.md`, puis **Commit changes**.
3. **Settings → Pages**. Dans « Source », choisir **Deploy from a branch**, branche `main`, dossier `/ (root)`, puis **Save**.
4. Une minute plus tard, le site est en ligne à l'adresse `https://<votre-pseudo>.github.io/cv-express/`.

Le code est public, mais il ne contient **aucune clé**. Sans clé, le site ne peut rien générer.

## La clé API (à faire par Maxence)

1. Sur **platform.claude.com**, aller dans **API keys** et créer **une clé par personne** (ex. « CV – Femme », « CV – Beau-père »). Chacune peut ainsi être révoquée séparément.
2. **Plafonner les dépenses**. L'API fonctionne avec des crédits prépayés : acheter un petit montant (10 $ par exemple) et **désactiver la recharge automatique**. On ne peut alors jamais dépenser plus que le crédit acheté. Un plafond mensuel peut aussi se régler dans la console.
3. Sur l'ordinateur ou le téléphone de chaque personne, ouvrir le site et coller la clé dans l'encadré « Première utilisation ». Elle reste enregistrée sur cet appareil uniquement.

**Coût indicatif** : 5 à 10 centimes par CV et lettre avec la qualité « Standard » (Claude Sonnet 5.5), un peu plus avec « Maximale ». Le coût cumulé est visible dans **Réglages**.

## Limites connues

- **LinkedIn et Indeed** bloquent souvent la lecture automatique de leurs annonces. Dans ce cas, le site le signale et il suffit de coller le texte de l'annonce.
- **PDF scannés** : s'ils ne contiennent pas de texte, Claude les lit (cela coûte quelques centimes de plus).
- **Anciens fichiers Word (.doc)** : non lus. Il faut les réenregistrer en .docx ou en PDF.
- **Couleur de l'entreprise** : trouvée par recherche web. Si elle est fausse ou trop claire, choisir une autre pastille. Les couleurs trop pâles sont assombries automatiquement pour rester lisibles.
- **Changer d'appareil** : l'historique et le parcours ne suivent pas (ils sont stockés dans le navigateur).
- **Sécurité de la clé** : quelqu'un qui utilise le même navigateur peut la récupérer. C'est acceptable entre membres de la famille. En cas de doute, révoquer la clé dans la console et en créer une nouvelle.
