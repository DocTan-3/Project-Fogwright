# A first sketch of Fogwright's world, from the lore (docs/lore.md): Aldrath's central land in the middle, the inner sea,
# the shards of Erde around it (inner coasts torn cliffs that fit together, outer coasts gentle), the Sundering beyond.
#   python3 sketch.py out.png      (1 px = 10 m; the world is 20 km across)
import math,random,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
N=2000; K=N/20.0                      # pixels per km; centre at (N/2,N/2); +y is north
def P(x,y): return (N/2+x*K, N/2-y*K)
rnd=random.Random(7)
def noise1(a,seed,oct=4):
    r=random.Random(seed); s=0;amp=1
    for o in range(oct):
        f=2**(o+1); ph=r.uniform(0,6.28); s+=amp*math.sin(a*f+ph)*0.5+amp*0.5*math.sin(a*f*1.7+ph*2); amp*=0.5
    return s
def shard(a0,a1,r_in,r_out,seed,wobble=0.35):
    """an annular sector of land: inner edge (facing the centre) jagged, outer edge smooth and wavy"""
    pts=[]; n=120
    for i in range(n+1):
        a=a0+(a1-a0)*i/n; r=r_out+wobble*noise1(a*3,seed); pts.append((r*math.cos(a),r*math.sin(a)))
    for i in range(n+1):
        a=a1-(a1-a0)*i/n; r=r_in+0.18*noise1(a*9,seed+1,5)+0.12*math.sin(a*41+seed); pts.append((r*math.cos(a),r*math.sin(a)))
    return pts
def blob(cx,cy,r,seed,n=80,w=0.25):
    return [(cx+(r+w*noise1(2*math.pi*i/n*2,seed))*math.cos(2*math.pi*i/n),cy+(r+w*noise1(2*math.pi*i/n*2,seed))*math.sin(2*math.pi*i/n)) for i in range(n)]
D=math.radians
LANDS={   # name: (polygons, fill)
 'central':([blob(0,0,2.1,3,w=0.28)],(118,150,92)),
 'north':([shard(D(38),D(142),4.3,7.6,11)],(150,163,150)),
 'south':([shard(D(212),D(328),4.4,7.4,21)],(205,180,128)),
 'east':([blob(5.6,0.6,1.2,31),blob(6.6,-1.3,0.8,32),blob(4.9,-1.9,0.55,33),blob(7.3,1.6,0.5,34)],(132,168,96)),
 'west':([blob(-5.4,-0.4,1.3,41),blob(-6.7,1.4,0.75,42),blob(-4.6,1.9,0.5,43)],(96,86,80)),
}
img=Image.new('RGB',(N,N)); px=img.load()
for j in range(N):                     # the sea: calm teal near the centre, darker and stormier toward the Sundering
    for i in range(0,N):
        x=(i-N/2)/K; y=(N/2-j)/K; r=math.hypot(x,y); t=min(1,max(0,(r-3)/6))
        px[i,j]=(int(70-40*t),int(130-70*t),int(150-70*t))
d=ImageDraw.Draw(img)
for name,(polys,fill) in LANDS.items():
    for poly in polys: d.polygon([P(x,y) for x,y in poly],fill=fill)
# the north: colder (snow) toward its outer edge; the Redwold (its west) forest green; mountains along its spine
rs=random.Random(5)
for k in range(260):   # snow on the high, cold outer north
    aa=D(rs.uniform(45,135)); rr=rs.uniform(6.2,7.5)
    if math.degrees(aa)>100 and rr<6.9: continue
    x,y=rr*math.cos(aa),rr*math.sin(aa); q=rs.uniform(0.08,0.2)
    d.ellipse([P(x-q,y+q),P(x+q,y-q)],fill=(226,230,234))
for k in range(320):   # the Redwold's forests
    aa=D(rs.uniform(100,140)); rr=rs.uniform(4.7,6.6); x,y=rr*math.cos(aa),rr*math.sin(aa); q=rs.uniform(0.07,0.16)
    d.ellipse([P(x-q,y+q),P(x+q,y-q)],fill=rs.choice([(62,100,58),(54,90,52),(72,110,64)]))
def ridge(points,col=(110,104,98)):
    for (x,y) in points:
        d.polygon([P(x-0.22,y-0.12),P(x,y+0.28),P(x+0.22,y-0.12)],fill=col,outline=(70,66,62))
ridge([(5.4*math.cos(D(a)),5.4*math.sin(D(a))) for a in range(52,98,6)])          # the northern spine (Animari ruins)
ridge([(-5.2,-0.2),(-5.6,-0.6),(-6.6,1.5)],(70,52,46))                              # Slag Isles volcanoes
for (x,y) in ((-5.2,-0.2),(-6.6,1.5)): d.ellipse([P(x-0.07,y+0.33),P(x+0.07,y+0.2)],fill=(230,90,40))
for a in range(222,320,10):                                                         # the Sere's dunes
    aa=D(a); x,y=6.1*math.cos(aa),6.1*math.sin(aa); d.arc([P(x-0.3,y+0.1),P(x+0.3,y-0.15)],200,340,fill=(176,150,100),width=3)
# inner coasts of the shards are cliffs: a dark torn line
for a0,a1,ri,seed in ((38,142,4.3,11),(212,328,4.4,21)):
    pts=[]
    for i in range(121):
        a=D(a0)+(D(a1)-D(a0))*i/120; r=ri+0.18*noise1(a*9,seed+1,5)+0.12*math.sin(a*41+seed); pts.append(P(r*math.cos(a),r*math.sin(a)))
    d.line(pts,fill=(52,46,44),width=7)
# rivers: from the inner ridges to the outer coasts
for a in (60,80,118):
    aa=D(a); d.line([P(4.6*math.cos(aa),4.6*math.sin(aa)),P(5.6*math.cos(aa+0.03),5.6*math.sin(aa+0.03)),P(7.4*math.cos(aa-0.02),7.4*math.sin(aa-0.02))],fill=(90,150,190),width=5)
d.line([P(5.0,0.2),P(5.6,0.6),P(6.4,0.9)],fill=(90,150,190),width=5)                   # Solmere's river
d.line([P(-0.2,1.6),P(0.1,0.9),P(0.0,-0.4),P(0.15,-1.4),P(0.2,-2.1)],fill=(90,150,190),width=5)  # through the central land
# the Sundering: the Fog thickens toward the world's edge
fog=Image.new('L',(N,N),0); fp=fog.load()
for j in range(0,N):
    for i in range(0,N):
        x=(i-N/2)/K; y=(N/2-j)/K; r=math.hypot(x,y); fp[i,j]=int(255*min(1,max(0,(r-7.8)/2.0))**1.2)
fog=fog.filter(ImageFilter.GaussianBlur(8)); img=Image.composite(Image.new('RGB',(N,N),(196,200,206)),img,fog)
d=ImageDraw.Draw(img)
# ship routes: spokes across the inner sea from Hollin's Cross
port=(0.15,-1.9)
for to in ((0.0,4.5),(4.6,0.4),(-4.4,-0.3),(0.4,-4.6),(3.4,3.6)):
    x0,y0=port; x1,y1=to; L=math.hypot(x1-x0,y1-y0); n=int(L/0.18)
    for k in range(0,n,2):
        a=k/n; b=(k+1)/n; d.line([P(x0+(x1-x0)*a,y0+(y1-y0)*a),P(x0+(x1-x0)*b,y0+(y1-y0)*b)],fill=(240,236,220),width=3)
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
def city(x,y,name,sub='',god=True,col=(250,230,150)):
    cx,cy=P(x,y); r=11
    d.rectangle([cx-r,cy-r,cx+r,cy+r],fill=col,outline=(40,30,20),width=3)
    if god: d.ellipse([cx-4,cy-4,cx+4,cy+4],fill=(120,60,200))
    d.text((cx+16,cy-20),name,font=F(30,True),fill=(25,20,18),stroke_width=4,stroke_fill=(245,240,228))
    if sub: d.text((cx+16,cy+12),sub,font=F(21),fill=(35,30,28),stroke_width=3,stroke_fill=(245,240,228))
def mark(x,y,name,col,shape='o'):
    cx,cy=P(x,y)
    if shape=='o': d.ellipse([cx-8,cy-8,cx+8,cy+8],fill=col,outline=(30,30,30),width=2)
    else: d.polygon([(cx,cy-11),(cx+10,cy+8),(cx-10,cy+8)],fill=col,outline=(30,30,30))
    d.text((cx+13,cy-12),name,font=F(21),fill=(25,22,20),stroke_width=3,stroke_fill=(245,240,228))
def region(x,y,name):
    cx,cy=P(x,y); d.text((cx,cy),name,font=F(40,True),fill=(255,255,250),stroke_width=5,stroke_fill=(40,40,44),anchor='mm')
region(0,1.2,'ALDRATH'); region(-1.4*0+0.0,6.5,''); region(-0.4,6.9,'THE RIMEHOLDS'); region(-4.6,4.9,'THE REDWOLD')
region(0,-6.4,'THE SERE'); region(6.2,2.6,'AURELAN ISLES'); region(-6.0,2.9,'SLAG ISLES'); region(6.4,8.0,'THE SUNDERING'); region(0,-9.2,'THE SUNDERING')
city(0,0.5,'Aldrath','outer city · sealed inner city')
mark(0,-0.5,'Starting village',(255,255,255))
city(0.15,-1.9,"Hollin's Cross",'starter port · Wayfolk',col=(240,200,120))
city(1.6,6.0,'Skarvhold','fjord arch · Hrimfolk')
city(-4.0,4.2,'Dun Brannoch','hill fort · Ruadhan')
city(5.6,0.5,'Solmere','river crossing · Aurelans')
city(-5.0,-0.6,'Ashforge','volcano flank · Ferrin')
city(0.6,-5.7,'Qaraseth','oasis · Zarhim')
city(3.0,7.2,'The Last Bastion','Lantern Vigil · falls in the story',col=(200,200,230))
mark(-5.8,-4.4,'Forsaken landing',(120,30,40),'^')
mark(2.6,5.0,'Animari ruins (spine)',(160,160,175),'^')
for (x,y) in ((-2.8,5.6),(5.2,-1.6),(-3.6,-5.3),(1.0,1.4)): mark(x,y,'',(80,170,90))
for (x,y) in ((-1.8,-6.6),(-6.4,0.6),(4.0,5.6)): mark(x,y,'',(150,120,200),'^')
mark(-1.0,-8.6,'Shattered capital?',(40,40,40),'^')
# legend and scale
L=Image.new('RGBA',(560,330),(250,246,236,235)); ld=ImageDraw.Draw(L)
items=[('square','God\'s city (warp at its heart)',(250,230,150)),('dot','Verdane\'s grove',(80,170,90)),('tri','Vael\'s ruins (broken warps)',(150,120,200)),('line','Inner coast: torn cliffs',(52,46,44)),('dash','Ship routes from the starter port',(120,110,90)),('fog','The Sundering: the Fog thickens',(196,200,206))]
for k,(kind,t,c) in enumerate(items):
    y=22+k*48
    if kind=='square': ld.rectangle([20,y,42,y+22],fill=c,outline=(40,30,20),width=2)
    elif kind=='dot': ld.ellipse([22,y+2,40,y+20],fill=c)
    elif kind=='tri': ld.polygon([(31,y),(42,y+20),(20,y+20)],fill=c)
    elif kind=='line': ld.line([(16,y+11),(46,y+11)],fill=c,width=6)
    elif kind=='dash': [ld.line([(16+k2*10,y+11),(21+k2*10,y+11)],fill=c,width=3) for k2 in range(3)]
    else: ld.rectangle([18,y,44,y+22],fill=c)
    ld.text((60,y),t,font=F(23),fill=(30,28,26))
img.paste(L,(30,N-360),L)
x0,y0=N-330,N-70; d.line([(x0,y0),(x0+5*K,y0)],fill=(255,255,255),width=6); d.text((x0,y0-40),'5 km',font=F(28,True),fill=(255,255,255),stroke_width=3,stroke_fill=(30,30,30))
d.text((30,24),'FOGWRIGHT · world sketch v1 (from the lore; not final)',font=F(36,True),fill=(255,255,255),stroke_width=4,stroke_fill=(30,30,34))
d.text((30,72),'20 km across · Erde broken outward from Aldrath · the shards still fit together',font=F(24),fill=(245,245,240),stroke_width=3,stroke_fill=(30,30,34))
img.save(sys.argv[1]); print('saved',sys.argv[1])
