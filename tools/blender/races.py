# Fogwright peoples: one rig, interchangeable parts, colour roles. Exports peoples.glb
# Every vertex carries meta = (role/32, piece/32, shade): the game picks each person's palette and which pieces show.
import bpy, bmesh, sys, math
OUT = sys.argv[-1]
src = open('tinker.py').read(); src = src[:src.index('bpy.ops.export_scene')]
sys.argv = ['x', '--', '/tmp/_unused.glb']; g = {'__name__': 'x'}; exec(compile(src, 'tinker.py', 'exec'), g)
arm, part, MT, mat = g['arm'], g['part'], g['MT'], g['mat']
T, R, S, upd = g['T'], g['R'], g['S'], g['upd']
bm_sphere, bm_cyl, bm_box, bm_torus, bm_cap = g['bm_sphere'], g['bm_cyl'], g['bm_box'], g['bm_torus'], g['bm_cap']
from mathutils import Vector

arm.data.pose_position = 'REST'; upd()
for k, n, c in [('ink', 'Ink', '#2f5fb8'), ('wrap', 'Wrap', '#d8c9a8'), ('fur', 'Fur', '#8a7058'), ('cloak', 'Cloak', '#3d5a34'),
                ('tabard', 'Tabard', '#3f4a6c'), ('metal', 'Metal', '#9aa2a8'), ('rope', 'Rope', '#b49a6a')]:
    MT[k] = mat(n, c, 0.8)
H = 0.022  # part() lowers head pieces by this much; we measured the finished head

def ell(c, semi, seg=12, ring=8):
    bm = bm_sphere(1, seg, ring); bmesh.ops.transform(bm, matrix=T(*c) @ S(*semi), verts=bm.verts); return bm
def join_bm(*bms):
    out = bmesh.new()
    for b in bms:
        me = bpy.data.meshes.new('_t'); b.to_mesh(me); b.free(); out.from_mesh(me); bpy.data.meshes.remove(me)
    return out
I = T(0, 0, 0)
# --- beard: jaw, chin and a fall onto the chest

# --- long hair: a fuller back of the head and a braid down the back
part('LongHair', join_bm(ell((0, 0.05, 1.7 + H), (0.108, 0.078, 0.108)), ell((0, 0.085, 1.585 + H), (0.092, 0.042, 0.085))), 'hair', I, 'head')
bt = bmesh.new()
for i in range(5):
    z = 1.58 - i * 0.045; r = 0.026 - i * 0.002
    b2 = ell((0, 0.115 + i * 0.004, z + H), (r, r * 0.9, 0.03)); me = bpy.data.meshes.new('_b'); b2.to_mesh(me); b2.free(); bt.from_mesh(me); bpy.data.meshes.remove(me)
part('Braid', bt, 'hair', I, 'head')
# --- Zarhim head wrap
part('Headwrap', join_bm(bm_torus(0.099, 0.033, 18, 7), ), 'wrap', T(0, 0.004, 1.738 + H) @ S(1.0, 1.12, 1.0) @ R('X', -0.15), 'head')
part('WrapCrown', bm_cap(0.108, 14, 7, 0.5), 'wrap', T(0, 0.006, 1.732 + H) @ S(1.02, 1.1, 1.3), 'head')
part('WrapBand', bm_torus(0.098, 0.03, 18, 6), 'wrap', T(0, 0.006, 1.79 + H) @ S(1.0, 1.1, 1.0) @ R('Y', 0.32) @ R('X', 0.1), 'head')
part('WrapTail', bm_box(0.06, 0.02, 0.17), 'wrap', T(0.035, 0.105, 1.63 + H) @ R('X', 0.25), 'head', False)
# --- Penitent hood: open at the face, falling to the shoulders
hb = bm_sphere(0.142, 16, 12)
bmesh.ops.transform(hb, matrix=S(1.0, 1.08, 1.05), verts=hb.verts)
kill = [f for f in hb.faces if f.calc_center_median().y < -0.03 and f.calc_center_median().z < 0.085 and abs(f.calc_center_median().x) < 0.12]
bmesh.ops.delete(hb, geom=kill, context='FACES')
part('Hood', hb, 'cloak', T(0, 0.014, 1.69 + H), 'head')
part('HoodMantle', bm_cyl(0.245, 0.1, 0.15, 14), 'cloak', T(0, 0.01, 1.465) @ S(1.0, 0.78, 1.0), 'chest')
# --- Hrimfolk fur mantle
part('Fur', join_bm(*[ell((math.cos(a) * 0.168, 0.012 + math.sin(a) * 0.13, 1.47 + 0.012 * math.sin(3 * a)), (0.072, 0.064, 0.058), 8, 6) for a in [i / 11 * 2 * math.pi for i in range(11)]],
                  ), 'fur', I, 'chest')
part('FurRing', bm_torus(0.165, 0.06, 16, 6), 'fur', T(0, 0.012, 1.47) @ S(1.08, 0.86, 0.9), 'chest')
part('FurPelt', ell((0, 0.135, 1.31), (0.17, 0.035, 0.17), 10, 7), 'fur', I, 'chest')
# --- Ferrin leather apron
part('ApronBib', bm_box(0.22, 0.014, 0.2), 'leather', T(0, -0.137, 1.3), 'chest', False)
part('ApronSkirt', bm_box(0.3, 0.014, 0.44), 'leather', T(0, -0.152, 0.87) @ R('X', -0.04), 'hips', False)
# --- Ruadhan cloak with a collar and brooch
part('Cloak', bm_box(0.44, 0.026, 0.82), 'cloak', T(0, 0.168, 1.07) @ R('X', 0.12), 'chest', False)
part('CloakCollar', bm_torus(0.13, 0.03, 16, 6), 'cloak', T(0, 0.01, 1.485) @ S(1.25, 1.0, 0.8), 'chest')
part('Brooch', ell((0.1, -0.11, 1.44), (0.022, 0.012, 0.022), 8, 6), 'metal', I, 'chest')
# --- Aurelan feudal tabard
part('TabardFront', bm_box(0.27, 0.014, 0.62), 'tabard', T(0, -0.131, 1.12), 'spine', False)
part('TabardBack', bm_box(0.27, 0.014, 0.62), 'tabard', T(0, 0.122, 1.12), 'spine', False)
# --- watch helm
part('Helm', bm_cap(0.127, 16, 8, 0.55), 'metal', T(0, 0.0, 1.70 + H) @ S(1.0, 1.08, 1.0), 'head')
part('HelmBrim', bm_torus(0.123, 0.013, 18, 5), 'metal', T(0, 0.0, 1.715 + H) @ S(1.0, 1.08, 1.0), 'head')
part('HelmNasal', bm_box(0.02, 0.012, 0.075), 'metal', T(0, -0.135, 1.69 + H), 'head', False)
# --- Penitent rope belt
part('Rope', bm_torus(0.19, 0.013, 18, 5), 'rope', T(0, 0, 1.06) @ S(1.02, 0.72, 1.0), 'hips')
part('RopeEnd', bm_box(0.016, 0.016, 0.22), 'rope', T(0.08, -0.14, 0.94), 'hips', False)

# --- Ilvari ink: copied from the face itself, lifted a hair off the skin
body = bpy.data.objects['Body']
ink = body.copy(); ink.data = body.data.copy(); ink.name = 'Ink'; bpy.context.scene.collection.objects.link(ink)
bm = bmesh.new(); bm.from_mesh(ink.data); mw = ink.matrix_world
def inked(c):
    x, y, z = c.x, c.y, c.z
    if y > -0.04: return False
    if abs(x) < 0.007 and 1.70 < z < 1.79: return True               # line down the brow
    if 0.032 < abs(x) < 0.08 and 1.648 < z < 1.662 and y < -0.05: return True  # across the cheekbones
    if 0.006 < abs(x) < 0.016 and 1.53 < z < 1.58: return True       # two lines on the chin
    return False
kill = [f for f in bm.faces if not inked(mw @ f.calc_center_median())]
bmesh.ops.delete(bm, geom=kill, context='FACES')
for v in bm.verts: v.co += v.normal * 0.0018
bm.to_mesh(ink.data); bm.free()
ink.data.materials.clear(); ink.data.materials.append(MT['ink'])
print('INK faces', len(ink.data.polygons))
# --- beard: grown out of the jaw and chin, so it follows the face
bd = body.copy(); bd.data = body.data.copy(); bd.name = 'Beard'; bpy.context.scene.collection.objects.link(bd)
bm = bmesh.new(); bm.from_mesh(bd.data); mw = bd.matrix_world
def bearded(c):
    if c.y > 0.035 or c.z > 1.632 or c.z < 1.5: return False
    if abs(c.x) < 0.03 and 1.592 < c.z < 1.632 and c.y < -0.08: return False   # leave the mouth clear
    if c.z > 1.6 and abs(c.x) < 0.06 and c.y < -0.095: return False             # and the upper lip
    return True
kill = [f for f in bm.faces if not bearded(mw @ f.calc_center_median())]
bmesh.ops.delete(bm, geom=kill, context='FACES')
for v in bm.verts:
    c = v.co; chin = max(0.0, 1.0 - abs(c.x) / 0.06) * max(0.0, (1.585 - c.z) / 0.06)
    v.co += v.normal * (0.012 + 0.022 * chin)
    v.co.z -= 0.05 * chin * chin; v.co.y -= 0.012 * chin
bm.to_mesh(bd.data); bm.free()
bd.data.materials.clear(); bd.data.materials.append(MT['hair'])
for md in list(bd.modifiers): bd.modifiers.remove(md)
dm = bd.modifiers.new('Dec', 'DECIMATE'); dm.ratio = 0.4
with bpy.context.temp_override(object=bd, active_object=bd): bpy.ops.object.modifier_apply(modifier='Dec')
so = bd.modifiers.new('Sol', 'SOLIDIFY'); so.thickness = 0.01; so.offset = -1
with bpy.context.temp_override(object=bd, active_object=bd): bpy.ops.object.modifier_apply(modifier='Sol')
print('BEARD faces', len(bd.data.polygons))

# --- assemble the townsfolk mesh, as npc_export did, but with roles and pieces
DROP = ('Rifle', 'Pauldron', 'PauldronRim', 'Rivet', 'Gauge', 'Brace', 'Knee', 'Tooth', 'Loupe', 'Wrench', 'ToolRoll', 'Satchel', 'Goggle', 'Pouch')
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o.name.startswith(DROP): bpy.data.objects.remove(o, do_unlink=True)
upd()
ROLE = {'Skin': 0, 'Hair': 1, 'Shirt': 2, 'Vest': 3, 'Trousers': 4, 'Shorts': 4, 'Leather': 5, 'LeatherDark': 5, 'Scarf': 6, 'Coat': 7, 'Eye': 8,
        'Ink': 10, 'Wrap': 11, 'Fur': 12, 'Cloak': 13, 'Tabard': 14, 'Metal': 15, 'Brass': 15, 'Iron': 15, 'Lining': 16, 'Boots': 17, 'Rope': 5}
PIECE = [('HairCap', 1), ('Sideburn', 1), ('Tache', 2), ('Vest', 3), ('Button', 3), ('Coat', 4), ('ScarfTail', 5), ('Scarf', 5), ('Belt', 6), ('Buckle', 6),
         ('Beard', 7), ('LongHair', 8), ('Braid', 8), ('Headwrap', 9), ('WrapCrown', 9), ('WrapBand', 9), ('WrapTail', 9), ('HoodMantle', 10), ('Hood', 10),
         ('FurPelt', 11), ('FurRing', 11), ('Fur', 11), ('ApronBib', 12), ('ApronSkirt', 12), ('Ink', 13), ('CloakCollar', 14), ('Cloak', 14), ('Brooch', 14),
         ('TabardFront', 15), ('TabardBack', 15), ('HelmBrim', 16), ('HelmNasal', 16), ('Helm', 16), ('RopeEnd', 17), ('Rope', 17), ('GlovesHand', 0), ('Gloves', 18)]
def piece_of(n):
    for p, i in PIECE:
        if n.startswith(p): return i
    return 0
def role_of(n, mname):
    if n.startswith('EyeWhite'): return 9
    if n.startswith('GlovesHand'): return 18
    if n.startswith(('Sleeve', 'Cuff')): return 19
    return ROLE.get(mname, 2)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in meshes:
    if o.name in ('Body', 'Hand.L', 'Hand.R'):
        bm = bmesh.new(); bm.from_mesh(o.data); mw = o.matrix_world
        cut = 1.34 if o.name == 'Body' else 1.49
        kill = [f for f in bm.faces if (mw @ f.calc_center_median()).z < cut or (o.name == 'Body' and abs((mw @ f.calc_center_median()).x) > 0.2)]
        bmesh.ops.delete(bm, geom=kill, context='FACES'); bm.to_mesh(o.data); bm.free()
meshes = [o for o in meshes if len(o.data.polygons)]
tri = lambda o: sum(len(p.vertices) - 2 for p in o.data.polygons)
total = sum(tri(o) for o in meshes); ratio = min(1.0, max(0.26, 4200 / total)); print('TOTAL TRIS', total, 'ratio', round(ratio, 3))
for o in meshes:
    me = o.data.copy(); o.data = me
    bpy.context.view_layer.objects.active = o
    for md in list(o.modifiers): o.modifiers.remove(md)
    if tri(o) > 110 and ratio < 1 and o.name not in ('Ink', 'Beard'):
        r_ = 0.38 if o.name == 'Body' else ratio
        dm = o.modifiers.new('Dec', 'DECIMATE'); dm.ratio = r_
        with bpy.context.temp_override(object=o, active_object=o): bpy.ops.object.modifier_apply(modifier='Dec')
    for a in list(me.color_attributes): me.color_attributes.remove(a)
    ca = me.color_attributes.new('meta', 'FLOAT_COLOR', 'CORNER')
    pc = piece_of(o.name)
    for p in me.polygons:
        m = me.materials[min(p.material_index, len(me.materials) - 1)] if len(me.materials) else None
        rl = role_of(o.name, m.name if m else '')
        if o.name == 'Body' and (o.matrix_world @ p.center).z < 1.475: rl = 2   # chest under the collar is shirt, not skin
        sh = 0.82 if (m and m.name == 'Lining') else 1.0
        for li in p.loop_indices: ca.data[li].color = (rl / 32, pc / 32, sh, 1)
    mw = o.matrix_world.copy(); bone = o.parent_bone if o.parent_type == 'BONE' else None
    me.transform(mw); o.parent = None; o.matrix_world = mw.Identity(4)
    if bone:
        for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
        vg = o.vertex_groups.new(name=bone); vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    for md in list(o.modifiers): o.modifiers.remove(md)
    me.materials.clear()
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
npc = bpy.context.view_layer.objects.active; npc.name = 'Folk'
m = bpy.data.materials.new('Folk'); m.use_nodes = True
nt = m.node_tree; b = nt.nodes.get('Principled BSDF'); vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'meta'; nt.links.new(vc.outputs['Color'], b.inputs['Base Color'])
npc.data.materials.append(m)
for p in npc.data.polygons: p.use_smooth = True
npc.data.color_attributes.active_color = npc.data.color_attributes['meta']
md = npc.modifiers.new('Armature', 'ARMATURE'); md.object = arm; npc.parent = arm
arm.data.pose_position = 'POSE'
print('FOLK TRIS', tri(npc))
bpy.ops.object.select_all(action='DESELECT'); npc.select_set(True); arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
                          export_skins=True, export_materials='EXPORT', export_force_sampling=True, export_vertex_color='ACTIVE')
print('EXPORTED', OUT)
