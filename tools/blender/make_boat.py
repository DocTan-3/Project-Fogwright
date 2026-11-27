# The fishing sailboat, remade from the user's reference (a clinker-built open boat with a gaff main and a jib): every
# part of the reference, low-poly, palette materials. Origin at the waterline, bow toward +x (Blender), 6 m long.
#   python3 make_boat.py <out dir>
import bpy,bmesh,math,os,sys
from mathutils import Vector,Matrix
OUT=os.path.abspath(sys.argv[-1]); os.makedirs(OUT,exist_ok=True)
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
M={}
def mat(n):
    if n not in M: M[n]=bpy.data.materials.new(n)
    return M[n]
PARTS=[]
def obj(bm,m):
    me=bpy.data.meshes.new('p'); bm.to_mesh(me); bm.free(); me.materials.append(mat(m))
    o=bpy.data.objects.new('p',me); bpy.context.scene.collection.objects.link(o); PARTS.append(o); return o
def box(m,c,size,rot=(0,0,0)):
    bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1)
    for v in bm.verts: v.co=Vector((v.co.x*size[0],v.co.y*size[1],v.co.z*size[2]))
    R=Matrix.Rotation(rot[2],4,'Z')@Matrix.Rotation(rot[1],4,'Y')@Matrix.Rotation(rot[0],4,'X')
    bmesh.ops.transform(bm,matrix=Matrix.Translation(Vector(c))@R,verts=bm.verts); return obj(bm,m)
def rod(m,a,b,r,n=5):   # a round spar or a line between two points
    a,b=Vector(a),Vector(b); d=b-a; L=d.length
    bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=n,radius1=r,radius2=r*0.85,depth=L)
    q=Vector((0,0,1)).rotation_difference(d.normalized())
    bmesh.ops.transform(bm,matrix=Matrix.Translation((a+b)/2)@q.to_matrix().to_4x4(),verts=bm.verts); return obj(bm,m)
def quads(m,rows):   # a surface from rows of points (each row the same length), both sides drawn
    bm=bmesh.new(); vs=[[bm.verts.new(p) for p in r] for r in rows]
    for i in range(len(rows)-1):
        for j in range(len(rows[0])-1): bm.faces.new((vs[i][j],vs[i][j+1],vs[i+1][j+1],vs[i+1][j]))
    return obj(bm,m)
L,B,D=6.0,1.9,0.78          # length, beam, depth
def half(s):   # half-breadth at the gunwale, s from transom (0) to stem (1)
    return B/2*max(0.0,1-((s-0.38)/0.62)**2)**0.85 if s>0.38 else B/2*(0.68+0.32*math.sin(s/0.38*math.pi/2))   # fining smoothly into the stem
def sheer(s): return 0.32+0.22*(s-0.45)**2*4 if s>0.45 else 0.32+0.06*(0.45-s)*2   # the gunwale's height, rising to the bow
def keel(s): return -0.46+0.28*max(0,(s-0.8)/0.2)**2                               # the keel line, sweeping up into the stem
def section(s,t,off=0.0):   # a point on the hull's side: t=0 at the keel, 1 at the gunwale
    b=half(s)+off; x=b*math.sin(t*math.pi/2)**0.75; z=keel(s)+(sheer(s)-keel(s))*(1-math.cos(t*math.pi/2))**0.9
    return x,z
S=[i/14 for i in range(12)]+[0.84,0.88,0.92,0.95,0.975,1.0]   # closer stations toward the bow, where the hull narrows fast
def X(s): return -L/2+s*L
# hull: five overlapping strakes a side (clinker), each lapping outside the one below; the top one darker
STRAKES=[0.0,0.22,0.42,0.6,0.78,1.0]
for side in (1,-1):
    for k in range(5):
        t0,t1=STRAKES[k],min(1.0,STRAKES[k+1]+0.04)
        rows=[]
        for s in S:
            row=[]
            for t in (t0,(t0+t1)/2,t1):
                y,z=section(s,t,0.012*k); row.append((X(s),side*y,z))
            rows.append(row)
        if side<0: rows=[r[::-1] for r in rows]
        quads('WoodTrim_Dark' if k==4 else 'WoodTrim',rows)
# transom (the flat stern), stem post, keel
tr=[(X(0),section(0,t)[0]*sg,section(0,t)[1]) for sg in (1,-1) for t in ((0,.25,.5,.75,1) if sg>0 else (1,.75,.5,.25,0))]
bm=bmesh.new(); bm.faces.new([bm.verts.new(p) for p in tr]); obj(bm,'WoodTrim_Dark')
rod('WoodTrim_Dark',(X(0.97),0,keel(0.97)),(X(1.0)+0.08,0,sheer(1.0)+0.1),0.06,4)
rod('WoodTrim_Dark',(X(0.0),0,keel(0)-0.03),(X(0.95),0,keel(0.95)-0.03),0.05,4)
# gunwale rail and rubbing strake along both sides
for side in (1,-1):
    for i in range(len(S)-1):
        a,b=S[i],S[i+1]
        for (dz,off,r,m) in ((0.0,0.03,0.035,'WoodTrim_Dark'),(-0.12,0.04,0.025,'WoodTrim_Wear')):
            ya,za=section(a,1.0,off); yb,zb=section(b,1.0,off)
            rod(m,(X(a),side*ya,za+dz),(X(b),side*yb,zb+dz),r,4)
# inside: ribs, three thwarts, the stern seat
for s in (0.15,0.3,0.45,0.6,0.75):
    pts=[section(s,t,-0.03) for t in (0.05,0.5,1.0)]
    for sg in (1,-1):
        rod('WoodTrim_Dark',(X(s),sg*pts[0][0],pts[0][1]),(X(s),sg*pts[1][0],pts[1][1]),0.025,4)
        rod('WoodTrim_Dark',(X(s),sg*pts[1][0],pts[1][1]),(X(s),sg*pts[2][0],pts[2][1]),0.025,4)
for s in (0.36,0.56,0.76):
    box('WoodTrim_Light',(X(s),0,0.12),(0.28,2*half(s)-0.12,0.05))
box('WoodTrim_Light',(X(0.06),0,0.14),(0.55,2*half(0.06)-0.14,0.06)); box('WoodTrim',(X(0.06),0,-0.06),(0.5,2*half(0.06)-0.2,0.36))
# mast with five iron bands, bowsprit, boom and gaff
mx=X(0.66); top=6.0
rod('WoodTrim',(mx,0,-0.4),(mx,0,top),0.075,6)
for z in (1.2,2.2,3.2,4.2,5.2): rod('Iron',(mx,0,z),(mx,0,z+0.07),0.088,6)
bow=(X(1.0)+0.08,0,sheer(1.0)+0.08); sprit=(X(1.0)+1.9,0,sheer(1.0)+0.35)
rod('WoodTrim',bow,sprit,0.05,5); rod('Iron',(X(1.0)+0.3,0,sheer(1.0)+0.12),(X(1.0)+0.38,0,sheer(1.0)+0.14),0.06,5)
boom0=(mx-0.1,0,1.05); boom1=(X(0)-0.55,0.35,0.95)
rod('WoodTrim',boom0,boom1,0.05,5)
gaff0=(mx-0.1,0,4.6); gaff1=(mx-2.6,0.25,5.9)
rod('WoodTrim',gaff0,gaff1,0.04,5)
# sails: the gaff main (four corners: tack, throat, peak, clew) and the jib, a little bellied, with seams
def sail(corners,belly,seams=3,side=0.18,nu=5):
    a,b,c,d=[Vector(p) for p in corners]   # luff bottom, luff top, leech top, leech bottom
    nv=seams+1; rows=[]
    for i in range(nu+1):
        u=i/nu; lo=a.lerp(d,u); hi=b.lerp(c,u); row=[]
        for j in range(nv+1):
            v=j/nv; p=lo.lerp(hi,v); p.y+=belly*math.sin(math.pi*u)*math.sin(math.pi*min(1,v*1.15))*side
            row.append(tuple(p))
        rows.append(row)
    quads('Cloth_Light',rows)
    for j in range(1,nv):   # each seam runs along one line of the sail's own grid, so it lies on the canvas
        for i in range(nu):
            for sg in (1,-1):
                p=Vector(rows[i][j])+Vector((0,0.01*sg,0)); q=Vector(rows[i+1][j])+Vector((0,0.01*sg,0))
                rod('Cloth_Dark',tuple(p),tuple(q),0.01,3)
sail([(mx-0.12,0,1.1),(mx-0.12,0,4.55),gaff1,boom1],1.0,seams=4)
jib_head=(mx+0.05,0,5.4)
sail([sprit,jib_head,jib_head,(mx+0.35,0.3,1.05)],0.8,seams=3)
# lines: forestay, two shrouds a side, bobstay, halyard, mainsheet
rod('Rope',(mx,0,top-0.15),sprit,0.012,3)
for sg in (1,-1):
    for ds in (-0.04,0.06):
        y,z=section(0.66+ds,1.0,0.04); rod('Rope',(mx,0,top-0.35),(X(0.66+ds),sg*y,z),0.012,3)
rod('Rope',sprit,(X(0.99),0,keel(0.99)+0.05),0.012,3)
rod('Rope',(mx+0.09,0,top-0.1),(mx+0.09,0,1.0),0.01,3)
rod('Rope',boom1,(X(0.02),0.2,sheer(0.02)),0.012,3)
# rudder and tiller
rod('WoodTrim_Dark',(X(0)-0.06,0,0.42),(X(0)-0.12,0,-0.42),0.03,4); box('WoodTrim_Dark',(X(0)-0.22,0,-0.15),(0.26,0.05,0.62))
rod('WoodTrim',(X(0)-0.05,0,0.45),(X(0.13),0,0.5),0.03,4)
# oars: one resting out over the side, one in the boat
def oar(a,b):
    a,b=Vector(a),Vector(b); rod('WoodTrim_Light',tuple(a),tuple(b),0.025,5); d=(b-a).normalized()
    box('WoodTrim_Light',tuple(b+d*0.35),(0.7,0.04,0.16),(0,-math.asin(d.z),math.atan2(d.y,d.x)))
oar((X(0.5),-0.3,0.45),(X(0.62),-B/2-1.4,-0.05))
oar((X(0.3),0.3,0.2),(X(0.8),0.35,0.22))
# cargo: a chest amidships, a sack at the bow, a coil of rope, the plaid blanket over the stern quarter
box('WoodTrim_Dark',(X(0.47),0.15,0.05),(0.55,0.42,0.35)); box('Iron',(X(0.47),0.15,0.23),(0.57,0.44,0.03))
bm=bmesh.new(); bmesh.ops.create_uvsphere(bm,u_segments=7,v_segments=4,radius=0.28)
for v in bm.verts: v.co=Vector((v.co.x*1.1,v.co.y,v.co.z*0.7+0.0))
bmesh.ops.transform(bm,matrix=Matrix.Translation(Vector((X(0.86),0.0,0.0))),verts=bm.verts); obj(bm,'Cloth_Light')
bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=8,radius1=0.22,radius2=0.18,depth=0.1)
bmesh.ops.transform(bm,matrix=Matrix.Translation(Vector((X(0.4),-0.35,-0.05))),verts=bm.verts); obj(bm,'Rope')
y,z=section(0.12,1.0,0.05); box('Fish_Dark',(X(0.12),0.0,z-0.02),(0.5,2*y+0.06,0.03)); box('Fish_Dark',(X(0.12),y+0.04,z-0.2),(0.5,0.03,0.4))   # the plaid blanket, blue-grey
# the lifebuoy on the hull side: a ring in red and white quarters
y,z=section(0.25,0.75,0.06)
for k in range(8):
    a0,a1=k*math.pi/4,(k+1)*math.pi/4; r=0.2
    rod('RedBrick' if k%2==0 else 'Cloth_Light',(X(0.25)+r*math.cos(a0),y+0.03,z+r*math.sin(a0)),(X(0.25)+r*math.cos(a1),y+0.03,z+r*math.sin(a1)),0.045,5)
# one object, uv'd, exported
bpy.ops.object.select_all(action='DESELECT')
for o in PARTS: o.select_set(True)
bpy.context.view_layer.objects.active=PARTS[0]; bpy.ops.object.join(); o=bpy.context.view_layer.objects.active; o.name='Sailboat'
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT'); bpy.ops.mesh.normals_make_consistent(inside=False); bpy.ops.uv.cube_project(cube_size=1.0); bpy.ops.object.mode_set(mode='OBJECT')
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT,'Sailboat.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
print('Sailboat %d tris %s'%(sum(len(p.vertices)-2 for p in o.data.polygons),tuple(round(v,2) for v in o.dimensions)))
