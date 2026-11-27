# Farhallow's plan v3, top-down (north up, 1 px = 10 cm, 140 x 110 m): stage 3 of the city-planning skill - every
# building from the logistics table (docs/settlements/farhallow.md) with its zone, door and the main roads.
#   python3 farhallow_plan.py out.png
import math,random,sys
from PIL import Image,ImageDraw,ImageFont
MW,H=1400,1100; W=MW+470; S=10.0
def P(x,y): return (x*S, y*S)            # metres from the top-left corner
rng=random.Random(4)
img=Image.new('RGB',(W,H),(104,138,74)); d=ImageDraw.Draw(img)
# the land rises from the harbour (south-east) to a rise in the north-east: contour lines every 2 m
for k,(cx,cy,rx,ry) in enumerate([(98,26,46,34),(100,24,36,26),(102,22,26,18),(104,21,16,11)]):
    d.ellipse([P(cx-rx,cy-ry),P(cx+rx,cy+ry)],outline=(88,120,62),width=3)
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
# the sea: a curving bay in the south-east
coast=[(55,110),(62,96),(74,88),(86,84),(96,76),(104,64),(112,58),(124,56),(140,52),(140,110)]
beach=[(x-3,y-3.5) for x,y in coast[:-1]]+[(140,48)]
d.polygon([P(x,y) for x,y in beach+[(140,110),(52,110)]],fill=(214,196,150))
d.polygon([P(x,y) for x,y in coast],fill=(64,128,150))
d.line([P(x,y) for x,y in coast[:-1]],fill=(240,240,232),width=3)
# woods around the clearing (drawn later, once we know where the buildings are)
TREES=[]
for _ in range(520):
    x=rng.uniform(0,140); y=rng.uniform(0,110)
    cx,cy=62,50
    if ((x-cx)/52)**2+((y-cy)/40)**2<1 or (x>50 and y>78) or (x>95 and y>48): continue
    TREES.append((x,y,rng.uniform(1.6,3.2),rng.choice([(48,84,46),(58,96,52),(42,74,42)])))
# fields in the north-west, fenced
d.rectangle([P(14,14),P(37,34)],fill=(196,170,88),outline=(110,80,50),width=4)
for k in range(15,34,2): d.line([P(15,k),P(36,k)],fill=(176,150,72),width=2)
d.rectangle([P(16,38),P(30,46)],fill=(120,100,64),outline=(110,80,50),width=3)   # vegetable plots
for k in range(17,30,3): d.line([P(k,39),P(k,45)],fill=(90,130,70),width=5)
# the palisade with the north gate, the road in from the north
pal=[(10,8),(40,6),(56,4)]; pal2=[(68,4),(92,6),(114,13),(121,40)]
d.line([P(x,y) for x,y in pal],fill=(92,66,44),width=8); d.line([P(x,y) for x,y in pal2],fill=(92,66,44),width=8)
d.line([P(10,8),P(6,40),P(8,70),P(20,92)],fill=(92,66,44),width=8)

def segd(p,a,b):
    ax,ay=a; bx,by=b; px,py=p; dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L)); return math.hypot(px-ax-t*dx,py-ay-t*dy)
ROADS=[([(62,0),(62,4),(60,14),(58,26),(60,40),(64,50)],4.2,'gate road'),
       ([(64,50),(72,58),(80,66),(84,74),(86,80)],3.6,'harbour road'),
       ([(64,50),(58,54),(46,60),(36,64)],3.0,'west road'),
       ([(64,50),(76,45),(90,38.5),(101,31),(104.5,25.5)],2.8,'rise road')]
# zones, tinted under everything: who lives where
ZLABELS=[]
def zone(poly,c,label,at):
    z=Image.new('RGBA',img.size,(0,0,0,0)); ImageDraw.Draw(z).polygon([P(x,y) for x,y in poly],fill=c)
    img.paste(Image.alpha_composite(img.convert('RGBA'),z).convert('RGB')); 
    ZLABELS.append((at,label))
zone([(68,28),(80,20),(98,10),(112,14),(112,30),(112,48),(98,52),(88,42),(70,44)],(255,215,120,70),'WELL-OFF (upwind, uphill)',(71,12.5))
zone([(48,66),(62,62),(80,62),(100,64),(100,74),(86,84),(74,88),(60,92),(46,84)],(70,60,90,70),'POOR (downwind, by the shore)',(30,93.5))
d=ImageDraw.Draw(img)
for pts,w,_ in ROADS:
    d.line([P(x,y) for x,y in pts],fill=(170,140,100),width=int(w*S),joint='curve')
    for x,y in pts: d.ellipse([P(x-w/2,y-w/2),P(x+w/2,y+w/2)],fill=(170,140,100))
d.ellipse([P(56,42),P(72,58)],fill=(176,150,112))                                    # the square round the well
d.ellipse([P(62.5,48.5),P(65.5,51.5)],fill=(130,150,170),outline=(70,70,70),width=3)
# the sea wall, breakwater, lighthouse and pier stay as in v2
d.line([P(x,y) for x,y in [(80,82),(92,76),(100,70),(106,62)]],fill=(150,146,138),width=22)
d.line([P(x,y) for x,y in [(106,62),(116,64),(126,70),(132,80)]],fill=(150,146,138),width=26)
d.ellipse([P(129,77),P(136,84)],fill=(214,210,200),outline=(90,80,70),width=4)
d.rectangle([P(85,80),P(90,100)],fill=(122,88,56)); d.rectangle([P(78,98),P(104,103)],fill=(122,88,56)); d.rectangle([P(104,96),P(108,104)],fill=(122,88,56))
def boat(x,y,l,w,a,c=(140,98,62)):
    pts=[(-l/2,0),(-l/2+1,-w/2),(l/2-l*0.25,-w/2),(l/2,0),(l/2-l*0.25,w/2),(-l/2+1,w/2)]
    ca,sa=math.cos(a),math.sin(a); d.polygon([P(x+u*ca-v*sa,y+u*sa+v*ca) for u,v in pts],fill=c,outline=(60,40,26))
boat(96,92,8,2.8,-0.3); boat(76,94,6,2.2,0.4); boat(120,100,16,5,0.05,(110,76,50))
RICH,MID,POOR,TRADE,PUB=(214,170,108),(166,122,84),(124,100,80),(112,100,96),(150,96,64)
# lanes (dashed): only so the buildings off the main roads know which way to face; drawn properly in stage 4
LANES=[([(80,66),(72,71),(64,77),(54,82.5)],2.2,'shore lane'),
       ([(58.3,28),(50,28),(38,27)],2.2,'field lane'),
       ([(46,60),(40,52),(37,45.5),(31.5,44.5)],2.0,'farm lane'),
       ([(84,41.3),(95,46),(101,46.5)],1.8,'salt path')]
for pts,w,_ in LANES:
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        d.line([P(x0,y0),P(x1,y1)],fill=(178,150,110),width=int(w*S))
    for x,y in pts: d.ellipse([P(x-w/2,y-w/2),P(x+w/2,y+w/2)],fill=(178,150,110))
STREETS={nm:(pts,w) for pts,w,nm in ROADS+LANES}
STREETS['square']=([(64+8.2*math.cos(i*math.pi/18),50+8.2*math.sin(i*math.pi/18)) for i in range(37)],0.0)   # its edge
def front(street,x,y,w,h,gap=1.0,flip=False):
    """Set a building along a street: long side parallel to it, the door side facing it, `gap` metres back from its edge.
    (x, y) only says roughly where along the street and on which side."""
    pts,rw=STREETS[street]; best=None
    for a_,b_ in zip(pts,pts[1:]):
        dx,dy=b_[0]-a_[0],b_[1]-a_[1]; L2=dx*dx+dy*dy; t=max(0,min(1,((x-a_[0])*dx+(y-a_[1])*dy)/L2))
        q=(a_[0]+t*dx,a_[1]+t*dy); dd=math.hypot(x-q[0],y-q[1])
        if best is None or dd<best[0]: best=(dd,q,(dx,dy))
    _,q,(dx,dy)=best; L=math.hypot(dx,dy); tx,ty=dx/L,dy/L; nx,ny=-ty,tx
    if (x-q[0])*nx+(y-q[1])*ny<0: nx,ny=-nx,-ny          # the side of the street the building is on
    off=rw/2+gap+h/2; cx,cy=q[0]+nx*off,q[1]+ny*off
    ang=math.atan2(ty,tx)
    # local -y is the front: make it point back at the street
    if -math.sin(ang)*0+(-1)*0: pass
    fx,fy=math.sin(ang),-math.cos(ang)                     # world direction of local (0,-1)
    if fx*(-nx)+fy*(-ny)<0: ang+=math.pi
    return cx,cy,ang
# (street, rough x, rough y, building type (a trailing ~ mirrors it), gap, colour, number, name); street None = placed by hand (x, y, angle).
# Only types from building_types.py may be placed, so the plan holds the real floorplans, plots and doors.
from building_types import T as TYPES, footprint
B=[('gate road',52,36,'inn',1.5,PUB,1,'The Gull & Lantern, tavern with rooms'),
   ('rise road',97,30,'merchant_house_small',1.5,RICH,2,"Harbour master's house"),
   ('rise road',78,40,'merchant_house',1.5,RICH,3,'Dunmore house (fish merchants)'),
   (None,107.3,20.3,'merrith_shrine',-2.58,(200,196,186),4,'Shrine of Merrith, on the rise'),
   ('harbour road',87,57,'workshop',1.5,TRADE,5,'Smithy: forge, quench trough, charcoal'),
   (None,92,67,'smokehouse',-2.21,TRADE,6,'Smokehouse'),
   ('harbour road',80,75,'store',1.0,TRADE,7,'Salt house and fish store'),
   (None,72,84,'boat_shed',-0.58,TRADE,8,"Boatwright's shed"),
   (None,104.5,52.5,'salt_works',-0.64,TRADE,16,'Salt-boiling hut and pans'),
   ('shore lane',72,68,'cottage',1.0,POOR,9,"Net-mender's cottage"),
   ('shore lane',63,74,'cottage',1.0,POOR,10,"Fishers' cottages"),('shore lane',54,79,'cottage',1.0,POOR,10,''),
   ('shore lane',52,87,'cottage',1.0,POOR,10,''),
   ('gate road',52,13,'granary',1.0,TRADE,11,'Granary, by the gate and fields'),
   ('gate road',66,11,'guard_post',1.0,PUB,12,'Guard post and bell'),
   ('west road',34,58,'farmstead',1.0,MID,13,'Farmstead and farming cottage'),('west road',42,69,'cottage',1.0,MID,13,''),
   (None,34.5,40,'hen_house',1.57,MID,14,'Hen house and goat pen'),
('field lane',46,24,'street_house',1.0,MID,15,'Old street house by the fields')]
def corners(x,y,w,h,a):
    ca,sa=math.cos(a),math.sin(a); return [(x+u*ca-v*sa,y+u*sa+v*ca) for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
def overlap(A,Bq,pad=0.5):   # separating axis test, with a little elbow room
    for poly in (A,Bq):
        for i in range(4):
            x0,y0=poly[i]; x1,y1=poly[(i+1)%4]; nx,ny=y0-y1,x1-x0; L=math.hypot(nx,ny); nx/=L; ny/=L
            pa=[px*nx+py*ny for px,py in A]; pb=[px*nx+py*ny for px,py in Bq]
            if max(pa)+pad<=min(pb) or max(pb)+pad<=min(pa): return False
    return True
placed=[]; PTYPE=[]
PMIR=[]
for st,x,y,ty,g,c,n,name in B:
    PMIR.append(ty.endswith('~')); ty=ty.rstrip('~')     # a trailing ~ mirrors the floorplan (a planned variation)
    w,h=footprint(ty)
    if st: x,y,a=front(st,x,y,w,h,g)
    else: a=g
    placed.append((x,y,w,h,a,c,n,name,st)); PTYPE.append(ty)
def local(k,u,v):   # a point in building k's floorplan coordinates (street along y=0) to the map
    x,y,w,h,a=placed[k][:5]; u=w-u if PMIR[k] else u; uu,vv=u-w/2,v-h/2; ca,sa=math.cos(a),math.sin(a); return (x+uu*ca-vv*sa,y+uu*sa+vv*ca)
def room_geo(k,r):   # a floorplan rectangle (x, y, w, h) as a map rectangle (cx, cy, w, h, angle)
    cx,cy=local(k,r[0]+r[2]/2,r[1]+r[3]/2); return (cx,cy,r[2],r[3],placed[k][4])
# plots behind the houses, Wayfolk style (docs/peoples/wayfolk.md): a long yard and garden behind each house that
# faces a street - walled for the well-off, a yard for the inn, short and fenced for the poor
PLOTS=[]   # (index of its house, label, x, y, w, max depth, angle): shortened later to the room the lot has
for k,ty in enumerate(PTYPE):
    pl=TYPES[ty]['plot']
    if not pl: continue
    px,pw,dmin,dmax,lab=pl; h=placed[k][3]
    PLOTS.append((k,lab)+room_geo(k,(px,h,pw,dmax)))
WAYSTONE=(57.6,49.2,3,3,0.38)   # the village waystone type, in the square, facing the gate road where travellers arrive
def outline(x,y,w,h,a,step=0.5):   # points every half metre round a rectangle, and its centre
    cs=corners(x,y,w,h,a); out=[(x,y)]
    for i in range(4):
        (x0,y0),(x1,y1)=cs[i],cs[(i+1)%4]; n=max(1,int(math.hypot(x1-x0,y1-y0)/step))
        out+=[(x0+(x1-x0)*k/n,y0+(y1-y0)*k/n) for k in range(n)]
    return out
def inside(p,poly):
    x,y=p; c=False
    for i in range(len(poly)):
        x0,y0=poly[i]; x1,y1=poly[i-1]
        if (y0>y)!=(y1>y) and x<x0+(y-y0)*(x1-x0)/(y1-y0): c=not c
    return c
def rect_hit(p,r,pad): return r[0]-pad<=p[0]<=r[2]+pad and r[1]-pad<=p[1]<=r[3]+pad
LINES=[(pal,1.5,'palisade'),(pal2,1.5,'palisade'),([(10,8),(6,40),(8,70),(20,92)],1.5,'palisade'),
       ([(80,82),(92,76),(100,70),(106,62)],1.6,'sea wall'),([(106,62),(116,64),(126,70),(132,80)],1.8,'breakwater')]
RECTS=[((14,14,37,34),'field'),((16,38,30,46),'vegetable plots'),((85,80,90,100),'pier'),((78,98,104,103),'pier')]
SHORE_OK={6,7,8,16}   # the smokehouse and the boatwright's shed belong on the shore
things=[(k,'%d %s'%(placed[k][6],(r[4] or 'passage').replace('\n',' ')),room_geo(k,r)) for k in range(len(placed)) for r in TYPES[PTYPE[k]]['rooms']]+\
       [(pl[0],'%d %s'%(placed[pl[0]][6],pl[1]),pl[2:]) for pl in PLOTS]+[(-1,'waystone',WAYSTONE)]
def ground_clash(n,nm,geo):   # everything but other buildings: streets, square, walls, fields, sea, beach
    pts=outline(*geo); out=[]
    for lp,rw,ln in ROADS+LANES:
        if any(segd(q,p0,p1)<rw/2+0.3 for q in pts for p0,p1 in zip(lp,lp[1:])): out.append('%s on the %s'%(nm,ln))
    if nm!='waystone' and any(math.hypot(q[0]-64,q[1]-50)<8.3 for q in pts): out.append('%s in the square'%nm)
    for lp,cl,ln in LINES:
        if any(segd(q,p0,p1)<cl for q in pts for p0,p1 in zip(lp,lp[1:])): out.append('%s against the %s'%(nm,ln))
    for r,rn in RECTS:
        if any(rect_hit(q,r,0.8) for q in pts): out.append('%s on the %s'%(nm,rn))
    if any(inside(q,coast) for q in pts): out.append('%s in the sea'%nm)
    elif (placed[n][6] if n>=0 else 0) not in SHORE_OK and any(inside(q,beach+[(140,110),(52,110)]) for q in pts): out.append('%s on the beach'%nm)
    return out
# plots take what room is left: each is shortened (never below 2 m) until it clears everything, like real plots that
# end where the neighbour's begins
PLOTNAMES=('yard and garden','walled garden')
fixed=[t for t in things if not t[1].split(' ',1)[-1] in PLOTNAMES]
plots=sorted([t for t in things if t not in fixed],key=lambda t:{RICH:0,PUB:1,MID:2}.get(placed[t[0]][5],3)); kept=[]; dropped=[]; shared=[]
for n,nm,(x,y,w,h,a) in plots:
    px,pw,dmin,dmax,_=TYPES[PTYPE[n]]['plot']; hh=placed[n][3]
    for dep in [dmax-0.5*i for i in range(int((dmax-dmin)/0.5)+1)]:
        geo=room_geo(n,(px,hh,pw,dep))
        if ground_clash(n,nm,geo): continue
        if any(o[0]!=n and overlap(corners(*geo),corners(*o[2]),0.4) for o in fixed+kept): continue
        kept.append((n,nm,geo)); break
    else:
        why=ground_clash(n,nm,geo)+[o[1] for o in fixed+kept if o[0]!=n and overlap(corners(*geo),corners(*o[2]),0.4)]
        (shared if placed[n][5]==POOR else dropped).append('%s at (%.0f,%.0f) (%s)'%(nm,placed[n][0],placed[n][1],', '.join(why[:3])))
PLOTS=[(n,nm.split(' ',1)[1],)+geo for n,nm,geo in kept]
things=fixed+kept
problems=['%s: no room for even the smallest plot'%nm for nm in dropped]
if shared: print('%d poor cottages share a yard instead of their own plot (Wayfolk: "shared yard or none"):\n  '%len(shared)+'\n  '.join(shared))
for i,(n,nm,geo) in enumerate(things):
    for j in range(i+1,len(things)):
        if things[j][0]==n and n>=0: continue    # rooms of one building and its plot
        if overlap(corners(*geo),corners(*things[j][2]),0.4): problems.append('%s overlaps %s'%(nm,things[j][1]))
    problems+=ground_clash(n,nm,geo)
# trees: none on a building, garden, yard, road or lane
def clear(x,y,r):
    r_=r
    for n,nm,geo in things:
        cx_,cy_,w_,h_,a_=geo
        if math.hypot(x-cx_,y-cy_)<math.hypot(w_,h_)/2+r: return False
    for lp,rw,_ in ROADS+LANES:
        if any(segd((x,y),p0,p1)<rw/2+r for p0,p1 in zip(lp,lp[1:])): return False
    if any(rect_hit((x,y),r,r_pad) for r,_ in RECTS for r_pad in [r_]): return False
    return not inside((x,y),beach+[(140,110),(52,110)])
for x,y,r,c in TREES:
    if clear(x,y,r*0.7): d.ellipse([P(x-r,y-r),P(x+r,y+r)],fill=c)
print('\n'.join(problems) or 'no overlaps')
if '-v' in sys.argv: [print(n,st,round(x,1),round(y,1),round(math.degrees(a))) for x,y,w,h,a,c,n,_,st in placed]
# ---- stage 4: paths. Every door gets a short path to the nearest road, lane or the square; then the checks.
def street_doors(k):   # the type's doors and gates on its street front
    return [local(k,dx,0) for dx,dy,o,dw,kind in TYPES[PTYPE[k]]['doors'] if o=='h' and abs(dy)<0.01 and kind!='o']
def nearest_on_paths(p,skip=None):
    best=(1e9,None,None)
    for lp,rw,ln in ROADS+LANES:
        if ln==skip: continue
        for p0,p1 in zip(lp,lp[1:]):
            dx,dy=p1[0]-p0[0],p1[1]-p0[1]; L2=dx*dx+dy*dy; t=max(0,min(1,((p[0]-p0[0])*dx+(p[1]-p0[1])*dy)/L2))
            q=(p0[0]+t*dx,p0[1]+t*dy); dd=math.hypot(p[0]-q[0],p[1]-q[1])-rw/2
            if dd<best[0]: best=(dd,q,ln)
    sq=math.hypot(p[0]-64,p[1]-50)-8
    if sq<best[0]: best=(sq,(64+(p[0]-64)*8/(sq+8),50+(p[1]-50)*8/(sq+8)),'square')
    return best
SPURS=[]; pproblems=[]
for k,b_ in enumerate(placed):
  for dp in street_doors(k):
    dist,q,ln=nearest_on_paths(dp)
    if dist>14: pproblems.append('door of %d is %.0f m from any path'%(b_[6],dist)); continue
    SPURS.append((k,dp,q,ln))
    # the spur may not cross any other building, plot or yard
    seg=[(dp[0]+(q[0]-dp[0])*i/10,dp[1]+(q[1]-dp[1])*i/10) for i in range(1,10)]
    for n,nm,geo in things:
        if n==k: continue
        cs=corners(*geo)
        if any(inside(pt,cs) for pt in seg): pproblems.append('path from door %d crosses %s'%(b_[6],nm))
# every lane must start and end somewhere: on another path, at a door, or at a named place
DEST=[((37,27),'field gate'),((30,44),'vegetable plots')]
doors=[dp for k in range(len(placed)) for dp in street_doors(k)]
for lp,rw,ln in LANES:
    for end in (lp[0],lp[-1]):
        dist,_,_=nearest_on_paths(end,skip=ln)
        if dist<0.5 or any(math.hypot(end[0]-x,end[1]-y)<3 for x,y in doors) or any(math.hypot(end[0]-x,end[1]-y)<3 for (x,y),_ in DEST): continue
        pproblems.append('the %s ends at (%.0f,%.0f), leading nowhere'%(ln,*end))
    # and must be needed: some door must use it
    if not any(sp[3]==ln for sp in SPURS) and not any(math.hypot(e[0]-x,e[1]-y)<3 for e in (lp[0],lp[-1]) for (x,y),_ in DEST):
        pproblems.append('nothing uses the %s'%ln)
print('\n'.join(pproblems) or 'paths: every door reached, every lane leads somewhere')
# ---- stage 5: doodads. Each has a purpose, stands on ground that suits it, and blocks no path or door.
# The ground each kind may stand on (city-planning skill, "Check every placement")
KINDS={'bench':{'front','square','yard','garden','grass','beach'},'barrel':{'front','yard','beach','pier','workshop'},
 'crate':{'front','yard','beach','pier'},'woodpile':{'yard','front','grass','beach','workshop'},'washing line':{'yard','garden'},
 'well':{'garden','yard','square'},'fruit tree':{'garden'},'flower bed':{'garden'},'lamp':{'front','square'},'sign':{'front'},
 'trough':{'yard','front','pen','grass'},'cart':{'yard','front','grass'},'net rack':{'beach','yard','grass'},
 'lobster pots':{'pier','beach'},'gutting table':{'beach','pier'},'scarecrow':{'field'},'haystack':{'field','yard'},
 'notice post':{'square','front'},'torch':{'wall'},'bell frame':{'front','grass','yard'},'anvil':{'workshop'},
 'quench trough':{'workshop'},'grindstone':{'workshop'},'charcoal':{'workshop','yard'},'candles':{'front'},
 'sacks':{'yard','front','beach','pier'},'chopping block':{'workshop','yard'},'manure heap':{'yard'},'drying rack':{'beach','grass'},'hen coop':{'yard','garden'},
 'boat hull':{'workshop','beach','yard'}}
COL={'bench':(120,84,50),'barrel':(140,96,56),'crate':(176,140,90),'woodpile':(120,86,52),'washing line':(240,240,230),
 'well':(130,150,170),'fruit tree':(70,120,60),'flower bed':(214,120,150),'lamp':(250,210,120),'sign':(200,160,90),
 'trough':(100,130,150),'cart':(150,110,70),'net rack':(200,200,180),'lobster pots':(150,110,80),'gutting table':(170,150,120),
 'scarecrow':(150,110,60),'haystack':(214,190,110),'notice post':(160,120,80),'torch':(250,160,60),'bell frame':(90,80,70),
 'anvil':(60,60,64),'quench trough':(100,130,150),'grindstone':(170,166,158),'charcoal':(40,36,34),'candles':(250,230,170),
 'sacks':(214,200,170),'chopping block':(110,80,50),'manure heap':(110,90,60),'drying rack':(190,180,150),'hen coop':(160,120,80),'boat hull':(130,92,56)}
# Farhallow's own props (map coordinates)
VILLAGE=[(60.6,53.4,0.4,0.4,0.0,'notice post',"the harbour master's notices: when the trader's ship is due"),
 (69.0,43.4,1.6,0.5,0.4,'bench','old folk sitting by the well'),
 (56,4.1,0.4,0.4,0.0,'torch','gate torch on the gate post, lit at dusk'),(68,4.1,0.4,0.4,0.0,'torch','gate torch on the gate post, lit at dusk'),
 (25,24,0.8,0.8,0.0,'scarecrow','keeping crows off the infield'),(32,30,2.0,2.0,0.0,'haystack','winter hay for the goats'),
 (61.5,90.5,2.6,0.4,-0.58,'net rack','fishers drying their nets'),(64.8,88.4,2.6,0.4,-0.58,'net rack','fishers drying their nets'),
 (99.5,62.0,2.4,0.5,0.9,'drying rack','fish drying in the wind before smoking'),
 (82.0,83.0,1.6,0.8,-0.4,'gutting table','gutting the catch as it lands'),
 (87.5,92,1.2,1.2,0.0,'lobster pots','pots stacked on the pier'),(88.4,84,1.0,1.0,0.0,'barrel','barrels being rolled to the boats'),
 (100.5,99.0,1.6,1.2,0.0,'crate',"cargo waiting for the trader's ship (the last ship)")]
DOODADS=[]   # (x, y, w, h, angle, kind, purpose, owner index or -1)
for k in range(len(placed)):
    ty=TYPES[PTYPE[k]]; a_=placed[k][4]
    for u,v,w_,h_,kind,why in ty['doodads']:
        DOODADS.append(room_geo(k,(u,v,w_,h_))+(kind,why,k))
    plot=[pl for pl in PLOTS if pl[0]==k]
    if plot and ty['plot']:
        dep=plot[0][5]; px=ty['plot'][0]
        for u,v,w_,h_,kind,why in ty['plot_doodads']:
            if v+h_<=dep-0.3: DOODADS.append(room_geo(k,(px+u,placed[k][3]+v,w_,h_))+(kind,why,k))
DOODADS+=[t_+(-1,) for t_ in VILLAGE]
def ground(p):   # what a point stands on
    for k in range(len(placed)):
        ty=TYPES[PTYPE[k]]
        for r in ty['rooms']:
            if inside(p,corners(*room_geo(k,r))):
                if PTYPE[k]=='workshop' and r[5] in ('shop','yard'): return 'workshop'
                if PTYPE[k]=='boat_shed': return 'workshop'
                if PTYPE[k]=='hen_house' and r[5]=='yard': return 'pen'
                return {'yard':'yard','garden':'garden'}.get(r[5],'indoor')
    for pl in PLOTS:
        if inside(p,corners(*pl[2:])): return 'garden' if pl[1]=='walled garden' else 'yard'
    for r,rn in RECTS:   # the pier stands over the sea, so it comes first
        if rect_hit(p,r,0): return {'field':'field','vegetable plots':'field','pier':'pier'}[rn]
    if inside(p,coast): return 'sea'
    if math.hypot(p[0]-64,p[1]-50)<8.2: return 'square'
    for lp,rw,ln in ROADS+LANES:
        if any(segd(p,p0,p1)<rw/2+0.15 for p0,p1 in zip(lp,lp[1:])): return 'path'   # a hand's breadth of margin
    for k,dp,q,ln in SPURS:
        if segd(p,dp,q)<0.6: return 'path'
    for k in range(len(placed)):
        # in front of the building, between its front and the street
        x,y,w,h,a=placed[k][:5]; ca,sa=math.cos(a),math.sin(a); dx,dy=p[0]-x,p[1]-y
        uu,vv=dx*ca+dy*sa,-dx*sa+dy*ca
        if -w/2<=uu<=w/2 and -h/2-2.6<=vv<-h/2: return 'front'

    for lp,cl,ln in LINES:
        if any(segd(p,p0,p1)<1.0 for p0,p1 in zip(lp,lp[1:])): return 'wall'
    if inside(p,beach+[(140,110),(52,110)]): return 'beach'
    return 'grass'
MOUNTED={'lamp','sign','candles','torch'}   # hung on a wall or post: only where they hang matters, and they block nothing
dproblems=[]
alldoors=[(k,dp) for k in range(len(placed)) for dp in street_doors(k)]
for i,(x,y,w_,h_,a_,kind,why,k) in enumerate(DOODADS):
    nm='%s (%s)'%(kind,placed[k][7] or placed[k][6] if k>=0 else 'village')
    if not why: dproblems.append('%s: no purpose'%nm)                     # 1. does it need to be there?
    pts=[(x,y)]+corners(x,y,w_,h_,a_)
    gs={ground(q) for q in ([(x,y)] if kind in MOUNTED else pts)}
    bad=gs-KINDS[kind]
    if 'path' in bad: dproblems.append('%s at (%.0f,%.0f) blocks a path'%(nm,x,y)); bad-= {'path'}        # 3. blocks a path?
    if bad: dproblems.append('%s at (%.0f,%.0f) stands on %s'%(nm,x,y,'/'.join(sorted(bad))))              # 2. ground that makes sense?
    for kk,dp in alldoors:                                                                                 # 3. blocks an entrance?
        if kind not in MOUNTED and (any(math.hypot(q[0]-dp[0],q[1]-dp[1])<1.0 for q in pts) or math.hypot(x-dp[0],y-dp[1])<1.8): dproblems.append('%s at (%.0f,%.0f) blocks a door'%(nm,x,y))
    for j in range(i+1,len(DOODADS)):
        o=DOODADS[j]
        if overlap(corners(x,y,w_,h_,a_),corners(*o[:5]),0.1): dproblems.append('%s overlaps %s'%(nm,o[5]))
print('\n'.join(dproblems) or 'doodads: %d placed, each with a purpose, on fitting ground, blocking nothing'%len(DOODADS))
for k,dp,q,ln in SPURS:
    d.line([P(*dp),P(*q)],fill=(178,150,110),width=int(1.2*S))
for k,kind,x,y,w,h,a in PLOTS:
    poly=[P(*q) for q in corners(x,y,w,h,a)]
    d.polygon(poly,fill={'walled garden':(150,184,110),'yard and garden':(140,170,100)}[kind],
              outline=(170,164,150) if kind=='walled garden' else (120,96,66),width=5 if kind=='walled garden' else 2)
wx,wy,ww,_,wa=WAYSTONE; d.polygon([P(*q) for q in corners(wx,wy,ww,ww,wa)],fill=(150,146,138),outline=(60,50,40))
d.ellipse([P(wx-0.6,wy-0.6),P(wx+0.6,wy+0.6)],fill=(250,210,120))
def tint(c,kind):   # rooms in the owner's colour, yards and outbuildings in their own
    return {'yard':(196,184,140),'garden':(150,184,110),'out':tuple(int(v*0.82) for v in c),'stone':(170,166,158)}.get(kind,c)
for k,(x,y,w,h,a,c,n,_,st) in enumerate(placed):
    rooms=TYPES[PTYPE[k]]['rooms']
    for r in rooms:   # shadow first, then the rooms
        if r[5] in ('room','shop','out','stone'): d.polygon([(px+5,py+5) for px,py in [P(*q) for q in corners(*room_geo(k,r))]],fill=(60,80,48))
    for r in rooms:
        d.polygon([P(*q) for q in corners(*room_geo(k,r))],fill=tint(c,r[5]),outline=(60,40,26),width=2 if r[5] not in ('yard','garden') else 1)
    for dx,dy,o,dw,kind in TYPES[PTYPE[k]]['doors']:
        if kind=='o': continue
        hw=dw/2; pts=[local(k,dx-hw,dy),local(k,dx+hw,dy)] if o=='h' else [local(k,dx,dy-hw),local(k,dx,dy+hw)]
        d.line([P(*pts[0]),P(*pts[1])],fill=(250,240,200),width=5)
    for hx_,hy_ in TYPES[PTYPE[k]]['hearths']:
        q=local(k,hx_,hy_); d.rectangle([P(q[0]-0.45,q[1]-0.45),P(q[0]+0.45,q[1]+0.45)],fill=(190,80,40))
    d.text(P(x,y),str(n),font=F(22,True),fill=(255,250,235),anchor='mm',stroke_width=3,stroke_fill=(40,30,20))
for x,y,w_,h_,a_,kind,why,k in DOODADS:   # the doodads
    poly=[P(*q) for q in corners(x,y,w_,h_,a_)]
    if kind in ('fruit tree','haystack','well','lobster pots','charcoal','manure heap'):
        r=max(w_,h_)/2; d.ellipse([P(x-r,y-r),P(x+r,y+r)],fill=COL[kind],outline=(40,30,20))
    else: d.polygon(poly,fill=COL[kind],outline=(40,30,20))
SMI=[k for k,b_ in enumerate(placed) if b_[6]==5][0]
fx,fy=local(SMI,0.6,1.2)
# smoke drifting downwind
for sx,sy in ((fx,fy),(95,70)):
    for k in range(5): d.ellipse([P(sx+k*2.6-1.2-0.3*k,sy+k*2.4-1.2-0.3*k),P(sx+k*2.6+1.2+0.3*k,sy+k*2.4+1.2+0.3*k)],outline=(200,200,200),width=2)
# wind rose
cx,cy=128,14; d.ellipse([P(cx-9,cy-9),P(cx+9,cy+9)],fill=(240,236,226),outline=(90,80,70),width=3)
d.line([P(cx-6,cy-6),P(cx+5,cy+5)],fill=(60,90,140),width=8); d.polygon([P(cx+7,cy+7),P(cx+2,cy+5.5),P(cx+5.5,cy+2)],fill=(60,90,140))
d.text(P(cx,cy-7.5),'N',font=F(18,True),fill=(40,30,20),anchor='mm'); d.text(P(cx-9,cy+11),'wind from the north-west',font=F(16,True),fill=(255,255,245),stroke_width=2,stroke_fill=(30,30,30))
def beat(x,y,t):
    d.ellipse([P(x-1.6,y-1.6),P(x+1.6,y+1.6)],fill=(200,60,50),outline=(255,255,255),width=3)
    d.text(P(x+2.3,y-1.2),t,font=F(19,True),fill=(255,255,255),stroke_width=3,stroke_fill=(60,20,20))
beat(67,54,'A  start'); beat(79,48.5,'B  first weapon'); beat(11,37,'C  first fight'); beat(62,6,'D  the gate falls'); beat(42,89,'E  the neighbour'); beat(110,103,'F  the last ship')
d.text(P(17,22),'INFIELD',font=F(20,True),fill=(120,96,50))
for (ax,ay,tx,ty,lab) in ((62,1.5,66,0.6,'north road to the OPEN FIELDS (~22 ha) and the common'),(6,24,1,18,'')):
    pass
d.text(P(66,0.8),'↑ to the open fields (~14 ha), the common pasture and woods',font=F(16,True),fill=(255,255,240),stroke_width=2,stroke_fill=(40,30,20))
d.text(P(1,3),'← open fields west',font=F(16,True),fill=(255,255,240),stroke_width=2,stroke_fill=(40,30,20))
d.text(P(124,88),'THE SEA',font=F(30,True),fill=(220,235,240)); d.text(P(114,44),'WOODS',font=F(24,True),fill=(200,220,190))
L=Image.new('RGBA',(440,1060),(250,246,236,240)); ld=ImageDraw.Draw(L); yy=12
for x,y,w,h,a,c,n,name,_ in placed:
    if not name: continue
    ld.rectangle((14,yy+3,32,yy+21),fill=c,outline=(60,40,26)); ld.text((40,yy),'%d  %s'%(n,name),font=F(17),fill=(30,28,26)); yy+=27
yy+=8
for t in ('white marks: doors and gates','yellow: well-off · purple: poor','green behind houses: yards, gardens','grey square by the well: the waystone','small marks: doodads (benches, barrels,','  woodpiles, nets...), each with a purpose','grey rings: smoke blowing downwind','rooms drawn from the building types:','    tools/map/building_types.py','',
          'A  you begin at the well','B  hatchet at the smithy woodpile,','    the blade above the smithy door','C  a Fog-warped wolf by the field',
          'D  something huge breaks the gate','E  the half-changed Vey son','F  the last ship at the pier\'s end','',
          'Paths (stage 4): roads, lanes, and a','path from every door to its street'):
    ld.text((14,yy),t,font=F(17,t[:1] in 'ABCDEF' and t[1:2]==' '),fill=(30,28,26) if t[:1] not in 'ABCDEF' or t[1:2]!=' ' else (140,40,30)); yy+=25
for at,label in ZLABELS: d.text(P(*at),label,font=F(20,True),fill=(255,255,245),stroke_width=3,stroke_fill=(40,30,20))
img.paste(L,(MW+15,15),L)
d.text((20,H-44),'FARHALLOW · plan v3: layout, paths and doodads (north up · 140 m × 110 m · ground rises to the north-east)',font=F(26,True),fill=(255,255,250),stroke_width=4,stroke_fill=(30,30,30))
img.save(sys.argv[1]); print('saved')
# ---- the plan for the game (godot/data/farhallow.json): everything the 3D village is built from, in plan metres
import json,os
ZONE={RICH:'rich',MID:'middling',POOR:'poor',TRADE:'trade',PUB:'public'}
data={'buildings':[dict(type=PTYPE[k],mirror=PMIR[k],x=b_[0],y=b_[1],w=b_[2],h=b_[3],a=b_[4],zone=ZONE.get(b_[5],'public'),n=b_[6],name=b_[7] or '',
                        doors=[list(dp) for dp in street_doors(k)]) for k,b_ in enumerate(placed)],
      'plots':[dict(owner=pl[0],label=pl[1],x=pl[2],y=pl[3],w=pl[4],h=pl[5],a=pl[6]) for pl in PLOTS],
      'roads':[dict(name=nm,pts=[list(q) for q in pts],width=w) for pts,w,nm in ROADS],
      'lanes':[dict(name=nm,pts=[list(q) for q in pts],width=w) for pts,w,nm in LANES],
      'spurs':[dict(owner=k,door=list(dp),to=list(q),street=ln) for k,dp,q,ln in SPURS],
      'doodads':[dict(kind=kind,x=x,y=y,w=w_,h=h_,a=a_,purpose=why,owner=k,mounted=kind in MOUNTED) for x,y,w_,h_,a_,kind,why,k in DOODADS],
      'waystone':dict(x=WAYSTONE[0],y=WAYSTONE[1],a=WAYSTONE[4]),'square':dict(x=64,y=50,r=8.2),
      'rects':[dict(name=rn,x0=r[0],y0=r[1],x1=r[2],y1=r[3]) for r,rn in RECTS],
      'walls':[dict(name=ln,pts=[list(q) for q in lp]) for lp,cl,ln in LINES],
      'destinations':[dict(name=nm,x=q[0],y=q[1]) for q,nm in DEST]}
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','godot','data','farhallow.json')
os.makedirs(os.path.dirname(out),exist_ok=True); json.dump(data,open(out,'w'),indent=1); print('wrote',os.path.relpath(out))
