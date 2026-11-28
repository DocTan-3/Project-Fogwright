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

- **Face presets (started):** `make_character.py` `FACE` lists the face options (eyes, spacing, nose, mouth, brows,
  scar, expression, hair, beard (None is clean-shaven), hair and eye colour) and `PRESETS` six faces per people and sex, for
  all eight peoples. Preset 0 is the base body's own face; presets 1 to 5 are written as head-only layers to
  `peoples/faces/<people>_<sex>_<k>.vox`, their names to `godot/data/faces.json`. A layer with a `head` replaces the
  base head and everything riding on it (`Vox.character`); `Equipment.dress(..., face)` puts it under any helm.
  `godot/tests/voxel_faces.tscn -- people=<people>` renders the presets. Sliders (height and bulk within each people's
  range, skin tone) are still to do.
- **Hair and beards are their own choices:** heads are always bald; each hair and beard style is a separate layer,
  `peoples/hair/<people>_<sex>_<style>.vox` and `peoples/beard/<people>_m_<style>.vox` (shaved and clean-shaven have
  none), shells grown one fine voxel out over the head plus the hanging pieces. Hair, beards and brows are written in
  key colours (`HAIR_KEYS`, `Vox.HAIR_KEYS`) and painted with the chosen colour when loaded. Layers replace by group
  (`group()` / `Vox.group()`: face, hair, beard). `Equipment.dress(..., look={hair, beard, hair_col})`, defaults from
  the face preset in `godot/data/faces.json` (which also lists each people's styles and hair colours). Hides match a
  piece name or `name*`. `godot/tests/voxel_hair.tscn -- people=<people>` shows every style and colour.
- **Wayfolk common iron set (weapons.md set 2):** `IRON` and `iron_shape()` in `make_equipment.py`, items `iron_<kind>`:
  sword, axe, mace, hammer, dagger, greatsword, greataxe, warhammer, spear, bow (one bow: short and long differ only in
  their damage to speed ratio), heavy crossbow, shield, tower shield. Cut by Doc Tan: buckler, hand crossbow (pistols cover
  it), halberd, glaive, wand and staff (no caster foci; magic is rare: runes, consumables, tools and relics). Blades thin to
  one-voxel edges and long points. Off-hand pieces (`weapon_off@hand_l`) ride the left hand; new
  stances `shield` and `bow` (off-hand stances win for the left arm). Carried: one-handers at the left hip, long ones
  across the back, the shield on the back, the tower shield on the back. `godot/tests/voxel_weapons.tscn` renders them
  drawn and carried with a ground check. Not yet: two-handers held in both hands (they use the one-hand grip), and sharing one weapon model across bodies (each weapon is still written per body, about 5 MB for the set).
- **Body sliders (the user's choice: scaled in the game, not regenerated):** `Vox.shape(root, height, bulk)`, each -1
  to 1: height stretches legs, torso and arms by up to 6%, bulk thickens or slims them by up to 12%. Heights above the
  ground scale too, so the feet stay down; the head keeps its size, gear riding on a part scales with it, weapons keep
  theirs. `Equipment.dress(..., face, height, bulk)` applies it. `godot/tests/voxel_bodies.tscn -- people=<people>`
  shows the slider corners bare and in heavy armour with a spear, and prints GROUND FAIL / FLOAT FAIL.
- **Each people looks its own (the user's rule):** `SIGNATURE` gives every people its brow style (Hrimfolk shaped and
  heavy, Ruadhan high arches, Aurelan level, Zarhim joined, Ilvari fine, Ferrin a bushy shelf, Penitent none) and marks
  (kohl, pointed ears, a high bridge, hollow eyes, rosy cheeks, freckles); `STYLES` its own hair and beards (Ruadhan
  manes and drooping moustaches, Aurelan side parts and goatees, Zarhim tails, Ilvari sleek, Ferrin forked beards,
  Penitent shorn). The Wayfolk are the plain ones, and that is their signature. Presets must use their people's styles
  (the generator asserts it).
- **Animation:** none yet. Parts are rigid and pivot at joints, and animation adds to the rest pose (`get_meta("rest")`).
- **Metrics:** a 1.6 m stylized character, against the research's 1.8 m person and 2.4 m door. The current proposal is
  doors of about 2.2 × 1.4 m for the WoW camera.

## Handoff: where the character work stands

**Branches:** `character-system` (this work, branched from `voxel`); design decisions are on `main` (`docs/design.md`
Character pipeline and Equipment, `docs/weapons.md`). The paused Farhallow Skyrim-scale plan is on
`farhallow-skyrim-scale` (its game checker not yet run).

**Done**
- Generator for all eight peoples, both sexes (`make_character.py`): builds, colours, marks, carved 1.25 cm heads,
  women's proportions, base bodies in underwear plus a starting-clothes layer, body measurements in `build.frame`.
- Equipment as recipes fitted to every body (`make_equipment.py`, `godot/scripts/voxel/equipment.gd`,
  `godot/data/equipment.json`): five armour tiers, colossus arms and gauntlets (they are the weapon: they take both
  hands), back arms (claw, saw, bulwark, twin cannons) on a pack or a spine, a basic common item in every slot.
- Farhallow tools (hatchet, fisher's spear, smith's hammer, the old blade, boat hook, cleaver, pitchfork) in hand and
  carried; two idle stances (weapons put away; drawn, by weapon class); polearms carried low with the haft through the
  fist and the wrist aiming it.
- Checks: `tests/voxel_equipment.tscn` prints `GROUND FAIL` for anything below the ground (clean now);
  `tests/voxel_polearm.tscn` for polearm grips; `tests/voxel_peoples.tscn` for the lineup and faces.

**Rendering here:** the test scenes need a display: start `Xvfb :99 -screen 0 2400x1000x24 &` and run Godot with
`DISPLAY=:99`. Godot rewrites `godot/project.godot` when run; restore it (`git checkout godot/project.godot`).

**Next, in the order discussed**
1. The character builder: about 6 face presets per people and sex (eyes, nose, mouth, brows, expression, marks) and
   sliders within each people's range.
2. The rest of the weapon list: the Wayfolk common iron set (every type), then fist weapons, harpoon and grapple guns,
   mechanical melee (epic and up).
3. Off-hand items (shields, tower shields) so the off hand has something to hold in the drawn stance.
4. Rebuild the approved Hrimfolk (`make_stylized.py`) from the generator; its skin is too bright for the game's light.
5. Later: trim triangles (the basics outfit is about 8,000; over budget, accepted for now); animate back arms (the
   importer needs pieces chained off other pieces); the design doc's slot table should say colossus pieces fill the
   hands (weapons.md already does).

### Bow at rest and ammunition (2026-11-28)

- A drawn bow at rest uses hold E (Doc Tan's side sketch): the left arm hangs straight and the bow lies level through the fist, running front to back beside the hip, its riser centred in the fist, the string on top and tilted in toward the leg. `Equipment.BOW_REF` and `bow_pose` hold it; `tests/bow_poses.tscn` renders holds side by side. The older holds (A-D, F-H, and "" for the low-across one) stay as options.
- **Ammunition slot** (`ammo`) on the belt, so a knapsack or anything else on the back can still be worn:
  - `quiver` (bows): a side quiver (Doc Tan's references). It hangs on two straps from the belt at the right hip, just outside the hanging arm, and slants from a wide studded mouth in front down to a narrow foot behind, with the arrows standing forward and up.
  - `bolt_case` (crossbows): a stiff iron-cornered box with its lid open and the bolts standing in a row.
  - `bullet_pouch` (guns): a cartridge box with a brass badge, a shot bag and a powder flask.

### Tiers (2026-11-28)

- **One version per tier first** (Doc Tan): five tiers, one per rarity step. T1 common is the Wayfolk iron set. T2 uncommon adds contrast trim and brass fittings. T3 rare adds tooled leather, rivets and small brass fittings. T4 epic adds working parts such as gauges, pipes and a glowing vial. T5 legendary glows; motion comes later. The item list doc tracks what exists.
- `TIERS` and `TIERED` in `make_equipment.py` set which types get tiers. Items are named `<type>_t2` .. `<type>_t5`, and `iron_<type>` stays as T1.
- **Axes and greataxes** are done too (`axe_tier`, `AXES`): flaring bits with a convex edge, a beard on the single axe, a back spike from T3; T2 brass langets, T3 iron-ringed dark haft and rivets, T4 a vial in the eye feeding a pipe to a gauge, T5 runes, eye and top crystals.
- **Maces** are done too (`blunt_tier`, `BLUNT`): flanges grow by tier (6, then 8 with a top spike, black round a potion core, gilt round an arc core with a crystal).
- **Hammers and warhammers** follow Doc Tan's T4 reference at every tier (`hammer_line`): a long double-faced head with vented ends, a strap round the middle and a bracket below. T1 iron, T2 steel with a brass strap and langets, T3 vents and an iron diamond bracket, T4 ivory with black vents, a copper strap inlaid teal, a gilt filigree bracket and a tasselled pommel, T5 gilt-edged with glowing vents, an outer wing and crystals.
- **Spears** (`spear_tier`): T2 steel leaf and brass socket, T3 longer leaf with a fuller, parrying wings and a butt spike, T4 black leaf, vial socket, pipe and gauge, T5 blued leaf with arc runes, gilt wings and a crystal butt.
- **Bows** (`bow_tier`): T2 a brass-fitted ash recurve, T3 a horn-bellied composite with ivory tips and an arrow shelf, T4 a compound bow on a black riser with brass cams, cables, a sight pin and a stabiliser, T5 a blued recurve with gilt inlay, arc runes, crystal tips and a glowing string.
- **Crossbows** (`crossbow_tier`): T2 a brass-fitted steel prod with a stirrup, T3 recurved prod, riveted stock, windlass and a loaded bolt, T4 a black skeleton stock with pulley wheels, cables, a steam cylinder, a gauge and a scope, T5 blued and gilt with a recurved gilt prod, crystal tips, a glowing string and bolt. Drawn, a crossbow is held level in both hands at the waist, pointing across to the left (stance `crossbow`, `Equipment._hold_crossbow`, after Doc Tan's references).
- **Pistols** (`pistol_shape`, all five tiers): T1 a scrap pipe pistol lashed to a block with a smouldering match, T2 a flintlock with walnut stock and brass furniture, T3 a six-barrel pepperbox, T4 a Ferrin steam pistol (finned barrel, copper tank, gauge, valve, vial), T5 an arcane pistol with a crystal cylinder and glowing runes. Bigger barrels (round, 5 voxels) and longer grips. Drawn, the grip runs through the fist and the muzzle points down at the ground (iron_shape turns the pistol frame for the hand); carried in a holster at the right hip. `tests/voxel_tiers` now also shoots a right-side view.
- **Swords, greatswords and daggers** are done (`blade_tier`, one design scaled to each blade by `BLADES`):
  - T2: bright steel with a brass guard whose tips sweep down, a brass-wired grip and a brass pommel.
  - T3: a broader blade with a wide fuller, a riveted guard with langets, a tooled grip and a wheel pommel.
  - T4: a blackened blade with a copper pipe up the fuller, fed by a glowing vial in the guard, plus a gauge and a valve pommel.
  - T5: blued steel with glowing runes down the fuller, gilt wings round an arcane crystal and a crystal pommel.
- `godot/tests/voxel_tiers.tscn -- type=sword` renders one type at every tier: drawn, close up, carried, and the weapons alone on a rack. It also runs the ground check.
- Glow is only colour so far. There is no emissive material yet.
