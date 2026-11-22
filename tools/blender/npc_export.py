import bpy, sys, runpy
OUT = sys.argv[-1]
sys.argv = ['x', '--', '_full.glb']
g = runpy.run_path('tinker.py')
arm = g['arm']
DROP = ('Rifle', 'Pauldron', 'PauldronRim', 'Rivet', 'Gauge', 'Brace', 'Knee', 'Tooth', 'Loupe', 'Wrench', 'ToolRoll', 'Satchel', 'Goggle', 'Pouch')
for o in list(bpy.data.objects):
    if o.type == 'MESH' and o.name.startswith(DROP):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
import bmesh as _bm
for o in meshes:
    if o.name in ('Body', 'Shirt', 'Hand.L', 'Hand.R'):
        bm=_bm.new(); bm.from_mesh(o.data); mw=o.matrix_world
        kill=[f for f in bm.faces if (mw @ f.calc_center_median()).z < 1.49]
        _bm.ops.delete(bm, geom=kill, context='FACES'); bm.to_mesh(o.data); bm.free()
for o in meshes:
    me = o.data.copy(); o.data = me
    # bake material colours into a colour attribute
    if 'npcCol' in me.color_attributes: me.color_attributes.remove(me.color_attributes['npcCol'])
    for a in list(me.color_attributes): me.color_attributes.remove(a)
    ca = me.color_attributes.new('npcCol', 'BYTE_COLOR', 'CORNER')
    for p in me.polygons:
        m = me.materials[min(p.material_index, len(me.materials) - 1)] if len(me.materials) else None
        c = (0.8, 0.8, 0.8, 1)
        if m and m.node_tree:
            b = m.node_tree.nodes.get('Principled BSDF')
            if b: bc = b.inputs['Base Color'].default_value; c = (bc[0], bc[1], bc[2], 1)
        for li in p.loop_indices: ca.data[li].color = c
    # make every part skinned to the armature
    mw = o.matrix_world.copy()
    bone = o.parent_bone if o.parent_type == 'BONE' else None
    me.transform(mw)
    o.parent = None; o.matrix_world = mw.Identity(4)
    if bone:
        for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
        vg = o.vertex_groups.new(name=bone); vg.add(list(range(len(me.vertices))), 1.0, 'REPLACE')
    for md in list(o.modifiers): o.modifiers.remove(md)
    me.materials.clear()
bpy.ops.object.select_all(action='DESELECT')
for o in meshes: o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.join()
npc = bpy.context.view_layer.objects.active; npc.name = 'Townsfolk'
tris0 = sum(len(p.vertices) - 2 for p in npc.data.polygons)
dm = npc.modifiers.new('Dec', 'DECIMATE'); dm.ratio = 3400 / tris0
bpy.ops.object.modifier_apply(modifier='Dec')
mat = bpy.data.materials.new('Townsfolk'); mat.use_nodes = True
nt = mat.node_tree; bsdf = nt.nodes.get('Principled BSDF'); bsdf.inputs['Roughness'].default_value = 0.8
vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'npcCol'; nt.links.new(vc.outputs['Color'], bsdf.inputs['Base Color'])
npc.data.materials.append(mat)
for p in npc.data.polygons: p.use_smooth = True
md = npc.modifiers.new('Armature', 'ARMATURE'); md.object = arm; npc.parent = arm
print('NPC TRIS', sum(len(p.vertices) - 2 for p in npc.data.polygons), 'from', tris0)
bpy.ops.object.select_all(action='DESELECT'); npc.select_set(True); arm.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
                          export_skins=True, export_materials='EXPORT', export_force_sampling=True, export_vertex_color='ACTIVE')
print('EXPORTED', OUT)
