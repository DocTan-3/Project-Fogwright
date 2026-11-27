# Bring pieces from downloaded CC0 packs into Fogwright: one small .glb per piece, its textures dropped and its materials
# renamed to palette keys (scripts/palette.gd colours them and adds the greyscale detail), so they match everything else.
#   python3 import_props.py <docks .glb> <village obj folder> <godot/assets/props>
import bpy,os,sys
docks,village,out=[os.path.abspath(a) for a in sys.argv[-3:]]
PAL={}
def clear():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m)
    for i in list(bpy.data.images): bpy.data.images.remove(i)
    PAL.clear()
# palette material by name, plain colour (the palette replaces it in the game)
def pal(name):
    if name not in PAL:
        m=bpy.data.materials.new(name); m.use_nodes=True
        m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.6,0.6,0.6,1); PAL[name]=m
    return PAL[name]
def export(o,folder,name):
    os.makedirs(folder,exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
    o.location=(0,0,0); o.name=name
    bpy.ops.export_scene.gltf(filepath=os.path.join(folder,name+'.glb'),export_format='GLB',use_selection=True,export_yup=True,
                              export_apply=True,export_texcoords=True,export_normals=True,export_materials='EXPORT')
    return sum(len(p.vertices)-2 for p in o.data.polygons)
def remap(o,table):
    for s in o.material_slots:
        n=s.material.name if s.material else ''
        key=next((v for k,v in table if k in n),None)
        if key is None: print('   unmapped material',n,'on',o.name); key='WoodTrim'
        s.material=pal(key)
# ---- Wooden Docks (loafbrr, CC0)
DOCKS=['Floor_Dock','Floor_Dock_End','Floor_Dock_Half','Floor_Dock_End_Half','Floor_Support','Floor_Support_Half','Floor_Support_VHalf',
       'Support_Post','Support_Post_Half','Dock_Bollard_1','Dock_Bollard_3','Boat_A_1','Boat_A_2','Boat_B_1','Boat_B_2','Boat_Stand','Paddle_1',
       'Harpoon_1','Props_Rack','Props_Rack_Fish','Props_Fish_1','Props_Barrel','Props_Box','Props_Crate','Props_Table_1','Props_Table_3','Rope_Coil.001']
DMAT=[('DockTrim','WoodTrim_Wear'),('BoatTrim','WoodTrim'),('Beams','WoodTrim_Dark'),('Floor','WoodTrim'),('Fish','Fish'),('Harpoon','Iron'),('Rope','Rope')]
clear(); bpy.ops.import_scene.gltf(filepath=docks); total=0
for name in DOCKS:
    o=bpy.data.objects.get(name)
    if not o: print('missing',name); continue
    o.parent=None; remap(o,DMAT); t=export(o,os.path.join(out,'docks'),name.replace('.001','')); total+=t; print('  docks/%s %d tris'%(name,t))
# ---- Modular Village Pack (Fertile Soil Productions, CC0)
VILLAGE=['Prop_Hay_1','Prop_Well_1','Wall_Prop_Bell_1','Wall_Prop_Sign_1','Prop_Lamp_Street','Prop_Cart_1_Hay','Prop_Cart_1','Prop_Ladder_1','Prop_Broom','Prop_Barrel_1_Open']
VMAT=[('Stucco','Plaster'),('Wood_Light','WoodTrim_Light'),('Wood_Medium','WoodTrim'),('Wood_Darker','WoodTrim_Dark'),('Wood_Dark','WoodTrim_Wear'),
      ('Dark_Red_Roof','RoundTiles_Dark'),('Red_Roof','RoundTiles'),('Stone_Brit_Gray_Dark','RockTrim_Dark'),('Stone_Bri_Gray_Lighter','RockTrim_Light'),
      ('Stone','RockTrim'),('Burlap','Cloth'),('Straw','Thatch'),('Iron_Grey_-_Dark','Iron_Dark'),('Iron_Grey_-_Light','Iron_Light'),('Iron','Iron'),
      ('Candlelight','Glow'),('Water','RockTrim_Dark'),('Dirt','earth'),('Grass','earth')]
for name in VILLAGE:
    clear(); bpy.ops.wm.obj_import(filepath=os.path.join(village,name+'.obj'))
    obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    bpy.ops.object.select_all(action='DESELECT')
    for o in obs: o.select_set(True)
    bpy.context.view_layer.objects.active=obs[0]
    if len(obs)>1: bpy.ops.object.join()
    o=bpy.context.view_layer.objects.active; remap(o,VMAT)
    bpy.ops.object.transform_apply(location=False,rotation=True,scale=True)
    t=export(o,os.path.join(out,'village2'),name); total+=t; print('  village2/%s %d tris'%(name,t))
print('total %d tris'%total)
