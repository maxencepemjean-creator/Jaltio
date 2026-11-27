#!/usr/bin/env python3
"""Fabrique les pages de conseils de jaltio.fr (dossier conseils/) et met à jour sitemap.xml.
Usage (depuis la racine du dépôt) : python3 outils/conseils.py, puis python3 outils/menu.py
Pour ajouter un article : ajouter un dictionnaire dans ARTICLES (slug, titre, description, date, intro, corps en HTML)."""
import html, json, pathlib, re
RACINE = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://jaltio.fr"

ARTICLES = [
{
"slug": "adapter-cv-offre",
"titre": "Adapter son CV à une offre d'emploi : la méthode en 5 étapes",
"court": "Adapter son CV à une offre",
"description": "Comment adapter votre CV à chaque annonce sans rien inventer : repérer ce que le recruteur cherche, reprendre ses mots, réécrire l'accroche, trier vos expériences.",
"date": "2026-11-15",
"intro": "Envoyer le même CV à toutes les annonces, c'est demander au recruteur de faire le tri à votre place. Il ne le fera pas : il lit vite, et souvent un logiciel a déjà comparé votre CV aux mots de l'annonce. Adapter son CV ne veut pas dire mentir. Cela veut dire mettre en avant, pour ce poste précis, ce que vous avez vraiment fait.",
"corps": """
<h2>1. Lire l'annonce comme un recruteur</h2>
<p>Avant de toucher à votre CV, soulignez dans l'annonce trois choses :</p>
<ul>
<li><b>Les missions</b> : ce que la personne fera chaque jour.</li>
<li><b>Les exigences obligatoires</b> : diplôme, permis, expérience minimale, horaires. Elles sont souvent introduites par « vous avez », « exigé », « indispensable ».</li>
<li><b>Le vocabulaire</b> : les mots exacts employés pour décrire le métier (« encaissement » plutôt que « caisse », « relation client » plutôt que « accueil »).</li>
</ul>
<p>Si une exigence obligatoire vous manque, mieux vaut le savoir maintenant : vous en parlerez dans la lettre ou vous choisirez une autre offre.</p>

<h2>2. Reprendre les mots de l'annonce, quand ils décrivent ce que vous avez fait</h2>
<p>Les logiciels de tri et les recruteurs cherchent les termes de leur annonce. Si vous avez fait la mission, nommez-la comme eux. Une ligne « Vente » devient, pour une annonce de vendeur en boulangerie : « Accueil et conseil des clients, encaissement, mise en rayon des produits frais ».</p>
<p>La règle est simple : vous changez les mots, jamais les faits.</p>

<h2>3. Réécrire le titre et l'accroche</h2>
<p>Le titre du CV doit correspondre au poste visé, pas à votre dernier poste. Sous le titre, deux ou trois lignes résument pourquoi vous êtes la bonne personne pour <i>ce</i> poste : votre expérience la plus proche, une compétence demandée par l'annonce, votre disponibilité si elle compte (horaires décalés, week-ends, permis).</p>

<h2>4. Trier et réordonner vos expériences</h2>
<ul>
<li>Dans chaque expérience, mettez en premier les missions qui correspondent à l'annonce.</li>
<li>Raccourcissez ce qui n'a pas de rapport avec le poste, sans effacer l'expérience : un trou dans un CV pose plus de questions qu'une ligne courte.</li>
<li>Ajoutez des chiffres seulement s'ils sont vrais et vérifiables : nombre de clients par jour, taille de l'équipe, chiffre d'affaires du rayon.</li>
<li>Remontez une compétence demandée (logiciel, langue, permis) si elle était cachée en bas de page.</li>
</ul>

<h2>5. Vérifier avant d'envoyer</h2>
<ul>
<li>Une page, sauf si vous avez une longue carrière dans le même domaine.</li>
<li>Rien d'inventé : tout ce qui est écrit doit pouvoir être raconté en entretien.</li>
<li>Coordonnées à jour, nom de fichier clair (« CV Prénom Nom - Vendeur.pdf »).</li>
<li>Une relecture à voix haute pour attraper les fautes.</li>
</ul>

<h2>Ce qu'il ne faut pas faire</h2>
<ul>
<li>Copier l'annonce entière dans votre CV : le recruteur le voit tout de suite.</li>
<li>Cacher des mots-clés en blanc sur blanc : le texte extrait par les logiciels est lu par un humain, et l'astuce se retourne contre vous.</li>
<li>Ajouter une expérience ou un diplôme que vous n'avez pas : c'est vérifiable, et c'est un motif de rupture de la période d'essai.</li>
</ul>
"""},
{
"slug": "cv-logiciel-recrutement-ats",
"titre": "CV et logiciels de recrutement (ATS) : ce qu'ils lisent vraiment",
"court": "CV et logiciels de recrutement",
"description": "Ce que fait un logiciel de recrutement (ATS) avec votre CV, les règles de mise en page qui évitent qu'il soit mal lu, et les idées reçues à oublier.",
"date": "2026-11-15",
"intro": "Quand vous postulez en ligne, votre CV arrive souvent d'abord dans un logiciel de suivi des candidatures, qu'on appelle ATS (applicant tracking system). Ce logiciel ne « rejette » pas votre CV par magie : il en extrait le texte, le range dans des cases et permet au recruteur de chercher et de trier les candidats. Si le texte est mal extrait, vous devenez invisible.",
"corps": """
<h2>Ce que fait le logiciel</h2>
<ul>
<li>Il <b>extrait le texte</b> de votre fichier (PDF ou Word).</li>
<li>Il essaie de repérer vos <b>coordonnées, expériences, dates, diplômes et compétences</b>.</li>
<li>Le recruteur <b>cherche ensuite par mots-clés</b> (un métier, un logiciel, un permis) et trie la liste. La décision finale reste humaine.</li>
</ul>
<p>Votre objectif est donc double : que le texte soit lu correctement, et que les mots que le recruteur va chercher soient présents, s'ils correspondent à votre parcours.</p>

<h2>Les règles de mise en page qui évitent les mauvaises surprises</h2>
<ul>
<li><b>Du vrai texte</b> : pas de CV scanné ni de CV entièrement en image. Test simple : ouvrez votre PDF, essayez de sélectionner une ligne. Si vous ne pouvez pas, le logiciel non plus.</li>
<li><b>Des titres de sections classiques</b> : « Expérience professionnelle », « Formation », « Compétences », « Langues ». Les titres originaux (« Mon aventure ») sont mal reconnus.</li>
<li><b>Des dates claires</b> : « 03/2021 – 06/2024 » ou « 2021 – 2024 », au même format partout.</li>
<li><b>Rien d'important dans l'en-tête ou le pied de page</b> du traitement de texte, ni dans des zones de texte flottantes : certains logiciels les ignorent.</li>
<li><b>Une police courante</b> et des puces simples. Les icônes peuvent rester, à condition que l'information soit aussi écrite en texte (le numéro à côté de l'icône de téléphone, pas seulement l'icône).</li>
<li><b>Le format demandé</b> : si l'annonce demande un fichier Word, envoyez un fichier Word. Sinon, un PDF généré depuis votre traitement de texte (pas une photo) convient.</li>
</ul>

<h2>Les idées reçues à oublier</h2>
<ul>
<li><b>« Un CV en couleur est rejeté »</b> : non. La couleur ne gêne pas l'extraction du texte. C'est le texte en image qui pose problème.</li>
<li><b>« Il faut mettre un maximum de mots-clés »</b> : un CV rempli de mots sans phrases est lu ensuite par un humain, qui le trouve vide. Les mots-clés doivent décrire ce que vous avez réellement fait.</li>
<li><b>« Le logiciel décide seul »</b> : il trie et facilite la recherche ; c'est une personne qui choisit qui appeler.</li>
</ul>

<h2>Vérification en deux minutes</h2>
<ol>
<li>Ouvrez votre PDF, sélectionnez tout (Ctrl + A ou Cmd + A), copiez, collez dans un bloc-notes.</li>
<li>Si le texte collé est dans le bon ordre et complet (nom, coordonnées, postes, dates), le logiciel le lira aussi.</li>
<li>Comparez avec l'annonce : les compétences demandées que vous avez vraiment figurent-elles dans le texte ?</li>
</ol>
"""},
{
"slug": "relancer-apres-candidature",
"titre": "Relancer après une candidature : quand et comment (modèle de mail)",
"court": "Relancer après une candidature",
"description": "Quand relancer un recruteur après une candidature ou un entretien, quoi écrire, combien de fois : la méthode et des modèles de mail à adapter.",
"date": "2026-11-15",
"intro": "Une candidature sans réponse n'est pas forcément un refus : le recruteur a peut-être beaucoup de dossiers, ou le poste a été mis en pause. Une relance courte et polie vous remet en haut de la pile. Elle ne coûte rien, et elle montre que le poste vous intéresse vraiment.",
"corps": """
<h2>Quand relancer</h2>
<ul>
<li><b>Après une candidature</b> : environ une semaine après l'envoi, si vous n'avez pas de nouvelles. Si l'annonce indique une date limite, attendez quelques jours après cette date.</li>
<li><b>Après un entretien</b> : envoyez un mail de remerciement dans la journée ou le lendemain. Relancez seulement si le délai annoncé par le recruteur est dépassé.</li>
<li><b>Combien de fois</b> : une relance, éventuellement une seconde une semaine plus tard. Au-delà, consacrez votre énergie à d'autres candidatures.</li>
</ul>

<h2>Comment relancer</h2>
<ul>
<li><b>Répondez au mail de votre candidature</b> plutôt que d'en écrire un nouveau : le recruteur retrouve votre dossier d'un coup d'œil.</li>
<li><b>Rappelez le poste et la date</b> de votre candidature.</li>
<li><b>Ajoutez une phrase utile</b> : votre disponibilité, un élément nouveau, une précision sur votre motivation. Pas de reproche sur l'absence de réponse.</li>
<li><b>Terminez par une question simple</b> : « Ma candidature est-elle toujours à l'étude ? »</li>
</ul>

<h2>Modèle : relance après une candidature</h2>
<div class="modele"><p><b>Objet :</b> Candidature au poste de [poste] – [Prénom Nom]</p>
<p>Madame, Monsieur,</p>
<p>Je me permets de revenir vers vous au sujet de ma candidature au poste de [poste], envoyée le [date]. Ce poste m'intéresse toujours beaucoup, notamment [une raison précise : la mission, l'équipe, le produit].</p>
<p>Je suis disponible [à partir de quand / pour un échange téléphonique cette semaine]. Ma candidature est-elle toujours à l'étude ?</p>
<p>Je vous remercie par avance de votre retour.<br>Bien cordialement,<br>[Prénom Nom] – [téléphone]</p></div>

<h2>Modèle : remerciement après un entretien</h2>
<div class="modele"><p><b>Objet :</b> Merci pour notre entretien – [poste]</p>
<p>Bonjour [Madame / Monsieur Nom],</p>
<p>Merci pour notre échange [d'aujourd'hui / d'hier] au sujet du poste de [poste]. [Une phrase sur un point de l'entretien qui vous a marqué.] Cela m'a conforté dans mon envie de rejoindre votre équipe.</p>
<p>Je reste à votre disposition pour toute information complémentaire.<br>Bien cordialement,<br>[Prénom Nom]</p></div>

<h2>Et par téléphone ?</h2>
<p>Pour les petites entreprises, les commerces et les postes où le contact compte (vente, accueil, artisanat), un appel court fonctionne souvent mieux qu'un mail. Préparez deux phrases : qui vous êtes, pour quel poste, et la question « Où en est le recrutement ? ».</p>

<h2>Ne perdez pas le fil</h2>
<p>Notez pour chaque candidature la date d'envoi, la personne à contacter et la date de relance prévue. Sans suivi, on relance trop tôt, trop tard, ou jamais.</p>
"""},
{
"slug": "lettre-de-motivation-structure",
"titre": "Lettre de motivation : la structure simple en 3 paragraphes",
"court": "Structure de la lettre de motivation",
"description": "Une lettre de motivation courte et précise : la structure vous, moi, nous, ce qu'il faut mettre dans chaque paragraphe, les phrases à éviter et un exemple.",
"date": "2026-11-15",
"intro": "Une bonne lettre de motivation est courte, précise et écrite pour une seule entreprise. Le recruteur doit comprendre en quelques secondes pourquoi vous, pour ce poste, chez eux. La structure la plus utilisée tient en trois paragraphes : vous, moi, nous.",
"corps": """
<h2>1. Vous : ce que vous savez de l'entreprise et du poste</h2>
<p>Montrez que vous avez lu l'annonce et regardé qui recrute. Une ou deux phrases suffisent : ce que fait l'entreprise, ce qui vous attire dans ce poste précis. Évitez les généralités qui marcheraient pour n'importe quelle entreprise (« leader dans son domaine », « entreprise dynamique »).</p>

<h2>2. Moi : ce que vous apportez</h2>
<p>Reprenez deux ou trois exigences de l'annonce et montrez, avec un exemple concret de votre parcours, que vous y répondez. Un exemple vaut mieux qu'une liste de qualités : « J'ai tenu seul la caisse le samedi pendant deux ans » dit plus que « je suis autonome et rigoureux ».</p>

<h2>3. Nous : la suite</h2>
<p>Une phrase sur ce que vous voulez construire ensemble, votre disponibilité, et la demande d'un entretien. Restez simple et direct.</p>

<h2>La longueur</h2>
<p>Moins d'une page, idéalement une dizaine de lignes par paragraphe au maximum. Si votre lettre est envoyée dans le corps d'un mail ou dans un champ « message » d'un site d'emploi, raccourcissez encore : l'essentiel des paragraphes 2 et 3.</p>

<h2>Les phrases à éviter</h2>
<ul>
<li>« Suite à votre annonce parue sur… » en ouverture : le recruteur le sait déjà, commencez par l'entreprise.</li>
<li>« Je me permets de vous adresser ma candidature » : remplissage.</li>
<li>Les qualités sans preuve : « dynamique, motivé, rigoureux ».</li>
<li>Répéter le CV ligne par ligne : la lettre explique, le CV liste.</li>
</ul>

<h2>Exemple (personne fictive)</h2>
<div class="modele"><p>Madame, Monsieur,</p>
<p>La Boulangerie du Marché est connue à Saintes pour ses pains au levain et son accueil le samedi matin, quand la file déborde sur le trottoir. Votre recherche d'un vendeur pour renforcer l'équipe du week-end correspond exactement à ce que je sais faire.</p>
<p>Pendant deux ans, j'ai tenu la caisse et le comptoir d'une supérette de quartier, seul le samedi, de l'ouverture à 13 h. J'y ai appris à servir vite sans bâcler le conseil, à gérer les produits frais et leurs dates, et à garder le sourire quand la file s'allonge.</p>
<p>Disponible dès maintenant, y compris le dimanche matin, je serais heureux d'échanger avec vous lors d'un entretien.</p>
<p>Bien cordialement,<br>Benjamin Martin</p></div>

<h2>Et pour une candidature spontanée ?</h2>
<p>Même structure, mais le premier paragraphe compte encore plus : expliquez pourquoi cette entreprise, et quel type de poste vous visez. Sans annonce, c'est à vous de dire en quoi vous pouvez être utile.</p>
"""},
{
"slug": "preparer-entretien-embauche",
"titre": "Préparer un entretien d'embauche : les questions classiques et comment y répondre",
"court": "Préparer un entretien d'embauche",
"description": "Comment préparer un entretien d'embauche : ce qu'il faut relire, la méthode pour raconter une expérience, les questions classiques (présentez-vous, défauts, salaire) et les questions à poser.",
"date": "2026-11-15",
"intro": "Un entretien se prépare comme un examen dont on connaît une bonne partie des questions. Les recruteurs posent presque toujours les mêmes, avec des variantes. Ce qui fait la différence, ce sont des réponses concrètes, appuyées sur des exemples tirés de votre parcours.",
"corps": """
<h2>Avant l'entretien</h2>
<ul>
<li><b>Relisez l'annonce et le CV que vous avez envoyé</b> : le recruteur les a sous les yeux.</li>
<li><b>Renseignez-vous sur l'entreprise</b> : ce qu'elle fait, ses clients, ses actualités récentes, son site et ses avis.</li>
<li><b>Préparez trois exemples concrets</b> de situations où vous avez réussi quelque chose en lien avec le poste.</li>
<li><b>Préparez deux ou trois questions</b> à poser.</li>
<li><b>La logistique</b> : adresse et temps de trajet, ou pour une visio, le lien, le micro et la caméra testés la veille.</li>
</ul>

<h2>La méthode pour raconter un exemple</h2>
<p>Pour chaque exemple, déroulez quatre temps, en une minute environ :</p>
<ol>
<li><b>La situation</b> : où, quand, le contexte.</li>
<li><b>Ce qu'on attendait de vous.</b></li>
<li><b>Ce que vous avez fait</b>, vous personnellement.</li>
<li><b>Le résultat</b>, chiffré si vous avez un chiffre vrai.</li>
</ol>

<h2>Les questions classiques</h2>
<h3>« Présentez-vous »</h3>
<p>Ce n'est pas votre biographie. En deux minutes : votre parcours en lien avec le poste, ce que vous savez faire, et pourquoi vous êtes là aujourd'hui. Finissez par le poste visé.</p>
<h3>« Pourquoi ce poste, pourquoi chez nous ? »</h3>
<p>Reliez une chose précise de l'entreprise (produit, clientèle, valeurs, proximité) à ce que vous cherchez. La réponse doit être impossible à recopier telle quelle pour une autre entreprise.</p>
<h3>« Quelles sont vos qualités et vos défauts ? »</h3>
<p>Pour les qualités, deux maximum, chacune avec un exemple. Pour le défaut, choisissez un vrai défaut qui ne bloque pas le poste, et dites ce que vous faites pour le corriger.</p>
<h3>« Pourquoi avez-vous quitté votre dernier poste ? »</h3>
<p>Restez factuel et tourné vers l'avenir. Ne critiquez jamais un ancien employeur.</p>
<h3>« Quelles sont vos prétentions salariales ? »</h3>
<p>Renseignez-vous avant : salaires affichés dans des annonces comparables, grille de la convention collective du secteur. Donnez une fourchette réaliste, en brut annuel ou mensuel selon l'usage du métier.</p>
<h3>« Avez-vous des questions ? »</h3>
<p>Répondez toujours oui. Par exemple : « À quoi ressemble une journée type ? », « Comment l'équipe est-elle organisée ? », « Quelles sont les prochaines étapes du recrutement ? ».</p>

<h2>Après l'entretien</h2>
<ul>
<li>Notez tout de suite ce qui s'est dit, les noms et les prochaines étapes.</li>
<li>Envoyez un court mail de remerciement dans la journée ou le lendemain.</li>
<li>Si le délai annoncé est dépassé, relancez une fois, poliment.</li>
</ul>
"""},
{
"slug": "cv-sans-experience",
"titre": "CV sans expérience : comment faire son premier CV (étudiant, premier emploi)",
"court": "CV sans expérience",
"description": "Étudiant, jeune diplômé, premier emploi : quoi mettre sur un CV sans expérience, dans quel ordre, et comment valoriser stages, jobs, projets et bénévolat.",
"date": "2026-11-17",
"intro": "Faire un CV quand on n'a jamais vraiment travaillé donne l'impression de partir d'une page blanche. En réalité, presque tout le monde a quelque chose à montrer : un stage, un job d'été, un projet d'école, du bénévolat, une responsabilité dans un club. Pour un premier emploi, le recruteur ne s'attend pas à une longue carrière. Il cherche des preuves que vous savez apprendre, tenir vos engagements et faire le travail demandé.",
"corps": """
<h2>Ce que le recruteur cherche sur un premier CV</h2>
<p>Face à un candidat sans expérience, le recruteur ne compare pas des années de métier. Il se pose des questions plus simples :</p>
<ul>
<li><b>Cette personne comprend-elle le poste ?</b> Votre titre et votre accroche doivent viser l'annonce, pas « tout type d'emploi ».</li>
<li><b>Est-elle fiable ?</b> Un job tenu tout un été, un engagement associatif sur plusieurs années, un stage mené jusqu'au bout le montrent.</li>
<li><b>A-t-elle les bases demandées ?</b> Le diplôme, le permis, une langue, un logiciel, la disponibilité.</li>
<li><b>Peut-elle apprendre vite ?</b> Les projets, les formations suivies seul et les responsabilités prises en disent beaucoup.</li>
</ul>

<h2>Tout ce qui compte comme expérience</h2>
<p>« Expérience » ne veut pas dire « CDI ». Faites la liste de tout ce que vous avez fait, puis gardez ce qui a un lien avec le poste visé :</p>
<ul>
<li><b>Les stages</b>, y compris les stages d'observation, s'ils sont en rapport avec le métier.</li>
<li><b>L'alternance et l'apprentissage</b> : c'est une vraie expérience professionnelle, présentez-la comme telle.</li>
<li><b>Les jobs étudiants et saisonniers</b> : vendanges, restauration rapide, animation, caisse, cueillette, inventaires.</li>
<li><b>Les petits boulots réguliers</b> : garde d'enfants, soutien scolaire, aide aux devoirs, petits travaux.</li>
<li><b>Le bénévolat et la vie associative</b> : distribution alimentaire, encadrement d'enfants dans un club, organisation d'un tournoi ou d'une fête.</li>
<li><b>Les projets d'école</b> : un projet de groupe, un mémoire, une étude de cas, une création, surtout s'il y avait un vrai résultat.</li>
<li><b>Les projets personnels</b> : un site, une chaîne vidéo, un objet fabriqué, une petite vente en ligne.</li>
</ul>
<p>Une seule règle : tout ce qui est écrit doit être vrai et pouvoir être raconté en entretien.</p>

<h2>Dans quel ordre mettre les rubriques</h2>
<p>Quand l'expérience est mince, c'est souvent la formation qui porte le CV. Un ordre qui fonctionne bien :</p>
<ol>
<li><b>Nom, coordonnées</b> (téléphone, adresse mail sérieuse, ville).</li>
<li><b>Titre</b> : le poste visé, par exemple « Employé polyvalent en restauration » ou « Assistant commercial – premier emploi ».</li>
<li><b>Accroche</b> : deux ou trois lignes (voir plus bas).</li>
<li><b>Formation</b> : en haut si votre diplôme est récent ou en lien direct avec le poste. Indiquez l'établissement, l'année, et une ou deux matières ou projets utiles pour le poste.</li>
<li><b>Expériences</b> : stages, jobs, bénévolat, du plus récent au plus ancien. Vous pouvez séparer « Expériences professionnelles » et « Engagements » si cela rend la lecture plus claire.</li>
<li><b>Compétences</b> : logiciels, langues avec un niveau honnête, permis, certifications.</li>
<li><b>Centres d'intérêt</b> : seulement s'ils disent quelque chose d'utile (un sport d'équipe pratiqué en club, un rôle d'encadrement, une passion liée au métier).</li>
</ol>
<p>Gardez des titres de rubriques classiques : ils sont mieux lus par les logiciels de recrutement (voir <a href="/conseils/cv-logiciel-recrutement-ats/">CV et logiciels de recrutement</a>).</p>

<h2>Décrire une petite expérience comme une vraie</h2>
<p>Un job d'été mérite autant de soin qu'un poste en entreprise. Pour chaque ligne :</p>
<ul>
<li><b>Commencez par un verbe d'action</b> : accueillir, préparer, encaisser, organiser, encadrer, ranger, conseiller.</li>
<li><b>Décrivez des missions précises</b> plutôt qu'un intitulé vague.</li>
<li><b>Ajoutez un repère concret s'il est vrai</b> : la durée, la taille de l'équipe, le nombre d'enfants encadrés, les horaires.</li>
<li><b>Reprenez les mots de l'annonce</b> quand ils décrivent ce que vous avez réellement fait.</li>
</ul>
<div class="modele"><p><b>Avant :</b> Job d'été – Camping – Juillet-août 2025</p>
<p><b>Après :</b> Agent d'accueil saisonnier – Camping (exemple fictif) – Juillet-août 2025<br>
– Accueil des vacanciers en français et en anglais, remise des clés et explication des services<br>
– Encaissement des séjours et tenue de la caisse en fin de journée<br>
– Réponse au téléphone et aux mails de réservation</p></div>

<h2>Écrire l'accroche quand on débute</h2>
<p>L'accroche remplace le « résumé de carrière » que vous n'avez pas encore. Elle dit en deux ou trois lignes : ce que vous êtes aujourd'hui, ce que vous apportez au poste, et ce que vous cherchez. Évitez les qualités sans preuve (« dynamique et motivé ») et visez un poste précis.</p>
<div class="modele"><p>Titulaire d'un BTS Management commercial opérationnel obtenu en 2026, avec deux stages en magasin et un job d'été en caisse. À l'aise avec l'encaissement, la mise en rayon et le conseil client. Disponible immédiatement, y compris le week-end, pour un premier poste de vendeur en grande surface spécialisée.</p></div>
<p>Changez cette accroche à chaque candidature : elle doit répondre à l'annonce que vous avez sous les yeux. La méthode complète est dans <a href="/conseils/adapter-cv-offre/">Adapter son CV à une offre d'emploi</a>.</p>

<h2>Exemple de CV sans expérience (personne fictive)</h2>
<div class="modele"><p><b>Léa Dubois</b> – Poitiers – 06 00 00 00 00 – lea.dubois@exemple.fr</p>
<p><b>Assistante administrative – premier emploi</b></p>
<p>Diplômée d'un bac pro Assistance à la gestion des organisations et de leurs activités, avec deux stages en entreprise. Rigoureuse sur le classement et la saisie, à l'aise avec le tableur et le traitement de texte. Disponible dès maintenant pour un poste à temps plein.</p>
<p><b>Formation</b><br>2026 – Bac pro AGORA – Lycée professionnel (exemple fictif), Poitiers</p>
<p><b>Expériences</b><br>
2026 – Stage de 6 semaines – Agence immobilière (exemple fictif)<br>
– Accueil téléphonique, prise de rendez-vous, classement des dossiers clients<br>
2025 – Stage de 4 semaines – Mairie (exemple fictif)<br>
– Saisie de courriers, mise à jour d'un tableau de suivi, accueil du public<br>
Depuis 2024 – Bénévole – Club de handball (exemple fictif)<br>
– Tenue de la table de marque les jours de match, aide à l'organisation du tournoi annuel</p>
<p><b>Compétences</b><br>Tableur et traitement de texte · Classement et archivage · Accueil physique et téléphonique · Anglais : niveau scolaire · Permis B</p></div>

<h2>Les erreurs à éviter</h2>
<ul>
<li><b>Gonfler ou inventer</b> une expérience : c'est vérifiable, et une seule question en entretien suffit à le voir.</li>
<li><b>Remplir avec des barres de niveau</b> (« Excel : 4 étoiles sur 5 ») : elles ne veulent rien dire pour le recruteur. Décrivez plutôt ce que vous savez faire.</li>
<li><b>Écrire « débutant » ou « sans expérience » en titre</b> : présentez le poste visé, pas ce qui vous manque.</li>
<li><b>Étaler sur deux pages</b> : un premier CV tient sur une page.</li>
<li><b>Oublier la relecture</b> : une faute se remarque encore plus sur un CV court. Faites relire par quelqu'un d'autre.</li>
<li><b>Garder une adresse mail fantaisiste</b> : créez une adresse simple avec votre prénom et votre nom.</li>
</ul>
"""},
{
"slug": "trou-dans-le-cv",
"titre": "Trou dans le CV : comment présenter et expliquer une période sans emploi",
"court": "Trou dans le CV",
"description": "Chômage, santé, enfants, voyage, reconversion : comment présenter une période sans emploi sur votre CV et l'expliquer sereinement en entretien, avec exemples.",
"date": "2026-11-20",
"intro": "Une période sans emploi sur un CV inquiète souvent plus le candidat que le recruteur. Ce qui gêne un recruteur, ce n'est pas le trou lui-même, c'est de ne pas comprendre ce qui s'est passé. Une ligne honnête sur le CV et une réponse courte et préparée pour l'entretien suffisent dans la plupart des cas. Voici comment faire, quelle que soit la raison.",
"corps": """
<h2>Ce qui inquiète vraiment le recruteur</h2>
<p>Devant un CV avec une interruption, le recruteur se pose surtout trois questions :</p>
<ul>
<li><b>Que s'est-il passé ?</b> Un trou sans explication laisse la place à toutes les suppositions, souvent pires que la réalité.</li>
<li><b>La personne est-elle disponible maintenant ?</b> Il veut savoir si la situation qui a causé la pause est derrière vous.</li>
<li><b>Ses compétences sont-elles à jour ?</b> Surtout dans les métiers où les outils changent vite.</li>
</ul>
<p>Votre objectif est donc simple : répondre à ces trois questions avant qu'il ne les pose, sans vous justifier à l'excès.</p>

<h2>Faut-il le faire apparaître sur le CV ?</h2>
<p>Pour une courte interruption entre deux postes, rien n'oblige à ajouter une ligne : indiquer les années plutôt que les mois (« 2022 – 2024 ») est une présentation courante. Pour une période plus longue, mieux vaut la nommer que la cacher.</p>
<ul>
<li><b>Ne trafiquez pas les dates</b> : les dates d'un poste se vérifient facilement (certificat de travail, appel à un ancien employeur), et une incohérence découverte coûte plus cher qu'un trou expliqué.</li>
<li><b>Gardez le même format de dates partout</b> : passer des mois aux années uniquement autour du trou se remarque.</li>
<li><b>Ajoutez une ligne courte et neutre</b> dans vos expériences, au bon endroit chronologique, si la période est longue ou si vous y avez fait quelque chose d'utile.</li>
</ul>
<div class="modele"><p>2024 – 2025 – Congé parental<br>
2023 – Recherche d'emploi et formation en ligne à la comptabilité (exemple fictif)<br>
2022 – 2023 – Projet personnel : voyage de huit mois en Amérique du Sud, pratique quotidienne de l'espagnol</p></div>

<h2>Quoi écrire selon la raison</h2>
<h3>Recherche d'emploi après un licenciement ou une fin de contrat</h3>
<p>C'est la situation la plus fréquente et la plus facile à comprendre. Mettez en avant ce que vous avez fait pendant cette période : une formation, une certification, des missions courtes, du bénévolat. Si vous n'avez rien de particulier à ajouter, une ligne « Recherche d'emploi » suffit.</p>
<h3>Raisons de santé</h3>
<p>Vous pouvez écrire simplement « Pause pour raisons personnelles » ou « Interruption pour raisons de santé ». Inutile d'entrer dans les détails médicaux, sur le CV comme en entretien. L'important est de pouvoir dire que vous êtes aujourd'hui disponible pour le poste.</p>
<h3>Enfants ou proche à accompagner</h3>
<p>« Congé parental » ou « Accompagnement d'un proche » sont des intitulés clairs et respectés. Si vous avez gardé un pied dans le métier (lectures, formation, activité associative), ajoutez-le en une ligne.</p>
<h3>Voyage, année sabbatique</h3>
<p>Présentez-le comme un projet, avec ce qu'il vous a apporté de concret pour le poste : une langue pratiquée, de l'autonomie, une organisation logistique, un travail sur place. Restez sobre : une ligne, pas un carnet de voyage.</p>
<h3>Reconversion ou formation</h3>
<p>Ce n'est pas un trou, c'est une étape. Placez la formation dans la rubrique « Formation » avec son intitulé exact et l'organisme, et reliez-la au poste visé dans votre accroche.</p>
<h3>Création d'entreprise ou activité indépendante</h3>
<p>Même si le projet s'est arrêté, c'est une expérience à part entière. Décrivez-la comme un poste : votre rôle, vos missions, ce que vous avez appris (prospection, gestion, relation client).</p>

<h2>Remplir la période avec ce que vous avez vraiment fait</h2>
<p>Beaucoup de personnes ont fait plus qu'elles ne le pensent pendant une pause. Faites la liste, puis gardez ce qui sert le poste visé :</p>
<ul>
<li><b>Formations</b> : en ligne, en centre, certifiantes ou non, y compris celles suivies seul.</li>
<li><b>Missions courtes</b> : intérim, CDD, extras, dépannage chez un ancien employeur.</li>
<li><b>Bénévolat</b> : trésorerie d'une association, encadrement, organisation d'événements.</li>
<li><b>Projets personnels</b> : un site créé, des travaux menés, une petite activité de vente.</li>
<li><b>Langues et outils</b> : un logiciel appris, un niveau de langue progressé.</li>
</ul>
<p>Une seule règle : tout ce qui est écrit doit être vrai et pouvoir être raconté en entretien.</p>

<h2>Préparer la réponse pour l'entretien</h2>
<p>Si la question vient, elle sera du type « Que s'est-il passé entre 2023 et 2024 ? ». Préparez une réponse de trois phrases, dans cet ordre :</p>
<ol>
<li><b>Le fait</b>, dit simplement et sans vous excuser.</li>
<li><b>Ce que vous en avez retiré</b> ou ce que vous avez fait pendant cette période.</li>
<li><b>Le retour au présent</b> : pourquoi vous êtes prêt aujourd'hui et pourquoi ce poste.</li>
</ol>
<div class="modele"><p><b>Exemple (personne fictive) :</b> « Après la fermeture du magasin où je travaillais, j'ai pris le temps de chercher un poste qui me corresponde vraiment. J'en ai profité pour suivre une formation à la gestion des stocks et j'ai fait plusieurs missions d'intérim en logistique. Aujourd'hui, je cherche un poste stable de préparateur de commandes, et votre entrepôt correspond exactement à ce que je veux faire. »</p></div>
<p>Dites-la à voix haute plusieurs fois avant l'entretien : une réponse fluide montre que le sujet est réglé pour vous. Pour les autres questions classiques, voir <a href="/conseils/preparer-entretien-embauche/">Préparer un entretien d'embauche</a>.</p>

<h2>Les erreurs à éviter</h2>
<ul>
<li><b>Inventer un poste ou allonger un contrat</b> pour boucher le trou : c'est vérifiable, et la confiance ne se rattrape pas.</li>
<li><b>Se justifier longuement</b> : plus l'explication est longue, plus elle attire l'attention.</li>
<li><b>Critiquer un ancien employeur</b> pour expliquer un départ, même si la situation était difficile.</li>
<li><b>Laisser un trou de plusieurs années sans un mot</b> : le recruteur imagine le pire, ou passe au CV suivant.</li>
<li><b>Utiliser le même CV pour toutes les offres</b> : selon le poste, ce que vous avez fait pendant la pause n'aura pas le même poids. Adaptez la ligne et l'accroche à chaque annonce (voir <a href="/conseils/adapter-cv-offre/">Adapter son CV à une offre d'emploi</a>).</li>
</ul>
"""},
{
"slug": "cv-reconversion-professionnelle",
"titre": "CV de reconversion professionnelle : comment l'adapter à votre nouveau métier",
"court": "CV de reconversion",
"description": "Reconversion professionnelle : comment construire un CV tourné vers votre nouveau métier, valoriser vos compétences transférables et présenter votre formation.",
"date": "2026-11-24",
"intro": "Changer de métier oblige à revoir son CV en profondeur. Un CV classique raconte un parcours dans l'ordre ; un CV de reconversion doit d'abord montrer où vous allez, puis prouver que votre passé vous y prépare. Le recruteur ne cherche pas quelqu'un qui a déjà tout fait dans le nouveau métier. Il veut comprendre votre projet, vérifier que vous avez les bases et voir ce que votre expérience passée apporte en plus.",
"corps": """
<h2>Ce que le recruteur se demande devant un CV de reconversion</h2>
<p>Face à un parcours qui change de direction, le recruteur se pose surtout quatre questions :</p>
<ul>
<li><b>Le projet est-il sérieux ?</b> Une formation suivie, un stage, des démarches concrètes montrent que ce n'est pas un coup de tête.</li>
<li><b>La personne a-t-elle les bases du nouveau métier ?</b> Un diplôme, une certification, des outils maîtrisés, une première pratique.</li>
<li><b>Qu'apporte son ancien métier ?</b> Souvent, c'est là que se trouve votre vraie différence avec un jeune diplômé.</li>
<li><b>Sait-elle ce qui l'attend ?</b> Les conditions du poste, le niveau de départ, parfois le salaire.</li>
</ul>
<p>Votre CV doit répondre à ces questions dès la première lecture, sans attendre la lettre ou l'entretien.</p>

<h2>Mettre le nouveau métier en haut du CV</h2>
<p>Le titre du CV, c'est le poste que vous visez, pas celui que vous quittez. « Comptable en reconversion vers le développement web » attire l'œil sur le passé ; « Développeuse web junior » dit clairement ce que vous cherchez.</p>
<p>Juste en dessous, l'accroche fait le lien entre les deux mondes en deux ou trois lignes :</p>
<ul>
<li>le nouveau métier visé ;</li>
<li>la formation ou la pratique qui vous y prépare ;</li>
<li>ce que votre ancien métier vous apporte pour ce poste ;</li>
<li>votre disponibilité, si elle compte.</li>
</ul>
<div class="modele"><p><b>Exemple d'accroche (personne fictive) :</b> Aide-soignante pendant huit ans, je me forme au métier de secrétaire médicale (formation en cours, fin prévue en juin). Habituée à l'accueil des patients, à la confidentialité et au vocabulaire médical, je recherche un premier poste de secrétaire médicale en cabinet ou en clinique.</p></div>

<h2>Choisir le bon ordre des rubriques</h2>
<p>Dans une reconversion, l'ordre chronologique strict met en avant ce qui intéresse le moins le recruteur. Un ordre qui fonctionne mieux :</p>
<ol>
<li><b>Titre et accroche</b> tournés vers le nouveau métier.</li>
<li><b>Compétences</b> liées au poste visé, regroupées par thème (voir plus bas).</li>
<li><b>Formation</b> : la formation de reconversion en premier, avec son intitulé exact, l'organisme, les dates et, si c'est le cas, le stage ou le projet de fin de formation.</li>
<li><b>Expériences en lien avec le nouveau métier</b> : stage, missions, bénévolat, projets.</li>
<li><b>Parcours précédent</b> : vos anciens postes, résumés et réécrits sous l'angle du poste visé.</li>
</ol>
<p>Gardez des intitulés de rubriques classiques (« Compétences », « Formation », « Expérience professionnelle ») : les logiciels de recrutement les reconnaissent mieux (voir <a href="/conseils/cv-logiciel-recrutement-ats/">CV et logiciels de recrutement</a>).</p>

<h2>Repérer vos compétences transférables</h2>
<p>Une compétence transférable, c'est quelque chose que vous savez faire dans votre ancien métier et qui sert aussi dans le nouveau. Pour les trouver :</p>
<ol>
<li>Prenez trois ou quatre annonces du métier visé et soulignez les missions et compétences demandées.</li>
<li>Pour chacune, cherchez une situation réelle de votre parcours où vous l'avez déjà pratiquée, même dans un autre contexte.</li>
<li>Gardez seulement celles que vous pouvez raconter avec un exemple précis en entretien.</li>
</ol>
<p>Quelques exemples de passerelles fréquentes :</p>
<ul>
<li><b>Vente ou commerce</b> : relation client, négociation, gestion des réclamations, objectifs à atteindre.</li>
<li><b>Restauration ou hôtellerie</b> : travail sous pression, organisation d'un service, gestion des stocks, accueil.</li>
<li><b>Soin et accompagnement</b> : écoute, confidentialité, rigueur dans les protocoles, travail en équipe.</li>
<li><b>Bâtiment ou industrie</b> : lecture de plans, respect des consignes de sécurité, contrôle qualité, maintenance.</li>
<li><b>Enseignement ou animation</b> : expliquer simplement, préparer un support, animer un groupe.</li>
</ul>
<p>Regroupez ensuite ces compétences par thème dans la rubrique « Compétences », plutôt qu'en une longue liste de qualités sans preuve.</p>

<h2>Réécrire vos anciens postes</h2>
<p>Vous ne cachez pas votre passé : vous le racontez autrement. Pour chaque ancien poste :</p>
<ul>
<li><b>Gardez l'intitulé réel</b>, l'entreprise et les dates : ce sont des faits vérifiables.</li>
<li><b>Mettez en premier les missions utiles</b> pour le nouveau métier.</li>
<li><b>Raccourcissez le reste</b> : une ou deux lignes suffisent pour ce qui n'a aucun rapport.</li>
<li><b>Reprenez le vocabulaire du nouveau métier</b>, quand il décrit vraiment ce que vous faisiez.</li>
</ul>
<div class="modele"><p><b>Avant :</b> Responsable de rayon – Supermarché (exemple fictif) – 2016 – 2025<br>
– Gestion du rayon fruits et légumes, commandes, mise en rayon, encadrement de l'équipe</p>
<p><b>Après, pour un poste d'assistant logistique :</b> Responsable de rayon – Supermarché (exemple fictif) – 2016 – 2025<br>
– Passage des commandes fournisseurs et suivi des livraisons<br>
– Gestion des stocks et des dates de péremption, inventaires mensuels<br>
– Organisation du planning d'une équipe de quatre personnes</p></div>
<p>Les faits n'ont pas changé ; seul l'angle a changé.</p>

<h2>Montrer que le projet est concret</h2>
<p>Ce qui rassure le plus un recruteur, ce sont les preuves que vous avez déjà mis un pied dans le nouveau métier. Indiquez sur le CV, si vous les avez :</p>
<ul>
<li><b>La formation</b> suivie ou en cours, avec la date de fin prévue.</li>
<li><b>Un stage</b> ou une période d'immersion en entreprise, décrite comme une vraie expérience.</li>
<li><b>Des projets réalisés</b> pendant la formation ou seul : un site, un dossier, une réalisation, avec un lien si c'est en ligne.</li>
<li><b>Du bénévolat</b> en lien avec le nouveau métier.</li>
<li><b>Des outils ou logiciels</b> du métier que vous savez utiliser.</li>
</ul>
<p>Pas besoin de raconter tout le cheminement sur le CV. Le « pourquoi » de votre reconversion se dit dans la lettre de motivation et en entretien, en quelques phrases positives et tournées vers le nouveau métier, sans critiquer l'ancien.</p>

<h2>Les erreurs à éviter</h2>
<ul>
<li><b>Garder l'ancien titre en haut du CV</b> : le recruteur vous classe dans votre ancien métier.</li>
<li><b>Effacer des années d'expérience</b> : un grand vide pose plus de questions qu'une ligne courte (voir <a href="/conseils/trou-dans-le-cv/">Trou dans le CV</a>).</li>
<li><b>Exagérer votre niveau</b> dans le nouveau métier : un test ou une question technique suffit à le voir.</li>
<li><b>Utiliser le même CV pour toutes les annonces</b> : les compétences transférables à mettre en avant changent d'un poste à l'autre. La méthode est dans <a href="/conseils/adapter-cv-offre/">Adapter son CV à une offre d'emploi</a>.</li>
<li><b>Dépasser une page</b> pour un premier poste dans le nouveau métier, sauf si l'annonce demande un parcours détaillé.</li>
</ul>
"""},
{
"slug": "candidature-spontanee",
"titre": "Candidature spontanée : à qui l'envoyer et comment la rédiger (modèle)",
"court": "Candidature spontanée",
"description": "Candidature spontanée : choisir les entreprises, trouver la bonne personne, écrire un mail court et un CV ciblé, relancer. Méthode et modèle de mail à adapter.",
"date": "2026-11-27",
"intro": "Toutes les offres ne sont pas publiées : beaucoup d'entreprises, surtout les petites, recrutent par le bouche-à-oreille ou parmi les candidatures qu'elles ont déjà reçues. Une candidature spontanée vous place dans cette pile avant même qu'une annonce existe. Elle demande un peu plus de travail qu'une réponse à une offre, car c'est à vous d'expliquer en quoi vous pouvez être utile. Bien ciblée, elle montre au recruteur que vous avez choisi son entreprise, et pas seulement une annonce.",
"corps": """
<h2>Choisir les entreprises à contacter</h2>
<p>Une candidature spontanée envoyée à cinquante entreprises au hasard donne rarement quelque chose. Mieux vaut une courte liste d'entreprises choisies, chacune avec une raison précise. Pour la construire :</p>
<ul>
<li><b>Partez du métier visé</b> : quelles entreprises emploient ce type de poste près de chez vous ou dans la zone où vous pouvez vous déplacer ?</li>
<li><b>Regardez autour de vous</b> : commerces, artisans, entreprises de la zone d'activité, fournisseurs ou clients de votre ancien employeur.</li>
<li><b>Repérez les signes de besoin</b> : ouverture d'un nouveau site, déménagement, nouveau produit, saison qui approche, annonces récentes pour des postes proches.</li>
<li><b>Consultez leur site et leur page sur les réseaux professionnels</b> : une rubrique « Nous rejoindre » ou « Carrières » indique souvent comment candidater.</li>
<li><b>Notez une raison par entreprise</b> : ce qui vous attire chez elle. Si vous n'en trouvez aucune, elle n'a probablement pas sa place sur la liste.</li>
</ul>

<h2>Trouver la bonne personne</h2>
<p>Une candidature adressée à une personne nommée a plus de chances d'être lue qu'un message envoyé à une adresse générale. Selon la taille de l'entreprise :</p>
<ul>
<li><b>Petite entreprise, commerce, artisan</b> : le gérant ou la gérante. Souvent, c'est la même personne qui recrute, encadre et décide.</li>
<li><b>Entreprise moyenne</b> : le responsable du service que vous visez (atelier, magasin, comptabilité, logistique), avec une copie au service des ressources humaines s'il existe.</li>
<li><b>Grande entreprise</b> : passez par la rubrique « Candidature spontanée » de son site carrières si elle existe ; sinon, cherchez le responsable du recrutement ou du service concerné.</li>
</ul>
<p>Pour trouver un nom : le site de l'entreprise (page « Équipe » ou « Qui sommes-nous »), les réseaux professionnels, ou tout simplement un appel à l'accueil : « Bonjour, je souhaiterais adresser une candidature pour un poste de [métier]. À quelle personne dois-je l'envoyer ? »</p>

<h2>Mail, site carrières ou dépôt en main propre ?</h2>
<ul>
<li><b>Par mail</b> : le plus courant. Le message tient lieu de lettre de motivation courte, avec le CV en pièce jointe.</li>
<li><b>Par le formulaire du site carrières</b> : à privilégier quand l'entreprise en propose un, car c'est là que le recruteur cherche.</li>
<li><b>En main propre</b> : efficace pour les commerces, la restauration, l'hôtellerie et l'artisanat. Venez à une heure calme (pas au moment du coup de feu), avec un CV imprimé, et demandez à parler au responsable.</li>
<li><b>Par téléphone</b> : utile pour obtenir un nom ou proposer de passer déposer votre CV. Préparez deux phrases : qui vous êtes et ce que vous cherchez.</li>
</ul>

<h2>Écrire un message court et ciblé</h2>
<p>Sans annonce, le recruteur ne sait pas pourquoi vous lui écrivez. Votre message doit le lui dire en quelques lignes :</p>
<ol>
<li><b>Pourquoi cette entreprise</b> : une chose précise que vous savez d'elle.</li>
<li><b>Quel poste vous visez</b> : un métier clair, pas « tout poste disponible ».</li>
<li><b>Ce que vous apportez</b> : une ou deux expériences concrètes en lien avec ce poste.</li>
<li><b>La suite</b> : votre disponibilité et une proposition simple (un échange, un passage sur place).</li>
</ol>
<p>Le mail doit rester lisible sans faire défiler l'écran. La structure détaillée est dans <a href="/conseils/lettre-de-motivation-structure/">Lettre de motivation : la structure en 3 paragraphes</a>.</p>

<h2>Modèle de mail de candidature spontanée</h2>
<div class="modele"><p><b>Objet :</b> Candidature spontanée – [poste visé] – [Prénom Nom]</p>
<p>Bonjour [Madame / Monsieur Nom],</p>
<p>[Une phrase sur l'entreprise : ce qu'elle fait, ce qui vous attire, une actualité récente.] C'est pourquoi je vous propose ma candidature pour un poste de [poste visé].</p>
<p>[Une ou deux phrases sur votre expérience la plus proche du poste, avec un exemple concret.]</p>
<p>Je suis disponible [à partir de quand / à temps plein, à temps partiel] et serais heureux de vous rencontrer, ou de passer vous déposer mon CV si vous le préférez. Vous le trouverez en pièce jointe.</p>
<p>Bien cordialement,<br>[Prénom Nom] – [téléphone]</p></div>
<div class="modele"><p><b>Exemple (personne fictive, entreprise fictive) :</b></p>
<p>Bonjour Madame Lefèvre,</p>
<p>J'ai vu que la Menuiserie des Deux Rives (exemple fictif) ouvrait un second atelier à Cognac. C'est pourquoi je vous propose ma candidature pour un poste d'agent de fabrication.</p>
<p>Pendant trois ans, j'ai travaillé sur une ligne de découpe et d'assemblage de meubles, avec la lecture des fiches de fabrication et le contrôle des pièces en fin de poste.</p>
<p>Je suis disponible dès le mois prochain, à temps plein, et serais heureux de vous rencontrer. Vous trouverez mon CV en pièce jointe.</p>
<p>Bien cordialement,<br>Karim Benali – 06 00 00 00 00</p></div>

<h2>Adapter le CV, même sans annonce</h2>
<p>Sans offre à suivre, il est tentant d'envoyer un CV général. C'est justement le moment de le cibler :</p>
<ul>
<li><b>Le titre</b> reprend le poste que vous proposez, avec les mots employés dans ce métier.</li>
<li><b>L'accroche</b> parle à cette entreprise : son secteur, sa clientèle, ses besoins probables.</li>
<li><b>Les expériences</b> mettent en premier les missions utiles pour ce poste.</li>
<li><b>Pour trouver les bons mots</b>, lisez deux ou trois annonces publiées ailleurs pour le même métier : elles montrent ce que les employeurs attendent.</li>
</ul>
<p>La méthode complète est dans <a href="/conseils/adapter-cv-offre/">Adapter son CV à une offre d'emploi</a>.</p>

<h2>Relancer et garder une trace</h2>
<ul>
<li><b>Relancez une fois</b>, environ une semaine plus tard, en répondant à votre premier mail ou par un appel court. Les modèles sont dans <a href="/conseils/relancer-apres-candidature/">Relancer après une candidature</a>.</li>
<li><b>Une réponse « pas de poste pour l'instant » n'est pas un refus définitif</b> : demandez si vous pouvez rester dans leurs contacts et revenir vers eux dans quelques mois.</li>
<li><b>Notez tout</b> : l'entreprise, la personne, la date d'envoi, la réponse, la date de relance. Sans suivi, on relance deux fois la même entreprise ou on en oublie une.</li>
</ul>

<h2>Les erreurs à éviter</h2>
<ul>
<li><b>Le même message pour toutes les entreprises</b>, avec seulement le nom changé : cela se voit dès la première phrase.</li>
<li><b>Ne pas dire quel poste vous visez</b> : le recruteur n'a pas le temps de deviner où vous placer.</li>
<li><b>Envoyer un mail groupé</b> avec toutes les adresses visibles : chaque entreprise doit recevoir son propre message.</li>
<li><b>Écrire « Madame, Monsieur » quand vous pouviez trouver un nom</b> : un appel de deux minutes suffit souvent.</li>
<li><b>Relancer trop souvent</b> : une relance, deux au maximum, puis passez à d'autres entreprises.</li>
</ul>
"""},
]

CSS = """<style>
.conseil h1{margin-bottom:10px}
.conseil .meta{color:#6E5872;font-size:14px;margin:0 0 24px}
.conseil h2{margin-top:34px}
.conseil h3{margin:22px 0 6px;font-size:18px}
.conseil ul,.conseil ol{padding-left:22px}
.conseil li{margin:6px 0}
.conseil .modele{background:#fff;border:1px solid #EEDFCF;border-left:4px solid #F2A93B;border-radius:12px;padding:6px 18px;margin:12px 0 18px}
.conseil .cta-box{background:#3A2340;color:#FFF8F0;border-radius:18px;padding:22px 24px;margin:40px 0 10px}
.conseil .cta-box h2{color:#fff;margin:0 0 8px}
.conseil .cta-box p{margin:0 0 16px;color:#EADDEB}
.conseil .cta-box .btn{background:#F2A93B;border-color:#F2A93B;color:#2A1A2F}
.conseil .autres{margin-top:34px}
.liste-conseils,.conseil .liste-conseils{list-style:none;padding:0;display:grid;gap:14px}
.conseil .sommaire{background:#fff;border:1px solid #EEDFCF;border-radius:14px;padding:14px 20px;margin:18px 0 8px}
.conseil .sommaire b{display:block;margin-bottom:4px;color:#3A2340}
.conseil .sommaire ol{margin:0;padding-left:20px}
.conseil .sommaire li{margin:3px 0}
.liste-conseils a{display:block;background:#fff;border:1px solid #EEDFCF;border-radius:16px;padding:18px 20px;text-decoration:none;color:inherit}
.liste-conseils a:hover{border-color:#F2A93B}
.liste-conseils b{display:block;font-size:18px;margin-bottom:6px;color:#2A1A2F}
.liste-conseils span{color:#6E5872}
</style>"""

def tete(titre, description, chemin, jsonld):
    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="color-scheme" content="only light">
<title>{html.escape(titre)} — Jaltio</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{SITE}{chemin}">
<meta property="og:type" content="article">
<meta property="og:title" content="{html.escape(titre)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:url" content="{SITE}{chemin}">
<meta property="og:locale" content="fr_FR">
<meta property="og:site_name" content="Jaltio">
<meta property="og:image" content="{SITE}/assets/og/conseils.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/favicon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preload" href="/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts.css">
<link rel="stylesheet" href="/pages.css">
<script src="/anim.js"></script>
{CSS}
<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"></header>
<main>
"""

PIED = """</main>
<footer class="foot"></footer>
<!-- Cloudflare Web Analytics --><script defer src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{"token": "dcd19a490f414e60909bf61deaae5385"}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>
"""

CTA = """<div class="cta-box">
  <h2>Un CV adapté à chaque offre, en quelques minutes</h2>
  <p>Collez le lien d'une annonce : Jaltio réécrit votre CV à partir de votre vrai parcours, sans rien inventer. 5 CV offerts, sans carte bancaire.</p>
  <a class="btn" href="/inscription/?offre=free">Essayer gratuitement</a>
</div>"""

def date_fr(iso):
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    a, m, j = iso.split("-")
    return f"{int(j)} {mois[int(m) - 1]} {a}"

(RACINE / "conseils").mkdir(exist_ok=True)
for a in ARTICLES:
    chemin = f"/conseils/{a['slug']}/"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": a["titre"], "description": a["description"],
          "datePublished": a.get("publie", a["date"]), "dateModified": a["date"], "inLanguage": "fr-FR", "mainEntityOfPage": SITE + chemin,
          "author": {"@type": "Organization", "name": "Jaltio", "url": SITE + "/"},
          "publisher": {"@type": "Organization", "name": "Jaltio", "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo-512.png"}}}
    i = ARTICLES.index(a)
    voisins = [ARTICLES[(i + k) % len(ARTICLES)] for k in range(1, min(4, len(ARTICLES)))]   # 3 articles liés, pas toute la liste
    autres = "".join(f'<li><a href="/conseils/{b["slug"]}/"><b>{html.escape(b["titre"])}</b><span>{html.escape(b["description"])}</span></a></li>' for b in voisins)
    corps, titres = a["corps"].strip(), []
    def ancre(m):
        n = len(titres) + 1; titres.append(re.sub(r"<[^>]+>", "", m.group(1))); return f'<h2 id="s{n}">{m.group(1)}</h2>'
    corps = re.sub(r"<h2>(.*?)</h2>", ancre, corps)
    sommaire = ('<nav class="sommaire" aria-label="Sommaire"><b>Au sommaire</b><ol>' + "".join(f'<li><a href="#s{k + 1}">{t}</a></li>' for k, t in enumerate(titres)) + '</ol></nav>\n') if len(titres) >= 3 else ""
    publie, maj = a.get("publie", a["date"]), a["date"]
    meta = f"Publié le {date_fr(publie)}" + (f" · mis à jour le {date_fr(maj)}" if maj != publie else "")
    page = (tete(a["titre"], a["description"], chemin, ld)
            + f'<article class="wrap narrow conseil">\n<p class="kicker"><a href="/conseils/">Conseils</a></p>\n<h1>{html.escape(a["titre"])}</h1>\n'
            + f'<p class="meta">{meta}</p>\n<p class="lead">{html.escape(a["intro"])}</p>\n' + sommaire
            + corps + "\n" + CTA
            + f'\n<section class="autres"><h2>Autres conseils</h2><ul class="liste-conseils">{autres}</ul></section>\n</article>\n' + PIED)
    d = RACINE / "conseils" / a["slug"]; d.mkdir(exist_ok=True)
    (d / "index.html").write_text(page)
    print("ok", chemin)

ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Conseils pour votre recherche d'emploi", "url": SITE + "/conseils/", "inLanguage": "fr-FR"}
liste = "".join(f'<li><a href="/conseils/{a["slug"]}/"><b>{html.escape(a["titre"])}</b><span>{html.escape(a["description"])}</span></a></li>' for a in ARTICLES)
index = (tete("Conseils pour votre recherche d'emploi : CV, lettre, relance, entretien",
              "Des conseils concrets pour votre recherche d'emploi : adapter son CV à une offre, passer les logiciels de recrutement, écrire sa lettre, relancer, préparer l'entretien.",
              "/conseils/", ld)
         + '<div class="wrap narrow conseil">\n<h1>Conseils pour votre recherche d\'emploi</h1>\n'
         + '<p class="lead">Des méthodes simples et concrètes, de l\'annonce à l\'entretien. Sans jargon, et sans rien inventer sur votre parcours.</p>\n'
         + f'<ul class="liste-conseils">{liste}</ul>\n' + CTA + '\n</div>\n' + PIED)
(RACINE / "conseils" / "index.html").write_text(index)
print("ok /conseils/")

# sitemap.xml : pages fixes + conseils
fixes = ["/", "/forfaits/", "/faq/", "/contact/", "/conseils/", "/cgv.html", "/confidentialite.html", "/mentions-legales.html"]
urls = fixes + [f"/conseils/{a['slug']}/" for a in ARTICLES]
xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"  <url><loc>{SITE}{u}</loc></url>\n" for u in urls) + "</urlset>\n"
(RACINE / "sitemap.xml").write_text(xml)
print("ok sitemap.xml", len(urls), "adresses")
