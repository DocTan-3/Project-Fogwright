## Two cameras (F3 switches); CLOSE, the WoW-style one, is the default. HIGH, Albion-style - a perspective camera high above and looking down at about 50 degrees,
## the cursor free (attacks and aim go toward it), the wheel zooms from 12 to 32 m, the middle mouse button (held) turns the
## view; walls and roofs between the camera and the player, and roofs over the player, are cut away (their shadows stay).
## And CLOSE, the third-person camera: it follows the player from just behind and above the shoulder, turns with the mouse
## (the cursor is captured; Esc frees it and a click takes it back), zooms with the wheel from over the shoulder out to
## WoW's distance (each notch a share of the distance, so zoom is fine close and quick far out), and can tilt up
## steeply to look at what towers over the street. A spring arm keeps it from going through walls.
extends Node3D

@export var target: Node3D
const MIN_PITCH := deg_to_rad(-55.0)   # looking down
const MAX_PITCH := deg_to_rad(70.0)    # looking up at towers
const MIN_DIST := 1.8
const MAX_DIST := 18.0   # WoW's default farthest is about 15 yards (14 m)
var max_dist_override := 0.0   # tests only
var aiming := false     # a gun or bow aimed (right click): the camera comes in over the shoulder and narrows
var shoulder := 0.0    # how far right of the head the camera sits (shooters keep the crosshair clear of their own back)
const SENSITIVITY := 0.005
const FOLLOW := 14.0

var yaw := 0.0
var high := false                # the Albion-style camera (F3 switches); WoW-style by default
var high_dist := 20.0
const HIGH_PITCH := deg_to_rad(-50.0)
const HIGH_MIN := 12.0
const HIGH_MAX := 32.0
var _turning := false
var pitch := deg_to_rad(-12.0)
var distance := 5.0
@onready var arm: SpringArm3D = $SpringArm3D

func _ready() -> void:
	arm.spring_length = distance
	for a in OS.get_cmdline_user_args():
		if a == "camera=close": high = false
	if not high and DisplayServer.get_name() != "headless":
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED   # the mouse turns the camera, as in a third-person game
	_apply_mode()
	if target:
		global_position = target.global_position + Vector3(0, 1.55, 0)

func _apply_mode() -> void:
	# from high above the arm would catch on every roof; the cutaway handles them. Layer 3 (4) is for the camera alone:
	# the building kit's doorways (KitDoor), so indoors the camera stays in the room instead of backing out of the door
	arm.collision_mask = 0 if high else 1 | 4
	if high: Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	elif DisplayServer.get_name() != "headless": Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	if not high: _cut(false)

## where on the screen attacks aim: the cursor in the high camera, the centre (the crosshair) in the close one
func screen_point() -> Vector2:
	var vp := get_viewport()
	return vp.get_mouse_position() if high else vp.get_visible_rect().size / 2.0

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("camera_mode"):
		high = not high; _apply_mode(); return
	if high:
		if event is InputEventMouseButton:
			if event.button_index == MOUSE_BUTTON_MIDDLE: _turning = event.pressed
			elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP: high_dist = maxf(HIGH_MIN, high_dist - 1.5)
			elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN: high_dist = minf(HIGH_MAX, high_dist + 1.5)
		elif event is InputEventMouseMotion and _turning:
			yaw -= event.relative.x * SENSITIVITY
		return
	if event is InputEventKey and event.pressed and event.physical_keycode == KEY_ESCAPE:
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE   # Esc frees the cursor
	elif event is InputEventMouseButton:
		if event.pressed and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED and event.button_index in [MOUSE_BUTTON_LEFT, MOUSE_BUTTON_RIGHT]:
			Input.mouse_mode = Input.MOUSE_MODE_CAPTURED; get_viewport().set_input_as_handled()   # a click takes it back
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_UP:
			distance = max(MIN_DIST, distance / 1.15)
		elif event.pressed and event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			distance = min(MAX_DIST, distance * 1.15)
	elif event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		yaw -= event.relative.x * SENSITIVITY
		pitch = clamp(pitch - event.relative.y * SENSITIVITY, MIN_PITCH, MAX_PITCH)

func _process(delta: float) -> void:
	yaw += (Input.get_action_strength("turn_left") - Input.get_action_strength("turn_right")) * 2.2 * delta   # Q and E turn the view
	if target:
		var want := target.global_position + Vector3(0, 1.55, 0)   # about the shoulders
		global_position = global_position.lerp(want, 1.0 - exp(-FOLLOW * delta))
	if high:
		# zoomed in the view also tilts a little lower, so close up it reads nearer to third person
		var z := (high_dist - HIGH_MIN) / (HIGH_MAX - HIGH_MIN)
		rotation = Vector3(lerpf(deg_to_rad(-38.0), HIGH_PITCH - deg_to_rad(6.0), z), yaw, 0)
		arm.spring_length = lerp(arm.spring_length, high_dist, 1.0 - exp(-10.0 * delta))
		arm.position.x = lerpf(arm.position.x, 0.0, 1.0 - exp(-10.0 * delta))
		var c := arm.get_node_or_null("Camera3D") as Camera3D
		if c: c.fov = lerpf(c.fov, 45.0, 1.0 - exp(-10.0 * delta))
		_cutaway(delta)
		return
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

# ---------------------------------------------------------------- the cutaway (high camera only)
# Every mesh of the level is indexed once by where it stands. Each update, the meshes near the player that the line from the
# camera to the player passes through, or that are a roof (above head height) over where the player stands, show only
# their shadow; the rest are restored.
var _index := {}          # cell -> [MeshInstance3D]
var _hidden := {}         # MeshInstance3D -> its own shadow setting
var _cut_t := 0.0
const CELL := 8.0

func _build_index() -> void:
	var level := get_tree().current_scene.find_child("Level", true, false) if get_tree().current_scene else null
	if level == null: level = get_parent().get_node_or_null("Level")
	if level == null: return
	for m in level.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var b := mi.global_transform * mi.get_aabb()
		if b.size.y < 0.4 or b.size.x > 40.0 or b.size.z > 40.0: continue   # ground and flat things never block the view
		var k := Vector2i(floori(b.get_center().x / CELL), floori(b.get_center().z / CELL))
		if not _index.has(k): _index[k] = []
		_index[k].append(mi)

func _cutaway(delta: float) -> void:
	_cut_t -= delta
	if _cut_t > 0.0 or target == null: return
	_cut_t = 0.1
	if _index.is_empty(): _build_index()
	var cam := arm.get_node_or_null("Camera3D") as Camera3D
	if cam == null: return
	var p := target.global_position
	var head := p + Vector3(0, 1.2, 0); var eye := cam.global_position
	var want := {}
	var c0 := Vector2i(floori(p.x / CELL), floori(p.z / CELL))
	var r := int(ceil(high_dist * 0.8 / CELL)) + 1
	for dx in range(-r, r + 1):
		for dz in range(-r, r + 1):
			for mi in _index.get(Vector2i(c0.x + dx, c0.y + dz), []):
				if not is_instance_valid(mi): continue
				var b: AABB = mi.global_transform * mi.get_aabb()
				var roof_over := b.position.y > p.y + 2.0 and b.grow(0.3).has_point(Vector3(p.x, b.get_center().y, p.z))
				if roof_over or b.grow(0.25).intersects_segment(eye, head): want[mi] = true
	for mi in _hidden.keys():
		if not want.has(mi):
			if is_instance_valid(mi): mi.cast_shadow = _hidden[mi]
			_hidden.erase(mi)
	for mi in want:
		if not _hidden.has(mi):
			_hidden[mi] = mi.cast_shadow; mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY

func _cut(_on: bool) -> void:
	for mi in _hidden.keys():
		if is_instance_valid(mi): mi.cast_shadow = _hidden[mi]
	_hidden.clear()
