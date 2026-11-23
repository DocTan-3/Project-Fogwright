// Fogwright equipment: World of Warcraft-style gear on the painted bodies. Load after bodypaint.js.
// Painted armour: each slot is a paint layer, laid on in a fixed order, then the whole character (skin, face, underclothes and
// every layer) is baked into one texture in the body's texture layout (tools/blender/uvbody.py). Built armour: pieces cut
// from the body's own surface and pushed outward, so they carry its skin weights and every people and build shape.
'use strict';

/* ---------- 1. the slots, and the order their paint goes on ---------- */
// Paint layers, bottom to top. Built-only slots (shoulders, head, back) have no layer.
const EQ_LAYERS=['shirt','legs','feet','chest','wrists','hands','waist','tabard'];
const EQ_SLOTS=[
  {id:'shirt',name:'Shirt'},{id:'chest',name:'Chest'},{id:'legs',name:'Legs'},{id:'feet',name:'Feet'},
  {id:'wrists',name:'Wrists'},{id:'hands',name:'Hands'},{id:'waist',name:'Waist'},{id:'shoulders',name:'Shoulders'},
  {id:'head',name:'Head'},{id:'back',name:'Back'},
  {id:'tabard',name:'Tabard',locked:'Unlocks when a god claims you'},
  {id:'face',name:'Face',locked:'Unlocks with Tinkerer crafts, in the gear and water era'},
  {id:'mecharm',name:'Mechanical arm',locked:'Unlocks in the gear and water era'},
  {id:'device',name:'Back device',locked:'Unlocks in the steam era'}];
const EQ_KIND={linen:0,wool:1,leather:2,studded:3,mail:4,plate:5,quilted:6,fur:7};
const EQ_PATTERN={plain:0,stripes:1,check:2,hemband:3};

/* ---------- 2. the paint layers (GLSL, in the paint template's space: see bodypaint.js) ---------- */
const EQUIP_GLSL=`
uniform vec4 uQ[48];  // 8 layers x 6: [kind, pattern, trim width, on] [a] [b] [main colour] [second colour] [trim colour]
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
float layerDist(int L,vec3 p,float arm,float t,vec4 a,vec4 b){
  float ax=abs(p.x), body=1.-arm;
  if(L==0||L==3){ // shirt, chest: a = hem, sleeve (in arm units: 0 shoulder .. 2 wrist; below 0 sleeveless), neckline style, depth; b.x = open front
    float dt=qTorso(p,a.x,a.z,a.w,b.x); if(a.y<0.)dt=min(dt,qArmhole(p));
    float da=a.y<0.?-1.:(a.y-t)*0.25;
    return p.z>1.53?-1.:mix(dt,da,smoothstep(0.35,0.65,arm));}
  if(L==1){if(arm>0.5)return -1.;return min(p.z-a.x,a.y-p.z);}                          // legs: cuff height, waist height
  if(L==2){if(arm>0.5)return -1.;return a.x-p.z;}                                         // feet: top of the boot
  if(L==4){if(arm<0.5)return -1.;return min(t-a.x,a.y-t)*0.25;}                          // wrists: from, to (arm units)
  if(L==5){if(arm<0.5)return -1.;return (t-a.x)*0.25;}                                   // hands: cuff
  if(L==6){if(arm>0.5)return -1.;return a.y*0.5-abs(p.z-a.x);}                           // waist: centre, width
  if(L==7){if(arm>0.5||p.z>1.5)return -1.;return min(min(a.y-ax,p.z-a.x),qNeck(p,0.,0.)-0.006-p.z);} // tabard: hem, half width
  return -1.;}
vec3 metal(vec3 c,vec2 s){return c*(0.86+0.2*vnoise(s*vec2(40.,700.)));}
vec3 layerColour(float kind,float pat,vec3 p,vec2 s,float d,vec3 c1,vec3 c2,vec3 c3){
  vec3 c=c1; float n=vnoise(s*vec2(520.,190.));
  if(pat>0.5&&pat<1.5)c=mix(c,c2,inside(abs(fract(s.x/0.03)-0.5)-0.18));                              // stripes
  else if(pat>1.5&&pat<2.5){float a=inside(abs(fract(s.x/0.05)-0.5)-0.12),b=inside(abs(fract(s.y/0.05)-0.5)-0.12);c=mix(c,c2,0.55*max(a,b)+0.35*a*b);} // woven check
  else if(pat>2.5)c=mix(c,c2,inside(abs(d-0.03)-0.008));                                               // a band along the hems
  if(kind<0.5)c*=0.92+0.08*n-0.05*vnoise(s*vec2(14.,5.));                                              // linen
  else if(kind<1.5)c*=0.86+0.12*vnoise(s*300.)+0.05*vnoise(s*vec2(40.,12.));                           // wool
  else if(kind<3.5){                                                                                    // leather, studded
    c*=0.88+0.1*vnoise(s*70.)+0.04*n; c*=mix(0.76,1.,smoothstep(0.,0.018,d));                          // darker towards its edges
    c=mix(c,c2*1.1,0.7*inside(abs(d-0.007)-0.0012)*step(0.45,fract((s.x+s.y)*90.)));                   // stitching along the edge
    if(kind>2.5){vec2 g=(fract(s/0.032)-0.5)*0.032;float st=inside(length(g)-0.0045);c=mix(c,metal(c3,s)*(1.15-0.5*smoothstep(0.,0.0045,length(g+0.0015))),st);}}
  else if(kind<4.5){vec2 q=vec2(s.x/0.012+0.5*floor(s.y/0.009),s.y/0.009),g=fract(q)-0.5;           // mail rings, softened to the texture's resolution
    float r=abs(length(g)-0.3),aa=max(fwidth(q.x),fwidth(q.y))*0.7,ring=1.-smoothstep(0.1-aa,0.17+aa,r);
    c=mix(metal(c1,s)*0.42,metal(c1,s)*(1.12-0.45*length(g)),mix(ring,0.6,smoothstep(0.25,0.6,aa)));}
  else if(kind<5.5){float band=fract(s.y/0.075),e=min(band,1.-band)*0.075;                            // plate: lames with rivets
    c=metal(c1,s)*(0.9+0.25*smoothstep(0.012,0.,abs(band-0.85)*0.075))*mix(0.55,1.,smoothstep(0.,0.004,e));
    vec2 g=vec2(fract(s.x/0.045)-0.5,band-0.82);c=mix(c,metal(c3,s)*1.2,inside(length(g*vec2(0.045,0.075))-0.0035));
    c*=mix(1.18,1.,smoothstep(0.,0.01,d));}
  else if(kind<6.5){float q=abs(fract((s.x+s.y)/0.06)-0.5),r=abs(fract((s.x-s.y)/0.06)-0.5);          // quilted
    c*=(0.9+0.08*n)*(1.-0.22*inside(min(q,r)-0.04))*(0.96+0.06*smoothstep(0.,0.5,min(q,r)));}
  else{c*=0.7+0.4*vnoise(s*vec2(150.,35.))+0.12*vnoise(s*vec2(600.,90.));}                              // fur
  return c;}
vec3 applyEquip(vec3 c,vec3 p){
  float arm=1.-smoothstep(0.3,0.7,vTorso), t=armT(p); vec2 s=qSurf(p,arm,t);
  for(int L=0;L<8;L++){
    vec4 h=uQ[L*6]; if(h.w<0.5)continue;
    float d=layerDist(L,p,arm,t,uQ[L*6+1],uQ[L*6+2]);
    c*=1.-0.22*smoothstep(-0.007,0.,d)*(1.-smoothstep(0.,0.0005,d));            // the layer's shadow on what lies under it
    float cov=inside(-d); if(cov<0.001)continue;
    vec3 lc=layerColour(h.x,h.y,p,s,d,uQ[L*6+3].rgb,uQ[L*6+4].rgb,uQ[L*6+5].rgb);
    if(h.z>0.)lc=mix(lc,(h.x>3.5&&h.x<5.5?metal(uQ[L*6+5].rgb,s):uQ[L*6+5].rgb*(0.9+0.1*vnoise(s*200.)))*mix(0.8,1.,smoothstep(0.,h.z,d)),inside(d-h.z)); // trim
    c=mix(c,lc,cov);}
  return c;}
`;

/* ---------- 3. the items ---------- */
// paint: the layer's kind, pattern, trim width (m), a and b (see layerDist), colours [main, second, trim]
// built: pieces made from the body (see section 5)
const EQ_ITEMS={
  shirt:[
    {id:'linen_shirt',name:'Linen shirt',paint:{kind:'linen',a:[0.93,1.92,1,0.05],dyes:['#e2d9c6','#cdbfa4','#b8a888']}},
    {id:'tunic',dye:'main',name:'Short tunic',paint:{kind:'wool',pattern:'hemband',trim:0.012,a:[0.8,0.45,0,0.02],dyes:['#7a5a3a','#a8844e','#5a3e26']}}],
  chest:[
    {id:'jerkin',dye:'leather',name:'Leather jerkin',paint:{kind:'leather',trim:0.01,a:[0.86,-1,2,0.1],b:[0.022],dyes:['#6a4428','#d8c49a','#3e2818']},
      built:[{type:'laces'}]},
    {id:'gambeson',dye:'main',name:'Quilted gambeson',paint:{kind:'quilted',trim:0.014,a:[0.8,1.72,0,0.0],dyes:['#a89a7e','#8a7c62','#6a4e34']},
      built:[{type:'collar',colour:0}]},
    {id:'mail',dye:'trim',name:'Mail shirt',paint:{kind:'mail',trim:0.008,a:[0.84,1.25,0,0.02],dyes:['#9ea4aa','#6a6e72','#7a5a3a']}},
    {id:'robe',dye:'main',name:'Wool robe',paint:{kind:'wool',pattern:'hemband',trim:0.012,a:[0.12,1.9,0,0.02],dyes:['#6a5a48','#a8844e','#4a3e30']},
      built:[{type:'skirt',top:0.97,hem:0.12,flare:0.35,kind:0},{type:'collar',colour:0}]},
    {id:'longcoat',dye:'leather',name:'Long coat',paint:{kind:'leather',trim:0.01,a:[0.5,1.86,1,0.07],b:[0.03],dyes:['#4a3424','#c8b48a','#2e2016']},
      built:[{type:'skirt',top:0.95,hem:0.5,flare:0.28,open:0.42,kind:1},{type:'collar',colour:0}]},
    {id:'doublet',people:'Aurelan',dye:'main',name:'Aurelan doublet',paint:{kind:'wool',pattern:'stripes',trim:0.01,a:[0.9,1.9,0,0.0],dyes:['#2e4a6a','#c9a046','#c9a046']},
      built:[{type:'collar',colour:0},{type:'buttons'}]},
    {id:'furjerkin',people:'Hrimfolk',dye:'leather',name:'Hrimfolk fur-collared jerkin',paint:{kind:'leather',trim:0.012,a:[0.86,-1,0,0.0],dyes:['#5a4030','#c8b48a','#3a2a1c']},
      built:[{type:'furcollar'}]},
    {id:'apron',people:'Ferrin',name:"Ferrin smith's apron",paint:{kind:'linen',a:[0.9,1.1,0,0.03],dyes:['#b8a888','#8a3a26','#c9a046']},
      built:[{type:'apron'}]},
    {id:'wraps',people:'Zarhim',dye:'main',name:'Zarhim desert wraps',paint:{kind:'linen',pattern:'hemband',trim:0.01,a:[0.86,1.95,1,0.06],dyes:['#d8c8a8','#a8783a','#7a5426']},
      built:[{type:'belt',thick:0.008,cloth:1,z:1.0,w:0.09,colour:1}]},
    {id:'ilvaricoat',people:'Ilvari',dye:'main',name:'Ilvari long coat',paint:{kind:'wool',trim:0.012,a:[0.5,1.9,0,0.0],b:[0.025],dyes:['#2a3040','#1a2030','#3a6ad0']},
      built:[{type:'skirt',top:0.95,hem:0.42,flare:0.22,open:0.3,kind:0,trim:1},{type:'collar',colour:0,high:1}]},
    {id:'brigandine',dye:'main',name:'Studded brigandine',paint:{kind:'studded',trim:0.012,a:[0.88,-1,0,0.0],dyes:['#5a2e24','#c9a046','#c9a046']},
      built:[{type:'collar',colour:0}]}],
  legs:[
    {id:'trousers',dye:'second',name:'Wool trousers',paint:{kind:'wool',a:[0.07,1.01],dyes:['#5e5446','#4a4238','#3a3026']}},
    {id:'breeches',dye:'leather',name:'Leather breeches',paint:{kind:'leather',trim:0.008,a:[0.4,1.01],dyes:['#4e3826','#c8b48a','#2e2016']}},
    {id:'plaid',dye:'main',name:'Woven trews',paint:{kind:'wool',pattern:'check',a:[0.07,1.01],dyes:['#3e5a3a','#8a3a26','#2a2a20']}}],
  feet:[
    {id:'shoes',name:'Shoes',paint:{kind:'leather',a:[0.075],dyes:['#3e2a1c','#a08a6a','#2a1c12']},built:[{type:'foot'}]},
    {id:'boots',name:'Tall boots',paint:{kind:'leather',trim:0.008,a:[0.43],dyes:['#4a3020','#b09a76','#2a1a10']},built:[{type:'foot'},{type:'cuff',slot:'feet'}]}],
  wrists:[
    {id:'bracers',name:'Leather bracers',paint:{kind:'studded',trim:0.006,a:[1.45,1.88],dyes:['#5a3a22','#c8b48a','#b0904a']},built:[{type:'cuff',slot:'wrists'}]}],
  hands:[
    {id:'gloves',name:'Work gloves',paint:{kind:'leather',a:[1.93],dyes:['#7a5a3a','#c8b48a','#4a3020']}},
    {id:'gauntlets',name:'Gauntlet gloves',paint:{kind:'leather',trim:0.008,a:[1.62],dyes:['#3a2a20','#b09a76','#2a1a10']},built:[{type:'cuff',slot:'hands'}]}],
  waist:[   // belts carry sockets: attachments (and, later, relics) hang from them
    {id:'belt',name:'Belt',paint:{kind:'leather',a:[1.005,0.034],dyes:['#3a2618','#c8b48a','#c9a046']},sockets:['hipL','hipR'],built:[{type:'belt'},{type:'buckle'}]},
    {id:'toolbelt',name:'Tool belt',paint:{kind:'studded',trim:0.005,a:[1.0,0.046],dyes:['#4a3020','#c8b48a','#b0904a']},sockets:['hipL','hipR','backL','backR'],built:[{type:'belt',thick:0.008},{type:'buckle',big:1}]},
    {id:'sash',name:'Sash',dye:'main',paint:{kind:'wool',pattern:'stripes',a:[1.0,0.07],dyes:['#7a2a26','#c9a046','#5a1e1a']},sockets:['hipL'],built:[{type:'belt',thick:0.006,cloth:1},{type:'knot'}]}],
  shoulders:[
    {id:'pads',name:'Leather pads',built:[{type:'pauldron',lames:2}],dyes:['#5a3a22','#c8b48a','#b0904a'],dye:'leather'},
    {id:'spaulders',name:'Layered spaulders',built:[{type:'pauldron',lames:4,metal:1,rivets:1,size:0.9}],dyes:['#8e959c','#5e6266','#b8bcc0'],dye:'trim'},
    {id:'plates',name:'Steel pauldrons',built:[{type:'pauldron',lames:3,metal:1,rivets:1,ridge:1,size:1.08}],dyes:['#9aa0a6','#6a6e72','#c9a046'],dye:'trim'},
    {id:'brass',name:'Brass pauldrons',built:[{type:'pauldron',lames:3,metal:1,rivets:1,ridge:1}],dyes:['#b08a42','#7a5a26','#e0c070'],dye:'trim'},
    {id:'furplates',name:'Fur-trimmed pauldrons',built:[{type:'pauldron',lames:3,metal:1,rivets:1,fur:1,size:1.1}],dyes:['#7e868c','#8a7458','#c9a046'],dye:'trim'},
    {id:'mantle',name:'Fur mantle',built:[{type:'mantle'}],dyes:['#6e5640','#3e3024','#2a2018']}],
  head:[
    {id:'hood',dye:'main',name:'Hood',hidesHair:1,built:[{type:'hood'}],dyes:['#4a5a3a','#3a4a2e','#2a2a20']},
    {id:'headwrap',people:'Zarhim',dye:'main',name:'Zarhim head wrap',hidesHair:1,built:[{type:'headwrap'}],dyes:['#d8c8a8','#a8783a','#7a5426']}],
  back:[
    {id:'cloak',dye:'main',name:'Cloak',built:[{type:'cloak'}],dyes:['#5a2a26','#3e1c18','#c9a046']},
    {id:'wovencloak',people:'Ruadhan',dye:'main',name:'Ruadhan woven cloak',built:[{type:'cloak',woven:1}],dyes:['#3e5a3a','#8a3a26','#c9a046']}],
};
// what can hang from a belt's sockets (relics will join these)
const EQ_ATTACH=[['None',null],['Pouch','pouch'],['Flask','flask'],['Scroll case','scroll']];
const EQ_SOCKETS={hipL:{name:'Left hip',a:1.35},hipR:{name:'Right hip',a:-1.35},backL:{name:'Left back',a:2.35},backR:{name:'Right back',a:-2.35}};
const EQ_DYES=[['Natural',null],['Forest',['#3e5a36','#2a3e26','#b0904a']],['Crimson',['#7a2626','#4e1818','#c9a046']],
  ['Midnight',['#2a3450','#1a2036','#b8b8c8']],['Ochre',['#a8783a','#7a5426','#4a3020']],['Ash',['#8a8a86','#5a5a58','#2e2e2c']]];
function eqItem(slot,id){return (EQ_ITEMS[slot]||[]).find(i=>i.id===id)||null;}
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
function eqLayerUniforms(outfit){ // outfit: {slot: itemId, dye: [..]}
  const Q=[];for(let i=0;i<48;i++)Q.push(new THREE.Vector4(0,0,0,0));   // (a bare Vector4 has w = 1, which would switch every layer on)
  EQ_LAYERS.forEach((slot,L)=>{const it=eqItem(slot,outfit[slot]);if(!it||!it.paint)return;const P=it.paint,dy=eqDyes(it,outfit.dye);
    Q[L*6].set(EQ_KIND[P.kind],EQ_PATTERN[P.pattern||'plain'],P.trim||0,1);
    const a=(P.a||[]).concat([0,0,0,0]),b=(P.b||[]).concat([0,0,0,0]);Q[L*6+1].set(a[0],a[1],a[2],a[3]);Q[L*6+2].set(b[0],b[1],b[2],b[3]);
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
    const U=paintedMaterial(look).userData.U; U.uQ={value:eqLayerUniforms(outfit||{})};
    const m=new THREE.ShaderMaterial({uniforms:U,side:THREE.DoubleSide,depthTest:false,depthWrite:false,
      vertexShader:'attribute vec3 rest;attribute float torso;varying vec3 vRest;varying float vTorso;void main(){vRest=rest;vTorso=torso;gl_Position=vec4(uv*2.-1.,0.,1.);}',
      fragmentShader:'varying float vTorso;\n'+PAINT_GLSL+EQUIP_GLSL+'\nvoid main(){'+(window.EQ_DEBUG||'vec3 c=paintBody(vRest);c=applyEquip(c,vRest);gl_FragColor=vec4(c,1.);')+'}'});
    m.extensions={derivatives:true}; return m;
  }
  // bake one body into a texture (6 passes of padding stop seams showing); the two targets are kept on the mesh and reused
  function bake(renderer,mesh,look,outfit,size){
    if(!scene)setup(); size=size||1024;
    const ud=mesh.userData; if(!ud.bakeRT||ud.bakeRT[0].width!==size){
      const mk=()=>new THREE.WebGLRenderTarget(size,size,{minFilter:THREE.LinearMipmapLinearFilter,magFilter:THREE.LinearFilter,generateMipmaps:true,depthBuffer:false,stencilBuffer:false});
      ud.bakeRT=[mk(),mk()];}
    const [A,B]=ud.bakeRT, g=new THREE.Mesh(mesh.geometry,material(look,outfit)); g.frustumCulled=false;
    const prevT=renderer.getRenderTarget(),prevC=renderer.getClearColor(new THREE.Color()),prevA=renderer.getClearAlpha(),prevAuto=renderer.autoClear;
    renderer.autoClear=true; renderer.setClearColor(0x000000,0);
    scene.add(g); renderer.setRenderTarget(A); renderer.render(scene,cam); scene.remove(g); g.material.dispose();
    scene.add(quad); let src=A,dst=B; dil.uniforms.uPx.value.set(1/size,1/size);
    for(let i=0;i<6;i++){dil.uniforms.uT.value=src.texture;renderer.setRenderTarget(dst);renderer.render(scene,cam);[src,dst]=[dst,src];}
    scene.remove(quad);
    renderer.setRenderTarget(prevT); renderer.setClearColor(prevC,prevA); renderer.autoClear=prevAuto;
    return src.texture;
  }
  return {bake,material};
})();
// the body's material once baked: a plain textured, skinned, morphed material
function bakedMaterial(tex){const m=new THREE.MeshLambertMaterial({map:tex,skinning:true,morphTargets:true,morphNormals:true});return m;}

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
function eqPiece(){return {P:[],N:[],C:[],DL:[],SK:[],I:[],RS:[],K:[],kind:1};}   // kind: 0 cloth 1 leather 2 metal 3 fur
function eqVert(pc,e,off,col){ // add one point (an evaluated body blend), pushed out along its normal
  const i=pc.P.length/3; for(let k=0;k<3;k++){pc.P.push(e.p[k]+e.n[k]*off);pc.N.push(e.n[k]);} pc.C.push(...col);
  pc.DL.push(e.dl); pc.SK.push(e.bones); pc.RS.push(...e.r); pc.K.push(pc.kind); return i;}
const eqKey=p=>p.map(v=>Math.round(v*2000)).join(',');
// a shell: the cut region pushed out by thick(point), with a wall round its edge so it reads as a solid piece
function eqShell(pc,D,fs,thick,colour,smooth,minH){   // smooth: passes; minH: how close to the body smoothing may bring it
  const polys=eqCut(D,fs), base=pc.P.length/3, edges=new Map(), at=new Map();
  for(const poly of polys){
    const ids=poly.map(v=>{const e=eqEval(D,v.rec),o=thick(e,v.f),key=eqKey(e.p);
      const id=eqVert(pc,e,o,colour(e,v.f,0)); at.set(id,{e,o,key,f:v.f}); return id;});
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
  for(const {a,b,n} of edges.values()){if(n!==1)continue;           // an edge of the piece: a wall from the body up to the shell
    const A=at.get(a),B=at.get(b),col=colour(A.e,A.f,1);
    const a0=eqVert(pc,A.e,0.0015,col),b0=eqVert(pc,B.e,0.0015,col),a1=eqVert(pc,A.e,A.o,col),b1=eqVert(pc,B.e,B.o,col);
    pc.I.push(a0,b0,b1,a0,b1,a1, a0,b1,b0,a0,a1,b1);}                 // both faces, so the wall shows from either side
  return polys.length;
}
// a small block pinned to the body (buckles, pouches, lacing): centred at a body point, facing out along its normal
function eqBlock(pc,D,rec,w,h,d,off,colour,shade,drop){
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
// an upright cylinder pinned to the body (flasks, scroll cases): its side touching the body at off, hanging drop below the pin
function eqCyl(pc,D,rec,r,h,off,drop,colour,shade,segs){
  segs=segs||12; const e=eqEval(D,rec),n=e.n,up=[0,1,0]; let x=[up[1]*n[2]-up[2]*n[1],up[2]*n[0]-up[0]*n[2],up[0]*n[1]-up[1]*n[0]];const lx=Math.hypot(...x)||1;x=x.map(v=>v/lx);
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

// the pieces
const EQ_BUILD={
  cuff(pc,D,item,dy,spec){pc.kind=1;                       // boot tops, gauntlet cuffs, bracers
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
  foot(pc,D,item,dy){pc.kind=1;const z=D.rest,main=eqRGB(dy[0]),sole=eqRGB(dy[2]),top=Math.min(item.paint.a[0],0.11);
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
      const lc=(lmin+lmax)/2,Wb=Math.max((lmax-lmin)/2,tw)+0.004,Hb=Math.min(top+0.004,hb+0.007),K=12,M=20,ring=[];
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
  belt(pc,D,item,dy,spec){pc.kind=spec.cloth?0:1;const z=D.rest,c=spec.z||item.paint.a[0],w=(spec.w||item.paint.a[1])/2,main=eqRGB(dy[spec.colour||0]),th=spec.thick||0.006;
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.5?w-Math.abs(z[i*3+2]-c):-1)],e=>spec.cloth?th+0.004*eqNoise(e.p,15):th,
      (e,f,rim)=>main.map(v=>v*(rim?0.7:spec.cloth?0.85+0.15*eqNoise(e.p,40):0.95)),spec.cloth?3:0);},
  knot(pc,D,item,dy){pc.kind=0;const c=item.paint.a[0],main=eqRGB(dy[0]),rec=eqBeltPoint(D,c,-0.5);   // a sash's knot and its hanging ends
    eqBlock(pc,D,rec,0.04,0.035,0.016,0.006,main,0.9); eqBlock(pc,D,rec,0.03,0.13,0.008,0.012,main,0.8,0.08); eqBlock(pc,D,rec,0.026,0.1,0.008,0.016,main,0.7,0.07);},
  buckle(pc,D,item,dy,spec){pc.kind=2;const c=item.paint.a[0],rec=eqBeltPoint(D,c,0),brass=eqRGB(dy[2]),k=spec.big?1.3:1;
    eqBlock(pc,D,rec,0.05*k,0.04*k,0.006,0.007,brass,1.15); eqBlock(pc,D,rec,0.03*k,0.022*k,0.004,0.0125,eqRGB(dy[0]),0.8);},
  // a skirt for robes and coats: rings from the hips to the hem, measured round the legs so it clears them, flaring towards
  // the hem; lower down it follows the thighs, so it moves when walking. open: a gap at the front (half-angle, radians)
  skirt(pc,D,item,dy,spec,ctx){pc.kind=spec.kind||0;const main=eqRGB(dy[0]),trim=eqRGB(dy[2]),z=D.rest,P=D.pos,legs=[];
    for(let i=0;i<D.n;i++)if(D.arm[i]<0.5&&z[i*3+2]<spec.top+0.03)legs.push(i);
    const med=a=>{a=a.slice().sort((x,y)=>x-y);return a[a.length>>1];};
    const topI=legs.filter(i=>Math.abs(z[i*3+2]-spec.top)<0.015),hemI=legs.filter(i=>Math.abs(z[i*3+2]-spec.hem)<0.015);
    const cx=topI.reduce((a,i)=>a+P[i*3],0)/topI.length,cz=topI.reduce((a,i)=>a+P[i*3+2],0)/topI.length;
    const yT=med(topI.map(i=>P[i*3+1])),yH=hemI.length?med(hemI.map(i=>P[i*3+1])):yT*spec.hem/spec.top;
    const M=32,K=11,open=spec.open||0,hips=ctx.bone('hips'),tl=ctx.bone('thigh.L'),tr=ctx.bone('thigh.R');
    const radius=(y,band)=>{const r=new Float32Array(M);for(const i of legs){const dy_=P[i*3+1]-y;if(Math.abs(dy_)>band)continue;
      const x=P[i*3]-cx,zz=P[i*3+2]-cz,b=((Math.round(Math.atan2(x,zz)/(Math.PI*2)*M)%M)+M)%M;r[b]=Math.max(r[b],Math.hypot(x,zz));}
      const o=new Float32Array(M);for(let b=0;b<M;b++){let m=0;for(let k=-2;k<=2;k++)m=Math.max(m,r[(b+k+M)%M]);o[b]=m;}return o;};
    const r0=radius(yT,0.02),rows=[];
    for(let k=0;k<=K;k++){const t=k/K,y=yT+(yH-yT)*t,rb=radius(y,0.03),ids=[];
      for(let b=0;b<=M;b++){const th=(b/M)*Math.PI*2-Math.PI;if(open&&Math.abs(th)<open)continue;   // front is th = 0 (+z)
        const bb=((Math.round(th/(Math.PI*2)*M)%M)+M)%M,r=Math.max(r0[bb]*(1+spec.flare*Math.pow(t,1.3)),rb[bb]+0.02+0.03*t)+0.006,x=cx+Math.sin(th)*r,zz=cz+Math.cos(th)*r;
        let best=-1,bd=1e9;for(const i of legs){const d=(P[i*3]-x)**2+(P[i*3+1]-y)**2+(P[i*3+2]-zz)**2;if(d<bd){bd=d;best=i;}}
        const e=eqEval(D,[[best,1]]);e.p=[x,y,zz];e.n=[Math.sin(th),-0.15,Math.cos(th)];
        if(t>0){const kk=Math.min(0.6,t*0.75),side=eqSm(-0.05,0.05,x-cx),b_=new Map();b_.set(hips,1-kk);b_.set(tl,kk*side);b_.set(tr,kk*(1-side));e.bones=b_;}
        const fold=0.88+0.12*Math.cos(th*9+t*2), col=(k===K||spec.trim&&k>=K-1)?trim:main;
        ids.push(eqVert(pc,e,0,col.map(v=>v*fold*(k===K?0.85:1))));}
      rows.push(ids);}
    for(let k=0;k<K;k++)for(let b=0;b+1<rows[k].length;b++){const a=rows[k][b],c=rows[k][b+1],d=rows[k+1][b+1],f=rows[k+1][b];pc.I.push(a,f,d,a,d,c);}
    if(!open){const a=rows[0].length-1;}
  },
  buttons(pc,D,item,dy){pc.kind=2;const brass=eqRGB(dy[2]);for(let z=0.98;z<1.44;z+=0.055)eqBlock(pc,D,eqNear(D,0,-0.2,z,2,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0),0.011,0.011,0.005,0.003,brass,1.2);},
  furcollar(pc,D,item,dy){pc.kind=3;const fur=eqRGB('#7a6248');
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,ax=Math.abs(r[i*3]),z_=r[i*3+2];if(D.arm[i]>0.5||z_>1.535)return -1;
      return Math.min(z_-1.43-0.02*eqSmooth([D.pos[i*3],D.pos[i*3+1],D.pos[i*3+2]],50),0.17-ax);})],
      e=>0.03+0.02*eqFur(e.p),(e,f,rim)=>fur.map(v=>v*(0.55+0.6*eqFur(e.p))),4,0.015);},
  apron(pc,D,item,dy,spec,ctx){pc.kind=1;const ctx_hips=ctx.bone('hips');const lea=eqRGB('#5a3a22'),strap=eqRGB('#3a2618'),NU=9,NV=12,top=1.36,bot=0.46,ids=[];   // a leather apron hanging in front
    const front=i=>D.arm[i]<0.5&&D.rest[i*3+1]<0.0;
    for(let v=0;v<NV;v++){const z=top-(top-bot)*v/(NV-1),hang=(top-z)/(top-bot),w=0.1+0.07*eqSm(0,0.4,hang);
      for(let u=0;u<NU;u++){const x=(u/(NU-1)*2-1)*w,e=eqEval(D,eqNear(D,x*(z<0.95?0.8:1),-0.2,z,4,front)),off=0.012+0.07*Math.pow(eqSm(0.25,1,hang),1.3);
        e.p=[e.p[0]+e.n[0]*0.3*off,e.p[1],e.p[2]+off];e.n=[0,0,1];
        if(z<1.0){const b=new Map();b.set(ctx_hips,1);e.bones=b;}
        ids.push(eqVert(pc,e,0,lea.map(c=>c*(0.9+0.12*Math.cos(u*1.3+v)))));}}
    for(let v=0;v+1<NV;v++)for(let u=0;u+1<NU;u++){const a=ids[v*NU+u],b=ids[v*NU+u+1],c=ids[(v+1)*NU+u+1],d=ids[(v+1)*NU+u];pc.I.push(a,d,c,a,c,b);}
    for(const sx of [-1,1])eqBlock(pc,D,eqNear(D,0.09*sx,-0.2,1.4,2,front),0.018,0.07,0.004,0.004,strap,1);},
  headwrap(pc,D,item,dy){pc.kind=0;const main=eqRGB(dy[0]),dark=eqRGB(dy[1]);   // wound cloth over the crown and brow, the face left open
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,x=r[i*3],y=r[i*3+1],z_=r[i*3+2];if(D.arm[i]>0.5||z_<1.55)return -1;
      return Math.min(z_-(y<-0.02?1.705:1.62),1)})],
      e=>0.016+0.01*eqSm(1.7,1.82,e.r[2])+0.006*Math.sin(e.r[2]*180+Math.atan2(e.r[0],-e.r[1])*2),(e,f,rim)=>(rim?dark:main).map(v=>v*(0.86+0.14*Math.sin(e.r[2]*180+Math.atan2(e.r[0],-e.r[1])*2))),3);
    const tail=eqNear(D,0.02,0.2,1.64,3,i=>D.arm[i]<0.5&&D.rest[i*3+1]>0.0);eqBlock(pc,D,tail,0.05,0.16,0.012,0.02,main,0.9,0.09);},
  // what hangs from a belt socket; an empty socket shows its brass ring
  attach(pc,D,item,dy,spec){pc.kind=1;const c=item.paint.a[0],w=item.paint.a[1]/2,rec=eqBeltPoint(D,c,EQ_SOCKETS[spec.socket].a),brass=eqRGB(item.paint.dyes[2]),th=0.007;
    const leather=eqRGB('#4a3020'),drop=w;
    if(!spec.what){eqBlock(pc,D,rec,0.016,0.02,0.004,th,brass,1.1,drop+0.004);return;}
    eqBlock(pc,D,rec,0.012,0.03,0.004,th,leather,0.8,drop);                                    // the strap from the belt
    if(spec.what==='pouch'){eqBlock(pc,D,rec,0.07,0.08,0.036,th,eqRGB('#6a4a2e'),1.0,drop+0.05);eqBlock(pc,D,rec,0.074,0.035,0.006,th+0.036,eqRGB('#5a3a22'),0.9,drop+0.027);
      eqBlock(pc,D,rec,0.01,0.01,0.004,th+0.042,brass,1.2,drop+0.04);}
    else if(spec.what==='flask'){eqCyl(pc,D,rec,0.026,0.075,th,drop+0.06,eqRGB('#8a6a46'),1.0);eqCyl(pc,D,rec,0.027,0.018,th-0.001,drop+0.05,eqRGB('#4a3020'),1.0);
      eqCyl(pc,D,rec,0.009,0.02,th+0.017,drop+0.012,eqRGB('#6a6e72'),1.1);eqCyl(pc,D,rec,0.007,0.012,th+0.019,drop+0.0,eqRGB('#a88458'),1.0);}
    else if(spec.what==='scroll'){eqCyl(pc,D,rec,0.019,0.12,th,drop+0.075,eqRGB('#5a3a22'),1.0);eqCyl(pc,D,rec,0.021,0.014,th-0.002,drop+0.022,brass,1.15);eqCyl(pc,D,rec,0.021,0.014,th-0.002,drop+0.128,brass,1.05);}
  },
  pouch(pc,D,item,dy){pc.kind=1;const rec=eqNear(D,-0.15,-0.05,0.955,3,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0.02),main=eqRGB(dy[0]);
    eqBlock(pc,D,rec,0.075,0.085,0.04,0.006,main,1.05); eqBlock(pc,D,rec,0.079,0.04,0.006,0.046,main,0.85);},
  laces(pc,D,item,dy){pc.kind=0;const open=item.paint.b[0],lace=eqRGB(dy[1]);
    for(let z=1.06;z<1.4;z+=0.045){const rec=eqNear(D,0,-0.2,z,2,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0);eqBlock(pc,D,rec,open*2*(0.4+0.6*eqSm(1.0,1.42,z))+0.012,0.005,0.004,0.003,lace,1);}},
  collar(pc,D,item,dy,spec){pc.kind=0;const z=D.rest,main=eqRGB(dy[spec.colour||0]);
    // a ring round the neck, from its base up, standing a little off it
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>D.arm[i]<0.5&&Math.abs(z[i*3])<0.1?Math.min(z[i*3+2]-1.488,1.527-z[i*3+2]):-1)],
      e=>0.005+0.009*eqSm(1.49,1.527,e.r[2]),(e,f,rim)=>main.map(v=>v*(rim?0.75:0.95)));},
  // pauldrons: stacked lames down the shoulder, each lighter at its crown and darker at its rim, with rivets along the lower
  // rims, an optional raised guard by the neck and an optional roll of fur over the top
  pauldron(pc,D,item,dy,spec){pc.kind=spec.metal?2:1;const metal=spec.metal,main=eqRGB(dy[0]),dark=eqRGB(dy[1]),trim=eqRGB(dy[2]),k=spec.size||1,N=spec.lames||2,r=D.rest;
    const cap=(L)=>({cx:0.205+0.02*L*k,cz:1.468-0.046*L*k,R:(0.122-0.016*L)*k,th:(metal?0.024:0.018)-0.004*L});   // each lame tucks under the one above
    const dist=(i,C)=>{const dx=Math.abs(r[i*3])-C.cx,dy_=(r[i*3+1]-0.02)*1.1,dz=r[i*3+2]-C.cz;return Math.sqrt(dx*dx+dy_*dy_+dz*dz);};
    const keep=i=>r[i*3+2]<1.53&&Math.abs(r[i*3])>0.125&&Math.abs(r[i*3+1]-0.02)<0.115;   // the outer shoulder only: not the chest, back or neck
    for(let L=0;L<N;L++){const C=cap(L),U=L?cap(L-1):null,f=Float32Array.from({length:D.n},(_,i)=>keep(i)?Math.min(C.R-dist(i,C),U?dist(i,U)-(U.R-0.03):1):-1);
      eqShell(pc,D,[f],e=>C.th+0.02*eqSm(0,C.R*0.9,C.R-Math.hypot(Math.abs(e.r[0])-C.cx,(e.r[1]-0.02)*1.1,e.r[2]-C.cz)),   // domed: highest at its crown
        (e,fv,rim)=>{if(rim)return (metal?dark:trim).map(v=>v*0.8);const t=eqSm(0,C.R*0.8,fv[0]);
          return main.map(v=>v*(metal?0.78+0.42*t:0.85+0.18*t)*(1-0.05*L)*(0.95+0.05*eqNoise(e.p,40)));},2);
      if(spec.rivets){const ring=[];for(let i=0;i<D.n;i++)if(keep(i)&&Math.abs(dist(i,C)-0.86*C.R)<0.009&&r[i*3+2]<C.cz-0.01)ring.push(i);
        const ang=i=>Math.atan2(r[i*3+1]-0.02,Math.abs(r[i*3])-C.cx);ring.sort((a,b)=>ang(a)-ang(b));
        const cnt=Math.min(5,ring.length);for(let q=0;q<cnt;q++){const i=ring[Math.floor((q+0.5)/cnt*ring.length)];eqBlock(pc,D,[[i,1]],0.008,0.008,0.004,C.th+0.006,trim,1.2);}}}
    if(spec.ridge){const C=cap(0),f=Float32Array.from({length:D.n},(_,i)=>keep(i)&&Math.abs(r[i*3])<C.cx+0.01?0.008-Math.abs(dist(i,C)-(C.R-0.014)):-1);
      eqShell(pc,D,[f],()=>C.th+0.012,(e,fv,rim)=>(rim?dark:main).map(v=>v*(rim?0.8:1.12)));}
    if(spec.fur){pc.kind=3;const C=cap(0),fur=eqRGB('#7a6248'),f=Float32Array.from({length:D.n},(_,i)=>{const z_=r[i*3+2];if(z_>1.53||z_<C.cz-0.01||Math.abs(r[i*3+1]-0.02)>0.12)return -1;return 0.024-Math.abs(dist(i,C)-(C.R-0.012));});   // a roll of fur along the top edge
      eqShell(pc,D,[f],e=>C.th+0.022+0.012*eqFur(e.p),(e,fv,rim)=>fur.map(v=>v*(0.55+0.6*eqFur(e.p))),6,C.th);}
  },
  mantle(pc,D,item,dy){pc.kind=3;const main=eqRGB(dy[0]),dark=eqRGB(dy[1]),pos=D.pos;
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,ax=Math.abs(r[i*3]),z=r[i*3+2];if(z>1.505&&ax<0.1)return -1;
      const tuft=0.03*(eqSmooth([pos[i*3],pos[i*3+1],pos[i*3+2]],60)-0.5);                 // a ragged, tufted hem
      return D.arm[i]>0.5?(0.38-D.t[i])*0.25+tuft:Math.min(z-(1.385-0.05*eqSm(0.0,0.06,r[i*3+1]))+tuft,0.25-ax);})],
      e=>0.026+0.022*eqFur(e.p),(e,f,rim)=>{const k=eqFur(e.p),tip=eqSm(0,0.03,f[0]);return (rim?dark:main).map(v=>v*(0.55+0.55*k)*(0.8+0.25*tip));},3,0.02);},
  hood(pc,D,item,dy){pc.kind=0;const main=eqRGB(dy[0]),lin=eqRGB(dy[1]);
    eqShell(pc,D,[Float32Array.from({length:D.n},(_,i)=>{const r=D.rest,x=r[i*3],y=r[i*3+1],z=r[i*3+2];if(D.arm[i]>0.5)return -1;
      const face=1-((x/0.07)**2+((z-1.665)/0.105)**2), open=y<0.0?face:-1;                    // the opening for the face
      return Math.min(-open*0.05, z-1.36, 0.24-Math.abs(x));})],
      e=>{const r=e.r; if(r[2]<1.5)return 0.012+0.02*eqSm(1.36,1.5,r[2]);
        const back=eqSm(-0.02,0.06,r[1]), top=eqSm(1.66,1.8,r[2]);
        return 0.032+0.018*back+0.012*top+0.05*back*top*eqSm(0.04,0.0,Math.abs(r[0]));},   // roomy over the head, a peak behind
      (e,f,rim)=>rim?lin.map(v=>v*0.8):main.map(v=>v*(0.9+0.1*eqNoise(e.p,20))));},
  cloak(pc,D,item,dy,spec,ctx){pc.kind=spec.woven?4:0;const main=eqRGB(dy[0]),lin=eqRGB(dy[1]),hips=ctx.bone('hips'),spine=ctx.bone('spine');
    const NU=13,NV=16,top=1.43,bot=0.3,back=i=>D.arm[i]<0.5&&D.rest[i*3+1]>0.0, ids=[];
    for(let v=0;v<NV;v++){const z=top-(top-bot)*v/(NV-1),hang=(top-z)/(top-bot),w=0.17+0.11*hang;
      for(let u=0;u<NU;u++){const x=(u/(NU-1)*2-1)*w,rec=eqNear(D,x*(z<0.95?0.75:1),0.2,z,4,back),e=eqEval(D,rec);
        const off=0.02+0.03*eqSm(0,0.25,hang)+0.17*Math.pow(hang,1.4), dir=[e.n[0]*0.4,e.n[1]*0.3,e.n[2]*0.6-0.6]; const L=Math.hypot(...dir);
        const p=[0,1,2].map(k=>e.p[k]+dir[k]/L*off);
        let bones=e.bones; if(z<1.08){const k=eqSm(1.08,0.92,z),b=new Map();for(const [bi,ww] of e.bones)b.set(bi,ww*(1-k));b.set(hips,(b.get(hips)||0)+k*0.8);b.set(spine,(b.get(spine)||0)+k*0.2);bones=b;}
        const i=pc.P.length/3;pc.P.push(...p);pc.N.push(0,0,-1);pc.DL.push(e.dl);pc.SK.push(bones);pc.RS.push(x,0.2+hang*0.1,z);pc.K.push(pc.kind);
        const fold=0.86+0.14*Math.cos((u/(NU-1))*Math.PI*5+hang*1.5);pc.C.push(...main.map(c=>c*fold*(v===NV-1?0.8:1)));ids.push(i);}}
    for(let v=0;v+1<NV;v++)for(let u=0;u+1<NU;u++){const a=ids[v*NU+u],b=ids[v*NU+u+1],c=ids[(v+1)*NU+u+1],d=ids[(v+1)*NU+u];pc.I.push(a,b,c,a,c,d);}
    for(const sx of [-1,1])eqBlock(pc,D,eqNear(D,0.155*sx,-0.2,1.425,2,i=>D.arm[i]<0.5&&D.rest[i*3+1]<0),0.026,0.026,0.008,0.006,eqRGB(dy[2]),1.2);},
};
// a character's whole set of built pieces, merged into one skinned mesh on the body's skeleton
function eqBuiltMesh(body,outfit){
  const D=eqBodyData(body),pc=eqPiece(),bones=body.skeleton.bones,san=n=>n.replace(/[\s\.\[\]:\/]/g,''),ctx={bone:n=>Math.max(0,bones.findIndex(b=>san(b.name)===san(n)))};
  for(const slot of Object.keys(EQ_ITEMS)){const it=eqItem(slot,outfit[slot]);if(!it||!it.built)continue;const dy=eqDyes(it,outfit.dye);
    for(const spec of it.built)EQ_BUILD[spec.type](pc,D,it,dy,spec,ctx);}
  const belt=eqItem('waist',outfit.waist);
  if(belt&&belt.sockets)for(const sk of belt.sockets)EQ_BUILD.attach(pc,D,belt,null,{socket:sk,what:(outfit.belt||{})[sk]||null},ctx);
  if(!pc.I.length)return null;
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
  return m;
}
// Built pieces are coloured per point; this adds the fine surface per fragment: fur strands, leather grain and creases, brushed
// metal with a stronger highlight, cloth weave.
function eqOutfitMaterial(){
  const m=new THREE.MeshPhongMaterial({vertexColors:true,skinning:true,morphTargets:true,shininess:24,specular:0x2a2a2a,side:THREE.DoubleSide});
  m.onBeforeCompile=sh=>{
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nattribute vec3 rest;attribute float kind;varying vec3 vRs;varying float vK;')
      .replace('#include <begin_vertex>','#include <begin_vertex>\nvRs=rest;vK=kind;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>',`#include <common>
varying vec3 vRs;varying float vK;
float oh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float on(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(oh(i),oh(i+vec2(1.,0.)),f.x),mix(oh(i+vec2(0.,1.)),oh(i+vec2(1.,1.)),f.x),f.y);}`)
      .replace('#include <color_fragment>',`#include <color_fragment>
  { vec2 a=vec2(atan(vRs.x,-vRs.y),vRs.z); float d=1.;
    if(vK<0.5) d=0.93+0.07*on(a*vec2(260.,700.))-0.05*on(a*vec2(9.,30.));                                          // cloth
    else if(vK<1.5) d=(0.9+0.12*on(a*vec2(140.,400.)))*(1.-0.1*smoothstep(0.6,0.9,on(a*vec2(14.,60.))));           // leather: grain and creases
    else if(vK<2.5) d=0.9+0.14*on(vec2(a.x*30.,a.y*900.));                                                        // brushed metal
    else if(vK<3.5){ float st=on(vec2(a.x*260.+on(a*vec2(20.,40.))*6.,a.y*30.)); d=0.62+0.6*st*st; }                // fur: strands running down
    else { vec2 q=vec2(vRs.x,vRs.z)*vec2(14.,14.); float u=step(0.62,fract(q.x)),v=step(0.62,fract(q.y)),fu=step(0.9,fract(q.x*2.)),fv=step(0.9,fract(q.y*2.));
      d=(0.95+0.05*on(a*vec2(300.,300.)))*(1.-0.28*u-0.28*v+0.12*u*v)*(1.+0.25*max(fu,fv)); }                 // woven check
    diffuseColor.rgb*=d; }`)
      .replace('#include <specularmap_fragment>','#include <specularmap_fragment>\n  specularStrength=vK>1.5&&vK<2.5?2.0:vK>2.5?0.15:0.55;');
  };
  m.customProgramCacheKey=()=>'eq-outfit'; return m;
}
// dress a figure: bake its paint and painted armour, and build its built armour
function dressOutfit(root,look,outfit,renderer,bakeOnly){
  const rig=root.userData.rig; if(!rig||!rig.body.geometry.attributes.uv)return;   // bodies without a texture layout keep live paint
  const body=rig.body, tex=EqBake.bake(renderer,body,look,outfit,1024);
  if(!body.userData.baked||body.material.map!==tex){body.material=bakedMaterial(tex);body.userData.baked=true;} else body.material.needsUpdate=true;
  if(bakeOnly)return;
  if(rig.outfit){rig.outfit.parent.remove(rig.outfit);rig.outfit.geometry.dispose();rig.outfit=null;}
  const m=eqBuiltMesh(body,outfit); if(m){body.parent.add(m);rig.outfit=m;}
  const head=eqItem('head',outfit.head), hide=head&&head.hidesHair;    // hoods and wraps hide the hair (beards and moustaches stay)
  root.traverse(o=>{if(o.isMesh&&hide&&o.name.startsWith('Hair_'))o.visible=false;});
}
