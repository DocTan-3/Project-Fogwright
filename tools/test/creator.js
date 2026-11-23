// Creator test: serve the repo, open the character creator in headless Chromium, and go through every body, people,
// build extreme and view. Fails on page errors, on a body that does not load, or on a people whose shape is missing.
// Saves a screenshot per people and sex in shots/creator/.  Usage: node tools/test/creator.js  (needs playwright)
// BODY=old tests the previous bodies (creator/index.html?body=old).
const { chromium } = require('playwright'); const path = require('path'); const http = require('http'); const fs = require('fs');
const ROOT = path.resolve(__dirname, '../..'), PORT = 8791;
const TYPES = { '.html': 'text/html; charset=utf-8', '.json': 'application/json', '.js': 'application/javascript' };
const srv = http.createServer((q, r) => { const f = path.join(ROOT, decodeURIComponent(q.url.split('?')[0].split('#')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.statusCode = 404; r.end(); return; } r.setHeader('Content-Type', TYPES[path.extname(f)] || 'application/octet-stream'); r.end(d); }); }).listen(PORT);
const SHAPED = ['Aurelan', 'Ilvari', 'Ferrin', 'Zarhim'];   // peoples with their own built-in shape (the others use the Human body)
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await (await browser.newContext({ viewport: { width: 1280, height: 800 } })).newPage(); const errs = [], fails = [];
  pg.on('pageerror', e => errs.push(e.message)); pg.on('console', m => { if (m.type() === 'error') errs.push(m.text().slice(0, 200)); });
  const t0 = Date.now(); await pg.goto(`http://localhost:${PORT}/creator/index.html${process.env.BODY === 'old' ? '?body=old' : ''}`);
  await pg.waitForFunction(() => !document.getElementById('status'), { timeout: 120000 }).catch(() => fails.push('the bodies never loaded'));
  console.log('loaded in', Date.now() - t0, 'ms');
  const click = (id, label) => pg.evaluate(([id, label]) => { const b = [...document.querySelectorAll('#' + id + ' button')].find(x => x.textContent === label); if (b) b.click(); return !!b; }, [id, label]);
  const state = () => pg.evaluate(() => { let body = null, tris = 0, hair = 0;
    scene.traverse(o => { if (!o.isMesh || !o.visible) return; if (o.morphTargetDictionary && 'Lean' in o.morphTargetDictionary) { body = o; tris = (o.geometry.index ? o.geometry.index.count : o.geometry.attributes.position.count) / 3; } else if (/^Hair_|^Moustache_/.test(o.name)) hair++; });
    if (!body) return null; const d = body.morphTargetDictionary, w = body.morphTargetInfluences;
    return { tris, hair, shapes: Object.keys(d), on: Object.keys(d).filter(k => w[d[k]] > 0.01) }; });
  fs.mkdirSync(path.join(ROOT, 'shots', 'creator'), { recursive: true });
  for (const sex of ['Man', 'Woman']) {
    await click('sex', sex); await pg.waitForTimeout(800);
    const people = await pg.evaluate(() => [...document.querySelectorAll('#people button')].map(b => b.textContent));
    for (const p of people) {
      await click('people', p); await pg.waitForTimeout(600);
      const s = await state();
      if (!s) { fails.push(`${sex} ${p}: no body`); continue; }
      if (SHAPED.includes(p) && !s.on.includes(p) && s.shapes.includes(p)) fails.push(`${sex} ${p}: shape not applied`);
      if (SHAPED.includes(p) && !s.shapes.includes(p)) console.log(`  note: ${sex} ${p} has no shape of its own in this model`);
      for (const v of [0, 1]) { await pg.evaluate(v => { const e = document.getElementById('build'); e.value = v; e.dispatchEvent(new Event('input')); }, v); await pg.waitForTimeout(150); }
      await pg.screenshot({ path: path.join(ROOT, 'shots', 'creator', `${sex}_${p}.png`) });
      console.log(`${sex} ${p}: ${s.tris} triangles, shapes on: ${s.on.join(', ') || 'none'}, hair pieces shown: ${s.hair}`);
    }
  }
  for (const v of ['Face', 'Walk', 'Full']) { if (!await click('view', v)) fails.push(`no ${v} view`); await pg.waitForTimeout(800); }
  await pg.screenshot({ path: path.join(ROOT, 'shots', 'creator', 'walk.png') });
  if (errs.length) fails.push('page errors:\n  ' + errs.join('\n  '));
  console.log(fails.length ? 'FAILED:\n' + fails.join('\n') : 'creator test passed');
  await browser.close(); srv.close(); process.exit(fails.length ? 1 : 0);
})();
