## Health, energy and stamina, and the defence state the rules read (scripts/combat/rules.gd). One per player and enemy.
class_name Fighter
extends Node

signal hit_taken(result: Dictionary, attack: Dictionary)
signal died

@export var max_hp := 220.0
var hp := 220.0
var energy := CombatRules.ENERGY_MAX
var stamina := CombatRules.STAMINA_MAX
var melee := true                 # holding a melee weapon: can parry
var blocking := false
var since_press := 99.0           # seconds since block was last pressed
var dodging := -1.0               # seconds into a dodge, or -1
var stun := 0.0                   # staggered, knocked down or reeling: no actions
var perks := {}
var dead := false
var _rest := 0.0                  # seconds since stamina was last spent

func _ready() -> void:
	hp = max_hp

func spend_stamina(n: float) -> bool:
	if stamina < n: return false
	stamina -= n; _rest = 0.0
	return true

func spend_energy(n: float) -> bool:
	if energy < n: return false
	energy -= n
	return true

func press_block() -> void:
	since_press = 0.0

func _process(delta: float) -> void:
	since_press += delta
	if dodging >= 0.0: dodging += delta
	stun = maxf(0.0, stun - delta)
	_rest += delta
	if _rest > CombatRules.STAMINA_DELAY and not blocking:
		stamina = minf(CombatRules.STAMINA_MAX, stamina + CombatRules.STAMINA_REGEN * delta)
	energy = minf(CombatRules.ENERGY_MAX, energy + CombatRules.ENERGY_REGEN * delta)

## an attack reaches this fighter: the rules decide what it does
func receive(attack: Dictionary) -> Dictionary:
	if dead: return {"outcome": "none", "taken": 0.0}
	var r := CombatRules.resolve(attack, {"dodging": dodging, "blocking": blocking, "since_press": since_press,
		"melee": melee, "stamina": stamina, "perks": perks})
	stamina = maxf(0.0, stamina - r.stamina)
	if r.stamina > 0.0: _rest = 0.0
	if r.outcome == "parried": since_press = 99.0   # one press parries one hit
	hp = maxf(0.0, hp - r.taken)
	stun = maxf(stun, r.stun + (1.3 if r.knockdown else 0.0))
	hit_taken.emit(r, attack)
	if hp <= 0.0 and not dead:
		dead = true; died.emit()
	return r
