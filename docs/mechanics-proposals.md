# Mechanics proposals: systems that follow the lore

2026-11-28 · drafted for Doc Tan

Game mechanics built from the lore in [lore.md](lore.md) and [lore-proposals.md](lore-proposals.md), and fitted to what
[design.md](design.md) already decided (tab-target combat, weapons give moves, one skill tree, paths, relics, the warp
space). Everything here is a **proposal**. Numbers are first guesses, to tune in play.

## Quick decisions

| # | Proposal | Why |
| --- | --- | --- |
| 1 | **Freeholds are the "settlement"**: the group's shared base is a frontier village they retake from the Fog; the warp space stays the private, safe home | Joins design.md's settlement loop to the lore's warp space |
| 2 | **Runecrafter becomes Relicwright**: the craft that reverse-engineers relics and makes relic cores; spells come only from gods | The lore bans magic for anyone unclaimed |
| 3 | **Gods are world state**: each god has a server-wide Grace value that players raise and lower, and that changes everyone's magic and the colour of that god's land | Makes the persistent co-op server matter |
| 4 | **Warps carry the chosen, not cargo**: the warp bag has a weight limit, so bulk goods move by ship and cart | Keeps ships and roads important, as lore.md asks |
| 5 | **Greying replaces "Fog corruption"** with five visible stages | Readable on a phone, and ties to the lore's Greyed |
| 6 | **Retaking Farhallow** is the first big Freehold goal | Gives the prologue a payoff |

## Things in design.md that clash with the lore

Found while reading; each needs a yes or no.

| Where | design.md says | Lore says | Proposal |
| --- | --- | --- | --- |
| Overview and Setting | "an arcane empire fell 300 years ago", "using inventions instead of spells", "the players are the first generation to resettle" | Three ages, gods, chosen players who do use magic | Rewrite Setting from the lore: 312 TA, three centuries after Merrith's sacrifice; "inventions instead of spells" becomes "inventions first, grace as the rare gift" |
| Crafts | Six crafts, one is Runecrafter (spells and enchantments) | Spells only from being claimed | Runecrafter becomes **Relicwright** (below) |
| Skill tree | "Players start as freefolk in Aldrath's outer city" | Players start in Farhallow and land at Hollin's Cross | Change to Farhallow and Hollin's Cross |
| Core loop and Survival | A home settlement with settlers and walls | Homes and bases live in the warp space, which events cannot reach | Both: the warp space is home, the Freehold is the shared frontier base (below) |
| The Fog | "Each spell adds to a settlement-wide Fog pressure" | Same idea | Keep, but measure pressure per region and per Freehold, not per home |
| Ruins and dungeons | "Ruins of the old empire" | Ruins of three ages and of the Animari and Sennari | Ruin types by people and age (below) |

## Being claimed

How a player gets a god, and what it gives.

1. **Merrith's thread.** From the prologue on, every player feels the pull: a faint golden glint on the compass and a
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

**One god at a time.** A player can change god by **apostasy**: going to a new god's site and passing their trial. The
old god's magic is locked (the points are refunded into the new region) and that god's people trust you less for a
while. It costs a quest and some reputation, not money.

**Vael (hidden).** Vael cannot be sought at the start. After Act III he can claim players who find him in a broken warp,
which opens Warpwalker-style magic properly.

**Galeth (falls).** Players claimed by Galeth become **Orphaned** when he falls: they keep their magic but its strength
drops slowly over weeks unless they join the Vigil's march, or change god. If Galeth is freed later (lore proposal),
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
| **Khesra**, Survival | Thirst and heat drain more slowly | **Shed** (cure one affliction or wound), **Mirage** (leave a decoy and slip away), **Adapt** (resist the last damage type that hit you) | Find water anywhere; Greying slows |
| **Brannoch**, Bonds | Tamed beasts and mounts take less damage | **Bond** (link to an ally or beast: share healing), **Call** (summon your bonded beast to you), **Kinship** (calm a wild animal) | Better prices with traders who know you; tame more easily |
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
- **What lowers it:** time (a slow fade, always), surges that break through in their region, freeholds of their region
  falling, and story events.
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
the Sundering), raised by night, storms, the Shard moon and magic use, and lowered by lanterns, lamps, pylons and cleared
ruins.

| Density | Name | What happens |
| --- | --- | --- |
| 0 | Clear | Gods' circles and lit streets; no night strength for enemies |
| 1 | Haze | Normal wilds by day |
| 2 | Mist | Night in the wilds; Fogtouched appear |
| 3 | Fog | The far coasts; Greying starts without a lantern; the map stops filling in |
| 4 | Deep Fog | Breaches open; Wrought roam; lanterns are needed to see |
| 5 | The Wall | The Sundering; only the best lanterns and Fogstalkers last long |

### Greying

A meter with five stages (lore-proposals.md). It rises in Fog of density 3 and up without light, from Fog creatures'
hits, and from carrying lots of Fog shards. It falls slowly in clear places and fast with remedies and grace.

| Stage | Sign on the character | Effect |
| --- | --- | --- |
| 1 Chill | Breath fogs, pale lips | Warmth drains faster |
| 2 Veins | Grey veins on hands and neck | Healing weaker; some townsfolk avoid you |
| 3 Eyes | Grey eyes | Stamina regenerates slower; Censors stop you; you see Echoes |
| 4 The tune | A song only you hear (a sound cue) | Random brief control loss in thick Fog; the Fog's creatures ignore you sometimes (a strange perk) |
| 5 The turn | Collapse | You fall and wake at your seat, Greying reset to stage 2, a lasting **scar** (a small permanent minus until treated by a god's quest) |

Players never truly turn. Settlers and NPCs can.

### Lanterns

Every adventurer carries a lantern (design.md). Proposals for the open parts:

- **Slot:** the lantern hangs from the belt (its own slot, always lit at night unless doused). A Lanternbearer can carry
  it in the off hand for a much larger light.
- **Fuel:** **lamp oil** (fish oil or tallow, cheap, from any trader or a Herbalist), burns for about one in-game night.
  **Vigil wicks** (bought from chapter houses) burn longer and push harder. A **Fog-shard cell** (Relicwright) burns
  longest but adds a little Fog pressure, the usual trade-off.
- **Upgrades:** lens (wider light), cowl (no light seen by enemies: stealth), coil (pushes Fog harder), cage (survives
  falls and swimming). Made by Tinkerers and Smiths.
- **Out of fuel:** density counts as one step higher around you, and Greying starts.

### Clearing the Fog

- Lanterns and pusher lamps hold Fog back for as long as they burn.
- **Warding pylons** (an invention: pylon frame, gear train, a power source, a pusher-coil payload) hold a clear circle
  around a Freehold or a road for as long as they are powered.
- **Clearing a ruin's heart** (the boss of a persistent dungeon) lowers a region's base density by one step for good,
  raises that region's god's Grace, and colour comes back there: the main long-term progress on a server.

## Freeholds: the group's frontier home

The shared base in design.md, placed in the lore. A **freehold** is a frontier village outside any god's circle (lore
proposals). Many are falling. Players can retake a fallen one, or found a new one on open ground, as a group.

- **Where:** fixed sites on the map (a ruined freehold, an empty valley, a headland), so they are part of the authored
  world. Farhallow is one, and the first goal: **go back and retake the village you fled**.
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

## Taming: Zarhim and Ruadhan ways

Two ways to get a beast, and both are open to everyone, but each people starts ahead in its own.

| | **Field taming** (the Zarhim way) | **Breeding** (the Ruadhan way) |
| --- | --- | --- |
| How | Find a wild beast, wear it down without hurting it badly, then **endure** with it: share water, follow it, survive a night beside it | Buy or tame a pair, keep them in a stable (warp space or Freehold), breed them; foals and pups are raised from birth |
| Result | A wild-born beast with random traits, often strong in harsh places | Predictable traits that improve over generations; can be sold |
| Speed | Hours of play for one beast | Days of real time for a line |
| Beasts (examples) | Sand striders, dune lizards, carrion kites (scouts), desert cats | Horses, war hounds, great elk, draught oxen |

**Mounts** (design.md plans them): horses first, then larger beasts. Fogtouched beasts can never be tamed, except by
Oriel's chosen with the Ride move, for a while.

## Trade, cargo and the economy

- **Prices follow the lore's gradient:** food is cheap near Aldrath and dear at the edges; ores, furs, timber, spices
  and relics are cheap where they come from and dear at the centre. Each port's trader shows a few goods "in demand".
- **Cargo:** goods have weight. The warp bag holds personal gear and a little more, so **bulk trade goods** (crates,
  barrels, bales) must be carried in a cart, on a mount, or shipped. Warps refuse cargo crates. This makes the ships and
  roads in design.md matter, and gives non-fighting players a real job.
- **Trade runs** as quests and as free play: buy at one port, ship to another. Ships can be attacked at sea under the
  Shard.
- **Regional coin** (lore-proposals.md): trading in a people's own money gives better prices; money changers take a cut.
- **Player trade** (design.md: gear is the build, so gear is traded): a market board in each city, and stalls in the
  Aldrath market for players later.

## Reputation

Players have standing with each **people** (eight), and with some **factions**:

| Faction | Who | What standing gives |
| --- | --- | --- |
| The Ordinal and Censure | Aldrath's church | Writs, pardons, the Ordinal's sealed archives; falls if you are caught with illegal magic or seen with cogwitches |
| The Lantern Vigil | Galeth's order | Vigil wicks, coil schematics, the march into the Fog; splits after Galeth falls |
| The Archive of Seraveth | The Ilvari | Lore, relic schematics, languages; hunted by the Censure |
| The Waylodges | Hollin's priests | Free beds, rumours (quest leads), help for the Penitent |
| Cogwitch circles | Outlaw technomancers | Technomancy schematics, Animari relics; illegal |
| Salvage companies | Rival scavengers of ruins | Contracts for relics; they compete with players in Breaches (design.md's rival NPCs) |

Standing with one often costs standing with another: the Censure and the cogwitches, the Ordinal and the Archive.

## Death and coming back

Following design.md (drop carried items, wake at home, friends can recover them), with lore added:

- **In the prologue:** Merrith's touch lifts you (lore.md).
- **After:** you wake at your **seat** (the god's city where you were claimed) or the last **waystone** you prayed at,
  whichever is nearer. Your warp bag's contents drop where you fell in a **cache** that glows faintly gold for your group
  (Merrith's thread marking it).
- **Dying in Deep Fog (density 4 and up):** the Fog remembers you. An **Echo of you** stands over your cache, fighting
  with a copy of your moves. Your group (or you) must put it down to get your things back. Hard, memorable, and a reason
  to go into the Fog together.
- **Hardcore option:** as design.md, death is permanent; the character becomes an Echo that stays in the world for others
  to find.

## Time and the moons

- **Days:** design.md's day and night, with the six-day week and twelve months of the lore proposal: one in-game day
  about an hour of real time (proposal), so a month is about 30 hours of play and a year a few months of real time.
- **Moons** (lore-proposals.md): the Hollow full lowers Fog density by one at night; the Veiled full raises magic
  strength by 10%; the Shard rising raises surge and Breach chances and keeps ships in port.
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

1. **The main story** (lore-proposals.md's acts), for the whole group.
2. **God questlines:** the claiming trial and a chain for each god, ending with something only their chosen get.
3. **Path starter quests** (design.md).
4. **People quests** in each hometown, raising standing.
5. **Freehold events:** refugees, raids, outbreaks, traders (the event director in design.md).
6. **Lore fragments:** inscriptions, books, Echoes; each found piece goes into the **Codex**, and finding sets of them
   gives skill points. Exploring is progress, as the lore wants ("learned slowly, through ruins, relics, writings").

## Progression, in one place

- **Skill points** come from **Renown**: quests, discoveries, Codex sets, clearing ruin hearts, holding freeholds. Not
  from killing alone.
- **Proficiency** rises by doing (design.md: crafts level by doing the work; weapons train by use).
- **Gear** brings item power and moves (weapons.md).
- **Grace** is a shared, world-level progression: the server's gods and colours are the group's history.
- The base game gives enough points for one path and half another (design.md), plus one god's region.

## Build order (proposal)

What to make first so it is playable soonest:

1. Lantern fuel and Fog density zones (the lamps already exist).
2. Greying stages 1 to 3 and the Herbalist remedy.
3. Merrith's thread on the compass and the first claiming trial (Hollin's, since Hollin's Cross is the start).
4. One god's magic region (Hollin's) and the Writ.
5. Grace for one god, driving colour in one region.
6. Retaking Farhallow as the first Freehold.
7. Everything else, region by region.
