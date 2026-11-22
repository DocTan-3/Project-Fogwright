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
     ((0, 0.006, 1.52), 0.054, 0.056, 4),       # 5 neck
     ((0, 0.004, 1.585), 0.058, 0.062, 5)]      # 6 neck top (head is built separately)
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
    ax, ay, az = 0.086, (0.099 if d.y < 0 else 0.106), (0.118 if d.z > 0 else 0.128)
    ax *= 1 - 0.3 * sm(0.0, -0.85, d.z)          # the jaw narrows toward the chin
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
            + 0.008 * gauss(x, z, 0, 1.572, 0.026, 0.014))                      # chin
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
        if v.co.x > 0: v.co.x *= 0.4
    bmesh.ops.rotate(eb, verts=eb.verts, cent=(0, 0, 0), matrix=g['R']('Z', -0.35 * sx))
    bmesh.ops.translate(eb, verts=eb.verts, vec=(0.083 * sx, 0.012, 1.676))
    if sx < 0: bmesh.ops.reverse_faces(eb, faces=eb.faces)
    em = bpy.data.meshes.new('ear'); eb.to_mesh(em); eb.free()
    bm = bmesh.new(); bm.from_mesh(body.data); bm.from_mesh(em); bm.to_mesh(body.data); bm.free(); bpy.data.meshes.remove(em)
bmesh_fix = bmesh.new(); bmesh_fix.from_mesh(body.data); bmesh.ops.recalc_face_normals(bmesh_fix, faces=bmesh_fix.faces); bmesh_fix.to_mesh(body.data); bmesh_fix.free()
for p in body.data.polygons: p.use_smooth = True
print('BODY tris', sum(len(p.vertices) - 2 for p in body.data.polygons))
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
arm.data.pose_position = 'POSE'
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
                          export_skins=True, export_materials='EXPORT', export_force_sampling=True, export_vertex_color='ACTIVE')
print('EXPORTED', OUT)
