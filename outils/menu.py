#!/usr/bin/env python3
"""Réécrit l'en-tête (menu) et le pied de page communs de toutes les pages publiques de jaltio.fr.
Usage : python3 outils/menu.py   (à relancer après avoir modifié le menu ci-dessous)"""
import re, pathlib
RACINE = pathlib.Path(__file__).resolve().parent.parent
LOGO = '<svg width="36" height="36" viewBox="0 0 72 72" role="img" aria-label="Logo Jaltio"><rect width="72" height="72" rx="18" fill="#3A2340"/><path d="M15 55H28V44H41V33H55" fill="none" stroke="#FFFFFF" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="50" cy="20" r="6.5" fill="#F2A93B"/></svg>'
MENU = [("/", "Accueil"), ("/forfaits/", "Tarifs"), ("/conseils/", "Conseils"), ("/faq/", "FAQ"), ("/contact/", "Contact")]
INSCRIPTION, CONNEXION = "/inscription/?offre=free", "/app/"
LIB_INSCRIPTION = "Essayer gratuitement"
# page -> lien actif du menu (None : aucun) ; "simple" = en-tête allégé (tunnel d'inscription)
PAGES = {"index.html": "/", "forfaits/index.html": "/forfaits/", "faq/index.html": "/faq/", "contact/index.html": "/contact/",
         "conseils/index.html": "/conseils/", "cgv.html": None, "confidentialite.html": None, "mentions-legales.html": None, "inscription/index.html": "simple",
         "retractation/index.html": None, "404.html": None}

def entete(actif):
    if actif == "simple":
        return ('<header class="top">\n  <a class="brand" href="/">' + LOGO + '<span class="name">Jaltio</span></a>\n'
                '  <a class="top-link" href="/forfaits/">Tarifs</a>\n</header>')
    cur = lambda h: ' aria-current="page"' if h == actif else ''
    liens = "".join(f'<a href="{h}"{cur(h)}>{t}</a>' for h, t in MENU)
    return ('<header class="top">\n  <a class="brand" href="/">' + LOGO + '<span class="name">Jaltio</span></a>\n'
            f'  <nav class="mainnav" aria-label="Menu principal">{liens}</nav>\n'
            f'  <div class="top-cta"><a class="top-link" href="{CONNEXION}">Se connecter</a><a class="top-link solid" href="{INSCRIPTION}">' + LIB_INSCRIPTION + '</a></div>\n'
            '  <details class="menu"><summary aria-label="Ouvrir le menu"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3A2340" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>\n'
            f'    <div class="menu-pop">{liens}<hr><a href="{CONNEXION}">Se connecter</a><a href="{INSCRIPTION}">' + LIB_INSCRIPTION + '</a></div></details>\n</header>')

LOGO_PIED = LOGO.replace('width="36" height="36"', 'width="26" height="26"').replace('role="img" aria-label="Logo Jaltio"', 'aria-hidden="true"')
PIED = ('<footer class="foot">\n  <a class="foot-brand" href="/">' + LOGO_PIED + 'Jaltio</a>\n'
        '  <p class="foot-tag">Un CV et une lettre adaptés à chaque offre d\'emploi.</p>\n'
        '  <nav aria-label="Pied de page"><a href="/forfaits/">Tarifs</a><a href="/conseils/">Conseils</a><a href="/conseils/adapter-cv-offre/">Adapter son CV</a><a href="/conseils/lettre-de-motivation-structure/">Lettre de motivation</a><a href="/conseils/preparer-entretien-embauche/">Entretien</a><a href="/faq/">FAQ</a><a href="/contact/">Contact</a></nav>\n'
        '  <nav aria-label="Informations légales"><a href="/cgv.html">CGV</a><a href="/confidentialite.html">Confidentialité</a><a href="/mentions-legales.html">Mentions légales</a>'
        '<a href="/app/?resilier">Résilier mon abonnement</a><a href="/retractation/">Me rétracter</a></nav>\n'
        '  <p class="foot-legal">© 2026 Jaltio · <a href="mailto:contact@jaltio.fr">contact@jaltio.fr</a> · Documents rédigés avec Claude, l\'IA d\'Anthropic (<a href="/faq/#ia">en savoir plus</a>)</p>\n</footer>')

# Articles de conseils : lien « Conseils » actif
for d in sorted((RACINE / "conseils").glob("*/index.html")):
    PAGES[str(d.relative_to(RACINE))] = "/conseils/"

for chemin, actif in PAGES.items():
    f = RACINE / chemin
    s = f.read_text()
    s, n1 = re.subn(r'<header class="top">.*?</header>', lambda m: entete(actif), s, count=1, flags=re.S)
    s, n2 = re.subn(r'<footer class="foot">.*?</footer>', lambda m: PIED, s, count=1, flags=re.S)
    if '<script src="/anim.js"></script>' not in s:   # animations communes (apparitions, en-tête, FAQ)
        s = s.replace('<link rel="stylesheet" href="/pages.css">', '<link rel="stylesheet" href="/pages.css">\n<script src="/anim.js"></script>', 1)
    f.write_text(s)
    print(f"{chemin}: en-tête {'ok' if n1 else 'ABSENT'}, pied {'ok' if n2 else 'ABSENT'}")
