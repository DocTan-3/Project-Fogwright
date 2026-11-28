# Fogwright's detailed voxel character bases at 2.5 cm (docs/design.md, Voxel art): fine enough for steampunk tubes, hoses,
# buckles and faces. Shaped, not boxed: tapered limbs and a torso with chest, waist and hips in elliptic sections, a head
# with jaw, nose, ears, eyes and brows, separate hands (with thumbs) and feet. Plain colours in two or three tones each,
# ready to recolour per people and outfit. Each body part is a named model; layered gear is named "<piece>@<part>" and
# rides on that part (godot/scripts/voxel/vox.gd).
#   python3 tools/voxel/make_base_hd.py   -> godot/assets/voxel/characters/base_m_hd.vox, base_f_hd.vox, gear_test_hd.vox
# Axes as MagicaVoxel: x across the body, y front (small) to back, z up. One voxel is 2.5 cm: the man is 72 tall (1.80 m).
import math, os, struct, importlib.util
spec = importlib.util.spec_from_file_location('mb', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'make_base.py'))

PAL = [   # name, colour; each material has a base and darker/lighter tones
    ('skin', (214, 160, 122)), ('skin_d', (186, 130, 98)), ('skin_l', (228, 180, 144)), ('lip', (170, 104, 88)),
    ('eye_w', (236, 232, 222)), ('eye', (40, 52, 64)), ('brow', (60, 42, 30)),
    ('hair', (74, 52, 36)), ('hair_d', (54, 38, 26)), ('hair_l', (96, 70, 48)),
    ('shirt', (220, 208, 184)), ('shirt_d', (190, 176, 150)), ('shirt_l', (234, 224, 204)), ('button', (120, 96, 70)),
    ('trousers', (78, 62, 50)), ('trousers_d', (60, 47, 38)), ('trousers_l', (94, 76, 62)),
    ('boots', (70, 48, 34)), ('boots_d', (50, 34, 24)), ('boots_l', (92, 64, 44)), ('sole', (32, 24, 18)), ('lace', (150, 120, 84)),
    ('belt', (112, 76, 44)), ('belt_d', (86, 58, 34)), ('brass', (198, 156, 76)), ('brass_d', (150, 112, 50)), ('brass_l', (228, 196, 120)),
    ('leather', (104, 70, 44)), ('glass', (70, 130, 140)), ('glass_l', (150, 200, 205)), ('copper', (176, 100, 62)), ('hose', (44, 40, 38)), ('hose_l', (66, 60, 56)),
    ('iron', (84, 86, 90)),
]
NAMES = [n for n, _ in PAL]

def h(x, y, z): return ((x * 73856093) ^ (y * 19349663) ^ (z * 83492791)) & 1023

def tone(c, x, y, z):
    """break up flat colour: a few voxels a shade lighter or darker, as a hand-painted model would"""
    r = h(x, y, z)
    if c + '_d' in NAMES and r < 140: return c + '_d'
    if c + '_l' in NAMES and r > 900: return c + '_l'
    return c

def ell(x, y, cx, cy, rx, ry): return ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2

def lerp(a, b, t): return a + (b - a) * max(0.0, min(1.0, t))

def prof(z, pts):   # piecewise-linear profile [(z, value), ...]
    for (z0, a), (z1, b) in zip(pts, pts[1:]):
        if z0 <= z <= z1: return lerp(a, b, (z - z0) / max(1e-6, z1 - z0))
    return pts[0][1] if z < pts[0][0] else pts[-1][1]

def body(sex):
    f = sex == 'f'
    K = 68 / 72 if f else 1.0               # the woman is 1.70 m
    Z = lambda v: int(round(v * K))
    P = {}
    def put(part, x, y, z, c): P.setdefault(part, {})[(x, y, z)] = c
    CX, CY = 20.0, 8.0
    ankle, knee, hip = Z(4), Z(20), Z(37)
    # feet: a boot shoe, the sole dark, laces up the front
    for side, lx in (('l', CX - 4.5), ('r', CX + 4.5)):
        for z in range(0, ankle + 1):
            for x in range(int(lx - 4), int(lx + 4)):
                for y in range(0, 16):
                    toe = 3 if z <= 1 else 4
                    if ell(x, y, lx, 9.0, 2.6, 6.0 - (0 if z <= 2 else 1.2)) <= 1 and y >= toe:
                        c = 'sole' if z == 0 else 'boots'
                        if z >= 2 and y <= toe and abs(x + 0.5 - lx) < 1: c = 'lace'
                        put('foot_' + side, x, y, z, tone(c, x, y, z))
        # lower leg: a calf that bulges, the boot to mid-calf with a turned top
        for z in range(ankle + 1, knee + 1):
            rx = prof(z, [(ankle, 2.1), (Z(12), 2.7), (knee, 2.4)]); ry = rx * 1.05
            boot = z <= Z(13)
            if z == Z(13) + 1: rx += 0.0
            for x in range(int(lx - 4), int(lx + 4)):
                for y in range(3, 14):
                    if ell(x, y, lx, CY + 0.5, rx + (0.45 if boot else 0), ry + (0.45 if boot else 0)) <= 1:
                        c = 'boots' if boot else 'trousers'
                        if z == Z(13): c = 'boots_l'
                        if boot and abs(x + 0.5 - lx) < 1 and y <= CY - ry + 1 and z % 2 == 0: c = 'lace'
                        put('leg_lower_' + side, x, y, z, tone(c, x, y, z))
        for z in range(knee + 1, hip + 1):
            rx = prof(z, [(knee, 2.5), (hip, 3.6 if not f else 3.9)]); ry = rx * 1.08
            for x in range(int(lx - 5), int(lx + 5)):
                for y in range(2, 15):
                    if ell(x, y, lx, CY, rx, ry) <= 1:
                        c = 'trousers'
                        if abs(x + 0.5 - (lx + (rx - 0.6) * (1 if side == 'r' else -1))) < 0.6: c = 'trousers_d'   # the outer seam
                        put('leg_upper_' + side, x, y, z, tone(c, x, y, z))
    # torso: hips, waist, chest, shoulders, neck in elliptic sections; trousers, a belt with a brass buckle, the shirt with a
    # placket and buttons, an open collar
    waist, belt0, chest, shoulder, neck_top = Z(44), Z(40), Z(52), Z(57), Z(61)
    if f:
        RX = [(hip + 1, 8.2), (waist, 6.4), (chest, 7.4), (shoulder, 7.8), (shoulder + 1, 5.0), (shoulder + 2, 2.2), (neck_top, 2.0)]
        RY = [(hip + 1, 4.3), (waist, 3.7), (chest, 4.4), (shoulder, 3.8), (shoulder + 1, 3.0), (shoulder + 2, 2.0), (neck_top, 2.0)]
    else:
        RX = [(hip + 1, 7.6), (waist, 7.0), (chest, 8.6), (shoulder, 9.0), (shoulder + 1, 6.0), (shoulder + 2, 2.4), (neck_top, 2.2)]
        RY = [(hip + 1, 4.2), (waist, 3.9), (chest, 4.7), (shoulder, 4.0), (shoulder + 1, 3.2), (shoulder + 2, 2.2), (neck_top, 2.2)]
    for z in range(hip + 1, neck_top + 1):
        rx = prof(z, RX); ry = prof(z, RY)
        bust = f and Z(48) <= z <= Z(53)
        for x in range(0, 41):
            for y in range(0, 16):
                cy = CY - (0.9 * math.sin(math.pi * (z - Z(48)) / max(1, Z(53) - Z(48))) if bust else 0)
                if ell(x, y, CX, cy, rx, ry + (0.9 * math.sin(math.pi * (z - Z(48)) / max(1, Z(53) - Z(48))) if bust else 0)) > 1: continue
                front = y + 0.5 < CY - ry * 0.6
                if z < belt0: c = 'trousers'
                elif z < belt0 + 2: c = 'belt' if not (front and abs(x + 0.5 - CX) < 1.6) else 'brass'
                elif z >= shoulder + 2: c = 'skin'
                else:
                    c = 'shirt'
                    if front and abs(x + 0.5 - CX) < 0.7: c = 'shirt_d' if (z - belt0) % 4 else 'button'
                    if front and z >= shoulder - 2 and abs(x + 0.5 - CX) < (z - shoulder + 3) * 0.8: c = 'skin'   # the open collar
                    if front and z == shoulder - 3 and abs(x + 0.5 - CX) < 2.6: c = 'shirt_l'
                put('torso', x, y, z, tone(c, x, y, z))
    # arms: shoulders at the torso's edge, the sleeves to the wrist with a cuff, hands with a thumb
    for side, sgn in (('l', -1), ('r', 1)):
        ax = CX + sgn * ((7.6 if f else 9.0) + 1.7)
        elbow, wrist, tip = Z(45), Z(33), Z(27)
        for z in range(elbow + 1, shoulder + 1):
            rx = prof(z, [(elbow, 1.9), (shoulder, 2.5 if not f else 2.2)])
            for x in range(int(ax - 4), int(ax + 4)):
                for y in range(3, 14):
                    if ell(x, y, ax, CY, rx, rx * 1.1) <= 1: put('arm_upper_' + side, x, y, z, tone('shirt', x, y, z))
        for z in range(wrist + 1, elbow + 1):
            rx = prof(z, [(wrist, 1.55), (elbow - 2, 2.0), (elbow, 1.9)])
            for x in range(int(ax - 4), int(ax + 4)):
                for y in range(3, 14):
                    if ell(x, y, ax, CY, rx, rx * 1.1) <= 1:
                        c = 'shirt_d' if z <= wrist + 2 else 'shirt'
                        put('arm_lower_' + side, x, y, z, tone(c, x, y, z))
        for z in range(tip, wrist + 1):
            for x in range(int(ax - 3), int(ax + 3)):
                for y in range(4, 13):
                    w = 1.3 if z > tip + 2 else 1.1
                    if ell(x, y, ax, CY, w, 1.9 if z > tip + 1 else 1.6) <= 1:
                        c = 'skin_d' if z == tip + 2 and (y + 0.5) < CY else 'skin'                  # the finger joints
                        put('hand_' + side, x, y, z, c)
            if tip + 2 <= z <= wrist - 1:   # the thumb, forward and toward the body
                tx = int(ax - sgn * 1.0); put('hand_' + side, tx, int(CY - 2.4), z, 'skin_d' if z == tip + 2 else 'skin')
    # head: an egg with a narrower jaw; eyes (white and iris), brows, a nose standing out, lips, ears; hair as a shell
    hz0 = neck_top + 1; hc = hz0 + 5.4; HR = (4.8, 5.3, 5.9)
    for z in range(hz0, hz0 + 11):
        for x in range(0, 41):
            for y in range(0, 16):
                dz = (z + 0.5 - hc) / HR[2]
                jaw = lerp(0.72, 1.0, (z - hz0) / 4.5)
                d = ((x + 0.5 - CX) / (HR[0] * jaw)) ** 2 + ((y + 0.5 - CY) / HR[1]) ** 2 + dz * dz
                if d > 1: continue
                hair_line = hz0 + (7 if f else 8)
                outer = d > 0.6
                c = 'skin'
                if outer and (z >= hair_line or (y + 0.5 > CY + 0.5 and z >= hz0 + 4) or (y + 0.5 > CY - 1 and z >= hz0 + 6 and abs(x + 0.5 - CX) > 3.4)):
                    c = tone('hair', x, y, z)
                put('head', x, y, z, c)
    face_y = min(y for (x, y, z) in P['head'] if z == hz0 + 5)
    ez = hz0 + 5
    for sx in (-1, 1):
        ex = int(CX + sx * 2.0 - (1 if sx < 0 else 0))
        put('head', ex, face_y, ez, 'eye_w'); put('head', ex + (1 if sx < 0 else -1), face_y, ez, 'eye')
        for k in range(3): put('head', int(CX + sx * (1.2 + k) - (1 if sx < 0 else 0)), face_y, ez + 2 - (1 if k == 2 else 0), 'brow')
        put('head', int(CX + sx * 5.0 - (1 if sx < 0 else 0)), int(CY), ez - 1, 'skin_d'); put('head', int(CX + sx * 5.0 - (1 if sx < 0 else 0)), int(CY), ez, 'skin')   # ears
    for z in (ez - 2, ez - 1, ez): put('head', int(CX), face_y - 1, z, 'skin' if z > ez - 2 else 'skin_d')   # the nose
    put('head', int(CX) - 1, face_y, ez - 2, 'skin_d'); put('head', int(CX), face_y, ez - 2, 'skin_d')
    for x in range(int(CX) - 1, int(CX) + 2): put('head', x, face_y, ez - 4, 'lip')
    if f:   # long hair: down the back to the shoulder blades, a parting
        for z in range(hz0 - 4, hz0 + 8):
            for x in range(int(CX - 5), int(CX + 5)):
                for y in range(int(CY + 2), int(CY + 7)):
                    if ell(x, y, CX, CY + 2, 5.2, 4.6) <= 1 and (x, y, z) not in P['head']: put('head', x, y, z, tone('hair', x, y, z))
    return P

def gear():
    """a steampunk test piece on the man: goggles on the brow, a brass tank on the back, a hose from the tank over the
    right shoulder to a gauge on the chest - the thin parts (hose, strap, gauge rim) that need small voxels"""
    P = {}
    def put(part, x, y, z, c): P.setdefault(part, {})[(x, y, z)] = c
    CX, CY = 20.0, 8.0
    hz0 = 62; bz = hz0 + 8   # the goggles sit on the brow, above the eyes
    for sx in (-1, 1):
        gx = CX + sx * 2.1
        for x in range(int(gx - 3), int(gx + 3)):
            for z in range(bz - 2, bz + 3):
                r = math.hypot(x + 0.5 - gx, z + 0.5 - bz)
                if r <= 2.0: put('goggles@head', x, 2, z, 'brass' if r > 1.2 else ('glass_l' if (x + z) % 3 == 0 else 'glass'))
                if 1.2 < r <= 2.0: put('goggles@head', x, 1, z, 'brass_d')
    for k in range(-60, 61):   # the strap round the head
        a = math.radians(k * 3); x = int(CX + math.sin(a) * 5.4); y = int(CY - math.cos(a) * 5.9)
        if y >= 3: put('goggles@head', x, y, bz, 'leather')
    # the tank: an upright brass cylinder with banded caps and rivets, on the back
    tx, ty = CX, CY + 7.5
    for z in range(44, 58):
        for x in range(int(tx - 4), int(tx + 5)):
            for y in range(int(ty - 4), int(ty + 5)):
                r = math.hypot(x + 0.5 - tx, y + 0.5 - ty)
                if r <= 3.4:
                    c = 'brass_d' if z in (44, 45, 56, 57) else ('brass_l' if (x + 0.5 - tx) < -1.8 else 'brass')
                    if 3.0 < r and z in (47, 53) and (x + y) % 2 == 0: c = 'iron'
                    put('tank@torso', x, y, z, c)
    for z in (58, 59): put('tank@torso', int(tx), int(ty), z, 'copper')   # the valve
    # the hose: a 2-voxel tube from the valve over the right shoulder down to a gauge on the chest
    path = [(tx, ty, 59.5), (tx + 4, ty - 1, 61), (tx + 7, CY + 2, 60.5), (tx + 7, CY - 3, 58), (tx + 5, CY - 5.2, 54), (tx + 3, CY - 5.4, 51)]
    for (a, b) in zip(path, path[1:]):
        n = 24
        for i in range(n + 1):
            t = i / n; p = [a[j] + (b[j] - a[j]) * t for j in range(3)]
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        q = (int(p[0] + dx * 0.5), int(p[1] + dy * 0.5), int(p[2] + dz * 0.5))
                        put('hose@torso', *q, 'hose_l' if (i % 6 == 0) else 'hose')
    gx, gz = tx + 3, 51   # the gauge: a brass rim, a pale face, a needle
    for x in range(int(gx - 3), int(gx + 3)):
        for z in range(gz - 3, gz + 3):
            r = math.hypot(x + 0.5 - gx, z + 0.5 - gz)
            if r <= 2.2: put('gauge@torso', x, 2, z, 'brass' if r > 1.4 else ('iron' if (x == int(gx) and z >= gz) else 'shirt_l'))
    return P

def write(path, parts):
    mb = importlib.util.module_from_spec(spec)
    src = open(spec.origin).read(); src = src[:src.index('OUT = ')]
    exec(compile(src, spec.origin, 'exec'), mb.__dict__)
    mb.COL = dict(PAL); mb.NAMES = NAMES
    mb.write(path, parts)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'godot', 'assets', 'voxel', 'characters')
for sx in ('m', 'f'): write(os.path.join(OUT, 'base_%s_hd.vox' % sx), body(sx))
write(os.path.join(OUT, 'gear_test_hd.vox'), gear())
