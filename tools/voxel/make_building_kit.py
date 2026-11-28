# Fogwright's voxel building kit (docs/design.md, Voxel buildings and interiors): the pieces every voxel building is
# assembled from, on the 2 m module in 10 cm voxels. Farhallow's look first: Wayfolk timber frame over limewash, grey
# fieldstone, straw thatch and a few slate shingles, poorer and plainer than the inner cities.
#   python3 tools/voxel/make_building_kit.py   -> godot/assets/voxel/buildings/kit_farhallow.vox
# MagicaVoxel axes: x along the piece, y from its outer face (0) inward, z up. Each piece is its own named model whose box
# starts at (0, 0, 0): the game places it by that corner (Vox.pieces), so every piece fills its box from the origin.
# Sizes (voxels, 10 cm): bay 20 wide, wall 3 thick, storey 30 (3.0 m) or 44 (4.4 m: 22 even stair risers), door 14 x 22, window 8 x 10 from a
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
for h in (30, 44):
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
stair("stair_30", 30); stair("stair_44", 44)

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

# ---------------------------------------------------------------- the freehold look (lore.md: Farhallow)
# Farhallow is a poor freehold on the far coast, outside any god's circle: wind-bent pines and no big timber, faded colour,
# the Fog at every dusk. So: drystone gathered from the fields and the shore in big flat stones, timbers salvaged from
# wrecks and tarred, heather thatch held down by ropes and hanging stones against the wind, the upper floor up in the roof
# behind a knee wall and lit by dormers, shutters to close against the Fog. Muted colours: the land is already greying.
PAL.update({
    'fst': (118, 116, 110), 'fst_d': (98, 97, 93), 'fst_l': (134, 131, 124), 'fst_g': (110, 114, 100),   # weathered, lichened
    'tar': (52, 44, 38), 'tar_d': (40, 34, 30), 'tar_l': (70, 60, 50),
    'drift': (126, 114, 98), 'drift_d': (104, 94, 80), 'drift_l': (142, 130, 112),
    'heather': (102, 90, 74), 'heather_d': (84, 74, 62), 'heather_l': (116, 102, 82),
    'rope': (150, 128, 92), 'turf': (86, 92, 60), 'turf_d': (70, 74, 50),
    'daub': (146, 136, 116),   # clay and lime daub over the stones inside: one flat face, cheap to draw
})
def drystone(x, z, ln=7, ht=3, seed=11):
    """big flat field and shore stones in courses, one weathered tone each, a few with lichen"""
    row = z // ht; sx = (x + (row % 2) * (ln // 2) + (row % 3) * 2) // ln
    r = _h(sx, row, seed)
    return 'fst_d' if r < 0.3 else ('fst_l' if r > 0.75 else ('fst_g' if r > 0.68 else 'fst'))
def dry_wall(name, h, opening=None, knee=False):
    box(name, 0, BAY - 1, 0, WALL - 1, 0, h - 1, lambda x, y, z: drystone(x, z) if y == 0 else 'daub')
    if opening:
        x0, x1, z0, z1 = opening
        cut(name, x0, x1, 0, WALL - 1, z0, min(z1, h - 1))
        if z1 + 2 <= h - 1: box(name, x0 - 2, x1 + 2, 0, WALL - 1, z1 + 1, z1 + 2, lambda x, y, z: 'tar' if z == z1 + 1 else 'tar_l')  # a ship-timber lintel
        if z0 > 0: box(name, x0 - 1, x1 + 1, 0, WALL - 1, z0 - 1, z0 - 1, 'fst_l')                                                    # a flat sill stone
    return name
for h in (44,):
    dry_wall('wall_dry_%d' % h, h); dry_wall('wall_dry_door_%d' % h, h, DOOR); dry_wall('wall_dry_window_%d' % h, h, WIN)
dry_wall('wall_dry_12', 12)   # the knee wall of a floor up in the roof
# a dormer over a knee-wall bay: its face carries on from the knee wall up to 2.6 m with the window in it, cheeks run back
# into the 45 degree roof, under a shallow heather lid. Its box: x the bay, y inward 0..13, z from the upper floor.
def dormer(name):
    top = 26
    for y in range(0, 14):
        lid = top - y // 4                                   # the lid falls one voxel in four toward the main roof
        if 12 + y > lid + 2: break
        for x in range(1, BAY):
            if y < WALL or x in (1, 2, BAY - 2, BAY - 1):    # the face, and the two cheeks
                for z in range(0, lid): put(name, x, y, z, (drystone(x, z) if y == 0 else 'daub') if y < WALL else 'drift')
            for t in range(2): put(name, x, y, lid + t, 'heather_d' if t == 0 else 'heather')
    for x in range(0, BAY + 1): put(name, x if x < BAY else BAY - 1, 0, top + 2, 'turf')   # a turf edge to the lid
    x0, x1, z0, z1 = WIN
    cut(name, x0, x1, 0, WALL - 1, z0, z1); box(name, x0 - 2, x1 + 2, 0, WALL - 1, z1 + 1, z1 + 2, lambda x, y, z: 'tar' if z == z1 + 1 else 'tar_l')
    box(name, x0 - 1, x1 + 1, 0, WALL - 1, z0 - 1, z0 - 1, 'fst_l')
dormer('dormer_12')
# partitions of salvaged planks between tarred posts: the freehold has no oak to frame with, so inner walls are boarded
def board_wall(name, h, opening=None):
    box(name, 0, BAY - 1, 0, WALL - 1, 0, h - 1, lambda x, y, z: 'tar' if x < 2 else ('drift_d' if (x // 4) % 3 == 0 else ('drift_l' if (x // 4) % 3 == 1 else 'drift')))
    box(name, 0, BAY - 1, 0, WALL - 1, h - 2, h - 1, 'tar')   # the plate the planks are nailed to
    if opening:
        x0, x1, z0, z1 = opening
        cut(name, x0, x1, 0, WALL - 1, z0, z1); box(name, x0 - 1, x1 + 1, 0, WALL - 1, z1 + 1, z1 + 2, 'tar')
        box(name, x0 - 1, x0 - 1, 0, WALL - 1, 0, z1, 'tar'); box(name, x1 + 1, x1 + 1, 0, WALL - 1, 0, z1, 'tar')
for h in (30, 44):
    board_wall('wall_board_%d' % h, h); board_wall('wall_board_door_%d' % h, h, DOOR)
    box('post_board_%d' % h, 0, 1, 0, WALL - 1, 0, h - 1, 'tar')
# a floor of big shore slabs, laid without mortar: few faces to draw
box('floor_slabs', 0, BAY - 1, 0, BAY - 1, 0, 0, lambda x, y, z: (lambda r: 'fst_d' if r < 0.3 else ('fst_l' if r > 0.7 else 'fst'))(_h(x // 10 + (y // 7) % 2 * 5, y // 7, 5)))
# shutters, open: two tarred leaves either side of a window, hung on the wall's face (the builder sets them 0.1 m proud)
box('shutters', 0, 15, 0, 0, 0, WIN_H - 1, lambda x, y, z: None if 4 <= x <= 11 else ('tar_d' if x % 2 == 0 else 'tar'))
P['shutters'] = {k: v for k, v in P['shutters'].items() if v}
# a door of salvaged hull planks, tarred, with an iron bar bracket
box('door_leaf_dry', 0, DOOR_W - 1, 0, 1, 0, DOOR_H - 1, lambda x, y, z: 'iron' if (z in (5, DOOR_H - 6) and y == 0) or (x in (10, 11) and z in range(10, 13) and y == 1) else ('tar_d' if x % 4 == 3 else 'tar'))
# heather thatch on a 45 degree slope, netted with ropes along it every 0.7 m (ropes along the slope stay cheap: they do
# not break the long runs the mesher merges), held down at the eave by hanging stones (eave_weights)
def heather_slope(name):
    for y in range(BAY):
        for t in range(3):
            for x in range(BAY):
                c = 'heather_d' if t < 2 else ('rope' if y % 7 == 3 else ('heather_l' if (y // 7) % 2 == 0 else 'heather'))
                put(name, x, y, y + t, c)
heather_slope('roof_heather')
box('ridge_heather', 0, BAY - 1, 0, 3, 0, 2, lambda x, y, z: 'turf_d' if z == 0 else 'turf')       # a turf ridge
# the stones that weigh the ropes down at the eave: one under each rope
for x in range(0, BAY, 20):
    box('eave_weights', x, x, 0, 0, 3, 5, 'rope'); box('eave_weights', x, x + 1, 0, 1, 0, 2, 'fst_d')
# a drystone gable for the 12 m depth, to go with drystone walls
for x in range(120):
    top = min(x, 119 - x)
    for z in range(top + 1): box('gable_dry_120', x, x, 0, WALL - 1, z, z, lambda xx, y, zz: drystone(xx, zz) if y == 0 else 'daub')
# floors of driftwood and wreck boards on tarred joists
for y in range(BAY):
    c = R.choice(('drift', 'drift', 'drift_d', 'drift_l'))
    for x in range(BAY): put('floor_salvage', x, y, 2, c)
for x in range(BAY):
    for y in range(2, BAY, 5): box('floor_salvage', x, x, y, y + 1, 0, 1, 'tar')
# Hollin's waystone: a standing stone by the door with the road's mark cut in it
box('waystone', 0, 4, 0, 2, 0, 11, lambda x, y, z: 'fst_l' if (y == 0 and ((x == 2 and 3 <= z <= 9) or (z == 6 and 1 <= x <= 3))) else ('fst_g' if z > 9 else 'fst'))

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

# ---------------------------------------------------------------- fittings, at 5 cm (props: Vox.CHAR), kit_fittings.vox
# The inn's furniture, as the plan lists it, placed by the builder like the pieces (x along, y inward from the wall or
# the front, z up) but meshed at 5 cm. Sizes in 5 cm voxels.
F = {}
FPAL = dict(PAL, board=(126, 112, 94), board_d=(104, 92, 78), board_l=(142, 128, 108), oak=(84, 70, 58), oak_d=(62, 52, 44), oak_l=(100, 86, 70), straw=(196, 168, 104), wool=(120, 46, 40), wool_d=(96, 36, 32), linen=(200, 192, 170), ale=(150, 104, 52),
            pewter=(128, 130, 132), flame=(255, 196, 92), hoop=(70, 68, 66))
def fput(part, x, y, z, c): F.setdefault(part, {})[(x, y, z)] = c
def fbox(part, x0, x1, y0, y1, z0, z1, c):
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1): fput(part, x, y, z, c(x, y, z) if callable(c) else c)
def plank(x, y, z, run=5): return 'board_d' if x % run == 0 else ('board_l' if _h(x // run, 9, 1) > 0.7 else 'board')
# a trestle table 1.6 x 0.8 m, 0.8 m high: a plank top on two trestles with a stretcher
fbox('table', 0, 31, 0, 15, 14, 15, lambda x, y, z: 'board_d' if y % 5 == 4 and z == 15 else 'board')
for x0 in (3, 27): fbox('table', x0, x0 + 1, 2, 13, 0, 13, lambda x, y, z: 'oak' if z > 1 else 'oak_d')
fbox('table', 5, 26, 7, 8, 5, 6, 'oak')
# a bench to go with it, 1.6 m long, 0.45 m high
fbox('bench', 0, 31, 0, 5, 8, 8, 'board'); fbox('bench', 0, 31, 0, 5, 7, 7, 'board_d')
for x0 in (2, 28): fbox('bench', x0, x0 + 1, 1, 4, 0, 6, 'oak')
# the bar counter, one 2 m length: boarded front, an oak top that overhangs, a shelf behind
fbox('bar_counter', 0, 39, 1, 11, 0, 20, lambda x, y, z: plank(x, y, z, 4) if y == 1 else 'board_d')
fbox('bar_counter', 0, 39, 0, 13, 21, 22, lambda x, y, z: 'oak_l' if z == 22 else 'oak')
fbox('bar_counter', 0, 39, 0, 0, 0, 1, 'oak_d')
for x in (5, 14, 23, 32): fbox('bar_counter', x, x + 2, 4, 6, 23, 25, lambda x, y, z: 'pewter' if z < 25 or x == x else 'ale')
# a bed 1 x 2 m: oak frame and posts, a straw tick, a wool blanket, a linen bolster at the head (y high)
fbox('bed', 0, 19, 0, 39, 3, 5, 'oak'); fbox('bed', 1, 18, 1, 38, 6, 8, 'straw')
fbox('bed', 1, 18, 1, 28, 9, 9, lambda x, y, z: 'wool_d' if y % 6 == 0 else 'wool'); fbox('bed', 3, 16, 32, 37, 9, 10, 'linen')
for x0, y0 in ((0, 0), (18, 0), (0, 38), (18, 38)): fbox('bed', x0, x0 + 1, y0, y0 + 1, 0, 11 if y0 else 7, 'oak_d')
fbox('bed', 0, 19, 38, 39, 8, 14, 'oak')
# a chest 0.7 x 0.45 m with iron bands
fbox('chest', 0, 13, 0, 8, 0, 9, lambda x, y, z: 'iron' if x in (2, 11) else ('oak_d' if z == 6 else 'oak'))
# an ale barrel 0.6 m across, 0.8 m tall, standing; hoops near the ends and the middle
for z in range(16):
    r = 5.0 if z in (0, 15) else 5.9
    for x in range(12):
        for y in range(12):
            if (x - 5.5) ** 2 + (y - 5.5) ** 2 <= r * r: fput('barrel', x, y, z, 'hoop' if z in (2, 13) else 'board')
# shelves 1.6 m long and 1.8 m high against a wall, with jugs and sacks
fbox('shelf', 0, 31, 0, 6, 0, 35, lambda x, y, z: 'oak' if x in (0, 1, 30, 31) else None)
for z0 in (0, 12, 24, 34): fbox('shelf', 0, 31, 0, 6, z0, z0 + 1, 'board')
F['shelf'] = {k: v for k, v in F['shelf'].items() if v}
for x0, z0, c in ((4, 14, 'pewter'), (9, 14, 'ale'), (20, 26, 'pewter'), (25, 2, 'straw'), (5, 2, 'straw'), (14, 26, 'linen')):
    fbox('shelf', x0, x0 + 3, 1, 4, z0, z0 + 4, c)
# a lantern on a hook, 0.3 m: an iron cage round a flame
fbox('lantern', 0, 5, 0, 5, 0, 7, lambda x, y, z: 'flame' if 1 <= x <= 4 and 1 <= y <= 4 and 1 <= z <= 5 else ('iron' if x in (0, 5) and y in (0, 5) or z in (0, 7) else None))
fbox('lantern', 2, 3, 2, 3, 8, 11, 'iron')
F['lantern'] = {k: v for k, v in F['lantern'].items() if v}
# the keeper's counter for rooms: a short desk with a ledger
fbox('desk', 0, 23, 0, 11, 0, 17, lambda x, y, z: plank(x, y, z, 4) if y == 0 else 'board_d')
fbox('desk', 0, 23, 0, 11, 18, 19, 'oak'); fbox('desk', 8, 15, 3, 8, 20, 20, 'linen')
# the Vigil's lantern over the inn's door, the "Lantern" of its name: a lit wick bought from a chapter house, in an iron
# cage with a copper coil wound round it (the Fog shies from its hum), on a bracket from the wall
FPAL.update(copper=(168, 100, 58), gull=(196, 198, 196), gull_d=(120, 124, 126))
fbox('vigil_lantern', 0, 1, 0, 1, 10, 21, 'iron'); fbox('vigil_lantern', 0, 9, 0, 1, 20, 21, 'iron')      # bracket (y 0 is the wall)
fbox('vigil_lantern', 5, 6, 0, 1, 16, 19, 'iron')
fbox('vigil_lantern', 2, 9, 2, 9, 3, 15, lambda x, y, z: 'flame' if 3 <= x <= 8 and 3 <= y <= 8 and 5 <= z <= 13 else ('copper' if z in (6, 9, 12) else ('iron' if x in (2, 9) and y in (2, 9) or z in (3, 15) else None)))
fbox('vigil_lantern', 4, 7, 4, 7, 0, 2, 'iron')
F['vigil_lantern'] = {k: v for k, v in F['vigil_lantern'].items() if v}
# the inn's carved gull for its gable: wings out, pale paint gone grey
fbox('gull', 4, 7, 0, 3, 2, 5, 'gull'); fbox('gull', 0, 11, 1, 2, 5, 5, 'gull'); fbox('gull', 0, 1, 1, 2, 6, 6, 'gull_d'); fbox('gull', 10, 11, 1, 2, 6, 6, 'gull_d')
fbox('gull', 7, 8, 1, 2, 6, 7, 'gull'); fbox('gull', 9, 9, 1, 2, 6, 6, 'copper'); fbox('gull', 5, 6, 1, 2, 0, 1, 'tar')
# a bar of wreck timber: the keel of a lost boat laid on two barrels' worth of stone, tarred dark
fbox('bar_keel', 0, 39, 1, 11, 0, 20, lambda x, y, z: ('fst_d' if (x // 7 + z // 4) % 2 else 'fst') if y == 1 else 'tar_d')
fbox('bar_keel', 0, 39, 0, 13, 21, 23, lambda x, y, z: 'tar_l' if z == 23 else 'tar')
for x in (5, 14, 23, 32): fbox('bar_keel', x, x + 2, 4, 6, 24, 26, 'pewter')
mb.COL = FPAL; mb.NAMES = list(FPAL)
mb.write(os.path.join(out, 'kit_fittings.vox'), {n: F[n] for n in sorted(F)})
for name in sorted(F):
    v = F[name]; s = [max(p[i] for p in v) + 1 for i in range(3)]
    print('  %-22s %3d x %3d x %3d voxels (%.2f x %.2f x %.2f m)' % (name, s[0], s[1], s[2], s[0] / 20, s[1] / 20, s[2] / 20))
