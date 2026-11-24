// Fogwright NPCs: who they are, what they wear and how they carry themselves, all from a seed. Shared by the townsfolk
// page and the game. Load after bodypaint.js, equip.js and peoples.js.
// npcGenerate(seed, {people, trade, sex}) -> a person (plain data, safe to save)
// npcSpawn(bodies, person, renderer, tier) -> a figure on the MakeHuman bodies, dressed for its detail tier
// npcAnimate(figure, dt) -> each frame, after the mixer: the person's posture, glances and sway
'use strict';

/* ---------- chance ---------- */
function npcRng(seed){let a=seed>>>0;return ()=>{a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
const npcPick=(r,a)=>a[Math.floor(r()*a.length)];
function npcWeighted(r,list){ // [[value, weight], ...]
  const tot=list.reduce((s,[,w])=>s+w,0);let x=r()*tot;for(const [v,w] of list){if((x-=w)<=0)return v;}return list[list.length-1][0];}

/* ---------- names, in each people's own sound ---------- */
const NPC_NAMES={
  Hrimfolk:{m:[['Hro','Sig','Ulf','Bjar','Thor','Ein','Rag','Hal','Grim','Vig'],['vald','urd','ar','nir','grim','mund','olf','stein']],
            f:[['Ast','Sig','Ing','Hild','Ran','Thy','Gud','Fre','Sol','Bry'],['rid','dis','veig','run','a','hild','ny']],
            last:['Frostborn','Ironhand','Ulfsson','of the Skerries','Halvardsdottir','Sealkeeper','Rimewalker']},
  Aurelan:{m:[['Aur','Mar','Val','Cas','Lor','Fel','Ten','Ser','Dar','Ott'],['elio','ius','en','ano','ric','is','orin']],
           f:[['Aur','Mar','Sel','Ves','Lia','Cor','Ele','Ise','Ama','Ros'],['ela','ina','ette','ia','ara','enne','ise']],
           last:['Dellacorte','of Solmere','Vantelli','Marrow','Castellane','Orvane','Pellisor']},
  Ilvari:{m:[['Ael','Ser','Ith','Vey','Cael','Lir','Thal','Ny','Eir','Sil'],['vyn','ith','orin','ael','ian','eth','ar']],
          f:[['Ile','Sera','Ny','Aes','Lyr','Eli','Ithi','Vael','Ser','Ama'],['wen','ith','ra','lis','ne','iel','vae']],
          last:['of no fixed road','Inkbound','Starwright','Velarin','Quietbrook','Lanternsworn']},
  Ferrin:{m:[['Dur','Brak','Gor','Thom','Kal','Mor','Bal','Hag','Dun','Grub'],['grim','dok','ram','in','uk','ash','mar','bolt']],
          f:[['Brun','Dag','Hel','Kat','Mag','Tor','Hil','Gret','Bet','Ruk'],['hild','na','ka','da','ra','wyn','ga']],
          last:['Slagborn','Anvilhand','of Ashforge','Coalbeard','Rivetson','Hammerfall','Gearwright']},
  Zarhim:{m:[['Kha','Zar','Ras','Tar','Am','Sa','Ha','Na','Far','Ja'],['im','ir','ad','eem','oud','ib','an','esh']],
          f:[['Za','Lei','Ya','Sa','Na','Ri','Ami','Fa','Sha','Da'],['ra','la','sha','mina','ida','iya','nah']],
          last:['al-Qaraseth','of the Sere','ibn Khesra','Duneborn','Wellfinder','Saltrider']},
  Ruadhan:{m:[['Ruai','Bran','Cor','Fearg','Dom','Ena','Lach','Oisin','Tor','Cael'],['ach','nan','an','gus','ri','lan','dhan']],
           f:[['Aoi','Brig','Mor','Eith','Siob','Cia','Fia','Nia','Una','Roi'],['fe','id','na','ne','han','ra','bhe']],
           last:['of Dun Brannoch','MacRuai','Redwold','Hillborn','Oakshield','Ferncroft']},
  Wayfolk:{m:[['Tom','Hal','Will','Jon','Ned','Sam','Rob','Wat','Hob','Kit'],['','','','son','kin','ley']],
           f:[['Meg','Nell','Bess','Ann','Mol','Kate','Jen','Rose','Lil','Mae'],['','','ie','a','y','wyn']],
           last:['Miller','Roadwell','Tanner','Cooper','Fletcher','of the Cross','Wainwright','Thatcher','Baker']}};
function npcName(r,people,sex){const N=NPC_NAMES[people]||NPC_NAMES.Wayfolk,L=N[sex];return npcPick(r,L[0])+npcPick(r,L[1])+' '+npcPick(r,N.last);}

/* ---------- temperaments: posture, how they look about, pace, and what they say ---------- */
// pose: bone offsets in radians (spine/neck x: forward, head x: down); look: [how far they glance, how often (s), how fast]
const NPC_TEMPERAMENTS={
  cheerful:{pose:{'spine.x':-0.02,'head.x':-0.04},look:[0.45,2.2,3],tilt:0.08,sway:0.03,pace:1.12,
    lines:['Lovely day for it, isn\'t it?','Mind the puddles, friend!','Have you tried the pies at the market? You must.']},
  gruff:{pose:{'spine.x':0.05,'neck.x':0.06,'head.x':0.03,'upper_armL.z':-0.05,'upper_armR.z':0.05},look:[0.2,4,1.5],tilt:0,sway:0,pace:0.95,
    lines:['What do you want?','Move along.','Hmph. Another one.']},
  nervous:{pose:{'spine.x':0.08,'neck.x':0.08,'head.x':0.02},look:[0.65,0.9,7],tilt:0.05,sway:0.01,pace:1.2,
    lines:['Did you hear that? No? Never mind.','They say the Fog came closer last night.','I\'d rather not talk out here.']},
  proud:{pose:{'spine.x':-0.08,'neck.x':-0.06,'head.x':-0.08},look:[0.3,3.5,1.5],tilt:0,sway:0,pace:0.95,
    lines:['Do you know who I am?','Make way, please.','I don\'t usually speak to strangers.']},
  weary:{pose:{'spine.x':0.15,'neck.x':0.12,'head.x':0.1},look:[0.25,5,1],tilt:0.04,sway:0.015,pace:0.75,
    lines:['Long day. Longer night.','Another shift, another coin.','Don\'t mind me, just tired.']},
  curious:{pose:{'head.x':-0.02},look:[0.75,2.6,2.2],tilt:0.14,sway:0.01,pace:1.05,
    lines:['Where are you from? That\'s not a local accent.','What\'s that you\'re carrying?','Have you seen the sealed walls up close?']},
  stern:{pose:{'spine.x':-0.03,'head.x':-0.02},look:[0.15,5,1],tilt:0,sway:0,pace:1.0,
    lines:['Keep to the road.','State your business.','No trouble today.']},
  dreamy:{pose:{'head.x':-0.1,'neck.x':-0.03},look:[0.4,4,0.8],tilt:0.1,sway:0.02,pace:0.85,
    lines:['Do you ever wonder what\'s behind the sealed walls?','The violet moon was bright last night.','I was thinking of the sea.']}};
const NPC_GREETING={Hrimfolk:'Hail.',Aurelan:'Good day.',Ilvari:'Well met.',Ferrin:'Oi.',Zarhim:'Peace upon your road.',Ruadhan:'Fair winds.',Wayfolk:'Mornin\'.'};

/* ---------- trades: what they wear, how well off they are, what they carry ---------- */
// each slot: [[item id or null, weight], ...]; wealth, wear, dirt: [low, high]; mats: material choices for the chest by wealth
const NPC_TRADES={
  watch:{name:'City watch',wealth:[0.4,0.6],wear:[0.1,0.4],dirt:[0,0.2],temper:['stern','proud','weary','gruff'],dye:'watch',
    gear:{shirt:[['linen_shirt',1]],chest:[['mail',3],['brigandine',2],['cuirass',2]],legs:[['breeches',2],['trousers',1],['platelegs',1]],feet:[['boots',1]],wrists:[['bracers',2],['vambraces',1]],
      hands:[['gauntlets',2],['gloves',1],['plategauntlets',1]],waist:[['belt',2],['warbelt',1]],shoulders:[['plates',2],['spaulders',2],['pads',1]],back:[['cloak',2],[null,1]],head:[['kettlehelm',2],['nasalhelm',2],[null,2]]},
    belt:{hipR:[['pouch',1],[null,1]]},signature:[[null,4],['scarf',1]],lines:['The gates close at dusk.','Keep your blade sheathed inside the walls.']},
  smith:{name:'Smith',wealth:[0.35,0.6],wear:[0.3,0.6],dirt:[0.3,0.6],temper:['gruff','cheerful','stern'],
    gear:{shirt:[['linen_shirt',1],['tunic',1]],chest:[['apron',3],['jerkin',1]],legs:[['breeches',2],['trousers',1]],feet:[['boots',1]],hands:[['gauntlets',1],['gloves',1]],waist:[['toolbelt',2],['belt',1]]},
    belt:{hipR:[['hammer',2],['pouch',1]],hipL:[['pouch',1],[null,1]],backL:[['hammer',1],[null,2]]},signature:[[null,3],['scarf',1]],lines:['Need something mended?','Good steel takes time.']},
  merchant:{name:'Merchant',wealth:[0.55,0.85],wear:[0,0.25],dirt:[0,0.1],temper:['cheerful','proud','curious'],
    gear:{shirt:[['linen_shirt',1]],chest:[['doublet',2],['longcoat',2],['gambeson',1]],legs:[['breeches',1],['trousers',1]],feet:[['boots',2],['shoes',1]],waist:[['belt',2],['sash',1]],hands:[[null,2],['gloves',1]]},
    belt:{hipR:[['pouch',3]],hipL:[['scroll',1],[null,1]]},signature:[['hat',3],['earring',1],['scarf',1]],lines:['Fine goods, fair prices!','For you, a special price.']},
  farmer:{name:'Farmer',wealth:[0.1,0.35],wear:[0.4,0.8],dirt:[0.4,0.8],temper:['cheerful','weary','curious'],
    gear:{shirt:[['tunic',2],['linen_shirt',2]],legs:[['trousers',1]],feet:[['shoes',2],['boots',1]],waist:[['sash',1],['belt',1]]},
    belt:{hipR:[['pouch',1],[null,1]]},signature:[['hat',3],[null,1],['stick',1]],mats:{shirt:['hessian','linen']},lines:['Rain\'s coming, mark my words.','The turnips won\'t sell themselves.']},
  porter:{name:'Porter',wealth:[0.1,0.3],wear:[0.5,0.85],dirt:[0.3,0.6],temper:['weary','gruff','cheerful'],
    gear:{shirt:[['linen_shirt',2],['tunic',1]],legs:[['trousers',1]],feet:[['shoes',1]],waist:[['sash',2],['belt',1]],hands:[['gloves',1],[null,2]]},
    belt:{hipL:[['flask',1],[null,1]]},signature:[[null,3],['scarf',1]],mats:{shirt:['hessian','linen']},lines:['Heavy load today.','Out of the way, coming through!']},
  sailor:{name:'Sailor',wealth:[0.2,0.45],wear:[0.3,0.6],dirt:[0.1,0.3],temper:['cheerful','gruff','dreamy'],
    gear:{shirt:[['tunic',2],['linen_shirt',1]],legs:[['breeches',2],['trousers',1]],feet:[['boots',2],['shoes',1]],waist:[['sash',2],['belt',1]]},
    belt:{hipL:[['flask',2],[null,1]]},signature:[['earring',2],['scarf',2],['hat',1]],lines:['Ship leaves at the turn of the tide.','Ever seen the Sundering? Don\'t.']},
  noble:{name:'Noble',wealth:[0.85,1],wear:[0,0.1],dirt:[0,0.05],temper:['proud','stern','dreamy','curious'],
    gear:{shirt:[['linen_shirt',1]],chest:[['doublet',3],['longcoat',2]],legs:[['breeches',2],['trousers',1]],feet:[['boots',1]],hands:[['gloves',2],[null,1]],waist:[['belt',1]],back:[['cloak',1],[null,2]]},
    belt:{hipL:[['scroll',1],[null,2]]},signature:[['hat',3],['earring',1]],mats:{chest:['velvet','jacquard','quatrefoil']},lines:['The plaza has gone to ruin.','My family has served Maelis for nine generations.']},
  priest:{name:'Priest',wealth:[0.4,0.7],wear:[0.05,0.3],dirt:[0,0.15],temper:['dreamy','stern','cheerful','curious'],
    gear:{shirt:[['linen_shirt',1]],chest:[['robe',1]],legs:[['trousers',1]],feet:[['shoes',1]],waist:[['sash',2],['belt',1]],head:[[null,3],['hood',1]]},
    belt:{},signature:[[null,3],['stick',1]],lines:['May your god find you.','The twelve still watch over us.']},
  scholar:{name:'Scholar',wealth:[0.45,0.7],wear:[0.1,0.35],dirt:[0,0.15],temper:['curious','dreamy','nervous'],
    gear:{shirt:[['linen_shirt',1]],chest:[['robe',2],['longcoat',2],['ilvaricoat',1]],legs:[['trousers',1]],feet:[['shoes',2],['boots',1]],waist:[['belt',1]]},
    belt:{hipL:[['scroll',2]],hipR:[['pouch',1],[null,1]]},signature:[[null,2],['hat',1],['scarf',1]],lines:['Have you found any relics? I\'d pay well.','The Animari ruins hold such secrets.']},
  innkeeper:{name:'Innkeeper',wealth:[0.35,0.6],wear:[0.2,0.5],dirt:[0.1,0.3],temper:['cheerful','gruff','curious'],
    gear:{shirt:[['linen_shirt',2],['tunic',1]],chest:[['apron',2],['jerkin',2]],legs:[['trousers',1]],feet:[['shoes',1]],waist:[['belt',1]]},
    belt:{hipL:[['flask',2]],hipR:[['pouch',1]]},signature:[[null,2],['scarf',1]],lines:['Room\'s two coin a night, meals extra.','You look like you need a drink.']},
  beggar:{name:'Beggar',wealth:[0,0.1],wear:[0.8,1],dirt:[0.6,0.9],temper:['weary','nervous','dreamy'],
    gear:{shirt:[['tunic',2],['linen_shirt',1]],chest:[['robe',1],[null,2]],legs:[['trousers',1]],feet:[[null,2],['shoes',1]],waist:[['sash',1],[null,1]]},
    belt:{},signature:[['stick',2],[null,1]],mats:{shirt:['hessian'],chest:['hessian']},lines:['Spare a coin?','I saw the Fog take a man once.']},
  hunter:{name:'Hunter',wealth:[0.25,0.5],wear:[0.3,0.6],dirt:[0.2,0.5],temper:['stern','curious','gruff'],
    gear:{shirt:[['linen_shirt',1],['tunic',1]],chest:[['brigandine',1],['jerkin',2]],legs:[['breeches',2],['plaid',1],['leathergreaves',2]],feet:[['boots',1]],wrists:[['bracers',1],[null,1]],
      hands:[['gloves',1]],waist:[['belt',1]],head:[['hood',1],[null,2]],back:[['cloak',2],[null,1]],shoulders:[['mantle',1],[null,3]]},
    belt:{hipL:[['flask',1]],hipR:[['pouch',1]]},signature:[[null,3],['scarf',1]],lines:['Wolves have been bold this season.','Stay off the old woods after dark.']}};

/* ---------- each people's own pieces and colours ---------- */
// swap: when the trade's pick is the first item, sometimes wear the people's own instead; palettes: [main, second, trim] sets
const NPC_STYLE={
  Aurelan:{swap:{gambeson:['doublet',0.5],longcoat:['doublet',0.3]},palettes:[['#2e4a6a','#c9a046','#c9a046'],['#6a2a2a','#d8c49a','#c9a046'],['#3e5a3a','#c8b48a','#b0904a']]},
  Hrimfolk:{swap:{jerkin:['furjerkin',0.7],brigandine:['furjerkin',0.3]},add:{shoulders:[['mantle',0.35]]},palettes:[['#4a5a6a','#8a8a86','#b8bcc0'],['#5a4a3a','#3a3026','#8a7458'],['#2a3a4a','#6a7a8a','#c9a046']]},
  Ilvari:{swap:{longcoat:['ilvaricoat',0.8],robe:['ilvaricoat',0.4],doublet:['ilvaricoat',0.5]},palettes:[['#2a3040','#1a2030','#3a6ad0'],['#3a4a5a','#2a3040','#5a8ae0'],['#d8d8e0','#8a8aa0','#3a6ad0']]},
  Ferrin:{swap:{jerkin:['apron',0.4],kettlehelm:['gogglehelm',0.7],nasalhelm:['gogglehelm',0.7]},add:{head:[['gogglehelm',0.25]]},palettes:[['#5a2e24','#3a2618','#c9a046'],['#4a3a2a','#2a201a','#b0904a'],['#3a3a3a','#5a3a26','#c9a046']]},
  Zarhim:{swap:{jerkin:['wraps',0.5],gambeson:['wraps',0.5]},add:{chest:[['wraps',0.65]],head:[['headwrap',0.6]]},palettes:[['#d8c8a8','#a8783a','#7a5426'],['#c87a3a','#e8d8b8','#7a3a1a'],['#e8e0d0','#4a6a8a','#a8783a']]},
  Ruadhan:{swap:{trousers:['plaid',0.6],cloak:['wovencloak',0.7]},palettes:[['#3e5a3a','#8a3a26','#c9a046'],['#8a3a26','#3e5a3a','#c9a046'],['#4a4a6a','#8a6a3a','#b0904a']]},
  Wayfolk:{palettes:[['#6a5a48','#a8844e','#4a3e30'],['#5a6a4a','#8a7a5a','#3a3026'],['#7a4a3a','#c8b48a','#4a3020'],['#4a5a6a','#a89c86','#3a3a3a']]}};
const NPC_WATCH_DYE=['#7a2626','#4e1818','#c9a046'];   // the city watch wears Aldrath's red and gold

/* ---------- a person ---------- */
function npcGenerate(seed,o){
  o=o||{}; const r=npcRng(seed), peoples=Object.keys(PEOPLE);
  const people=o.people||npcWeighted(r,peoples.map(p=>[p,p==='Wayfolk'?3:1]));
  const trade=o.trade||npcPick(r,Object.keys(NPC_TRADES)), T=NPC_TRADES[trade], S=NPC_STYLE[people]||NPC_STYLE.Wayfolk, P=PEOPLE[people];
  const sex=o.sex||(trade==='watch'&&r()<0.7?'m':r()<0.5?'m':'f'), fem=sex==='f', R_=fem?P.f:P.m;
  const lerp=(a,t)=>a[0]+(a[1]-a[0])*t, wealth=lerp(T.wealth,r()), temper=o.temper||npcPick(r,T.temper);
  const hairs=fem?['Long','Ponytail','Topknot','Swept']:['Short','Swept','Ponytail','Long','Topknot',null];
  const person={seed,people,sex,trade,temper,name:npcName(r,people,sex),wealth,
    h:r(),w:r(),skin:Math.floor(r()*P.skin.length),hcol:Math.floor(r()*P.hair.length),eye:Math.floor(r()*P.eyes.length),
    hair:npcPick(r,hairs),moustache:!fem&&r()<0.35?npcPick(r,['Chevron','Horseshoe','Walrus','Handlebar','Pencil']):null,
    energy:0.75+r()*0.5,tidiness:1-lerp(T.wear,r()),outfit:{}};
  // the outfit: the trade's choices, swapped for the people's own pieces now and then
  const gear={};
  for(const [slot,opts] of Object.entries(T.gear)){let id=npcWeighted(r,opts);const sw=id&&S.swap&&S.swap[id];if(sw&&eqItem(slot,sw[0])&&r()<sw[1])id=sw[0];gear[slot]=id;}
  if(S.add)for(const [slot,opts] of Object.entries(S.add))for(const [id,p] of opts)if(!gear[slot]&&r()<p&&trade!=='watch')gear[slot]=id;
  const belt={};for(const [sk,opts] of Object.entries(T.belt||{}))belt[sk]=npcWeighted(r,opts);
  const mats={};for(const [slot,ms] of Object.entries(T.mats||{}))mats[slot]=npcPick(r,ms);
  const pal=trade==='watch'?NPC_WATCH_DYE:npcPick(r,S.palettes), dim=c=>'#'+new THREE.Color(c).multiplyScalar(0.55+0.45*Math.min(1,wealth*1.6)).getHexString();
  const sig=npcWeighted(r,T.signature||[[null,1]]);
  const signature=sig==='hat'?{type:'hat',colour:npcPick(r,['#4a3424','#2a2a2a','#6a5a3a','#3a2a2a','#7a6a4a']),feather:wealth>0.6&&r()<0.6?npcPick(r,['#c94a3a','#e8e0d0','#3a6ad0']):null}
    :sig==='scarf'?{type:'scarf',colour:npcPick(r,['#a83a2a','#3a5a8a','#c9a046','#4a7a4a','#8a5a8a'])}:sig?{type:sig,colour:'#5a3e26'}:null;
  person.outfit=Object.assign({dye:pal.map(dim),belt,mats,signature,wear:{wear:1-person.tidiness,dirt:lerp(T.dirt,r()),seed:r()*10}},gear);
  person.line=npcPick(r,(T.lines||[]).concat(NPC_TEMPERAMENTS[temper].lines));
  person.greeting=NPC_GREETING[people]||'Hello.';
  return person;
}
function npcDescribe(p){const T=NPC_TRADES[p.trade];return {name:p.name,what:(p.sex==='f'?'Woman':'Man')+' · '+p.people+' · '+T.name,
  temper:p.temper[0].toUpperCase()+p.temper.slice(1),wealth:p.wealth<0.2?'poor':p.wealth<0.45?'modest':p.wealth<0.75?'comfortable':'wealthy',
  line:p.greeting+' '+p.line};}

/* ---------- on the bodies ---------- */
const NPC_TIERS={hero:{size:1024,maxBuilt:null},townsfolk:{size:512,maxBuilt:6},crowd:{size:256,maxBuilt:2,cloth:false}};
// bodies: {m, f, ml, fl} loaded glTFs (preparePainted already run); returns the figure, with userData.mixer
function npcSpawn(bodies,p,renderer,tier){
  const g=bodies[p.sex], P=PEOPLE[p.people], R_=p.sex==='f'?P.f:P.m, fig=THREE.SkeletonUtils.clone(g.scene);
  rigPeople(fig,g); const lg=bodies[p.sex+'l'];
  if(lg)lg.scene.traverse(o=>{if(o.isSkinnedMesh&&o.morphTargetDictionary)fig.userData.rig.lightSrc=o;});
  setPeople(fig,P.shape);
  const h=R_.h[0]+(R_.h[1]-R_.h[0])*p.h, w=R_.w[0]+(R_.w[1]-R_.w[0])*p.w; fig.scale.setScalar(h); setBuild(fig,Math.max(0,-w),Math.max(0,w));
  const look=paintLook({people:p.people,sex:p.sex,skin:p.skin,hcol:p.hcol,eye:p.eye,hair:p.hair,moustache:p.moustache,definition:Math.max(0,Math.min(1,1+w))*(p.sex==='f'?0.4:1)});
  dressFigure(fig,look); dressOutfit(fig,look,p.outfit,renderer,false,NPC_TIERS[tier||'townsfolk']);
  fig.userData.npc=p; fig.userData.npcState={yaw:0,tYaw:0,tilt:0,tTilt:0,timer:0,t:0};
  const mixer=new THREE.AnimationMixer(fig); fig.userData.mixer=mixer; fig.userData.clip=null;
  npcPlay(fig,'Idle'); return fig;
}
function npcPlay(fig,clip){if(fig.userData.clip===clip)return;fig.userData.clip=clip;const a=playPeople(fig,fig.userData.mixer,clip);
  if(a){const p=fig.userData.npc,T=NPC_TEMPERAMENTS[p.temper];a.timeScale=clip==='Walk'?T.pace*p.energy:0.8+0.4*p.energy;}}
// personality, each frame after the mixer: posture, glances, a tilt of the head, a sway
function npcAnimate(fig,dt){
  const p=fig.userData.npc,T=NPC_TEMPERAMENTS[p.temper],S=fig.userData.npcState; S.t+=dt; S.timer-=dt;
  const r=Math.random;
  if(S.timer<=0){const [far,every]=T.look;S.tYaw=(r()*2-1)*far;S.tTilt=(r()*2-1)*T.tilt;S.timer=every*(0.5+r());}
  const k=Math.min(1,dt*T.look[2]); S.yaw+=(S.tYaw-S.yaw)*k; S.tilt+=(S.tTilt-S.tilt)*k*0.6;
  const pose=Object.assign({},T.pose); pose['head.y']=(pose['head.y']||0)+S.yaw*0.65; pose['neck.y']=(pose['neck.y']||0)+S.yaw*0.35;
  pose['head.z']=(pose['head.z']||0)+S.tilt; if(T.sway)pose['spine.z']=(pose['spine.z']||0)+Math.sin(S.t*1.3*p.energy)*T.sway;
  fig.userData.pose=pose; fig.userData.mixer.update(dt); buildPosture(fig); eqClothUpdate(fig,dt);
}
