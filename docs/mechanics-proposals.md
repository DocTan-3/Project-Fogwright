# Mechanics proposals: systems that follow the lore

2026-11-28 · drafted for Doc Tan

Game mechanics built from the lore in [lore.md](lore.md) and [lore-proposals.md](lore-proposals.md), and fitted to what
[design.md](design.md) already decided (action-aim combat, gear gives skills, one skill tree, paths, relics, the warp
space). Everything here is a **proposal**. Numbers are first guesses, to tune in play.

## Decisions so far (2026-11-28)

- **Decided:** the warp space is each player's private home (**player freeholds dropped for now**, see below); Runecrafter
  becomes the **Relicwright**; each god has a server-wide **Grace**; warps and the warp bag have a **weight limit that
  grows over time**; **no Fog exposure meter** on players (Fog is gated by lanterns instead); **Farhallow stays lost**;
  being claimed grants a **starting node in the one skill tree**; **players do not drop items on death**.
- **Also decided:** a one-hour day; two pools (stamina and energy); dodge and block on their own buttons; the Writ and
  Censors are lore only for now; lanterns burn easy-to-craft oil; a **Skyrim-style compass** across the top of the
  screen, where Merrith's thread shows as a gold mark; design.md rewritten to match.
- **Economy (decided):** one global market whose stock spreads between cities (local buys instant, imports take
  time); listing fee plus sales tax; NPC merchants with weaker but always-available stock; regional prices; a direct
  trade window; a later vending-stall skill node (one per player, trading districts, sells a few hours offline).
- **Combat (decided):** action aim everywhere (no tab-target); weapons, cybernetics and belt tools give skills for
  every role; the skill web unlocks extra skill choices and modifies them; soft roles with threat; no friendly fire;
  PvP opt-in only (duels, arenas); cooldowns plus pool costs; large bar with extra rows on PC, six plus the page
  switcher on mobile.
- **Summons and mounts (decided):** summons from gear and skills (drones, sentries), attack or support, last until
  destroyed, cap from nodes starting at 0; taming is for mounts only; built mounts need specialisation; mounts are
  travel only with their own moves, have their own health (knocked out on a cooldown), equip as items, tradeable.
- **Quests (decided):** personal story plus server-wide world beats; marked givers and notice boards; small choices;
  light dailies; compass marks.
- **Tank and support (decided):** taunts that bosses resist; heavy-gear base plus tank skills; self-protection and
  protecting others are separate, neighbouring node groups; no healing weapon family, heals from drones, sentries, back
  arms and belt tools, soft-targeted; throw potions at allies; buffs, cleanses, shields and revives as node clusters;
  a downed state anyone can revive.
- **Freeholds (decided):** dropped for now as a player feature, with settlers and the base event director. Homes are
  the warp space. Freeholds remain in the lore as falling frontier villages.

## Core mechanics (decided 2026-11-28)

The basics, settled first:

| System | Decision |
| --- | --- |
| **Levels** | Characters have levels with **no cap**: each level comes slower, and each gives **node points** for the one large skill tree, which is the progression. **Experience comes from everything you do**: fighting, gathering, crafting, quests, and discovering places and lore. Horizontal progression (breadth of the tree, gear, gods' magic) stays worthwhile |
| **Mobility** | Basic moves for everyone (move, sprint, jump, swim, the dodge). Advanced mobility (dash, leap, slide, climbing and the like) comes from skill-tree nodes |
| **Health** | One health bar, no wounds per body part. Bleeds, burns and stuns are short combat effects. Health comes back by **slow natural regen**, which food speeds up a lot |
| **Survival needs** | None to maintain: no hunger, warmth or rest meters. **Food gives timed buffs** (more health, stamina, regen) |
| **Fog** | No exposure meter: lantern tiers gate the deeper Fog (below) |
| **Inventory** | A **grid of stacking slots with a weight limit**; the warp bag adds slots and weight as it is upgraded |
| **Gathering** | Trees, ore and herbs are **shared** by everyone and **respawn on a timer**; felled trees stay down until they regrow |
| **Loot** | **Free for all**: whoever picks a drop up first keeps it |
| **Death** | You keep everything. You wake at your seat or last waystone, and your **equipped gear loses durability**, repaired by Smiths |
| **Crafting** | **Basics anywhere** (bandages, torches, a campfire); weapons, armour and inventions at **stations** (forge, workbench, loom) |
| **Recipes** | Basics known; the rest from ruins, trainers and experimenting. Pick a recipe, choose materials, a short timer, a queue. One refining step. Quality fixed by recipe; some recipes make higher tiers; some legendaries are craft-only. Inventions are normal recipes (no part slots). Maker's name in the tooltip |
| **Repair, salvage, stations** | Smiths repair; gear salvages to materials and Fog shards. Public stations in cities for a fee, own stations at home (warp space) |
| **Players as NPCs** | Implants are fitted by an NPC or a player with the node. Generally, skill nodes let players do NPC services in the field, so players can trade services on trust |
| **Skill web** | One Path of Exile-style web plus Albion-style mastery by use. One centre for all; pick one path and one craft at creation for a node or two each. Wedges: Combat, Crafting, Gathering, Utility, and a Magic wedge (gods) shut until claimed; Aldrath has none. Small, notable and keystone nodes, all always active. Mastery soft-gates gear tiers. Respec at an expensive NPC |

## Things in design.md that clash with the lore

Found while reading; each needs a yes or no.

| Where | design.md says | Lore says | Proposal |
| --- | --- | --- | --- |
| Overview and Setting | "an arcane empire fell 300 years ago", "using inventions instead of spells", "the players are the first generation to resettle" | Three ages, gods, chosen players who do use magic | Rewrite Setting from the lore: 312 TA, three centuries after Merrith's sacrifice; "inventions instead of spells" becomes "inventions first, grace as the rare gift" |
| Crafts | Six crafts, one is Runecrafter (spells and enchantments) | Spells only from being claimed | Runecrafter becomes **Relicwright** (below) |
| Skill tree | "Players start as freefolk in Aldrath's outer city" | Players start in Farhallow and land at Hollin's Cross | Change to Farhallow and Hollin's Cross |
| Core loop and Survival | A home settlement with settlers and walls | Homes and bases live in the warp space, which events cannot reach | The warp space is home; player freeholds dropped for now (2026-11-28) |
| The Fog | "Each spell adds to a settlement-wide Fog pressure" | Same idea | Keep, but measure pressure per region, not per home |
| Ruins and dungeons | "Ruins of the old empire" | Ruins of three ages and of the Animari and Sennari | Ruin types by people and age (below) |

## Being claimed

How a player gets a god, and what it gives.

1. **Merrith's thread.** From the prologue on, every player feels the pull: a gold mark on the top compass (decided: a
   Skyrim-style compass strip that also shows quest and place markers) and a
   hum near shrines. It points at the nearest **claiming site** they have not visited.
2. **Seek a god.** Every god has a claiming site: their seat in their hometown (Verdane:
   any of the great groves; Oriel: an Animari ruin; Vael: none that anyone knows, see below; Galeth: the Last Bastion,
   until he falls).
3. **The trial.** A quest that shows what the god values. Examples: Hrothvar asks you to stand a night on the ice without
   a fire; Maelis asks you to settle a dispute between a lord and his tenants; Seraveth asks you to bring back one thing
   that was lost; Ostrak asks you to forge a blade and then try to break it; Khesra asks you to cross a stretch of the
   Sere carrying water for someone else; Brannoch asks you to win the trust of an animal; Hollin asks you to walk a road
   end to end and be welcomed at the end of it.
4. **Claimed.** The god's magic opens as a region of the skill tree; the Ordinal issues a **Writ of Grace**; the warps
   open to you; you get a **seat** in that god's city (a free warp bind and favour with that people).

**A starting node, not a lock (decided).** Being claimed grants a starting node in the one skill tree, inside that god's
region, placed far from the other gods' regions. Every player can eventually walk the tree to other gods' magic and
unlock it too; the god who claimed you only decides where you start. There is no apostasy.

**Vael (hidden).** Vael cannot be sought at the start. After Act III he can claim players who find him in a broken warp,
which opens Warpwalker-style magic properly.

**Galeth (falls).** Players claimed by Galeth become **Orphaned** when he falls: they keep their magic but its strength
drops slowly over weeks unless they join the Vigil's march. If Galeth is freed later (lore proposal),
the Orphaned are the first to feel it.

**Aldrath** claims no one (decided 2026-11-28), so his plaza is not a claiming site.

## Gods' magic

Each god's magic is a region of the skill tree: a passive that every claimed player gets, then 5 to 8 nodes of active
moves and modifiers. The moves are quiet and strange, never fireballs. They shape both fighting and crafting.

| God | Passive (always on) | Active moves (examples) | In crafting and the world |
| --- | --- | --- | --- |
| **Hrothvar**, Endurance | Cold drains warmth more slowly | **Unbowed** (cannot be staggered or knocked down for 6 s), **Frostbreath** (a short cone that slows), **Hold the Line** (take hits meant for a nearby ally) | Temper metal tougher; sail through storms safely |
| **Maelis**, Stewardship | Food and potions last longer | **Oath** (bind an ally: you share damage taken), **Bounty** (heal over time in an area), **Keep** (a ward on a door or wall that holds) | Freehold fields yield more; buildings go up faster |
| **Seraveth**, Remembrance | Read ruin inscriptions without the language skill | **Recall** (step back to where you stood 4 s ago), **Echo** (see a fallen enemy's last moves replayed), **Mend** (restore a broken item's durability) | See Echoes of the past at ruins (lore discovery), restore relics |
| **Ostrak**, Valor | Deal more damage the lower your health | **Anvil Skin** (block takes no stamina for a while), **Ember** (weapon hits burn), **Stand Fast** (heal from damage you block) | Better forging quality; heat a forge without fuel for a time |
| **Khesra**, Survival | Thirst and heat drain more slowly | **Shed** (cure one affliction or wound), **Mirage** (leave a decoy and slip away), **Adapt** (resist the last damage type that hit you) | Find water anywhere |
| **Brannoch**, Bonds | Your mount has more health and recovers faster | **Bond** (link to an ally: share healing), **Call** (your mount comes back sooner after it is knocked out), **Kinship** (calm a wild animal) | Better prices with traders who know you; tame more easily |
| **Hollin**, the Road | Faster on roads and paths | **Stride** (a long sprint with no stamina cost), **Waystone** (recall to the last waystone you prayed at), **Welcome** (a safe camp circle: no Fog, enemies won't enter for a time) | Travel time between ports shortens; better at inns |
| **Oriel**, Understanding | See enemies' weak points (more critical hits) | **Ride** (move your mind into a beast or machine for a while), **Know** (reveal a creature's moves and weaknesses), **Wake** (start a dead Animari machine) | Technomancy: summons gather resources; repair machines |
| **Vael**, Passage (after Act III) | Fall damage greatly reduced | **Fold** (a short blink), **Door** (a two-way gate between two points for your group), **Slip** (pass through a thin wall) | Open broken Sennari warps for a time |
| **Verdane**, the Living World | Gathering plants yields more | **Rain** (a small storm that slows enemies and heals allies), **Root** (vines hold enemies), **Grow** (raise a quick barrier of thorns) | Grow crops anywhere; read the weather days ahead |
| **Galeth**, Protection (until he falls) | Your lantern's light is wider | **Ward** (a shield on an ally), **Lantern Flare** (push the Fog back hard for a while), **Stand Between** (taunt nearby enemies) | Light Vigil flames; make pusher coils |

**Every spell costs energy and feeds the Fog** (design.md): each cast adds Fog pressure to the region you are in. Magic
used inside a Freehold's walls raises that Freehold's pressure, so surges there grow harder. The quiet moves (passives,
crafting uses) add nothing.

## Grace: gods as world state

Every god has a **Grace** value from 0 to 100 on the server, shared by everyone on it.

- **What it does:** the strength of that god's magic for everyone claimed by them (from about 70% at low Grace to 115%
  at high), the size of their circle around their city, and **the colour of their land** (design.md already wants colour
  to retreat as a god fades: Grace drives that).
- **What raises it:** magic used by that god's chosen (the Return: every cast sends a little back), clearing Fog in their
  region, bringing back Greyed people of their region, finishing that god's quests, freeing captives late in the story.
- **What lowers it:** time (a slow fade, always), surges that break through in their region, and story events.
- **Aldrath** gains a little from every other god's loss. Players will not see why until the reveal; afterward the
  Grace screen shows his true value and where it comes from.
- **Never zero by accident:** a god can fall only in a story event, never because a quiet server did nothing.
- **The tension with Fog pressure:** casting raises your god's Grace and also raises Fog pressure. Magic is a gift to
  your god and a danger to your home at the same time.

## The Writ and the Censure

- A **Writ of Grace** lets a chosen use magic openly in cities. It is issued at the claiming.
- **Unlicensed magic** (cast where the Writ is not recognised, for instance by a Penitent player in some places, or by
  anyone after crossing the Censure) draws a **Censor**: guards are told, prices rise, and some quests close until it
  is settled (a fine, a quest, or a pardon).
- Censors' **sounding bells** ring near anything magical, so carrying Fog shards or relics past a Censor can get you
  searched. Smuggling is a small game of its own.
- Penitent characters start with a **Writ under watch**: allowed, but every town's Censor knows their name, and some
  traders will not deal with them at first.

## The Fog, in play

### Fog density

Each place has a density from 0 to 5, from the lore's gradient (thinnest near Aldrath and the gods' cities, thickest at
the Sundering), raised by night, storms and magic use, and lowered by lanterns, lamps, pylons and cleared
ruins.

| Density | Name | What happens |
| --- | --- | --- |
| 0 | Clear | Gods' circles and lit streets; no night strength for enemies |
| 1 | Haze | Normal wilds by day |
| 2 | Mist | Night in the wilds; Fogtouched appear |
| 3 | Fog | The far coasts; needs a lantern of tier 1 or better; the map stops filling in |
| 4 | Deep Fog | Breaches open; Wrought roam; needs a tier 2 lantern |
| 5 | The Wall | The Sundering; needs a tier 3 lantern (or a Fogstalker's) |

### Gating, not a meter (decided)

Players have **no Fog exposure meter or status**: the Fog does nothing to a player's body. Instead each density is a
gate: from density 3 up you need a lantern of high enough tier to go in at all. Without it the Fog is too thick to walk
into (the way back is always open). Better lanterns, made or bought as the game goes on, open the deeper Fog, the way
gear opens harder zones. Danger inside comes from what lives there.

**Greying stays in the lore** for NPCs and settlers: the Greyed are people the Fog took over years, never players.

### Lanterns

Every adventurer carries a lantern (design.md). Proposals for the open parts:

- **Slot:** the lantern hangs from the belt (its own slot, always lit at night unless doused). A Lanternbearer can carry
  it in the off hand for a much larger light.
- **Fuel (decided):** lanterns burn **lamp oil**, and oil is easy to craft. A **rendering still** (working name), a
  relic-made device, turns organic materials into oil: fish, fat, meat, hide, seeds, wood resin. So if you run out in
  the wilds, hunt an animal and render its meat and hide into oil. Oil is also sold cheaply everywhere. (Proposals still:
  Vigil wicks that burn longer, Fog-shard cells from Relicwrights.)
- **Upgrades (decided): tiers only.** Each tier is a new lantern you craft; there are no add-on parts.
- **Tiers:** the lantern's tier sets the deepest Fog density you can enter (see Gating).

### Clearing the Fog

- Lanterns and pusher lamps hold Fog back for as long as they burn.
- **Warding pylons** (an invention: pylon frame, gear train, a power source, a pusher-coil payload) hold a clear circle
  around a camp or a road for as long as they are powered.
- **Clearing a ruin's heart** (the boss of a persistent dungeon) lowers a region's base density by one step for good,
  raises that region's god's Grace, and colour comes back there: the main long-term progress on a server.

## Freeholds: the group's frontier home *(dropped for now, 2026-11-28)*

**Decision:** player-owned freeholds are dropped for now, along with settlers and the base event director. Homes live in
the warp space; the frontier is pushed by quests, Breaches and Grace. Freeholds stay in the lore as falling villages.
The proposal below is kept only for reference, in case they return later (for example as a guild feature).

The shared base in design.md, placed in the lore. A **freehold** is a frontier village outside any god's circle (lore
proposals). Many are falling. Players can retake a fallen one, or found a new one on open ground, as a group.

- **Where:** fixed sites on the map (a ruined freehold, an empty valley, a headland), so they are part of the authored
  world. **Farhallow stays lost (decided):** it remains a Fog-taken ruin; the group's first freehold is somewhere new.
- **What it holds:** buildings the group builds (on the voxel building kit), fields, workshops that need power (water,
  wind, steam), walls, turrets, pylons, and **settlers** (design.md: traits, moods, jobs).
- **The risk:** Freeholds are not safe. Surges at night, raids by Briarkin and Lessborn, outbreaks of Greying among
  settlers. If a Freehold falls, buildings are damaged and settlers may flee or turn; it can be retaken. (design.md's rule
  holds: while everyone is offline it never falls, only gathers news.)
- **The warp space** is where each player's own home, storage and trophies live, safe from everything. A Freehold can
  have a **warp anchor** once a Warpwalker builds one, linking it to the group's warp spaces.
- **Why bother:** a Freehold produces things nothing else does (food far from the centre, power for big inventions, a
  place for settlers), lowers Fog density around it, and every Freehold held raises the region god's Grace. Holding
  freeholds is how players push the map outward.
- **Open-world camps** (design.md's temporary camps at dungeon mouths) stay as they are: small, cheap, and lost to events.

## Crafts and the Relicwright

The six crafts stay as regions of the one skill tree, with one change:

| Craft | Change |
| --- | --- |
| Tinkerer, Millwright, Smith, Herbalist, Warden | As design.md |
| **Relicwright** (replaces Runecrafter) | Studies relics of the three ages and the lost peoples and makes copies: warp bags (and their upgrades), relic cores that power arcane-era inventions, Fog-shard cells, lantern coils, and the "enchantments" of gear, which are really small relic parts set into it. Needs the Old Concordant skill to read schematics |

Relicwright work uses no god's magic, but relic cores and shard cells raise Fog pressure where they run, as design.md
says arcane engines do.

**Languages as a skill:** Old Concordant (first age), Animari machine-script, Sennari door-signs. Learned by reading
inscriptions and books, raised by use. They open schematics, lore fragments and hidden doors. Seraveth's chosen read them
all without the skill.

## Taming (decided: one method for everyone)

Every people tames the same way; only the beasts differ by region (decided 2026-11-28). Proposal for the method: find a
wild beast, wear it down without hurting it badly, then calm it (food, patience, staying near it) until it accepts you.
Zarhim and Ruadhan start with a small bonus to taming, as the peoples known for it.

| Region | Beasts (examples) |
| --- | --- |
| The Sere (Zarhim) | Sand striders, dune lizards, carrion kites (scouts), desert cats |
| The Redwold (Ruadhan) | Horses, war hounds, great elk |
| The Rimeholds | Snow wolves, shaggy draught oxen, sea eagles |
| Aldrath's heartland | Horses, oxen, hounds |

**Taming is for mounts only** *(decided 2026-11-28)*: there are no fighting pets. Fogtouched beasts can never be
tamed, except by Oriel's chosen with the Ride move, for a while.

## Summons and mounts *(decided 2026-11-28)*

- **Summons come from gear and skills:** drones, sentries and turrets you build or deploy. They can attack or support
  (heal, shield, buff). They **last until destroyed**. The **cap starts at 0** and skill nodes raise it, so a summoner
  starts with the class that has it or builds toward it in the web.
- **Mounts** are tamed beasts, or **built mounts** that need deeper specialisation (a craft path in the web).
- **Travel only:** your own skills are off while riding. Some mounts have **their own special moves**, like Albion.
- **Mount health:** a mount has its own health. When it runs out you are dismounted and the mount is on a
  **cooldown** before you can ride again; it is not lost.
- **Equipped as an item:** the mount takes a gear slot and counts toward weight; you mount it after a short cast.
- **Tradeable:** tamed and built mounts are items, sold on the market or traded like any gear.

## Trade, cargo and the economy *(decided 2026-11-28)*

- **One global market.** Every city's market board lists the same world-wide pool of player listings. Listed stock
  slowly **spreads out** to other cities over time (list 100 potions in one city and they drift across many).
  Buying stock that is already in your city is **instant**; buying stock that sits elsewhere is an **import** that
  takes time to arrive.
- **Fees:** a small **listing fee** to post, and a **sales tax** taken when it sells. Both take coin out of the game.
- **NPC merchants** sell their **own stock**. It is weaker than player-made gear and its price follows supply and
  demand, so it can cost more, but it is **always there to buy**. Late-game player crafts are far better.
- **Regional prices** follow local supply and demand: food is cheap near Aldrath and dear at the edges; ores, furs,
  timber, spices and relics are cheap where they come from and dear at the centre.
- **Cargo (decided):** goods have weight. Warps and the warp bag have a **weight limit that grows over time**, so
  early on bulk goods (crates, barrels, bales) go by cart, mount or ship. Carrying goods yourself beats waiting on
  an import, which gives haulers and non-fighting players a real job.
- **Player to player:** a **direct trade window** for face-to-face swaps.
- **Vending stall (later, skill node):** a contraption that sets up a stall and sells for you, like a merchant.
  **One per player**, only in **trading districts**, and it keeps selling for **a few hours after you log out**,
  then packs up.
- **One coin**, the mark (decided).

## Reputation

Players have standing with each **people** (eight), and with some **factions**:

| Faction | Who | What standing gives |
| --- | --- | --- |
| The Ordinal and Censure | Aldrath's church | Writs, pardons, the Ordinal's sealed archives; falls if you are caught with illegal magic or seen with cogwitches |
| The Lantern Vigil | Galeth's order | Vigil wicks, coil schematics, the march into the Fog after Galeth falls |
| The Archive of Seraveth | The Ilvari | Lore, relic schematics, languages; hunted by the Censure |
| The Waylodges | Hollin's priests | Free beds, rumours (quest leads), help for the Penitent |
| Cogwitch circles | Outlaw technomancers | Technomancy schematics, Animari relics; illegal |
| Salvage companies | Rival scavengers of ruins | Contracts for relics; they compete with players in Breaches (design.md's rival NPCs) |

Standing with one often costs standing with another: the Censure and the cogwitches, the Ordinal and the Archive.

## Death and coming back (decided: no item drop)

- **In the prologue:** Merrith's touch lifts you (lore.md).
- **After:** you wake at your **seat** (the god's city where you were claimed) or the last **waystone** you prayed at,
  whichever is nearer, **with everything you carried**. Nothing drops. (This replaces design.md's drop rule.)
- What dying costs instead is open: a short weakness, gear durability, or nothing but the walk back.

## Time and the moons

- **Days:** design.md's day and night, with the six-day week and twelve months of the lore proposal: one in-game day
  about an hour of real time (proposal), so a month is about 30 hours of play and a year a few months of real time.
- **Moons:** looks only (decided); no effect on play.
- **The Mourning** (five days, once a year): no surges, every Merrith shrine lit, a world event where players lay
  candles and the year's Greyed who were brought back are counted for Merrith's thread (the endgame).
- **Festivals** of each god in their month: small events with their own quests and goods.

## Ruins by age and people

So ruins look different and teach the history (design.md asks for hand-made rooms and landmarks):

| Ruin | Age and people | Looks like | Inside |
| --- | --- | --- | --- |
| Concord ruins | First age, the empire | White stone, huge arches, worn statues of many gods (more than twelve) | Old Concordant inscriptions, the oldest relics |
| War ruins | Second age, all peoples | Forts, gun towers, trenches, rusted war machines | Weapons, schematics, Echoes of battles |
| Animari machine cities | Second age, Oriel's people | Metal halls built into mountains, every door a mechanism | Sleeping minds in machines that wake; technomancy |
| Sennari warp halls | First and second age, Vael's people | Rings of dark stone, doorways that open on nothing | Broken warps, Sennari door-signs, Vael's traces |
| Fallen freeholds | Third age | Villages like Farhallow, grey and quiet | Greyed villagers still living their last day; settlers to save |

## Quests, in layers

**Decided 2026-11-28:** personal story progress, with big world moments happening once for the whole server;
marked quest givers plus notice boards (mostly simple jobs, some long questlines); small choices that change rewards
and standing, not the world; light optional dailies with a small bonus; compass marks and a map area for the tracked
quest.

1. **The main story** (lore-proposals.md's acts), for the whole group.
2. **God questlines:** the claiming trial and a chain for each god, ending with something only their chosen get.
3. **Path starter quests** (design.md).
4. **People quests** in each hometown, raising standing.
5. ~~Freehold events~~ (dropped with freeholds for now).
6. **Lore fragments:** inscriptions, books, Echoes; each found piece goes into the **Codex**, and finding sets of them
   gives skill points. Exploring is progress, as the lore wants ("learned slowly, through ruins, relics, writings").

## Progression, in one place

- **Levels** give node points for the skill tree (decided).
- **Proficiency** rises by doing (design.md: crafts level by doing the work; weapons train by use).
- **Gear** brings item power and moves (weapons.md).
- **Grace** is a shared, world-level progression: the server's gods and colours are the group's history.
- **No level cap**; experience from everything you do (decided).

## Build order (proposal)

What to make first so it is playable soonest:

1. Lantern fuel and Fog density zones (the lamps already exist).
2. Lantern tiers as gates into Fog densities 3 to 5.
3. Merrith's thread on the compass and the first claiming trial (Hollin's, since Hollin's Cross is the start).
4. One god's magic region (Hollin's) and the Writ.
5. Grace for one god, driving colour in one region.
6. Everything else, region by region.
