## The close third-person camera: it follows the player from just behind and above the shoulder, turns with the mouse
## (the cursor is captured; Esc frees it and a click takes it back), zooms a little with the wheel (never far out: the world is seen from street level), and can tilt up
## steeply to look at what towers over the street. A spring arm keeps it from going through walls.
extends Node3D

@export var target: Node3D
const MIN_PITCH := deg_to_rad(-55.0)   # looking down
const MAX_PITCH := deg_to_rad(70.0)    # looking up at towers
const MIN_DIST := 1.8
const MAX_DIST := 5.5
var max_dist_override := 0.0   # tests only
var aiming := false     # a gun or bow aimed (right click): the camera comes in over the shoulder and narrows
var shoulder := 0.0    # how far right of the head the camera sits (shooters keep the crosshair clear of their own back)
const SENSITIVITY := 0.005
const FOLLOW := 14.0

var yaw := 0.0
var pitch := deg_to_rad(-12.0)
var distance := 3.6
@onready var arm: SpringArm3D = $SpringArm3D

func _ready() -> void:
	arm.spring_length = distance
	if not OS.has_feature("editor") or DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED   # the mouse turns the camera, as in a third-person game
	if target:
		global_position = target.global_position + Vector3(0, 1.55, 0)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and event.physical_keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE   # Esc frees the cursor
	elif event is InputEventMouseButton:
		if event.pressed and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED and event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED; get_viewport().set_input_as_handled()   # a click takes it back
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP:
			distance = max(MIN_DIST, distance - 0.4)
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			distance = min(MAX_DIST, distance + 0.4)
	elif event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		yaw -= event.relative.x * SENSITIVITY
		pitch = clamp(pitch - event.relative.y * SENSITIVITY, MIN_PITCH, MAX_PITCH)

func _process(delta: float) -> void:
	yaw += (Input.get_action_strength("turn_left") - Input.get_action_strength("turn_right")) * 2.2 * delta   # Q and E turn the view
	if target:
		var want := target.global_position + Vector3(0, 1.55, 0)   # about the shoulders
		global_position = global_position.lerp(want, 1.0 - exp(-FOLLOW * delta))
	rotation = Vector3(pitch, yaw, 0)   # negative pitch tilts down, so the camera sits above, looking down at the shoulders
	# looking up, the camera slides in toward the head (as WoW's does) instead of sinking into the ground behind
	var up := clampf(pitch / MAX_PITCH, 0.0, 1.0)
	var want_len: float = distance * lerpf(1.0, 0.35, up)
	if aiming: want_len = minf(want_len, 1.9)
	arm.spring_length = lerp(arm.spring_length, want_len, 1.0 - exp(-10.0 * delta))
	var k := 1.0 - exp(-10.0 * delta)
	arm.position.x = lerpf(arm.position.x, shoulder * (1.25 if aiming else 1.0), k)
	var cam := arm.get_node_or_null("Camera3D") as Camera3D
	if cam: cam.fov = lerpf(cam.fov, 50.0 if aiming else 65.0, k)
