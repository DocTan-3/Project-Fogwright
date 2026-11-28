# Fogwright's voxel building kit (docs/design.md, Voxel buildings and interiors): the pieces every voxel building is
# assembled from, on the 2 m module in 10 cm voxels. Farhallow's look first: Wayfolk timber frame over limewash, grey
# fieldstone, straw thatch and a few slate shingles, poorer and plainer than the inner cities.
#   python3 tools/voxel/make_building_kit.py   -> godot/assets/voxel/buildings/kit_farhallow.vox
# MagicaVoxel axes: x along the piece, y from its outer face (0) inward, z up. Each piece is its own named model whose box
# starts at (0, 0, 0): the game places it by that corner (Vox.pieces), so every piece fills its box from the origin.
# Sizes (voxels, 10 cm): bay 20 wide, wall 3 thick, storey 30 (3.0 m) or 45 (4.5 m), door 14 x 22, window 8 x 10 from a
# 9 sill, stair 2 rise x 3 tread x 14 wide, plinth 5.
import os, importlib.util, random
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('mb', os.path.join(HERE, 'make_base.py')); mb = importlib.util.module_from_spec(spec)
src = open(spec.origin).read(); exec(compile(src[:src.rindex('\nOUT = ')], spec.origin, 'exec'), mb.__dict__)

PAL = {
    'lime': (212, 204, 182), 'lime_d': (190, 181, 158), 'lime_l': (224, 217, 198),
    'oak': (104, 76, 50), 'oak_d': (78, 56, 36), 'oak_l': (126, 94, 62),
    'board': (146, 108, 70), 'board_d': (124, 90, 58), 'board_l': (162, 122, 80),
    'stone': (112, 110, 104), 'stone_d': (90, 88, 83), 'stone_l': (132, 129, 122), 'mortar': (150, 145, 132),
    'thatch': (190, 154, 92), 'thatch_d': (156, 122, 68), 'thatch_l': (210, 176, 112),
    'slate': (84, 90, 98), 'slate_d': (66, 72, 80), 'slate_l': (102, 108, 116),
    'iron': (64, 64, 68), 'glass': (112, 140, 150), 'lead': (58, 60, 64), 'soot': (46, 42, 40),
}
BAY, WALL, DOOR_W, DOOR_H, WIN_W, WIN_H, SILL, PLINTH = 20, 3, 14, 22, 8, 10, 9, 5
P = {}
def put(part, x, y, z, c): P.setdefault(part, {})[(x, y, z)] = c
def box(part, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1): put(part, x, y, z, c(x, y, z) if callable(c) else c)
def cut(part, x0, x1, y0, y1, z0, z1):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1): P[part].pop((x, y, z), None)
R = random.Random(7)
def tone(base, p=(0.18, 0.12)):
    """a colour with its darker and lighter tone mixed in, the way our materials carry one of each"""
    r = R.random(); return base + '_d' if r < p[0] else (base + '_l' if r > 1 - p[1] else base)
def _h(*k):
    n = 0
    for v in k: n = (n * 73856093 ^ (v + 0x9e37)) & 0x7fffffff
    n = (n ^ (n >> 13)) * 1274126177 & 0x7fffffff
    return (n % 10000) / 10000.0
def stones(base, x, y, z, ln=4, ht=2):
    """coursed stone for solid blocks: stones ln long and ht high, each course offset by half a stone, one tone per stone,
    so a face is a few large rectangles (cheap after greedy meshing), not a speckle of single voxels"""
    row = z // ht; sx = (x + (row % 2) * (ln // 2)) // ln; sy = (y + (row % 2) * (ln // 2)) // ln
    r = _h(sx, sy, row); return base + '_d' if r < 0.28 else (base + '_l' if r > 0.78 else base)
def patches(base, x, z, size=5, p=(0.12, 0.1)):
    """plaster that is mostly one colour, with a few weathered or fresher patches"""
    r = _h(x // size, z // size, 3); return base + '_d' if r < p[0] else (base + '_l' if r > 1 - p[1] else base)

# ---------------------------------------------------------------- walls: one bay, 2 m wide
def frame_wall(name, h, opening=None):
    """timber frame over limewash: a post at the bay's left end, sill and head beams, a mid rail and a brace; the infill
    sits one voxel back from the timbers, so the frame stands out. opening: (x0, x1, z0, z1) cut through, framed in oak"""
    box(name, 0, BAY - 1, 1, WALL - 1, 0, h - 1, lambda x, y, z: patches('lime', x, z))      # infill, set back
    box(name, 0, 1, 0, WALL - 1, 0, h - 1, 'oak')                                             # the post
    box(name, 0, BAY - 1, 0, WALL - 1, 0, 1, 'oak_d')                                         # sill beam
    box(name, 0, BAY - 1, 0, WALL - 1, h - 2, h - 1, 'oak')                                   # head beam
    mid = h // 2
    if not opening:
        box(name, 2, BAY - 1, 0, 0, mid - 1, mid, 'oak')                                      # mid rail
        for k in range(2, mid - 1):                                                           # a brace up from the sill
            x = 2 + int((k - 2) * (BAY - 4) / (mid - 3)); box(name, x, x + 1, 0, 0, k, k, 'oak_l')
    else:
        x0, x1, z0, z1 = opening
        box(name, x0 - 1, x1 + 1, 0, WALL - 1, z0 - 1 if z0 > 0 else 0, z1 + 2, 'oak')        # the frame round it
        cut(name, x0, x1, 0, WALL - 1, z0, z1)
        if z1 + 2 < mid - 1 or z0 > mid + 1: box(name, 2, BAY - 1, 0, 0, mid - 1, mid, 'oak')
    return name

def stone_wall(name, h, opening=None):
    """fieldstone in rough courses: stones 2 to 4 voxels long, two high, each its own tone, mortar between some"""
    for z in range(0, h, 2):
        x = -(z // 2 % 2) * 2
        while x < BAY:
            ln = R.choice((3, 4, 5, 6)); c = tone('stone', (0.25, 0.2))
            for xx in range(max(0, x), min(BAY, x + ln)):
                for zz in (z, z + 1):
                    if zz < h:
                        for y in range(WALL): put(name, xx, y, zz, c)
            x += ln
    if opening:
        x0, x1, z0, z1 = opening
        box(name, x0 - 1, x1 + 1, 0, WALL - 1, z1 + 1, z1 + 2, 'stone_l')                     # a stone lintel
        cut(name, x0, x1, 0, WALL - 1, z0, z1)
    return name

# openings are centred between this bay's post (x 0-1) and the next bay's (x 20-21), not on the bay's own 0-19, or the
# post and the left jamb merge into one thick timber and the door looks off-centre
def centred(w): x0 = 2 + (BAY - 2 - w) // 2; return x0, x0 + w - 1
DOOR = (*centred(DOOR_W), 0, DOOR_H - 1)
WIN = (*centred(WIN_W), SILL, SILL + WIN_H - 1)
for h in (30, 45):
    frame_wall('wall_frame_%d' % h, h); frame_wall('wall_frame_door_%d' % h, h, DOOR); frame_wall('wall_frame_window_%d' % h, h, WIN)
    stone_wall('wall_stone_%d' % h, h); stone_wall('wall_stone_door_%d' % h, h, DOOR); stone_wall('wall_stone_window_%d' % h, h, WIN)
    box('post_%d' % h, 0, 1, 0, WALL - 1, 0, h - 1, 'oak')   # the end post that closes a row of bays

# a window's glazing: leaded panes in a frame, one voxel thick, set into the opening's middle
box('window_leaded', 0, WIN_W - 1, 0, 0, 0, WIN_H - 1, lambda x, y, z: 'lead' if (x + z) % 3 == 0 or x in (0, WIN_W - 1) or z in (0, WIN_H - 1) else 'glass')
# a door leaf: vertical planks with two iron bands, hinged on its left edge (the game swings it about x = 0)
box('door_leaf', 0, DOOR_W - 1, 0, 1, 0, DOOR_H - 1, lambda x, y, z: 'iron' if z in (4, DOOR_H - 5) and y == 0 else ('board_d' if x % 3 == 2 else 'board'))

# ---------------------------------------------------------------- floors, plinth, stairs
box('plinth', 0, BAY - 1, 0, BAY - 1, 0, PLINTH - 1, lambda x, y, z: stones('stone', x, y, z, 5, 3))   # a 2 x 2 m footing block
def floor_boards(name):
    """an upper floor: boards along x on top, joists below every 5 voxels (they show as the ceiling of the room under it)"""
    for y in range(BAY):
        c = R.choice(('board', 'board', 'board_d', 'board_l'))
        for x in range(BAY): put(name, x, y, 2, c)
    for x in range(BAY):
        for y in range(2, BAY, 5): box(name, x, x, y, y + 1, 0, 1, 'oak')
floor_boards('floor_boards')
box('floor_flags', 0, BAY - 1, 0, BAY - 1, 0, 0, lambda x, y, z: stones('stone', x, y, 0, 5, 4) if (x % 5 and y % 5) else 'mortar')
def stair(name, rise):
    """a straight flight for one storey: 2-voxel risers, 3-voxel treads, 14 wide, on a solid oak stringer"""
    n = rise // 2
    for i in range(n):
        box(name, 0, DOOR_W - 1, i * 3, i * 3 + 2, 0, (i + 1) * 2 - 1, lambda x, y, z: 'board' if z >= (i + 1) * 2 - 1 else 'oak_d')
stair('stair_30', 30)

# ---------------------------------------------------------------- roofs
def roof_45(name, mat, length=BAY, run=20):
    """one 2 m length of a 45-degree roof slope: rising one voxel per voxel inward, three voxels thick, its lower edge
    at the eave (y = 0, z = 0); courses run along x"""
    for y in range(run):
        for t in range(3):
            for x in range(length): put(name, x, y, y + t, (stones(mat, x, 0, y, 5, 3) if t == 2 else mat + '_d'))
roof_45('roof_thatch', 'thatch'); roof_45('roof_slate', 'slate')
box('ridge_thatch', 0, BAY - 1, 0, 3, 0, 2, 'thatch_d')
def gable(name, span):
    """the gable end over a span (in voxels) under a 45-degree roof: limewash with a timber frame line, its base the
    width of the span and its peak span / 2 high"""
    half = span // 2
    for x in range(span):
        top = min(x, span - 1 - x)
        for z in range(top + 1): box(name, x, x, 0, WALL - 1, z, z, 'oak' if z <= 1 or z >= top - 1 or abs(x - half) <= 0 else patches('lime', x, z, 8))
gable('gable_120', 120)   # the inn's 12 m depth
box('chimney', 0, 7, 0, 7, 0, 39, lambda x, y, z: stones('stone', x, y, z, 4, 2))
for k in [(x, y, z) for x in range(2, 6) for y in range(2, 6) for z in range(37, 40)]: P['chimney'].pop(k, None)   # its flue

# ---------------------------------------------------------------- fittings (10 cm, the solid ones; small props come at 5 cm)
box('hearth', 0, 19, 0, 7, 0, 14, lambda x, y, z: 'soot' if 4 <= x <= 15 and y <= 6 and z <= 10 else stones('stone', x, y, z, 5, 3))
cut('hearth', 4, 15, 0, 5, 1, 9)   # the fire opening, floor stone left in

mb.COL = PAL; mb.NAMES = list(PAL)
out = os.path.join(HERE, '..', '..', 'godot', 'assets', 'voxel', 'buildings'); os.makedirs(out, exist_ok=True)
# lay the pieces out in a row in the file, so MagicaVoxel shows them side by side
x = 0; placed = {}
for name in sorted(P):
    vox = P[name]; w = max(p[0] for p in vox) + 1
    placed[name] = {(px + x, py, pz): c for (px, py, pz), c in vox.items()}; x += w + 4
mb.write(os.path.join(out, 'kit_farhallow.vox'), placed)
for name in sorted(P):
    v = P[name]; s = [max(p[i] for p in v) + 1 for i in range(3)]
    print('  %-22s %3d x %3d x %3d voxels (%.1f x %.1f x %.1f m)' % (name, s[0], s[1], s[2], s[0] / 10, s[1] / 10, s[2] / 10))
