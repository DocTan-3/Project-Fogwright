# Cut a Quaternius base body down to the parts an outfit leaves bare, so outfits replace the body rather than sit over
# it (the muscular body otherwise pokes through the clothes):  python3 body_parts.py in.gltf out.gltf keep_hands(0/1)
import bpy,bmesh,sys
import os
src,dst,hands=os.path.abspath(sys.argv[1]),os.path.abspath(sys.argv[2]),sys.argv[3]=='1'   # absolute: the exporter writes beside dst
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=src)
keep_bones=['Head','neck_01']+(['hand_l','hand_r']+[f'{f}_0{k}_{s}' for f in ('index','middle','ring','pinky','thumb') for k in (1,2,3) for s in 'lr'] if hands else [])
for o in bpy.data.objects:
    if o.type!='MESH' or not o.vertex_groups: continue
    if o.name.startswith(('Eye',)): continue
    gi={g.index:g.name for g in o.vertex_groups}
    bm=bmesh.new(); bm.from_mesh(o.data); dl=bm.verts.layers.deform.active
    drop=[v for v in bm.verts if sum(w for g,w in v[dl].items() if gi.get(g) in keep_bones)<0.35]
    bmesh.ops.delete(bm,geom=drop,context='VERTS'); bm.to_mesh(o.data); bm.free()
    print(o.name,'kept',len(o.data.vertices))
bpy.ops.export_scene.gltf(filepath=dst,export_format='GLTF_SEPARATE',export_skins=True,export_animations=False)
