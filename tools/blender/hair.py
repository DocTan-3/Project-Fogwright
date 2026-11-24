# Low-poly hair for the Fogwright bodies, built in Blender:  python3 hair.py <body.gltf> <out.json>
# Each style is a scalp cap plus a few locks, a few hundred triangles, textured from creator/tex/hair.png (cap strands on the
# left half, four lock shapes on the right) and cut out by its alpha, the way low-poly games do hair.
#  - The cap is a dome laid onto the head and cut at a real hairline (forehead, temples, sideburns, over the ears, nape). Its
#    pole sits where the hair grows from or gathers (the crown, the forehead for swept hair, the tie of a ponytail, a topknot's
#    bun), so the strands in the texture always run the right way; each meridian's last row ends in the texture's jagged tips.
#  - Locks are strips with a raised middle, laid along paths that follow the head and fall under gravity onto the shoulders.
#  - Shading normals point away from the head, so cards light like volume. Skin: the head, blending to the chest below the
#    neck. Every point carries the body's shapes (the peoples, Lean, Heavy) from the body points nearest it.
import bpy,sys,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
body_path,out_path=sys.argv[1:3]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=body_path)
body=bpy.data.objects['Body']; arm=body.parent; me=body.data
arm.data.pose_position='REST'   # the importer leaves the first animation frame posed; measure the body at rest, as the game binds it
bpy.context.view_layer.update()
for o in list(bpy.data.objects):
    if o.type=='MESH' and o!=body: bpy.data.objects.remove(o)
# template ('rest') place of every body point, from its colour; actual places from the mesh
ca=me.color_attributes[0]; REST=[None]*len(me.vertices)
for l in me.loops:
    c=ca.data[l.index].color if ca.domain=='CORNER' else ca.data[l.vertex_index].color
    REST[l.vertex_index]=Vector((c[0]-0.5,c[1]-0.5,c[2]*2))
P=[v.co.copy() for v in me.vertices]
kd=KDTree(len(P))
for i,p in enumerate(P): kd.insert(p,i)
kd.balance()
dg=bpy.context.evaluated_depsgraph_get(); bvh=BVHTree.FromObject(body,dg)
def tz_coarse(p): return REST[kd.find(p)[1]].z
def zof(rz):   # a template height on this body (widening the search until body points are found)
    for tol in (0.01,0.02,0.04):
        pts=[P[i].z for i in range(len(P)) if abs(REST[i].z-rz)<tol and abs(P[i].x)<0.15]
        if pts: return sum(pts)/len(pts)
    raise ValueError(rz)
head=[P[i] for i in range(len(P)) if REST[i].z>1.62 and abs(P[i].x)<0.1]
eyeZ=zof(1.69); C=Vector((0,(min(p.y for p in head)+max(p.y for p in head))/2,eyeZ+0.02))
# a smooth template height: the stored one comes from 8-bit colours, in steps of about 1.6 cm, which would cut the hairline
# along those steps (a dead straight edge); height above the eyes, scaled to the template, is smooth
TOPZ=max(p.z for p in head); TS=(1.81-1.69)/(TOPZ-eyeZ)
def tz(p): return 1.69+(p.z-eyeZ)*TS
NECK=zof(1.60); SHOULDER=zof(1.46)
sm=lambda a,b,x:(lambda t:t*t*(3-2*t))(min(1,max(0,(x-a)/(b-a))))
def phi_of(p): return math.atan2(p.x,-(p.y-C.y))              # 0 = the face, +x (the figure's left) positive
HAIRLINE=[(0, 1.756), (0.3, 1.76), (0.65, 1.77), (0.95, 1.758), (1.15, 1.735), (1.3, 1.672), (1.42, 1.69), (1.6, 1.697), (1.85, 1.697), (2.05, 1.682), (2.25, 1.662), (2.6, 1.628), (3.1416, 1.622)]   # (angle from the face, template height); the notch just clears the top of the ear (~1.688); bodypaint.js cardline() is written from the same points
def hairline(phi):
    a=min(abs(phi),math.pi)
    for (a0,z0),(a1,z1) in zip(HAIRLINE,HAIRLINE[1:]):
        if a<=a1: return z0+(z1-z0)*(a-a0)/(a1-a0)
    return HAIRLINE[-1][1]
def onhead(d,off):   # the head's surface toward direction d from the centre, pushed out by off
    hit=bvh.ray_cast(C+d*0.4,-d,0.5)
    if hit[0] is None: return None,None
    return hit[0]+hit[1]*off,hit[1]
def frame(pole):
    pole=pole.normalized(); a=Vector((1,0,0)) if abs(pole.x)<0.9 else Vector((0,1,0))
    A=(a-pole*a.dot(pole)).normalized(); B=pole.cross(A); return pole,A,B

class Mesh:
    def __init__(s): s.P=[];s.N=[];s.UV=[];s.I=[]
    def v(s,p,n,uv): s.P.append(p.copy());s.N.append(n.normalized());s.UV.append(uv);return len(s.P)-1
    def quad(s,a,b,c,d): s.I+= [a,b,c,a,c,d]
    def tri(s,a,b,c): s.I+=[a,b,c]

def cap(M,pole,tmax,thick,margin=0.0,M_=18,N_=12,tipLen=0.006,edge='roots'):
    U0=0.0 if edge=='tips' else 0.25   # which quarter of the sheet: an edge of tips (crop, fringe) or of roots (pulled back)
    """A dome from the pole down each of M_ meridians to the hairline. Each meridian ends exactly where it crosses the
    hairline (found by bisection), plus a short run of jagged tips past it; meridians of different lengths are stitched."""
    pole,A,B=frame(pole)
    def at(th,ph):
        d=(pole*math.cos(th)+(A*math.cos(ph)+B*math.sin(ph))*math.sin(th)).normalized(); p,n=onhead(d,0.0)
        return p,n
    def hair_at(th,ph):
        p,_=at(th,ph); return p is not None and tz(p)>=hairline(phi_of(p))-margin
    def place(p,n):   # full thickness inside the hair, thinning to a skin-close edge at the hairline
        k=sm(0.0,0.03,tz(p)-hairline(phi_of(p))); p2=p+n*(0.003+(thick(p)-0.003)*k); return p2,((p2-C).normalized()*0.5+n*0.5)
    pp,pn=at(0,0); pole_id=M.v(*place(pp,pn),(U0+0.125,0.0))
    cols=[]
    for m in range(M_+1):
        ph=2*math.pi*(m%M_)/M_
        k=1
        while k<=N_ and hair_at(tmax*k/N_,ph): k+=1
        lo,hi=tmax*(k-1)/N_,tmax*min(k,N_)/N_     # the crossing lies between these
        for _ in range(12):
            mid=(lo+hi)/2
            if hair_at(mid,ph): lo=mid
            else: hi=mid
        # arc length along the meridian, to the hairline, then the tips beyond it
        ths=[tmax*j/N_ for j in range(1,k)]+[lo]
        pts=[at(t,ph) for t in ths]; pts=[(p,n) for p,n in pts if p is not None]
        if not pts: cols.append([]); continue
        L=[0.0]; prev=pp
        for p,_ in pts: L.append(L[-1]+(p-prev).length); prev=p
        tot=L[-1]; p_last,n_last=pts[-1]; fwd=(p_last-pts[-2][0]).normalized() if len(pts)>1 else (p_last-pp).normalized()
        tip=(p_last+fwd*tipLen,n_last)
        col=[]
        for (p,n),s_ in zip(pts,L[1:]):
            v=0.82*s_/max(tot,1e-4); col.append((M.v(*place(p,n),(U0+0.25*m/M_,v)),s_/(tot+tipLen)))
        col[-1]=(col[-1][0],tot/(tot+tipLen)); M.UV[col[-1][0]]=(U0+0.25*m/M_,0.84)
        col.append((M.v(*place(*tip),(U0+0.25*m/M_,1.0)),1.0))
        cols.append(col)
    for m in range(M_):
        a_,b_=cols[m],cols[m+1]
        if not a_ or not b_: continue
        M.tri(pole_id,a_[0][0],b_[0][0])
        i=j=0
        while i<len(a_)-1 or j<len(b_)-1:   # stitch the two meridians, advancing whichever is behind
            if j>=len(b_)-1 or (i<len(a_)-1 and a_[i+1][1]<=b_[j+1][1]): M.tri(a_[i][0],a_[i+1][0],b_[j][0]); i+=1
            else: M.tri(a_[i][0],b_[j+1][0],b_[j][0]); j+=1

def lock(M,phi,el,length,width,variant,desired,g=1.0,off=0.012,rows=5,bulge=0.3,taper=0.45,twist=0.0,start=None,hug=True,radial=None):
    if start: p,n=start
    else:
        d=Vector((math.sin(phi)*math.cos(el),-math.cos(phi)*math.cos(el),math.sin(el)))
        p,n=onhead(d,off)
    if p is None: return
    path=[p]; dr=Vector(desired).normalized(); dr=(dr-n*dr.dot(n)).normalized()
    steps=max(4,int(length/0.012)); st=length/steps
    for i in range(steps):
        dr=(dr+Vector((0,0,-1))*g*0.2).normalized(); q=path[-1]+dr*st
        loc,nn,_,dist=bvh.find_nearest(q)
        if loc is not None:
            o=off if q.z>NECK else off+0.008
            h=(q-loc).dot(nn)
            if h<o or (hug and q.z>eyeZ-0.04 and h>o):   # on the head the lock lies on the scalp; below, it only stays clear
                q=loc+nn*o
                if h<o: dr=(dr-nn*dr.dot(nn)).normalized()   # and where it meets the body it slides along it, as hair does
        if q.z>eyeZ-0.04: dr=(q-path[-1]).normalized()
        path.append(q)
    # resample to rows
    L=[0]
    for a,b in zip(path,path[1:]): L.append(L[-1]+(b-a).length)
    pts=[]
    for r in range(rows):
        t=L[-1]*r/(rows-1); j=max(1,min(len(L)-1,next((i for i in range(1,len(L)) if L[i]>=t),len(L)-1)))
        f=(t-L[j-1])/max(1e-6,L[j]-L[j-1]); pts.append(path[j-1].lerp(path[j],f))
    ids=[]
    u0=0.5+0.125*variant
    for r,q in enumerate(pts):
        t=r/(rows-1); fw=(pts[min(r+1,rows-1)]-pts[max(r-1,0)]).normalized()
        out=(q-C); loc,nn,_,_=bvh.find_nearest(q); out=(out.normalized()*0.5+nn*0.5).normalized()
        if radial is not None: out=(radial-fw*radial.dot(fw)).normalized()   # a bundle's locks face out from its axis
        side=fw.cross(out).normalized(); w=width*(1-taper*t)*0.5
        side=(side*math.cos(twist*t)+out*math.sin(twist*t)).normalized()
        row=[M.v(q-side*w,out-side*0.4,(u0+0.003,t)),M.v(q+out*w*bulge,out,(u0+0.0625,t)),M.v(q+side*w,out+side*0.4,(u0+0.122,t))]
        ids.append(row)
    for r in range(rows-1):
        for c in range(2): M.quad(ids[r][c],ids[r+1][c],ids[r+1][c+1],ids[r][c+1])

def ring(M,centre,axis,radius,height,segs=8,v0=0.02):   # a hair tie or bun band, dark from the texture's groove
    ax,A,B=frame(axis); ids=[]
    for m in range(segs+1):
        ph=2*math.pi*m/segs; dvec=A*math.cos(ph)+B*math.sin(ph)
        ids.append((M.v(centre+dvec*radius-ax*height/2,dvec,(0.0+0.02*m/segs,v0)),M.v(centre+dvec*radius+ax*height/2,dvec,(0.0+0.02*m/segs,v0+0.02))))
    for m in range(segs): M.quad(ids[m][0],ids[m+1][0],ids[m+1][1],ids[m][1])

def bun(M,centre,r,squash=0.8,segs=8,rings=5):
    ids=[]
    for k in range(rings+1):
        th=math.pi*k/rings; row=[]
        for m in range(segs+1):
            ph=2*math.pi*m/segs; d=Vector((math.sin(th)*math.cos(ph),math.sin(th)*math.sin(ph),math.cos(th)*squash))
            row.append(M.v(centre+d*r,d,(0.5*m/segs,0.75*k/rings)))
        ids.append(row)
    for k in range(rings):
        for m in range(segs): M.quad(ids[k][m],ids[k+1][m],ids[k+1][m+1],ids[k][m+1])

def dirn(phi,el): return Vector((math.sin(phi)*math.cos(el),-math.cos(phi)*math.cos(el),math.sin(el)))
STYLES={}
# --- Short: a close crop
M=Mesh(); cap(M,dirn(math.pi,1.2),2.9,lambda p:0.004+0.005*sm(1.74,1.80,tz(p)),margin=0.002,edge='tips')
STYLES['Short']=M
# --- Swept: swept back from the forehead with volume on top, lying on the scalp
M=Mesh(); cap(M,dirn(0.0,0.36),2.9,lambda p:0.006+0.01*sm(1.75,1.81,tz(p)),margin=0.002)
for i,f in enumerate((-0.55,-0.3,-0.08,0.15,0.38,0.6)): lock(M,f,0.62,0.16,0.065,i%4,(0,1,0.6),g=0.0,off=0.016,rows=5,bulge=0.35,taper=0.3)
for i,f in enumerate((1.0,1.25,-1.0,-1.25)): lock(M,f,0.5,0.1,0.05,(i+1)%4,(0,1,0.2),g=0.0,off=0.011,rows=4,bulge=0.25,taper=0.3)
STYLES['Swept']=M
# --- Long: parted at the crown, framing the face, falling past the shoulders
M=Mesh(); cap(M,dirn(math.pi,1.45),2.9,lambda p:0.006+0.006*sm(1.74,1.80,tz(p)),margin=0.002)
for i in range(11):
    f=1.2+(math.pi-1.2)*i/10
    for sgn in (1,-1):
        if sgn<0 and i==10: continue
        lock(M,f*sgn,0.95-0.2*(i/10),0.42+0.03*((i*7)%3),0.08,(i+(sgn>0))%4,(0.0,0.1*(i/10),-1),g=1.0,off=0.013,rows=6,bulge=0.3,taper=0.35)
for sgn in (1,-1): lock(M,1.0*sgn,1.05,0.34,0.065,2,(0.25*sgn,0.15,-1),g=1.0,off=0.016,rows=5,bulge=0.3,taper=0.4)   # the front locks, just behind the temples
STYLES['Long']=M
# --- Ponytail: pulled back to a tie at the back of the head; the tail is a bundle of locks hanging from it
M=Mesh(); tieDir=dirn(math.pi,0.45); cap(M,tieDir,2.9,lambda p:0.005+0.003*sm(1.74,1.80,tz(p)),margin=0.002)
tie,tn=onhead(tieDir,0.02)
ax=Vector((0,0.35,-1)).normalized(); U_=ax.cross(Vector((1,0,0))).normalized(); V_=ax.cross(U_).normalized()
for i in range(5):
    a_=2*math.pi*i/5+0.3; rad=U_*math.cos(a_)+V_*math.sin(a_)
    lock(M,0,0,0.27,0.045,i%4,(0,0.35,-1),g=1.0,off=0.012,rows=5,bulge=0.3,taper=0.45,start=(tie+rad*0.014,tn),hug=False,radial=rad)
ring(M,tie,tn,0.018,0.016)
STYLES['Ponytail']=M
# --- Topknot: pulled up to a bun on the crown
M=Mesh(); top=dirn(math.pi,1.35); cap(M,top,2.9,lambda p:0.005+0.003*sm(1.74,1.80,tz(p)),margin=0.002)
kn,knn=onhead(top,0.0)
bun(M,kn+knn*0.04,0.042,0.85); ring(M,kn+knn*0.008,knn,0.024,0.014)
STYLES['Topknot']=M

# --- skin, shapes, rest, and out (glTF axes: x, z, -y)
keys=[k for k in (me.shape_keys.key_blocks if me.shape_keys else []) if k.name!='Basis']
out={}
for name,M in STYLES.items():
    o={'pos':[],'nrm':[],'uv':[],'rest':[],'idx':M.I,'bones':['head','neck','chest'],'skin':[],'morph':{k.name:[] for k in keys}}
    for p,n,uv in zip(M.P,M.N,M.UV):
        o['pos']+=[round(p.x,4),round(p.z,4),round(-p.y,4)]; o['nrm']+=[round(n.x,3),round(n.z,3),round(-n.y,3)]; o['uv']+=[round(uv[0],4),round(1-uv[1],4)]
        near=kd.find_n(p,4); ws=[(i,1/(d+0.005)) for _,i,d in near]; s=sum(w for _,w in ws)
        r=sum((REST[i]+(p-P[i]) for i,_ in ws),Vector())*0 
        r=Vector(); 
        for i,w in ws: r+=(REST[i]+(p-P[i]))*(w/s)
        o['rest']+=[round(r.x,4),round(r.y,4),round(r.z,4)]
        a=sm(NECK,SHOULDER,p.z) if p.z<NECK else 0.0
        b=sm(NECK+0.03,NECK-0.02,p.z)*0.3*(1-a)
        o['skin'].append([round(1-a-b,3),round(b,3),round(a,3)])
        for k in keys:
            d=Vector()
            for i,w in ws: d+=(k.data[i].co-P[i])*(w/s)
            o['morph'][k.name]+=[round(d.x,4),round(d.z,4),round(-d.y,4)]
    out[name]=o
    print(name,len(M.P),'points',len(M.I)//3,'triangles')
json.dump(out,open(out_path,'w'),separators=(',',':'))
