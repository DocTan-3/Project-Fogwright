# Fogwright: working rules

- **References are remade, not approximated.** When the user sends a reference image (a house, a floor plan, a map, a
  prop, a character), first take it apart in writing - count the walls, storeys, windows, doors and parts, and list every
  detail - then rebuild all of it in Fogwright's art direction (our kit, palette and lighting). Never drop parts to make it
  easier or hand back something that only resembles it; where the kit lacks a part, build it. Compare a render with the
  reference and say plainly anything that still differs.
- **Settlements follow the city-planning skill** (`.claude/skills/city-planning`): who it is for (the people's culture sheet), lore, logistics, a plan, paths, doodads, then build, and the
  checker (`godot --path godot res://tests/check.tscn`) must report 0 problems before committing.
- The game is in `godot/` (Godot 4.7, GL Compatibility). Builds for the user go to the `builds` branch as a one-click zip.
- **Know the tools before building:** read `tools/assets/INVENTORY.md` (regenerate it with `python3 tools/assets/inventory.py`
  after adding packs, models or building types). Use what we have; anything marked missing is made (Blender) or found
  before the 3D build that needs it. New packs go into `tools/assets/packs.json` with their licence checked first.
- The repository is public: only CC0 or our own assets are committed; third-party packs are listed with their licences in
  `tools/assets/packs.json`.
