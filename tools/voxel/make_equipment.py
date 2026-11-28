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
import json, os, importlib.util
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
    'fur_d': (112, 96, 76), 'canvas': (120, 100, 72), 'red': (120, 42, 36), 'red_d': (86, 30, 26), 'cord': (170, 150, 110), 'bronze': (138, 88, 54), 'bronze_d': (90, 56, 34), 'bronze_l': (182, 128, 82), 'hose': (150, 44, 40), 'hose_d': (104, 30, 28),
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

# ---------------------------------------------------------------- the catalogue
# order: the fixed layering from the inside out (design doc): wardrobe, legs and feet, chest, coat, arms, belt,
# shoulders, back, head; a later layer wins where two would take the same part.
ITEMS = {
    'warden_hood':        (hood, 'light', ['head'], 8, ['hair', 'bun', 'crown', 'braids']),
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
    'iron_helm':          (full_helm, 'plate', ['head', 'eyes', 'mouth'], 8, ['hair', 'bun', 'crown', 'braids', 'beard', 'braid']),
    'iron_breastplate':   (breastplate, 'plate', ['chest', 'coat'], 2, []),
    'iron_arms':          (plate_arms, 'plate', ['shoulder_l', 'shoulder_r', 'arms'], 4, []),
    'iron_gauntlets':     (gauntlets, 'plate', ['hands'], 4, []),
    'iron_legs':          (plate_legs, 'plate', ['legs'], 1, []),
    'iron_sabatons':      (sabatons, 'plate', ['feet'], 1, []),
    'arcane_rig':         (rig, 'rig', ['rig'], 10, []),
    'colossus_arms':      (colossus_arms, 'heavy', ['shoulder_l', 'shoulder_r', 'arms', 'wrists', 'hands'], 6, []),
}
SETS = {
    'light':  ("Warden's leathers", ['warden_hood', 'warden_jerkin', 'warden_bracers', 'warden_boots', 'warden_belt']),
    'medium': ("Tinkerer's brigandine", ['tinker_goggles', 'tinker_brigandine', 'tinker_pauldron', 'canister_gauntlet', 'tinker_belt']),
    'heavy':  ("Steamwright's brass", ['steam_respirator', 'steam_cuirass', 'steam_pauldrons', 'steam_boiler', 'steam_greaves', 'steam_gloves']),
    'plate':  ('Ironclad plate', ['iron_helm', 'iron_breastplate', 'iron_arms', 'iron_gauntlets', 'iron_legs', 'iron_sabatons']),
    'rig':    ('Arcane engine rig', ['tinker_goggles', 'arcane_rig']),
    'colossus': ('Colossus arms over light leathers', ['warden_jerkin', 'warden_boots', 'warden_belt', 'colossus_arms']),
}

if __name__ == '__main__':
    db = {'items': {}, 'sets': {k: {'name': n, 'items': v} for k, (n, v) in SETS.items()}}
    for name, (fn, tier, slots, order, hides) in ITEMS.items():
        db['items'][name] = {'tier': tier, 'slots': slots, 'order': order, 'hides': hides, 'file': 'res://assets/voxel/gear/%s/%%s_%%s.vox' % name}
        os.makedirs(os.path.join(ROOT, 'assets', 'voxel', 'gear', name), exist_ok=True)
    tall = {}
    for people in mc.PEOPLES:
        for sex in ('m', 'f'):
            Pb, PAL = mc.build(people, sex, dressed=False); F = mc.build.frame
            Pc, _ = mc.build(people, sex, dressed=True)
            pal = dict(PAL); pal.update(MAT); mb.COL = pal; mb.NAMES = list(pal)
            for name, (fn, *_r) in ITEMS.items():
                parts = {k: v for k, v in fn(F, Pb, Pc).items() if v}
                path = os.path.join(ROOT, 'assets', 'voxel', 'gear', name, '%s_%s.vox' % (people, sex))
                import contextlib, io
                with contextlib.redirect_stdout(io.StringIO()): mb.write(path, parts)
                if name == 'arcane_rig':
                    z = [vz / (2 if '#2' in k else 1) for k, v in {**Pb, **parts}.items() for (_, _, vz) in v]
                    x = [vx for k, v in parts.items() for (vx, _, _) in v]
                    tall[(people, sex)] = ((max(z) - min(z) + 1) * 0.025, (max(x) - min(x) + 1) * 0.025)
    json.dump(db, open(os.path.join(ROOT, 'data', 'equipment.json'), 'w'), indent=1)
    print('%d items x %d bodies' % (len(ITEMS), 2 * len(mc.PEOPLES)))
    for k, (h, w) in tall.items(): print('rig on %s %s: %.2f m tall, %.2f m wide' % (k[0], k[1], h, w))
