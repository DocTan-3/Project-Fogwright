# Fogwright building kit: Victorian rowhouses, castle wall, round tower, gatehouse. Exports kit.glb
import bpy, bmesh, math, sys
from mathutils import Vector, Matrix

OUT = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.context.scene.collection

def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple((v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c) + (1.0,)

class Kit:
    def __init__(s, name):
        s.name = name; s.bm = bmesh.new(); s.cl = s.bm.loops.layers.color.new('Col')
    def _add(s, g, M, color):
        bmesh.ops.transform(g, matrix=M, verts=g.verts)
        vm = {v: s.bm.verts.new(v.co) for v in g.verts}
        c = lin(color)
        for f in g.faces:
            nf = s.bm.faces.new([vm[v] for v in f.verts])
            for l in nf.loops: l[s.cl] = c
        g.free()
    def box(s, sx, sy, sz, x, y, z, color, rz=0, rx=0):
        g = bmesh.new(); bmesh.ops.create_cube(g, size=1)
        self_M = Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X') @ Matrix.Diagonal((sx, sy, sz, 1))
        s._add(g, self_M, color)
    def cyl(s, r1, r2, h, seg, x, y, z, color, rx=0):
        g = bmesh.new(); bmesh.ops.create_cone(g, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
        s._add(g, Matrix.Translation((x, y, z + h / 2)) @ Matrix.Rotation(rx, 4, 'X'), color)
    def prism(s, w, d, h, x, y, z, color, rz=0):  # triangular gable along x, ridge on top
        g = bmesh.new()
        v = [g.verts.new(p) for p in [(-w/2, -d/2, 0), (w/2, -d/2, 0), (w/2, d/2, 0), (-w/2, d/2, 0), (-w/2, 0, h), (w/2, 0, h)]]
        for f in [(0, 1, 2, 3), (0, 4, 5, 1), (3, 2, 5, 4), (0, 3, 4), (1, 5, 2)]: g.faces.new([v[i] for i in f])
        s._add(g, Matrix.Translation((x, y, z)) @ Matrix.Rotation(rz, 4, 'Z'), color)
    def frustum(s, w0, d0, w1, d1, h, x, y, z, color):  # mansard roof block
        g = bmesh.new()
        v = [g.verts.new(p) for p in [(-w0/2, -d0/2, 0), (w0/2, -d0/2, 0), (w0/2, d0/2, 0), (-w0/2, d0/2, 0),
                                      (-w1/2, -d1/2, h), (w1/2, -d1/2, h), (w1/2, d1/2, h), (-w1/2, d1/2, h)]]
        for f in [(0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7), (4, 5, 6, 7), (3, 2, 1, 0)]: g.faces.new([v[i] for i in f])
        s._add(g, Matrix.Translation((x, y, z)), color)
    def finish(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me = bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        ob = bpy.data.objects.new(s.name, me); col.objects.link(ob)
        mat = bpy.data.materials.get('Kit') or bpy.data.materials.new('Kit')
        if not mat.node_tree:
            mat.use_nodes = True
        nt = mat.node_tree; b = nt.nodes.get('Principled BSDF')
        if not any(n.type == 'VERTEX_COLOR' for n in nt.nodes):
            vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'; nt.links.new(vc.outputs['Color'], b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.85
        me.materials.append(mat)
        print(s.name, 'tris', sum(len(p.vertices) - 2 for p in me.polygons))
        return ob

# --- Victorian rowhouse: front faces -y, width along x, 8 m wide, 9 m deep
def rowhouse(name, brick, trim, roof, floors, bay, mansard, door):
    k = Kit(name); W, D, F = 8.0, 9.0, 3.3
    H = 0.8 + floors * F
    k.box(W + 0.3, D + 0.3, 0.8, 0, 0, 0.4, '#8f877b')                      # stone plinth
    k.box(W, D, floors * F, 0, 0, 0.8 + floors * F / 2, brick)              # brick body
    for f in range(1, floors):
        k.box(W + 0.12, D + 0.12, 0.18, 0, 0, 0.8 + f * F, trim)            # string courses
    k.box(W + 0.5, D + 0.5, 0.45, 0, 0, H + 0.2, trim)                      # cornice
    for sx in (-1, 1):
        k.box(0.35, D + 0.1, floors * F, sx * (W / 2 - 0.05), 0, 0.8 + floors * F / 2, trim)   # quoins / pilasters
    y = -D / 2
    for f in range(floors):
        zc = 0.8 + f * F + F * 0.55
        xs = ([-2.6, 2.6] if f == 0 else [-2.6, 0, 2.6])
        for x in xs:
            if f == 0 and abs(x - (-2.6 if door < 0 else 2.6)) < 0.1:
                continue
            k.box(1.05, 0.2, 1.75, x, y - 0.02, zc, '#2a2a33')                                  # glass
            k.box(1.35, 0.14, 0.18, x, y - 0.06, zc + 1.0, trim)                                # lintel
            k.box(1.35, 0.3, 0.14, x, y - 0.12, zc - 0.95, trim)                                # sill
            k.box(0.07, 0.24, 1.7, x, y - 0.05, zc, trim)                                       # mullion
    dx = -2.6 if door < 0 else 2.6
    k.box(1.4, 0.2, 2.5, dx, y - 0.02, 0.8 + 1.25, '#4a2e22')                                  # door
    k.box(1.9, 0.2, 0.4, dx, y - 0.08, 0.8 + 2.7, trim)                                         # door hood
    for i in range(3):
        k.box(2.0, 0.45, 0.27, dx, y - 0.3 - i * 0.42, 0.13 + (2 - i) * 0.27, '#9d958a')      # steps
    if bay:  # bay window over the ground and first floor
        bw, bd = 3.0, 1.0
        k.box(bw, bd, F * 2 - 0.4, 0, y - bd / 2, 0.8 + F - 0.2, brick)
        for f in range(2):
            k.box(bw - 0.6, 0.12, 1.8, 0, y - bd - 0.04, 0.8 + f * F + F * 0.55, '#2a2a33')
        k.box(bw + 0.3, bd + 0.3, 0.3, 0, y - bd / 2, 0.8 + F * 2 - 0.4, trim)
        k.prism(bw + 0.2, bd + 0.2, 0.8, 0, y - bd / 2, 0.8 + F * 2 - 0.25, roof)
    if floors > 2:  # wrought-iron balcony
        k.box(3.2, 0.9, 0.14, 0 if not bay else 2.6, y - 0.45, 0.8 + 2 * F + 0.05, trim)
        k.box(3.2, 0.06, 0.9, 0 if not bay else 2.6, y - 0.88, 0.8 + 2 * F + 0.5, '#26262b')
    if mansard:
        k.frustum(W + 0.3, D + 0.3, W - 2.2, D - 2.2, 3.0, 0, 0, H + 0.4, roof)
        for x in (-2.2, 2.2):  # dormers
            k.box(1.4, 1.6, 1.7, x, -D / 2 + 1.3, H + 1.6, trim)
            k.box(0.9, 0.12, 1.1, x, -D / 2 + 0.48, H + 1.6, '#2a2a33')
            k.prism(1.6, 1.8, 0.7, x, -D / 2 + 1.3, H + 2.45, roof, rz=math.pi / 2)
    else:
        k.prism(W + 0.6, D + 0.8, 3.6, 0, 0, H + 0.4, roof)
    for x in (-W / 2 + 1.0, W / 2 - 1.0):  # chimney stacks with pots
        top = H + (3.4 if mansard else 4.2)
        k.box(1.3, 0.8, top - H + 0.6, x, 1.5, H + (top - H) / 2, brick)
        k.box(1.5, 1.0, 0.25, x, 1.5, top + 0.4, trim)
        for o in (-0.3, 0.3):
            k.cyl(0.16, 0.13, 0.55, 6, x + o, 1.5, top + 0.5, '#9a5a3a')
    if name.endswith('C'):  # light steampunk: a brass pipe and gauge on the side, rooftop vent
        k.cyl(0.14, 0.14, H + 1.2, 6, W / 2 + 0.25, 1.0, 0.2, '#b8893e')
        k.cyl(0.35, 0.35, 0.15, 10, W / 2 + 0.3, 1.0, 2.6, '#b8893e', rx=math.pi / 2)
    return k.finish()

rowhouse('RowA', '#9a4a36', '#e3dccb', '#3f4a5c', 3, True, True, -1)
rowhouse('RowB', '#c9b48e', '#f1ecdf', '#4a3f3a', 3, False, False, 1)
rowhouse('RowC', '#7a3c31', '#d9cfba', '#2f3640', 4, True, True, 1)

# --- castle wall section: 24 m long, 6 m thick, along x; outside faces +y
k = Kit('WallSeg'); L, T, Hh = 24.0, 6.0, 22.0
k.box(L, T, Hh, 0, 0, Hh / 2, '#a8a091')
k.box(L + 0.2, T + 1.0, 1.4, 0, 0, 0.7, '#8f877b')                      # batter at the base
for sy in (-1, 1):
    k.box(L, 0.9, 1.6, 0, sy * (T / 2 - 0.2), Hh + 0.8, '#a8a091')       # parapets
    for i in range(8):
        k.box(1.6, 0.9, 1.4, -L / 2 + 1.5 + i * 3.0, sy * (T / 2 - 0.2), Hh + 2.3, '#a8a091')   # merlons
for i in range(6):
    k.box(0.5, 0.2, 1.6, -L / 2 + 2 + i * 4.0, T / 2 + 0.05, 12, '#3a3632')   # arrow slits outside
k.box(L, 0.4, 0.4, 0, T / 2 + 0.3, Hh - 0.5, '#8f877b')                   # corbel line
k.finish()

# --- round tower
k = Kit('Tower')
k.cyl(8.6, 7.6, 2.0, 12, 0, 0, 0, '#8f877b')
k.cyl(7.4, 7.0, 30, 12, 0, 0, 2.0, '#a8a091')
k.cyl(8.2, 8.2, 1.6, 12, 0, 0, 32, '#8f877b')
for i in range(12):
    a = i / 12 * math.pi * 2
    k.box(1.8, 1.2, 1.6, math.cos(a) * 7.8, math.sin(a) * 7.8, 34.4, '#a8a091', rz=a + math.pi / 2)
k.cyl(7.6, 0.4, 9, 12, 0, 0, 33.6, '#3f4a5c')                             # conical slate roof
for i in range(4):
    a = i / 4 * math.pi * 2 + 0.4
    k.box(0.6, 0.3, 1.8, math.cos(a) * 7.2, math.sin(a) * 7.2, 18, '#3a3632', rz=a + math.pi / 2)
k.finish()

# --- gatehouse: twin towers and an arch, opening 18 m wide, outside faces +y
k = Kit('Gatehouse')
for sx in (-1, 1):
    k.cyl(7.4, 7.0, 36, 12, sx * 16.5, 0, 0, '#a8a091')
    k.cyl(7.6, 0.4, 10, 12, sx * 16.5, 0, 36, '#3f4a5c')
k.box(26, 7, 8, 0, 0, 25, '#a8a091')                                      # bridge over the gate
k.box(26.4, 7.6, 1.2, 0, 0, 29.6, '#8f877b')
for i in range(7):
    k.box(1.8, 1.0, 1.6, -10.5 + i * 3.5, 3.4, 31, '#a8a091')
k.box(2.6, 1.2, 5.2, 0, 3.6, 22, '#d9cfba')                               # crest plaque
k.cyl(1.0, 1.0, 0.3, 14, 0, 4.3, 22.3, '#c9a046', rx=math.pi / 2)        # brass clock face
k.finish()

for o in col.objects: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_materials='EXPORT', export_vertex_color='ACTIVE')
print('EXPORTED', OUT)
