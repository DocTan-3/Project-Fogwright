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
	_anim = _find_anim_player()
	if _anim:
		_anim.playback_default_blend_time = 0.18

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

func _animate(ground_speed: float) -> void:
	if not _anim:
		return
	var clip := "Idle"
	var rate := 1.0
	if not is_on_floor() and _air_time > 0.12:
		clip = "Jump" if velocity.y < 1.0 else "Jump_Start"
	elif _landing > 0.0:
		clip = "Jump_Land"
	elif ground_speed > (RUN_SPEED + SPRINT_SPEED) * 0.5:
		clip = "Sprint"; rate = ground_speed / SPRINT_SPEED
	elif ground_speed > (WALK_SPEED + RUN_SPEED) * 0.5:
		clip = "Jog_Fwd"; rate = ground_speed / RUN_SPEED
	elif ground_speed > 0.3:
		clip = "Walk"; rate = ground_speed / WALK_ANIM_SPEED
	var full := "ual/" + clip
	if _anim.current_animation != full:
		_anim.play(full)
	_anim.speed_scale = clamp(rate, 0.5, 2.0)
