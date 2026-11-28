## The player's side of the prologue's fights, for voxel bodies (docs/design.md, Combat: action aim everywhere, no
## tab-target): a child of the player.
##   - left click swings the weapon in hand toward where the camera looks: the body turns to the aim, the arm draws back
##     and cuts across, and whatever stands in the arc in reach at the moment of the cut is hit (two swings alternate);
##   - right click held raises a guard: hits from the front take a quarter, at a cost in stamina; a guard raised just
##     before a hit lands is a parry, which staggers the attacker and costs nothing;
##   - Alt (or C) dodges: a quick roll the way you move (back if standing), untouchable for a moment, for stamina;
##   - stamina comes back when you rest; health does not, in a fight.
## The arm poses go through VoxelWalk.extra, so the walk keeps going underneath.
class_name VoxelFighter
extends Node

signal downed
signal hurt(amount: float)
var player: CharacterBody3D
var walk: VoxelWalk
var rig: Node3D
var weapon := ""                 # the item in the main hand ("" bare hands)
var hp := 100.0
var stamina := 100.0
var enabled := true
var invulnerable := false
var min_hp := 0.0                # the first fight teaches: it can hurt you, it cannot down you
var auto_guard := 0.0            # tests: the guard held for this long, as if right click were down
var _swing := -1.0               # time into the current swing, -1 when none
var _side := 1
var _hit_done := false
var _guard := false
var _guard_t := 0.0
var _dodge := 0.0
const SWING := 0.5
const CUT_AT := 0.2
const REACH := 2.1
const ARC := deg_to_rad(65.0)
const DAMAGE := 34.0

func _ready() -> void:
	player = get_parent() as CharacterBody3D
	walk = player.get_node("Walk") as VoxelWalk
	rig = player.camera_rig

func aim_dir() -> Vector3:
	var f := -rig.global_transform.basis.z if rig else -player.global_transform.basis.z
	f.y = 0.0; return f.normalized()

func _physics_process(delta: float) -> void:
	if not (stamina >= 100.0): stamina = minf(100.0, stamina + delta * (8.0 if _guard else 22.0))
	_dodge = maxf(0.0, _dodge - delta)
	invulnerable = _dodge > 0.1
	var can: bool = enabled and not player.frozen
	if can and Input.is_action_just_pressed("attack") and _swing < 0.0 and weapon != "" and _dodge <= 0.0: start_swing()
	auto_guard = maxf(0.0, auto_guard - delta)
	var g: bool = can and (Input.is_action_pressed("block") or auto_guard > 0.0) and weapon != "" and _swing < 0.0
	if g and not _guard: _guard_t = 0.0
	_guard = g; _guard_t += delta
	player.speed_scale = 0.45 if _guard else 1.0
	if can and Input.is_action_just_pressed("dodge") and _dodge <= 0.0 and stamina >= 20.0: dodge()
	var ex := {}
	if _swing >= 0.0:
		_swing += delta
		var t := _swing / SWING
		var wind := clampf(t / 0.35, 0.0, 1.0); var cut := clampf((t - 0.35) / 0.3, 0.0, 1.0)
		# drawn back and up over the shoulder, then cut down and across the body
		ex["arm_upper_r"] = Vector3(lerpf(-150.0 * wind, -40.0, cut), 0, lerpf(-30.0 * wind * _side, 30.0 * _side, cut))
		ex["arm_lower_r"] = Vector3(lerpf(-70.0 * wind, -10.0, cut), 0, 0)
		ex["torso"] = Vector3(lerpf(-6.0 * wind, 10.0, cut), lerpf(25.0 * wind * _side, -30.0 * _side, cut), 0)
		player.face_yaw = atan2(aim_dir().x, aim_dir().z); player.face_lock = 0.1
		if _swing >= CUT_AT + 0.1 and not _hit_done: _hit_done = true; _cut()
		if _swing >= SWING: _swing = -1.0
	elif _guard:
		ex["arm_upper_r"] = Vector3(-80, 0, 30); ex["arm_lower_r"] = Vector3(-70, 0, 0); ex["arm_upper_l"] = Vector3(-60, 0, -30); ex["arm_lower_l"] = Vector3(-80, 0, 0)
		player.face_yaw = atan2(aim_dir().x, aim_dir().z); player.face_lock = 0.1
	elif hp <= 0.0:
		ex["torso"] = Vector3(70, 0, 0); ex["leg_upper_l"] = Vector3(-80, 0, 0); ex["leg_upper_r"] = Vector3(-80, 0, 0); ex["leg_lower_l"] = Vector3(100, 0, 0); ex["leg_lower_r"] = Vector3(100, 0, 0)
	walk.extra = ex
	walk.calm = 0.0 if not ex.is_empty() else 1.0

func start_swing() -> void:
	_swing = 0.0; _hit_done = false; _side = -_side
	player.face_yaw = atan2(aim_dir().x, aim_dir().z); player.face_lock = SWING

func _cut() -> void:
	var me := player.global_position; var f := aim_dir()
	for e in player.get_tree().get_nodes_in_group("fog_enemy"):
		if not is_instance_valid(e) or not e.has_method("take_hit"): continue
		var d: Vector3 = e.global_position - me; d.y = 0.0
		if d.length() > REACH + float(e.get("radius") if e.get("radius") != null else 0.4): continue
		if d.length() > 0.3 and f.angle_to(d.normalized()) > ARC: continue
		e.take_hit(DAMAGE, d.normalized())

func dodge() -> void:
	stamina -= 20.0; _dodge = 0.42; _swing = -1.0
	var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var b := rig.global_transform.basis
	var fw := -b.z; fw.y = 0; fw = fw.normalized(); var rt := b.x; rt.y = 0; rt = rt.normalized()
	var dir := (rt * input.x - fw * input.y)
	if dir.length() < 0.1: dir = -fw
	player.forced = dir.normalized() * 8.5; player.control_lock = 0.32

## a hit from an attacker at `from` (its position); returns what happened: "dodged", "parried", "blocked", "hit"
func take_hit(amount: float, from: Vector3, attacker: Node = null) -> String:
	if invulnerable or hp <= 0.0: return "dodged"
	var to := from - player.global_position; to.y = 0
	var front := to.length() < 0.01 or aim_dir().angle_to(to.normalized()) < deg_to_rad(75.0)
	if _guard and front:
		if _guard_t < 0.25:
			if attacker and attacker.has_method("stagger"): attacker.stagger(1.0)
			return "parried"
		stamina = maxf(0.0, stamina - amount * 1.5)
		if stamina > 0.0:
			hp -= amount * 0.25; hurt.emit(amount * 0.25); _check(); return "blocked"
	hp -= amount; hurt.emit(amount)
	var push := -to.normalized() if to.length() > 0.01 else Vector3.ZERO
	player.forced = push * 4.0; player.control_lock = 0.15
	_check()
	return "hit"

func _check() -> void:
	if min_hp > 0.0: hp = maxf(hp, min_hp)
	if hp <= 0.0:
		hp = 0.0; enabled = false; downed.emit()

func revive(to := 100.0) -> void:
	hp = to; stamina = 100.0; enabled = true
