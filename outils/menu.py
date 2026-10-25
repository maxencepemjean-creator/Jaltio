#!/usr/bin/env python3
"""Réécrit l'en-tête (menu) et le pied de page communs de toutes les pages publiques de jaltio.fr.
Usage : python3 outils/menu.py   (à relancer après avoir modifié le menu ci-dessous)"""
import re, pathlib
RACINE = pathlib.Path(__file__).resolve().parent.parent
LOGO = '<svg width="36" height="36" viewBox="0 0 72 72" role="img" aria-label="Logo Jaltio"><rect width="72" height="72" rx="18" fill="#3A2340"/><path d="M19 38l11 11 23-26" fill="none" stroke="#FFFFFF" stroke-width="6.5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="53" cy="22" r="4.5" fill="none" stroke="#F2A93B" stroke-width="3.5"/></svg>'
MENU = [("/", "Accueil"), ("/forfaits/", "Tarifs"), ("/faq/", "FAQ"), ("/contact/", "Contact")]
INSCRIPTION, CONNEXION = "/inscription/?offre=essentiel", "/app/"
# page -> lien actif du menu (None : aucun) ; "simple" = en-tête allégé (tunnel d'inscription)
PAGES = {"index.html": "/", "forfaits/index.html": "/forfaits/", "faq/index.html": "/faq/", "contact/index.html": "/contact/",
         "cgv.html": None, "confidentialite.html": None, "mentions-legales.html": None, "inscription/index.html": "simple"}

def entete(actif):
    if actif == "simple":
        return ('<header class="top">\n  <a class="brand" href="/">' + LOGO + '<span class="name">Jaltio</span></a>\n'
                '  <a class="top-link" href="/forfaits/">Tarifs</a>\n</header>')
    cur = lambda h: ' aria-current="page"' if h == actif else ''
    liens = "".join(f'<a href="{h}"{cur(h)}>{t}</a>' for h, t in MENU)
    return ('<header class="top">\n  <a class="brand" href="/">' + LOGO + '<span class="name">Jaltio</span></a>\n'
            f'  <nav class="mainnav" aria-label="Menu principal">{liens}</nav>\n'
            f'  <div class="top-cta"><a class="top-link" href="{CONNEXION}">Se connecter</a><a class="top-link solid" href="{INSCRIPTION}">S\'inscrire</a></div>\n'
            '  <details class="menu"><summary aria-label="Ouvrir le menu"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3A2340" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></summary>\n'
            f'    <div class="menu-pop">{liens}<hr><a href="{CONNEXION}">Se connecter</a><a href="{INSCRIPTION}">S\'inscrire</a></div></details>\n</header>')

PIED = ('<footer class="foot">\n  <nav><a href="/">Accueil</a><a href="/forfaits/">Tarifs</a><a href="/faq/">FAQ</a><a href="/contact/">Contact</a>'
        '<a href="/cgv.html">CGV</a><a href="/confidentialite.html">Confidentialité</a><a href="/mentions-legales.html">Mentions légales</a>'
        '<a href="/app/?resilier">Résilier mon abonnement</a></nav>\n'
        '  Jaltio · <a href="mailto:contact@jaltio.fr">contact@jaltio.fr</a> · IA : Claude, d\'Anthropic (États-Unis)\n</footer>')

for chemin, actif in PAGES.items():
    f = RACINE / chemin
    s = f.read_text()
    s, n1 = re.subn(r'<header class="top">.*?</header>', lambda m: entete(actif), s, count=1, flags=re.S)
    s, n2 = re.subn(r'<footer class="foot">.*?</footer>', lambda m: PIED, s, count=1, flags=re.S)
    f.write_text(s)
    print(f"{chemin}: en-tête {'ok' if n1 else 'ABSENT'}, pied {'ok' if n2 else 'ABSENT'}")
