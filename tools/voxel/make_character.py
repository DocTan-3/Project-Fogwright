# Fogwright's voxel character generator: any people, either sex, in the approved stylized look (make_stylized.py's
# Hrimfolk man): a big bevelled head with a face drawn as a pixel map, a short broad neckless body, thick arms with big
# fists, short sturdy legs, big boots, flat colours with a darker and lighter tone. docs/characters.md has the peoples.
#   python3 tools/voxel/make_character.py   -> godot/assets/voxel/characters/peoples/<people>_<m|f>.vox (the base body in its
#   underwear, as the creator shows it) and <people>_<m|f>_clothes.vox (the starting clothes: parts that replace the bare ones)
# 2.5 cm voxels; MagicaVoxel axes: x across (0 = the character's right seen from the front), y front (small) to back, z up.
# Skin colours stay within real skin's reflectance (pale skin reflects about 60% of light, sRGB about 200 at most): brighter
# values flare yellow or white under the game's sun.
# Eyes: off-white whites (pure white glares) and an iris dark enough to read against them, darker below.
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
                  skin=(170, 156, 160), hair_m=(36, 38, 48), hair_f=(186, 192, 204), eye=(70, 136, 186), tunic=(40, 48, 70), trousers=(34, 36, 44),
                  leather=(70, 60, 60), bracers=False, hair=('long', 'long'), beard=None, mark='ink'),
 'ferrin':   dict(UL=7, LL=5, TH=18, TW=22, TD=11, AW=7, AU=10, AL=9, LW=8,
                  skin=(172, 110, 86), hair_m=(52, 34, 24), hair_f=(60, 40, 28), eye=(50, 36, 28), tunic=(110, 70, 46), trousers=(60, 52, 46),
                  leather=(70, 48, 34), bracers=True, hair=('crop', 'crown'), beard='big', mark='soot'),
 'wayfolk':  dict(UL=9, LL=8, TH=20, TW=18, TD=9, AW=6, AU=11, AL=10, LW=7,
                  skin=(184, 142, 110), hair_m=(100, 70, 46), hair_f=(110, 76, 50), eye=(90, 70, 50), tunic=(140, 110, 80), trousers=(80, 70, 60),
                  leather=(96, 64, 40), bracers=False, hair=('crop', 'long'), beard='stubble', mark=None),
 'penitent': dict(UL=9, LL=8, TH=20, TW=16, TD=8, AW=5, AU=11, AL=10, LW=6,
                  skin=(164, 150, 142), hair_m=(60, 56, 52), hair_f=(66, 60, 56), eye=(112, 116, 126), tunic=(100, 96, 92), trousers=(60, 58, 56),
                  leather=(70, 60, 50), bracers=False, hair=('crop', 'crop'), beard=None, mark='veins'),
}
WOMAN = dict(UL=0, LL=0, TH=-2, TW=-2, TD=-1, AW=-1, AU=-1, AL=-1, LW=-1)
# a woman's frame: shoulders pulled in (SH), hips at full width, a defined waist, a bust, smaller hands and feet, a softer jaw
HEAD = {'ilvari': (24, 22)}   # narrower, shallower heads (width, depth, in 1.25 cm voxels); men 28 x 26, women 24 x 24
EXPR = {}   # (people, sex) -> stern, grim, calm, smile; men default stern, women calm (a face preset overrides it)
# ---- faces: what a preset (or the creator's face options) can change. Only the head's pieces change, so a preset is a
# layer over the base body (faces/<people>_<sex>_<k>.vox) and every helm still fits (the head's box stays the same size).
#   eyes: round | narrow (a heavy lid) | big (a taller iris);  set: the eyes' spacing, -2 close-set, 0, +2 wide-set
#   nose: straight | broad | hooked | button | long;  mouth: normal | thin | wide | full
#   brows: normal | heavy | thin;  scar: None | brow | cheek | lip;  expr: stern | grim | calm | smile
#   hair, beard, hair_col: override the people's (hair_col stays within the people's own range)
FACE = dict(eyes='round', set=0, nose='straight', mouth='normal', brows='normal', scar=None, expr=None, hair=None, beard=None, hair_col=None)
# six presets per people and sex; preset 0 is the base body's own face (for the Hrimfolk man, the approved one)
PRESETS = {
 ('hrimfolk', 'm'): [
   dict(name='Warden', scar='brow'),
   dict(name='Greybeard', expr='grim', eyes='narrow', brows='heavy', beard='big', hair='long', hair_col=(132, 126, 116), nose='long'),
   dict(name='Youngblood', expr='calm', eyes='big', hair='braids', beard='short', hair_col=(170, 120, 64), set=-2),
   dict(name='Laughing', expr='smile', nose='broad', mouth='wide', hair='crop', beard='moustache', hair_col=(120, 66, 34)),
   dict(name='Raider', expr='grim', nose='hooked', eyes='narrow', hair='long', beard='full_braid', scar='cheek', hair_col=(58, 40, 30), set=2),
   dict(name='Shorn', expr='stern', brows='heavy', beard='stubble', scar='lip', set=2, nose='broad'),
 ],
 ('hrimfolk', 'f'): [
   dict(name='Braided'),
   dict(name='Bright', expr='smile', eyes='big', nose='button', hair='bun', hair_col=(214, 176, 112)),
   dict(name='Shieldmaiden', expr='stern', hair='crop', hair_col=(120, 80, 44), brows='heavy', scar='brow', eyes='narrow'),
   dict(name='Fox', expr='calm', eyes='narrow', hair='long', hair_col=(150, 74, 40), nose='long', mouth='thin'),
   dict(name='Hearth', expr='calm', hair='crown', mouth='full', set=-2, hair_col=(176, 132, 76)),
   dict(name='Elder', expr='grim', eyes='narrow', mouth='thin', hair='long', hair_col=(150, 146, 140), brows='heavy', nose='hooked'),
 ],
}
def presets(people, sex):
    return PRESETS.get((people, sex), [dict(name='Default')])

def tone(c, f): return tuple(max(0, min(255, int(v * f))) for v in c)
def build(people, sex, dressed=True, face=0):
    """the character dressed in its starting clothes, or (dressed=False) the base body in its underwear; face: a preset's
    number (presets()) or a dict of FACE options"""
    p = dict(PEOPLES[people])
    F = dict(FACE); F.update(presets(people, sex)[face] if isinstance(face, int) else face)
    if sex == 'f':
        for k, v in WOMAN.items(): p[k] += v
    hair_col = F['hair_col'] or p['hair_f' if sex == 'f' else 'hair_m']
    PAL = {'skin': p['skin'], 'skin_d': tone(p['skin'], 0.86), 'skin_l': tone(p['skin'], 1.07), 'eye_w': (206, 198, 188), 'eye': p['eye'], 'eye_d': tone(p['eye'], 0.55), 'pupil': (26, 22, 22), 'lid': tone(p['skin'], 0.7), 'nostril': tone(p['skin'], 0.5), 'lip_d': tone(p['skin'], 0.55) if sex == 'm' else (120, 58, 54),
           'brow': tone(hair_col, 0.7), 'hair': hair_col, 'hair_d': tone(hair_col, 0.72), 'hair_l': tone(hair_col, 1.25),
           'lip': tone(p['skin'], 0.62) if sex == 'm' else (150, 78, 70), 'scar': tone(p['skin'], 1.12),
           'tunic': p['tunic'], 'tunic_d': tone(p['tunic'], 0.76), 'leather': p['leather'], 'leather_d': tone(p['leather'], 0.72),
           'trousers': p['trousers'], 'trousers_d': tone(p['trousers'], 0.78), 'boots': (84, 52, 32), 'boots_d': (60, 36, 22),
           'iron': (128, 132, 136), 'iron_d': (90, 92, 96), 'bead': (176, 150, 96),
           'ink': (56, 116, 210), 'tattoo': (40, 58, 56), 'vein': tone(p['skin'], 0.7), 'soot': tone(p['skin'], 0.55), 'freckle': tone(p['skin'], 0.78), 'stub': tone(p['skin'], 0.88), 'linen': (122, 106, 88), 'linen_d': (94, 80, 64), 'cheek': (min(255, p['skin'][0] + 12), int(p['skin'][1] * 0.86), int(p['skin'][2] * 0.86))}
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
    FR = {'people': people, 'sex': sex, 'TW': TW, 'TD': TD, 'LW': LW, 'AW': AW, 'hip': hip, 'LL': p['LL'], 'UL': p['UL'], 'legs': {}, 'arms': {}}
    for side, x0 in (('l', x0l), ('r', x0r)):
        x1 = x0 + LW - 1; yc = (TD - 8) // 2; FR['legs'][side] = (x0, x1, yc)
        if dressed:     # boots with a turned cuff, trousers
            rbox('foot_' + side, x0, x1, yc - (1 if sex == 'f' else 2), yc + 7, 0, 3, lambda x, y, z: 'boots_d' if z == 0 else 'boots')
            rbox('foot_' + side, x0, x1, yc, yc + 7, 4, 6, 'boots')
            rbox('leg_lower_' + side, x0 - 1, x1 + 1, yc - 1, yc + 8, 7, 8, 'boots_d')
            rbox('leg_lower_' + side, x0, x1, yc, yc + 7, 9, 8 + p['LL'], 'trousers')
            rbox('leg_upper_' + side, x0, x1, yc, yc + 7, 9 + p['LL'], hip, lambda x, y, z, x0=x0, x1=x1: 'trousers_d' if (x in (x0, x1) and z % 3 == 0) else 'trousers')
        else:           # bare feet with toes, bare legs, linen drawers to mid-thigh
            rbox('foot_' + side, x0, x1, yc - 1, yc + 6, 0, 2, lambda x, y, z, x0=x0: 'skin_d' if z == 0 or (y == yc - 1 and z == 1 and (x - x0) % 2 == 1) else 'skin')
            rbox('foot_' + side, x0 + 1, x1 - 1, yc + 1, yc + 6, 3, 6, 'skin')
            rbox('leg_lower_' + side, x0, x1, yc, yc + 7, 7, 8 + p['LL'], lambda x, y, z: 'skin_d' if (y == yc and z == 7 + p['LL'] - 1 and 1 <= x - x0 <= LW - 2) else 'skin')
            dz = hip - (p['UL'] + 1) // 2
            rbox('leg_upper_' + side, x0, x1, yc, yc + 7, 9 + p['LL'], hip, lambda x, y, z, dz=dz: 'linen_d' if z == dz else ('linen' if z > dz else 'skin'))
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
            if not dressed:      # bare: drawers at the hips, a breast band on women, the chest and navel shaded on the skin
                if r <= 2: return 'linen_d' if r == 2 else 'linen'
                if sex == 'f' and top - 10 <= z <= top - 4: return 'linen_d' if z == top - 10 else 'linen'
                if sex == 'm' and z == top - 8 and y <= d and not (cx - 1 <= x <= cx): return 'skin_d'
                if y <= d and z == hip + 6 and cx - 1 <= x <= cx: return 'skin_d'
                return 'skin'
            if r <= 1: return 'leather_d' if r == 0 else 'leather'
            if r == 2: return 'tunic_d'
            if y <= d and cx - 2 <= x <= cx + 1 and z >= top - 4: return 'skin' if z >= top - 3 and cx - 1 <= x <= cx else ('leather_d' if x in (cx - 2, cx + 1) and z % 2 == 0 else 'tunic')
            return 'tunic'
        rbox('torso', w, TW - 1 - w, d, TD - 1 - d, z, z, col, bev=2 if up else 1)
    if sex == 'f':     # the bust: two soft forms on the upper chest
        for k, z in enumerate(range(top - 9, top - 4)):
            inset = 1 if k in (0, 4) else 0
            for x in list(range(SH + 1 + inset, cx - 1 - inset)) + list(range(cx + 1 + inset, TW - 1 - SH - inset)):
                put('torso', x, -1, z, ('tunic_d' if k == 0 else 'tunic') if dressed else 'linen')
    if p['mark'] == 'veins' and not dressed:     # healed scourge scars, diagonal across the back
        for k in range(5):
            zb = top - 4 - k * 3
            for x in range(2, TW - 2):
                if (x + k) % 6 < 4: put('torso', x, TD, zb - x // 4, 'scar')
    if dressed:
        for x in range(cx - 1, cx + 1): put('torso', x, 0, hip + 2, 'iron'); put('torso', x, -1, hip + 2, 'iron_d')
    if not dressed and people == 'hrimfolk':     # knotwork over the shoulders and up the neck's base
        for x in list(range(0, 4)) + list(range(TW - 4, TW)):
            for y in range(0, TD):
                if y in (0, TD - 1) or (x + y) % 2 == 0: put('torso', x, y, top, 'tattoo')
        for x in (1, 2, TW - 3, TW - 2):
            for z in (top - 1, top - 2): put('torso', x, 0, z, 'tattoo')
    if not dressed and p['mark'] == 'soot':     # old forge burns on the chest
        for x, z in ((3, top - 3), (4, top - 3), (4, top - 4), (TW - 5, top - 6), (TW - 6, top - 6)): put('torso', x, 0, z, 'scar')
    # ---- arms: sleeves, bare forearms (bracers for some peoples), big fists with a thumb
    ay0 = (TD - AW) // 2
    for side, (x0, x1) in (('l', (TW - SH, TW - SH + AW - 1)), ('r', (SH - AW, SH - 1))):
        au0 = top - p['AU'] + 1; al0 = au0 - p['AL']; h0 = al0 - (5 if sex == 'f' else 6)
        FR['arms'][side] = (x0, x1, ay0, au0, al0, h0)
        sleeve = top - p['AU'] * 2 // 3
        rbox('arm_upper_' + side, x0, x1, ay0, ay0 + AW - 1, au0, top, lambda x, y, z: 'tunic' if z >= sleeve and dressed else ('tattoo' if people == 'hrimfolk' and not dressed and (z in (top - 6, top - 3) or (z in (top - 5, top - 4) and (x + y + z) % 2 == 0)) else 'skin'), top_bev=True)
        rbox('arm_lower_' + side, x0, x1, ay0, ay0 + AW - 1, al0, au0 - 1, 'skin')
        if p['bracers'] and dressed:
            rbox('arm_lower_' + side, x0 - 1 if side == 'r' else x0, x1 if side == 'r' else x1 + 1, ay0 - 1, ay0 + AW, al0, al0 + 5,
                 lambda x, y, z: 'leather_d' if z in (al0, al0 + 5) else 'leather')
        rbox('hand_' + side, x0, x1, ay0 - 1, ay0 + AW, h0, al0 - 1, lambda x, y, z: 'skin_d' if (y == ay0 - 1 and z in (h0 + 1, h0 + 3)) else 'skin')
        for z in ((h0 + 1, h0 + 2) if sex == 'f' else (h0 + 1, h0 + 2, h0 + 3)): put('hand_' + side, x0 + 1 if side == 'l' else x1 - 1, ay0 - 2, z, 'skin')
        if p['mark'] == 'ink':
            for z in (h0 + 2, h0 + 3, h0 + 4): put('hand_' + side, x0 + AW // 2, ay0 + AW, z, 'ink')
        # marks on the bare forearm
        mz = al0 + (6 if p['bracers'] and dressed else 1)
        for z in range(mz, au0):
            for x in range(x0, x1 + 1):
                k = (x * 3 + z * 5) % 7
                if p['mark'] == 'knotwork' and (z in (mz + 1, mz + 4) or (z in (mz + 2, mz + 3) and (x + z) % 2 == 0)): put('arm_lower_' + side, x, ay0, z, 'tattoo')
                if p['mark'] == 'veins' and k == 0: put('arm_lower_' + side, x, ay0, z, 'vein')
                if p['mark'] == 'veins' and side == 'r' and (x + z) % 4 == 0 and z % 3 == 0: put('arm_lower_' + side, x, ay0, z, 'scar')   # old lash scars
                if p['mark'] == 'soot' and k == 1: put('arm_lower_' + side, x, ay0, z, 'soot')
                if p['mark'] == 'ink' and side == 'l' and x == x0 + AW // 2: put('arm_lower_' + side, x, ay0, z, 'ink')
                if p['mark'] == 'freckles' and k == 2 and z % 2: put('arm_lower_' + side, x, ay0, z, 'freckle')
    # ---- the head, at half-size voxels (1.25 cm, part "head#2"): the same size as before, twice the detail. Everything here
    # is in fine units, drawn from the face's centre line so any head width works. c: column as you face the character
    # (0 = your left), v: row from the top, d: depth from the face. Expressions: brows and mouth corners (EXPR).
    W, D = HEAD.get(people, (24, 24) if sex == 'f' and people != 'ferrin' else (28, 26)); H = 30
    if people in HEAD and sex == 'f': W, D = W - 2, D - 2
    X0 = TW - W // 2; Y0 = -4; Z0 = (top + 1) * 2
    expr = F['expr'] or EXPR.get((people, sex), 'stern' if sex == 'm' else 'calm')
    hair_m, hair_f = p['hair']; hs = F['hair'] or (hair_f if sex == 'f' else hair_m)
    beard = F['beard'] or (p['beard'] if sex == 'm' else None)
    HP = 'head#2'
    def X(c): return X0 + W - 1 - c
    def Z(v): return Z0 + H - 1 - v
    def hput(part, c, d, v, col): put(part, X(c), Y0 + d, Z(v), col)
    mid = W // 2; gap = 2 * (W // 8) + 2 + F['set']
    FR.update(top=top, cx=cx, SH=SH, head=(X0, Y0, Z0, W, D, H), mid=mid, hair=hs, beard=beard)
    EYES = (mid - gap // 2 - 6, mid + gap // 2)          # first column of each eye
    MW = (4 if sex == 'm' else 3) + {'wide': 1, 'thin': -1}.get(F['mouth'], 0)   # half the mouth's width
    def inset(v):                                       # the jaw narrowing toward the chin
        if sex == 'f' and people != 'ferrin': return max(0, (v - 20) // 2)
        return max(0, (v - 25) // 2)
    def hair_at(c, d, v):
        side = c < 2 or c > W - 3
        if hs == 'shaved': return False
        if v < 4 or (v < 6 and d < 3 and (c * 5) % 4 != 0): return True          # the top and an uneven hairline
        if d >= D * 0.5 and v < 17: return True                                 # back and upper sides
        if d >= D - 3 and v < 21: return True                                   # the nape
        if side and v < 11 and d >= 2: return True                              # temples
        if hs in ('long', 'braids', 'crown', 'bun') and side and v < 25: return True    # framing the face, over the ears
        if hs in ('long', 'braids', 'crown', 'bun') and d >= D * 0.4 and v < 26: return True
        return False
    def beard_at(c, d, v):
        if beard not in ('full_braid', 'big', 'short'): return False
        side = c < 2 or c > W - 3
        if side and v >= 13 and d < D * 0.6: return True                        # sideburns
        if d < D * 0.6 and v >= 26: return True                                 # the chin and jaw
        if d < D * 0.5 and v >= 21 and not (mid - MW - 1 <= c <= mid + MW) and (c < EYES[0] + 2 or c > EYES[1] + 3 or v >= 22): return True
        return False
    marks = {}     # (c, v) -> colour on the face's front
    # eyes: 6 x 4 - a lid, the iris with its pupil and a catch-light, the lower iris in shadow
    EYE = {'round': ["LLLLLL", "WIPPIW", "WIPPIW", ".QQQQ."], 'narrow': ["LLLLLL", "LLLLLL", "WIPPIW", ".QQQQ."],
           'big': ["LLLLLL", "WIPPIW", "WIPPIW", "WIIIIW", ".QQQQ."]}[F['eyes']]
    if sex == 'f': EYE = ["ELLLLE"] + EYE[1:]
    EV = 13; EH = len(EYE); ER = next(r for r, row in enumerate(EYE) if 'P' in row)    # the eye's height, its first open row
    for k, c0 in enumerate(EYES):
        for r, row in enumerate(EYE):
            line = row if k == 1 else row[::-1]
            for i, ch in enumerate(line):
                if ch != '.': marks[(c0 + i, EV + r)] = {'L': 'lid', 'E': 'brow', 'W': 'eye_w', 'I': 'eye', 'P': 'pupil', 'Q': 'eye_d'}[ch]
        marks[(c0 + 2, EV + ER)] = 'eye_w'         # the catch-light, on the same side in both eyes (one light)
        if sex == 'f': marks[(c0 - 1 if k == 0 else c0 + 6, EV)] = 'brow'    # lashes flick out at the outer corner
    # nose: a bridge, a broader tip, nostrils, the shadow under it
    nose = F['nose']; NT = 21 if nose != 'long' else 22           # the row of the nostrils
    NB = 2 if nose != 'broad' else 3                              # the tip's half-width
    for v in range(15 if nose != 'button' else 17, NT + 1): marks[(mid - 1, v)] = marks[(mid, v)] = 'skin_l' if v < NT - 1 else 'skin'
    for c in (mid - NB, mid + NB - 1): marks[(c, NT - 1)] = 'skin'; marks[(c, NT)] = 'nostril'
    if nose == 'broad': marks[(mid - 2, NT)] = marks[(mid + 1, NT)] = 'skin'
    for c in range(mid - NB, mid + NB): marks[(c, NT + 1)] = 'skin_d'
    # mouth: an upper lip line, a fuller lower lip; corners set the expression
    for c in range(mid - MW, mid + MW): marks[(c, 24)] = 'lip_d'; marks[(c, 25)] = 'lip' if (sex == 'f' or F['mouth'] == 'full' or abs(c - mid + 0.5) < MW - 1) else 'skin_d'
    if sex == 'f' and F['mouth'] != 'thin':
        for c in range(mid - MW + 1, mid + MW - 1): marks[(c, 23)] = 'lip'
    cy = {'smile': 23, 'stern': 25, 'calm': 24, 'grim': 25}[expr]
    marks[(mid - MW - 1, cy)] = marks[(mid + MW, cy)] = 'lip_d'
    if expr == 'smile':
        for c in (mid - MW - 1, mid + MW): marks[(c, 20)] = 'skin_d'    # the cheeks lift
    marks.update({(c, 28): 'skin_d' for c in range(mid - 2, mid + 2)} if sex == 'm' else {})   # a cleft under the lip
    # people's marks
    if people == 'hrimfolk':
        for c in (EYES[0] - 1, EYES[0], EYES[1] + 5, EYES[1] + 6):
            for v in (18, 19): marks[(c, v)] = 'cheek'
    if p['mark'] == 'ink':      # lines of blue ink from under each eye, a chevron on the brow
        for c in (EYES[0] + 2, EYES[1] + 3):
            for v in range(17, 24): marks[(c, v)] = 'ink'
        for i in range(4): marks[(mid - 1 - i, 6 + i)] = marks[(mid + i, 6 + i)] = 'ink'
    if p['mark'] == 'freckles':
        for c in range(EYES[0] - 1, EYES[1] + 7):
            for v in (17, 18, 19):
                if (c * 7 + v * 3) % 5 == 0 and (c, v) not in marks: marks[(c, v)] = 'freckle'
    if p['mark'] == 'soot':
        for c, v in ((EYES[0], 18), (EYES[0] + 1, 19), (EYES[0] + 2, 18), (EYES[1] + 4, 19), (EYES[1] + 5, 18), (mid + 4, 4), (mid + 5, 5)): marks[(c, v)] = 'soot'
    if p['mark'] == 'veins':
        for c, v in ((1, 8), (2, 9), (2, 10), (3, 11), (W - 2, 9), (W - 3, 10), (W - 3, 11), (W - 4, 12)): marks[(c, v)] = 'vein'
    if F['scar'] == 'brow':    # the approved man's scar, through his left brow and down the cheek
        for v in range(10, 21):
            if not (EV <= v <= EV + EH - 1): marks[(EYES[1] + 4, v)] = 'scar'
    if F['scar'] == 'cheek':   # a slash across the right cheek
        for k in range(6): marks[(EYES[0] + k, 17 + k // 2)] = 'scar'
    if F['scar'] == 'lip':     # a split lip, from under the nose to the chin
        for v in range(NT + 1, 29):
            if not 23 <= v <= 25: marks[(mid + 2 + (v > 25), v)] = 'scar'     # broken by the lips, so it reads as a cut, not a tooth
    if beard == 'stubble':
        for c in range(W):
            for v in range(21, H):
                if (c, v) not in marks and (c < mid - MW - 1 or c > mid + MW or v >= 26) and inset(v) <= c < W - inset(v): marks[(c, v)] = 'stub'
    # the face carved, not only painted: how far in the face's surface sits at each point (0 = the front plane,
    # 1 = cut one voxel in). Eye sockets under the brow ridge, sides turning back, cheekbones, mouth corners pressed in.
    def front(c, v):
        e = min(c, W - 1 - c)                                   # distance from the face's side
        if v < 3: return 1                                      # the forehead turns over into the crown
        for c0 in EYES:                                         # the sockets: the eye sits in, under the brow
            if c0 <= c < c0 + 6 and EV <= v <= EV + EH - 1: return 1
        if people == 'penitent' and 20 <= v <= 22 and 3 <= e <= 4: return 1     # gaunt: hollow cheeks
        if v >= 27 and e < 4: return 1                          # the jaw narrows to the chin
        if v in (24, 25) and abs(c - mid + 0.5) == MW + 0.5 and not beard_at(c, 0, v): return 1   # mouth corners
        return 0
    # the head's volume
    for v in range(H):
        a = inset(v)
        for c in range(a, W - a):
            fr = front(c, v)
            for d in range(fr, D):
                ec = c - a < 2 or W - 1 - a - c < 2; ed = d < 2 or d >= D - 2
                if ec and ed and not ((c - a in (1,) or W - 1 - a - c == 1) and (d in (1, D - 2))): continue    # rounded vertical edges
                if v == 0 and (ec or ed): continue
                if hair_at(c, d, v): col = 'hair_l' if v < 2 and c % 4 == 1 else ('hair_d' if (c + d) % 4 == 0 else 'hair')
                elif beard_at(c, d, v): col = 'hair_d' if c % 3 == 0 else 'hair'
                elif d == fr and (c, v) in marks: col = marks[(c, v)]
                elif hs == 'shaved' and (d >= 3 or v < 3) and d > fr - 1 and ((v in (5, 8) and (c + d) % 4 != 3) or (v in (6, 7) and (c + d + v) % 4 == 0) or (v == 0 and abs(c - mid + 0.5) + abs(d - D / 2) in (3, 3.5, 4.5, 6) )): col = 'tattoo'
                else: col = 'skin'
                hput(HP, c, d, v, col)
    # what stands proud of the face: the nose, a moustache, the front of a full beard
    for v in range(16 if nose != 'button' else 18, NT + 1):
        for c in ((mid - 1, mid) if v < NT - 1 else range(mid - NB, mid + NB)): hput(HP, c, -1, v, 'skin' if v < NT else 'skin_d')
    hput(HP, mid - 1, -2, NT - 1, 'skin'); hput(HP, mid, -2, NT - 1, 'skin')
    if nose == 'hooked':       # a high bridge with a hump
        for v in (17, 18, 19): hput(HP, mid - 1, -2, v, 'skin_l'); hput(HP, mid, -2, v, 'skin_l')
    if beard in ('moustache', 'full_braid', 'big', 'short'):
        for c in range(mid - MW - 1, mid + MW + 1): hput(HP, c, -1, 23, 'hair_d'); hput(HP, c, -1, 22, 'hair') if abs(c - mid + 0.5) < MW else None
        if beard != 'moustache':
            for c in (mid - MW - 1, mid + MW): hput(HP, c, -1, 24, 'hair_d'); hput(HP, c, -1, 25, 'hair_d')
    if beard in ('full_braid', 'big', 'short'):
        for v in range(26, H):
            a = inset(v)
            for c in range(a + 1, W - a - 1): hput(HP, c, -1, v, 'hair_d' if c % 3 == 0 else 'hair')
    if sex == 'f' or F['mouth'] == 'full':      # a fuller lower lip, raised
        for c in range(mid - MW + 1, mid + MW - 1): hput(HP, c, -1, 25, 'lip')
    elif beard in (None, 'stubble', 'moustache'):      # a jutting chin
        for c in range(mid - 3, mid + 3):
            for v in (27, 28): hput(HP, c, -1, v, 'stub' if beard == 'stubble' else 'skin')
    # ears (under long hair)
    for c, cc in ((-1, 'l'), (W, 'r')):
        for v in range(13, 20):
            for d in range(D // 2 - 3, D // 2 + 1):
                covered = hs in ('long', 'braids', 'crown', 'bun') or beard_at(0, d, v)
                hput(HP, c, d, v, 'hair' if covered else ('skin_d' if (d == D // 2 - 2 and 14 < v < 19) else 'skin'))
    # brows: their own pieces, tilted by the expression (men heavier)
    tilt = {'stern': 14, 'grim': 18, 'calm': 4, 'smile': -4}[expr]
    for name, c0 in (('brow_r@head#2~z%d' % -tilt, EYES[1] - 1), ('brow_l@head#2~z%d' % tilt, EYES[0] - 1)):
        for c in range(c0, c0 + 8):
            if F['scar'] == 'brow' and c == EYES[1] + 4: continue     # the scar cuts the brow
            heavy = sex == 'm' or people == 'ferrin'
            rows = {'heavy': (9, 10, 11) if heavy else (10, 11), 'thin': (11,)}.get(F['brows'], (10, 11) if heavy else (11,))
            for v in rows:
                for d in (-1, 0): hput(name, c, d, v, 'brow')
    # ---- hair pieces
    if hs in ('long', 'braids'):     # down the back
        for v in range(H, H + (16 if hs == 'long' else 8)):
            for c in range(2, W - 2):
                for d in (D - 4, D - 3, D - 2, D - 1): hput('hair@head#2', c, d, v, 'hair_d' if (c * 3) % 5 == 0 else 'hair')
    if hs == 'braids':   # two braids forward over the shoulders, ringed in iron
        for c0 in (0, W - 3):
            for k in range(22):
                for c in (c0, c0 + 1, c0 + 2):
                    col = 'iron' if k in (5, 17) else ('hair_l' if (c + k) % 3 == 0 else ('hair_d' if (c + k) % 3 == 1 else 'hair'))
                    for d in (D // 2 - 3, D // 2 - 2, D // 2 - 1): hput('braids@head#2~x-6', c, d, 22 + k, col)
    if hs == 'bun':
        for c in range(mid - 5, mid + 5):
            for d in range(D - 1, D + 6):
                for v in range(-2, 8):
                    if abs(c - mid + 0.5) + abs(v - 3) * 0.8 + abs(d - D - 2) * 0.6 < 7: hput('bun@head#2', c, d, v, 'hair_d' if (c + v) % 4 == 0 else 'hair')
    if hs == 'crown':    # braids wound round the head
        for c in range(-1, W + 1):
            for d in (-1, D):
                for v in (5, 6, 7): hput('crown@head#2', c, d, v, 'hair_l' if (c + v) % 3 == 0 else 'hair_d')
        for d in range(0, D):
            for c in (-1, W):
                for v in (5, 6, 7): hput('crown@head#2', c, d, v, 'hair_l' if (d + v) % 3 == 0 else 'hair_d')
    # ---- beards that hang below the chin
    if beard in ('full_braid', 'big'):
        rows = 6 if beard == 'full_braid' else 14
        for k in range(rows):
            a = inset(H - 1) + 2 + k // 2
            for c in range(a, W - a):
                for d in range(-1, 7 - k // 4): hput('beard@head#2', c, d, H + k, 'hair_d' if c % 3 == 0 or d == 6 - k // 4 else 'hair')
    if beard == 'full_braid':
        for k in range(16):
            for c in (mid - 1, mid):
                col = 'iron' if k in (1, 11) else ('bead' if k in (4, 8) else ('hair_l' if (c + k) % 2 else 'hair_d'))
                for d in (-1, 0, 1): hput('braid@head#2~x-10z4', c, d, H + 6 + k, col)
    build.frame = FR      # the body's measurements, for equipment fitted to it (make_equipment.py)
    return P, PAL

OUT = os.path.join(HERE, '..', '..', 'godot', 'assets', 'voxel', 'characters', 'peoples')
CLOTHED = ['torso', 'arm_upper_l', 'arm_upper_r', 'arm_lower_l', 'arm_lower_r', 'leg_upper_l', 'leg_upper_r', 'leg_lower_l', 'leg_lower_r', 'foot_l', 'foot_r']
def is_head(name): return name.split('~')[0].split('#')[0] == 'head' or name.split('~')[0].split('#')[0].endswith('@head')
FACES_JSON = os.path.join(HERE, '..', '..', 'godot', 'data', 'faces.json')
if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for people in PEOPLES:
        for sex in ('m', 'f'):
            P, PAL = build(people, sex, dressed=False)
            mb.COL = PAL; mb.NAMES = list(PAL)
            mb.write(os.path.join(OUT, '%s_%s.vox' % (people, sex)), P)
            C, _ = build(people, sex, dressed=True)      # the starting clothes: the body parts they cover, replacing the bare ones
            mb.write(os.path.join(OUT, '%s_%s_clothes.vox' % (people, sex)), {k: v for k, v in C.items() if k in CLOTHED})
            for k in range(1, len(presets(people, sex))):     # the other face presets: layers of the head's pieces only
                H_, HPAL = build(people, sex, dressed=False, face=k)
                mb.COL = HPAL; mb.NAMES = list(HPAL)
                os.makedirs(os.path.join(OUT, 'faces'), exist_ok=True)
                mb.write(os.path.join(OUT, 'faces', '%s_%s_%d.vox' % (people, sex, k)), {n: v for n, v in H_.items() if is_head(n)})
            mb.COL = PAL; mb.NAMES = list(PAL)
            zs = [z / (2 if '#2' in n else 1) for n, part in P.items() for (_, _, z) in part]; xs = [x / (2 if '#2' in n else 1) for n, part in P.items() for (x, _, _) in part]
            print('%-9s %s  %d voxels tall (%.2f m), %d across (%.2f m)' % (people, sex, max(zs) - min(zs) + 1, (max(zs) - min(zs) + 1) * 0.025, max(xs) - min(xs) + 1, (max(xs) - min(xs) + 1) * 0.025))
    import json     # the presets' names, for the creator (godot/data/faces.json): face 0 is the base body's own
    json.dump({'%s_%s' % (pp, sx): [pr['name'] for pr in presets(pp, sx)] for pp in PEOPLES for sx in ('m', 'f')}, open(FACES_JSON, 'w'), indent=1)
