## Fogwright's combat rules in one place (docs/design.md, Combat > Moves, the bar and defence): what an attack does to a
## defender who is dodging, blocking, parrying or doing nothing, and what that costs them. Pure functions and numbers, so
## tests/combat_rules.gd can check every case without a scene.
##
## Energy pays for skills; stamina pays for defence (dodge, block, parry).
## Everyone can block and parry with the same button: hold it to block, press it just before a hit lands to parry.
## Only a melee weapon can parry; with anything else a well-timed press is a block.
class_name CombatRules
extends RefCounted

# ---------------------------------------------------------------- the defences
const BLOCK_TAKEN := 0.35          # a block lets through 35% of the damage
const PARRY_TAKEN := 0.05          # a parry lets through 5%
const PARRY_WINDOW := 0.22         # seconds before the hit in which a press of block counts as a parry
const BLOCK_STAMINA := [6.0, 0.25] # stamina per blocked hit: base + per point of its damage (a 100-damage hit: 31)
const PARRY_STAMINA := [18.0, 0.75] # a parry drains three times what a block does (93 for that hit: one parry from full)
const GUARD_BROKEN_TAKEN := 0.7    # blocking without the stamina for it: the guard breaks, most of the hit gets through
const GUARD_BREAK_STUN := 1.1      # seconds staggered after a broken guard
const PARRY_STUN := 1.0            # the attacker reels after being parried
const DODGE_STAMINA := 22.0
const DODGE_IFRAMES := 0.38        # untouchable for this long from the start of a roll
const STAMINA_MAX := 100.0
const STAMINA_REGEN := 20.0        # per second, once no defence has been used for STAMINA_DELAY
const STAMINA_DELAY := 0.9
const ENERGY_MAX := 100.0
const ENERGY_REGEN := 6.0

# ---------------------------------------------------------------- attack kinds (from the animation inventory)
## each kind: whether it can be blocked, parried, dodged; what it does on a clean hit; its telegraph colour
const KINDS := {
	"strike":     {"block": true,  "parry": true,  "dodge": true,  "color": Color(0.95, 0.95, 0.9), "label": "strike"},
	"combo":      {"block": true,  "parry": true,  "dodge": false, "color": Color(1.0, 0.82, 0.2), "label": "combo: block or parry"},
	"heavy":      {"block": false, "parry": false, "dodge": true,  "color": Color(0.95, 0.2, 0.15), "label": "heavy: dodge", "knockdown": true},
	"charge":     {"block": false, "parry": false, "dodge": true,  "color": Color(0.95, 0.2, 0.15), "label": "charge: dodge or step aside", "knockdown": true},
	"bash":       {"block": true,  "parry": true,  "dodge": false, "color": Color(1.0, 0.55, 0.1), "label": "bash: parry", "stun": 0.9},
	"projectile": {"block": true,  "parry": false, "dodge": true,  "color": Color(0.35, 0.65, 1.0), "label": "projectile: dodge or block"},
}

## perks from the skill tree that change the rules (docs/design.md: "with the right node an unblockable attack becomes blockable")
const PERKS := {
	"iron_guard": "heavy blows and charges can be blocked",
	"slip": "a dodge also slips through combos and bashes",
	"deflect": "a parry also turns away projectiles (melee only)",
	"steady_guard": "blocking costs a third less stamina",
	"dash": "the dodge is a dash: farther and faster, fewer untouchable frames",
	"dash_reload": "dodging reloads a gun",
}

static func stamina_for(kind_cost: Array, dmg: float, perks: Dictionary, blocking := false) -> float:
	var c: float = kind_cost[0] + kind_cost[1] * dmg
	if blocking and perks.has("steady_guard"): c *= 0.67
	return c

## the outcome of one hit.
##   attack: {dmg, kind}
##   d (the defender): {dodging: seconds into a dodge or -1, blocking: bool, since_press: seconds since block was pressed,
##                      melee: holding a melee weapon, stamina, perks: {name: true}}
## returns {outcome: hit|dodged|blocked|parried|guard_broken, taken, stamina, knockdown, stun, attacker_stun}
static func resolve(attack: Dictionary, d: Dictionary) -> Dictionary:
	var k: Dictionary = KINDS[attack.kind]; var dmg: float = attack.dmg
	var perks: Dictionary = d.get("perks", {})
	var can_block: bool = k.block or (perks.has("iron_guard") and (attack.kind == "heavy" or attack.kind == "charge"))
	var can_parry: bool = d.get("melee", false) and (k.parry or (perks.has("deflect") and attack.kind == "projectile"))
	var can_dodge: bool = k.dodge or (perks.has("slip") and (attack.kind == "combo" or attack.kind == "bash"))
	var iframes: float = DODGE_IFRAMES * (0.7 if perks.has("dash") else 1.0)
	var r := {"outcome": "hit", "taken": dmg, "stamina": 0.0, "knockdown": k.get("knockdown", false), "stun": k.get("stun", 0.0), "attacker_stun": 0.0}
	var dodging: float = d.get("dodging", -1.0)
	if dodging >= 0.0 and dodging <= iframes and can_dodge:
		return {"outcome": "dodged", "taken": 0.0, "stamina": 0.0, "knockdown": false, "stun": 0.0, "attacker_stun": 0.0}
	var stamina: float = d.get("stamina", 0.0)
	var pressed: float = d.get("since_press", 99.0)
	if can_parry and pressed <= PARRY_WINDOW:
		var cost := stamina_for(PARRY_STAMINA, dmg, perks)
		if stamina >= cost:
			return {"outcome": "parried", "taken": dmg * PARRY_TAKEN, "stamina": cost, "knockdown": false, "stun": 0.0, "attacker_stun": PARRY_STUN}
		# not enough for a parry: it falls back to a block below
	if d.get("blocking", false) or pressed <= PARRY_WINDOW:
		if not can_block:
			return r   # an unblockable attack goes through a guard
		var bcost := stamina_for(BLOCK_STAMINA, dmg, perks, true)
		if stamina >= bcost:
			return {"outcome": "blocked", "taken": dmg * BLOCK_TAKEN, "stamina": bcost, "knockdown": false, "stun": 0.0, "attacker_stun": 0.0}
		return {"outcome": "guard_broken", "taken": dmg * GUARD_BROKEN_TAKEN, "stamina": stamina, "knockdown": false, "stun": GUARD_BREAK_STUN, "attacker_stun": 0.0}
	return r
