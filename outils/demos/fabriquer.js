/* Fabrique les images des démos vidéo : demos/Dxx_avant.png (CV brut) et demos/Dxx_apres.png (CV rendu par l'appli Jaltio).
   Usage : node outils/demos/fabriquer.js outils/demos/lots/lot-AAAAMMJJ.json
   Le fichier lot est une liste : { id, metier, profil, ancien_cv, offre, score, couleur, cv } — cv au format JSON de l'appli. */
const { chromium } = require("playwright");
const fs = require("fs"), path = require("path"), http = require("http");

const RACINE = path.resolve(__dirname, "..", "..");
const lot = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));

const esc = s => String(s || "").replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
function pageAvant(texte) {
  const [nom, ...reste] = String(texte).split("\n");
  const lignes = reste.join("\n").split(/\n\s*\n/);
  const entete = lignes.shift().split("\n").map(esc).join("<br>");
  return `<!doctype html><html><head><meta charset="utf-8"><style>
    @page{size:A4} body{margin:0;background:#fff}
    .p{width:794px;height:1123px;box-sizing:border-box;padding:70px 76px;font-family:"Liberation Serif","Times New Roman",Times,serif;font-size:14.6px;line-height:1.42;color:#111}
    h1{font-size:19px;text-align:center;text-decoration:underline;margin:0 0 30px;letter-spacing:.5px}
    .n{font-weight:bold;font-size:15.5px} p{margin:0 0 12px;text-align:justify}
  </style></head><body><div class="p"><h1>CURRICULUM VITAE</h1><div class="n">${esc(nom)}</div><p>${entete}</p>${lignes.map(l => `<p>${esc(l).replace(/\n/g, "<br>")}</p>`).join("")}</div></body></html>`;
}

function mix(hex, autre, t) {
  const a = hex.match(/\w\w/g).map(x => parseInt(x, 16)), b = autre.match(/\w\w/g).map(x => parseInt(x, 16));
  return "#" + a.map((v, i) => Math.round(v + (b[i] - v) * t).toString(16).padStart(2, "0")).join("");
}

(async () => {
  const serveur = http.createServer((req, res) => {
    let f = path.join(RACINE, decodeURIComponent(req.url.split("?")[0]));
    if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, "index.html");
    if (!fs.existsSync(f)) { res.writeHead(404); return res.end(); }
    const types = { ".html": "text/html; charset=utf-8", ".css": "text/css", ".js": "text/javascript", ".woff2": "font/woff2", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp" };
    res.writeHead(200, { "content-type": types[path.extname(f)] || "application/octet-stream" });
    fs.createReadStream(f).pipe(res);
  }).listen(0);
  const port = serveur.address().port;
  const navigateur = await chromium.launch();
  const ctx = await navigateur.newContext({ viewport: { width: 1400, height: 1200 }, deviceScaleFactor: 2, reducedMotion: "reduce" });
  await ctx.route(/workers\.dev/, r => r.fulfill({ status: 200, contentType: "application/json", body: "{}" }));

  for (const d of lot) {
    // Avant : CV brut, page A4
    const pa = await ctx.newPage();
    await pa.setContent(pageAvant(d.ancien_cv));
    await pa.locator(".p").screenshot({ path: path.join(RACINE, "demos", d.id + "_avant.png") });
    await pa.close();

    // Après : CV rendu par l'appli, aux couleurs choisies
    const pp = await ctx.newPage();
    await pp.addInitScript(() => { try { localStorage.setItem("cvx_tourSeen", "true"); } catch (e) {} });
    await pp.goto(`http://localhost:${port}/app/`);
    await pp.waitForFunction(() => window.__cvx && window.__cvx.renderAll);
    await pp.addStyleTag({ content: ".gate,.tour,.overlay,.sync-toast{display:none!important} body.gate-open{overflow:auto!important}" });
    const c = d.couleur || "#2E5E8C";
    const pal = { accent: c, dark: mix(c.slice(1), "000000", .6), tint: mix(c.slice(1), "ffffff", .91), light: mix(c.slice(1), "ffffff", .6) };
    await pp.evaluate(({ out, pal }) => {
      document.querySelectorAll(".gate,.tour,.overlay").forEach(e => { e.hidden = true; });
      window.__cvx.setView("create");
      window.__cvx.renderAll(out);
      const cv = document.querySelector("#page-cv");
      for (const k of ["accent", "dark", "tint", "light"]) cv.style.setProperty("--" + k, pal[k]);
      cv.removeAttribute("contenteditable");
    }, { out: { offre_lue: true, cv: d.cv, lettre: null, alertes: [] }, pal });
    await pp.waitForTimeout(500);
    const deborde = await pp.evaluate(() => { const p = document.querySelector("#page-cv"); return p.scrollHeight > p.clientHeight + 2; });
    await pp.locator("#page-cv").screenshot({ path: path.join(RACINE, "demos", d.id + "_apres.png") });
    await pp.close();
    console.log(d.id, d.metier, deborde ? "ATTENTION : le CV après dépasse la page" : "ok");
  }
  await navigateur.close();
  serveur.close();
})();
