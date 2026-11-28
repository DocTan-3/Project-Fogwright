# Fogwright's sample voxel character bases (docs/design.md, Voxel art): a man and a woman at 5 cm voxels, standing straight
# with the arms at the sides, every body part its own named model in one MagicaVoxel file, so it opens and edits in
# MagicaVoxel and animates as rigid parts in the game (godot/scripts/voxel/vox.gd: parts pivot at their joints by name).
#   python3 tools/voxel/make_base.py            -> godot/assets/voxel/characters/base_m.vox, base_f.vox
#
# MagicaVoxel axes: x across the body, y front (0) to back, z up. One voxel is 5 cm: the man is 36 voxels (1.80 m), the
# woman 34 (1.70 m). Plain colours, chosen to be recoloured per people and outfit.
import os, struct

COL = {   # index in the file's palette: colour
    'skin': (198, 142, 106), 'skin_d': (164, 106, 82), 'hair': (59, 42, 31), 'eye': (26, 22, 20), 'brow': (52, 36, 27),
    'shirt': (216, 204, 180), 'shirt_d': (184, 170, 146), 'trousers': (74, 58, 46), 'boots': (58, 42, 32), 'sole': (34, 26, 20),
    'belt': (110, 74, 42), 'buckle': (196, 154, 74),
}
NAMES = list(COL)

def body(sex):
    f = sex == 'f'
    P = {}   # part -> {(x, y, z): colour}
    def put(part, x, y, z, c): P.setdefault(part, {})[(x, y, z)] = c
    def box(part, x0, x1, y0, y1, z0, z1, c):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1): put(part, x, y, z, c)
    leg_top = 15 if f else 16          # the hip joint (the top of the upper leg)
    knee = 8
    tz0 = leg_top + 1                  # torso: from the pelvis ...
    tz1 = tz0 + (10 if f else 11)      # ... to the shoulders
    # legs: lower leg and boot (with the toe forward), upper leg; 3 wide, a voxel apart
    for side, (x0, x1) in (('l', (5, 7)), ('r', (9, 11))):
        box('leg_lower_' + side, x0, x1, 1, 3, 0, knee, 'trousers')
        box('leg_lower_' + side, x0, x1, 1, 3, 1, 3, 'boots'); box('leg_lower_' + side, x0, x1, 0, 3, 0, 0, 'sole')
        box('leg_lower_' + side, x0, x1, 0, 0, 1, 2, 'boots')
        box('leg_upper_' + side, x0, x1, 1, 3, knee + 1, leg_top, 'trousers')
    # torso: pelvis in trousers, a belt with a buckle, the shirt; the woman's waist narrower and hips a little wider
    for z in range(tz0, tz1 + 1):
        w0, w1 = 5, 11
        if f and tz0 + 3 <= z <= tz0 + 5: w0, w1 = 6, 10
        c = 'trousers' if z <= tz0 else ('belt' if z == tz0 + 1 else 'shirt')
        box('torso', w0, w1, 0, 4, z, z, c)
        if z == tz0 + 1: put('torso', 8, 0, z, 'buckle')
    box('torso', 6, 10, 0, 0, tz0 + 2, tz0 + 2, 'shirt_d')           # the shirt's hem, shaded
    if f: box('torso', 6, 10, 0, 0, tz1 - 3, tz1 - 2, 'shirt')       # the bust: a voxel forward
    for x in (7, 9): put('torso', x, 0, tz1, 'shirt_d')              # the collar's opening
    put('torso', 8, 0, tz1, 'skin'); put('torso', 8, 0, tz1 - 1, 'skin')
    # arms: the upper arm in the sleeve, the lower arm with a cuff, the hand
    sh = tz1                                   # shoulder top
    elbow = sh - (7 if f else 8)
    hand = elbow - 7
    for side, (x0, x1) in (('l', (2, 4)), ('r', (12, 14))):
        box('arm_upper_' + side, x0, x1, 1, 3, elbow + 1, sh, 'shirt')
        box('arm_lower_' + side, x0, x1, 1, 3, hand + 2, elbow, 'shirt')
        box('arm_lower_' + side, x0, x1, 1, 3, hand + 2, hand + 2, 'shirt_d')
        box('arm_lower_' + side, x0 + (1 if side == 'l' else 0), x1 - (0 if side == 'l' else 1), 1, 3, hand - 1, hand + 1, 'skin')
    # head: 7 wide, 6 deep, 7 tall; eyes, brows, a mouth; hair over the top, back and sides (the woman's long down the back)
    hz0 = tz1 + 1; hz1 = hz0 + 6
    box('head', 5, 11, 0, 5, hz0, hz1, 'skin')
    for x in (6, 10): put('head', x, 0, hz0 + 3, 'eye'); put('head', x, 0, hz0 + 4, 'brow')
    for x in (7, 8, 9): put('head', x, 0, hz0 + 1, 'skin_d')
    put('head', 8, 0, hz0 + 2, 'skin_d')                                  # the nose's shadow
    box('head', 5, 11, 0, 5, hz1, hz1, 'hair')                            # the top
    box('head', 5, 11, 5, 5, hz0 + 2, hz1, 'hair')                        # the back
    for x in (5, 11): box('head', x, x, 2, 5, hz0 + 3, hz1, 'hair')       # the sides, above the ears
    box('head', 5, 11, 0, 0, hz1, hz1, 'hair')                            # a fringe
    if f:
        box('head', 5, 11, 6, 6, hz0 - 2, hz1, 'hair')                    # long hair down the back
        for x in (5, 11): box('head', x, x, 1, 5, hz0 + 1, hz1, 'hair')
        box('head', 4, 4, 2, 5, hz0 - 1, hz1 - 1, 'hair'); box('head', 12, 12, 2, 5, hz0 - 1, hz1 - 1, 'hair')
    return P

def s(v): b = v.encode(); return struct.pack('<i', len(b)) + b
def d(dd): return struct.pack('<i', len(dd)) + b''.join(s(k) + s(v) for k, v in dd.items())
def chunk(cid, content, children=b''): return cid.encode() + struct.pack('<ii', len(content), len(children)) + content + children

def write(path, parts):
    models, scene = b'', []
    for i, (name, vox) in enumerate(parts.items()):
        xs = [p[0] for p in vox]; ys = [p[1] for p in vox]; zs = [p[2] for p in vox]
        mn = (min(xs), min(ys), min(zs)); size = (max(xs) - mn[0] + 1, max(ys) - mn[1] + 1, max(zs) - mn[2] + 1)
        models += chunk('SIZE', struct.pack('<iii', *size))
        data = struct.pack('<i', len(vox)) + b''.join(struct.pack('<BBBB', x - mn[0], y - mn[1], z - mn[2], NAMES.index(c) + 1) for (x, y, z), c in sorted(vox.items()))
        models += chunk('XYZI', data)
        t = (mn[0] + size[0] // 2, mn[1] + size[1] // 2, mn[2] + size[2] // 2)   # MagicaVoxel places a model by its centre
        scene.append((name, t))
    # the scene graph: a root transform, a group, and per part a named transform with its shape
    n = len(scene); nodes = b''
    nodes += chunk('nTRN', struct.pack('<i', 0) + d({}) + struct.pack('<iiii', 1, -1, -1, 1) + d({}))
    nodes += chunk('nGRP', struct.pack('<i', 1) + d({}) + struct.pack('<i', n) + b''.join(struct.pack('<i', 2 + 2 * i) for i in range(n)))
    for i, (name, t) in enumerate(scene):
        nodes += chunk('nTRN', struct.pack('<i', 2 + 2 * i) + d({'_name': name}) + struct.pack('<iiii', 3 + 2 * i, -1, 0, 1) + d({'_t': '%d %d %d' % t}))
        nodes += chunk('nSHP', struct.pack('<i', 3 + 2 * i) + d({}) + struct.pack('<i', 1) + struct.pack('<i', i) + d({}))
    pal = b''.join(struct.pack('<BBBB', *COL[k], 255) for k in NAMES) + b'\x00\x00\x00\xff' * (256 - len(NAMES))
    body_ = models + nodes + chunk('RGBA', pal)
    open(path, 'wb').write(b'VOX ' + struct.pack('<i', 150) + chunk('MAIN', b'', body_))
    print('%s: %d parts, %d voxels, %d tall' % (os.path.basename(path), n, sum(len(v) for v in parts.values()),
          max(p[2] for v in parts.values() for p in v) + 1))

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'godot', 'assets', 'voxel', 'characters')
os.makedirs(OUT, exist_ok=True)
for sx in ('m', 'f'): write(os.path.join(OUT, 'base_%s.vox' % sx), body(sx))
