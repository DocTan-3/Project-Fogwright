// Fogwright's peoples: each one's body shape, the ranges its height and build may take, and its colours. Shared by the
// character creator, the NPC system and the game. Load after bodypaint.js.
'use strict';
// The peoples: shape, and the range each slider may move within (height is a scale, build runs -1 slight .. 0 muscular .. 1 heavy)
const PEOPLE={
 Aurelan:{shape:'Aurelan',desc:'Ingenious islanders; balanced and handsome.',m:{h:[0.97,1.03],w:[-0.45,0.3]},f:{h:[0.95,0.99],w:[-0.45,0.15]},
   skin:['#efceb4','#e8c2a2','#d9ab88','#c9966e'],hair:['#4a3426','#2e2420','#6a4a30','#8a5a3a','#c7a66b'],eyes:['#4a6a8a','#5a7a4a','#5a3a26','#6e7a86']},
 Hrimfolk:{shape:'Human',desc:'The sturdiest of all: tall, broad northerners.',m:{h:[1.05,1.12],w:[-0.4,0.95]},f:{h:[1.0,1.05],w:[-0.6,0.15]},
   skin:['#f3d9c4','#f0cfb4','#e5bd9e','#dcae8c'],hair:['#e0c690','#c7a66b','#e6dcc0','#a8916c','#9a5a34'],eyes:['#5a8aa8','#7a9aae','#4a6a5a','#6e7a86']},
 Ilvari:{shape:'Ilvari',desc:'Tall and slender, marked in blue ink.',ink:1,m:{h:[0.98,1.02],w:[-1,-0.6]},f:{h:[0.98,1.02],w:[-1,-0.7]},
   skin:['#ecdacb','#e2cbb8','#f2e2d6','#d8c4b4'],hair:['#1c1c26','#d8d8e0','#2a2a3a','#b8b8c8'],eyes:['#7a8aa0','#5a7ab0','#8a9a9a','#6a5a7a']},
 Ferrin:{shape:'Ferrin',desc:'Short, broad and tattooed; centuries of mining.',tattoo:1,m:{h:[0.96,1.0],w:[-0.3,1]},f:{h:[1.06,1.12],w:[-0.3,0.5]},
   skin:['#dca88c','#d9946e','#c48466','#b87a5e'],hair:['#6e2c1e','#2a201c','#5a3a28','#8a4a2a','#6e6a66'],eyes:['#3a4a5a','#4a3a2a','#5a6a4a','#6e7a86']},
 Zarhim:{shape:'Zarhim',desc:'Lean, wiry desert nomads.',m:{h:[0.97,1.03],w:[-1,-0.2]},f:{h:[0.95,1.0],w:[-1,-0.45]},
   skin:['#9c6a48','#8a5a3c','#7a4e34','#6e4630','#5a3a28'],hair:['#14100e','#1e1814','#2a2018'],eyes:['#3a2a1a','#5a3a1a','#2a2018','#6a5a3a']},
 Ruadhan:{shape:'Human',desc:'Tall, red-haired people of the hills and forests.',freckles:1,m:{h:[1.03,1.09],w:[-0.85,0.3]},f:{h:[1.0,1.04],w:[-0.85,-0.2]},
   skin:['#f6dac6','#f4d2b6','#f2cdb0','#eabd9c'],hair:['#c85a24','#b8441c','#e07a3a','#9a3a1a'],eyes:['#5a7a4a','#4a6a8a','#6a8a5a','#7a6a4a']},
 Wayfolk:{shape:'Human',desc:'The mixed peoples, found everywhere.',m:{h:[0.94,1.04],w:[-0.85,0.6]},f:{h:[0.93,1.0],w:[-0.85,0.1]},
   skin:['#efceb4','#d9ab88','#c9966e','#a8724e','#8a5a3c'],hair:['#4a3426','#2e2420','#8a5a3a','#c7a66b','#1e1a18','#9a3a1a'],eyes:['#4a3a2a','#4a6a8a','#5a7a4a','#6e7a86']}};
const HAIRS=[['None',null],['Short','Short'],['Swept','Swept'],['Ponytail','Ponytail'],['Long','Long'],['Topknot','Topknot']];
const BEARDS=[['None',null],['Short','Short'],['Full','Full'],['Pointed','Pointed'],['Forked','Forked'],['Braided','Braided']];
const STACHES=[['None',null],['Chevron','Chevron'],['Horseshoe','Horseshoe'],['Walrus','Walrus'],['Handlebar','Handlebar'],['Pencil','Pencil']];


// a paint look (see paintedMaterial in bodypaint.js) for one person: o = {people, sex, skin, hcol, eye (indices into the
// people's palettes), hair, beard, moustache, lower (0 trousers, 1 boxers), definition (0 soft .. 1 defined)}
function paintLook(o){
  const P=PEOPLE[o.people]||PEOPLE.Wayfolk, fem=o.sex==='f';
  return {name:o.people,people:o.people,fem:fem?1:0,hair:o.hair,beard:fem?null:o.beard,moustache:fem?null:o.moustache,
    base:[1,o.lower||0,fem?0:(o.people==='Hrimfolk'||o.people==='Ruadhan'?0.6:0.2),o.definition==null?0.6:o.definition],
    uSkin:P.skin[(o.skin||0)%P.skin.length],uHair:P.hair[(o.hcol||0)%P.hair.length],uEye:P.eyes[(o.eye||0)%P.eyes.length],
    uPants:['#cbbd9f','#a89c86','#b9bbc0','#8e8676','#d8c9a8','#b8ab8c','#9c9488'][Math.max(0,Object.keys(PEOPLE).indexOf(o.people))],uBoots:'#4a3a2c',
    uLip:fem?'#b8605a':'#a8665a',uInk:o.people==='Ferrin'?'#4a3430':'#2f5fd0',uShirt:'#ddd4c2',uVest:'#6c2e2a',uBelt:'#5a3a26',uTrim:'#c9a046',
    f1:[0,fem?0:1,P.ink?1:0,P.freckles?1:0],f2:[o.hair?1:0,0,0,P.tattoo&&!fem?1:0]};
}
