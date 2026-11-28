# Voxel characters: how they are made (handoff for the peoples)

The approved look is the stylized Hrimfolk man. Every other people starts from how he is built. Everything is on the
`voxel` branch.

## The approved character

- **Source:** `tools/voxel/make_stylized.py` writes `godot/assets/voxel/characters/hrim_stylized.vox`. Run it with
  `python3 tools/voxel/make_stylized.py`. The file opens in MagicaVoxel.
- **Gear samples:** `tools/voxel/make_gear_stylized.py` writes `godot/assets/voxel/gear/hrim_*.vox`: pauldrons, goggles,
  toolbelt, steam tank, and a cyberarm with its chest implant.
- **Test scenes:**
  - `godot/tests/voxel_style.tscn`: the character alone.
  - `godot/tests/voxel_gear.tscn`: three gear loadouts.
  - Run either with `godot --path godot --rendering-driver opengl3 res://tests/<name>.tscn -- out=<png prefix>`.

## Proportions (the user's references, approved)

- **Scale:** voxels are 2.5 cm (`Vox.FINE`). He is 64 voxels (1.6 m) tall, about 4.3 heads.
- **Head:** 14 wide, 13 deep and 15 tall, with bevelled edges.
- **Body:** a short, broad torso with no neck, 20 wide and tapering at the waist. Thick arms with bracers and big fists
  with a thumb. Short, thick legs and big boots with a turned cuff.
- **Shapes:** boxy, with bevelled vertical edges (`rbox()`). Flat colours, with one darker and one lighter tone per material.
- **Face:** drawn voxel by voxel from an ASCII map (`FACE` in `make_stylized.py`), not computed from shapes.
  - The nose, moustache and beard stand out from the face by one voxel.
  - The brows are separate tilted pieces.
- **New peoples:** each people or face is a new map plus a palette, and its proportions change within this style.

## Rules the importer applies (`godot/scripts/voxel/vox.gd`, `Vox.character()`)

- **Part names:** each body part is its own named model in the .vox file:
  - `head` and `torso`;
  - `arm_upper_l`, `arm_lower_l` and `hand_l`, with `_r` for the right;
  - `leg_upper_l`, `leg_lower_l` and `foot_l`, with `_r` for the right.
- **Pivots:** parts pivot at their joints by name, and lower limbs hang from upper ones.
- **Sides:** in MagicaVoxel, x = 0 is the character's right as seen from the front.
- **Gear:** `piece@part` rides on that part, for example `goggles@head` or `tank@torso`. A layer file whose parts take a
  body part's own name replaces that part, as the cyberarm does. One item can cover several parts and slots.
- **Tilts:** `name~x-8z12` gives a part off-grid degrees in game axes. It turns about the end nearest its parent's joint.
  This gives the references' living, off-grid look: the brows, the braid, the pauldrons and the belt tools.
- **Finer parts:** `part#2` is a part at half-size voxels.
- **Rest pose:** `Vox.REST` gives a relaxed stance: arms a little out, fists turned in, feet turned out, head tipped.

## Budget

- **Triangles:** a geared character is about 2,800–3,900 triangles after greedy meshing. Keep peoples in that range.

## The peoples and equipment (character-system branch)

- **Every people, both sexes:** `tools/voxel/make_character.py` writes `godot/assets/voxel/characters/peoples/`:
  `<people>_<sex>.vox` is the base body in its underwear (what the creator shows), `<people>_<sex>_clothes.vox` the
  starting clothes as a layer of replacement parts. The head is `head#2`, at 1.25 cm, carved and painted.
  `build(people, sex, dressed)` also records the body's measurements in `build.frame`.
- **Equipment:** `tools/voxel/make_equipment.py` fits every item to every body from those measurements and writes
  `godot/assets/voxel/gear/<item>/<people>_<sex>.vox` and `godot/data/equipment.json` (slots, layering order, what an
  item hides). `godot/scripts/voxel/equipment.gd` dresses a character: `Equipment.dress(people, sex, items)`.
- **Tests:** `godot/tests/voxel_peoples.tscn` (the lineup, face close-ups; `clothes=1` for the starting clothes) and
  `godot/tests/voxel_equipment.tscn` (every armour tier on five bodies).
- **Rules learnt:** keep colours within real reflectance (sRGB about 200 at most for pale skin); give the test sun a
  shadow bias or flat voxel faces show acne; carve faces with whole features (sockets, jaw, lips), since single-voxel
  steps read as creases.

## Not settled yet

- **Face presets and sliders:** next, for the character creator.
- **Animation:** none yet. Parts are rigid and pivot at joints, and animation adds to the rest pose (`get_meta("rest")`).
- **Metrics:** a 1.6 m stylized character, against the research's 1.8 m person and 2.4 m door. The current proposal is
  doors of about 2.2 × 1.4 m for the WoW camera.
