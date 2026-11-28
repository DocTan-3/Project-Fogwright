# Fogwright — Game Design Document

2026-11-22 · @Dev Tan

## Overview

Fogwright is a lightweight, cross-platform co-op survival game where a small group of friends resettles a fantasy world broken by its own magic, using inventions instead of spells.

**Pitch:** Three centuries after the arcane empire fell, the land is wild, the ruins are full of relics, and a magical Fog creeps over everything. You and your friends build a settlement, rediscover lost crafts, and engineer your way back to the shattered capital. Every spell you cast feeds the Fog.

**Design pillars**

1.  **Build together, depend on each other.** Crafts are interlocking, so no player can do everything alone.

2.  **Invent, don't just craft.** Machines are assembled from parts, so experimenting is the fun.

3.  **The world pushes back.** The Fog, events and settlers generate stories without a script.

4.  **Light enough to run anywhere.** A browser link works on PC, Mac, phone and tablet, with small downloads and modest hardware.

**Influences**

| Game            | What we take                                                        |
|-----------------|---------------------------------------------------------------------|
| Valheim         | Co-op survival, biomes that get harder with distance, base building |
| RimWorld        | Settlers with needs and moods, events that create stories           |
| Project Zomboid | Detailed wounds and sickness, scavenging, creeping dread            |
| Ragnarok Online | Job classes, a persistent shared world, social progression          |
| Skyrim          | Open exploration, a landmark on the horizon to aim for              |

**Players:** 2 to 16 friends on one persistent server, which keeps running between sessions. Built for groups that play a few evenings a week, not for thousands of strangers. Co-op only for now; PvP is planned for later, and the server already decides all game state, so it can be added without a rewrite.

## Setting

The world is a fantasy realm 300 years after a magical collapse, being resettled by people who build machines because magic is dangerous.

- **The fall.** An arcane empire ran everything on magic until a great working went wrong. Its cities fell in a single night, and the magic that was left curdled into the Fog.

- **The land now.** Forests, marshes and mountains have reclaimed the empire. Its ruins (towers, aqueducts, vaults) are scattered everywhere, half-buried and full of relics.

- **The survivors.** Scattered villages that rejected magic and kept the old mechanical trades alive. The players are the first generation to push out and resettle.

- **The Fog.** Leftover magic that spreads, twists living things, and is drawn to spellcasting. It is the main threat and the reason the world is dangerous.

- **The goal on the horizon.** The shattered capital of the first age lies somewhere in the Sundering, the thickest Fog at the world's edge (exactly where is still open). Reaching it and finding out what happened is the long-term goal.

**Tone:** high fantasy on the surface, grimdark underneath. The world first looks like a medieval high-tech high fantasy: grand cities around their gods, proud peoples, steam and brass progress, and chosen heroes guided by a kind goddess. The story then peels it back layer by layer to reveal a grimdark reality: a betrayer at the head of the Gods, gods fading and hiding, protectors devoured by the Fog. Visually the game starts bright and grand, and darkness creeps in as the story goes on. The land itself shows the gods' power: areas near the gods and their cities are colourful, tended and alive; toward the Fog at the world's boundaries, colour drains away and the land turns bleak, untamed and overgrown, more relic and ruin than civilization. As a god fades during the story, colour retreats from their lands. The world was once peaceful and is now forgotten: players piece its history together slowly from ruins, inscriptions, relics, the writings of lost peoples, and the warps nobody understands. The full history is in the lore document. The sky is a single procedural dome rather than image skyboxes: a moving sun, clouds, stars and moons, clear and blue near the gods and washed grey toward the Fog, ready for weather later (the number of moons is a lore decision still open). Mounts, from horses to larger beasts, are planned, so roads and city streets are built wide for riders. Prototypes use placeholder buildings and props; each people's architectural style is important and will be designed in a later art pass, once the systems settle.

## Core loop

Each session, players head out from the settlement, bring back resources and knowledge, and turn them into inventions that let them reach farther.

**Session loop (30 to 90 minutes)**

1.  **Check in.** See what happened while you were away: settler moods, Fog movement, events.

2.  **Plan.** Decide as a group what to build or where to go.

3.  **Venture out.** Gather, scavenge ruins, hunt, push into the Fog edge, or dive into a Breach before it collapses.

4.  **Return.** Carry loot home before night or a storm rolls in.

5.  **Build and invent.** Combine parts into new machines, upgrade the settlement, and treat wounds.

6.  **Defend.** Hold off Fog surges at night with walls, turrets and traps.

**Long-term loop (weeks)**

- Move up through the tech eras, from rope and timber to arcane engines.

- Push the Fog back and build outposts linked by roads, then rail carts.

- Rediscover all six crafts and recruit settlers.

- Reach the shattered capital and learn what caused the fall.

The loop runs on distance: the farther from the settlement, the richer the loot and the thicker the Fog.

## The opening: the fall of Farhallow

The tutorial is the story. Players begin as freefolk in Farhallow, a village on the far coast outside any god's circle, on the evening the Fog takes it. Each beat teaches something without instructions on screen: a calm late afternoon (moving, the camera, talking, picking things up); the Fog rolling in at dusk as colour drains away (sprinting, danger); the first weapon, grabbed in the panic, picked up and equipped (picking up, the equipment screen, equipping); a Fog-warped animal (the first fight, with that weapon); a half-changed neighbour (the grimdark moment, once); a huge shape glimpsed tearing down the gate (running, never fighting); the escape through fires to the last ship (following others, using the surroundings); the crossing as the Fog thins and colour returns; and arrival at Hollin's Cross at dawn, with Aldrath's glow on the horizon, where the game opens. If the player falls, Merrith's touch lifts them up once: safety that is also the first sign they are chosen. It is built beat by beat, each polished before the next: the village at peace first, then the Fog's arrival, then movement and the first enemy, and so on.

## Crafts

Players each choose a primary craft and can learn a secondary one later, so a group of four covers most needs but still has to trade.

| Craft       | Role                   | Signature abilities and inventions                                        | Depends on                                          |
|-------------|------------------------|---------------------------------------------------------------------------|-----------------------------------------------------|
| Tinkerer    | Engineer               | Crossbow turrets, traps, gliders, grappling hooks, clockwork scout drones | Smith for parts, Millwright for power               |
| Millwright  | Builder and automation | Waterwheels, windmills, bellows, conveyors, automatic sawmills            | Smith for gears, Warden for timber from far forests |
| Smith       | Gear and parts         | Weapons, armor, tools, gears, springs, pipes                              | Millwright to power the forge                       |
| Runecrafter | Magic                  | Spells, enchantments, relic cores for arcane engines (feeds the Fog)      | Herbalist for corruption cures                      |
| Herbalist   | Support and medicine   | Bandages, splints, antidotes, food, Fog-corruption remedies               | Warden for rare plants                              |
| Warden      | Scout and fighter      | Tracking, beast-taming, pushing back the Fog edge, escort duty            | Tinkerer for gear, Herbalist for healing            |

**Progression:** crafts level up by doing the work. New techniques are unlocked by finding schematic fragments in ruins, so exploring and crafting feed each other.

**Solo or small groups:** settlers can fill missing crafts at a lower skill level, so two players are still viable.

### Combat

Combat is tab-target, like Albion Online and World of Warcraft, with mobile controls like Albion mobile, Wild Rift and Mobile Legends.

- **Targeting:** tap an enemy or press Attack to select the nearest. The character walks into range and auto-attacks while standing still; moving with the joystick pauses attacks but keeps the target.

- **Skills:** skill buttons arc around a large Attack button. In Classic, skills are skillshots: on touch screens press and drag to aim with a ground indicator and release to cast (a quick tap casts at the current target); on PC the keys cast toward the mouse cursor. In Action, skills cast at the crosshair. Skills cost energy and have cooldowns shown on the buttons. Where skills come from is set out under *Moves, the bar and defence* below; the five in the prototype are placeholders for testing the controls, not designed skills.

- **Enemies:** levels rise with distance from camp, more spawn at night, and elites use telegraphed attacks marked on the ground.

- **Loot:** creatures drop Fog shards and gear by rarity (common, uncommon, rare, epic, and the one-of-a-kind legendaries in weapons.md), with item power and stats. Gear can be equipped or salvaged into shards.

- **Quests:** quest givers at settlements offer chains that lead outward, ending in dungeons and elites.

- **Layout:** landscape only on phones and tablets. Building has its own mode with its own controls.

- **Two control styles on PC:** Classic (tab-target, auto-attack, skills on the target) or Action (WASD, mouse aim with a crosshair, left click attacks, right click blocks, 1 to 6 cast at the crosshair, Space jumps). Both use the same skills and balance; phones and tablets use Classic.

#### Moves, the bar and defence

Decided with the user; items marked *(proposal)* are still open.

- **Weapons give the special moves.** A weapon's moves depend on its rarity (weapons.md): a common weapon only attacks, and rarer ones add traits and active moves that suit their type, such as a gun with a dash-reload or a sword with a magic slash. Later, trinkets, relics and magic rings add more special moves. Armour gives none: it gives protection, stats and passives. Because the build is the gear, gear is what players trade (the player economy, later).

- **The skill tree gives movement and changes how moves work.** Movement modifiers and the moves that come with them (dashing instead of a dodge roll, a leap, a slide) are skill-tree nodes. Most other nodes are modifiers rather than new buttons: reload while dashing, a wider slash, a second charge. Gear and the tree shape the same move, so two players with the same sword can fight differently. The tree also gives stats, armour proficiencies and the path moves.

- **Every character has the basic verbs:** move, auto-attack, a dodge, a block and a parry. The dodge is a roll by default; skill-tree nodes can turn it into a dash or a blink.

- **Block and parry share one button.** Held, it blocks: damage is reduced (35% gets through). Pressed just before a hit lands (a fifth of a second), it parries: only 5% gets through and the attacker reels, but a parry drains three times the stamina of a block. Only melee weapons can parry; with any other weapon a timed press is a block. Blocking without the stamina for it breaks the guard and staggers. *(Numbers from the first playable, to tune.)*

- **Stamina and energy.** Stamina pays for defence (dodge, block, parry) and recovers quickly once no defence is used; energy pays for skills. *(The user asked for parries to drain stamina; keeping it a pool apart from energy is our reading, to confirm.)*

- **Paths and gods' magic** add their own moves: a path's utility (Lanternbearers push back the Fog, Ironclads become cover) and, once claimed, the god's magic.

- **The bar:** six skills, and a button that swaps to a second page of six. The second page is free: the same gear, six more slots for any moves the character has. Buttons arc around the Attack button on phones; on PC the keys are 1 to 6 and a swap key. *(proposal: the defensive move has its own button, outside the pages.)*

- **Energy:** one energy pool for everyone and a cooldown on each skill, plus one quirk per weapon family:
  - **Guns** hold one shot or a few and must reload (and the tree can make a reload part of a dash).
  - **Heavy melee** builds momentum while it keeps hitting, and loses it when it stops.
  - **Bows** reward a longer draw.
  - **Caster foci** spend Fog shards, which raises Fog pressure, as the lore says magic does.

- **Defence: telegraphs, and the build decides.** Enemy attacks are telegraphed on the ground, coloured by kind, and each kind has a natural counter: dodge the unblockable, parry the undodgeable, step out of what is too wide for either. The kinds come from the animations we have (the Quaternius libraries; tools/assets/INVENTORY.md):

  | Kind | Animations | Natural counter |
  | --- | --- | --- |
  | Strike | jab, a single sword cut, the zombie scratch | anything: block, parry, dodge |
  | Combo | the sword combo, jab and cross | block or parry (it cannot be dodged) |
  | Heavy blow | the heavy combo, the hook | dodge (unblockable; it knocks you down) |
  | Charge | the sword dash, the shield dash | dodge or step aside (unblockable; it knocks you down) |
  | Shield bash | the shield strike | parry (it cannot be dodged; it stuns) |
  | Projectile | the overhand throw, a spell, a pistol shot | dodge, step aside or block (no parry) |
 Every defence works, but only for a character who builds toward it: perks change the rules, so with the right node an unblockable attack becomes blockable, or a dodge goes through what it normally cannot. Without those perks, a character answers each attack with its natural counter.

- **Perks that change the rules** (first set): iron guard (heavy blows and charges can be blocked), slip (a dodge also slips through combos and bashes), deflect (a melee parry also turns projectiles), steady guard (blocks cost less stamina), dash (the dodge becomes a dash), dash reload (a dodge reloads a gun).

- **PC keys in the first playable** *(placeholders; touch controls later)*: Tab targets, R attacks, 1 to 6 cast, X swaps the page, F blocks (a tap parries), C dodges.

- **Open:** the numbers; how many moves each rarity gives; clips still missing (a bow draw, two-handed weapons, a parry of its own).

### Skill tree, paths and gods

There are no classes. Every character can fight and craft completely without the Gods; who you are comes from where you grow in the skill tree. Players start as freefolk in Aldrath's outer city at the centre of the world.

| Layer       | What it gives                                                             | Where it comes from                 |
|-------------|---------------------------------------------------------------------------|-------------------------------------|
| Skills      | How you fight and craft: weapons, armour, inventions, trades              | The skill tree, earned by doing     |
| Paths       | Oaths you can swear, each with striking utility that changes how you play | Regions of the skill tree           |
| Gods' magic | A mysterious bonus that shapes both combat and crafting                   | Being claimed by a god              |
| Relics      | Reverse-engineered devices of old that any adventurer can use             | Found, bought or crafted, like gear |

**Paths.** Every character can enter every path, but progress is slow and limited: in the base game a character has enough skill points to finish one path and maybe half of another. Working names: Tinker, Technomancer, Ironclad, Fogstalker, Sapper, Lanternbearer, Beastbinder, Warpwalker. Proposed utility examples: Tinkers deploy inventions anywhere; Technomancers move their mind into a machine; Ironclads become cover; Fogstalkers endure thick Fog; Sappers blast open shortcuts; Lanternbearers push back the Fog around their group; Beastbinders bond with a creature; Warpwalkers set warp anchors.

**Gods.** Being claimed by a god does not decide your role; it decides which magic you can take. Magic is mysterious and a bonus, not a tool for everyday use.

**Entering a path.** Each path begins with a starter quest. Paths carry no vows.

**Relics.**

- **Warp bag:** the inventory. Easily reproduced, so every adventurer has one. It holds a limited amount at first and grows as it is upgraded.

- **Warp bracelet:** found later; opens a personal warp space. This is where players build their homes and bases, invite friends, and later host guild members.

**Building in the open world.** Some open-world areas are buildable, for camps at dungeon entrances and outposts at the frontier. These are never permanent: regular world events, such as monsters attacking settlements or dungeon entrances leaking creatures, can kill everyone there and let the monsters destroy what players built. This keeps the world from filling with clutter and gives defending a camp real stakes. Anything a player wants to keep belongs in their warp space, which events cannot reach.

**Open:** none for now.

- **One big tree.** Paths and crafts are regions of the tree. Nodes grant stats, armour proficiencies, movement moves, path moves and modifiers to the moves weapons give (see *Moves, the bar and defence*).

- **Hybrid builds.** Walking the tree toward a neighbouring craft unlocks its abilities and armor, so a Tinkerer can path into plate, or a Smith into gadgets.

- **Wear everything, eventually.** Enough points let any build use every armor tier. Balance is tuned later; this is the intent, not final numbers.

- **Respecs** cost resources, not real money, so groups can rebalance roles.

| Armor tier                                                               | Arrives in      | Crafts nearest to it        | Trade-offs                                              |
|--------------------------------------------------------------------------|-----------------|-----------------------------|---------------------------------------------------------|
| Light (cloth, leather, single mechanical pieces)                         | Rope and timber | All                         | Fast, quiet, low protection                             |
| Medium (reinforced leather, one mechanical arm or shoulder)              | Gear and water  | Warden, Tinkerer, Herbalist | Balanced; asymmetric builds start here                  |
| Heavy (brass and leather, powered back slot such as a jetpack or boiler) | Steam           | Smith, Warden               | Strong but needs fuel for powered parts                 |
| Plate (full metal shell, exposed mechanical joints)                      | Steam           | Smith                       | Highest armor, slow, loud, hot                          |
| Rig (a powered suit you climb into)                                      | Arcane engine   | Tinkerer, Millwright        | An invention, not armor: its own body, fuel and repairs |

Armor tiers follow the tech eras, because brass suits and firearms need foundries and boilers the group builds first.

## Inventions

Inventions are assembled from four kinds of parts, so a small set of parts produces hundreds of machines without hand-made art or data for each.

| Slot      | Examples                                                      | What it decides                            |
|-----------|---------------------------------------------------------------|--------------------------------------------|
| Frame     | Wooden stand, iron tripod, cart, wall mount, backpack harness | Where it goes and whether it moves         |
| Mechanism | Lever, spring, gear train, crank, piston                      | How it acts: once, repeating or continuous |
| Power     | Hand crank, water, wind, steam, relic core                    | How long it runs and what it needs         |
| Payload   | Bolt launcher, saw blade, bellows, lantern, net, hook         | What it actually does                      |

Examples: a wall mount, spring and bolt launcher make a crossbow turret. A cart, gear train, water power and saw blade make an automatic sawmill. A backpack harness, spring and hook make a grappling hook.

**Discovery:** schematics found in ruins reveal some combinations. Others are found by experimenting at a workbench, and the game records each new invention with the name of the player who found it first.

**Quality:** part material (wood, bronze, iron, steel) and the builder's skill set durability and strength.

### Tech eras

1.  **Rope and timber:** hand tools, palisades, snares, hand-cranked devices.

2.  **Gear and water:** waterwheels, cranes, crossbow turrets, the first conveyors.

3.  **Steam:** boilers, steam hammers, rail carts to outposts, diving suits for flooded ruins.

4.  **Arcane engine:** relic cores power the strongest machines, and every one draws the Fog toward the settlement.

## The Fog

The Fog is the world's pressure system: it grows with distance, time and magic use, and players push it back with machines and wardens.

**What feeds it**

- Distance from Aldrath and the gods: thinnest in Aldrath's heartland and around each god's city, thicker and more dangerous toward the far coasts and the Sundering at the world's edge. It weakens life itself there: poorer harvests, sicklier herds, harder winters.

- Night and storms: surges roll in and press against walls.

- Magic: each spell and running arcane engine adds to a settlement-wide Fog pressure value, which raises surge strength and frequency.

**What it does**

- Corrupts animals into Fog-touched creatures, stronger and stranger the deeper you go.

- Corrupts people slowly. Long exposure gives a corruption meter that needs an Herbalist's remedy, and untreated it becomes a lasting affliction.

- Hides the map and blocks travel until cleared.

**How players fight it**

- Fog lanterns and warding pylons (inventions) hold clear zones around outposts and roads.

- Wardens can push the edge back during expeditions.

- Clearing a ruin's heart removes Fog from that region permanently, which is the main milestone of territory progress.

**Night and lanterns.** At night the Fog strengthens and monsters grow stronger, by an amount that depends on the region: mild near the gods' cities, brutal near the Sundering. Players need lanterns to feel safe. Every adventurer carries one; its light pushes the Fog back a little and weakens monsters inside it. Lanternbearers' lanterns light the whole group and reach farther. Open: lantern fuel, and lantern upgrades.

**The choice it creates:** magic is a shortcut with a cost. A group can rush with runes and arcane engines, but its home will face much harder nights.

## World generation

Terrain and biomes are generated from a seed, but places, regions and cities are authored to fit the game's lore. The server stores the authored places plus what players change; clients generate the rest locally.

**Generated versus authored:** the generator supplies the ground: terrain shape, biomes, vegetation, rocks and minor ruins. Everything with a name is authored: regions, cities, landmarks, roads, ship routes and dungeons, placed and designed according to the lore. Authored places are laid onto the generated land, which is shaped around them (flattened for a city, carved for a river crossing, raised for a sea cliff).

- **Chunks.** The world is split into 32 × 32 tile chunks generated on demand as players approach. Every client generates the same chunk from the seed and chunk coordinates.

- **Terrain.** Layered noise for height, moisture and temperature produces biomes. Rivers trace downhill from mountains, which matters because waterwheels need them.

- **Biomes by region, danger by distance.** Each homeland has its own climate (see Geography): cold in the north, hot in the south, temperate in the east, volcanic in the west, forested in the west of the main continent. Danger and the Fog rise with distance from Aldrath: lowest in its heartland, rising toward each region's far coast, highest in the Sundering. Noise bends the bands so they feel natural.

- **Ruins.** Placed by a second seeded pass, built from room templates assembled by rules (towers, vaults, aqueduct segments, villas). Loot tables depend on biome and ruin type, and ruins respawn their lesser loot over time so the world doesn't run dry.

- **Settlers and encounters.** Survivor camps, traders and hostile groups are placed by seed but tracked by the server once players meet them.

- **Changes.** A placed wall, a felled tree, or a cleared ruin is stored as an edit against the generated chunk. The world on disk is the seed plus a list of edits per chunk.

**Determinism rule:** all generation uses a seeded random generator and integer or fixed-step math, never `Math.random()`, so every device produces exactly the same world.

**World size:** about 20 km across, similar to Valheim, bounded by an impassable wall of Fog at the edge. Only the area around each player is ever built or simulated, so size does not cost performance. Because players can travel up to 10 km from the center, the client uses a floating origin, re-centring the world on the player every few kilometres, to avoid jitter from limited graphics precision.

### Cities

Cities must feel like cities: hundreds of buildings across 500 m to 1 km, not a village of twenty houses. Windhelm and Solitude are style references: dense, vertical, and built into dramatic geography.

- **The gods' cities:** Aldrath's outer city, by far the greatest city of the third age and the trade hub where all players meet, and each people's hometown, smaller and harder-pressed the farther it lies from Aldrath, each with its god and a warp at its heart: Hollin's Cross (the starter port), Skarvhold, Solmere, Ashforge, Qaraseth and Dun Brannoch (working names; see the lore). Launch can begin with Aldrath's outer city and one neighbouring domain, opening the others in later updates.

- **Ruined cities of the old empire:** huge, Fog-filled and half-collapsed exploration zones, with persistent dungeons under their towers.

- **The shattered capital:** the largest city, and the endgame.

**What makes them feel big:** districts with their own character (smiths' quarter, market, docks, temple, slums), buildings of three or four floors, towers, bridges and walkable walls, a skyline visible from far away, and crowds of traders, guards and townsfolk.

**How they stay light:**

| Technique                                   | Purpose                                                                                          |
|---------------------------------------------|--------------------------------------------------------------------------------------------------|
| Generated layout with hand-placed landmarks | Roads, plots and buildings from rules and a modular kit; gates, markets and keeps placed by hand |
| Modular buildings merged into single meshes | Hundreds of buildings at low draw cost                                                           |
| Distance levels of detail                   | Simplified distant buildings; the skyline still reads from kilometres away                       |
| Narrow streets and walls block the view     | Only a slice of the city is drawn at once                                                        |
| Interiors only where they matter            | Shops, inns, guild halls and quest locations open; most houses stay closed                       |
| Ambient crowds near the player only         | Background townsfolk are cheap; important NPCs are always simulated                              |

### Geography

The land must feel real at scale: mountains that feel like mountains, seas that feel like seas.

**World layout (follows the lore).** Continents and isles, like World of Warcraft's, 20 km across in all, with natural coastlines (old cliffs and chasms still show where Erde tore apart):

- **The main continent** holds Aldrath's heartland at its centre: the outer city, by far the biggest city, and Hollin's Cross, the starter port two kilometres south, where ship routes leave. The Redwold's forested hills (the Ruadhan) lie in its west, and Farhallow, the village where the game begins, on its far coast.
- **The other homelands:** the Rimeholds on the northern continent (fjords, glaciers, high peaks, a mountain spine with Animari ruins), the Sere's deserts on the southern continent, the Aurelan Isles in the east and the volcanic Slag Isles in the west.
- **Life weakens with distance from Aldrath:** thinner harvests, sicklier herds, shorter seasons and thicker Fog toward the world's edge, so the hometowns are smaller and specialised, and food flows outward while ores, furs, timber, spices and relics flow inward. Each people fares differently (see the lore's table of hometowns).
- **The Sundering** lies beyond the outer coasts: no man's land where the Fog thickens into the wall at the world's edge. The Last Bastion faces it from the north, and the Forsaken landed on the southern continent's far coast.

A first sketch from the lore is in `docs/references/world-sketch-v2.png`; placements the lore marks as proposals are still open.

**Mountains**

- Peaks of roughly 500 to 800 m above the sea, in ranges with ridges, passes, cliffs and valleys.

- A snow line, colder nights and harsher weather with altitude.

- Steep slopes that take real effort, cliff paths, and inventions such as grappling hooks for climbing.

- Distant terrain drawn in simplified form so peaks stay on the horizon kilometres away.

**Oceans and seas**

- Rolling waves, colour shifting from shallows to deep water, shore foam and a true horizon.

- Storms, deep water that can drown you, and creatures beneath.

### Ships

Ships travel like the boats in World of Warcraft: they really sail.

- Scheduled ships sail real routes between ports in a few minutes, with the coast passing by.

- Players walk the deck, talk and fight on board; jumping overboard means swimming.

- The server sails the ship, so everyone aboard sees the same voyage.

- Later: player-built boats from Millwrights and Tinkerers.

**Tech notes:** terrain detail by distance (near terrain detailed, far terrain simplified), an ocean surface with moving waves, and ships as moving platforms that carry players with them.

### Beyond the Fog (post-launch expansion)

Location expansions come after launch. The first priority is a playable game with a playable world. One planned expansion: past the Fog wall at the edge of the world lie endless generated Fog realms, fractured lands each built from a seed, for deep expeditions, rare materials and the pride of reaching far-out realms. The core island stays the authored heart of the game.

## Dungeons

The world has two kinds of dungeon: persistent dungeons fixed in the open world and shared by everyone, and Breaches that open temporarily and are private to the group that enters.

|               | Persistent dungeons                                                                                                 | Breaches                                       |
|---------------|---------------------------------------------------------------------------------------------------------------------|------------------------------------------------|
| Where         | Fixed places: under major ruins, the broken tower, old mines and vaults                                             | Open anywhere near heavy Fog, then vanish      |
| Layout        | Generated once from the world seed, then hand-tuned; the same for everyone                                          | Generated fresh from room templates every time |
| Who is inside | Shared: anyone on the server can enter, and groups can meet                                                         | Private instance for the group that entered    |
| What persists | Opened doors, levers, shortcuts, cleared floors (enemies return on a timer), outposts players build at the entrance | Nothing after it closes                        |
| Purpose       | Long-term goals, deep multi-floor delves, landmarks worth returning to                                              | Quick sessions, fresh loot, Fog pushback       |

### Persistent dungeons

- Each region has 1 to 3, placed by the world generator at its biggest ruins, so they become known landmarks for the group.

- Several floors deep, getting harder with depth. Deeper floors unlock with inventions (a crank lift, a diving suit for flooded levels).

- Progress is shared and permanent: a shortcut one player opens stays open for everyone, and the group can build a camp at a dungeon's mouth.

- Floors are cleared, then slowly retaken by the Fog: enemies and lesser loot return over a few days, while boss relics are one-time finds.

- The broken tower near camp is the first persistent dungeon and the natural tutorial.

**Scope:** these reuse the Breach room pieces and enemy set, plus saving dungeon state on the server. They belong in M4 alongside Breaches.

### Breaches

Breaches are temporary, generated dungeons that open in the overworld when the Fog swells, inspired by Albion Online's randomized dungeons.

The overworld stays persistent and shared. Breaches are private instances for the group that enters, generated fresh each time and reset afterward, so loot never runs out.

| Feature  | How it works                                                                                                                                                |
|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Spawning | Breaches open near Fog-heavy areas and stay open for a few hours of real time or until cleared. The settlement's lookout tower reveals them on the map.     |
| Tiers    | The Fog glow shows the tier: grey, green, violet, gold. Higher tiers mean tougher Fog-touched enemies and better relics.                                    |
| Layout   | Hand-made room templates of the old empire (archive, forge hall, flooded cistern, rune chamber, vault) stitched together by rules, ending in a boss chamber |
| Size     | Small Breaches for 1 to 2 players, large ones for 3 to 6                                                                                                    |
| Maps     | Schematic fragments can point to a specific vault and open it on demand                                                                                     |
| Collapse | When the timer runs out the Breach starts to collapse. Get out in time or lose what you carry.                                                              |

**Fogwright twists**

- Casting magic inside a Breach raises its danger live, so the magic-versus-machines choice matters underground too.

- Inventions open alternate routes: a grappling hook reaches a high ledge, and a crank lift raises a flooded gate.

- Clearing a gold Breach pushes the Fog back in that region for a while, so dungeons feed overworld progress.

- Co-op at launch. PvP comes later; rival groups invading a Breach is a natural first mode, and rival scavenger NPCs can fill that role until then.

**Scope:** an entrance spawn system, a room-stitching generator, instance servers, groups and a starting set of 15 to 25 room templates. Room templates are small layouts of code-built pieces, so download size barely changes.

## Survival and settlers

Survival is detailed enough to create stories but simple enough to read at a glance on a phone.

**Player needs:** hunger, warmth, rest and Fog corruption. Each has a clear meter and slows you down before it harms you.

**Wounds:** injuries are tracked per body area (head, torso, arms, legs). Each wound has a type (cut, bruise, fracture, bite, burn) with its own treatment: bandage, splint, stitches or antidote. An untreated wound can turn infected. A broken leg slows you, and a hurt arm weakens attacks and crafting.

**Death:** you drop your carried items where you fall and wake at the settlement. Your gear stays in the world for friends to recover. A hardcore server option makes death permanent for that character.

**Settlers**

- Recruited from survivor camps or rescued in ruins.

- Each has 2 or 3 traits (brave, greedy, night owl, ex-runecrafter) plus needs and a mood.

- They work assigned jobs such as farming, hauling or guard duty, and can fill a missing craft at a low level.

- They form relationships and grudges with each other and with players, which shape their mood and loyalty.

**Events** fire from a director that watches the settlement's wealth, defenses and Fog pressure:

- Threats: Fog surges, raider bands, Fog-touched beasts, a sick settler starting an outbreak.

- Opportunities: traders, refugees asking to join, a ruin exposed by a landslide.

- Weather: storms, cold snaps, droughts that slow waterwheels.

While everyone is offline, the server keeps simulating at a reduced level so there is news on return, but it never kills settlers or destroys the base without players there to respond.

## Art and audio

The look is simple low-poly 3D, built mostly in code, so buildings feel grand and worn gear shows on the character while the game stays light. Prototype 1 ([Fogwright Prototype](https://claude.ai/artifact/UdQogHruyFvnyrzd4UwbkK)) shows the style.

**Visual style**

- An angled third-person camera that players can rotate and zoom; walls fade when they block the view.

- Flat-shaded low-poly models. Terrain, trees, rocks and ruins are generated from palettes and shape rules, not modeled one by one.

- Characters are shaped from two shared base bodies and dressed by the equipment system, so gear fits and moves seamlessly on every people (see Character pipeline and Equipment). The world stays generated in code.

- Inventions are drawn by assembling their parts in 3D, so a new combination needs no new art.

- Buildings use grid snapping with fixed floor heights, so multi-floor halls and towers are possible without free-placement complexity.

- Muted natural colors. The Fog is real distance fog that thickens and turns violet farther from camp, and is the main source of atmosphere.

- Day and night lighting with warm lantern and forge light, which helps sell the settlement as a safe place.

### Architecture

Architecture is diverse because of each people's culture and its level of technology. The reference set shows the range: chunky, hand-painted timber houses with overhanging upper floors, curved slate or clay-tile roofs, crooked chimneys and lanterns; workshops with boilers, copper pipes, gears and cranes bolted onto their sides; tall stacked buildings that grow upward with towers, balconies and tanks; steep A-frame halls with carved, riveted beams; and, in the greatest cities, glass-and-iron arcades on dark, rain-slick streets.

| People               | Style direction (proposal)                                                                                                                                                                                                                                                                              |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Wayfolk and Aurelans | Timber-framed houses, jettied upper floors, tiled roofs, flower boxes; small boilers and pipes added on                                                                                                                                                                                                 |
| Hrimfolk             | Steep A-frame longhalls of dark timber with carved, riveted beams, horn and antler ornaments                                                                                                                                                                                                            |
| Ferrin               | Stone and iron, heavy and squat, furnaces, chimneys, gears and pipework everywhere                                                                                                                                                                                                                      |
| Zarhim               | Sandstone with flat roofs, arches, awnings and courtyards                                                                                                                                                                                                                                               |
| Ruadhan              | Round timber halls and hill forts woven into the forest                                                                                                                                                                                                                                                 |
| Ilvari               | Elegant, glass-and-brass workshops with blue accents and arcane machinery                                                                                                                                                                                                                               |
| Aldrath's outer city | Western European castle walls, round towers and gatehouse; urban Victorian housing (brick and stone rowhouses, bay windows, steep or mansard roofs, chimneys, wrought-iron balconies); medieval cobblestone streets; very light steampunk accents such as gas lamps, clocks, the odd pipe or steam vent |

Technology level shows on the buildings: frontier villages are mostly timber and stone with a few machines; great cities are layered with pipes, boilers, cranes and glass. The current prototype uses painted facades per style as placeholders; full modular building kits come in the art pass.

**Your direction for the cities:** Western European castles for the walls, a more urban Victorian style for the housing, medieval stone streets, and only very light steampunk imagery. The walls read as far older than the city that grew inside them.

### Voxel buildings and interiors

These were chosen on 2026-11-28 for the voxel art direction, which is on the `voxel` branch. For voxel art they supersede the
person and door metrics in `docs/research/skyrim-scenes.md` (a 1.8 m person, 1.2 x 2.4 m doors). The realistic bodies keep theirs.

**Interiors (chosen): Skyrim-level, under a mixed plan.**

- Ground-level buildings are true-size and seamless in the open world: you open the door and walk in, with no loading screen.
- Spaces bigger than their shell (deep cellars, delves, great halls) go below ground, or behind a gate into their own instance.
- The Farhallow prologue is a private instance, because the Fog takes the village for every new player. Afterwards the ruin is
  part of the open world.
- Indoors the camera's zoom is capped to the room, and the upper floors and roof are cut away while you are under them.
- Doors remember whether they are open. Furniture is fixed for now.

**Sizes (chosen), for the 1.6 m stylized people and the WoW-style camera:**

| Metric | Size | In 10 cm voxels |
| --- | --- | --- |
| Building module (wall bay, floor tile) | 2 x 2 m | 20 x 20 |
| Standard door | 2.2 m tall x 1.4 m wide (some doors are larger: gates, halls, barns) | 22 x 14 |
| Wall thickness | 0.3 m | 3 |
| Window, sill to head | 0.9 to 1.9 m | 10 tall |
| Storey, houses and upper floors | 3.0 m floor to floor | 30 |
| Storey, inn taprooms and halls | 4.4 m floor to floor (22 even stair risers) | 44 |
| Stair | 0.2 m rise, 0.3 m tread, 1.4 m wide | 2 x 3, 14 wide |
| Narrowest path or corridor | 1.6 m | 16 |
| Plinth over the ground | 0.5 m (one ground-kit step) | 5 |

**The building kit.** Fogwright's own voxel pieces, generated as `.vox` files by a script, are assembled on the 2 m grid
and merged into one mesh per material per floor, with box collision. A building stays under about 25,000 triangles and
8 draw calls, with at most 2 lights per room, so a browser build can still draw a whole village. The inn (the Gull &
Lantern, 16 x 12 m) is built first, as the test of walking in with the camera. The plan is
[Fogwright voxel building kit: plan (inn first)](https://claude.ai/artifact/SCRmEZaBvNDowucFbip9Rt).

### Character pipeline

Characters are voxel models in the approved stylized look: a big head, a short broad body with no neck, thick arms
with big fists, short sturdy legs, flat colours with a darker and a lighter tone. Every character, player or NPC, is
generated from its people, its sex and its sliders, so any item fits any character and nothing clips or floats.
The handoff details are in `docs/voxel-characters.md` on the voxel branches.

- **Voxels:** 2.5 cm for the body and gear; the head is a finer part at 1.25 cm, the same size with four times the
  detail on the face. Each body part is its own named model (head, torso, upper and lower arms, hands, upper and lower
  legs, feet), pivoting at its joint; animation adds to a relaxed rest pose.
- **Generated, not modelled:** `tools/voxel/make_character.py` builds every people and both sexes from a few numbers
  (leg, torso and arm lengths, torso width and depth, limb thickness), so builds differ in bulk as well as height. All
  of them fit the standard door (about 2.2 x 1.4 m): the Hrimfolk tallest at 1.6 m, the Ferrin short and the broadest.
- **Women:** narrower shoulders, full hips, a defined waist, a bust, slimmer arms, smaller hands and feet, narrower
  heads with a softer jaw and lashes, and legs as long as the men's.
- **Faces carved and painted:** eyes with lid, iris, pupil and catch-light set in sockets under the brow; a shaped nose
  with nostrils; lips and mouth corners. Expressions (stern, grim, calm, a smile) come from the brows' tilt and the
  mouth's corners. Marks are voxels too: Hrimfolk knotwork, Ilvari ink, Ferrin soot and burns, Penitent scars.
- **Colours:** within real reflectance (pale skin no brighter than about 60%), so nothing flares under the sun.
- **Base body in underwear:** the base body wears undyed wool drawers (and a breast band for women) with bare feet,
  as the creator shows it, every mark visible. The starting clothes are a layer, like any equipment.
- **Budget:** about 2,600 to 4,200 triangles for a dressed character and 4,000 to 7,000 in full armour, after merging
  same-coloured faces; one material for everything (vertex colours).

### Equipment

Equipment works like World of Warcraft's: every piece shows on the character, some is painted onto the body and some is built around it, and a fixed layering order makes pieces from different sets combine cleanly. A character wears two layers: a **wardrobe** of everyday clothes that is only for looks, and **gear** over it that carries the stats. The more special slots unlock as you progress.

**Wardrobe (looks only).** Shirt, lower (trousers, breeches, skirts and layered skirts), socks (stockings, leg warmers) and shoes. Wardrobe pieces are collected: crafted, bought, found and given as quest rewards. A character with no gear still looks dressed in their own everyday clothes, and an NPC's wardrobe gives them character while their gear shows their job. Earrings are wardrobe too.

**Gear slots (stats)**

| Slot | Item types | Available |
| --- | --- | --- |
| Head | Hats, hoods, caps, helmets | From the start |
| Eyes | Goggles, monocles, visors, eyepatches | From the start |
| Mouth | Respirators, Fog masks, scarves, pipes | From the start |
| Shoulders (left and right) | Pads, pauldrons, vial-pauldrons; an item is a pair or a single side, and two different singles can be mixed | Unlocked with progress |
| Arms (left and right) | Armguards, armbands, tool sleeves | From the start |
| Chest | Waistcoats, corsets, jerkins, gambesons, mail, brigandines | From the start |
| Coat | Long coats, greatcoats, trench coats, robes, tabards | From the start |
| Wrists | Bracers | From the start |
| Hands | Gloves, gauntlets | From the start |
| Waist | Belts, tool belts, belt stacks, sashes; each belt has sockets (hips and back) for pouches, tools, weapons and, later, relics | From the start; sockets unlock with progress |
| Legs | Light (reinforced trousers, chaps) to heavy (greaves, plate legs, armoured skirts) | From the start |
| Feet | Boots; they replace wardrobe shoes | From the start |
| Back | Utility items: jetpack, boiler, glider frame, canister pack, Fog lantern, packs, quivers, cloaks, back arms | Skill-gated: what you can wear depends on your skills |
| Trinkets | Two rings and a necklace; not shown on the character for now | From the start |
| Main and off hand | Weapons and tools, held or carried on the body | From the start |
| Rig | A powered suit you climb into; it replaces the body rather than being worn | Arcane engine era |

**Items that fill more than one slot**, like a two-handed weapon taking both hands:

- **Heavy armour and plate** are split like WoW's: a chest piece and a legs piece. The chest piece fills chest and coat; plate covers the wardrobe completely. Heavy chests come in versions with a built-in tabard or coat skirt, since nothing goes over them. Plate skirts and tassets come from the legs piece or from a belt (a war belt with tassets), as WoW's belts and leggings carry the hip plates.
- **Robes** sit in the coat slot and hide the legs; the legs slot still counts for stats.
- **Full helms** fill head, eyes and mouth and are the strongest (as in Ragnarok Online); others fill head and eyes, or head alone.
- **Mechanical arms** always come as a pair: they fill the shoulders, arms, wrists and hands on both sides and replace the gloves. Whether one arm or both look mechanical is a cosmetic choice of the item. The heaviest, the colossus arms, go over any chest piece (see *How it's made*).
- **The canister gauntlet** fills hands and wrists. **A cowl mantle** fills head and shoulders.

**Covering and layering.** Each gear item either *replaces* what is under it (reinforced trousers take the wardrobe lower's place, boots take the shoes, heavy armour takes the shirt) or *overlays* it (chaps, greaves and tassets go over trousers or a skirt; waistcoats and corsets over the shirt). The order from the inside out is fixed: skin, wardrobe, chest, coat, belt, shoulders, back. A slot blocked by another item shows greyed out, linked to the item that blocks it. Robes and long coats drop the boot tops beneath them, and headgear removes the hair it covers.

**Straps and beards.** Harnesses, cross straps and bandoliers are not items: they appear only as part of a piece of armour, as cosmetic detail. Beards and braids show over the chest only with select gear (open collars, some breastplates); other gear covers them, and a full helm covers the beard completely.

**Weapons on the body.** Weapons are carried where it makes sense for the weapon: daggers at the hip, boot or small of the back; one-handed swords, axes, maces and hammers at the hip; pistols in a thigh or hip holster; two-handed weapons, polearms and bows across the back; rifles and crossbows slung from the shoulder; shields on the back or forearm. Hip weapons hang from the belt's sockets. When a back utility item takes the back, two-handers move to a hip sling or clip onto the item if it has mounts (a jetpack with rifle clips), and casters keep their staff in hand.

**Rarity shows on the item.** Common gear is plain cloth and simple stitching; uncommon adds contrast trim and brass buttons; rare adds tooled leather, rivets and small brass fittings; epic adds working parts (gauges, small pipes, faintly glowing vials); legendary glows and moves.

**Sets and makers.** Each craft has its own set look for now, with unique set looks later:

| Craft | Silhouette | Materials and details | Signature piece |
| --- | --- | --- | --- |
| Tinkerer | Waistcoat, rolled sleeves, tool belt | Brass fittings, goggles, small gauges, coloured glass | Canister gauntlet or canister pack |
| Millwright | Sturdy work clothes, apron, heavy gloves | Canvas, rope, wooden toggles, cogs as buttons | Rope coil on the shoulder, toolbox on the back |
| Smith | Leather apron, a short sleeve, heavy boots | Scorched leather, rivets, chain | One big gauntlet, a hammer on the belt |
| Runecrafter | Long coat or robe, high collar | Dark wool, etched symbols, glowing relic cores | Vial-pauldrons with tubes to the back |
| Herbalist | Layered skirt or wrap, satchels, rolled sleeves | Linen, dried herbs, glass phials, cork | A belt stack of pouches and jars |
| Warden | Trench or hooded coat, cape | Waxed leather, fur trim, buckled straps | A lantern on the belt, a cowl mantle |

Crafted items show who made them: a small stamped sigil in a fixed place on each item (a buckle, a collar tab, a pauldron rim), the craft's own finishing style (a Tinkerer's boots get brass eyelets, a Smith's get iron toe caps) and a visible flourish on master work. Sigils are earned: from your settlement, a guild, the god who claims you, and great deeds. There are no items limited to one people for now.

**Later:** dyes as items, restyling gear to look like other gear (transmog), and Fog wear on clothing.

**How it's made (voxels)**

- **Items are recipes, not models.** Each item is a short program (`tools/voxel/make_equipment.py`) that reads a
  body's measurements (shoulders, waist, hips, limb boxes, the head's box) and builds itself to fit it. One item fits
  every people and both sexes, the Ferrin's short limbs and the Ilvari's long ones alike. It is written per body as a
  layer file.
- **Covering pieces replace the body part under them**, the way WoW swaps body sections for armour-shaped ones
  (its geosets): a breastplate replaces the torso, boots the feet and shins, gauntlets the hands. Nothing is left
  underneath to poke through.
- **Rigid pieces ride a part:** pauldrons on the upper arms, a helm or goggles on the head, a boiler or a lantern on
  the torso. They move with it.
- **A fixed order from the inside out** decides which layer wins where two would take the same part: the body, the
  wardrobe, legs and feet, chest, coat, arms, belt, shoulders, back, head, eyes and mouth, then a rig.
- **Items hide what they cover:** a full helm hides the hair and the hanging beard and braid; a hood tucks the hair in.
- **Slots are checked:** two items may not take the same slot. `godot/scripts/voxel/equipment.gd` dresses a character
  from `data/equipment.json` (each item's slots, order and what it hides) and refuses a clash.

**The armour tiers as built** (`godot/tests/voxel_equipment.tscn` shows each on five very different bodies):

| Tier | Set | Pieces |
| --- | --- | --- |
| Light | Warden's leathers | A hood and capelet, a laced jerkin with a fur collar, bracers, tall boots, a belt with a pouch and a lantern |
| Medium | Tinkerer's brigandine | Goggles, a riveted brigandine, one mechanical pauldron with a cog (asymmetric), the canister gauntlet, a tool belt |
| Heavy | Steamwright's brass | A respirator, a brass cuirass with a pressure gauge, pauldrons on fur with a gauge and a pipe, a boiler with a glowing firebox and a chimney, greaves with glowing knee cores, work gloves |
| Plate | Ironclad | A full helm with an eye slit and a crest, a ridged breastplate with a fauld, plate arms with exposed pistons, gauntlets, plate legs with tassets, sabatons |
| Rig | Arcane engine rig | An exosuit you climb into: it replaces the body with its frame and lifts the pilot 25 cm; a glowing arcane core, an engine with exhaust stacks, a roll cage, clamp hands; still inside the door (at most 2.0 x 1.25 m) |

**Back arms.** A mechanical arm worn in the back slot, mounted on a pack or on an iron spine down the back. It rises
over the left shoulder, high above the head, and arcs forward, its joints cogs with glowing cores, so the weapon hand
stays free. It gives one action of its own, like any back item: a **utility** arm grabs, carries and repairs at arm's
length (a claw, here holding a potion); a **combat** arm strikes alongside your weapon (a guarded saw), or, at its
largest, two arms spread from a tall mast and each fires a triple-barrelled cannon; a **defence** arm swings a
shield before your chest so your hands stay on the weapon, two-handers included. Two-handers then hang at the hip,
as with any back item.

**Colossus gauntlets** are the colossus arms from the elbow down only: huge plated forearms and fists in blued steel
and brass, a glowing gem at the wrist, filling the wrist and hand slots and leaving the upper arms and sleeves seen.

**Mechanical arms over any tier.** The heaviest cybernetics are arms, not suits: the colossus arms (huge bronze arms
with domed shoulders, a round port, red hoses, corrugated cables to the neck and brass-capped fists hanging low) fill
the shoulder, arm, wrist and hand slots and go over anything, even light leathers or a uniform coat. The contrast of a
light outfit with the heaviest arms is a look we want.

**Visual language:** big forms (helmets, shoulder plates, tanks, boilers) are built; rivets, seams and wear are voxels of a darker or lighter tone. Glowing accents (furnace cores, gauges, lenses) mark powered gear and read clearly at a distance. Each armour tier gets a clearly different silhouette, from a slim coat to a full plate shell.

**NPCs.** Not every NPC needs full detail, but every one needs personality.

| Tier | Who | Detail |
| --- | --- | --- |
| Hero | Players, named and quest NPCs | The full system, unique pieces, detailed faces |
| Townsfolk | Guards, merchants, smiths, innkeepers | Outfits generated from their people, trade and wealth, plus one signature item |
| Crowd | Background passers-by | Painted outfits, at most one built piece, a cheaper body at a distance |

Clothes carry personality: wealth shows in fabric, trim and jewellery; tidiness in wear, dirt and patches; trade in aprons, tools and uniforms; and each people has its own style palette (Hrimfolk furs and lacing, Aurelan tabards and doublets, Ferrin leather aprons and brass, Zarhim layered wraps, Ilvari fitted coats over blue ink, Ruadhan cloaks and woven patterns, Wayfolk a mix of everything). A signature item, such as a red scarf, a pipe or a mended hat, keeps faces in the crowd memorable.

**The NPC system.** Every townsperson is generated from a seed, so a crowd costs nothing to store and the same person returns the same way:

- **Who:** a people, a sex, a height and build within that people's range, their colouring, and a name in their people's own sound (Norse for the Hrimfolk, Persian for the Zarhim, Gaelic for the Ruadhan, and so on).
- **Trade:** one of twelve so far (city watch, smith, merchant, farmer, porter, sailor, noble, priest, scholar, innkeeper, beggar, hunter). A trade sets the outfit choices for each slot, the belt and what hangs from it, and a range of wealth, wear and dirt.
- **Their people's style:** each people swaps in its own pieces and colours (Ferrin aprons, Zarhim wraps and head wraps, Hrimfolk fur, Ilvari coats, Ruadhan plaid). The city watch wears Aldrath's red and gold.
- **Wealth:** poorer folk wear hessian and worn linen with patches, frayed hems and dirt; the rich wear velvet and jacquard.
- **A signature item:** a hat (sometimes feathered), a scarf, an earring or a walking stick, so faces in a crowd stay memorable.
- **Temperament:** cheerful, gruff, nervous, proud, weary, curious, stern or dreamy. It sets their posture, how often and how far they glance about, the tilt of their head, how they sway and how fast they walk, and the lines they say.

**Colours, not textures.** Every voxel carries one colour from a small palette, baked into the mesh: there is no texture sheet. Rarity, dyes and wear are palette swaps and patterns of voxels; recolouring a tunic is swapping one entry.

**References:** the armour reference set covers all five tiers. Designs are original, inspired by the references, never copies of another artist's work.

**Audio**

- Sound effects generated in code with the Web Audio API (hammering, gears, crossbow twang, footsteps).

- Ambient layers by biome, plus a low drone that rises when the Fog is close.

- A few short music tracks as compressed files, streamed after load so they don't slow startup.

**Readability rules:** every interactable object has a distinct silhouette, and the game must be playable on a 6-inch phone screen.

## Tech plan

The game is a web app first, wrapped for desktop and mobile stores later, with a target under 10 MB to install and smooth on a mid-range phone.

**Client**

- TypeScript, rendering with three.js (WebGL, about 170 KB compressed). No game engine and no physics engine; collision uses simple shapes against the terrain height.

- Runs in any modern browser. It is installable as a Progressive Web App (PWA) for an app-like icon and offline asset caching.

- Wrapped with Tauri for Windows, Mac and Linux (installers of a few MB, using the system's web view) and Capacitor for iOS and Android.

- Input works with mouse and keyboard, touch (virtual stick, drag to look, pinch to zoom), and gamepad.

- Phone performance: low poly counts, Fog to limit draw distance, chunk streaming, and a quality setting.

- Simple 3D is estimated to add about 30 to 50% development time over 2D, almost all of it in building, art and animation.

**Server**

- Node.js or Bun with WebSockets, one process per world, authoritative over all game state.

- Breaches run as separate short-lived instances, started when a group enters and shut down after everyone leaves.

- SQLite for persistence: the world seed, chunk edits, players, settlers and invention discoveries. Breaches store nothing after they close.

- Shared TypeScript code between client and server for world generation and game rules.

- Hosting: a \$5 to \$10 per month VPS per server for one group. Friends can also self-host.

**Netcode**

- The server simulates at 20 ticks per second and sends only what changed nearby.

- Clients predict their own movement and smoothly interpolate everyone else.

- The world itself is never sent; only chunk edits and entity state are.

**Size and performance budgets**

| Item                                        | Budget        |
|---------------------------------------------|---------------|
| First load in the browser (code + core art) | Under 3 MB    |
| Desktop installer (Tauri)                   | Under 10 MB   |
| Mobile app (Capacitor)                      | Under 25 MB   |
| Network per player while playing            | Under 10 KB/s |
| Frame rate on a mid-range phone             | 60 fps        |
| Players per server                          | 16            |

## Milestones

The first playable build (M1) is two friends building a shelter together in a generated world over the internet; everything after it is layered on top.

*[Diagram: roadmap · 5 milestones and their gates. It lives in the online doc and does not export to Markdown.]*

Each milestone ends with a gate the group plays, and the next one only starts once that gate feels right. Prototype v0.2 now covers M0 and the single-player half of M1: harvesting, crafting, grid building and day-night survival, saved as edits on the seed. Next is the multiplayer server.

**M1 first playable: in scope**

- Seeded, chunked world with three biomes (meadow, forest, marsh) and rivers

- 2 to 8 players connect by link, see and chat with each other

- Walk, chop trees, mine rocks, carry resources

- Place and remove walls, floors and a campfire

- Everything saved on the server and still there next session

- Mouse and keyboard only

**Out of scope until later:** combat, the Fog, crafts, inventions, settlers, dungeons, hand-made characters, touch controls and store builds.

## Open questions and risks

**Open questions**

- Is Fogwright the name, or a working title?

- Does grid-based building feel good on a phone in 3D? Prototype 2 answers this.

- Write the world lore: regions, cities, factions and history, which the authored places are built from.

- Which PvP comes first once co-op is solid: rival groups in a Breach, or raiding other settlements?

- When do firearms arrive: with steam, or only with arcane engines?

- Can a character be in several worlds or servers, or is each world self-contained?

- Should magic be fully playable as a main path, or mostly a risky late-game tool?

- A separate private repository for the game, since this one holds Valheim files and must stay private.

**Risks**

| Risk               | Why it matters                                               | Mitigation                                                                |
|--------------------|--------------------------------------------------------------|---------------------------------------------------------------------------|
| Scope creep        | Six crafts, settlers, the Fog and inventions add up to a lot | Ship each milestone as something playable, cut features before polish     |
| Generated sameness | Noise-based worlds get repetitive                            | Hand-authored ruin rooms and landmarks mixed into generation              |
| Netcode feel       | Laggy movement ruins combat                                  | Client-side prediction from M1, tested over real internet early           |
| Touch controls     | Building and inventing UIs are hard on phones                | Design UI for touch from M2, not as a late port                           |
| Offline simulation | Players may come back to bad news                            | Offline mode never destroys or kills, only creates news and small changes |
| Hosting and ops    | Someone has to run the server                                | One-command self-host plus a cheap VPS guide                              |
