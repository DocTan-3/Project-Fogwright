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
d.rectangle([P(14,14),P(42,34)],fill=(196,170,88),outline=(110,80,50),width=4)
for k in range(15,34,2): d.line([P(15,k),P(41,k)],fill=(176,150,72),width=2)
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
       ([(64,50),(76,46),(90,40),(100,32),(105,24)],2.8,'rise road')]
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
LANES=[([(80,66),(72,71),(64,77),(55,82),(46,86)],2.2,'shore lane'),
       ([(58.3,28),(50,28),(42,27)],2.2,'field lane'),
       ([(46,60),(40,52),(37,45)],2.0,'farm lane')]
for pts,w,_ in LANES:
    for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
        L=math.hypot(x1-x0,y1-y0); n=int(L/2)
        for k in range(0,n,2): d.line([P(x0+(x1-x0)*k/n,y0+(y1-y0)*k/n),P(x0+(x1-x0)*(k+1)/n,y0+(y1-y0)*(k+1)/n)],fill=(170,140,100),width=int(w*S*0.6))
STREETS={nm:(pts,w) for pts,w,nm in ROADS+LANES}
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
# (street, rough x, rough y, w, h, gap, colour, number, name); street None = placed by hand (x, y, angle) facing a yard
B=[('gate road',52,36,12,8,1.5,PUB,1,'The Gull & Lantern, tavern with rooms'),
   ('rise road',99,40,9,7,5.5,RICH,2,"Harbour master's house"),
   ('rise road',82,38,9,7,5.5,RICH,3,'Dunmore house (fish merchants)'),
   (None,107.3,20.3,5,5,-2.58,(200,196,186),4,'Shrine of Merrith, on the rise'),
   ('harbour road',87,57,10,7,1.5,TRADE,5,'Smithy: forge, furnace, charcoal'),
   (None,92,67,6,5,0.9,TRADE,6,'Smokehouse'),
   ('harbour road',80,75,9,6,1.0,TRADE,7,'Salt house and fish store'),
   (None,72,84,8,5,-0.58,TRADE,8,"Boatwright's shed"),
   ('shore lane',72,68,6,5,1.0,POOR,9,"Net-mender's house"),
   ('shore lane',63,74,5,4,0.6,POOR,10,"Fishers' cottages"),('shore lane',54,79,5,4,0.6,POOR,10,''),('shore lane',45,83,5,4,0.6,POOR,10,''),
   ('shore lane',68,77,5,4,0.6,POOR,10,''),('shore lane',60,83,5,4,0.6,POOR,10,''),('shore lane',52,87,5,4,0.6,POOR,10,''),
   ('gate road',52,13,8,5,1.0,TRADE,11,'Granary, by the gate and fields'),
   ('gate road',66,11,4,4,1.0,PUB,12,'Guard post and bell'),
   ('farm lane',44,52,6,5,1.0,MID,13,'Farming cottages'),('west road',34,58,6,5,1.0,MID,13,''),('west road',42,69,6,5,1.0,MID,13,''),
   (None,34,42,4,3,0.2,MID,14,'Hen house and goat pen'),
   ('west road',52,62,5,5,1.0,MID,15,'Old core houses along the roads'),('rise road',82,47,5,5,1.0,MID,15,''),
   ('gate road',65,27,5,5,1.0,MID,15,''),('field lane',46,24,5,6,1.0,MID,15,''),
   ('gate road',54,22,5,5,1.0,MID,15,'')]
def corners(x,y,w,h,a):
    ca,sa=math.cos(a),math.sin(a); return [(x+u*ca-v*sa,y+u*sa+v*ca) for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
def overlap(A,Bq,pad=0.5):   # separating axis test, with a little elbow room
    for poly in (A,Bq):
        for i in range(4):
            x0,y0=poly[i]; x1,y1=poly[(i+1)%4]; nx,ny=y0-y1,x1-x0; L=math.hypot(nx,ny); nx/=L; ny/=L
            pa=[px*nx+py*ny for px,py in A]; pb=[px*nx+py*ny for px,py in Bq]
            if max(pa)+pad<=min(pb) or max(pb)+pad<=min(pa): return False
    return True
placed=[]
for st,x,y,w,h,g,c,n,name in B:
    if st: x,y,a=front(st,x,y,w,h,g); door=True
    else: a=g; door=False
    placed.append((x,y,w,h,a,c,n,name,st))
blocks=list(placed)   # the well-off houses' walled front gardens count as part of them
for k,(x,y,w,h,a,c,n,_,st) in enumerate(placed):
    if c==RICH:
        ca,sa=math.cos(a),math.sin(a); blocks[k]=(x+1.25*sa,y-1.25*ca,w+6,h+6.5,a,c,n,_,st)
# the smithy's yard, behind the smithy (away from the road): furnace, quench trough, charcoal heap, woodpile
sm=[b_ for b_ in placed if b_[6]==5][0]; _sx,_sy,_sw,_sh,_sa=sm[:5]
def yard(u,v): ca,sa=math.cos(_sa),math.sin(_sa); return (_sx+u*ca-v*sa,_sy+u*sa+v*ca)
YARD=[('furnace',)+yard(2.2,_sh/2+2.2)+(2.6,2.6,_sa),('quench trough',)+yard(-0.8,_sh/2+1.6)+(2.6,1.0,_sa),
      ('charcoal heap',)+yard(-3.8,_sh/2+2.4)+(2.4,2.4,_sa),('woodpile',)+yard(_sw/2+1.8,0)+(1.6,4.0,_sa)]
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
RECTS=[((14,14,42,34),'field'),((16,38,30,46),'vegetable plots'),((85,80,90,100),'pier'),((78,98,104,103),'pier')]
SHORE_OK={6,7,8}   # the smokehouse and the boatwright's shed belong on the shore
things=[(b_[6],'%d'%b_[6],b_[:5]) for b_ in blocks]+[(5,t[0],t[1:6]) for t in YARD]
problems=[]
for i,(n,nm,geo) in enumerate(things):
    pts=outline(*geo)
    for j in range(i+1,len(things)):
        if things[j][0]==n and (nm.isdigit() or things[j][1].isdigit()): continue    # the smithy and its own yard
        if overlap(corners(*geo),corners(*things[j][2]),0.4): problems.append('%s overlaps %s'%(nm,things[j][1]))
    for lp,rw,ln in ROADS+LANES:
        if any(segd(q,p0,p1)<rw/2+0.3 for q in pts for p0,p1 in zip(lp,lp[1:])): problems.append('%s on the %s'%(nm,ln))
    if any(math.hypot(q[0]-64,q[1]-50)<8.3 for q in pts): problems.append('%s in the square'%nm)
    for lp,cl,ln in LINES:
        if any(segd(q,p0,p1)<cl for q in pts for p0,p1 in zip(lp,lp[1:])): problems.append('%s against the %s'%(nm,ln))
    for r,rn in RECTS:
        if any(rect_hit(q,r,0.8) for q in pts): problems.append('%s on the %s'%(nm,rn))
    if any(inside(q,coast) for q in pts): problems.append('%s in the sea'%nm)
    elif n not in SHORE_OK and any(inside(q,beach+[(140,110),(52,110)]) for q in pts): problems.append('%s on the beach'%nm)
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
for x,y,w,h,a,c,n,_,st in placed:
    poly=[P(*q) for q in corners(x,y,w,h,a)]
    d.polygon([(px+6,py+6) for px,py in poly],fill=(60,80,48)); d.polygon(poly,fill=c,outline=(60,40,26))
    if st or n==4:   # the door in the middle of the front (local -y), facing the street
        ca,sa=math.cos(a),math.sin(a); dx,dy=x+(h/2)*sa,y-(h/2)*ca
        d.rectangle([P(dx-0.8,dy-0.8),P(dx+0.8,dy+0.8)],fill=(250,240,200),outline=(60,40,26))
    d.text(P(x,y),str(n),font=F(24,True),fill=(255,250,235),anchor='mm',stroke_width=3,stroke_fill=(40,30,20))
# walled gardens of the well-off, in front of the house down to the road, with a gate
for x,y,w,h,a,c,n,_,st in placed:
    if c!=RICH: continue
    ca,sa=math.cos(a),math.sin(a); R=lambda u,v:(x+u*ca-v*sa,y+u*sa+v*ca)
    wall=[R(-1.4,-h/2-4.5),R(-w/2-3,-h/2-4.5),R(-w/2-3,h/2+2),R(w/2+3,h/2+2),R(w/2+3,-h/2-4.5),R(1.4,-h/2-4.5)]
    d.line([P(*q) for q in wall],fill=(170,164,150),width=6)
    wx,wy=R(w/2+1.5,h/2+0.5); d.ellipse([P(wx-1,wy-1),P(wx+1,wy+1)],fill=(130,150,170),outline=(80,80,80),width=2)   # own well
for nm,x,y,w,h,a in YARD:   # the smithy's yard
    poly=[P(*q) for q in corners(x,y,w,h,a)]
    col={'furnace':(90,70,60),'quench trough':(100,130,150),'charcoal heap':(40,36,34),'woodpile':(120,86,52)}[nm]
    d.polygon(poly,fill=col,outline=(40,30,26))
fx,fy=YARD[0][1:3]
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
beat(67,54,'A  start'); beat(96,52,'B  first weapon'); beat(26,37,'C  first fight'); beat(62,6,'D  the gate falls'); beat(60,70,'E  the neighbour'); beat(110,103,'F  the last ship')
d.text(P(124,88),'THE SEA',font=F(30,True),fill=(220,235,240)); d.text(P(114,44),'WOODS',font=F(24,True),fill=(200,220,190))
L=Image.new('RGBA',(440,1060),(250,246,236,240)); ld=ImageDraw.Draw(L); yy=12
for x,y,w,h,a,c,n,name,_ in placed:
    if not name: continue
    ld.rectangle((14,yy+3,32,yy+21),fill=c,outline=(60,40,26)); ld.text((40,yy),'%d  %s'%(n,name),font=F(17),fill=(30,28,26)); yy+=27
yy+=8
for t in ('□ door, on the front, facing its street','yellow: well-off · purple: poor','grey rings: smoke blowing downwind','smithy yard: furnace, quench trough,','    charcoal heap, woodpile','',
          'A  you begin at the well','B  hatchet at the smithy woodpile,','    the blade above the smithy door','C  a Fog-warped wolf by the field',
          'D  something huge breaks the gate','E  the half-changed Vey son','F  the last ship at the pier\'s end','',
          'Dashed: lanes, only to show which way','the houses off the main roads face;','paths are drawn properly in stage 4.'):
    ld.text((14,yy),t,font=F(17,t[:1] in 'ABCDEF' and t[1:2]==' '),fill=(30,28,26) if t[:1] not in 'ABCDEF' or t[1:2]!=' ' else (140,40,30)); yy+=25
for at,label in ZLABELS: d.text(P(*at),label,font=F(20,True),fill=(255,255,245),stroke_width=3,stroke_fill=(40,30,20))
img.paste(L,(MW+15,15),L)
d.text((20,H-44),'FARHALLOW · plan v3: building layout (north up · 140 m × 110 m · ground rises to the north-east)',font=F(26,True),fill=(255,255,250),stroke_width=4,stroke_fill=(30,30,30))
img.save(sys.argv[1]); print('saved')
