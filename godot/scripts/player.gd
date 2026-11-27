## The player: a third-person character that runs by default (walk is a toggle), sprints, jumps and turns to face where it
## moves, relative to the camera. Speeds match how far each animation's feet actually travel, so the feet never slide.
extends CharacterBody3D

# measured from the animations' root motion (Quaternius Universal Animation Library; Godot's importer drops the
# clips' "_Loop" suffix and loops them)
const WALK_SPEED := 1.6     # Walk_Loop travels 0.97 m/s; played a little faster
const RUN_SPEED := 5.36    # Jog_Fwd_Loop
const SPRINT_SPEED := 8.25 # Sprint_Loop
const WALK_ANIM_SPEED := 0.97
const ACCEL := 10.0
const TURN_SPEED := 12.0
const JUMP_VELOCITY := 5.0
const GRAVITY := 14.0

@export var camera_rig: Node3D

var walking := false
var _anim: AnimationPlayer
var _model: Node3D
var _air_time := 0.0
var _landing := 0.0

func _ready() -> void:
	_model = $Model

func _find_anim_player() -> AnimationPlayer:
	# the character model has no animations of its own; the library's AnimationPlayer is added beside it (see main.gd)
	return $Model.get_node_or_null("AnimationPlayer") as AnimationPlayer

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("walk_toggle"):
		walking = not walking

func _physics_process(delta: float) -> void:
	var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var basis := camera_rig.global_transform.basis if camera_rig else global_transform.basis
	var forward := -basis.z; forward.y = 0.0; forward = forward.normalized()
	var right := basis.x; right.y = 0.0; right = right.normalized()
	var dir := (right * input.x - forward * input.y)
	if dir.length() > 1.0:
		dir = dir.normalized()

	var speed := RUN_SPEED
	if walking:
		speed = WALK_SPEED
	if Input.is_action_pressed("sprint") and not walking:
		speed = SPRINT_SPEED
	var target := dir * speed
	velocity.x = lerp(velocity.x, target.x, 1.0 - exp(-ACCEL * delta))
	velocity.z = lerp(velocity.z, target.z, 1.0 - exp(-ACCEL * delta))

	if is_on_floor():
		if Input.is_action_just_pressed("jump"):
			velocity.y = JUMP_VELOCITY
			if _tree: (_tree.get("parameters/playback") as AnimationNodeStateMachinePlayback).travel("takeoff")   # at once, not when airborne
	else:
		velocity.y -= GRAVITY * delta

	var was_in_air := not is_on_floor()
	move_and_slide()
	if was_in_air and is_on_floor() and _air_time > 0.35:
		_landing = 0.25
	_air_time = 0.0 if is_on_floor() else _air_time + delta
	_landing = max(0.0, _landing - delta)

	if dir.length() > 0.05:   # face where we go
		var want := atan2(dir.x, dir.z)
		_model.rotation.y = lerp_angle(_model.rotation.y, want, 1.0 - exp(-TURN_SPEED * delta))
	_animate(Vector2(velocity.x, velocity.z).length())

var _tree: AnimationTree
var _blend := 0.0
var _state := ""
var _state_time := 0.0   # how long the animation state machine has been in its current state

func setup_animation(ap: AnimationPlayer, tree: AnimationTree) -> void:
	_anim = ap; _tree = tree

## where the feet would naturally travel at a point of the blend space (the clips' own speeds, measured from root motion)
func _natural(pos: float) -> float:
	if pos <= WALK_SPEED: return lerpf(0.0, WALK_ANIM_SPEED, pos / WALK_SPEED)
	if pos <= RUN_SPEED: return lerpf(WALK_ANIM_SPEED, RUN_SPEED, (pos - WALK_SPEED) / (RUN_SPEED - WALK_SPEED))
	return lerpf(RUN_SPEED, SPRINT_SPEED, clampf((pos - RUN_SPEED) / (SPRINT_SPEED - RUN_SPEED), 0.0, 1.0))

func _animate(ground_speed: float) -> void:
	if not _tree:
		return
	var dt := get_physics_process_delta_time()
	_blend = lerpf(_blend, ground_speed, 1.0 - exp(-12.0 * dt))       # eased, so the mix never jumps
	_tree.set("parameters/ground/loco/blend_position", _blend)
	var nat := _natural(_blend)
	_tree.set("parameters/ground/rate/scale", clampf(_blend / nat, 0.7, 1.8) if _blend > 0.25 and nat > 0.01 else 1.0)
	var pb: AnimationNodeStateMachinePlayback = _tree.get("parameters/playback")
	var state := pb.get_current_node()
	if state != _state:
		_state = state; _state_time = 0.0
	_state_time += dt
	if not is_on_floor() and _air_time > 0.12:
		if state == "ground" or state == "land":
			pb.travel("takeoff" if velocity.y > 1.0 else "fall")
		elif state == "takeoff" and _state_time > 0.72:   # only a real drop falls; a jump lands from its take-off
			pb.travel("fall")
	elif is_on_floor():
		if state == "fall" or state == "takeoff":
			# landing standing still plays the landing; landing on the move runs straight on
			pb.travel("land" if ground_speed < 1.0 else "ground")
		elif state == "land" and (ground_speed > 1.0 or _state_time > 0.45):
			pb.travel("ground")   # a short landing, cut as soon as you move on
