# Brings a generated ship (e.g. from Meshy) into Fogwright: bow turned to +x like our boats, scaled to its real length,
# its waterline put at the origin plane, its texture shrunk for phones and made matte (no shine, no metal).
#   python3 import_ship.py <in.glb> <out.glb> <bow: +x|-x> <length m> <waterline height in the source, 0..1 of keel..top>
import bpy,math,os,sys
src,dst,bow,length,wl=sys.argv[-5],sys.argv[-4],sys.argv[-3],float(sys.argv[-2]),float(sys.argv[-1])
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
bpy.ops.import_scene.gltf(filepath=os.path.abspath(src))
ms=[o for o in bpy.data.objects if o.type=='MESH']
bpy.ops.object.select_all(action='DESELECT')
for o in ms: o.select_set(True)
bpy.context.view_layer.objects.active=ms[0]
if len(ms)>1: bpy.ops.object.join()
o=bpy.context.view_layer.objects.active; o.parent=None
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
vs=[v.co for v in o.data.vertices]; xs=[v.x for v in vs]; zs=[v.z for v in vs]
L=max(xs)-min(xs); s=length/L; keel=min(zs); top=max(zs)
water=keel+(top-keel)*wl
for v in o.data.vertices:
    x,y,z=v.co.x-(min(xs)+max(xs))/2,v.co.y,v.co.z
    if bow=='-x': x,y=-x,-y
    v.co=(x*s,y*s,(z-water)*s)
o.data.update()
for m in o.data.materials:
    if m.use_nodes:
        b=m.node_tree.nodes.get('Principled BSDF')
        if b: b.inputs['Metallic'].default_value=0.0; b.inputs['Roughness'].default_value=1.0
for im in bpy.data.images:
    if im.size[0]>1024: im.scale(1024,1024)
o.name='Last_Ship'
bpy.ops.export_scene.gltf(filepath=os.path.abspath(dst),export_format='GLB',use_selection=False,export_yup=True,export_apply=True,export_image_format='AUTO')
d=o.dimensions; print('ship %d tris, %.1f x %.1f x %.1f m, keel %.2f m below the water'%(sum(len(p.vertices)-2 for p in o.data.polygons),d.x,d.y,d.z,(water-keel)*s))
