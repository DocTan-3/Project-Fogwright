# Wayfolk building types, ground-floor plans (docs/peoples/wayfolk.md): the street is at the top of every plan.
#   python3 wayfolk_plans.py out.png
import sys
from PIL import Image,ImageDraw,ImageFont
F=lambda s,b=False: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf'%('-Bold' if b else ''),s)
S=20; PW=470; ROWS=[0,700]; PH=1100; img=Image.new('RGB',(PW*4,PH+70),(246,241,230)); d=ImageDraw.Draw(img)
WALL=(70,52,40); FLOOR={'room':(236,222,196),'shop':(226,206,170),'yard':(206,214,180),'garden':(172,200,140),'out':(214,200,176),'stone':(200,198,190),'hearth':(0,0,0)}
# each type: name, size note, [(x, y, w, h, label, kind)], doors [(x, y, 'h' or 'v')], hearths [(x, y)], extras
T=[("1  Street house","6 × 10 m house, 2-3 storeys, on a 6 × 26 m plot",
    [(0,0,6,5,'shop / workshop','shop'),(4.6,5,1.4,5,'','room'),(0,5,4.6,5,'kitchen','room'),
     (0,10,6,7,'yard','yard'),(0,17,3,3,'store','out'),(3,17,3,3,'privy,\nhens','out'),(0,20,6,6,'garden','garden')],
    [(2.5,0,'h'),(5.3,0,'h'),(5.3,10,'h'),(2.5,26,'h')],[(2.3,9.6)],"a side passage runs from the street door to the yard; upper floors: hall over the shop (jettied), bedrooms behind"),
   ("2  Cottage","6 × 8 m, one storey and a loft",
    [(0,0,6,6,'main room','room'),(3.6,3.4,2.4,2.6,'bed\nalcove','room'),(0,6,6,2,'lean-to store','out')],
    [(2,0,'h')],[(2.5,5.6)],"loft over the back half, by ladder; bench by the door"),
   ("3  Merchant's house","10 × 12 m, 3 storeys, walled garden behind",
    [(0,0,4,6,'counting\nroom','shop'),(6,0,4,6,'shop','shop'),(4,0,2,6,'hall','room'),(0,6,10,6,'\nkitchen and stores','room'),
     (10,0,4,12,'coach\nyard','yard'),(10,12,4,4,'stable','out'),(0,12,10,8,'walled garden','garden')],
    [(5,0,'h'),(12,0,'h'),(5,6,'h'),(3,12,'h'),(11,12,'h')],[(1.2,11.6)],"hall and parlour upstairs, bedrooms above; own well in the garden"),
   ("4  Inn","12 × 16 m round a yard",
    [(0,0,7,6,'taproom','room'),(7,0,2,6,'arch-\nway','yard'),(9,0,3,6,'bar,\ncellar','shop'),(0,6,4,6,'kitchen','room'),
     (4,6,8,6,'coach yard','yard'),(0,12,12,4,'stable','out')],
    [(3.5,0,'h'),(8,0,'h'),(4,9,'v'),(6,12,'h'),(10,12,'h'),(10.5,6,'h')],[(0.4,3),(2,11.6)],"archway from the street to the yard; guest rooms above and in a gallery round the yard"),
   ("5  Waylodge","8 × 12 m, beside the waystone",
    [(0,0,8,8,'common room\nbenches, long table','room'),(0,8,8,2,'bunks','room'),(0,10,4,2,"priest",'room'),(4,10,4,2,'store','out')],
    [(4,0,'h')],[(7.6,4)],"sleeping lofts over the bunks; the road lamp burns all night over the door"),
   ("6  Waystone shrine","stone 2.5 m tall on a stepped base",
    [(0,0,5,5,'','stone'),(1,1,3,3,'','stone')],[],[],"carved with the roads and their distances; lamp niche faces the main road; in towns under an open roof on four posts"),
   ("7  Workshop with yard","8 × 10 m (smithy, cooper, carpenter)",
    [(0,0,6,5,'open work\nbay: forge\nor bench','shop'),(0,5,6,5,'store','room'),(6,0,4,10,'yard: fuel,\nmaterials','yard')],
    [(3,0,'h'),(8,0,'h')],[(1.2,1.2)],"open to the street by day, shutters at night; smoky trades at the downwind end of town"),
   ("8  Farmstead","house, barn and byre round a yard",
    [(0,0,4,8,'house','room'),(4,0,4,8,'yard','yard'),(8,0,4,8,'byre','out'),(0,8,12,4,'barn','out')],
    [(6,0,'h'),(4,4,'v'),(8,4,'v'),(6,8,'h')],[(0.4,5)],"all doors face the yard; the yard gate faces the road")]
for k,(name,size,rooms,doors,hearths,note) in enumerate(T):
    ox,oy=(k%4)*PW+30,ROWS[k//4]+40
    d.text((ox,oy-28),name,font=F(22,True),fill=(40,30,24)); d.text((ox,oy-2),size,font=F(14),fill=(90,80,70))
    oy+=46
    xs=max(r[0]+r[2] for r in rooms); sc=S   # one scale for all, so sizes compare
    Q=lambda x,y:(ox+x*sc,oy+y*sc)
    d.rectangle([ox,oy-14,ox+xs*sc,oy-2],fill=(170,140,100)); d.text((ox+4,oy-14),'STREET',font=F(10,True),fill=(255,255,240))
    for x,y,w,h,lab,kind in rooms:
        d.rectangle([Q(x,y),Q(x+w,y+h)],fill=FLOOR[kind],outline=WALL,width=3 if kind not in('yard','garden') else 1)
        if lab: d.multiline_text(Q(x+w/2,y+h/2),lab,font=F(12),fill=(40,30,24),anchor='mm',align='center')
    for x,y,o in doors:
        a,b=(Q(x-0.5,y-0.15),Q(x+0.5,y+0.15)) if o=='h' else (Q(x-0.15,y-0.5),Q(x+0.15,y+0.5)); d.rectangle([a,b],fill=(250,246,236))
    for x,y in hearths:
        a,b=Q(x-0.4,y-0.4),Q(x+0.4,y+0.4); d.rectangle([a,b],fill=(190,80,40))
    if k==5:
        cx,cy=Q(2.5,2.5); d.ellipse([cx-10,cy-10,cx+10,cy+10],fill=(150,146,138),outline=WALL,width=2)
        d.rectangle([cx-4,oy-2,cx+4,cy-10],fill=(250,210,120))
    # wrap the note
    words=note.split(); line=''; ny=ROWS[k//4]+(630 if k<4 else 330)
    for w_ in words:
        if len(line+w_)>52: d.text((ox,ny),line,font=F(13),fill=(70,60,52)); ny+=17; line=''
        line+=w_+' '
    d.text((ox,ny),line,font=F(13),fill=(70,60,52))
for m in range(0,6): d.rectangle([30+m*2*S,PH+8,30+(m*2+1)*S,PH+14],fill=(70,52,40))
d.text((30+12*S,PH+2),'12 m',font=F(13),fill=(70,52,40))
d.text((30,PH+30),'WAYFOLK BUILDING TYPES · ground floors · street at the top · white gaps: doors · orange: hearths · 2 m kit grid',font=F(20,True),fill=(40,30,24))
img.save(sys.argv[1]); print('saved')
