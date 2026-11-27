# Wayfolk building types, ground-floor plans (docs/peoples/wayfolk.md): the street is at the top of every plan.
# Every room must be reachable from outside through doors; the script checks it and prints any problem.
#   python3 wayfolk_plans.py out.png
import sys
from PIL import Image,ImageDraw,ImageFont
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
S=20; PW=470; ROWS=[0,700]; PH=1100
img=Image.new('RGB',(PW*4,PH+70),(246,241,230)); d=ImageDraw.Draw(img)
WALL=(70,52,40); GLASS=(110,160,200)
FLOOR={'room':(236,222,196),'shop':(226,206,170),'yard':(206,214,180),'garden':(172,200,140),'out':(214,200,176),'stone':(200,198,190)}
# rooms: (x, y, w, h, label, kind) in metres, street along y=0
# doors: (x, y, 'h'|'v', width, kind) - kind 'd' a door, 'g' a gate or archway, 'o' open (no wall), 's' shop front
# hearths: (x, y); stairs: (x, y, w, h, 'stairs'|'ladder'); windows: (x, y, 'h'|'v', length)
T=[dict(name="1  Street house",size="6 × 10 m house, 2-3 storeys, on a 6 × 26 m plot",
    rooms=[(0,0,4.6,5,'shop /\nworkshop','shop'),(4.6,0,1.4,10,'','room'),(0,5,4.6,5,'kitchen','room'),
           (0,10,6,7,'yard','yard'),(0,17,2.5,3,'store','out'),(2.5,17,1,3,'','yard'),(3.5,17,2.5,3,'privy,\nhens','out'),(0,20,6,6,'garden','garden')],
    doors=[(5.3,0,'h',1,'d'),(4.6,2.5,'v',1,'d'),(4.6,7.6,'v',1,'d'),(5.3,10,'h',1,'d'),(2.4,10,'h',1,'d'),
           (1.25,17,'h',1,'d'),(4.75,17,'h',1,'d'),(3,17,'h',1,'o'),(3,20,'h',1,'o'),(3,26,'h',1,'g')],
    hearths=[(2.3,5)],stairs=[(0.1,5.6,1.1,2.6,'stairs')],
    windows=[(2.3,0,'h',3.2),(3.9,10,'h',1.0)],
    note="street door into the side passage to the yard; the shop and kitchen open off it; stairs in the kitchen to the hall over the shop (jettied) and bedrooms behind; back-to-back hearth for shop and kitchen"),
   dict(name="2  Cottage",size="6 × 8 m, one storey and a loft",
    rooms=[(0,0,6,6,'main room','room'),(3.6,3.4,2.4,2.6,'bed\nalcove','room'),(0,6,6,2,'lean-to store','out')],
    doors=[(1.6,0,'h',1,'d'),(3.6,4.7,'v',1.6,'o'),(5,8,'h',1,'d')],
    hearths=[(2.4,5.6)],stairs=[(0.2,4.2,0.8,1.6,'ladder')],
    windows=[(4.2,0,'h',1.4),(0,2.5,'v',1.2)],
    note="ladder to the loft over the back half; the lean-to opens to the back; bench by the front door"),
   dict(name="3  Merchant's house",size="10 × 12 m, 3 storeys, coach yard and walled garden",
    rooms=[(0,0,3.6,6,'counting\nroom','shop'),(3.6,0,2.8,6,'','room'),(6.4,0,3.6,6,'shop','shop'),(0,6,10,6,'kitchen and stores','room'),
           (10,0,4,12,'coach\nyard','yard'),(10,12,4,4,'stable','out'),(0,12,10,8,'walled garden','garden')],
    doors=[(4.6,0,'h',1.2,'d'),(3.6,2,'v',1,'d'),(6.4,5.4,'v',0.9,'d'),(8.4,0,'h',1,'d'),(4.4,6,'h',1,'d'),(10,9,'v',1,'d'),
           (12,0,'h',2.6,'g'),(12,12,'h',1.6,'d'),(3,12,'h',1,'d')],
    hearths=[(0,9),(0,4.2)],stairs=[(5.2,1.0,1.1,3.2,'stairs')],
    windows=[(1.8,0,'h',1.4),(8.4,0,'h',0),(9.3,0,'h',1),(7,12,'h',2),(0,1.6,'v',1.2)],
    note="front door into the stair hall between counting room and shop; hall and parlour upstairs, bedrooms above; coach gate to the yard; own well in the garden"),
   dict(name="4  Inn",size="12 × 16 m round a coach yard",
    rooms=[(0,0,7,6,'taproom\n(bar counter)','room'),(7,0,2,6,'arch-\nway','yard'),(9,0,3,6,'cellar\nstore','shop'),(0,6,4,6,'kitchen','room'),
           (4,6,8,6,'coach yard','yard'),(0,12,12,4,'stable','out')],
    doors=[(3.5,0,'h',1.2,'d'),(8,0,'h',2,'g'),(8,6,'h',2,'o'),(9,3,'v',1,'d'),(7,4.4,'v',1,'d'),(2,6,'h',1,'d'),(4,9,'v',1,'d'),
           (6,12,'h',1.6,'d'),(10,12,'h',1.6,'d')],
    hearths=[(0,3),(2,12)],stairs=[(5,0.3,1.8,2.2,'stairs'),(10.2,6.2,1.6,2.6,'stairs')],
    windows=[(1.6,0,'h',1.6),(5.6,0,'h',0),(10.5,0,'h',1),(0,8.5,'v',1)],
    note="stairs from the taproom and from the yard gallery up to the guest rooms; the archway takes coaches to the yard and stable"),
   dict(name="5  Waylodge",size="8 × 12 m, beside the waystone",
    rooms=[(0,0,8,8,'common room\nbenches, long table','room'),(0,8,8,2,'bunks','room'),(0,10,4,2,"priest",'room'),(4,10,4,2,'store','out')],
    doors=[(4,0,'h',1.2,'d'),(4,8,'h',2,'o'),(2,10,'h',1,'d'),(6,10,'h',1,'d'),(8,11,'v',1,'d')],
    hearths=[(8,4)],stairs=[(7,8.1,0.8,1.8,'ladder')],
    windows=[(1.6,0,'h',1.4),(6.4,0,'h',1.4),(0,4,'v',1.6)],
    note="ladder to the sleeping lofts over the bunks; the road lamp burns all night over the street door; store door to the back"),
   dict(name="6  Waystone shrine",size="stone 2.5 m tall on a stepped base",
    rooms=[(0,0,5,5,'','stone')],doors=[(2.5,0,'h',3,'o')],hearths=[],stairs=[],windows=[],
    note="carved with the roads and their distances; the lamp niche faces the main road; in towns under an open roof on four posts"),
   dict(name="7  Workshop with yard",size="8 × 10 m (smithy, cooper, carpenter)",
    rooms=[(0,0,6,5,'open work bay:\nforge or bench','shop'),(0,5,6,5,'store','room'),(6,0,4,10,'yard: fuel,\nmaterials','yard')],
    doors=[(3,0,'h',4.4,'s'),(6,2.5,'v',1,'d'),(3,5,'h',1,'d'),(6,7.5,'v',1,'d'),(8,0,'h',2.4,'g')],
    hearths=[(0,1.2)],stairs=[],windows=[(0,7.5,'v',1.2)],
    note="the whole front of the work bay opens to the street by day, shuttered at night; smoky trades at the downwind end of town"),
   dict(name="8  Farmstead",size="house, byre and barn round a yard",
    rooms=[(0,0,4,8,'house','room'),(4,0,4,8,'yard','yard'),(8,0,4,8,'byre','out'),(0,8,12,4,'barn','out')],
    doors=[(6,0,'h',2.4,'g'),(4,4,'v',1,'d'),(8,4,'v',1.6,'d'),(6,8,'h',2.4,'d')],
    hearths=[(0,5)],stairs=[(0.2,0.3,0.8,1.6,'ladder')],windows=[(2,0,'h',1.4),(0,2.5,'v',1)],
    note="all doors face the yard; the yard gate faces the road; ladder to the loft")]
def on_edge(r,x,y,o):   # the door lies on this room's wall?
    rx,ry,rw,rh=r[:4]; e=0.05
    if o=='h': return abs(y-ry)<e and rx-e<=x<=rx+rw+e or abs(y-ry-rh)<e and rx-e<=x<=rx+rw+e
    return abs(x-rx)<e and ry-e<=y<=ry+rh+e or abs(x-rx-rw)<e and ry-e<=y<=ry+rh+e
problems=[]
for t in T:   # every room reachable from outside, every door between two rooms or a room and outside
    rooms=t['rooms']; links={i:set() for i in range(len(rooms))}; links['out']=set()
    W_=max(r[0]+r[2] for r in rooms); H_=max(r[1]+r[3] for r in rooms)
    for x,y,o,w,k in t['doors']:
        hit=[i for i,r in enumerate(rooms) if on_edge(r,x,y,o)]
        outer=(o=='h' and (abs(y)<0.05 or abs(y-H_)<0.05)) or (o=='v' and (abs(x)<0.05 or abs(x-W_)<0.05))
        if len(hit)==1:   # a room set inside another (an alcove): the door opens into the room around it
            hit+=[i for i,r in enumerate(rooms) if i not in hit and r[0]+0.05<x<r[0]+r[2]-0.05 and r[1]+0.05<y<r[1]+r[3]-0.05]
        ends=hit+(['out'] if outer and len(hit)==1 else [])
        if len(ends)!=2: problems.append('%s: door at (%s,%s) does not join two spaces %s'%(t['name'],x,y,ends)); continue
        a,b=ends; links[a].add(b); links[b].add(a)
    seen={'out'}; todo=['out']
    while todo:
        for n in links[todo.pop()]:
            if n not in seen: seen.add(n); todo.append(n)
    for i,r in enumerate(rooms):
        if i not in seen: problems.append('%s: %s cannot be reached'%(t['name'],(r[4] or 'room %d'%i).replace('\n',' ')))
for t in T:   # stairs and ladders must leave a way past them and keep clear of doors
    for x,y,w,h,_ in t['stairs']:
        r=[r for r in t['rooms'] if r[0]-0.01<=x and x+w<=r[0]+r[2]+0.01 and r[1]-0.01<=y and y+h<=r[1]+r[3]+0.01]
        if not r: problems.append('%s: stairs at (%s,%s) are not inside one room'%(t['name'],x,y)); continue
        r=min(r,key=lambda q:q[2]*q[3])
        if r[2]-w<0.9 and r[3]-h<0.9 or (r[2]-w<0.9 and h>r[3]*0.3) or (r[3]-h<0.9 and w>r[2]*0.3):
            problems.append('%s: stairs at (%s,%s) block the %s'%(t['name'],x,y,(r[4] or 'passage').replace('\n',' ')))
        for dx,dy,o,dw,k in t['doors']:
            if x-0.7<dx<x+w+0.7 and y-0.7<dy<y+h+0.7: problems.append('%s: stairs at (%s,%s) crowd the door at (%s,%s)'%(t['name'],x,y,dx,dy))
print('\n'.join(problems) or 'every room reachable, no stairs in the way')
for k,t in enumerate(T):
    ox,oy=(k%4)*PW+30,ROWS[k//4]+40
    d.text((ox,oy-28),t['name'],font=F(22,True),fill=(40,30,24)); d.text((ox,oy-2),t['size'],font=F(14),fill=(90,80,70))
    oy+=46; rooms=t['rooms']; xs=max(r[0]+r[2] for r in rooms)
    Q=lambda x,y:(ox+x*S,oy+y*S)
    d.rectangle([ox,oy-14,ox+xs*S,oy-2],fill=(170,140,100)); d.text((ox+4,oy-14),'STREET',font=F(10,True),fill=(255,255,240))
    for x,y,w,h,lab,kind in rooms:
        d.rectangle([Q(x,y),Q(x+w,y+h)],fill=FLOOR[kind],outline=WALL,width=3 if kind not in('yard','garden') else 1)
    for x,y,w,h,kind in t['stairs']:
        d.rectangle([Q(x,y),Q(x+w,y+h)],fill=(206,190,160),outline=WALL,width=1)
        n=int(h/0.3) if kind=='stairs' else int(h/0.4)
        for i in range(1,n): d.line([Q(x,y+h*i/n),Q(x+w,y+h*i/n)],fill=WALL,width=1)
        if kind=='stairs': d.line([Q(x+w/2,y+h-0.2),Q(x+w/2,y+0.3)],fill=(150,60,40),width=2)
    for x,y,o,L in t['windows']:
        if not L: continue
        a,b=(Q(x-L/2,y-0.1),Q(x+L/2,y+0.1)) if o=='h' else (Q(x-0.1,y-L/2),Q(x+0.1,y+L/2))
        d.rectangle([a,b],fill=GLASS)
    for x,y,o,w,kind in t['doors']:
        a,b=(Q(x-w/2,y-0.16),Q(x+w/2,y+0.16)) if o=='h' else (Q(x-0.16,y-w/2),Q(x+0.16,y+w/2))
        if kind=='o': continue
        d.rectangle([a,b],fill={'d':(250,246,236),'g':(250,246,236),'s':(250,230,170)}[kind])
        if kind=='d':   # the door leaf, swung open
            if o=='h': d.line([Q(x-w/2,y),Q(x-w/2,y+w*0.8)],fill=WALL,width=2)
            else: d.line([Q(x,y-w/2),Q(x+w*0.8,y-w/2)],fill=WALL,width=2)
    for x,y in t['hearths']:
        d.rectangle([Q(x-0.45,y-0.45),Q(x+0.45,y+0.45)],fill=(190,80,40))
    for x,y,w,h,lab,kind in rooms:
        if lab: d.multiline_text(Q(x+w/2,y+h/2),lab,font=F(12),fill=(40,30,24),anchor='mm',align='center')
    if k==5:
        cx,cy=Q(2.5,2.5)
        for st in (2.2,1.6): d.rectangle([Q(2.5-st,2.5-st),Q(2.5+st,2.5+st)],outline=WALL,width=2)
        d.ellipse([cx-11,cy-11,cx+11,cy+11],fill=(150,146,138),outline=WALL,width=2)
        d.rectangle([cx-5,cy-11,cx+5,cy-4],fill=(250,210,120))
    if k==2:   # the well in the garden
        cx,cy=Q(8.6,18.6); d.ellipse([cx-9,cy-9,cx+9,cy+9],fill=(130,150,170),outline=WALL,width=2)
    words=t['note'].split(); line=''; ny=ROWS[k//4]+(630 if k<4 else 330)
    for w_ in words:
        if len(line+w_)>52: d.text((ox,ny),line,font=F(13),fill=(70,60,52)); ny+=17; line=''
        line+=w_+' '
    d.text((ox,ny),line,font=F(13),fill=(70,60,52))
for m in range(0,6): d.rectangle([30+m*2*S,PH+8,30+(m*2+1)*S,PH+14],fill=WALL)
d.text((30+12*S,PH+2),'12 m',font=F(13),fill=WALL)
d.text((30,PH+30),'WAYFOLK BUILDING TYPES · ground floors · street at the top · doors (with leaf), gates, blue: windows, orange: hearths, hatched: stairs and ladders',font=F(18,True),fill=(40,30,24))
img.save(sys.argv[1]); print('saved')
