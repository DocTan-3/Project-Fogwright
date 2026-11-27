extends Node
## checks every rule in scripts/combat/rules.gd and prints COMBAT-RULES <n> failure(s):
##   godot --headless --path . res://tests/combat_rules.tscn
var fails := 0

func check(name: String, got, want) -> void:
	var ok: bool = (absf(float(got) - float(want)) < 0.001) if (typeof(want) == TYPE_FLOAT or typeof(want) == TYPE_INT) else got == want
	if not ok:
		fails += 1; print("FAIL ", name, ": got ", got, ", want ", want)

func _ready() -> void:
	var R := CombatRules
	var hit := {"dmg": 100.0, "kind": "strike"}
	var idle := {"stamina": 100.0, "melee": true}
	check("no defence: full hit", R.resolve(hit, idle).taken, 100.0)
	var block := {"stamina": 100.0, "melee": true, "blocking": true, "since_press": 2.0}
	var b := R.resolve(hit, block)
	check("block reduces damage", b.taken, 100.0 * R.BLOCK_TAKEN); check("block outcome", b.outcome, "blocked")
	var parry := {"stamina": 100.0, "melee": true, "blocking": true, "since_press": 0.1}
	var p := R.resolve(hit, parry)
	check("parry takes 5%", p.taken, 5.0); check("parry outcome", p.outcome, "parried")
	check("parry drains three times a block", p.stamina, b.stamina * 3.0)
	check("parry stuns the attacker", p.attacker_stun, R.PARRY_STUN)
	var ranged := parry.duplicate(); ranged.melee = false
	check("only melee parries: a gun's timed press is a block", R.resolve(hit, ranged).outcome, "blocked")
	var late := parry.duplicate(); late.since_press = 0.5
	check("a late press is a block", R.resolve(hit, late).outcome, "blocked")
	var tired := parry.duplicate(); tired.stamina = 40.0
	check("too tired to parry: blocks instead", R.resolve(hit, tired).outcome, "blocked")
	var spent := block.duplicate(); spent.stamina = 5.0
	var gb := R.resolve(hit, spent)
	check("no stamina to block: the guard breaks", gb.outcome, "guard_broken"); check("guard broken takes most", gb.taken, 100.0 * R.GUARD_BROKEN_TAKEN)
	var dodge := {"stamina": 100.0, "melee": true, "dodging": 0.1}
	check("dodge a strike", R.resolve(hit, dodge).outcome, "dodged")
	var lateroll := dodge.duplicate(); lateroll.dodging = 0.6
	check("past the untouchable frames, the hit lands", R.resolve(hit, lateroll).outcome, "hit")
	# the natural counters
	var heavy := {"dmg": 100.0, "kind": "heavy"}
	check("heavy goes through a block", R.resolve(heavy, block).outcome, "hit"); check("heavy goes through a parry", R.resolve(heavy, parry).outcome, "hit")
	check("heavy is dodged", R.resolve(heavy, dodge).outcome, "dodged"); check("heavy knocks down", R.resolve(heavy, idle).knockdown, true)
	var combo := {"dmg": 40.0, "kind": "combo"}
	check("a combo cannot be dodged", R.resolve(combo, dodge).outcome, "hit"); check("a combo is parried", R.resolve(combo, parry).outcome, "parried")
	var bash := {"dmg": 30.0, "kind": "bash"}
	check("a bash is parried", R.resolve(bash, parry).outcome, "parried"); check("a bash stuns on a clean hit", R.resolve(bash, idle).stun, 0.9)
	var shot := {"dmg": 50.0, "kind": "projectile"}
	check("a projectile cannot be parried: blocked", R.resolve(shot, parry).outcome, "blocked"); check("a projectile is dodged", R.resolve(shot, dodge).outcome, "dodged")
	# perks change the rules
	var guard := block.duplicate(); guard.perks = {"iron_guard": true}
	check("iron guard: heavy blows can be blocked", R.resolve(heavy, guard).outcome, "blocked")
	var slip := dodge.duplicate(); slip.perks = {"slip": true}
	check("slip: dodge through a combo", R.resolve(combo, slip).outcome, "dodged")
	var defl := parry.duplicate(); defl.perks = {"deflect": true}
	check("deflect: parry a projectile", R.resolve(shot, defl).outcome, "parried")
	var steady := block.duplicate(); steady.perks = {"steady_guard": true}
	check("steady guard: cheaper blocks", R.resolve(hit, steady).stamina, b.stamina * 0.67)
	var dash := {"stamina": 100.0, "dodging": 0.3, "perks": {"dash": true}}
	check("dash: fewer untouchable frames", R.resolve(hit, dash).outcome, "hit")
	print("COMBAT-RULES %d failure(s)" % fails)
	get_tree().quit(1 if fails else 0)
