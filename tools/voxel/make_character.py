# Fogwright's voxel character generator: any people, either sex, in the approved stylized look (make_stylized.py's
# Hrimfolk man): a big bevelled head with a face drawn as a pixel map, a short broad neckless body, thick arms with big
# fists, short sturdy legs, big boots, flat colours with a darker and lighter tone. docs/characters.md has the peoples.
#   python3 tools/voxel/make_character.py                 -> godot/assets/voxel/characters/peoples/<people>_<m|f>.vox
# 2.5 cm voxels; MagicaVoxel axes: x across (0 = the character's right seen from the front), y front (small) to back, z up.
# Skin colours stay within real skin's reflectance (pale skin reflects about 60% of light, sRGB about 200 at most): brighter
# values flare yellow or white under the game's sun.
# Every character fits the standard door: at most 72 voxels (1.8 m) tall, 36 (0.9 m) across with its arms.
import os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('mb', os.path.join(HERE, 'make_base.py')); mb = importlib.util.module_from_spec(spec)
src = open(spec.origin).read(); exec(compile(src[:src.rindex('\nOUT = ')], spec.origin, 'exec'), mb.__dict__)

# ---- the peoples: proportions in voxels (men; women adjust below), colours, hair and beards, signature
# UL/LL upper and lower leg, TH torso, TW/TD torso width and depth, AW arm width, AU/AL upper and lower arm, LW leg width
PEOPLES = {
 'hrimfolk': dict(UL=10, LL=8, TH=22, TW=20, TD=10, AW=6, AU=12, AL=10, LW=8,
                  skin=(200, 158, 134), hair_m=(92, 58, 34), hair_f=(206, 168, 100), eye=(70, 110, 140), tunic=(84, 96, 70), trousers=(58, 54, 46),
                  leather=(98, 60, 36), bracers=True, hair=('shaved', 'braids'), beard='full_braid', mark='knotwork'),
 'ruadhan':  dict(UL=10, LL=9, TH=20, TW=18, TD=9, AW=6, AU=12, AL=10, LW=7,
                  skin=(204, 168, 148), hair_m=(176, 72, 36), hair_f=(196, 88, 40), eye=(70, 120, 70), tunic=(70, 100, 60), trousers=(96, 70, 46),
                  leather=(110, 70, 40), bracers=True, hair=('crop', 'long'), beard='short', mark='freckles'),
 'aurelan':  dict(UL=9, LL=8, TH=20, TW=18, TD=9, AW=6, AU=11, AL=10, LW=7,
                  skin=(174, 132, 98), hair_m=(70, 44, 30), hair_f=(78, 50, 34), eye=(96, 70, 40), tunic=(70, 80, 130), trousers=(90, 70, 56),
                  leather=(90, 58, 40), bracers=False, hair=('crop', 'bun'), beard='moustache', mark=None),
 'zarhim':   dict(UL=9, LL=8, TH=20, TW=16, TD=9, AW=5, AU=11, AL=10, LW=7,
                  skin=(108, 72, 50), hair_m=(30, 24, 22), hair_f=(34, 26, 24), eye=(150, 100, 40), tunic=(196, 168, 120), trousers=(150, 120, 86),
                  leather=(120, 80, 50), bracers=True, hair=('crop', 'long'), beard='short', mark=None),
 'ilvari':   dict(UL=11, LL=9, TH=19, TW=16, TD=8, AW=5, AU=12, AL=11, LW=6,
                  skin=(170, 156, 160), hair_m=(36, 38, 48), hair_f=(186, 192, 204), eye=(150, 190, 220), tunic=(40, 48, 70), trousers=(34, 36, 44),
                  leather=(70, 60, 60), bracers=False, hair=('long', 'long'), beard=None, mark='ink'),
 'ferrin':   dict(UL=7, LL=5, TH=18, TW=22, TD=11, AW=7, AU=10, AL=9, LW=8,
                  skin=(172, 110, 86), hair_m=(52, 34, 24), hair_f=(60, 40, 28), eye=(50, 36, 28), tunic=(110, 70, 46), trousers=(60, 52, 46),
                  leather=(70, 48, 34), bracers=True, hair=('crop', 'crown'), beard='big', mark='soot'),
 'wayfolk':  dict(UL=9, LL=8, TH=20, TW=18, TD=9, AW=6, AU=11, AL=10, LW=7,
                  skin=(184, 142, 110), hair_m=(100, 70, 46), hair_f=(110, 76, 50), eye=(90, 70, 50), tunic=(140, 110, 80), trousers=(80, 70, 60),
                  leather=(96, 64, 40), bracers=False, hair=('crop', 'long'), beard='stubble', mark=None),
 'penitent': dict(UL=9, LL=8, TH=20, TW=16, TD=8, AW=5, AU=11, AL=10, LW=6,
                  skin=(164, 150, 142), hair_m=(60, 56, 52), hair_f=(66, 60, 56), eye=(170, 170, 176), tunic=(100, 96, 92), trousers=(60, 58, 56),
                  leather=(70, 60, 50), bracers=False, hair=('crop', 'crop'), beard=None, mark='veins'),
}
WOMAN = dict(UL=0, LL=0, TH=-2, TW=-2, TD=-1, AW=-1, AU=-1, AL=-1, LW=-1)
# a woman's frame: shoulders pulled in (SH), hips at full width, a defined waist, a bust, smaller hands and feet, a softer jaw
HEAD = {'ilvari': (12, 12)}   # narrower, shallower heads (width, depth); others 14 x 13

def tone(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)
def build(people, sex):
    p = dict(PEOPLES[people])
    if sex == 'f':
        for k, v in WOMAN.items(): p[k] += v
    hair_col = p['hair_f' if sex == 'f' else 'hair_m']
    PAL = {'skin': p['skin'], 'skin_d': tone(p['skin'], 0.86), 'skin_l': tone(p['skin'], 1.07), 'eye_w': (240, 236, 228), 'eye': p['eye'],
           'brow': tone(hair_col, 0.7), 'hair': hair_col, 'hair_d': tone(hair_col, 0.72), 'hair_l': tone(hair_col, 1.25),
           'lip': tone(p['skin'], 0.62) if sex == 'm' else (150, 78, 70), 'scar': tone(p['skin'], 1.12),
           'tunic': p['tunic'], 'tunic_d': tone(p['tunic'], 0.76), 'leather': p['leather'], 'leather_d': tone(p['leather'], 0.72),
           'trousers': p['trousers'], 'trousers_d': tone(p['trousers'], 0.78), 'boots': (84, 52, 32), 'boots_d': (60, 36, 22),
           'iron': (128, 132, 136), 'iron_d': (90, 92, 96), 'bead': (176, 150, 96),
           'ink': (56, 116, 210), 'tattoo': (40, 58, 56), 'vein': tone(p['skin'], 0.7), 'soot': tone(p['skin'], 0.55), 'freckle': tone(p['skin'], 0.78), 'stub': tone(p['skin'], 0.8), 'cheek': (min(255, p['skin'][0] + 12), int(p['skin'][1] * 0.86), int(p['skin'][2] * 0.86))}
    P = {}
    def put(part, x, y, z, c): P.setdefault(part, {})[(x, y, z)] = c
    def rbox(part, x0, x1, y0, y1, z0, z1, c, bev=1, top_bev=False):
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in range(z0, z1 + 1):
                    ex = (x - x0 < bev) + (x1 - x < bev); ey = (y - y0 < bev) + (y1 - y < bev)
                    if ex and ey: continue
                    if top_bev and z == z1 and (ex or ey): continue
                    put(part, x, y, z, c(x, y, z) if callable(c) else c)
    TW, TD, LW, AW = p['TW'], p['TD'], p['LW'], p['AW']
    # ---- boots and legs
    x0r = (TW - 2 * LW - 2) // 2; x0l = TW - 1 - x0r - LW + 1
    hip = 6 + 2 + p['LL'] + p['UL']
    for side, x0 in (('l', x0l), ('r', x0r)):
        x1 = x0 + LW - 1; yc = (TD - 8) // 2
        rbox('foot_' + side, x0, x1, yc - (1 if sex == 'f' else 2), yc + 7, 0, 3, lambda x, y, z: 'boots_d' if z == 0 else 'boots')
        rbox('foot_' + side, x0, x1, yc, yc + 7, 4, 6, 'boots')
        rbox('leg_lower_' + side, x0 - 1, x1 + 1, yc - 1, yc + 8, 7, 8, 'boots_d')
        rbox('leg_lower_' + side, x0, x1, yc, yc + 7, 9, 8 + p['LL'], 'trousers')
        rbox('leg_upper_' + side, x0, x1, yc, yc + 7, 9 + p['LL'], hip, lambda x, y, z, x0=x0, x1=x1: 'trousers_d' if (x in (x0, x1) and z % 3 == 0) else 'trousers')
    # ---- torso: chest tapering to the waist (a woman's waist narrower, her hips wider at the belt), belt, laced V neck
    top = hip + p['TH']; cx = TW // 2; SH = 1 if sex == 'f' else 0
    for z in range(hip + 1, top + 1):
        r = z - hip - 1; up = r >= 3 + 3 + (p['TH'] - 6) * 7 // 16
        if sex == 'f':     # full hips at the belt, a narrow waist, the chest and shoulders pulled in by SH
            w = 0 if r <= 3 else (1 if r <= 4 else (3 if not up else SH))
        elif r <= 2: w = 1
        elif r <= 5: w = 2
        else: w = 0 if up else 1
        d = 0 if r >= 9 else 1
        def col(x, y, z=z, r=r, d=d):
            if r <= 1: return 'leather_d' if r == 0 else 'leather'
            if r == 2: return 'tunic_d'
            if y <= d and cx - 2 <= x <= cx + 1 and z >= top - 4: return 'skin' if z >= top - 3 and cx - 1 <= x <= cx else ('leather_d' if x in (cx - 2, cx + 1) and z % 2 == 0 else 'tunic')
            return 'tunic'
        rbox('torso', w, TW - 1 - w, d, TD - 1 - d, z, z, col, bev=2 if up else 1)
    if sex == 'f':     # the bust: two soft forms on the upper chest
        for k, z in enumerate(range(top - 9, top - 4)):
            inset = 1 if k in (0, 4) else 0
            for x in list(range(SH + 1 + inset, cx - 1 - inset)) + list(range(cx + 1 + inset, TW - 1 - SH - inset)):
                put('torso', x, -1, z, 'tunic_d' if k == 0 else 'tunic')
    if p['mark'] == 'veins':     # healed scourge scars, diagonal across the back (through the tunic's wear: shown on a bare back later)
        for k in range(5):
            zb = top - 4 - k * 3
            for x in range(2, TW - 2):
                if (x + k) % 6 < 4: put('torso', x, TD, zb - x // 4, 'scar')
    for x in range(cx - 1, cx + 1): put('torso', x, 0, hip + 2, 'iron'); put('torso', x, -1, hip + 2, 'iron_d')
    # ---- arms: sleeves, bare forearms (bracers for some peoples), big fists with a thumb
    ay0 = (TD - AW) // 2
    for side, (x0, x1) in (('l', (TW - SH, TW - SH + AW - 1)), ('r', (SH - AW, SH - 1))):
        au0 = top - p['AU'] + 1; al0 = au0 - p['AL']; h0 = al0 - (5 if sex == 'f' else 6)
        sleeve = top - p['AU'] * 2 // 3
        rbox('arm_upper_' + side, x0, x1, ay0, ay0 + AW - 1, au0, top, lambda x, y, z: 'tunic' if z >= sleeve else 'skin', top_bev=True)
        rbox('arm_lower_' + side, x0, x1, ay0, ay0 + AW - 1, al0, au0 - 1, 'skin')
        if p['bracers']:
            rbox('arm_lower_' + side, x0 - 1 if side == 'r' else x0, x1 if side == 'r' else x1 + 1, ay0 - 1, ay0 + AW, al0, al0 + 5,
                 lambda x, y, z: 'leather_d' if z in (al0, al0 + 5) else 'leather')
        rbox('hand_' + side, x0, x1, ay0 - 1, ay0 + AW, h0, al0 - 1, lambda x, y, z: 'skin_d' if (y == ay0 - 1 and z in (h0 + 1, h0 + 3)) else 'skin')
        for z in ((h0 + 1, h0 + 2) if sex == 'f' else (h0 + 1, h0 + 2, h0 + 3)): put('hand_' + side, x0 + 1 if side == 'l' else x1 - 1, ay0 - 2, z, 'skin')
        if p['mark'] == 'ink':
            for z in (h0 + 2, h0 + 3, h0 + 4): put('hand_' + side, x0 + AW // 2, ay0 + AW, z, 'ink')
        # marks on the bare forearm
        mz = al0 + (6 if p['bracers'] else 1)
        for z in range(mz, au0):
            for x in range(x0, x1 + 1):
                k = (x * 3 + z * 5) % 7
                if p['mark'] == 'knotwork' and z % 2 == 0 and k < 3: put('arm_lower_' + side, x, ay0, z, 'tattoo')
                if p['mark'] == 'veins' and k == 0: put('arm_lower_' + side, x, ay0, z, 'vein')
                if p['mark'] == 'veins' and side == 'r' and (x + z) % 4 == 0 and z % 3 == 0: put('arm_lower_' + side, x, ay0, z, 'scar')   # old lash scars
                if p['mark'] == 'soot' and k == 1: put('arm_lower_' + side, x, ay0, z, 'soot')
                if p['mark'] == 'ink' and side == 'l' and x == x0 + AW // 2: put('arm_lower_' + side, x, ay0, z, 'ink')
                if p['mark'] == 'freckles' and k == 2 and z % 2: put('arm_lower_' + side, x, ay0, z, 'freckle')
    # ---- the head: 14 wide, 13 deep, 15 tall, the face drawn on its front
    HW, HD = HEAD.get(people, (12, 12) if sex == 'f' and people != 'ferrin' else (14, 13)); HH = 15; HX0 = (TW - HW) // 2; HY0 = -2; HZ0 = top + 1   # women: narrower heads (Ferrin stay broad)
    F = [list(row) for row in (
        "..SSSSSSSSSS..", ".SSSSSSSSSSSS.", "SSSSSSSSSSSSSS", "SSSSSSSSSSSSSS", "SSSSSSSSSSSSSS",
        "SnnnnSSSSnnnnS", "SSWPSSSSSSPWSS", "SSWPSSNNSSPWSS", "SSSSSSNNSSSSSS", "SSSSSnNNnSSSSS",
        "SSSSSSSSSSSSSS", "SSSSSLLLLSSSSS", "SSSSSSSSSSSSSS", ".SSSSSSSSSSSSS."[:14], "..SSSSSSSSSS..")]
    if sex == 'f':
        F[9] = list("SSSSSSNNSSSSSS"); F[11] = list("SSSSSLLLLSSSSS"); F[12] = list(".SSSSSSSSSSSS."); F[13] = list("..SSSSSSSSSS.."); F[14] = list("...SSSSSSSS...")
        F[6] = list("SEWPSSSSSSPWES")      # lashes at the outer corners
        F[5] = list("SSnnSSSSSSnnSS")
    hair_m, hair_f = p['hair']; hs = hair_f if sex == 'f' else hair_m
    if hs != 'shaved':
        for r in range(0, 3):
            for i in range(14):
                if F[r][i] == 'S': F[r][i] = 'H'
        if hs in ('long', 'braids', 'crown', 'bun'):
            for r in range(3, 9): F[r][0] = 'H'; F[r][13] = 'H'
    else:
        F[1] = list(".SSSTTSSSTTSS."); F[2] = list("SSSSSTTTTSSSSS")
    beard = p['beard'] if sex == 'm' else None
    if beard in ('full_braid', 'big'):
        F[10] = list("SRRSMMMMMMSRRS"); F[11] = list("SRRRMLLLLMRRRS"); F[12] = list("RRRRRRRRRRRRRR"); F[13] = list(".RRRRRRRRRRRR."); F[14] = list("..RRRRRRRRRR..")
    elif beard == 'short':
        F[10] = list("SSSSMMMMMMSSSS"); F[11] = list("SRRRMLLLLMRRRS"); F[12] = list("SRRRRRRRRRRRRS"); F[13] = list(".RRRRRRRRRRRR."); F[14] = list("..RRRRRRRRRR..")
    elif beard == 'moustache':
        F[10] = list("SSSSMMMMMMSSSS")
    elif beard == 'stubble':
        for r in (11, 12, 13):
            for i in range(14):
                if F[r][i] == 'S' and 2 <= i <= 11: F[r][i] = 'D'
    if people == 'hrimfolk':   # wind-burnt cheeks
        for r, i in ((8, 2), (8, 3), (9, 2), (8, 10), (8, 11), (9, 11)): F[r][i] = 'C' if F[r][i] == 'S' else F[r][i]
    if p['mark'] == 'ink':      # Ilvari: lines of blue ink down from the eyes and across the brow
        for r in (8, 9, 10): F[r][3] = 'K'; F[r][10] = 'K'
        for i in (5, 6, 7, 8): F[3][i] = 'K'
    if p['mark'] == 'soot':
        for r, i in ((8, 2), (9, 3), (9, 2), (8, 11), (10, 10)): F[r][i] = 'D' if F[r][i] == 'S' else F[r][i]
    if p['mark'] == 'freckles':
        for r, i in ((8, 2), (8, 4), (9, 3), (8, 10), (8, 12), (9, 11)): F[r][i] = 'F' if F[r][i] == 'S' else F[r][i]
    if p['mark'] == 'veins':
        for r, i in ((3, 2), (4, 2), (4, 3), (9, 12), (10, 12), (10, 11)): F[r][i] = 'V' if F[r][i] == 'S' else F[r][i]
    if HW == 12: F = [row[:1] + row[2:12] + row[13:] for row in F]
    KEY = {'S': 'skin', 'T': 'tattoo', 'H': 'hair', 'W': 'eye_w', 'P': 'eye', 'N': 'skin', 'n': 'skin_d', 'M': 'hair_d', 'L': 'lip',
           'R': 'hair', 'D': 'stub' if beard == 'stubble' else 'soot', 'K': 'ink', 'F': 'freckle', 'V': 'vein', 'C': 'cheek', 'E': 'brow'}
    for row in range(HH):
        z = HZ0 + HH - 1 - row
        for i in range(HW):
            ch = F[row][i]
            if ch == '.': continue
            x = HX0 + HW - 1 - i
            for y in range(HY0, HY0 + HD):
                if i in (0, HW - 1) and y in (HY0, HY0 + HD - 1): continue
                deep = y - HY0
                if deep == 0: c = KEY[ch]
                elif ch == 'R' and deep <= 7: c = 'hair_d' if deep >= 5 else 'hair'
                elif hs == 'shaved' and row <= 3 and (x + y) % 5 == 0 and deep >= 2: c = 'tattoo'
                elif hs != 'shaved' and (row <= 2 or (deep >= HD - 4 and row <= (11 if hs in ('long', 'braids', 'crown', 'bun') else 8))
                                         or (i in (0, HW - 1) and row <= (9 if hs != 'crop' else 4))): c = 'hair'
                else: c = 'skin'
                put('head', x, y, z, c)
    for row in range(HH):     # the nose and moustache stand out; a full beard too
        z = HZ0 + HH - 1 - row
        for i in range(HW):
            ch = F[row][i]; x = HX0 + HW - 1 - i
            if ch == 'N' or ch == 'M' or (ch == 'R' and row >= 12): put('head', x, HY0 - 1, z, 'skin' if ch == 'N' else ('hair_d' if ch == 'M' else 'hair'))
    for side in (HX0 - 1, HX0 + HW):     # ears (under long hair)
        for z in (HZ0 + 6, HZ0 + 7, HZ0 + 8):
            for y in (HY0 + 5, HY0 + 6): put('head', side, y, z, 'hair' if hs in ('long', 'braids', 'crown') else ('skin_d' if z == HZ0 + 6 else 'skin'))
    # brows: their own tilted pieces
    tilt = 10 if sex == 'f' else 14
    for name, xs in (('brow_l@head~z%d' % tilt, range(HX0 + HW - 5, HX0 + HW - 1)), ('brow_r@head~z-%d' % tilt, range(HX0 + 1, HX0 + 5))):
        for x in xs:
            for z in ((HZ0 + 9,) if sex == 'f' else (HZ0 + 9, HZ0 + 10)):
                for y in (HY0 - 1, HY0): put(name, x, y, z, 'brow')
    # ---- hair pieces
    if hs == 'long':     # down the back to the shoulders
        for z in range(HZ0 - 6, HZ0 + 6):
            for x in range(HX0 + 1, HX0 + HW - 1):
                for y in (HY0 + HD - 1, HY0 + HD): put('hair@head', x, y, z, 'hair_d' if (x + z) % 4 == 0 else 'hair')
    if hs == 'braids':   # two braids forward over the shoulders, with rings
        for bx in (HX0, HX0 + HW - 2):
            for k in range(12):
                z = HZ0 + 3 - k
                for x in (bx, bx + 1):
                    c = 'iron' if k in (3, 9) else ('hair_l' if (x + k) % 2 else 'hair_d')
                    put('braids@head~x-6', x, HY0 + 4, z, c); put('braids@head~x-6', x, HY0 + 5, z, c)
    if hs == 'bun':
        rbox('bun@head', HX0 + HW // 2 - 3, HX0 + HW // 2 + 2, HY0 + HD - 1, HY0 + HD + 3, HZ0 + 9, HZ0 + 13, 'hair')
    if hs == 'crown':    # Ferrin women: braids wound round the head
        for x in range(HX0, HX0 + HW):
            for y in (HY0 + 1, HY0 + HD - 2):
                put('crown@head', x, y, HZ0 + HH - 3, 'hair_l' if x % 2 else 'hair_d')
        for y in range(HY0 + 1, HY0 + HD - 1):
            for x in (HX0 - 1, HX0 + HW): put('crown@head', x, y, HZ0 + HH - 3, 'hair_l' if y % 2 else 'hair_d')
    # ---- beards that hang
    if beard == 'full_braid':
        for k, (a, b) in enumerate(((3, 10), (4, 9))):
            for x in range(HX0 + a, HX0 + b + 1):
                for y in range(HY0 - 1, HY0 + 4): put('beard@head', x, y, HZ0 - 1 - k, 'hair_d' if (y == HY0 + 3 or (x + k) % 3 == 0) else 'hair')
        for k in range(8):
            for x in (HX0 + 6, HX0 + 7):
                for y in (HY0 - 1, HY0):
                    put('braid@head~x-10z4', x, y, HZ0 - 3 - k, 'iron' if k in (0, 5) else ('bead' if k == 2 else ('hair_l' if (x + k) % 2 else 'hair_d')))
    if beard == 'big':   # Ferrin: a broad beard down the chest, braided at the sides
        for k in range(6):
            a, b = 2 + k // 2, 11 - k // 2
            for x in range(HX0 + a, HX0 + b + 1):
                for y in range(HY0 - 1, HY0 + 4): put('beard@head', x, y, HZ0 - 1 - k, 'hair_d' if (x + k) % 3 == 0 else 'hair')
    return P, PAL

OUT = os.path.join(HERE, '..', '..', 'godot', 'assets', 'voxel', 'characters', 'peoples')
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for people in PEOPLES:
        for sex in ('m', 'f'):
            P, PAL = build(people, sex)
            mb.COL = PAL; mb.NAMES = list(PAL)
            mb.write(os.path.join(OUT, '%s_%s.vox' % (people, sex)), P)
            zs = [z for part in P.values() for (_, _, z) in part]; xs = [x for part in P.values() for (x, _, _) in part]
            print('%-9s %s  %d voxels tall (%.2f m), %d across (%.2f m)' % (people, sex, max(zs) - min(zs) + 1, (max(zs) - min(zs) + 1) * 0.025, max(xs) - min(xs) + 1, (max(xs) - min(xs) + 1) * 0.025))
