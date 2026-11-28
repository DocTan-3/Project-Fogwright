# Handoff: Fogwright's voxel direction (from the cloud session, 2026-11-28)

Read this first, then `docs/voxel-characters.md`. All of this work is on the **`voxel`** branch. `main` holds the design
docs, the Farhallow plan and the Skyrim research. `characters` and `builds` hold the earlier combat and Windows builds.

## Where the project stands

- **Engine:** Godot 4.7 with the GL Compatibility renderer, kept on purpose. It must stay light enough that a browser
  build could run it, even though the game ships for Windows. The user decided to stay on Godot over three.js, Unity,
  Unreal and Bevy.
- **Budget:** the user wants the game made purely with Claude, at no cost beyond the Claude subscriptions. Free assets
  and tools are fine. Mixamo was declined.
- **Art direction: voxels.**
  - **Voxel sizes:** 2.5 cm for characters, gear and weapons (`Vox.FINE`), 5 cm for props, 10 cm for buildings and the world.
  - **Grass, water, fog, smoke, fire and cloth are not voxels.** They are low-poly, in palette colours, and move.
- **Camera:** the WoW-style third-person camera is the default (`godot/scripts/camera_rig.gd`).
  - The mouse turns the view.
  - The wheel zooms from over the shoulder out to 18 m.
  - A spring arm stops it at walls.
  - F3 switches to the Albion-style high camera, with roof cutaway.
- **Combat:** built earlier on the `characters` branch, with the old Quaternius human. The spec is in `docs/design.md`
  on `main`. It has not been moved onto voxel characters yet.

## Done on `voxel`

1. **Voxel importer** (`godot/scripts/voxel/vox.gd`):
   - MagicaVoxel `.vox` files become greedy-meshed parts that pivot at their joints by name.
   - Gear is `piece@part`; finer parts are `part#k`; tilts are `name~x..y..z..`.
   - The rest pose is `Vox.REST`.
   - `Vox.prop()` places MagicaVoxel `.glb` packs pixel-exact and matte.
2. **The approved Hrimfolk character and sample gear:** see `docs/voxel-characters.md`. The user has approved them.
3. **Medieval Voxel Assets** (Felix Strefter, CC0) in `godot/assets/buildings/medieval_voxel/` (`LICENSE.md` is with
   them):
   - The pack is built from 10 cm voxels, the same as our world voxels.
   - It is pale cream and straw-yellow; we may recolour it.
   - **Max Parata's Medieval Town is CC BY-ND:** reference only, unless bought and used unmodified.
4. **Ground kit** (`godot/scripts/voxel/ground_kit.gd`, test `godot/tests/ground_sheet.tscn`). The user's brief was
   "Valheim snapping pieces for the dirt", not Minecraft cubes.
   - **Pieces:** 1 m cells whose corners snap to 0.5 m steps. That gives a fixed set: flat, 27° slope, 45° bank, and
     their corners.
   - **Cliffs:** where the ground drops more than 1 m across a cell, it becomes rock made of 25 cm columns with ledges and moss.
   - **Surface:** flat-shaded facets with a 10 cm speckle for voxel grain. Where kinds meet (path, sand), cells are drawn
     in 25 cm squares.
   - **Grass:** MultiMesh tufts in 16 m chunks, drawn only within 45 m of the camera. They sway in the wind, and
     `GroundKit.push()` makes them part round up to 8 walkers. The user wanted grass that reacts, not static blobs.
5. **Voxel Farhallow** (`godot/scenes/farhallow_voxel.tscn`, `godot/scripts/farhallow_voxel.gd`, test
   `godot/tests/farhallow_voxel_shot.tscn`):
   - The ground kit runs on Farhallow's real land, reusing `farhallow.gd`'s height, coast and terraces and
     `data/farhallow.json`.
   - The roads, lanes and trails are stamped into a 25 cm mask and drawn as paths.
   - There is sea and grass.
   - Each plan building gets the nearest-shaped stand-in from the Felix pack, scaled to its plot.
   - The player is the voxel Hrimfolk, using `player.gd`. It walks with `voxel_walk.gd`, a procedural limb swing that
     stands in until real animation exists.
   - It renders correctly. **The Windows test build was not made yet.**

## Decisions the user made

- **Interiors:** Skyrim-level, under a mixed plan (the user asked; I recommended it; written up below, not yet in
  `docs/design.md`).
  - Ground-level buildings are true-size and seamless in the open world.
  - Spaces bigger than their shell go below ground or behind a gate into their own instance.
  - The Farhallow prologue is a private instance, because the Fog takes the village for every new player. Afterwards,
    the ruin is part of the open world.
- **Sizes for the WoW camera:**
  - Rooms need about 4–5 m ceilings in halls and inns.
  - **Proposed, not yet approved:** doors about 2.2 m tall and 1.4 m wide, with Felix's pack scaled up about 1.2× to match.
  - The research on `main` says a 1.8 m person and 2.4 m doors; the stylized characters are 1.6 m.
- **Modular gear:** one item can span several body parts and inventory slots, for example the cyberarm with its chest
  implant. The body is drawn as parts and items replace or ride on them.
- **Pending a check:** the Ferrin buildings ported to Godot earlier, to be checked against the new assets.

## Next steps, in order

1. **Make the Windows test build** of `scenes/farhallow_voxel.tscn`:
   - Either set it as `run/main_scene` on the `voxel` branch, or add a launcher.
   - Run `python3 tools/build/export_list.py`, then export with `--export-release "Windows Desktop"`.
   - Publish to the `builds` branch, as the earlier builds were.
   - The user wants to walk through the grass with the WoW camera.
2. **Fix the dark seams** between 25 cm-subdivided cells and plain cells. They are T-junction cracks. Fix them by
   subdividing a cell's neighbours' shared edges as well, or by drawing paths as a draped overlay.
3. **Buildings:**
   - The stand-ins are solid boxes for collision, so nobody can go inside yet.
   - The next step is Fogwright's own voxel building kit on the 2 m module, with real interiors.
   - The inn comes first, as the test of walking in with the WoW camera.
4. **Write the interiors and sizes decisions into `docs/design.md`**, after the user confirms the door size.
5. **Later:**
   - trees, rocks and the well as voxel props;
   - grass density and draw distance tuned for a browser build (and a web export as a lightness benchmark);
   - moving combat onto voxel characters;
   - real animation for voxel parts.

## How to work here

- **Tests:** they render PNGs.
  - Run one with `godot --path godot --rendering-driver opengl3 res://tests/<name>.tscn -- out=<prefix>`.
  - Headless parse check: `godot --headless --path godot res://tests/parse.tscn -- script=res://<file>`.
  - After adding a new `class_name`, run `godot --headless --path godot --import` once, or scenes using it fail to load.
- **Git:** commit trailers as before. Pushing to `main` needs the user's explicit OK.
- **Tone with the user:** they want honest assessments and renders shown, and short answers.
