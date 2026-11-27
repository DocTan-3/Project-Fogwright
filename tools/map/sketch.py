# A sketch of Fogwright's world from the lore (docs/lore.md): continents and isles like World of Warcraft's, Aldrath at the
# heart of the main continent, the hometowns of each people around it, life and colour fading with distance from Aldrath,
# and the Sundering at the edges.   python3 sketch.py out.png      (1 px = 10 m; the world is 20 km across)
import math,random,sys
from PIL import Image,ImageDraw,ImageFont,ImageFilter
N=2000; K=N/20.0
def P(x,y): return (N/2+x*K, N/2-y*K)
def noise1(a,seed,oct=5):
    r=random.Random(seed); s=0;amp=1
    for o in range(oct):
        f=2**o; ph=r.uniform(0,6.28); s+=amp*(math.sin(a*f+ph)+0.6*math.sin(a*f*1.9+ph*1.7)); amp*=0.55
    return s
def land(cx,cy,rx,ry,seed,rough=0.16,rot=0.0,n=220):
    pts=[]
    for i in range(n):
        a=2*math.pi*i/n; k=1+rough*noise1(a,seed)
        x=rx*k*math.cos(a); y=ry*k*math.sin(a); c,s=math.cos(rot),math.sin(rot)
        pts.append((cx+x*c-y*s,cy+x*s+y*c))
    return pts
LANDS=[  # (polygon, base colour)
 (land(-0.6,0.4,4.6,3.6,3,0.15),(118,150,92)),            # the main continent: Aldrath's heartland, the Redwold in its west
 (land(1.6,6.6,5.4,1.9,11,0.17,0.08),(150,163,150)),       # the northern continent: the Rimeholds
 (land(-0.4,-6.6,5.6,2.2,21,0.15,-0.06),(205,180,128)),    # the southern continent: the Sere
 (land(6.6,0.9,1.3,1.0,31),(132,168,96)),(land(7.4,-1.4,0.8,0.65,32),(132,168,96)),(land(5.9,-0.9,0.45,0.4,33),(132,168,96)),
 (land(-7.4,-0.2,1.3,1.1,41),(96,86,80)),(land(-7.0,2.2,0.7,0.55,42),(96,86,80)),(land(-8.3,1.3,0.45,0.4,43),(96,86,80)),
]
img=Image.new('RGB',(N,N)); px=img.load()
for j in range(N):
    for i in range(N):
        x=(i-N/2)/K; y=(N/2-j)/K; t=min(1,max(0,(math.hypot(x,y)-3)/6))
        px[i,j]=(int(70-40*t),int(130-70*t),int(150-70*t))
d=ImageDraw.Draw(img)
for poly,fill in LANDS: d.polygon([P(x,y) for x,y in poly],fill=fill)
# the bay that brings the sea up to Hollin's Cross, two kilometres south of Aldrath
d.polygon([P(x,y) for x,y in [(-0.7,-3.6),(-0.35,-2.7),(-0.15,-2.05),(0.25,-1.85),(0.55,-2.2),(0.7,-2.9),(1.1,-3.8)]],fill=(64,122,142))
rs=random.Random(5)
def dots(n,area,col,size):
    for _ in range(n):
        x,y=area(); q=rs.uniform(*size); d.ellipse([P(x-q,y+q),P(x+q,y-q)],fill=col if not isinstance(col,list) else rs.choice(col))
dots(330,lambda:(rs.uniform(-4.4,-2.0),rs.uniform(-1.6,2.8)),[(62,100,58),(54,90,52),(72,110,64)],(0.07,0.16))   # the Redwold
dots(240,lambda:(rs.uniform(-2.6,6.2),rs.uniform(7.1,8.2)),(226,230,234),(0.08,0.2))                               # snow on the north
for x in [0.4+0.55*k for k in range(9)]:                                                                              # the northern spine
    y=6.3+0.25*math.sin(x*2); d.polygon([P(x-0.24,y-0.13),P(x,y+0.3),P(x+0.24,y-0.13)],fill=(110,104,98),outline=(70,66,62))
for (x,y) in ((-7.4,-0.1),(-7.0,2.3)):                                                                                 # Slag Isles volcanoes
    d.polygon([P(x-0.35,y-0.2),P(x,y+0.4),P(x+0.35,y-0.2)],fill=(70,52,46)); d.ellipse([P(x-0.08,y+0.45),P(x+0.08,y+0.3)],fill=(230,90,40))
for k in range(16):                                                                                                    # the Sere's dunes
    x=rs.uniform(-5,4.5); y=rs.uniform(-8,-5.6); d.arc([P(x-0.3,y+0.1),P(x+0.3,y-0.15)],200,340,fill=(176,150,100),width=3)
rv=(90,150,190)
d.line([P(0.2,3.4),P(0.0,1.5),P(0.1,0.3),P(0.05,-1.0),P(0.05,-1.9)],fill=rv,width=6)        # Aldrath's river, down to the bay
d.line([P(-3.6,2.6),P(-3.2,1.0),P(-3.9,-0.6),P(-4.6,-1.6)],fill=rv,width=5)                  # through the Redwold
d.line([P(6.0,0.7),P(6.6,1.0),P(7.6,1.3)],fill=rv,width=5)                                   # Solmere's river
for x0 in (1.0,3.2,5.0): d.line([P(x0,6.2),P(x0+0.2,5.2)],fill=rv,width=4)
# life fades with distance from Aldrath: the land greys toward the edges (the lore's Fog, and the palettes' mute)
fog=Image.new('L',(N,N),0); fp=fog.load()
for j in range(0,N,2):
    for i in range(0,N,2):
        x=(i-N/2)/K; y=(N/2-j)/K; v=int(255*min(1,max(0,(math.hypot(x,y)-2.5)/7.5))**1.6*0.55)
        fp[i,j]=v; fp[min(N-1,i+1),j]=v; fp[i,min(N-1,j+1)]=v; fp[min(N-1,i+1),min(N-1,j+1)]=v
grey=img.convert('L').convert('RGB'); img=Image.composite(grey,img,fog)
fog2=Image.new('L',(N,N),0); fp=fog2.load()
for j in range(N):
    for i in range(N):
        x=(i-N/2)/K; y=(N/2-j)/K; fp[i,j]=int(255*min(1,max(0,(math.hypot(x,y)-8.2)/1.9))**1.2)
img=Image.composite(Image.new('RGB',(N,N),(196,200,206)),img,fog2.filter(ImageFilter.GaussianBlur(8)))
d=ImageDraw.Draw(img)
port=(0.1,-1.95)
for to in ((-6.2,0.0),(6.0,0.4),(1.5,4.9),(-0.6,-4.8),(5.6,-1.2)):
    x0,y0=port; x1,y1=to; L=math.hypot(x1-x0,y1-y0); n=int(L/0.18)
    for k in range(0,n,2):
        a=k/n; b=(k+1)/n; d.line([P(x0+(x1-x0)*a,y0+(y1-y0)*a),P(x0+(x1-x0)*b,y0+(y1-y0)*b)],fill=(240,236,220),width=3)
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
def city(x,y,name,sub='',size=11,col=(250,230,150)):
    cx,cy=P(x,y); r=size
    d.rectangle([cx-r,cy-r,cx+r,cy+r],fill=col,outline=(40,30,20),width=3); d.ellipse([cx-4,cy-4,cx+4,cy+4],fill=(120,60,200))
    d.text((cx+r+6,cy-20),name,font=F(30 if size<20 else 40,True),fill=(25,20,18),stroke_width=4,stroke_fill=(245,240,228))
    if sub: d.text((cx+r+6,cy+(14 if size<20 else 24)),sub,font=F(21),fill=(35,30,28),stroke_width=3,stroke_fill=(245,240,228))
def mark(x,y,name,col,shape='o'):
    cx,cy=P(x,y)
    if shape=='o': d.ellipse([cx-8,cy-8,cx+8,cy+8],fill=col,outline=(30,30,30),width=2)
    else: d.polygon([(cx,cy-11),(cx+10,cy+8),(cx-10,cy+8)],fill=col,outline=(30,30,30))
    if name: d.text((cx+13,cy-12),name,font=F(21),fill=(25,22,20),stroke_width=3,stroke_fill=(245,240,228))
def region(x,y,name,sz=40):
    cx,cy=P(x,y); d.text((cx,cy),name,font=F(sz,True),fill=(255,255,250),stroke_width=5,stroke_fill=(40,40,44),anchor='mm')
region(0.9,2.4,"ALDRATH'S HEARTLAND",34); region(-3.0,3.2,'THE REDWOLD',34); region(1.6,8.0,'THE RIMEHOLDS'); region(-0.4,-7.9,'THE SERE')
region(6.8,2.6,'AURELAN ISLES',32); region(-7.3,3.4,'SLAG ISLES',32); region(-6.4,8.4,'THE SUNDERING',30); region(6.6,-8.4,'THE SUNDERING',30)
city(0.1,0.0,'Aldrath','the greatest city · all peoples',size=22)
mark(0.05,-1.0,'Starting village',(255,255,255))
city(0.1,-1.95,"Hollin's Cross",'starter port · Wayfolk · thriving',col=(240,200,120))
city(-3.4,0.4,'Dun Brannoch','Ruadhan · struggling',size=9)
city(2.4,6.2,'Skarvhold','Hrimfolk · enduring',size=9)
city(6.5,0.6,'Solmere','Aurelans · declining',size=9)
city(-7.2,-0.6,'Ashforge','Ferrin · thriving',size=9)
city(0.6,-6.0,'Qaraseth','Zarhim · holding',size=9)
city(4.2,8.1,'The Last Bastion','Lantern Vigil · besieged',size=9,col=(200,200,230))
mark(-5.6,-5.4,'Forsaken landing',(120,30,40),'^')
mark(1.8,6.6,'Animari ruins',(160,160,175),'^')
for (x,y) in ((-2.6,1.6),(6.9,-1.3),(-2.8,-6.2),(1.6,1.0),(4.6,6.3)): mark(x,y,'',(80,170,90))
for (x,y) in ((-1.6,-7.2),(-7.8,1.5),(5.4,7.1),(-1.2,2.6)): mark(x,y,'',(150,120,200),'^')
mark(2.6,-9.0,'Shattered capital?',(40,40,40),'^')
L=Image.new('RGBA',(600,380),(250,246,236,235)); ld=ImageDraw.Draw(L)
items=[('big','Aldrath: by far the biggest city',(250,230,150)),('square',"A people's hometown (its god, a warp)",(250,230,150)),('dot',"Verdane's grove",(80,170,90)),('tri',"Vael's ruins (broken warps)",(150,120,200)),('dash','Ship routes from the starter port',(120,110,90)),('grey','Colour and life fade from Aldrath',(150,150,150)),('fog','The Sundering: the Fog thickens',(196,200,206))]
for k,(kind,t,c) in enumerate(items):
    y=20+k*50
    if kind=='big': ld.rectangle([16,y-2,44,y+26],fill=c,outline=(40,30,20),width=2)
    elif kind=='square': ld.rectangle([22,y+4,38,y+20],fill=c,outline=(40,30,20),width=2)
    elif kind=='dot': ld.ellipse([22,y+3,38,y+19],fill=c)
    elif kind=='tri': ld.polygon([(30,y),(41,y+20),(19,y+20)],fill=c)
    elif kind=='dash': [ld.line([(16+k2*10,y+11),(21+k2*10,y+11)],fill=c,width=3) for k2 in range(3)]
    elif kind=='grey': [ld.rectangle([16+k2*7,y+2,22+k2*7,y+22],fill=(int(118+k2*8),int(150-k2*3),int(92+k2*10))) for k2 in range(4)]
    else: ld.rectangle([18,y,44,y+22],fill=c)
    ld.text((60,y),t,font=F(23),fill=(30,28,26))
img.paste(L,(30,N-410),L)
x0,y0=N-330,N-70; d.line([(x0,y0),(x0+5*K,y0)],fill=(255,255,255),width=6); d.text((x0,y0-40),'5 km',font=F(28,True),fill=(255,255,255),stroke_width=3,stroke_fill=(30,30,30))
d.text((30,24),'FOGWRIGHT · world sketch v2 (from the lore; not final)',font=F(36,True),fill=(255,255,255),stroke_width=4,stroke_fill=(30,30,34))
d.text((30,72),'20 km across · Aldrath at the heart · life fades with distance from it',font=F(24),fill=(245,245,240),stroke_width=3,stroke_fill=(30,30,34))
img.save(sys.argv[1]); print('saved')
