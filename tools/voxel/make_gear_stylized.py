# Sample equipment for the stylized Hrimfolk (make_stylized.py), each piece its own .vox in the same frame as the body, so
# it loads as a layer over it (godot/scripts/voxel/vox.gd, Vox.character(..., layers)):
#   - gear named "<piece>@<part>" rides on that body part and moves with it (pauldrons on the upper arms, goggles on the
#     head, a toolbelt and a steam tank on the torso);
#   - gear that takes a body part's own name replaces it: the cyberarm replaces arm_upper_l, arm_lower_l and hand_l, and
#     its shoulder implant rides on the torso - one item over several body parts (and inventory slots).
#   python3 tools/voxel/make_gear_stylized.py   -> godot/assets/voxel/gear/hrim_*.vox
# 2.5 cm voxels, MagicaVoxel axes (x across, 0 = the character's right; y front to back; z up), the body's coordinates as
# make_stylized.py draws them before it drops everything above the legs by LIFT.
import math, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('mb', os.path.join(HERE, 'make_base.py')); mb = importlib.util.module_from_spec(spec)
src = open(spec.origin).read(); exec(compile(src[:src.rindex('\nOUT = ')], spec.origin, 'exec'), mb.__dict__)

LIFT = 4
HX0, HY0, HZ0, HW, HD, HH = 3, -2, 53, 14, 13, 15          # the head's box (make_stylized.py)
PAL = {
    'iron': (128, 132, 136), 'iron_d': (84, 88, 94), 'iron_l': (168, 172, 176), 'brass': (196, 150, 66), 'brass_d': (150, 108, 44),
    'brass_l': (232, 194, 110), 'copper': (176, 98, 60), 'copper_d': (128, 66, 40), 'rubber': (40, 36, 34), 'glass': (120, 196, 200),
    'glow': (255, 176, 74), 'leather': (98, 60, 36), 'leather_d': (70, 42, 24), 'leather_l': (124, 82, 52), 'wood': (140, 100, 62),
    'cloth': (120, 104, 80),
}

def out(name, parts):
    mb.COL = PAL; mb.NAMES = list(PAL)
    parts = {p: {(x, y, z - LIFT): c for (x, y, z), c in v.items()} for p, v in parts.items() if v}
    d = os.path.join(HERE, '..', '..', 'godot', 'assets', 'voxel', 'gear'); os.makedirs(d, exist_ok=True)
    mb.write(os.path.join(d, name + '.vox'), parts)

def new(): return {}
def put(P, part, x, y, z, c): P.setdefault(part, {})[(x, y, z)] = c
def box(P, part, x0, x1, y0, y1, z0, z1, c, bev=0):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                if bev and ((x - x0 < bev) + (x1 - x < bev)) and ((y - y0 < bev) + (y1 - y < bev)): continue
                put(P, part, x, y, z, c(x, y, z) if callable(c) else c)
def cyl(P, part, cx, cy, r, z0, z1, c):
    """an upright cylinder; cx, cy at voxel corners (10.0 centres it between voxels 9 and 10)"""
    for x in range(int(cx - r) - 1, int(cx + r) + 2):
        for y in range(int(cy - r) - 1, int(cy + r) + 2):
            if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                for z in range(z0, z1 + 1): put(P, part, x, y, z, c(x, y, z) if callable(c) else c)
def mirror(vox): return {(19 - x, y, z): c for (x, y, z), c in vox.items()}   # the character's left <-> right (x 20..25 <-> -1..-6)

# ---- pauldrons: three stepped iron lames over a leather pad, riveted, flaring out over the shoulder (left; the right mirrored)
def pauldron():
    P = new(); n = 'pauldron_l@arm_upper_l'
    box(P, n, 19, 26, 1, 8, 52, 53, 'leather_d', bev=1)                                       # the pad on the shoulder's top
    for k, (z0, x1, y0, y1) in enumerate(((51, 27, 0, 9), (48, 28, 0, 9), (45, 28, 1, 8))):   # the lames, each lower one wider
        x0 = 19 + k * 2
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for z in (z0, z0 + 1, z0 + 2):
                    edge_out = x == x1 or y in (y0, y1)
                    inside = x < x1 and y0 < y < y1 and z < z0 + 2   # hollow underneath: the arm is there
                    if inside and x >= 20: continue
                    c = 'iron_d' if z == z0 else ('iron_l' if z == z0 + 2 and edge_out else 'iron')
                    put(P, n, x, y, z, c)
        for y in (y0 + 1, y1 - 1): put(P, n, x1 + 1, y, z0 + 1, 'brass')                     # rivets on the edge
    box(P, n, 21, 24, -1, -1, 53, 54, 'leather')                                              # a strap to the chest
    box(P, n, 22, 23, -1, -1, 49, 52, 'leather'); put(P, n, 22, -2, 51, 'brass'); put(P, n, 23, -2, 51, 'brass')
    return P[n]
pl = pauldron()
out('hrim_pauldron_l', {'pauldron_l@arm_upper_l': pl})
out('hrim_pauldron_r', {'pauldron_r@arm_upper_r': mirror(pl)})

# ---- goggles, pushed up on the brow: brass rims, glass lenses, a leather strap round the head
P = new(); n = 'goggles@head'
zc = HZ0 + 12
for cx in (HX0 + 3, HX0 + 10):                       # the lenses' left columns (x across the head's front)
    for x in range(cx - 1, cx + 3):
        for z in range(zc - 1, zc + 3):
            rim = x in (cx - 1, cx + 2) or z in (zc - 1, zc + 2)
            corner = x in (cx - 1, cx + 2) and z in (zc - 1, zc + 2)
            if corner: continue
            put(P, n, x, HY0 - 1, z, 'brass' if rim else 'glass'); put(P, n, x, HY0 - 2, z, 'brass_d' if rim else 'glass')
    put(P, n, cx, HY0 - 3, zc + 1, 'brass_l')          # a glint on the lens's rim
box(P, n, HX0 + 6, HX0 + 7, HY0 - 1, HY0 - 1, zc, zc + 1, 'brass_d')   # the bridge
for z in (zc, zc + 1):                                 # the strap: round the sides and the back of the head
    for y in range(HY0 + 2, HY0 + HD + 1):                 # from behind the lenses' sides, so it hugs the head
        put(P, n, HX0 - 1, y, z, 'leather_d'); put(P, n, HX0 + HW, y, z, 'leather_d')
    for x in range(HX0 - 1, HX0 + HW + 1): put(P, n, x, HY0 + HD, z, 'leather_d')
out('hrim_goggles', P)

# ---- a toolbelt: a second, wider belt over the tunic with pouches, a wrench and a hammer, an oil can at the back
P = new(); n = 'toolbelt@torso'
for x in range(-0, 20):
    for y in range(-1, 11):
        for z in (33, 34):
            if 0 < x < 19 and -1 < y < 10: continue      # a ring round the waist
            put(P, n, x, y, z, 'brass' if (x in (9, 10) and y == -1) else ('leather_d' if z == 33 else 'leather'))
put(P, n, 9, -2, 34, 'brass_l'); put(P, n, 10, -2, 34, 'brass_l')
for x0 in (13, 2):                                        # pouches on the front, either side of the buckle
    box(P, n, x0, x0 + 3, -3, -2, 29, 34, 'leather', bev=0)
    box(P, n, x0, x0 + 3, -4, -3, 33, 34, 'leather_d'); put(P, n, x0 + 1, -5, 33, 'brass'); put(P, n, x0 + 2, -5, 33, 'brass')
box(P, n, 18, 19, -1, 0, 22, 32, 'iron')                  # the wrench on the left hip: a shaft ...
box(P, n, 17, 20, -1, 0, 20, 22, 'iron_l'); put(P, n, 18, -1, 20, None); put(P, n, 18, 0, 20, None)   # ... and its open jaw
for k in [k for k, v in P[n].items() if v is None]: del P[n][k]
box(P, n, 0, 1, 0, 1, 24, 32, 'wood')                     # the hammer on the right hip: the haft ...
box(P, n, -1, 2, -1, 2, 23, 25, 'iron'); put(P, n, -1, -1, 23, 'iron_l')   # ... and its head
cyl(P, n, 10.0, 11.5, 1.6, 28, 33, lambda x, y, z: 'brass_d' if z == 28 else 'brass')   # an oil can at the back
box(P, n, 9, 10, 11, 11, 34, 36, 'brass_l')               # its spout
out('hrim_toolbelt', P)

# ---- a steam tank on the back: a copper cylinder with iron bands, a valve, a gauge, straps over the shoulders
P = new(); n = 'tank@torso'
cyl(P, n, 10.0, 14.0, 3.6, 37, 51, lambda x, y, z: 'iron_d' if z in (39, 49) else ('copper_d' if z == 37 else 'copper'))
cyl(P, n, 10.0, 14.0, 2.4, 52, 52, 'copper_d'); cyl(P, n, 10.0, 14.0, 1.2, 53, 54, 'brass')
box(P, n, 8, 11, 13, 14, 55, 55, 'iron'); put(P, n, 7, 13, 55, 'rubber'); put(P, n, 12, 14, 55, 'rubber')   # the valve wheel
box(P, n, 13, 14, 17, 18, 43, 46, 'brass'); put(P, n, 13, 19, 44, 'glass'); put(P, n, 14, 19, 45, 'glass'); put(P, n, 13, 19, 45, 'glow')   # gauge
for x0 in (4, 13):                                         # the straps: down the back, over the shoulder, down the chest
    box(P, n, x0, x0 + 1, 10, 10, 36, 53, 'leather_d')
    box(P, n, x0, x0 + 1, -1, 10, 53, 53, 'leather')
    box(P, n, x0, x0 + 1, -1, -1, 42, 52, 'leather'); put(P, n, x0, -2, 44, 'brass'); put(P, n, x0 + 1, -2, 44, 'brass')
out('hrim_tank', P)

# ---- the cyberarm (left): replaces the whole arm. A brass ball joint at the shoulder, an iron frame with a copper piston
# for the upper arm, a riveted forearm with vents, a gauge and a hose, a three-fingered claw; and its implant on the chest
P = new()
u, l, h = 'arm_upper_l', 'arm_lower_l', 'hand_l'
for x in range(19, 27):                                    # the shoulder ball, z 48..54
    for y in range(1, 9):
        for z in range(47, 55):
            if (x + 0.5 - 22.5) ** 2 + (y + 0.5 - 4.5) ** 2 + (z + 0.5 - 51) ** 2 <= 3.9 ** 2:
                put(P, u, x, y, z, 'brass_l' if z >= 53 and x <= 22 else ('brass_d' if z <= 48 else 'brass'))
for (x, y) in ((20, 2), (25, 2), (20, 7), (25, 7)): box(P, u, x, x, y, y, 41, 47, 'iron_d')          # the frame's rods
cyl(P, u, 23.0, 5.0, 1.5, 42, 47, lambda x, y, z: 'iron_l' if z <= 44 else 'copper')                 # the piston
box(P, u, 20, 25, 2, 7, 41, 41, 'iron', bev=1)                                                       # the elbow's top plate
for z in range(41, 51): put(P, u, 26 + (1 if 44 <= z <= 47 else 0), 6, z, 'rubber')                  # a hose down the outside
box(P, l, 20, 25, 2, 7, 39, 40, 'brass', bev=1)                                                       # the elbow joint
box(P, l, 20, 25, 2, 7, 31, 38, lambda x, y, z: 'iron_d' if (y == 2 and x in (21, 23) and z in (34, 35, 36)) else 'iron', bev=1)  # vents on the front
for z in (31, 38): box(P, l, 20, 25, 2, 7, z, z, 'brass_d', bev=1)
for z in (33, 36): put(P, l, 26, 3, z, 'brass_l'); put(P, l, 26, 6, z, 'brass_l')                     # rivets
box(P, l, 26, 26, 4, 5, 34, 35, 'glow'); box(P, l, 27, 27, 4, 5, 34, 35, 'glass')                    # a gauge glowing on the outside
for z in range(31, 40): put(P, l, 23, 8 + (1 if 33 <= z <= 37 else 0), z, 'rubber')                  # a hose loop on the back
box(P, h, 20, 25, 2, 7, 29, 30, 'iron_d', bev=1)                                                     # the palm ...
for x in (20, 22, 24):                                                                                # ... three fingers ...
    box(P, h, x, x + 1, 3, 4, 26, 28, 'iron'); box(P, h, x, x + 1, 2, 3, 25, 25, 'brass_l')
box(P, h, 21, 22, 1, 1, 27, 29, 'iron'); put(P, h, 21, 0, 27, 'brass_l')                             # ... and a thumb, forward
# the implant: a brass plate on the left of the chest, wired into the shoulder
n = 'implant@torso'
box(P, n, 15, 19, -1, -1, 44, 51, lambda x, y, z: 'brass_d' if x in (15, 19) or z in (44, 51) else 'brass', bev=0)
for (x, z) in ((16, 45), (18, 45), (16, 50), (18, 50)): put(P, n, x, -2, z, 'iron_l')                  # bolts
box(P, n, 17, 17, -2, -2, 47, 48, 'glow')                                                            # a core
for x in range(16, 20): put(P, n, x, 0, 52, 'rubber'); put(P, n, x, 1, 53, 'rubber')                 # a cable to the shoulder
out('hrim_cyberarm', P)
