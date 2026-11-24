// Shared by the character creator and the game: painted bodies, hair, builds, and peoples as built-in shapes.
// Load after three.js, GLTFLoader and SkeletonUtils.
/* ---------- Painted bodies: one seamless mesh, everything else is paint, computed from where each point sits on the body ---------- */
// rest-space coordinates (as modelled): x across, y forward is negative, z up, metres.
const PAINT_GLSL=`
uniform vec3 uSkin,uHair,uEye,uShirt,uVest,uPants,uBelt,uBoots,uTrim,uInk,uLip;
uniform vec4 uF1; // vest, bare chest, ink, freckles
uniform vec4 uF2; // hair (0 bald 1 short 2 long), gloves, stripes, tabard
uniform float uFem; // 1 for the female body
uniform vec4 uFace;  // heritage: eye tilt, brow weight, socket depth, eye size
uniform vec4 uFace2; // heritage: cheekbones, jaw, warmth, lip fullness
uniform vec4 uB;  // base layer: on, lower (0 trousers 1 boxers), chest hair, muscle definition (0 soft .. 1 defined)
varying vec3 vRest;
float hsh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float vnoise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hsh(i),hsh(i+vec2(1.,0.)),f.x),mix(hsh(i+vec2(0.,1.)),hsh(i+vec2(1.,1.)),f.x),f.y);}
float inside(float d){float w=max(fwidth(d),1e-5);return 1.-smoothstep(-w,w,d);}  // 1 where d<0, antialiased
float gss(vec2 p,vec2 c,vec2 w){vec2 d=(p-c)/w;return exp(-dot(d,d));}
float hairline(float th){ // height of the hairline around the head (0 = brow, pi = nape)
  th=abs(th);
  return th<0.6?mix(1.745,1.748,th/0.6):th<1.15?mix(1.748,1.706,(th-0.6)/0.55):th<1.5?mix(1.706,1.655,(th-1.15)/0.35):th<2.45?mix(1.655,1.618,(th-1.5)/0.95):mix(1.618,1.604,(th-2.45)/0.7);
}
float cardline(float th){ // the hair meshes' hairline (tools/blender/hair.py HAIRLINE): rising at the temples, down to the sideburns, just over the ears
  float a=abs(th);
  if(a<0.3000)return mix(1.756,1.760,(a-0.0000)/0.3000);
  if(a<0.6500)return mix(1.760,1.770,(a-0.3000)/0.3500);
  if(a<0.9500)return mix(1.770,1.758,(a-0.6500)/0.3000);
  if(a<1.1500)return mix(1.758,1.735,(a-0.9500)/0.2000);
  if(a<1.3000)return mix(1.735,1.672,(a-1.1500)/0.1500);
  if(a<1.4200)return mix(1.672,1.690,(a-1.3000)/0.1200);
  if(a<1.6000)return mix(1.690,1.697,(a-1.4200)/0.1800);
  if(a<1.8500)return mix(1.697,1.697,(a-1.6000)/0.2500);
  if(a<2.0500)return mix(1.697,1.682,(a-1.8500)/0.2000);
  if(a<2.2500)return mix(1.682,1.662,(a-2.0500)/0.2000);
  if(a<2.6000)return mix(1.662,1.628,(a-2.2500)/0.3500);
  if(a<3.1416)return mix(1.628,1.622,(a-2.6000)/0.5416);
  return 1.622;}
vec3 cloth(vec3 base,vec3 p,float k){return base*(0.94+0.06*vnoise(p.xz*vec2(260.,90.))+0.05*(vnoise(p.xz*40.)-.5)*k);}
vec3 paintHead(vec3 p){
  float ax=abs(p.x), th=atan(p.x,-(p.y-0.002)), front=(1.-smoothstep(-0.07,-0.03,p.y));
  vec3 c=uSkin*(0.97+0.05*vnoise(p.xz*300.));
  // under the jaw and the neck sit in shadow
  c*=mix(0.86,1.,smoothstep(1.56,1.6,p.z));
  // healthy colour: warm cheeks and nose, more for ruddy peoples
  float warm=0.35+0.65*uFace2.z+0.45*uFem;
  c=mix(c,c*vec3(1.07,0.91,0.89),warm*front*(0.55*gss(vec2(ax,p.z),vec2(0.05,1.65),vec2(0.02,0.016))+0.35*gss(vec2(ax,p.z),vec2(0.,1.656),vec2(0.009,0.012))));
  if(uF1.w>0.5){float fr=step(0.9,hsh(floor(p.xz*520.)))*front*gss(vec2(ax,p.z),vec2(0.03,1.656),vec2(0.04,0.02));c=mix(c,c*vec3(0.8,0.62,0.52),fr);}
  if(front>0.){
    // sculpting light and shade, kept soft so faces stay pleasing
    float deep=uFace.z;
    c*=1.-(0.16+0.2*deep)*(1.-0.55*uFem)*front*gss(vec2(ax,p.z),vec2(0.034,1.693),vec2(0.021,0.011));    // under the brow
    c*=1.-0.1*(1.-0.7*uFem)*front*gss(vec2(ax,p.z),vec2(0.017,1.642),vec2(0.006,0.028));                // beside the nose
    c*=1.-0.16*(1.-0.6*uFem)*front*gss(vec2(ax,p.z),vec2(0.,1.638),vec2(0.011,0.004));                  // under the nose
    c*=1.-(0.05+0.14*uFace2.x)*(1.-0.65*uFem)*front*gss(vec2(ax,p.z),vec2(0.053,1.63),vec2(0.011,0.016)); // hollow under the cheekbone
    c*=1.+(0.04+0.1*uFace2.x)*front*gss(vec2(ax,p.z),vec2(0.052,1.664),vec2(0.016,0.008)); // cheekbones catch the light
    c*=1.-0.12*uFace2.y*(1.-0.7*uFem)*gss(vec2(ax,p.z),vec2(0.066,1.585),vec2(0.012,0.02));             // a strong jaw's edge
    c*=1.+0.1*front*gss(vec2(ax,p.z),vec2(0.,1.69),vec2(0.006,0.03));                     // light down the bridge
    c*=1.+0.05*front*gss(vec2(ax,p.z),vec2(0.,1.735),vec2(0.03,0.02));                    // forehead
    // lips: shaped, with the faintest upturn at the corners
    float full=0.85+0.4*uFace2.w+0.25*uFem, cz=0.0014*smoothstep(0.012,0.02,ax);
    float up=inside(length((vec2(ax,p.z-cz)-vec2(0.,1.6206))/vec2(0.0195,0.0040*full))-1.)*(1.-0.6*inside(length(vec2(ax,p.z-1.6232))-0.0022));  // a cupid's bow
    float lo=inside(length((vec2(ax,p.z-cz)-vec2(0.,1.6132))/vec2(0.0175,0.005*full))-1.);
    vec3 lipc=mix(c,uLip*(1.+0.08*uFem),0.55+0.42*uFem);
    c=mix(c,lipc*0.92,up*front); c=mix(c,lipc,lo*front);
    c=mix(c,c*(1.08+0.1*uFem),front*inside(length((vec2(ax,p.z)-vec2(0.,1.6118))/vec2(0.007+0.002*uFem,0.0018))-1.)*lo);
    c=mix(c,c*1.06,uFem*front*inside(length((vec2(ax,p.z)-vec2(0.006,1.6216))/vec2(0.004,0.0011))-1.)*up);   // a touch of shine on the upper lip   // highlight on the lower lip
    float line=inside(abs(p.z-(1.6172+cz*1.2))-0.0009)*step(ax,0.0195)*front; c=mix(c,uLip*0.4,line);
    c=mix(c,c*(0.5+0.25*uFem),front*inside(length(vec2(ax-0.0072,p.z-1.6497))-0.0021*(1.-0.3*uFem)));            // nostrils
    // eyes: tilt and size by heritage; bright whites, coloured iris with a dark rim, pupil, catchlight
    float sz=uFace.w*(1.+0.22*uFem), tilt=uFace.x+0.08*uFem;
    vec2 e=vec2(ax-0.0338,p.z-1.6872); e.y-=tilt*e.x;                    // outer corners up
    float alm=length(e/vec2(0.0122*sz,0.0051*sz))-1.;
    float w=inside(alm)*front; c=mix(c,vec3(0.9,0.88,0.84),w);
    vec2 ic=e-vec2(-0.0004*sign(p.x),0.0003); float ri=length(ic);
    float ir=inside(ri-0.0047*sz)*w; vec3 icol=mix(uEye*1.25,uEye*0.7,smoothstep(0.0025,0.0047*sz,ri)); c=mix(c,icol,ir);
    c=mix(c,vec3(0.03),inside(ri-0.0019*sz)*w);
    c=mix(c,vec3(1.),inside(length(e-vec2(0.0013,0.0014))-0.0008*sz)*w);
    c*=1.-0.18*w*smoothstep(0.,0.004,e.y);
    c=mix(c,vec3(0.06,0.045,0.045),uFem*front*inside(abs(alm-0.06)-0.1)*step(-0.0035,-e.y)*step(e.x,0.009*sz)*0.5);   // a soft lower lash line                                                // the upper lid's shadow on the eye
    float lid=inside(abs(alm-0.1)-0.16-0.24*uFem)*step(-0.0008,e.y)*front; c=mix(c,vec3(0.08,0.06,0.05),lid*0.9);
    float wing=inside(abs(e.y-0.0008-(e.x-0.0115*sz)*0.55)-0.0011*(1.-smoothstep(0.0115*sz,0.0165*sz,e.x)))*step(0.0105*sz,e.x)*step(e.x,0.0165*sz);
    c=mix(c,vec3(0.06,0.045,0.045),uFem*front*wing);   // the winged lash line
    c=mix(c,c*vec3(0.9,0.8,0.84),uFem*0.6*front*gss(e,vec2(0.002,0.0065),vec2(0.017,0.0055)));  // soft colour on the lids
    c=mix(c,c*0.86,inside(abs(alm-0.6)-0.22)*step(0.0018,e.y)*front);                    // lid crease
    // brows: thin and arched to heavy and straight
    float bw=uFace.y, bx=ax-0.036;
    float bz=1.7005+(0.0035*(1.-bw)+0.0012+0.0025*uFem)*(1.-(bx*bx/0.000361))+0.0025*tilt*bx/0.02+0.0032*uFem;
    float thick=(0.0028+0.0034*bw)*(1.-0.4*smoothstep(0.,0.021,bx))*(1.-0.45*uFem);
    float brow=inside(abs(p.z-bz)-thick)*step(0.0115-0.002*bw,ax)*step(ax,0.058+0.003*bw)*front;
    c=mix(c,uHair*(0.6-0.15*bw)+vec3(0.02),brow*(0.85+0.15*bw));
  }
  // ink: a line down the brow, bars across the cheekbones, two lines on the chin
  if(uF1.z>0.5){float ink=0.;
    ink=max(ink,inside(ax-0.0032)*step(1.708,p.z)*step(p.z,1.79));
    ink=max(ink,inside(abs(p.z-1.6535-(ax-0.03)*0.12)-0.0035)*step(0.031,ax)*step(ax,0.078));
    ink=max(ink,inside(abs(ax-0.0105)-0.0022)*step(1.574,p.z)*step(p.z,1.598));
    c=mix(c,uInk,ink*front*0.92+ink*(1.-front)*0.5);}
  // hair painted on the scalp
  if(uF2.x>0.5){float hl=cardline(th)-0.004; float h=smoothstep(-0.007,0.006,p.z-hl)*step(ax,0.083+step(1.68,p.z))*0.9;   // fades softly into the skin, a few mm past the hair mesh's clean edge
    float strands=0.78+0.3*vnoise(vec2(th*90.,p.z*160.))+0.12*vnoise(vec2(th*12.,p.z*20.));
    c=mix(c,uHair*strands,h);}
  else c=mix(c,c*0.93,smoothstep(1.74,1.75,p.z)*0.5);
  return c;
}

vec3 paintClothes(vec3 p,float ax,bool armR);
vec3 linen(vec3 p,float k);
vec4 femWrap(vec3 p){ // a linen chest wrap: colour and coverage
  float band=inside(abs(p.z-1.3)-0.062); vec3 w=linen(p,1.)*1.04;
  w*=1.-0.04*smoothstep(0.35,0.5,abs(fract((p.z-1.238)*30.+0.6*vnoise(p.xz*40.))-0.5));   // soft, irregular folds w*=mix(0.85,1.,smoothstep(1.238,1.25,p.z))*mix(1.,0.85,smoothstep(1.35,1.362,p.z));
  w*=1.-0.08*smoothstep(0.03,0.07,p.y);                                               // the back, in its own shade
  return vec4(w,band);}
// ---- the base layer: bare skin, shaded softly like a painted texture, and plain undyed underclothes
vec3 skinTone(vec3 p){return uSkin*(0.965+0.045*vnoise(p.xz*170.)+0.02*vnoise(p.yz*55.));}
vec3 linen(vec3 p,float k){vec3 c=uPants*(0.93+0.07*vnoise(p.xz*vec2(240.,80.))); return c*(1.-0.05*k*(vnoise(p.xy*35.)-0.5));}
float NECK=0.;
vec3 paintBase(vec3 p,float ax,bool armR){
  float fr=1.-smoothstep(-0.06,0.0,p.y), bk=smoothstep(0.0,0.06,p.y);
  vec3 c=skinTone(p);
  if(armR){
    float wrist=0.962+(ax-0.35)*0.4;
    c*=1.+0.07*(1.-0.6*uFem)*gss(vec2(ax,p.z),vec2(0.215,1.43),vec2(0.035,0.05));                 // shoulder cap catches the light
    c*=1.+0.05*(1.-0.7*uFem)*fr*gss(vec2(ax,p.z),vec2(0.235,1.29),vec2(0.03,0.06));               // biceps
    c*=1.-0.06*(1.-0.6*uFem)*gss(vec2(ax,p.z),vec2(0.25,1.35),vec2(0.02,0.04))*bk;                  // back of the arm
    c=mix(c,c*vec3(1.05,0.9,0.86),0.55*(1.-0.5*uFem)*gss(vec2(ax,p.z),vec2(0.262,1.17),vec2(0.03,0.025)));   // ruddy elbow
    c*=1.+0.04*(1.-0.6*uFem)*gss(vec2(ax,p.z),vec2(0.28,1.07),vec2(0.03,0.06));                   // forearm
    if(p.z<wrist){c=mix(c,c*vec3(1.05,0.9,0.86),0.35);c*=mix(0.84,1.,smoothstep(0.72,0.86,p.z));} // warmer hands, shaded fingers
    c*=1.-0.18*gss(vec2(ax,p.z),vec2(0.19,1.37),vec2(0.02,0.05));                    // armpit
    c*=1.-0.13*smoothstep(1.3,1.45,p.z);                                            // match the torso where the shoulder meets it
    if(uF2.w>0.5&&ax>0.215){                                                          // Ferrin tattoos: bold geometric marks
      float t=0.;
      float d=p.z-1.065+p.y*0.45; t=max(t,inside(abs(d)-0.009)*step(abs(p.y),0.04)*step(1.0,p.z)*step(p.z,1.14));
      t=max(t,inside(abs(d-0.034)-0.005)*step(abs(p.y),0.04)*step(1.0,p.z)*step(p.z,1.16));
      float tz=(p.z-1.24)/0.065; t=max(t,inside(abs(p.y)-0.026*tz)*step(0.,tz)*step(tz,1.));
      for(int i=0;i<2;i++){float zz=1.385-float(i)*0.022; t=max(t,inside(abs(p.z-zz-abs(p.y)*0.55)-0.0055)*step(abs(p.y),0.035));}
      c=mix(c,uInk*0.85,t*0.85);}
    return c;}
  if(NECK>1.5||(NECK<0.5&&p.z>1.468&&ax<0.075)){                                  // neck (NECK: 0 by height, 1 never, 2 always)
    if(uFem>0.5){c*=1.-0.08*fr*smoothstep(1.5,1.556,p.z); return c;}               // her neck: smooth, only a soft shadow under the jaw
    c*=1.-0.16*fr*smoothstep(1.5,1.556,p.z);                                       // shadow under the jaw
    c*=1.-0.08*fr*gss(vec2(ax,p.z),vec2(0.,1.475),vec2(0.012,0.012));               // the pit of the throat
    return c;}
  if(p.z>1.04){                                                                      // torso
    if(uFem>0.5){                                                                    // her torso: soft forms, no muscle lines
      c*=1.-0.1*smoothstep(0.07,0.165,ax);                                          // rounding toward the sides
      c*=1.-0.08*gss(vec2(ax,p.z),vec2(0.165,1.37),vec2(0.025,0.05));               // a soft armpit
      c*=1.+0.05*fr*gss(vec2(ax,p.z),vec2(0.,1.15),vec2(0.06,0.08));               // light on the stomach
      float ub=1.252+0.012*(1.-pow(clamp((ax-0.075)/0.062,-1.,1.),2.));
      c*=1.-0.11*fr*exp(-pow((p.z-ub)/0.013,2.))*(1.-smoothstep(0.12,0.16,ax));    // the soft shadow beneath the bust
      c*=1.-0.04*fr*gss(vec2(ax,p.z),vec2(0.095,1.18),vec2(0.022,0.05));           // the ribcage curving in to the waist
      c*=1.-0.025*fr*exp(-pow(ax/0.006,2.))*smoothstep(1.1,1.13,p.z)*(1.-smoothstep(1.2,1.23,p.z));  // the faintest line above the navel
      c*=1.-0.3*fr*inside(length(vec2(ax/0.0035,(p.z-1.09)/0.007))-1.);           // navel
      c*=1.+0.04*fr*gss(vec2(ax,p.z),vec2(0.,1.06),vec2(0.05,0.03));               // the lower belly, softly lit
      c*=1.+0.03*fr*exp(-pow((p.z-(1.452-(ax-0.03)*0.15))/0.009,2.))*smoothstep(0.01,0.035,ax)*(1.-smoothstep(0.11,0.15,ax));  // collarbones, gently
      c*=1.-0.06*bk*exp(-pow(ax/0.014,2.));                                             // spine
      c*=1.+0.03*bk*gss(vec2(ax,p.z),vec2(0.07,1.35),vec2(0.04,0.05));               // shoulder blades
      return c*mix(0.88,1.,smoothstep(1.035,1.07,p.z));}
    c*=1.-0.13*smoothstep(0.08,0.17,ax);                                            // rounding toward the sides
    c*=1.-0.2*gss(vec2(ax,p.z),vec2(0.165,1.37),vec2(0.025,0.05));                  // armpits
    vec3 soft=c;
    float pz=1.296+0.02*(1.-clamp(abs(ax-0.075)/0.075,0.,1.));
    c*=1.+0.07*fr*gss(vec2(ax,p.z),vec2(0.075,1.355),vec2(0.05,0.035));             // chest catches the light
    c*=1.-0.12*fr*exp(-pow((p.z-pz)/0.017,2.))*(1.-smoothstep(0.12,0.17,ax))*smoothstep(0.,0.025,ax);  // soft shadow under the chest
    c*=1.-0.06*fr*exp(-pow(ax/0.011,2.))*smoothstep(1.2,1.24,p.z)*(1.-smoothstep(1.4,1.44,p.z));  // breastbone
    c*=1.+0.05*fr*exp(-pow((p.z-(1.452-(ax-0.03)*0.15))/0.009,2.))*smoothstep(0.01,0.035,ax)*(1.-smoothstep(0.11,0.15,ax));  // collarbones, lit
    c*=1.-0.05*fr*exp(-pow((p.z-(1.436-(ax-0.03)*0.15))/0.009,2.))*smoothstep(0.01,0.035,ax)*(1.-smoothstep(0.11,0.15,ax));  // and the hollow beneath
    float rows=0.; for(int i=0;i<3;i++){rows+=gss(vec2(ax,p.z),vec2(0.03,1.235-float(i)*0.055),vec2(0.02,0.022));}
    c*=1.+0.03*fr*rows;                                                              // the stomach: only a hint of form
    c*=1.-0.045*fr*exp(-pow(ax/0.008,2.))*smoothstep(1.07,1.1,p.z)*(1.-smoothstep(1.24,1.27,p.z));
    c*=1.-0.06*fr*gss(vec2(ax,p.z),vec2(0.125,1.12),vec2(0.02,0.06));               // obliques
    if(uFem>0.5){                                                                    // a linen chest wrap
      return c*mix(0.84,1.,smoothstep(1.035,1.07,p.z));}   // the chest wrap is laid over in paintBody, all the way round
    c=mix(c,c*vec3(0.88,0.74,0.7),fr*(1.-smoothstep(0.004,0.0085,length(vec2(ax-0.084,p.z-1.317)))));  // nipples
    c*=1.-0.22*fr*gss(vec2(ax,p.z),vec2(0.,1.088),vec2(0.0045,0.006));              // navel
    c*=1.-0.1*bk*exp(-pow(ax/0.012,2.));                                              // spine
    c*=1.+0.05*bk*gss(vec2(ax,p.z),vec2(0.07,1.35),vec2(0.04,0.05));                // shoulder blades
    c=mix(soft,c,0.25+0.75*uB.w);                                                   // leaner people show less muscle
    if(uB.z>0.){float m=fr*(gss(vec2(ax,p.z),vec2(0.045,1.33),vec2(0.06,0.05))+exp(-pow(ax/0.014,2.))*step(p.z,1.4)*(1.-smoothstep(1.0,1.04,p.z)*0.)*step(1.04,p.z)*0.8);
      float sp=smoothstep(0.5,0.75,vnoise(p.xz*vec2(320.,140.))); c=mix(c,uHair*0.85,clamp(m,0.,1.)*sp*0.6*uB.z);}   // chest hair
    c*=mix(0.84,1.,smoothstep(1.035,1.07,p.z));                                     // shade above the waistband
    return c;}
  if(p.z>0.985){                                                                     // drawstring waistband
    c=linen(p,0.3)*0.86; c*=1.-0.18*inside(abs(p.z-0.99)-0.003); c*=1.-0.12*inside(abs(p.z-1.035)-0.003);
    c*=1.-0.1*step(0.5,fract(ax*90.+0.25))*fr;                                         // gathered folds
    float kn=fr*inside(length(vec2(ax,p.z-1.012))-0.007); c=mix(c,uPants*0.62,kn);
    float str=fr*inside(abs(ax-0.003*sin(p.z*300.))-0.0028)*step(0.95,p.z)*(1.-step(1.008,p.z)); c=mix(c,uPants*0.6,str);
    return c;}
  float lx=ax-0.11, hem=uB.y>0.5?0.70:0.13;
  if(p.z>hem){                                                                       // boxers or trousers (to the ankle)
    c=linen(p,1.5);
    c*=0.92+0.08*(1.-smoothstep(0.,0.05,abs(lx)));
    c*=1.-0.1*fr*exp(-pow(ax/0.02,2.))*smoothstep(0.9,0.82,p.z);                       // the fork
    c*=1.-0.07*vnoise(vec2(p.x*40.,p.z*25.))*smoothstep(0.9,0.75,p.z);              // soft folds
    c*=mix(0.78,1.,smoothstep(hem,hem+0.03,p.z));                                     // turned-up hem
    c*=1.-0.15*inside(abs(p.z-hem-0.02)-0.0015);
    if(uB.y<0.5){c*=1.-0.08*gss(vec2(lx,p.z),vec2(0.,0.52),vec2(0.05,0.03)); c*=1.-0.06*vnoise(vec2(p.x*30.,p.z*12.))*smoothstep(0.35,0.15,p.z);}  // knee, gathered ankles
    return c;}
  if(p.z>0.1){                                                                       // bare legs and ankles
    c*=0.94+0.07*(1.-smoothstep(0.,0.05,abs(lx)));
    c=mix(c,c*vec3(1.04,0.9,0.86),0.5*fr*gss(vec2(lx,p.z),vec2(0.,0.52),vec2(0.04,0.03)));  // ruddy knees
    c*=1.+0.05*(1.-0.7*uFem)*fr*gss(vec2(lx,p.z),vec2(0.,0.43),vec2(0.02,0.06));                   // shin
    c*=1.-0.06*(1.-0.7*uFem)*bk*gss(vec2(lx,p.z),vec2(0.,0.4),vec2(0.05,0.08));                    // calf shadow
    c*=1.-0.08*gss(vec2(ax-0.125,p.z),vec2(0.03,0.12),vec2(0.01,0.012));            // ankle bones
    c*=1.-0.08*gss(vec2(ax-0.125,p.z),vec2(-0.03,0.12),vec2(0.01,0.012));
    return c;}
  // bare feet: warmer, darker underneath, toes painted at the front
  c=mix(c,c*vec3(1.05,0.9,0.86),0.3); c*=mix(0.8,1.,smoothstep(0.0,0.05,p.z));
  float dx=ax-0.15, toes=1.-smoothstep(-0.11,-0.13,-p.y);
  float gap=0.; for(int i=0;i<4;i++){gap=max(gap,inside(abs(dx-(-0.016+float(i)*0.011))-0.0012));}
  c*=1.-0.35*gap*toes*step(p.z,0.05);
  c=mix(c,c*vec3(1.1,1.0,0.95)*1.08,0.5*toes*step(0.025,p.z)*step(p.z,0.045)*(1.-gap));  // nails catch the light
  c*=1.-0.1*gss(vec2(dx,p.y),vec2(0.,0.03),vec2(0.02,0.03))*step(p.z,0.06);         // heel
  return c;
}
vec3 paintBody(vec3 p){
  // how much a point belongs to the arm comes from the rig's own skin weights (vTorso), so arm and torso paint meet where the body bends
  float ax=abs(p.x), arm=1.-smoothstep(0.3,0.7,vTorso); bool armR=arm>0.5;
  float hk=(1.-arm)*smoothstep(1.535,1.568,p.z);                                   // face paint fades in up the neck, no line
  if(hk>0.998)return paintHead(p);
  if(uB.x>0.5){
    vec3 r=(arm>0.002&&arm<0.998)?mix(paintBase(p,ax,false),paintBase(p,ax,true),arm):paintBase(p,ax,armR);
    float nk=(1.-arm)*smoothstep(1.452,1.484,p.z)*(1.-smoothstep(0.062,0.088,ax));   // the neck fades in over the collar, no line
    if(nk>0.002&&nk<0.998&&p.z>1.04){NECK=1.;vec3 t=paintBase(p,ax,false);NECK=2.;vec3 n=paintBase(p,ax,false);NECK=0.;r=mix(r,mix(t,n,nk),1.-arm);}
    if(uFem>0.5&&abs(p.z-1.3)<0.07){vec4 w=femWrap(p); r=mix(r,w.rgb,w.a*(1.-arm));}   // the wrap goes all the way round the torso, never onto the arm
    if(hk>0.002)r=mix(r,paintHead(p),hk);
    return r;}
  return paintClothes(p,ax,armR);
}
vec3 paintClothes(vec3 p,float ax,bool armR){
  vec3 c;
  if(armR){ // sleeves to the wrist, then hands (bare or gloved)
    float wrist=0.962+(ax-0.35)*0.4;
    if(p.z>wrist&&uF1.y>0.5){c=uSkin*(0.95+0.05*vnoise(p.xz*200.));c*=1.-0.12*gss(vec2(ax-0.24,p.z-1.32),vec2(0.),vec2(0.02,0.05));c*=1.+0.08*gss(vec2(ax-0.21,p.z-1.4),vec2(0.),vec2(0.03,0.03));}
    else if(p.z>wrist){c=cloth(uShirt,p,1.);if(uF2.z>2.5)c=cloth(uVest,p,1.); c*=mix(0.82,1.,smoothstep(wrist,wrist+0.03,p.z)); c=mix(c,c*0.7,inside(abs(p.z-wrist-0.022)-0.0012)*step(0.5,fract(p.x*220.)));}
    else if(uF2.y>0.5){c=cloth(uBelt,p,0.5);c=mix(c,c*0.7,inside(abs(p.z-wrist+0.006)-0.004));}
    else{c=uSkin*(0.95+0.05*vnoise(p.xz*200.));c*=mix(0.85,1.,smoothstep(0.78,0.86,p.z));}
    return c;}
  if(p.z>1.468){ // neck, with the collar
    c=uSkin*mix(0.86,0.97,smoothstep(1.47,1.53,p.z));
    float collar=(1.-step(0.5,uF1.y))*step(p.z,1.505)*(1.-step(p.y,-0.02)*inside(ax-(p.z-1.468)*0.9)); c=mix(c,cloth(uShirt,p,1.)*0.95,collar);
    return c;}
  if(p.z>1.04&&uF1.y>0.5){ // bare torso: muscle painted in, as Valheim does
    float fr=1.-smoothstep(-0.05,0.01,p.y);
    c=uSkin*(0.96+0.04*vnoise(p.xz*220.));
    float pec=1.29+0.035*(1.-pow(clamp((ax-0.075)/0.075,-1.,1.),2.));
    c*=1.-0.3*fr*exp(-pow((p.z-pec)/0.009,2.))*step(ax,0.16);                       // under the pecs
    c*=1.+0.08*fr*gss(vec2(ax,p.z),vec2(0.075,1.34),vec2(0.045,0.035));             // pecs catch the light
    c*=1.-0.18*fr*inside(ax-0.0035)*step(1.08,p.z)*step(p.z,1.3);                   // the line down the middle
    for(int i=0;i<3;i++){float zz=1.125+float(i)*0.05;c*=1.-0.14*fr*exp(-pow((p.z-zz)/0.005,2.))*step(ax,0.05);}  // abs
    c*=1.-0.2*fr*exp(-pow((p.z-(1.448-(ax-0.03)*0.18))/0.005,2.))*step(0.02,ax)*step(ax,0.13);  // collarbones
    c=mix(c,c*vec3(0.75,0.55,0.5),fr*inside(length(vec2(ax-0.085,p.z-1.315))-0.006));          // nipples
    c*=1.-0.35*fr*inside(length(vec2(ax,p.z-1.085))-0.004);                        // navel
    c*=1.-0.15*smoothstep(0.,0.06,p.y)*gss(vec2(ax,p.z),vec2(0.,1.3),vec2(0.012,0.12));  // spine
    c*=mix(0.84,1.,smoothstep(1.04,1.075,p.z));
    return c;}
  if(p.z>1.04){ // torso: shirt, perhaps a waistcoat over it
    c=cloth(uShirt,p,1.);
    if(uF2.z>0.5&&uF2.z<1.5){float s=step(0.5,fract(p.z*38.));c=mix(c,c*vec3(0.75,0.78,0.92),s*0.5);} // striped linen
    float vee=step(p.y,-0.02)*inside(ax-(p.z-1.39)*0.55)*step(1.39,p.z); c=mix(c,uSkin*0.9,vee);
    c=mix(c,c*0.65,step(p.y,-0.02)*inside(ax-0.0011)*step(p.z,1.39)*step(1.25,p.z)); // placket
    if(uF1.x>0.5){float open=step(p.y,-0.02)*inside(ax-0.018-(p.z-1.2)*0.12);
      float top=1.47-0.75*max(0.,ax-0.055); float arm=max(inside(length(vec2((ax-0.168)/0.072,(p.z-1.452)/0.13))-1.),1.-inside(p.z-top));
      float v=(1.-open)*(1.-arm);
      vec3 vc=cloth(uVest,p,1.); vc=mix(vc,vc*0.72,inside(abs(ax-0.018-(p.z-1.2)*0.12-0.006)-0.0009)*step(0.5,fract(p.z*120.))*step(p.y,-0.02));
      vc=mix(vc,uTrim,step(p.y,-0.02)*inside(length(vec2(ax-0.03-(p.z-1.2)*0.12,mod(p.z-1.06,0.045)-0.022))-0.0042));
      c=mix(c,vc,v);}
    if(uF2.w>0.5){float tb=inside(ax-0.115)*step(1.06,p.z)*step(p.z,1.43); vec3 t=cloth(uTrim,p,0.6); t=mix(t,t*0.7,inside(abs(ax-0.105)-0.003)); c=mix(c,t,tb);}
    c*=mix(0.82,1.,smoothstep(1.04,1.075,p.z));
    return c;}
  if(p.z>0.985){ // belt and buckle
    c=cloth(uBelt,p,0.3); c=mix(c,c*0.6,inside(abs(p.z-1.0125)-0.024)*inside(-(abs(p.z-1.0125)-0.021)));
    float bk=step(p.y,-0.02)*inside(max(ax-0.02,abs(p.z-1.0125)-0.02)); c=mix(c,uTrim,bk); c=mix(c,uTrim*0.5,bk*inside(max(ax-0.011,abs(p.z-1.0125)-0.011)));
    return c;}
  if(p.z>0.335){ // trousers
    c=cloth(uPants,p,1.5);
    float lx=ax-0.11; c*=0.92+0.08*(1.-smoothstep(0.,0.05,abs(lx))); // rounder down the middle of each leg
    c=mix(c,c*0.75,inside(abs(lx-0.055)-0.0011)*step(0.5,fract(p.z*110.)));                 // outer seam
    c*=1.-0.1*gss(vec2(lx,p.z),vec2(0.,0.52),vec2(0.05,0.03));                               // knee
    c*=mix(0.8,1.,smoothstep(0.335,0.37,p.z));
    return c;}
  // boots
  c=cloth(uBoots,p,0.4)*mix(1.08,0.9,1.-smoothstep(0.05,0.33,p.z));
  c=mix(c,c*1.25,inside(abs(p.z-0.315)-0.018)); c=mix(c,vec3(0.08,0.06,0.05),inside(p.z-0.028));
  c=mix(c,c*0.6,inside(abs(p.z-0.296)-0.0012));
  return c;
}`;
function preparePainted(gltf){
  gltf.scene.traverse(o=>{if(!o.isMesh||o.geometry.userData.rest)return;const ca=o.geometry.attributes.color;o.geometry.userData.rest=true;
    const sz=ca.itemSize,src=ca.array,div=!ca.normalized?1:src instanceof Uint8Array?255:src instanceof Uint16Array?65535:1,out=new Float32Array(ca.count*3);
    const tm=new Float32Array(ca.count);
    for(let i=0;i<ca.count;i++){out[i*3]=src[i*sz]/div-0.5;out[i*3+1]=src[i*sz+1]/div-0.5;out[i*3+2]=src[i*sz+2]/div*2;tm[i]=sz>3?src[i*sz+3]/div:1.;}
    o.geometry.setAttribute('rest',new THREE.BufferAttribute(out,3)); o.geometry.setAttribute('torso',new THREE.BufferAttribute(tm,1)); o.geometry.deleteAttribute('color');});
}
// heritage in the face: eye tilt, brow weight, socket depth, eye size | cheekbones, jaw, warmth, lip fullness
const FACES={
  Aurelan:  [0.0, 0.45,0.35,1.0,  0.45,0.4, 0.3,0.5],
  Wayfolk:  [0.0, 0.5, 0.35,1.0,  0.35,0.4, 0.4,0.5],
  Hrimfolk: [-0.05,0.95,0.8,0.95, 0.55,0.9, 0.85,0.35],
  Ilvari:   [0.32,0.1, 0.25,1.08, 0.95,0.15,0.1,0.55],
  Ferrin:   [-0.08,1.0,0.7,0.95,  0.35,0.85,0.9,0.4],
  Zarhim:   [0.12,0.7, 0.5,1.02,  0.9,0.55, 0.15,0.6],
  Ruadhan:  [0.05,0.4, 0.3,1.04,  0.6,0.45, 0.75,0.5],
  Penitent: [0.0, 0.5, 0.75,0.98, 0.8,0.5, 0.0,0.4],
  'City watch':[0.0,0.65,0.5,1.0, 0.5,0.65, 0.4,0.45]};
const PAINT_KEYS=['uSkin','uHair','uEye','uShirt','uVest','uPants','uBelt','uBoots','uTrim','uInk','uLip'];
function paintedMaterial(look){
  const U={}; PAINT_KEYS.forEach(k=>U[k]={value:new THREE.Color(look[k]||'#888888')}); U.uF1={value:new THREE.Vector4(...look.f1)}; U.uF2={value:new THREE.Vector4(...look.f2)}; U.uFem={value:look.fem?1:0}; const F=look.face||FACES[look.people||look.name]||FACES.Aurelan; U.uFace={value:new THREE.Vector4(F[0],F[1],F[2],F[3])}; U.uFace2={value:new THREE.Vector4(F[4],F[5],F[6],F[7])}; U.uB={value:new THREE.Vector4(...(look.base||[0,0,0,1]))};
  const m=new THREE.MeshLambertMaterial({skinning:true,morphTargets:true,morphNormals:true}); m.extensions={derivatives:true};
  m.onBeforeCompile=sh=>{Object.assign(sh.uniforms,U);
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nattribute vec3 rest;\nattribute float torso;\nvarying vec3 vRest;\nvarying float vTorso;').replace('#include <begin_vertex>','#include <begin_vertex>\nvRest=rest;vTorso=torso;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>','#include <common>\nvarying float vTorso;\n'+PAINT_GLSL).replace('vec4 diffuseColor = vec4( diffuse, opacity );','vec4 diffuseColor = vec4( paintBody(vRest), opacity );');};
  m.customProgramCacheKey=()=>'painted-body'; m.userData.U=U; return m;
}
// hair and beards: their own meshes, shaded with strands that run with the locks
function hairMaterial(hex){
  const U={uHair:{value:new THREE.Color(hex)}};
  const m=new THREE.MeshLambertMaterial({skinning:true}); m.extensions={derivatives:true};
  m.onBeforeCompile=sh=>{Object.assign(sh.uniforms,U);
    sh.vertexShader=sh.vertexShader.replace('#include <common>','#include <common>\nattribute vec3 rest;\nvarying vec3 vRest;').replace('#include <begin_vertex>','#include <begin_vertex>\nvRest=rest;');
    sh.fragmentShader=sh.fragmentShader.replace('#include <common>',`#include <common>
uniform vec3 uHair; varying vec3 vRest;
float hh(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
float hn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hh(i),hh(i+vec2(1.,0.)),f.x),mix(hh(i+vec2(0.,1.)),hh(i+vec2(1.,1.)),f.x),f.y);}`)
      .replace('vec4 diffuseColor = vec4( diffuse, opacity );',`float th=atan(vRest.x,-(vRest.y-0.002));
  // painted strands: broad clumps, fine streaks, and dark grooves between clumps
  float w=hn(vec2(th*9.,vRest.z*14.))*0.9;
  float clump=fract(th*5.+w*1.3+hn(vec2(th*3.,vRest.z*40.))*0.25);
  float groove=smoothstep(0.84,0.98,clump)+(1.-smoothstep(0.0,0.05,clump))*0.5;
  float s=0.55*hn(vec2(th*60.+w*3.,vRest.z*6.))+0.45*hn(vec2(th*170.,vRest.z*20.));
  float shade=mix(0.74,1.06,s)*(1.-0.28*groove);
  shade*=mix(0.78,1.,smoothstep(1.5,1.6,vRest.z));                 // beard tips and the underside go darker
  vec4 diffuseColor=vec4(uHair*shade,opacity);`);};
  m.customProgramCacheKey=()=>'painted-hair'; return m;
}
const HAIR_MESHES=['Hair_Short','Hair_Swept','Hair_Ponytail','Hair_Long','Hair_Topknot','Beard_Full','Beard_Short','Beard_Pointed','Beard_Braided','Beard_Forked','Moustache_Chevron','Moustache_Horseshoe','Moustache_Walrus','Moustache_Handlebar','Moustache_Pencil'];
// Low-poly hair (tools/blender/hair.py): a scalp cap and a few locks per style, a few hundred triangles, textured from
// tex/hair.png and cut out by its alpha. Installed once per figure in place of the older hair meshes of the same name; it is
// skinned to the figure's own skeleton and shares the body's shape weights, so it fits every people and build.
const HAIR_TEX=(typeof THREE!=='undefined')?new THREE.TextureLoader().load('tex/hair.png',t=>{t.anisotropy=4;}):null;
function hairInstall(root,sex){
  if(typeof HAIR_CARDS==='undefined'||!HAIR_CARDS[sex]||root.userData.hairCards===sex)return;
  let body=null;root.traverse(o=>{if(!body&&o.isSkinnedMesh&&o.morphTargetDictionary&&'Lean' in o.morphTargetDictionary)body=o;});if(!body)return;
  const styles=HAIR_CARDS[sex],old=[];
  root.traverse(o=>{if(o.isMesh&&(o.userData.hairCard||Object.keys(styles).some(k=>o.name.startsWith('Hair_'+k))))old.push(o);});
  for(const o of old)o.parent.remove(o);
  const bones=body.skeleton.bones,san=n=>n.replace(/[\s\.\[\]:\/]/g,''),names=Object.keys(body.morphTargetDictionary).sort((a,b)=>body.morphTargetDictionary[a]-body.morphTargetDictionary[b]);
  for(const [style,H] of Object.entries(styles)){
    const g=new THREE.BufferGeometry(),n=H.pos.length/3;
    g.setAttribute('position',new THREE.Float32BufferAttribute(H.pos,3));g.setAttribute('normal',new THREE.Float32BufferAttribute(H.nrm,3));
    g.setAttribute('uv',new THREE.Float32BufferAttribute(H.uv,2));g.setAttribute('rest',new THREE.Float32BufferAttribute(H.rest,3));
    const bi=H.bones.map(b=>Math.max(0,bones.findIndex(x=>san(x.name)===san(b)))),si=new Uint16Array(n*4),sw=new Float32Array(n*4);
    H.skin.forEach((w,i)=>w.forEach((x,k)=>{si[i*4+k]=bi[k];sw[i*4+k]=x;}));
    g.setAttribute('skinIndex',new THREE.BufferAttribute(si,4));g.setAttribute('skinWeight',new THREE.BufferAttribute(sw,4));
    g.morphAttributes.position=names.map(k=>new THREE.Float32BufferAttribute(H.morph[k]||new Array(n*3).fill(0),3));g.morphTargetsRelative=true;
    g.setIndex(H.idx);g.computeBoundingSphere();g.userData.hairCard=true;g.userData.rest=true;
    const m=new THREE.SkinnedMesh(g,new THREE.MeshBasicMaterial());m.name='Hair_'+style;m.userData.hairCard=true;m.frustumCulled=false;
    m.bind(body.skeleton,body.bindMatrix);m.morphTargetInfluences=body.morphTargetInfluences;body.parent.add(m);}
  root.userData.hairCards=sex;
}
function hairCardMaterial(hex){
  const m=new THREE.MeshLambertMaterial({map:HAIR_TEX,color:new THREE.Color(hex).multiplyScalar(1.15),alphaTest:0.5,side:THREE.DoubleSide,skinning:true,morphTargets:true});
  m.onBeforeCompile=sh=>{sh.fragmentShader=sh.fragmentShader.replace(/gl_FrontFacing/g,'true');};   // both faces of a card light as its front: cards stand for volume
  m.customProgramCacheKey=()=>'hair-card';
  m.userData.depth=new THREE.MeshDepthMaterial({depthPacking:THREE.RGBADepthPacking,map:HAIR_TEX,alphaTest:0.5,skinning:true,morphTargets:true});
  return m;
}
function dressFigure(root,look){ // body gets the paint, chosen hair and beard get hair, the rest hide
  hairInstall(root,look.fem?'f':'m');
  const want=new Set([look.hair&&'Hair_'+look.hair,look.beard&&'Beard_'+look.beard,look.moustache&&'Moustache_'+look.moustache].filter(Boolean));
  root.traverse(o=>{if(!o.isMesh)return;o.frustumCulled=false;o.castShadow=true;
    const n=HAIR_MESHES.find(h=>o.name.startsWith(h));
    if(!n){o.material=paintedMaterial(look);o.visible=true;}else if(want.has(n)){if(o.userData.hairCard){o.material=hairCardMaterial(look.uHair);o.customDepthMaterial=o.material.userData.depth;}else o.material=hairMaterial(look.uHair);o.visible=true;}else o.visible=false;});
}

// body type: Lean and Heavy blend shapes on the one body, and a posture that goes with them
function setBuild(root,lean,heavy){
  root.userData.build=[lean,heavy];
  root.traverse(o=>{if(o.isMesh&&o.morphTargetDictionary&&'Lean' in o.morphTargetDictionary){o.morphTargetInfluences[o.morphTargetDictionary.Lean]=lean;o.morphTargetInfluences[o.morphTargetDictionary.Heavy]=heavy;}});
}
// Posture, laid over the animation each frame. Offsets are applied once, never accumulated: [bone, axis, per lean, per heavy,
// always]. The arms are brought in toward the thighs (the clips hang them a little wide). root.userData.pose adds offsets of
// its own ({'head.y': 0.2, ...}), which NPC personality drives.
const POSTURE=[['spine','x',0.1,0,0],['neck','x',0.16,0,0],['head','x',-0.12,0,0],['upper_armL','z',0,0.2,0.26],['upper_armR','z',0,-0.2,-0.26],
  ['forearmL','z',0,0,0.06],['forearmR','z',0,0,-0.06]];
function buildPosture(root){ // call after the animation mixer each frame
  const [lean,heavy]=root.userData.build||[0,0], pose=root.userData.pose||{};
  const want=new Map();   // bone -> {x, y, z}
  const add=(k,v)=>{const d=k.lastIndexOf('.'),n=k.slice(0,d),ax=k.slice(d+1);if(!want.has(n))want.set(n,{x:0,y:0,z:0});want.get(n)[ax]+=v;};
  for(const [n,ax,kl,kh,k0] of POSTURE)add(n+'.'+ax,kl*lean+kh*heavy+k0);
  for(const k in pose)add(k,pose[k]);
  const B=root.userData.bones||(root.userData.bones={map:new Map()});
  for(const n of B.map.keys())if(!want.has(n))want.set(n,{x:0,y:0,z:0});
  for(const [n,off] of want){   // per bone: undo last frame's offsets if the mixer left the bone alone, then apply this frame's
    let e=B.map.get(n); if(!e){const o=root.getObjectByName(n);if(!o)continue;e={o,prev:{x:0,y:0,z:0},q:null};B.map.set(n,e);}
    if(e.q&&e.o.quaternion.equals(e.q)){e.o.rotation.x-=e.prev.x;e.o.rotation.y-=e.prev.y;e.o.rotation.z-=e.prev.z;}
    e.o.rotation.x+=off.x;e.o.rotation.y+=off.y;e.o.rotation.z+=off.z; e.prev=off; e.q=e.o.quaternion.clone();
  }
}

function setDefinition(root,d){root.traverse(o=>{if(o.material&&o.material.userData&&o.material.userData.U&&o.material.userData.U.uB)o.material.userData.U.uB.value.w=d;});}

/* ---------- One body per sex, peoples as built-in shapes: the morph changes the mesh, the skeleton follows ---------- */
const SANE=n=>n.replace(/\s/g,'_').replace(/[\[\]\.:\/]/g,'');
function rigPeople(root,gltf){ // once per figure, straight after cloning (at rest, before any animation)
  const meshes=[]; root.traverse(o=>{if(o.isSkinnedMesh)meshes.push(o);});
  const body=meshes.find(o=>o.morphTargetDictionary&&'Lean' in o.morphTargetDictionary); if(!body)return;
  const bones=body.skeleton.bones, P=root.parent; root.parent=null;
  const s0=root.position.clone(),q0=root.quaternion.clone(),k0=root.scale.clone(); root.position.set(0,0,0);root.quaternion.identity();root.scale.set(1,1,1); root.updateMatrixWorld(true);
  const rest=new Map(); for(const b of bones)rest.set(b,{pos:b.position.clone(),quat:b.quaternion.clone(),scl:b.scale.clone()});
  const top=bones.find(b=>!b.parent||!b.parent.isBone), anchor=top.parent?top.parent.matrixWorld.clone():new THREE.Matrix4();
  root.position.copy(s0);root.quaternion.copy(q0);root.scale.copy(k0); root.parent=P;
  root.userData.rig={body,bones,rest,anchor,joints:(gltf.scene.userData||{}).peopleJoints||null,clips:gltf.animations,people:'Human',cache:{}};
}
function peopleClip(rig,clip){ // positions in the clips are the human skeleton's: rebase them on this people's joints
  const key=rig.people+'/'+clip.name; if(rig.cache[key])return rig.cache[key];
  const c=clip.clone();
  c.tracks=c.tracks.filter(t=>{
    if(!t.name.endsWith('.position'))return true;
    const b=rig.bones.find(x=>t.name.startsWith(x.name+'.')); if(!b)return true;
    const r=rig.rest.get(b), n=rig.local&&rig.local.get(b); if(!n)return true;
    if(b===rig.bones.find(x=>!x.parent||!x.parent.isBone)){ // the hips keep their motion, moved to the new rest
      t.values=t.values.slice(); for(let i=0;i<t.values.length;i+=3){t.values[i]+=n.x-r.pos.x;t.values[i+1]+=n.y-r.pos.y;t.values[i+2]+=n.z-r.pos.z;} return true;}
    return false;});   // other bones only rotate: their positions come from the people's skeleton
  rig.cache[key]=c; return c;
}
function setPeople(root,name){
  const rig=root.userData.rig; if(!rig)return;
  const body=rig.body, d=body.morphTargetDictionary;
  for(const k of ['Ferrin','Ilvari','Zarhim','Aurelan'])if(k in d)body.morphTargetInfluences[d[k]]=(k===name)?1:0;
  const J=rig.joints&&(rig.joints[name]||rig.joints.Human); rig.people=(rig.joints&&rig.joints[name])?name:'Human';
  if(!J){rig.local=null;return;}
  const byName={}; for(const k in J)byName[SANE(k)]=new THREE.Vector3(...J[k]);
  const world=new Map(), local=new Map(), inv=[], m=new THREE.Matrix4(), one=new THREE.Vector3(1,1,1);
  const depth=b=>{let n=0;for(let p=b.parent;p&&p.isBone;p=p.parent)n++;return n;};
  for(const b of rig.bones.slice().sort((a,c)=>depth(a)-depth(c))){
    const r=rig.rest.get(b), pw=b.parent&&b.parent.isBone?world.get(b.parent):rig.anchor;
    const target=byName[b.name]; let lp=r.pos.clone();
    if(target){const pi=pw.clone().invert(); lp=target.clone().applyMatrix4(pi);}
    const wm=pw.clone().multiply(m.compose(lp,r.quat,one)); world.set(b,wm); local.set(b,lp);
  }
  rig.local=local;
  for(const b of rig.bones){b.position.copy(local.get(b));}
  body.skeleton.boneInverses=rig.bones.map(b=>world.get(b).clone().invert());   // the body binds to the people's skeleton;
  // hair and beards keep their human binding, so they ride along with the head wherever it moved
}
function playPeople(root,mixer,clipName){
  const rig=root.userData.rig, src=(rig?rig.clips:[]).find(c=>c.name===clipName); if(!src)return null;
  mixer.stopAllAction(); const a=mixer.clipAction(rig?peopleClip(rig,src):src); a.play(); return a;
}

