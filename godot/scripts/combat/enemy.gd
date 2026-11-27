## A Fog-touched enemy: it closes in, picks an attack its range allows, shows the attack's telegraph on the ground while it
## winds up, and lands the hit at the end of the wind-up; the player's fighter and the rules decide what the hit does.
## Three kinds to test the counters: the husk (strikes, combos, heavy hooks), the brute (charges, shield bashes, heavy
## blows) and the thrower (projectiles from a distance).
class_name FogEnemy
extends CharacterBody3D

const MODEL := "res://assets/characters/quaternius/Superhero_Male_FullBody.gltf"   # the whole body: the "_Head" model is a head only (villagers wear outfits)
const TYPES := {
	"husk": {"name": "Fog husk", "hp": 90.0, "speed": 2.3, "aggro": 16.0, "scale": 1.0, "tint": Color(0.17, 0.16, 0.21),
		"walk": "ual2/Zombie_Walk_Fwd", "idle": "ual2/Zombie_Idle",
		"attacks": [
			{"kind": "strike", "dmg": 14.0, "windup": 0.8, "shape": {"type": "cone", "len": 2.5, "angle": 1.5}, "clip": "ual2/Zombie_Scratch", "range": 2.2, "w": 3.0, "cd": 1.6},
			{"kind": "combo", "dmg": 9.0, "hits": 3, "gap": 0.32, "windup": 0.75, "shape": {"type": "cone", "len": 2.6, "angle": 1.3}, "clip": "ual2/Sword_Regular_Combo", "range": 2.3, "w": 2.0, "cd": 4.0},
			{"kind": "heavy", "dmg": 32.0, "windup": 1.25, "shape": {"type": "cone", "len": 3.0, "angle": 2.2}, "clip": "ual2/Melee_Hook", "range": 2.4, "w": 1.4, "cd": 5.0}]},
	"brute": {"name": "Fog brute", "hp": 240.0, "speed": 3.0, "aggro": 18.0, "scale": 1.28, "tint": Color(0.22, 0.15, 0.14),
		"walk": "ual/Walk", "idle": "ual2/Idle_Shield", "shield": true,
		"attacks": [
			{"kind": "charge", "dmg": 34.0, "windup": 1.1, "shape": {"type": "line", "len": 9.0, "w": 1.9}, "clip": "ual2/Shield_Dash", "range": 9.0, "min": 3.5, "w": 2.0, "cd": 7.0, "dash": true},
			{"kind": "bash", "dmg": 18.0, "windup": 0.6, "shape": {"type": "cone", "len": 2.4, "angle": 1.1}, "clip": "ual2/Shield_OneShot", "range": 2.2, "w": 2.5, "cd": 3.0},
			{"kind": "heavy", "dmg": 42.0, "windup": 1.4, "shape": {"type": "circle", "r": 3.0}, "clip": "ual2/Sword_Heavy_Combo", "range": 2.5, "w": 1.5, "cd": 6.0}]},
	"thrower": {"name": "Fog thrower", "hp": 70.0, "speed": 2.6, "aggro": 20.0, "scale": 0.95, "tint": Color(0.15, 0.18, 0.21), "keep": 7.5,
		"walk": "ual/Walk", "idle": "ual/Idle",
		"attacks": [
			{"kind": "projectile", "dmg": 18.0, "windup": 0.9, "clip": "ual2/OverhandThrow", "range": 16.0, "min": 3.0, "w": 3.0, "cd": 2.2, "speed": 13.0},
			{"kind": "strike", "dmg": 10.0, "windup": 0.7, "shape": {"type": "cone", "len": 2.3, "angle": 1.4}, "clip": "ual/Punch_Jab", "range": 2.0, "w": 2.0, "cd": 1.8}]},
}
const GRAVITY := 14.0

var type := "husk"
var D: Dictionary
var fighter: Fighter
var target: Node3D                # the player
var _ap: AnimationPlayer
var _model: Node3D
var _state := "idle"              # idle, chase, windup, strike, recover, dead
var _t := 0.0
var _atk: Dictionary
var _hits_left := 0
var _tel: Telegraph
var _origin := Vector3.ZERO
var _fwd := Vector3.FORWARD
var _cds := {}
var _dash_v := Vector3.ZERO
var _engaged := false

func _init(kind := "husk") -> void:
	type = kind

func _ready() -> void:
	D = TYPES[type]
	add_to_group("enemies")
	collision_layer = 2; collision_mask = 1   # a layer of their own: the camera's spring arm does not see them as walls
	var col := CollisionShape3D.new(); var cap := CapsuleShape3D.new(); cap.radius = 0.38 * D.scale; cap.height = 1.8 * D.scale
	col.shape = cap; col.position.y = 0.9 * D.scale; add_child(col)
	_model = (load(MODEL) as PackedScene).instantiate(); add_child(_model); _model.scale = Vector3.ONE * D.scale
	var m := StandardMaterial3D.new(); m.albedo_color = D.tint; m.roughness = 0.9
	for mi in _model.find_children("*", "MeshInstance3D", true, false): (mi as MeshInstance3D).material_override = m
	_ap = CombatRig.animate(_model)
	if D.get("shield", false):
		CombatRig.hold(_model, "hand_l", "res://assets/props/quaternius/Shield_Wooden.gltf", 1.0, Vector3(0, 90, 90))
		CombatRig.hold(_model, "hand_r", "res://assets/props/quaternius/Axe_Bronze.gltf", 1.4, Vector3(0, 0, 90))
	fighter = Fighter.new(); fighter.name = "Fighter"; fighter.max_hp = D.hp; fighter.melee = false; add_child(fighter)
	fighter.died.connect(_on_died); fighter.hit_taken.connect(_on_hit)
	_play(D.idle)
	if target == null:
		var ps := get_tree().get_nodes_in_group("player")
		if not ps.is_empty(): target = ps[0]

func display_name() -> String: return D.name

func _play(clip: String, speed := 1.0, blend := 0.15) -> void:
	if _ap.has_animation(clip): _ap.play(clip, blend, speed)

func _face(dir: Vector3, delta: float, rate := 10.0) -> void:
	if dir.length() < 0.01: return
	_model.rotation.y = lerp_angle(_model.rotation.y, atan2(dir.x, dir.z), 1.0 - exp(-rate * delta))

func forward() -> Vector3:
	return Vector3(sin(_model.rotation.y), 0, cos(_model.rotation.y))

func _physics_process(delta: float) -> void:
	for k in _cds: _cds[k] = maxf(0.0, _cds[k] - delta)
	if not is_on_floor(): velocity.y -= GRAVITY * delta
	else: velocity.y = 0.0
	velocity.x = 0.0; velocity.z = 0.0
	if _state == "dead" or target == null: move_and_slide(); return
	var to := target.global_position - global_position; to.y = 0.0; var dist := to.length()
	if fighter.stun > 0.0:   # reeling from a parry, or staggered
		if _tel: _tel.queue_free(); _tel = null
		if _state != "stunned": _state = "stunned"; _play("ual/Hit_Chest", 0.6)
		move_and_slide(); return
	elif _state == "stunned":
		_state = "chase"
	var tdead: bool = target.has_method("is_dead") and target.is_dead()
	if tdead: _state = "idle"; _play(D.idle); move_and_slide(); return
	match _state:
		"idle":
			if dist < D.aggro or _engaged: _state = "chase"
		"chase":
			var atk := _choose(dist)
			if not atk.is_empty():
				_begin(atk, to)
			else:
				var want := to.normalized()
				if dist < 1.4: want = Vector3.ZERO   # close enough: it stands its ground and waits for an attack to come round
				elif D.has("keep") and dist < D.keep: want = -want   # throwers back off to their range
				elif D.has("keep") and dist < D.keep + 3.0: want = Vector3.ZERO
				velocity.x = want.x * D.speed; velocity.z = want.z * D.speed
				_face(to if want == Vector3.ZERO else want, delta)
				_play(D.walk if want != Vector3.ZERO else D.idle)
		"windup":
			_t += delta
			if not _atk.has("shape"): _face(to, delta, 6.0)   # a thrower tracks its target until the throw
			if _t >= _atk.windup: _strike()
		"strike":
			_t += delta
			if _atk.get("dash", false) and _t < 0.32:
				velocity.x = _dash_v.x; velocity.z = _dash_v.z
			if _hits_left > 0 and _t >= _atk.get("gap", 0.3):
				_t = 0.0; _resolve_melee()
			elif _hits_left <= 0 and _t > 0.5:
				_state = "recover"; _t = 0.0
		"recover":
			_t += delta
			if _t > 0.55: _state = "chase"
	move_and_slide()

func _choose(dist: float) -> Dictionary:
	var opts := []; var total := 0.0
	for a in D.attacks:
		if dist <= a.range and dist >= a.get("min", 0.0) and _cds.get(a.clip + a.kind, 0.0) <= 0.0:
			opts.append(a); total += a.w
	if opts.is_empty(): return {}
	var r := randf() * total
	for a in opts:
		r -= a.w
		if r <= 0.0: return a
	return opts[-1]

func _begin(atk: Dictionary, to: Vector3) -> void:
	_atk = atk; _state = "windup"; _t = 0.0; _engaged = true
	_model.rotation.y = atan2(to.x, to.z)
	_origin = global_position; _fwd = forward()
	var clip_len := _ap.get_animation(atk.clip).length if _ap.has_animation(atk.clip) else 1.0
	_play(atk.clip, clampf(clip_len * 0.45 / atk.windup, 0.35, 1.6), 0.1)   # the clip's blow lands about when the wind-up ends
	if atk.has("shape"):
		_tel = Telegraph.new(); get_parent().add_child(_tel)
		_tel.global_position = global_position + Vector3(0, 0.06, 0); _tel.rotation.y = _model.rotation.y
		_tel.setup(atk.shape, atk.kind, atk.windup)

func _strike() -> void:
	_cds[_atk.clip + _atk.kind] = _atk.cd
	_state = "strike"; _t = 0.0
	if _tel: _tel.queue_free(); _tel = null
	if _atk.kind == "projectile":
		var p := FogProjectile.new(); get_parent().add_child(p)
		p.launch(global_position + Vector3(0, 1.5 * D.scale, 0) + forward() * 0.5, target.global_position + Vector3(0, 1.1, 0), _atk, self)
		_hits_left = 0
		return
	if _atk.get("dash", false): _dash_v = _fwd * (_atk.shape.len / 0.32)
	_hits_left = int(_atk.get("hits", 1))
	_resolve_melee()

func _resolve_melee() -> void:
	_hits_left -= 1
	var shape: Dictionary = _atk.shape
	if Telegraph.contains(shape, _origin, _fwd, target.global_position):
		deliver({"dmg": _atk.dmg, "kind": _atk.kind, "source": self})

func deliver(attack: Dictionary) -> void:
	var f: Fighter = target.get_node_or_null("Fighter")
	if f: f.receive(attack)

func _on_hit(r: Dictionary, _a: Dictionary) -> void:
	_engaged = true
	if r.taken > 0.0: CombatText.spawn(get_parent(), global_position + Vector3(0, 2.1 * D.scale, 0), str(roundi(r.taken)), Color(1, 0.9, 0.6))

func _on_died() -> void:
	_state = "dead"
	if _tel: _tel.queue_free(); _tel = null
	_play("ual/Death01", 1.0, 0.1)
	for c in get_children(): if c is CollisionShape3D: c.disabled = true
	remove_from_group("enemies")
	await get_tree().create_timer(8.0).timeout
	queue_free()
