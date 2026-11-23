# The gear texture sheet: sixteen CC0 surfaces from Poly Haven (https://polyhaven.com), each turned into greyscale detail
# (mean 0.5, so the game multiplies it by twice the dye colour) and packed 4 x 4 at 256 px into creator/tex/gear.jpg.
# Tile order is EQ_MAT in creator/equip.js. Tiles 12 (brushed steel) and 14 (mail) are drawn here: Poly Haven has neither.
# usage: python3 gearsheet.py [out.jpg]   (downloads the 1k diffuse maps into ./cache)
import os, sys, io, urllib.request, json
import numpy as np
from PIL import Image
TILES = ['rough_linen', 'caban', 'poly_wool_herringbone', 'brown_leather', 'leather_red_02', 'scuba_suede', 'curly_teddy_natural',
         'hessian_230', 'velour_velvet', 'floral_jacquard', 'quatrefoil_jacquard_fabric', 'knitted_fleece', 'brushed',
         'rusty_metal_02', None, 'wool_boucle']
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', '..', 'creator', 'tex', 'gear.jpg')
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache'); os.makedirs(CACHE, exist_ok=True)
S = 256
UA = {'User-Agent': 'gearsheet-builder/1.0'}
def get(url): return urllib.request.urlopen(urllib.request.Request(url, headers=UA)).read()
def fetch(name):
    p = os.path.join(CACHE, name + '.jpg')
    if not os.path.exists(p):
        files = json.loads(get('https://api.polyhaven.com/files/' + name))
        key = 'Diffuse' if 'Diffuse' in files else sorted(k for k in files if k.startswith('coll'))[0]   # some sets name their colour maps coll1, coll2
        data = get(files[key]['1k']['jpg']['url']); open(p, 'wb').write(data)
    return Image.open(p).convert('L')
def detail(img, spread):
    a = np.asarray(img.resize((S, S), Image.LANCZOS), dtype=np.float64) / 255.0
    a = a / max(a.mean(), 1e-3) * 0.5                       # mean 0.5: multiplying by 2x keeps the dye's own brightness
    a = 0.5 + (a - 0.5) * (spread / max(a.std(), 1e-3))     # every tile carries a set amount of detail, whatever the photo's contrast
    return np.clip(a, 0, 1)
SPREAD = {'curly_teddy_natural': 0.12, 'wool_boucle': 0.12, 'floral_jacquard': 0.11, 'quatrefoil_jacquard_fabric': 0.1, 'hessian_230': 0.11,
          'metal_plate_02': 0.07, 'rusty_metal_02': 0.1}
def brushed():
    rng = np.random.default_rng(7); a = rng.random((S, S))
    for _ in range(40): a = 0.5 * a + 0.25 * (np.roll(a, 1, 1) + np.roll(a, -1, 1))      # streaks along one direction, wrapping
    a = 0.6 * a + 0.4 * (0.5 + 0.5 * np.sin(np.linspace(0, 6 * np.pi, S))[:, None] * 0.15)
    a = (a - a.mean()) / a.std() * 0.07 + 0.5
    return np.clip(a, 0, 1)
def mail():
    y, x = np.mgrid[0:S, 0:S] / S * 16.0                     # 16 x 22 rings per tile, each row offset by half a ring
    rows = np.floor(y * 1.375); gx = (x + 0.5 * (rows % 2)) % 1 - 0.5; gy = (y * 1.375) % 1 - 0.5
    r = np.abs(np.hypot(gx, gy) - 0.3)
    ring = np.clip(1 - (r - 0.08) / 0.08, 0, 1)
    return np.clip(0.18 + 0.62 * ring * (1.15 - 0.6 * np.hypot(gx, gy)), 0, 1)
sheet = np.zeros((S * 4, S * 4))
for k, name in enumerate(TILES):
    t = mail() if name is None else brushed() if name == 'brushed' else detail(fetch(name), SPREAD.get(name, 0.08))
    r, c = divmod(k, 4); sheet[r * S:(r + 1) * S, c * S:(c + 1) * S] = t
    print(k, name or 'mail (drawn)', round(t.mean(), 3), round(t.std(), 3))
Image.fromarray((sheet * 255).astype(np.uint8)).convert('RGB').save(OUT, quality=88)
print('wrote', OUT)
