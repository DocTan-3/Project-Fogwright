---
name: city-planning
description: Plan and dress a Fogwright town, village, city district or other settlement in Godot, in six stages - who it is for (people, culture, architecture), lore, logistics, building layout, paths, doodads - and check every path and placement makes sense. Use whenever building or changing a settlement, placing buildings or props, or reviewing a settlement's layout.
---

# City planning for Fogwright

Settlements are built in six stages, each finished and shown to the user before the next: **who it is for, lore,
logistics, building layout, paths, doodads.** Then the checks, a look, and the performance budget. Every object placed must earn its place.

## 0. Who it is for: people, culture, architecture

Before anything else, settle whose place this is. A people's culture decides how its towns are arranged, and its
architecture decides the floorplans; a Zarhim oasis town and a Hrimfolk fjord hold are planned differently from the
ground up. Each people has a **culture sheet** in the docs (`docs/peoples/<people>.md`), written once with the user and
reused for every settlement of theirs. If the sheet is missing or thin, write it (with the user's choices) first.

A culture sheet covers:

- **How they live together:** family and household (nuclear, clan, extended), who holds power (elders, a lord, a guild,
  priests), what they value and what they hide.
- **How their towns are arranged:** what stands at the centre (hall, temple, market, well, the lord's house), whether
  houses face the street or turn inward round courtyards, the street pattern (organic, ring, grid, terraces), walls and
  gates, where the dead are buried, what is sacred and where it goes, how they use water, wind and slope.
- **How rich and poor show:** in size, height, material, distance from the centre, walls, decoration.
- **Their architecture:** building types and their floorplans (rooms, sizes, storeys, where the hearth is, where animals
  sleep, where the door is and what it opens onto), materials, roofs, windows, ornament and colour, how they build on
  slopes. Sketch a plan of each common building type; these become the kit pieces and layouts in 3D.
- **What a stranger notices first:** the two or three things that make one of their towns unmistakable.

For a mixed settlement (a port, Aldrath's outer city), say whose culture shapes which part: the common building style,
and where other peoples' families built in their own way.

## 1. Lore

Write it down before anything is drawn (`docs/settlements/<name>.md` in the docs):

- **Who lives here** (peoples, how many), **how they live** (trades, what they make, eat, sell and buy), **how rich or poor**
  they are and how unevenly, and **how close to Aldrath** (farther means harder lives and more muted colours: lore.md,
  "Life and the Fog").
- **Its history:** why it was founded here, what changed, who holds power, a few named people and a story or two that
  side quests can grow from.
- **What it is for in the game:** which quest beats happen here, where the player arrives and leaves.
- **The climate and the wind:** where the prevailing wind comes from (smoke, smells and noise drift downwind).

## 2. Logistics

From the lore, work out what the place needs and where each thing must be, *before* placing a single building. Write a
short table: each building or facility, why it is where it is, what it needs next to it.

- **Trades sit with what they need:** the smithy with its forge and furnace, charcoal and a water trough for quenching,
  on a road for customers and deliveries; a mill on running water or the wind; the bakery near the granary and the
  ovens' fuel; the fishmonger, smokehouse, net-menders and boatwright at the harbour; the tannery and the slaughterhouse
  downwind and downstream, at the edge; stables and the farrier at the gates.
- **Smoke, smell and noise go downwind and to the edge:** forges, smokehouses, tanneries, dye works, middens.
- **Rich and poor:** the well-off live upwind, uphill, near the temple and the square, on paved streets, with their own
  wells, gardens, walls and better views; the poor live downwind, downhill, by the smelly trades, the docks and the walls,
  in smaller, crowded, patched houses, sharing a well. More amenities where the money is: fountains, benches, lamps,
  paving, planters, shops.
- **Gathering places at the centre or the gates:** taverns and inns stand by the gates (travellers arrive there) or on the
  main square (locals gather there) - never out at the edge. The market sits where the main roads cross. The well or
  fountain is in the square. The temple or shrine takes a prominent spot (high ground or the end of a main street).
- **Defence and supply:** the gate on the main road with a guard post; the granary and stores near the gate and fields;
  water within reach of every house.
- **Growth:** the old core is dense and central; newer, poorer houses spread outward along the roads.

## 3. Building layout

Draw a top-down plan (tools/map/farhallow_plan.py is the pattern): north up, metres, terrain contours, and every building
from the logistics table with its size, angle and use. Show it to the user before building in 3D.

- **Terrain that makes sense:** high and low ground, water and shore, and why. Elevation only where real geography puts it.
- **Buildings face the street they serve** (unless the people's culture turns them inward): the front runs along the
  road, the door opens onto it, and houses on one street share a setback, so streets read as streets. A corner building
  faces the more important street. The angles come from the roads, which bend with the ground, so not everything faces
  a cardinal direction. Only workshops with yards, sheds, barns and the like face their yard or the shore instead; the
  well-off may sit back behind a front garden, still facing the road with a gate onto it.
- **Dense in the core, looser outward,** sized to their use (a tavern is big, a hen house small), with room left for
  the paths and yards between them. Buildings that sit off the main roads face the lane that will reach them, so draw
  those lanes as dashed lines on the layout.
- **Edges:** walls or palisades with gates where roads enter; fields and woods around; the place should feel enclosed.
- **Check the plan's boundaries by script, not by eye:** every building, garden and yard (forge, woodpile, pens) against
  every other, every road and lane (with its width), the square, walls and palisades, fields and plots, the sea, beach
  and sea walls, and piers; trees kept off all of them. The plan script prints each clash; it must print none before the
  plan goes to the user. Special places (a shrine at the end of a road, a shed on the shore) are allowed by name only.
- **Gameplay marks:** where each quest beat happens, with room to fight, flee and gather.

## 4. Paths

Only now draw the paths, along the routes people take between the places in the logistics table (desire lines): branching
and widening naturally, never a grid, main roads wider than lanes, each ending at a door, a gate or another path. Every
path gets a purpose and passes the path checks (below).

Like the layout, the paths are checked by the plan script, not by eye: every door reaches a path without crossing
another building, plot or yard; every path starts and ends on another path, at a door or at a named place; no path goes
unused.

## 5. Doodads

Last, the props and plants of daily life, each with a purpose that follows from the lore and logistics: the smith's anvil,
quench barrel and coal heap at the smithy; nets and barrels at the harbour; benches, lamps and planters where the
well-off live; carts and crates at the market; flowers and grass only where nothing is built or walked. Every placement
passes the placement checks (below).

## Building to the plan (3D)

- Terrain is a real mesh from a height function; never place buildings or props on flat planes floating over slopes.
- Each building stands on its own level terrace cut into the slope, with a foundation where the ground falls away.
- The kit (scripts/village_kit.gd) snaps pieces to a 2 m grid *inside* a building only; the building itself takes any angle.
- Houses must be closed: matching wall pieces all round, corner posts or quoins at every corner, a roof that fits (the
  kit's roofs only come in some sizes - check both orientations, and resize the building to a size with a roof if neither
  fits), and gable ends closing the roof.
- Paths are curves laid on the terrain with worn edges, not tiles.

## Reference images: remake them faithfully

When the user sends a reference (a house, a floor plan, a town map, a prop), the job is to bring **that** design into
Fogwright's art direction - not to make something that only resembles it, and never to drop parts until it is easy.

1. **Take it apart first, in writing:** count the walls, storeys, bays, windows and doors per wall; note roof shape and
   pitch, chimneys, dormers, balconies, overhangs, stairs, materials per part, trims, signs, and every prop. For a plan or
   map: every building (with its size and angle), every path and where it goes, terrain features, walls, water, landmarks.
2. **Rebuild all of it,** part for part, at the same proportions, in our kit, palette and lighting. Where the kit lacks a
   part, build or model it - do not leave it out.
3. **Compare** a render against the reference side by side and list what still differs; keep going until the list is
   empty or the user accepts a difference. Say plainly which parts, if any, could not be matched yet and why.

## Check every path

Every path is in `PATHS` with a width and a **purpose** ("the well west to the tavern's door"). The checker tests:

1. **Does it lead somewhere?** Both ends must arrive at a destination - a door, the plaza, a gate, the pier's head, a
   field's gate - or join another path (`PATH-END`).
2. **Does it hit a building anywhere but an entrance?** A path may touch a building only at its door; otherwise move the
   building or the path (`PATH-WALL`).
3. **Does it have to exist?** It needs a purpose: who walks it, from where to where (`PATH-WHY`). Paths come from where
   people go, not decoration.
4. **Is it redundant?** Two paths running side by side for a long stretch, or joining the same two places, merge into one
   (`PATH-DUP`).

## Check every placement

Every object goes through `put()` with a **role** and a **purpose**, and the checker (`check_plan()` on the level, run
with `godot --path godot res://tests/check.tscn`) must report **0 problems** before anything is committed. For each
object, ask:

1. **Does it need to be there?** Every clutter prop needs a purpose that a villager would recognise ("the tavern's ale
   barrels against its east wall", "the hatchet in the chopping block: the first weapon"). No purpose, no prop. Props
   gather where people work and live (doorsteps, walls, yards, stalls, docks), never scattered at random.
2. **Is it on ground that makes sense?** Flora (grass, flowers, ferns, bushes, crops) grows only on open ground of its
   kind: grass and flowers on grass, crops in fields and plots, ferns in the woods - never on paths, plazas, terraces,
   cobbles, stone, sand or inside buildings. `scatter()` drops points on the wrong ground; give it the ground kinds allowed.
   Clutter stands on solid ground (not in the sea, not floating, not sunk), against walls rather than in open space.
3. **Does it block a path or an entrance?** Nothing stands in a walkway or within a doorway's clear zone. Things go
   beside paths and beside doors, never in front of them.
4. **Is every building complete?** The checker flags any building without a roof.

The checker reports: `PATH-END`, `PATH-WALL`, `PATH-WHY`, `PATH-DUP` (paths, above), `WHY` (no purpose), `GROUND` (wrong ground), `PATH` (in a walkway), `DOOR` (blocks a doorway),
`INSIDE` (inside a building), `ROOF` (no roof). Fix each by moving or removing the object - never by weakening the check.

## Look at it

Render it (`res://tests/look.tscn -- out=<prefix> "at=x,y,dist,yaw,pitch;..."` takes plan coordinates) from street level
at several places, plus a top-down view, and look for what the checker cannot see: odd silhouettes, open gaps, repeated
buildings, empty or over-cluttered spots, things that don't read at a glance. Show the user the renders.

## Performance budget

Batch repeated small things (grass, flowers, trees) with MultiMesh; bake static shadows (no live shadows on the world);
keep a settlement within the frame budget in docs/design.md. Measure the FPS counter after each step.
