# Fogwright base body, the clean way: one continuous mesh, built for painting. Exports body.glb
# Torso, limbs, hands and feet come from a skin-modifier stick figure; the head is built ring by ring and
# shaped by one smooth function (skull, jaw, brow, nose, lips, chin), then bridged to the neck with no seam.
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix
OUT = sys.argv[-1]
src = open('tinker.py').read(); src = src[:src.index('bpy.ops.export_scene')]
sys.argv = ['x', '--', '/tmp/_unused.glb']; g = {'__name__': 'x'}; exec(compile(src, 'tinker.py', 'exec'), g)
arm, upd = g['arm'], g['upd']
for o in list(bpy.data.objects):
    if o.type == 'MESH': bpy.data.objects.remove(o, do_unlink=True)
arm.data.pose_position = 'REST'; upd()
col = bpy.context.scene.collection
sm = lambda a, b, x: (lambda t: t * t * (3 - 2 * t))(min(1.0, max(0.0, (x - a) / (b - a))))

# ---------- stick figure for the skin modifier: (position, radius x, radius y, parent)
N = [((0, 0.005, 0.95), 0.150, 0.105, None),    # 0 pelvis (root)
     ((0, 0.0, 1.08), 0.128, 0.088, 0),         # 1 waist
     ((0, -0.004, 1.24), 0.150, 0.100, 1),      # 2 ribs
     ((0, -0.006, 1.36), 0.160, 0.104, 2),      # 3 chest
     ((0, 0.0, 1.44), 0.140, 0.090, 3),         # 4 shoulder line
     ((0, 0.006, 1.52), 0.062, 0.062, 4),       # 5 neck
     ((0, 0.004, 1.585), 0.064, 0.066, 5)]      # 6 neck top (head is built separately)
for sx in (1, -1):
    b = len(N)
    N += [((0.175 * sx, 0.0, 1.425), 0.056, 0.056, 4),        # shoulder
          ((0.27 * sx, 0.01, 1.18), 0.043, 0.043, b),         # elbow
          ((0.352 * sx, 0.0, 0.955), 0.031, 0.027, b + 1),    # wrist
          ((0.372 * sx, -0.008, 0.875), 0.042, 0.019, b + 2), # palm
          ((0.388 * sx, -0.014, 0.785), 0.036, 0.015, b + 3), # fingertips (mitten)
          ((0.352 * sx, -0.038, 0.895), 0.013, 0.013, b + 2), # thumb
          ((0.095 * sx, 0.0, 0.89), 0.078, 0.078, 0),         # hip
          ((0.11 * sx, -0.006, 0.52), 0.052, 0.054, b + 6),   # knee
          ((0.117 * sx, 0.012, 0.095), 0.038, 0.042, b + 7),  # ankle
          ((0.13 * sx, -0.115, 0.035), 0.044, 0.028, b + 8)]  # toes
me = bpy.data.meshes.new('skel')
me.from_pydata([p for p, *_ in N], [(i, n[3]) for i, n in enumerate(N) if n[3] is not None], [])
body = bpy.data.objects.new('Body', me); col.objects.link(body)
sk = body.modifiers.new('Skin', 'SKIN'); sk.branch_smoothing = 0.6; sk.use_smooth_shade = True
for i, n in enumerate(N):
    sv = me.skin_vertices[0].data[i]; sv.radius = (n[1], n[2]); sv.use_root = (i == 0)
sub = body.modifiers.new('Sub', 'SUBSURF'); sub.levels = 1
bpy.context.view_layer.objects.active = body
for m in ('Skin', 'Sub'):
    with bpy.context.temp_override(object=body, active_object=body): bpy.ops.object.modifier_apply(modifier=m)
print('SKIN verts', len(body.data.vertices), 'top', round(max(v.co.z for v in body.data.vertices), 3))

# ---------- head: rings of vertices on a sculpted surface
C = Vector((0, 0.004, 1.68))
# The head, built as a low-poly head is modelled: horizontal cross-sections from the neck to the crown.
# Each row: height, centre y, half-width, front depth, back depth, squareness (2 = round, higher = boxier).
# The sharp step from the neck (1.556) to the jaw (1.568) makes the under-jaw plane and a real jawline.
ROWS = [(1.540, 0.012, 0.057, 0.053, 0.060, 2.2),   # neck
        (1.556, 0.012, 0.059, 0.056, 0.062, 2.2),   # top of the neck
        (1.562, 0.008, 0.064, 0.078, 0.066, 2.6),   # under the jaw
        (1.570, 0.004, 0.071, 0.104, 0.070, 3.4),   # chin and jaw line
        (1.585, 0.002, 0.075, 0.108, 0.078, 3.2),   # lower jaw
        (1.602, 0.000, 0.077, 0.111, 0.088, 2.9),   # mouth
        (1.622, 0.000, 0.079, 0.112, 0.095, 2.7),   # upper lip
        (1.642, 0.000, 0.083, 0.109, 0.100, 2.6),   # under the nose
        (1.664, 0.000, 0.089, 0.104, 0.104, 2.6),   # cheekbones
        (1.688, 0.000, 0.090, 0.097, 0.107, 2.5),   # eyes
        (1.708, 0.000, 0.090, 0.108, 0.108, 2.7),   # brow
        (1.732, 0.002, 0.088, 0.100, 0.108, 2.5),   # forehead
        (1.758, 0.005, 0.084, 0.088, 0.104, 2.4),   # upper forehead
        (1.782, 0.008, 0.075, 0.070, 0.092, 2.3),   # cranium
        (1.801, 0.010, 0.058, 0.048, 0.068, 2.2),   # flat top
        (1.812, 0.010, 0.034, 0.024, 0.040, 2.0)]
ZB, ZT = ROWS[0][0], 1.815
def row_at(z):
    z = min(max(z, ROWS[0][0]), ROWS[-1][0])
    for r0, r1 in zip(ROWS, ROWS[1:]):
        if z <= r1[0]:
            t = (z - r0[0]) / (r1[0] - r0[0]); t = t * t * (3 - 2 * t) if r1[0] - r0[0] > 0.012 else t
            return tuple(a + (b - a) * t for a, b in zip(r0[1:], r1[1:]))
    return ROWS[-1][1:]
def gauss(x, z, cx, cz, wx, wz): return math.exp(-((x - cx) / wx) ** 2 - ((z - cz) / wz) ** 2)
def outline(th, z):
    cy, a, f, b, n = row_at(z); s, c = math.sin(th), -math.cos(th)
    dep = f if c < 0 else b
    r = 1 / ((abs(s) / a) ** n + (abs(c) / dep) ** n) ** (1 / n)
    return Vector((s * r, cy + c * r, z))
def features(p, th):
    x, z = p.x, p.z; front = max(0.0, math.cos(th)) ** 2
    nose = (0.012 + 0.018 * sm(1.71, 1.655, z)) * sm(1.722, 1.708, z) * (1 - sm(1.652, 1.638, z)) * math.exp(-(x / 0.0125) ** 4)
    d = (nose + 0.007 * (gauss(x, z, 0.012, 1.646, 0.006, 0.006) + gauss(x, z, -0.012, 1.646, 0.006, 0.006))      # nostril wings
         - 0.012 * (gauss(x, z, 0.034, 1.689, 0.016, 0.011) + gauss(x, z, -0.034, 1.689, 0.016, 0.011))          # deep eye sockets
         + 0.006 * (gauss(x, z, 0.056, 1.664, 0.016, 0.012) + gauss(x, z, -0.056, 1.664, 0.016, 0.012))          # cheekbones
         + 0.004 * gauss(x, z, 0, 1.617, 0.02, 0.007) - 0.004 * (gauss(x, z, 0.025, 1.616, 0.006, 0.006) + gauss(x, z, -0.025, 1.616, 0.006, 0.006))
         - 0.003 * gauss(x, z, 0, 1.602, 0.02, 0.004)                                                          # under the lip
         - 0.003 * gauss(x, z, 0, 1.709, 0.007, 0.008))                                                        # between the brows
    p.y -= d * front
    return p
def head_point(th, ph):  # ph -1 at the neck .. 1 at the crown
    z = ZB + (ZT - ZB) * (ph + 1) / 2
    if z >= ZT - 1e-6: return Vector((0, 0.01, ZT + 0.004))
    return features(outline(th, z), th)
def inside_head(q):
    if q.z < ZB or q.z > ZT: return False
    th = math.atan2(q.x, -(q.y - 0.0))
    o = head_point(th, 2 * (q.z - ZB) / (ZT - ZB) - 1)
    return math.hypot(q.x, q.y) <= math.hypot(o.x, o.y)
def head_r(d):  # distance from C to the skull along direction d
    d = d.normalized(); lo, hi = 0.0, 0.25
    for _ in range(26):
        m = (lo + hi) / 2
        if inside_head(C + d * m): lo = m
        else: hi = m
    return lo
# columns denser at the face, rows from the neck to the crown
LON = 32
def warp_th(u): return math.pi * (2 * u - 1) * (0.55 + 0.45 * abs(2 * u - 1))
ZS = [1.540, 1.556, 1.562, 1.570, 1.578, 1.586, 1.596, 1.606, 1.614, 1.622, 1.632, 1.642, 1.652, 1.664, 1.676, 1.684, 1.692, 1.700, 1.708, 1.718, 1.732, 1.746, 1.760, 1.772, 1.784, 1.795, 1.804, 1.811]
hb = bmesh.new()
rings = [[hb.verts.new(features(outline(warp_th(i / LON), z), warp_th(i / LON))) for i in range(LON)] for z in ZS]
top = hb.verts.new(Vector((0, 0.01, ZT + 0.004)))
for j in range(len(rings) - 1):
    a_, b_ = rings[j], rings[j + 1]
    for i in range(LON): hb.faces.new((a_[i], a_[(i + 1) % LON], b_[(i + 1) % LON], b_[i]))
for i in range(LON): hb.faces.new((rings[-1][i], rings[-1][(i + 1) % LON], top))

bm = bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 1.52], context='VERTS')
print('NECK ring', sum(1 for v in bm.verts if v.is_boundary))
tmp = bpy.data.meshes.new('_h'); hb.to_mesh(tmp); hb.free(); bm.from_mesh(tmp); bpy.data.meshes.remove(tmp)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
print('BOUNDARY verts', sum(1 for v in bm.verts if v.is_boundary))
bmesh.ops.bridge_loops(bm, edges=[e for e in bm.edges if e.is_boundary])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
print('OPEN after bridge', sum(1 for e in bm.edges if e.is_boundary))
bm.to_mesh(body.data); bm.free()
for p in body.data.polygons: p.use_smooth = True
# ---------- ears: small flaps tucked into the side of the head
for sx in (1, -1):
    eb = bmesh.new(); bmesh.ops.create_uvsphere(eb, u_segments=10, v_segments=7, radius=1)
    for v in eb.verts:
        v.co = Vector((v.co.x * 0.008, v.co.y * 0.019, v.co.z * 0.03))
        if v.co.x * sx < 0: v.co.x *= 0.3
    bmesh.ops.rotate(eb, verts=eb.verts, cent=(0, 0, 0), matrix=g['R']('Z', 0.35 * sx))
    bmesh.ops.translate(eb, verts=eb.verts, vec=(0.089 * sx, 0.014, 1.672))
    em = bpy.data.meshes.new('ear'); eb.to_mesh(em); eb.free()
    bm = bmesh.new(); bm.from_mesh(body.data); bm.from_mesh(em); bm.to_mesh(body.data); bm.free(); bpy.data.meshes.remove(em)
bmesh_fix = bmesh.new(); bmesh_fix.from_mesh(body.data); bmesh.ops.recalc_face_normals(bmesh_fix, faces=bmesh_fix.faces); bmesh_fix.to_mesh(body.data); bmesh_fix.free()
for p in body.data.polygons: p.use_smooth = True
print('BODY tris', sum(len(p.vertices) - 2 for p in body.data.polygons))
# ---------- hair and beards: real volumes grown from the head surface, shaped into locks
HL = [(0.0, 1.745), (0.6, 1.748), (1.15, 1.706), (1.5, 1.655), (2.45, 1.618), (math.pi, 1.604)]
def hairline(th):
    th = abs(th)
    for (a, za), (b, zb) in zip(HL, HL[1:]):
        if th <= b: return za + (zb - za) * (th - a) / (b - a)
    return HL[-1][1]
def tri(x): return abs((x % 1.0) * 2 - 1)
def shell(name, inside_fn, thick_fn, droop_fn=lambda th, ph, p: 0.0, NT=44, NP=26, ph0=-0.75):
    bm = bmesh.new(); grid = {}
    ths = [-math.pi + 2 * math.pi * i / NT for i in range(NT)]
    for i, th in enumerate(ths):
        for j in range(NP):
            ph = ph0 + (1 - ph0) * j / (NP - 1) * 0.999
            p = head_point(th, ph)
            if not inside_fn(th, ph, p): continue
            n = (p - C).normalized()
            q = p + n * thick_fn(th, ph, p); q.z -= droop_fn(th, ph, p)
            grid[(i, j)] = bm.verts.new(q)
    for (i, j), v in list(grid.items()):
        a, b, c = grid.get(((i + 1) % NT, j)), grid.get(((i + 1) % NT, j + 1)), grid.get((i, j + 1))
        if a and b and c: bm.faces.new((v, a, b, c))
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    so = ob.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = 0.008; so.offset = -1; so.use_even_offset = True
    for m in ('Sol',):
        with bpy.context.temp_override(object=ob, active_object=ob): bpy.ops.object.modifier_apply(modifier=m)
    for p in me.polygons: p.use_smooth = True
    print(name, 'tris', sum(len(p.vertices) - 2 for p in me.polygons))
    return ob
def locks(th, ph, k=14, a=0.35): return 1 + a * (0.5 + 0.5 * math.sin(th * k + 1.7 * math.sin(ph * 5)))
def ph_at(th, z, lo=-0.98, hi=0.999):  # the latitude on the head at which the surface reaches height z
    for _ in range(30):
        m = (lo + hi) / 2
        if head_point(th, m).z < z: lo = m
        else: hi = m
    return (lo + hi) / 2
def shell(name, th0, th1, z_lo, z_hi, thick, droop=lambda th, f: 0.0, NT=40, NR=14, wrap=False):
    """Columns around the head from th0 to th1; each column runs from height z_lo(th) up to z_hi(th),
    so every edge lands exactly where it should. thick(th, f, p) and droop(th, f) shape it (f: 0 bottom .. 1 top)."""
    bm = bmesh.new(); cols = []
    n = NT if wrap else NT + 1
    for i in range(n):
        th = th0 + (th1 - th0) * i / NT
        a, b = ph_at(th, z_lo(th)), (0.999 if z_hi(th) >= 9 else ph_at(th, z_hi(th)))
        col_ = []
        for j in range(NR):
            f = j / (NR - 1); ph = a + (b - a) * f
            p = head_point(th, ph); nrm = (p - C).normalized()
            q = p + nrm * (thick(th, f, p) if j < NR - 1 else thick(0.0, f, p)); dr = droop(th, f)
            if dr: q.z -= dr; q += Vector((nrm.x, nrm.y, 0)).normalized() * dr * 0.28
            col_.append(bm.verts.new(q))
        cols.append(col_)
    for i in range(NT if wrap else NT):
        A, B = cols[i], cols[(i + 1) % n]
        for j in range(NR - 1): bm.faces.new((A[j], B[j], B[j + 1], A[j + 1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    so = ob.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = 0.007; so.offset = -1; so.use_even_offset = True
    with bpy.context.temp_override(object=ob, active_object=ob): bpy.ops.object.modifier_apply(modifier='Sol')
    bm2 = bmesh.new(); bm2.from_mesh(me); bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces); bm2.to_mesh(me); bm2.free()
    for p in me.polygons: p.use_smooth = True
    print(name, 'tris', sum(len(p.vertices) - 2 for p in me.polygons))
    return ob
TOP = lambda th: 99
tips = lambda k, d: (lambda th: d * tri(th * k / math.pi))
def surf(d, lift):  # a point on the skull in direction d, lifted off it
    d = d.normalized(); p = C + d * head_r(d); return p + d * lift
def slerp(a, b, t):
    a, b = a.normalized(), b.normalized(); om = math.acos(max(-1, min(1, a.dot(b))))
    if om < 1e-4: return a
    return (a * math.sin((1 - t) * om) + b * math.sin(t * om)) / math.sin(om)
def dir_th(th, z):  # direction from the head centre to the skull at angle th and height z
    return (head_point(th, ph_at(th, z)) - C).normalized()
def lock(bm, pts, w0, t0, tipw=0.1, flat=True):
    """A clump of hair: a flattened diamond tube along pts, tapering to a point."""
    n = len(pts); rings = []
    for i, p in enumerate(pts):
        T = (pts[min(i + 1, n - 1)] - pts[max(i - 1, 0)]).normalized()
        out = Vector((p.x, p.y - 0.004, max(p.z - 1.58, 0) * 0.3)); out = out - T * out.dot(T)
        N_ = out.normalized() if out.length > 1e-5 else T.orthogonal().normalized(); B = T.cross(N_).normalized()
        f = i / (n - 1); w = w0 * (1 - (1 - tipw) * f ** 1.3); t = t0 * (1 - 0.7 * f)
        if i == n - 1: rings.append([bm.verts.new(p)]); continue
        rings.append([bm.verts.new(p + B * w / 2), bm.verts.new(p + N_ * t / 2), bm.verts.new(p - B * w / 2), bm.verts.new(p - N_ * t / 2)])
    bm.faces.new(rings[0][::-1])
    for i in range(n - 1):
        A, Bq = rings[i], rings[i + 1]
        for k in range(4):
            if len(Bq) == 1: bm.faces.new((A[k], A[(k + 1) % 4], Bq[0]))
            else: bm.faces.new((A[k], A[(k + 1) % 4], Bq[(k + 1) % 4], Bq[k]))
def hang(p, d, n, seg, out=0.25, curl=0.0):
    """Continue a lock from p in direction d, bending down under its own weight and away from the body."""
    pts = []; d = d.normalized()
    for i in range(n):
        away = Vector((p.x, p.y - 0.01, 0)); away = away.normalized() if away.length > 1e-4 else Vector((0, 0, 0))
        d = (d * 0.62 + Vector((0, 0, -1)) * 0.38 + away * out * 0.3).normalized()
        p = p + d * seg; pts.append(p)
    return pts
def arc(d0, d1, lift0, lift1, n=7, puff=0.0):
    return [surf(slerp(d0, d1, i / (n - 1)), lift0 + (lift1 - lift0) * i / (n - 1) + puff * math.sin(math.pi * i / (n - 1))) for i in range(n)]
def finish_hair(name, bm, cap=None):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    if cap is not None:
        with bpy.context.temp_override(active_object=ob, selected_editable_objects=[ob, cap], object=ob): bpy.ops.object.join()
    bm2 = bmesh.new(); bm2.from_mesh(ob.data); bmesh.ops.recalc_face_normals(bm2, faces=bm2.faces); bm2.to_mesh(ob.data); bm2.free()
    for p_ in ob.data.polygons: p_.use_smooth = False   # chunky, faceted locks
    print(name, 'tris', sum(len(p_.vertices) - 2 for p_ in ob.data.polygons)); return ob
def scalp(name, lower=0.004):  # a thin cap under the locks, so no skin shows between them
    return shell(name + '_cap', -math.pi, math.pi, lambda th: hairline(th) - lower, TOP, lambda th, f, p: 0.003 + 0.004 * f, NT=28, NR=8, wrap=True)
HAIRS = []
# ---------- Valheim's way: each beard and hairstyle is ONE solid sculpted mass; strands are only painted grooves
def solid(name, th0, th1, z_top, z_bot, thick, L, conv=0.5, depth=lambda th: 0.02, NT=24, NF=6, NS=8, fwd=0.006):
    """A closed volume built from slices across the face. Each slice hugs the head from z_top(th) down to z_bot(th),
    offset by thick(th, z), then hangs L(th) further down, narrowing toward the middle by conv and thinning to its tip."""
    bm = bmesh.new(); loops = []
    for i in range(NT + 1):
        th = th0 + (th1 - th0) * i / NT
        outer, inner = [], []
        for k in range(NF):
            z = z_top(th) + (z_bot(th) - z_top(th)) * k / (NF - 1)
            p = head_point(th, ph_at(th, z)); n = Vector((p.x, p.y - 0.004, (p.z - C.z) * 0.25)).normalized()
            outer.append(p + n * thick(th, z)); inner.append(p + n * 0.0008)
        Lh = L(th); base_o, base_i = outer[-1], inner[-1]
        if Lh > 0.002:
            for k in range(1, NS + 1):
                s = k / NS; z = base_o.z - Lh * s
                x = base_o.x * (1 - conv * s ** 1.2); y = base_o.y - fwd * math.sin(math.pi * s * 0.8)
                o = Vector((x, y, z)); outer.append(o)
                d = depth(th) * (1 - s) ** 0.8 + 0.0015
                inner.append(Vector((x * 0.97, y + d, z + 0.002 * (1 - s))))
        loops.append([bm.verts.new(v) for v in outer + inner[::-1]])
    m = min(len(l) for l in loops)
    if any(len(l) != m for l in loops):   # keep every slice the same length: pad short ones at their tip
        for idx, l in enumerate(loops):
            while len(l) < max(len(x) for x in loops):
                h = len(l) // 2; l.insert(h, bm.verts.new(l[h - 1].co.lerp(l[h].co, 0.5)))
    n = len(loops[0])
    for i in range(len(loops) - 1):
        A, B = loops[i], loops[i + 1]
        for k in range(n): bm.faces.new((A[k], A[(k + 1) % n], B[(k + 1) % n], B[k]))
    bm.faces.new(loops[0][::-1]); bm.faces.new(loops[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    for p_ in me.polygons: p_.use_smooth = True
    print(name, 'tris', sum(len(p_.vertices) - 2 for p_ in me.polygons)); return ob
def tube(bm, pts, r0, r1, seg=8, sq=1.0):
    rings = []
    for i, p in enumerate(pts):
        T = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized(); U = T.orthogonal().normalized(); V = T.cross(U)
        r = r0 + (r1 - r0) * i / (len(pts) - 1)
        rings.append([bm.verts.new(p + (U * math.cos(2 * math.pi * k / seg) + V * math.sin(2 * math.pi * k / seg) * sq) * r) for k in range(seg)])
    for i in range(len(rings) - 1):
        for k in range(seg): bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1]); tip = bm.verts.new(pts[-1] + (pts[-1] - pts[-2]).normalized() * r1)
    for k in range(seg): bm.faces.new((rings[-1][k], rings[-1][(k + 1) % seg], tip))
def as_object(name, bm, smooth=True):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); ob = bpy.data.objects.new(name, me); col.objects.link(ob)
    for p_ in me.polygons: p_.use_smooth = smooth
    return ob
def join(target, *others):
    with bpy.context.temp_override(active_object=target, selected_editable_objects=[target, *others], object=target): bpy.ops.object.join()
    print(target.name, 'tris', sum(len(p_.vertices) - 2 for p_ in target.data.polygons)); return target
fw = lambda th, w=0.6: math.exp(-(th / w) ** 2)
chunks = lambda th, k, a: 1 + a * (tri(th * k / math.pi) - 0.5)
beard_top = lambda th: 1.664 - 0.03 * sm(1.0, 0.3, abs(th)) - 0.032 * fw(th, 0.32)   # sideburns, cheeks, under the lip
beard_jaw = lambda th: 1.576 - 0.004 * fw(th)
bthick = lambda th, z: 0.006 + 0.012 * fw(th, 0.9) * sm(1.63, 1.59, z)
def beard(name, Lmax, shape, conv, depth=0.03):
    return solid(name, -1.55, 1.55, beard_top, beard_jaw, bthick, lambda th: Lmax * shape(th), conv, lambda th: depth * fw(th, 0.8) + 0.006)
HAIRS.append(beard('Beard_Short', 0.022, lambda th: fw(th, 0.9) * chunks(th, 5, 0.3), 0.2, 0.012))
HAIRS.append(beard('Beard_Full', 0.085, lambda th: (0.08 + 0.92 * fw(th, 0.55) ** 1.3) * chunks(th, 4, 0.4), 0.6))
HAIRS.append(beard('Beard_Pointed', 0.12, lambda th: (0.05 + 0.95 * fw(th, 0.32) ** 1.5) * chunks(th, 3, 0.25), 0.9))
HAIRS.append(beard('Beard_Forked', 0.11, lambda th: (0.06 + 0.94 * max(fw(th - 0.24, 0.17), fw(th + 0.24, 0.17)) ** 1.3), 0.3))
bb = beard('Beard_Braided', 0.045, lambda th: (0.3 + 0.7 * fw(th, 0.7)) * chunks(th, 4, 0.3), 0.55)
bm = bmesh.new(); top = head_point(0, ph_at(0, 1.576)) + Vector((0, -0.012, -0.04))
pts = [top + Vector((0.003 * math.sin(k * 1.9), -0.004 * math.sin(k * 0.5), -k * 0.022)) for k in range(7)]
tube(bm, pts, 0.016, 0.008, 8, 0.8)
for k in range(1, 6): r = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.013 - k * 0.0012); bmesh.ops.transform(bm, verts=r['verts'], matrix=Matrix.Translation(pts[k] + Vector((0.004 * (-1) ** k, 0, 0))) @ Matrix.Diagonal((1, 0.75, 1.1, 1)))
HAIRS.append(join(bb, as_object('_braid', bm)))
HAIRS.append(solid('Moustache', -0.48, 0.48, lambda th: 1.638 - 0.004 * sm(0.1, 0.45, abs(th)), lambda th: 1.624 - 0.012 * sm(0.18, 0.45, abs(th)),
                   lambda th, z: 0.006 + 0.004 * fw(th, 0.3), lambda th: 0.016 * sm(0.25, 0.48, abs(th)), 0.0, lambda th: 0.008, NT=14, NF=4, NS=4, fwd=0.004))
# hair: a solid cap with volume, a few chunky points at the hairline, strands painted on
def cap(name, lower, thick, notch_k=6, notch=0.01, droop=lambda th, f: 0.0, NR=12):
    return shell(name, -math.pi, math.pi, lambda th: hairline(th) - lower(th) - notch * tri(th * notch_k / math.pi), TOP, thick, droop, NT=40, NR=NR, wrap=True)
HAIRS.append(cap('Hair_Short', lambda th: 0.003, lambda th, f, p: 0.007 + 0.012 * f, 7, 0.007))
HAIRS.append(cap('Hair_Swept', lambda th: 0.004, lambda th, f, p: 0.005 + 0.03 * f ** 0.8 * (1 + 0.35 * fw(th, 0.8) * f), 5, 0.012))
backw = lambda th: sm(1.15, 2.0, abs(th))
HAIRS.append(cap('Hair_Long', lambda th: 0.004 + 0.03 * backw(th), lambda th, f, p: 0.008 + 0.018 * f + 0.014 * backw(th) * (1 - f), 4, 0.016,
                 lambda th, f: backw(th) * (1 - f) ** 2.2 * (0.19 + 0.04 * tri(th * 2.0)), NR=16))
pt = cap('Hair_Ponytail', lambda th: 0.003, lambda th, f, p: 0.006 + 0.016 * f, 7, 0.006)
bm = bmesh.new(); tie = surf(Vector((0, 1, 0.3)), 0.02)
tube(bm, [tie + Vector((0, 0.01 + 0.03 * k, -0.04 * k * k * 0.5 - 0.012 * k)) for k in range(7)], 0.024, 0.01, 8, 0.75)
r = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.02, radius2=0.02, depth=0.012); bmesh.ops.transform(bm, verts=r['verts'], matrix=Matrix.Translation(tie + Vector((0, 0.004, 0))) @ Matrix.Rotation(1.2, 4, 'X'))
HAIRS.append(join(pt, as_object('_tail', bm)))
tk = cap('Hair_Topknot', lambda th: 0.003, lambda th, f, p: 0.005 + 0.01 * f, 7, 0.006)
bm = bmesh.new(); knot = surf(Vector((0, 0.35, 1)), 0.012)
r = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.03); bmesh.ops.transform(bm, verts=r['verts'], matrix=Matrix.Translation(knot + Vector((0, 0.004, 0.016))) @ Matrix.Diagonal((1, 1, 0.8, 1)))
tube(bm, [knot + Vector((0, 0.01, 0.03)), knot + Vector((0, 0.035, 0.03)), knot + Vector((0, 0.055, 0.005)), knot + Vector((0, 0.065, -0.03))], 0.014, 0.006, 7, 0.7)
HAIRS.append(join(tk, as_object('_knot', bm)))

for ob in HAIRS:
    ob.data.materials.append(bpy.data.materials.new(ob.name))
    ca = ob.data.color_attributes.new('rest', 'FLOAT_COLOR', 'POINT')
    for v in ob.data.vertices: ca.data[v.index].color = (v.co.x + 0.5, v.co.y + 0.5, v.co.z / 2, 1)
    ob.data.color_attributes.active_color = ca
# ---------- rest position, stored as a colour so the game can paint in body space
me = body.data
ca = me.color_attributes.new('rest', 'FLOAT_COLOR', 'POINT')
for v in me.vertices: ca.data[v.index].color = (v.co.x + 0.5, v.co.y + 0.5, v.co.z / 2, 1)
me.color_attributes.active_color = ca
mat = bpy.data.materials.new('Body'); me.materials.append(mat)
# ---------- skin it to the rig
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
print('GROUPS', len(body.vertex_groups))
# hair and beards take the skin weights of the face beneath them, so they move exactly with it
for ob in HAIRS:
    dt = ob.modifiers.new('DT', 'DATA_TRANSFER'); dt.object = body; dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'POLYINTERP_NEAREST'
    dt.layers_vgroup_select_src = 'ALL'; dt.layers_vgroup_select_dst = 'NAME'
    with bpy.context.temp_override(object=ob, active_object=ob):
        bpy.ops.object.datalayout_transfer(modifier='DT'); bpy.ops.object.modifier_apply(modifier='DT')
    keep = {ob.vertex_groups[n].index for n in ('head', 'neck') if n in ob.vertex_groups}
    hi = ob.vertex_groups['head'].index if 'head' in ob.vertex_groups else ob.vertex_groups.new(name='head').index
    for v in ob.data.vertices:
        ws = {g.group: g.weight for g in v.groups if g.group in keep}; tot = sum(ws.values())
        for g in list(v.groups):
            if g.group not in keep: ob.vertex_groups[g.group].remove([v.index])
        if tot < 1e-4: ob.vertex_groups[hi].add([v.index], 1.0, 'REPLACE')
        else:
            for gi, w in ws.items(): ob.vertex_groups[gi].add([v.index], w / tot, 'REPLACE')
    ob.modifiers.new('Armature', 'ARMATURE').object = arm; ob.parent = arm
    print(ob.name, 'groups', len(ob.vertex_groups))
arm.data.pose_position = 'POSE'
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True)
for ob in HAIRS: ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
                          export_skins=True, export_materials='EXPORT', export_force_sampling=True, export_vertex_color='ACTIVE')
print('EXPORTED', OUT)
