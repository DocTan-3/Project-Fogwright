## The test weapons, one per family (docs/weapons.md), each with its family's quirk (docs/design.md):
##   guns reload, heavy melee builds momentum, bows reward the draw, caster foci spend Fog shards.
## Guns and bows cannot block: their right click aims ("spread": the crosshair's half-angle in degrees when fired from the
## hip, when aimed, and how much each shot blooms it). The wand blocks and fires from the hip only.
## Attacks come one per click, no faster than "interval" (seconds); hits are slower and heavier than in the first test.
## Moves are what the weapon's rarity gives (a common weapon only attacks); these are first test moves, not designed skills.
## Clips are from the Quaternius animation libraries ("ual" = UAL1, "ual2" = UAL2); the bow and the heavy weapon have no
## clips of their own yet and borrow the pistol's aim and the sword's heavy combo.
class_name Weapons
extends RefCounted

const LIST := ["sword", "warhammer", "pistol", "shortbow", "wand"]

const DEFS := {
	"sword": {"name": "Wayfolk iron sword", "family": "melee", "melee": true, "range": 2.4, "dmg": 18.0, "interval": 1.1,
		"clips": ["ual2/Sword_Regular_A", "ual2/Sword_Regular_B", "ual2/Sword_Regular_C"], "hit_at": 0.32, "model": "res://assets/props/quaternius/Sword_Bronze.gltf", "grip": {"rot": Vector3(0, 0, -90), "off": Vector3.ZERO}, "idle": "ual/Sword_Idle",
		"moves": ["arc_slash"]},
	"warhammer": {"name": "Smith's warhammer", "family": "heavy", "melee": true, "range": 2.7, "dmg": 34.0, "interval": 2.0,
		"clips": ["ual2/Melee_Hook"], "hit_at": 0.55, "model": "res://assets/weapons/fogwright/Warhammer_Iron.glb", "grip": {"rot": Vector3(0, 0, -90), "off": Vector3.ZERO}, "idle": "ual/Sword_Idle",
		"moves": ["ground_slam"]},
	"pistol": {"name": "Flintlock pistol", "family": "gun", "melee": false, "range": 14.0, "dmg": 26.0, "interval": 1.2, "block": false, "spread": [7.0, 1.2, 4.0],
		"clips": ["ual/Pistol_Shoot"], "hit_at": 0.1, "ammo": 2, "model": "res://assets/weapons/fogwright/Pistol_Flintlock.glb", "grip": {"rot": Vector3(0, 0, -90), "off": Vector3.ZERO}, "idle": "ual/Pistol_Idle", "reload": 1.6, "moves": ["scatter_shot"]},
	"shortbow": {"name": "Ash shortbow", "family": "bow", "melee": false, "range": 18.0, "dmg": 12.0, "interval": 0.8, "block": false, "spread": [6.0, 0.8, 2.5],
		"clips": ["ual/Pistol_Shoot"], "hit_at": 0.1, "draw": 1.2, "model": "res://assets/weapons/fogwright/Shortbow_Ash.glb", "grip": {"basis": [Vector3(0, -1, 0), Vector3(0, 0, 1), Vector3(-1, 0, 0)], "off": Vector3.ZERO},   # limbs upright, the belly forward along the fingers
		 "idle": "ual/Pistol_Idle", "moves": ["volley"]},
	"wand": {"name": "Brass wand", "family": "focus", "melee": false, "range": 12.0, "dmg": 14.0, "interval": 1.4, "spread": [5.0, 5.0, 2.0],
		"clips": ["ual/Spell_Simple_Shoot"], "hit_at": 0.25, "model": "res://assets/weapons/fogwright/Wand_Brass.glb", "hand": "hand_l", "grip": {"rot": Vector3(0, 0, 0), "off": Vector3(0, 0.04, 0)},   # the casting hand in the spell clips is the left; it points along the fingers
		 "idle": "ual/Spell_Simple_Idle", "moves": ["fog_bolt"]},
}

## the Fog brute's arms (not a player weapon): an axe and a round shield; their grips checked in the brute's own clips
const ENEMY_ARMS := {
	"fog_axe": {"name": "Fog brute's axe", "clips": ["ual2/Sword_Heavy_Combo"], "hit_at": 0.5, "model": "res://assets/props/quaternius/Axe_Bronze.gltf", "model_scale": 1.4,
		"grip": {"rot": Vector3(0, 0, 180), "slide": Vector3(0, 0.36, 0)},   # the bronze axe's origin is mid-haft: slid so the fist holds its end, head up
		"offhand": "res://assets/props/quaternius/Shield_Wooden.gltf", "offgrip": {"rot": Vector3(0, -90, 0)},   # the boss outward, the forearm behind it
		"check_poses": [["ual2/Idle_Shield", 0.3], ["ual/Walk", 0.3], ["ual2/Shield_OneShot", 0.3], ["ual2/Sword_Heavy_Combo", 0.6]]},
}

## skills: energy, cooldown, what it does; "shards": Fog shards spent (caster foci), raising Fog pressure
const MOVES := {
	"arc_slash": {"name": "Arc slash", "energy": 25.0, "cd": 10.0, "clip": "ual2/Sword_Regular_C", "kind": "line", "len": 9.0, "dmg": 32.0,
		"text": "a magic slash that runs along the ground"},
	"ground_slam": {"name": "Ground slam", "energy": 30.0, "cd": 14.0, "clip": "ual2/Sword_Heavy_Combo", "kind": "circle", "r": 3.6, "dmg": 40.0,
		"text": "hits everything round you; momentum makes it stronger"},
	"scatter_shot": {"name": "Scatter shot", "energy": 20.0, "cd": 12.0, "clip": "ual/Pistol_Shoot", "kind": "cone", "len": 7.0, "dmg": 34.0, "ammo": 1,
		"text": "a cone of shot; uses a load"},
	"volley": {"name": "Volley", "energy": 25.0, "cd": 15.0, "clip": "ual/Pistol_Shoot", "kind": "target", "dmg": 14.0, "count": 3,
		"text": "three arrows at once"},
	"fog_bolt": {"name": "Fog bolt", "energy": 15.0, "cd": 8.0, "clip": "ual/Spell_Simple_Shoot", "kind": "target", "dmg": 38.0, "shards": 1,
		"text": "spends a Fog shard and feeds the Fog"},
}

## momentum (heavy melee): each hit in a row adds this much damage, up to the cap; it fades after a pause
const MOMENTUM_STEP := 0.12
const MOMENTUM_MAX := 0.6
const MOMENTUM_KEEP := 2.5
