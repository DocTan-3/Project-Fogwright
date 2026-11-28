## A voxel character's walk, until real animations exist: its rigid parts swing at their joints with its speed - legs and
## arms in opposition, knees bending on the back swing, a bounce at each step and a lean into the run - easing back to
## the rest pose (Vox.REST) when it stops. A child of the CharacterBody3D; the model is its sibling "Model".
class_name VoxelWalk
extends Node

const STRIDE := 2.2        # metres per full cycle (two steps) at a run
var phase := 0.0
var amount := 0.0          # 0 standing, 1 running
var parts := {}
var model: Node3D
var _base_y := 0.0
var extra := {}            # part name -> degrees added on top (an attack, a block, a scripted pose), set by others
var calm := 1.0           # 1: the walk swings the arms; 0: the arms are left to `extra` (an attack in progress)

func _ready() -> void:
	model = get_parent().get_node("Model")
	parts.clear()
	for n in ["leg_upper_l", "leg_upper_r", "leg_lower_l", "leg_lower_r", "arm_upper_l", "arm_upper_r", "arm_lower_l", "arm_lower_r", "torso", "head"]:
		var p := model.find_child(n, true, false) as Node3D
		if p: parts[n] = p
	_base_y = model.position.y

func _process(delta: float) -> void:
	var body := get_parent() as CharacterBody3D
	var v := Vector2(body.velocity.x, body.velocity.z).length()
	var air := not body.is_on_floor()
	amount = lerpf(amount, clampf(v / 5.4, 0.0, 1.3), 1.0 - exp(-10.0 * delta))
	phase = fmod(phase + TAU * v / STRIDE * delta, TAU)
	var s := sin(phase); var a := amount
	var swing := 38.0 * a; var arm := 30.0 * a
	_rot("leg_upper_l", Vector3(-s * swing, 0, 0)); _rot("leg_upper_r", Vector3(s * swing, 0, 0))
	_rot("leg_lower_l", Vector3(maxf(0.0, s) * 45.0 * a, 0, 0)); _rot("leg_lower_r", Vector3(maxf(0.0, -s) * 45.0 * a, 0, 0))
	_rot("arm_upper_l", Vector3(s * arm, 0, 0)); _rot("arm_upper_r", Vector3(-s * arm * calm, 0, 0))
	_rot("arm_lower_l", Vector3(-25.0 * a, 0, 0)); _rot("arm_lower_r", Vector3(-25.0 * a, 0, 0))
	_rot("torso", Vector3(8.0 * a, s * 4.0 * a, 0)); _rot("head", Vector3(-6.0 * a, -s * 3.0 * a, 0))
	if air:   # tucked in the air
		_rot("leg_upper_l", Vector3(-35, 0, 0)); _rot("leg_upper_r", Vector3(-15, 0, 0))
		_rot("leg_lower_l", Vector3(50, 0, 0)); _rot("leg_lower_r", Vector3(30, 0, 0))
	model.position.y = _base_y + absf(cos(phase)) * 0.05 * a

func _rot(n: String, add: Vector3) -> void:
	if not parts.has(n): return
	var p: Node3D = parts[n]
	var rest: Vector3 = p.get_meta("rest", Vector3.ZERO)
	p.rotation_degrees = p.rotation_degrees.lerp(rest + add + extra.get(n, Vector3.ZERO), 0.5)
