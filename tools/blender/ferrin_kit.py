# The rest of the Ferrin Quarter kit, to the forge-house's standard: the gunsmith's shop, the smelter and Ostrak's shrine.
# Shares the forge-house's materials, building blocks and walls-with-true-openings (the head of ferrin_forge.py, up to the
# forge itself), and finishes each building the same way: baked occlusion, soot and rust in the vertex colours, a decimated
# mid-distance version, a GLB with materials by name.
#
#   BUILDING=shop|smelter|shrine python3.11 ferrin_kit.py -- out.glb      (RENDER=shot.png for a Cycles beauty shot)
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'ferrin_forge.py')).read()
exec(compile(src[:src.index('# ---------------------------------------------------------------- the forge-house')], 'ferrin_forge_head', 'exec'))
BUILDING = os.environ.get('BUILDING', 'shop')
random.seed({'shop': 21, 'smelter': 33, 'shrine': 45, 'narrow': 57, 'toolmaker': 69, 'stair': 81, 'foundry': 93}.get(BUILDING, 7))

def smooth(a, b, x): t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
SOOT = []      # (x, y, z0, z1, radius, strength): plumes and stained places
GLOWS = []     # (x, y, z, energy): for the beauty shot
LIGHT_SPOTS = []

# ---------------------------------------------------------------- the Ferrin shell: thick basalt walls with true openings,
# a battered base, quoins, a string course, a corbel table under an iron cornice, a coped parapet, a low iron roof
def shell(W, D, H1, H2, PAR, T, front, sides=(), back=(), batter_gaps=(), course_at=None, lsides=None):
    fy = -D / 2; HT = H1 + H2 + PAR
    wall_panel((-W / 2, fy, 0), (1, 0, 0), (0, -1, 0), W, HT, T, front)
    wall_panel((W / 2, fy, 0), (0, 1, 0), (1, 0, 0), D, HT, T, list(sides))
    wall_panel((-W / 2, D / 2, 0), (0, -1, 0), (-1, 0, 0), D, HT, T, list(sides if lsides is None else lsides))
    wall_panel((W / 2, D / 2, 0), (-1, 0, 0), (0, 1, 0), W, HT, T, list(back))
    def batter(x0, x1, face, n, along_x, hb=1.2, out=0.4):
        x = x0
        while x < x1 - 0.05:
            L = min(random.uniform(0.8, 1.3), x1 - x)
            if along_x:
                pts = [Vector((x + 0.006, face, 0)), Vector((x + L - 0.006, face, 0)), Vector((x + L - 0.006, face, hb)), Vector((x + 0.006, face, hb))]
                sl = lambda p: Vector((p.x, p.y + n * out * (1 - p.z / hb), p.z)); bk = lambda p: Vector((p.x, face - n * 0.15, p.z))
            else:
                pts = [Vector((face, x + 0.006, 0)), Vector((face, x + L - 0.006, 0)), Vector((face, x + L - 0.006, hb)), Vector((face, x + 0.006, hb))]
                sl = lambda p: Vector((p.x + n * out * (1 - p.z / hb), p.y, p.z)); bk = lambda p: Vector((face - n * 0.15, p.y, p.z))
            bm = bmesh.new(); f = [bm.verts.new(sl(p)) for p in pts]; b = [bm.verts.new(bk(p)) for p in pts]
            bm.faces.new(f); bm.faces.new(list(reversed(b)))
            for k in range(4): bm.faces.new([f[k], b[k], b[(k + 1) % 4], f[(k + 1) % 4]])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bevel_all(bm, 0.03); add_bm(bm, 'F_ashlar', 'plinth'); x += L
    xs = [-W / 2 - 0.4] + [v for g in batter_gaps for v in g] + [W / 2 + 0.4]
    for k in range(0, len(xs), 2):
        if xs[k + 1] - xs[k] > 1.2: batter(xs[k], xs[k + 1], fy, -1, True)
    batter(-D / 2, D / 2 + 0.4, W / 2, 1, False); batter(-D / 2, D / 2 + 0.4, -W / 2, -1, False); batter(-W / 2, W / 2, D / 2, 1, True)
    for cx, cy, sx, sy in [(-W / 2, fy, 1, 1), (W / 2, fy, -1, 1), (-W / 2, D / 2, 1, -1), (W / 2, D / 2, -1, -1)]:   # quoins
        z = 0.6; k = 0
        while z < H1 + H2 - 0.1:
            h = 0.42; Lf, Ls = (0.9, 0.48) if k % 2 == 0 else (0.48, 0.9)
            box((cx + sx * (Lf / 2 - 0.04), cy - sy * 0.03, z + h / 2), (Lf, 0.14, h - 0.015), 'F_ashlar', 0.035, tag='quoin')
            box((cx - sx * 0.03, cy + sy * (Ls / 2 - 0.04), z + h / 2), (0.14, Ls, h - 0.015), 'F_ashlar', 0.035, tag='quoin')
            z += h; k += 1
    if course_at:
        for (c, s) in [((0, fy - 0.07, course_at), (W + 0.3, 0.26, 0.3)), ((0, D / 2 + 0.07, course_at), (W + 0.3, 0.26, 0.3)),
                       ((W / 2 + 0.07, 0, course_at), (0.26, D + 0.3, 0.3)), ((-W / 2 - 0.07, 0, course_at), (0.26, D + 0.3, 0.3))]:
            box(c, s, 'F_ashlar', 0.05, tag='course')
    top = H1 + H2
    def corbels(a0, a1, face, n, along_x):
        k = a0 + 0.45
        while k < a1 - 0.3:
            for dz, out in [(0.0, 0.16), (0.2, 0.3)]:
                c = (k, face + n * out / 2, top - 0.25 + dz) if along_x else (face + n * out / 2, k, top - 0.25 + dz)
                box(c, (0.36, out, 0.2) if along_x else (out, 0.36, 0.2), 'F_ashlar', 0.02, tag='corbel')
            k += 0.85
        c = ((a0 + a1) / 2, face + n * 0.2, top + 0.08) if along_x else (face + n * 0.2, (a0 + a1) / 2, top + 0.08)
        box(c, (a1 - a0 + 0.8, 0.42, 0.12) if along_x else (0.42, a1 - a0 + 0.8, 0.12), 'F_iron', 0.01, tag='cornice')
    corbels(-W / 2, W / 2, fy, -1, True); corbels(-W / 2, W / 2, D / 2, 1, True); corbels(-D / 2, D / 2, W / 2, 1, False); corbels(-D / 2, D / 2, -W / 2, -1, False)
    def coping(a0, a1, fixed, along_x):
        x = a0
        while x < a1 - 0.05:
            L = min(random.uniform(0.9, 1.2), a1 - x)
            if along_x: box(((2 * x + L) / 2, fixed, HT + 0.09), (L - 0.01, T + 0.18, 0.18), 'F_ashlar', 0.04, tag='coping')
            else: box((fixed, (2 * x + L) / 2, HT + 0.09), (T + 0.18, L - 0.01, 0.18), 'F_ashlar', 0.04, tag='coping')
            x += L
    coping(-W / 2, W / 2, fy + T / 2, True); coping(-W / 2, W / 2, D / 2 - T / 2, True)
    coping(fy + T, D / 2 - T, W / 2 - T / 2, False); coping(fy + T, D / 2 - T, -W / 2 + T / 2, False)
    rz0 = top + 0.05; rz1 = rz0 + 0.7; ix0, ix1, iy0, iy1 = -W / 2 + T, W / 2 - T, fy + T, D / 2 - T; ry = (iy0 + iy1) / 2
    bm = bmesh.new(); v = [bm.verts.new(p) for p in [(ix0, iy0, rz0), (ix1, iy0, rz0), (ix1, iy1, rz0), (ix0, iy1, rz0), (ix0 + 1.0, ry, rz1), (ix1 - 1.0, ry, rz1)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4)]: bm.faces.new([v[i] for i in f])
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=2, use_grid_fill=True); add_bm(bm, 'F_iron', 'roof')
    for k in range(1, 10):
        x = ix0 + (ix1 - ix0) * k / 10
        if ix0 + 0.8 < x < ix1 - 0.8:
            for ya in (iy0, iy1): pipe((x, ya, rz0 + 0.03), (x, ry, rz1 + 0.03), 0.025, 'F_iron', seg=4)
    return dict(fy=fy, HT=HT, top=top, rz0=rz0)

def iron_window(x, y, n, along, w, hgt, z0, shutters=True):
    n = Vector(n); a = Vector(along); ax = abs(a.x) > 0.5
    dims = lambda la, ln, lz: (la, ln, lz) if ax else (ln, la, lz)
    base = Vector((x, y, 0))
    box(base + n * 0.06 + Vector((0, 0, z0 - 0.07)), dims(w + 0.32, 0.34, 0.14), 'F_ashlar', 0.025, tag='sill')
    box(base + n * 0.03 + Vector((0, 0, z0 + hgt + 0.16)), dims(w + 0.42, 0.28, 0.32), 'F_ashlar', 0.03, tag='lintel')
    box(base - n * 0.34 + Vector((0, 0, z0 + hgt / 2)), dims(w, 0.03, hgt), 'F_glass', 0.0, tag='glass')
    for k in (-1, 1): box(base - n * 0.3 + a * (k * w / 6) + Vector((0, 0, z0 + hgt / 2)), dims(0.035, 0.035, hgt), 'F_iron', 0.0)
    box(base - n * 0.3 + Vector((0, 0, z0 + hgt * 0.55)), dims(w, 0.035, 0.035), 'F_iron', 0.0)
    if shutters:
        th = math.radians(18); lw = w / 2 + 0.04
        for k in (-1, 1):
            hinge = base + a * (k * (w / 2 + 0.03)) + n * 0.03; d = a * (k * math.cos(th)) + n * math.sin(th); ctr = hinge + d * (lw / 2)
            box((ctr.x, ctr.y, z0 + hgt / 2), (lw, 0.05, hgt + 0.04), 'F_iron', 0.008, rz=math.atan2(d.y, d.x), tag='shutter')

def cog(cx, y, cz, cr, teeth=12, depth=0.1):
    cyl((cx, y - depth * 0.7, cz), cr, cr, depth, 'F_iron', seg=24, axis='Y', bev=0.012, tag='cog')
    for t in range(teeth):
        a = t / teeth * math.pi * 2; h0, h1 = cr * 0.28, cr * 0.18
        P = lambda r, s2: Vector((cx + math.cos(a) * r - math.sin(a) * s2, y - 0.025, cz + math.sin(a) * r + math.cos(a) * s2))
        prism([P(cr - 0.03, -h0), P(cr - 0.03, h0), P(cr + cr * 0.32, h1), P(cr + cr * 0.32, -h1)], depth * 0.9, (0, -1, 0), 'F_iron', 0.008, tag='cog')
    cyl((cx, y - depth * 1.3, cz), cr * 0.4, cr * 0.4, depth * 0.8, 'F_iron', seg=12, axis='Y', bev=0.01)

# ================================================================ the gunsmith's shop
if BUILDING == 'shop':
    NAME = 'FerrinShop'
    W, D, T, H1, H2, PAR = 7.8, 10.0, 0.58, 4.1, 2.9, 0.8
    FX = lambda u: -W / 2 + u
    SHOPW = dict(u0=0.85, u1=4.55, z0=0.75, z1=3.0); DOOR = dict(u0=5.6, u1=6.7, z0=0.0, z1=2.3)
    WINU = [1.6, 4.0, 6.3]; WN = (0.66, 0.95, H1 + 0.8)
    S = shell(W, D, H1, H2, PAR, T, [SHOPW, DOOR] + [dict(u0=c - WN[0] / 2, u1=c + WN[0] / 2, z0=WN[2], z1=WN[2] + WN[1]) for c in WINU],
              sides=[dict(u0=4.6, u1=5.3, z0=WN[2], z1=WN[2] + WN[1])], back=[dict(u0=3.4, u1=4.4, z0=0, z1=2.2)],
              batter_gaps=[(FX(DOOR['u0']) - 0.32, FX(DOOR['u1']) + 0.32)], course_at=H1)
    fy = S['fy']
    # the shop window: a flat arch of wedge stones and a keystone over a dressed sill wall; an iron frame of small panes
    x0, x1, zt = FX(SHOPW['u0']), FX(SHOPW['u1']), SHOPW['z1']; n = 9
    for i in range(n):
        u0 = x0 - 0.25 + (x1 - x0 + 0.5) * i / n; u1 = x0 - 0.25 + (x1 - x0 + 0.5) * (i + 1) / n; key = i == n // 2; m = (u0 + u1) / 2; tilt = (m - (x0 + x1) / 2) * 0.09
        pts = [Vector((u0 + 0.006, fy - (0.09 if key else 0.05), zt)), Vector((u1 - 0.006, fy - (0.09 if key else 0.05), zt)), Vector((u1 + tilt * 0.6 - 0.006, fy - (0.09 if key else 0.05), zt + (0.62 if key else 0.52))), Vector((u0 + tilt * 0.6 + 0.006, fy - (0.09 if key else 0.05), zt + (0.62 if key else 0.52)))]
        prism(pts, T + (0.09 if key else 0.05), (0, -1, 0), 'F_ashlar', 0.02, tag='arch')
    box(((x0 + x1) / 2, fy - 0.08 + T / 2, SHOPW['z0'] - 0.07), (x1 - x0 + 0.5, T + 0.2, 0.16), 'F_ashlar', 0.025, tag='sill')
    box(((x0 + x1) / 2, fy + T - 0.12, (SHOPW['z0'] + zt) / 2), (x1 - x0, 0.03, zt - SHOPW['z0']), 'F_glass', 0.0, tag='glass')
    for k in range(7): box((x0 + (x1 - x0) * k / 6, fy + T - 0.15, (SHOPW['z0'] + zt) / 2), (0.06, 0.06, zt - SHOPW['z0']), 'F_iron', 0.0)
    for z in (SHOPW['z0'] + 0.75, SHOPW['z0'] + 1.5): box(((x0 + x1) / 2, fy + T - 0.15, z), (x1 - x0, 0.05, 0.05), 'F_iron', 0.0)
    # behind the glass: a rack of long guns, a breastplate on its stand
    box(((x0 + x1) / 2, fy + T + 0.6, SHOPW['z0'] + 0.15), (x1 - x0 - 0.2, 0.9, 0.3), 'F_wood', 0.02)
    box(((x0 + x1) / 2 - 0.6, fy + T + 1.0, 1.9), (2.2, 0.08, 2.2), 'F_wood', 0.01)
    for k in range(6):
        gx = x0 + 0.45 + k * 0.32
        pipe((gx, fy + T + 0.92, 0.95), (gx + 0.06, fy + T + 0.92, 2.55), 0.022, 'F_iron', seg=5); box((gx - 0.02, fy + T + 0.9, 1.05), (0.07, 0.06, 0.45), 'F_wood', 0.01)
    bx = x1 - 0.75
    cyl((bx, fy + T + 0.7, 1.05), 0.05, 0.05, 0.6, 'F_wood', seg=6); box((bx, fy + T + 0.7, 0.76), (0.4, 0.4, 0.05), 'F_wood', 0.0)
    cyl((bx, fy + T + 0.7, 1.68), 0.27, 0.22, 0.7, 'F_iron', seg=12, bev=0.01); cyl((bx, fy + T + 0.7, 2.1), 0.12, 0.1, 0.18, 'F_iron', seg=8)
    # an iron shutter propped up on two stays: it closes the window at night and keeps the rain off the window by day
    sz0 = zt + 0.62; L = 1.35; ang = math.radians(28)
    pts = [Vector((x0 - 0.1, fy - 0.06, sz0)), Vector((x1 + 0.1, fy - 0.06, sz0)), Vector((x1 + 0.1, fy - 0.06 - L * math.cos(ang), sz0 - L * math.sin(ang))), Vector((x0 - 0.1, fy - 0.06 - L * math.cos(ang), sz0 - L * math.sin(ang)))]
    prism(pts, 0.04, (0, 0, 1), 'F_iron', 0.006, tag='awning')
    for k in range(3): pipe(((x0 + x1) / 2 + (k - 1) * (x1 - x0) / 2.4, fy - 0.06, sz0 - 0.03), ((x0 + x1) / 2 + (k - 1) * (x1 - x0) / 2.4, fy - 0.06 - L * math.cos(ang), sz0 - L * math.sin(ang) - 0.03), 0.02, 'F_iron', seg=4)
    for k in range(8): rivet((x0 + k * (x1 - x0) / 7, fy - 0.06 - L * math.cos(ang) - 0.01, sz0 - L * math.sin(ang) - 0.01), (0, -1, 0))
    for x in (x0 + 0.1, x1 - 0.1):
        pipe((x, fy - 0.03, zt - 0.4), (x, fy - 0.06 - L * math.cos(ang) + 0.05, sz0 - L * math.sin(ang) - 0.02), 0.025, 'F_iron', seg=5)
        cyl((x, fy - 0.03, zt - 0.4), 0.05, 0.05, 0.06, 'F_iron', seg=6, axis='Y')
    # the door: studded, in a dressed frame, with a step
    dx0, dx1 = FX(DOOR['u0']), FX(DOOR['u1'])
    box(((dx0 + dx1) / 2, fy + 0.28, DOOR['z1'] / 2), (dx1 - dx0, 0.08, DOOR['z1']), 'F_wood', 0.01, tag='door')
    for z in (0.45, 1.85): box(((dx0 + dx1) / 2 - 0.12, fy + 0.235, z), (0.85, 0.02, 0.09), 'F_iron', 0.005)
    for i in range(3):
        for j in range(5): rivet((dx0 + 0.2 + i * (dx1 - dx0 - 0.4) / 2, fy + 0.235, 0.35 + j * 0.42), (0, -1, 0))
    box(((dx0 + dx1) / 2, fy - 0.04, DOOR['z1'] + 0.22), (dx1 - dx0 + 0.6, T + 0.08, 0.44), 'F_ashlar', 0.035, tag='lintel')
    for x in (dx0 - 0.16, dx1 + 0.16):
        z = 0.6
        while z < DOOR['z1'] - 0.05:
            hh = min(0.42, DOOR['z1'] - z); box((x, fy - 0.035 + T / 2, z + hh / 2), (0.32, T + 0.07, hh - 0.015), 'F_ashlar', 0.03, tag='jamb'); z += hh
    box(((dx0 + dx1) / 2, fy + 0.05, 0.07), (dx1 - dx0 + 0.4, 0.5, 0.14), 'F_ashlar', 0.03)
    for c in WINU: iron_window(FX(c), fy, (0, -1, 0), (1, 0, 0), WN[0], WN[1], WN[2])
    iron_window(W / 2, fy + 4.95, (1, 0, 0), (0, 1, 0), 0.7, WN[1], WN[2]); iron_window(-W / 2, D / 2 - 4.95, (-1, 0, 0), (0, -1, 0), 0.7, WN[1], WN[2])
    # the sign: crossed muskets on a riveted plate, hung from a wrought bracket
    sxp = dx1 + 0.55
    box((sxp, fy - 0.5, 3.45), (0.06, 1.0, 0.06), 'F_iron', 0.0); pipe((sxp, fy - 0.02, 3.0), (sxp, fy - 0.8, 3.45), 0.022, 'F_iron', seg=6)
    for y in (fy - 0.3, fy - 0.8): pipe((sxp, y, 3.42), (sxp, y, 3.22), 0.012, 'F_iron', seg=4)
    box((sxp, fy - 0.55, 2.9), (0.05, 0.75, 0.6), 'F_rust', 0.01, tag='sign')
    for s2 in (-1, 1): pipe((sxp - 0.04, fy - 0.55 - s2 * 0.3, 2.68), (sxp - 0.04, fy - 0.55 + s2 * 0.3, 3.12), 0.02, 'F_iron', seg=5)
    # a modest stack for the shop's hearth, at the back
    sx, sy, SH = W / 2 - 1.2, D / 2 - 1.2, S['top'] + 4.2
    box((sx, sy, (S['rz0'] + SH) / 2), (1.1, 1.1, SH - S['rz0']), 'F_brick', 0.02, tag='stack')
    for k, g in enumerate((0.05, 0.1)): box((sx, sy, SH + 0.08 + k * 0.15), (1.1 + 2 * g, 1.1 + 2 * g, 0.15), 'F_brick', 0.012, tag='stack')
    box((sx, sy, SH + 0.38), (0.8, 0.8, 0.05), 'F_glass', 0.0)
    cog(FX(5.95), fy, H1 + 1.25, 0.34, teeth=10)
    SOOT += [(sx, sy, S['rz0'] + 2, SH + 0.6, 0.9, 0.7)]
    LIGHT_SPOTS += [((x0 + x1) / 2, fy + T + 1.2, 2.2, 120)]
    PLOT = (W + 0.8, D + 0.8); VENTS = [(sx, SH + 0.5, sy)]

# ================================================================ the smelter
if BUILDING == 'smelter':
    NAME = 'FerrinSmelter'
    W, D, T, H1, H2, PAR = 12.4, 12.4, 0.7, 6.2, 0.0, 0.9
    FX = lambda u: -W / 2 + u
    ARCH = dict(u0=3.6, u1=8.8, z0=0.0, z1=3.1, rise=1.1)
    S = shell(W, D, H1, H2, PAR, T, [ARCH, dict(u0=1.3, u1=2.0, z0=3.4, z1=4.9), dict(u0=10.4, u1=11.1, z0=3.4, z1=4.9)],
              sides=[dict(u0=3.0, u1=3.7, z0=3.4, z1=4.9), dict(u0=8.6, u1=9.3, z0=3.4, z1=4.9)], back=[],
              batter_gaps=[(FX(ARCH['u0']) - 0.75, FX(ARCH['u1']) + 0.75)])
    fy = S['fy']
    c = (ARCH['u1'] - ARCH['u0']) / 2; h = ARCH['rise']; R = (c * c + h * h) / (2 * h); cu = FX(ARCH['u0']) + c; cz = ARCH['z1'] + h - R
    a0 = math.atan2(ARCH['z1'] - cz, -c); a1 = math.atan2(ARCH['z1'] - cz, c)
    for i in range(9):
        t0 = a0 + (a1 - a0) * i / 9; t1 = a0 + (a1 - a0) * (i + 1) / 9; key = i == 4; r0, r1 = R, R + (0.95 if key else 0.75)
        pts = [Vector((cu + math.cos(t) * r, fy - (0.1 if key else 0.06), cz + math.sin(t) * r)) for (t, r) in [(t0 + 0.004, r0), (t1 - 0.004, r0), (t1 - 0.004, r1), (t0 + 0.004, r1)]]
        prism(pts, T + (0.1 if key else 0.06) - 0.02, (0, -1, 0), 'F_ashlar', 0.025, tag='arch')
    for side in (0, 1):
        z = 0.6; k = 0
        while z < ARCH['z1'] - 0.05:
            hh = min(0.45, ARCH['z1'] - z); Lb = 0.7 if k % 2 == 0 else 0.45; x = FX(ARCH['u0']) - Lb / 2 if side == 0 else FX(ARCH['u1']) + Lb / 2
            box((x, fy - 0.035 + T / 2, z + hh / 2), (Lb, T + 0.07, hh - 0.015), 'F_ashlar', 0.03, tag='jamb'); z += hh; k += 1
    # the iron doors, swung open against the wall
    for s2 in (-1, 1):
        dw = c; hx = cu + s2 * c; ang = math.radians(100); d = Vector((-s2 * math.cos(ang), -math.sin(ang), 0)) * -1
        ctr = Vector((hx, fy - 0.05, 0)) + Vector((s2 * math.cos(math.radians(80)) * 0, 0, 0))
        box((hx + s2 * 0.12, fy - dw / 2 - 0.05, ARCH['z1'] / 2 + 0.05), (0.08, dw, ARCH['z1'] - 0.1), 'F_iron', 0.008, tag='door')
        for z in (0.5, 1.5, 2.5): box((hx + s2 * 0.17, fy - dw / 2 - 0.05, z), (0.03, dw - 0.1, 0.12), 'F_rust', 0.004)
        for z in (0.5, 1.5, 2.5):
            for k in range(5): rivet((hx + s2 * 0.18, fy - 0.3 - k * (dw - 0.6) / 4, z), (s2, 0, 0))
    # inside: a dark hall, the crucible glowing in its furnace, tongs and moulds on the floor
    by0, by1 = fy + T, fy + T + 5.5; bx0, bx1 = FX(ARCH['u0']) - 0.6, FX(ARCH['u1']) + 0.6; top = ARCH['z1'] + ARCH['rise'] + 1.2
    box(((bx0 + bx1) / 2, (by0 + by1) / 2, 0.05), (bx1 - bx0, by1 - by0, 0.1), 'F_ashlar', 0.0, tag='inside')
    box((bx0 - 0.1, (by0 + by1) / 2, top / 2), (0.2, by1 - by0, top), 'F_stone', 0.0, tag='inside'); box((bx1 + 0.1, (by0 + by1) / 2, top / 2), (0.2, by1 - by0, top), 'F_stone', 0.0, tag='inside')
    box(((bx0 + bx1) / 2, by1 + 0.1, top / 2), (bx1 - bx0 + 0.4, 0.2, top), 'F_stone', 0.0, tag='inside')
    box(((bx0 + bx1) / 2, (by0 + by1) / 2, top + 0.1), (bx1 - bx0 + 0.4, by1 - by0, 0.2), 'F_wood', 0.0, tag='inside')
    fx0 = cu; fyc = by1 - 1.6
    cyl((fx0, fyc, 1.2), 1.5, 1.7, 2.4, 'F_brick', seg=16, bev=0.02, tag='furnace')
    cyl((fx0, fyc, 2.55), 1.2, 1.5, 0.3, 'F_iron', seg=16)
    box((fx0, fyc - 1.55, 0.75), (0.6, 0.3, 0.6), 'F_glow', 0.0, tag='glow')                       # the tap hole
    box((fx0, fyc - 2.2, 0.15), (0.35, 1.3, 0.12), 'F_iron', 0.01)                                    # the runner
    for k in range(4): box((fx0 - 1.4 + k * 0.95, fyc - 3.2, 0.2), (0.6, 0.35, 0.3), 'F_iron', 0.01) # ingot moulds
    box((fx0 - 1.4 + 0.95, fyc - 3.2, 0.36), (0.45, 0.22, 0.04), 'F_glow', 0.0, tag='glow')
    cyl((fx0, fyc, (2.7 + top) / 2), 0.45, 0.45, top - 2.7, 'F_iron', seg=10)
    # the furnace stack: round, tall, banded with iron, outside at the back
    sx, sy, SH = W / 2 - 2.1, D / 2 - 2.1, 19.0                                                          # inside the back corner, through the roof
    cyl((sx, sy, SH / 2), 1.5, 1.15, SH, 'F_brick', seg=20, bev=0.02, tag='stack')
    for z in (2.0, 5.0, 8.0, 11.0, 14.0, 17.0): cyl((sx, sy, z), 1.5 - z * 0.0185 + 0.04, 1.5 - z * 0.0185 + 0.04, 0.12, 'F_iron', seg=20, tag='stack')
    cyl((sx, sy, SH + 0.2), 1.35, 1.35, 0.4, 'F_brick', seg=20, tag='stack'); cyl((sx, sy, SH + 0.42), 1.05, 1.05, 0.05, 'F_glass', seg=16)
    pipe((sx - 0.6, sy - 0.5, 3.0), (cu, fyc + 0.6, 3.0), 0.35, 'F_iron', seg=12)                    # the flue from the furnace to the stack
    # the ore hopper on the roof and its chute down into the hall
    hx2, hy2 = FX(3.0), fy + 4.5; hz = S['rz0'] + 0.6
    for (x, y) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]: box((hx2 + x * 0.9, hy2 + y * 0.9, hz + 0.8), (0.15, 0.15, 1.6), 'F_iron', 0.0)
    bm = bmesh.new(); lo = [(hx2 - 0.45, hy2 - 0.45), (hx2 + 0.45, hy2 - 0.45), (hx2 + 0.45, hy2 + 0.45), (hx2 - 0.45, hy2 + 0.45)]; hi = [(hx2 - 1.2, hy2 - 1.2), (hx2 + 1.2, hy2 - 1.2), (hx2 + 1.2, hy2 + 1.2), (hx2 - 1.2, hy2 + 1.2)]
    vl = [bm.verts.new((x, y, hz + 1.5)) for x, y in lo]; vh = [bm.verts.new((x, y, hz + 3.0)) for x, y in hi]
    for i in range(4): bm.faces.new([vl[i], vl[(i + 1) % 4], vh[(i + 1) % 4], vh[i]])
    bm.faces.new(vl); bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, 'F_rust', 'hopper')
    box((hx2, hy2, hz + 2.95), (2.3, 2.3, 0.1), 'F_stone', 0.0)                                       # heaped ore
    pipe((hx2, hy2, hz + 1.5), (hx2, hy2, S['rz0'] - 0.2), 0.32, 'F_rust', seg=8)
    # a louvred ventilator on the ridge
    vx = FX(7.5)
    box((vx, 0, S['rz0'] + 1.3), (2.2, 1.6, 0.9), 'F_iron', 0.01, tag='vent')
    for k in range(4): box((vx, -0.82, S['rz0'] + 1.0 + k * 0.2), (2.0, 0.08, 0.06), 'F_iron', 0.0, rx=0.5)
    prism([Vector((vx - 1.3, -1.0, S['rz0'] + 1.75)), Vector((vx + 1.3, -1.0, S['rz0'] + 1.75)), Vector((vx + 1.3, 0, S['rz0'] + 2.15)), Vector((vx - 1.3, 0, S['rz0'] + 2.15))], 0.04, (0, 0, 1), 'F_iron', 0.0)
    prism([Vector((vx - 1.3, 0, S['rz0'] + 2.15)), Vector((vx + 1.3, 0, S['rz0'] + 2.15)), Vector((vx + 1.3, 1.0, S['rz0'] + 1.75)), Vector((vx - 1.3, 1.0, S['rz0'] + 1.75))], 0.04, (0, 0, 1), 'F_iron', 0.0)
    for (u, n_, a_) in [(1.65, (0, -1, 0), (1, 0, 0)), (10.75, (0, -1, 0), (1, 0, 0))]: iron_window(FX(u), fy, n_, a_, 0.7, 1.5, 3.4, shutters=False)
    cog(cu, fy, ARCH['z1'] + ARCH['rise'] + 1.45, 0.42, teeth=12)
    SOOT += [(cu, fy, ARCH['z1'], S['HT'] + 0.5, c + 1.0, 0.9), (sx, sy, 10, SH + 0.5, 1.8, 0.85), (vx, 0, S['rz0'], S['rz0'] + 2.5, 1.8, 0.6)]
    LIGHT_SPOTS += [(fx0, fyc - 2.3, 1.0, 900)]
    PLOT = (W + 0.8, D + 0.8); VENTS = [(sx, SH + 0.6, sy), (vx, S['rz0'] + 2.3, 0)]

# ================================================================ Ostrak's shrine
if BUILDING == 'shrine':
    NAME = 'FerrinShrine'
    W, D, T, H1, H2, PAR = 6.0, 6.6, 0.75, 4.6, 0.0, 0.7
    FX = lambda u: -W / 2 + u
    DOOR = dict(u0=2.2, u1=3.8, z0=0.0, z1=2.4, rise=0.8)
    S = shell(W, D, H1, H2, PAR, T, [DOOR], sides=[dict(u0=3.0, u1=3.6, z0=2.4, z1=3.6)], back=[], batter_gaps=[(-W / 2 + 0.5, W / 2 - 0.5)])
    fy = S['fy']
    c = (DOOR['u1'] - DOOR['u0']) / 2; R = c; cu = FX(DOOR['u0']) + c; cz = DOOR['z1']                # a full round arch
    for i in range(7):
        t0 = math.pi - math.pi * i / 7; t1 = math.pi - math.pi * (i + 1) / 7; key = i == 3; r1 = R + (0.6 if key else 0.48)
        pts = [Vector((cu + math.cos(t) * r, fy - (0.1 if key else 0.06), cz + math.sin(t) * r)) for (t, r) in [(t0 - 0.004, R), (t1 + 0.004, R), (t1 + 0.004, r1), (t0 - 0.004, r1)]]
        prism(pts, T + 0.06, (0, -1, 0), 'F_ashlar', 0.02, tag='arch')
    for side in (0, 1):
        z = 0.6; k = 0
        while z < DOOR['z1'] - 0.05:
            hh = min(0.45, DOOR['z1'] - z); Lb = 0.55 if k % 2 == 0 else 0.35; x = FX(DOOR['u0']) - Lb / 2 if side == 0 else FX(DOOR['u1']) + Lb / 2
            box((x, fy - 0.035 + T / 2, z + hh / 2), (Lb, T + 0.07, hh - 0.015), 'F_ashlar', 0.03, tag='jamb'); z += hh; k += 1
    for (cx, cy) in [(-W / 2, fy), (W / 2, fy), (-W / 2, D / 2), (W / 2, D / 2)]:                      # sloping basalt buttresses at the corners, dressed caps
        for (nx, ny) in [(0, -1 if cy < 0 else 1), (1 if cx > 0 else -1, 0)]:
            n_ = Vector((nx, ny, 0)); sg = lambda v: 1 if v > 0 else -1
            if nx == 0: ax_ = Vector((1, 0, 0)); base = Vector((cx - sg(cx) * 0.55, cy, 0))      # on the front or back face, just in from the corner
            else: ax_ = Vector((0, 1, 0)); base = Vector((cx, cy - sg(cy) * 0.55, 0))
            w2 = 0.32; hb = 3.6
            P = [base - ax_ * w2, base + ax_ * w2, base + ax_ * w2 + Vector((0, 0, hb)) , base - ax_ * w2 + Vector((0, 0, hb))]
            bm = bmesh.new(); f = [bm.verts.new(q) for q in P]; o = [bm.verts.new(q + n_ * (0.85 if q.z < 0.1 else 0.18)) for q in P]
            bm.faces.new(f); bm.faces.new(list(reversed(o)))
            for k in range(4): bm.faces.new([f[k], o[k], o[(k + 1) % 4], f[(k + 1) % 4]])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bevel_all(bm, 0.03); add_bm(bm, 'F_stone', 'buttress')
            box(base + n_ * 0.12 + Vector((0, 0, hb + 0.08)), tuple(abs(v) for v in (ax_ * (2 * w2 + 0.12) + n_ * 0.36 + Vector((0, 0, 0.16)))), 'F_ashlar', 0.025, tag='buttress')
    for k in range(3): box((cu, fy - 0.35 - k * 0.38, 0.09 + k * 0.0), (2.6 - k * 0.0 + 0.4 * (2 - k), 0.4 + 0.38 * (2 - k) * 0, 0.18 * (3 - k)), 'F_ashlar', 0.03, tag='steps') if False else None
    for k in range(3): box((cu, fy - 0.3 - (2 - k) * 0.38, 0.09 * (k + 1)), (2.2 + 0.3 * (2 - k), 0.38 * (3 - k) + 0.02, 0.18 * (k + 1)), 'F_ashlar', 0.03, tag='steps')
    # the open iron gate: bars and a band, folded back inside the reveal
    for s2 in (-1, 1):
        for k in range(4): box((cu + s2 * (c - 0.05), fy + 0.25 + k * 0.12, 1.2), (0.03, 0.03, 2.3), 'F_iron', 0.0)
        for z in (0.4, 2.0): box((cu + s2 * (c - 0.05), fy + 0.43, z), (0.03, 0.45, 0.05), 'F_iron', 0.0)
    # inside: the anvil altar on a stepped plinth, candles, an ever-glowing ember bowl
    iy = fy + T + 2.2
    box((cu, iy, 0.3), (2.0, 1.4, 0.6), 'F_ashlar', 0.03, tag='altar'); box((cu, iy, 0.75), (1.6, 1.0, 0.3), 'F_ashlar', 0.03, tag='altar')
    box((cu, iy, 1.05), (0.9, 0.36, 0.3), 'F_iron', 0.02); box((cu - 0.15, iy, 1.25), (1.1, 0.42, 0.14), 'F_iron', 0.02)
    prism([Vector((cu + 0.4, iy - 0.16, 1.3)), Vector((cu + 0.8, iy - 0.08, 1.27)), Vector((cu + 0.8, iy + 0.08, 1.27)), Vector((cu + 0.4, iy + 0.16, 1.3))], 0.1, (0, 0, 1), 'F_iron', 0.01)
    for k in range(6):
        a = k / 6 * math.pi * 2; x = cu + math.cos(a) * 0.95; y = iy + math.sin(a) * 0.62
        cyl((x, y, 0.72), 0.04, 0.04, 0.24, 'F_wood', seg=6); box((x, y, 0.88), (0.05, 0.05, 0.08), 'F_glow', 0.0, tag='glow')
    cyl((cu, iy + 1.1, 0.6), 0.35, 0.25, 0.4, 'F_iron', seg=10); box((cu, iy + 1.1, 0.82), (0.45, 0.45, 0.06), 'F_glow', 0.0, tag='glow')
    # the cog carved over the door; the brazier on the roof whose fire never goes out
    cog(cu, fy, DOOR['z1'] + R + 1.05, 0.38, teeth=12)
    bzx, bzy, bzz = 0, 0, S['rz0'] + 1.4
    box((bzx, bzy, S['rz0'] + 0.45), (0.8, 0.8, 1.1), 'F_ashlar', 0.03, tag='pedestal')
    for k in range(3):
        a = k / 3 * math.pi * 2; pipe((bzx + math.cos(a) * 0.6, bzy + math.sin(a) * 0.6, bzz - 0.6), (bzx + math.cos(a) * 0.3, bzy + math.sin(a) * 0.3, bzz + 0.5), 0.05, 'F_iron', seg=5)
    cyl((bzx, bzy, bzz + 0.6), 0.55, 0.35, 0.35, 'F_iron', seg=14, bev=0.01, tag='brazier'); box((bzx, bzy, bzz + 0.8), (0.6, 0.6, 0.1), 'F_glow', 0.0, tag='glow')
    SOOT += [(bzx, bzy, bzz - 0.5, bzz + 1.5, 1.2, 0.6), (cu, fy, DOOR['z1'] - 0.5, S['HT'], c + 0.5, 0.45)]
    LIGHT_SPOTS += [(cu, iy, 1.2, 150), (bzx, bzy, bzz + 1.2, 260)]
    PLOT = (W + 1.6, D + 1.6); VENTS = [(bzx, bzz + 1.2, bzy)]

# ================================================================ the narrow house: a smith's family home squeezed into a gap
if BUILDING == 'narrow':
    NAME = 'FerrinNarrow'
    W, D, T, H1, H2, PAR = 5.6, 9.6, 0.55, 3.8, 2.9, 0.8
    FX = lambda u: -W / 2 + u
    DOOR = dict(u0=1.0, u1=2.05, z0=0.0, z1=2.25); WINL = dict(u0=3.25, u1=4.55, z0=0.9, z1=2.6)
    S = shell(W, D, H1, H2, PAR, T, [DOOR, WINL, dict(u0=1.0, u1=1.66, z0=H1 + 0.8, z1=H1 + 1.75), dict(u0=3.5, u1=4.16, z0=H1 + 0.8, z1=H1 + 1.75)],
              sides=[], back=[dict(u0=2.3, u1=3.3, z0=0, z1=2.2)], batter_gaps=[(FX(DOOR['u0']) - 0.3, FX(DOOR['u1']) + 0.3)], course_at=H1)
    fy = S['fy']
    dx0, dx1 = FX(DOOR['u0']), FX(DOOR['u1'])
    box(((dx0 + dx1) / 2, fy + 0.28, DOOR['z1'] / 2), (dx1 - dx0, 0.08, DOOR['z1']), 'F_wood', 0.01, tag='door')
    for z in (0.45, 1.8): box(((dx0 + dx1) / 2 - 0.12, fy + 0.235, z), (0.85, 0.02, 0.09), 'F_iron', 0.005)
    for j in range(4): rivet(((dx0 + dx1) / 2, fy + 0.235, 0.4 + j * 0.45), (0, -1, 0))
    box(((dx0 + dx1) / 2, fy - 0.04, DOOR['z1'] + 0.2), (dx1 - dx0 + 0.55, T + 0.08, 0.4), 'F_ashlar', 0.035, tag='lintel')
    box(((dx0 + dx1) / 2, fy + 0.05, 0.07), (dx1 - dx0 + 0.4, 0.5, 0.14), 'F_ashlar', 0.03)
    wx0, wx1 = FX(WINL['u0']), FX(WINL['u1'])                                                          # the parlour window: a stone mullion, iron bars, shutters
    box(((wx0 + wx1) / 2, fy - 0.04, WINL['z1'] + 0.2), (wx1 - wx0 + 0.5, T + 0.08, 0.4), 'F_ashlar', 0.035, tag='lintel')
    box(((wx0 + wx1) / 2, fy - 0.06 + 0.17, WINL['z0'] - 0.07), (wx1 - wx0 + 0.4, 0.36, 0.14), 'F_ashlar', 0.025, tag='sill')
    box(((wx0 + wx1) / 2, fy + 0.25, (WINL['z0'] + WINL['z1']) / 2), (0.16, T - 0.1, WINL['z1'] - WINL['z0']), 'F_ashlar', 0.02)
    box(((wx0 + wx1) / 2, fy + 0.36, (WINL['z0'] + WINL['z1']) / 2), (wx1 - wx0, 0.03, WINL['z1'] - WINL['z0']), 'F_glass', 0.0, tag='glass')
    for k in range(5): box((wx0 + 0.12 + k * (wx1 - wx0 - 0.24) / 4, fy + 0.12, (WINL['z0'] + WINL['z1']) / 2), (0.035, 0.035, WINL['z1'] - WINL['z0']), 'F_iron', 0.0)
    for c in (1.33, 3.83): iron_window(FX(c), fy, (0, -1, 0), (1, 0, 0), 0.66, 0.95, H1 + 0.8)
    for x in (wx0 - 0.35, wx1 + 0.35):                                                                 # parlour shutters, iron-clad, thrown back
        box((x + (0.08 if x < wx0 else -0.08), fy - 0.06, (WINL['z0'] + WINL['z1']) / 2), (0.62, 0.05, WINL['z1'] - WINL['z0'] + 0.04), 'F_iron', 0.008, rz=(0.3 if x < wx0 else -0.3), tag='shutter')
    pipe((W / 2 - 0.25, fy + 0.3, S['rz0'] + 0.1), (W / 2 - 0.25, fy - 0.3, S['rz0'] + 0.1), 0.06, 'F_iron', seg=8)   # a spout and its downpipe
    pipe((W / 2 - 0.25, fy - 0.3, S['rz0']), (W / 2 - 0.25, fy - 0.3, 0.3), 0.055, 'F_iron', seg=8, tag='downpipe')
    for z in (1.2, 3.0, 5.0): box((W / 2 - 0.25, fy - 0.18, z), (0.16, 0.24, 0.05), 'F_iron', 0.004)
    sx, sy, SH = -W / 2 + 1.1, D / 2 - 1.1, S['top'] + 3.6
    box((sx, sy, (S['rz0'] + SH) / 2), (1.0, 1.0, SH - S['rz0']), 'F_brick', 0.02, tag='stack')
    box((sx, sy, SH + 0.08), (1.14, 1.14, 0.15), 'F_brick', 0.012, tag='stack'); box((sx, sy, SH + 0.17), (0.7, 0.7, 0.05), 'F_glass', 0.0)
    SOOT += [(sx, sy, S['rz0'] + 1.5, SH + 0.5, 0.8, 0.7)]
    PLOT = (W + 0.8, D + 0.8); VENTS = [(sx, SH + 0.4, sy)]


def plank_door(dx0, dx1, fy, z1, T, ajar=0.0, lintel=True):   # a boarded door, iron straps and rivets, a dressed lintel and step
    box(((dx0 + dx1) / 2, fy + 0.28, z1 / 2), (dx1 - dx0, 0.08, z1), 'F_wood', 0.01, tag='door')
    for z in (0.45, z1 - 0.45): box(((dx0 + dx1) / 2 - 0.1, fy + 0.235, z), (dx1 - dx0 - 0.2, 0.02, 0.09), 'F_iron', 0.005)
    for j in range(4): rivet(((dx0 + dx1) / 2, fy + 0.235, 0.4 + j * (z1 - 0.8) / 3), (0, -1, 0))
    if lintel: box(((dx0 + dx1) / 2, fy - 0.04, z1 + 0.2), (dx1 - dx0 + 0.55, T + 0.08, 0.4), 'F_ashlar', 0.035, tag='lintel')
    box(((dx0 + dx1) / 2, fy + 0.05, 0.07), (dx1 - dx0 + 0.4, 0.5, 0.14), 'F_ashlar', 0.03)

def stack(sx, sy, z0, SH, w=1.0):
    box((sx, sy, (z0 + SH) / 2), (w, w, SH - z0), 'F_brick', 0.02, tag='stack')
    box((sx, sy, SH + 0.08), (w + 0.14, w + 0.14, 0.15), 'F_brick', 0.012, tag='stack'); box((sx, sy, SH + 0.17), (w * 0.7, w * 0.7, 0.05), 'F_glass', 0.0)

# ================================================================ the toolmaker's house: three bays, a hooded door, an oriel over it
if BUILDING == 'toolmaker':
    NAME = 'FerrinToolmaker'
    W, D, T, H1, H2, PAR = 7.4, 9.0, 0.58, 3.9, 3.0, 0.8
    FX = lambda u: -W / 2 + u
    DOOR = dict(u0=3.15, u1=4.25, z0=0.0, z1=2.3)
    WG = [(1.45, 0.9, 1.25, 0.95), (5.95, 0.9, 1.25, 0.95)]                     # ground windows: centre, width, height, sill
    WU = [(1.45, 0.66, 0.95, H1 + 0.8), (5.95, 0.66, 0.95, H1 + 0.8)]
    op = lambda c, w, h, z: dict(u0=c - w / 2, u1=c + w / 2, z0=z, z1=z + h)
    S = shell(W, D, H1, H2, PAR, T, [DOOR] + [op(*w) for w in WG + WU], sides=[dict(u0=4.0, u1=4.66, z0=H1 + 0.8, z1=H1 + 1.75)], back=[dict(u0=3.2, u1=4.2, z0=0, z1=2.2)],
              batter_gaps=[(FX(DOOR['u0']) - 0.3, FX(DOOR['u1']) + 0.3)], course_at=H1, lsides=[])
    fy = S['fy']; dx0, dx1 = FX(DOOR['u0']), FX(DOOR['u1']); dc = (dx0 + dx1) / 2
    plank_door(dx0, dx1, fy, DOOR['z1'], T)
    box((dc, fy - 0.36, DOOR['z1'] + 0.62), (dx1 - dx0 + 1.0, 0.78, 0.16), 'F_ashlar', 0.03, tag='hood')            # a stone hood over the door on iron brackets
    for sx2 in (-1, 1):
        x = dc + sx2 * (dx1 - dx0 + 0.7) / 2
        pipe((x, fy - 0.02, DOOR['z1'] - 0.05), (x, fy - 0.68, DOOR['z1'] + 0.54), 0.03, 'F_iron', seg=5); pipe((x, fy - 0.02, DOOR['z1'] + 0.54), (x, fy - 0.68, DOOR['z1'] + 0.54), 0.03, 'F_iron', seg=5)
    for (c, w, h, z) in WG: iron_window(FX(c), fy, (0, -1, 0), (1, 0, 0), w, h, z)
    for (c, w, h, z) in WU: iron_window(FX(c), fy, (0, -1, 0), (1, 0, 0), w, h, z)
    # the oriel: a stone bay over the door, carried on stepped corbels, glazed on three sides, an iron cap
    ow, od, oz0, oz1 = 2.3, 0.72, H1 + 0.35, H1 + 2.45
    for k, (dz, out) in enumerate([(0.0, 0.25), (0.22, 0.5), (0.44, od)]):
        box((dc, fy - out / 2, oz0 - 0.66 + dz), (ow * (0.55 + 0.22 * k), out, 0.22), 'F_ashlar', 0.025, tag='corbel')
    box((dc, fy - od / 2, oz0 + 0.12), (ow + 0.1, od + 0.06, 0.24), 'F_ashlar', 0.03)
    for sx2 in (-1, 1): box((dc + sx2 * (ow / 2 - 0.14), fy - od / 2, (oz0 + oz1) / 2), (0.28, od, oz1 - oz0), 'F_ashlar', 0.025)
    box((dc, fy - od + 0.06, (oz0 + 0.24 + oz1 - 0.2) / 2), (ow - 0.56, 0.03, oz1 - oz0 - 0.44), 'F_glass', 0.0, tag='glass')
    for k in range(4): box((dc - (ow - 0.56) / 2 + k * (ow - 0.56) / 3, fy - od + 0.02, (oz0 + oz1) / 2), (0.05, 0.05, oz1 - oz0 - 0.44), 'F_iron', 0.0)
    box((dc, fy - od + 0.02, oz0 + (oz1 - oz0) * 0.62), (ow - 0.56, 0.04, 0.04), 'F_iron', 0.0)
    box((dc, fy - od / 2, oz1 - 0.08), (ow + 0.1, od + 0.06, 0.18), 'F_ashlar', 0.03)
    prism([Vector((dc - ow / 2 - 0.12, fy - od - 0.14, oz1)), Vector((dc + ow / 2 + 0.12, fy - od - 0.14, oz1)), Vector((dc + ow / 2 + 0.12, fy, oz1 + 0.55)), Vector((dc - ow / 2 - 0.12, fy, oz1 + 0.55))], 0.05, (0, 0, 1), 'F_iron', 0.0, tag='roof')
    # the chimney breast on the gable: stone to the parapet, brick above
    bx = W / 2 + 0.36; by = 1.2; SH = S['top'] + 3.3
    box((bx, by, (S['HT'] + 0.3) / 2), (0.72, 1.3, S['HT'] + 0.3), 'F_stone', 0.02)
    for z in (H1, S['HT'] + 0.15): box((bx, by, z), (0.84, 1.42, 0.2), 'F_ashlar', 0.03)
    stack(bx, by, S['HT'] + 0.25, SH, 0.95)
    pipe((-W / 2 + 0.25, fy + 0.3, S['rz0'] + 0.1), (-W / 2 + 0.25, fy - 0.3, S['rz0'] + 0.1), 0.06, 'F_iron', seg=8)
    pipe((-W / 2 + 0.25, fy - 0.3, S['rz0']), (-W / 2 + 0.25, fy - 0.3, 0.3), 0.055, 'F_iron', seg=8, tag='downpipe')
    SOOT += [(bx, by, S['HT'], SH + 0.5, 0.8, 0.7)]
    PLOT = (W + 1.6, D + 0.8); VENTS = [(bx, SH + 0.4, by)]

# ================================================================ the stair house: a workshop below, the family above, up a stone stair on the side
if BUILDING == 'stair':
    NAME = 'FerrinStair'
    W, D, T, H1, H2, PAR = 6.4, 9.4, 0.56, 3.4, 3.0, 0.8
    FX = lambda u: -W / 2 + u
    WD = dict(u0=0.7, u1=3.2, z0=0.0, z1=2.6)                                  # the workshop's wide doors
    WIN = dict(u0=4.1, u1=5.4, z0=0.9, z1=2.4)
    SD = dict(u0=4.6, u1=5.6, z0=H1 + 0.05, z1=H1 + 2.25)                       # the house door, up the stair on the right-hand side
    S = shell(W, D, H1, H2, PAR, T, [WD, WIN, dict(u0=1.6, u1=2.26, z0=H1 + 0.8, z1=H1 + 1.75), dict(u0=4.4, u1=5.06, z0=H1 + 0.8, z1=H1 + 1.75)],
              sides=[SD, dict(u0=7.4, u1=8.06, z0=H1 + 0.8, z1=H1 + 1.75)], back=[dict(u0=2.7, u1=3.7, z0=0, z1=2.2)],
              batter_gaps=[(FX(WD['u0']) - 0.3, FX(WD['u1']) + 0.3)], course_at=H1, lsides=[])
    fy = S['fy']; x0, x1 = FX(WD['u0']), FX(WD['u1'])
    box(((x0 + x1) / 2, fy - 0.06, WD['z1'] + 0.17), (x1 - x0 + 0.6, T + 0.14, 0.34), 'F_wood', 0.02, tag='lintel')   # a great timber lintel, iron-strapped
    for k in (0.25, 0.75): box((x0 + (x1 - x0) * k, fy - 0.24, WD['z1'] + 0.17), (0.08, 0.02, 0.38), 'F_iron', 0.0)
    hw = (x1 - x0) / 2
    for leaf, ang in ((-1, 0.0), (1, 0.55)):                                    # two leaves, one standing open
        hx = x0 if leaf < 0 else x1; d = Vector((-leaf * math.cos(ang), -math.sin(ang), 0)); c = Vector((hx, fy + 0.26, 0)) + d * (hw / 2)
        box((c.x, c.y, WD['z1'] / 2), (hw - 0.02, 0.08, WD['z1'] - 0.02), 'F_wood', 0.01, rz=math.atan2(d.y, d.x), tag='door')
        for z in (0.4, 1.3, 2.2):
            c2 = Vector((hx, fy + 0.21, z)) + d * (hw / 2 - 0.05); box(c2, (hw - 0.2, 0.025, 0.08), 'F_iron', 0.004, rz=math.atan2(d.y, d.x))
    box(((x0 + x1) / 2, fy + 0.6, 0.02), (x1 - x0, 1.2, 0.04), 'F_ashlar', 0.01)
    wx0, wx1 = FX(WIN['u0']), FX(WIN['u1'])
    box(((wx0 + wx1) / 2, fy - 0.04, WIN['z1'] + 0.2), (wx1 - wx0 + 0.5, T + 0.08, 0.4), 'F_ashlar', 0.035, tag='lintel')
    box(((wx0 + wx1) / 2, fy + 0.11, WIN['z0'] - 0.07), (wx1 - wx0 + 0.4, 0.36, 0.14), 'F_ashlar', 0.025, tag='sill')
    box(((wx0 + wx1) / 2, fy + 0.36, (WIN['z0'] + WIN['z1']) / 2), (wx1 - wx0, 0.03, WIN['z1'] - WIN['z0']), 'F_glass', 0.0, tag='glass')
    for k in range(5): box((wx0 + 0.12 + k * (wx1 - wx0 - 0.24) / 4, fy + 0.12, (WIN['z0'] + WIN['z1']) / 2), (0.035, 0.035, WIN['z1'] - WIN['z0']), 'F_iron', 0.0)
    for c in (1.93, 4.73): iron_window(FX(c), fy, (0, -1, 0), (1, 0, 0), 0.66, 0.95, H1 + 0.8)
    # the stair: up the right-hand wall from the street to a landing at the house door, solid stone beneath, an iron rail
    xs0, xs1 = W / 2, W / 2 + 1.05; ys0 = fy + 0.35; nst = 17; run = 0.235; rise = (H1 + 0.02) / nst; yl0 = ys0 + nst * run; yl1 = fy + SD['u1'] + 0.35
    prism([Vector((xs0, ys0, 0)), Vector((xs0, yl0, 0)), Vector((xs0, yl0, H1 - 0.15)), Vector((xs0, ys0 + run, rise - 0.15))], -(xs1 - xs0 - 0.04), (1, 0, 0), 'F_stone', 0.02)
    for k in range(nst):
        box(((xs0 + xs1) / 2, ys0 + (k + 0.5) * run, (k + 1) * rise - 0.07), (xs1 - xs0, run + 0.04, 0.14), 'F_ashlar', 0.02, tag='step')
    box(((xs0 + xs1) / 2, (yl0 + yl1) / 2, H1 / 2 - 0.05), (xs1 - xs0, yl1 - yl0, H1 - 0.1), 'F_stone', 0.02)
    box(((xs0 + xs1 + 0.05) / 2, (yl0 + yl1) / 2, H1 - 0.04), (xs1 - xs0 + 0.08, yl1 - yl0 + 0.08, 0.16), 'F_ashlar', 0.03)
    rail = []
    for k in range(0, nst + 1, 2): rail.append(Vector((xs1 - 0.06, ys0 + k * run, k * rise + 0.02)))
    rail += [Vector((xs1 - 0.06, (yl0 + yl1) / 2, H1 + 0.02)), Vector((xs1 - 0.06, yl1 - 0.06, H1 + 0.02)), Vector((xs0 + 0.06, yl1 - 0.06, H1 + 0.02))]
    for p in rail: pipe(p, p + Vector((0, 0, 0.95)), 0.022, 'F_iron', seg=5)
    for a, b in zip(rail, rail[1:]): pipe(a + Vector((0, 0, 0.95)), b + Vector((0, 0, 0.95)), 0.03, 'F_iron', seg=6); pipe(a + Vector((0, 0, 0.45)), b + Vector((0, 0, 0.45)), 0.016, 'F_iron', seg=4)
    # the house door on the landing, a lantern by it
    dy0, dy1 = fy + SD['u0'], fy + SD['u1']
    box((W / 2 - 0.28, (dy0 + dy1) / 2, SD['z0'] + (SD['z1'] - SD['z0']) / 2), (0.08, dy1 - dy0, SD['z1'] - SD['z0']), 'F_wood', 0.01, tag='door')
    box((W / 2 + 0.04, (dy0 + dy1) / 2, SD['z1'] + 0.2), (T + 0.08, dy1 - dy0 + 0.5, 0.4), 'F_ashlar', 0.035, tag='lintel')
    pipe((W / 2 + 0.02, dy1 + 0.35, SD['z1'] + 0.1), (W / 2 + 0.4, dy1 + 0.35, SD['z1'] + 0.1), 0.025, 'F_iron', seg=5)
    box((W / 2 + 0.4, dy1 + 0.35, SD['z1'] - 0.2), (0.2, 0.2, 0.32), 'F_glow', 0.0, tag='glow'); box((W / 2 + 0.4, dy1 + 0.35, SD['z1'] - 0.01), (0.26, 0.26, 0.06), 'F_iron', 0.0)
    sx, sy, SH = -W / 2 + 1.1, D / 2 - 1.2, S['top'] + 3.4
    stack(sx, sy, S['rz0'], SH)
    pipe((-W / 2 + 0.25, fy + 0.3, S['rz0'] + 0.1), (-W / 2 + 0.25, fy - 0.3, S['rz0'] + 0.1), 0.06, 'F_iron', seg=8)
    pipe((-W / 2 + 0.25, fy - 0.3, S['rz0']), (-W / 2 + 0.25, fy - 0.3, 0.3), 0.055, 'F_iron', seg=8, tag='downpipe')
    SOOT += [(sx, sy, S['rz0'] + 1.5, SH + 0.5, 0.8, 0.7), ((x0 + x1) / 2, fy, WD['z1'] - 0.3, S['HT'], 1.4, 0.35)]
    PLOT = (W + 2.6, D + 0.8); VENTS = [(sx, SH + 0.4, sy)]


# ================================================================ the Ironway Foundry: the quarter's great works hall (a walk-in hub)
# Built in metres at its true size (24 x 21 m) and scaled to the kit's units at the end (the game draws it at 1.5x). The
# walls stand just outside the hall's interior, and the doorway is a true opening the interior is entered through.
if BUILDING == 'foundry':
    NAME = 'FerrinFoundry'; OUTSCALE = 1 / 1.5
    W, D, T, H1, H2, PAR = 24.0, 21.0, 0.55, 6.6, 3.4, 1.0
    FX = lambda u: -W / 2 + u
    GW, GH = 5.4, 6.3
    DOOR = dict(u0=W / 2 - GW / 2, u1=W / 2 + GW / 2, z0=0.0, z1=GH)
    WL = [2.3, 5.6, 21.7]                                                   # tall hall windows along the front
    op = lambda c, w, h, z: dict(u0=c - w / 2, u1=c + w / 2, z0=z, z1=z + h)
    front = [DOOR] + [op(c, 1.4, 3.4, 1.6) for c in WL] + [op(c, 1.0, 1.3, H1 + 0.9) for c in (2.3, 5.6, 8.6, 15.4, 18.4, 21.7)]
    sides = [op(c, 1.4, 3.4, 1.6) for c in (3.5, 7.8, 13.2, 17.5)] + [op(c, 1.0, 1.3, H1 + 0.9) for c in (3.5, 7.8, 13.2, 17.5)]
    S = shell(W, D, H1, H2, PAR, T, front, sides=sides, back=[op(c, 1.4, 3.4, 1.6) for c in (6, 18)], batter_gaps=[(FX(DOOR['u0']) - 0.4, FX(DOOR['u1']) + 0.4)], course_at=H1)
    fy = S['fy']
    for c in WL: iron_window(FX(c), fy, (0, -1, 0), (1, 0, 0), 1.4, 3.4, 1.6, shutters=False)
    for c in (2.3, 5.6, 8.6, 15.4, 18.4, 21.7): iron_window(FX(c), fy, (0, -1, 0), (1, 0, 0), 1.0, 1.3, H1 + 0.9, shutters=False)
    for side in (-1, 1):
        for c in (3.5, 7.8, 13.2, 17.5):
            y = fy + c if side > 0 else D / 2 - c
            iron_window(side * W / 2, y, (side, 0, 0), (0, 1, 0), 1.4, 3.4, 1.6, shutters=False); iron_window(side * W / 2, y, (side, 0, 0), (0, 1, 0), 1.0, 1.3, H1 + 0.9, shutters=False)
    # the doorway: dressed jambs, a riveted iron lintel beam, a flat arch of voussoirs above, the great iron door rolled aside on its rail
    for sx in (-1, 1):
        z = 0.0; k = 0
        while z < GH - 0.05:
            hh = min(0.55, GH - z); Lb = 0.8 if k % 2 == 0 else 0.5
            box((sx * (GW / 2 + Lb / 2 - 0.02), fy - 0.04 + T / 2, z + hh / 2), (Lb, T + 0.1, hh - 0.015), 'F_ashlar', 0.035, tag='jamb'); z += hh; k += 1
    box((0, fy - 0.08, GH + 0.25), (GW + 1.0, 0.5, 0.5), 'F_iron', 0.02, tag='lintel')
    for i in range(12): rivet((-GW / 2 - 0.3 + i * (GW + 0.6) / 11, fy - 0.34, GH + 0.25), (0, -1, 0))
    for i in range(11):
        u = -GW / 2 - 0.5 + (i + 0.5) * (GW + 1.0) / 11; tilt = (u / (GW / 2 + 0.5)) * 0.35
        box((u, fy - 0.03, GH + 0.95), ((GW + 1.0) / 11 - 0.03, T + 0.06, 0.9), 'F_ashlar', 0.03, rz=0, rx=0, tag='voussoir')
    box((0, fy - 0.05, GH + 0.95), (0.9, T + 0.12, 1.1), 'F_ashlar', 0.035)                                          # the keystone
    cog(0, fy - 0.05, GH + 2.2, 0.75, teeth=14)
    box((0, fy - 0.45, GH + 0.62), (GW * 2 + 1.2, 0.12, 0.16), 'F_iron', 0.01)                                         # the door's rail
    for k in range(3): pipe((GW / 2 + 0.5 + k * 2.4, fy - 0.3, GH + 0.62), (GW / 2 + 0.5 + k * 2.4, fy - 0.02, GH + 0.62), 0.04, 'F_iron', seg=5)
    dx0 = GW / 2 + 0.15; box((dx0 + GW / 2, fy - 0.3, GH / 2 + 0.1), (GW, 0.12, GH + 0.2), 'F_iron', 0.01, tag='door')   # the door, rolled clear of the opening
    for z in (0.6, GH / 2, GH - 0.4): box((dx0 + GW / 2, fy - 0.38, z), (GW, 0.04, 0.16), 'F_rust', 0.0)
    for x in (dx0 + 0.25, dx0 + GW - 0.25): box((x, fy - 0.38, GH / 2), (0.16, 0.04, GH), 'F_rust', 0.0)
    for i in range(2): cyl((dx0 + 0.6 + i * (GW - 1.2), fy - 0.3, GH + 0.72), 0.14, 0.14, 0.1, 'F_iron', seg=10, axis='Y')
    box((0, fy - 1.0, 0.03), (GW + 0.4, 2.0, 0.06), 'F_ashlar', 0.01)                                                  # a worn threshold
    for sx in (-0.7, 0.7): box((sx, fy - 1.0, 0.07), (0.1, 2.2, 0.06), 'F_iron', 0.0)                                  # rails run in through the door
    # the roof: a louvred ventilator along the ridge, the heat out of the hall
    rz = S['rz0'] + 0.7; vx = 7.0
    box((0, 0, rz + 0.1), (2 * vx, 2.4, 0.2), 'F_iron', 0.01)
    for sy in (-1, 1):
        for i in range(14):
            x = -vx + 0.5 + i * (2 * vx - 1) / 13
            box((x, sy * 1.15, rz + 0.75), (0.5, 0.06, 0.9), 'F_iron', 0.0, rx=sy * 0.5)
    prism([Vector((-vx - 0.2, -1.6, rz + 1.25)), Vector((vx + 0.2, -1.6, rz + 1.25)), Vector((vx + 0.2, 0, rz + 1.9)), Vector((-vx - 0.2, 0, rz + 1.9))], 0.05, (0, 0, 1), 'F_iron', 0.0, tag='roof')
    prism([Vector((-vx - 0.2, 1.6, rz + 1.25)), Vector((vx + 0.2, 1.6, rz + 1.25)), Vector((vx + 0.2, 0, rz + 1.9)), Vector((-vx - 0.2, 0, rz + 1.9))], 0.05, (0, 0, 1), 'F_iron', 0.0, tag='roof')
    for x in (-vx, vx): box((x, 0, rz + 0.65), (0.1, 2.4, 1.1), 'F_iron', 0.0)
    # two great stacks at the back corners, iron-banded
    VENTS = []
    for sx in (-1, 1):
        cx, cy2, SH = sx * 7.5, D / 2 - 3.0, 25.0
        cyl((cx, cy2, (S['rz0'] + SH) / 2), 1.45, 1.15, SH - S['rz0'], 'F_brick', seg=16, tag='stack')
        for z in (S['rz0'] + 3, S['rz0'] + 8, SH - 2.5): cyl((cx, cy2, z), 1.47 - (z - S['rz0']) / (SH - S['rz0']) * 0.3 + 0.04, 1.47 - (z - S['rz0']) / (SH - S['rz0']) * 0.3 + 0.04, 0.3, 'F_iron', seg=16)
        cyl((cx, cy2, SH + 0.2), 1.35, 1.35, 0.4, 'F_brick', seg=16); cyl((cx, cy2, SH + 0.42), 0.85, 0.85, 0.05, 'F_glass', seg=16)
        SOOT.append((cx, cy2, S['rz0'], SH + 1, 1.8, 0.8)); VENTS.append((cx, SH + 0.6, cy2))
    # the boiler on the left: riveted iron on stone saddles, its steam pipe into the hall
    bx = -W / 2 - 1.95; by = -2.0
    for y in (by - 2.0, by + 2.0): box((bx, y, 0.55), (2.6, 0.8, 1.1), 'F_ashlar', 0.03)
    cyl((bx, by, 2.25), 1.2, 1.2, 6.2, 'F_iron', seg=20, axis='Y', tag='boiler')
    for k in range(5): cyl((bx, by - 2.6 + k * 1.3, 2.25), 1.24, 1.24, 0.08, 'F_rust', seg=20, axis='Y')
    for sy in (-1, 1): cyl((bx, by + sy * 3.12, 2.25), 1.05, 0.2, 0.5 if False else 0.1, 'F_iron', seg=20, axis='Y')
    cyl((bx, by - 1.0, 3.75), 0.35, 0.35, 0.8, 'F_iron', seg=12); cyl((bx, by - 1.0, 4.2), 0.45, 0.45, 0.12, 'F_copper', seg=12)   # a steam dome
    pipe((bx, by + 1.5, 3.35), (bx, by + 1.5, 5.4), 0.16, 'F_copper', seg=10); pipe((bx, by + 1.5, 5.4), (-W / 2 + 0.2, by + 1.5, 5.4), 0.16, 'F_copper', seg=10)
    box((bx, by - 3.2, 1.0), (1.4, 0.4, 1.6), 'F_iron', 0.02); box((bx, by - 3.42, 1.0), (0.6, 0.06, 0.5), 'F_glow', 0.0, tag='glow')   # the firebox
    VENTS.append((bx, 5.0, by - 1.0))
    # the gantry crane on the right: two iron A-frames, a beam, a hoist and its chain
    gx = W / 2 + 2.1
    for gy in (-D / 2 + 2.0, D / 2 - 2.0):
        for s2 in (-1, 1): pipe((gx + s2 * 1.1, gy, 0.0), (gx, gy, 9.0), 0.16, 'F_iron', seg=8)
        box((gx, gy, 0.15), (2.8, 0.7, 0.3), 'F_ashlar', 0.03); pipe((gx - 0.8, gy, 3.0), (gx + 0.8, gy, 3.0), 0.08, 'F_iron', seg=6)
    box((gx, 0, 9.15), (0.5, D - 3.2, 0.6), 'F_iron', 0.01)
    box((gx, -1.5, 8.6), (0.8, 1.0, 0.6), 'F_rust', 0.02)
    for k in range(12): box((gx, -1.5, 8.2 - k * 0.42), (0.08, 0.18 if k % 2 else 0.06, 0.4), 'F_iron', 0.0)
    box((gx, -1.5, 2.9), (1.4, 1.0, 0.7), 'F_iron', 0.03); box((gx, -1.5, 3.32), (1.2, 0.8, 0.06), 'F_glow', 0.0)        # an ingot mould on the hook
    PLOT = (W + 7.5, D + 4.5)

# ---------------------------------------------------------------- one mesh, UVs by world projection, weathering
me = bpy.data.meshes.new(NAME); obj = bpy.data.objects.new(NAME, me); scene.collection.objects.link(obj)
for name in MAT_LIST:
    mm = make_material(name); mm.use_backface_culling = name != 'F_iron'; me.materials.append(mm)
bm = bmesh.new()
for vs, fs, mat, tag in PARTS:
    base = [bm.verts.new(p) for p in vs]
    for f in fs:
        try: face = bm.faces.new([base[i] for i in f])
        except ValueError: continue
        face.material_index = MAT_LIST.index(mat)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
uvl = bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    tile = MATS[MAT_LIST[f.material_index]][1]; n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
    for l in f.loops:
        p = l.vert.co; u, v = ((p.y, p.z) if ax == 0 else (p.x, p.z) if ax == 1 else (p.x, p.y))
        if ax == 0 and n.x < 0: u = -u
        if ax == 1 and n.y > 0: u = -u
        l[uvl].uv = (u / tile, v / tile)
bm.to_mesh(me); bm.free()
if 'OUTSCALE' in globals(): me.transform(Matrix.Scale(OUTSCALE, 4)); SOOT[:] = [(a2 * OUTSCALE, b2 * OUTSCALE, c2 * OUTSCALE, d2 * OUTSCALE, e2 * OUTSCALE, f2) for (a2, b2, c2, d2, e2, f2) in SOOT]; VENTS = [tuple(v * OUTSCALE for v in V) for V in VENTS]; PLOT = tuple(v * OUTSCALE for v in PLOT)   # built at true size, drawn scaled up
for p in me.polygons: p.use_smooth = False
col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); me.color_attributes.active_color = col
for d in col.data: d.color = (1, 1, 1, 1)
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 64
ground = bpy.data.objects.new('ground', bpy.data.meshes.new('g')); scene.collection.objects.link(ground)
gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=1, y_segments=1, size=30); gb.to_mesh(ground.data); gb.free()
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
scene.render.bake.target = 'VERTEX_COLORS'; scene.world = bpy.data.worlds.new('w')
bpy.ops.object.bake(type='AO')
rust_src = []
for vs, fs, mat, tag in PARTS:
    if tag in ('shutter', 'awning', 'sign', 'door', 'cog'):
        xs = [p.x for p in vs]; ys = [p.y for p in vs]; zs = [p.z for p in vs]; rust_src.append((min(xs), max(xs), min(ys), max(ys), min(zs)))
HTOP = S['HT'] * globals().get('OUTSCALE', 1.0)
if 'OUTSCALE' in globals(): rust_src = [tuple(v * OUTSCALE for v in r2) for r2 in rust_src]
for i, v in enumerate(me.vertices):
    ao = 0.35 + 0.65 * col.data[i].color[0]; p = v.co
    soot = smooth(HTOP - 1.4, HTOP + 0.3, p.z) * 0.3
    for (sx_, sy_, z0, z1, rad, st) in SOOT:
        if z0 - 0.2 < p.z < z1 + 0.5:
            d = math.hypot(p.x - sx_, (p.y - sy_) * 0.6)
            soot = max(soot, (1 - smooth(rad * 0.5, rad + 0.8, d)) * st * (0.55 + 0.45 * smooth(z0, z1, p.z)))
    rust = 0.0
    for (x0, x1, y0, y1, z0) in rust_src:
        if x0 - 0.05 < p.x < x1 + 0.05 and y0 - 0.25 < p.y < y1 + 0.25 and z0 - 1.3 < p.z < z0:
            rust = max(rust, (1 - smooth(0, 1.3, z0 - p.z)) * 0.5 * (0.6 + 0.4 * math.sin(p.x * 37.0) ** 2))
    k = 1 - soot; r, g, b = ao * k, ao * k, ao * k * 0.97
    r, g, b = r * (1 - rust) + rust * 0.42 * ao, g * (1 - rust) + rust * 0.24 * ao, b * (1 - rust) + rust * 0.13 * ao
    col.data[i].color = (r, g, b, 1)
bpy.data.objects.remove(ground)
print('%s: %d verts, %d tris, plot %s, vents %s' % (NAME, len(me.vertices), sum(len(p.vertices) - 2 for p in me.polygons), PLOT, VENTS))
lod = obj.copy(); lod.data = obj.data.copy(); lod.name = NAME + '_LOD1'; scene.collection.objects.link(lod)
dm = lod.modifiers.new('dec', 'DECIMATE'); dm.ratio = float(os.environ.get('LOD1', '0.16'))
bpy.context.view_layer.objects.active = lod; bpy.ops.object.select_all(action='DESELECT'); lod.select_set(True); bpy.ops.object.modifier_apply(modifier='dec')
print('LOD1: %d tris' % sum(len(p.vertices) - 2 for p in lod.data.polygons))
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); lod.select_set(True)
kw = dict(filepath=OUT, use_selection=True, export_format='GLB', export_image_format='NONE', export_materials='EXPORT', export_yup=True)
try: bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError: bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('EXPORTED', OUT)
if RENDER:
    lod.hide_render = True
    world = scene.world; world.use_nodes = True; nt = world.node_tree
    sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(float(os.environ.get('SUNEL', '7'))); sky.sun_rotation = math.radians(210)
    nt.links.new(sky.outputs['Color'], nt.nodes['Background'].inputs['Color']); nt.nodes['Background'].inputs['Strength'].default_value = float(os.environ.get('SKY', '0.22'))
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = float(os.environ.get('SUNE', '1.8')); sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(58), 0, math.radians(-35)); scene.collection.objects.link(sun)
    g = bpy.data.objects.new('street', bpy.data.meshes.new('street')); scene.collection.objects.link(g)
    gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=40, y_segments=40, size=18); gb.to_mesh(g.data); gb.free()
    g.data.materials.append(make_material('F_ashlar')); guv = g.data.uv_layers.new()
    for l in g.data.loops: co = g.data.vertices[l.vertex_index].co; guv.data[l.index].uv = (co.x / 2.5, co.y / 2.5)
    gc = g.data.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for d in gc.data: d.color = (0.55, 0.52, 0.5, 1)
    for (x, y, z, e) in LIGHT_SPOTS:
        L = bpy.data.objects.new('l', bpy.data.lights.new('l', 'POINT')); L.data.energy = e; L.data.color = (1.0, 0.5, 0.2); L.location = (x, y, z); scene.collection.objects.link(L)
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.lens = float(os.environ.get('LENS', '30'))
    cp = Vector(tuple(float(v) for v in os.environ.get('CAM', '-9.5,-15.5,4.2').split(','))); tgt = Vector(tuple(float(v) for v in os.environ.get('TGT', '0.6,-2.0,4.6').split(',')))
    cam.location = cp; cam.rotation_euler = (tgt - cp).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1280, 800; scene.cycles.samples = int(os.environ.get('SAMPLES', '48'))
    scene.view_settings.view_transform = 'AgX'; scene.render.filepath = RENDER
    try: scene.cycles.use_denoising = True
    except Exception: pass
    bpy.ops.render.render(write_still=True); print('RENDERED', RENDER)
