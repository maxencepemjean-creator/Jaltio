# Régénère les PDF des documents légaux à partir des pages HTML du site.
# Usage (depuis la racine du dépôt) : python3 outils/generer-pdf-legaux.py
import http.server, threading, functools, os
from playwright.sync_api import sync_playwright
racine = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=racine)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8799), Handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
pages = {"cgv.html": "legal/jaltio-cgv.pdf", "confidentialite.html": "legal/jaltio-confidentialite.pdf"}
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    for src, dst in pages.items():
        pg.goto("http://127.0.0.1:8799/" + src); pg.wait_for_timeout(400)
        pg.pdf(path=os.path.join(racine, dst), format="A4", print_background=True,
               margin={"top": "16mm", "bottom": "16mm", "left": "15mm", "right": "15mm"},
               display_header_footer=True, header_template="<span></span>",
               footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#777">Jaltio · jaltio.fr · page <span class="pageNumber"></span>/<span class="totalPages"></span></div>')
        print("ok", dst, os.path.getsize(os.path.join(racine, dst)))
    b.close()
srv.shutdown()
