# Fogwright builds

Ready-to-run builds of the game, replaced with each new version. The code is on the other branches.

- **Windows:** download `Fogwright-windows.zip`, unzip it, double-click `Fogwright.exe`. If it does not start, run
  `Fogwright.console.exe` instead: a text window opens showing what went wrong.
  Windows may warn that the file is from an unknown publisher: choose "More info", then "Run anyway".

Controls: WASD or the arrows to move (you run by default), Shift to sprint, Space to jump, Ctrl to switch between walking
and running, hold the right mouse button or press Q and E to turn the camera, the mouse wheel to zoom, F2 for live character shadows.

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

- **Tab** targets the nearest enemy (or click one); **R** attacks: you walk into range and attack while standing still.
  Moving pauses your attacks but keeps the target.
- **F** blocks while held (35% of the damage gets through). **Tap F just before a hit lands to parry**: only 5% gets
  through and the enemy reels, but it costs three times the stamina. Only melee weapons (sword, warhammer) can parry.
- **C** dodges (a roll: untouchable for its first moments). Dodging, blocking and parrying spend stamina (the yellow bar).
- **1-6** cast skills (energy, the blue bar); **X** swaps to the second page of six.
- **G** changes weapon: sword, warhammer (builds momentum while it keeps hitting), flintlock pistol (two loads, then a
  reload), shortbow (a longer draw hits harder), brass wand (spends Fog shards).
- Skill-tree perks to try (toggle): **F5** block heavy blows, **F6** dodge through combos, **F7** parry projectiles,
  **F8** dash instead of roll, **F10** dodging reloads a gun, **F11** cheaper blocks.
