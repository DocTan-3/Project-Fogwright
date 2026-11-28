# Fogwright builds

Ready-to-run builds of the game, replaced with each new version. The code is on the other branches.

- **Windows:** download `Fogwright-windows.zip`, unzip it, double-click `Fogwright.exe`. If it does not start, run
  `Fogwright.console.exe` instead: a text window opens showing what went wrong.
  Windows may warn that the file is from an unknown publisher: choose "More info", then "Run anyway".

Controls: WASD or the arrows to move (you run by default), Shift to sprint, Space to jump, Ctrl to switch between walking
and running, move the mouse to turn the camera (Esc frees the cursor, a click takes it back), the mouse wheel to zoom, F2 for live character shadows.

**Combat test.** Press **F9** to spawn one of each Fog enemy in front of you: a husk (strikes, combos, heavy hooks), a
brute with a shield and axe (charges, shield bashes, heavy blows) and a thrower that keeps its distance. Each attack is
marked on the ground while it winds up, coloured by what counters it:

| Colour | Attack | Counter |
| --- | --- | --- |
| white | strike | anything: block, parry or dodge |
| yellow | combo | block or parry (you cannot dodge it) |
| red | heavy blow, charge | dodge or step aside (you cannot block it; it knocks you down) |
| orange | shield bash | parry (you cannot dodge it; it stuns) |
| blue (a flying stone) | projectile | dodge, step aside or block (no parry) |

- **Left click** attacks toward the crosshair: a sword or hammer cuts what is in front of you; a pistol, bow or wand
  shoots to where the crosshair points (the bow: hold to draw, release to loose; a longer draw hits harder).
- **Right click (held)** blocks with the sword, warhammer or wand (35% of the damage gets through). **Raise the block
  just before a hit lands to parry**: only 5% gets through and the enemy reels, but it costs three times the stamina.
  Only the sword and warhammer can parry.
- Pistols and bows cannot block: their **right click aims**. The crosshair is wide when you fire from the hip and
  narrows when you aim; each shot widens it for a moment, and so does moving.
- **Alt** dodges. Dodging, blocking and parrying spend stamina (the yellow bar).
- **Tab** locks onto the nearest enemy (melee attacks turn to it). **1-6** and **Q E R T Z V** cast the twelve skills
  (energy, the blue bar).
- **G** changes weapon: sword, warhammer (builds momentum while it keeps hitting), flintlock pistol (two loads, then a
  reload), shortbow, brass wand (spends Fog shards).
- Skill-tree perks to try (toggle): **F5** block heavy blows, **F6** dodge through combos, **F7** parry projectiles,
  **F8** dash instead of roll, **F10** dodging reloads a gun, **F11** cheaper blocks.

**Camera test.** The game now starts with an Albion-style camera: high above you, looking down. Move with WASD; your
attacks and aim go toward the mouse cursor; the mouse wheel zooms (it tilts lower as you zoom in); hold the middle mouse
button to turn the view. Walls and roofs between the camera and you are cut away. **F3** switches to the close
third-person camera and back.
