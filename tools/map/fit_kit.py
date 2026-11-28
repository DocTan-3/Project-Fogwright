# Fit Farhallow's plan to what the voxel kit really builds (city-planning, after the build: the plan must hold the real
# footprints). The kit makes each house bigger than its plan rectangle (thick walls, porches, side wings, yards), so
# this moves each building straight back from whatever it crowds - streets, the square, walls, fields, its neighbours -
# keeping its angle and its own layout (so its bake stays good), and carries its doors, spurs, plot, trails and
# doodads with it. It writes each building's real footprint ("foot": [u0, v0, u1, v1] in its own frame) for the terraces.
#   godot --headless --path godot res://tests/footprints.tscn    (measures data/kit_footprints.json)
#   python3 tools/map/fit_kit.py [--report]
import json, math, os, sys
GD = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'godot', 'data')
plan = json.load(open(os.path.join(GD, 'farhallow.json')))
foot = json.load(open(os.path.join(GD, 'kit_footprints.json')))
B = plan['buildings']
ORIG = [(b['x'], b['y'], b['a']) for b in B]
CLEAR_STREET = 0.8   # bare ground between a street's edge and a wall or yard
CLEAR_HOUSE = 1.2    # between two buildings
def segd(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]; L = dx*dx+dy*dy
    t = max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L)) if L else 0
    q = (a[0]+t*dx, a[1]+t*dy); return math.hypot(p[0]-q[0], p[1]-q[1]), q
# the older floorplan scene (scripts/farhallow.gd, which the plan checker builds) lays each type's rooms out from the
# plot's corner, and some reach past the plot (the inn's stable): the room each building needs is both
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from building_types import T as TYPES
def _rooms(i):
    b = B[i]; rs = TYPES.get(b['type'], {}).get('rooms', [])
    if not rs: return None
    u1 = max(r[0]+r[2] for r in rs); v1 = max(r[1]+r[3] for r in rs); u0 = min(r[0] for r in rs); v0 = min(r[1] for r in rs)
    w, h = b['w'], b['h']; a0, a1 = u0-w/2, u1-w/2
    if b.get('mirror'): a0, a1 = -a1, -a0
    return (a0, v0-h/2, a1, v1-h/2)
ROOMS = [_rooms(i) for i in range(len(B))]
def rect(i, k=0.0):
    f = foot[str(i)]; r = ROOMS[i] or (f['min'][0], f['min'][1], f['max'][0], f['max'][1])
    return (min(f['min'][0], r[0])-k, min(f['min'][1], r[1])-k, max(f['max'][0], r[2])+k, max(f['max'][1], r[3])+k)
def to_world(b, u, v):
    ca, sa = math.cos(b['a']), math.sin(b['a']); return (b['x']+u*ca-v*sa, b['y']+u*sa+v*ca)
def to_local(b, x, y):
    ca, sa = math.cos(b['a']), math.sin(b['a']); dx, dy = x-b['x'], y-b['y']; return (dx*ca+dy*sa, -dx*sa+dy*ca)
def samples(i, k=0.0, step=0.5):
    b = B[i]; u0, v0, u1, v1 = rect(i, k); out = []
    nu = max(1, int((u1-u0)/step)); nv = max(1, int((v1-v0)/step))
    for a in range(nu+1):
        for c in range(nv+1):
            if a in (0, nu) or c in (0, nv): out.append(to_world(b, u0+(u1-u0)*a/nu, v0+(v1-v0)*c/nv))
    return out
def inside(i, p, k=0.0):
    u, v = to_local(B[i], *p); u0, v0, u1, v1 = rect(i, k); return u0 <= u <= u1 and v0 <= v <= v1
STREETS = [(s['pts'], s['width']) for s in plan['roads']+plan['lanes']]
NAMES = {id(s['pts']): s['name'] for s in plan['roads']+plan['lanes']}
SQ = plan['square']
WALLS = [(w['pts'], 1.5) for w in plan['walls']]
RECTS = [r for r in plan['rects']]
def clashes(i):
    """push vectors (world) that would clear building i of what it crowds, with what each one is"""
    out = []
    for p in samples(i):
        for pts, w in STREETS:
            for a, b in zip(pts, pts[1:]):
                d, q = segd(p, a, b); need = w/2+CLEAR_STREET
                if d < need:
                    n = ((p[0]-q[0])/d, (p[1]-q[1])/d) if d > 1e-3 else (0, 0); out.append(('street '+NAMES[id(pts)], n, need-d))
        d = math.hypot(p[0]-SQ['x'], p[1]-SQ['y']); need = SQ['r']+CLEAR_STREET
        if d < need: out.append(('square', ((p[0]-SQ['x'])/d, (p[1]-SQ['y'])/d), need-d))
        for pts, cl in WALLS:
            for a, b in zip(pts, pts[1:]):
                d, q = segd(p, a, b)
                if d < cl and d > 1e-3: out.append(('wall', ((p[0]-q[0])/d, (p[1]-q[1])/d), cl-d))
        for r in RECTS:
            if r['x0']-0.8 <= p[0] <= r['x1']+0.8 and r['y0']-0.8 <= p[1] <= r['y1']+0.8:
                c = ((r['x0']+r['x1'])/2, (r['y0']+r['y1'])/2); d = math.hypot(p[0]-c[0], p[1]-c[1]) or 1
                out.append((r['name'], ((p[0]-c[0])/d, (p[1]-c[1])/d), 0.5))
    for j in range(len(B)):
        if j == i: continue
        hit = [p for p in samples(i, CLEAR_HOUSE/2) if inside(j, p, CLEAR_HOUSE/2)]
        if hit:
            dx, dy = B[i]['x']-B[j]['x'], B[i]['y']-B[j]['y']; d = math.hypot(dx, dy) or 1
            out.append(('building %d' % j, (dx/d, dy/d), 0.25*len(hit)**0.5))
    return out
def report():
    bad = 0
    for i, b in enumerate(B):
        c = clashes(i)
        if c:
            bad += 1; what = sorted({k for k, _, _ in c}); worst = max(x for _, _, x in c)
            print('  %2d %-40s crowds %s (up to %.1f m)' % (i, b['name'][:40] or b['type'], ', '.join(what), worst))
    return bad
print('before:'); n0 = report()
if '--report' in sys.argv: sys.exit(0)
moved = [(0.0, 0.0)]*len(B)
def shift(i, du, dv):   # move building i in its own frame
    b = B[i]; ca, sa = math.cos(b['a']), math.sin(b['a']); dx, dy = du*ca-dv*sa, du*sa+dv*ca
    b['x'] += dx; b['y'] += dy; moved[i] = (moved[i][0]+dx, moved[i][1]+dy)
GROUND = lambda c: [k for k in c if not k[0].startswith('building')]
OVERRIDE = {}   # by hand, where pushing back is not enough: building -> (along, back) in its own frame, metres
for i, (du, dv) in OVERRIDE.items(): pass
HOUSES = lambda c: [k for k in c if k[0].startswith('building')]
# 1. straight back from the street it faces (its front is its local -v) until the ground is clear, then
# 2. a search: small moves of one building at a time, kept when they leave less crowding (streets and walls count ten
#    times a neighbour's yard), and moving a building far from where the plan put it costs a little
import random
rng = random.Random(7)
# by hand first, where the site was too small for what the kit built: the inn steps back west off the gate road and
# north of the square; the farmstead and its byre wing go to the west end of the west road, which now runs on to its
# yard; the farm lane bends west round the inn's back
START = {0: (45.5, 39.5), 15: (27.0, 55.5), 9: (93.5, 54.0), 17: (12.3, 42.0)}   # the hen house and goat pen by the west palisade, past the vegetable plots
REFACE = {9: 0.0}   # the net-mender's cottage had no room in the wedge by the square: it faces the salt path now
for i, (x, y) in START.items():
    moved[i] = (x-B[i]['x'], y-B[i]['y']); B[i]['x'], B[i]['y'] = x, y
for i, a in REFACE.items(): B[i]['a'] = a
for r in plan['roads']:
    if r['name'] == 'west road' and r['pts'][-1] == [36, 64]: r['pts'].append([30, 64.5])
for r in plan['lanes']:
    if r['name'] == 'farm lane': r['pts'] = [[46, 60], [38.5, 54], [34.5, 47.5], [31.5, 44.5]]
ANCHOR = [(b['x'], b['y']) for b in B]   # where the plan (or the hand) put each: the search stays near it
STREETS[:] = [(s['pts'], s['width']) for s in plan['roads']+plan['lanes']]
NAMES.clear(); NAMES.update({id(s['pts']): s['name'] for s in plan['roads']+plan['lanes']})
for i in range(len(B)):
    if i in START: continue
    for k in range(40):
        if not GROUND(clashes(i)): break
        shift(i, 0, 0.1)
def cost(i):
    c = clashes(i); m = (B[i]['x']-ANCHOR[i][0], B[i]['y']-ANCHOR[i][1])
    return sum(x*(10 if not k.startswith('building') else 6) for k, _, x in c) + 0.04*(m[0]**2+m[1]**2)
total = lambda: sum(cost(i) for i in range(len(B)))
T = total(); print('search from %.1f' % T)
for step in range(int(sys.argv[sys.argv.index('--steps')+1]) if '--steps' in sys.argv else 6000):
    i = rng.randrange(len(B))
    if i in (3, 13, 14, 17): continue   # the shrine, the granary, the guard post and the hen house stand where they must
    temp = 0.3*(1-step/6000)
    before = cost(i) + sum(cost(j) for j in range(len(B)) if j != i and abs(B[j]['x']-B[i]['x'])+abs(B[j]['y']-B[i]['y']) < 30)
    du, dv = rng.gauss(0, 0.6), rng.gauss(0, 0.6); shift(i, du, dv)
    after = cost(i) + sum(cost(j) for j in range(len(B)) if j != i and abs(B[j]['x']-B[i]['x'])+abs(B[j]['y']-B[i]['y']) < 30)
    if after > before and rng.random() > math.exp(-(after-before)/max(temp, 1e-4)): shift(i, -du, -dv)
print('search to %.1f' % total())
it = 0
print('after %d rounds:' % (it+1)); n1 = report()
# carry each building's things with it: doors, spurs, its plot, its trails and doodads keep their place in its frame
def carry(i, p):
    o = ORIG[i]; return list(to_world(B[i], *to_local({'x': o[0], 'y': o[1], 'a': o[2]}, *p)))
def near_old(i, p, k=3.0):
    o = ORIG[i]; u, v = to_local({'x': o[0], 'y': o[1], 'a': o[2]}, *p); u0, v0, u1, v1 = rect(i, k); return u0 <= u <= u1 and v0 <= v <= v1
turn = lambda i: B[i]['a']-ORIG[i][2]
for i, b in enumerate(B):
    b['doors'] = [carry(i, p) for p in b['doors']]
    f = foot[str(i)]; b['foot'] = [round(f['min'][0], 2), round(f['min'][1], 2), round(f['max'][0], 2), round(f['max'][1], 2)]
def nearest_street(p):
    best = None
    for r in plan['roads']+plan['lanes']:
        for a_, b_ in zip(r['pts'], r['pts'][1:]):
            d, q = segd(p, a_, b_)
            if best is None or d < best[0]: best = (d, q, r['name'])
    return best
for s in plan['spurs']:
    i = s['owner']; s['door'] = carry(i, s['door'])
    if i in REFACE: s['street'] = nearest_street(s['door'])[2]
    pts = next((r['pts'] for r in plan['roads']+plan['lanes'] if r['name'] == s.get('street')), None)
    if pts: s['to'] = list(min((segd(s['door'], a, b2) for a, b2 in zip(pts, pts[1:])), key=lambda t: t[0])[1])
    else: s['to'] = carry(i, s['to'])
for pl in plan['plots']:
    i = pl['owner']; pl['x'], pl['y'] = carry(i, (pl['x'], pl['y'])); pl['a'] += turn(i)
for d in plan['doodads']:
    o = d.get('owner', -1)
    if isinstance(o, int) and o >= 0: d['x'], d['y'] = carry(o, (d['x'], d['y'])); d['a'] = d.get('a', 0) + turn(o)
for t in plan['trails']:
    for i in range(len(B)):
        if any(near_old(i, p) for p in t['pts'][:2]):
            t['pts'] = [carry(i, p) if near_old(i, p) else p for p in t['pts']]; break
# plots: each is shortened from its far end until it clears the streets, the walls and other buildings (real plots end
# where the neighbour's begin); the plot's near edge stays against its house
def plot_pts(pl, step=0.5):
    out = []; b = {'x': pl['x'], 'y': pl['y'], 'a': pl['a']}; w, h = pl['w']/2, pl['h']/2
    for k in range(int(2*w/step)+1):
        for v in (-h, h): out.append(to_world(b, -w+k*step, v))
    for k in range(int(2*h/step)+1):
        for u in (-w, w): out.append(to_world(b, u, -h+k*step))
    return out
def plot_bad(pl):
    for p in plot_pts(pl):
        for pts, w in STREETS:
            if any(segd(p, a_, b_)[0] < w/2+0.3 for a_, b_ in zip(pts, pts[1:])): return True
        for pts, cl in WALLS:
            if any(segd(p, a_, b_)[0] < cl for a_, b_ in zip(pts, pts[1:])): return True
        if math.hypot(p[0]-SQ['x'], p[1]-SQ['y']) < SQ['r']+0.3: return True
        if any(j != pl['owner'] and inside(j, p, 0.9) for j in range(len(B))): return True
    return False
for pl in list(plan['plots']):
    o = B[pl['owner']]; _, vh = to_local({'x': pl['x'], 'y': pl['y'], 'a': pl['a']}, o['x'], o['y'])
    away = -1 if vh > 0 else 1   # the far end, in the plot's frame
    while plot_bad(pl) and pl['h'] > 2.0:
        pl['h'] -= 0.5; c = to_world({'x': pl['x'], 'y': pl['y'], 'a': pl['a']}, 0, -away*0.25); pl['x'], pl['y'] = c
    if plot_bad(pl): plan['plots'].remove(pl); print('  dropped the plot of', B[pl['owner']]['name'] or B[pl['owner']]['type'])
# trails from the doors of moved buildings are walked again: the shortest way over open ground (round houses, plots and
# walls, cheaper on the streets) to the nearest street
import heapq
G = 0.5; NX, NY = int(140/G), int(110/G)
def cell(p): return (int(p[0]/G), int(p[1]/G))
def blocked_grid():
    bl = set(); on = set()
    for y in range(NY):
        for x in range(NX):
            p = ((x+0.5)*G, (y+0.5)*G)
            if any(inside(j, p, 0.2) for j in range(len(B))): bl.add((x, y)); continue
            if any(segd(p, a_, b_)[0] < cl*0.7 for pts, cl in WALLS for a_, b_ in zip(pts, pts[1:])): bl.add((x, y)); continue
            if any(segd(p, a_, b_)[0] < w/2 for pts, w in STREETS for a_, b_ in zip(pts, pts[1:])) or math.hypot(p[0]-SQ['x'], p[1]-SQ['y']) < SQ['r']: on.add((x, y))
    return bl, on
def in_plan_rect(i, p, k=0.9):   # the house itself (its plan rectangle and its older floorplan's rooms)
    u, v = to_local(B[i], *p); r = ROOMS[i]
    return (abs(u) <= B[i]['w']/2+k and abs(v) <= B[i]['h']/2+k) or bool(r and r[0]-k <= u <= r[2]+k and r[1]-k <= v <= r[3]+k)
def walk(start, bl, on, own):
    s0 = cell(start); best = {s0: 0}; prev = {}; q = [(0, s0)]
    while q:
        c, cur = heapq.heappop(q)
        if cur in on and cur != s0:
            path = [cur]
            while path[-1] in prev: path.append(prev[path[-1]])
            return [((x+0.5)*G, (y+0.5)*G) for x, y in reversed(path)]
        if c > best.get(cur, 1e9) or c > 120: continue
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            n = (cur[0]+dx, cur[1]+dy)
            if not (0 <= n[0] < NX and 0 <= n[1] < NY): continue
            p = ((n[0]+0.5)*G, (n[1]+0.5)*G)
            if n in bl and not (inside(own, p, 0.2) and not in_plan_rect(own, p)): continue
            nc = c + math.hypot(dx, dy)*G*(1.0 if n not in on else 0.5)
            if nc < best.get(n, 1e9): best[n] = nc; prev[n] = cur; heapq.heappush(q, (nc, n))
    return None
bl, on = blocked_grid()
for t in list(plan['trails']):
    named = [i for i in range(len(B)) if B[i]['name'] and t['purpose'].endswith(B[i]['name'])]
    own = named[0] if named else next((i for i in range(len(B)) if inside(i, t['pts'][0], 3.0)), None)
    if own is None or abs(moved[own][0]) + abs(moved[own][1]) + abs(B[own]['a']-ORIG[own][2]) < 0.01: continue
    if own is None: continue
    head = t['pts'][:2]
    route = walk(head[-1], bl, on, own)
    if route is None: plan['trails'].remove(t); print('  no way out for', t['purpose']); continue
    t['pts'] = head + [list(p) for p in route[1::3]] + [list(route[-1])]
def inside_plot(pl, p):
    u, v = to_local({'x': pl['x'], 'y': pl['y'], 'a': pl['a']}, *p); return abs(u) <= pl['w']/2+0.3 and abs(v) <= pl['h']/2+0.3
# doodads that the move left standing on a street, a trail or in another house are taken away (the kit's own yards
# dress each house anyway)
TR = [(t['pts'], t['width']) for t in plan['trails']]
keep = []
COAST = [(55,110),(62,96),(74,88),(86,84),(96,76),(104,64),(112,58),(124,56),(140,52),(140,110)]   # farhallow_plan.py's
def in_sea(p):
    x, y = p; c = False
    for i in range(len(COAST)):
        x0, y0 = COAST[i]; x1, y1 = COAST[i-1]
        if (y0 > y) != (y1 > y) and x < x0+(y-y0)*(x1-x0)/(y1-y0): c = not c
    return c or any(math.hypot(x-cx, y-cy) < 2.5 for cx, cy in COAST[:-1] if in_sea_edge(p, cx, cy))
in_sea_edge = lambda p, cx, cy: False
def on_fence(pl, p):   # near a plot's wall or fence line
    u, v = to_local({'x': pl['x'], 'y': pl['y'], 'a': pl['a']}, *p); w, h = pl['w']/2, pl['h']/2
    return abs(u) <= w+0.3 and abs(v) <= h+0.3 and (abs(abs(u)-w) < 0.4 or abs(abs(v)-h) < 0.4)
for dd in plan['doodads']:
    o = dd.get('owner', -1); mine = isinstance(o, int) and o >= 0
    b = {'x': dd['x'], 'y': dd['y'], 'a': dd.get('a', 0)}; hw, hh = dd.get('w', 0.5)/2, dd.get('h', 0.5)/2
    pts = [(dd['x'], dd['y'])] + [to_world(b, su*hw, sv*hh) for su in (-1, 1) for sv in (-1, 1)]
    if mine and abs(moved[o][0]) + abs(moved[o][1]) > 0.01:
        bad = any(segd(p, a_, b_)[0] < w/2+0.3 for p in pts for pts2, w in STREETS+TR for a_, b_ in zip(pts2, pts2[1:])) or \
              any(j != o and inside(j, p, 1.0) for p in pts for j in range(len(B))) or \
              any(segd(p, a_, b_)[0] < cl for p in pts for w2, cl in WALLS for a_, b_ in zip(w2, w2[1:])) or \
              any(in_sea(p) or any(segd(p, COAST[k], COAST[k+1])[0] < 2.0 for k in range(len(COAST)-2)) for p in pts) or \
              any(on_fence(pl, p) or (pl['owner'] != o and inside_plot(pl, p)) for p in pts for pl in plan['plots'])
    else:   # the village's own (bell, torches, racks): when a house now stands on it, it steps out of the way
        hit = [j for p in pts for j in range(len(B)) if inside(j, p, 0.2)]
        for k in range(30):
            if not hit: break
            j = hit[0]; dx, dy = dd['x']-B[j]['x'], dd['y']-B[j]['y']; L = math.hypot(dx, dy) or 1
            dd['x'] += dx/L*0.1; dd['y'] += dy/L*0.1; b = {'x': dd['x'], 'y': dd['y'], 'a': dd.get('a', 0)}
            pts = [(dd['x'], dd['y'])] + [to_world(b, su*hw, sv*hh) for su in (-1, 1) for sv in (-1, 1)]
            hit = [j for p in pts for j in range(len(B)) if inside(j, p, 0.2)]
        bad = bool(hit)
    if bad and 'beat' in dd.get('purpose', ''): bad = False   # the prologue needs it: it stays where its house took it
    if bad: print('  took away the %s (%s)' % (dd['kind'], dd.get('purpose', '')))
    else: keep.append(dd)
plan['doodads'] = keep
for i, (dx, dy) in enumerate(moved):
    if abs(dx)+abs(dy) > 0.01: print('  moved %2d %-40s %.1f m' % (i, B[i]['name'][:40] or B[i]['type'], math.hypot(dx, dy)))
json.dump(plan, open(os.path.join(GD, 'farhallow.json'), 'w'), indent=1)
print('wrote farhallow.json: %d buildings crowded something before, %d after' % (n0, n1))
