# Fogwright base body, the clean way: one continuous mesh, built for painting. Exports body.glb
# Torso, limbs, hands and feet come from a skin-modifier stick figure; the head is built ring by ring and
# shaped by one smooth function (skull, jaw, brow, nose, lips, chin), then bridged to the neck with no seam.
import bpy, bmesh, math, sys
from mathutils import Vector
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
C = Vector((0, 0.002, 1.69))
def head_r(d):
    ax, ay, az = 0.093, (0.1 if d.y < 0 else 0.106), (0.116 if d.z > 0 else 0.118)
    ax *= 1 - 0.15 * sm(0.0, -0.85, d.z)          # the jaw narrows toward the chin
    ay *= 1 - 0.12 * sm(0.1, -0.9, d.z) * (d.y > 0)  # the back of the jaw tucks in
    return 1 / math.sqrt((d.x / ax) ** 2 + (d.y / ay) ** 2 + (d.z / az) ** 2)
def gauss(x, z, cx, cz, wx, wz): return math.exp(-((x - cx) / wx) ** 2 - ((z - cz) / wz) ** 2)
def head_point(th, ph):
    # th: angle around (0 = face), ph: latitude from -1 (neck) to 1 (crown)
    d = Vector((math.sin(th) * math.cos(ph * math.pi / 2), -math.cos(th) * math.cos(ph * math.pi / 2), math.sin(ph * math.pi / 2)))
    p = C + d * head_r(d)
    front = max(0.0, -d.y) ** 1.5; x, z = p.x, p.z
    nose = 0.025 * sm(1.715, 1.66, z) * (1 - sm(1.656, 1.636, z)) * math.exp(-(x / 0.0125) ** 2)
    nose += 0.006 * gauss(x, z, 0, 1.648, 0.016, 0.008)                       # nostril wings
    bump = (nose + 0.007 * gauss(x, z, 0, 1.712, 0.05, 0.009)                   # brow ridge
            - 0.008 * (gauss(x, z, 0.034, 1.686, 0.014, 0.011) + gauss(x, z, -0.034, 1.686, 0.014, 0.011))  # eye sockets
            + 0.005 * (gauss(x, z, 0.054, 1.656, 0.016, 0.014) + gauss(x, z, -0.054, 1.656, 0.016, 0.014))  # cheekbones
            + 0.004 * gauss(x, z, 0, 1.617, 0.02, 0.007)                        # lips
            - 0.003 * gauss(x, z, 0, 1.603, 0.02, 0.004)                        # under the lip
            + 0.017 * gauss(x, z, 0, 1.566, 0.03, 0.016)                        # a strong chin
            + 0.006 * gauss(x, z, 0, 1.548, 0.034, 0.012))                      # and its underside
    p.x += math.copysign(0.007, x) * gauss(abs(x), z, 0.066, 1.582, 0.02, 0.022) * (1 - max(0.0, d.y))  # jaw corners
    p.y -= bump * front
    return p
# denser around the face: warp the angles so more columns sit at the front and more rows at eye level
LON, LAT = 36, 26
def warp_th(u): return math.pi * (2 * u - 1) * (0.55 + 0.45 * abs(2 * u - 1))   # u 0..1 -> -pi..pi, dense at 0
def warp_ph(v): return -1 + 2 * v + 0.12 * math.sin(2 * math.pi * v)
hb = bmesh.new()
rings = [[hb.verts.new(C + Vector((0, 0, -head_r(Vector((0, 0, -1))))))]]
for j in range(1, LAT - 1):
    ph = warp_ph(j / (LAT - 1))
    rings.append([hb.verts.new(head_point(warp_th(i / LON), ph)) for i in range(LON)])
rings.append([hb.verts.new(C + Vector((0, 0, head_r(Vector((0, 0, 1))))))])
for j in range(len(rings) - 1):
    a, b = rings[j], rings[j + 1]
    for i in range(LON):
        if len(a) == 1: hb.faces.new((a[0], b[(i + 1) % LON], b[i]))
        elif len(b) == 1: hb.faces.new((a[i], a[(i + 1) % LON], b[0]))
        else: hb.faces.new((a[i], a[(i + 1) % LON], b[(i + 1) % LON], b[i]))
# the neck meets the head along a slanted line: under the chin in front, at the nape behind
plane = lambda co: co.z < 1.612 + 0.36 * co.y and math.hypot(co.x, co.y - 0.004) < 0.085
bmesh.ops.delete(hb, geom=[f for f in hb.faces if plane(f.calc_center_median())], context='FACES')
bm = bmesh.new(); bm.from_mesh(body.data)
bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 1.556], context='VERTS')
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
    bmesh.ops.translate(eb, verts=eb.verts, vec=(0.083 * sx, 0.012, 1.676))
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
HAIRS = []
HAIRS.append(shell('Hair_Short', -math.pi, math.pi, lambda th: hairline(th) - 0.003 - tips(9, 0.008)(th), TOP,
                   lambda th, f, p: (0.006 + 0.012 * f) * locks(th, f, 18, 0.3), wrap=True))
HAIRS.append(shell('Hair_Swept', -math.pi, math.pi, lambda th: hairline(th) - 0.004 - tips(7, 0.012)(th), TOP,
                   lambda th, f, p: (0.003 + 0.034 * f ** 0.8 * (1 + 0.45 * math.exp(-(th / 0.7) ** 2) * f)) * locks(th, f, 12, 0.4), wrap=True))
back = lambda th: sm(1.1, 1.9, abs(th))
HAIRS.append(shell('Hair_Long', -math.pi, math.pi, lambda th: hairline(th) - 0.004 - tips(6, 0.012)(th) - 0.03 * back(th), TOP,
                   lambda th, f, p: (0.009 + 0.018 * f) * locks(th, f, 10, 0.45) + 0.012 * back(th) * (1 - f),
                   lambda th, f: back(th) * (1 - f) ** 2.2 * (0.2 + 0.03 * tri(th * 2.5)), NR=18, wrap=True))
# beards: from under the jaw up to the cheeks, dipping under the lower lip in front
chinw = lambda th: math.exp(-(th / 0.5) ** 2)
beard_top = lambda th: 1.636 - 0.032 * chinw(th / 0.9)
HAIRS.append(shell('Beard_Full', -1.65, 1.65, lambda th: 1.548 - 0.01 * chinw(th), beard_top,
                   lambda th, f, p: (0.006 + 0.02 * chinw(th) * (1 - f)) * locks(th, f, 20, 0.3),
                   lambda th, f: 0.05 * chinw(th) * (1 - f) ** 2 * (1 + 0.3 * tri(th * 4)), NT=30, NR=10))
HAIRS.append(shell('Beard_Short', -1.65, 1.65, lambda th: 1.556, beard_top,
                   lambda th, f, p: (0.004 + 0.007 * chinw(th) * (1 - f)) * locks(th, f, 24, 0.25), NT=30, NR=8))
HAIRS.append(shell('Moustache', -0.42, 0.42, lambda th: 1.627, lambda th: 1.639,
                   lambda th, f, p: 0.005 + 0.004 * chinw(th / 0.4), lambda th, f: 0.014 * sm(0.18, 0.42, abs(th)) * (1 - f), NT=16, NR=4))
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
