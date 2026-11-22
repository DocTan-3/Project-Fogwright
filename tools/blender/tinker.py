# Fogwright: light Tinker. Builds body, rig, gear and animations, exports tinker.glb
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

OUT = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 24
col = scene.collection

def T(x, y, z): return Matrix.Translation((x, y, z))
def R(axis, a): return Matrix.Rotation(a, 4, axis)
def S(x, y, z): return Matrix.Diagonal((x, y, z, 1))
def upd(): bpy.context.view_layer.update()

# ---------------- materials ----------------
def lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def hexrgb(h):
    h = h.lstrip('#'); return [lin(int(h[i:i+2], 16)) for i in (0, 2, 4)]
def mat(name, hexc, rough=0.75, metal=0.0, emit=None, strength=3.0):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    nt = m.node_tree
    b = nt.nodes.get('Principled BSDF')
    if b is None:
        b = nt.nodes.new('ShaderNodeBsdfPrincipled')
        out = nt.nodes.get('Material Output') or nt.nodes.new('ShaderNodeOutputMaterial')
        nt.links.new(b.outputs[0], out.inputs[0])
    b.inputs['Base Color'].default_value = (*hexrgb(hexc), 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = (*hexrgb(emit), 1)
        b.inputs['Emission Strength'].default_value = strength
    return m

MT = {
 'skin': mat('Skin', '#c88a64', 0.72), 'hair': mat('Hair', '#3b2a21', 0.9),
 'shirt': mat('Shirt', '#e9e2d4', 0.6), 'shorts': mat('Shorts', '#6f5a43', 0.95), 'vest': mat('Vest', '#6c4a30', 0.8),
 'coat': mat('Coat', '#46525a', 0.85), 'lining': mat('Lining', '#7d2f2c', 0.8),
 'trousers': mat('Trousers', '#4e4842', 0.9), 'boots': mat('Boots', '#3a2a20', 0.7),
 'leather': mat('Leather', '#7e5533', 0.7), 'leatherDark': mat('LeatherDark', '#4c3323', 0.75),
 'brass': mat('Brass', '#c9973f', 0.35, 0.85), 'iron': mat('Iron', '#8d949b', 0.45, 0.8),
 'wood': mat('Wood', '#6f4a2b', 0.7), 'scarf': mat('Scarf', '#8a3a2d', 0.9),
 'eye': mat('Eye', '#1c1613', 0.4), 'glow': mat('Glow', '#5fe6d4', 0.3, 0.0, '#5fe6d4', 4.0),
 'amber': mat('GaugeGlow', '#f0b45a', 0.3, 0.0, '#f0a040', 3.0), 'glass': mat('Glass', '#9fd8d0', 0.15, 0.0, '#7fe0d0', 1.2),
}

# ---------------- bmesh primitives ----------------
def bm_sphere(r, seg=14, ring=10):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=r); return bm
def bm_cyl(r1, r2, h, seg=12):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r1, radius2=r2, depth=h); return bm
def bm_box(x, y, z):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bmesh.ops.scale(bm, vec=(x, y, z), verts=bm.verts); return bm
def bm_torus(Rr, r, seg=18, tseg=6, arc=2 * math.pi):
    bm = bmesh.new(); closed = arc >= 2 * math.pi - 1e-6; n = seg if closed else seg + 1; rows = []
    for i in range(n):
        a = arc * i / seg; d = Vector((math.cos(a), math.sin(a), 0)); c = d * Rr
        rows.append([bm.verts.new(c + d * (math.cos(2 * math.pi * j / tseg) * r) + Vector((0, 0, math.sin(2 * math.pi * j / tseg) * r))) for j in range(tseg)])
    for i in range(seg):
        a, b = rows[i], rows[(i + 1) % n]
        for j in range(tseg):
            bm.faces.new((a[j], b[j], b[(j + 1) % tseg], a[(j + 1) % tseg]))
    return bm
def bm_cap(r, seg=14, ring=8, frac=0.5):
    bm = bm_sphere(r, seg, ring)
    kill = [v for v in bm.verts if v.co.z < r * (1 - 2 * frac) - 1e-6]
    bmesh.ops.delete(bm, geom=kill, context='VERTS'); return bm

def make_obj(name, bm, mats, smooth=True):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    for p in me.polygons: p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me); col.objects.link(ob); return ob

# ---------------- armature ----------------
BONES = [
 ('hips', (0, 0, 0.96), (0, 0, 1.10), None),
 ('spine', (0, 0, 1.10), (0, 0, 1.28), 'hips'),
 ('chest', (0, 0, 1.28), (0, 0, 1.47), 'spine'),
 ('neck', (0, 0, 1.47), (0, 0, 1.60), 'chest'),
 ('head', (0, 0, 1.60), (0, 0, 1.82), 'neck'),
]
for s, sx in (('L', 1), ('R', -1)):
    BONES += [
     (f'shoulder.{s}', (0.03 * sx, 0, 1.44), (0.165 * sx, 0, 1.44), 'chest'),
     (f'upper_arm.{s}', (0.165 * sx, 0, 1.44), (0.27 * sx, 0.01, 1.18), f'shoulder.{s}'),
     (f'forearm.{s}', (0.27 * sx, 0.01, 1.18), (0.355 * sx, 0, 0.94), f'upper_arm.{s}'),
     (f'hand.{s}', (0.355 * sx, 0, 0.94), (0.39 * sx, -0.015, 0.81), f'forearm.{s}'),
     (f'thigh.{s}', (0.095 * sx, 0, 0.92), (0.11 * sx, -0.004, 0.52), 'hips'),
     (f'shin.{s}', (0.11 * sx, -0.004, 0.52), (0.117 * sx, 0.012, 0.08), f'thigh.{s}'),
     (f'foot.{s}', (0.117 * sx, 0.012, 0.08), (0.135 * sx, -0.125, 0.03), f'shin.{s}'),
    ]
arm_data = bpy.data.armatures.new('TinkerRig')
arm = bpy.data.objects.new('Tinker', arm_data); col.objects.link(arm)
bpy.context.view_layer.objects.active = arm; arm.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
for n, h, t, p in BONES:
    eb = arm_data.edit_bones.new(n); eb.head = h; eb.tail = t; eb.roll = 0
    if p: eb.parent = arm_data.edit_bones[p]; eb.use_connect = (Vector(arm_data.edit_bones[p].tail) - Vector(h)).length < 1e-4
bpy.ops.object.mode_set(mode='OBJECT')
SEG = {n: (Vector(h), Vector(t)) for n, h, t, p in BONES}

def seg_dist(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared)); return (a + ab * t - p).length

def skin_to(ob, candidates, custom=None, power=8):
    groups = {n: ob.vertex_groups.new(name=n) for n in SEG}
    for v in ob.data.vertices:
        p = ob.matrix_world @ v.co
        w = custom(p) if custom else None
        if w is None:
            ds = sorted(((seg_dist(p, *SEG[n]) + 1e-4, n) for n in candidates))[:2]
            raw = [(1 / d ** power, n) for d, n in ds]; tot = sum(x for x, _ in raw)
            w = {n: x / tot for x, n in raw}
        for n, x in w.items():
            if x > 0.001: groups[n].add([v.index], x, 'REPLACE')
    md = ob.modifiers.new('Armature', 'ARMATURE'); md.object = arm
    ob.parent = arm

def bone_tail_matrix(name):
    pb = arm.pose.bones[name]
    return arm.matrix_world @ pb.matrix @ T(0, pb.length, 0)

def part(name, bm, m, M, bone, smooth=True):
    if bone == 'head': M = T(0, 0, -0.022) @ M
    if bone in ('thigh.R', 'shin.R'): M = T(-0.008 if bone == 'thigh.R' else -0.013, 0, 0) @ M
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    ob = make_obj(name, bm, [MT[m]], smooth)
    ob.parent = arm; ob.parent_type = 'BONE'; ob.parent_bone = bone
    upd(); ob.matrix_basis = bone_tail_matrix(bone).inverted()
    return ob

# ---------------- body: sculpted from muscle volumes, reduced to low poly ----------------
DEFORM = [n for n, *_ in BONES]
K = 1 / 0.5748  # metaball radius -> surface radius
mbd = bpy.data.metaballs.new('BodyBlob'); mbd.resolution = 0.006; mbd.render_resolution = 0.006; mbd.threshold = 0.6
mbo = bpy.data.objects.new('BodyBlob', mbd); col.objects.link(mbo)
def frame_quat(axis, xhint=None):
    z = Vector(axis).normalized()
    x = Vector(xhint) if xhint else (Vector((1, 0, 0)) if abs(z.x) < 0.9 else Vector((0, 1, 0)))
    x = (x - z * x.dot(z)).normalized(); y = z.cross(x)
    return Matrix((x, y, z)).transposed().to_quaternion()
def blob(c, semi, axis=(0, 0, 1), xhint=None, neg=False, stiff=2.0):
    e = mbd.elements.new(); e.type = 'ELLIPSOID'; e.co = c; e.radius = K
    e.size_x, e.size_y, e.size_z = semi; e.rotation = frame_quat(axis, xhint); e.use_negative = neg; e.stiffness = stiff
    return e
def lerp3(a, b, t): return Vector(a).lerp(Vector(b), t)
def along(a, b, t, off=(0, 0, 0), semi=(0.05, 0.05, 0.1), xhint=None):
    blob(lerp3(a, b, t) + Vector(off), semi, Vector(b) - Vector(a), xhint)
# torso
blob((0, 0.006, 1.305), (0.142, 0.098, 0.15))
blob((0, -0.006, 1.385), (0.158, 0.094, 0.075))
blob((0, -0.022, 1.15), (0.116, 0.074, 0.095))
blob((0, -0.055, 1.17), (0.064, 0.026, 0.085))
blob((0, 0.004, 0.985), (0.138, 0.092, 0.08))
for sx in (1, -1):
    blob((0.072 * sx, -0.068, 1.345), (0.08, 0.042, 0.06))                          # pec
    blob((0.105 * sx, 0.022, 1.26), (0.058, 0.066, 0.12))                            # lat
    blob((0.075 * sx, 0.068, 1.37), (0.066, 0.032, 0.075))                           # scapula
    blob((0.085 * sx, 0.02, 1.468), (0.047, 0.045, 0.095), (sx, 0, -0.38))            # trapezius
    blob((0.098 * sx, -0.012, 1.10), (0.045, 0.065, 0.065))                          # oblique
    blob((0.066 * sx, 0.046, 0.922), (0.064, 0.052, 0.068))                            # glute
blob((0, 0.006, 1.54), (0.06, 0.058, 0.095))                                       # neck
blob((0, 0.03, 1.515), (0.056, 0.036, 0.06))
# arms: tapered muscles that overlap the elbow so the joint has no pinch
for sx in (1, -1):
    sh, el, wr, ht = (0.165 * sx, 0, 1.44), (0.27 * sx, 0.01, 1.18), (0.355 * sx, 0, 0.94), (0.39 * sx, -0.015, 0.81)
    blob((0.19 * sx, 0.0, 1.425), (0.07, 0.074, 0.075))                             # deltoid
    along(sh, el, 0.32, (0.006 * sx, 0, 0), (0.056, 0.058, 0.085))                  # deltoid insertion, upper arm mass
    along(sh, el, 0.56, (0.002 * sx, -0.022, 0), (0.047, 0.047, 0.08))              # biceps peak
    along(sh, el, 0.52, (0.006 * sx, 0.022, 0), (0.046, 0.046, 0.12))               # triceps long head
    along(sh, el, 0.86, (0.004 * sx, 0.02, 0), (0.036, 0.034, 0.06))                # triceps into the elbow
    blob(Vector(el) + Vector((0.004 * sx, 0.03, 0.0)), (0.022, 0.02, 0.026))        # point of the elbow
    along(sh, el, 0.9, (0.024 * sx, -0.004, 0), (0.03, 0.03, 0.07))                 # forearm muscle origin above the elbow
    along(el, wr, 0.16, (0.014 * sx, -0.006, 0), (0.05, 0.046, 0.09))              # forearm, thickest below the elbow
    along(el, wr, 0.2, (-0.012 * sx, 0.004, 0), (0.042, 0.04, 0.08))               # inner forearm
    along(el, wr, 0.55, (0.004 * sx, 0, 0), (0.038, 0.032, 0.09))                   # mid forearm
    along(el, wr, 0.85, (0, 0, 0), (0.033, 0.025, 0.06), (0, 1, 0))                 # flat wrist end
    blob(wr, (0.03, 0.033, 0.03))
# legs
for sx in (1, -1):
    hp, kn, an = (0.095 * sx, 0, 0.92), (0.11 * sx, -0.004, 0.52), (0.117 * sx, 0.012, 0.08)
    along(hp, kn, 0.12, (0.004 * sx, 0.004, 0), (0.08, 0.076, 0.095))              # hip to thigh
    blob((0.132 * sx, 0.004, 0.885), (0.045, 0.058, 0.07))                           # outer hip
    along(hp, kn, 0.48, (0.004 * sx, -0.018, 0), (0.071, 0.065, 0.19))              # quads
    along(hp, kn, 0.45, (0, 0.022, 0), (0.063, 0.056, 0.17))                        # hamstrings
    along(hp, kn, 0.3, (-0.03 * sx, 0, 0), (0.05, 0.052, 0.11))                     # adductor
    along(hp, kn, 0.8, (0, -0.004, 0), (0.058, 0.055, 0.09))                        # lower thigh
    along(hp, kn, 0.84, (-0.02 * sx, -0.022, 0), (0.032, 0.028, 0.04))              # inner knee muscle
    blob(Vector(kn) + Vector((0, -0.01, 0.004)), (0.046, 0.045, 0.05))              # knee
    along(kn, an, 0.12, (0, 0.006, 0), (0.049, 0.049, 0.07))                        # top of shin
    along(kn, an, 0.28, (0.004 * sx, 0.03, 0), (0.054, 0.056, 0.11))               # calf
    along(kn, an, 0.55, (0, -0.002, 0), (0.039, 0.039, 0.17))                       # shin
    along(kn, an, 0.82, (0, 0, 0), (0.034, 0.034, 0.07))
    blob(an, (0.032, 0.034, 0.032))
    fx = 0.117 * sx
    blob((fx, 0.028, 0.042), (0.032, 0.034, 0.034))                                  # heel
    blob((fx + 0.006 * sx, -0.045, 0.036), (0.042, 0.03, 0.085), (0.12 * sx, -1, 0), (1, 0, 0))    # foot
    blob((fx + 0.016 * sx, -0.116, 0.026), (0.042, 0.02, 0.03), (0.12 * sx, -1, 0), (1, 0, 0))     # toes
# head (already at its final height): taller cranium, upright forehead, lighter brow, defined jaw and chin
blob((0, 0.008, 1.708), (0.084, 0.096, 0.1))                                        # cranium
blob((0, -0.045, 1.722), (0.07, 0.045, 0.052))                                      # upright forehead
blob((0, -0.03, 1.66), (0.066, 0.064, 0.07))                                        # mid face
blob((0, -0.036, 1.612), (0.058, 0.052, 0.034))                                     # jaw
for sx in (1, -1):
    blob((0.045 * sx, -0.02, 1.612), (0.022, 0.035, 0.024), (0, -1, -0.35))         # jaw line
blob((0, -0.08, 1.592), (0.026, 0.02, 0.022))                                       # chin
blob((0, -0.08, 1.708), (0.055, 0.014, 0.011))                                      # light brow
blob((0, -0.095, 1.684), (0.012, 0.015, 0.03), (0, -0.5, -1))                       # nose bridge
blob((0, -0.108, 1.662), (0.016, 0.015, 0.015))                                     # nose tip
for sx in (1, -1):
    blob((0.044 * sx, -0.066, 1.668), (0.022, 0.016, 0.013))                         # cheekbone, subtle
    blob((0.011 * sx, -0.098, 1.659), (0.009, 0.009, 0.008))                         # nostril wing
    blob((0.084 * sx, 0.008, 1.664), (0.008, 0.016, 0.022))                          # ear base
    blob((0.034 * sx, -0.088, 1.684), (0.016, 0.012, 0.012), neg=True)               # eye socket, shallow
blob((0, -0.086, 1.63), (0.024, 0.01, 0.009))                                       # mouth
upd(); dg = bpy.context.evaluated_depsgraph_get()
dense = bpy.data.meshes.new_from_object(mbo.evaluated_get(dg)); bpy.data.objects.remove(mbo)
dense_keep = dense.copy()
tmp = bpy.data.objects.new('BodyDense', dense); col.objects.link(tmp)
dm = tmp.modifiers.new('Dec', 'DECIMATE'); dm.decimate_type = 'COLLAPSE'; dm.ratio = 5600 / max(1, len(dense.polygons))
upd(); dg = bpy.context.evaluated_depsgraph_get()
bme = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg)); bpy.data.objects.remove(tmp)
bme.name = 'Body'
body = bpy.data.objects.new('Body', bme); col.objects.link(body)
for k in ('skin', 'shorts'): bme.materials.append(MT[k])
for p in bme.polygons:
    c = p.center
    p.material_index = 1 if (0.78 < c.z < 1.045 and abs(c.x) < 0.2) else 0
    p.use_smooth = True
def body_w(p):
    if p.z > 1.585 and abs(p.x) < 0.13: return {'head': 1.0}
    if p.z > 1.545 and abs(p.x) < 0.1:
        t = (p.z - 1.545) / 0.04; return {'head': t, 'neck': 1 - t}
    return None
skin_to(body, DEFORM, body_w, 5)
# dominant bone per vertex, for tailoring and garments
GI = {g.index: g.name for g in body.vertex_groups}
DOM = []
for v in bme.vertices:
    best = max(v.groups, key=lambda g: g.weight) if len(v.groups) else None
    DOM.append(GI[best.group] if best else 'hips')
BV = [v.co.copy() for v in bme.vertices]
ARMISH = ('shoulder', 'upper_arm', 'forearm', 'hand')
def torso_extent(z, band=0.02):
    pts = [p for p, d in zip(BV, DOM) if abs(p.z - z) < band and not d.startswith(ARMISH)]
    if not pts: return None
    return max(abs(p.x) for p in pts), max(-p.y for p in pts), max(p.y for p in pts)
def limb_radius(center, axis, prefixes, band=0.02, cut=0.14):
    c = Vector(center); a = Vector(axis).normalized(); best = 0
    for p, d in zip(BV, DOM):
        if not d.startswith(prefixes): continue
        v = p - c; h = v.dot(a)
        if abs(h) < band:
            r = (v - a * h).length
            if r < cut: best = max(best, r)
    return best

# ambient shading baked into the skin colors
try:
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 48; scene.cycles.device = 'CPU'
    if scene.world is None: scene.world = bpy.data.worlds.new('W')
    scene.world.light_settings.distance = 0.08
    for a in list(bme.color_attributes): bme.color_attributes.remove(a)
    ca = bme.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER'); bme.color_attributes.active_color = ca
    for o in col.objects: o.select_set(False)
    body.select_set(True); bpy.context.view_layer.objects.active = body
    scene.render.bake.target = 'VERTEX_COLORS'
    bpy.ops.object.bake(type='AO')
    for d in ca.data:
        a = d.color[0]; v = 0.32 + 0.68 * a
        d.color = (v, v * 0.93 + 0.07 * a, v * 0.9 + 0.1 * a, 1)
    print('AO BAKED')
except Exception as ex:
    print('AO BAKE FAILED', ex)
bpy.context.view_layer.objects.active = arm

# garments as shells offset from the body, sharing its skin weights
def shell(name, pred, offset, m):
    bm = bmesh.new(); bm.from_mesh(bme)
    bm.verts.ensure_lookup_table()
    kill = [f for f in bm.faces if not pred(f.calc_center_median(), DOM[f.verts[0].index])]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    bm.normal_update()
    for v in bm.verts: v.co = v.co + v.normal * offset
    me2 = bpy.data.meshes.new(name); bm.to_mesh(me2); bm.free()
    me2.materials.append(MT[m])
    for p in me2.polygons: p.use_smooth = True
    for a in list(me2.color_attributes): me2.color_attributes.remove(a)
    ob = bpy.data.objects.new(name, me2); col.objects.link(ob)
    for g in body.vertex_groups: ob.vertex_groups.new(name=g.name)
    md = ob.modifiers.new('Armature', 'ARMATURE'); md.object = arm; ob.parent = arm
    return ob
LEGS = ('thigh', 'shin', 'hips')
shell('Trousers', lambda c, d: 0.27 < c.z < 1.05 and d.startswith(LEGS + ('spine',)) , 0.007, 'trousers')
shell('Shirt', lambda c, d: 0.98 < c.z < 1.5 and d in ('spine', 'chest', 'hips', 'neck') and abs(c.x) < 0.15, 0.005, 'shirt')
shell('Vest', lambda c, d: 1.0 < c.z < 1.47 and d in ('spine', 'chest', 'hips', 'neck') and abs(c.x) < 0.17, 0.011, 'vest')
shell('Boots', lambda c, d: (c.z < 0.31 and d.startswith(('shin', 'foot'))), 0.013, 'boots')
HAIRLINE = [(0.0, 1.742), (0.6, 1.746), (0.95, 1.727), (1.15, 1.703), (1.3, 1.66), (1.5, 1.652), (1.95, 1.638), (2.45, 1.616), (math.pi, 1.604)]
def hair_g(p):
    x, y, z = p.x, p.y, p.z
    ph = abs(math.atan2(x, -(y - 0.005)))
    for (a0, h0), (a1, h1) in zip(HAIRLINE, HAIRLINE[1:]):
        if ph <= a1:
            t = (ph - a0) / (a1 - a0); t = t * t * (3 - 2 * t); H = h0 + (h1 - h0) * t; break
    g = z - H
    if abs(x) > 0.04:
        e = ((y - 0.01) / 0.041) ** 2 + ((z - 1.667) / 0.053) ** 2 - 1.0
        g = min(g, e * 0.03)
    return g
def build_hair():
    src = bmesh.new(); src.from_mesh(dense_keep)
    bmesh.ops.triangulate(src, faces=src.faces[:]); src.normal_update()
    out = bmesh.new(); cache = {}
    def vkey(co):
        return (round(co.x, 5), round(co.y, 5), round(co.z, 5))
    def getv(co, n):
        k = vkey(co)
        if k not in cache:
            v = out.verts.new(co); cache[k] = (v, n.normalized())
        return cache[k][0]
    for f in src.faces:
        if f.calc_center_median().z < 1.55: continue
        vs = [(l.vert.co.copy(), l.vert.normal.copy(), hair_g(l.vert.co)) for l in f.loops]
        if all(g <= 0 for _, _, g in vs): continue
        poly = []
        for i in range(3):
            c0, n0, g0 = vs[i]; c1, n1, g1 = vs[(i + 1) % 3]
            if g0 > 0: poly.append((c0, n0))
            if (g0 > 0) != (g1 > 0):
                t = g0 / (g0 - g1); poly.append((c0.lerp(c1, t), n0.lerp(n1, t)))
        if len(poly) >= 3:
            vv = [getv(c, n) for c, n in poly]
            if len(set(vv)) == len(vv):
                try: out.faces.new(vv)
                except ValueError: pass
    src.free()
    nrm = {v: n for v, n in cache.values()}
    for v in out.verts: v.co = v.co + nrm[v] * 0.011
    bnd = [e for e in out.edges if e.is_boundary]
    ret = bmesh.ops.extrude_edge_only(out, edges=bnd)
    for e in [g for g in ret['geom'] if isinstance(g, bmesh.types.BMEdge)]:
        pass
    newv = [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]
    for v in newv:
        src_v = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in nrm]
        n = nrm[src_v[0]] if src_v else Vector((0, 0, 1))
        v.co = v.co - n * 0.012
    out.normal_update()
    me2 = bpy.data.meshes.new('HairCap'); out.to_mesh(me2); out.free()
    t = bpy.data.objects.new('HairTmp', me2); col.objects.link(t)
    dm2 = t.modifiers.new('Dec', 'DECIMATE'); dm2.decimate_type = 'COLLAPSE'; dm2.ratio = min(1.0, 2000 / max(1, len(me2.polygons)))
    upd(); dg2 = bpy.context.evaluated_depsgraph_get()
    hm = bpy.data.meshes.new_from_object(t.evaluated_get(dg2)); bpy.data.objects.remove(t)
    hm.name = 'HairCap'
    for a in list(hm.color_attributes): hm.color_attributes.remove(a)
    hm.materials.clear(); hm.materials.append(MT['hair'])
    for p in hm.polygons: p.use_smooth = True
    ob = bpy.data.objects.new('HairCap', hm); col.objects.link(ob)
    g = ob.vertex_groups.new(name='head'); g.add(list(range(len(hm.vertices))), 1.0, 'REPLACE')
    md = ob.modifiers.new('Armature', 'ARMATURE'); md.object = arm; ob.parent = arm
    print('HAIR TRIS', sum(len(p.vertices) - 2 for p in hm.polygons))
    return ob
build_hair()
shell('Gloves', lambda c, d: (d.startswith('hand') and c.z > 0.925) or (d.startswith('forearm') and c.z < 1.0), 0.005, 'leatherDark')

def tube(points, radii, sides=10, mat_i=0):
    bm = bmesh.new(); rings = []
    for k, (p, r) in enumerate(zip(points, radii)):
        p = Vector(p); d = (Vector(points[min(k + 1, len(points) - 1)]) - Vector(points[max(k - 1, 0)])).normalized()
        a = d.cross(Vector((0, 1, 0))).normalized(); b = d.cross(a).normalized()
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * j / sides) + b * math.sin(2 * math.pi * j / sides)) * r) for j in range(sides)])
    for k in range(len(rings) - 1):
        for j in range(sides):
            bm.faces.new((rings[k][j], rings[k][(j + 1) % sides], rings[k + 1][(j + 1) % sides], rings[k + 1][j]))
    bm.normal_update(); return bm


# ---------------- hands: modelled palm, jointed fingers and thumb ----------------
def add_tube(bm, pts, radii, ref, sides=7, cap=True):
    rings = []
    for k, p in enumerate(pts):
        d = (pts[min(k + 1, len(pts) - 1)] - pts[max(k - 1, 0)]).normalized()
        a = (ref - d * ref.dot(d)).normalized(); b2 = d.cross(a)
        rings.append([bm.verts.new(p + (a * math.cos(2 * math.pi * j / sides) + b2 * math.sin(2 * math.pi * j / sides)) * radii[k]) for j in range(sides)])
    for k in range(len(rings) - 1):
        for j in range(sides):
            bm.faces.new((rings[k][j], rings[k][(j + 1) % sides], rings[k + 1][(j + 1) % sides], rings[k + 1][j]))
    if cap:
        d = (pts[-1] - pts[-2]).normalized(); tip = bm.verts.new(pts[-1] + d * radii[-1] * 0.95)
        for j in range(sides): bm.faces.new((rings[-1][j], rings[-1][(j + 1) % sides], tip))
        d0 = (pts[0] - pts[1]).normalized(); base = bm.verts.new(pts[0] + d0 * radii[0] * 0.6)
        for j in range(sides): bm.faces.new((rings[0][(j + 1) % sides], rings[0][j], base))
def add_ellipsoid(bm, c, ax, r):
    g = bmesh.new(); bmesh.ops.create_uvsphere(g, u_segments=10, v_segments=7, radius=1)
    M = Matrix((ax[0] * r[0], ax[1] * r[1], ax[2] * r[2])).transposed().to_4x4(); M.translation = c
    bmesh.ops.transform(g, matrix=M, verts=g.verts)
    vm = {v: bm.verts.new(v.co) for v in g.verts}
    for f in g.faces: bm.faces.new([vm[v] for v in f.verts])
    g.free()
def build_hand(s, sx, grip):
    W = Vector((0.355 * sx, 0, 0.94)); D = (Vector((0.39 * sx, -0.015, 0.81)) - W).normalized()
    N = Vector((-sx, 0, 0)); N = (N - D * N.dot(D)).normalized()          # palm faces the body
    F = Vector((0, -1, 0)); F = (F - D * F.dot(D) - N * F.dot(N)).normalized()   # thumb side
    bm = bmesh.new()
    # palm: lofted rounded box
    stations = [(0.0, 0.026, 0.0155), (0.028, 0.034, 0.015), (0.058, 0.039, 0.0135), (0.084, 0.04, 0.0105)]
    rings = []
    for t, hw, ht_ in stations:
        ring = []
        for j in range(12):
            a = 2 * math.pi * j / 12; ca, sa = math.cos(a), math.sin(a)
            u = math.copysign(abs(ca) ** 0.55, ca) * hw; v = math.copysign(abs(sa) ** 0.7, sa) * ht_
            ring.append(bm.verts.new(W + D * t + F * u + N * (v - 0.002)))
        rings.append(ring)
    for k in range(len(rings) - 1):
        for j in range(12):
            bm.faces.new((rings[k][j], rings[k][(j + 1) % 12], rings[k + 1][(j + 1) % 12], rings[k + 1][j]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    add_ellipsoid(bm, W + D * 0.036 + F * 0.021 + N * 0.009, (F, D, N), (0.019, 0.03, 0.013))   # thumb muscle
    # fingers
    curl = [0.95, 1.15, 0.85] if grip else [0.22, 0.38, 0.28]
    fingers = [(0.027, 0.0405, 0.0245, 0.019, 0.0098, 0.04), (0.0095, 0.045, 0.027, 0.021, 0.0102, 0.0),
               (-0.0095, 0.042, 0.026, 0.02, 0.0097, -0.03), (-0.0265, 0.034, 0.02, 0.017, 0.0086, -0.07)]
    for off, l1, l2, l3, r, splay in fingers:
        knuckle = W + D * (0.081 - abs(off) * 0.12) + F * off
        d = (D * math.cos(splay) + F * math.sin(splay)).normalized()
        pts = [knuckle - d * 0.006, knuckle]; p = knuckle
        for L, c in zip((l1, l2, l3), curl):
            n = (N - d * N.dot(d)).normalized(); d = (d * math.cos(c) + n * math.sin(c)).normalized()
            p = p + d * L; pts.append(p)
        add_tube(bm, pts, [r * 0.95, r, r * 0.93, r * 0.85, r * 0.75], N)
        add_ellipsoid(bm, knuckle - N * 0.0015 - D * 0.002, (F, D, N), (r * 0.98, r * 1.0, r * 0.85))       # knuckle bump
    # thumb
    tc = [0.2, 0.3] if not grip else [0.75, 0.85]
    base = W + D * 0.03 + F * 0.03 + N * 0.008
    d = (D * 0.8 + F * 0.42 + N * 0.42).normalized(); pts = [base, base + d * 0.006]; p = pts[-1]
    for L, c in zip((0.034, 0.027), tc):
        n = (N - d * N.dot(d)).normalized(); d = (d * math.cos(c) + n * math.sin(c)).normalized()
        p = p + d * L; pts.append(p)
    add_tube(bm, pts, [0.0125, 0.0128, 0.0115, 0.0095], N)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0002)
    bm.normal_update()
    def finish(name, bmx, m, off):
        if off:
            for v in bmx.verts: v.co = v.co + v.normal * off
        me2 = bpy.data.meshes.new(name); bmx.to_mesh(me2); bmx.free()
        me2.materials.append(MT[m])
        for pp in me2.polygons: pp.use_smooth = True
        ob = bpy.data.objects.new(name, me2); col.objects.link(ob)
        g = ob.vertex_groups.new(name=f'hand.{s}'); g.add(list(range(len(me2.vertices))), 1.0, 'REPLACE')
        md = ob.modifiers.new('Armature', 'ARMATURE'); md.object = arm; ob.parent = arm
        return ob
    glove = bm.copy()
    finish(f'Hand.{s}', bm, 'skin', 0)
    finish(f'GlovesHand.{s}', glove, 'leatherDark', 0.0032)
for s_, sx_ in (('L', 1), ('R', -1)):
    build_hand(s_, sx_, grip=(s_ == 'R'))

# ---------------- head (rigid to head bone) ----------------
H = 'head'
for sx in (1, -1):
    part(f'EyeWhite{sx}', bm_sphere(0.0105, 12, 8), 'shirt', T(0.034 * sx, -0.0805, 1.706) @ S(1.1, 0.8, 0.8), H)
    part(f'Eye{sx}', bm_sphere(0.0055, 8, 6), 'eye', T(0.034 * sx, -0.089, 1.706) @ S(1, 0.6, 1), H)
    part(f'Lid{sx}', bm_cap(0.0118, 12, 8, 0.45), 'skin', T(0.034 * sx, -0.0805, 1.7075) @ S(1.12, 0.85, 0.9) @ R('X', -0.3), H)
    part(f'Brow{sx}', tube([(0.013 * sx, -0.1, 1.727), (0.036 * sx, -0.1, 1.733), (0.057 * sx, -0.09, 1.726)], [0.0055, 0.006, 0.0038], 6), 'hair', Matrix.Identity(4), H)
    part(f'Tache{sx}', tube([(0.0, -0.104, 1.655), (0.022 * sx, -0.102, 1.651), (0.042 * sx, -0.092, 1.639), (0.052 * sx, -0.082, 1.623)], [0.01, 0.011, 0.0085, 0.004], 7), 'hair', Matrix.Identity(4), H)
    part(f'Sideburn{sx}', tube([(0.088 * sx, -0.012, 1.728), (0.088 * sx, -0.022, 1.70), (0.085 * sx, -0.032, 1.665), (0.076 * sx, -0.045, 1.632)], [0.009, 0.009, 0.0085, 0.005], 6), 'hair', Matrix.Identity(4), H)
# ears: curled rim, inner bowl, lobe and the small front flap
for sx in (1, -1):
    C0 = Vector((0.086 * sx, 0.012, 1.665 + 0.022))
    W0, U0, V0 = Vector((sx, 0, 0)), Vector((0, 0, 1)), Vector((0, 1, 0))
    tb, pr = math.radians(14), math.radians(22)
    U1 = U0 * math.cos(tb) + V0 * math.sin(tb); V1 = V0 * math.cos(tb) - U0 * math.sin(tb)
    V2 = V1 * math.cos(pr) + W0 * math.sin(pr); W2 = W0 * math.cos(pr) - V1 * math.sin(pr)
    def ep(v, u, w): return C0 + V2 * v + U1 * u + W2 * w
    rim = [ep(0.021 * math.cos(math.radians(a)), 0.034 * math.sin(math.radians(a)), 0.007) for a in range(115, -86, -25)]
    part(f'EarRim{sx}', tube([tuple(p) for p in rim], [0.005, 0.0066, 0.007, 0.0068, 0.0066, 0.0062, 0.0058, 0.0054, 0.0048], 7), 'skin', Matrix.Identity(4), H)
    fr = Matrix((V2, U1, W2)).transposed().to_4x4()
    part(f'EarBowl{sx}', bm_sphere(1, 12, 8), 'skin', T(*ep(0.002, -0.002, 0.001)) @ fr @ S(0.018, 0.027, 0.006), H)
    part(f'EarLobe{sx}', bm_sphere(1, 10, 8), 'skin', T(*ep(-0.002, -0.032, 0.004)) @ fr @ S(0.0105, 0.0115, 0.006), H)
    part(f'EarFlap{sx}', bm_sphere(1, 8, 6), 'skin', T(*ep(-0.016, -0.006, 0.004)) @ fr @ S(0.0055, 0.0075, 0.004), H)
# goggles pushed up on the forehead
gm = T(0, 0, 1.752) @ R('X', -0.22)
part('GoggleStrap', bm_torus(0.1, 0.009, 22, 5), 'leatherDark', gm @ S(0.93, 1.06, 1), H)
for sx in (1, -1):
    lm = T(0.037 * sx, -0.112, 1.772) @ R('X', math.pi / 2 - 0.35)
    part(f'GoggleRim{sx}', bm_cyl(0.026, 0.024, 0.024, 14), 'brass', lm, H)
    part(f'GoggleLens{sx}', bm_cyl(0.019, 0.019, 0.026, 14), 'glass', lm, H)
part('GoggleBridge', bm_box(0.022, 0.008, 0.008), 'brass', T(0, -0.115, 1.775), H, False)
# eyepiece loupe over the right eye
lp = T(-0.036, -0.112, 1.705) @ R('X', math.pi / 2)
part('Loupe', bm_cyl(0.019, 0.016, 0.03, 14), 'brass', lp, H)
part('LoupeLens', bm_cyl(0.013, 0.013, 0.032, 12), 'glow', lp, H)
part('LoupeArm', bm_box(0.006, 0.006, 0.06), 'brass', T(-0.075, -0.07, 1.715) @ R('Y', 0.4) @ R('X', 0.9), H, False)
# scarf
part('Scarf', bm_torus(0.068, 0.024, 16, 7), 'scarf', T(0, -0.005, 1.535) @ S(1.05, 1.0, 1.15) @ R('X', 0.12), 'neck')
part('ScarfTail', bm_box(0.05, 0.02, 0.11), 'scarf', T(0.03, -0.085, 1.45) @ R('Y', 0.2) @ R('X', 0.15), 'chest', False)

# ---------------- coat (skinned) ----------------
RINGS = [(1.585, .122, .104), (1.535, .112, .098), (1.505, .148, .112), (1.47, .178, .12), (1.43, .192, .126), (1.37, .186, .127), (1.30, .178, .126), (1.20, .162, .117),
         (1.10, .148, .108), (1.02, .158, .118), (0.94, .172, .13), (0.84, .19, .145), (0.74, .205, .158), (0.64, .22, .17),
         (0.55, .235, .18), (0.47, .247, .19)]
def open_at(z):
    if z >= 1.53: return 0.5
    if z >= 1.40: return 0.16
    return 0.16 + (1.40 - z) / (1.40 - 0.47) * 0.74
fit = []
for z, rx, ry in RINGS:
    e = torso_extent(z) if z > 0.9 else None
    if e: rx = max(rx, e[0] + 0.03); ry = max(ry, max(e[1], e[2]) + 0.03)
    if fit and z < 0.95: rx = max(rx, fit[-1][1] + 0.012); ry = max(ry, fit[-1][2] + 0.008)
    fit.append((z, rx, ry))
RINGS = fit
C = 24
cb = bmesh.new(); outer = []; inner = []
for z, rx, ry in RINGS:
    o = open_at(z); ro, ri = [], []
    for j in range(C + 1):
        th = o + (2 * math.pi - 2 * o) * j / C
        ro.append(cb.verts.new((rx * math.sin(th), -ry * math.cos(th), z)))
        ri.append(cb.verts.new(((rx - 0.008) * math.sin(th), -(ry - 0.008) * math.cos(th), z)))
    outer.append(ro); inner.append(ri)
for i in range(len(RINGS) - 1):
    for j in range(C):
        f = cb.faces.new((outer[i][j], outer[i + 1][j], outer[i + 1][j + 1], outer[i][j + 1])); f.material_index = 0
        f = cb.faces.new((inner[i][j + 1], inner[i + 1][j + 1], inner[i + 1][j], inner[i][j])); f.material_index = 1
last = len(RINGS) - 1
for j in range(C):  # hem thickness
    f = cb.faces.new((outer[last][j], inner[last][j], inner[last][j + 1], outer[last][j + 1])); f.material_index = 1
for i in range(len(RINGS) - 1):  # front edges
    f = cb.faces.new((outer[i][0], inner[i][0], inner[i + 1][0], outer[i + 1][0])); f.material_index = 1
    f = cb.faces.new((outer[i + 1][C], inner[i + 1][C], inner[i][C], outer[i][C])); f.material_index = 1
cb.normal_update()
coat = make_obj('Coat', cb, [MT['coat'], MT['lining']])
def coat_w(p):
    if p.z > 1.0: return None
    t = max(0.0, min(1.0, (0.99 - p.z) / 0.42)) * 0.6
    if abs(p.x) < 0.03: return {'hips': 1 - t, 'thigh.L': t / 2, 'thigh.R': t / 2}
    return {'hips': 1 - t, ('thigh.L' if p.x > 0 else 'thigh.R'): t}
skin_to(coat, ['hips', 'spine', 'chest', 'neck', 'shoulder.L', 'shoulder.R'], coat_w, 6)
# sleeves
for s, sx in (('L', 1), ('R', -1)):
    pts = [(0.14 * sx, 0, 1.425), (0.175 * sx, 0, 1.43), (0.22 * sx, 0.005, 1.31), (0.27 * sx, 0.01, 1.18), (0.31 * sx, 0.006, 1.07), (0.345 * sx, 0.002, 0.975), (0.352 * sx, 0.0, 0.955)]
    rad = [0.07, 0.074, 0.066, 0.058, 0.055, 0.058, 0.064]
    for k in range(len(pts)):
        a0 = Vector(pts[max(k - 1, 0)]); a1 = Vector(pts[min(k + 1, len(pts) - 1)])
        rad[k] = max(rad[k], limb_radius(pts[k], a1 - a0, (f'upper_arm.{s}', f'forearm.{s}'), 0.015, 0.085) + 0.014)
    sb = tube(pts, rad, 12)
    for f in sb.faces:
        if sx < 0: f.normal_flip()
    slv = make_obj(f'Sleeve.{s}', sb, [MT['coat']])
    skin_to(slv, [f'shoulder.{s}', f'upper_arm.{s}', f'forearm.{s}', 'chest'], None, 8)
    cuff = tube([(0.345 * sx, 0.002, 0.975), (0.356 * sx, 0.0, 0.948)], [0.062, 0.066], 12)
    if sx < 0:
        for f in cuff.faces: f.normal_flip()
    cf = make_obj(f'Cuff.{s}', cuff, [MT['lining']]); skin_to(cf, [f'forearm.{s}'], None, 8)

# ---------------- vest details, belt, pouches ----------------
for k, z in enumerate((1.36, 1.30, 1.24, 1.18)):
    part(f'Button{k}', bm_sphere(0.008, 8, 6), 'brass', T(0, -0.106 + (1.36 - z) * 0.05, z), 'chest' if z > 1.28 else 'spine')
_be = torso_extent(1.085)
part('Belt', bm_torus(0.13, 0.016, 26, 6), 'leather', T(0, 0.004, 1.085) @ S((_be[0] + 0.042) / 0.13, (max(_be[1], _be[2]) + 0.04) / 0.13, 1.15), 'hips')
part('Buckle', bm_box(0.05, 0.012, 0.04), 'brass', T(0, -(max(_be[1], _be[2]) + 0.055), 1.085), 'hips', False)
part('PouchL', bm_box(0.06, 0.035, 0.07), 'leatherDark', T(0.12, -0.085, 1.045) @ R('Z', 0.55), 'hips', False)
part('PouchFlapL', bm_box(0.064, 0.038, 0.02), 'leather', T(0.12, -0.086, 1.075) @ R('Z', 0.55), 'hips', False)
part('PouchR', bm_box(0.05, 0.03, 0.06), 'leatherDark', T(-0.135, -0.06, 1.05) @ R('Z', -0.8), 'hips', False)
part('WrenchHandle', bm_box(0.012, 0.008, 0.16), 'iron', T(0.165, -0.02, 0.99) @ R('Y', 0.15), 'hips', False)
part('WrenchHead', bm_torus(0.02, 0.007, 10, 5, math.pi * 1.5), 'iron', T(0.177, -0.02, 0.905) @ R('X', math.pi / 2), 'hips')

# ---------------- left shoulder: pauldron with a pressure gauge ----------------
pm = T(0.2, 0.0, 1.47) @ R('Y', 0.45) @ S(1.15, 1.15, 1.15)
part('Pauldron', bm_cap(0.088, 16, 10, 0.5), 'brass', pm @ S(1.1, 1.05, 0.75), 'upper_arm.L')
part('PauldronRim', bm_torus(0.088, 0.008, 18, 5), 'iron', pm @ S(1.1, 1.05, 1), 'upper_arm.L')
for k in range(5):
    a = -1.1 + k * 0.55
    part(f'Rivet{k}', bm_sphere(0.007, 6, 5), 'iron', pm @ T(math.cos(a) * 0.075, math.sin(a) * 0.072, 0.03), 'upper_arm.L')
gg = T(0.2, -0.085, 1.43) @ R('X', math.pi / 2)
part('Gauge', bm_cyl(0.03, 0.03, 0.018, 16), 'brass', gg, 'upper_arm.L')
part('GaugeFace', bm_cyl(0.024, 0.024, 0.02, 16), 'amber', gg @ T(0, 0, -0.001), 'upper_arm.L')
part('GaugeNeedle', bm_box(0.003, 0.004, 0.02), 'eye', T(0.205, -0.097, 1.435) @ R('Y', 0.6), 'upper_arm.L', False)
part('GaugePipe', bm_torus(0.07, 0.008, 12, 5, math.pi * 0.9), 'brass', T(0.21, -0.02, 1.43) @ R('Z', -math.pi / 2) @ R('X', math.pi / 2), 'upper_arm.L')

# ---------------- right leg: mechanical brace ----------------
part('BraceThighStrap', bm_torus(limb_radius((-0.105, 0, 0.66), (0, 0, 1), ('thigh.R',)) + 0.01, 0.009, 16, 5), 'leatherDark', T(-0.098, 0, 0.66), 'thigh.R')
part('BraceThighStrut', bm_box(0.016, 0.016, 0.16), 'brass', T(-0.15, -0.045, 0.61) @ R('Y', 0.05), 'thigh.R', False)
km = T(-0.152, -0.045, 0.52) @ R('Y', math.pi / 2) @ R('X', 0.5)
part('KneeGear', bm_cyl(0.042, 0.042, 0.018, 12), 'brass', km, 'shin.R')
for k in range(12):
    a = 2 * math.pi * k / 12
    part(f'Tooth{k}', bm_box(0.012, 0.012, 0.016), 'brass', km @ T(math.cos(a) * 0.046, math.sin(a) * 0.046, 0) @ R('Z', a), 'shin.R', False)
part('KneeCore', bm_cyl(0.018, 0.018, 0.024, 12), 'glow', km, 'shin.R')
part('BraceShinStrut', bm_box(0.016, 0.016, 0.34), 'brass', T(-0.145, -0.05, 0.32), 'shin.R', False)
part('BracePiston', bm_cyl(0.011, 0.011, 0.2, 8), 'iron', T(-0.118, -0.068, 0.36) @ R('Y', 0.08), 'shin.R')
for z in (0.42, 0.22):
    part(f'BraceShinStrap{z}', bm_torus(limb_radius((-0.113, 0.006, z), (0, 0, 1), ('shin.R',)) + (0.016 if z < 0.31 else 0.01), 0.009, 16, 5), 'leatherDark', T(-0.1, 0.004, z), 'shin.R')
part('BraceAnkle', bm_cyl(0.022, 0.022, 0.02, 10), 'iron', T(-0.15, -0.03, 0.13) @ R('Y', math.pi / 2), 'shin.R')
part('SatchelStrap', bm_torus(0.21, 0.01, 28, 4), 'leatherDark', T(0, 0.0, 1.24) @ R('Y', -0.62) @ S(1.0, 0.62, 1.0), 'chest')
part('Satchel', bm_box(0.17, 0.07, 0.14), 'leather', T(-0.17, 0.08, 1.0) @ R('Z', -0.5), 'hips', False)
part('SatchelFlap', bm_box(0.175, 0.075, 0.05), 'leatherDark', T(-0.17, 0.08, 1.06) @ R('Z', -0.5), 'hips', False)
part('SatchelBuckle', bm_box(0.025, 0.01, 0.03), 'brass', T(-0.205, 0.05, 1.045) @ R('Z', -0.5), 'hips', False)
part('ToolRoll', bm_cyl(0.035, 0.035, 0.22, 10), 'leather', T(0, 0.14, 1.36) @ R('Y', math.pi / 2), 'chest')
for k in (-1, 1):
    part(f'ToolRollTie{k}', bm_torus(0.037, 0.006, 10, 4), 'leatherDark', T(0.07 * k, 0.14, 1.36) @ R('Y', math.pi / 2), 'chest')
for s, sx in (('L', 1), ('R', -1)):
    part(f'BootCuff.{s}', bm_torus(limb_radius((0.114 * sx, 0.006, 0.30), (0, 0, 1), (f'shin.{s}',)) + 0.012, 0.015, 16, 6), 'boots', T(0.114 * sx + (0.013 if sx < 0 else 0), 0.006, 0.30), f'shin.{s}')

# ---------------- poses ----------------
SIGN = {}
def tail(n): upd(); return arm.pose.bones[n].tail.copy()
for n in DEFORM:
    pb = arm.pose.bones[n]; pb.rotation_mode = 'XYZ'
for n in DEFORM:
    pb = arm.pose.bones[n]; t0 = tail(n)
    pb.rotation_euler = (0.25, 0, 0); f = tail(n) - t0
    pb.rotation_euler = (0, 0, 0.25); sd = tail(n) - t0
    pb.rotation_euler = (0, 0, 0)
    inward = Vector((-1 if n.endswith('.L') else 1, 0, 0))
    SIGN[n] = (1 if f.y < 0 else -1, 1 if sd.dot(inward) > 0 else -1)

def point_bone(n, target):
    # rotate bone n (minimal rotation) so its tail points at target (armature space)
    upd(); pb = arm.pose.bones[n]
    M = pb.matrix.copy(); y = (M.to_3x3() @ Vector((0, 1, 0))).normalized()
    want = (Vector(target) - pb.head).normalized()
    q = y.rotation_difference(want)
    R3 = q.to_matrix() @ M.to_3x3()
    N = R3.to_4x4(); N.translation = pb.head
    pb.matrix = N; upd()

def pose(d, loc_up=0.0, chains=None):
    for n in DEFORM:
        fwd, side, tw = d.get(n, (0, 0, 0)); sf, ssd = SIGN[n]
        arm.pose.bones[n].rotation_euler = (fwd * sf, tw, side * ssd)
    arm.pose.bones['hips'].location = (0, loc_up, 0)
    upd()
    for bone, target in (chains or []):
        point_bone(bone, target)

# arm targets (armature space): elbow, wrist, hand tip
CARRY_R = [('upper_arm.R', (-0.215, -0.02, 1.17)), ('forearm.R', (-0.2, -0.27, 1.07)), ('hand.R', (-0.19, -0.36, 1.03))]
AIM_R = [('upper_arm.R', (-0.25, -0.1, 1.25)), ('forearm.R', (-0.11, -0.3, 1.33)), ('hand.R', (-0.08, -0.4, 1.34))]
AIM_L = [('upper_arm.L', (0.2, -0.22, 1.24)), ('forearm.L', (0.0, -0.46, 1.29)), ('hand.L', (-0.04, -0.55, 1.29))]
AIM_BODY = {'spine': (0.04, 0, 0.0), 'chest': (0.02, 0, 0.0), 'neck': (0.08, 0, 0), 'head': (0.06, 0, 0.12),
            'thigh.L': (0.2, 0, 0), 'shin.L': (-0.22, 0, 0), 'thigh.R': (-0.16, 0, 0), 'shin.R': (-0.1, 0, 0), 'foot.L': (0.02, 0, 0)}

# rifle, built in the aim pose: level, pointing forward, stock toward the right shoulder
pose(AIM_BODY, -0.04, AIM_R + AIM_L)
grip = arm.pose.bones['hand.R'].tail.copy() + Vector((0, 0.02, 0.0))
fwd = Vector((0.06, -1, 0.0)).normalized()
yax = -fwd; xax = yax.cross(Vector((0, 0, 1))).normalized(); zax = xax.cross(yax).normalized()
RM = T(*grip) @ Matrix((xax, yax, zax)).transposed().to_4x4()
rifle = [
 ('Stock', bm_box(0.034, 0.24, 0.055), 'wood', T(0, 0.16, -0.03) @ R('X', 0.1)),
 ('Grip', bm_box(0.03, 0.04, 0.08), 'wood', T(0, 0.04, -0.045) @ R('X', -0.3)),
 ('Receiver', bm_box(0.042, 0.17, 0.05), 'brass', T(0, -0.05, 0.0)),
 ('Barrel', bm_cyl(0.014, 0.014, 0.46, 10), 'iron', T(0, -0.36, 0.008) @ R('X', math.pi / 2)),
 ('Muzzle', bm_cyl(0.024, 0.018, 0.05, 12), 'brass', T(0, -0.59, 0.008) @ R('X', math.pi / 2)),
 ('Scope', bm_cyl(0.012, 0.012, 0.15, 10), 'brass', T(0, -0.08, 0.048) @ R('X', math.pi / 2)),
 ('ScopeLens', bm_cyl(0.009, 0.009, 0.152, 10), 'glass', T(0, -0.08, 0.048) @ R('X', math.pi / 2)),
 ('Cell', bm_cyl(0.016, 0.016, 0.06, 10), 'glow', T(0.03, -0.03, 0.0) @ R('X', math.pi / 2)),
 ('Guard', bm_torus(0.022, 0.004, 10, 4, math.pi), 'brass', T(0, 0.02, -0.03) @ R('Y', math.pi / 2)),
]
for k in range(7):
    rifle.append((f'Coil{k}', bm_torus(0.023, 0.0045, 12, 4), 'brass', T(0, -0.19 - k * 0.035, 0.008) @ R('X', math.pi / 2)))
for name, bm, m, M in rifle:
    part('Rifle' + name, bm, m, RM @ M, 'hand.R')
pose({})

# ---------------- animations ----------------
arm.animation_data_create()
def bake(name, frames, fn):
    act = bpy.data.actions.new(name); act.use_fake_user = True
    arm.animation_data.action = act
    for f in frames:
        d, up, ch = fn(f); pose(d, up, ch)
        for n in DEFORM:
            arm.pose.bones[n].keyframe_insert('rotation_euler', frame=f)
        arm.pose.bones['hips'].keyframe_insert('location', frame=f)
    return act
def shift(chain, dz=0.0, dy=0.0):
    return [(b, (p[0], p[1] + dy, p[2] + dz)) for b, p in chain]
def idle(f):
    ph = 2 * math.pi * f / 48; b = math.sin(ph)
    d = {'spine': (0.035, 0, 0), 'chest': (-0.03 + 0.02 * b, 0, 0), 'neck': (0.07 - 0.02 * b, 0, 0), 'head': (-0.03 + 0.03 * math.sin(ph * 0.5), 0, 0.05 * math.sin(ph)),
         'thigh.L': (0.1, 0, 0), 'shin.L': (-0.2, 0, 0), 'foot.L': (0.1, 0, 0), 'thigh.R': (0.08, 0, 0), 'shin.R': (-0.16, 0, 0), 'foot.R': (0.08, 0, 0),
         'upper_arm.L': (0.05 + 0.03 * b, 0.08, 0), 'forearm.L': (0.28, 0, 0), 'hand.L': (0.1, 0, 0)}
    return d, -0.014 - 0.006 * (1 - math.cos(ph)) / 2, shift(CARRY_R, -0.014 + 0.006 * b)
def walk(f):
    ph = 2 * math.pi * f / 24; s, c = math.sin(ph), math.cos(ph)
    d = {
     'thigh.L': (0.5 * s, 0, 0), 'thigh.R': (-0.5 * s, 0, 0),
     'shin.L': (-(0.08 + 0.75 * max(0, c)), 0, 0), 'shin.R': (-(0.08 + 0.75 * max(0, -c)), 0, 0),
     'foot.L': (0.25 * max(0, -s) - 0.15 * max(0, s), 0, 0), 'foot.R': (0.25 * max(0, s) - 0.15 * max(0, -s), 0, 0),
     'upper_arm.L': (-0.4 * s, 0.05, 0), 'forearm.L': (0.25 - 0.15 * s, 0, 0),
     'hips': (0, 0, -0.08 * s), 'spine': (0.06, 0, 0.08 * s), 'chest': (0.03, 0, 0.06 * s), 'neck': (-0.05, 0, -0.1 * s)}
    return d, -0.03 * (1 - abs(c)), shift(CARRY_R, 0.012 * abs(c), 0.02 * s)
def aim(f):
    ph = 2 * math.pi * f / 48; b = math.sin(ph) * 0.004
    return AIM_BODY, -0.04, shift(AIM_R, b) + shift(AIM_L, b)
bake('Idle', range(0, 49, 4), idle)
bake('Walk', range(0, 25, 2), walk)
bake('Aim', range(0, 49, 8), aim)
arm.animation_data.action = None
pose({})

# ---------------- stats and export ----------------
tris = 0
for ob in col.objects:
    if ob.type == 'MESH':
        ob.data.calc_loop_triangles(); tris += len(ob.data.loop_triangles)
print('TRIANGLES', tris, 'OBJECTS', len([o for o in col.objects if o.type == 'MESH']))
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_yup=True, export_apply=False,
                          export_animations=True, export_animation_mode='ACTIONS', export_skins=True,
                          export_morph=False, export_materials='EXPORT', export_force_sampling=True)
print('EXPORTED', OUT)
