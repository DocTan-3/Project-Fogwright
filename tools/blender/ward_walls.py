# Aldrath's ward walls: the retaining walls that hold each district up at its own level, and the pieces where they stop,
# turn and meet. The city's own warm grey stone (not the Ferrin basalt), same building blocks and baked occlusion as the
# Ferrin kit (the head of ferrin_forge.py). One GLB, one object per piece, each with a decimated _LOD1.
#
# Every wall piece has its coping at z = 0 and runs 10 m down: the game sets the coping at the height the upper district
# needs and lets the ground swallow the rest, so a wall is never stretched taller and its masonry never distorts.
# The low side (the face you see full height) is -y here, +z in the game.
#
#   python3.11 ward_walls.py -- out.glb          (RENDER=sheet.png for a Cycles contact sheet)
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'ferrin_forge.py')).read()
exec(compile(src[:src.index('# ---------------------------------------------------------------- the forge-house')], 'ferrin_forge_head', 'exec'))
random.seed(7)

# the city stone: warm grey ashlar for the faces, paler dressed stone for copings, caps and quoins, rubble for the deep footing
MATS['W_ashlar'] = ('medieval_blocks_03', 1.7, (0.62, 0.58, 0.52), 0.0, 1.0)
MATS['W_cope'] = ('medieval_blocks_03', 1.2, (0.76, 0.72, 0.64), 0.0, 0.9)
MATS['W_rubble'] = ('rock_wall_05', 2.0, (0.62, 0.57, 0.50), 0.0, 1.0)
MAT_LIST[:] = list(MATS.keys())
SAT = {'W_ashlar': 0.45, 'W_cope': 0.4, 'W_rubble': 0.4}
DEEP = -10.0

def stones(x0, x1, y0, y1, z0, z1, mat, n=None, gap=0.012, bev=0.03, jit=0.012, tag=''):
    """A course of separate dressed stones along x: copings, string courses, caps."""
    L = x1 - x0; n = n or max(1, round(L / 0.8)); w = L / n
    for i in range(n):
        dz = random.uniform(-jit, jit); dy = random.uniform(-jit, jit) * 0.5
        box((x0 + w * (i + 0.5), (y0 + y1) / 2 + dy, (z0 + z1) / 2 + dz), (w - gap, y1 - y0, z1 - z0), mat, bev, tag=tag)

def pyramid(cx, cy, z0, hw, hd, h, mat, tag=''):
    bm = bmesh.new(); b = [bm.verts.new((cx + a * hw, cy + c * hd, z0)) for a, c in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]; t = bm.verts.new((cx, cy, z0 + h))
    bm.faces.new(list(reversed(b)))
    for i in range(4): bm.faces.new([b[i], b[(i + 1) % 4], t])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, mat, tag)

PIECES = {}
T = 1.0      # the wall's thickness; the parapet sits flush with the low face and leaves a ledge on the high side
def wall():
    L = 4.2; x0, x1 = -L / 2, L / 2
    box((0, 0, (DEEP - 1.15) / 2), (L, T, -1.15 - DEEP), 'W_ashlar', 0.0)                                  # the body, down into the ground
    stones(x0, x1, -T / 2 - 0.07, T / 2 + 0.07, -1.33, -1.13, 'W_cope', n=4, bev=0.025)                     # a string course at the high ground's level
    box((0, -T / 2 + 0.36, -0.68), (L, 0.72, 0.9), 'W_ashlar', 0.0)                                          # the parapet
    stones(x0, x1, -T / 2 - 0.06, -T / 2 + 0.78, -0.23, 0.0, 'W_cope', n=5, bev=0.035, tag='cope')            # its coping, a drip on the low side
    # one buttress per module on the low face, its top sloping back into the wall below the string course
    bx = x0 + 0.45
    prism([Vector((bx + 0.4, -T / 2 + 0.02, -1.5)), Vector((bx + 0.4, -T / 2 + 0.02, DEEP)), Vector((bx + 0.4, -T / 2 - 0.6, DEEP)), Vector((bx + 0.4, -T / 2 - 0.6, -2.45))], 0.8, (1, 0, 0), 'W_ashlar', 0.03)
    prism([Vector((bx + 0.43, -T / 2 + 0.02, -1.38)), Vector((bx + 0.43, -T / 2 - 0.66, -2.42)), Vector((bx + 0.43, -T / 2 - 0.66, -2.56)), Vector((bx + 0.43, -T / 2 + 0.02, -1.52))], 0.86, (1, 0, 0), 'W_cope', 0.015)   # its sloped weathering
    for z in (-2.6, -5.6):                                                                                     # weep holes: a retaining wall drains
        box((0.9, -T / 2 - 0.005, z), (0.16, 0.06, 0.12), 'F_glass', 0.0)
        box((0.9, -T / 2 - 0.02, z - 0.11), (0.3, 0.06, 0.05), 'W_cope', 0.01)
PIECES['WardWall'] = wall

def pier(name, top, s, lantern=False):
    def make():
        h = s / 2
        box((0, 0, (DEEP + top - 0.6) / 2), (s, s, top - 0.6 - DEEP), 'W_ashlar', 0.02)
        for z0 in (-1.35, top - 0.62):                                                                         # a band at the high ground, a cap
            stones(-h - 0.08, h + 0.08, -h - 0.08, h + 0.08, z0, z0 + 0.22, 'W_cope', n=1, bev=0.035)
        for k in range(int((top + 1.1) / 0.55)):                                                               # quoins up the corners, long and short in turn
            z = -1.13 + k * 0.55
            if z + 0.5 > top - 0.62: break
            for (a, c) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
                lx, ly = (0.5, 0.3) if (k + (a * c > 0)) % 2 else (0.3, 0.5)
                box((a * (h - lx / 2 + 0.012), c * (h - ly / 2 + 0.012), z + 0.25), (lx, ly, 0.5), 'W_cope', 0.02)
        pyramid(0, 0, top - 0.4, h - 0.1, h - 0.1, 0.45 if not lantern else 0.25, 'W_cope')
        if lantern:                                                                                             # an iron lantern on a short post
            cyl((0, 0, top - 0.05), 0.13, 0.1, 0.5, 'F_iron', seg=8); cyl((0, 0, top + 0.25), 0.26, 0.26, 0.08, 'F_iron', seg=8)
            for (a, c) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]: box((a * 0.18, c * 0.18, top + 0.56), (0.04, 0.04, 0.55), 'F_iron', 0.0)
            box((0, 0, top + 0.55), (0.3, 0.3, 0.45), 'F_glow', 0.0, tag='glow')
            pyramid(0, 0, top + 0.84, 0.27, 0.27, 0.3, 'F_iron'); cyl((0, 0, top + 1.2), 0.05, 0.02, 0.15, 'F_iron', seg=6)
    return make
PIECES['WardPier'] = pier('WardPier', 0.55, 1.8)
PIECES['WardEnd'] = pier('WardEnd', 0.75, 1.7, lantern=True)

def knot():   # where walls meet: a squat corner tower, battered at the foot, a corbelled cornice and a stone cap
    h = 2.1; top = 2.7
    box((0, 0, (DEEP + top - 0.7) / 2), (2 * h, 2 * h, top - 0.7 - DEEP), 'W_ashlar', 0.02)
    stones(-h - 0.1, h + 0.1, -h - 0.1, h + 0.1, -1.36, -1.12, 'W_cope', n=3, bev=0.03)
    for k in range(9):
        z = -1.1 + k * 0.42
        if z + 0.4 > top - 0.75: break
        for (a, c) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
            lx, ly = (0.62, 0.36) if (k + (a * c > 0)) % 2 else (0.36, 0.62)
            box((a * (h - lx / 2 + 0.012), c * (h - ly / 2 + 0.012), z + 0.2), (lx, ly, 0.4), 'W_cope', 0.02)
    for side in range(4):                                                                                       # corbels under the cornice
        for i in range(5):
            u = -h + 0.42 + i * (2 * h - 0.84) / 4
            p = [(u, -h - 0.1), (h + 0.1, u), (-u, h + 0.1), (-h - 0.1, -u)][side]
            box((p[0], p[1], top - 0.9), (0.3 if side % 2 == 0 else 0.26, 0.26 if side % 2 == 0 else 0.3, 0.3), 'W_cope', 0.02)
    stones(-h - 0.22, h + 0.22, -h - 0.22, h + 0.22, top - 0.75, top - 0.45, 'W_cope', n=4, bev=0.04)
    pyramid(0, 0, top - 0.45, h + 0.05, h + 0.05, 1.5, 'W_cope'); cyl((0, 0, top + 1.2), 0.12, 0.06, 0.5, 'F_iron', seg=8)
    for side in range(4):                                                                                       # a narrow window each way
        p, n = [((0, -h), 'y'), ((h, 0), 'x'), ((0, h), 'y'), ((-h, 0), 'x')][side]
        box((p[0], p[1], 0.9), (0.22 if n == 'y' else 0.08, 0.08 if n == 'y' else 0.22, 0.75), 'F_glass', 0.0)
PIECES['WardKnot'] = knot

def gate():   # a ward gate: one round arch between two towers, a parapet over it; its street at z = 0 (scaled whole to fit)
    W, R, SP, D, PH = 10.0, 5.0, 1.6, 2.4, 8.4
    for sx in (-1, 1):
        cx = sx * (W / 2 + 1.3)
        box((cx, 0, (PH - 3) / 2), (2.6, D + 0.2, PH + 3), 'W_ashlar', 0.03)
        for k in range(int(PH / 0.5)):
            for c in (-1, 1):
                for a in (-1, 1):
                    lx, ly = (0.55, 0.32) if (k + (a > 0)) % 2 else (0.32, 0.55)
                    box((cx + a * (1.3 - lx / 2 + 0.012), c * ((D + 0.2) / 2 - ly / 2 + 0.012), k * 0.5 + 0.25), (lx, ly, 0.5), 'W_cope', 0.02)
        stones(cx - 1.45, cx + 1.45, -(D + 0.5) / 2, (D + 0.5) / 2, PH, PH + 0.3, 'W_cope', n=2, bev=0.04)
        pyramid(cx, 0, PH + 0.3, 1.3, (D + 0.3) / 2, 1.0, 'W_cope')
    n = 21
    for i in range(n):   # the voussoirs of a round arch, the keystone proud
        t0 = math.pi - i / n * math.pi; t1 = math.pi - (i + 1) / n * math.pi; tm = (t0 + t1) / 2
        r0, r1 = R, R + (0.75 if i == n // 2 else 0.62)
        pts = [Vector((r0 * math.cos(t0), -D / 2 - 0.04, SP + r0 * math.sin(t0))), Vector((r0 * math.cos(t1), -D / 2 - 0.04, SP + r0 * math.sin(t1))),
               Vector((r1 * math.cos(t1), -D / 2 - 0.04, SP + r1 * math.sin(t1))), Vector((r1 * math.cos(t0), -D / 2 - 0.04, SP + r1 * math.sin(t0)))]
        prism(pts, -(D + 0.08), (0, -1, 0), 'W_cope', 0.015)
    # the spandrels: the wall over the arch, cut round it
    for i in range(24):
        t0 = math.pi - i / 24 * math.pi; t1 = math.pi - (i + 1) / 24 * math.pi
        pts = [Vector((R * math.cos(t0), -D / 2, SP + R * math.sin(t0))), Vector((R * math.cos(t1), -D / 2, SP + R * math.sin(t1))), Vector((R * math.cos(t1), -D / 2, PH - 0.9)), Vector((R * math.cos(t0), -D / 2, PH - 0.9))]
        prism(pts, -D, (0, -1, 0), 'W_ashlar', 0.0)
    for sx in (-1, 1): box((sx * (W / 2 - 0.0), 0, SP / 2 - 1.5), (0.02, D, SP + 3), 'W_ashlar', 0.0)
    for sx in (-1, 1): stones(sx * W / 2 - (0.3 if sx > 0 else -0.3) - 0.3, sx * W / 2 - (0.3 if sx > 0 else -0.3) + 0.3, -D / 2 - 0.1, D / 2 + 0.1, SP - 0.25, SP, 'W_cope', n=1)   # imposts
    stones(-W / 2, W / 2, -D / 2 - 0.12, D / 2 + 0.12, PH - 0.95, PH - 0.75, 'W_cope', n=10, bev=0.03)        # a string course
    box((0, 0, PH - 0.3), (W, D - 0.5, 0.9), 'W_ashlar', 0.0)                                                   # the parapet
    stones(-W / 2, W / 2, -D / 2 + 0.15, D / 2 - 0.15, PH + 0.15, PH + 0.38, 'W_cope', n=12, bev=0.035)
    box((0, 0, PH - 0.85), (W, 0.6, 0.1), 'W_ashlar', 0.0)
PIECES['WardGateA'] = gate

def build(name, maker):
    PARTS.clear(); maker()
    me = bpy.data.meshes.new(name); obj = bpy.data.objects.new(name, me); scene.collection.objects.link(obj)
    for nm in MAT_LIST:
        mm = bpy.data.materials.get(nm)
        if not mm:
            mm = make_material(nm)
            if nm in SAT:
                for nd in mm.node_tree.nodes:
                    if nd.type == 'HUE_SAT': nd.inputs['Saturation'].default_value = SAT[nm]
        mm.use_backface_culling = nm != 'F_iron'; me.materials.append(mm)
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
            p = l.vert.co; u, v = ((p.y, p.z) if ax == 0 else (p.x, p.z) if ax == 1 else (p.x, p.y)); l[uvl].uv = (u / tile, v / tile)
    bm.to_mesh(me); bm.free()
    col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); me.color_attributes.active_color = col
    for d in col.data: d.color = (1, 1, 1, 1)
    return obj

scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 48; scene.render.bake.target = 'VERTEX_COLORS'; scene.world = bpy.data.worlds.new('w')
# the ground the pieces stand in, for the occlusion bake: the high side at the string course, the low side 3 m down
g1 = bpy.data.objects.new('ground_hi', bpy.data.meshes.new('g1')); scene.collection.objects.link(g1)
gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=1, y_segments=1, size=12); bmesh.ops.translate(gb, verts=gb.verts, vec=(0, 12.5, -1.15)); gb.to_mesh(g1.data); gb.free()
g2 = bpy.data.objects.new('ground_lo', bpy.data.meshes.new('g2')); scene.collection.objects.link(g2)
gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=1, y_segments=1, size=12); bmesh.ops.translate(gb, verts=gb.verts, vec=(0, -11.5, -3.6)); gb.to_mesh(g2.data); gb.free()
objs = []
for name, maker in PIECES.items():
    o = build(name, maker)
    if name == 'WardGateA': g1.hide_render = g2.hide_render = True
    else: g1.hide_render = g2.hide_render = False
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.bake(type='AO')
    col = o.data.color_attributes['Col']
    for i, v in enumerate(o.data.vertices):
        ao = 0.45 + 0.55 * col.data[i].color[0]
        grime = 0.0 if name == 'WardGateA' else max(0.0, min(0.22, (-v.co.z - 1.4) * 0.04))   # damp and grime gather down the low face
        k = ao * (1 - grime); col.data[i].color = (k, k * 0.99, k * 0.96, 1)
    lod = o.copy(); lod.data = o.data.copy(); lod.name = name + '_LOD1'; scene.collection.objects.link(lod)
    dm = lod.modifiers.new('dec', 'DECIMATE'); dm.ratio = 0.3
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = lod; lod.select_set(True); bpy.ops.object.modifier_apply(modifier='dec')
    print('%s: %d tris, LOD1 %d' % (name, sum(len(p.vertices) - 2 for p in o.data.polygons), sum(len(p.vertices) - 2 for p in lod.data.polygons))); objs += [o, lod]
for g in (g1, g2): bpy.data.objects.remove(g)
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
kw = dict(filepath=OUT, use_selection=True, export_format='GLB', export_image_format='NONE', export_materials='EXPORT', export_yup=True)
try: bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError: bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('EXPORTED', OUT)
if RENDER:   # a contact sheet: a run of wall with its pieces, seen from the low side
    for o in objs:
        if o.name.endswith('_LOD1'): o.hide_render = True
    P = {o.name: o for o in objs}
    for k in range(3):
        c = P['WardWall'].copy(); scene.collection.objects.link(c); c.location = (-8.4 + k * 4.2, 0, 0)
    P['WardWall'].location = (-12.6, 0, 0); P['WardKnot'].location = (-16.7, 0, 0); P['WardPier'].location = (-4.2 + 1.1, 0, 0)
    P['WardEnd'].location = (-1.5, 0, 0); P['WardGateA'].location = (8, 0, -3.6); P['WardGateA'].scale = (0.8, 0.8, 0.8)
    lo = bpy.data.objects.new('lo', bpy.data.meshes.new('lo')); scene.collection.objects.link(lo)
    gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=2, y_segments=2, size=40); bmesh.ops.translate(gb, verts=gb.verts, vec=(0, -39.5, -3.6)); gb.to_mesh(lo.data); gb.free()
    hi = bpy.data.objects.new('hi', bpy.data.meshes.new('hi')); scene.collection.objects.link(hi)
    gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=2, y_segments=2, size=40); bmesh.ops.translate(gb, verts=gb.verts, vec=(-20, 40.5, -1.15)); gb.to_mesh(hi.data); gb.free()
    world = scene.world; world.use_nodes = True; nt = world.node_tree; sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(25)
    nt.links.new(sky.outputs['Color'], nt.nodes['Background'].inputs['Color']); nt.nodes['Background'].inputs['Strength'].default_value = 0.3
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 2.2; sun.rotation_euler = (math.radians(55), 0, math.radians(-30)); scene.collection.objects.link(sun)
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam; cam.data.lens = 30
    cp = Vector((-3, -24, 4.5)); tgt = Vector((-3, 0, -0.5)); cam.location = cp; cam.rotation_euler = (tgt - cp).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1400, 700; scene.cycles.samples = 40; scene.view_settings.view_transform = 'AgX'; scene.render.filepath = RENDER
    bpy.ops.render.render(write_still=True); print('RENDERED', RENDER)
