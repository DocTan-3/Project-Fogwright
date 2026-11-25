// Fogwright equipment: World of Warcraft-style gear on the painted bodies. Load after bodypaint.js.
// Painted armour: each slot is a paint layer, laid on in a fixed order, then the whole character (skin, face, underclothes and
// every layer) is baked into one texture in the body's texture layout (tools/blender/uvbody.py). Built armour: pieces cut
// from the body's own surface and pushed outward, so they carry its skin weights and every people and build shape.
'use strict';

/* ---------- 1. the slots, and the order their paint goes on ---------- */
// Paint layers, bottom to top. Built-only slots (shoulders, head, back) have no layer.
// Paint layers, inside out; each slot paints a region of its own shape (EQ_LAYER_SHAPE: 0/3 torso, 1 legs band, 2 feet, 4 wrists,
// 5 hands, 6 waist, 7 tabard). The wardrobe (shirt, lower, socks, shoes) is looks only; gear goes over it and carries stats.
const EQ_LAYERS=['shirt','lower','socks','shoes','legs','feet','chest','coat','wrists','hands','waist'];
const EQ_LAYER_SHAPE={shirt:0,lower:1,socks:1,shoes:2,legs:1,feet:2,chest:3,coat:3,wrists:4,hands:5,waist:6,tabard:7};
const EQ_SLOTS=[
  {id:'shirt',name:'Shirt',group:'Wardrobe'},{id:'lower',name:'Lower',group:'Wardrobe'},{id:'socks',name:'Socks',group:'Wardrobe'},{id:'shoes',name:'Shoes',group:'Wardrobe'},
  {id:'head',name:'Head',group:'Gear'},{id:'eyes',name:'Eyes',group:'Gear',soon:'Goggles, monocles and visors are coming'},{id:'mouth',name:'Mouth',group:'Gear',soon:'Respirators, Fog masks and scarves are coming'},{id:'shoulders',name:'Shoulders',group:'Gear'},
  {id:'chest',name:'Chest',group:'Gear'},{id:'coat',name:'Coat',group:'Gear'},{id:'wrists',name:'Wrists',group:'Gear'},{id:'hands',name:'Hands',group:'Gear'},
  {id:'waist',name:'Waist',group:'Gear'},{id:'legs',name:'Legs',group:'Gear'},{id:'feet',name:'Feet',group:'Gear'},{id:'back',name:'Back',group:'Gear'},
  {id:'mecharm',name:'Mechanical arm',group:'Gear',locked:'Unlocks in the gear and water era; always a pair, filling the shoulders, arms, wrists and hands (one or both arms look mechanical)'}];
const EQ_KIND={linen:0,wool:1,leather:2,studded:3,mail:4,plate:5,quilted:6,fur:7};
// The gear texture sheet (tools/textures/gearsheet.py): sixteen surfaces as greyscale detail, 4 x 4. A layer or built piece
// names one; each kind has its usual one, and items can choose another (velvet for a noble, hessian for the poor).
const EQ_MAT={linen:0,wool:1,herringbone:2,leather:3,pebbled:4,suede:5,fur:6,hessian:7,velvet:8,jacquard:9,quatrefoil:10,knit:11,steel:12,rusty:13,mail:14,check:15};
const EQ_KIND_MAT=[0,1,3,4,14,12,0,6];      // linen, wool, leather, studded, mail, plate, quilted, fur
// the metres one repeat of each tile covers
const EQ_MAT_SCALE=[0.14,0.2,0.22,0.3,0.25,0.2,0.3,0.22,0.22,0.3,0.2,0.18,0.4,0.35,0.11,0.32];
const EQ_GEAR=(()=>{const t=new THREE.TextureLoader().load((window.FOGWRIGHT_GEAR||'tex/gear.jpg'),()=>{EQ_GEAR_WAIT.splice(0).forEach(f=>f());});
  t.wrapS=t.wrapT=THREE.ClampToEdgeWrapping; t.anisotropy=4; return t;})();
const EQ_GEAR_WAIT=[];   // dressings made before the sheet arrived, redone once it has
const EQ_PATTERN={plain:0,stripes:1,check:2,hemband:3};

/* ---------- 2. the paint layers (GLSL, in the paint template's space: see bodypaint.js) ---------- */
const EQUIP_GLSL=`
uniform vec4 uQ[66];  // 11 layers x 6 (on = the layer's shape + 1): [kind, pattern, trim width, on] [a] [b; b.w = material tile] [main colour] [second colour] [trim colour]
uniform sampler2D uGear;
uniform float uMatScale[16];
uniform vec4 uWear;   // wear (faded, frayed, patched), dirt, a seed for where patches fall
float gearTile(float tile,vec2 uv){ // greyscale detail from the sheet (mean 0.5), uv in repeats; gradients taken before the wrap, so no seams
  vec2 o=vec2(mod(tile,4.),floor(tile/4.)),f=fract(uv)*0.2421875+0.00390625,t=vec2(o.x*0.25+f.x,1.-(o.y*0.25+f.y));
#if __VERSION__ >= 300
  vec2 g=uv*0.2421875; return textureGrad(uGear,t,dFdx(g),dFdy(g)).r;
#else
  return texture2D(uGear,t).r;
#endif
}
// the arm in the template: shoulder, elbow, wrist, fingertip (x across from the body's middle, z up)
const vec2 QA0=vec2(0.2,1.43), QA1=vec2(0.255,1.17), QA2=vec2(0.296,0.95), QA3=vec2(0.315,0.70);
float qSeg(vec2 q,vec2 a,vec2 b,out float d){vec2 ab=b-a;float t=clamp(dot(q-a,ab)/dot(ab,ab),0.,1.);d=length(q-a-ab*t);return t;}
float armT(vec3 p){ // 0 at the shoulder, 1 elbow, 2 wrist, 3 fingertips
  vec2 q=vec2(abs(p.x),p.z);float d0,d1,d2;float t0=qSeg(q,QA0,QA1,d0);float t1=qSeg(q,QA1,QA2,d1);float t2=qSeg(q,QA2,QA3,d2);
  float t=t0,d=d0;if(d1<d){d=d1;t=1.+t1;}if(d2<d){t=2.+t2;}return t;}
float legX(float z){return mix(0.125,0.09,smoothstep(0.08,0.92,z));}
vec2 qSurf(vec3 p,float arm,float t){ // a flat, roughly metre-scaled coordinate on the surface, for weaves, studs and rings
  if(arm>0.5){float ax=abs(p.x)-mix(mix(QA0.x,QA1.x,clamp(t,0.,1.)),mix(QA1.x,QA2.x,clamp(t-1.,0.,1.)),step(1.,t));return vec2(atan(p.y-0.03,ax)*0.04,-t*0.25);}
  if(p.z<0.92){float lx=abs(p.x)-legX(p.z);return vec2(atan(lx,-p.y)*0.065,p.z);}
  return vec2(atan(p.x,-p.y)*0.15,p.z);}
// signed distances, positive inside, in metres along the body
float qNeck(vec3 p,float style,float depth){ // the neckline's height
  // the base of the neck sits at 1.505 on the template (the shoulder tops at about 1.49): clothes come up to it
  float ax=abs(p.x),front=1.-smoothstep(-0.03,0.03,p.y),top=1.503;
  if(style<0.5)return top-(0.012+depth*0.3)*front*(1.-smoothstep(0.03,0.07,ax));         // crew
  if(style<1.5)return top-depth*front*(1.-clamp(ax/0.075,0.,1.));                          // v
  return top-depth*front*(1.-pow(clamp(ax/0.1,0.,1.),2.));}                                 // scoop
float qTorso(vec3 p,float hem,float style,float depth,float open){ // body garment: hem to neckline, an open front
  float d=min(p.z-hem,qNeck(p,style,depth)-p.z);
  if(open>0.){float fr=1.-smoothstep(-0.04,-0.01,p.y);d=min(d,mix(1.,abs(p.x)-open*(0.4+0.6*smoothstep(1.0,1.42,p.z)),fr));}
  return d;}
float qArmhole(vec3 p){return length(vec2(abs(p.x)-0.205,(p.z-1.39)*0.8))-0.075;}       // for sleeveless pieces
float gCut=1.;
float layerDist(int L,vec3 p,float arm,float t,vec4 a,vec4 b){
  gCut=1.;
  float ax=abs(p.x), body=1.-arm;
  if(L==0||L==3){ // shirt, chest: a = hem, sleeve (in arm units: 0 shoulder .. 2 wrist; below 0 sleeveless), neckline style, depth; b.x = open front
    float dt=qTorso(p,a.x,a.z,a.w,b.x);
    gCut=p.z<0.95?(abs(p.x)-0.03)*0.5-(0.95-p.z)*0.03:1.;   // below the crease, a panel on each thigh, open at the inner thigh, as WoW paints a tunic (no trim on that edge)
    float da=a.y<0.?(0.14-t)*0.25:(a.y-t)*0.25;     // sleeveless pieces still cover the shoulder, ending in a short cap where the arm begins
    return p.z>1.53?-1.:mix(dt,da,smoothstep(0.35,0.65,arm));}
  if(L==1){if(arm>0.5)return -1.;return min(p.z-a.x,a.y-p.z);}                          // legs: cuff height, waist height
  if(L==2){if(arm>0.5)return -1.;return a.x-p.z;}                                         // feet: top of the boot
  if(L==4){if(arm<0.5)return -1.;return min(t-a.x,a.y-t)*0.25;}                          // wrists: from, to (arm units)
  if(L==5){if(arm<0.5)return -1.;return (t-a.x)*0.25;}                                   // hands: cuff
  if(L==6){if(arm>0.5)return -1.;return a.y*0.5-abs(p.z-a.x);}                           // waist: centre, width
  if(L==7){if(arm>0.5||p.z>1.5)return -1.;return min(min(a.y-ax,p.z-a.x),qNeck(p,0.,0.)-0.006-p.z);} // tabard: hem, half width
  return -1.;}
vec3 metal(vec3 c,vec2 s){return c*(0.86+0.2*vnoise(s*vec2(40.,700.)));}
vec3 layerColour(float kind,float pat,float tile,vec3 p,vec2 s,float d,vec3 c1,vec3 c2,vec3 c3){
  vec3 c=c1; float n=vnoise(s*vec2(520.,190.)), g=2.*gearTile(tile,s/uMatScale[int(tile)]);
  if(pat>0.5&&pat<1.5)c=mix(c,c2,inside(abs(fract(s.x/0.03)-0.5)-0.18));                              // stripes
  else if(pat>1.5&&pat<2.5){float a=inside(abs(fract(s.x/0.05)-0.5)-0.12),b=inside(abs(fract(s.y/0.05)-0.5)-0.12);c=mix(c,c2,0.55*max(a,b)+0.35*a*b);} // woven check
  else if(pat>2.5)c=mix(c,c2,inside(abs(d-0.03)-0.008));                                               // a band along the hems
  if(kind<0.5)c*=g-0.05*vnoise(s*vec2(14.,5.));                                                         // linen
  else if(kind<1.5)c*=g*(0.96+0.06*vnoise(s*vec2(40.,12.)));                                           // wool
  else if(kind<3.5){                                                                                    // leather, studded
    c*=g; c*=mix(0.76,1.,smoothstep(0.,0.018,d));                                                        // darker towards its edges
    c=mix(c,c2*1.1,0.7*inside(abs(d-0.007)-0.0012)*step(0.45,fract((s.x+s.y)*90.)));                   // stitching along the edge
    if(kind>2.5){vec2 g=(fract(s/0.032)-0.5)*0.032;float st=inside(length(g)-0.0045);c=mix(c,metal(c3,s)*(1.15-0.5*smoothstep(0.,0.0045,length(g+0.0015))),st);}}
  else if(kind<4.5){c=metal(c1,s)*(0.22+1.05*gearTile(tile,s/uMatScale[int(tile)]));}             // mail, from the sheet
  else if(kind<5.5){float band=fract(s.y/0.075),e=min(band,1.-band)*0.075;                            // plate: lames with rivets
    c=c1*g*(0.9+0.25*smoothstep(0.012,0.,abs(band-0.85)*0.075))*mix(0.55,1.,smoothstep(0.,0.004,e));
    vec2 g=vec2(fract(s.x/0.045)-0.5,band-0.82);c=mix(c,metal(c3,s)*1.2,inside(length(g*vec2(0.045,0.075))-0.0035));
    c*=mix(1.18,1.,smoothstep(0.,0.01,d));}
  else if(kind<6.5){float q=abs(fract((s.x+s.y)/0.06)-0.5),r=abs(fract((s.x-s.y)/0.06)-0.5);          // quilted
    c*=g*(1.-0.22*inside(min(q,r)-0.04))*(0.96+0.06*smoothstep(0.,0.5,min(q,r)));}
  else{c*=g*(0.8+0.3*vnoise(s*vec2(150.,35.)));}                                                        // fur
  return c;}
vec3 applyEquip(vec3 c,vec3 p){
  float arm=1.-smoothstep(0.3,0.7,vTorso), t=armT(p); vec2 s=qSurf(p,arm,t);
  for(int L=0;L<11;L++){
    vec4 h=uQ[L*6]; if(h.w<0.5)continue;
    float d=layerDist(int(h.w+0.5)-1,p,arm,t,uQ[L*6+1],uQ[L*6+2]);
    c*=1.-0.22*smoothstep(-0.007,0.,d)*(1.-smoothstep(0.,0.0005,d));            // the layer's shadow on what lies under it
    float cov=inside(-d)*inside(-gCut); if(uWear.x>0.)cov*=step(uWear.x*0.009*vnoise(s*vec2(320.,45.)),d);   // worn hems fray
    if(cov<0.001)continue;
    vec3 lc=layerColour(h.x,h.y,uQ[L*6+2].w,p,s,d,uQ[L*6+3].rgb,uQ[L*6+4].rgb,uQ[L*6+5].rgb);
    if(uWear.x>0.){
      float knees=(1.-arm)*exp(-pow((abs(p.x)-legX(p.z))/0.05,2.)-pow((p.z-0.52)/0.05,2.)),elbows=arm*exp(-pow((t-1.)/0.16,2.));
      lc=mix(lc,lc*1.15+0.035,uWear.x*0.65*max(knees,elbows));                                   // faded where it rubs
      for(int k=0;k<2;k++){if(uWear.x<0.45)break;                                                // patches, stitched on
        vec2 c0=vec2(hsh(vec2(float(L)*7.+float(k),uWear.z))*0.8-0.4,0.3+hsh(vec2(float(L)+uWear.z,float(k)*3.+1.))*1.1);
        vec2 q=abs(s-c0)-vec2(0.034,0.028); float pd=max(q.x,q.y);
        if(pd<0.){lc=lc*vec3(0.84,0.8,0.74)+0.05;lc*=1.-0.35*inside(abs(pd+0.004)-0.0011)*step(0.5,fract((s.x+s.y)*110.));}}}
    if(h.z>0.)lc=mix(lc,(h.x>3.5&&h.x<5.5?metal(uQ[L*6+5].rgb,s):uQ[L*6+5].rgb*(0.9+0.1*vnoise(s*200.)))*mix(0.8,1.,smoothstep(0.,h.z,d)),inside(d-h.z)); // trim
    c=mix(c,lc,cov);}
  if(uWear.y>0.)c*=1.-uWear.y*(0.32*smoothstep(0.42,0.0,p.z)+0.16*smoothstep(0.55,0.8,vnoise(p.xz*16.+p.yz*9.)));   // dirt: the legs, and stains
  return c;}
`;

/* ---------- 3. the items ---------- */
// paint: the layer's kind, pattern, trim width (m), a and b (see layerDist), colours [main, second, trim]
// built: pieces made from the body (see section 5)
const EQ_ITEMS={
  lower:[
    {id:'trousers',dye:'second',name:'Wool trousers',paint:{kind:'wool',a:[0.07,1.01],dyes:['#5e5446','#4a4238','#3a3026']}},
    {id:'breeches',dye:'leather',name:'Leather breeches',paint:{kind:'leather',trim:0.008,a:[0.4,1.01],dyes:['#4e3826','#c8b48a','#2e2016']}},
    {id:'plaid',dye:'main',name:'Woven trews',paint:{kind:'wool',pattern:'check',a:[0.07,1.01],dyes:['#3e5a3a','#8a3a26','#2a2a20']}}],
  socks:[
    {id:'stockings',name:'Stockings',paint:{kind:'wool',mat:'knit',trim:0.006,a:[0.0,0.5],dyes:['#d8d0c0','#b8b0a0','#8a8070']}},
    {id:'argyle',name:'Argyle socks',paint:{kind:'wool',mat:'knit',pattern:'check',trim:0.006,a:[0.0,0.46],dyes:['#6a6e78','#a04a3a','#3a3e48']}},
    {id:'legwarmers',name:'Leg warmers',paint:{kind:'wool',mat:'knit',trim:0.01,a:[0.1,0.42],dyes:['#6a3a2a','#8a5a3a','#4a2a1a']}}],
  shoes:[
    {id:'shoes',name:'Shoes',paint:{kind:'leather',a:[0.075],dyes:['#3e2a1c','#a08a6a','#2a1c12']},built:[{type:'fitted',asset:'shoe'}]}],
  coat:[
    {id:'longcoat',dye:'leather',name:'Long coat',paint:{kind:'leather',trim:0.01,a:[0.97,1.86,1,0.07],b:[0.03],dyes:['#4a3424','#c8b48a','#2e2016']},
      built:[{type:'drape',asset:'longcoat',kind:1},{type:'collar',colour:0}]},
    {id:'greatcoat',dye:'main',name:'Greatcoat',paint:{kind:'wool',trim:0.012,a:[0.97,1.86,1,0.07],b:[0.03],dyes:['#1e1c20','#141216','#b08a48']},
      built:[{type:'drape',asset:'greatcoat'},{type:'collar',colour:0,high:1},{type:'buttons',xs:[-0.065,0.065],z0:1.05,z1:1.4}]},
    {id:'robe',dye:'main',name:'Wool robe',hides:['legs'],paint:{kind:'wool',pattern:'hemband',trim:0.012,a:[0.12,1.9,0,0.02],dyes:['#6a5a48','#a8844e','#4a3e30']},
      built:[{type:'skirt',top:1.0,hem:0.12,flare:0.35,kind:0},{type:'collar',colour:0}]},
    {id:'ilvaricoat',dye:'main',name:'Ilvari long coat',paint:{kind:'wool',trim:0.012,a:[0.5,1.9,0,0.0],b:[0.025],dyes:['#2a3040','#1a2030','#3a6ad0']},
      built:[{type:'skirt',top:1.0,hem:0.42,flare:0.22,open:0.3,kind:0,trim:1},{type:'collar',colour:0,high:1}]}],
  shirt:[
    {id:'linen_shirt',name:'Linen shirt',paint:{kind:'linen',a:[0.93,1.92,1,0.05],dyes:['#e2d9c6','#cdbfa4','#b8a888']}},
    {id:'tunic',dye:'main',name:'Short tunic',paint:{kind:'wool',pattern:'hemband',trim:0.012,a:[0.8,0.45,0,0.02],dyes:['#7a5a3a','#a8844e','#5a3e26']}}],
  chest:[
    {id:'jerkin',dye:'leather',name:'Leather jerkin',paint:{kind:'leather',trim:0.01,a:[0.86,-1,2,0.1],b:[0.022],dyes:['#6a4428','#d8c49a','#3e2818']},
      built:[{type:'laces'}]},
    {id:'gambeson',dye:'main',name:'Quilted gambeson',paint:{kind:'quilted',trim:0.014,a:[0.8,1.72,0,0.0],dyes:['#a89a7e','#8a7c62','#6a4e34']},
      built:[{type:'collar',colour:0}]},
    {id:'mail',dye:'trim',name:'Mail shirt',paint:{kind:'mail',trim:0.008,a:[0.84,1.25,0,0.02],dyes:['#9ea4aa','#6a6e72','#7a5a3a']}},
    {id:'doublet',people:'Aurelan',dye:'main',name:'Aurelan doublet',paint:{kind:'wool',pattern:'stripes',trim:0.01,a:[0.9,1.9,0,0.0],dyes:['#2e4a6a','#c9a046','#c9a046']},
      built:[{type:'collar',colour:0},{type:'buttons'}]},
    {id:'furjerkin',people:'Hrimfolk',dye:'leather',name:'Hrimfolk fur-collared jerkin',paint:{kind:'leather',trim:0.012,a:[0.86,-1,0,0.0],dyes:['#5a4030','#c8b48a','#3a2a1c']},
      built:[{type:'furcollar'}]},
    {id:'apron',people:'Ferrin',name:"Ferrin smith's apron",paint:{kind:'linen',a:[0.95,1.1,0,0.03],dyes:['#b8a888','#8a3a26','#c9a046']},
      built:[{type:'apron'}]},
    {id:'wraps',people:'Zarhim',dye:'main',name:'Zarhim desert wraps',paint:{kind:'linen',pattern:'hemband',trim:0.01,a:[0.86,1.95,1,0.06],dyes:['#d8c8a8','#a8783a','#7a5426']},
      built:[{type:'belt',thick:0.008,cloth:1,z:1.0,w:0.09,colour:1}]},
    {id:'cuirass',dye:'trim',name:'Steel breastplate',fills:['coat'],paint:{kind:'mail',trim:0.008,a:[0.95,1.25,0,0.02],dyes:['#9ea4aa','#6a6e72','#7a5a3a']},built:[{type:'cuirass',metal:'#a4aab0'}]},
    {id:'brigandine',dye:'main',name:'Studded brigandine',fills:['coat'],paint:{kind:'studded',trim:0.012,a:[0.88,-1,0,0.0],dyes:['#5a2e24','#c9a046','#c9a046']},
      built:[{type:'collar',colour:0}]}],
  legs:[
    {id:'reinforced',dye:'second',name:'Reinforced trousers',replaces:['lower'],paint:{kind:'leather',mat:'suede',trim:0.008,a:[0.07,1.01],dyes:['#5a4a3a','#3e3226','#2e2218']}},
    {id:'chaps',dye:'leather',name:'Leather chaps',paint:{kind:'leather',trim:0.01,a:[0.3,0.99],dyes:['#6a4428','#c8b48a','#3e2818']}},
    {id:'platelegs',dye:'second',name:'Steel leg harness',paint:{kind:'wool',a:[0.07,1.01],dyes:['#4a4238','#3a3026','#2a2018']},built:[{type:'legplates',metal:'#9aa0a6'}],legPad:0.024},
    {id:'leathergreaves',dye:'leather',name:'Leather greaves',paint:{kind:'leather',trim:0.008,a:[0.07,1.01],dyes:['#4e3826','#c8b48a','#2e2016']},built:[{type:'legplates',greavesOnly:1,leather:'#5a3a22'}],legPad:0.012}
],
  feet:[
    {id:'boots',name:'Tall boots',replaces:['shoes'],paint:{kind:'leather',trim:0.008,a:[0.43],dyes:['#4a3020','#b09a76','#2a1a10']},built:[{type:'fitted',asset:'boot'}]}],
  wrists:[
    {id:'vambraces',name:'Steel vambraces',dyes:['#9aa0a6','#5e6266','#c9a046'],built:[{type:'vambrace',metal:'#9aa0a6'}]},
    {id:'bracers',name:'Leather bracers',paint:{kind:'studded',trim:0.006,a:[1.45,1.88],dyes:['#5a3a22','#c8b48a','#b0904a']},built:[{type:'cuff',slot:'wrists'}]}],
  hands:[
    {id:'gloves',name:'Work gloves',paint:{kind:'leather',a:[1.93],dyes:['#7a5a3a','#c8b48a','#4a3020']}},
    {id:'plategauntlets',name:'Plate gauntlets',paint:{kind:'leather',a:[1.62],dyes:['#3a2a20','#b09a76','#2a1a10']},built:[{type:'gauntlet',metal:'#9aa0a6'}]},
    {id:'gauntlets',name:'Gauntlet gloves',paint:{kind:'leather',trim:0.008,a:[1.62],dyes:['#3a2a20','#b09a76','#2a1a10']},built:[{type:'cuff',slot:'hands'}]}],
  waist:[   // belts carry sockets: attachments (and, later, relics) hang from them
    {id:'belt',name:'Belt',paint:{kind:'leather',a:[1.005,0.034],dyes:['#3a2618','#c8b48a','#c9a046']},sockets:['hipL','hipR'],built:[{type:'belt'},{type:'buckle'}]},
    {id:'toolbelt',name:'Tool belt',paint:{kind:'studded',trim:0.005,a:[1.0,0.046],dyes:['#4a3020','#c8b48a','#b0904a']},sockets:['hipL','hipR','backL','backR'],built:[{type:'belt',thick:0.008},{type:'buckle',big:1}]},
    {id:'warbelt',name:'War belt with tassets',paint:{kind:'leather',a:[1.0,0.04],dyes:['#3a2618','#c8b48a','#c9a046']},sockets:['hipL','hipR'],built:[{type:'belt',thick:0.008},{type:'buckle',big:1},{type:'tassets',metal:'#9aa0a6'}],legPad:0.02},
    {id:'sash',name:'Sash',dye:'main',paint:{kind:'wool',pattern:'stripes',a:[1.0,0.07],dyes:['#7a2a26','#c9a046','#5a1e1a']},sockets:['hipL'],built:[{type:'belt',thick:0.006,cloth:1},{type:'knot'}]}],
  shoulders:[
    {id:'pads',name:'Leather pads',built:[{type:'pauldron',lames:2}],dyes:['#5a3a22','#c8b48a','#b0904a'],dye:'leather'},
    {id:'spaulders',name:'Layered spaulders',built:[{type:'pauldron',lames:4,metal:1,rivets:1,size:0.9}],dyes:['#8e959c','#5e6266','#b8bcc0'],dye:'trim'},
    {id:'plates',name:'Steel pauldrons',built:[{type:'pauldron',lames:3,metal:1,rivets:1,ridge:1,size:1.08}],dyes:['#9aa0a6','#6a6e72','#c9a046'],dye:'trim'},
    {id:'brass',name:'Brass pauldrons',built:[{type:'pauldron',lames:3,metal:1,rivets:1,ridge:1}],dyes:['#b08a42','#7a5a26','#e0c070'],dye:'trim'},
    {id:'furplates',name:'Fur-trimmed pauldrons',built:[{type:'pauldron',lames:3,metal:1,rivets:1,fur:1,size:1.1}],dyes:['#7e868c','#8a7458','#c9a046'],dye:'trim'},
    {id:'mantle',name:'Fur mantle',built:[{type:'mantle'}],dyes:['#6e5640','#3e3024','#2a2018']}],
  head:[
    {id:'kettlehelm',name:'Kettle helm',hair:'helm',dyes:['#9aa0a6','#5e6266','#c9a046'],built:[{type:'helm',brim:1,metal:'#9aa0a6'}]},
    {id:'nasalhelm',name:'Nasal helm',hair:'hide',dyes:['#a0a6ac','#5e6266','#c9a046'],built:[{type:'helm',cone:1,nasal:1,metal:'#a0a6ac'}]},
    {id:'gogglehelm',people:'Ferrin',name:'Ferrin goggle helm',hair:'hide',dyes:['#8a6a3a','#5a4026','#c9a046'],built:[{type:'helm',goggles:1,metal:'#8a6a3a'}]},
    {id:'hood',dye:'main',hair:'hide',name:'Hood',built:[{type:'hood'}],dyes:['#4a5a3a','#3a4a2e','#2a2a20']},
    {id:'hat',dye:'main',hair:'hat',name:'Brimmed hat',built:[{type:'hat'}],dyes:['#4a3424','#3a2618','#c9a046']},
    {id:'headwrap',people:'Zarhim',dye:'main',hair:'wrap',name:'Zarhim head wrap',built:[{type:'headwrap'}],dyes:['#d8c8a8','#a8783a','#7a5426']}],
  back:[
    {id:'cloak',dye:'main',name:'Cloak',built:[{type:'cloak'}],dyes:['#5a2a26','#3e1c18','#c9a046']},
    {id:'wovencloak',people:'Ruadhan',dye:'main',name:'Ruadhan woven cloak',built:[{type:'cloak',woven:1}],dyes:['#3e5a3a','#8a3a26','#c9a046']}],
};
// what can hang from a belt's sockets (relics will join these)
const EQ_ATTACH=[['None',null],['Pouch','pouch'],['Flask','flask'],['Scroll case','scroll'],['Hammer','hammer']];
const EQ_SOCKETS={hipL:{name:'Left hip',a:1.35},hipR:{name:'Right hip',a:-1.35},backL:{name:'Left back',a:2.35},backR:{name:'Right back',a:-2.35}};
const EQ_DYES=[['Natural',null],['Forest',['#3e5a36','#2a3e26','#b0904a']],['Crimson',['#7a2626','#4e1818','#c9a046']],
  ['Midnight',['#2a3450','#1a2036','#b8b8c8']],['Ochre',['#a8783a','#7a5426','#4a3020']],['Ash',['#8a8a86','#5a5a58','#2e2e2c']]];
function eqItem(slot,id){return (EQ_ITEMS[slot]||[]).find(i=>i.id===id)||null;}
function eqSlotOf(id){for(const s in EQ_ITEMS)if(EQ_ITEMS[s].some(i=>i.id===id))return s;return null;}
// What is actually drawn: every item in its own slot (older outfits put coats in chest, trousers in legs, shoes in feet); slots
// another item fills are emptied (a breastplate fills the coat slot too); slots an item replaces or hides are left undrawn
// (boots replace shoes, reinforced trousers the wardrobe's lower, a robe hides the legs, which still count for stats).
function eqNormalize(o){const out=Object.assign({},o);
  for(const k of Object.keys(o)){if(!EQ_ITEMS[k]||o[k]==null)continue;const s=eqSlotOf(o[k]);if(s&&s!==k){if(out[k]===o[k])delete out[k];if(out[s]==null)out[s]=o[k];}}
  for(const s of Object.keys(EQ_ITEMS)){const it=eqItem(s,out[s]);if(it)for(const f of it.fills||[])if(f!==s)delete out[f];}
  for(const s of Object.keys(EQ_ITEMS)){const it=eqItem(s,out[s]);if(it)for(const f of (it.replaces||[]).concat(it.hides||[]))delete out[f];}
  return out;}
// which item, if any, takes this slot away (for the equipment panel)
function eqBlockedBy(o,slot){const n=eqNormalize(o);for(const s of Object.keys(EQ_ITEMS)){const it=eqItem(s,n[s]);if(it&&(it.fills||[]).includes(slot)&&s!==slot)return it;}return null;}
// How an outfit's dye reaches each item: 'main' (chests, cloaks, hoods), 'second' (trousers), 'leather' (a part tint, so it
// still reads as leather), 'trim' (metal keeps its colour, its trim takes the dye); items without a role keep their own colours.
function eqDyes(item,dye){
  const own=item.dyes||(item.paint&&item.paint.dyes), role=item.dye;
  if(!dye||!role)return own;
  const mixc=(a,b,t)=>'#'+new THREE.Color(a).lerp(new THREE.Color(b),t).getHexString();
  if(role==='main')return [dye[0],dye[1],dye[2]];
  if(role==='second')return [dye[1],mixc(dye[1],'#000000',0.3),dye[2]];
  if(role==='leather')return [mixc(own[0],dye[0],0.45),own[1],dye[2]];
  if(role==='trim')return [own[0],own[1],dye[2]];
  return own;
}

/* ---------- 4. the bake: paint + layers into one texture per character ---------- */
const EQ_CREASE=0.95;   // the template height where the legs part from the body
function eqLayerUniforms(outfit){ // outfit: {slot: itemId, dye: [..]}
  const Q=[];for(let i=0;i<66;i++)Q.push(new THREE.Vector4(0,0,0,0));   // (a bare Vector4 has w = 1, which would switch every layer on)
  EQ_LAYERS.forEach((slot,L)=>{const it=eqItem(slot,outfit[slot]);if(!it||!it.paint)return;const P=it.paint,dy=eqDyes(it,outfit.dye);
    Q[L*6].set(EQ_KIND[P.kind],EQ_PATTERN[P.pattern||'plain'],P.trim||0,(P.shape!=null?P.shape:EQ_LAYER_SHAPE[slot])+1);
    const a=(P.a||[]).concat([0,0,0,0]),b=(P.b||[]).concat([0,0,0,0]),tile=P.mat!==undefined?EQ_MAT[P.mat]:EQ_KIND_MAT[EQ_KIND[P.kind]];
    Q[L*6+1].set(a[0],a[1],a[2],a[3]);Q[L*6+2].set(b[0],b[1],b[2],tile);
    for(let k=0;k<3;k++){const c=new THREE.Color(dy[k]);Q[L*6+3+k].set(c.r,c.g,c.b,1);}});
  return Q;
}
const EqBake=(()=>{
  let scene,cam,quad,dil;
  function setup(){
    scene=new THREE.Scene();cam=new THREE.OrthographicCamera(-1,1,1,-1,0,1);
    dil=new THREE.ShaderMaterial({uniforms:{uT:{value:null},uPx:{value:new THREE.Vector2()}},vertexShader:'varying vec2 vU;void main(){vU=uv;gl_Position=vec4(position.xy,0.,1.);}',
      fragmentShader:`uniform sampler2D uT;uniform vec2 uPx;varying vec2 vU;void main(){vec4 c=texture2D(uT,vU);if(c.a>0.5){gl_FragColor=c;return;}
        vec4 s=vec4(0.);for(int i=-1;i<=1;i++)for(int j=-1;j<=1;j++){vec4 n=texture2D(uT,vU+vec2(float(i),float(j))*uPx);s+=vec4(n.rgb*n.a,n.a);}
        gl_FragColor=s.a>0.?vec4(s.rgb/s.a,1.):vec4(0.);}`,depthTest:false,depthWrite:false});
    quad=new THREE.Mesh(new THREE.PlaneGeometry(2,2),dil);quad.frustumCulled=false;
  }
  function material(look,outfit){
    const U=paintedMaterial(look).userData.U; U.uQ={value:eqLayerUniforms(outfit||{})}; U.uGear={value:EQ_GEAR}; U.uMatScale={value:EQ_MAT_SCALE};
    const W=(outfit&&outfit.wear)||{}; U.uWear={value:new THREE.Vector4(W.wear||0,W.dirt||0,W.seed||0,0)};
    const m=new THREE.ShaderMaterial({uniforms:U,side:THREE.DoubleSide,depthTest:false,depthWrite:false,
      vertexShader:'attribute vec3 rest;attribute float torso;varying vec3 vRest;varying float vTorso;void main(){vRest=rest;vTorso=torso;gl_Position=vec4(uv*2.-1.,0.,1.);}',
      fragmentShader:'varying float vTorso;\n'+PAINT_GLSL+EQUIP_GLSL+'\nvoid main(){'+(window.EQ_DEBUG||'vec3 c=paintBody(vRest);c=applyEquip(c,vRest);gl_FragColor=vec4(c,1.);')+'}'});
    m.extensions={derivatives:true}; return m;
  }
  // bake one body into a texture: painted into a scratch target shared by every bake of that size, padded six times so seams
  // don't show, the last pass written into the body's own target (one per body, mipmapped)
  const scratch={};
  const mk=(size,mip)=>new THREE.WebGLRenderTarget(size,size,{minFilter:mip?THREE.LinearMipmapLinearFilter:THREE.LinearFilter,magFilter:THREE.LinearFilter,generateMipmaps:mip,depthBuffer:false,stencilBuffer:false});
  function bake(renderer,mesh,look,outfit,size){
    if(!scene)setup(); size=size||1024;
    const S=scratch[size]||(scratch[size]=[mk(size,false),mk(size,false)]), ud=mesh.userData;
    if(!ud.bakeRT||ud.bakeRT.width!==size){if(ud.bakeRT)ud.bakeRT.dispose();ud.bakeRT=mk(size,true);}
    const g=new THREE.Mesh(mesh.geometry,material(look,outfit)); g.frustumCulled=false;
    const prevT=renderer.getRenderTarget(),prevC=renderer.getClearColor(new THREE.Color()),prevA=renderer.getClearAlpha(),prevAuto=renderer.autoClear;
    renderer.autoClear=true; renderer.setClearColor(0x000000,0);
    scene.add(g); renderer.setRenderTarget(S[0]); renderer.render(scene,cam); scene.remove(g); g.material.dispose();
    scene.add(quad); let src=S[0],dst=S[1]; dil.uniforms.uPx.value.set(1/size,1/size);
    for(let i=0;i<6;i++){const out=i===5?ud.bakeRT:dst;dil.uniforms.uT.value=src.texture;renderer.setRenderTarget(out);renderer.render(scene,cam);[src,dst]=[dst,src];}
    scene.remove(quad);
    renderer.setRenderTarget(prevT); renderer.setClearColor(prevC,prevA); renderer.autoClear=prevAuto;
    return ud.bakeRT.texture;
  }
  return {bake,material};
})();
// the body's material once baked: a plain textured, skinned, morphed material
function bakedMaterial(tex){const m=new THREE.MeshLambertMaterial({map:tex,skinning:true,morphTargets:true,morphNormals:true});
  // tuck: where cloth lies tight over the body, the body beneath draws in a little, so it never shows through as it moves
  m.onBeforeCompile=sh=>{sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nattribute float tuck;')
    .replace('#include <begin_vertex>','#include <begin_vertex>\ntransformed-=normal*tuck;');};return m;}

/* ---------- 5. built armour: pieces cut from the body's own surface ---------- */
// A point of a built piece is a blend of body points ([[index, weight], ...]): its position, skin weights and every
// people and build shape come from those points, so the piece fits whoever wears it.
const eqSm=(a,b,x)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);};
const EQ_ARM=[[0.2,1.43],[0.255,1.17],[0.296,0.95],[0.315,0.70]];
function eqArmT(x,z){let best=1e9,tt=0;for(let k=0;k<3;k++){const [ax,az]=EQ_ARM[k],[bx,bz]=EQ_ARM[k+1],dx=bx-ax,dz=bz-az;
  const t=Math.min(1,Math.max(0,((Math.abs(x)-ax)*dx+(z-az)*dz)/(dx*dx+dz*dz))),ex=Math.abs(x)-ax-dx*t,ez=z-az-dz*t,d=ex*ex+ez*ez;if(d<best){best=d;tt=k+t;}}return tt;}
function eqBodyData(body){ // what the builders read from the body, once per geometry
  const g=body.geometry; if(g.userData.eq)return g.userData.eq;
  const n=g.attributes.position.count, rest=g.attributes.rest.array, tor=g.attributes.torso.array;
  const D={g,n,pos:g.attributes.position.array,nrm:g.attributes.normal.array,rest,tor,si:g.attributes.skinIndex.array,sw:g.attributes.skinWeight.array,
    morph:(g.morphAttributes.position||[]).map(a=>a.array),idx:g.index.array,arm:new Float32Array(n),t:new Float32Array(n)};
  for(let i=0;i<n;i++){D.arm[i]=1-eqSm(0.3,0.7,tor[i]);D.t[i]=eqArmT(rest[i*3],rest[i*3+2]);}
  return g.userData.eq=D;
}
function eqEval(D,rec){ // a blended point: position, normal, shape deltas, skin
  const p=[0,0,0],nn=[0,0,0],r=[0,0,0],dl=D.morph.map(()=>[0,0,0]),bones=new Map();
  for(const [i,w] of rec){for(let k=0;k<3;k++){p[k]+=D.pos[i*3+k]*w;nn[k]+=D.nrm[i*3+k]*w;r[k]+=D.rest[i*3+k]*w;}
    D.morph.forEach((m,j)=>{for(let k=0;k<3;k++)dl[j][k]+=m[i*3+k]*w;});
    for(let k=0;k<4;k++){const b=D.si[i*4+k],ww=D.sw[i*4+k]*w;if(ww>0)bones.set(b,(bones.get(b)||0)+ww);}}
  const L=Math.hypot(...nn)||1;
  return {p,n:nn.map(v=>v/L),r,dl,bones};
}
// cut the body's triangles to where f >= 0 (f: per body point), returning polygons of blended points
function eqCut(D,fs){
  const val=(rec,f)=>rec.reduce((s,[i,w])=>s+f[i]*w,0);
  const mix=(a,b,t)=>{const m=new Map();for(const [i,w] of a)m.set(i,(m.get(i)||0)+w*(1-t));for(const [i,w] of b)m.set(i,(m.get(i)||0)+w*t);return [...m].filter(e=>e[1]>1e-6);};
  const out=[];
  for(let t=0;t<D.idx.length;t+=3){
    let poly=[[[D.idx[t],1]],[[D.idx[t+1],1]],[[D.idx[t+2],1]]];
    for(const f of fs){
      const vs=poly.map(r=>val(r,f)); if(vs.every(v=>v<0)){poly=null;break;} if(vs.every(v=>v>=0))continue;
      const np=[];for(let k=0;k<poly.length;k++){const a=poly[k],b=poly[(k+1)%poly.length],va=vs[k],vb=vs[(k+1)%poly.length];
        if(va>=0)np.push(a); if((va>=0)!==(vb>=0))np.push(mix(a,b,va/(va-vb)));}
      poly=np.length>=3?np:null; if(!poly)break;}
    if(poly)out.push(poly.map(r=>({rec:r,f:fs.map(f=>val(r,f))})));
  }
  return out;
}
// a piece under construction: plain arrays, merged into one mesh at the end
function eqPiece(){return {P:[],N:[],C:[],DL:[],SK:[],I:[],RS:[],K:[],kind:3};}   // kind: the material tile (EQ_MAT)
const eqMatOf=(item,spec,def)=>{const m=(spec&&spec.mat)||item.mat;return m!==undefined?EQ_MAT[m]:def;};
function eqVert(pc,e,off,col){ // add one point (an evaluated body blend), pushed out along its normal
  const i=pc.P.length/3; for(let k=0;k<3;k++){pc.P.push(e.p[k]+e.n[k]*off);pc.N.push(e.n[k]);} pc.C.push(...col);
  pc.DL.push(e.dl); pc.SK.push(e.bones); pc.RS.push(...e.r); pc.K.push(pc.kind); return i;}
const eqKey=p=>p.map(v=>Math.round(v*2000)).join(',');
// a shell: the cut region pushed out by thick(point), with a wall round its edge so it reads as a solid piece
function eqShell(pc,D,fs,thick,colour,smooth,minH){   // smooth: passes; minH: how close to the body smoothing may bring it
  const polys=eqCut(D,fs), base=pc.P.length/3, edges=new Map(), at=new Map();
  for(const poly of polys){
    const ids=poly.map(v=>{const e=eqEval(D,v.rec),o=Math.max(thick(e,v.f),eqOccAt(D,v.rec)+0.004),key=eqKey(e.p);
      const id=eqVert(pc,e,o,colour(e,v.f,0)); at.set(id,{e,o,key,f:v.f,rec:v.rec}); return id;});
    for(let k=1;k+1<ids.length;k++)pc.I.push(ids[0],ids[k],ids[k+1]);
    for(let k=0;k<ids.length;k++){const a=ids[k],b=ids[(k+1)%ids.length],ka=at.get(a).key,kb=at.get(b).key,key=ka<kb?ka+'|'+kb:kb+'|'+ka;
      const E=edges.get(key);if(E)E.n++;else edges.set(key,{a,b,n:1});}
  }
  if(smooth){   // relax the inside of the shell (points sharing a place move together; the edge stays put)
    const edgeK=new Set(); for(const {a,b,n} of edges.values())if(n===1){edgeK.add(at.get(a).key);edgeK.add(at.get(b).key);}
    const nb=new Map(), grp=new Map();
    for(const [id,v] of at){if(!grp.has(v.key))grp.set(v.key,[]);grp.get(v.key).push(id);}
    for(const {a,b} of edges.values()){const ka=at.get(a).key,kb=at.get(b).key;if(!nb.has(ka))nb.set(ka,new Set());if(!nb.has(kb))nb.set(kb,new Set());nb.get(ka).add(kb);nb.get(kb).add(ka);}
    let P=new Map([...grp].map(([k,ids])=>[k,pc.P.slice(ids[0]*3,ids[0]*3+3)]));
    const floor=new Map([...grp].map(([k,ids])=>{const v=at.get(ids[0]);return [k,{b:v.e.p,n:v.e.n,o:v.o}];}));
    for(let it=0;it<smooth;it++){const Q=new Map();for(const [k,p] of P){if(edgeK.has(k)||!nb.has(k)){Q.set(k,p);continue;}
      const m=[0,0,0];let c=0;for(const j of nb.get(k)){const q=P.get(j);m[0]+=q[0];m[1]+=q[1];m[2]+=q[2];c++;}
      const q=p.map((v,i)=>v*0.4+m[i]/c*0.6), F=floor.get(k), h=(q[0]-F.b[0])*F.n[0]+(q[1]-F.b[1])*F.n[1]+(q[2]-F.b[2])*F.n[2];
      const lo=minH===undefined?F.o:minH; if(h<lo)for(let i=0;i<3;i++)q[i]+=F.n[i]*(lo-h);   // smoothing fills hollows, it never sinks into the body
      Q.set(k,q);}P=Q;}
    for(const [k,ids] of grp){const p=P.get(k);for(const id of ids){pc.P[id*3]=p[0];pc.P[id*3+1]=p[1];pc.P[id*3+2]=p[2];}}
  }
  for(const v of at.values())eqOccMark(D,v.rec,v.o+0.002);   // what's outside now
  if(D.hide)for(let i=0;i<D.n;i++){let m=1e9;for(const f of fs)m=Math.min(m,f[i]);if(m>=0.012)D.hide[i]=1;}   // the body under it goes, all but a margin at its edge
  for(const {a,b,n} of edges.values()){if(n!==1)continue;           // an edge of the piece: a wall from the body up to the shell
    const A=at.get(a),B=at.get(b),col=colour(A.e,A.f,1);
    const a0=eqVert(pc,A.e,0.0015,col),b0=eqVert(pc,B.e,0.0015,col),a1=eqVert(pc,A.e,A.o,col),b1=eqVert(pc,B.e,B.o,col);
    pc.I.push(a0,b0,b1,a0,b1,a1);}                                     // one face: the material draws both sides
  return polys.length;
}
// Like World of Warcraft, pieces never fight over the same surface. Each build keeps, for every body point, how far out the
// pieces already on it reach (D.occ); a later piece goes outside them. Pieces are built from the inside out (EQ_LAYER_ORDER).
// And the body under a piece is removed (D.hide), the way WoW swaps a body section for an armour-shaped one, so nothing
// underneath can poke through.
const eqOccAt=(D,rec)=>D.occ?rec.reduce((a,[i,w])=>a+D.occ[i]*w,0):0;
function eqOccMark(D,rec,o){if(!D.occ)return;for(const [i,w] of rec)if(w>0.2&&D.occ[i]<o)D.occ[i]=o;}
// a small block pinned to the body (buckles, pouches, lacing): centred at a body point, facing out along its normal
function eqBlock(pc,D,rec,w,h,d,off,colour,shade,drop){
  off=Math.max(off,eqOccAt(D,rec)+0.001); eqOccMark(D,rec,off+d);
  const e=eqEval(D,rec), n=e.n, up=[0,1,0]; let x=[up[1]*n[2]-up[2]*n[1],up[2]*n[0]-up[0]*n[2],up[0]*n[1]-up[1]*n[0]]; const lx=Math.hypot(...x)||1; x=x.map(v=>v/lx);
  const y=[n[1]*x[2]-n[2]*x[1],n[2]*x[0]-n[0]*x[2],n[0]*x[1]-n[1]*x[0]];
  const P=(sx,sy,sz)=>[0,1,2].map(k=>e.p[k]+n[k]*(off+sz*d)+x[k]*sx*w/2+y[k]*(sy*h/2-(drop||0)));
  const faces=[[[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1],n,1],[[1,-1,0],[-1,-1,0],[-1,1,0],[1,1,0],n.map(v=>-v),0.7],
    [[-1,-1,0],[1,-1,0],[1,-1,1],[-1,-1,1],y.map(v=>-v),0.8],[[-1,1,1],[1,1,1],[1,1,0],[-1,1,0],y,0.95],
    [[1,-1,0],[1,1,0],[1,1,1],[1,-1,1],x,0.88],[[-1,1,0],[-1,-1,0],[-1,-1,1],[-1,1,1],x.map(v=>-v),0.88]];
  for(const [a,b,c,dd,fn,sh] of faces){const i0=pc.P.length/3;
    for(const q of [a,b,c,dd]){const p=P(...q);pc.P.push(...p);pc.N.push(...fn);pc.C.push(...colour.map(v=>v*sh*(shade||1)));pc.DL.push(e.dl);pc.SK.push(e.bones);pc.RS.push(...e.r);pc.K.push(pc.kind);}
    pc.I.push(i0,i0+1,i0+2,i0,i0+2,i0+3);}
}
// a stud: one small face looking out (rivets, buttons), two triangles
function eqStud(pc,D,rec,size,off,colour){
  off=Math.max(off,eqOccAt(D,rec)+0.0015);
  const e=eqEval(D,rec),n=e.n,up=[0,1,0];let x=[up[1]*n[2]-up[2]*n[1],up[2]*n[0]-up[0]*n[2],up[0]*n[1]-up[1]*n[0]];const lx=Math.hypot(...x)||1;x=x.map(v=>v/lx);
  const y=[n[1]*x[2]-n[2]*x[1],n[2]*x[0]-n[0]*x[2],n[0]*x[1]-n[1]*x[0]],i0=pc.P.length/3;
  for(const [a,b,sh] of [[-1,-1,0.8],[1,-1,0.9],[1,1,1.25],[-1,1,1.1]]){pc.P.push(...[0,1,2].map(k=>e.p[k]+n[k]*off+x[k]*a*size/2+y[k]*b*size/2));pc.N.push(...n);
    pc.C.push(...colour.map(v=>v*sh));pc.DL.push(e.dl);pc.SK.push(e.bones);pc.RS.push(...e.r);pc.K.push(12);}
  pc.I.push(i0,i0+1,i0+2,i0,i0+2,i0+3);
}
// an upright cylinder pinned to the body (flasks, scroll cases): its side touching the body at off, hanging drop below the pin
function eqCyl(pc,D,rec,r,h,off,drop,colour,shade,segs){
  off=Math.max(off,eqOccAt(D,rec)+0.001); eqOccMark(D,rec,off+2*r);
  segs=segs||8; const e=eqEval(D,rec),n=e.n,up=[0,1,0]; let x=[up[1]*n[2]-up[2]*n[1],up[2]*n[0]-up[0]*n[2],up[0]*n[1]-up[1]*n[0]];const lx=Math.hypot(...x)||1;x=x.map(v=>v/lx);
  const y=[n[1]*x[2]-n[2]*x[1],n[2]*x[0]-n[0]*x[2],n[0]*x[1]-n[1]*x[0]], c=[0,1,2].map(k=>e.p[k]+n[k]*(off+r)-y[k]*drop);
  const ring=sy=>{const ids=[];for(let s_=0;s_<segs;s_++){const a=s_/segs*Math.PI*2,dir=[0,1,2].map(k=>n[k]*Math.cos(a)+x[k]*Math.sin(a));
    ids.push(pc.P.length/3);pc.P.push(...[0,1,2].map(k=>c[k]+dir[k]*r+y[k]*sy*h/2));pc.N.push(...dir);pc.C.push(...colour.map(v=>v*(shade||1)*(0.85+0.2*Math.cos(a-0.6))));pc.DL.push(e.dl);pc.SK.push(e.bones);pc.RS.push(...e.r);pc.K.push(pc.kind);}return ids;};
  const lo=ring(-1),hi=ring(1);for(let s_=0;s_<segs;s_++){const a=lo[s_],b=lo[(s_+1)%segs],c2=hi[(s_+1)%segs],d=hi[s_];pc.I.push(a,b,c2,a,c2,d);}
  for(const [rg,sg] of [[hi,1],[lo,-1]]){const ci=pc.P.length/3;pc.P.push(...[0,1,2].map(k=>c[k]+y[k]*sg*h/2));pc.N.push(...y.map(v=>v*sg));pc.C.push(...colour.map(v=>v*(shade||1)*(sg>0?1.05:0.7)));pc.DL.push(e.dl);pc.SK.push(e.bones);pc.RS.push(...e.r);pc.K.push(pc.kind);
    for(let s_=0;s_<segs;s_++){const a=rg[s_],b=rg[(s_+1)%segs];if(sg>0)pc.I.push(a,b,ci);else pc.I.push(b,a,ci);}}
}
// a point on the belt at an angle round the waist (0 the front, positive towards the left hip)
function eqBeltPoint(D,c,ang){const cand=[];for(let i=0;i<D.n;i++){if(D.arm[i]>0.5)continue;const z=D.rest[i*3+2];if(Math.abs(z-c)>0.02)continue;
  let d=Math.atan2(D.rest[i*3],-D.rest[i*3+1])-ang;d=Math.atan2(Math.sin(d),Math.cos(d));cand.push([i,Math.abs(d)+Math.abs(z-c)*3]);}
  cand.sort((a,b)=>a[1]-b[1]);const best=cand.slice(0,3),ws=best.map(([i,d])=>[i,1/(d+0.02)]),sw=ws.reduce((a,b)=>a+b[1],0);return ws.map(([i,w])=>[i,w/sw]);}
// the body point nearest a spot on the paint template (and blends of a few, for a smooth pin)
function eqNear(D,x,y,z,k,filter){
  const best=[];for(let i=0;i<D.n;i++){if(filter&&!filter(i))continue;const dx=D.rest[i*3]-x,dy=D.rest[i*3+1]-y,dz=D.rest[i*3+2]-z,d=dx*dx+dy*dy+dz*dz;
    if(best.length<k||d<best[best.length-1][1]){best.push([i,d]);best.sort((a,b)=>a[1]-b[1]);if(best.length>k)best.pop();}}
  const ws=best.map(([i,d])=>[i,1/(Math.sqrt(d)+0.004)]),s=ws.reduce((a,b)=>a+b[1],0);return ws.map(([i,w])=>[i,w/s]);
}
const eqRGB=h=>{const c=new THREE.Color(h);return [c.r,c.g,c.b];};
// smooth value noise in 3D (for fur clumps and tufted edges); eqNoise below is per-point
const eqHash=(x,y,z)=>{const v=Math.sin(x*127.1+y*311.7+z*74.7)*43758.5453;return v-Math.floor(v);};
function eqSmooth(p,s){const x=p[0]*s,y=p[1]*s,z=p[2]*s,ix=Math.floor(x),iy=Math.floor(y),iz=Math.floor(z),fx=x-ix,fy=y-iy,fz=z-iz,u=t=>t*t*(3-2*t);
  const a=u(fx),b=u(fy),c=u(fz),H=eqHash,l=(q,w,t)=>q+(w-q)*t;
  return l(l(l(H(ix,iy,iz),H(ix+1,iy,iz),a),l(H(ix,iy+1,iz),H(ix+1,iy+1,iz),a),b),l(l(H(ix,iy,iz+1),H(ix+1,iy,iz+1),a),l(H(ix,iy+1,iz+1),H(ix+1,iy+1,iz+1),a),b),c);}
const eqFur=(p)=>0.6*eqSmooth(p,38)+0.4*eqSmooth(p,95);
const eqNoise=(p,s)=>{const v=Math.sin(p[0]*s*12.9898+p[1]*s*78.233+p[2]*s*37.719)*43758.5453;return v-Math.floor(v);};

// Drapes (cloaks, aprons, skirts) hang the way cloth does: from where they are fastened they may move away from the body but
// never back toward it, so they fall straight from whatever sticks out most (shoulder blades, chest, hips) instead of
// following every curve. Their surface directions come from their own grid, and their triangles face outward.
function eqDrapeFinish(pc,grid,hint,closed){
  const R=grid.length,Cn=grid[0].length,G=(r,c)=>{const id=grid[r][c];return [pc.P[id*3],pc.P[id*3+1],pc.P[id*3+2]];};
  for(let r=0;r<R;r++)for(let c=0;c<Cn;c++){
    const cl=closed?(c+Cn-1)%Cn:Math.max(0,c-1),cr=closed?(c+1)%Cn:Math.min(Cn-1,c+1),A=G(r,cl),B=G(r,cr),U=G(Math.max(0,r-1),c),Dn=G(Math.min(R-1,r+1),c);
    const du=B.map((v,k)=>v-A[k]),dv=Dn.map((v,k)=>v-U[k]);let n=[du[1]*dv[2]-du[2]*dv[1],du[2]*dv[0]-du[0]*dv[2],du[0]*dv[1]-du[1]*dv[0]];
    const h=hint(G(r,c),r,c),L=Math.hypot(...n)||1;if(n[0]*h[0]+n[1]*h[1]+n[2]*h[2]<0)n=n.map(v=>-v);const id=grid[r][c];for(let k=0;k<3;k++)pc.N[id*3+k]=n[k]/L;}
  for(let r=0;r+1<R;r++)for(let c=0;c<(closed?Cn:Cn-1);c++){const c2=(c+1)%Cn,a=grid[r][c],b=grid[r][c2],cc=grid[r+1][c2],d=grid[r+1][c];
    const A=G(r,c),B=G(r,c2),Dd=G(r+1,c),u=B.map((v,k)=>v-A[k]),w=Dd.map((v,k)=>v-A[k]),n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]],o=pc.N.slice(a*3,a*3+3);
    if(n[0]*o[0]+n[1]*o[1]+n[2]*o[2]>0)pc.I.push(a,b,cc,a,cc,d);else pc.I.push(a,d,cc,a,cc,b);}
}
// the body's height (glTF y) at a template height; the nearest body point to a spot (for shapes and skin); blended skin
function eqYAt(D,zt,filter){const ys=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&Math.abs(D.rest[i*3+2]-zt)<0.012&&(!filter||filter(i)))ys.push(D.pos[i*3+1]);ys.sort((a,b)=>a-b);return ys.length?ys[ys.length>>1]:null;}
function eqNearPos(D,ids,x,y,z){let b=ids[0],bd=1e9;for(const i of ids){const d=(D.pos[i*3]-x)**2+(D.pos[i*3+1]-y)**2*1.5+(D.pos[i*3+2]-z)**2;if(d<bd){bd=d;b=i;}}return b;}
function eqMixBones(a,b,t){const m=new Map();for(const [k,w] of a)m.set(k,(m.get(k)||0)+w*(1-t));for(const [k,w] of b)m.set(k,(m.get(k)||0)+w*t);return m;}
// metal for built armour: its own colour (spec.metal), a dark edge, and the outfit's trim colour for rivets and rims
function eqMetal(spec,dy){const m=eqRGB(spec.metal||spec.leather||dy[0]).map(v=>spec.metal?v*0.82:v);return {main:m,dark:m.map(v=>v*0.55),trim:eqRGB(dy[2])};}
const eqMetalShade=M=>(e,f,rim)=>rim?M.dark:M.main.map(v=>v*(0.82+0.24*eqSm(0,0.025,f[0]))*(0.95+0.05*eqNoise(e.p,40)));
// the pieces
const EQ_BUILD={
  cuff(pc,D,item,dy,spec,ctx){if(spec.slot==='feet'&&ctx&&ctx.longDrape)return;   // under a long coat the boot top is painted only (WoW drops boot geosets under robes)
    pc.kind=eqMatOf(item,null,3);                       // boot tops, gauntlet cuffs, bracers
    const main=eqRGB(dy[0]),trim=eqRGB(dy[2]),z=D.rest,P=item.paint;
    let fs,thick;
    if(spec.slot==='feet'){const top=P.a[0];
      fs=[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.5&&z[i*3+2]<0.8?z[i*3+2]-(top-0.055):-1),Float32Array.from({length:D.n},(_,i)=>top+0.004-z[i*3+2])];
      thick=e=>0.006+0.012*eqSm(top-0.055,top,e.r[2]);}
    else if(spec.slot==='hands'){fs=[Float32Array.from({length:D.n},(_,i)=>D.arm[i]>0.5?(D.t[i]-1.6)*0.25:-1),Float32Array.from({length:D.n},(_,i)=>(1.86-D.t[i])*0.25)];
      thick=e=>0.005+0.012*eqSm(1.84,1.6,eqArmT(e.r[0],e.r[2]));}
    else {fs=[Float32Array.from({length:D.n},(_,i)=>D.arm[i]>0.5?(D.t[i]-P.a[0])*0.25:-1),Float32Array.from({length:D.n},(_,i)=>(P.a[1]-D.t[i])*0.25)];
      thick=()=>0.0045;}
    eqShell(pc,D,fs,thick,(e,f,rim)=>rim?trim.map(v=>v*0.85):main.map(v=>v*(0.92+0.1*eqNoise(e.p,40))));
  },
  foot(pc,D,item,dy){pc.kind=eqMatOf(item,null,3);const z=D.rest,main=eqRGB(dy[0]),sole=eqRGB(dy[2]),top=Math.min(item.paint.a[0],0.11);
    if(D.hide)for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&z[i*3+2]<top-0.012)D.hide[i]=1;   // the shoe replaces the foot
    const col=(e,f,rim)=>e.r[2]<0.018?sole.map(v=>v*0.8):main.map(v=>v*(0.9+0.1*eqNoise(e.p,30)));
    for(const side of [1,-1]){
      const F=[];for(let i=0;i<D.n;i++)if(z[i*3+2]<0.13&&D.arm[i]<0.5&&Math.sign(z[i*3])===side)F.push(i);
      // the foot's own frame (glTF space: y up, the feet point along +z): forward s, across l
      let mx=0,mz=0;for(const i of F){mx+=D.pos[i*3];mz+=D.pos[i*3+2];}mx/=F.length;mz/=F.length;
      let sxx=0,sxz=0,szz=0;for(const i of F){const a=D.pos[i*3]-mx,b=D.pos[i*3+2]-mz;sxx+=a*a;sxz+=a*b;szz+=b*b;}
      const ang=0.5*Math.atan2(2*sxz,sxx-szz);let fx=Math.cos(ang),fz=Math.sin(ang);if(Math.abs(fz)<Math.abs(fx))[fx,fz]=[-fz,fx];if(fz<0){fx=-fx;fz=-fz;}
      const lx=fz,lz=-fx,S=i=>(D.pos[i*3]-mx)*fx+(D.pos[i*3+2]-mz)*fz,L=i=>(D.pos[i*3]-mx)*lx+(D.pos[i*3+2]-mz)*lz;
      let s0=1e9,s1=-1e9;for(const i of F){const v=S(i);s0=Math.min(s0,v);s1=Math.max(s1,v);}
      const sb=s0+0.62*(s1-s0);
      // heel and instep: the foot's own surface, up to the ball
      eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.5&&Math.sign(z[i*3])===side&&z[i*3+2]<0.4?Math.min(top-z[i*3+2],(sb+0.012-S(i))):-1)],
        e=>0.005+0.003*eqSm(0.06,0.0,e.r[2]),col);
      // the toe box: one smooth shape from a few measurements (the width and height at the ball, where the toes end), wide
      // enough for every toe, no taller than the shoe's top edge, rounded at the tip
      let lmin=1e9,lmax=-1e9,hb=0,tw=0;
      for(const i of F){const sv=S(i),l=L(i),y=D.pos[i*3+1];if(Math.abs(sv-sb)<0.015&&y<top+0.01){lmin=Math.min(lmin,l);lmax=Math.max(lmax,l);hb=Math.max(hb,y);}
        if(sv>sb)tw=Math.max(tw,Math.abs(l-(lmin+lmax)/2));}
      const lc=(lmin+lmax)/2,Wb=Math.max((lmax-lmin)/2,tw)+0.004,Hb=Math.min(top+0.004,hb+0.007),K=5,M=10,ring=[];
      for(let k=0;k<=K;k++){const sv=sb-0.035+(s1+0.012-(sb-0.035))*k/K,t=Math.max(0,(sv-sb)/(s1+0.012-sb));
        const W=Wb*Math.sqrt(Math.max(0.16,1-Math.pow(t,3.5))),H=Hb+(0.034-Hb)*Math.pow(t,1.2),ids=[];
        for(let m=0;m<M;m++){const a=m/M*Math.PI*2,c=Math.cos(a),sn=Math.sin(a),l=lc+W*Math.sign(c)*Math.pow(Math.abs(c),0.8),y=Math.max(0.001,H/2+H/2*Math.sign(sn)*Math.pow(Math.abs(sn),0.8));
          const px=mx+fx*sv+lx*l,pz=mz+fz*sv+lz*l;
          const best=F.map(i=>[i,(D.pos[i*3]-px)**2+(D.pos[i*3+1]-y)**2+(D.pos[i*3+2]-pz)**2]).sort((a_,b_)=>a_[1]-b_[1]).slice(0,4),ws=best.map(([i,d2])=>[i,1/(Math.sqrt(d2)+0.004)]),sw=ws.reduce((a_,b_)=>a_+b_[1],0);
          const e=eqEval(D,ws.map(([i,w])=>[i,w/sw]));e.p=[px,y,pz];
          const dn=[c*lx/Math.max(W,1e-3),sn/Math.max(H/2,1e-3),c*lz/Math.max(W,1e-3)],ln=Math.hypot(...dn);e.n=dn.map(v=>v/ln);
          ids.push(eqVert(pc,e,0,y<0.004?sole.map(v=>v*0.8):main.map(v=>v*(0.92+0.08*eqNoise(e.p,30)))));}
        ring.push(ids);}
      for(let k=0;k<K;k++)for(let m=0;m<M;m++){const a=ring[k][m],b=ring[k][(m+1)%M],c=ring[k+1][(m+1)%M],d=ring[k+1][m];
        const P_=j=>[pc.P[j*3],pc.P[j*3+1],pc.P[j*3+2]],A=P_(a),B=P_(b),C_=P_(d),u=B.map((v,q)=>v-A[q]),w=C_.map((v,q)=>v-A[q]),
          n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]],out=pc.N.slice(a*3,a*3+3);
        if(n[0]*out[0]+n[1]*out[1]+n[2]*out[2]>0)pc.I.push(a,b,c,a,c,d);else pc.I.push(a,d,c,a,c,b);}   // facing out
      const tip=ring[K],cx=[0,1,2].map(j=>tip.reduce((a_,id)=>a_+pc.P[id*3+j],0)/M),ci=pc.P.length/3;   // close the tip
      pc.P.push(...cx);pc.N.push(fx,0,fz);pc.C.push(...main);pc.DL.push(pc.DL[tip[0]]);pc.SK.push(pc.SK[tip[0]]);pc.RS.push(...pc.RS.slice(tip[0]*3,tip[0]*3+3));pc.K.push(pc.kind);
      for(let m=0;m<M;m++){const a=tip[m],b=tip[(m+1)%M],A=pc.P.slice(a*3,a*3+3),B=pc.P.slice(b*3,b*3+3),u=B.map((v,q)=>v-A[q]),w=cx.map((v,q)=>v-A[q]),n=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]];
        if(n[0]*fx+n[2]*fz>0)pc.I.push(a,b,ci);else pc.I.push(a,ci,b);}
    }
  },
  belt(pc,D,item,dy,spec,ctx){pc.kind=eqMatOf(item,spec,spec.cloth?1:3);const z=D.rest,c=spec.z||item.paint.a[0],w=(spec.w||item.paint.a[1])/2,main=eqRGB(dy[spec.colour||0]),th=spec.thick||0.006;
    const pad=ctx&&ctx.torsoPad||0;
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.5?w-Math.abs(z[i*3+2]-c):-1)],e=>(spec.cloth?th+0.004*eqNoise(e.p,15):th)+pad,
      (e,f,rim)=>main.map(v=>v*(rim?0.7:spec.cloth?0.85+0.15*eqNoise(e.p,40):0.95)),spec.cloth?3:0);},
  knot(pc,D,item,dy){pc.kind=eqMatOf(item,null,1);const c=item.paint.a[0],main=eqRGB(dy[0]),rec=eqBeltPoint(D,c,-0.5);   // a sash's knot and its hanging ends
    eqBlock(pc,D,rec,0.04,0.035,0.016,0.006,main,0.9); eqBlock(pc,D,rec,0.03,0.13,0.008,0.012,main,0.8,0.08); eqBlock(pc,D,rec,0.026,0.1,0.008,0.016,main,0.7,0.07);},
  buckle(pc,D,item,dy,spec,ctx){pc.kind=12;const c=item.paint.a[0],rec=eqBeltPoint(D,c,0),brass=eqRGB(dy[2]),k=spec.big?1.3:1,pad=ctx&&ctx.torsoPad||0;
    eqBlock(pc,D,rec,0.05*k,0.04*k,0.006,0.007+pad,brass,1.15); eqBlock(pc,D,rec,0.03*k,0.022*k,0.004,0.0125+pad,eqRGB(dy[0]),0.8);},
  // a skirt for robes and coats: rings from the hips to the hem, measured round the legs so it clears them, flaring towards
  // the hem; lower down it follows the thighs, so it moves when walking. open: a gap at the front (half-angle, radians)
  // skirts for robes and coats, the way WoW builds them: no cloth simulation, but a smooth shape round the body (and whatever
  // it already wears) skinned partly to the hips and partly to each thigh by where it lies: its front-left follows the left
  // thigh, its back-right the right one, its sides split between. The legs move it rather than pass through it, and the hem
  // stays a clean line. open: a gap at the front (half-angle, radians); arc: [from, to] for a panel (an apron)
  skirt(pc,D,item,dy,spec,ctx){pc.kind=spec.kind!=null?spec.kind:eqMatOf(item,spec,item.paint?(item.paint.mat!==undefined?EQ_MAT[item.paint.mat]:EQ_KIND_MAT[EQ_KIND[item.paint.kind]]):1)
      +16*(item.paint?(item.paint.kind==='quilted'?4:EQ_PATTERN[item.paint.pattern||'plain']||0):0);
    const main=spec.colour||eqRGB(dy[0]),trim=spec.trimColour||eqRGB(dy[2]),P=D.pos,oc=D.occ||new Float32Array(D.n),body=[];
    for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+2]<spec.top+0.04&&D.rest[i*3+2]>0.1)body.push(i);
    const ring=body.filter(i=>Math.abs(D.rest[i*3+2]-spec.top)<0.015),cx=ring.reduce((a,i)=>a+P[i*3],0)/ring.length,cz=ring.reduce((a,i)=>a+P[i*3+2],0)/ring.length;
    const yT=eqYAt(D,spec.top),yH0=eqYAt(D,spec.hem),yH=yH0==null?yT*spec.hem/spec.top:yH0,len=spec.top-spec.hem;
    const open=spec.open||0,arc=spec.arc||(open?[open,Math.PI*2-open]:null),closed=!arc,M=closed?24:Math.max(8,Math.round(24*(arc[1]-arc[0])/(Math.PI*2)))+1,K=Math.max(3,Math.min(10,Math.round(len/0.07)));
    const TH=[...Array(closed?M:M)].map((_,b)=>closed?b/M*Math.PI*2:arc[0]+(arc[1]-arc[0])*b/(M-1));   // th = 0 is the front (+z), +x is the left
    const hips=ctx.bone('hips'),tl=ctx.bone('thigh.L'),tr=ctx.bone('thigh.R');
    // the envelope: how far the body (and what's on it) reaches in each direction, at each height, all the way down
    const env=(th,y,band)=>{let r=0;const sx=Math.sin(th),sz=Math.cos(th);for(const i of body){if(Math.abs(P[i*3+1]-y)>band)continue;r=Math.max(r,(P[i*3]-cx)*sx+(P[i*3+2]-cz)*sz+oc[i]);}return r;};
    // the top ring follows the waist itself (its radius in each direction, not the envelope), so the skirt starts snug under the belt
    const waist=(th,y)=>{let r=0;const half=Math.PI/24*1.5;for(const i of body){if(Math.abs(P[i*3+1]-y)>0.014)continue;const x=P[i*3]-cx,z=P[i*3+2]-cz;let d=Math.atan2(x,z)-th;d=Math.atan2(Math.sin(d),Math.cos(d));if(Math.abs(d)<half)r=Math.max(r,Math.hypot(x,z)+Math.min(oc[i],0.012));}return r||env(th,y,0.02);};
    const Rr=[];
    for(let k=0;k<=K;k++){const t=k/K,y=yT+(yH-yT)*t;
      let row=TH.map(th=>(k?env(th,y,0.035):waist(th,y))+(k?(spec.ease!=null?spec.ease:0.014)+0.018*t:0.012)+(spec.off||0));
      if(k)row=row.map((v,b)=>Math.max(v,Rr[k-1][b]));                                       // it never draws back in below the hips
      for(let pass=0;pass<4;pass++){const n=row.length;row=row.map((v,b)=>{const a=closed?row[(b+n-1)%n]:row[Math.max(0,b-1)],c=closed?row[(b+1)%n]:row[Math.min(n-1,b+1)];return Math.max(v,(a+2*v+c)/4);});}
      if(k)row=row.map(v=>v+(spec.flare||0.3)*0.02*t*t);
      Rr.push(row);}
    const grid=[];
    for(let k=0;k<=K;k++){const t=k/K,y=yT+(yH-yT)*t,ids=[];
      TH.forEach((th,b)=>{const r=Rr[k][b]*(1+0.018*t*Math.cos(th*7)),x=cx+Math.sin(th)*r,z=cz+Math.cos(th)*r;
        const e=eqEval(D,[[eqNearPos(D,body,x,y,z),1]]);e.p=[x,y,z];e.n=[Math.sin(th),0,Math.cos(th)];
        const legW=eqSm(0,0.45,t)*(0.5+0.45*Math.abs(Math.cos(th))),side=eqSm(-0.5,0.5,Math.sin(th));
        e.bones=new Map([[hips,1-legW],[tl,legW*side],[tr,legW*(1-side)]]);
        e.r=[Math.sin(th)*0.1,-Math.cos(th)*0.1,spec.top-(spec.top-spec.hem)*t];
        const col=(k===K||(spec.trim&&k>=K-1))?trim:main;ids.push(eqVert(pc,e,0,col.map(v=>v*(0.94+0.06*Math.cos(th*7))*(k===K?0.85:1))));});
      grid.push(ids);}
    eqDrapeFinish(pc,grid,(q)=>[q[0]-cx,0,q[2]-cz],closed);
    if(closed&&len>0.4&&D.hide)for(let i=0;i<D.n;i++){const z=D.rest[i*3+2];if(D.arm[i]<0.5&&z<0.93&&z>spec.hem+0.14)D.hide[i]=1;}   // a robe replaces the upper legs, as WoW's robe geoset does
    if(D.occ){   // the belt and anything later go over the skirt's top: every body point near it is marked as covered out to the skirt
      const ringAt=th=>{let best=0,bd=9;TH.forEach((t2,b)=>{let d=Math.abs(Math.atan2(Math.sin(t2-th),Math.cos(t2-th)));if(d<bd){bd=d;best=b;}});return {r0:Rr[0][best],r1:Rr[Math.min(1,K)][best]};};
      for(const i of body){const y=P[i*3+1];if(y<yT-(yT-yH)/K*1.2||y>yT+0.03)continue;const x=P[i*3]-cx,z=P[i*3+2]-cz,th=Math.atan2(x,z),R_=ringAt(th),f=Math.min(1,Math.max(0,(yT-y)/((yT-yH)/K)));
        const need=(R_.r0*(1-f)+R_.r1*f)-Math.hypot(x,z)+0.004;if(need>D.occ[i])D.occ[i]=need;}}
  },
  // a draped garment: cloth hung on this body in Blender (tools/blender/drape.py), frozen. Its points carry their own skin; the
  // body's people and build shapes reach it from the body points nearest each one, and its folds carry a baked cavity shade.
  drape(pc,D,item,dy,spec,ctx){const G=(typeof EQ_DRAPES!=='undefined'&&EQ_DRAPES[ctx.sex||'m']||{})[spec.asset];if(!G)return;
    pc.kind=spec.kind!=null?spec.kind:eqMatOf(item,spec,item.paint?(item.paint.mat!==undefined?EQ_MAT[item.paint.mat]:EQ_KIND_MAT[EQ_KIND[item.paint.kind]]):1);
    const main=eqRGB(dy[spec.colour||0]),trim=eqRGB(dy[spec.trim!=null?spec.trim:2]),P=D.pos,body=[],bi=G.bones.map(b=>ctx.bone(b)),base=pc.P.length/3;
    for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+2]<G.top+0.1&&D.rest[i*3+2]>0.05)body.push(i);
    const n=G.pos.length/3,hemZ=G.hemY+0.025;
    for(let v=0;v<n;v++){const x=G.pos[v*3],y=G.pos[v*3+1],z=G.pos[v*3+2];
      const near=[];for(const i of body){const d=(P[i*3]-x)**2+(P[i*3+1]-y)**2+(P[i*3+2]-z)**2;if(near.length<4||d<near[3][1]){near.push([i,d]);near.sort((a,b)=>a[1]-b[1]);if(near.length>4)near.pop();}}
      const ws=near.map(([i,d])=>[i,1/(Math.sqrt(d)+0.01)]),sw=ws.reduce((a,b)=>a+b[1],0),e=eqEval(D,ws.map(([i,w])=>[i,w/sw]));
      const b0=e.p;e.r=[e.r[0]+(x-b0[0]),e.r[1]-(z-b0[2]),e.r[2]+(y-b0[1])];e.p=[x,y,z];e.n=[G.nrm[v*3],G.nrm[v*3+1],G.nrm[v*3+2]];
      // where the cloth lies on the body it moves exactly as the body does; where it hangs free, by the drape's own blend
      const free=Math.max(eqSm(0.012,0.05,Math.sqrt(near[0][1])),eqSm(0.1,0.2,G.topY-y)),own=new Map(G.skin[v].map((w,k)=>[bi[k],w]).filter(b=>b[1]>0));e.bones=eqMixBones(e.bones,own,free);
      const sh=G.shade[v],col=(y<hemZ&&spec.trim!=null?trim:main).map(c=>c*sh*(y<hemZ?0.85:1));eqVert(pc,e,0,col);}
    for(const i of G.idx)pc.I.push(base+i);
    if(D.occ){const near=new Float32Array(D.n).fill(9);   // the belt, what hangs from it, and anything later go over the cloth
      for(let v=0;v<n;v++){const y=G.pos[v*3+1];
        for(const i of body){const d=Math.hypot(P[i*3]-G.pos[v*3],P[i*3+1]-y,P[i*3+2]-G.pos[v*3+2]);if(d<near[i])near[i]=d;}}
      for(const i of body)if(near[i]<0.08&&near[i]+0.004>D.occ[i])D.occ[i]=near[i]+0.004;}   // all the way down: what hangs from the belt hangs outside the coat
    if(D.tuck)for(let v=0;v<n;v++){const x=G.pos[v*3],y=G.pos[v*3+1],z=G.pos[v*3+2];
      const leg=y<G.topY-0.12;   // on the legs (hidden but for the slit) the tuck is deeper and reaches further
      for(const i of body){const d=Math.hypot(P[i*3]-x,P[i*3+1]-y,P[i*3+2]-z);
        if(leg?d<0.08:d<0.03)D.tuck[i]=Math.max(D.tuck[i],leg?0.028*(1-eqSm(0.05,0.08,d)):0.012*(1-eqSm(0.02,0.03,d)));}}
    if(spec.hideLegs&&D.hide)for(let i=0;i<D.n;i++){const z=D.rest[i*3+2];if(D.arm[i]<0.5&&z<0.93&&z>G.hem+0.14)D.hide[i]=1;}
  },
  // a fitted piece made in Blender (tools/blender/shoes.py): shoes and boots shaped round the body's own foot and leg. Its
  // points carry their own skin and parts (0 upper, 1 sole and heel, 2 collar or cuff); the body's people and build shapes
  // reach it from the nearest body points; the body inside it (the foot, and in a boot the lower leg) is removed, as WoW's
  // boots replace the feet; what goes on later (greaves, a coat) sits outside it.
  fitted(pc,D,item,dy,spec,ctx){const G=(typeof EQ_FITTED!=='undefined'&&EQ_FITTED[ctx.sex||'m']||{})[spec.asset];if(!G)return;
    pc.kind=eqMatOf(item,spec,3);
    /* colours: upper, sole, collar or cuff (a darker turn of the upper unless a trim is named) */
    const cols=[eqRGB(dy[0]),eqRGB(dy[2]).map(v=>v*0.55),spec.trim!=null?eqRGB(dy[spec.trim]):eqRGB(dy[0]).map(v=>v*0.72)],P=D.pos,legs=[],bi=G.bones.map(b=>ctx.bone(b)),base=pc.P.length/3,n=G.pos.length/3;
    for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+2]<0.6)legs.push(i);
    for(let v=0;v<n;v++){const x=G.pos[v*3],y=G.pos[v*3+1],z=G.pos[v*3+2];
      const near=[];for(const i of legs){const d=(P[i*3]-x)**2+(P[i*3+1]-y)**2+(P[i*3+2]-z)**2;if(near.length<4||d<near[3][1]){near.push([i,d]);near.sort((a,b)=>a[1]-b[1]);if(near.length>4)near.pop();}}
      const ws=near.map(([i,d])=>[i,1/(Math.sqrt(d)+0.004)]),sw=ws.reduce((a,b)=>a+b[1],0),e=eqEval(D,ws.map(([i,w])=>[i,w/sw]));
      e.p=[x,y,z];e.n=[G.nrm[v*3],G.nrm[v*3+1],G.nrm[v*3+2]];e.r=[G.rest[v*3],G.rest[v*3+1],G.rest[v*3+2]];
      e.bones=new Map(G.skin[v].map(([b,w])=>[bi[b],w]));
      if(G.morph&&ctx.morphNames)e.dl=ctx.morphNames.map(nm=>{const a=G.morph[nm];return a?[a[v*3],a[v*3+1],a[v*3+2]]:[0,0,0];});   // shapes worked out on the full body
      eqVert(pc,e,0,cols[G.part[v]].map(c=>c*G.shade[v]));}
    for(const i of G.idx)pc.I.push(base+i);
    if(D.hide)for(const i of legs)if(D.rest[i*3+2]<G.hideZ)D.hide[i]=1;
    if(D.tuck)for(const i of legs){const z=D.rest[i*3+2];if(z<G.hideZ+0.05)D.tuck[i]=Math.max(D.tuck[i],0.02*(1-eqSm(G.hideZ+0.02,G.hideZ+0.05,z)));}   // what is left of the leg at the top draws in under the rim
    if(D.occ)for(const i of legs){if(D.rest[i*3+2]>G.hideZ+0.06)continue;let m=9;for(let v=0;v<n;v+=2){const d=Math.hypot(P[i*3]-G.pos[v*3],P[i*3+1]-G.pos[v*3+1],P[i*3+2]-G.pos[v*3+2]);if(d<m)m=d;}
      if(m<0.04&&m+0.004>D.occ[i])D.occ[i]=m+0.004;}
  },
  buttons(pc,D,item,dy,spec){pc.kind=12;const brass=eqRGB(dy[2]),xs=(spec&&spec.xs)||[0],z1=(spec&&spec.z1)||1.44;   // xs: columns (two for double-breasted)
    for(const x of xs)for(let z=(spec&&spec.z0)||0.98;z<z1;z+=0.055)eqStud(pc,D,eqNear(D,x,-0.2,z,2,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0),0.012,0.006,brass);},
  furcollar(pc,D,item,dy){pc.kind=6;const fur=eqRGB('#7a6248');
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,ax=Math.abs(r[i*3]),z_=r[i*3+2];if(D.arm[i]>0.5||z_>1.535)return -1;
      return Math.min(z_-1.43-0.02*eqSmooth([D.pos[i*3],D.pos[i*3+1],D.pos[i*3+2]],50),0.17-ax);})],
      e=>0.03+0.02*eqFur(e.p),(e,f,rim)=>fur.map(v=>v*(0.55+0.6*eqFur(e.p))),4,0.015);},
  // a smith's apron, the WoW way: a bib that lies on the chest, a thin strap round the neck, a tie at the waist, and below the
  // belt a leather panel that follows the legs like a robe's front
  apron(pc,D,item,dy,spec,ctx){pc.kind=3;const lea=eqRGB('#5a3a22'),strap=eqRGB('#3a2618'),r=D.rest,F=f=>[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.5?f(i):-1)];
    const col=(e,f,rim)=>rim?lea.map(v=>v*0.7):lea.map(v=>v*(0.9+0.1*eqNoise(e.p,25)));
    { // the bib: a smooth panel that lies on the chest and falls straight from the bust (or the chest) to the waist
      const P=D.pos,oc=D.occ||new Float32Array(D.n),front=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&r[i*3+1]<0.02&&r[i*3+2]>0.95&&r[i*3+2]<1.45)front.push(i);
      const yT=eqYAt(D,1.385),yW=eqYAt(D,0.995),NU=9,NV=9,W=t=>0.085+0.05*eqSm(0.15,0.9,t),Z=[];
      const fz=(x,y)=>{let z=-1e9;for(const i of front)if(Math.abs(P[i*3+1]-y)<0.035&&Math.abs(P[i*3]-x)<0.045)z=Math.max(z,P[i*3+2]+oc[i]);return z>-1e8?z:null;};
      for(let v=0;v<NV;v++){const t=v/(NV-1),y=yT+(yW-yT)*t;Z.push([...Array(NU)].map((_,u)=>fz((u/(NU-1)*2-1)*W(t),y)));}
      for(const row of Z){const have=row.map((z,u)=>z==null?null:u).filter(u=>u!=null);if(!have.length){row.fill(0.1);continue;}
        for(let u=0;u<NU;u++)if(row[u]==null){const n=have.reduce((a,b)=>Math.abs(b-u)<Math.abs(a-u)?b:a);row[u]=row[n];}}   // empty cells take the nearest filled one
      for(let u=0;u<NU;u++){let apex=0;for(let v=0;v<NV;v++)if(Z[v][u]>Z[apex][u])apex=v;for(let v=apex+1;v<NV;v++)Z[v][u]=Math.max(Z[v][u],Z[v-1][u]-0.002);}   // stiff leather: falls straight from the bust or chest, never back into the hollow beneath
      for(let pass=0;pass<3;pass++)for(let v=0;v<NV;v++){const row=Z[v].slice();for(let u=0;u<NU;u++)Z[v][u]=Math.max(row[u],(row[Math.max(0,u-1)]+2*row[u]+row[Math.min(NU-1,u+1)])/4);}
      const grid=[];
      for(let v=0;v<NV;v++){const t=v/(NV-1),y=yT+(yW-yT)*t,ids=[];
        for(let u=0;u<NU;u++){const x=(u/(NU-1)*2-1)*W(t),z=Z[v][u]+0.017,e=eqEval(D,[[eqNearPos(D,front,x,y,z),1]]);e.p=[x,y,z];e.n=[0,0,1];e.r=[x,-0.1,1.4-0.4*t];
          { const near=front.map(i=>[i,(D.pos[i*3]-x)**2+(D.pos[i*3+1]-y)**2]).sort((a,b)=>a[1]-b[1]).slice(0,10),ws=near.map(([i,d])=>[i,1/(Math.sqrt(d)+0.03)]),sw=ws.reduce((a,b)=>a+b[1],0);
            const avg=eqEval(D,ws.map(([i,w])=>[i,w/sw]));e.bones=avg.bones;
            e.dl=e.dl.map((d,j)=>{const m=near.slice(0,6).reduce((b,[i])=>{const v=D.morph[j][i*3+2];return Math.abs(v)>Math.abs(b)?v:b;},d[2]);return [d[0],d[1],Math.abs(m)>Math.abs(d[2])&&m>0?m:d[2]];}); }   // shapes: as deep as the deepest body beneath   // bends as the body beneath it does, smoothly
          ids.push(eqVert(pc,e,0,(u===0||u===NU-1||v===0)?lea.map(c=>c*0.75):lea.map(c=>c*(0.9+0.1*eqNoise(e.p,25)))));}
        grid.push(ids);}
      eqDrapeFinish(pc,grid,()=>[0,0,1],false);
      for(const row of grid)for(const id of row){const i=eqNearPos(D,front,pc.P[id*3],pc.P[id*3+1],pc.P[id*3+2]);if(D.occ&&D.occ[i]<0.012)D.occ[i]=0.012;}}
    eqShell(pc,D,F(i=>{const z=r[i*3+2],ax=Math.abs(r[i*3]);                                       // the neck strap: up from the bib, round the back of the neck
      const up=r[i*3+1]<0.01?Math.min(0.012-Math.abs(ax-0.075),z-1.37,1.49-z):-1, round=0.008-Math.abs(z-1.495)+(ax<0.09?0:-1);return Math.max(up,round);}),()=>0.004,()=>strap,1);
    eqShell(pc,D,F(i=>0.011-Math.abs(r[i*3+2]-0.995)),()=>0.004,()=>strap,1);                         // the waist tie
    EQ_BUILD.skirt(pc,D,item,dy,{top:0.99,hem:0.47,arc:[-1.0,1.0],ease:0.006,flare:0.15,kind:3,colour:lea,trimColour:lea.map(v=>v*0.7)},ctx);
  },
  headwrap(pc,D,item,dy){pc.kind=0;const main=eqRGB(dy[0]),dark=eqRGB(dy[1]);   // wound cloth over the crown and brow, the face left open
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,x=r[i*3],y=r[i*3+1],z_=r[i*3+2];if(D.arm[i]>0.5||z_<1.55)return -1;
      return Math.min(z_-(y<-0.02?1.705:1.62),1)})],
      e=>0.01+0.006*eqSm(1.7,1.82,e.r[2])+0.004*Math.sin(e.r[2]*180+Math.atan2(e.r[0],-e.r[1])*2),(e,f,rim)=>(rim?dark:main).map(v=>v*(0.86+0.14*Math.sin(e.r[2]*180+Math.atan2(e.r[0],-e.r[1])*2))),3);
    const tail=eqNear(D,0.02,0.2,1.64,3,i=>D.arm[i]<0.5&&D.rest[i*3+1]>0.0);eqBlock(pc,D,tail,0.05,0.16,0.012,0.02,main,0.9,0.09);},
  // ---- armour shells: cut from the body, so they ride its bones and never cross each other when walking ----
  // a leg harness: thigh plates (cuisses) over the front and sides, a domed cop over each knee, greaves all round the shin
  legplates(pc,D,item,dy,spec){const r=D.rest,F=f=>Float32Array.from({length:D.n},(_,i)=>f(i)),M=eqMetal(spec,dy);pc.kind=spec.leather?3:12;
    const leg=i=>D.arm[i]<0.5&&r[i*3+2]<0.93, sh=eqMetalShade(M);
    if(!spec.greavesOnly){
      eqShell(pc,D,[F(i=>leg(i)&&r[i*3+1]<0.035?Math.min(r[i*3+2]-0.555,0.86-r[i*3+2]):-1)],()=>0.016,sh,2);
      for(const sd of [1,-1])eqShell(pc,D,[F(i=>{if(!leg(i)||Math.sign(r[i*3])!==sd||r[i*3+1]>0.0)return -1;return 0.07-Math.hypot((Math.abs(r[i*3])-0.106)*0.85,r[i*3+2]-0.525);})],
        e=>0.02+0.014*eqSm(0.07,0,Math.hypot((Math.abs(e.r[0])-0.106)*0.85,e.r[2]-0.525)),sh,2);}
    eqShell(pc,D,[F(i=>leg(i)?Math.min(r[i*3+2]-0.15,(spec.greavesOnly?0.46:0.505)-r[i*3+2]):-1)],e=>(spec.leather?0.016:0.02)+0.006*eqSm(0.15,0.3,e.r[2]),sh,2);},
  // a breastplate and back plate, a ridge down the middle and a line where the belly plate (plackart) laps over
  cuirass(pc,D,item,dy,spec){const r=D.rest,M=eqMetal(spec,dy);pc.kind=12;
    const f=Float32Array.from({length:D.n},(_,i)=>{if(D.arm[i]>0.25)return -1;const ax=Math.abs(r[i*3]),z=r[i*3+2];return Math.min(z-0.985,1.458-0.35*Math.max(0,ax-0.07)-z,0.172-ax);});
    eqShell(pc,D,[f],e=>{const front=e.r[1]<0?1:0,ax=Math.abs(e.r[0]);return 0.018+front*0.016*(1-Math.min(1,(ax/0.17)**2))*eqSm(1.02,1.25,e.r[2])*(1-eqSm(1.38,1.45,e.r[2]));},
      (e,fv,rim)=>{if(rim)return M.dark;const z=e.r[2],ax=Math.abs(e.r[0]),k=(0.8+0.35*eqSm(0.12,0,ax))*(Math.abs(z-1.12)<0.007?0.62:1)*(ax<0.006&&e.r[1]<0?1.15:1);return M.main.map(v=>v*k);},3);
    if(false)eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.3?0.02-Math.abs(r[i*3+2]-0.975):-1)],()=>0.024,(e,fv,rim)=>rim?M.trim:M.main.map(v=>v*0.85),1);},   // a fauld round the hips
  // vambraces over the forearms, a raised ridge at the wrist
  vambrace(pc,D,item,dy,spec){const M=eqMetal(spec,dy);pc.kind=12;
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]>0.5?Math.min(D.t[i]-1.18,1.84-D.t[i])*0.25:-1)],e=>0.011+0.006*eqSm(1.7,1.84,eqArmT(e.r[0],e.r[2])),eqMetalShade(M),2);},
  // plate gauntlets: a shell over the hand and a flared cuff
  gauntlet(pc,D,item,dy,spec){const M=eqMetal(spec,dy);pc.kind=12;
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]>0.5?(D.t[i]-1.86)*0.25:-1)],()=>0.006,eqMetalShade(M),1);
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]>0.5?Math.min(D.t[i]-1.66,1.9-D.t[i])*0.25:-1)],e=>0.008+0.016*eqSm(1.88,1.68,eqArmT(e.r[0],e.r[2])),eqMetalShade(M),2);},
  // tassets: lames hanging from a war belt over the front of each thigh; they ride the thighs, so they never cross them
  tassets(pc,D,item,dy,spec){const r=D.rest,M=eqMetal(spec,dy);pc.kind=12;
    for(const sd of [1,-1])eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{if(D.arm[i]>0.5||Math.sign(r[i*3])!==sd||r[i*3+1]>0.0)return -1;const ax=Math.abs(r[i*3]);return Math.min(r[i*3+2]-0.76,0.975-r[i*3+2],ax-0.03,0.19-ax);})],
      e=>0.022+0,(e,fv,rim)=>rim?M.dark:M.main.map(v=>v*(Math.abs(((0.975-e.r[2])/0.055)%1-0.95)<0.06?0.6:0.9+0.15*eqSm(0,0.03,fv[0]))),2);},
  // helmets: a dome fitted to the scalp, lower behind; brim (kettle helm), cone and nose guard (nasal helm), goggles (Ferrin)
  helm(pc,D,item,dy,spec,ctx){pc.kind=12;const hb=ctx.bone('head'),i0=pc.P.length/3;const M=eqMetal(spec,dy),S=eqScalp(D),[cx,cy,cz]=S.c,[rx,ry,zf,zb]=S.r;
    const headPts=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+2]>1.5)headPts.push(i);
    const MM=22,K=8,yTop=S.top+0.03+(spec.cone?0.04:0),rimY=th=>cy+0.045-0.07*(1-Math.cos(th))/2,grid=[];
    const vert=(x,y,z,n,col)=>{const e=eqEval(D,[[eqNearPos(D,headPts,x,y,z),1]]);e.p=[x,y,z];e.n=n;e.r=[n[0]*0.1,-n[2]*0.1,1.6+(y-cy)];return eqVert(pc,e,0,col);};
    for(let k=0;k<=K;k++){const ang=k/K*Math.PI/2,ids=[];
      for(let m=0;m<MM;m++){const th=m/MM*Math.PI*2,sx=Math.sin(th),c=Math.cos(th),w=Math.sin(ang),y0=rimY(th);
        let y=y0+(yTop-y0)*Math.cos(ang);if(spec.cone)y+=0.03*Math.pow(Math.cos(ang),3)-0.02*Math.cos(ang)*w;
        const x=cx+sx*(rx+0.028)*w,z=cz+c*(c>0?zf+0.024:zb+0.03)*w;
        const rib=!spec.cone&&Math.abs(sx)<0.06&&k<K?1.18:1, col=M.main.map(v=>v*(0.82+0.3*Math.cos(ang)*0.7)*rib*(k===K?0.7:1));
        ids.push(vert(x,y,z,[sx,Math.cos(ang),c],col));}
      grid.push(ids);}
    if(spec.brim){for(const [out,dy_,sh] of [[0.065,-0.012,0.85],[0.06,-0.02,0.6],[0.004,-0.012,0.55]]){const ids=[];   // brim: out, its edge, back under
        for(let m=0;m<MM;m++){const th=m/MM*Math.PI*2,sx=Math.sin(th),c=Math.cos(th),y0=rimY(th)*0.4+(cy+0.03)*0.6;
          ids.push(vert(cx+sx*(rx+0.028+out),y0+dy_,cz+c*((c>0?zf+0.024:zb+0.03)+out),[sx,0.4,c],M.main.map(v=>v*sh)));}grid.push(ids);}}
    eqDrapeFinish(pc,grid,(q)=>[q[0]-cx,q[1]-cy+0.02,q[2]-cz],true);
    for(let i=i0;i<pc.P.length/3;i++)pc.SK[i]=new Map([[hb,1]]);   // rigid on the head, as WoW's helmets are
    const front=[cx,cy+0.02,cz+zf+0.03];
    if(spec.nasal){const rec=[[eqNearPos(D,headPts,front[0],front[1],front[2]),1]];eqBlock(pc,D,rec,0.016,0.075,0.006,0.026,M.main,1.05,0.0);}
    if(spec.goggles)for(const sx of [-1,1]){const rec=[[eqNearPos(D,headPts,cx+sx*0.034,cy+0.055,cz+zf),1]];
      eqBlock(pc,D,rec,0.036,0.03,0.016,0.03,M.trim,1.15);eqBlock(pc,D,rec,0.026,0.021,0.004,0.046,[0.18,0.35,0.3],1.4);}
    for(let i=i0;i<pc.P.length/3;i++)pc.SK[i]=new Map([[hb,1]]);},
  // signature pieces: what makes one townsperson recognisable in a crowd
  hat(pc,D,item,dy,spec,ctx){const hb0=ctx.bone('head'),i00=pc.P.length/3;pc.kind=spec.mat!==undefined?EQ_MAT[spec.mat]:1;const P=D.pos,head=[];   // a brimmed hat sized to the head
    for(let i=0;i<D.n;i++)if(D.rest[i*3+2]>1.56&&D.arm[i]<0.5)head.push(i);
    let top=-1e9;for(const i of head)top=Math.max(top,P[i*3+1]);
    const band=top-0.075,ring=head.filter(i=>Math.abs(P[i*3+1]-band)<0.012);
    const cx=ring.reduce((a,i)=>a+P[i*3],0)/ring.length,cz=ring.reduce((a,i)=>a+P[i*3+2],0)/ring.length;
    let r=0;for(const i of ring)r=Math.max(r,Math.hypot(P[i*3]-cx,P[i*3+2]-cz));
    const pin=head.reduce((b,i)=>P[i*3+1]>P[b*3+1]?i:b,head[0]),e0=eqEval(D,[[pin,1]]),col=eqRGB(dy[0]),bandc=eqRGB(spec.band||'#3a2618'),M=12;
    const ringAt=(rad,y,shade,col_)=>{const ids=[];for(let m=0;m<M;m++){const a=m/M*Math.PI*2,e={...e0,p:[cx+Math.sin(a)*rad,y,cz+Math.cos(a)*rad],n:[Math.sin(a),0.2,Math.cos(a)]};ids.push(eqVert(pc,e,0,col_.map(v=>v*shade)));}return ids;};
    const strip=(A,B)=>{for(let m=0;m<M;m++){const a=A[m],b=A[(m+1)%M],c=B[(m+1)%M],d=B[m];pc.I.push(a,b,c,a,c,d);}};
    const cap=(A,y,sh)=>{const ci=pc.P.length/3;eqVert(pc,{...e0,p:[cx,y,cz],n:[0,1,0]},0,col.map(v=>v*sh));for(let m=0;m<M;m++)pc.I.push(A[m],A[(m+1)%M],ci);};
    const brimO=ringAt(r+0.065,band-0.004,0.85,col),brimI=ringAt(r+0.004,band,0.95,col),b0=ringAt(r+0.006,band,1,bandc),b1=ringAt(r+0.008,band+0.022,1,bandc),c1=ringAt(r-0.004,band+0.075,1.05,col);
    strip(brimO,brimI);strip(b0,b1);strip(b1,c1);cap(c1,band+0.085,1.1);
    if(spec.feather){pc.kind=6;eqBlock(pc,D,[[pin,1]],0.012,0.11,0.004,0.02,eqRGB(spec.feather),1.1,-0.03);}
    for(let i=i00;i<pc.P.length/3;i++)pc.SK[i]=new Map([[hb0,1]]);},
  stick(pc,D,item,dy,spec,ctx){pc.kind=3;const P=D.pos,hand=[];   // a walking stick in the right hand, to the ground
    for(let i=0;i<D.n;i++)if(D.arm[i]>0.5&&D.rest[i*3]<0&&D.t[i]>2.25)hand.push(i);
    const c=[0,1,2].map(k=>hand.reduce((a,i)=>a+P[i*3+k],0)/hand.length),hb=ctx.bone('hand.R'),bones=new Map([[hb,1]]),e0={...eqEval(D,[[hand[0],1]]),bones};
    const M=6,r=0.013,col=eqRGB(spec.colour||'#5a3e26'),ring=y=>{const ids=[];for(let m=0;m<M;m++){const a=m/M*Math.PI*2;ids.push(eqVert(pc,{...e0,p:[c[0]+Math.sin(a)*r,y,c[2]+Math.cos(a)*r+0.01],n:[Math.sin(a),0,Math.cos(a)]},0,col.map(v=>v*(0.85+0.2*Math.cos(a)))));}return ids;};
    const A=ring(0.01),B=ring(c[1]+0.12);for(let m=0;m<M;m++){const a=A[m],b=A[(m+1)%M],cc=B[(m+1)%M],d=B[m];pc.I.push(a,b,cc,a,cc,d);}},
  scarf(pc,D,item,dy,spec){pc.kind=spec.mat!==undefined?EQ_MAT[spec.mat]:11;const z=D.rest,col=eqRGB(dy[0]);   // a knitted scarf, knotted in front
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.5&&Math.abs(z[i*3])<0.12?Math.min(z[i*3+2]-1.47,1.525-z[i*3+2]):-1)],
      e=>0.016+0.006*eqSmooth(e.p,40),(e,f,rim)=>col.map(v=>v*(rim?0.75:0.9+0.15*Math.sin(e.r[2]*400))),2);
    const k=eqNear(D,0.02,-0.2,1.47,2,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0);eqBlock(pc,D,k,0.04,0.035,0.02,0.012,col,0.95);eqBlock(pc,D,k,0.035,0.16,0.01,0.014,col,0.85,0.09);},
  earring(pc,D,item,dy){pc.kind=12;let best=-1,bx=-1;for(let i=0;i<D.n;i++){const r=D.rest;if(r[i*3+2]>1.62&&r[i*3+2]<1.68&&r[i*3]>bx&&D.arm[i]<0.5){bx=r[i*3];best=i;}}
    if(best>=0)eqBlock(pc,D,[[best,1]],0.008,0.016,0.004,0.002,eqRGB('#d8b060'),1.2,0.018);},
  // what hangs from a belt socket; an empty socket shows its brass ring
  attach(pc,D,item,dy,spec,ctx){pc.kind=3;const c=item.paint.a[0],w=item.paint.a[1]/2,rec=eqBeltPoint(D,c,EQ_SOCKETS[spec.socket].a),brass=eqRGB(item.paint.dyes[2]),th=0.007+(ctx&&ctx.torsoPad||0);
    const leather=eqRGB('#4a3020'),drop=w;
    if(!spec.what){eqBlock(pc,D,rec,0.016,0.02,0.004,th,brass,1.1,drop+0.004);return;}
    eqBlock(pc,D,rec,0.012,0.03,0.004,th,leather,0.8,drop);                                    // the strap from the belt
    if(spec.what==='pouch'){eqBlock(pc,D,rec,0.07,0.08,0.036,th,eqRGB('#6a4a2e'),1.0,drop+0.05);eqBlock(pc,D,rec,0.074,0.035,0.006,th+0.036,eqRGB('#5a3a22'),0.9,drop+0.027);
      eqBlock(pc,D,rec,0.01,0.01,0.004,th+0.042,brass,1.2,drop+0.04);}
    else if(spec.what==='flask'){eqCyl(pc,D,rec,0.026,0.075,th,drop+0.06,eqRGB('#8a6a46'),1.0);eqCyl(pc,D,rec,0.027,0.018,th-0.001,drop+0.05,eqRGB('#4a3020'),1.0);
      eqCyl(pc,D,rec,0.009,0.02,th+0.017,drop+0.012,eqRGB('#6a6e72'),1.1);eqCyl(pc,D,rec,0.007,0.012,th+0.019,drop+0.0,eqRGB('#a88458'),1.0);}
    else if(spec.what==='hammer'){eqCyl(pc,D,rec,0.008,0.2,th,drop+0.1,eqRGB('#6a4a2e'),1.0,6);pc.kind=12;eqBlock(pc,D,rec,0.07,0.032,0.03,th-0.01,eqRGB('#6a6e72'),1.1,drop+0.215);pc.kind=3;}
    else if(spec.what==='scroll'){eqCyl(pc,D,rec,0.019,0.12,th,drop+0.075,eqRGB('#5a3a22'),1.0);eqCyl(pc,D,rec,0.021,0.014,th-0.002,drop+0.022,brass,1.15);eqCyl(pc,D,rec,0.021,0.014,th-0.002,drop+0.128,brass,1.05);}
  },
  pouch(pc,D,item,dy){pc.kind=3;const rec=eqNear(D,-0.15,-0.05,0.955,3,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0.02),main=eqRGB(dy[0]);
    eqBlock(pc,D,rec,0.075,0.085,0.04,0.006,main,1.05); eqBlock(pc,D,rec,0.079,0.04,0.006,0.046,main,0.85);},
  laces(pc,D,item,dy){pc.kind=0;const open=item.paint.b[0],lace=eqRGB(dy[1]);
    for(let z=1.06;z<1.4;z+=0.045){const rec=eqNear(D,0,-0.2,z,2,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0);eqBlock(pc,D,rec,open*2*(0.4+0.6*eqSm(1.0,1.42,z))+0.012,0.005,0.004,0.003,lace,1);}},
  // a collar: a smooth band round the neck (rings measured from the neck itself), standing a little off it at the top, with
  // a thickness at its upper edge; skinned as the neck beneath it bends
  collar(pc,D,item,dy,spec){pc.kind=eqMatOf(item,spec,item.paint?EQ_KIND_MAT[EQ_KIND[item.paint.kind]]:0);const main=eqRGB(dy[spec.colour||0]),P=D.pos,R_=D.rest;
    const z0=1.49,z1=spec.high?1.56:1.53,M=20,neck=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&Math.abs(R_[i*3])<0.13&&R_[i*3+2]>z0-0.03&&R_[i*3+2]<z1+0.03)neck.push(i);
    const yAt=zt=>{const ys=neck.filter(i=>Math.abs(R_[i*3+2]-zt)<0.012).map(i=>P[i*3+1]).sort((a,b)=>a-b);return ys.length?ys[ys.length>>1]:null;};
    const rows=[[z0,0.005,1],[ (z0+z1)/2,0.008,1],[z1,0.012,1],[z1,0.004,0.7]],grid=[];
    for(const [zt,off,sh] of rows){const y=yAt(zt);if(y==null)continue;const band=neck.filter(i=>Math.abs(P[i*3+1]-y)<0.012);if(band.length<4)continue;
      const cx=band.reduce((a,i)=>a+P[i*3],0)/band.length,cz=band.reduce((a,i)=>a+P[i*3+2],0)/band.length,ids=[];
      for(let m=0;m<M;m++){const th=m/M*Math.PI*2;let r=0;for(const i of band){const x=P[i*3]-cx,z=P[i*3+2]-cz;let d=Math.atan2(x,z)-th;d=Math.atan2(Math.sin(d),Math.cos(d));if(Math.abs(d)<Math.PI/M*1.6)r=Math.max(r,Math.hypot(x,z));}
        r+=off+Math.min(0.02,...band.map(i=>D.occ?D.occ[i]:0));const x=cx+Math.sin(th)*r,z=cz+Math.cos(th)*r;
        const near=band.map(i=>[i,(P[i*3]-x)**2+(P[i*3+2]-z)**2]).sort((a,b)=>a[1]-b[1]).slice(0,6),ws=near.map(([i,d])=>[i,1/(Math.sqrt(d)+0.01)]),sw=ws.reduce((a,b)=>a+b[1],0);
        const e=eqEval(D,ws.map(([i,w])=>[i,w/sw]));e.p=[x,y,z];e.n=[Math.sin(th),0,Math.cos(th)];e.r=[Math.sin(th)*0.1,-Math.cos(th)*0.1,zt];
        ids.push(eqVert(pc,e,0,main.map(v=>v*sh*(0.95+0.05*Math.cos(th*5)))));}
      grid.push(ids);}
    if(grid.length>1)eqDrapeFinish(pc,grid,(q)=>[q[0],0,q[2]],true);},
  // pauldrons: stacked lames down the shoulder, each lighter at its crown and darker at its rim, with rivets along the lower
  // rims, an optional raised guard by the neck and an optional roll of fur over the top
  pauldron(pc,D,item,dy,spec){pc.kind=spec.metal?12:eqMatOf(item,spec,3);const metal=spec.metal,main=eqRGB(dy[0]),dark=eqRGB(dy[1]),trim=eqRGB(dy[2]),k=spec.size||1,N=spec.lames||2,r=D.rest;
    const cap=(L)=>({cx:0.205+0.02*L*k,cz:1.468-0.046*L*k,R:(0.122-0.016*L)*k,th:(metal?0.024:0.018)-0.004*L});   // each lame tucks under the one above
    const dist=(i,C)=>{const dx=Math.abs(r[i*3])-C.cx,dy_=(r[i*3+1]-0.02)*1.1,dz=r[i*3+2]-C.cz;return Math.sqrt(dx*dx+dy_*dy_+dz*dz);};
    const keep=i=>r[i*3+2]<1.53&&Math.abs(r[i*3])>0.125&&Math.abs(r[i*3+1]-0.02)<0.115;   // the outer shoulder only: not the chest, back or neck
    for(let L=0;L<N;L++){const C=cap(L),U=L?cap(L-1):null,f=Float32Array.from({length:D.n},(_,i)=>keep(i)?Math.min(C.R-dist(i,C),U?dist(i,U)-(U.R-0.03):1):-1);
      eqShell(pc,D,[f],e=>C.th+0.02*eqSm(0,C.R*0.9,C.R-Math.hypot(Math.abs(e.r[0])-C.cx,(e.r[1]-0.02)*1.1,e.r[2]-C.cz)),   // domed: highest at its crown
        (e,fv,rim)=>{if(rim)return (metal?dark:trim).map(v=>v*0.8);const t=eqSm(0,C.R*0.8,fv[0]);
          return main.map(v=>v*(metal?0.78+0.42*t:0.85+0.18*t)*(1-0.05*L)*(0.95+0.05*eqNoise(e.p,40)));},2);
      if(spec.rivets){const ring=[];for(let i=0;i<D.n;i++)if(keep(i)&&Math.abs(dist(i,C)-0.86*C.R)<0.009&&r[i*3+2]<C.cz-0.01)ring.push(i);
        const ang=i=>Math.atan2(r[i*3+1]-0.02,Math.abs(r[i*3])-C.cx);ring.sort((a,b)=>ang(a)-ang(b));
        const cnt=Math.min(5,ring.length);for(let q=0;q<cnt;q++){const i=ring[Math.floor((q+0.5)/cnt*ring.length)];eqStud(pc,D,[[i,1]],0.009,C.th+0.006,trim);}}}
    if(spec.ridge){const C=cap(0),f=Float32Array.from({length:D.n},(_,i)=>keep(i)&&Math.abs(r[i*3])<C.cx+0.01?0.008-Math.abs(dist(i,C)-(C.R-0.014)):-1);
      eqShell(pc,D,[f],()=>C.th+0.012,(e,fv,rim)=>(rim?dark:main).map(v=>v*(rim?0.8:1.12)));}
    if(spec.fur){pc.kind=6;const C=cap(0),fur=eqRGB('#7a6248'),f=Float32Array.from({length:D.n},(_,i)=>{const z_=r[i*3+2];if(z_>1.53||z_<C.cz-0.01||Math.abs(r[i*3+1]-0.02)>0.12)return -1;return 0.024-Math.abs(dist(i,C)-(C.R-0.012));});   // a roll of fur along the top edge
      eqShell(pc,D,[f],e=>C.th+0.022+0.012*eqFur(e.p),(e,fv,rim)=>fur.map(v=>v*(0.55+0.6*eqFur(e.p))),6,C.th);}
  },
  mantle(pc,D,item,dy){pc.kind=6;const main=eqRGB(dy[0]),dark=eqRGB(dy[1]),pos=D.pos;
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,ax=Math.abs(r[i*3]),z=r[i*3+2];if(z>1.505&&ax<0.1)return -1;
      const tuft=0.03*(eqSmooth([pos[i*3],pos[i*3+1],pos[i*3+2]],60)-0.5);                 // a ragged, tufted hem
      return D.arm[i]>0.5?(0.38-D.t[i])*0.25+tuft:Math.min(z-(1.385-0.05*eqSm(0.0,0.06,r[i*3+1]))+tuft,0.25-ax);})],
      e=>0.026+0.022*eqFur(e.p),(e,f,rim)=>{const k=eqFur(e.p),tip=eqSm(0,0.03,f[0]);return (rim?dark:main).map(v=>v*(0.55+0.55*k)*(0.8+0.25*tip));},3,0.02);},
  // a hood: a rounded dome fitted to the scalp, roomy enough for the hair (which is reshaped to fit, see eqHairFit), open at the
  // face, with a soft peak behind; below the jaw a cowl lies over the shoulders
  // a hood, the way WoW makes one: a rigid cowl on the head bone (it never stretches with the face or neck), fitted to this
  // head, its rim standing proud of the face so the face sits recessed, a dark lining inside and a rolled edge joining the two.
  // The hair beneath is hidden entirely (see dressOutfit). Over the shoulders, a short capelet rides the body.
  hood(pc,D,item,dy,spec,ctx){pc.kind=eqMatOf(item,null,1);const main=eqRGB(dy[0]),lin=eqRGB(dy[1]),S=eqScalp(D),[cx,cy,cz]=S.c,[rx,ry,zf,zb]=S.r,P=D.pos;
    const headBone=ctx.bone('head'),headPts=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+2]>1.5)headPts.push(i);
    const yTop=S.top+0.03,yBot=(eqYAt(D,1.505)??S.nape-0.08)-0.005,chin=cy-0.12,M=22,K=11,K1=6;
    let neckR=0.06;{const rs=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&Math.abs(D.rest[i*3])<0.075&&Math.abs(P[i*3+1]-yBot)<0.015)rs.push(Math.hypot(P[i*3]-cx,P[i*3+2]-cz));rs.sort((x,y)=>x-y);if(rs.length)neckR=rs[Math.floor(rs.length*0.8)];}
    const HX=0.028,HF=0.02,HB=0.04,EAR=y=>0.012*Math.exp(-Math.pow((y-(cy-0.025))/0.045,2));
    const mid=(S.top-0.035+chin)/2,half=(S.top-0.035-chin)/2,openW=y=>{const q=(y-mid)/half;return q>=1?-1:q>0?0.95*Math.sqrt(1-q*q):0.95;};
    const ring=(k)=>{let y,fx,fzF,fzB;
      if(k<=K1){const ang=k/K1*Math.PI/2;y=cy+(yTop-cy)*Math.cos(ang);const w=Math.sin(ang);fx=(rx+HX+EAR(y))*w;fzF=(zf+HF)*w;fzB=(zb+HB)*w;}
      else{const t=(k-K1)/(K-K1),e_=t*t*(3-2*t);y=cy+(yBot-cy)*t;const nr=neckR+0.03;fx=(rx+HX+EAR(y))+(nr-(rx+HX+EAR(y)))*e_*0.8;fzF=(zf+HF)+(nr+0.03-(zf+HF))*e_;fzB=(zb+HB)+(nr+0.02-(zb+HB))*e_*0.85;}
      return {y,fx,fzF,fzB,pk:k<=K1?Math.pow(Math.cos(k/K1*Math.PI/2),1.5):0};};
    // each ring runs round the head from one edge of the face opening to the other, so the opening is one smooth curve; where
    // there's no opening (the crown, under the chin) the ring closes on itself
    const place=[],openAt=[];
    for(let k=0;k<=K;k++){const R=ring(k),w=Math.max(0,openW(R.y)),row=[];openAt.push(w);
      for(let m=0;m<=M;m++){const th=w+(Math.PI*2-2*w)*m/M,sx=Math.sin(th),c=Math.cos(th);
        const near=w>0?eqSm(0.5,0,Math.abs(Math.atan2(sx,c))-w):0, lip=0.03*near*(c>0?1:0);   // the rim stands forward of the face
        row.push({p:[cx+sx*(R.fx+0.01*near),R.y+0.006*near,cz+c*(c>0?R.fzF:R.fzB)-0.035*R.pk*(c<0?1:0.5)+lip],n:[sx,k<=K1?Math.cos(k/K1*Math.PI/2):-0.3,c]});}
      place.push(row);}
    const mk=(q,n,col,inset)=>{const p=[q[0]-n[0]*inset,q[1]-n[1]*inset,q[2]-n[2]*inset];
      const e=eqEval(D,[[eqNearPos(D,headPts,p[0],p[1],p[2]),1]]);e.p=p;e.n=inset?n.map(v=>-v):n;e.bones=new Map([[headBone,1]]);
      e.r=[n[0]*0.1,-n[2]*0.1,1.5+(p[1]-yBot)];return eqVert(pc,e,0,col);};
    const outer=place.map(row=>row.map(v=>mk(v.p,v.n,main.map(x=>x*(0.9+0.1*eqNoise(v.p,20))),0)));
    const inner=place.map(row=>row.map(v=>mk(v.p,v.n,main.map(x=>x*0.32),0.009)));   // the lining, in shadow
    for(const g of [outer,inner])for(const row of g)for(const id of row){const l=Math.hypot(pc.N[id*3],pc.N[id*3+1],pc.N[id*3+2])||1;for(let q=0;q<3;q++)pc.N[id*3+q]/=l;}
    for(let k=0;k<K;k++)for(let m=0;m<M;m++){
      pc.I.push(outer[k][m],outer[k+1][m],outer[k+1][m+1],outer[k][m],outer[k+1][m+1],outer[k][m+1]);
      pc.I.push(inner[k][m],inner[k][m+1],inner[k+1][m+1],inner[k][m],inner[k+1][m+1],inner[k+1][m]);}
    const rimCol=lin.map(v=>v*0.75),rim=(A,B)=>{   // the rolled edge, outer to lining
      const ids=[outer[A[0]][A[1]],outer[B[0]][B[1]],inner[B[0]][B[1]],inner[A[0]][A[1]]].map(id=>{const n_=pc.P.length/3;pc.P.push(...pc.P.slice(id*3,id*3+3));pc.N.push(...pc.N.slice(id*3,id*3+3));pc.C.push(...rimCol);pc.DL.push(pc.DL[id]);pc.SK.push(pc.SK[id]);pc.RS.push(...pc.RS.slice(id*3,id*3+3));pc.K.push(pc.K[id]);return n_;});
      pc.I.push(ids[0],ids[1],ids[2],ids[0],ids[2],ids[3]);};
    for(let k=0;k<K;k++)if(openAt[k]>0.01||openAt[k+1]>0.01){rim([k,0],[k+1,0]);rim([k,M],[k+1,M]);}   // round the face
    for(let m=0;m<M;m++)rim([K,m],[K,m+1]);                                                             // the hem at the neck
    // the cowl: a short rounded capelet over the tops of the shoulders, cut in a curve
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,z=r[i*3+2];if(D.arm[i]>0.5)return -1;return Math.min(1.53-z,0.17-Math.hypot(Math.abs(r[i*3])*0.85,(1.53-z)*1.25));})],
      e=>0.008+0.012*eqSm(1.42,1.52,e.r[2]),(e,f,rim)=>rim?lin.map(v=>v*0.8):main.map(v=>v*(0.9+0.1*eqNoise(e.p,20))),6,0.01);},
  // a cloak: fastened across the shoulders, falling straight from the shoulder blades, clear of the legs at the hem; the
  // edges curl forward round the shoulders, and lower down it rides the hips, not the legs
  cloak(pc0,D,item,dy,spec,ctx){const pc=ctx.drapePiece();pc.kind=eqMatOf(item,spec,spec.woven?15:1);const main=eqRGB(dy[0]),P=D.pos,hips=ctx.bone('hips'),spine=ctx.bone('spine');
    const back=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+1]>-0.02&&D.rest[i*3+2]<1.53)back.push(i);
    const yT=eqYAt(D,1.47),yH=eqYAt(D,0.36);let wT=0;for(const i of back)if(Math.abs(P[i*3+1]-yT)<0.04)wT=Math.max(wT,Math.abs(P[i*3]));wT=Math.min(0.2,wT*0.84);   // across the shoulder blades, inside the swing of the arms
    const all=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+2]<1.53)all.push(i);
    const NU=11,NV=12,Z=[],W=t=>wT+0.06*Math.pow(t,1.2);
    const oc=D.occ||new Float32Array(D.n);
    const backZ=(x,y)=>{let z=1e9;for(const i of back)if(Math.abs(P[i*3+1]-y)<0.035&&Math.abs(P[i*3]-x)<0.06)z=Math.min(z,P[i*3+2]-oc[i]);return z;};
    const yW=eqYAt(D,1.0)||yT*0.6, over=ctx.underSkirt?0.035:0, plate=ctx.torsoPad||0;   // over a skirt or flap it stands off at the hips; over a back plate, all the way down
    for(let v=0;v<NV;v++){const t=v/(NV-1),y=yT+(yH-yT)*t,clear=0.02+0.04*eqSm(0,0.45,t)+0.07*Math.pow(eqSm(0.45,1,t),1.3)+(y<yW+0.05?over:0)+plate;
      Z.push([...Array(NU)].map((_,u)=>{const b=backZ((u/(NU-1)*2-1)*W(t),y);return b<1e8?b-clear:null;}));}
    for(const row of Z){const have=row.map((z,u)=>z==null?null:u).filter(u=>u!=null);   // columns with no body near them take the nearest that has one
      if(have.length)for(let u=0;u<NU;u++)if(row[u]==null){const n=have.reduce((a,b)=>Math.abs(b-u)<Math.abs(a-u)?b:a);row[u]=row[n];}}
    for(let v=0;v<NV;v++)for(let u=0;u<NU;u++){if(Z[v][u]==null)Z[v][u]=v?Z[v-1][u]:0;if(v)Z[v][u]=Math.min(Z[v-1][u],Z[v][u]);}   // it never moves back toward the body
    for(let pass=0;pass<2;pass++)for(let v=0;v<NV;v++){const row=Z[v].slice();for(let u=0;u<NU;u++)Z[v][u]=Math.min(row[u],(row[Math.max(0,u-1)]+row[u]*2+row[Math.min(NU-1,u+1)])/4);}
    const grid=[];
    for(let v=0;v<NV;v++){const t=v/(NV-1),y=yT+(yH-yT)*t,ids=[];
      for(let u=0;u<NU;u++){const uu=u/(NU-1)*2-1,x=uu*W(t);let y_=y,z=Z[v][u]+0.07*uu*uu*Math.pow(1-t,2)-0.014*Math.sin(uu*Math.PI*3.2)*eqSm(0.2,1,t);
        if(v===0){   // the top edge lies over the shoulders and round the back of the neck
          let ty=-1e9,zs=0,n=0;for(const i of all)if(Math.abs(P[i*3]-x)<0.04&&Math.abs(P[i*3+1]-yT)<0.09){ty=Math.max(ty,P[i*3+1]);}
          for(const i of all)if(Math.abs(P[i*3]-x)<0.04&&Math.abs(P[i*3+1]-ty)<0.02){zs+=P[i*3+2];n++;}
          if(n){y_=ty+0.012;z=Math.min(zs/n-0.01*(1-Math.abs(uu)),Z[1][u]+0.03);}}
        const e=eqEval(D,[[eqNearPos(D,back,x,y_,z),1]]);e.p=[x,y_,z];e.n=[0,0,-1];
        e.bones=eqMixBones(e.bones,new Map([[spine,0.25],[hips,0.75]]),eqSm(0.15,0.55,t));
        const fold=0.88+0.12*Math.cos(uu*Math.PI*2.5+t*1.2);ids.push(eqVert(pc,e,0,main.map(c=>c*fold*(v===NV-1?0.82:1))));}
      grid.push(ids);}
    eqDrapeFinish(pc,grid,()=>[0,0,-1],false); ctx.drapeGrid(pc,grid,false,2,1,true);
    for(const sx of [-1,1])eqBlock(pc0,D,eqNear(D,0.15*sx,-0.2,1.43,2,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0),0.022,0.022,0.008,0.006,eqRGB(dy[2]),1.2);},
};
// a character's whole set of built pieces, merged into one skinned mesh on the body's skeleton
function eqBuiltMesh(body,outfit,src,maxBuilt,sex){
  const D=eqBodyData(src||body),pc=eqPiece(),bones=body.skeleton.bones,san=n=>n.replace(/[\s\.\[\]:\/]/g,''),drapes=[];
  const mdict=(src||body).morphTargetDictionary||{};
  const ctx={sex,morphNames:Object.keys(mdict).sort((a,b)=>mdict[a]-mdict[b]),bone:n=>Math.max(0,bones.findIndex(b=>san(b.name)===san(n))),
    drapePiece:()=>{const d=eqPiece();drapes.push({pc:d});return d;},
    drapeGrid:(d,grid,closed,pinRows,reach,flat)=>{const e=drapes.find(x=>x.pc===d);e.grid=grid;e.closed=closed;e.pinRows=pinRows;e.reach=reach==null?1:reach;e.flat=!!flat;}};
  { const ch=eqItem('chest',outfit.chest),sh=eqItem('shirt',outfit.shirt),co=eqItem('coat',outfit.coat),low=it=>it&&(it.built||[]).some(sp=>sp.type==='skirt');
    ctx.underSkirt=low(ch)||low(sh)||low(co)||[ch,sh,co].some(it=>it&&(it.built||[]).some(sp=>sp.type==='drape'));
    ctx.legPad=Math.max(...['legs','waist'].map(sl=>(eqItem(sl,outfit[sl])||{}).legPad||0));   // armour on the legs: skirts and cloth make room
    ctx.torsoPad=0;
    ctx.longDrape=[ch,sh,co].some(it=>it&&(it.built||[]).some(sp=>sp.type==='drape'&&typeof EQ_DRAPES!=='undefined'&&((EQ_DRAPES.m||{})[sp.asset]||{}).hem<0.45)); }   // a breastplate: belts, buckles and cloaks sit over it
  D.occ=new Float32Array(D.n); D.hide=new Uint8Array(D.n); D.tuck=new Float32Array(D.n);
  let slots=EQ_BUILT_PRIORITY.filter(sl=>sl==='signature'?outfit.signature:(eqItem(sl,outfit[sl])||{}).built);
  if(maxBuilt!=null)slots=slots.slice(0,maxBuilt);
  slots.sort((a,b)=>EQ_LAYER_ORDER.indexOf(a)-EQ_LAYER_ORDER.indexOf(b));   // inside out
  for(const slot of slots){
    if(slot==='signature'){for(const sg of [].concat(outfit.signature))EQ_BUILD[sg.type](pc,D,{},[sg.colour||'#8a3a26',sg.colour||'#8a3a26','#c9a046'],sg,ctx);continue;}
    const it=eqItem(slot,outfit[slot]),dy=eqDyes(it,outfit.dye);
    for(const spec of it.built)EQ_BUILD[spec.type](pc,D,it,dy,spec,ctx);
    if(slot==='waist'&&it.sockets)for(const sk of it.sockets)EQ_BUILD.attach(pc,D,it,null,{socket:sk,what:(outfit.belt||{})[sk]||null},ctx);}
  // what the legs wear, measured from the layering: the cloth's leg capsules grow to match, so cloth clears boots and greaves too
  const pad={thigh:0,shin:0,foot:outfit.feet||outfit.shoes?0.018:0};
  for(let i=0;i<D.n;i++){if(D.arm[i]>0.5)continue;const z=D.rest[i*3+2],o=D.occ[i];if(z<0.12)pad.foot=Math.max(pad.foot,o);else if(z<0.5)pad.shin=Math.max(pad.shin,o);else if(z<0.9)pad.thigh=Math.max(pad.thigh,o);}
  const cloth=drapes.filter(d=>d.grid).map(d=>{const m=eqClothMesh(body,D,d);m.userData.cloth.pad=pad;return m;});
  const hide=D.hide,tuck=D.tuck; D.occ=null; D.hide=null; D.tuck=null;
  if(!pc.I.length)return {mesh:null,cloth,hide,tuck};
  const n=pc.P.length/3,g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(pc.P,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(pc.N,3));
  g.setAttribute('color',new THREE.Float32BufferAttribute(pc.C,3));
  const si=new Uint16Array(n*4),sw=new Float32Array(n*4);
  pc.SK.forEach((m,i)=>{const top=[...m].sort((a,b)=>b[1]-a[1]).slice(0,4),s=top.reduce((a,b)=>a+b[1],0)||1;top.forEach(([b,w],k)=>{si[i*4+k]=b;sw[i*4+k]=w/s;});});
  g.setAttribute('skinIndex',new THREE.BufferAttribute(si,4));g.setAttribute('skinWeight',new THREE.BufferAttribute(sw,4));
  g.morphAttributes.position=D.morph.map((_,j)=>{const a=new Float32Array(n*3);pc.DL.forEach((dl,i)=>{a[i*3]=dl[j][0];a[i*3+1]=dl[j][1];a[i*3+2]=dl[j][2];});return new THREE.BufferAttribute(a,3);});
  g.morphTargetsRelative=true; g.setIndex(pc.I); g.computeBoundingSphere();
  g.setAttribute('rest',new THREE.Float32BufferAttribute(pc.RS,3)); g.setAttribute('kind',new THREE.Float32BufferAttribute(pc.K,1));
  const m=new THREE.SkinnedMesh(g,eqOutfitMaterial());
  m.name='Outfit'; m.frustumCulled=false; m.castShadow=true; m.bind(body.skeleton,body.bindMatrix);
  m.morphTargetInfluences=body.morphTargetInfluences;   // the body's people and build shapes drive the outfit too
  return {mesh:m,cloth,hide,tuck};
}
/* ---------- cloth: skirts, cloaks and aprons, stepped each frame ---------- */
// Each drape is a small grid of points (a few hundred). Every frame each point is pulled toward where it would hang (skinned
// to the hips, spine or chest like the rest of the outfit), swings under gravity, is held to its neighbours, pushed out of
// capsules round the thighs and shins, kept from sinking into the body, and kept within reach of where it would hang. The
// top rows are fastened. This is what lets robes, coats and cloaks walk and run without the legs passing through them.
function eqClothMesh(body,D,d){
  const pc=d.pc,n=pc.P.length/3,g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.Float32BufferAttribute(pc.P.slice(),3).setUsage(THREE.DynamicDrawUsage));
  g.setAttribute('normal',new THREE.Float32BufferAttribute(pc.N.slice(),3));g.setAttribute('color',new THREE.Float32BufferAttribute(pc.C,3));
  g.setAttribute('rest',new THREE.Float32BufferAttribute(pc.RS,3));g.setAttribute('kind',new THREE.Float32BufferAttribute(pc.K,1));
  g.setIndex(pc.I);g.computeBoundingSphere();
  const m=new THREE.Mesh(g,eqOutfitMaterial(true));m.name='Cloth';m.frustumCulled=false;m.castShadow=true;
  // skin (top four bones), shape deltas, the hang of each point (0 fastened .. 1 hem), its neighbours
  const si=new Uint16Array(n*4),sw=new Float32Array(n*4);
  pc.SK.forEach((mp,i)=>{const top=[...mp].sort((a,b)=>b[1]-a[1]).slice(0,4),s=top.reduce((a,b)=>a+b[1],0)||1;top.forEach(([b,w],k)=>{si[i*4+k]=b;sw[i*4+k]=w/s;});});
  const dl=D.morph.map((_,j)=>{const a=new Float32Array(n*3);pc.DL.forEach((x,i)=>{a[i*3]=x[j][0];a[i*3+1]=x[j][1];a[i*3+2]=x[j][2];});return a;});
  const R_=d.grid.length,C_=d.grid[0].length,hang=new Float32Array(n),pin=new Uint8Array(n),edges=[];
  d.grid.forEach((row,r)=>row.forEach((id,c)=>{hang[id]=Math.max(0,(r-(d.pinRows-1))/Math.max(1,R_-d.pinRows));pin[id]=r<d.pinRows?1:0;
    if(r+1<R_)edges.push(id,d.grid[r+1][c],1);if(r+2<R_)edges.push(id,d.grid[r+2][c],0.3);
    if(c+1<C_)edges.push(id,row[c+1],0.6);else if(d.closed)edges.push(id,row[0],0.6);
    if(r+1<R_&&c+1<C_)edges.push(id,d.grid[r+1][c+1],0.25);}));
  m.userData.cloth={n,grid:d.grid,closed:d.closed,flat:d.flat,reach:d.reach,base:Float32Array.from(pc.P),nrm:Float32Array.from(pc.N),si,sw,dl,hang,pin,edges,pos:null,prev:null,len:null,T:new Float32Array(n*3),TN:new Float32Array(n*3)};
  return m;
}
const _cm=new THREE.Matrix4(),_cv=new THREE.Vector3(),_cw=new THREE.Vector3();
function eqLegCapsules(root,rig,inv){   // thigh and shin of each leg, in the figure's own space, with radii measured from the body
  const B=n=>{const o=root.getObjectByName(n);return o?o.getWorldPosition(new THREE.Vector3()).applyMatrix4(inv):null;},caps=[];
  for(const s of ['L','R']){const h=B('thigh'+s),k=B('shin'+s),f=B('foot'+s);if(!h||!k||!f)continue;caps.push([h.clone().lerp(k,0.12),k,'thigh'],[k,f,'shin'],[f.clone().add(new THREE.Vector3(0,0,-0.03)),f.clone().add(new THREE.Vector3(0,-0.04,0.08)),'foot']);}   // and the foot, heel to toe   // the thigh's capsule starts below the hip joint, which lies deep in the pelvis
  const sig=rig.body.morphTargetInfluences.map(v=>v.toFixed(2)).join();
  if(!rig.legR||rig.legRSig!==sig){   // measure: the body's own leg points, skinned now, against these segments
    const D=eqBodyData(rig.lightSrc||rig.body),sk=rig.body.skeleton,inf=rig.body.morphTargetInfluences,ds={thigh:[],shin:[]};
    const M=sk.bones.map((b,i)=>new THREE.Matrix4().multiplyMatrices(inv,b.matrixWorld).multiply(sk.boneInverses[i]).multiply(rig.body.bindMatrix));
    for(let i=0;i<D.n;i+=2){const z=D.rest[i*3+2];if(D.arm[i]>0.5||z>0.86||z<0.12)continue;
      _cv.set(D.pos[i*3],D.pos[i*3+1],D.pos[i*3+2]);for(let j=0;j<D.morph.length;j++)if(inf[j])_cv.x+=D.morph[j][i*3]*inf[j],_cv.y+=D.morph[j][i*3+1]*inf[j],_cv.z+=D.morph[j][i*3+2]*inf[j];
      _cw.set(0,0,0);for(let k=0;k<4;k++){const w=D.sw[i*4+k];if(w>0)_cw.addScaledVector(_cv.clone().applyMatrix4(M[D.si[i*4+k]]),w);}
      let best=1e9,kind='thigh';for(const [a,b,kd] of caps){const t=Math.max(0,Math.min(1,_cw.clone().sub(a).dot(b.clone().sub(a))/b.distanceToSquared(a)));const dd=_cw.distanceTo(a.clone().lerp(b,t));if(dd<best){best=dd;kind=kd;}}
      if(best<0.2)ds[kind].push(best);}
    const q=a=>{a.sort((x,y)=>x-y);return a.length?a[Math.floor(a.length*0.6)]:0.07;};
    rig.legR={thigh:q(ds.thigh),shin:q(ds.shin),foot:0.05};rig.legRSig=sig;}
  return caps.map(([a,b,kd])=>({a,b,kind:kd,r:rig.legR[kd]+0.008}));
}
function eqClothUpdate(root,dt){
  const rig=root.userData.rig; if(!rig||!rig.cloth||!rig.cloth.length)return;
  dt=Math.min(dt,1/20); const body=rig.body,sk=body.skeleton,inf=body.morphTargetInfluences;
  if(rig.clothSim===false&&dt>0&&(rig.clothTick=(rig.clothTick||0)+1)%2)return;   // background figures: every other frame is enough
  root.updateMatrixWorld(true); const inv=new THREE.Matrix4().copy(root.matrixWorld).invert(), sc=root.scale.y||1;
  const M=sk.bones.map((b,i)=>new THREE.Matrix4().multiplyMatrices(inv,b.matrixWorld).multiply(sk.boneInverses[i]).multiply(body.bindMatrix));
  const caps=eqLegCapsules(root,rig,inv);
  // the figure's own movement, felt by the cloth as inertia (it trails a little when walking)
  const wp=root.getWorldPosition(new THREE.Vector3()), last=rig.clothLast||wp.clone(), mv=wp.clone().sub(last).applyQuaternion(root.getWorldQuaternion(new THREE.Quaternion()).invert()).divideScalar(sc);
  rig.clothLast=wp; if(mv.length()>0.5)mv.set(0,0,0);
  const steps=dt>1/45?2:1, h=dt/steps, grav=9.8*h*h/sc;
  for(const mesh of rig.cloth){const C=mesh.userData.cloth,n=C.n,T=C.T,TN=C.TN;
    for(let i=0;i<n;i++){   // where each point would hang, and which way is out
      let x=C.base[i*3],y=C.base[i*3+1],z=C.base[i*3+2];for(let j=0;j<C.dl.length;j++)if(inf[j]){x+=C.dl[j][i*3]*inf[j];y+=C.dl[j][i*3+1]*inf[j];z+=C.dl[j][i*3+2]*inf[j];}
      let tx=0,ty=0,tz=0,nx=0,ny=0,nz=0;
      for(let k=0;k<4;k++){const w=C.sw[i*4+k];if(!w)continue;const e=M[C.si[i*4+k]].elements;
        tx+=w*(e[0]*x+e[4]*y+e[8]*z+e[12]);ty+=w*(e[1]*x+e[5]*y+e[9]*z+e[13]);tz+=w*(e[2]*x+e[6]*y+e[10]*z+e[14]);
        const a=C.nrm[i*3],b=C.nrm[i*3+1],c=C.nrm[i*3+2];nx+=w*(e[0]*a+e[4]*b+e[8]*c);ny+=w*(e[1]*a+e[5]*b+e[9]*c);nz+=w*(e[2]*a+e[6]*b+e[10]*c);}
      const l=Math.hypot(nx,ny,nz)||1;T[i*3]=tx;T[i*3+1]=ty;T[i*3+2]=tz;TN[i*3]=nx/l;TN[i*3+1]=ny/l;TN[i*3+2]=nz/l;}
    if(!C.pos){C.pos=Float32Array.from(T);C.prev=Float32Array.from(T);C.len=[];for(let e=0;e<C.edges.length;e+=3){const a=C.edges[e],b=C.edges[e+1];C.len.push(Math.hypot(T[a*3]-T[b*3],T[a*3+1]-T[b*3+1],T[a*3+2]-T[b*3+2]));}}
    // where it hangs, moved out of the legs' way: each point's deficit along its outward direction to clear any leg beside it,
    // spread along its row (a cloak or apron row moves as one; a skirt's points share with their neighbours), never less
    // than the row above. The cloth is then never asked to be inside a leg, so it doesn't fight the legs.
    // the outward direction for leg clearance: a cloak or apron row shares one (its edges curl round, which would push sideways)
    const ON=C.ON||(C.ON=new Float32Array(n*3));
    if(C.flat){for(const row of C.grid){let x=0,y=0,z=0;for(const id of row){x+=TN[id*3];y+=TN[id*3+1];z+=TN[id*3+2];}const l=Math.hypot(x,z)||1;for(const id of row){ON[id*3]=x/l;ON[id*3+1]=0;ON[id*3+2]=z/l;}}}
    else for(let i=0;i<n;i++){const x=TN[i*3],z=TN[i*3+2],l=Math.hypot(x,z)||1;ON[i*3]=x/l;ON[i*3+1]=0;ON[i*3+2]=z/l;}   // skirts clear the legs sideways, never downward
    if(caps.length){const G=C.grid,R_=G.length,dv=new Float32Array(n);
      for(let i=0;i<n;i++){if(C.pin[i])continue;const k3=i*3;let need=0;
        for(const c of caps){const cr=c.r+(C.pad?C.pad[c.kind]:0.02)+0.006,ax=c.a.x,ay=c.a.y,az=c.a.z,bx=c.b.x-ax,by=c.b.y-ay,bz=c.b.z-az;
          if(Math.abs(by)<1e-4)continue;const u=(T[k3+1]-ay)/by;if(u<-0.05||u>1.05)continue;const uu=Math.max(0,Math.min(1,u));
          const lx=ax+bx*uu-T[k3],lz=az+bz*uu-T[k3+2],along=lx*ON[k3]+lz*ON[k3+2],lat=Math.hypot(lx-ON[k3]*along,lz-ON[k3+2]*along);
          if(lat<cr+0.04)need=Math.max(need,along+cr*Math.sqrt(Math.max(0,1-Math.pow(lat/(cr+0.04),2))));}
        dv[i]=need;}
      for(let r=0;r<R_;r++){const row=G[r];
        if(C.flat){let m=0;for(const id of row)m=Math.max(m,dv[id]);for(const id of row)dv[id]=m;}
        else{const v=row.map(id=>dv[id]),L_=row.length,nb=c=>C.closed?[(c+L_-1)%L_,(c+1)%L_]:[Math.max(0,c-1),Math.min(L_-1,c+1)];
          for(let c=0;c<L_;c++){const [a,b]=nb(c);dv[row[c]]=Math.max(v[c],0.7*Math.max(v[a],v[b]));}}
        if(r>0)for(let c=0;c<row.length;c++)dv[row[c]]=Math.max(dv[row[c]],dv[G[r-1][c]]*0.9);}
      for(let i=0;i<n;i++)if(dv[i]>0){T[i*3]+=ON[i*3]*dv[i];T[i*3+1]+=ON[i*3+1]*dv[i]*0.3;T[i*3+2]+=ON[i*3+2]*dv[i];}}
    const P=C.pos,Q=C.prev;
    if(rig.clothSim===false){P.set(T);Q.set(T);}   // background figures: the cloth just follows the hips and thighs
    else for(let st=0;st<steps;st++){
      for(let i=0;i<n;i++){const k3=i*3;
        if(C.pin[i]){P[k3]=Q[k3]=T[k3];P[k3+1]=Q[k3+1]=T[k3+1];P[k3+2]=Q[k3+2]=T[k3+2];continue;}
        const t=C.hang[i],pull=0.1*(1-t)+0.03;
        for(let a=0;a<3;a++){const v=(P[k3+a]-Q[k3+a])*0.9;Q[k3+a]=P[k3+a];P[k3+a]+=v+(T[k3+a]-P[k3+a])*pull-(a===0?mv.x:a===1?mv.y:mv.z)*0.5/steps;}
        P[k3+1]-=grav;}
      for(let it=0;it<4;it++){
        for(let e=0,q=0;e<C.edges.length;e+=3,q++){const a=C.edges[e],b=C.edges[e+1],s=C.edges[e+2],pa=C.pin[a],pb=C.pin[b];if(pa&&pb)continue;
          const dx=P[b*3]-P[a*3],dy=P[b*3+1]-P[a*3+1],dz=P[b*3+2]-P[a*3+2],L=Math.hypot(dx,dy,dz)||1e-6,f=(L-C.len[q])/L*s;
          const wa=pa?0:pb?1:0.5,wb=pb?0:pa?1:0.5;
          P[a*3]+=dx*f*wa;P[a*3+1]+=dy*f*wa;P[a*3+2]+=dz*f*wa;P[b*3]-=dx*f*wb;P[b*3+1]-=dy*f*wb;P[b*3+2]-=dz*f*wb;}
        for(let i=0;i<n;i++){if(C.pin[i])continue;const k3=i*3,t=C.hang[i];
          const ox=P[k3]-T[k3],oy=P[k3+1]-T[k3+1],oz=P[k3+2]-T[k3+2],into=ox*TN[k3]+oy*TN[k3+1]+oz*TN[k3+2];   // never into the body
          if(into<-0.004){const f=-0.004-into;P[k3]+=TN[k3]*f;P[k3+1]+=TN[k3+1]*f;P[k3+2]+=TN[k3+2]*f;}
          const md=0.02+0.3*t*C.reach,dd=Math.hypot(P[k3]-T[k3],P[k3+1]-T[k3+1],P[k3+2]-T[k3+2]);   // within reach of where it would hang
          if(dd>md){const f=md/dd;for(let a=0;a<3;a++)P[k3+a]=T[k3+a]+(P[k3+a]-T[k3+a])*f;}
          // the legs have the last word: whatever the other rules did, cloth ends outside them
          for(const c of caps){   // round the legs, one-sided and horizontal: at its own height, cloth ends on its outer side of each leg
            const ax=c.a.x,ay=c.a.y,az=c.a.z,bx=c.b.x-ax,by=c.b.y-ay,bz=c.b.z-az,wt=Math.min(1,t*3);
            if(!wt||Math.abs(by)<1e-4)continue; const u=(P[k3+1]-ay)/by; if(u<-0.05||u>1.05)continue; const uu=Math.max(0,Math.min(1,u));
            const cr=c.r+(C.pad?C.pad[c.kind]:0.02),ox_=P[k3]-(ax+bx*uu),oz_=P[k3+2]-(az+bz*uu),nx=ON[k3],nz=ON[k3+2],nl=Math.hypot(nx,nz)||1;
            const side=(ox_*nx+oz_*nz)/nl,lat=Math.abs((ox_*nz-oz_*nx)/nl);
            if(lat>=cr||side<-(cr+0.06))continue;
            const need=Math.sqrt(cr*cr-lat*lat);
            if(side<need){const f=(need-side)*wt/nl;P[k3]+=nx*f;P[k3+2]+=nz*f;}}
        }}}
    const A=mesh.geometry.attributes.position;A.array.set(P);A.needsUpdate=true;mesh.geometry.computeVertexNormals();
  }
}
// Remove the body under built pieces (hide: per point of the light body the pieces were built on). The figure gets its own
// view of the body: the same points, shapes and skin, a shorter triangle list.
function eqHideBody(rig,hide,tuck){
  const body=rig.body, g0=rig.bodyGeo0||(rig.bodyGeo0=body.geometry);
  if(body.geometry!==g0){body.geometry.dispose();body.geometry=g0;}
  const hasT=tuck&&tuck.some(v=>v>0);
  if(!hasT&&g0.attributes.tuck)g0.attributes.tuck.array.fill(0),g0.attributes.tuck.needsUpdate=true;
  if(!hasT&&(!hide||!hide.some(v=>v)))return;
  const src=rig.lightSrc||body, L=eqBodyData(src);
  let map=g0.userData.toLight;                                // each body point's nearest point on the light body, by template place
  if(!map||map.src!==L){const R0=g0.attributes.rest.array,n=g0.attributes.rest.count;map=new Int32Array(n);
    if(src===body)for(let i=0;i<n;i++)map[i]=i;
    else for(let i=0;i<n;i++){let b=0,bd=1e9;const x=R0[i*3],y=R0[i*3+1],z=R0[i*3+2];
      for(let j=0;j<L.n;j++){const dx=L.rest[j*3]-x,dy=L.rest[j*3+1]-y,dz=L.rest[j*3+2]-z,d=dx*dx+dy*dy+dz*dz;if(d<bd){bd=d;b=j;}}map[i]=b;}
    map.src=L;g0.userData.toLight=map;}
  if(hasT){const n=map.length;if(!g0.attributes.tuck)g0.setAttribute('tuck',new THREE.BufferAttribute(new Float32Array(n),1));
    const ta=g0.attributes.tuck.array;for(let i=0;i<n;i++)ta[i]=tuck[map[i]];g0.attributes.tuck.needsUpdate=true;}
  if(!hide||!hide.some(v=>v))return;
  const I0=g0.index.array,keep=[];
  for(let t=0;t<I0.length;t+=3)if(!(hide[map[I0[t]]]&&hide[map[I0[t+1]]]&&hide[map[I0[t+2]]]))keep.push(I0[t],I0[t+1],I0[t+2]);
  const g=new THREE.BufferGeometry();for(const k in g0.attributes)g.setAttribute(k,g0.attributes[k]);
  g.morphAttributes=g0.morphAttributes;g.morphTargetsRelative=g0.morphTargetsRelative;g.userData=g0.userData;
  g.setIndex(keep);g.boundingSphere=g0.boundingSphere;g.boundingBox=g0.boundingBox;body.geometry=g;
}
// Hat hair: headgear doesn't hide the hair, it reshapes it to fit, as games commonly do. Each hairstyle is worked out once per
// kind of headgear (and cached on its geometry) against an ellipsoid fitted to the scalp:
//  hat: hair above the hatband is pressed onto the scalp inside the crown; below the brim it is left as it is
//  hood: hair is pressed close to the scalp, and long hair below the skull is folded up into the nape, inside the hood
//  wrap: hair under the wrap is pressed flat; long hair still hangs out below it
function eqScalp(D){
  if(D.scalp)return D.scalp; const P=D.pos,pts=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+2]>1.56)pts.push(i);
  const q=(arr,f)=>{arr=arr.slice().sort((a,b)=>a-b);return arr[Math.min(arr.length-1,Math.floor(arr.length*f))];};
  const ys=pts.map(i=>P[i*3+1]),top=Math.max(...ys),eyeY=q(pts.filter(i=>Math.abs(D.rest[i*3+2]-1.69)<0.015).map(i=>P[i*3+1]),0.5)||top-0.12;
  const crown=pts.filter(i=>P[i*3+1]>eyeY-0.02),cx=0,cz=(Math.max(...crown.map(i=>P[i*3+2]))+Math.min(...crown.map(i=>P[i*3+2])))/2;
  const rx=q(crown.map(i=>Math.abs(P[i*3]-cx)),0.9),zf=q(crown.map(i=>P[i*3+2]-cz),0.97),zb=-q(crown.map(i=>P[i*3+2]-cz),0.03);
  let nape=null;{const ns=[];for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&D.rest[i*3+1]>0&&Math.abs(D.rest[i*3+2]-1.62)<0.015)ns.push(P[i*3+1]);ns.sort((a,b)=>a-b);nape=ns.length?ns[ns.length>>1]:eyeY-0.08;}
  return D.scalp={c:[cx,eyeY,cz],r:[rx,top-eyeY,zf,zb],top,eyeY,nape,bottom:Math.min(...ys)};
}
function eqHairFit(geo,mode,S){
  const base=geo.userData.hairBase||geo; base.userData.fits=base.userData.fits||{};
  const key=mode+':'+S.top.toFixed(3); if(base.userData.fits[key])return base.userData.fits[key];
  const g=base.clone(), A=g.attributes.position, [cx,cy,cz]=S.c, [rx,ry,zf,zb]=S.r, band=mode==='helm'?cy+0.03:S.top-0.075;
  if(mode==='helm')mode='hat';   // a helmet: like a hat, but its rim sits lower, at the brow
  const lim=mode==='hat'?1.04:mode==='wrap'?1.05:1.1;
  for(let i=0;i<A.count;i++){let x=A.getX(i),y=A.getY(i),z=A.getZ(i);
    const w=mode==='hat'?eqSm(band-0.03,band+0.005,y):mode==='wrap'?eqSm(S.nape-0.02,S.nape+0.015,y):1;
    if(mode==='hood'&&y<S.nape){const k=eqSm(S.nape,S.nape-0.25,y);y=S.nape-(S.nape-y)*(1-0.85*k);x=cx+(x-cx)*(1-0.45*k);z=cz+(z-cz)*(1-0.3*k)+0.02*k;}   // long hair folds up into the nape
    if(w>0){const dx=(x-cx)/rx,dy=Math.max(0,y-cy)/ry,dz=(z-cz)/(z>cz?zf:zb),sN=Math.hypot(dx,dy,dz);
      if(sN>lim){const k=lim/sN;const nx=cx+(x-cx)*k,ny=y>cy?cy+(y-cy)*k:y,nz=cz+(z-cz)*k;x+=(nx-x)*w;y+=(ny-y)*w;z+=(nz-z)*w;}}
    if(mode==='hat'&&y>band+0.07)y=band+0.07;
    A.setXYZ(i,x,y,z);}
  // like WoW, hair under the headgear is removed, not squashed: under a hat or helmet everything above the rim; under a wrap
  // everything above the nape; under a hood all but the fringe in the face opening
  const O=base.attributes.position, keep=i=>{const x=O.getX(i),y=O.getY(i),z=O.getZ(i);
    if(mode==='hat')return y<band+0.02; if(mode==='wrap')return y<S.nape+0.01;
    return z>cz+zf*0.45&&y>cy&&y<S.top-0.03&&Math.abs(x-cx)<rx*0.8;};
  const I=base.index?Array.from(base.index.array):[...Array(O.count).keys()], kept=[];
  for(let t=0;t<I.length;t+=3)if(keep(I[t])||keep(I[t+1])||keep(I[t+2]))kept.push(I[t],I[t+1],I[t+2]);
  g.setIndex(kept);
  A.needsUpdate=true; g.computeBoundingSphere(); g.userData.hairBase=base;
  return base.userData.fits[key]=g;
}
// Built pieces are coloured per point; this adds the fine surface per fragment: fur strands, leather grain and creases, brushed
// metal with a stronger highlight, cloth weave.
function eqOutfitMaterial(cloth){
  const m=new THREE.MeshPhongMaterial({vertexColors:true,skinning:!cloth,morphTargets:!cloth,shininess:24,specular:0x2a2a2a,side:THREE.DoubleSide}); m.extensions={derivatives:true};
  m.onBeforeCompile=sh=>{ sh.uniforms.uGear={value:EQ_GEAR}; sh.uniforms.uMatScale={value:EQ_MAT_SCALE};
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nattribute vec3 rest;attribute float kind;varying vec3 vRs;varying float vK;')
      .replace('#include <begin_vertex>','#include <begin_vertex>\nvRs=rest;vK=kind;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>',`#include <common>
varying vec3 vRs;varying float vK;
float oh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float on(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(oh(i),oh(i+vec2(1.,0.)),f.x),mix(oh(i+vec2(0.,1.)),oh(i+vec2(1.,1.)),f.x),f.y);}
uniform sampler2D uGear; uniform float uMatScale[16];
float gearTile(float tile,vec2 uv){vec2 o=vec2(mod(tile,4.),floor(tile/4.)),f=fract(uv)*0.2421875+0.00390625,t=vec2(o.x*0.25+f.x,1.-(o.y*0.25+f.y));
#if __VERSION__ >= 300
  vec2 g=uv*0.2421875; return textureGrad(uGear,t,dFdx(g),dFdy(g)).r;
#else
  return texture2D(uGear,t).r;
#endif
}`)
      .replace('#include <color_fragment>',`#include <color_fragment>
  { float kc=floor(vK+0.5),tile=mod(kc,16.),pat=floor(kc/16.); vec2 a=vec2(atan(vRs.x,-vRs.y)*0.16,vRs.z)/uMatScale[int(tile)];
    float g=2.*gearTile(tile,a); vec2 s=vec2(atan(vRs.x,-vRs.y)*0.15,vRs.z);
    if(pat>0.5&&pat<1.5) g*=1.-0.28*step(0.32,abs(fract(s.x/0.03)-0.5));                                   // stripes
    else if(pat>1.5&&pat<2.5){float u=step(0.38,abs(fract(s.x/0.05)-0.5)),v=step(0.38,abs(fract(s.y/0.05)-0.5));g*=1.-0.22*max(u,v)-0.1*u*v;}   // check
    else if(pat>3.5){float q=abs(fract((s.x+s.y)/0.06)-0.5),r=abs(fract((s.x-s.y)/0.06)-0.5);g*=1.-0.22*(1.-smoothstep(0.03,0.05,min(q,r)));}   // quilted
    if(tile>5.5&&tile<6.5) g*=0.75+0.5*on(vec2(a.x*60.+on(a*vec2(6.,12.))*3.,a.y*8.));                   // fur: strands running down
    diffuseColor.rgb*=g; if(!gl_FrontFacing)diffuseColor.rgb*=0.45; }`)
      .replace('#include <specularmap_fragment>','#include <specularmap_fragment>\n  { float tile=mod(floor(vK+0.5),16.); specularStrength=(tile>11.5&&tile<14.5)?1.3:(tile>5.5&&tile<6.5)?0.12:(tile>7.5&&tile<8.5)?0.9:(tile>2.5&&tile<5.5)?0.45:0.14; }');
  };
  m.customProgramCacheKey=()=>cloth?'eq-cloth':'eq-outfit'; return m;
}
// dress a figure: bake its paint and painted armour, and build its built armour
// rig.lightSrc (optional): the distance body's mesh; built pieces are cut from it, so they stay light.
// opts: size (the baked texture, default 1024), maxBuilt (how many slots may have built pieces, in EQ_BUILT_PRIORITY order)
const EQ_LAYER_ORDER=['shoes','feet','legs','hands','wrists','chest','coat','waist','shoulders','back','head','signature'];
const EQ_BUILT_PRIORITY=['coat','chest','back','head','waist','feet','shoes','legs','shoulders','hands','wrists','signature'];
function dressOutfit(root,look,outfit,renderer,bakeOnly,opts){
  opts=opts||{}; outfit=eqNormalize(outfit);
  const rig=root.userData.rig; if(!rig||!rig.body.geometry.attributes.uv)return;   // bodies without a texture layout keep live paint
  if(!EQ_GEAR.image)EQ_GEAR_WAIT.push(()=>dressOutfit(root,look,outfit,renderer,true,opts));
  const body=rig.body, tex=EqBake.bake(renderer,body,look,outfit,opts.size||1024);
  if(!body.userData.baked||body.material.map!==tex){body.material=bakedMaterial(tex);body.userData.baked=true;} else body.material.needsUpdate=true;
  if(bakeOnly)return;
  if(rig.outfit){rig.outfit.parent.remove(rig.outfit);rig.outfit.geometry.dispose();rig.outfit=null;}
  for(const c of rig.cloth||[]){c.parent.remove(c);c.geometry.dispose();} rig.cloth=[]; rig.clothSim=opts.cloth!==false;
  const built=eqBuiltMesh(body,outfit,rig.lightSrc,opts.maxBuilt,look&&(look.sex||(look.fem?"f":"m")));
  eqHideBody(rig,built&&built.hide,built&&built.tuck);
  if(built){if(built.mesh){body.parent.add(built.mesh);rig.outfit=built.mesh;} for(const c of built.cloth){root.add(c);rig.cloth.push(c);}}
  eqClothUpdate(root,0);
  // hat hair: reshape the hairstyle to the headgear (beards and moustaches stay as they are)
  const head=eqItem('head',outfit.head), hat=[].concat(outfit.signature||[]).some(sg=>sg&&sg.type==='hat');
  const mode=head&&head.hair?head.hair:hat?'hat':null, S=mode?eqScalp(eqBodyData(rig.lightSrc||body)):null;
  root.traverse(o=>{if(!o.isMesh||!o.name.startsWith('Hair_'))return;const base=o.geometry.userData.hairBase||o.geometry;
    if(mode==='hide'){o.geometry=base;o.visible=false;return;}   // full helms and hoods hide the hair, as WoW's do
    o.geometry=mode?eqHairFit(base,mode,S):base;});
}
