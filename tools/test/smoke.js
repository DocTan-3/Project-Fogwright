// Smoke test: serve the repo, boot the game in headless Chromium at phone size, visit a few places with the
// Admin teleports, save screenshots and report page errors.  Usage: node tools/test/smoke.js  (needs playwright)
const { chromium, devices } = require('playwright'); const path = require('path'); const http = require('http'); const fs = require('fs');
const ROOT = path.resolve(__dirname, '../..'), PORT = 8790;
const TYPES = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.js': 'application/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0].split('#')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.statusCode = 404; r.end(); return; } r.setHeader('Content-Type', TYPES[path.extname(f)] || 'application/octet-stream'); r.end(d); }); }).listen(PORT);
const SPOTS = (process.env.SPOTS || 'The village,Outside the city gate,The outskirts,Zarhim Quarter').split(',');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await (await browser.newContext({ ...devices['Pixel 7 landscape'] })).newPage(); const errs = [];
  pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
  const t0 = Date.now(); await pg.goto(`http://localhost:${PORT}/game/index.html`);
  await pg.waitForFunction(() => !document.getElementById('loading'), { timeout: 120000 }); console.log('ready in', Date.now() - t0, 'ms');
  fs.mkdirSync(path.join(ROOT, 'shots'), { recursive: true });
  for (const s of SPOTS) {
    await pg.evaluate(l => { const b = [...document.querySelectorAll('#adminSpots button')].find(x => x.textContent === l); if (b) b.click(); document.getElementById('adminPanel').hidden = true; }, s);
    await pg.waitForTimeout(4000); const f = path.join(ROOT, 'shots', s.replace(/\W+/g, '_') + '.png'); await pg.screenshot({ path: f });
    console.log(s, '->', await pg.textContent('#biomeName'));
  }
  console.log(errs.length ? 'ERRORS:\n' + errs.join('\n') : 'no page errors'); await browser.close(); srv.close(); process.exit(errs.length ? 1 : 0);
})();
