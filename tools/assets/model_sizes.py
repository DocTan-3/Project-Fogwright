# Measures every prop model the plans can place (godot/data/doodad_models.json) and writes its footprint and height in
# Godot's axes (x across, z deep, y up) to godot/data/model_sizes.json, so a plan reserves the real size of each prop.
#   python3 tools/assets/model_sizes.py
import bpy,json,os
G=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','godot')
kinds=json.load(open(os.path.join(G,'data','doodad_models.json'))); out={}
for kind,m in kinds.items():
    path=os.path.join(G,m['model'].replace('res://',''))
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    bpy.ops.import_scene.gltf(filepath=path)
    xs=[];ys=[];zs=[]
    for o in bpy.data.objects:
        if o.type!='MESH': continue
        for v in o.data.vertices:
            w=o.matrix_world@v.co; xs.append(w.x); ys.append(w.y); zs.append(w.z)
    out[m['model']]=[round(max(xs)-min(xs),3),round(max(ys)-min(ys),3),round(max(zs)-min(zs),3)]   # x, z (Blender y), height
json.dump(out,open(os.path.join(G,'data','model_sizes.json'),'w'),indent=1)
for k,v in out.items(): print('%-55s %s'%(k.replace('res://assets/',''),v))
