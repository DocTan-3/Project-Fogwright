# Credits

## Base male body

`studies/rpgbody.gltf.json` and the characters built from it start from **Simple RPG Human Male**, a model downloaded from Sketchfab. The sword, shield and painted texture from that download are not used. The model has been rigged to Fogwright's skeleton and repainted by code, and Fogwright's own hair, beards, moustaches and builds are added on top.

**License: to be confirmed.** Before this ships, record the author, the model's Sketchfab page and its license here. If it's CC BY, keep this credit. A non-commercial (NC) or no-derivatives (ND) license would rule it out.

The original download is not in this repository. To rebuild, put `model_0.obj` in `tools/blender/source/` and run `tools/blender/rpgbody.py`.

## MakeHuman bodies

`creator/mh_m.gltf.json` and `creator/mh_f.gltf.json` are built from **MakeHuman**'s base mesh, shape targets, joints and skin weights, as shipped in MPFB (https://github.com/makehumancommunity/mpfb2). These assets are released under **CC0** (public domain): no credit is required and commercial use is allowed. The credit here is a courtesy. Copyright holders at the time of the CC0 release: Data Collection AB, Joel Palmius, Jonas Hauquier.

## Surface textures (game/tex/city.jpg)

CC0 photo textures from Poly Haven (https://polyhaven.com), public domain, packed into one 4x4 sheet at 512 px each:
brick_wall_001, old_stone_wall, damaged_plaster, medieval_wood, clay_roof_tiles_02, roof_slates_02, thatch_roof_angled,
grey_roof_01, rusty_corrugated_iron, clay_plaster, white_sandstone_blocks_02, brown_planks_05, cobblestone_square,
cobblestone_large_01, large_sandstone_blocks (cropped and mirrored), stony_dirt_path.

## World and prop textures (game/tex/world.jpg)

CC0 photo textures from Poly Haven (https://polyhaven.com), public domain, 4x4 sheet at 512 px each:
leafy_grass, forest_leaves_02, coast_land_rocks_01, coast_sand_01, brown_mud, grass_path_2, bark_brown_02, forest_leaves_04,
wood_table_worn, quatrefoil_jacquard_fabric (greyscale), brown_leather, rusty_metal_02, green_metal_rust, dirty_carpet,
terry_cloth (greyscale), aerial_rocks_02.

## Gear textures (creator/tex/gear.jpg)

CC0 photo textures from Poly Haven (https://polyhaven.com), public domain, turned into greyscale detail and packed into one 4x4 sheet at 256 px each by `tools/textures/gearsheet.py`:
rough_linen, caban, poly_wool_herringbone, brown_leather, leather_red_02, scuba_suede, curly_teddy_natural, hessian_230,
velour_velvet, floral_jacquard, quatrefoil_jacquard_fabric, knitted_fleece, wool_boucle. Brushed steel and mail are drawn by the script.

## Animations (assets/animations/quaternius)

Universal Animation Library 1 and 2 (Standard) by Quaternius, CC0 1.0 (public domain):
https://quaternius.itch.io/universal-animation-library, https://quaternius.itch.io/universal-animation-library-2
Universal Base Characters (Standard) by Quaternius, CC0 1.0 (public domain), in assets/characters/quaternius (textures
scaled to 1024 px): https://quaternius.itch.io/universal-base-characters

## Asset packs (tools/assets/packs.json)

Third-party packs are listed with their licences in tools/assets/packs.json and downloaded by tools/assets/fetch.py; only
CC0 packs may be committed here. Packs that forbid redistribution ship only inside the game. Credit required for any use:
Post-Apocalyptic World by Atomic Realm, https://atomicrealm.itch.io/

CC0 photo textures from Poly Haven (https://polyhaven.com), public domain, 1K colour, normal (OpenGL) and roughness maps, for
the Ferrin buildings (godot/assets/buildings/ferrin/tex; the stone colour maps desaturated): rock_wall_05, medieval_blocks_03,
castle_brick_07, metal_plate_02, rusty_metal_02, dark_wooden_planks. The models are our own, built in Blender by
tools/blender/ferrin_forge.py and tools/blender/ferrin_kit.py (BUILDING=shop|smelter|shrine|narrow|toolmaker|stair|foundry).
