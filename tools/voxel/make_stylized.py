# Fogwright's stylized voxel character (the user's references): about 4.5 heads tall, a big head, a short broad torso with
# no neck, thick arms with bracers and big fists, short sturdy legs, big boots, boxy shapes with bevelled edges, flat colours.
# The face is drawn voxel by voxel on the front of the head (a map, as a pixel artist would), not computed from shapes.
# A Hrimfolk man: a shaved, tattooed scalp, heavy brows, a scar over the left eye, a beard round the mouth with a braid.
#   python3 tools/voxel/make_stylized.py   -> godot/assets/voxel/characters/hrim_stylized.vox
# 2.5 cm voxels, MagicaVoxel axes: x across (0 = the character's right as seen from the front), y front (small) to back, z up.
import os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('mb', os.path.join(HERE, 'make_base.py')); mb = importlib.util.module_from_spec(spec)
src = open(spec.origin).read(); exec(compile(src[:src.rindex('\nOUT = ')], spec.origin, 'exec'), mb.__dict__)

PAL = {
    'skin': (222, 170, 132), 'skin_d': (190, 138, 104), 'skin_l': (236, 192, 158), 'eye_w': (240, 236, 228), 'eye': (36, 30, 28),
    'brow': (58, 38, 24), 'beard': (92, 58, 34), 'beard_d': (66, 40, 22), 'beard_l': (116, 76, 46), 'lip': (120, 70, 56), 'scar': (244, 206, 186),
    'tattoo': (40, 58, 56), 'tunic': (84, 96, 70), 'tunic_d': (64, 74, 52), 'tunic_l': (102, 114, 86), 'leather': (98, 60, 36), 'leather_d': (70, 42, 24),
    'trousers': (58, 54, 46), 'trousers_d': (44, 40, 34), 'boots': (84, 52, 32), 'boots_d': (60, 36, 22), 'iron': (128, 132, 136), 'iron_d': (90, 92, 96),
    'bead': (176, 150, 96),
}
P = {}
def put(part, x, y, z, c): P.setdefault(part, {})[(x, y, z)] = c
def rbox(part, x0, x1, y0, y1, z0, z1, c, bev=1, top_bev=False):
    """a box with its vertical edges bevelled (and optionally its top edges): the references' chunky, softened blocks"""
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                ex = (x - x0 < bev) + (x1 - x < bev); ey = (y - y0 < bev) + (y1 - y < bev)
                if ex and ey: continue
                if top_bev and z == z1 and (ex or ey): continue
                put(part, x, y, z, c(x, y, z) if callable(c) else c)

LIFT = 4   # the legs are this much shorter than first drawn; everything above them drops by it (applied at the end)
# ---- boots, legs: short and thick; boots big, toes forward, a turned cuff
for side, (x0, x1) in (('l', (11, 18)), ('r', (1, 8))):      # thick, almost touching
    rbox('foot_' + side, x0, x1, -2, 7, 0, 3, lambda x, y, z: 'boots_d' if z == 0 else 'boots')
    rbox('foot_' + side, x0, x1, 0, 7, 4, 6, 'boots')
    rbox('leg_lower_' + side, x0 - 1, x1 + 1, -1, 8, 7, 8, 'boots_d')                    # the cuff
    rbox('leg_lower_' + side, x0, x1, 0, 7, 9, 16, 'trousers')
    rbox('leg_upper_' + side, x0, x1, 0, 7, 17, 30 - LIFT, lambda x, y, z: 'trousers_d' if (x in (x0, x1) and z % 3 == 0) else 'trousers')

# ---- torso: wide chest tapering to the waist, the tunic with a dark hem, a belt with a round iron buckle, a laced V neck
for z in range(31, 53):
    w = 0 if z >= 44 else (1 if z >= 37 else (2 if z >= 34 else 1))          # how far each side is pulled in (waist)
    d = 0 if z >= 40 else 1
    def col(x, y, z=z):
        if z <= 32: return 'leather_d' if z == 31 else 'leather'
        if z == 33: return 'tunic_d'
        if y <= d and 8 <= x <= 11 and z >= 48 - (11 - x if x >= 10 else x - 8) * 0: return 'skin' if z >= 49 and 9 <= x <= 10 else ('leather_d' if z >= 47 and x in (8, 11) and z % 2 == 0 else 'tunic')
        return 'tunic'
    rbox('torso', w, 19 - w, d, 9 - d, z, z, col, bev=2 if z >= 44 else 1)
for x, z in ((9, 31), (10, 31), (9, 32), (10, 32), (8, 32), (11, 32)): put('torso', x, 0 if z > 31 else 1, z, 'iron')   # the buckle
put('torso', 9, -1, 32, 'iron_d'); put('torso', 10, -1, 32, 'iron_d')

# ---- arms: thick, short tunic sleeves, bare forearms with leather bracers, big fists with knuckles
for side, (x0, x1) in (('l', (20, 25)), ('r', (-6, -1))):
    rbox('arm_upper_' + side, x0, x1, 2, 7, 41, 52, lambda x, y, z: 'tunic' if z >= 45 else 'skin', top_bev=True)
    rbox('arm_lower_' + side, x0, x1, 2, 7, 31, 40, 'skin')
    rbox('arm_lower_' + side, x0 - 1 if side == 'r' else x0, x1 if side == 'r' else x1 + 1, 1, 8, 31, 36, lambda x, y, z: 'leather_d' if z in (31, 36) else 'leather')
    rbox('hand_' + side, x0, x1, 1, 8, 25, 30, lambda x, y, z: 'skin_d' if (y == 1 and z in (26, 28)) else 'skin')
    for z in (26, 27, 28): put('hand_' + side, x0 + 1 if side == 'l' else x1 - 1, 0, z, 'skin')   # the thumb, forward

# ---- the head: 14 wide, 13 deep, 15 tall, bevelled; the face drawn on its front (rows from the top, columns across)
FACE = [   # S skin, T tattoo, B brow, W eye white, P pupil, N nose, n nose shadow, X scar, M moustache, L lip, R beard, . none
    "..SSSSSSSSSS..",
    ".SSSTTSSSTTSS.",
    "SSSSSTTTTSSSSS",
    "SSSSSSSSSSSSSS",
    "SBBBBSSSSBBXBS",
    "SSBBBSSSSBBXSS",
    "SSWPSSSSSSPXSS",
    "SSWPSSNNSSPWSS",
    "SSSSSSNNSSSXSS",
    "SSSSSnNNnSSSSS",
    "SRRSMMMMMMSRRS",
    "SRRRMLLLLMRRRS",
    "RRRRRRRRRRRRRR",
    ".RRRRRRRRRRRR.",
    "..RRRRRRRRRR..",
]
KEY = {'S': 'skin', 'T': 'tattoo', 'B': 'brow', 'W': 'eye_w', 'P': 'eye', 'N': 'skin', 'n': 'skin_d', 'X': 'scar', 'M': 'beard_d', 'L': 'lip', 'R': 'beard'}
HX0, HY0, HZ0, HW, HD, HH = 3, -2, 53, 14, 13, 15
for row, line in enumerate(FACE):
    z = HZ0 + HH - 1 - row
    for i, ch in enumerate(line):
        if ch == '.': continue
        x = HX0 + HW - 1 - i            # the map is drawn as you face the character
        for y in range(HY0, HY0 + HD):
            edge_x = i in (0, HW - 1); edge_y = y in (HY0, HY0 + HD - 1)
            if edge_x and edge_y: continue
            deep = y - HY0
            if deep == 0: c = KEY[ch]
            elif ch == 'R' and deep <= 7: c = 'beard_d' if deep >= 5 else 'beard'          # the beard wraps round the jaw
            elif row <= 3 and (x + y) % 5 == 0 and deep >= 2: c = 'tattoo'                  # knotwork on the scalp
            else: c = 'skin'
            put('head', x, y, z, c)
# the nose and moustache stand out from the face; the beard is full under the chin
for row, line in enumerate(FACE):
    z = HZ0 + HH - 1 - row
    for i, ch in enumerate(line):
        x = HX0 + HW - 1 - i
        if ch in 'NM' or (ch == 'R' and row >= 12): put('head', x, HY0 - 1, z, 'skin' if ch == 'N' else ('beard_d' if ch == 'M' else 'beard'))
# ears
for side in (HX0 - 1, HX0 + HW):
    for z in (HZ0 + 6, HZ0 + 7, HZ0 + 8):
        for y in (HY0 + 5, HY0 + 6): put('head', side, y, z, 'skin_d' if z == HZ0 + 6 else 'skin')
# the braid under the beard, with two beads, and the beard's underside
for z in range(HZ0 - 10, HZ0 - 3):
    for x in (HX0 + 6, HX0 + 7):
        for y in (HY0, HY0 + 1):
            put('braid@head', x, y, z, 'bead' if z in (HZ0 - 6, HZ0 - 9) else ('beard_l' if (z + x) % 2 else 'beard'))   # rides on the head

# the beard hangs over the chest: two more rows below the chin, narrowing, darker underneath
for k, (a, b) in enumerate(((3, 10), (4, 9))):
    z = HZ0 - 1 - k
    for x in range(HX0 + a, HX0 + b + 1):
        for y in range(HY0 - 1, HY0 + 4): put('beard@head', x, y, z, 'beard_d' if (y == HY0 + 3 or (x + z) % 3 == 0) else 'beard')
# beard texture: streaks of dark and light down its front
for (x, y, z), c in list(P['head'].items()):
    if c == 'beard' and y <= HY0 and (x * 7 + z * 3) % 5 == 0: P['head'][(x, y, z)] = 'beard_d' if z % 2 else 'beard_l'
for part in list(P):
    if not part.startswith(('foot', 'leg')): P[part] = {(x, y, z - LIFT): c for (x, y, z), c in P[part].items()}
mb.COL = PAL; mb.NAMES = list(PAL)
mb.write(os.path.join(HERE, '..', '..', 'godot', 'assets', 'voxel', 'characters', 'hrim_stylized.vox'), P)
