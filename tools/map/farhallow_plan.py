# Farhallow's plan, top-down (north up, 1 px = 10 cm, 140 x 110 m): the village laid out for the prologue's beats.
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
def path(pts,w):
    d.line([P(x,y) for x,y in pts],fill=(170,140,100),width=int(w*S),joint='curve')
    for x,y in pts: d.ellipse([P(x-w/2,y-w/2),P(x+w/2,y+w/2)],fill=(170,140,100))
path([(62,0),(62,4),(60,14),(58,26),(60,40),(64,50)],4.2)                          # the road from the gate to the well
path([(64,50),(72,58),(80,66),(84,74),(86,80)],3.6)                                # down to the harbour
path([(64,50),(52,54),(40,58),(30,64)],3.0)                                         # west, to the tavern and cottages
path([(60,30),(48,30),(42,26)],2.4)                                                 # to the fields
path([(64,50),(78,44),(92,38),(100,30)],2.8)                                       # east, to the smithy and the shrine
path([(80,66),(70,72),(62,80)],2.2)
# the sea wall along the harbour, and a breakwater running out to the lighthouse
d.line([P(x,y) for x,y in [(80,82),(92,76),(100,70),(106,62)]],fill=(150,146,138),width=22)
d.line([P(x,y) for x,y in [(106,62),(116,64),(126,70),(132,80)]],fill=(150,146,138),width=26)
d.ellipse([P(129,77),P(136,84)],fill=(214,210,200),outline=(90,80,70),width=4)
d.text(P(126,86),'lighthouse',font=F(18,True),fill=(255,255,245),stroke_width=3,stroke_fill=(40,40,50))
for x,y in ((60,44),(73,40),(89,42)):     # stairs between terraces
    for k in range(4): d.line([P(x-1.5,y+k*0.8),P(x+1.5,y+k*0.8)],fill=(150,120,88),width=3)
# the dock: a T-shaped pier with boats; the last ship at its end
d.rectangle([P(85,80),P(90,100)],fill=(122,88,56)); d.rectangle([P(78,98),P(104,103)],fill=(122,88,56))
d.rectangle([P(104,96),P(108,104)],fill=(122,88,56))
def boat(x,y,l,w,a,c=(140,98,62)):
    pts=[(-l/2,0),(-l/2+1,-w/2),(l/2-l*0.25,-w/2),(l/2,0),(l/2-l*0.25,w/2),(-l/2+1,w/2)]
    ca,sa=math.cos(a),math.sin(a); d.polygon([P(x+u*ca-v*sa,y+u*sa+v*ca) for u,v in pts],fill=c,outline=(60,40,26))
boat(96,92,8,2.8,-0.3); boat(76,94,6,2.2,0.4); boat(120,100,16,5,0.05,(110,76,50))   # the last ship
d.line([P(116,100),P(124,100)],fill=(230,225,210),width=3)
# buildings: (x, y, w, h, angle, fill, label number)
B=[(30,62,14,10,-0.12,(150,104,70),1),(46,70,7,6,0.25,(160,118,80),2),(36,78,6,6,-0.3,(160,118,80),3),(72,63,6,5,0.5,(160,118,80),4),
   (74,72,6,5,-0.4,(150,120,90),5),(92,64,8,6,0.35,(150,120,90),6),(52,40,7,7,-0.15,(160,118,80),7),(70,36,6,6,0.2,(160,118,80),8),
   (96,34,9,7,0.15,(110,96,90),9),(104,22,5,5,-0.1,(200,196,186),10),(44,12,7,5,0.05,(150,110,76),11),(58,62,3,3,0,(120,100,80),0),
   (30,48,4,4,0.3,(140,110,80),12),
   (56,46,5,5,0.1,(166,120,82),13),(70,45,5,6,-0.25,(166,120,82),14),(56,57,5,4,0.6,(158,114,78),15),(78,52,5,5,0.4,(158,114,78),16),
   (84,58,4,5,0.5,(150,112,80),17),(62,68,5,4,-0.5,(158,114,78),18),(66,26,5,5,0.1,(166,120,82),19),(52,24,5,6,-0.2,(158,114,78),20)]
for x,y,w,h,a,c,n in B:
    pts=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]; ca,sa=math.cos(a),math.sin(a)
    poly=[P(x+u*ca-v*sa,y+u*sa+v*ca) for u,v in pts]
    d.polygon([(px+6,py+6) for px,py in poly],fill=(60,80,48))
    d.polygon(poly,fill=c,outline=(60,40,26)); d.line([poly[0],poly[1]],fill=(90,60,40),width=2)
    if n: d.text(P(x,y),str(n),font=F(26,True),fill=(255,250,235),anchor='mm',stroke_width=3,stroke_fill=(40,30,20))
d.ellipse([P(62.5,48.5),P(65.5,51.5)],fill=(130,150,170),outline=(70,70,70),width=3)       # the well
for x,y in ((68,54),(55,52),(66,46)): d.rectangle([P(x-0.7,y-0.5),P(x+0.7,y+0.5)],fill=(140,100,60))  # clutter by the well
for x,y in ((82,86),(88,76),(78,80)): d.line([P(x-2,y),P(x+2,y)],fill=(110,80,50),width=5)          # fish drying racks
d.rectangle([P(85,44),P(88,46)],fill=(120,86,52))                                              # the woodpile
# markers for the prologue's beats
def beat(x,y,t):
    d.ellipse([P(x-1.6,y-1.6),P(x+1.6,y+1.6)],fill=(200,60,50),outline=(255,255,255),width=3)
    d.text(P(x+2.3,y-1.2),t,font=F(19,True),fill=(255,255,255),stroke_width=3,stroke_fill=(60,20,20))
beat(66,52,'A  start'); beat(87,48,'B  first weapon'); beat(40,24,'C  first fight'); beat(62,6,'D  the gate falls'); beat(48,66,'E  the neighbour'); beat(110,103,'F  the last ship')
d.text(P(124,80),'THE SEA',font=F(30,True),fill=(220,235,240)); d.text(P(118,28),'WOODS',font=F(24,True),fill=(200,220,190))
d.text(P(58,1.5),'road north',font=F(18),fill=(255,255,240),stroke_width=2,stroke_fill=(40,30,20))
L=Image.new('RGBA',(430,1000),(250,246,236,240)); ld=ImageDraw.Draw(L)
names=['1  The Gull & Lantern, the tavern','2  Cottage','3  Cottage','4  Net-mender\'s house','5  Fish store','6  Harbour master\'s house','7  Cottage',
       '8  Cottage','9  Smithy (woodpile, tools)','10 Shrine of Merrith, on the rise','11 Granary by the gate','12 Hen house',
       '13-20  Houses packed along the paths','        (the plaza is round the well)','',
       'A  you begin at the well','B  a hatchet at the woodpile,','    a blade above the smithy door','C  a Fog-warped wolf by the field',
       'D  something huge breaks the gate','E  the half-changed neighbour','F  the last ship at the pier\'s end']
for k,t in enumerate(names): ld.text((14,12+k*30),t,font=F(19,k>=16 and t!=''),fill=(30,28,26) if k<16 else (140,40,30))
img.paste(L,(MW+20,20),L)
d.text((20,H-44),'FARHALLOW · plan v2 (north up · 140 m × 110 m · the ground rises to the north-east)',font=F(28,True),fill=(255,255,250),stroke_width=4,stroke_fill=(30,30,30))
img.save(sys.argv[1]); print('saved')
