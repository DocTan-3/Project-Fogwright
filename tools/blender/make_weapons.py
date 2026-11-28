# Fogwright's own props, the ones no pack has (tools/assets/INVENTORY.md lists them): built from simple shapes, real-world
# sizes, origin at the base centre, a few hundred triangles each, palette materials by name.
#   python3 make_props.py <out dir>      (godot/assets/props/fogwright)
import bpy,bmesh,math,os,sys
from mathutils import Vector,Matrix
OUT=os.path.abspath(sys.argv[-1]); os.makedirs(OUT,exist_ok=True)
PAL={}
def clear():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
    for m in list(bpy.data.materials): bpy.data.materials.remove(m)
    PAL.clear()
def mat(name):
    if name not in PAL: PAL[name]=bpy.data.materials.new(name)
    return PAL[name]
PARTS=[]
def part(kind,m,loc=(0,0,0),rot=(0,0,0),**k):
    """a primitive: box (size), cyl (r, h, n, r2), sphere (r, n, sz), cone (r, h, n)"""
    bm=bmesh.new()
    if kind=='box':
        bmesh.ops.create_cube(bm,size=1); sx,sy,sz=k['size']
        for v in bm.verts: v.co=Vector((v.co.x*sx,v.co.y*sy,v.co.z*sz+sz/2))
    elif kind=='cyl':
        bmesh.ops.create_cone(bm,cap_ends=k.get('caps',True),segments=k.get('n',8),radius1=k['r'],radius2=k.get('r2',k['r']),depth=k['h'])
        if rot==(0,0,0):   # standing cylinders sit on their base; turned ones are centred on loc
            for v in bm.verts: v.co.z+=k['h']/2
    elif kind=='sphere':
        bmesh.ops.create_uvsphere(bm,u_segments=k.get('n',8),v_segments=max(3,k.get('n',8)//2),radius=k['r'])
        for v in bm.verts: v.co.z*=k.get('sz',1.0)
    elif kind=='plane':
        sx,sy=k['size']; bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=0.5)
        for v in bm.verts: v.co=Vector((v.co.x*sx,0,v.co.y*sy+sy/2))
    R=Matrix.Rotation(rot[2],4,'Z')@Matrix.Rotation(rot[1],4,'Y')@Matrix.Rotation(rot[0],4,'X')
    bmesh.ops.transform(bm,matrix=Matrix.Translation(Vector(loc))@R,verts=bm.verts)
    me=bpy.data.meshes.new('p'); bm.to_mesh(me); bm.free(); me.materials.append(mat(m))
    o=bpy.data.objects.new('p',me); bpy.context.scene.collection.objects.link(o); PARTS.append(o); return o
def done(name):
    global PARTS
    bpy.ops.object.select_all(action='DESELECT')
    for o in PARTS: o.select_set(True)
    bpy.context.view_layer.objects.active=PARTS[0]; bpy.ops.object.join(); o=bpy.context.view_layer.objects.active; o.name=name
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=1.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,name+'.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    t=sum(len(p.vertices)-2 for p in o.data.polygons); print('  %-16s %4d tris  %s'%(name,t,tuple(round(v,2) for v in o.dimensions)))
    PARTS=[]; clear()
TAU=math.pi*2
clear()
# Fogwright's test weapons, one per family with no pack model (docs/weapons.md: Wayfolk common iron, plain forged iron, ash
# wood, leather grips). Real sizes. The origin is the main grip and the weapon runs along +Z here (+Y in Godot): the
# handle across the palm, as the bronze sword from the props kit does, so one grip suits them all (Weapons.DEFS "grip").
#   python3 make_weapons.py <out dir>      (godot/assets/weapons/fogwright)
# smith's warhammer: an ash haft, a leather grip, an iron head with a striking face and a short peen
part('cyl','WoodTrim',(0,0,-0.14),r=0.022,h=0.72,n=8)
part('cyl','Cloth_Dark',(0,0,-0.12),r=0.026,h=0.2,n=8)
part('cyl','Iron',(0,0,-0.16),r=0.03,h=0.04,n=8)
part('box','Iron',(0,0,0.5),size=(0.08,0.08,0.11))
part('cyl','Iron',(0.12,0,0.555),(0,math.pi/2,0),r=0.055,h=0.16,n=8)
part('cyl','Iron',(0.205,0,0.555),(0,math.pi/2,0),r=0.06,h=0.03,n=8)
part('cyl','Iron',(-0.11,0,0.555),(0,math.pi/2,0),r=0.03,r2=0.012,h=0.14,n=6)
done('Warhammer_Iron')
# flintlock pistol: a curved walnut stock in the hand, the barrel out along the fingers (-X here), a brass butt cap,
# the lock and the hammer on the side
part('box','WoodTrim_Dark',(0.01,0,-0.07),(0,0.25,0),size=(0.045,0.032,0.13))
part('sphere','MetalOrnaments',(0.03,0,-0.075),r=0.03,n=8,sz=0.8)
part('box','WoodTrim_Dark',(-0.09,0,0.065),size=(0.2,0.034,0.04))
part('cyl','Iron',(-0.15,0,0.095),(0,math.pi/2,0),r=0.013,h=0.26,n=8)
part('cyl','Iron',(-0.28,0,0.095),(0,math.pi/2,0),r=0.016,h=0.012,n=8)
part('box','Iron',(-0.01,0.019,0.07),size=(0.05,0.006,0.03))
part('box','Iron',(0.0,0.012,0.1),(0,0.5,0),size=(0.012,0.012,0.035))
part('box','Iron',(-0.02,0,0.035),size=(0.025,0.006,0.025))
done('Pistol_Flintlock')
# ash shortbow: the grip in the hand, two limbs curving forward (-X) to the tips, the string behind (+X)
pts=[]
for i in range(13):
    t=-1+i/6; z=t*0.6; x=-0.11*(1-t*t)+0.02
    pts.append((x,z))
for i in range(12):
    (x0,z0),(x1,z1)=pts[i],pts[i+1]; L=math.hypot(x1-x0,z1-z0); r=0.016 if abs(i-5.5)<2 else 0.011
    part('cyl','WoodTrim',((x0+x1)/2,0,(z0+z1)/2),(0,math.atan2(x1-x0,z1-z0),0),r=r,h=L+0.01,n=6)
part('cyl','Cloth_Dark',(0.0,0,-0.06),r=0.022,h=0.12,n=8)
x0,z0=pts[0]; x1,z1=pts[-1]
part('box','Rope',(0.04,0,-0.6),size=(0.004,0.004,1.2))
done('Shortbow_Ash')
# brass wand: a short rod with a leather grip, a brass collar and a glowing crystal in a claw
part('cyl','WoodTrim_Dark',(0,0,-0.08),r=0.012,r2=0.009,h=0.36,n=8)
part('cyl','Cloth_Dark',(0,0,-0.07),r=0.015,h=0.1,n=8)
part('cyl','MetalOrnaments',(0,0,0.27),r=0.016,h=0.03,n=8)
for k in range(3):
    a=k/3*TAU; part('box','MetalOrnaments',(math.cos(a)*0.012,math.sin(a)*0.012,0.3),(math.sin(a)*0.3,-math.cos(a)*0.3,0),size=(0.006,0.006,0.05))
part('sphere','Glow',(0,0,0.32),r=0.02,n=6,sz=1.4)
done('Wand_Brass')
