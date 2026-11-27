# Building types, ground-floor plans, drawn from building_types.py (docs/peoples/wayfolk.md): street at the top.
# Every room must be reachable from outside through doors; the script checks it and prints any problem.
#   python3 wayfolk_plans.py out.png
import sys
from PIL import Image,ImageDraw,ImageFont
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
S=20; PW=470

WALL=(70,52,40); GLASS=(110,160,200)
FLOOR={'room':(236,222,196),'shop':(226,206,170),'yard':(206,214,180),'garden':(172,200,140),'out':(214,200,176),'stone':(200,198,190)}
from building_types import T as TYPES
# every type from building_types.py, its plot drawn at full depth with typical outbuildings
T=[]
for key,ty in TYPES.items():
    T.append(dict(ty,key=key,name='%d  %s'%(len(T)+1,ty['name']),rooms=ty['rooms']+ty['plot_rooms'],doors=ty['doors']+ty['plot_doors']))
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
ROWS=[]; y=0
for r in range(0,len(T),4):
    ROWS.append(y); y+=int(max(max(q[1]+q[3] for q in t['rooms']) for t in T[r:r+4])*S)+190
PH=y; img=Image.new('RGB',(PW*4,PH+70),(246,241,230)); d=ImageDraw.Draw(img)
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
    if t['key'].startswith('waystone'):
        c_=rooms[0][2]/2; cx,cy=Q(c_,c_)
        for st in (c_-0.3,c_-0.9): d.rectangle([Q(c_-st,c_-st),Q(c_+st,c_+st)],outline=WALL,width=2)
        d.ellipse([cx-11,cy-11,cx+11,cy+11],fill=(150,146,138),outline=WALL,width=2)
        d.rectangle([cx-5,cy-11,cx+5,cy-4],fill=(250,210,120))
    if t['key']=='merchant_house':   # the well in the garden
        cx,cy=Q(8.6,18.6); d.ellipse([cx-9,cy-9,cx+9,cy+9],fill=(130,150,170),outline=WALL,width=2)
    words=t['note'].split(); line=''; ny=oy+max(q[1]+q[3] for q in rooms)*S+14
    for w_ in words:
        if len(line+w_)>52: d.text((ox,ny),line,font=F(13),fill=(70,60,52)); ny+=17; line=''
        line+=w_+' '
    d.text((ox,ny),line,font=F(13),fill=(70,60,52))
for m in range(0,6): d.rectangle([30+m*2*S,PH+8,30+(m*2+1)*S,PH+14],fill=WALL)
d.text((30+12*S,PH+2),'12 m',font=F(13),fill=WALL)
d.text((30,PH+30),'BUILDING TYPES · ground floors · street at the top · doors with leaf, gates · blue: windows · orange: hearths · hatched: stairs',font=F(18,True),fill=(40,30,24))
img.save(sys.argv[1]); print('saved')
