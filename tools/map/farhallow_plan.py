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
# woods around the clearing
for _ in range(520):
    x=rng.uniform(0,140); y=rng.uniform(0,110)
    cx,cy=62,50
    if ((x-cx)/52)**2+((y-cy)/40)**2<1 or (x>50 and y>78) or (x>95 and y>48): continue
    r=rng.uniform(1.6,3.2); d.ellipse([P(x-r,y-r),P(x+r,y+r)],fill=rng.choice([(48,84,46),(58,96,52),(42,74,42)]))
# fields in the north-west, fenced
d.rectangle([P(14,14),P(42,34)],fill=(196,170,88),outline=(110,80,50),width=4)
for k in range(15,34,2): d.line([P(15,k),P(41,k)],fill=(176,150,72),width=2)
d.rectangle([P(16,38),P(30,46)],fill=(120,100,64),outline=(110,80,50),width=3)   # vegetable plots
for k in range(17,30,3): d.line([P(k,39),P(k,45)],fill=(90,130,70),width=5)
# the palisade with the north gate, the road in from the north
pal=[(10,8),(40,6),(56,4)]; pal2=[(68,4),(92,8),(112,18),(118,40)]
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
def zone(poly,c,label,at):
    z=Image.new('RGBA',img.size,(0,0,0,0)); ImageDraw.Draw(z).polygon([P(x,y) for x,y in poly],fill=c)
    img.paste(Image.alpha_composite(img.convert('RGBA'),z).convert('RGB')); 
    ImageDraw.Draw(img).text(P(*at),label,font=F(20,True),fill=(255,255,245),stroke_width=3,stroke_fill=(40,30,20))
zone([(68,28),(80,20),(98,10),(112,14),(110,30),(96,40),(84,44),(68,44)],(255,215,120,70),'WELL-OFF (upwind, uphill)',(71,12.5))
zone([(48,66),(62,62),(80,62),(100,64),(100,74),(86,84),(74,88),(60,92),(46,84)],(70,60,90,70),'POOR (downwind, by the shore)',(32,88))
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
# walled gardens of the well-off
for x,y,w,h,a in ((92,23,17,13,0.12),(78,35,16,13,-0.2)):
    ca,sa=math.cos(a),math.sin(a); pts=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2),(-w/2,-h/2)]
    d.line([P(x+u*ca-v*sa,y+u*sa+v*ca) for u,v in pts],fill=(170,164,150),width=6)
    d.ellipse([P(x-w/2+1.2+0.5,y+h/2-3.2),P(x-w/2+3.2+0.5,y+h/2-1.2)],fill=(130,150,170),outline=(80,80,80),width=2)   # own well
RICH,MID,POOR,TRADE,PUB=(214,170,108),(166,122,84),(124,100,80),(112,100,96),(150,96,64)
# (x, y, w, h, angle, colour, number, name)
B=[(51,46,12,8,-0.08,PUB,1,'The Gull & Lantern, tavern with rooms'),
   (92,23,9,7,0.12,RICH,2,"Harbour master's house"),
   (78,35,9,7,-0.2,RICH,3,'Dunmore house (fish merchants)'),
   (107,20,5,5,-0.1,(200,196,186),4,'Shrine of Merrith, on the rise'),
   (86,57,10,7,0.62,TRADE,5,'Smithy: forge, furnace, charcoal'),
   (95,70,6,5,0.9,TRADE,6,'Smokehouse'),
   (79,76,9,6,0.45,TRADE,7,'Salt house and fish store'),
   (69,85,8,5,0.55,TRADE,8,"Boatwright's shed"),
   (72,73,6,5,-0.4,POOR,9,"Net-mender's house"),
   (66,67,5,4,-0.5,POOR,10,"Fishers' cottages"),(60,74,5,4,0.3,POOR,10,''),(55,81,5,4,-0.2,POOR,10,''),
   (70,81,5,4,0.7,POOR,10,''),(77,67,5,4,0.8,POOR,10,''),(50,74,5,4,-0.1,POOR,10,''),
   (48,12,8,5,0.05,TRADE,11,'Granary, by the gate and fields'),
   (66,11,4,4,0.1,PUB,12,'Guard post and bell'),
   (38,50,6,5,-0.2,MID,13,'Farming cottages'),(30,57,6,5,0.3,MID,13,''),(42,69,6,5,-0.1,MID,13,''),
   (34,42,4,3,0.2,MID,14,'Hen house and goat pen'),
   (56,61,5,5,0.5,MID,15,'Old core houses round the square'),(66,40,5,6,-0.25,MID,15,''),(76,52,5,5,0.75,MID,15,''),
   (53,35,6,5,-0.15,MID,15,''),(66,28,5,5,0.1,MID,15,''),(52,24,5,6,-0.2,MID,15,'')]
road_pts=[pts for pts,_,_ in ROADS]
def near_road(p):
    best=1e9
    for pts in road_pts:
        for a,b in zip(pts,pts[1:]): best=min(best,segd(p,a,b))
    return min(best,max(0,math.hypot(p[0]-64,p[1]-50)-8))
for x,y,w,h,a,c,n,_ in B:
    ca,sa=math.cos(a),math.sin(a); R=lambda u,v:(x+u*ca-v*sa,y+u*sa+v*ca)
    poly=[P(*R(u,v)) for u,v in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]]
    d.polygon([(px+6,py+6) for px,py in poly],fill=(60,80,48)); d.polygon(poly,fill=c,outline=(60,40,26))
    # the door on the side facing the nearest road (the smokehouse, sheds and hen house face their yard instead)
    sides=[(0,-h/2),(w/2,0),(0,h/2),(-w/2,0)]; m=min(sides,key=lambda s:near_road(R(*s)))
    dx,dy=R(*m); d.rectangle([P(dx-0.8,dy-0.8),P(dx+0.8,dy+0.8)],fill=(250,240,200),outline=(60,40,26))
    d.text(P(x,y),str(n),font=F(24,True),fill=(255,250,235),anchor='mm',stroke_width=3,stroke_fill=(40,30,20))
# the smithy's yard: furnace, quench trough, charcoal heap, woodpile
d.ellipse([P(91.5,60),P(94.5,63)],fill=(90,70,60),outline=(40,30,26),width=3); d.text(P(95,60.5),'furnace',font=F(15,True),fill=(255,255,240),stroke_width=2,stroke_fill=(40,30,20))
d.rectangle([P(88,63.4),P(91,64.6)],fill=(100,130,150)); d.ellipse([P(78.5,61),P(81,63.5)],fill=(40,36,34)); d.rectangle([P(90,50.5),P(94,52.5)],fill=(120,86,52))
# smoke drifting downwind
for sx,sy in ((92,57),(95,70)):
    for k in range(5): d.ellipse([P(sx+k*2.6-1.2-0.3*k,sy+k*2.4-1.2-0.3*k),P(sx+k*2.6+1.2+0.3*k,sy+k*2.4+1.2+0.3*k)],outline=(200,200,200),width=2)
# wind rose
cx,cy=128,14; d.ellipse([P(cx-9,cy-9),P(cx+9,cy+9)],fill=(240,236,226),outline=(90,80,70),width=3)
d.line([P(cx-6,cy-6),P(cx+5,cy+5)],fill=(60,90,140),width=8); d.polygon([P(cx+7,cy+7),P(cx+2,cy+5.5),P(cx+5.5,cy+2)],fill=(60,90,140))
d.text(P(cx,cy-7.5),'N',font=F(18,True),fill=(40,30,20),anchor='mm'); d.text(P(cx-9,cy+11),'wind from the north-west',font=F(16,True),fill=(255,255,245),stroke_width=2,stroke_fill=(30,30,30))
def beat(x,y,t):
    d.ellipse([P(x-1.6,y-1.6),P(x+1.6,y+1.6)],fill=(200,60,50),outline=(255,255,255),width=3)
    d.text(P(x+2.3,y-1.2),t,font=F(19,True),fill=(255,255,255),stroke_width=3,stroke_fill=(60,20,20))
beat(61,56,'A  start'); beat(90,54,'B  first weapon'); beat(26,37,'C  first fight'); beat(62,6,'D  the gate falls'); beat(60,70,'E  the neighbour'); beat(110,103,'F  the last ship')
d.text(P(124,88),'THE SEA',font=F(30,True),fill=(220,235,240)); d.text(P(114,44),'WOODS',font=F(24,True),fill=(200,220,190))
L=Image.new('RGBA',(440,1060),(250,246,236,240)); ld=ImageDraw.Draw(L); yy=12
for x,y,w,h,a,c,n,name in B:
    if not name: continue
    ld.rectangle((14,yy+3,32,yy+21),fill=c,outline=(60,40,26)); ld.text((40,yy),'%d  %s'%(n,name),font=F(17),fill=(30,28,26)); yy+=27
yy+=8
for t in ('□ door, facing the road it opens onto','yellow: well-off · purple: poor','grey rings: smoke blowing downwind','',
          'A  you begin at the well','B  hatchet at the smithy woodpile,','    the blade above the smithy door','C  a Fog-warped wolf by the field',
          'D  something huge breaks the gate','E  the half-changed Vey son','F  the last ship at the pier\'s end','',
          'Main roads only; lanes are stage 4.'):
    ld.text((14,yy),t,font=F(17,t[:1] in 'ABCDEF' and t[1:2]==' '),fill=(30,28,26) if t[:1] not in 'ABCDEF' or t[1:2]!=' ' else (140,40,30)); yy+=25
img.paste(L,(MW+15,15),L)
d.text((20,H-44),'FARHALLOW · plan v3: building layout (north up · 140 m × 110 m · ground rises to the north-east)',font=F(26,True),fill=(255,255,250),stroke_width=4,stroke_fill=(30,30,30))
img.save(sys.argv[1]); print('saved')
