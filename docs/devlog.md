# Fogwright Devlog

Nov 22, 2026 · @Dev Tan

The story of making Fogwright, written as we go: what we built, what we decided, and the patch notes for each step. Newest entries first.

## Devlog 51 · The townsfolk

*Characters · 24 November 2026*

Your notes: NPCs first, armour and clothes low-poly but good-looking (maybe with a texture sheet), and the arms hung too wide, like a halfway T-pose.

**The townsfolk.** Every NPC is generated from a seed:
- **Who they are:** a people, a body, colouring and a name in their people's own sound.
- **Trade:** one of twelve, from the city watch to beggars, setting what they wear and carry and how worn and dirty it is.
- **Style:** their people's own pieces and colours.
- **Signature item:** a hat, a scarf, an earring or a walking stick.
- **Temperament:** sets their posture, how they look about, their pace and what they say.

They come in three detail tiers, so the crowd in the background is cheap. A new page shows a crowd of them; tap anyone to read their card.

**Lighter and better-looking gear.** Built pieces are now cut from the 1,500-triangle distance body, with fewer segments and flat rivets. A full suit of armour dropped from 10,000 triangles to 3,000, and a townsperson's outfit is 500 to 1,600. The detail comes from a texture sheet of sixteen CC0 surfaces from Poly Haven, from linen and leather to velvet, fur and brushed steel, plus drawn mail, as greyscale detail the dyes colour.

**Arms.** They now hang by the thighs. Along the way, posture offsets on one bone were piling up frame after frame whenever more than one axis moved, which bent a few NPCs double. Fixed.

## Devlog 50 · Fur, robes and each people's style

*Characters · 24 November 2026*

**Surfaces.** Built pieces had only a colour at each corner, so fur looked like smooth plastic and steel like grey card. They now get their own surface shader: fur strands, leather grain and creases, brushed metal with a proper highlight, cloth weave. Fur is clumped and tufted at the hem, dark at the roots. Mail rings are larger and softened, so they no longer shimmer.

**Robes and coats.** A chest piece can now add a skirt: rings from the hips to the hem, measured round each people's legs so it clears them, flaring towards the hem and following the thighs lower down, so it moves when walking. Coats leave the front open. A wool robe and a long coat to start.

**Each people's style.** A first piece for each: an Aurelan striped doublet with buttons, a Hrimfolk jerkin with a fur collar, a Ferrin smith's apron, Zarhim desert wraps with a sash and a head wrap, an Ilvari fitted long coat with blue trim, and a Ruadhan woven check cloak. Hoods and wraps hide the hair.

## Devlog 49 · Necks, pauldrons and belts

*Characters · 23 November 2026*

Your notes: the whole neck showed, pauldrons needed attention, and belts need room for the relics coming later.

**Necklines.** Clothes stopped at the paint template's collarbone height, which on the MakeHuman bodies sits well below the neck, so every outfit looked strapless. They now come up to the base of the neck, and collars are rings round it.

**Pauldrons.** Domed lames on the outer shoulder, each tucked under the one above, with rivets along the rims, an optional raised guard by the neck and an optional roll of fur. Five so far: leather pads, layered spaulders, steel, brass and fur-trimmed pauldrons.

**Belts.** Each belt carries sockets at the hips and back where attachments hang: a pouch, a flask and a scroll case for now, and relics later through the same sockets. An empty socket shows its brass ring. Three belts: a plain belt with two sockets, a studded tool belt with four, and a sash with one.

## Devlog 48 · Gear that fits everyone

*Characters · 23 November 2026*

You asked for equipment like World of Warcraft's: every piece shows on the character, some armour painted on and some built around the body, with the special slots unlocking as you progress. It's built on your MakeHuman bodies, on the `characters` branch, and the design doc's new Equipment section describes the whole system.

**Slots.** Shirt, chest, legs, feet, wrists, hands, waist, shoulders, head, back and weapons are open from the start. The tabard unlocks when a god claims you, the face slot with Tinkerer crafts, the mechanical arm in the gear and water era, and the back device in the steam era.

**Painted armour.** Each slot is a paint layer, laid on in a fixed order (shirt, legs, feet, chest, wrists, hands, waist, tabard), so gloves sit over sleeves and boots over trousers. Layers come in linen, wool, leather, studded leather, mail, plate, quilted cloth and fur, with trims, stitching and a soft shadow at each layer's edge. Like WoW, everything is baked into one texture per character, so a crowd costs about the same as one person. For that the bodies needed a texture layout: seams cut at the neck, wrists, hips and ankles, down the back and along the inner limbs, with the face given extra room.

**Built armour.** Pieces are cut out of the body's own surface and pushed outward, so they carry its skin weights and every people and build shape: one piece fits an Ilvari woman and a Ferrin man without being modelled twice. So far: boot and gauntlet cuffs, bracers, belts with buckles and pouches, lacing, collars, layered pauldrons, a fur mantle, a hood and a cloak. MakeHuman models individual toes, so shoes and boots get a toe box built round the forefoot.

**Dyes.** A dye set colours the main garments (chest, cloak, hood), gives trousers a darker second shade, tints leather lightly, and leaves metal and fur alone.

## Devlog 47 · Open armpits, fresh paint

*Character study · 23 November 2026*

Your notes: the men's armpits looked joined to their sides, and the paint was still made for the old skeleton.

**Armpits.** Our arms hung closer to the body than on your sheet, and when the body is welded into one surface that narrow gap filled in. The arms now hang at the sheet's A-pose, 7° out. The weld runs with them at 12°, so it can't bridge the gap, then swings them back.

The first try swung each arm as a rigid piece, and the bodies vanished in the creator. The borrowed model's arm shells are open at the top and only the torso closes them. Swinging them tore that seam, the weld fell apart into hundreds of pieces, and the body ended up with no skin weights at all. The swing now fades to nothing at the shoulder seam, so the arm bends out instead of tearing away. The build now stops if any point is left without weights.

**Repaint.** Three changes:

- **Arm and torso:** the paint used to split them with fixed distances from the old rig. It now follows the new rig's skin weights, so the two meet where the body actually bends.
- **Arms:** painted as if swung back in, so the elbows, wrists and shoulder caps stay where they were drawn.
- **Torso:** paint heights are remapped by landmarks on the fitted body. Her chest wrap now sits on the bust instead of above it, and goes evenly round the back.

The pale, wavy band over his collarbones came from hard cut-offs in the collarbone highlight and in the switch to face paint. Both now blend, so the line is gone.

## Devlog 46 · Fitting to the sheets

*Character study · 22 to 23 November 2026*

You sent turnaround sheets for the Aurelan, Hrimfolk and Ilvari, and asked us to match the shapes one people at a time, starting with the Aurelan.

New tools in `tools/fit` cut the sheet into silhouettes and measure the width and front and back outlines at every height. The body build then reshapes the Aurelan man and woman band by band to match. Heights are aligned at the crotch and the neck. The fit covers the torso, each leg, the side outline, the shoulder width (the arms and their bones move with it) and the thickness along each arm. The fitted widths land within millimetres of the sheet.

To give the curves room, every body now has about 16,000 triangles instead of 9,000.

## Devlog 45 · The women

*Character study · 21 to 22 November 2026*

The women are built from the same base body as the men, with their own shape on top. Most of the work went into the chest and neck, from your notes and WoW's blood elves:

- **Bust:** first it read as two ridges, because it was pushed out of the male chest and kept his pectoral lines. It's now a flattened chest with two round domes added after all the smoothing, with extra triangles there so they stay round.
- **Neck and shoulders:** a slimmer neck, small traps, and a lower, narrower shoulder line. The bumps around the collarbones are smoothed away.
- **Waist:** a slimmer midriff tapering into the hips.
- **Chest wrap:** a linen wrap that goes all the way round, as part of the base layer.

## Devlog 44 · One body, a shape per people

*Character study · 21 November 2026*

Instead of a separate model for each people, there is now one base body per sex. Each people's proportions are a built-in shape on it, and the skeleton moves to that people's joints when you pick one. Height and build sliders sit on top, each limited to a range that keeps the people recognisable.

This is the character creator: sex, people, height, build, skin, eyes, hair and hair colour, moustache and base layer, with a full, face, walk and turntable view. Beards are out for now, until they look right. Along the way, the build slider stopped widening the waist when set to slim: the sides of the waist were following the forearms.

## Devlog 43 · Necks, waists and feet

*Character study · 22 November 2026*

Your notes: the neck muscles were too big and too long, everyone had love handles, and the feet should be 5% wider.

Those came from the source model itself. Its traps rise in a steep hump, and its hips flare out above where its belt used to be. They're now corrected on the base body before each people gets its own proportions: the traps follow one smooth slope from the neck to the shoulder, the neck column is thinner, the hips taper into the waist, and the feet are 5% wider. The Ilvari and Zarhim necks are shorter too. A first attempt left spikes at the shoulder tips; the change now fades out toward the shoulder and the line is smoothed.

## Devlog 42 · No more pills

*Character study · 22 November 2026*

You said the Ilvari and Zarhim looked like pills. Fair: the old Lean blend shrank shoulders, chest and waist all at once, so the bodies became even tubes. Slender means tapered, not shrunk.

So the Ferrin pass is now a per-people table: leg and neck length, head size, shoulder width, torso width and depth at each height, and limb thickness. The Ilvari stand about 1.9 m, with longer legs and neck, square shoulders over a narrow waist and hips, and slim arms and legs. The Zarhim are lean and wiry, with a slight taper. Each people's body is built once in Blender with its own refitted rig, so idle, walk, hair, beards and paint all still work.

## Devlog 41 · The first dwarf

*Character study · 22 November 2026*

You showed the Ferrin you had in mind: a stylised dwarf-smith, bald and red-bearded, with a barrel chest, huge forearms and bold geometric tattoos, but shorter. So the Ferrin are the first people with their own silhouette, not just a recoloured human.

The rig script now takes a people. For the Ferrin it reshapes the welded body: legs cut to 70%, a barrel chest and belly, thick forearms and big hands, a shorter neck, and the head kept full size so it reads large. The skeleton is refitted to the new joints, so idle and walk still work. Hair and beards are grown on the moved head, and the paint maps back onto the original layout, so the waistband and face land where they should. He stands about 1.45 m, with painted chevrons, bands and a triangle on his arms.

Also settled: the Ilvari get no elf ears. They are elf-like in build and bearing only.

## Devlog 40 · One skin, one shape each

*Character study · 22 November 2026*

The sliders kept opening seams at the shoulders, so we agreed to keep one look per people for now. The seams themselves are now fixed at the root: the source model's separate arm, head and eye shells were rebuilt as one closed surface, smoothed and brought back down to about 9,000 triangles. The faces got larger eyes with lash lines, heavier brows and deeper eye shadow. Hairlines moved up and back, and the hair caps thin toward their edges instead of sitting like helmets. Beards hug the jaw, start below the cheekbones and stop at the ears. Moustaches are smaller, and the Ilvari are clean-shaven.

You then shared what inspired the peoples in the first place: the D&D lineup and WoW's races. The lesson is that peoples are told apart by silhouette first (tiny halflings, stocky dwarves, tall slender elves, towering half-orcs), and only then by colour and dress. That's the next step.

## Devlog 39 · Each people their own shape

*Character study · 22 November 2026*

You asked why everyone was so muscular. The borrowed body is a heroic build, and every people was inheriting it. Peoples should keep their stereotypes: elf-like Ilvari slender, Ferrin short and broad. And the boots had to go.

- **One weight axis:** skinny → ordinary → muscular → heavy. Muscular is now something you choose, not the default.
- **Per-people limits:** each people's height and weight sliders are clamped to its own range, with a breadth factor on top. Ilvari: tall and slender. Zarhim: lean. Aurelan: ordinary. Ruadhan: tall, lean to fit. Hrimfolk: big, up to heavy. Ferrin: short and stocky.
- **Better shapes:** Lean now slims evenly, and both shapes are smoothed over the surface so the shoulders no longer crease where parts meet. Heavy puts bulk in the body, not giant arms. Painted muscle definition fades as people get leaner.
- **Bare feet:** the boots are reshaped into feet with painted toes, heels and ankle bones, and the trousers now run to the ankle.

Your notes on the first try: Hrimfolk great, Aurelan too wide, Ilvari plain wrong, Ferrin's shoulders and arms too big. All four were addressed.

## Devlog 38 · The base layer

*Character study · 22 November 2026*

Your call: everyone should start in trousers or boxers, so players can fully customise their style on top. That's the WoW and Valheim way, and the shirts and waistcoats now become something you put on later.

The base layer is bare skin painted with soft form instead of drawn lines. You were right that the old abs looked goofy. Now there's light across the chest with a soft shadow under it, the collarbones and the hollow beneath them, only a hint of the stomach, obliques, the spine and shoulder blades, ruddy elbows and knees, warmer hands, and optional chest hair. Below the waist: undyed linen trousers or boxers with a gathered drawstring waistband, and simple leather foot wraps. The study has a toggle between trousers, boxers and a mix.

You also sent a Meshy model to see if it could be another body type. It's a 418-triangle mannequin with no face, skeleton or hands, so we're passing on it: new body types are cheaper and better as blend shapes on the base we have.

## Devlog 37 · A borrowed body, our paint

*Character study · 22 November 2026*

You found Simple RPG Human Male on Sketchfab: a clean, hand-painted, WoW-style man of about 1,700 triangles, with a sword and shield. It's now our first base body.

- **Rigged to our skeleton.** His legs, hips and head already lined up with our rig. His arms are longer with bigger hands, so the arm bones moved to fit him instead of stretching him.
- **Sword and shield gone. His texture too.** Every person is repainted by code: we map his face onto our paint layout (his eyes, mouth and chin onto ours), so the same shader paints shirts, waistcoats, trousers, boots, eyes, brows, lips, freckles and Ilvari ink on him. His own teeth and mouth pieces were removed; the painted mouth replaces them.
- **Our hair and beards on his head.** The hair and beard system now finds the head surface by raycasting, so every style fits him: five hairstyles, five beards and five moustaches.
- **Builds and motion carry over:** Lean and Heavy blend shapes, the Valheim-style idle, and a walk with the arms swinging.

One open item: the model's license. It's credited in the repository's CREDITS.md. Before shipping, we record the author and confirm the license allows use in the game.

## Devlog 36 · Lean, heroic, heavy

*Character study · 22 November 2026*

You showed WoW's humans: the same race in very different sizes, from a lean, hunched man to a heroic build to a huge, heavy one with a belly. So the one body now has two blend shapes, Lean and Heavy, mixed per person on top of the heroic base. The head never changes. Heavy adds a belly, love handles, bigger traps and thicker limbs; Lean thins everything and flattens the traps. A small posture layer goes with them: lean builds hunch forward a little, and heavy arms ride out around the bulk.

Each people can lean one way: Hrimfolk and Ferrin heavier, Ilvari and Zarhim leaner. It costs almost nothing, because every person is still the same mesh and the same draw call. The study has a build slider to push everyone at once.

## Devlog 35 · Standing like a Viking

*Character study · 22 November 2026*

You sent Valheim's character creator and some gameplay shots: their bodies, postures and hands look nothing like ours. Ours was a thin stick figure holding its arms out as if carrying a rifle (the Tinker's idle). Theirs stand like heroes.

- **Build:** a thick neck sloping into big trapezius, deltoid caps, biceps and forearms that swell below the elbow, a deep chest with pecs, shoulder blades and lats, glutes, and heavier thighs and calves. The hands are closed fists, like theirs.
- **Painted muscle:** bare torsos get pecs, abs, the line down the middle, collarbones and the spine painted in, the way Valheim bakes its shading.
- **Posture:** a new Idle and Walk for the townsfolk. The chest is up and the shoulders back, arms hang down and out with soft elbows and fists by the thighs, feet sit apart with soft knees, and a slow breath runs through it. In the walk, the arms swing opposite the legs.
- **Moustaches:** chevron, horseshoe, walrus, handlebar and pencil, combinable with any beard.

## Devlog 34 · Merged, not simulated

*Character study · 22 November 2026*

Your note on Valheim's beards: they're merged, and not every strand has to be modelled. Right again. Each beard there is one solid, sculpted mass with a strong silhouette; the strands are just paint.

So beards are now single closed volumes that hug the jaw and cheeks and hang below the chin in a set shape: short, full spade, pointed, forked, and a spade with a braid. There's also a thick chevron moustache. Hair is a solid cap with real volume and a few chunky points at the hairline, with solid tails for the ponytail and topknot. Strands are painted as broad clumps with darker grooves between them, darkening toward the tips. The model file halved to about 1 MB.

## Devlog 33 · Jaws, brows and locks

*Character study · 22 November 2026*

You sent Valheim's faces and hair, and called ours what they were: onions, with no chin and no jaw.

- **A head built like a head.** It used to be an egg with bumps pushed onto it. Now it's modelled the way low-poly heads are: sixteen cross-sections from the neck to the crown, each a squared-off outline. The jump from the neck to the jaw gives a real jawline and an under-jaw plane. Above that come squared jaw corners, a square chin, cheekbones over hollow cheeks, a heavy brow, a straight strong nose and a flat-topped skull.
- **Eyes in shadow.** Smaller eyes, set deep under the brow, with shadow painted under the brow, beside and under the nose and in the cheek hollows, like Valheim's baked-in shading. Thicker, furrowed brows.
- **Hair and beards from locks.** Every style is now built from tapered, faceted clumps of hair laid over the head, with a thin dark cap underneath so no skin shows between them. Swept back, ponytail with a tie, long and loose with locks framing the face, topknot, short crop. Beards: short, full, braided and forked, each with a moustache that runs into the beard.

Pushed to project-fogwright main.

## Devlog 32 · One skin, real hair

*Character study · 22 November 2026*

You looked at the eight peoples and called it: not clean. Lumpy faces, tomato noses, seams everywhere. And you put your finger on why WoW works: a handful of clean base meshes, with the detail painted on.

So the characters are being rebuilt that way:

- **One seamless body.** Torso, limbs, hands and feet are grown from a stick figure into one continuous mesh. The head is built ring by ring on a single smooth surface (skull, brow, eye sockets, cheekbones, nose, lips and a strong chin and jaw) and stitched to the neck. There are no gaps anywhere, and it's about 3,600 triangles: half the old townsfolk.
- **Painted by code.** Eyes with irises and lids, brows, lips, nostrils, freckles and Ilvari ink are all painted on, along with shirts, waistcoats with buttons, belts and buckles, striped linen, trousers with seams, gloves and boots. Nothing is stored as an image.
- **Real hair and beards.** As you said, hair and beards shouldn't be painted skin. There are now separate volumes: short, swept and long hair, full and short beards, and a moustache. Each is built column by column from the hairline, with ragged lock tips at the edge. They take the skin weights of the face beneath them, so they move with the jaw.

**Also:** the project now has its own repository, project-fogwright, with the game, the studies, the Blender scripts and a smoke test on main.

**Next:** a female base body on the same method, then the shared garment meshes (coats, robes, skirts, helms) painted per people and armor tier, then swapping the new bodies into the city.

## Devlog 31 · Eight peoples

*Prototype v0.14.0 · 22 November 2026*

Until now every townsperson was a recoloured Tinker. You said it was time to make the race appearances so the capital could actually be populated, so here is the first pass at all eight playable peoples, drawn from the lore:

- **Hrimfolk:** tallest and broadest; fair skin, blond, ash and white hair; braids, beards, fur ruffs over the shoulders.
- **Aurelans:** the feudal islanders; waistcoats and coats in house colours, some in their lord's tabard.
- **Ilvari:** slender, in long blue coats, with blue ink: a line down the brow, bars across the cheekbones, lines on the chin.
- **Ferrin:** short and broad from centuries of mining; full beards, leather aprons, gloves, sooty colours.
- **Zarhim:** lean, darker skinned, in linen and indigo, heads wrapped against the sun.
- **Ruadhan:** tall, red and copper-haired, cloaked in greens and browns with a brooch.
- **Wayfolk:** the mixed peoples: any skin, any hair, plain travelling clothes.
- **The Penitent:** hooded, in sackcloth robes and rope belts.

Plus **the city watch:** helm, violet tabard and gloves, drawn from any people.

**How it works.** It's one rig and one model with a set of interchangeable parts: beards grown out of the jaw itself, braids, head wraps, hoods, fur ruffs, aprons, cloaks, tabards, helms and ink. Each person rolls their own build (height and breadth), palette and parts, and is still a single draw call. The whole people model is 420 KB. Who you meet depends on where you are: the Hrimfolk Quarter is mostly Hrimfolk, the Temple Ward has Penitent, the outskirts are full of Zarhim caravaners and Ruadhan tamers.

**Patch notes · v0.14.0**

- Added: the eight peoples and the city watch, with per-person builds, colours and parts.
- Added: a peoples lineup viewer for review.
- Changed: townsfolk, villagers, the gate queue, outskirts crowds and guards all use the new peoples, chosen by location.
- Changed: only nearby townsfolk cast shadows, to keep crowds cheap.
- Fixed: the game could freeze near the gate's quarters. The outskirts crowd kept looking for a camp close enough to spawn at and never gave up.
- Known: everyone is built on the male Tinker body for now.

## Devlog 30 · Outside the walls

*Prototype v0.13.0 · 22 November 2026*

Your direction: there shouldn't be monsters this close to the capital. Guards patrol, and the land outside the walls should be busy with everything the guards won't allow inside: camps, stalls, the trades nobody wants next door. The gate becomes a checkpoint.

**The gate checkpoint.** A stone guard booth with a ledger table, two striped booms raised over the road, guards on watch, and a queue of townsfolk shuffling forward. Every few seconds the one at the front is let through and someone new joins the back.

**The outskirts.** A great arc of trampled ground in front of the gate:

- **Market lane:** stalls and wagons line the road for nearly 200 m.
- **Camps:** forty of them, each around a campfire. Some are caravans with a striped pavilion and wagons, some are nomad yurts, some are tents and crates.
- **The trades kept outside:** out on the far fringe stand open-air smithies, tanneries with hides on racks and vats, and livestock pens.
- **People:** about thirty wander between stalls, fires and workshops, stopping to browse, then moving on.

All of it is generated in code, like the city: eleven more recipes.

**The watch.** Guards now patrol two arcs through the camps, the outside of the wall, and both sides of the road down toward the village. They keep walking even when you're far away, and they only take a body when you come near.

**Peace near the capital.** No monsters spawn within about a kilometre of Aldrath. The camps' fires count as safe light: the Fog stays thin around them at night.

**Patch notes · v0.13.0**

- Added: the outskirts, with 40 camps, a market lane, smithies, tanneries, livestock pens, wagons and crates, on trampled ground.
- Added: a gate checkpoint with a guard booth, raised booms, gate guards and a moving queue.
- Added: five guard patrols (two camp arcs, the outer wall, and both sides of the south road).
- Added: campfires that light the night and count as safe light.
- Changed: no monsters within about 1 km of the capital.
- Added: new place names "The gate checkpoint" and "The outskirts", plus an Admin teleport to the outskirts.

## Devlog 29 · Every people under one wall

*Prototype v0.12.0 · 22 November 2026*

You wanted Aldrath's city to feel like the place every people ended up: a mish-mash of cultures, slums, and richer districts. So the city is no longer one style of rowhouse. It's now a city of eighteen building types, and all of them are generated by code in the browser. The Blender kit file (350 KB) is gone. The houses are recipes now, so they cost nothing to download.

**Who lives where.** Each quarter mostly builds in its own people's way, but neighbours mix:

- **Hrimfolk:** steep A-frame halls on stone footings, with slate or turf roofs and crossed gable horns.
- **Zarhim:** sun-baked flat roofs with parapets, striped awnings, beam ends, water jars and teal domes.
- **Ilvari:** white round towers banded in blue, with tall pointed caps.
- **Ferrin:** squat stone forge-houses with iron roofs, a furnace glow, a copper boiler and a tall brick stack.
- **Ruadhan:** wattle roundhouses under deep thatch.
- **Wayfolk:** timber-framed houses with a copper boiler on the side.
- **Temple Ward:** white stone with gilded domes.
- **Market Ward:** shopfronts with big glass and striped awnings.
- **Aldrath's own:** the Victorian rowhouses, scattered everywhere.

**Rich and poor.** Wealth falls from the sealed core outward. Around the first ring stand pale stone manors with columned porticos, with walled gardens and fountains behind them. The middle rings are ordinary houses. Toward the walls come crooked five-storey tenements with laundry lines, and then the slums: plank shacks with patched lean-to roofs and stovepipes, some stacked two high with ladders. They crowd the back alleys and press against the inside of the wall in the poorest quarters. Wealth also shifts by quarter (the Temple Ward is richer, the Wayfolk Quarter poorer), plus slow random swings, so districts form on their own.

**Windows at night.** Every house now has lit windows after dusk, about six in ten.

**Patch notes · v0.12.0**

- Changed: the building kit is now generated in code; the 350 KB model file is removed.
- Added: 13 new building types: Manor, Tenement, two Shacks, Longhouse, Lodge, Adobe, Domed adobe, Spire, Forge, Roundhouse, Timberframe, Chapel, Shopfront, plus Gardens.
- Changed: Aldrath's houses are chosen by quarter culture and by wealth: manors by the plaza, slums by the walls. About 900 buildings, drawn in about 20 instanced batches.
- Added: windows glow at night, randomly lit house by house.
- Added: Admin teleports for the Wall slums and the Rich ring.
- Fixed: plaza lamps no longer stand in the mouths of the avenues.

## Devlog 28 · The lamps that push the Fog

*Prototype v0.11.0 · 22 November 2026*

You added a piece of lore: street lamps in this world aren't just lights. They burn a tech made to push the Fog back, so a lit street is a safe street, and you don't need your own lantern in cities and safe places.

So the streets are lit now. Aldrath's city has about 400 cast-iron lamps with brass collars (the pusher coil) along both sides of every ring street and avenue, around the grand plaza and the market, and outside the gate. The village and Hollin's Cross have oak posts with hanging brass lanterns, and a line of them follows each road out of town until the wilds begin. At dusk they warm up, cast pools of light on the cobbles, and the nearest ones light everything around you.

Under the lamps the night works differently: the Fog stays thin, monsters don't gain their night strength, and they fight as if you were holding a lantern. Step past the last lamp on the road and the night is as dangerous as before.

**Patch notes · v0.11.0**

- Added: Fog-pusher street lamps: 450 in all (cast-iron city lamps and oak village lamps), drawn in a few instanced batches.
- Added: safe light: inside the city walls, the village, the port, and within 10 m of any lamp, night fog stays thin and enemies don't get their night buff.
- Changed: lamps glow and cast light pools at night; the eight nearest light the area around you.
- Changed: the dusk message tells you when the street lamps are holding the Fog back.
- Known: the city's rowhouse windows don't glow at night yet (the village houses do).

## Devlog 27 · Brick, slate and old stone

*Prototype v0.10.0 · 22 November 2026*

Your idea for the architecture: Western European castles for the walls, urban Victorian housing inside, medieval stone streets, and only the lightest touch of steampunk. So the first building kit was made in Blender: three Victorian rowhouses (red brick with a bay window and a mansard roof with dormers; a pale sandstone house with a slate gable; a tall four-storey with a balcony and a brass pipe and gauge on its side), a castle wall section with merlons and arrow slits, a round tower with a conical slate roof, and a twin-towered gatehouse with a brass clock.

Aldrath's city is rebuilt from them. Hundreds of terraced houses stand shoulder to shoulder along the ring streets, tinted subtly by quarter, inside a ring of castle wall, and the streets are cobbled. Every house and wall piece is drawn as one instanced batch, so the whole city costs only a handful of draw calls.

You also asked for a way to check places quickly, so there is now an Admin panel: teleport to fifteen locations, set dawn, noon, dusk or night, turn on invulnerability or fast travel speed, and spawn an enemy.

**Patch notes · v0.10.0**

- Added: Blender building kit: three Victorian rowhouses, castle wall section, round tower, gatehouse (about 350 to 980 triangles each).
- Changed: Aldrath's outer city uses the kit, with terraced streets inside castle walls; light steampunk accents.
- Changed: cobblestone streets in the city.
- Added: Admin panel (button, or P on desktop) with teleports, time of day, invulnerability, fast travel speed and enemy spawning.
- Known: the village and port still use the older painted houses; other peoples' cities will get their own kits.

## Devlog 26 · People in the streets

*Prototype v0.9.0 · 22 November 2026*

Your list was blunt: barren houses, no architectural style, weird grass, generic trees. And one wish: put our character into the world.

The Tinker from Blender now walks the island as the player, with his coat, goggles, gauge pauldron and spring rifle, and his walk, idle and aim animations. A lighter version of him, stripped of his gear and simplified to about 3,400 triangles in a single mesh, fills the streets as townsfolk, each tinted differently, walking the village square and the city's ring streets, with guards holding spears at the gate.

Houses got faces: timber framing, shuttered windows, stone, sandstone and white-and-gold facades by quarter, upper floors that jut out, a ridge beam, door frames and steps, flower boxes, barrels and crates. At night the windows glow. Trees grew branches and layered crowns that are darker at the base and lighter at the top; the grass became soft clumps of blades.

Then you sent a stack of architecture references, from hand-painted timber houses with boilers bolted on, to riveted Viking A-frames, to a rain-soaked city of glass and iron. They are now the art direction in the design doc, with a style for each people.

**Patch notes · v0.9.0**

- Added: the Blender Tinker as the player character, animated.
- Added: townsfolk model for crowds, villagers and gate guards.
- Changed: houses have styled facades by quarter, jettied upper floors, ridge beams, door frames, flower boxes, barrels and crates; windows glow at night.
- Changed: trees have branches, layered crowns and top-lit shading; pines have three tiers.
- Changed: grass is drawn as clumps of blades.
- Fixed: black flowers; characters rendering nearly black.
- Added: architecture art direction per people, from your references.

## Devlog 25 · Three moons and a long road

*Prototype v0.8.0 · 22 November 2026*

Three moons, one of them broken: that was your call, and it is in the sky now. A large pale moon, a small violet one, and a third split by a jagged crack, fragments drifting beside it. Each follows its own path, so some nights all three are up and some nights only one. What they mean is still to be written.

Then two sharp observations. First, why so many jagged edges? Every ground triangle had one solid colour, so roads, fields and streets stepped like staircases. Now colours blend between the corners of each triangle, and the edges are soft. Second, the distances were too small: the village sat 180 metres from the city wall, closer than any real town to its city. Riverwood is a walk from Whiterun, and Falkreath farther still. So the land grew. The city now stands about a kilometre north of the village, a skyline on the horizon with its spire, and Hollin's Cross about a kilometre south, each at the end of a road that winds through groves and meadows.

**Patch notes · v0.8.0**

- Added: three moons, one broken, each on its own orbit.
- Fixed: jagged, stair-stepped edges on roads, fields and streets; terrain colours now blend smoothly.
- Changed: the outer city moved about 1.1 km north of the village, Hollin's Cross about 1 km south.
- Changed: the island grew to fit; longer winding roads between the three.
- Changed: clearer air near civilisation, so the city stays visible from the village.

## Devlog 24 · A sky to look up at

*Prototype v0.7.0 · 22 November 2026*

Three notes from you: mounts are coming, horses and bigger beasts, so roads must be wide enough; the land should look better before we go further; and what about the sky, and how many moons?

The sky is now a single dome drawn by code every frame, rather than painted pictures. The sun rises in the east and crosses the sky, warm and orange near the horizon and white at noon, and the light on the land follows it. Clouds drift. Toward the Fog the blue washes grey. At night, stars come out and a moon rises opposite the sun, and the moonlight is faintly blue. The number of moons is waiting on a lore decision; the sky can hold up to three.

The sea now rolls in faceted waves that catch the light. Trees grow in groves with clearings instead of being scattered evenly, with new white birches and fuller three-lobed oaks, and tufts of grass cover the meadows. Roads and city streets are widened for riders: the country road is about nine metres, city ring streets about eighteen, the main avenues over twenty, and the city gate opening about nineteen. The camera also stops at walls now instead of passing through them.

**Patch notes · v0.7.0**

- Added: procedural sky with a moving sun, sunrise and sunset colours, clouds, stars and a moon.
- Changed: sunlight direction and colour follow the time of day; blue moonlight at night.
- Added: animated sea with waves.
- Changed: forests grow in groves with clearings; added birches, fuller oaks and grass tufts; patches of colour in the grass.
- Changed: roads, streets and the city gate widened for mounts.
- Added: the camera pulls in front of walls instead of clipping through them.
- Open: how many moons the world has.

## Devlog 23 · A capital, not a town

*Prototype v0.6.1 · 22 November 2026*

You walked the new city and said it plainly: if this is the greatest city of the age, home to every people and the hub of all trade, it is too small. It was about 250 metres across. Now it is 600.

The walls moved out and grew taller, with a tower every hundred metres. Inside, three ring streets and eight avenues divide the city into quarters, one for each people, each with its own colours: slate and iron for the Ferrin, grey stone for the Hrimfolk, sand and ochre for the Zarhim, greens for the Ruadhan, blues for the Ilvari enclave, a Temple Ward in white and gold, and a crowded Wayfolk quarter of every colour. Several hundred houses line the streets. At the heart, a grand plaza circles the sealed core, now larger, with statues of the twelve gods standing around it and guards at its edge.

One honest bug: scaling the walls up shifted where the wall segments fell, and for one build the great gate was quietly bricked over.

**Patch notes · v0.6.1**

- Changed: outer city from about 250 to about 600 metres across; taller walls, more towers.
- Added: quarters for each people with their own roof and wall colours, named in the HUD.
- Added: three ring streets and eight avenues; several hundred houses.
- Added: a grand plaza around a larger sealed core, with statues of the twelve.
- Changed: crowds now gather on the streets nearest to you.
- Fixed: the gate was walled shut after the resize.

## Devlog 22 · Through the gate

*Prototype v0.6.0 · 22 November 2026*

The gate of Aldrath's outer city stands open now. Two guards with spears watch it from between the towers, and past them a long avenue runs north under rows of banners. A ring street circles the city, and two rows of tall houses line it, three and four floors, roofs in every colour. Just inside the gate, the market square: stalls with striped awnings around a stone fountain, and townsfolk drifting along the streets, thinning out after dark.

Walk far enough north and the houses end at the sealed core: a dark ring of wall, buttressed and banded in violet light, with the spire rising out of it. You can touch the wall. You cannot go in.

**Patch notes · v0.6.0**

- Added: the city gate opens; gate guards.
- Added: inside the outer city, a main avenue with banners, a ring street, about a hundred houses, and paved streets.
- Added: the market square with stalls and a fountain.
- Added: crowds of townsfolk that walk the streets, fewer at night, only simulated near you.
- Added: the sealed core's walls, with buttresses; they block your way.
- Added: place names for the gate, the market square, the city and the sealed walls.
- Known: buildings are placeholders; architectural style comes in a later art pass.

## Devlog 21 · A village in the shadow of the walls

*Prototype v0.5.0 · 22 November 2026*

The lore had a map; now the map has ground under it. The old camp with its palisade is gone. In its place stands the starting village: houses with red, blue, yellow and green roofs around a square with a well, market stalls, banners and Warden Edda, a windmill turning over striped fields. North, past the meadows, rise the walls of Aldrath's outer city, with towers and a closed gate, rooftops crowding behind, and at its heart the sealed core, ringed by a band of violet light, with a spire that catches the eye from anywhere on the island. South, a dirt road winds through flower meadows to Hollin's Cross: a few houses, a long pier, a ship rocking at its mooring, and a red-and-white lighthouse.

The colour now follows civilisation. Near the village, the road and the city the grass is bright and full of flowers; walk away from them and the land greys, woods turn to overgrown wilds, broken pillars appear, and the Fog closes in. At night it all goes dark except the warm windows, and the Fog thickens, hardest in the wilds. Light your lantern and the darkness pulls back a little; monsters inside its light hit softer and fall faster. Out in the wilds at night they hit much harder.

**Patch notes · v0.5.0**

- Added: the starting village, Aldrath's outer city with its sealed core, the south road, and Hollin's Cross with a pier, ship and lighthouse.
- Added: an island coastline with the inner sea around it.
- Changed: colour, wildness, ruins and danger now depend on distance from the village, road, port and city.
- Added: the lantern (button or L): light at night, weaker monsters inside it.
- Added: night makes the Fog thicker and monsters stronger, by region.
- Added: place names in the HUD.
- Known: the city gate and the ship are not usable yet; those are the next prototype steps.

## Devlog 20 · The gods have names

*Lore document v1 · 22 November 2026*

Today the world got its history, and it came from you, one piece at a time, while I mostly listened. An empire of men on the continent of Erde. A head of the Gods strong enough to split a continent, and corrupt enough to plan for ages. A ban on magic that was really a trap. A Fog born from magic and the smoke of endless war, and a kind goddess, Merrith the Merciful, who gave herself to weaken it.

Then the peoples, eight of them playable: the hardy Hrimfolk of the north, the feudal Aurelans of the eastern isles where every player begins, the blue-inked Ilvari chasing lost magic, the short and brutal Ferrin of the Slag Isles, the desert Zarhim, the red-haired Ruadhan of the forests, the everywhere Wayfolk, and the Forsaken who were freed and now whip themselves for what they were. And twelve gods who are each the best of their people, not gods of fire or water. Among them a god who hid from the truth, a goddess who taught everyone nature's magic, and a god of protection whose fall into the Fog will be part of the story.

The tone settled last, and it might be the best idea of the day: the world looks like bright high fantasy, and the story slowly shows you the grimdark truth underneath.

**Patch notes · lore**

- Added: [Fogwright Lore](https://claude.ai/artifact/FJAb6SGL6Z4E8NJdw6sapX) with the three ages, the split of Erde, the ban on magic and the birth of the Fog.
- Added: the twelve gods, the 13th, and the hidden 14th; the lost gods, technomancy and the warps.
- Added: ten peoples, eight playable, with working names.
- Added: magic as a mysterious force that every chosen player can use according to their class.
- Changed: tone is high fantasy on the surface, grimdark underneath, in both the lore and the design doc.

## Devlog 19 · Made, not just generated

*Design doc update · 22 November 2026*

You brought up the games with millions of galaxies, then landed on a clear line: build a playable game with a playable world first, and save location expansions for later. The land itself can come from the generator, but every place with a name will be made by hand, from lore we write together.

So the generator becomes the ground under the story rather than the story. It shapes hills, forests, rocks and stray ruins. Regions, cities, roads, ship routes and dungeons are authored and set onto that ground, which bends around them. And the endless lands people dream about have a home in the plan: beyond the Fog wall, as an expansion after launch.

**Patch notes · design doc**

- Changed: terrain and biomes are generated; places, regions and cities are authored from lore.
- Added: Beyond the Fog as a post-launch expansion of endless generated realms.
- Added: open task to write the world lore.

## Devlog 18 · Mountains, seas and a ship that sails

*Design doc update · 22 November 2026*

You named the cities you love: Windhelm and Solitude, not Whiterun. What they share is not just size but place: a fortress guarding a river crossing, a city perched on a stone arch over the sea. And you asked for the land itself to earn its words: mountains that feel like mountains, seas that feel like seas, and a ship that actually sails, like the boats in World of Warcraft.

So Fogwright's world now has a shape. A large island with a mountain spine, peaks of 500 to 800 metres with snow and cliffs, rivers running to coasts on two sides, and an inland sea wide enough to lose the shore. A cliff city above the sea and a river fortress inland, joined by a ship that leaves on a schedule and carries everyone aboard across real water. The shattered capital waits in the Fog-bound peaks.

**Patch notes · design doc**

- Added: Geography section with world layout, mountains and oceans.
- Added: Ships section: scheduled ships on real routes, walkable decks, shared voyages.
- Changed: Cities now reference Windhelm and Solitude, built into dramatic geography.

## Devlog 17 · A world with edges, and cities with room

*Design doc update · 22 November 2026*

Two decisions, no code. Skills will not be designed one by one; they come from the skill tree, and the five in the prototype are only there to test the controls. And the world gets a size: about 20 km across, like Valheim, walled in by impassable Fog.

You also asked whether a big open world would glitch. Mostly no, since only the area around each player ever exists. But that far from the centre, graphics cards start rounding positions, so the world will quietly re-centre itself on the player every few kilometres.

Then the more fun question: cities should feel like cities, not like Whiterun. So the plan now has living survivor cities several hundred metres across, ruined imperial cities full of Fog, and the shattered capital at the end, with districts, rooftops, walls you can walk, and crowds, built from modular pieces so a phone can still carry them.

**Patch notes · design doc**

- Added: world size of about 20 km with a Fog wall at the edge.
- Added: floating origin to prevent jitter far from the centre.
- Added: Cities section with living cities, ruined cities and the capital, and how they stay light.
- Changed: prototype skills marked as placeholders; real skills come from the skill tree.

## Devlog 16 · Aim it yourself

*Prototype v0.4.1 · 22 November 2026*

A sharpening of the rules from you: in Classic, skills are skillshots; in Action, they go where the crosshair points.

On touch screens, a skill now works the way Wild Rift and Mobile Legends players expect. Press it and drag: a bright ring on the ground shows the skill's reach, a line shows where Overcharge will fly, a circle shows where the Shock canister lands, and Dash shows its path. Let go to cast, or slide onto the Cancel circle to change your mind. A quick tap still fires at your current target for when there is no time to aim. On PC in Classic, the number keys fire toward the mouse cursor, the way Albion does it. Overcharge is now a true skillshot that flies straight and hits the first thing in its path.

The first version of the aiming ring was nearly invisible on the meadow grass, so it got a bright edge and draws on top of everything.

**Patch notes · v0.4.1**

- Changed: Classic skills are skillshots. Touch: press and drag to aim, release to cast, quick tap to cast at your target. PC: keys cast toward the mouse cursor.
- Added: ground indicators for range, line skills and area skills, and a Cancel circle.
- Changed: Overcharge flies straight and hits the first enemy in its path; Gear turret can be placed where you aim.
- Unchanged: Action mode skills aim at the crosshair; Dash follows WASD when keys are held.

## Devlog 15 · Two ways to fight

*Prototype v0.4.0 · 22 November 2026*

Your note: PC players should be able to drop the classic MMO controls for something more active, with WASD, number keys for spells, left click to attack and right click to block. And both styles must keep working.

So PC now has a switch in the top-right corner. Classic stays exactly as it was: target, auto-attack, cast. Action puts the camera over the Tinker's right shoulder with a crosshair. The mouse aims, left click fires where you look, right click raises a brass gear shield that turns away most of a frontal hit while it drains your energy, and Space jumps. Shock canisters land wherever the crosshair meets the ground. When the crosshair sits on an enemy it turns red and shots home in, so a twitchy mouse is not punished.

To give the number row five keys, the Tinker learned a fifth trick for both control styles: a Gear turret on a little tripod that shoots whatever comes near for twelve seconds.

**Patch notes · v0.4.0**

- Added: Action controls for PC: mouse aim with an over-the-shoulder camera and crosshair, left click to shoot, right click to block, Space to jump.
- Added: blocking cuts frontal damage by 70%, drains energy and slows movement.
- Added: Gear turret skill on key 5 and a fifth button on touch screens.
- Added: Classic or Action switch on PC, remembered between sessions; phones and tablets stay Classic.
- Changed: in Action mode skills aim at the crosshair; Steam dash follows WASD.
- Fixed: aimed shots stopped after the first one; shots now home in on the enemy under the crosshair.
- Known: if the browser refuses to lock the mouse, the cursor aims instead and the screen edges turn the camera.

## Devlog 14 · First blood in the Fog

*Prototype v0.3.0 · 22 November 2026*

A change of course from you: park building and survival, and focus on fighting, looting and questing, with combat like Albion Online and World of Warcraft and controls like Albion mobile, Wild Rift and Mobile Legends. Also: landscape only, and build mode as its own button.

So the Fog finally has teeth. Fog wolves hunt in packs, Fog husks lumber after you, and both get stronger the farther you go from camp. Tap one, or press Attack, and the Tinker walks into range and fires his spring rifle on his own. Around the big Attack button sit four skills: Overcharged shot, a Shock canister that slows everything it hits, a Steam dash, and a Patch kit. Damage numbers pop, crits flash gold, and Edda waits at the camp with a three-quest chain that ends at the broken tower, where the Tower Warden slams the ground with a red warning circle you had better step out of.

The funniest bug of the day: the 'Next target' button and the enemy you were targeting shared a style name, so your target's health bar turned into a giant red-and-black button floating over the wolf.

**Patch notes · v0.3.0**

- Added: tab-target combat; tap an enemy or press Attack to target, walk into range and auto-attack.
- Added: skills Overcharged shot, Shock canister, Steam dash and Patch kit, with energy and cooldowns.
- Added: Fog wolf, Fog husk and the elite Tower Warden with a telegraphed ground slam.
- Added: enemy levels by distance, more enemies at night, a safe zone around camp.
- Added: XP and levels; health, damage and armor from level and gear.
- Added: loot bags in four rarities, Fog shards, a bag panel to equip or salvage, gear shown on the character.
- Added: Warden Edda with the quests First Watch, Lamp Oil and The Broken Tower, plus a quest tracker.
- Changed: landscape layout for phones and tablets, with a turn-your-device screen in portrait.
- Changed: building moved behind a Build button that swaps the controls; hunger and warmth paused.
- Known: one class and one weapon so far; no PvP; tuning is rough.

## Devlog 13 · Level ground

*Prototype v0.2.1 · 22 November 2026*

Your first build on a phone came back as two screenshots: floors at different heights like a staircase, walls of uneven height, and a note that the controls were difficult.

Every piece had been choosing its height from the ground under it, so on a slope no two agreed. Now heights snap to quarter-metre steps, and a building stands on one level: when a new floor needs to sit higher, the whole connected floor and the walls on it rise to match. Walls that meet end to end share a height too.

The controls asked too much of a thumb. Building aimed wherever the character happened to face, so you had to walk around to aim. Chopping needed you to face the tree exactly and keep holding a button. Now building aims where the camera looks, and walls turn to face you on their own. Tapping Use near a tree, rock or bush keeps working until it is done; a gold ring shows what you will hit. The camera follows behind you as you walk, and the joystick sits visibly in the corner so your thumb knows where to go.

**Patch notes · v0.2.1**

- Fixed: floors and walls at uneven heights on slopes.
- Added: connected floors and their walls level to one height.
- Changed: building aims where the camera looks; walls face you automatically; Rotate flips them.
- Changed: tap Use once to keep chopping, mining or picking; tap again or walk away to stop.
- Changed: harvesting picks the nearest resource in any direction and turns you toward it.
- Added: gold ring under the resource you are about to harvest.
- Added: camera follows behind you while walking forward.
- Added: joystick visible at rest on phones.

## Devlog 12 · Something to do before dark

*Prototype v0.2.0 · 22 November 2026*

Your verdict on the new hands was short: still bad. So the character went back on the shelf, and the game got its first real loop instead: gather, craft, build, survive the night.

Now the world wants things from you. Trees, rocks and berry bushes can be harvested; walk up and hold Use. The workbench at camp turns wood and stone into a stone axe and a pickaxe, which double your speed. Build mode snaps floors, wooden walls, stone walls and campfires to a two-metre grid, and walls actually stop you. Every five minutes the sun goes down: the world turns blue-black, warmth drains unless you stand near a fire, and hunger never stops ticking. Let either run out and your health follows. Collapse and you wake at camp having lost half of what you carried.

Everything you change is saved as a list of edits on top of the world seed: trees felled, pieces built. That is exactly the shape the multiplayer server will store, so this code moves to the server mostly unchanged.

**Patch notes · v0.2.0**

- Added: harvesting trees (wood), rocks (stone) and berry bushes (berries).
- Added: crafting at the workbench: stone axe and pickaxe, each doubling harvest speed.
- Added: build mode with floors, wooden walls, stone walls and campfires on a grid; rotate, remove with half refund.
- Added: wall collision.
- Added: day and night cycle of five minutes with darker skies and fog at night.
- Added: hunger, warmth and health; eat berries; fires keep you warm; water chills you.
- Added: collapse and respawn at camp.
- Added: autosave of the world edits, inventory and needs, per seed.
- Added: phone controls: hold Use, Build, Rotate, Eat, Craft. Desktop keys: E, B, R, Q, C, 1 to 5.
- Known: the character's hands are still not good enough and will get another pass later.
- Known: no enemies yet; the Fog does not attack at night.

## Devlog 11 · Hands, at last

*Character model r7 · 22 November 2026*

"Those are some horrendous hands." No arguing with that. The hands were the last part still made of melted blobs, and fingers are exactly where soft blobs fail: they fuse into a lump.

So the hands stopped being sculpted and started being built, like a puppet maker would. A lofted palm that is wider at the knuckles and thin across the back. Four fingers, each with three jointed segments, a slight fan, and lengths that step down from middle to little finger. A two-joint thumb resting along the side of the palm, with the soft muscle at its base. The left hand hangs relaxed; the right hand curls closed, because it is always holding the rifle.

The leather gloves are the same hand lifted a few millimetres off the skin, so they fit every knuckle.

**Patch notes · Tinker r7**

- Fixed: blobby, fused hands.
- Added: modelled hands with palm, jointed fingers, thumb and thumb muscle.
- Added: relaxed pose for the left hand, gripping pose for the right.
- Changed: gloves now fit the new hands exactly.
- Added: Hand view in [Tinker Model Review](https://claude.ai/artifact/XeXAVhVZRCBe9MePg7TJBV), centred on the left hand.
- Known: about 31k triangles; the optimization pass will bring this down.

## Devlog 10 · Out of the cave

*Character model r6 · 22 November 2026*

Two sharp notes from you. First, the facial bones made him look like a caveman. Second, the elbows turned his arms into sausages.

Both were right, and both had the same root: shapes stacked too literally. The face had a heavy brow shelf, deep eye sockets, a low sloping forehead and a wide jutting jaw. Now it has a taller cranium, an upright forehead, a light brow, a defined jawline and chin, and a straighter nose. The eyes, brows and moustache were reseated on the new face.

The arm had even tubes meeting a ball at the elbow, so it pinched. Now the muscles taper and overlap the joint the way real ones do: the triceps narrows into the point of the elbow, and the forearm muscles start above it, swell just below, then flatten toward the wrist.

**Patch notes · Tinker r6**

- Changed: face structure with taller cranium, upright forehead, lighter brow, shallower eye sockets, defined jaw and chin.
- Changed: eyes, eyebrows and moustache reseated on the new face.
- Fixed: sausage arms; muscles now taper and overlap across the elbow.
- Added: point of the elbow, triceps insertion and forearm muscles starting above the joint.
- Added: Arm view in [Tinker Model Review](https://claude.ai/artifact/XeXAVhVZRCBe9MePg7TJBV).

## Devlog 9 · A proper haircut

*Character model r5 · 22 November 2026*

You sent a screenshot from your phone with a simple verdict: the square-cut hair did not look good. Up close it was obvious why. The hair was cut from the simplified head, whose triangles are about two centimetres wide, so every hairline came out as a staircase.

The first fix made it worse. Cutting from the detailed head and then smoothing the jagged edge folded it into spikes, a lesson in fixing the cause rather than the symptom.

The real fix was to stop picking triangles at all. The hairline is now a smooth curve drawn around the head: across the forehead, dipping at the temples into the sideburns, swinging around each ear and tapering at the nape. The detailed head surface is sliced exactly along that curve, and the cut piece is lifted off the scalp with a real edge, so the hair has volume. The sideburns now rise to meet it.

**Patch notes · Tinker r5**

- Fixed: square, stepped hairline.
- Changed: hair is cut along a designed hairline curve from the detailed head, about 2,200 triangles.
- Added: hair thickness, with an edge that meets the scalp.
- Changed: sideburns extended up to join the hair at the temples.
- Known: about 27k triangles in total; the optimization pass is next on the list.

## Devlog 8 · He can hear us now

*Character model r4 · 22 November 2026*

One word from you: "Ears?" Fair question. They were technically there, as two small bumps, but the new hair grew right over them and a sideburn sat where the ear should be.

Now each ear is modelled: a curled outer rim, an inner bowl, a lobe and the little flap at the front, tilted back and angled out from the head the way real ears sit. The hair is trimmed in an oval around each ear, and the sideburns moved forward and slimmed down.

**Patch notes · Tinker r4**

- Added: modelled ears with rim, bowl, lobe and front flap.
- Fixed: hair covering the ears; it now stops in an oval around them.
- Changed: sideburns moved forward and made thinner.
- Added: Profile view in [Tinker Model Review](https://claude.ai/artifact/XeXAVhVZRCBe9MePg7TJBV).
- Known: the hairline around the ear is still angular; smoothing is planned for the optimization pass.

## Devlog 7 · Standing like he means it

*Character model r3 · 22 November 2026*

Your eye caught what the muscles missed: the hips and knees were awkward, places where one shape simply bumped into the next. The thigh started thin under a wide pelvis, and the knee was a knob with narrow sticks above and below. You also suggested fixing it together with the posture, and that turned out to be the key, because a locked-straight leg shows every seam.

The skeleton itself moved: the legs now stand a little wider, with the feet turned slightly out. New volumes bridge the gaps: a broad mass where thigh meets pelvis, an outer hip, a lower thigh that tapers into the knee, and a top of the shin that flows on into the calf. The joints also blend more softly between bones, so they bend without creasing. In the idle pose he now stands with soft knees, chest up and head a little forward, like someone who has been walking all day.

**Patch notes · Tinker r3**

- Changed: wider stance with feet turned slightly out.
- Fixed: pinched transition between pelvis and thigh.
- Fixed: lumpy knee; thigh, knee and shin now flow into each other.
- Changed: smaller glutes and a flatter belly.
- Changed: softer weight blending across joints.
- Changed: idle posture with soft knees, chest up, head forward and relaxed arms.
- Added: Legs view in [Tinker Model Review](https://claude.ai/artifact/XeXAVhVZRCBe9MePg7TJBV).

## Devlog 6 · A body worth wearing armor on

*Character model r2 · 22 November 2026*

You sent three Valheim screenshots and a short verdict: the armor looked okay, the body did not. Fair again. The first body was a chain of tubes, and no amount of gear hides that when the coat comes off.

So the body was sculpted again from scratch, this time from muscles. Every muscle group is a soft volume (chest, shoulders, trapezius, back, abs, glutes, biceps, forearms, thighs, calves) and they melt together into one surface. The face got a skull, a jaw, cheekbones, a brow ridge and real eye sockets carved inward. Then the surface is reduced to about 5,600 triangles, which gives that hand-chiselled low-poly look, and ambient shadow is baked into the skin so the muscle lines read without textures.

The nicest idea of the day: clothes are now grown from the body itself. Trousers, shirt, waistcoat, boots, gloves and even the hair are shells lifted a few millimetres off the skin, so they fit perfectly and bend exactly like the body. The coat, sleeves, belt and straps measure the body and size themselves to it. The first time that measuring ran, it measured both arms at once and the sleeves ballooned into wings. One line of code later, they fit.

**Patch notes · Tinker r2**

- Changed: base body rebuilt from muscle volumes with heroic proportions; hands with fingers and a thumb.
- Changed: face rebuilt with skull, jaw, cheekbones, brow ridge and eye sockets; smaller eyes with lids.
- Added: baked ambient shading in the skin.
- Added: garments as shells from the body: trousers, shirt, waistcoat, boots, gloves, hair.
- Added: coat, sleeves, belt, straps and boot cuffs sized automatically to the body.
- Added: Base body button in [Tinker Model Review](https://claude.ai/artifact/XeXAVhVZRCBe9MePg7TJBV).
- Fixed: the baked shading was hidden behind an empty color layer.
- Known: 24k triangles, mostly from duplicated garment shells. The optimization pass will trim shells and merge pieces.

## Devlog 5 · The Tinker takes shape

*Character model r1 · 22 November 2026*

The first real character of Fogwright exists. You sent five pieces of concept art, from a coat-and-goggles tinkerer to a riveted steam suit, and they showed both the armor ladder and the world: grey mist, broken rock, and warm brass glowing against the cold.

The Tinker is built entirely by code. A Blender script shapes the body, tailors a long coat around it, places every rivet and gear tooth, builds a skeleton, binds the mesh to it and animates it. Nothing was sculpted by hand, which means every later armor piece can be made to fit the same body exactly.

The hardest moment was the rifle. The first aim pose had him pointing it at his own boots, because twisting bones by angles in an A-pose gets unpredictable fast. The fix was to stop rotating bones and start pointing them: say where the elbow and the hand should be, and let the bones aim there. The rifle came up to the shoulder on the next try.

Then a question from you: how many triangles does Valheim's character have? No one publishes that number, but it made us look again. The Tinker's 10.8k triangles are fine; what phones really choke on is the 100 separate pieces, so the next pass merges them instead of stripping detail.

**Patch notes · Tinker r1**

- Added: base body on the shared skeleton that every armor tier will use.
- Added: light Tinker gear — long coat with red lining, waistcoat, goggles, glowing eyepiece, scarf, brass gauge pauldron, geared leg brace, belt with pouches and wrench, satchel, tool roll.
- Added: spring rifle with brass coil, scope and glowing cell.
- Added: Idle, Walk and Aim animations.
- Added: [Tinker Model Review](https://claude.ai/artifact/XeXAVhVZRCBe9MePg7TJBV), a viewer with turntable, views, animations and gear toggles.
- Fixed: rifle aimed at the ground; now level at the shoulder.
- Fixed: bead eyes, block nose and box moustache replaced with shaped versions.
- Fixed: flat shelf shoulders on the coat; long neck; boot soles sticking out.
- Known: 10,842 triangles in about 100 pieces. Merging and distance levels of detail come next.

**Behind the scenes:** Blender 5 quietly dropped the export option we needed, so the model is converted to a format the web page can load by a tiny script of our own.

## Devlog 4 · Dungeons, tiers and a skill tree

*Design doc updates · 22 November 2026*

A day of big decisions, mostly made in a sentence or two. You were picturing Albion Online's dungeons, and they fit so well that they became Breaches: vaults of the old empire that crack open when the Fog swells, then collapse behind you. Persistent dungeons followed, fixed under the great ruins, where a shortcut one friend opens stays open for everyone.

The tone shifted too. Your armor references were full steampunk, and you pointed out the obvious: you cannot build a steam suit from the wood and stone you gather on day one. So technology now climbs with the game, from rope and timber to foundries, boilers and brass.

**Decisions**

- Simple low-poly 3D, so buildings feel grand and gear shows on the character.
- Co-op first; PvP later, with Breach invasions as a likely first mode.
- Two dungeon types: persistent dungeons in the open world, and temporary Breaches.
- Crafts grant abilities and armor proficiency, like World of Warcraft; one shared skill tree, like Path of Exile, lets builds grow wide until anyone can wear anything.
- Five armor tiers: light, medium, heavy, plate, and the Rig, a powered suit you climb into.
- Characters are built by Claude from your references, on one shared skeleton.

**Patch notes · design doc**

- Added: Dungeons section with Persistent dungeons and Breaches.
- Added: Skill tree and armor section with the five armor tiers.
- Added: Character pipeline, gear slots (separate left and right arm) and visual language.
- Changed: art and tech sections from 2D to simple low-poly 3D.
- Changed: roadmap now has six milestones, with M4 Dungeons.
- Changed: setting tone from Leonardo workshops to technology that climbs with progression.

## Devlog 3 · Less Minecraft, more character

*Prototype 1 v0.1.1 · 22 November 2026*

Your verdict on the first character was honest: it looked like it came from Minecraft. Fair. The boxes had done their job of proving gear could show on the model, so they were retired.

The new character got knees and elbows, a smaller head, a nose, ears, a beard and a topknot. The world got real sunlight: trees, the palisade and the broken tower now cast long shadows across the meadow, which did more for the mood than any single model.

**Patch notes · v0.1.1**

- Changed: character rebuilt with tapered limbs, knee and elbow joints and smooth shading.
- Changed: gear refitted — rounded helmet with nose guard, fitted cuirass, curved cape, level crossbow.
- Added: real-time sun shadows for the character, trees, buildings and ruins.
- Added: walk with bending knees, swinging arms, torso twist, idle sway and a cape that lifts when running.
- Fixed: crossbow held pointing at the sky.
- Known: shadows cost frame rate; a quality setting may be needed on phones.

## Devlog 2 · First steps in a generated world

*Prototype 1 v0.1.0 · 22 November 2026*

The first playable thing: a world you can walk on your phone. Everything in it grows from one seed number, so the same seed makes the same world on every device, and a link with that seed lets a friend walk the same land.

You worried 2D would make buildings feel small and gear invisible, so the prototype went straight to low-poly 3D. Walking out from the camp, the meadow gives way to old forest, then marsh, then ashen highlands, while the Fog thickens and turns violet. A broken tower of the old empire stands near camp, and on the far horizon a pillar of light marks the shattered capital.

**Patch notes · v0.1.0**

- Added: [Fogwright Prototype](https://claude.ai/artifact/UdQogHruyFvnyrzd4UwbkK), playable on phone and desktop.
- Added: seeded, endless world streamed in chunks, with four biomes ringed outward from camp.
- Added: rivers, scattered ruin circles, trees, rocks, reeds.
- Added: the Fog, thickening with distance, with a meter in the corner.
- Added: camp with longhouse, campfire, workbench and palisade; the broken tower nearby.
- Added: touch joystick, drag to look, pinch to zoom; keyboard and mouse on desktop.
- Added: gear toggles and Tinkerer, Smith and Warden presets.
- Added: New world button; the seed is saved in the link.
- Fixed: rivers too wide, a stray roof piece, the compass label cut off at the bottom of the screen.

## Devlog 1 · A game is born

*Design doc v1 · 22 November 2026*

It started with "let's plan a game" and a question about those tiny procedurally generated games on Reddit: could one be an MMO to play with friends? Then a list of loves: Project Zomboid, RimWorld, Valheim, Ragnarok Online, Skyrim.

The common thread was surviving and building together in a world that pushes back. Modern or medieval? Fantasy won, but with a twist: a world three centuries after its magic broke, where every spell feeds a creeping Fog and survivors rebuild with inventions instead. The name came with it: Fogwright, a maker who works against the Fog.

You also corrected an early assumption: the 1 MB size was never the point. The point was being light enough to run anywhere, so the game is web-first and wrapped for desktop and phones later.

**Patch notes · design doc v1**

- Added: [Fogwright design doc](https://claude.ai/artifact/8gLwC7k38EPbFi2mVEWpYa) — pitch, pillars, setting, core loop, six crafts, part-based inventions, the Fog, world generation, survival and settlers, tech plan, roadmap, risks.
- Decided: co-op for 2 to 16 friends on a persistent server.
- Decided: magic is powerful but feeds the Fog; machines are safe but slow to build.
- Decided: lightweight and cross-platform, starting in the browser.
