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
def done(name,center=False):
    global PARTS
    bpy.ops.object.select_all(action='DESELECT')
    for o in PARTS: o.select_set(True)
    bpy.context.view_layer.objects.active=PARTS[0]; bpy.ops.object.join(); o=bpy.context.view_layer.objects.active; o.name=name
    if center:   # its footprint centred on the origin, so a planned spot is where it stands
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        xs=[v.co.x for v in o.data.vertices]; ys=[v.co.y for v in o.data.vertices]; cx,cy=(min(xs)+max(xs))/2,(min(ys)+max(ys))/2
        for v in o.data.vertices: v.co.x-=cx; v.co.y-=cy
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.uv.cube_project(cube_size=1.0)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,name+'.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
    t=sum(len(p.vertices)-2 for p in o.data.polygons); print('  %-16s %4d tris  %s'%(name,t,tuple(round(v,2) for v in o.dimensions)))
    PARTS=[]; clear()
TAU=math.pi*2
clear()
# woodpile: split logs stacked in a pyramid against nothing, ends showing
for row,(n,z) in enumerate(((4,0.11),(3,0.31),(2,0.5))):
    for i in range(n):
        x=(i-(n-1)/2)*0.24; part('cyl','WoodTrim_Dark',(x,0,z),(math.pi/2,0,0),r=0.11,h=0.9,n=7)
done('Woodpile')
# washing line: two posts, a sagging line, three cloths
for x in (-1.7,1.7): part('cyl','WoodTrim_Wear',(x,0,0),r=0.05,h=1.9,n=6)
for i in range(6):
    a,b=-1.7+i*3.4/6,-1.7+(i+1)*3.4/6; za=1.85-0.18*math.sin(math.pi*(a+1.7)/3.4); zb=1.85-0.18*math.sin(math.pi*(b+1.7)/3.4)
    part('box','Rope',((a+b)/2,0,(za+zb)/2-0.01),(0,-math.atan2(zb-za,b-a),0),size=(math.hypot(b-a,zb-za),0.02,0.02))
for x,w,h,m in ((-0.9,0.7,0.8,'Cloth'),(0.05,0.9,0.6,'Cloth_Light'),(0.95,0.5,0.7,'Cloth_Dark')):
    z=1.85-0.18*math.sin(math.pi*(x+1.7)/3.4); part('box',m,(x,0,z-h),size=(w,0.02,h))
done('Washing_Line')
# trough: a wooden box with water
part('box','WoodTrim_Wear',(0,-0.36,0),size=(2.2,0.08,0.5)); part('box','WoodTrim_Wear',(0,0.36,0),size=(2.2,0.08,0.5))
part('box','WoodTrim_Wear',(-1.06,0,0),size=(0.08,0.64,0.5)); part('box','WoodTrim_Wear',(1.06,0,0),size=(0.08,0.64,0.5))
part('box','WoodTrim_Dark',(0,0,0),size=(2.1,0.64,0.08)); part('box','sea_Dark',(0,0,0.36),size=(2.04,0.64,0.02))
done('Trough')
# quench trough: smaller, stone
part('box','RockTrim',(0,-0.26,0),size=(1.4,0.12,0.6)); part('box','RockTrim',(0,0.26,0),size=(1.4,0.12,0.6))
part('box','RockTrim',(-0.64,0,0),size=(0.12,0.4,0.6)); part('box','RockTrim',(0.64,0,0),size=(0.12,0.4,0.6))
part('box','RockTrim_Dark',(0,0,0),size=(1.3,0.42,0.1)); part('box','sea_Dark',(0,0,0.48),size=(1.18,0.42,0.02))
done('Quench_Trough')
# net rack: two posts and a bar, a net hanging over it with cork floats
for x in (-1.3,1.3): part('cyl','WoodTrim_Wear',(x,0,0),r=0.06,h=1.9,n=6)
part('cyl','WoodTrim_Wear',(0,0,1.82),(0,math.pi/2,0),r=0.04,h=2.7,n=6)
for s in (-1,1): part('box','Rope',(0,s*0.12,0.45),(s*0.12,0,0),size=(2.4,0.015,1.35))
for i in range(7): part('sphere','WoodTrim_Light',(-1.1+i*0.37,0.2,0.55+0.1*(i%2)),r=0.05,n=6)
done('Net_Rack')
# lobster pots: three domed creels, stacked
for (x,y,z) in ((-0.32,0,0),(0.32,0,0),(0,0,0.42)):
    part('cyl','Rope_Dark',(x,y,z),r=0.28,h=0.08,n=10); part('sphere','Rope',(x,y,z+0.22),r=0.28,n=10,sz=0.75)   # a dome on its base, nothing below
done('Lobster_Pots')
# scarecrow: post, crossbar, coat, sack head, hat
part('cyl','WoodTrim_Wear',(0,0,0),r=0.05,h=2.1,n=6); part('box','WoodTrim_Wear',(0,0,1.55),size=(1.5,0.08,0.08))
part('box','Cloth_Dark',(0,0,0.95),size=(0.55,0.28,0.7)); part('box','Cloth_Dark',(0,0,1.5),size=(1.2,0.22,0.16))
part('sphere','Cloth',(0,0,1.95),r=0.17,n=8); part('cyl','Thatch_Dark',(0,0,2.08),r=0.32,h=0.04,n=10); part('cyl','Thatch_Dark',(0,0,2.1),r=0.14,r2=0.11,h=0.18,n=8)
for s in (-1,1): part('cyl','Thatch',(s*0.75,0,1.48),r=0.06,r2=0.02,h=0.12,n=5)   # straw at the cuffs
done('Scarecrow')
# notice post: a post with a small roofed board and pinned notices
part('box','WoodTrim_Wear',(0,0,0),size=(0.12,0.12,1.9)); part('box','WoodTrim',(0,-0.07,1.0),size=(0.9,0.04,0.65))
part('box','WoodTrim_Dark',(0,-0.02,1.7),(0.35,0,0),size=(1.05,0.4,0.04))
for (x,z,w,h) in ((-0.22,1.3,0.3,0.25),(0.18,1.25,0.26,0.3),(-0.05,1.05,0.4,0.18)): part('box','Cloth_Light',(x,-0.095,z),size=(w,0.005,h))
done('Notice_Post')
# charcoal heap and manure heap: low mounds
part('sphere','Iron_Dark',(0,0,0),r=0.8,n=10,sz=0.45); done('Charcoal_Heap')
part('sphere','earth_Dark',(0,0,0),r=0.65,n=9,sz=0.5); part('sphere','Thatch_Dark',(0.25,0.1,0.15),r=0.25,n=6,sz=0.5); done('Manure_Heap')
# hen coop: a small house on legs with a ramp
for (x,y) in ((-0.5,-0.4),(0.5,-0.4),(-0.5,0.4),(0.5,0.4)): part('box','WoodTrim_Wear',(x,y,0),size=(0.07,0.07,0.4))
part('box','WoodTrim',(0,0,0.4),size=(1.15,0.95,0.55))
for s in (-1,1): part('box','Thatch',(0,s*0.27,0.97),(s*0.75,0,0),size=(1.3,0.68,0.05))
part('box','WoodTrim_Wear',(0,-0.75,0.02),(-0.55,0,0),size=(0.3,0.75,0.03))
done('Hen_Coop')
# bell frame: two posts, a beam, a roof, the alarm bell
for x in (-0.6,0.6): part('box','WoodTrim_Wear',(x,0,0),size=(0.16,0.16,2.5))
part('box','WoodTrim',(0,0,2.4),size=(1.5,0.2,0.18))
for s in (-1,1): part('box','WoodTrim_Dark',(0,s*0.22,2.62),(s*0.6,0,0),size=(1.7,0.55,0.04))
part('cyl','MetalOrnaments',(0,0,1.85),r=0.26,r2=0.13,h=0.42,n=12); part('cyl','MetalOrnaments_Dark',(0,0,1.83),r=0.29,r2=0.26,h=0.05,n=12)
part('cyl','Rope',(0.35,0,0.9),r=0.012,h=1.5,n=4)
done('Bell_Frame')
# staddle stone: the mushroom stone a granary stands on
part('cyl','RockTrim',(0,0,0),r=0.2,r2=0.11,h=0.5,n=8); part('cyl','RockTrim_Light',(0,0,0.5),r=0.32,r2=0.3,h=0.1,n=10)
done('Staddle_Stone')
# salt pan: a shallow iron pan on a stone firebox, open at the front, white salt crust
part('box','RockTrim',(0,0,0),size=(1.9,1.3,0.5)); part('box','Iron_Dark',(0,-0.66,0.05),size=(0.6,0.02,0.3))
part('box','Iron',(0,0,0.5),size=(1.8,1.2,0.12)); part('box','Plaster_Light',(0,0,0.6),size=(1.66,1.06,0.02))
done('Salt_Pan')
# village waystone: one step, a tapering stone with a lamp niche and carved road lines
part('box','RockTrim_Dark',(0,0,0),size=(2.0,2.0,0.25))
bm_stone=part('cyl','RockTrim',(0,0,0.25),r=0.42,r2=0.32,h=1.9,n=4); bm_stone.rotation_euler.z=math.pi/4
part('box','Iron_Dark',(0,-0.25,1.45),size=(0.26,0.12,0.3)); part('sphere','Glow',(0,-0.26,1.56),r=0.07,n=6)
for z in (0.7,0.85,1.0): part('box','RockTrim_Dark',(0,-0.31+0.06*(z-0.7),z),size=(0.4,0.02,0.03))
done('Waystone_Village')
# dry-stone wall: a 2 m segment of rough fieldstones in four courses, no mortar, flat capstones on top (the well-off's
# garden walls); seeded, so every build makes the same stones
import random
rnd=random.Random(11)
z=0.0
for course,(h,shade) in enumerate(((0.3,'RockTrim_Dark'),(0.28,'RockTrim'),(0.26,'RockTrim'),(0.24,'RockTrim_Light'))):
    x=-1.0+(0.25 if course%2 else 0.0)*rnd.random()
    while x<1.0:
        w=min(rnd.uniform(0.32,0.55),1.0-x)
        if w<0.12: break
        d=0.55-course*0.05
        part('box',rnd.choice([shade,'RockTrim','RockTrim_Dark']) if course<3 else shade,(x+w/2,rnd.uniform(-0.03,0.03),z),(rnd.uniform(-0.04,0.04),rnd.uniform(-0.05,0.05),rnd.uniform(-0.06,0.06)),size=(w-0.03,d,h-0.02))
        x+=w
    z+=h
x=-1.0
while x<1.0:
    w=min(rnd.uniform(0.35,0.6),1.0-x)
    part('box','RockTrim_Light',(x+w/2,0,z),(0,0,rnd.uniform(-0.05,0.05)),size=(w-0.02,0.5,0.1)); x+=w
done('Drystone_Wall')
# a wooden garden gate between two stone gateposts, 1.2 m opening
for sx in (-0.8,0.8): part('box','RockTrim',(sx,0,0),size=(0.4,0.55,1.35)); part('box','RockTrim_Light',(sx,0,1.35),size=(0.46,0.6,0.1))
for zz in (0.25,0.95): part('box','WoodTrim',(0,0,zz),size=(1.2,0.06,0.12))
for k in range(6): part('box','WoodTrim_Wear',(-0.5+k*0.2,0,0.1),size=(0.1,0.05,1.0))
part('box','WoodTrim_Dark',(0,0,0.55),(0,0.75,0),size=(1.3,0.05,0.09))
done('Garden_Gate')
# wattle hurdle: hazel rods woven between seven stakes, 2 m long, about 1 m tall (the poor's yards and plots)
for k in range(7): part('cyl','WoodTrim_Wear',(-0.96+k*0.32,0,0),r=0.035,r2=0.025,h=1.1,n=4)
for row in range(6):
    zz=0.14+row*0.15
    for k in range(6):
        off=0.035*(1 if (k+row)%2 else -1)
        part('box','Thatch_Dark' if row%3 else 'WoodTrim_Light',(-0.8+k*0.32,off,zz),(0,0,0.1*(1 if (k+row)%2 else -1)),size=(0.34,0.03,0.11))
done('Wattle_Fence')
# forest trees: cheap enough to plant thousands as the wall of woods round the village (the kit's trees are 1,600-6,300
# triangles; these are 200-320): pines of drooping, jagged tiers and oaks of several lumpy crowns, palette colours
import random as _r
R2=_r.Random(5)
def jag(o,amt):   # roughen a mesh's vertices so no two trees look turned on a lathe
    for v in o.data.vertices: v.co.x+=R2.uniform(-amt,amt); v.co.y+=R2.uniform(-amt,amt); v.co.z+=R2.uniform(-amt*0.6,amt*0.6)
for k,(h,layers) in enumerate(((8.0,5),(10.5,6))):
    part('cyl','WoodTrim_Dark',(0,0,0),r=0.22,r2=0.08,h=h*0.55,n=6)
    for l in range(layers):
        z=h*0.18+l*(h*0.74/layers); r=2.1*(1.0-l/(layers+0.4))+0.25
        o=part('cyl',['Leaf_Dark','Leaf','Leaf_Dark'][l%3],(0,0,z),r=r,r2=0.05,h=h*0.3,n=9); jag(o,0.18)
    o=part('cyl','Leaf',(0,0,h*0.9),r=0.45,r2=0.02,h=h*0.18,n=6)
    done('Forest_Pine_%d'%(k+1))
for k,(h,blobs) in enumerate(((7.0,((0,0,0,2.1),(1.2,0.5,-0.7,1.6),(-1.1,-0.6,-0.5,1.5),(0.3,-1.0,0.6,1.3))),(8.5,((0,0,0.2,2.4),(1.3,-0.4,-0.9,1.8),(-1.2,0.7,-0.8,1.7),(0.2,-1.2,0.6,1.4),(-0.4,1.0,0.9,1.3))))):
    part('cyl','WoodTrim_Dark',(0,0,0),r=0.26,r2=0.16,h=h*0.62,n=6)
    for (x,y,dz,r) in ((0.9,0.3,-1.6,0.08),(-0.8,-0.4,-1.4,0.08)):   # two limbs reaching into the crown
        part('cyl','WoodTrim_Dark',(x*0.5,y*0.5,h*0.45),(0.5*y,-0.5*x,0),r=0.1,r2=0.06,h=1.6,n=5)
    for (x,y,dz,r) in blobs:
        o=part('sphere',['Leaf','Leaf_Dark'][int(r*10)%2],(x,y,h*0.68+dz),r=r,n=9,sz=0.8); jag(o,0.2)
    done('Forest_Broadleaf_%d'%(k+1))
# chopping block: a stout oak round with its axe-scarred top (the hatchet waits in it, beat B)
part('cyl','WoodTrim_Dark',(0,0,0),r=0.3,r2=0.27,h=0.55,n=10); part('cyl','WoodTrim_Light',(0,0,0.55),r=0.27,h=0.02,n=10)
done('Chopping_Block')
# the village gate: two timber towers with plank walls and a lookout under a shingle roof, a lintel beam over the 7 m
# opening, and two plank gate leaves with iron straps standing open inward (it is day; beat D breaks them)
for sx in (-1,1):
    cx=sx*4.5
    for (dx,dy) in ((-0.9,-0.9),(0.9,-0.9),(-0.9,0.9),(0.9,0.9)): part('box','WoodTrim_Dark',(cx+dx,dy,0),size=(0.3,0.3,6.2))
    for k in range(9):   # horizontal planks round the lower tower
        z=0.1+k*0.42
        for (px,py,w,d) in ((cx,-1.0,2.0,0.08),(cx,1.0,2.0,0.08),(cx-1.0,0,0.08,2.0),(cx+1.0,0,0.08,2.0)):
            part('box','WoodTrim' if k%2 else 'WoodTrim_Wear',(px,py,z),size=(w,d,0.4))
    part('box','WoodTrim_Dark',(cx,0,4.0),size=(2.6,2.6,0.2))                       # the lookout floor
    for (px,py,w,d) in ((cx,-1.25,2.6,0.08),(cx,1.25,2.6,0.08),(cx-1.25,0,0.08,2.6),(cx+1.25,0,0.08,2.6)):
        part('box','WoodTrim_Wear',(px,py,4.2),size=(w,d,0.9))                       # its parapet
    for sgn in (-1,1): part('box','Thatch_Dark',(cx,sgn*0.75,6.5),(sgn*0.62,0,0),size=(3.0,1.85,0.1))
part('box','WoodTrim_Dark',(0,0,4.0),size=(9.2,0.45,0.45))                              # the lintel over the opening
for sx in (-1,1):   # the leaves, swung open inward against the towers
    hx=sx*3.4
    for k in range(7): part('box','WoodTrim',(hx,0.25+k*0.5,0.1),size=(0.12,0.48,3.4))
    for z in (0.5,1.7,2.9): part('box','Iron',(hx-sx*0.08,1.85,z),size=(0.03,3.4,0.12))
    part('box','WoodTrim_Dark',(hx-sx*0.08,1.85,1.75),(0.85,0,0),size=(0.05,0.12,4.4))
done('Village_Gate')
# the lighthouse: a squat beacon tower on a rock base at the breakwater's end, the kind a harbour master would pay for:
# rough limewashed stone tapering up, one door, two slit windows, a corbelled gallery with an iron rail, a lantern room
# of iron frames round a lamp, and a conical cap
part('cyl','RockTrim_Dark',(0,0,-0.6),r=3.0,r2=2.6,h=1.4,n=10)                          # the rock it stands on
part('cyl','Plaster',(0,0,0.8),r=2.0,r2=1.5,h=8.0,n=12)                                 # the tower
part('cyl','RockTrim',(0,0,0.8),r=2.05,r2=1.95,h=0.6,n=12)                              # its stone plinth course
part('box','WoodTrim_Dark',(0,-1.98,0.8),(0.0,0,0),size=(0.9,0.12,1.9))                 # the door, facing the breakwater
for z,a in ((3.5,0.6),(6.0,-0.9)): part('box','Iron_Dark',(1.75*math.sin(a),-1.75*math.cos(a)+0.02,z),(0,0,a),size=(0.22,0.15,0.7))
part('cyl','RockTrim',(0,0,8.8),r=1.55,r2=2.2,h=0.5,n=12)                               # corbels under the gallery
part('cyl','RockTrim_Light',(0,0,9.3),r=2.25,h=0.18,n=12)                               # the gallery floor
for k in range(12):
    a=k*math.pi/6; part('box','Iron_Dark',(2.15*math.cos(a),2.15*math.sin(a),9.48),size=(0.05,0.05,0.9))
part('cyl','Iron_Dark',(0,0,10.35),r=2.18,h=0.06,n=12,caps=False)                       # the rail
part('cyl','Iron_Dark',(0,0,9.48),r=1.2,h=0.25,n=8)                                     # lantern room sill
for k in range(8):
    a=k*math.pi/4; part('box','Iron_Dark',(1.1*math.cos(a),1.1*math.sin(a),9.7),size=(0.07,0.07,1.6))
part('sphere','Glow',(0,0,10.4),r=0.55,n=8)                                             # the lamp
part('cyl','Iron_Dark',(0,0,11.3),r=1.3,r2=0.1,h=1.3,n=8)                               # the cap
part('cyl','Iron',(0,0,12.6),r=0.06,h=0.6,n=4)
done('Lighthouse')
# ---- the smithy (docs/research/smithy.md): what a working village smithy has
# forge: a waist-high stone hearth, brick rim, glowing coals in the fire pot, a stone hood narrowing into a chimney
# that rises through the roof; its back (local +y) goes against the wall
part('box','RockTrim_Dark',(0,0,0),size=(1.6,1.3,0.78))
part('box','RedBrick',(0,0,0.78),size=(1.6,1.3,0.12))
part('box','Iron_Dark',(0,-0.1,0.86),size=(0.7,0.6,0.06)); part('box','Glow',(0,-0.1,0.9),size=(0.55,0.45,0.05))
part('box','Iron_Dark',(0,0.55,0.9),size=(0.24,0.2,0.18))                                 # the tuyere, where the bellows blow in
part('cyl','RockTrim',(0,0.2,1.6),r=1.0,r2=0.45,h=1.1,n=4).rotation_euler.z=math.pi/4     # the hood
part('box','RockTrim',(0,0.3,2.7),size=(0.7,0.7,2.3))                                     # the chimney, up through the roof
part('box','RockTrim_Light',(0,0.3,5.0),size=(0.85,0.85,0.15))
done('Forge',True)
# great bellows: two wedge boards with leather between, a nozzle to the forge, on a frame, worked by a rocker pole
part('box','WoodTrim',(0,0,0),size=(0.12,0.12,0.9)); part('box','WoodTrim',(0,1.0,0),size=(0.12,0.12,0.9))
part('box','WoodTrim_Dark',(0,0.5,0.85),size=(0.1,1.2,0.1))
for z,sh in ((0.95,'WoodTrim'),(1.35,'WoodTrim')):
    part('cyl',sh,(0,0.5,z),r=0.55,r2=0.12,h=0.06,n=3).rotation_euler.z=-math.pi/2
part('cyl','Cloth_Dark',(0,0.5,1.0),r=0.5,r2=0.11,h=0.35,n=3).rotation_euler.z=-math.pi/2   # the leather
part('cyl','Iron_Dark',(0,-0.25,1.15),(math.pi/2,0,0),r=0.06,h=0.5,n=6)                  # the nozzle
part('box','WoodTrim_Dark',(0,0.5,1.8),size=(0.08,0.08,0.9)); part('box','WoodTrim_Wear',(0,1.0,2.25),(math.pi/2-0.35,0,0),size=(0.07,0.07,1.6))   # the rocker pole
done('Great_Bellows',True)
# slack tub: a half barrel of water, iron hoops
part('cyl','WoodTrim_Wear',(0,0,0),r=0.38,r2=0.42,h=0.55,n=10)
for z in (0.08,0.45): part('cyl','Iron_Dark',(0,0,z),r=0.405+0.03*z/0.55,h=0.05,n=10)
part('cyl','sea_Dark',(0,0,0.48),r=0.38,h=0.02,n=10)
done('Slack_Tub',True)
# coal bin: a plank box of charcoal
for (x,y,w,d) in ((0,-0.4,0.9,0.06),(0,0.4,0.9,0.06),(-0.45,0,0.06,0.8),(0.45,0,0.06,0.8)): part('box','WoodTrim_Dark',(x,y,0),size=(w,d,0.5))
part('sphere','Iron_Dark',(0,0,0.25),r=0.42,n=7,sz=0.5)
done('Coal_Bin',True)
# tool rack: a board on two posts with tongs and hammers hanging from pegs
for x in (-0.65,0.65): part('box','WoodTrim_Dark',(x,0,0),size=(0.08,0.08,1.6))
part('box','WoodTrim',(0,0,1.3),size=(1.4,0.05,0.18))
for k in range(6):   # tongs: two long jaws each
    x=-0.55+k*0.14; part('box','Iron_Dark',(x,-0.05,0.75),(0,0.06,0),size=(0.025,0.025,0.6)); part('box','Iron_Dark',(x+0.03,-0.05,0.75),(0,-0.06,0),size=(0.025,0.025,0.6))
for k in range(3):   # hammers
    x=0.3+k*0.14; part('box','WoodTrim_Light',(x,-0.05,0.95),size=(0.03,0.03,0.38)); part('box','Iron',(x,-0.05,0.9),size=(0.12,0.05,0.06))
done('Tool_Rack',True)
# swage block on its stand, and the mandrel cone beside it
part('box','WoodTrim_Dark',(0,0,0),size=(0.55,0.55,0.5)); part('box','Iron_Dark',(0,0,0.5),size=(0.42,0.42,0.14))
for (x,y) in ((-0.1,-0.1),(0.1,-0.1),(-0.1,0.1),(0.1,0.1)): part('box','Iron',(x,y,0.62),size=(0.06,0.06,0.025))
part('cyl','Iron_Dark',(0.45,0.1,0),r=0.12,r2=0.03,h=0.75,n=7)
done('Swage_Block',True)
# workbench with a leg vise
part('box','WoodTrim',(0,0,0.82),size=(1.9,0.65,0.08))
for (x,y) in ((-0.85,-0.25),(0.85,-0.25),(-0.85,0.25),(0.85,0.25)): part('box','WoodTrim_Dark',(x,y,0),size=(0.08,0.08,0.82))
part('box','WoodTrim_Dark',(0,0.2,0.2),size=(1.8,0.25,0.04))                               # shelf
part('box','Iron_Dark',(-0.6,-0.38,0),size=(0.08,0.08,0.95)); part('box','Iron_Dark',(-0.6,-0.4,0.86),size=(0.16,0.12,0.12))   # the leg vise
part('cyl','Iron',(-0.6,-0.5,0.9),(math.pi/2,0,0),r=0.015,h=0.3,n=4)
for k in range(3): part('box','Iron',(0.2+k*0.2,0.05,0.9),size=(0.03,0.25,0.015))          # files
done('Bench_Vise',True)
# iron stock rack: a frame with bars and rods leaning in it
part('box','WoodTrim_Dark',(0,0,0),size=(1.2,0.25,0.08)); part('box','WoodTrim_Dark',(0,0.08,1.1),size=(1.2,0.08,0.08))
for x in (-0.55,0.55): part('box','WoodTrim_Dark',(x,0.08,0),size=(0.08,0.08,1.2))
for k in range(9): part('box','Iron_Dark' if k%2 else 'Iron',(-0.45+k*0.11,0.02,0.04),(-0.12,0,0),size=(0.035,0.035,1.7))
done('Stock_Rack',True)
# finished work hung on the wall: a beam of hooks with chain, boat hooks and rings; and a small anchor leaning below
part('box','WoodTrim_Dark',(0,0,1.7),size=(1.6,0.08,0.12))
for k in range(5):
    x=-0.6+k*0.3
    for c in range(4): part('cyl','Iron_Dark',(x,0.0,1.6-c*0.12),(0,math.pi/2*(c%2),0),r=0.05,h=0.02,n=6,caps=False)
part('cyl','Iron_Dark',(0.2,0.12,0),(0.15,0,0),r=0.03,h=1.0,n=5); part('box','Iron_Dark',(0.2,0.12,0.05),size=(0.6,0.05,0.05))
part('box','Iron_Dark',(-0.08,0.12,0.05),(0,0.7,0),size=(0.05,0.05,0.3)); part('box','Iron_Dark',(0.48,0.12,0.05),(0,-0.7,0),size=(0.05,0.05,0.3))
done('Smith_Goods',True)
# the old blade: his father's arming sword on two pegs (hung above a door, beat B)
part('box','WoodTrim_Dark',(-0.3,0,0),size=(0.05,0.1,0.1)); part('box','WoodTrim_Dark',(0.3,0,0),size=(0.05,0.1,0.1))
part('box','Iron_Light',(0.05,-0.04,0.09),size=(0.75,0.02,0.05)); part('box','Iron_Dark',(-0.34,-0.04,0.09),size=(0.04,0.02,0.18))
part('box','Cloth_Dark',(-0.45,-0.04,0.09),size=(0.18,0.03,0.035)); part('sphere','Iron',(-0.56,-0.04,0.09),r=0.035,n=5)
done('Old_Blade',True)
print('done')
