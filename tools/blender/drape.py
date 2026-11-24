# Drape a garment on a Fogwright body with Blender's cloth simulation, once, offline; freeze it and write it out for the game.
#   python3 drape.py <body.gltf> <garment> <out.json> [preview.png]
# The garment starts as a loose cone round the body, its top edge pinned under the belt; gravity drapes it over the hips,
# buttocks and legs, so the folds and the fit come from cloth, not from code. The result is skinned the WoW way (hips at the
# top, blending to each thigh lower down, the front and back panels most), carries the body's shapes in the game, and gets a
# cavity shade so its folds read in flat light.
import bpy,bmesh,sys,json,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree

GARMENTS={
  # top/hem: heights of the waist edge and the hem (body rest space, metres); slit: the front opening (radians, total);
  # flare: extra width at the hem before it falls; stiff: bending stiffness (leather is stiffer than wool); seg: points round
  'longcoat':  dict(top=1.012,hem=0.47,slit=0.16,flare=0.045,stiff=3.0,mass=0.4,seg=40,rows=18,yoke=0.07),
  'greatcoat': dict(top=1.012,hem=0.16,slit=0.10,flare=0.025,stiff=2.5,mass=0.45,seg=44,rows=30,yoke=0.07),
  'ilvaricoat':dict(top=1.0,hem=0.40,slit=0.12,flare=0.08,stiff=3.0,mass=0.30,seg=56,rows=30),
  'robe':      dict(top=1.0,hem=0.12,slit=0.0, flare=0.12,stiff=2.0,mass=0.30,seg=60,rows=40),
}
argv=sys.argv[1:]; body_path,gname,out_path=argv[:3]; preview=argv[3] if len(argv)>3 else None; G=dict(GARMENTS[gname])

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=body_path)
body=bpy.data.objects['Body']; arm=body.parent
arm.data.pose_position='REST'   # the importer leaves the first animation frame posed; measure the body at rest, as the game binds it
bpy.context.view_layer.update()
for o in list(bpy.data.objects):
    if o.type=='MESH' and o!=body: bpy.data.objects.remove(o)
# the collider: the body at rest without its arms (the coat must not rest on them; they swing away)
dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(body.evaluated_get(dg))
gi={g.index:g.name for g in body.vertex_groups}
def armw(v): return sum(g.weight for g in body.data.vertices[v.index].groups if any(k in gi[g.group] for k in ('arm','hand','forearm')))
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm,geom=[v for v in bm.verts if armw(v)>0.4],context='VERTS'); bm.to_mesh(me); bm.free()
# below the knee the legs wear boots (built shells up to ~2 cm thick, flared at the top): the cloth hangs clear of them
KNEE=(arm.matrix_world@arm.data.bones['shin.L'].head_local).z
for v in me.vertices:
    if v.co.z<KNEE+0.06: v.co+=v.normal*0.022*min(1,(KNEE+0.06-v.co.z)/0.08)
col=bpy.data.objects.new('Collider',me); bpy.context.scene.collection.objects.link(col)
col.modifiers.new('c','COLLISION'); col.collision.thickness_outer=0.008; col.collision.cloth_friction=8
P=[v.co.copy() for v in me.vertices]
# heights are given in the template ('rest') space the game paints and places belts in, which is not each body's own scale
# (the female body is drawn about 5% shorter): read each body point's template place from its colour and convert
ca_=body.data.color_attributes[0]; src=body.data
if ca_.domain=='POINT': RZ=[ca_.data[i].color[2]*2 for i in range(len(src.vertices))]
else:
    RZ=[0]*len(src.vertices)
    for l in src.loops: RZ[l.vertex_index]=ca_.data[l.index].color[2]*2
def zof(rz):   # a template height on this body
    pts=[(RZ[v.index],v.co.z) for v in src.vertices if abs(RZ[v.index]-rz)<0.012 and abs(v.co.x)<0.2]
    return sum(z for _,z in pts)/len(pts)
G['top'],G['hem']=zof(G['top']),zof(G['hem']); G['yoke']=G.get('yoke',0)*(G['top']-G['hem'])/0.542
print('heights on this body: top',round(G['top'],3),'hem',round(G['hem'],3))

# the waist: centre and radius in each direction, and the body's reach at each height below it
band=lambda z,w:[p for p in P if abs(p.z-z)<w]
ring=band(G['top'],0.012); cx=sum(p.x for p in ring)/len(ring); cy=sum(p.y for p in ring)/len(ring)
def reach(th,z,w=0.03,cone=0.35):   # how far the body reaches from the centre toward angle th (th 0 = front, -y; +x = left)
    r=0
    for p in band(z,w):
        x,y=p.x-cx,-(p.y-cy); a=math.atan2(x,y)-th; a=math.atan2(math.sin(a),math.cos(a))
        if abs(a)<cone: r=max(r,math.hypot(x,y)*math.cos(a))
    return r
S,R=G['seg'],G['rows']; slit=G['slit']
TH=[slit/2+(2*math.pi-slit)*i/(S-1) for i in range(S)] if slit else [2*math.pi*i/S for i in range(S)]
bm=bmesh.new(); grid=[]; prev=None; PIN=list(range(S))
for k in range(R+1):
    t=(k/R)**1.35; z=G['top']-(G['top']-G['hem'])*t   # rows closer together near the waist, where the body curves most
    dz=(G['top']-G['hem'])*((k/R)**1.35-((k-1)/R)**1.35 if k else 0.01); yk=G['top']-z<G.get('yoke',0)   # the yoke: fitted to the hips and held there; the cloth falls free below it
    rr=[ (reach(th,z,0.012,0.12)+0.002) if k==0 else (reach(th,z-0.5*dz,dz*1.1,0.25)+0.007) if yk else max(reach(th,z)+0.01+G['flare']*max(0,(G['top']-G.get('yoke',0)-z)/(G['top']-G.get('yoke',0)-G['hem'])), prev[i]) for i,th in enumerate(TH)]
    for _ in range(6):   # smooth round the body (never inward): the measured reach is spiky from point to point
        n_=len(rr); rr=[max(v,(rr[(i-1)%n_ if not slit else max(0,i-1)]+2*v+rr[(i+1)%n_ if not slit else min(n_-1,i+1)])/4) for i,v in enumerate(rr)]
    if yk: PIN.extend(range(k*S,(k+1)*S))
    prev=rr; grid.append([bm.verts.new((cx+math.sin(th)*r, cy-math.cos(th)*r, z)) for th,r in zip(TH,rr)])
for k in range(R):
    for i in range(S if not slit else S-1):
        j=(i+1)%S; bm.faces.new((grid[k][i],grid[k+1][i],grid[k+1][j],grid[k][j]))   # wound so the faces look outward
# the yoke lies a fixed distance off the body: each of its points goes to the nearest point of the body's surface plus 12 mm
# along its normal, then the rings are smoothed round and set off the body again, so nothing starts inside it
tree0=BVHTree.FromObject(col,bpy.context.evaluated_depsgraph_get())
yrows=[k for k in range(R+1) if all(v.index in set(PIN) for v in grid[k][:1])] if False else sorted(set(i//S for i in PIN))
for it in range(4):
    for k in yrows:
        row=grid[k]; new=[]
        for i,v in enumerate(row):
            loc,n,_,_=tree0.find_nearest(v.co); p=loc+n*(0.002+min(k,4)*0.0012)
            new.append(Vector((p.x,p.y,row[i].co.z)))
        for i,v in enumerate(row):
            a=new[i-1] if (i>0 or not slit) else new[i]; c=new[(i+1)%len(row)] if (i<len(row)-1 or not slit) else new[i]
            v.co=(a+new[i]*2+c)/4 if it<3 else new[i]
gm=bpy.data.meshes.new(gname); bm.to_mesh(gm); bm.free()
gar=bpy.data.objects.new(gname,gm); bpy.context.scene.collection.objects.link(gar)
pin=gar.vertex_groups.new(name='pin'); pin.add(sorted(set(PIN)),1.0,'REPLACE')
cl=gar.modifiers.new('cloth','CLOTH'); s=cl.settings
s.quality=10; s.mass=G['mass']; s.tension_stiffness=30; s.compression_stiffness=3; s.shear_stiffness=4; s.bending_stiffness=G['stiff']
s.air_damping=2; s.vertex_group_mass='pin'; s.pin_stiffness=1
cs=cl.collision_settings; cs.distance_min=0.006; cs.use_self_collision=True; cs.self_distance_min=0.004; cs.collision_quality=4
sc=bpy.context.scene; sc.frame_start=1; sc.frame_end=120; cl.point_cache.frame_end=120
for f in range(1,121): sc.frame_set(f)
dg=bpy.context.evaluated_depsgraph_get(); dm=bpy.data.meshes.new_from_object(gar.evaluated_get(dg))
gar.modifiers.clear(); gar.data=dm

# nothing may sit inside the body (or closer than a few millimetres): push such points out along the body's surface normal
tree=BVHTree.FromObject(col,bpy.context.evaluated_depsgraph_get())
for v in dm.vertices:
    loc,n,_,d=tree.find_nearest(v.co)
    if loc is None: continue
    out=(v.co-loc).dot(n)
    if out<0.01: v.co=loc+n*0.01
# the waist edge goes back exactly to its ring (the sim can let it sag a millimetre)
for i in range(S): dm.vertices[i].co.z=G['top']
PINSET=set(PIN)

# shade: a cavity term from Blender's dirt bake, so folds read
bpy.context.view_layer.objects.active=gar; gar.select_set(True)
ca=dm.color_attributes.new('shade','FLOAT_COLOR','POINT'); dm.color_attributes.active_color=ca
bpy.ops.object.mode_set(mode='VERTEX_PAINT'); bpy.ops.paint.vertex_color_dirt(blur_strength=1,blur_iterations=2,clean_angle=3.14,dirt_angle=0,dirt_only=False); bpy.ops.object.mode_set(mode='OBJECT')
shade=[ca.data[i].color[0] for i in range(len(dm.vertices))]
lo,hi=min(shade),max(shade); shade=[0.72+0.28*(c-lo)/max(1e-6,hi-lo) for c in shade]

# skin, the WoW way: the waist follows the hips; lower down it blends to the thighs, the front and back panels most
sm=lambda a,b,x:(lambda u:u*u*(3-2*u))(min(1,max(0,(x-a)/(b-a))))
out={'name':gname,'top':GARMENTS[gname]['top'],'hem':GARMENTS[gname]['hem'],'topY':round(G['top'],4),'hemY':round(G['hem'],4),'pos':[],'nrm':[],'shade':[],'skin':[],'idx':[],'rows':R+1,'cols':S,'closed':not slit}
dm.calc_loop_triangles()
vn=[Vector() for _ in dm.vertices]
for p in dm.polygons:
    for i in p.vertices: vn[i]+=p.normal*p.area
for i,v in enumerate(dm.vertices):
    x,y,z=v.co; t=min(1,max(0,(G['top']-z)/(G['top']-G['hem']))); th=math.atan2(x-cx,-(y-cy))
    legW=sm(0,0.22,t)*(0.45+0.55*abs(math.cos(th))); side=sm(-0.5,0.5,math.sin(th))
    sh=legW*0.9*sm(-0.04,0.12,KNEE-z)   # below the knee part of each leg's share goes to its shin, so a long hem gets out of the boot's way
    n=vn[i].normalized()
    out['pos']+= [round(x,4),round(z,4),round(-y,4)]; out['nrm']+=[round(n.x,3),round(n.z,3),round(-n.y,3)]
    out['shade'].append(round(shade[i],2)); out['skin'].append([round(1-legW,2),round((legW-sh)*side,2),round((legW-sh)*(1-side),2),round(sh*side,2),round(sh*(1-side),2)])
for tr in dm.loop_triangles: out['idx']+=list(tr.vertices)
out['bones']=['hips','thigh.L','thigh.R','shin.L','shin.R']
json.dump(out,open(out_path,'w'),separators=(',',':'))
print('wrote',out_path,len(dm.vertices),'points',len(dm.loop_triangles),'triangles')

if preview:   # a quick Cycles look: front, side, back
    for o in list(bpy.data.objects):
        if o.name=='Collider': o.hide_render=True
    mat=bpy.data.materials.new('m'); mat.use_nodes=True; mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.25,0.16,0.1,1)
    gar.data.materials.append(mat)
    bm_=bpy.data.materials.new('b'); bm_.use_nodes=True; bm_.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.6,0.5,0.45,1)
    body.data.materials.clear(); body.data.materials.append(bm_)
    for p in gar.data.polygons: p.use_smooth=True
    sc.render.engine='CYCLES'; sc.cycles.samples=16; sc.cycles.device='CPU'; sc.render.resolution_x=360; sc.render.resolution_y=560
    w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; w.node_tree.nodes['Background'].inputs[1].default_value=1.0
    sun=bpy.data.objects.new('sun',bpy.data.lights.new('sun','SUN')); sc.collection.objects.link(sun); sun.rotation_euler=(0.7,0.1,-0.5); sun.data.energy=3
    cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam; cam.data.lens=50
    import os
    for k,a in enumerate((0,math.pi/2,math.pi)):
        d=Vector((math.sin(a),-math.cos(a),0)); cam.location=Vector((0,0,0.85))+d*3.2; cam.rotation_euler=(math.pi/2,0,a)
        sc.render.filepath=preview.replace('.png',f'_{k}.png'); bpy.ops.render.render(write_still=True)
