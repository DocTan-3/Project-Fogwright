# Character system

How a player's character is made, following the lore (lore.md, "The peoples"). Choices made with the user are marked
**(chosen)**; the rest are proposals. Written to be renderer-independent: it applies to the voxel character system (the
approved Hrimfolk test character), whose details are added when that work is merged.

## The rules that hold everything together

- **One skeleton for everyone, one doorway for everyone (chosen).** Every people and both sexes share one rig, and every
  character fits the game's standard door (1.2 x 2.4 m, docs/research/skyrim-scenes.md): no one is taller than about
  2.0 m nor wider than about 0.7 m at the shoulders. So doors, corridors, seats, animations and above all **equipment**
  work for every character without per-people versions.
- **Peoples differ in build, not only height (chosen):** each people has its own proportions (shoulder width, limb
  thickness, torso depth, head size, neck), within limits small enough that one set of gear fits all by deforming with
  the body. Gear is made once on the base body and follows the body's shape (and, for the Ferrin, its shorter limbs).
- **Both sexes for every people, with the same choices (chosen).**

## The peoples

| People | Height (avg, range) | Build | Skin | Hair | Eyes | Signature (creator options) |
| --- | --- | --- | --- | --- | --- | --- |
| **Hrimfolk** | 1.90 m (1.80-1.98) | heavy-boned, broad chest and shoulders, thick neck and wrists | pale, wind-burnt cheeks | flax-blond to white and ash | pale blue, grey | braids with metal rings, braided beards; blue-black knotwork tattoos on arms and neck |
| **Ruadhan** | 1.85 m (1.75-1.95) | tall, rangy, long-limbed, lean muscle | fair, freckled | red to copper | green | (none yet: plaid comes from clothes) |
| **Aurelans** | 1.75 m (1.65-1.85) | balanced, upright, well-fed | olive to warm tan | dark brown | hazel, brown | (none yet: heraldry comes from clothes) |
| **Zarhim** | 1.75 m (1.65-1.85) | lean, wiry, light-framed | deep brown to dark | black | amber, dark | (none yet: wraps come from clothes) |
| **Ilvari** | 1.85 m (1.75-1.95) | slender, long limbs and neck, narrow shoulders | cool pale to grey-blue | silver to black | light, clear | blue ink lines on face and hands, faintly glowing in the Fog (lore) |
| **Ferrin** | 1.35 m (1.25-1.45) | short, very broad, thick hands, forearms and shoulders, short legs | ruddy, soot-darkened | dark brown to black, greying early | dark | forge-burn scars and soot; thick beards and braided sideburns; braided crowns |
| **Wayfolk** | 1.75 m (1.60-1.90) | any, from all peoples | any | any | any | the mix: any one feature from any people |
| **Penitent** (freed Forsaken) | 1.75 m (1.65-1.85) | gaunt, sinewy | ashen, faint grey veins | any, often cropped | any, sometimes pale-rimmed | healed scourge scars on back and arms; often hooded |

Colouring (chosen) as in the table; the creator offers each people's own range, and the Wayfolk get all of them.

## Making a character (chosen: presets plus a few sliders)

1. **People** (8), then **sex**.
2. **Face preset:** about 6 hand-made faces per people and sex, each true to that people.
3. **A few sliders**, all clamped to the people's range: height, build (slim to heavy), face width, jaw, brow, nose,
   age.
4. **Colours:** skin, hair, eyes, from the people's range.
5. **Hair and beard:** styles per people (Hrimfolk braids, Ferrin beards and crowns, Zarhim close crops and long ties,
   Ilvari long and sleek...).
6. **Signature:** the people's marks (table), each with a few variants and on/off.
7. **Name**, in the people's own sound (Norse for the Hrimfolk, Persian for the Zarhim, Gaelic for the Ruadhan;
   design.md).

Built for phones: one screen per step, big swatches, a live model you can turn.

## Open

- The voxel system's own limits (resolution, how gear and hair attach, how sliders map to voxels) once it is merged.
- Face presets per people: to design with reference sheets, like the approved Hrimfolk test character.
- Signature marks for the Ruadhan, Aurelans and Zarhim beyond their clothes (if wanted).
- How the Fog changes a character (the half-changed neighbour, beat E) and whether players can show it.
