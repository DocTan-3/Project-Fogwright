# Fogwright's voxel equipment: items are recipes, not models (docs/design.md, Equipment). Each item is a function that
# reads a body's measurements (make_character.py's build.frame) and builds itself to fit that body, so one item fits
# every people and both sexes. Written per body as a layer file the importer stacks on the character
# (godot/scripts/voxel/vox.gd, Vox.character(..., layers); godot/scripts/voxel/equipment.gd dresses a character):
#   - parts named "<piece>@<part>" ride on that body part (pauldrons on the upper arms, a helm on the head, a boiler on
#     the torso);
#   - parts that take a body part's own name replace it, as WoW's geosets swap body sections for armour-shaped ones:
#     nothing is left underneath to poke through (a breastplate replaces the torso, boots the feet and shins);
#   - an item lists what it hides (a helm hides the hair and hanging beard, a hood tucks the hair in).
# The five armour tiers of the design doc, each a set: light (Warden's leathers), medium (the Tinkerer's brigandine,
# asymmetric), heavy (the Steamwright's brass and boiler), plate (Ironclad, exposed mechanical joints) and the rig (an
# arcane-engine exosuit you climb into, which replaces the body).
#   python3 tools/voxel/make_equipment.py   -> godot/assets/voxel/gear/<item>/<people>_<sex>.vox, godot/data/equipment.json
# Base parts are in 2.5 cm voxels, head pieces ("@head#2") in the head's 1.25 cm voxels. MagicaVoxel axes: x across
# (0 = the character's right as you face it), y front (small) to back, z up.
import json, math, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('mc', os.path.join(HERE, 'make_character.py')); mc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mc)
mb = mc.mb
ROOT = os.path.join(HERE, '..', '..', 'godot')

MAT = {   # kept within real reflectance, like the skins: metals read by their tones, not by brightness
    'iron': (112, 116, 122), 'iron_d': (72, 76, 82), 'iron_l': (150, 154, 160), 'brass': (176, 134, 60), 'brass_d': (128, 94, 40),
    'brass_l': (208, 170, 96), 'copper': (160, 90, 56), 'copper_d': (112, 60, 38), 'rubber': (40, 36, 34), 'glass': (96, 160, 168),
    'glass_l': (176, 214, 216), 'glow': (255, 168, 64), 'arc': (110, 200, 255), 'arc_d': (50, 110, 170), 'leather': (96, 60, 38),
    'leather_d': (66, 42, 26), 'leather_l': (128, 86, 56), 'wool': (78, 86, 60), 'wool_d': (58, 64, 44), 'fur': (150, 132, 108),
    'fur_d': (112, 96, 76), 'canvas': (120, 100, 72), 'red': (120, 42, 36), 'red_d': (86, 30, 26), 'cord': (170, 150, 110), 'bronze': (138, 88, 54), 'bronze_d': (90, 56, 34), 'bronze_l': (182, 128, 82), 'hose': (150, 44, 40), 'potion': (80, 168, 96), 'blued': (50, 62, 100), 'quilt': (150, 134, 104), 'quilt_d': (116, 100, 74), 'cloth_b': (66, 76, 92), 'cloth_b_d': (46, 54, 66), 'wood': (132, 96, 62), 'wood_d': (100, 70, 44), 'blued_d': (34, 42, 70), 'blued_l': (76, 92, 136), 'hose_d': (104, 30, 28),
    'ash': (164, 128, 86), 'ash_d': (128, 96, 62),
    # the higher tiers' steels: bright steel (uncommon, rare), blackened (epic), blued with arcane light (legendary)
    'steel': (138, 146, 156), 'steel_l': (184, 192, 200), 'steel_d': (92, 100, 110), 'black': (52, 52, 58), 'black_d': (34, 34, 40),
    'gilt': (214, 176, 84),
}
SIDES = ('l', 'r')
def out_side(F, s): return 1 if s == 'l' else -1      # the left arm is at large x: its outer side faces +x

# ---------------------------------------------------------------- helpers
def grow(vox, n=1, zs=None):
    """the part thickened outward by n voxels across (x and y), as armour over it; zs limits which rows grow"""
    out = dict(vox)
    for _ in range(n):
        add = {}
        for (x, y, z), c in out.items():
            if zs is not None and z not in zs: continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (x + dx, y + dy, z)
                if q not in out: add[q] = c
        out.update(add)
    return out
def paint(vox, f):
    """recolour every voxel by f(x, y, z, front, back, xmin, xmax) - the part's extent in that row, so patterns follow it"""
    rows = {}
    for (x, y, z) in vox:
        r = rows.setdefault(z, [99, -99, 99, -99]); r[0] = min(r[0], y); r[1] = max(r[1], y); r[2] = min(r[2], x); r[3] = max(r[3], x)
    return {(x, y, z): f(x, y, z, *rows[z]) for (x, y, z) in vox}
def box(P, part, x0, x1, y0, y1, z0, z1, c, bev=0):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if bev and ((x - x0 < bev) + (x1 - x < bev)) and ((y - y0 < bev) + (y1 - y < bev)): continue
                P.setdefault(part, {})[(x, y, z)] = c(x, y, z) if callable(c) else c
class Head:
    """the head's frame in its own 1.25 cm voxels: c column as you face it, d depth from the face, v row from the top"""
    def __init__(self, F):
        self.X0, self.Y0, self.Z0, self.W, self.D, self.H = F['head']; self.mid = F['mid']
        gap = 2 * (self.W // 8) + 2; self.eyes = (self.mid - gap // 2 - 6, self.mid + gap // 2)
    def xyz(self, c, d, v): return (self.X0 + self.W - 1 - c, self.Y0 + d, self.Z0 + self.H - 1 - v)
    def put(self, P, part, c, d, v, col): P.setdefault(part, {})[self.xyz(c, d, v)] = col

# ---------------------------------------------------------------- shared pieces
def pauldron(F, P, s, mat, lames=3, cog=False):
    """a shoulder piece riding on the upper arm: a domed cap and stepped lames down the outer side"""
    x0, x1, ay0, au0, al0, h0 = F['arms'][s]; AW = F['AW']; top = F['top']; o = out_side(F, s)
    part = 'pauldron_%s@arm_upper_%s' % (s, s)
    m, md, ml = mat, mat + '_d', mat + '_l'
    box(P, part, x0 - 1, x1 + 1, ay0 - 1, ay0 + AW, top + 1, top + 2, lambda x, y, z: ml if z == top + 2 else m, bev=1)
    for k in range(lames):         # each lame a little lower and further out
        zt = top - k * 2; xo = (x1 + 1 + k // 2) if o > 0 else (x0 - 1 - k // 2)
        for x in ((xo, xo + 1) if o > 0 else (xo - 1, xo)):
            for y in range(ay0 - 1, ay0 + AW + 1):
                for z in (zt, zt - 1): P.setdefault(part, {})[(x, y, z)] = md if z == zt - 1 else m
    for y in (ay0, ay0 + AW - 1): P[part][((x1 + 2) if o > 0 else (x0 - 2), y, top)] = 'brass_l'      # rivets
    if cog:                        # a cog turning on the outer plate
        cx = (x1 + 3) if o > 0 else (x0 - 3); cy = ay0 + AW // 2; cz = top - 2
        for dy in range(-2, 3):
            for dz in range(-2, 3):
                r = abs(dy) + abs(dz)
                if r <= 2 or (abs(dy) == 2 and abs(dz) == 2 and False): P[part][(cx, cy + dy, cz + dz)] = 'brass_l' if r == 0 else ('iron_d' if r == 2 else 'iron')
        for dy, dz in ((-3, 0), (3, 0), (0, -3), (0, 3)): P[part][(cx, cy + dy, cz + dz)] = 'iron'
def belt(F, P, Pc, mat='leather_d', buckle='brass'):
    """a belt over the hips: a band one voxel out from the torso's lowest rows, a buckle at the front"""
    hip = F['hip']; cx = F['cx']
    rows = {z for (_, _, z) in Pc['torso'] if z in (hip + 1, hip + 2)}
    band = {k: c for k, c in grow({k: c for k, c in Pc['torso'].items() if k[2] in rows}).items() if k not in Pc['torso']}
    P['belt@torso'] = {k: mat for k in band}
    fy = min(y for (x, y, z) in band if z == hip + 1)
    for x in range(cx - 1, cx + 1):
        for z in (hip + 1, hip + 2): P['belt@torso'][(x, fy - 1, z)] = buckle
    return fy
def pouch(P, part, x0, y0, z0, w=3, d=2, h=4, mat='leather'):
    box(P, part, x0, x0 + w - 1, y0, y0 + d - 1, z0, z0 + h - 1, lambda x, y, z: mat + '_d' if z == z0 + h - 1 else mat)
    P[part][(x0 + w // 2, y0 - 1, z0 + h - 2)] = 'brass'

# ---------------------------------------------------------------- light: Warden's leathers (rope and timber)
def hood(F, Pb, Pc):
    """a deep hood: a shell round the head two voxels thick, the face framed by its rim; hair tucked inside"""
    h = Head(F); P = {}; X0, Y0, Z0, W, D, H = h.X0, h.Y0, h.Z0, h.W, h.D, h.H
    for x in range(X0 - 2, X0 + W + 2):
        for y in range(Y0 - 1, Y0 + D + 2):
            for z in range(Z0 + 3, Z0 + H + 2):
                inside = X0 <= x < X0 + W and y < Y0 + D and z < Z0 + H
                rim = y < Y0 + 1 and (x < X0 + 2 or x >= X0 + W - 2 or z >= Z0 + H - 4)
                if inside and not rim: continue
                if y < Y0 and not (x < X0 or x >= X0 + W or z >= Z0 + H or rim): continue
                edge = (x in (X0 - 2, X0 + W + 1)) + (y == Y0 + D + 1) + (z == Z0 + H + 1)
                if edge >= 2: continue             # rounded
                P.setdefault('hood@head#2', {})[(x, y, z)] = 'wool_d' if (y == Y0 - 1 or y == Y0) and rim else 'wool'
    for x in range(X0, X0 + W):              # the hood falls down the back of the neck
        for y in (Y0 + D, Y0 + D + 1):
            for z in range(Z0 - 4, Z0 + 3): P['hood@head#2'][(x, y, z)] = 'wool'
    # a short capelet round the shoulders
    top = F['top']
    sh = {k: c for k, c in grow({k: c for k, c in Pc['torso'].items() if k[2] >= top - 2}, 2).items() if k not in Pc['torso']}
    P['capelet@torso'] = {k: ('wool_d' if k[2] == top - 2 else 'wool') for k in sh}
    for (x, y, z) in list(P['capelet@torso']):
        if z == top: P['capelet@torso'][(x, y, z + 1)] = 'wool'
    return P
def jerkin(F, Pb, Pc):
    """a leather jerkin: replaces the torso, laced up the front, a fur collar"""
    top, cx = F['top'], F['cx']
    def col(x, y, z, front, back, xmin, xmax):
        if z >= top - 1: return 'fur_d' if (x + y) % 3 == 0 else 'fur'
        if y == front and cx - 1 <= x <= cx: return 'cord' if z % 2 else 'leather_d'
        if x in (xmin, xmax) and z % 2 == 0: return 'leather_d'
        return 'leather'
    t = paint(grow(Pc['torso']), col)
    for (x, y, z) in [k for k in t if k[2] == top]:                    # the collar stands out
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (x + dx, y + dy, z) not in t: t[(x + dx, y + dy, z)] = 'fur'
    return {'torso': t}
def bracers(F, Pb, Pc):
    """leather bracers: replace the forearms (the bare forearm inside, with its marks), a buckle on each"""
    P = {}; AW = F['AW']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]
        P['arm_lower_' + s] = dict(Pb['arm_lower_' + s])
        box(P, 'arm_lower_' + s, x0 - 1, x1 + 1, ay0 - 1, ay0 + AW, al0, al0 + 6, lambda x, y, z: 'leather_d' if z in (al0, al0 + 6) else 'leather', bev=1)
        P['arm_lower_' + s][((x0 + x1) // 2, ay0 - 2, al0 + 3)] = 'brass'
    return P
def tall_boots(F, Pb, Pc):
    """tall boots to the knee: replace the feet and shins, a turned-down top and a strap"""
    P = {}; LL = F['LL']
    for s in SIDES:
        x0, x1, yc = F['legs'][s]
        P['foot_' + s] = {k: {'boots': 'leather', 'boots_d': 'leather_d'}.get(c, c) for k, c in Pc['foot_' + s].items()}
        box(P, 'leg_lower_' + s, x0 - 1, x1 + 1, yc - 1, yc + 8, 7, 8 + LL,
            lambda x, y, z: 'leather_l' if z >= 7 + LL else ('leather_d' if z == 10 else 'leather'), bev=1)
        P['leg_lower_' + s][((x0 + x1) // 2, yc - 2, 10)] = 'brass'
    return P
def warden_belt(F, Pb, Pc):
    """a belt with a pouch on the right hip and the Warden's lantern on the left"""
    P = {}; hip, TW = F['hip'], F['TW']
    fy = belt(F, P, Pc)
    pouch(P, 'belt@torso', 1, fy - 1, hip - 2, w=4, d=2, h=4)
    lx = TW - 6; ly = fy - 4                     # the lantern hangs from a hook at the front of the left hip
    box(P, 'lantern@torso', lx, lx + 3, ly, ly + 3, hip - 6, hip - 1, lambda x, y, z: 'brass_d' if z in (hip - 6, hip - 1) or (x in (lx, lx + 3) and y in (ly, ly + 3)) else 'glow')
    P['lantern@torso'][(lx + 1, ly + 1, hip)] = 'brass'; P['lantern@torso'][(lx + 2, ly + 2, hip)] = 'brass'
    return P

# ---------------------------------------------------------------- medium: the Tinkerer's brigandine (gear and water)
def goggles(F, Pb, Pc):
    """goggles pushed up on the brow: brass rims, glass with a highlight, a leather strap round the head"""
    h = Head(F); P = {}; part = 'goggles@head#2'
    for c0 in h.eyes:
        for c in range(c0, c0 + 6):
            for v in range(3, 9):
                rim = c in (c0, c0 + 5) or v in (3, 8)
                h.put(P, part, c, -3, v, 'brass' if rim else ('glass_l' if (c - c0, v) == (1, 4) else 'glass'))
                h.put(P, part, c, -2, v, 'brass_d'); h.put(P, part, c, -1, v, 'brass_d')
    for c in range(h.eyes[0] + 6, h.eyes[1]): h.put(P, part, c, -2, 5, 'brass'); h.put(P, part, c, -2, 6, 'brass')
    for v in (5, 6):                       # the strap
        for d in range(-1, h.D + 1):
            h.put(P, part, -1, d, v, 'leather_d'); h.put(P, part, h.W, d, v, 'leather_d')
        for c in range(-1, h.W + 1): h.put(P, part, c, h.D, v, 'leather_d')
    return P
def brigandine(F, Pb, Pc):
    """a brigandine: replaces the torso; canvas over small brass plates, their rivets in rows"""
    hip = F['hip']
    def col(x, y, z, front, back, xmin, xmax):
        if z <= hip + 2: return 'leather_d'
        if (z - hip) % 3 == 0: return 'red_d'
        if (y == front or y == back or x in (xmin, xmax)) and (x + y) % 3 == 1 and (z - hip) % 3 == 1: return 'brass_l'
        return 'red'
    return {'torso': paint(grow(Pc['torso']), col)}
def mech_pauldron(F, Pb, Pc):
    """one mechanical pauldron on the left shoulder, with a cog and a pipe: medium armour's asymmetry"""
    P = {}; pauldron(F, P, 'l', 'brass', lames=3, cog=True)
    x0, x1, ay0, au0, al0, h0 = F['arms']['l']; AW = F['AW']; top = F['top']
    for z in range(top - 4, top + 2): P['pauldron_l@arm_upper_l'][(x0, ay0 + AW + 1, z)] = 'copper'
    return P
def canister_gauntlet(F, Pb, Pc):
    """the canister gauntlet on the right arm: replaces forearm and hand; a glowing glass canister on the outer side"""
    P = {}; s = 'r'; x0, x1, ay0, au0, al0, h0 = F['arms'][s]; AW = F['AW']
    P['arm_lower_r'] = {}
    box(P, 'arm_lower_r', x0 - 1, x1 + 1, ay0 - 1, ay0 + AW, al0, au0 - 2, lambda x, y, z: 'brass_d' if z in (al0, au0 - 2) else ('leather' if z > al0 + 6 else 'brass'), bev=1)
    box(P, 'arm_lower_r', x0, x1, ay0, ay0 + AW - 1, au0 - 1, au0 - 1, 'tunic')
    cy = ay0 + AW // 2 - 1
    box(P, 'arm_lower_r', x0 - 3, x0 - 2, cy, cy + 2, al0 + 1, al0 + 7, lambda x, y, z: 'brass' if z in (al0 + 1, al0 + 7) else ('glow' if x == x0 - 3 and y == cy + 1 else 'glass'))
    P['hand_r'] = paint(grow(Pb['hand_r']), lambda x, y, z, f, b, a, m: 'brass_l' if y == f and z % 2 else 'leather_d')
    return P
def tool_belt(F, Pb, Pc):
    """the Tinkerer's tool belt: pouches on both hips, a wrench, an oil can at the back"""
    P = {}; hip, TW, TD = F['hip'], F['TW'], F['TD']
    fy = belt(F, P, Pc, mat='leather', buckle='brass_l')
    pouch(P, 'belt@torso', 0, fy - 1, hip - 2, w=3, d=2, h=4)
    pouch(P, 'belt@torso', TW - 3, fy - 1, hip - 2, w=3, d=2, h=4, mat='leather')
    for z in range(hip - 6, hip + 1): P['belt@torso'][(4, fy - 1, z)] = 'iron'            # the wrench
    for x in (3, 5): P['belt@torso'][(x, fy - 1, hip - 6)] = 'iron'
    box(P, 'belt@torso', F['cx'] - 1, F['cx'] + 1, TD + 1, TD + 2, hip - 3, hip, lambda x, y, z: 'copper_d' if z == hip else 'copper')   # oil can
    return P

# ---------------------------------------------------------------- heavy: the Steamwright's brass and boiler (steam)
def respirator(F, Pb, Pc):
    """a respirator over nose and mouth: a rubber plate with a brass rim, a filter canister either side, a strap"""
    h = Head(F); P = {}; part = 'mask@head#2'; m = h.mid
    for c in range(m - 6, m + 6):
        for v in range(18, 29):
            rim = c in (m - 6, m + 5) or v in (18, 28)
            h.put(P, part, c, -4, v, 'brass' if rim else ('iron_d' if (v % 2 == 0 and m - 2 <= c <= m + 1) else 'rubber'))
            h.put(P, part, c, -3, v, 'rubber')
            if rim: h.put(P, part, c, -2, v, 'rubber'); h.put(P, part, c, -1, v, 'rubber')
    for c0 in (m - 10, m + 6):
        for c in range(c0, c0 + 4):
            for v in range(22, 29):
                for d in (-5, -4, -3, -2): h.put(P, part, c, d, v, 'brass' if v in (22, 28) else ('iron_d' if d == -5 and v % 2 else 'iron'))
    for d in range(-1, h.D):
        h.put(P, part, -1, d, 21, 'leather_d'); h.put(P, part, h.W, d, 21, 'leather_d')
    for c in range(-1, h.W + 1): h.put(P, part, c, h.D, 21, 'leather_d')
    return P
def cuirass(F, Pb, Pc):
    """a brass cuirass: replaces the torso; breast and back plates over leather, lames over the belly, a pressure gauge"""
    hip, top, cx = F['hip'], F['top'], F['cx']
    def col(x, y, z, front, back, xmin, xmax):
        if z <= hip + 2: return 'leather_d'
        if z <= hip + 7: return 'brass_d' if (z - hip) % 2 == 0 else 'brass'
        if y == front or y == back: return 'brass_l' if x in (cx - 1, cx) else 'brass'
        return 'leather'
    t = paint(grow(Pc['torso']), col)
    fy = min(y for (x, y, z) in t if z == top - 4)
    for x in range(cx + 2, cx + 6):
        for z in range(top - 6, top - 2):
            ring = x in (cx + 2, cx + 5) or z in (top - 6, top - 3)
            t[(x, fy - 1, z)] = 'brass_d' if ring else ('rubber' if (x, z) == (cx + 3, top - 4) else 'glass_l')
    return {'torso': t}
def brass_pauldrons(F, Pb, Pc):
    """brass pauldrons on fur, a pressure gauge on the left one and a pipe rising from it (the brawler reference)"""
    P = {}; AW = F['AW']; top = F['top']
    for s in SIDES:
        pauldron(F, P, s, 'brass', lames=3)
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]
        for x in range(x0 - 1, x1 + 2):          # a ring of fur where the pauldron meets the arm
            for y in range(ay0 - 1, ay0 + AW + 1):
                if x in (x0 - 1, x1 + 1) or y in (ay0 - 1, ay0 + AW): P['pauldron_%s@arm_upper_%s' % (s, s)][(x, y, top - 6)] = 'fur' if (x + y) % 2 else 'fur_d'
    x0, x1, ay0, au0, al0, h0 = F['arms']['l']; gy = ay0 - 2; gx = (x0 + x1) // 2
    for dx in range(-2, 3):                      # the gauge, facing forward on the left pauldron's cap
        for dz in range(-2, 3):
            if abs(dx) + abs(dz) <= 3: P['pauldron_l@arm_upper_l'][(gx + dx, gy, top + dz)] = 'brass_d' if abs(dx) + abs(dz) == 3 or abs(dx) == 2 or abs(dz) == 2 else ('rubber' if (dx, dz) in ((0, 0), (1, 1)) else 'glass_l')
    for z in range(top + 2, top + 7): P['pauldron_l@arm_upper_l'][(x0 + 1, ay0 + AW - 1, z)] = 'copper'
    return P
def boiler(F, Pb, Pc):
    """a boiler on the back: a copper drum in iron bands, a firebox glowing below, a chimney, pipes over the shoulders"""
    P = {}; hip, top, TW, TD, cx = F['hip'], F['top'], F['TW'], F['TD'], F['cx']; part = 'boiler@torso'
    r = min(5, TW // 4 + 1); cy = TD + 1 + r
    for z in range(hip + 1, top + 4):
        for x in range(cx - r - 1, cx + r + 1):
            for y in range(cy - r - 1, cy + r + 1):
                dd = (x - cx + 0.5) ** 2 + (y - cy + 0.5) ** 2
                if dd <= r * r:
                    band = (z - hip) % 5 == 0
                    fire = z <= hip + 4 and y >= cy + r - 1 and abs(x - cx + 0.5) < r - 1
                    P.setdefault(part, {})[(x, y, z)] = 'glow' if fire and z > hip + 1 else ('iron_d' if band else ('copper_d' if dd > (r - 1) ** 2 and (x + z) % 4 == 0 else 'copper'))
    for z in range(top + 4, top + 12):          # the chimney, with a cap
        for x in (cx + 1, cx + 2):
            for y in (cy + 1, cy + 2): P[part][(x, y, z)] = 'iron_d' if z == top + 11 else 'iron'
    for x in (cx, cx + 3):
        for y in (cy, cy + 3): P[part][(x, y, top + 11)] = 'iron_d'
    for px in (2, TW - 3):                      # pipes from the drum over each shoulder
        for y in range(1, cy - r + 1): P[part][(px, y, top + 1)] = 'copper'
        P[part][(px, 0, top)] = 'brass'
    for px in (3, TW - 4):                      # straps down the front
        for z in range(hip + 3, top + 1): P[part][(px, -2, z)] = 'leather_d'
    return P
def greaves(F, Pb, Pc):
    """brass greaves over the boots: replace the shins, a knee cop with a rivet"""
    P = {}; LL = F['LL']
    for s in SIDES:
        x0, x1, yc = F['legs'][s]
        box(P, 'leg_lower_' + s, x0 - 1, x1 + 1, yc - 1, yc + 8, 7, 8 + LL, lambda x, y, z: 'brass_d' if z == 7 else ('brass' if y <= yc + 1 else 'leather'), bev=1)
        box(P, 'leg_lower_' + s, x0, x1, yc - 3, yc - 2, 6 + LL, 9 + LL, lambda x, y, z: 'glow' if (z in (7 + LL, 8 + LL) and x in ((x0 + x1) // 2, (x0 + x1) // 2 + 1) and y == yc - 3) else 'brass', bev=1)
    return P
def work_gloves(F, Pb, Pc):
    """heavy leather gloves with flared cuffs: replace the hands"""
    P = {}; AW = F['AW']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]
        P['hand_' + s] = paint(grow(Pb['hand_' + s]), lambda x, y, z, f, b, a, m: 'leather_d' if z == h0 else 'leather')
        box(P, 'hand_' + s, x0 - 1, x1 + 1, ay0 - 2, ay0 + AW + 1, al0 - 2, al0 - 1, 'leather_l', bev=1)
    return P

# ---------------------------------------------------------------- plate: Ironclad (steam), exposed mechanical joints
def full_helm(F, Pb, Pc):
    """a full helm: a shell round the whole head, an eye slit, breaths, a brass crest; it hides hair and beard"""
    h = Head(F); P = {}; X0, Y0, Z0, W, D, H = h.X0, h.Y0, h.Z0, h.W, h.D, h.H; part = 'helm@head#2'
    x0, x1, y0, y1, z0, z1 = X0 - 2, X0 + W + 1, Y0 - 4, Y0 + D + 1, Z0 - 1, Z0 + H + 2
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                shell = x < x0 + 2 or x > x1 - 2 or y < y0 + 2 or y > y1 - 2 or z > z1 - 2
                if not shell: continue
                if ((x in (x0, x1)) + (y in (y0, y1)) + (z == z1)) >= 2: continue      # rounded edges
                c, d, v = X0 + W - 1 - x, y - Y0, Z0 + H - 1 - z
                col = 'iron'
                if y < y0 + 2:          # the face plate
                    if 12 <= v <= 14 and h.eyes[0] - 1 <= c <= h.eyes[1] + 6: col = 'rubber' if not (c == h.mid - 1 or c == h.mid) else 'iron_d'
                    elif 19 <= v <= 25 and abs(c - h.mid + 0.5) < 5 and (c + v) % 2 == 0: col = 'iron_d'
                    elif c in (h.mid - 1, h.mid): col = 'iron_l'
                if v == 4 and (x + y) % 3 == 0: col = 'brass_l'      # a band of rivets
                if z <= z0 + 1: col = 'iron_d'                      # the gorget rim
                P.setdefault(part, {})[(x, y, z)] = col
    for y in range(y0 + 1, y1):                                     # the crest
        for x in (X0 + W // 2 - 1, X0 + W // 2):
            for z in (z1 + 1, z1 + 2): P[part][(x, y, z)] = 'brass' if z == z1 + 1 else 'brass_l'
    return P
def breastplate(F, Pb, Pc):
    """a breastplate: replaces the torso; a ridged plastron, a fauld of lames at the hips, a gorget, rivets at the sides"""
    hip, top, cx = F['hip'], F['top'], F['cx']
    chest = set(range(hip + 8, top + 1))
    def col(x, y, z, front, back, xmin, xmax):
        if z >= top - 1: return 'iron_d'
        if z <= hip + 6: return 'iron_d' if (z - hip) % 2 == 1 else 'iron'
        if y == front and x in (cx - 1, cx): return 'iron_l'
        if x in (xmin, xmax) and z % 3 == 0: return 'brass_l'
        return 'iron'
    return {'torso': paint(grow(grow(Pc['torso']), 1, zs=chest), col)}
def plate_arms(F, Pb, Pc):
    """plate arms: replace the upper and lower arms; round pauldrons, elbow cops and exposed pistons at the joints"""
    P = {}; AW = F['AW']; top = F['top']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]; o = out_side(F, s)
        P['arm_upper_' + s] = paint(grow(Pb['arm_upper_' + s]), lambda x, y, z, f, b, a, m: 'iron_d' if z % 3 == 0 else 'iron')
        P['arm_lower_' + s] = paint(grow(Pb['arm_lower_' + s]), lambda x, y, z, f, b, a, m: 'iron_d' if z in (al0, al0 + 1) else 'iron')
        box(P, 'arm_lower_' + s, x0, x1, ay0 + AW + 1, ay0 + AW + 2, au0 - 3, au0 - 1, 'iron_l')         # elbow cop
        pauldron(F, P, s, 'iron', lames=4)
        px = (x1 + 2) if o > 0 else (x0 - 2); py = ay0 + AW // 2
        for z in range(au0 + 1, top - 3):        # the piston from shoulder to elbow, on the outer side
            P.setdefault('piston_%s@arm_upper_%s' % (s, s), {})[(px, py, z)] = 'iron_l' if z < (au0 + top) // 2 else 'copper'
            if z >= (au0 + top) // 2: P['piston_%s@arm_upper_%s' % (s, s)][(px, py + 1, z)] = 'copper_d'
        for z in range(al0 + 2, au0 - 2):        # and down the back of the forearm
            P['arm_lower_' + s][((x0 + x1) // 2, ay0 + AW + 1, z)] = 'brass' if z % 4 else 'brass_d'
    return P
def gauntlets(F, Pb, Pc):
    P = {}; AW = F['AW']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]
        P['hand_' + s] = paint(grow(Pb['hand_' + s]), lambda x, y, z, f, b, a, m: 'iron_d' if (y == f and z % 2 == 0) else 'iron')
        box(P, 'hand_' + s, x0 - 1, x1 + 1, ay0 - 2, ay0 + AW + 1, al0 - 2, al0 - 1, 'iron_l', bev=1)
    return P
def plate_legs(F, Pb, Pc):
    """plate legs: replace thighs and shins; tassets hang from the hips, knee cops (poleyns) with a rivet"""
    P = {}; LL, hip = F['LL'], F['hip']
    for s in SIDES:
        x0, x1, yc = F['legs'][s]
        box(P, 'leg_upper_' + s, x0 - 1, x1 + 1, yc - 1, yc + 8, 9 + LL, hip, lambda x, y, z: 'iron_d' if z % 3 == 0 else 'iron', bev=1)
        box(P, 'leg_lower_' + s, x0 - 1, x1 + 1, yc - 1, yc + 8, 7, 8 + LL, lambda x, y, z: 'iron_d' if z == 7 else 'iron', bev=1)
        box(P, 'leg_lower_' + s, x0, x1, yc - 3, yc - 2, 6 + LL, 9 + LL, lambda x, y, z: 'brass_l' if (z == 8 + LL and x == (x0 + x1) // 2) else 'iron_l', bev=1)
        for k in range(3):                       # tassets: three lames over the front of the thigh
            z = hip - k * 2
            for x in range(x0 - 1, x1 + 2):
                for zz in (z, z - 1): P.setdefault('tasset_%s@leg_upper_%s' % (s, s), {})[(x, yc - 2 - (k == 0), zz)] = 'iron_d' if zz == z - 1 else 'iron_l'
    return P
def sabatons(F, Pb, Pc):
    P = {}
    for s in SIDES:
        P['foot_' + s] = paint(grow(Pc['foot_' + s], 1, zs={4, 5, 6}), lambda x, y, z, f, b, a, m: 'iron_d' if (z == 0 or (y == f and z % 2)) else 'iron')
    return P

# ---------------------------------------------------------------- the rig: an arcane-engine exosuit (arcane engine era)
RL = 10     # the rig lifts its pilot this many voxels (25 cm) off the ground
def rig(F, Pb, Pc):
    """a powered suit the pilot climbs into: it replaces the torso, arms, hands, legs and feet with its own frame, and
    lifts the pilot; a glowing arcane core, an engine on the back with exhaust stacks, a roll cage over the head.
    Kept inside the standard door: under 2.2 m tall and 1.4 m wide."""
    P = {}; hip, top, TW, TD, cx = F['hip'], F['top'], F['TW'], F['TD'], F['cx']
    # the chassis: the pilot's clothed torso held in a frame, a pelvis block below, the engine behind
    P['torso'] = dict(Pc['torso'])
    box(P, 'torso', -3, TW + 2, -3, TD + 2, hip - 3, hip, lambda x, y, z: 'iron_d' if z == hip - 3 else 'iron', bev=1)
    for (x, y) in ((-3, -3), (TW + 2, -3), (-3, TD + 2), (TW + 2, TD + 2)):    # corner posts
        for z in range(hip + 1, top + 2): P['torso'][(x, y, z)] = 'iron_l' if z % 4 else 'brass'
    for x in range(-3, TW + 3):
        for y in (-3, TD + 2): P['torso'][(x, y, top + 1)] = 'iron'
    for y in range(-3, TD + 3):
        for x in (-3, TW + 2): P['torso'][(x, y, top + 1)] = 'iron'
    for x in range(cx - 2, cx + 2):             # the arcane core, on the pelvis block
        for z in range(hip - 2, hip + 1): P['torso'][(x, -4, z)] = 'arc' if 0 <= x - cx + 1 <= 1 else 'brass'
    box(P, 'torso', 1, TW - 2, TD + 3, TD + 8, hip - 2, top + 3, lambda x, y, z: 'arc' if (y == TD + 8 and z % 3 == 0 and 3 <= x <= TW - 4) else 'iron_d', bev=1)
    for ex in (2, TW - 3):                      # exhaust stacks
        for z in range(top + 4, top + 11):
            for x in (ex - 1, ex):
                for y in (TD + 6, TD + 7): P['torso'][(x, y, z)] = 'copper' if z >= top + 9 else 'iron'
    for x in range(-2, TW + 2):                 # the roll cage over the pilot's head
        P.setdefault('cage@torso', {})[(x, TD + 2, top + 19)] = 'iron'
        P['cage@torso'][(x, TD + 2, top + 20)] = 'iron_d'
    for x in (-2, TW + 1):
        for z in range(top + 2, top + 21): P['cage@torso'][(x, TD + 2, z)] = 'iron'
    for y in range(-2, TD + 2): P['cage@torso'][(cx, y, top + 20)] = 'iron'
    P['cage@torso'][(cx, -3, top + 19)] = 'arc'; P['cage@torso'][(cx - 1, -3, top + 19)] = 'arc'
    # legs: thick frames with pistons, the knee forward, big clawed feet below the pilot
    knee = (hip - 4 - RL) // 2
    for s in SIDES:
        x0, x1, yc = F['legs'][s]
        box(P, 'leg_upper_' + s, x0 - 1, x1 + 1, yc - 2, yc + 8, knee + 1, hip - 4, lambda x, y, z: 'iron_d' if z % 4 == 0 else 'iron', bev=1)
        for z in range(knee + 2, hip - 4): P['leg_upper_' + s][((x0 + x1) // 2, yc - 3, z)] = 'iron_l' if z < (knee + hip) // 2 else 'copper'
        box(P, 'leg_lower_' + s, x0, x1, yc - 1, yc + 7, -RL + 5, knee, 'iron', bev=1)
        box(P, 'leg_lower_' + s, x0, x1, yc - 4, yc - 2, knee - 2, knee + 1, 'brass', bev=1)
        for z in range(-RL + 5, knee - 2): P['leg_lower_' + s][((x0 + x1) // 2, yc + 8, z)] = 'copper'
        box(P, 'foot_' + s, x0 - 2, x1 + 2, yc - 2, yc + 9, -RL, -RL + 4, lambda x, y, z: 'iron_d' if z == -RL else 'iron', bev=1)
        for k in range(3):                      # three toes
            tx = x0 - 2 + k * (x1 - x0 + 4) // 2
            box(P, 'foot_' + s, tx, tx + 1, yc - 6, yc - 3, -RL, -RL + 2, 'iron_d')
    # arms: a ball joint at each shoulder, a heavy upper arm, a forearm with an arcane strip, a three-fingered clamp
    elbow = (top + hip) // 2
    for s in SIDES:
        o = out_side(F, s); ax0 = TW + 3 if o > 0 else -12; ax1 = ax0 + 9
        box(P, 'arm_upper_' + s, ax0, ax1, -2, TD + 1, elbow, top + 2, lambda x, y, z: 'iron_d' if z % 4 == 0 else 'iron', bev=2)
        box(P, 'arm_upper_' + s, ax0 + 2, ax1 - 2, 0, TD - 1, top + 3, top + 5, 'brass', bev=1)
        box(P, 'arm_lower_' + s, ax0 - 1, ax1 + 1, -3, TD + 2, hip - 2, elbow - 1, lambda x, y, z: 'arc' if (y == -3 and x in (ax0 + 4, ax0 + 5)) else 'iron', bev=2)
        for fx in (ax0, ax0 + 4, ax0 + 8):      # the clamp: two fingers forward, one thumb behind
            fy = -3 if fx != ax0 + 4 else TD - 1
            box(P, 'hand_' + s, fx, fx + 1, fy, fy + 3, hip - 9, hip - 3, lambda x, y, z: 'iron_d' if z == hip - 9 else 'iron_l')
    return P

# ---------------------------------------------------------------- colossus arms: the heaviest mechanical arms
def colossus_arms(F, Pb, Pc):
    """the heaviest mechanical arms, worn over anything (the user's reference: huge bronze arms over a light uniform).
    They replace both whole arms: a domed shoulder with a round port in its side and a gear rim behind, a thick upper
    arm, a ball elbow, a forearm swelling toward a huge fist with brass-capped knuckles hanging to the knees, a red hose
    from shoulder to forearm; corrugated cables run from the back of the neck to each shoulder. Within the door's width."""
    P = {}; top, TW, TD, cx, LL = F['top'], F['TW'], F['TD'], F['cx'], F['LL']
    r = 6; sz = top - 1; sy = TD // 2
    h0 = 7 + LL; elbow = sz - (sz - (h0 + 10)) * 9 // 20
    for s in SIDES:
        o = out_side(F, s); sx = TW + 5 if o > 0 else -6
        U, L, Hd = 'arm_upper_' + s, 'arm_lower_' + s, 'hand_' + s
        for x in range(sx - r, sx + r + 1):        # the shoulder dome
            for y in range(sy - r, sy + r + 1):
                for z in range(sz - r, sz + r + 1):
                    d2 = (x - sx) ** 2 + (y - sy) ** 2 + (z - sz) ** 2
                    if d2 > r * r + r: continue
                    pr = ((y - sy) ** 2 + (z - sz) ** 2) ** 0.5
                    if (x - sx) * o >= r - 1 and pr <= 3: c = 'rubber' if pr <= 1.5 else 'iron_d'       # the round port
                    elif y >= sy + r - 1 and (x + z) % 2 == 0: c = 'iron'                                 # the gear rim behind
                    elif abs(z - sz) == 2 or abs((x - sx) * o - 2) == 0 and z > sz: c = 'bronze_d'         # plate seams
                    elif z >= sz + r - 2: c = 'bronze_l'
                    else: c = 'bronze'
                    P.setdefault(U, {})[(x, y, z)] = c
        box(P, U, sx - 3, sx + 3, sy - 3, sy + 3, elbow + 1, sz - r, lambda x, y, z: 'bronze_d' if z % 4 == 0 else ('bronze_l' if (x - sx) * o == 3 else 'bronze'), bev=1)
        for x in range(sx - 4, sx + 5):             # the elbow ball
            for y in range(sy - 4, sy + 5):
                for z in range(elbow - 4, elbow + 1):
                    if (x - sx) ** 2 + (y - sy) ** 2 + (z - elbow + 2) ** 2 <= 17: P.setdefault(L, {})[(x, y, z)] = 'brass_d' if z == elbow - 2 else 'iron'
        for z in range(h0 + 10, elbow - 3):         # the forearm, swelling toward the fist
            w = 3 + (elbow - 3 - z) * 3 // max(1, elbow - h0 - 13)
            for x in range(sx - w, sx + w + 1):
                for y in range(sy - w, sy + w + 1):
                    edge = abs(x - sx) == w and abs(y - sy) == w
                    if edge: continue
                    P[L][(x, y, z)] = 'bronze_d' if z % 5 == 0 else ('bronze_l' if y == sy - w and abs(x - sx) <= 1 else 'bronze')
        box(P, Hd, sx - 6, sx + 5, sy - 6, sy + 5, h0, h0 + 9, lambda x, y, z: 'bronze_d' if (y == sy - 6 and (x - sx) % 3 == 0) or z == h0 else 'bronze', bev=2)
        for k in range(4):                          # brass caps on the knuckles
            kx = sx - 5 + k * 3
            for x in (kx, kx + 1):
                for z in (h0 + 6, h0 + 7): P[Hd][(x, sy - 7, z)] = 'brass_l'
        tx = sx - 7 * o if True else 0              # the thumb, on the inner side
        box(P, Hd, min(tx, tx + o), max(tx, tx + o), sy - 4, sy - 1, h0 + 3, h0 + 7, 'bronze_d')
        for z in range(elbow - 2, sz - 2):          # the red hose: shoulder to elbow...
            P[U if z > elbow else L][(sx + 3 * o, sy - 5, z)] = 'hose' if z % 3 else 'hose_d'
        for z in range(h0 + 12, elbow - 1):         # ...and on down the forearm's outer side
            P[L][(sx + 6 * o, sy - 2, z)] = 'hose' if z % 3 else 'hose_d'
        for k in range(abs(sx - cx) - r):           # corrugated cables from the back of the neck
            x = cx + k * o if o > 0 else cx - 1 + k * o
            for y in (TD - 3, TD - 2):
                P.setdefault('cables@torso', {})[(x, y, top + 1)] = 'rubber' if k % 2 else 'iron_d'
                P['cables@torso'][(x, y, top + 2)] = 'rubber' if k % 2 else 'iron_d'
    return P

# ---------------------------------------------------------------- back arms: a third arm on a pack (back slot)
# The references: an arm that rises from the upper back well above the head and arcs forward like a scorpion's tail,
# its joints glowing; a buckled leather pack with a cog at every joint, the claw holding a potion; a mast on the pack
# with two arms spread wide, each ending in a triple-barrelled cannon. Our own design in brass, iron and leather.
def beam(P, part, a, b, w, col):
    """a thick straight segment from a to b (any angle, stepped on the grid), w voxels across"""
    n = max(abs(b[i] - a[i]) for i in range(3)) * 2 or 1; h = w // 2
    for i in range(n + 1):
        p = tuple(round(a[k] + (b[k] - a[k]) * i / n) for k in range(3))
        for dx in range(-h, w - h):
            for dy in range(-h, w - h):
                for dz in range(-h, w - h):
                    P.setdefault(part, {})[(p[0] + dx, p[1] + dy, p[2] + dz)] = col(i, n) if callable(col) else col
def cog(P, part, c, r=3, side=1, core='glow'):
    """a brass cog turned to face sideways, teeth round its rim and a glowing core: a joint"""
    import math
    for dy in range(-r - 1, r + 2):
        for dz in range(-r - 1, r + 2):
            d = (dy * dy + dz * dz) ** 0.5
            tooth = r < d <= r + 1 and int(round(math.atan2(dz, dy) * 8 / math.pi)) % 2 == 0
            if d <= r or tooth:
                for dx in (0, side):
                    P.setdefault(part, {})[(c[0] + dx, c[1] + dy, c[2] + dz)] = core if d < 1.2 else ('brass_d' if d > r - 0.6 and not tooth else 'brass')
def pack(F, P):
    """a buckled leather pack on the back, straps over the shoulders, a cog on its side"""
    top, TW, TD = F['top'], F['TW'], F['TD']; part = 'pack@torso'
    box(P, part, 3, TW - 4, TD, TD + 4, top - 12, top - 1, lambda x, y, z: 'leather_l' if z >= top - 3 else ('leather_d' if z == top - 12 else 'leather'), bev=1)
    for x in (6, TW - 7):                       # buckled straps down the back of the pack
        for z in range(top - 11, top - 1): P[part][(x, TD + 5, z)] = 'leather_d'
        P[part][(x, TD + 6, top - 6)] = 'brass'
    for x in (4, TW - 5):                       # shoulder straps
        for y in range(-1, TD): P[part][(x, y, top + 1)] = 'leather_d'
        for z in range(top - 7, top + 1): P[part][(x, -1, z)] = 'leather_d'
        P[part][(x, -2, top - 4)] = 'brass'
    cog(P, part, (2, TD + 2, top - 7), r=2, side=-1, core='brass_l')
def spine(F, P):
    """an iron spine down the back, its vertebrae plated, a glowing core between the shoulder blades, straps over the
    shoulders: the other way to carry an arm (or two)"""
    top, hip, TD, cx = F['top'], F['hip'], F['TD'], F['cx']; part = 'spine@torso'
    for z in range(hip + 2, top + 1):
        wide = (z - hip) % 3 == 0
        for x in range(cx - (3 if wide else 1), cx + (3 if wide else 1)):
            for y in (TD, TD + 1) if not wide else (TD, TD + 1, TD + 2): P.setdefault(part, {})[(x, y, z)] = 'iron_l' if wide and y == TD + 2 else ('iron_d' if wide else 'iron')
    for x in range(cx - 2, cx + 2):
        for z in range(top - 6, top - 2): P[part][(x, TD + 3, z)] = 'glow' if 0 <= x - cx + 1 <= 1 and top - 5 <= z <= top - 4 else 'brass'
    for x in (4, F['TW'] - 5):
        for y in range(-1, TD): P[part][(x, y, top + 1)] = 'leather_d'
        for z in range(top - 7, top + 1): P[part][(x, -1, z)] = 'leather_d'
def seg(i, n): return 'brass' if i % 6 == 0 else ('iron_d' if i % 6 == 3 else 'iron')
def back_arm(F, head):
    P = {}; top, TW, TD = F['top'], F['TW'], F['TD']
    (pack if head == 'claw' else spine)(F, P); A = 'backarm@torso'
    ax = max(TW - 1, TW // 2 + 8)               # outside the head, behind the left shoulder
    if head == 'cannons':                       # a mast with a lamp, two arms spread wide, triple barrels
        m = TW // 2
        beam(P, A, (m, TD + 2, top - 1), (m, TD + 2, top + 21), 3, seg)
        for x in (m - 1, m, m + 1):
            for z in (top + 22, top + 23, top + 24): P[A][(x, TD + 2, z)] = 'glow' if x == m and z < top + 24 else 'brass'
        for o, ex in ((-1, -9), (1, TW + 8)):
            sh = (m + 2 * o, TD + 2, top + 18); el = (ex, TD, top + 18); hd = (ex, -1, top + 12)
            beam(P, A, sh, el, 3, seg); cog(P, A, el, 2, side=o); beam(P, A, el, hd, 3, seg)
            box(P, A, ex - 3, ex + 3, -10, -2, top + 9, top + 15, lambda x, y, z: 'brass' if y in (-2, -3) else 'iron_d', bev=2)
            for bx, bz in ((ex - 2, top + 13), (ex + 2, top + 13), (ex, top + 10)):    # three barrels
                for y in range(-13, -9):
                    for dx in (0, 1):
                        for dz in (0, 1): P[A][(bx + dx - 1 if bx > ex else bx + dx, y, bz + dz)] = 'rubber' if (y == -13 and dx == dz) else 'brass_d'
        return P
    base = (ax - 2, TD + 2, top)
    if head == 'shield':                        # over the shoulder and down before the chest
        j1 = (ax, TD + 1, top + 14); j2 = (ax + 1, -3, top + 16); tool = (ax - 2, -8, top - 2)
    else:                                       # high above the head, arcing forward, the tool out in front
        j1 = (ax + 1, TD + 1, top + 24); j2 = (ax, -4, top + 28); tool = (ax, -9, top + 20)
    cog(P, A, base, 3, side=1)
    beam(P, A, base, j1, 3, seg)
    for i in range(1, 9):                       # a piston alongside the first segment
        p = tuple(round(base[k] + (j1[k] - base[k]) * i / 10) for k in range(3))
        P[A][(p[0] + 2, p[1] + 1, p[2])] = 'copper' if i > 4 else 'iron_l'
    cog(P, A, j1, 3, side=1)
    beam(P, A, j1, j2, 3, seg)
    cog(P, A, j2, 2, side=1)
    beam(P, A, j2, tool, 2, seg)
    tx, ty, tz = tool
    if head == 'claw':                          # three fingers round a potion bottle
        for k in range(4):
            for fx, fz in ((tx - 2, tz + 2 - k // 2), (tx + 2, tz + 2 - k // 2), (tx, tz - 3 + k // 3)):
                P[A][(fx, ty - 1 - k, fz)] = 'brass' if k < 3 else 'iron_l'
        box(P, A, tx - 1, tx + 1, ty - 4, ty - 2, tz - 1, tz + 1, lambda x, y, z: 'glass_l' if (x, z) == (tx - 1, tz + 1) else 'potion')
        P[A][(tx, ty - 3, tz + 2)] = 'leather'                 # the cork
    if head == 'saw':                           # a toothed disc, half in its guard
        import math
        cy, cz, r = ty - 6, tz, 6
        for y in range(cy - r - 1, cy + r + 2):
            for z in range(cz - r - 1, cz + r + 2):
                d = ((y - cy) ** 2 + (z - cz) ** 2) ** 0.5
                if d <= r: P[A][(tx, y, z)] = 'brass_l' if d < 1.5 else ('iron_l' if d > r - 1 else 'iron')
                elif d <= r + 1 and int(round(math.atan2(z - cz, y - cy) * 4)) % 2 == 0: P[A][(tx, y, z)] = 'iron_l'
                if z >= cz + 2 and r - 0.5 <= d <= r + 2: P[A][(tx - 1, y, z)] = 'copper'; P[A][(tx + 1, y, z)] = 'copper'
    if head == 'shield':                        # a broad plate guarding the chest and the left side
        sx0, sx1 = tx - 9, tx + 4; sz0, sz1 = top - 12, top + 2
        for x in range(sx0, sx1 + 1):
            for z in range(sz0, sz1 + 1):
                if (x in (sx0, sx1)) and (z in (sz0, sz1)): continue
                rim = x in (sx0, sx1) or z in (sz0, sz1)
                boss = abs(x - (sx0 + sx1) // 2) <= 1 and abs(z - (sz0 + sz1) // 2) <= 1
                P[A][(x, ty - 1, z)] = 'brass' if rim else ('glow' if boss and (x, z) == ((sx0 + sx1) // 2, (sz0 + sz1) // 2) else ('brass_l' if boss else ('iron_d' if (x - sx0) % 4 == 0 else 'iron')))
                if rim or boss: P[A][(x, ty - 2, z)] = 'brass_d'
    return P
def arm_claw(F, Pb, Pc): return back_arm(F, 'claw')
def arm_saw(F, Pb, Pc): return back_arm(F, 'saw')
def arm_bulwark(F, Pb, Pc): return back_arm(F, 'shield')
def arm_cannons(F, Pb, Pc): return back_arm(F, 'cannons')

def colossus_gauntlets(F, Pb, Pc):
    """the colossus arms as gauntlets only (the Vi reference): huge plated forearms and fists from the elbow down, blued
    steel panels in brass frames, a glowing gem at the wrist, segmented fingers; the upper arm and sleeve stay"""
    P = {}; AW = F['AW']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]; o = out_side(F, s)
        X0, X1, Y0, Y1 = x0 - 3, x1 + 3, ay0 - 3, ay0 + AW + 2
        def plate(x, y, z, zb, zt):
            edge = x in (X0, X1) or y in (Y0, Y1)
            if z in (zb, zt) or (edge and (z - zb) % 4 == 0): return 'brass'
            if y == Y0 and abs(x - (X0 + X1) / 2) < 2: return 'brass_l'
            return 'blued' if not edge or (x + z) % 5 else 'blued_d'
        box(P, 'arm_lower_' + s, X0, X1, Y0, Y1, al0, au0 - 1, lambda x, y, z: plate(x, y, z, al0, au0 - 1), bev=2)
        gx = X1 + 1 if o > 0 else X0 - 1         # the gem on the outer side of the wrist
        for y in range(ay0, ay0 + 3):
            for z in range(al0 + 2, al0 + 5): P['arm_lower_' + s][(gx, y, z)] = 'arc' if (y - ay0, z - al0) in ((1, 3), (1, 2)) else 'brass'
        hz0 = h0 - 4
        box(P, 'hand_' + s, X0, X1, Y0 - 1, Y1, hz0, al0 - 1, lambda x, y, z: 'brass' if z == al0 - 1 else ('blued_d' if (y == Y0 - 1 and (x - X0) % 3 == 0) or z == hz0 else 'blued'), bev=2)
        for x in range(X0 + 1, X1):              # the knuckle row
            P['hand_' + s][(x, Y0 - 2, hz0 + 5)] = 'brass_l' if (x - X0) % 3 else 'brass_d'
            P['hand_' + s][(x, Y0 - 2, hz0 + 4)] = 'brass_d'
    return P

# ---------------------------------------------------------------- the basics: one common item in every slot
# Plain, everyday gear for the start: wool, canvas, quilting and leather, simple stitching (common rarity, design.md).
def cap(F, Pb, Pc):
    """a flat cloth cap with a short brim; long hair falls below it"""
    h = Head(F); P = {}; X0, Y0, Z0, W, D, H = h.X0, h.Y0, h.Z0, h.W, h.D, h.H; part = 'cap@head#2'
    for x in range(X0 - 1, X0 + W + 1):
        for y in range(Y0 - 1, Y0 + D + 1):
            for z in range(Z0 + H - 6, Z0 + H + 2):
                if X0 <= x < X0 + W and Y0 <= y < Y0 + D and z < Z0 + H: continue
                if (x in (X0 - 1, X0 + W)) and (y in (Y0 - 1, Y0 + D)): continue
                P.setdefault(part, {})[(x, y, z)] = 'wool_d' if z == Z0 + H - 6 else ('wool' if (x + y) % 5 else 'wool_d')
    for x in range(X0 + 1, X0 + W - 1):
        for y in range(Y0 - 5, Y0 - 1):
            for z in (Z0 + H - 6, Z0 + H - 5): P[part][(x, y, z)] = 'wool_d'
    return P
def spectacles(F, Pb, Pc):
    """round wire spectacles: rims round each eye, a bridge, arms back to the ears"""
    h = Head(F); P = {}; part = 'specs@head#2'
    for c0 in h.eyes:
        for c in range(c0 - 1, c0 + 7):
            for v in range(12, 18):
                if (c in (c0 - 1, c0 + 6) or v in (12, 17)) and not ((c in (c0 - 1, c0 + 6)) and (v in (12, 17))): h.put(P, part, c, -2, v, 'iron_d')
    for c in range(h.eyes[0] + 7, h.eyes[1] - 1): h.put(P, part, c, -2, 13, 'iron_d')
    for d in range(-2, h.D // 2): h.put(P, part, -1, d, 14, 'iron_d'); h.put(P, part, h.W, d, 14, 'iron_d')
    return P
def scarf(F, Pb, Pc):
    """a wool scarf wound round the neck and pulled up over mouth and nose, its tail hanging down the back"""
    h = Head(F); P = {}; part = 'scarf@head#2'
    for v in range(19, 31):
        for c in range(-1, h.W + 1):
            h.put(P, part, c, -3, v, 'red_d' if v % 3 == 0 else 'red')
        for d in range(-3, h.D + 1):
            h.put(P, part, -1, d, v, 'red'); h.put(P, part, h.W, d, v, 'red')
        for c in range(-1, h.W + 1): h.put(P, part, c, h.D, v, 'red')
    top, TD, cx = F['top'], F['TD'], F['cx']
    for z in range(top - 10, top + 1):
        for x in (cx + 1, cx + 2, cx + 3): P.setdefault('scarf@torso', {})[(x, TD, z)] = 'red_d' if z == top - 10 or x == cx + 3 else 'red'
    return P
def shoulder_pads(F, Pb, Pc):
    """quilted shoulder pads, stitched in rows"""
    P = {}; AW = F['AW']; top = F['top']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]
        box(P, 'pad_%s@arm_upper_%s' % (s, s), x0 - 1, x1 + 1, ay0 - 1, ay0 + AW, top - 3, top + 1, lambda x, y, z: 'quilt_d' if (z - top) % 2 == 0 else 'quilt', bev=1)
    return P
def armbands(F, Pb, Pc):
    """a leather band round each upper arm, buckled"""
    P = {}; AW = F['AW']; top = F['top']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]; part = 'band_%s@arm_upper_%s' % (s, s)
        for x in range(x0 - 1, x1 + 2):
            for y in range(ay0 - 1, ay0 + AW + 1):
                if x in (x0 - 1, x1 + 1) or y in (ay0 - 1, ay0 + AW):
                    for z in (top - 7, top - 6): P.setdefault(part, {})[(x, y, z)] = 'leather_d'
        P[part][((x0 + x1) // 2, ay0 - 2, top - 7)] = 'brass'
    return P
def gambeson(F, Pb, Pc):
    """a quilted gambeson: replaces the torso; diamond stitching, a standing collar, ties down the front"""
    top, cx = F['top'], F['cx']
    def col(x, y, z, front, back, xmin, xmax):
        if z >= top - 1: return 'quilt_d'
        if y == front and cx - 1 <= x <= cx and z % 3 == 0: return 'cord'
        return 'quilt_d' if (x + z) % 4 == 0 or (x - z) % 4 == 0 else 'quilt'
    return {'torso': paint(grow(Pc['torso']), col)}
def long_coat(F, Pb, Pc):
    """a long travelling coat: a shell outside the chest, open down the front with brass buttons, a raised collar, and a
    skirt riding each thigh down to the knee (as WoW skins its coat skirts to the thighs)"""
    P = {}; top, hip, cx, LL = F['top'], F['hip'], F['cx'], F['LL']
    t = Pc['torso']; outer = grow(t, 2)
    fy = {}
    for (x, y, z) in outer: fy[(x, z)] = min(fy.get((x, z), 99), y)
    for (x, y, z) in outer:
        if (x, y, z) in grow(t, 1): continue
        if y == fy[(x, z)] and cx - 2 <= x <= cx + 1 and z < top: continue          # open at the front
        col = 'cloth_b'
        if y == fy[(x, z)] and x in (cx - 3, cx + 2) and z % 4 == 0: col = 'brass'
        if z >= top - 1: col = 'cloth_b_d'
        P.setdefault('coat@torso', {})[(x, y, z)] = col
    for (x, y, z) in list(P['coat@torso']):
        if z == top: P['coat@torso'][(x, y, z + 1)] = 'cloth_b_d'; P['coat@torso'][(x, y, z + 2)] = 'cloth_b_d'
    for s in SIDES:
        x0, x1, yc = F['legs'][s]; inner = x0 if s == 'l' else x1
        for z in range(9 + LL - 1, hip + 1):
            for x in range(x0 - 2, x1 + 3):
                for y in range(yc - 2, yc + 10):
                    edge = x in (x0 - 2, x1 + 2) or y in (yc - 2, yc + 9)
                    if not edge: continue
                    if x == (x0 - 2 if s == 'l' else x1 + 2): continue                 # open on the inner side
                    if y == yc - 2 and (x <= x0 if s == 'l' else x >= x1): continue    # and at the front
                    P.setdefault('coatskirt_%s@leg_upper_%s' % (s, s), {})[(x, y, z)] = 'cloth_b_d' if z == 9 + LL - 1 else 'cloth_b'
    return P
def wrist_wraps(F, Pb, Pc):
    """cloth wraps round the wrists: replace the forearms (bare inside, with their marks)"""
    P = {}; AW = F['AW']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]
        P['arm_lower_' + s] = dict(Pb['arm_lower_' + s])
        box(P, 'arm_lower_' + s, x0 - 1, x1 + 1, ay0 - 1, ay0 + AW, al0, al0 + 4, lambda x, y, z: 'canvas' if (x + z) % 3 else 'linen_d')
    return P
def leather_gloves(F, Pb, Pc):
    P = {}; AW = F['AW']
    for s in SIDES:
        x0, x1, ay0, au0, al0, h0 = F['arms'][s]
        P['hand_' + s] = paint(grow(Pb['hand_' + s], 1, zs={al0 - 1}), lambda x, y, z, f, b, a, m: 'leather_d' if z == al0 - 1 or (y == f and z % 2) else 'leather')
    return P
def plain_belt(F, Pb, Pc):
    P = {}; hip = F['hip']; fy = belt(F, P, Pc, mat='leather', buckle='iron_l')
    pouch(P, 'belt@torso', 1, fy - 1, hip - 2, w=3, d=2, h=3)
    return P
def work_trousers(F, Pb, Pc):
    """reinforced work trousers: replace the legs; leather knee patches, seams; no boot cuff"""
    P = {}; LL, hip = F['LL'], F['hip']
    for s in SIDES:
        x0, x1, yc = F['legs'][s]
        box(P, 'leg_upper_' + s, x0, x1, yc, yc + 7, 9 + LL, hip, lambda x, y, z: 'trousers_d' if x in (x0, x1) and z % 3 == 0 else 'trousers')
        box(P, 'leg_lower_' + s, x0, x1, yc, yc + 7, 7, 8 + LL, lambda x, y, z: 'leather' if (y == yc and 6 + LL <= z and x0 < x < x1) else ('trousers_d' if z == 7 else 'trousers'))
    return P
def shoes(F, Pb, Pc):
    """low leather shoes, the trouser leg falling to them"""
    P = {}
    for s in SIDES:
        x0, x1, yc = F['legs'][s]
        box(P, 'foot_' + s, x0, x1, yc - 1, yc + 7, 0, 3, lambda x, y, z: 'leather_d' if z == 0 else ('leather_l' if z == 3 else 'leather'), bev=1)
        box(P, 'foot_' + s, x0, x1, yc, yc + 7, 4, 6, 'trousers')
    return P
def knapsack(F, Pb, Pc):
    """a canvas knapsack with a bedroll strapped on top and a tin cup"""
    P = {}; top, TW, TD, cx = F['top'], F['TW'], F['TD'], F['cx']; part = 'knapsack@torso'
    box(P, part, 3, TW - 4, TD, TD + 4, top - 11, top - 3, lambda x, y, z: 'canvas' if z > top - 10 else 'leather_d', bev=1)
    for x in range(2, TW - 2):                  # the bedroll
        for y in range(TD + 1, TD + 5):
            for z in (top - 2, top - 1, top):
                if (y - TD - 3) ** 2 + (z - top + 1) ** 2 <= 3: P[part][(x, y, z)] = 'wool_d' if x in (4, TW - 5) else 'wool'
    for x in (4, TW - 5):
        for y in range(-1, TD): P[part][(x, y, top + 1)] = 'leather_d'
        for z in range(top - 7, top + 1): P[part][(x, -1, z)] = 'leather_d'
    box(P, part, cx - 1, cx + 1, TD + 5, TD + 6, top - 9, top - 7, 'iron_l')
    return P

# ---------------------------------------------------------------- ammunition (the ammunition slot, on the belt)
# Worn on the belt (the quiver at the right hip, the others behind) so a knapsack or anything on the back can still be worn. Finer voxels (#2): the torso's back face
# is at y = 2 * TD, the belt at z = 2 * hip + 2 .. 2 * hip + 5; low x is the wearer's right, y below 0 is in front.
def _rod(P, part, a, b, c, r=0.0):
    """voxels along the line a -> b (r: a thicker rod)"""
    n = max(abs(b[i] - a[i]) for i in range(3)) or 1
    for t in range(n + 1):
        q = tuple(round(a[i] + (b[i] - a[i]) * t / n) for i in range(3))
        P[part][q] = c
def quiver(F, Pb, Pc):
    """a side quiver for bows (Doc Tan's references), worn on the body: strapped tight to the belt at the right hip, just
    behind the hanging arm; a flat leather case slanting from a wide laced mouth at the hip down and back past the seat
    to a narrow capped foot; brass studs round the mouth and along the top, a tooled panel; the arrows stand up out of
    the mouth behind the arm, where the drawing hand reaches back for them"""
    P = {}; hip = F['hip']; part = 'ammo@torso#2'; P[part] = {}
    TD = F['TD']
    sl = math.radians(52); L = 42
    m = (-3, 2 * TD + 1, 2 * hip - 1)                   # the mouth's centre: at the hip, behind the arm, against the body
    ay, az = math.cos(sl), -math.sin(sl)                # mouth -> foot: back and down
    for x in range(m[0] - 4, m[0] + 5):
        for y in range(m[1] - 6, m[1] + L + 6):
            for z in range(m[2] - L // 2 - 8, m[2] + 8):
                dy, dz = y - m[1], z - m[2]; t = dy * ay + dz * az
                if not (0 <= t <= L): continue
                n = -dy * az + dz * ay                 # up the case's side, across the axis
                hz = 5.0 - 2.4 * t / L; hx = 3.2 - 1.0 * t / L    # wide at the mouth, narrow at the foot
                ex, ez = (x - m[0]) / hx, n / hz
                if ex * ex + ez * ez > 1.0: continue
                if t < 1.5 and ex * ex + ez * ez < 0.5: c = 'wood_d'       # the dark mouth the arrows stand in
                elif t < 2.5: c = 'leather_d'                              # the laced rim
                elif t > L - 3: c = 'leather_d'                            # the capped foot
                elif ez > 0.75 and round(t) % 4 == 0: c = 'brass'          # studs along the top
                elif t < 3.5 and round(n) % 2 == 0: c = 'brass'            # studs round the mouth
                elif 5 <= t <= 15 and ex < -0.7 and (round(t) + round(n)) % 3 == 0: c = 'leather_l'   # the tooled panel
                elif ez < -0.8 and round(t) % 3 == 0: c = 'cord'           # the lacing along the bottom seam
                else: c = 'leather'
                P[part][(x, y, z)] = c
    for tt in (3, 13):                                  # the two straps, short and tight to the belt
        y = round(m[1] + tt * ay); ztop = round(m[2] + tt * az + 5.0 - 2.4 * tt / L)
        for z in range(ztop - 1, 2 * hip + 4):
            for yy in (y, y + 1): P[part][(-1, yy, z)] = 'leather_d'
        P[part][(-2, y, 2 * hip + 1)] = 'brass'         # the strap's buckle
    dy_, dz_ = math.sin(math.radians(8)), math.cos(math.radians(8))       # the arrows: up, leaning a little back
    for i, (dx, dn) in enumerate(((0, 0), (-1, 2), (1, -1), (0, -2), (-1, 1))):
        base = (m[0] + dx, round(m[1] + 3 * ay - dn * az), round(m[2] + 3 * az + dn * ay)); ln = 18 + (i % 3) * 3
        top_ = (base[0], round(base[1] + dy_ * ln), round(base[2] + dz_ * ln))
        _rod(P, part, base, top_, 'ash')
        fl = ('red', 'wool', 'canvas')[i % 3]
        for k in range(1, 6):
            q = (top_[0], round(top_[1] - dy_ * k), round(top_[2] - dz_ * k))
            for o in ((1, 0, 0), (-1, 0, 0), (0, 0, 1)): P[part].setdefault((q[0] + o[0], q[1] + o[1], q[2] + o[2]), fl)
        P[part][top_] = 'cord'                         # the nock
    return P
def bolt_case(F, Pb, Pc):
    """a bolt case for crossbows at the back of the belt, right side: a stiff box, iron-cornered, its lid hinged back,
    the bolts' short fletching standing in a row"""
    P = {}; TD, hip = F['TD'], F['hip']; part = 'ammo@torso#2'
    x0, x1, y0, y1, z0, z1 = 3, 14, 2 * TD + 1, 2 * TD + 8, 2 * hip - 12, 2 * hip + 6
    box(P, part, x0, x1, y0, y1, z0, z1, lambda x, y, z: 'iron' if (x in (x0, x1) and z in (z0, z0 + 1, z1)) else ('leather_d' if x in (x0, x1) or z == z0 else 'leather'))
    for x in range(x0 + 1, x1):                        # hollow at the top, so the bolts sit in it
        for y in range(y0 + 1, y1):
            for z in (z1,): P[part].pop((x, y, z), None)
    box(P, part, x0, x1, y1 + 1, y1 + 1, z1 - 2, z1 + 5, 'leather_d')     # the lid, hinged back and hanging open
    for i, x in enumerate(range(x0 + 2, x1 - 1, 3)):
        for y in (y0 + 2, y0 + 5):
            for z in range(z1 - 4, z1 + 5): P[part][(x, y, z)] = 'ash'
            for z in range(z1 + 1, z1 + 5): P[part][(x + 1, y, z)] = 'wood' if (i + y) % 2 else 'leather_l'   # vanes
    P[part][(x0 + 6, y1 + 2, z1 + 1)] = 'brass'                           # the lid's catch
    return P
def bullet_pouch(F, Pb, Pc):
    """bullet pouches for guns at the back of the belt: a stiff cartridge box with a flap and a brass badge, a round
    shot bag on a drawstring beside it, and a small brass powder flask"""
    P = {}; TD, hip, cx = F['TD'], F['hip'], F['cx']; part = 'ammo@torso#2'
    X0 = 2 * cx - 7; y0, y1 = 2 * TD + 1, 2 * TD + 6; z0, z1 = 2 * hip - 6, 2 * hip + 5
    box(P, part, X0, X0 + 13, y0, y1, z0, z1, lambda x, y, z: 'leather_d' if z in (z0, z1) else 'leather')
    box(P, part, X0 - 1, X0 + 14, y1 + 1, y1 + 1, z0 + 3, z1 + 1, 'leather_d')     # the flap
    for x in range(X0 + 4, X0 + 10):
        for z in range(z0 + 5, z0 + 9):
            if (x - X0 - 6.5) ** 2 / 9 + (z - z0 - 6.5) ** 2 / 4 <= 1: P[part][(x, y1 + 2, z)] = 'brass_l' if z == z0 + 7 else 'brass'
    sx, sz = 6, 2 * hip - 4                               # the shot bag, on the right
    for x in range(sx - 4, sx + 5):
        for y in range(y0, y0 + 8):
            for z in range(sz - 5, sz + 6):
                r = ((x - sx) / 4.2) ** 2 + ((y - y0 - 4) / 3.6) ** 2 + ((z - sz) / 5.2) ** 2
                if r <= 1: P[part][(x, y, z)] = 'canvas' if z < sz + 3 else 'leather_d'
    for z in range(sz + 5, 2 * hip + 4): P[part][(sx, y0 + 4, z)] = 'cord'
    fx = X0 + 18                                          # the powder flask, on the left
    for z in range(2 * hip - 9, 2 * hip + 2):
        w = 2 if z < 2 * hip - 1 else 1
        for x in range(fx - w, fx + w + 1):
            for y in range(y0 + 1, y0 + 2 * w + 2): P[part][(x, y, z)] = 'brass_d' if z == 2 * hip - 9 else 'brass'
    P[part][(fx, y0 + 2, 2 * hip + 2)] = 'iron'
    return P

# ---------------------------------------------------------------- the Farhallow tools (the prologue's weapons)
# Chunky and about 1.3x real size (weapons.md), at the head's finer voxels (1.25 cm). Each is drawn in its own frame -
# u across, w forward (negative) and back, h up the haft from the grip - then placed in the right fist (head up) or
# carried where it belongs: hatchets, hammers, blades and cleavers at the back of the left hip, long tools across the back.
def tool_shape(kind, floor):
    """the tool's voxels in its own frame; floor: how far below the grip the haft may reach (the ground)"""
    V = {}
    def b(u0, u1, w0, w1, h0, h1, c):
        for u in range(u0, u1 + 1):
            for w in range(w0, w1 + 1):
                for h in range(h0, h1 + 1): V[(u, w, h)] = c(u, w, h) if callable(c) else c
    def haft(h0, h1, wrap=(-6, 6)):
        b(-1, 1, -1, 1, max(h0, -floor), h1, lambda u, w, h: ('cord' if (h % 2) else 'leather_d') if wrap[0] <= h <= wrap[1] else ('wood_d' if (u + w + h) % 7 == 0 else 'wood'))
    if kind == 'hatchet':
        haft(-12, 36)
        for h in range(26, 38):                 # a bearded head: wider toward the edge
            reach = 12 + max(0, 33 - h) // 2 if h < 33 else 12
            b(-1, 1, -reach + 3, 3, h, h, lambda u, w, hh: 'iron_d' if w >= 2 else 'iron')
            b(0, 0, -reach, -reach + 2, h, h, 'iron_l')          # the edge: one voxel thin
    if kind == 'spear':                         # the fisher's spear: a barbed head on a long haft
        haft(-70, 78, (-8, 8))
        b(-1, 1, -1, 1, 74, 78, 'cord')
        for h in range(79, 100):
            r = max(0, 2 - (h - 79) // 8)
            b(-r, r, -r, r, h, h, 'iron_l' if h > 94 else 'iron')
        for side in (-1, 1):                    # two barbs
            for k in range(5): V[(side * (2 + k // 2), 0, 84 - k)] = 'iron'
    if kind == 'hammer':                        # the smith's hammer
        haft(-10, 32)
        b(-4, 4, -10, 8, 32, 42, lambda u, w, h: 'iron_l' if w in (-10, 8) else ('iron_d' if h in (32, 42) else 'iron'))
    if kind == 'blade':                         # the old blade from above the smithy door: worn, a little rust
        b(-1, 1, -1, 1, -8, 8, lambda u, w, h: 'leather_d' if h % 3 else 'cord')
        b(-2, 2, -2, 2, -11, -9, 'brass_d')
        b(-2, 2, -11, 11, 9, 11, lambda u, w, h: 'iron_d' if abs(w) < 10 else 'brass_d')
        for h in range(12, 80):      # the flat runs front to back, so the edge faces whoever the wielder faces
            hw = 4 if h < 72 else max(0, 4 - (h - 72) // 2)
            b(-1, 1, -hw, hw, h, h, lambda u, w, hh: 'copper_d' if (w * 5 + hh * 3) % 23 == 0 else ('iron_d' if w == 0 else ('iron_l' if abs(w) == hw else 'iron')))
    if kind == 'boathook':
        haft(-70, 70, (-8, 8))
        b(-1, 1, -1, 1, 70, 84, lambda u, w, h: 'iron_l' if h > 80 else 'iron')
        for k in range(9):                      # the hook, curling back and down
            w = 2 + min(k, 5); h = 74 - max(0, k - 5) * 2
            b(-1, 1, w, w + 1, h, h + 1, 'iron')
    if kind == 'cleaver':
        b(-1, 1, -1, 1, -8, 8, lambda u, w, h: 'brass' if h in (-4, 2) else 'wood')
        b(-1, 1, -18, 3, 9, 26, lambda u, w, h: 'iron_l' if w <= -17 else ('rubber' if (w, h) in ((0, 23), (-1, 23), (0, 22), (-1, 22)) else 'iron'))
    if kind == 'pitchfork':
        haft(-70, 62, (-8, 8))
        b(-9, 9, -1, 1, 62, 64, 'iron_d')
        for u in (-8, 0, 8):
            b(u - 1, u + 1, -1, 1, 65, 84, lambda uu, w, h: 'iron_l' if h > 81 else 'iron')
    return V
def tool_item(kind, carry):
    def fn(F, Pb, Pc):
        P = {}; x0, x1, ay0, au0, al0, h0 = F['arms']['r']; AW = F['AW']
        gx, gy, gz = x0 + x1 + 1, 2 * ay0 + AW, h0 + al0        # the fist's centre, in fine voxels
        if carry == 'back':     # polearm stance: the forearm forward, the haft drawn through the fist front to back as fingers
            # wrap a haft; equipment.gd turns the wrist to aim it
            V = tool_shape(kind, 52)         # gripped a third of the way up from the butt, as a spear is carried
            P['weapon@hand_r#2'] = {(gx + u, gy - h, gz + w): c for (u, w, h), c in V.items()}   # through the fist, front to back; the wrist aims it (equipment.gd)
        else:                   # one-handers point forward from the fist, the edge or face down (raised by the stance)
            V = tool_shape(kind, gz - 2)
            P['weapon@hand_r#2'] = {(gx + u, gy - h, gz + w): c for (u, w, h), c in V.items()}
        return P
    def fn_carried(F, Pb, Pc):
        P = {}; top, hip, TW, TD, cx = F['top'], F['hip'], F['TW'], F['TD'], F['cx']
        V = tool_shape(kind, 999)
        where = carry
        if kind == 'blade' and 2 * (hip + 4) - 80 < 6: where = 'back'   # too long for this hip: across the back
        if where == 'hip':                      # hanging at the back of the left hip
            if kind == 'blade':                 # sheathed, hilt up
                V = {k: c for k, c in V.items() if k[2] < 9}
                for h in range(9, 80):
                    for w in range(-5, 6):
                        for u in (-2, -1, 0, 1, 2):
                            if abs(w) == 5 or abs(u) == 2: V[(u, w, h)] = 'leather_d' if h > 76 or h < 12 else 'leather'
                part = {(2 * TW - 4 + u, 2 * TD + 4 + w, 2 * (hip + 4) - h): c for (u, w, h), c in V.items()}
            else:                               # through a belt loop, head up
                part = {(2 * TW - 4 + u, 2 * TD + 4 + w, 2 * hip - 22 + h): c for (u, w, h), c in V.items()}
            P['weapon@torso#2'] = part
        else:                                   # across the back, tilted
            P['weapon@torso#2~z35'] = {(2 * cx + u, 2 * TD + 8 + w, 2 * (hip + 10) + h): c for (u, w, h), c in V.items()}
        return P
    return fn, fn_carried
TOOLS = {'hatchet': 'hip', 'spear': 'back', 'hammer': 'hip', 'blade': 'hip', 'boathook': 'back', 'cleaver': 'hip', 'pitchfork': 'back'}

# ---------------------------------------------------------------- the Wayfolk common iron set (weapons.md, set 2)
# The starter weapons bought and looted around Hollin's Cross and Aldrath: every type, in plain forged iron, ash wood,
# leather grips, round pommels and nail heads. Common: the normal attack only. The same frame as the tools: u across,
# w forward (negative) and back, h along the weapon from the grip. Chunky, about 1.3x real size.
IRON = {   # kind: (where it is carried, the hands it takes, its stance when drawn)
    'sword': ('hip', 1, 'one_hand'), 'axe': ('hip', 1, 'one_hand'), 'mace': ('hip', 1, 'one_hand'),
    'hammer': ('hip', 1, 'one_hand'), 'dagger': ('hip', 1, 'one_hand'),
    'greatsword': ('back', 2, 'one_hand'), 'greataxe': ('back', 2, 'one_hand'), 'warhammer': ('back', 2, 'one_hand'),
    'spear': ('back', 2, 'polearm'),
    'bow': ('back', 2, 'bow'),       # one bow; its damage to speed ratio is a stat, not a model
    'heavy_crossbow': ('back', 2, 'one_hand'),
    'shield': ('shield', 0, 'shield'), 'tower_shield': ('tower', 0, 'shield'),
}
# ---------------------------------------------------------------- tiers (one version per tier, by rarity: weapons.md)
# T1 common is the Wayfolk iron set above. T2 uncommon: contrast trim, brass fittings. T3 rare: tooled leather, rivets,
# small brass fittings. T4 epic: working parts (gauges, pipes, a glowing vial). T5 legendary: glows (and later moves).
TIERS = {2: 'uncommon', 3: 'rare', 4: 'epic', 5: 'legendary'}
def sword_tier(V, b, t):
    """the sword at tiers 2-5, in the same frame as the iron sword: u thickness, w across the flat, h along the blade
    from the middle of the grip (the fist)"""
    g = 8
    def blade(h0, h1, hw, body, edge, fuller=None, fw=0, tip=None, profile=None):
        tip = tip or 3 * hw
        for h in range(h0, h1 + 1):
            w_ = profile(h) if profile else hw
            if h >= h1 - tip: w_ = min(w_, round(hw * (h1 - h) / tip))
            for w in range(-w_, w_ + 1):
                thick = abs(w) < max(1, w_ - 1) and h < h1 - 2
                col = edge if abs(w) == w_ else body
                if fuller and abs(w) <= fw and h0 + 3 <= h < h1 - tip - 2: col = fuller(h, w) if callable(fuller) else fuller
                b(-1 if thick else 0, 1 if thick else 0, w, w, h, h, col)
    def ball(h, r, c):
        for du in range(-r, r + 1):
            for dw in range(-r, r + 1):
                for dh in range(-r, r + 1):
                    if du * du + dw * dw + dh * dh <= r * r + 1: V[(du, dw, h + dh)] = c(du, dw, dh) if callable(c) else c
    if t == 2:      # uncommon: bright steel, a brass guard with down-swept tips, brass wire round the grip, brass pommel
        b(-1, 1, -1, 1, -g, g, lambda u, w, h: 'brass' if h % 4 == 0 else 'leather_d')
        ball(-g - 3, 2, lambda du, dw, dh: 'brass_l' if dh == 1 else 'brass')
        b(-2, 2, -10, 10, g + 1, g + 3, lambda u, w, h: 'brass_d' if abs(w) < 3 else 'brass')
        for k in range(3): b(-1, 1, 10 + k, 10 + k, g + 1 - k, g + 2 - k, 'brass_l'); b(-1, 1, -10 - k, -10 - k, g + 1 - k, g + 2 - k, 'brass_l')
        b(-1, 1, -4, 4, g + 4, g + 5, 'brass')                          # a brass collar at the blade's root
        blade(g + 6, 86, 4, 'steel', 'steel_l', 'steel_d', 0)
    if t == 3:      # rare: a broader blade with a wide fuller, a riveted guard with langets, a tooled grip, a wheel pommel
        b(-2, 2, -2, 2, -g, g, lambda u, w, h: 'leather_l' if (h + w) % 3 == 0 else 'leather')
        b(-2, 2, -2, 2, -g, -g, 'leather_d'); b(-2, 2, -2, 2, g, g, 'leather_d')
        for dw in range(-5, 6):                                             # the wheel pommel, flat to the blade's face
            for dh in range(-5, 6):
                r2 = dw * dw + dh * dh
                if r2 <= 26: b(-2, 2, dw, dw, -g - 6 + dh, -g - 6 + dh, 'iron_d' if r2 > 16 else 'steel')
        V[(2, 0, -g - 6)] = V[(-2, 0, -g - 6)] = 'brass_l'; V[(-3, 0, -g - 6)] = V[(3, 0, -g - 6)] = 'brass'   # its rivet
        b(-2, 2, -12, 12, g + 1, g + 4, lambda u, w, h: 'brass' if (abs(w) % 4 == 2 and abs(u) == 2 and h == g + 2) else ('iron_d' if abs(w) > 10 else 'steel_d'))
        b(-2, 2, -3, 3, g + 5, g + 9, lambda u, w, h: 'brass' if (abs(u) == 2 and w == 0 and h == g + 7) else 'steel_d')   # langets
        blade(g + 5, 90, 5, 'steel', 'steel_l', 'iron_d', 1, tip=13)
    if t == 4:      # epic: a blackened blade with bright edges; a glowing vial set in the guard feeds a copper pipe up the
        # fuller; a little gauge on the guard; a valve on the pommel cap
        b(-1, 1, -1, 1, -g, g, lambda u, w, h: 'rubber' if h % 2 else 'black')
        b(-2, 2, -2, 2, -g - 4, -g - 1, lambda u, w, h: 'brass_d' if h == -g - 1 else 'brass')
        b(0, 0, -1, 1, -g - 6, -g - 5, 'copper'); b(-1, 1, 0, 0, -g - 6, -g - 6, 'copper')     # the valve wheel
        b(-3, 3, -11, 11, g + 1, g + 4, lambda u, w, h: 'black_d' if abs(w) > 8 else 'black')
        b(-3, 3, -2, 2, g + 1, g + 6, lambda u, w, h: 'glass_l' if abs(u) == 3 or abs(w) == 2 else 'potion')   # the vial
        b(-3, 3, -2, 2, g + 7, g + 7, 'brass')
        for dw in range(-3, 4):                                             # the gauge, on the guard's arm
            for dh in range(-3, 4):
                if dw * dw + dh * dh <= 10: V[(-4, 8 + dw, g + 3 + dh)] = 'brass' if dw * dw + dh * dh > 5 else 'glass_l'
        V[(-5, 8, g + 3)] = V[(-5, 9, g + 4)] = 'red'                       # its needle
        blade(g + 8, 88, 4, 'black', 'steel_l', lambda h, w: 'copper' if h % 9 else 'copper_d', 1, tip=12)
        for h in range(g + 10, 66, 8): V[(0, 0, h)] = 'potion'             # the vial's light seen through the pipe's ports
    if t == 5:      # legendary: blued steel with glowing runes down the fuller, gilt wings for a guard round an arcane
        # crystal, a crystal pommel; the blade swells a little before the point
        b(-1, 1, -1, 1, -g, g, lambda u, w, h: 'gilt' if h % 3 == 0 else 'blued_d')
        for dh in range(-4, 5):                                             # the pommel crystal, a long diamond
            r = 3 - abs(dh) * 3 // 4
            b(-r, r, -r, r, -g - 5 + dh, -g - 5 + dh, 'arc' if abs(dh) < 3 else 'arc_d')
        for k in range(14):                                                 # gilt wings sweeping up and out
            lift = (k * k) // 28
            b(-2, 2, k, k, g + 1 + lift, g + 3 + lift, 'gilt' if k < 12 else 'brass_l'); b(-2, 2, -k, -k, g + 1 + lift, g + 3 + lift, 'gilt' if k < 12 else 'brass_l')
        for dh in range(-3, 4):                                             # the crystal in the guard
            r = 2 - abs(dh) * 2 // 3
            b(-3, 3, -r, r, g + 5 + dh, g + 5 + dh, 'arc')
        rune = {0: (0,), 1: (-1, 1), 2: (0,), 3: (-1, 0, 1), 4: ()}
        blade(g + 9, 96, 5, 'blued', 'blued_l', lambda h, w: 'arc' if w in rune[h % 5] else 'arc_d', 1, tip=14,
              profile=lambda h: 5 if h < 66 else (6 if h < 80 else 5))
    return V

def iron_shape(kind, floor, tier=1):
    V = {}
    def b(u0, u1, w0, w1, h0, h1, c):
        for u in range(u0, u1 + 1):
            for w in range(w0, w1 + 1):
                for h in range(h0, h1 + 1): V[(u, w, h)] = c(u, w, h) if callable(c) else c
    def haft(h0, h1, grip=(-7, 7)):    # ash, a leather grip, iron nail heads where the head is fixed
        b(-1, 1, -1, 1, max(h0, -floor), h1, lambda u, w, h: 'leather' if grip[0] <= h <= grip[1] else ('ash_d' if (h % 11 == 0 or (u == 1 and h % 7 == 3)) else 'ash'))
    def pommel(h):                      # a round iron pommel
        for dh in range(-3, 1):
            r = 2 if dh in (-3, 0) else 3
            b(-r + 1, r - 1, -r, r, h + dh, h + dh, 'iron_d')
    def blade(h0, h1, hw, tip=None, fuller=True):     # a straight two-edged blade, its flat front to back: thick down the
        tip = tip or 3 * hw                             # middle, thinning to one-voxel edges, drawn out to a long point
        for h in range(h0, h1 + 1):
            w_ = hw if h < h1 - tip else round(hw * (h1 - h) / tip)
            for w in range(-w_, w_ + 1):
                thick = abs(w) < max(1, w_ - 1) and h < h1 - 2
                col = 'iron_d' if (fuller and w == 0 and h < h1 - tip - 2) else ('iron_l' if abs(w) == w_ else 'iron')
                b(-1 if thick else 0, 1 if thick else 0, w, w, h, h, col)
    if kind == 'sword' and tier > 1:
        sword_tier(V, b, tier)
    elif kind in ('sword', 'dagger', 'greatsword'):
        g, bl, hw, gw = {'sword': (8, 80, 4, 10), 'dagger': (6, 34, 3, 6), 'greatsword': (16, 124, 5, 15)}[kind]
        b(-1, 1, -1, 1, -g, g, lambda u, w, h: 'leather_d' if h % 3 == 0 else 'leather')
        pommel(-g - 1)
        b(-2, 2, -gw, gw, g + 1, g + 3, lambda u, w, h: 'iron_d' if abs(w) < gw else 'iron_l')     # the cross guard
        blade(g + 4, bl, hw)
    if kind == 'axe':
        haft(-12, 42)
        for h in range(28, 46):         # a bearded bit: thick at the eye, thinning to a flared one-voxel edge
            reach = 11 + abs(h - 39) // 2 + (2 if h < 32 else 0)
            b(-1, 1, -5, 3, h, h, lambda u, w, hh: 'iron_d' if w >= 2 else 'iron')
            b(0, 0, -reach + 2, -6, h, h, 'iron'); b(0, 0, -reach, -reach + 1, h, h, 'iron_l')
        V[(2, 0, 37)] = V[(-2, 0, 37)] = 'iron_l'     # nail heads through the eye
    if kind == 'greataxe':
        haft(-60, 74, (-10, 10))
        for h in range(52, 78):         # a double bit, crescent edges flaring at the horns, one voxel thin
            reach = 14 + abs(h - 65) // 2
            b(-1, 1, -5, 5, h, h, lambda u, w, hh: 'iron_d' if abs(w) <= 2 else 'iron')
            b(0, 0, -reach + 2, -6, h, h, 'iron'); b(0, 0, 6, reach - 2, h, h, 'iron')
            b(0, 0, -reach, -reach + 1, h, h, 'iron_l'); b(0, 0, reach - 1, reach, h, h, 'iron_l')
        b(-2, 2, -2, 2, 75, 77, 'iron_d')
    if kind == 'mace':
        haft(-12, 34)
        b(-2, 2, -2, 2, 34, 48, 'iron_d')
        for k in range(4):              # four flanges
            du, dw = ((1, 0), (-1, 0), (0, 1), (0, -1))[k]
            for r in range(3, 6):
                b(du * r, du * r, dw * r, dw * r, 36 + (r == 5), 46 - (r == 5), 'iron' if r < 5 else 'iron_l')
        b(-1, 1, -1, 1, 49, 50, 'iron_l')
    if kind in ('hammer', 'warhammer'):
        top, hl, hd = (38, 8, 4) if kind == 'hammer' else (70, 11, 6)
        haft(-12 if kind == 'hammer' else -60, top, (-7, 7) if kind == 'hammer' else (-10, 10))
        b(-hd, hd, -hl, 2, top - hd, top + hd, lambda u, w, h: 'iron_l' if w == -hl else ('iron_d' if h in (top - hd, top + hd) else 'iron'))   # the square face
        for k in range(hl):              # the back spike, tapering
            r = max(0, 2 - k // 3)
            b(-r, r, 3 + k, 3 + k, top - r, top + r, 'iron')
    if kind == 'spear':
        haft(-70, 80, (-8, 8))
    if kind == 'spear':                 # a leaf head and an iron socket
        b(-1, 1, -1, 1, 76, 82, 'iron_d')
        for h in range(83, 104):
            hw = min(3, (h - 82) // 2) if h < 94 else max(0, 3 - (h - 94) // 3)
            b(0, 0, -hw, hw, h, h, lambda u, w, hh: 'iron_l' if abs(w) == hw else 'iron'); b(-1, 1, 0, 0, h, h, 'iron_d')
    if kind == 'bow':     # limbs along h, curving back toward the archer (+w), the string behind
        L = 54
        for h in range(-L, L + 1):
            bend = round(10 * (h / L) ** 2)
            th = 1 if abs(h) > L * 0.6 else 2
            b(-1, 1, bend - th + 1, bend, h, h, lambda u, w, hh: 'leather' if abs(hh) <= 5 else ('ash_d' if abs(hh) > L - 3 else 'ash'))
        for h in range(-L + 1, L): V[(0, 11, h)] = 'cord'
    if kind == 'heavy_crossbow':     # the stock along h, pointing forward from the grip; the prod across
        n, pw, back = 60, 26, 14
        b(-1, 1, -2, 2, -back, n, lambda u, w, h: 'ash_d' if h < 0 or h % 7 == 0 else 'ash')
        b(-1, 1, 3, 6, -4, 2, 'ash_d')                       # the grip under the stock
        for u in range(-pw, pw + 1):                         # the prod, bowed forward
            hh = n - 4 + round(4 * (1 - (u / pw) ** 2))
            b(u, u, -1, 1, hh, hh + 1, 'iron' if abs(u) > 2 else 'iron_d')
        for u in range(-pw + 1, pw): V[(u, 0, n - 12 + round(-4 * (1 - abs(u) / pw)))] = 'cord'
        if kind == 'heavy_crossbow':                         # the crank at the back
            b(-3, 3, -3, 3, -back - 3, -back - 1, 'iron_d'); b(4, 6, -1, 1, -back - 2, -back - 2, 'iron')
    if kind == 'tower_shield':          # a tall shield of planks, curved round its bearer, rounded at the top; iron rim,
        HW, HB, HT = 20, -50, 42        # two iron bands and a small boss. Its face is forward (-w), the grip at h 0.
        for u in range(-HW, HW + 1):
            bend = round(4 * (u / HW) ** 2)                  # the sides curve back round the bearer
            for h in range(HB, HT + 1):
                cut = HT - h < 6 and (abs(u) - (HW - 6)) ** 2 + (h - (HT - 6)) ** 2 > 36 and abs(u) > HW - 6
                if cut: continue
                rim = abs(u) >= HW - 1 or h <= HB + 1 or HT - h <= 1 or (HT - h < 7 and abs(u) > HW - 7 and (abs(u) - (HW - 6)) ** 2 + (h - (HT - 6)) ** 2 > 25)
                band = h in (HB + 14, HB + 15, HT - 16, HT - 15)
                col = 'iron_d' if rim else ('iron' if band else ('ash_d' if u % 7 in (0, 1) else 'ash'))
                V[(u, bend, h)] = col; V[(u, bend + 1, h)] = 'ash_d'
        for u in range(-4, 5):
            for h in range(-4, 5):
                d2 = u * u + h * h
                if d2 <= 16: V[(u, -1, h)] = 'iron'
                if d2 <= 6: V[(u, -2, h)] = 'iron_l'
    if kind == 'shield':               # a round shield: planks, an iron rim, an iron boss, facing forward (-w)
        R = 26
        for u in range(-R, R + 1):
            for h in range(-R, R + 1):
                d2 = u * u + h * h
                if d2 > R * R: continue
                rim = d2 > (R - 2) ** 2
                if kind == 'shield': col = 'iron_d' if rim else ('ash_d' if u % 8 in (0, 1) else 'ash')
                else: col = 'iron_d' if rim else 'iron'
                V[(u, 0, h)] = col; V[(u, 1, h)] = 'ash_d' if kind == 'shield' else 'iron_d'
        Bs = 6 if kind == 'shield' else 4
        for u in range(-Bs, Bs + 1):
            for h in range(-Bs, Bs + 1):
                d2 = u * u + h * h
                if d2 <= Bs * Bs: V[(u, -1, h)] = 'iron'; V[(u, -2, h)] = 'iron_l' if d2 <= (Bs - 3) ** 2 else 'iron'
                if d2 <= (Bs - 2) ** 2: V[(u, -3, h)] = 'iron_l'
    return V
def iron_item(kind, tier=1):
    carry, hands, stance = IRON[kind]
    def fn(F, Pb, Pc):
        P = {}
        if carry in ('shield', 'tower') or stance == 'bow':     # the off hand: held out in front by the stance
            x0, x1, ay0, au0, al0, h0 = F['arms']['l']; AW = F['AW']
            gx, gy, gz = x0 + x1 + 1, 2 * ay0 + AW, h0 + al0
            V = iron_shape(kind, 999, tier)
            if stance == 'bow':       # idle: the bow hangs upright in the lowered hand at the side, the string between
                o = 1 if gx < F['cx'] else -1          # the arm and the body
                P['weapon_off@hand_l#2'] = {(gx + o * w, gy + u, gz + h): c for (u, w, h), c in V.items()}
            else:                     # the shield on the forearm's front, facing forward once the forearm is raised
                P['weapon_off@hand_l#2'] = {(gx + u, gy - h, gz - AW - 2 + w): c for (u, w, h), c in V.items()}
            return P
        x0, x1, ay0, au0, al0, h0 = F['arms']['r']; AW = F['AW']
        gx, gy, gz = x0 + x1 + 1, 2 * ay0 + AW, h0 + al0
        V = iron_shape(kind, 52 if stance == 'polearm' else gz - 2, tier)
        P['weapon@hand_r#2'] = {(gx + u, gy - h, gz + w): c for (u, w, h), c in V.items()}
        return P
    def fn_carried(F, Pb, Pc):
        P = {}; top, hip, TW, TD, cx = F['top'], F['hip'], F['TW'], F['TD'], F['cx']
        V = iron_shape(kind, 999, tier)
        hl = max(h for (_, _, h) in V); lo = min(h for (_, _, h) in V)
        where = carry
        if where == 'hip' and kind in ('sword', 'dagger') and 2 * (hip + 4) - hl < 6: where = 'back'    # too long for this hip
        if where == 'hip' and kind in ('sword', 'dagger'):     # sheathed at the left hip, hilt up
            g = {'sword': 8, 'dagger': 6}[kind]
            hc = g + 3 + (4 if tier >= 4 else 2 if tier == 3 else 0)       # the hilt and guard stand out of the sheath
            sw = max(5, max(abs(k[1]) for k in V if k[2] > hc + 4) + 1)   # the sheath fits the blade's width
            W_ = {k: c for k, c in V.items() if k[2] <= hc}
            for h in range(hc + 1, hl + 1):
                for w in range(-sw, sw + 1):
                    for u in (-2, -1, 0, 1, 2):
                        if abs(w) == sw or abs(u) == 2: W_[(u, w, h)] = 'leather_d' if h > hl - 3 or h < g + 7 else 'leather'
            P['weapon_hip@torso#2'] = {(2 * TW - 4 + u, 2 * TD + 4 + w, 2 * (hip + 4) - h): c for (u, w, h), c in W_.items()}
        elif where == 'hip':          # through a belt loop at the left hip, head up
            P['weapon_hip@torso#2'] = {(2 * TW - 4 + u, 2 * TD + 4 + w, 2 * hip - 22 + h): c for (u, w, h), c in V.items()}
        elif where == 'shield':       # flat on the back, its face and boss outward
            P['weapon_offback@torso#2'] = {(2 * cx + u, 2 * TD + 4 - w, 2 * (top - 12) + h): c for (u, w, h), c in V.items()}
        elif where == 'tower':        # slung on the back, its foot a hand above the ground
            z0 = max(2 * top - 44, 6 - lo)
            P['weapon_offback@torso#2'] = {(2 * cx + u, 2 * TD + 4 - w, z0 + h): c for (u, w, h), c in V.items()}
        else:                         # across the back, tilted; long ones lifted so they clear the ground
            z0 = max(2 * (hip + 10), 4 - lo)
            P['weapon_back@torso#2~z35'] = {(2 * cx + u, 2 * TD + 10 + w, z0 + h): c for (u, w, h), c in V.items()}
        return P
    return fn, fn_carried

# ---------------------------------------------------------------- the catalogue
# order: the fixed layering from the inside out (design doc): wardrobe, legs and feet, chest, coat, arms, belt,
# shoulders, back, head; a later layer wins where two would take the same part.
ITEMS = {
    'warden_hood':        (hood, 'light', ['head'], 8, ['hair*']),     # every hair piece ('hair*' matches hair, hair_bun, ...)
    'warden_jerkin':      (jerkin, 'light', ['chest'], 2, []),
    'warden_bracers':     (bracers, 'light', ['wrists'], 4, []),
    'warden_boots':       (tall_boots, 'light', ['feet'], 1, []),
    'warden_belt':        (warden_belt, 'light', ['waist'], 5, []),
    'tinker_goggles':     (goggles, 'medium', ['eyes'], 9, []),
    'tinker_brigandine':  (brigandine, 'medium', ['chest'], 2, []),
    'tinker_pauldron':    (mech_pauldron, 'medium', ['shoulder_l'], 6, []),
    'canister_gauntlet':  (canister_gauntlet, 'medium', ['hand_r', 'wrist_r'], 4, []),
    'tinker_belt':        (tool_belt, 'medium', ['waist'], 5, []),
    'steam_respirator':   (respirator, 'heavy', ['mouth'], 9, []),
    'steam_cuirass':      (cuirass, 'heavy', ['chest'], 2, []),
    'steam_pauldrons':    (brass_pauldrons, 'heavy', ['shoulder_l', 'shoulder_r'], 6, []),
    'steam_boiler':       (boiler, 'heavy', ['back'], 7, []),
    'steam_greaves':      (greaves, 'heavy', ['legs'], 1, []),
    'steam_gloves':       (work_gloves, 'heavy', ['hands'], 4, []),
    'iron_helm':          (full_helm, 'plate', ['head', 'eyes', 'mouth'], 8, ['hair*', 'beard*']),
    'iron_breastplate':   (breastplate, 'plate', ['chest', 'coat'], 2, []),
    'iron_arms':          (plate_arms, 'plate', ['shoulder_l', 'shoulder_r', 'arms'], 4, []),
    'iron_gauntlets':     (gauntlets, 'plate', ['hands'], 4, []),
    'iron_legs':          (plate_legs, 'plate', ['legs'], 1, []),
    'iron_sabatons':      (sabatons, 'plate', ['feet'], 1, []),
    'arcane_rig':         (rig, 'rig', ['rig'], 10, []),
    'arm_claw':           (arm_claw, 'medium', ['back'], 7, []),
    'arm_saw':            (arm_saw, 'heavy', ['back'], 7, []),
    'arm_bulwark':        (arm_bulwark, 'heavy', ['back'], 7, []),
    'arm_cannons':        (arm_cannons, 'heavy', ['back'], 7, []),
    'colossus_gauntlets': (colossus_gauntlets, 'heavy', ['wrists', 'hands', 'main_hand', 'off_hand'], 4, []),
    'colossus_arms':      (colossus_arms, 'heavy', ['shoulder_l', 'shoulder_r', 'arms', 'wrists', 'hands', 'main_hand', 'off_hand'], 6, []),
}
ITEMS.update({
    'cloth_cap':      (cap, 'common', ['head'], 8, ['hair', 'hair_bun', 'hair_crown', 'hair_mane']),     # the hair on top; tails and locks hang out
    'spectacles':     (spectacles, 'common', ['eyes'], 9, []),
    'wool_scarf':     (scarf, 'common', ['mouth'], 9, ['beard*']),
    'shoulder_pads':  (shoulder_pads, 'common', ['shoulder_l', 'shoulder_r'], 6, []),
    'armbands':       (armbands, 'common', ['arms'], 4, []),
    'gambeson':       (gambeson, 'common', ['chest'], 2, []),
    'long_coat':      (long_coat, 'common', ['coat'], 3, []),
    'wrist_wraps':    (wrist_wraps, 'common', ['wrists'], 4, []),
    'leather_gloves': (leather_gloves, 'common', ['hands'], 4, []),
    'plain_belt':     (plain_belt, 'common', ['waist'], 5, []),
    'work_trousers':  (work_trousers, 'common', ['legs'], 1, []),
    'shoes':          (shoes, 'common', ['feet'], 1, []),
    'knapsack':       (knapsack, 'common', ['back'], 7, []),
    'quiver':         (quiver, 'common', ['ammo'], 6, []),
    'bolt_case':      (bolt_case, 'common', ['ammo'], 6, []),
    'bullet_pouch':   (bullet_pouch, 'common', ['ammo'], 6, []),
})
for _k, _c in TOOLS.items():
    _h, _cr = tool_item(_k, _c)
    ITEMS[_k] = (_h, 'common', ['main_hand'] + (['off_hand'] if _c == 'back' else []), 11, [], _cr)
for _k, (_c, _n, _st) in IRON.items():
    _h, _cr = iron_item(_k)
    _slots = {0: ['off_hand'], 1: ['main_hand'], 2: ['main_hand', 'off_hand']}[_n]
    ITEMS['iron_' + _k] = (_h, 'common', _slots, 11, [], _cr)
STANCE = {'iron_' + k: st for k, (_, _, st) in IRON.items()}
TIERED = ['sword']        # types built at tiers 2-5 so far (the item list)
for _k in TIERED:
    for _t, _r in TIERS.items():
        _h, _cr = iron_item(_k, _t)
        ITEMS['%s_t%d' % (_k, _t)] = (_h, _r, {0: ['off_hand'], 1: ['main_hand'], 2: ['main_hand', 'off_hand']}[IRON[_k][1]], 11, [], _cr)
        STANCE['%s_t%d' % (_k, _t)] = IRON[_k][2]
SETS = {
    'light':  ("Warden's leathers", ['warden_hood', 'warden_jerkin', 'warden_bracers', 'warden_boots', 'warden_belt']),
    'medium': ("Tinkerer's brigandine", ['tinker_goggles', 'tinker_brigandine', 'tinker_pauldron', 'canister_gauntlet', 'tinker_belt']),
    'heavy':  ("Steamwright's brass", ['steam_respirator', 'steam_cuirass', 'steam_pauldrons', 'steam_boiler', 'steam_greaves', 'steam_gloves']),
    'plate':  ('Ironclad plate', ['iron_helm', 'iron_breastplate', 'iron_arms', 'iron_gauntlets', 'iron_legs', 'iron_sabatons']),
    'rig':    ('Arcane engine rig', ['tinker_goggles', 'arcane_rig']),
    'arm_utility': ('Tinkerer with a third arm (utility)', ['tinker_goggles', 'tinker_brigandine', 'canister_gauntlet', 'tinker_belt', 'arm_claw']),
    'arm_combat': ('Warden with a saw arm (combat)', ['warden_jerkin', 'warden_bracers', 'warden_boots', 'warden_belt', 'arm_saw']),
    'arm_defence': ('Ironclad with a bulwark arm (defence)', ['iron_breastplate', 'iron_arms', 'iron_gauntlets', 'iron_legs', 'iron_sabatons', 'arm_bulwark']),
    'arm_cannons': ('Steamwright with twin cannon arms (combat)', ['steam_respirator', 'steam_cuirass', 'steam_greaves', 'steam_gloves', 'arm_cannons']),
    'gauntlets': ('Colossus gauntlets over light leathers', ['warden_hood', 'warden_jerkin', 'warden_boots', 'warden_belt', 'colossus_gauntlets']),
    'basics': ('Basics: one common item in every slot', ['cloth_cap', 'spectacles', 'wool_scarf', 'shoulder_pads', 'armbands', 'gambeson', 'long_coat', 'wrist_wraps', 'leather_gloves', 'plain_belt', 'work_trousers', 'shoes', 'knapsack', 'hatchet']),
    'colossus': ('Colossus arms over light leathers', ['warden_jerkin', 'warden_boots', 'warden_belt', 'colossus_arms']),
}

if __name__ == '__main__':
    db = {'items': {}, 'sets': {k: {'name': n, 'items': v} for k, (n, v) in SETS.items()}}
    for name, (fn, tier, slots, order, hides, *carried) in ITEMS.items():
        db['items'][name] = {'tier': tier, 'slots': slots, 'order': order, 'hides': hides, 'file': 'res://assets/voxel/gear/%s/%%s_%%s.vox' % name}
        os.makedirs(os.path.join(ROOT, 'assets', 'voxel', 'gear', name), exist_ok=True)
        if carried:
            db['items'][name]['carried'] = 'res://assets/voxel/gear/%s_carried/%%s_%%s.vox' % name
            db['items'][name]['stance'] = STANCE.get(name) or ('polearm' if TOOLS.get(name) == 'back' else 'one_hand')
            os.makedirs(os.path.join(ROOT, 'assets', 'voxel', 'gear', name + '_carried'), exist_ok=True)
    tall = {}
    for people in mc.PEOPLES:
        for sex in ('m', 'f'):
            Pb, PAL = mc.build(people, sex, dressed=False); F = mc.build.frame
            Pc, _ = mc.build(people, sex, dressed=True)
            pal = dict(PAL); pal.update(MAT); mb.COL = pal; mb.NAMES = list(pal)
            for name, (fn, *_r) in ITEMS.items():
                import contextlib, io
                for suffix, f_ in (('', fn),) + ((('_carried', _r[-1]),) if len(_r) == 5 else ()):
                    parts = {k: v for k, v in f_(F, Pb, Pc).items() if v}
                    path = os.path.join(ROOT, 'assets', 'voxel', 'gear', name + suffix, '%s_%s.vox' % (people, sex))
                    with contextlib.redirect_stdout(io.StringIO()): mb.write(path, parts)
                if name == 'arcane_rig':
                    z = [vz / (2 if '#2' in k else 1) for k, v in {**Pb, **parts}.items() for (_, _, vz) in v]
                    x = [vx for k, v in parts.items() for (vx, _, _) in v]
                    tall[(people, sex)] = ((max(z) - min(z) + 1) * 0.025, (max(x) - min(x) + 1) * 0.025)
    json.dump(db, open(os.path.join(ROOT, 'data', 'equipment.json'), 'w'), indent=1)
    print('%d items x %d bodies' % (len(ITEMS), 2 * len(mc.PEOPLES)))
    for k, (h, w) in tall.items(): print('rig on %s %s: %.2f m tall, %.2f m wide' % (k[0], k[1], h, w))
