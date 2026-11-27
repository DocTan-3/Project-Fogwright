---
name: city-planning
description: Plan and dress a Fogwright town, village, city district or other settlement in Godot - from lore and a top-down plan to terrain, buildings, paths and props - and check every placement makes sense. Use whenever building or changing a settlement, placing buildings or props, or reviewing a settlement's layout.
---

# City planning for Fogwright

Settlements are built from a plan, not improvised, and every object placed must earn its place. Follow these steps in
order; do not skip the checks.

## 1. Lore first

- Who lives here, what they do for a living, how rich or poor they are, and how close they are to Aldrath (farther means
  more muted colours and harder lives: docs/lore.md, "Life and the Fog").
- What the place is *for* in the game: which quest beats happen here, where the player arrives and leaves.
- The palette for the district (scripts/palette.gd: Hearth, Fog Coast, Iron & Ember; `fog` mutes colours with distance).

## 2. Plan on paper before building

Draw a top-down plan (tools/map/farhallow_plan.py is the pattern): north up, metres, and show it to the user before
building in 3D. It must have:

- **Terrain that makes sense:** where the ground is high and low, water and shore, and why (a harbour is low, a shrine or
  keep on the rise). Elevation only where real geography would put it.
- **Paths where people walk:** desire lines between the places people go (gate, well or square, tavern, harbour, fields,
  workshops), branching and widening naturally, never a grid. Main roads wider than lanes.
- **Buildings at varied angles,** clustered densely along the paths with their doors facing them, and sized to what they
  are (a tavern is big; a hen house small). Not everything faces a cardinal direction.
- **Edges:** walls or palisades with gates where roads enter; fields and woods around; the place should feel enclosed.
- **Gameplay marks:** where each quest beat happens, with room to fight, flee and gather.

## 3. Build to the plan

- Terrain is a real mesh from a height function; never place buildings or props on flat planes floating over slopes.
- Each building stands on its own level terrace cut into the slope, with a foundation where the ground falls away.
- The kit (scripts/village_kit.gd) snaps pieces to a 2 m grid *inside* a building only; the building itself takes any angle.
- Houses must be closed: matching wall pieces all round (plain walls that match the window and door walls), corner posts
  or quoins at every corner, a roof that fits (the kit's roofs only come in some sizes - check both orientations, and
  resize the building to a size with a roof if neither fits), and gable ends closing the roof.
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

## 4. Check every path

Every path is in `PATHS` with a width and a **purpose** ("the well west to the tavern's door"). The checker tests:

1. **Does it lead somewhere?** Both ends must arrive at a destination - a door, the plaza, a gate, the pier's head, a
   field's gate - or join another path (`PATH-END`).
2. **Does it hit a building anywhere but an entrance?** A path may touch a building only at its door; otherwise move the
   building or the path (`PATH-WALL`).
3. **Does it have to exist?** It needs a purpose: who walks it, from where to where (`PATH-WHY`). Paths come from where
   people go, not decoration.
4. **Is it redundant?** Two paths running side by side for a long stretch, or joining the same two places, merge into one
   (`PATH-DUP`).

## 5. Check every placement

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

## 6. Look at it

Render it (`res://tests/look.tscn -- out=<prefix> "at=x,y,dist,yaw,pitch;..."` takes plan coordinates) from street level
at several places, plus a top-down view, and look for what the checker cannot see: odd silhouettes, open gaps, repeated
buildings, empty or over-cluttered spots, things that don't read at a glance. Show the user the renders.

## 7. Performance budget

Batch repeated small things (grass, flowers, trees) with MultiMesh; bake static shadows (no live shadows on the world);
keep a settlement within the frame budget in docs/design.md. Measure the FPS counter after each step.
