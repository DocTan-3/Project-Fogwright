# Research: how Bethesda builds Skyrim's scenes

What Fogwright takes from The Elder Scrolls V: Skyrim. Part 1 is from Bethesda's own account (Joel Burgess and Nate
Purkeypile, "Skyrim's Modular Level Design", GDC 2013). Part 2 is what the user's reference shots of Riverwood show
(observation, not a Bethesda source). Part 3 is what Fogwright adopts.

## 1. Bethesda's method (sources)

**Scale of the work.** A 16 sq. mile overworld, 5 major cities, 37 towns, farms and villages, 300+ dungeons; 8 level
designers and 2 kit artists built "well over 400" interior cells from just 7 kits in about two and a half years. Kits are
"the primary building blocks of level design" at Bethesda.

**Fix the human metrics before any building.** A character is about 128 units ("six feet") tall; one door-frame size for
the whole game, so every kit shares doors; the narrowest walkable space is "two character widths" so two people can pass;
slopes of 30-45 degrees look best for walking characters.

**Footprints and the grid.** A kit is built on one footprint, and sub-kits use multiples of it ("a 512 room will always
tile nicely with a 256 hallway"; a 384 room "will eventually create gaps and/or overlaps"). The footprint is the full
bounds of a piece, not its walkable space, and pieces stay inside it. Designers snap to half the footprint. Floors have
real thickness, so stacked pieces never share a plane (no z-fighting).

**Test the kit before dressing it.** Proof (1-3 weeks, untextured blocks, real proportions), graybox (1-4 weeks, the
most-used sub-kit first, tested in real layouts), then build-out. Stress tests: loop a layout back on itself and see it
close; stack floors; build rooms from corner pieces and look for accidental pillars. Never fix a gap with a one-off
"patch-up" piece; fix the core piece. Finish one piece completely before making variants.

**Hiding repetition.** Players notice repeated clutter first, then repeated architecture. So the kit gives a place its
architecture and other things set its mood: unique props, lighting, enemies, and kit-bashing (mixing two kits gave an
"instant shift in tone and atmosphere"). Ambient occlusion and good lighting "go a long way to hide any awkward
intersections". Rule-bound kits "always feel like a kit"; give each kit one quirk that breaks its grid, and free-placed
pieces (walls, pillars, balconies) over standard shells break spaces up organically ("shell-based building").

**Workflow.** Artist and designer pair from the first day; pieces are instanced hundreds of times, so changes reach every
instance at once; function first, looks second; designers stay in daily contact with the art.

## 2. What the Riverwood references show (observation)

- **Every building is a real space at human scale**: houses of roughly 10 x 15-20 m with tall single storeys and lofts,
  the inn and trader larger; inside and out are one model, so the outside's proportions come from real rooms.
- **Every building rests on the ground it stands on**: a dry-stone foundation under the wall line, taller where the
  ground falls away; heavy posts carry the frame; a raised plank deck or porch along the front with steps down to the
  street. The building's footprint includes its foundation, deck, steps and roof overhang.
- **Room around every building**: 5-15 m between houses, with ground, plants, stacked wood and carts in between; the
  street is a worn track between the decks.
- **Each house tells its owner's story**: firewood under the eaves, a cart and wheel by the deck, a shop sign on a gallows
  bracket, smoke from the chimney, the mill on the river; no two houses dressed alike although they share one kit.
- **The village fits its land**: one road through it, buildings following the river and the slope, a few large houses
  rather than many small ones (about 12 buildings).

## 3. What Fogwright adopts

1. **Metrics first** (fixed, game-wide): person 1.8 m; door 1.2 x 2.4 m; narrowest path 1.6 m (two people); slopes for
   walking up to 30 degrees, steps beyond; storey 3.1 m; the 2 m kit module.
2. **Real building sizes** with interiors laid out even when closed (cottage about 8 x 12 m, street house 8 x 14 m,
   farmstead and smithy about 12 x 14 m, inn about 16 x 22 m).
3. **A building's lot** = walls + foundation + porch or deck + steps + 1 m of eaves; lots at least 4 m apart; floors
   0.5 m above the highest ground under them, foundations down to the ground, steps at any door above the ground.
4. **Kit discipline**: footprints in multiples of 2 m; real floor thickness; loop and stack tests on new building types;
   no patch-up pieces.
5. **Hide repetition with dressing, light and mixing**: every house dressed for its owner (the doodad stage), varied by
   the Wayfolk variation rules, lit and shadowed; one quirk per building type.
6. **Interiors only where play opens them**, but every shell sized as if it had one.

## Sources

- [Skyrim's Modular Approach to Level Design (Game Developer repost of the GDC 2013 talk)](https://www.gamedeveloper.com/design/skyrim-s-modular-approach-to-level-design)
- [Joel Burgess: Skyrim's Modular Level Design, GDC 2013 transcript](http://blog.joelburgess.com/2013/04/skyrims-modular-level-design-gdc-2013.html) (the site was down when checked)
- [The Level Design Book: Modular kit design](https://book.leveldesignbook.com/process/blockout/metrics/modular)
- [GDC Vault: How We Used Iterative Level Design to Ship Skyrim and Fallout 3](https://www.gdcvault.com/play/1020171/Level-Design-in-a-Day)
