# Shoes and boots for the Fogwright bodies, built in Blender:  python3 shoes.py <body.gltf> <out.json>
# A shoe is a last measured from the body's own foot: the foot below the ankle is wrapped (its convex hull, which merges the
# toes into a toe box), padded out, rebuilt as an even mesh (voxel remesh, smoothed) and reduced to low poly. A boot adds a
# shaft wrapped round the lower leg up to its top, joined to the shoe. The top is left open round the leg; the sole gets a
# welt and a heel block; the collar or cuff a trim. In the game the body's foot (and, in a boot, the shin) inside is removed.
import bpy,bmesh,sys,json,math
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree
body_path,out_path=sys.argv[1:3]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=body_path)
body=bpy.data.objects['Body']; arm=body.parent; arm.data.pose_position='REST'; bpy.context.view_layer.update()
me=body.data
for o in list(bpy.data.objects):
    if o.type=='MESH' and o!=body: bpy.data.objects.remove(o)
ca=me.color_attributes[0]; REST=[None]*len(me.vertices)
for l in me.loops:
    c=ca.data[l.index].color; REST[l.vertex_index]=Vector((c[0]-0.5,c[1]-0.5,c[2]*2))
gi={g.index:g.name for g in body.vertex_groups}
W=[{gi[g.group]:g.weight for g in v.groups} for v in me.vertices]
P=[v.co.copy() for v in me.vertices]
BVH=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
kd=KDTree(len(P))
for i,p in enumerate(P): kd.insert(p,i)
kd.balance()
sm=lambda a,b,x:(lambda t:t*t*(3-2*t))(min(1,max(0,(x-a)/(b-a))))
def zof(rz,side):   # a template height on this body's leg
    for tol in (0.01,0.02,0.04):
        pts=[P[i].z for i in range(len(P)) if abs(REST[i].z-rz)<tol and P[i].x*side>0.03 and W[i].get('shin.'+('L' if side>0 else 'R'),0)+W[i].get('foot.'+('L' if side>0 else 'R'),0)>0.5]
        if pts: return sum(pts)/len(pts)
    raise ValueError(rz)

def hull2d(pts):   # monotone chain
    pts=sorted(set((round(x,5),round(y,5)) for x,y in pts))
    if len(pts)<3: return pts
    def half(ps):
        h=[]
        for p in ps:
            while len(h)>=2 and (h[-1][0]-h[-2][0])*(p[1]-h[-2][1])-(h[-1][1]-h[-2][1])*(p[0]-h[-2][0])<=0: h.pop()
            h.append(p)
        return h
    lo=half(pts); hi=half(pts[::-1]); return lo[:-1]+hi[:-1]
def ring_of(pts2,K,pad,flat=None):
    """K points round a 2-D convex outline, at even angles from its centre, padded outward; flat: a floor the ring may
    not go below (the ground)"""
    h=hull2d(pts2); cx=sum(p[0] for p in h)/len(h); cy=sum(p[1] for p in h)/len(h); out=[]
    for k in range(K):
        a=2*math.pi*k/K; d=(math.cos(a),math.sin(a)); best=0
        for (x0,y0),(x1,y1) in zip(h,h[1:]+h[:1]):   # where the ray from the centre leaves the outline
            ex,ey=x1-x0,y1-y0; den=d[0]*ey-d[1]*ex
            if abs(den)<1e-9: continue
            t=((x0-cx)*ey-(y0-cy)*ex)/den; u=((x0-cx)*d[1]-(y0-cy)*d[0])/den
            if t>0 and -1e-6<=u<=1+1e-6: best=max(best,t)
        x,y=cx+d[0]*(best+pad),cy+d[1]*(best+pad)
        if flat is not None: y=max(y,flat)
        out.append((x,y))
    return out
def ring_cast(c,u,v,K,pad,r0=0.085,floor=None,ceil=None,inside=False):
    """the body's real cross-section round an axis point c, in the plane of u and v: K rays cast inward from r0 (between
    the legs, so they never reach the other one), padded outward; floor/ceil clamp heights"""
    pts=[]; rs=[]
    for k in range(K):
        a=2*math.pi*k/K; d=(u*math.cos(a)+v*math.sin(a)).normalized()
        hit=BVH.ray_cast(c,d,0.15) if inside else BVH.ray_cast(c+d*r0,-d,r0)   # from inside: the first surface is this limb's own
        rs.append((hit[0]-c).length if hit[0] is not None and (hit[0]-c).length<0.12 else None)
    good=[r for r in rs if r is not None]; fill=sum(good)/len(good) if good else 0.04
    for k in range(K):
        a=2*math.pi*k/K; d=(u*math.cos(a)+v*math.sin(a)).normalized(); q=c+d*((rs[k] or fill)+pad)
        if floor is not None: q.z=max(q.z,floor)
        if ceil is not None: q.z=min(q.z,ceil)
        pts.append(q)
    return pts
def loft(rings,caps=True):
    """a mesh object from rings of 3-D points (equal counts), closed at both ends"""
    bm=bmesh.new(); vs=[[bm.verts.new(p) for p in r] for r in rings]; K=len(rings[0])
    for a,b in zip(vs,vs[1:]):
        for k in range(K): bm.faces.new((a[k],a[(k+1)%K],b[(k+1)%K],b[k]))
    if caps:
        for r,flip in ((vs[0],True),(vs[-1],False)):
            c=bm.verts.new(sum((v.co for v in r),Vector())/K)
            for k in range(K): bm.faces.new((r[k],r[(k+1)%K],c) if not flip else (r[(k+1)%K],r[k],c))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    m=bpy.data.meshes.new('loft'); bm.to_mesh(m); bm.free()
    o=bpy.data.objects.new('loft',m); bpy.context.scene.collection.objects.link(o); return o
def apply_all(o):
    bpy.context.view_layer.objects.active=o
    for o2 in bpy.context.selected_objects: o2.select_set(False)
    o.select_set(True)
    for md in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=md.name)
def prism(bm,poly,z0,z1,part_list,part):
    """a slab from z0 to z1 over a 2-D polygon (sole, heel); its points are tagged with part"""
    b=[bm.verts.new((x,y,z0)) for x,y in poly]; t=[bm.verts.new((x,y,z1)) for x,y in poly]; n=len(poly)
    for k in range(n): bm.faces.new((b[k],b[(k+1)%n],t[(k+1)%n],t[k]))
    bm.faces.new(t); bm.faces.new(b[::-1])
    part_list.extend([part]*(2*n))

def build(side,top_rz,kind):
    S='L' if side>0 else 'R'
    leg=[i for i in range(len(P)) if P[i].x*side>0.02 and W[i].get('shin.'+S,0)+W[i].get('foot.'+S,0)>0.5]
    ground=min(P[i].z for i in leg)
    fb=arm.data.bones['foot.'+S]; ah=arm.matrix_world@fb.head_local; at=arm.matrix_world@fb.tail_local
    ankle=ah.z; collar=ankle-0.004
    fwd=Vector((at.x-ah.x,at.y-ah.y,0)).normalized(); lat=fwd.cross(Vector((0,0,1))).normalized()
    foot=[P[i] for i in leg if P[i].z<collar+0.01]
    ss=[p.dot(fwd) for p in foot]; heel,toe=min(ss),max(ss)
    # the last: cross-sections of the foot, heel to toe, cast round a line along the foot a little above the ground
    K=12; rings=[]; N=9; o0=ah-fwd*ah.dot(fwd); o0=Vector((o0.x,o0.y,0))
    for k in range(N):
        sk=heel+0.004+(toe-heel-0.008)*k/(N-1); h=ground+0.028*(1-0.35*k/(N-1))
        c=o0+fwd*sk+Vector((0,0,h))
        rings.append(ring_cast(c,lat,Vector((0,0,1)),K,0.005 if 0<k<N-1 else 0.003,r0=0.07,floor=ground,ceil=collar+0.01))
    o=loft(rings)
    topZ=collar
    if kind=='boot':
        topZ=zof(top_rz,side); srings=[]
        sb=arm.data.bones['shin.'+S]; sh_=arm.matrix_world@sb.head_local; st_=arm.matrix_world@sb.tail_local
        z=collar-0.02
        while z<topZ+0.012:
            t=(z-st_.z)/(sh_.z-st_.z); c=st_.lerp(sh_,t)   # the shin bone's line at this height
            srings.append(ring_cast(c,Vector((1,0,0)),Vector((0,1,0)),K,0.007,inside=True))
            z+=0.025
        o2=loft(srings)
        bo=o.modifiers.new('u','BOOLEAN'); bo.operation='UNION'; bo.object=o2; bo.solver='EXACT'; apply_all(o); bpy.data.objects.remove(o2)
    r=o.modifiers.new('r','REMESH'); r.mode='VOXEL'; r.voxel_size=0.0035
    sm_=o.modifiers.new('s','CORRECTIVE_SMOOTH'); sm_.iterations=8; sm_.use_only_smooth=True
    apply_all(o)
    dec=o.modifiers.new('d','DECIMATE'); dec.decimate_type='COLLAPSE'; dec.ratio=min(1.0,(75 if kind=='shoe' else 150)/max(1,len(o.data.polygons))); apply_all(o)
    bm=bmesh.new(); bm.from_mesh(o.data)
    # clean cuts: the opening round the leg, and the bottom where the upper meets the sole
    g=bm.verts[:]+bm.edges[:]+bm.faces[:]
    bmesh.ops.bisect_plane(bm,geom=g,plane_co=(0,0,topZ),plane_no=(0,0,1),clear_outer=True)
    g=bm.verts[:]+bm.edges[:]+bm.faces[:]
    bmesh.ops.bisect_plane(bm,geom=g,plane_co=(0,0,ground+0.012),plane_no=(0,0,-1),clear_outer=True)
    parts=[0]*len(bm.verts)
    for i,v in enumerate(bm.verts):
        if v.co.z>topZ-(0.004 if kind=='shoe' else 0.0): parts[i]=2   # the collar's edge
    # the sole, with a welt a few millimetres proud of the upper; a heel block under the back third
    outline=ring_of([(p.dot(fwd),p.dot(lat)) for p in foot],16,0.009)
    sole=[tuple(fwd*a_+lat*b_) for a_,b_ in outline]; sole=[(x,y) for x,y,_ in sole]
    prism(bm,sole,ground,ground+0.012,parts,1)
    hz=ground+(0.026 if kind=='boot' else 0.02); cut=heel+(toe-heel)*0.27
    heelpoly=[(a_,b_) for a_,b_ in outline if a_<cut]; heelpoly=[(cut,max(b_ for a_,b_ in outline if a_<cut+0.02))]+sorted(heelpoly,key=lambda t:math.atan2(t[1],t[0]-heel-0.04))+[(cut,min(b_ for a_,b_ in outline if a_<cut+0.02))] if heelpoly else []
    if len(heelpoly)>=3:
        hp=ring_of(heelpoly,10,-0.001); prism(bm,[(tuple(fwd*a_+lat*b_)[0],tuple(fwd*a_+lat*b_)[1]) for a_,b_ in hp],ground,hz,parts,1)
    if kind=='boot':   # a folded cuff at the top: a band a little proud of the shaft, 3.5 cm deep
        # the opening's own edge loop, walked in order (sorting its points by angle can zig-zag on a shaft like this)
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
        rim=[e for e in bm.edges if e.is_boundary and all(abs(v.co.z-topZ)<2e-4 for v in e.verts)]
        nb={}
        for e in rim:
            a_,b_=e.verts; nb.setdefault(a_,[]).append(b_); nb.setdefault(b_,[]).append(a_)
        loops=[]; seen=set()
        for v0 in nb:
            if v0 in seen: continue
            loop=[v0]; seen.add(v0); prev=None; cur=v0
            while True:
                nxt=[w for w in nb[cur] if w is not prev and w not in seen]
                if not nxt: break
                prev,cur=cur,nxt[0]; loop.append(cur); seen.add(cur)
            loops.append(loop)
        top=max(loops,key=len) if loops else []
        if len(top)>=6:
            def outward(v):
                n=sum((f.normal for f in v.link_faces),Vector()); n.z=0
                return n.normalized() if n.length>1e-6 else Vector((1,0,0))
            out=[outward(v) for v in top]
            up=[bm.verts.new(v.co+w*0.008+Vector((0,0,0.003))) for v,w in zip(top,out)]
            dn=[bm.verts.new(v.co+w*0.01+Vector((0,0,-0.035))) for v,w in zip(top,out)]
            n=len(top)
            for k in range(n):
                j=(k+1)%n
                for quad in ((up[k],up[j],dn[j],dn[k]),(top[k],top[j],up[j],up[k])):
                    f=bm.faces.new(quad); f.normal_update()
                    od=(out[k]+out[j]).normalized()
                    if quad[0] is up[k] and f.normal.dot(od)<0: f.normal_flip()     # the band faces out
                    if quad[0] is top[k] and f.normal.z<0: f.normal_flip()         # the lip faces up
            parts+= [2]*(2*n)
    bmesh.ops.triangulate(bm,faces=bm.faces[:])
    bm.to_mesh(o.data); bm.free()
    o.data['parts']=parts
    return o,dict(ground=ground,collar=collar,top=topZ,heel=heel,toe=toe,fwd=fwd,leg=leg,parts=parts)

out={}
for kind,top_rz in (('shoe',None),('boot',0.43)):
    keys=[k for k in (me.shape_keys.key_blocks if me.shape_keys else []) if k.name!='Basis']
    item={'pos':[],'nrm':[],'shade':[],'part':[],'skin':[],'idx':[],'rest':[],'bones':[],'morph':{k.name:[] for k in keys}}
    bones=[]; base=0
    for side in (1,-1):
        o,info=build(side,top_rz,kind)
        m=o.data
        # shade: Blender's dirt bake, so creases and the sole's edge read
        bpy.context.view_layer.objects.active=o; o.select_set(True)
        c_=m.color_attributes.new('shade','FLOAT_COLOR','POINT'); m.color_attributes.active_color=c_
        bpy.ops.object.mode_set(mode='VERTEX_PAINT'); bpy.ops.paint.vertex_color_dirt(blur_strength=1,blur_iterations=1,clean_angle=3.14,dirt_angle=0,dirt_only=False); bpy.ops.object.mode_set(mode='OBJECT')
        sh=[c_.data[i].color[0] for i in range(len(m.vertices))]; lo,hi=min(sh),max(sh)
        m.calc_loop_triangles()
        vn=[Vector() for _ in m.vertices]
        for p in m.polygons:
            for i in p.vertices: vn[i]+=p.normal*p.area
        for i,v in enumerate(m.vertices):
            x,y,z=v.co; n=vn[i].normalized()
            part=info['parts'][i] if i<len(info['parts']) else 0
            item['pos']+=[round(x,4),round(z,4),round(-y,4)]; item['nrm']+=[round(n.x,3),round(n.z,3),round(-n.y,3)]
            item['shade'].append(round(0.7+0.3*(sh[i]-lo)/max(1e-6,hi-lo),2)); item['part'].append(part)
            near=kd.find_n(v.co,6); acc={}; tot=0; rest=Vector()
            for _,j,d in near:
                w=1/(d+0.004); tot+=w; rest+=(REST[j]+(v.co-P[j]))*w
                for b,bw in W[j].items(): acc[b]=acc.get(b,0)+bw*w
            rest/=tot; item['rest']+=[round(rest.x,4),round(rest.y,4),round(rest.z,4)]
            for k in keys:   # the body's shapes (peoples, Lean, Heavy) from the full body's nearest points, as the hair does
                d=Vector()
                for _,j,dd in near: d+=(k.data[j].co-P[j])*((1/(dd+0.004))/tot)
                item['morph'][k.name]+=[round(d.x,4),round(d.z,4),round(-d.y,4)]
            S_='L' if side>0 else 'R'; acc={b:w for b,w in acc.items() if b in ('foot.'+S_,'shin.'+S_)} or {'shin.'+S_:1.0}   # a boot follows the shin and foot only, never the thigh
            top4=sorted(acc.items(),key=lambda t:-t[1])[:4]; s4=sum(w for _,w in top4)
            sk=[]
            for b,w in top4:
                if b not in bones: bones.append(b)
                sk.append([bones.index(b),round(w/s4,3)])
            item['skin'].append(sk)
        for t in m.loop_triangles: item['idx']+=[base+k for k in t.vertices]
        base+=len(m.vertices)
        tri=len(m.loop_triangles)
        print(kind,'side',side,len(m.vertices),'points',tri,'triangles')
        bpy.data.objects.remove(o)
    item['bones']=bones
    # the template height below which the body is replaced (the foot under a shoe, the lower leg in a boot)
    item['hideZ']=0.072 if kind=='shoe' else top_rz+0.005
    out[kind]=item
json.dump(out,open(out_path,'w'),separators=(',',':'))
