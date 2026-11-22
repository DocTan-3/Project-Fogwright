# Fogwright base body from the Simple RPG Human Male (Sketchfab), rigged and repainted by code.
# RACE=human (default), ferrin, ilvari, zarhim or female, e.g.  RACE=female python rpgbody.py -- female.glb
# (adapted from body.py): one continuous mesh, built for painting. Exports body.glb
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


import os
RACE = os.environ.get('RACE', 'human')
MODEL_DIR = os.path.abspath('source')   # put model_0.obj from the Sketchfab download here (not committed)
# ---------- 1. fit our rig's arms to the model (its arms are longer, with bigger hands)
ARMFIT = {'L': [(0.2, 0.03, 1.43), (0.255, 0.05, 1.17), (0.296, 0.03, 0.95), (0.315, 0.01, 0.70)]}
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
for side, sx in (('L', 1), ('R', -1)):
    sh, el, wr, tip = [Vector((p[0] * sx, p[1], p[2])) for p in ARMFIT['L']]
    eb[f'shoulder.{side}'].tail = sh
    eb[f'upper_arm.{side}'].head = sh; eb[f'upper_arm.{side}'].tail = el
    eb[f'forearm.{side}'].head = el; eb[f'forearm.{side}'].tail = wr
    eb[f'hand.{side}'].head = wr; eb[f'hand.{side}'].tail = tip
REST_ARM = {s: [eb[f'upper_arm.{s}'].tail.copy(), eb[f'forearm.{s}'].tail.copy(), eb[f'hand.{s}'].tail.copy()] for s in ('L', 'R')}
newB = []
for nm, h, t, par in g['BONES']:
    newB.append((nm, tuple(eb[nm].head), tuple(eb[nm].tail), par))
g['BONES'][:] = newB
bpy.ops.object.mode_set(mode='OBJECT'); upd()
# ---------- 2. the model: body, head, arms, eyes and mouth (sword and shield left out), scaled to our height
bpy.ops.wm.obj_import(filepath=os.path.join(MODEL_DIR, 'model_0.obj'))
body = bpy.context.selected_objects[0]; body.name = 'Body'
SC = 1.815 / 2.138
body.data.transform(Matrix.Scale(SC, 4) @ Matrix.Rotation(-math.pi / 2, 4, 'X') @ body.matrix_world); body.matrix_world = Matrix()
body.data.materials.clear()
for p in body.data.polygons: p.use_smooth = True
def find_islands():
    global islands
    bm = bmesh.new(); bm.from_mesh(body.data); bm.verts.ensure_lookup_table(); ISL = [-1] * len(bm.verts); islands = []
    for v in bm.verts:
        if ISL[v.index] >= 0: continue
        st = [v]; comp = []; k = len(islands)
        while st:
            x = st.pop()
            if ISL[x.index] >= 0: continue
            ISL[x.index] = k; comp.append(x.index)
            for e in x.link_edges: st.append(e.other_vert(x))
        islands.append(comp)
    bm.free()
    return islands
islands = find_islands()
V = body.data.vertices
# the model's own mouth parts (teeth rows, mouth interior) go: our paint draws the mouth on the face
_small = [k for k in range(len(islands)) if len(islands[k]) < 32 and all(abs(V[i].co.x) < 0.04 for i in islands[k]) and all(1.55 < V[i].co.z < 1.7 for i in islands[k])]
_bm = bmesh.new(); _bm.from_mesh(body.data); _bm.verts.ensure_lookup_table()
_kill = set(i for k in _small for i in islands[k]); bmesh.ops.delete(_bm, geom=[v for v in _bm.verts if v.index in _kill], context='VERTS'); _bm.to_mesh(body.data); _bm.free()
print('removed mouth pieces', len(_small), 'verts', len(_kill))
islands = find_islands()
V = body.data.vertices
def box(ix): zs = [V[i].co for i in islands[ix]]; return (min(c.x for c in zs), max(c.x for c in zs), min(c.y for c in zs), max(c.y for c in zs), min(c.z for c in zs), max(c.z for c in zs))
order = sorted(range(len(islands)), key=lambda k: -len(islands[k]))
BODYI = order[0]; HEADI = order[1]; ARMI = [k for k in order if box(k)[0] > 0.15 or box(k)[1] < -0.15][:2]
EYEI = [k for k in order[2:] if k not in ARMI and abs((box(k)[0] + box(k)[1]) / 2) > 0.01]
MOUTHI = [k for k in order[2:] if k not in ARMI and k not in EYEI]
hb_ = box(HEADI)
eye_z = sum(V[i].co.z for k in EYEI for i in islands[k]) / sum(len(islands[k]) for k in EYEI)
eye_x = sum(abs(V[i].co.x) for k in EYEI for i in islands[k]) / sum(len(islands[k]) for k in EYEI)
mouth_z = 1.624
front = [V[i].co for i in islands[HEADI] if abs(V[i].co.x) < 0.02 and V[i].co.y < -0.05]
chin_z = min(c.z for c in front)
top_z = hb_[5]
print('MODEL head', [round(x, 3) for x in hb_], 'eye z/x', round(eye_z, 3), round(eye_x, 3), 'mouth', round(mouth_z, 3), 'chin', round(chin_z, 3))
# canonical landmarks of our painted face, and the model's
ZM = [1.45, chin_z, mouth_z, eye_z, top_z]; ZCAN = [1.45, 1.57, 1.6175, 1.6865, 1.815]
def pl(z, A, B):
    if z <= A[0]: return z - A[0] + B[0]
    for a0, a1, b0, b1 in zip(A, A[1:], B, B[1:]):
        if z <= a1: return b0 + (b1 - b0) * (z - a0) / (a1 - a0)
    return B[-1] + (z - A[-1]) * (B[-1] - B[-2]) / (A[-1] - A[-2])
Zm2c = lambda z: pl(z, ZM, ZCAN); Zc2m = lambda z: pl(z, ZCAN, ZM)
KX = 0.0338 / eye_x
C = Vector((0, (hb_[2] + hb_[3]) / 2 + 0.01, (eye_z + 0.005)))
# ---------- weld: the source model's arms, head and eyes are separate shells that overlap the torso, so seams
# opened whenever the body changed shape. Rebuild it as one closed surface, then bring it back to a low count.
tris0 = sum(len(p.vertices) - 2 for p in body.data.polygons)
rm = body.modifiers.new('Weld', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = 0.006; rm.adaptivity = 0.0; rm.use_smooth_shade = True
with bpy.context.temp_override(object=body, active_object=body): bpy.ops.object.modifier_apply(modifier='Weld')
tris1 = sum(len(p.vertices) - 2 for p in body.data.polygons)
sm_ = body.modifiers.new('Calm', 'LAPLACIANSMOOTH'); sm_.iterations = 6; sm_.lambda_factor = 0.6; sm_.use_volume_preserve = True; sm_.use_normalized = True
with bpy.context.temp_override(object=body, active_object=body): bpy.ops.object.modifier_apply(modifier='Calm')
dm = body.modifiers.new('Dec', 'DECIMATE'); dm.ratio = 9000 / tris1
with bpy.context.temp_override(object=body, active_object=body): bpy.ops.object.modifier_apply(modifier='Dec')
sm2 = body.modifiers.new('Even', 'SMOOTH'); sm2.factor = 0.35; sm2.iterations = 2
with bpy.context.temp_override(object=body, active_object=body): bpy.ops.object.modifier_apply(modifier='Even')
for p in body.data.polygons: p.use_smooth = True
V = body.data.vertices
_b = bmesh.new(); _b.from_mesh(body.data)
print('WELD tris', tris0, '->', tris1, '->', sum(len(p.vertices) - 2 for p in body.data.polygons), 'open edges', sum(1 for e in _b.edges if e.is_boundary)); _b.free()
islands = find_islands(); print('pieces after weld', len(islands), sorted(len(k) for k in islands)[-4:])
if RACE == 'female':   # more triangles over the bust, so it rounds smoothly
    _b = bmesh.new(); _b.from_mesh(body.data)
    _e = [e for e in _b.edges if all(1.2 < v.co.z < 1.37 and 0.0 < abs(v.co.x) < 0.15 and v.co.y < 0.0 for v in e.verts)]
    bmesh.ops.subdivide_edges(_b, edges=_e, cuts=1, use_grid_fill=True, smooth=0.5)
    bmesh.ops.triangulate(_b, faces=[f for f in _b.faces if len(f.verts) > 4])
    _b.to_mesh(body.data); _b.free(); V = body.data.vertices
    print('BUST subdivided edges', len(_e), 'tris', sum(len(p.vertices) - 2 for p in body.data.polygons))
isarm = lambda c: abs(c.x) > 0.185 and 0.6 < c.z < 1.47
# ---------- 3. the head surface, found by raycasting the model's head (for hair and beards)
from mathutils.bvhtree import BVHTree
hbm = bmesh.new(); hbm.from_mesh(body.data); hbm.verts.ensure_lookup_table()
keep = set(i for i in range(len(V)) if V[i].co.z > 1.45 and math.hypot(V[i].co.x, V[i].co.y - C.y) < 0.135)
bmesh.ops.delete(hbm, geom=[v for v in hbm.verts if v.index not in keep], context='VERTS')
HBVH = BVHTree.FromBMesh(hbm)
ZB, ZT = 1.47, top_z
def head_point(th, ph):
    z = ZB + (ZT - ZB) * (ph + 1) / 2
    if z >= ZT - 0.004: return Vector((0, C.y, ZT))
    d = Vector((math.sin(th), -math.cos(th), 0)); o = Vector((C.x, C.y, z)) + d * 0.4
    hit = HBVH.ray_cast(o, -d, 0.45)
    if hit[0] is None: return Vector((C.x, C.y, z)) + d * 0.02
    return hit[0].copy()
def head_r(d):
    d = d.normalized(); hit = HBVH.ray_cast(C + d * 0.4, -d, 0.45)
    return 0.4 - hit[3] if hit[0] is not None else 0.09

# ---------- body types as blend shapes on the one body: Lean and Heavy (the base is Heroic). The head never changes.
SEGS = []
for nm, h, t, par in g['BONES']:
    if nm in ('head',): continue
    SEGS.append((nm, Vector(h), Vector(t)))
def nearest_seg(co, arm_ok=True):   # arm_ok False: a torso point never belongs to a nearby arm
    best = None
    for nm, h, t in SEGS:
        if not arm_ok and nm.startswith(('shoulder', 'upper_arm', 'forearm', 'hand')): continue
        d = t - h; u = max(0.0, min(1.0, (co - h).dot(d) / d.length_squared)); q = h + d * u; dist = (co - q).length
        if best is None or dist < best[0]: best = (dist, nm, q, u)
    return best
TORSO = ('hips', 'spine', 'chest', 'neck')
def region_scale(nm, u, z, co, lean):
    if nm in TORSO:  return (0.74, 0.76) if lean else (1.14, 1.2)          # heavy: bulk in the body,
    if nm.startswith('shoulder'): return (0.72, 0.74) if lean else (1.06, 1.06)   # not in the arms
    if nm.startswith('upper_arm'): return (0.66, 0.66) if lean else (1.1, 1.1)
    if nm.startswith('forearm'): return (0.7, 0.7) if lean else (1.08, 1.08)
    if nm.startswith('hand'): return (0.85, 0.85) if lean else (1.04, 1.04)
    if nm.startswith('thigh'): return (0.76, 0.78) if lean else (1.18, 1.18)
    if nm.startswith('shin'): return (0.8, 0.8) if lean else (1.12, 1.12)
    return (0.9, 0.9) if lean else (1.06, 1.06)
ARMV = set(i for i in range(len(V)) if isarm(V[i].co))
# ---------- bare feet: the source model wears boots; pull them in to feet and ankles
for v in body.data.vertices:
    x, y, z = v.co; s_ = 1 if x > 0 else -1
    if z < 0.12:
        cx, cy = 0.15 * s_, -0.02
        v.co.x = cx + (x - cx) * 0.546; v.co.y = cy + (y - cy) * 0.8
        if z > 0.02: v.co.z = 0.02 + (z - 0.02) * 0.8
    elif z < 0.36:
        k = 0.74 + 0.26 * sm(0.12, 0.36, z); cx, cy = 0.125 * s_, 0.045
        v.co.x = cx + (x - cx) * k; v.co.y = cy + (y - cy) * k
# ---------- per-people proportions. The mesh is reshaped and the rig refitted to it; paint still uses the original layout.
ORIG = [v.co.copy() for v in body.data.vertices]
ZM0, KX0, C0 = list(ZM), KX, C.copy()
Zm2c0 = lambda z: pl(z, ZM0, ZCAN)
RACES = {  # leg length, neck length, head size, shoulder shift, torso width/depth bumps (z, spread, amount), limb thickness
  'ferrin': dict(KL=0.7, KN=0.55, HS=1.04, SHX=0.031, W=[(1.25, 0.17, 0.2), (1.05, 0.1, 0.08)], D=[(1.18, 0.2, 0.28)], D0=1.0, W0=1.0, belly=0.035,
                 ARM={'shoulder': 1.15, 'upper_arm': 1.25, 'forearm': 1.45, 'hand': 1.4}, LEG=1.22, LEGX=1.05),
  'ilvari': dict(KL=1.07, KN=0.9, HS=0.98, SHX=-0.026, W=[(1.42, 0.06, 0.0), (1.33, 0.08, -0.08), (1.28, 0.1, -0.12), (1.1, 0.08, -0.2), (1.02, 0.045, -0.05), (0.97, 0.07, -0.12)], D=[(1.2, 0.2, -0.05)], D0=0.84, W0=0.96, belly=-0.012,
                 ARM={'shoulder': 0.9, 'upper_arm': 0.76, 'forearm': 0.78, 'hand': 0.84}, LEG=0.82, LEGX=0.96),
  'female': dict(KL=1.035, KN=0.6, HS=0.93, SHX=-0.052, W=[(1.5, 0.05, -0.18), (1.465, 0.035, -0.16), (1.4, 0.06, -0.15), (1.3, 0.07, -0.17), (1.2, 0.07, -0.22), (1.12, 0.06, -0.33), (1.04, 0.05, -0.14), (0.93, 0.06, 0.12)],
                 D=[(1.1, 0.1, -0.12), (1.25, 0.09, -0.07), (1.33, 0.07, -0.13), (1.42, 0.05, -0.06)], D0=0.92, W0=0.95, belly=-0.012,
                 ARM={'shoulder': 0.76, 'upper_arm': 0.58, 'forearm': 0.54, 'hand': 0.58}, LEG=0.8, LEGX=1.02, FEM=True, UCK=0.8),
  'zarhim': dict(KL=1.03, KN=1.1, HS=1.0, SHX=-0.008, W=[(1.28, 0.1, -0.04), (1.1, 0.08, -0.14), (0.97, 0.07, -0.06)], D=[(1.2, 0.2, -0.03)], D0=0.9, W0=0.98, belly=-0.008,
                 ARM={'shoulder': 0.95, 'upper_arm': 0.86, 'forearm': 0.88, 'hand': 0.92}, LEG=0.88, LEGX=0.98),
}
if RACE in RACES:
    P_ = RACES[RACE]
    HIP, KL, NECK0, NECK1, KN, HS = 0.92, P_['KL'], 1.45, 1.556, P_['KN'], P_['HS']
    DZ = HIP * (1 - KL)
    LEGB = ('thigh', 'shin', 'foot')
    SEGS0 = [(bn, Vector(bh), Vector(bt)) for bn, bh, bt, bp in g['BONES']]
    def seg_of(co, arm_ok=True):
        best = None
        for nm, h, t in SEGS0:
            if not arm_ok and nm.startswith(('shoulder', 'upper_arm', 'forearm', 'hand')): continue
            d = t - h; u = max(0.0, min(1.0, (co - h).dot(d) / d.length_squared)); q = h + d * u; dist = (co - q).length
            if best is None or dist < best[0]: best = (dist, nm, q)
        return best
    def torso_w(z):
        return (P_['W0'] + sum(a * math.exp(-((z - c) / w) ** 2) for c, w, a in P_['W']),
                P_['D0'] + sum(a * math.exp(-((z - c) / w) ** 2) for c, w, a in P_['D']))
    SHX = P_['SHX']
    UC0, UCK = 1.34, P_.get('UCK', 1.0)   # upper chest, from the top of the bust to the neck: shortened by UCK
    def zmap(z):  # above the hips: lowered; the upper chest and the neck shortened
        z = z - DZ
        u0 = UC0 - DZ; n0, n1 = NECK0 - DZ, NECK1 - DZ
        if z <= u0: return z
        if z <= n0: return u0 + (z - u0) * UCK
        n0b = u0 + (n0 - u0) * UCK
        if z <= n1: return n0b + (z - n0) * KN
        return n0b + (n1 - n0) * KN + (z - n1) * HS
    def F(co, nm, q):
        x, y, z = co; s_ = 1 if x >= 0 else -1
        if nm.startswith(LEGB) and not (nm.startswith('thigh') and z > HIP + 0.02):
            cx, cy = 0.115 * s_, 0.03
            return Vector((cx * P_['LEGX'] + (x - cx) * P_['LEG'], cy + (y - cy) * P_['LEG'], z * KL))
        if nm.startswith(('shoulder', 'upper_arm', 'forearm', 'hand')):
            k = P_['ARM'][nm.split('.')[0]]
            off = co - q; qn = Vector((q.x + s_ * SHX, q.y, zmap(q.z)))
            return qn + off * k
        if z > NECK1:  # the head keeps its size
            if P_.get('FEM'):   # softer face, after WoW's elf women: tapered jaw, small pointed chin, a little width at the cheekbones
                ax_ = abs(x)
                x *= 1 - 0.085 * sm(1.665, 1.575, z) - 0.05 * sm(1.62, 1.565, z) * sm(0.02, 0.065, ax_)                      + 0.018 * math.exp(-((z - 1.665) / 0.018) ** 2) * sm(0.04, 0.07, ax_)
                if z < 1.6: z = z + 0.006 * sm(1.6, 1.56, z)                       # a slightly shorter lower face
                if y < -0.07 and ax_ < 0.022 and 1.635 < z < 1.715:                 # a smaller nose
                    y += 0.004 * math.exp(-((z - 1.665) / 0.03) ** 2) * (1 - ax_ / 0.022)
            return Vector((x * HS, C.y + (y - C.y) * HS, zmap(z)))
        wx, wy = torso_w(z)
        out = Vector((x * wx, 0.004 + (y - 0.004) * wy - P_['belly'] * math.exp(-((z - 1.1) / 0.1) ** 2) * (y < 0.02) * math.exp(-(x / 0.12) ** 2), zmap(z)))
        return out
    for v in body.data.vertices:
        d, nm, q = seg_of(v.co, RACE != 'female' or v.index in ARMV); v.co = F(v.co.copy(), nm, q)
    if RACE in ('ferrin', 'female'):   # each part is reshaped differently; blend the change across the joins so they don't form spikes
        nb = [[] for _ in body.data.vertices]
        for e in body.data.edges: a_, b_ = e.vertices; nb[a_].append(b_); nb[b_].append(a_)
        D = [body.data.vertices[i].co - ORIG[i] for i in range(len(ORIG))]
        fix = [ORIG[i].z > NECK1 + 0.02 and abs(ORIG[i].x) < 0.13 for i in range(len(ORIG))]
        for _ in range(12):
            D = [D[i] if fix[i] or not nb[i] else D[i] * 0.4 + sum((D[j] for j in nb[i]), Vector()) * (0.6 / len(nb[i])) for i in range(len(D))]
        for i, v in enumerate(body.data.vertices): v.co = ORIG[i] + D[i]
    if P_.get('FEM'):   # a feminine midsection: rounded cross-sections, the ribcage tapering into a slim waist, then the hips
        PROF = [(0.95, 0.152, 0.086, 0.104), (1.0, 0.13, 0.079, 0.093), (1.05, 0.112, 0.074, 0.084), (1.1, 0.104, 0.072, 0.081),
                (1.15, 0.11, 0.076, 0.086), (1.2, 0.123, 0.086, 0.094), (1.26, 0.136, 0.1, 0.104)]
        def prof(z):
            z = min(max(z, PROF[0][0]), PROF[-1][0])
            for r0, r1 in zip(PROF, PROF[1:]):
                if z <= r1[0]:
                    t = (z - r0[0]) / (r1[0] - r0[0]); t = t * t * (3 - 2 * t)
                    return [a_ + (b_ - a_) * t for a_, b_ in zip(r0[1:], r1[1:])]
        CY = 0.008
        for i, v in enumerate(body.data.vertices):
            if i in ARMV: continue
            x, y, z = v.co
            if not (0.93 < z < 1.28) or abs(x) > 0.23: continue
            if z > 1.2 and y < -0.02 and abs(x) < 0.15: continue          # leave the bust to its own step
            a_, f_, b_ = prof(z); dep = f_ if y < CY else b_
            th = math.atan2(x, -(y - CY)); sx_, cy_ = math.sin(th), -math.cos(th)
            n = 2.3; r = 1 / ((abs(sx_) / a_) ** n + (abs(cy_) / dep) ** n) ** (1 / n)
            w = sm(0.93, 0.98, z) * (1 - sm(1.24, 1.28, z)) * 0.8
            tx, ty = sx_ * r, CY + cy_ * r
            v.co.x = x + (tx - x) * w; v.co.y = y + (ty - y) * w
    if P_.get('FEM'):   # the bust, after the blending so it keeps its shape: full and rounded on a flattened chest
        for i, v in enumerate(body.data.vertices):
            x, y, z = ORIG[i]
            ax = abs(x)
            if 1.38 < z < 1.56 and 0.035 < ax < 0.24:   # small traps: a gentle slope from the neck to the shoulder
                t = math.exp(-((ax - 0.11) / 0.06) ** 2) * math.exp(-((z - 1.465) / 0.045) ** 2)
                v.co.z -= 0.038 * t; v.co.x -= math.copysign(0.008, x) * t
            if y > 0.03 or abs(x) > 0.2: continue
            # a rounded dome, fuller in its lower half, easing into the chest at its rim
            dz = z - 1.278; ry = 0.062 if dz > 0 else 0.052
            d = math.sqrt(((ax - 0.077) / 0.06) ** 2 + (dz / ry) ** 2)
            if d < 1.35:
                dome = (1 - min(d, 1.0) ** 2) ** 0.55 if d < 1 else 0.0
                rim = math.exp(-((d - 0.95) / 0.18) ** 2) * 0.18
                k = max(dome, rim) * (1 - sm(1.15, 1.35, d))
                v.co.y -= 0.072 * k
                v.co.z -= 0.01 * k * (1 if dz < 0 else 0.4)
                v.co.x += math.copysign(0.01, x) * k * (ax - 0.04) / 0.06
        # a real neck: the shoulder line slopes gently down from beside the neck, well below the chin
        reg = []
        for i, v in enumerate(body.data.vertices):
            ax = abs(v.co.x); z = v.co.z
            if not (1.3 < z < 1.58 and 0.045 < ax < 0.27 and abs(v.co.y) < 0.13): continue
            L = 1.455 - (ax - 0.06) * 0.32
            w = sm(0.045, 0.08, ax) * (1 - sm(0.22, 0.27, ax))
            if z > L: v.co.z = z - (z - L) * 0.7 * w
            reg.append(i)
        nb2 = [[] for _ in body.data.vertices]
        for e in body.data.edges: a_, b_ = e.vertices; nb2[a_].append(b_); nb2[b_].append(a_)
        soft = [i for i, c in enumerate(ORIG) if 0.13 < c.z < 1.47 and not (c.z < 0.97 and i in ARMV) and nb2[i]]   # softer forms all over
        for _ in range(3):
            new = {i: sum((body.data.vertices[j].co for j in nb2[i]), Vector()) / len(nb2[i]) for i in soft}
            for i, c_ in new.items(): body.data.vertices[i].co = body.data.vertices[i].co * 0.7 + c_ * 0.3
        bust = [i for i, c in enumerate(ORIG) if 1.2 < c.z < 1.37 and abs(c.x) < 0.16 and c.y < 0.0 and i not in ARMV and nb2[i]]
        for _ in range(3):
            new = {i: sum((body.data.vertices[j].co for j in nb2[i]), Vector()) / len(nb2[i]) for i in bust}
            for i, c_ in new.items(): body.data.vertices[i].co = body.data.vertices[i].co * 0.6 + c_ * 0.4
        for i, c in enumerate(ORIG):   # a slender neck: the column drawn in toward its centre
            if not (1.43 < c.z < 1.575) or math.hypot(c.x, c.y - 0.01) > 0.09 or i in ARMV: continue
            w = sm(1.43, 1.47, c.z) * (1 - sm(1.545, 1.575, c.z)) * 0.2
            v = body.data.vertices[i]; v.co.x *= 1 - w; v.co.y = 0.01 + (v.co.y - 0.01) * (1 - w)
        armreg = [i for i in ARMV if 0.97 < ORIG[i].z < 1.44 and nb2[i]]   # smoother arms: soften the muscle forms (not the hands)
        pit = [i for i, c in enumerate(ORIG) if 1.12 < c.z < 1.43 and 0.11 < abs(c.x) < 0.24 and nb2[i]]   # armpit and lats: blend the side of the chest into the arm
        for _ in range(6):
            new = {i: sum((body.data.vertices[j].co for j in nb2[i]), Vector()) / len(nb2[i]) for i in pit}
            for i, c_ in new.items(): body.data.vertices[i].co = body.data.vertices[i].co * 0.5 + c_ * 0.5
        for _ in range(4):
            new = {i: sum((body.data.vertices[j].co for j in nb2[i]), Vector()) / len(nb2[i]) for i in armreg}
            for i, c_ in new.items(): body.data.vertices[i].co = body.data.vertices[i].co * 0.55 + c_ * 0.45
        for _ in range(3):
            new = {i: sum((body.data.vertices[j].co for j in nb2[i]), Vector()) / len(nb2[i]) for i in reg if nb2[i]}
            for i, c_ in new.items(): body.data.vertices[i].co = body.data.vertices[i].co * 0.6 + c_ * 0.4
    sm3 = body.modifiers.new('Settle', 'SMOOTH'); sm3.factor = 0.4; sm3.iterations = 3
    with bpy.context.temp_override(object=body, active_object=body): bpy.ops.object.modifier_apply(modifier='Settle')
    # refit the rig to the new shape
    bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
    eb = arm.data.edit_bones
    def Fj(p, nm):
        p = Vector(p); s_ = 1 if p.x >= 0 else -1
        if nm.startswith(LEGB): return Vector((0.115 * s_ * P_['LEGX'] + (p.x - 0.115 * s_) * P_['LEG'], p.y, p.z * KL)) if p.z < HIP + 0.02 else Vector((p.x, p.y, p.z - DZ))
        if nm.startswith(('shoulder', 'upper_arm', 'forearm', 'hand')): return Vector((p.x + s_ * SHX * (abs(p.x) > 0.05), p.y, zmap(p.z)))
        return Vector((p.x, p.y, zmap(p.z)))
    newB = []
    for nm, h, t, par in g['BONES']:
        hh, tt = Fj(h, nm), Fj(t, nm)
        eb[nm].head = hh; eb[nm].tail = tt; newB.append((nm, tuple(hh), tuple(tt), par))
    for nm, h, t, par in newB:   # keep children attached to their parents
        if par and nm in eb and par in eb and (eb[nm].head - eb[par].tail).length < 0.03: eb[nm].head = eb[par].tail
    g['BONES'][:] = [(nm, tuple(eb[nm].head), tuple(eb[nm].tail), par) for nm, h, t, par in g['BONES']]
    REST_ARM = {sd: [eb[f'upper_arm.{sd}'].tail.copy(), eb[f'forearm.{sd}'].tail.copy(), eb[f'hand.{sd}'].tail.copy()] for sd in ('L', 'R')}
    bpy.ops.object.mode_set(mode='OBJECT'); upd()
    SEGS[:] = [(nm, Vector(h), Vector(t)) for nm, h, t, par in g['BONES'] if nm != 'head']
    # the head moved: landmarks, mapping and the raycast surface follow
    ZM = [zmap(z) if z > NECK1 else zmap(z) for z in ZM0]; ZM[0] = zmap(1.45)
    eye_x = eye_x * HS; KX = 0.0338 / eye_x; C = Vector((0, C0.y, zmap(C0.z))); top_z = zmap(top_z)
    hbm = bmesh.new(); hbm.from_mesh(body.data); hbm.verts.ensure_lookup_table()
    bmesh.ops.delete(hbm, geom=[v for v in hbm.verts if not (v.co.z > ZM[0] and math.hypot(v.co.x, v.co.y - C.y) < 0.14)], context='VERTS')
    HBVH = BVHTree.FromBMesh(hbm); ZB, ZT = ZM[0] + 0.02, top_z
    print(RACE.upper(), 'height', round(max(v.co.z for v in body.data.vertices), 3), 'eye', round(ZM[3], 3))
body.shape_key_add(name='Basis')
KEYS = {}
for kname, lean in (('Lean', True), ('Heavy', False)):
    kb = body.shape_key_add(name=kname, from_mix=False); KEYS[kname] = kb
    for v in body.data.vertices:
        co = v.co.copy()
        if co.z > 1.535 and abs(co.x) < 0.12: kb.data[v.index].co = co; continue      # the head stays as it is
        dist, nm, q, u = nearest_seg(co, RACE != 'female' or v.index in ARMV)
        sx_, sy_ = region_scale(nm, u, co.z, co, lean)
        off = co - q
        if nm in TORSO: off = Vector((co.x - 0.0, co.y - 0.004, 0)); q = Vector((0, 0.004, co.z))
        w = 1.0 if nm not in ('neck',) else sm(1.535, 1.46, co.z)                      # fade out under the jaw
        new_ = q + Vector((off.x * (1 + (sx_ - 1) * w), off.y * (1 + (sy_ - 1) * w), off.z * (1 + (sx_ - 1) * w * 0.6)))
        if not lean:
            ax_ = abs(co.x)
            new_.y -= 0.06 * math.exp(-(ax_ / 0.11) ** 2 - ((co.z - 1.13) / 0.11) ** 2) * (co.y < 0.02)   # a belly
            new_.x += math.copysign(0.018, co.x) * math.exp(-((co.z - 1.1) / 0.09) ** 2) * (nm in TORSO)  # love handles
            new_.z += 0.012 * math.exp(-((ax_ - 0.11) / 0.06) ** 2 - ((co.z - 1.47) / 0.04) ** 2)        # bigger traps
        else:
            if v.index in ARMV: new_.x -= math.copysign(0.018, co.x) * sm(0.6, 1.2, co.z)   # arms come in with the narrower chest
            new_.z -= 0.008 * math.exp(-((abs(co.x) - 0.11) / 0.06) ** 2 - ((co.z - 1.47) / 0.04) ** 2)   # flatter traps
        kb.data[v.index].co = new_
# smooth each shape over the surface, so neighbouring parts blend instead of creasing where they meet
NB = [[] for _ in body.data.vertices]
for e in body.data.edges: a_, b_ = e.vertices; NB[a_].append(b_); NB[b_].append(a_)
basis = [v.co.copy() for v in body.data.vertices]
fixed = [c.z > 1.535 and abs(c.x) < 0.12 for c in basis]
for kname in ('Lean', 'Heavy'):
    kb = KEYS[kname]; D = [kb.data[i].co - basis[i] for i in range(len(basis))]
    for _ in range(8):
        D = [Vector((0, 0, 0)) if fixed[i] else (D[i] * 0.4 + sum((D[j] for j in NB[i]), Vector((0, 0, 0))) * (0.6 / len(NB[i])) if NB[i] else D[i]) for i in range(len(D))]
    for i in range(len(D)): kb.data[i].co = basis[i] + D[i]
print('SHAPE KEYS', [k.name for k in body.data.shape_keys.key_blocks])
# ---------- hair and beards: real volumes grown from the head surface, shaped into locks
HL = [(0.0, 1.768), (0.5, 1.77), (1.0, 1.742), (1.35, 1.698), (1.6, 1.658), (2.45, 1.618), (math.pi, 1.604)]   # forehead and temples clear
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
def ph_at_m(th, z, lo=-0.98, hi=0.999):  # the latitude on the head at which the surface reaches height z
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
def ph_at(th, z): return ph_at_m(th, Zc2m(z))
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
beard_top = lambda th: 1.648 - 0.02 * sm(1.0, 0.3, abs(th)) - 0.026 * fw(th, 0.32)   # below the cheekbones   # sideburns, cheeks, under the lip
beard_jaw = lambda th: 1.576 - 0.004 * fw(th)
bthick = lambda th, z: 0.0035 + 0.009 * fw(th, 0.9) * sm(1.63, 1.59, z)   # hugs the jaw
def beard(name, Lmax, shape, conv, depth=0.03):
    return solid(name, -1.38, 1.38, beard_top, beard_jaw, bthick, lambda th: Lmax * shape(th), conv, lambda th: depth * fw(th, 0.8) + 0.006)
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
def stache(name, ends_down, width, thick, curl=0.0, top=1.638):
    ob = solid(name, -width, width, lambda th: top - 0.004 * sm(0.1, width, abs(th)), lambda th: 1.624 - 0.012 * sm(0.18, width, abs(th)),
               lambda th, z: thick + 0.004 * fw(th, 0.3), lambda th: ends_down * sm(width * 0.5, width, abs(th)), 0.0, lambda th: thick + 0.002, NT=14, NF=4, NS=5, fwd=0.004)
    if curl:  # handlebar: the ends sweep out and up
        bm = bmesh.new()
        for sx in (1, -1):
            a0 = head_point(width * sx, ph_at(width * sx, 1.62)); n = (a0 - C); n.z = 0; n = n.normalized()
            pts = [a0 + n * 0.006 + Vector((0.006 * sx * k, -0.002 * k, curl * (k / 4) ** 1.6)) for k in range(5)]
            tube(bm, pts, 0.006, 0.0025, 6, 0.8)
        ob = join(ob, as_object('_curl', bm))
    return ob
HAIRS.append(stache('Moustache_Chevron', 0.01, 0.42, 0.0045))
HAIRS.append(stache('Moustache_Horseshoe', 0.04, 0.44, 0.004))
HAIRS.append(stache('Moustache_Walrus', 0.018, 0.5, 0.008, top=1.641))
HAIRS.append(stache('Moustache_Handlebar', 0.002, 0.38, 0.0045, curl=0.01))
HAIRS.append(stache('Moustache_Pencil', 0.0, 0.3, 0.002, top=1.634))
# hair: a solid cap with volume, a few chunky points at the hairline, strands painted on
def cap(name, lower, thick, notch_k=6, notch=0.01, droop=lambda th, f: 0.0, NR=12):
    return shell(name, -math.pi, math.pi, lambda th: hairline(th) - lower(th) - notch * tri(th * notch_k / math.pi), TOP, thick, droop, NT=40, NR=NR, wrap=True)
HAIRS.append(cap('Hair_Short', lambda th: 0.002, lambda th, f, p: 0.0035 + 0.011 * f ** 1.3, 7, 0.006))
HAIRS.append(cap('Hair_Swept', lambda th: 0.003, lambda th, f, p: 0.003 + 0.028 * f ** 1.4 * (1 + 0.3 * fw(th, 0.8) * f), 5, 0.009))
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

for ob in HAIRS:   # hair never hangs in front of the face below the eyes: drop any stray points the fitting threw there
    if not ob.name.startswith('Hair_'): continue
    _b = bmesh.new(); _b.from_mesh(ob.data)
    _k = [v for v in _b.verts if (v.co.y < C.y - 0.06 and v.co.z < C.z - 0.06) or (v.co - C).length > 0.36]
    if _k: bmesh.ops.delete(_b, geom=_k, context='VERTS'); print(ob.name, 'removed stray', len(_k))
    _b.to_mesh(ob.data); _b.free()
for ob in HAIRS:
    ob.data.materials.append(bpy.data.materials.new(ob.name))
    ca = ob.data.color_attributes.new('rest', 'FLOAT_COLOR', 'POINT')
    for v in ob.data.vertices: ca.data[v.index].color = (v.co.x + 0.5, v.co.y + 0.5, v.co.z / 2, 1)
    ob.data.color_attributes.active_color = ca
# ---------- rest position: where each point sits on OUR painted body, so the same paint fits this model
me = body.data
ca = me.color_attributes.new('rest', 'FLOAT_COLOR', 'POINT')
armset = set(i for i in range(len(me.vertices)) if isarm(ORIG[i]))
for v in me.vertices:
    x, y, z = ORIG[v.index]                       # paint follows the original body, whatever shape it took
    if z > 1.47 and v.index not in armset:      # blend from body space into the face layout up the neck
        t = sm(1.47, 1.555, z)
        x = x + (x * KX0 - x) * t; y = y + ((y - C0.y) * KX0 + 0.004 - y) * t; z = z + (Zm2c0(z) - z) * t
    ca.data[v.index].color = (x + 0.5, y + 0.5, z / 2, 0.0 if v.index in armset else 1.0)   # alpha: 0 on the arms
me.color_attributes.active_color = ca
mat = bpy.data.materials.new('Body'); me.materials.append(mat)

# ---------- skin it to the rig
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True); bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
print('GROUPS', len(body.vertex_groups))
# alpha of the rest colour: how much each point belongs to the torso (not the upper arm, forearm or hand), from the skin weights
_arm = {body.vertex_groups[n].index for n in ('upper_arm.L', 'upper_arm.R', 'forearm.L', 'forearm.R', 'hand.L', 'hand.R') if n in body.vertex_groups}
_ca = body.data.color_attributes['rest']
for v in body.data.vertices:
    tot = sum(gv.weight for gv in v.groups) or 1.0; aw = sum(gv.weight for gv in v.groups if gv.group in _arm) / tot
    c_ = _ca.data[v.index].color; _ca.data[v.index].color = (c_[0], c_[1], c_[2], max(0.0, min(1.0, 1.0 - aw)))
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
        ws = {gv.group: gv.weight for gv in v.groups if gv.group in keep}; tot = sum(ws.values())
        for gv in list(v.groups):
            if gv.group not in keep: ob.vertex_groups[gv.group].remove([v.index])
        if tot < 1e-4: ob.vertex_groups[hi].add([v.index], 1.0, 'REPLACE')
        else:
            for gi, w in ws.items(): ob.vertex_groups[gi].add([v.index], w / tot, 'REPLACE')
    ob.modifiers.new('Armature', 'ARMATURE').object = arm; ob.parent = arm
    print(ob.name, 'groups', len(ob.vertex_groups))
# ---------- Valheim-style idle and walk: chest up, arms hanging out and down, fists by the thighs
for a_ in list(bpy.data.actions):
    if a_.name in ('Idle', 'Walk', 'Aim'): bpy.data.actions.remove(a_)
pose, bake = g['pose'], g['bake']
def arms(sw=0.0, br=0.0):
    out = []
    for sx, side in ((1, 'L'), (-1, 'R')):
        k = sw * (1 if side == 'L' else -1)
        e, w, h = REST_ARM[side]
        out += [(f'upper_arm.{side}', (e[0] + 0.01 * sx, e[1] + 0.07 * k, e[2] + br)),
                (f'forearm.{side}', (w[0] - 0.01 * sx, w[1] + 0.14 * k - 0.04 * abs(sw), w[2] + br + 0.01)),
                (f'hand.{side}', (h[0] - 0.015 * sx, h[1] + 0.18 * k - 0.05 * abs(sw), h[2] + br + 0.02))]
    return out
def idle2(f):
    ph = 2 * math.pi * f / 48; b = math.sin(ph)
    d = {'spine': (-0.02, 0, 0), 'chest': (-0.07 + 0.015 * b, 0, 0), 'neck': (0.07 - 0.012 * b, 0, 0), 'head': (0.01, 0, 0.04 * math.sin(ph * 0.5)),
         'thigh.L': (0.07, -0.07, 0), 'thigh.R': (0.07, -0.07, 0), 'shin.L': (-0.13, 0, 0), 'shin.R': (-0.13, 0, 0), 'foot.L': (0.06, 0.05, 0), 'foot.R': (0.06, 0.05, 0)}
    return d, -0.012 - 0.004 * (1 - math.cos(ph)) / 2, arms(0.0, 0.004 * b)
def walk2(f):
    ph = 2 * math.pi * f / 24; s, c = math.sin(ph), math.cos(ph)
    d = {'thigh.L': (0.5 * s, -0.03, 0), 'thigh.R': (-0.5 * s, -0.03, 0),
         'shin.L': (-(0.1 + 0.75 * max(0, c)), 0, 0), 'shin.R': (-(0.1 + 0.75 * max(0, -c)), 0, 0),
         'foot.L': (0.25 * max(0, -s) - 0.15 * max(0, s), 0, 0), 'foot.R': (0.25 * max(0, s) - 0.15 * max(0, -s), 0, 0),
         'hips': (0, 0, -0.08 * s), 'spine': (0.03, 0, 0.08 * s), 'chest': (-0.04, 0, 0.07 * s), 'neck': (0.03, 0, -0.1 * s)}
    return d, -0.03 * (1 - abs(c)), arms(s, 0.008 * abs(c))
arm.data.pose_position = 'POSE'
bake('Idle', range(0, 49, 4), idle2)
bake('Walk', range(0, 25, 2), walk2)
arm.animation_data.action = None; pose({})
arm.data.pose_position = 'POSE'
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True)
for ob in HAIRS: ob.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
                          export_skins=True, export_materials='EXPORT', export_force_sampling=True, export_vertex_color='ACTIVE')
print('EXPORTED', OUT)
