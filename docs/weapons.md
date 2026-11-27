# Weapons

The weapon plan: what weapon types exist, what a weapon can do, how guns enter the world, how weapons come in sets, and
prompts for making them. Choices made with the user are marked **(chosen)**; the rest are proposals.

## Families and types (chosen: all four families at launch)

| Family | One-handed / light | Two-handed / heavy | Off hand | Carried (design.md) |
| --- | --- | --- | --- | --- |
| **Melee** | sword, axe, mace, hammer, dagger | greatsword, greataxe, warhammer, spear, polearm (halberd, glaive) | shield, buckler, parrying dagger | daggers at hip, boot or back; one-handers at the hip; two-handers and polearms across the back; shields on back or forearm |
| **Bows and crossbows** | shortbow, hand crossbow | longbow, heavy crossbow (with a crank) | quiver (back) or bolt case (hip) | bows across the back; crossbows slung from the shoulder |
| **Gunpowder** | pistol, pepperbox | rifle, musket, blunderbuss, hand cannon | powder horn, cartridge box (belt) | pistols in a hip or thigh holster; long guns slung from the shoulder |
| **Caster foci** | wand, rod, relic focus | staff | tome, lantern focus | staff kept in hand or across the back; wands and rods at the hip |

**Tools that fight** *(proposal)*: early weapons are tools first (woodsman's hatchet, fisher's spear, smith's hammer,
boat hook, pitchfork, cleaver). They count as their family (the hatchet is an axe, the fisher's spear a spear) and are
how the prologue arms the player (lore.md, beat 3).

## What a weapon can do: rarity decides (chosen)

Common weapons only have a normal attack. What else a weapon can do comes from its rarity, so the rarest weapons are
truly unique. *(proposal for the steps between:)*

| Rarity | Capabilities | Look (design.md) |
| --- | --- | --- |
| **Common** | the normal attack only | plain iron and wood, simple wraps |
| **Uncommon** | the normal attack plus one passive trait (bleed on hit, faster swings, longer reach) | contrast trim, brass fittings |
| **Rare** | plus one active ability tied to the weapon type (a cleave for axes, a lunge for spears, a volley for bows) | tooled leather, rivets, small brass fittings |
| **Epic** | plus a second ability or a stronger trait, and a mechanism (a spring blade, a twin-shot crossbow) | working parts: gauges, pipes, faintly glowing vials |
| **Legendary** | a unique named weapon with its own story, look and kit that nothing else has; very rare | glows and moves |

**With the skill tree (chosen):** the weapon brings the moves, by its rarity; the skill tree changes how they work (a
dash-reload instead of a standing reload, a wider cleave, a second charge) and trains each family's handling. Armour
brings abilities by rarity the same way. See design.md, *Moves, the bar and defence*.

## Guns (chosen: rare, more common higher up, several types, crude early ones)

Guns are rare in the start regions and grow more common at higher levels and farther from Aldrath's heartland toward the
Ferrin's Slag Isles. Early guns are crude and badly made. *(proposal for the tiers:)*

| Tier | Where and when | Examples | How it handles |
| --- | --- | --- | --- |
| **Scrap guns** | early, rare: smuggled or home-made | pipe pistol, nail blunderbuss, a cracked matchlock | slow to load, inaccurate, can misfire or jam; a puff of black smoke |
| **Matchlocks** | early-mid, from traders | matchlock musket, hand cannon | slow, heavy, a glowing match cord; strong at short range |
| **Flintlocks** | mid levels, Wayfolk and Aurelan gunsmiths | flintlock pistol, musket, blunderbuss | dependable, still one shot per load |
| **Ferrin rifles** | high levels, the Slag Isles | rifled long gun, pepperbox, breech-loading pistol | accurate and long-ranged, faster to reload |
| **Steam and arcane guns** | endgame (steam and arcane eras) | pressure rifle, rotary hand cannon | late inventions; very rare |

## Sets: weapons made to match (proposal)

Weapons are designed and made as **sets**: one look carried across every type in that set, so a sword, a bow and a
pistol from one set clearly belong together. The first sets:

1. **Farhallow tools** (prologue): hatchet, fisher's spear, smith's hammer, the old blade above the smithy door, boat
   hook, kitchen cleaver. Worn, home-made, wooden hafts, rope and rag wraps. Common only.
2. **Wayfolk common iron** (the starter sets bought and looted around Hollin's Cross and Aldrath): every melee type,
   shortbow, longbow, hand and heavy crossbow, a shield and buckler, a wand and staff. Plain forged iron, ash wood,
   leather grips, simple round pommels and nail heads.
3. **Scrap guns:** pipe pistol, nail blunderbuss, cracked matchlock: rough tubes, wire, mismatched wood.
4. **People sets**, one per people (Hrimfolk, Aurelans, Ferrin, Zarhim, Ruadhan, Ilvari), in their style from design.md
   (Hrimfolk riveted dark iron and antler; Aurelan blued steel with gilt and heraldry; Ferrin brass, gears and blackened
   steel; Zarhim curved blades, wrapped hilts and sandstone tones; Ruadhan bronze, knotwork and red enamel; Ilvari slim
   glass-and-brass with blue light).
5. **Craft sets**, one per craft, matching the armour sets.
6. **Legendaries**, each one of a kind.

Every set covers the same type list, so a player who likes a look can keep it whatever they fight with.

## Making them

- **Budget:** one-handers 300-800 triangles, two-handers and guns 600-1,500, staffs 500-1,200; one 512 px texture per
  set (atlas), from the palette (scripts/palette.gd); real-world size (a one-handed sword about 0.9 m, a longbow 1.8 m).
- **Pivot and grip:** the pivot at the main grip, blade or barrel along +Y (Godot), a second grip marker for
  two-handers; sockets for the belt, back and holster mounts.
- **Prompts:** `art/weapon-prompts.md` has the 2D (concept) and 3D (model) prompts, starting with the Farhallow tools
  and the Wayfolk common iron set.
