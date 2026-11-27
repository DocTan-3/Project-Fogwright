## The player's side of combat (docs/design.md, Combat): tab-target, auto-attack, two pages of six skills, and the defences.
##   Tab: the nearest enemy (or click one)   R: attack (targets the nearest if none)   1-6: skills   X: the other page
##   F: block (hold) / parry (press just before a hit; melee weapons only)   C: dodge
##   testing: G next weapon, F9 spawn enemies, F5-F8 and F10-F11 toggle skill-tree perks
## Moving pauses attacks but keeps the target; out of range, the character walks into range.
class_name PlayerCombat
extends Node

signal changed

var player: CharacterBody3D
var fighter: Fighter
var weapon := "sword"
var W: Dictionary
var target: Node3D
var engaged := false
var page := 0
var pages := [["", "", "", "", "", ""], ["", "", "", "", "", ""]]
var cds := {}
var ammo := 0
var reloading := 0.0
var momentum := 0.0
var momentum_keep := 0.0
var drawing := -1.0
var shards := 12
var fog_pressure := 0
var _aa := 0.0
var _act := 0.0                 # busy with an attack or a skill
var _pending := []              # [seconds, callable]: hits that land partway through a clip
var _held: Node3D
var _tree: AnimationTree
var _clip_node: AnimationNodeAnimation
const PERK_KEYS := {KEY_F5: "iron_guard", KEY_F6: "slip", KEY_F7: "deflect", KEY_F8: "dash", KEY_F10: "dash_reload", KEY_F11: "steady_guard"}

func _ready() -> void:
	player = get_parent()
	player.add_to_group("player")
	player.collision_mask |= 2   # the player still bumps into enemies
	fighter = Fighter.new(); fighter.name = "Fighter"; fighter.max_hp = 220.0; player.add_child.call_deferred(fighter)
	fighter.hit_taken.connect(_on_hit); fighter.died.connect(_on_died)
	equip(weapon)

func setup_animation(tree: AnimationTree, clip_node: AnimationNodeAnimation) -> void:
	_tree = tree; _clip_node = clip_node

func equip(id: String) -> void:
	weapon = id; W = Weapons.DEFS[id]; fighter.melee = W.melee
	ammo = int(W.get("ammo", 0)); reloading = 0.0; momentum = 0.0; drawing = -1.0
	pages[0] = ["", "", "", "", "", ""]
	for i in W.moves.size(): pages[0][i] = W.moves[i]
	if _held: _held.get_parent().queue_free(); _held = null
	var model: Node3D = player.get_node("Model")
	if W.has("model"): _held = CombatRig.hold(model, "hand_r", W.model, float(W.get("model_scale", 1.0)), Vector3(0, 0, 90))
	changed.emit()

func is_dead() -> bool: return fighter.dead

func _unhandled_input(event: InputEvent) -> void:
	if fighter.dead: return
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT and Input.mouse_mode != Input.MOUSE_MODE_CAPTURED:
		var e := _pick(event.position)
		if e: target = e; engaged = true; changed.emit()
	if event is InputEventKey and event.pressed and not event.echo and PERK_KEYS.has(event.physical_keycode):
		var p: String = PERK_KEYS[event.physical_keycode]
		if fighter.perks.has(p): fighter.perks.erase(p)
		else: fighter.perks[p] = true
		changed.emit()
	if event.is_action_pressed("target_nearest"): target = _nearest(); engaged = target != null; changed.emit()
	elif event.is_action_pressed("attack"):
		if target == null or not is_instance_valid(target): target = _nearest()
		engaged = target != null; changed.emit()
	elif event.is_action_pressed("page_swap"): page = 1 - page; changed.emit()
	elif event.is_action_pressed("dodge"): dodge()
	elif event.is_action_pressed("block"): fighter.press_block()
	elif event.is_action_pressed("weapon_next"): equip(Weapons.LIST[(Weapons.LIST.find(weapon) + 1) % Weapons.LIST.size()])
	elif event.is_action_pressed("spawn_enemies"): spawn_test_enemies()
	for i in 6:
		if event.is_action_pressed("skill_%d" % (i + 1)): cast(pages[page][i])

func _pick(screen: Vector2) -> Node3D:
	var cam := player.get_viewport().get_camera_3d()
	if cam == null: return null
	var from := cam.project_ray_origin(screen); var dir := cam.project_ray_normal(screen)
	var best: Node3D = null; var bd := 1e9
	for e in player.get_tree().get_nodes_in_group("enemies"):
		var c: Vector3 = (e as Node3D).global_position + Vector3(0, 1.0, 0)
		var t := (c - from).dot(dir); if t < 0.0: continue
		var miss := (from + dir * t).distance_to(c)
		if miss < 0.9 and t < bd: bd = t; best = e
	return best

func _nearest() -> Node3D:
	var best: Node3D = null; var bd := 30.0
	for e in player.get_tree().get_nodes_in_group("enemies"):
		var d := (e as Node3D).global_position.distance_to(player.global_position)
		if d < bd: bd = d; best = e
	return best

func _target_ok() -> bool:
	return target != null and is_instance_valid(target) and target.is_in_group("enemies")

func _moving() -> bool:
	return Input.get_vector("move_left", "move_right", "move_forward", "move_back").length() > 0.1

func _play(clip: String, speed := 1.0) -> void:
	if _tree == null or _clip_node == null: return
	_clip_node.animation = clip
	_tree.set("parameters/ground/actrate/scale", speed)
	_tree.set("parameters/ground/act/request", AnimationNodeOneShot.ONE_SHOT_REQUEST_FIRE)

func _face_target() -> void:
	if not _target_ok(): return
	var d := target.global_position - player.global_position
	player.get_node("Model").rotation.y = atan2(d.x, d.z)

func _physics_process(delta: float) -> void:
	for k in cds: cds[k] = maxf(0.0, cds[k] - delta)
	for p in _pending.duplicate():
		p[0] -= delta
		if p[0] <= 0.0: _pending.erase(p); (p[1] as Callable).call()
	_act = maxf(0.0, _act - delta); _aa = maxf(0.0, _aa - delta)
	momentum_keep -= delta
	if momentum_keep <= 0.0: momentum = maxf(0.0, momentum - delta * 0.4)
	if reloading > 0.0:
		reloading -= delta
		if reloading <= 0.0: ammo = int(W.ammo); changed.emit()
	if fighter.dodging >= 0.0 and player.control_lock <= 0.0: fighter.dodging = -1.0
	fighter.blocking = Input.is_action_pressed("block") and fighter.dodging < 0.0 and fighter.stun <= 0.0 and not fighter.dead
	player.speed_scale = 0.4 if fighter.blocking else 1.0
	if _tree: _tree.set("parameters/ground/guard/blend_amount", lerpf(float(_tree.get("parameters/ground/guard/blend_amount")), 1.0 if fighter.blocking else 0.0, 1.0 - exp(-14.0 * delta)))
	if fighter.dead or fighter.stun > 0.0: player.auto_dir = Vector3.ZERO; return
	if not _target_ok():
		target = null; engaged = false; player.auto_dir = Vector3.ZERO; return
	if not engaged or _moving() or fighter.blocking:
		player.auto_dir = Vector3.ZERO; drawing = -1.0; return
	var to := target.global_position - player.global_position; to.y = 0.0
	if to.length() > W.range:
		player.auto_dir = to.normalized(); drawing = -1.0; return   # walk into range
	player.auto_dir = Vector3.ZERO
	_face_target()
	if _act > 0.0: return
	if W.family == "gun" and ammo <= 0:
		if reloading <= 0.0: reloading = W.reload; _play("ual/Pistol_Reload"); _act = W.reload; changed.emit()
		return
	if W.family == "bow":   # the draw: held as long as the bow allows, then loosed; a longer draw hits harder
		if drawing < 0.0: drawing = 0.0; _play("ual/Pistol_Aim_Neutral", 0.6)
		drawing += delta
		if drawing >= W.draw: _auto_attack(1.0 + 1.2 * clampf(drawing / W.draw, 0.0, 1.0)); drawing = -1.0
		return
	if _aa <= 0.0: _auto_attack(1.0)

func _auto_attack(mult: float) -> void:
	_aa = W.interval; _act = minf(W.interval, 0.6)
	var clips: Array = W.clips; _play(clips[randi() % clips.size()], 1.3 if W.melee else 1.0)
	var t := target
	_pending.append([W.hit_at, func(): _land(t, W.dmg * mult)])
	if W.family == "gun": ammo -= 1; changed.emit()

func _land(t: Node3D, dmg: float, kind := "strike") -> void:
	if t == null or not is_instance_valid(t) or not t.is_in_group("enemies"): return
	if W.melee:
		if t.global_position.distance_to(player.global_position) > W.range + 0.8: return
		if W.family == "heavy": dmg *= 1.0 + momentum; momentum = minf(Weapons.MOMENTUM_MAX, momentum + Weapons.MOMENTUM_STEP); momentum_keep = Weapons.MOMENTUM_KEEP; changed.emit()
		(t.get_node("Fighter") as Fighter).receive({"dmg": dmg, "kind": kind})
	else:
		var p := FogProjectile.new(); player.get_parent().add_child(p)
		p.launch(player.global_position + Vector3(0, 1.4, 0) + _fwd() * 0.4, t.global_position + Vector3(0, 1.1, 0), {"dmg": dmg, "speed": 30.0, "kind": kind}, player, "enemies")

func _fwd() -> Vector3:
	var r: float = player.get_node("Model").rotation.y
	return Vector3(sin(r), 0, cos(r))

## a skill: energy, cooldown, and the weapon's quirk (a load for guns, a Fog shard for foci)
func cast(id: String) -> void:
	if id == "" or fighter.dead or fighter.stun > 0.0 or _act > 0.0 or cds.get(id, 0.0) > 0.0: return
	var M: Dictionary = Weapons.MOVES[id]
	if M.kind == "target" and not _target_ok(): target = _nearest()
	if M.kind == "target" and not _target_ok(): return
	if M.has("ammo") and ammo < int(M.ammo): return
	if M.has("shards") and shards < int(M.shards): return
	if not fighter.spend_energy(M.energy): return
	cds[id] = M.cd; _act = 0.6
	if M.has("ammo"): ammo -= int(M.ammo)
	if M.has("shards"): shards -= int(M.shards); fog_pressure += int(M.shards)
	if _target_ok(): _face_target()
	_play(M.clip)
	var origin := player.global_position; var fwd := _fwd()
	match M.kind:
		"line", "circle", "cone":
			var shape := {"type": M.kind, "len": M.get("len", 0.0), "r": M.get("r", 0.0), "w": 2.2, "angle": 1.2}
			var dmg: float = M.dmg * (1.0 + momentum if W.family == "heavy" else 1.0)
			_pending.append([0.35, func():
				for e in player.get_tree().get_nodes_in_group("enemies"):
					if Telegraph.contains(shape, origin, fwd, (e as Node3D).global_position, 0.4):
						(e.get_node("Fighter") as Fighter).receive({"dmg": dmg, "kind": "strike"})])
		"target":
			var t := target
			for i in int(M.get("count", 1)):
				_pending.append([0.25 + i * 0.14, func():
					var p := FogProjectile.new(); player.get_parent().add_child(p)
					p.launch(player.global_position + Vector3(0, 1.4, 0) + _fwd() * 0.4, t.global_position + Vector3(0, 1.1, 0) if is_instance_valid(t) else player.global_position + _fwd() * 10.0, {"dmg": M.dmg, "speed": 26.0, "kind": "strike"}, player, "enemies")])
	changed.emit()

## the defensive move: a roll by default; the "dash" perk makes it a dash (farther and faster); "dash_reload" reloads a gun
func dodge() -> void:
	if fighter.dead or fighter.stun > 0.0 or player.control_lock > 0.0: return
	if not fighter.spend_stamina(CombatRules.DODGE_STAMINA): return
	var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var basis: Basis = player.camera_rig.global_transform.basis if player.camera_rig else player.global_transform.basis
	var f := -basis.z; f.y = 0; f = f.normalized(); var r := basis.x; r.y = 0; r = r.normalized()
	var dir := (r * input.x - f * input.y)
	if dir.length() < 0.1: dir = _fwd()
	dir = dir.normalized()
	var dash: bool = fighter.perks.has("dash")
	player.control_lock = 0.38 if dash else 0.62
	player.forced = dir * (13.0 if dash else 6.4)
	player.get_node("Model").rotation.y = atan2(dir.x, dir.z)
	fighter.dodging = 0.0; _act = 0.0; drawing = -1.0
	_play("ual2/Sword_Dash" if dash else "ual/Roll", 1.4 if dash else 1.15)
	if fighter.perks.has("dash_reload") and W.family == "gun": ammo = int(W.ammo); reloading = 0.0
	changed.emit()

func _on_hit(r: Dictionary, attack: Dictionary) -> void:
	var at: Vector3 = player.global_position + Vector3(0, 2.0, 0)
	var parent := player.get_parent()
	match r.outcome:
		"parried": CombatText.spawn(parent, at, "PARRIED", Color(1, 0.85, 0.3), true); _play("ual2/Sword_Block", 1.6)
		"blocked": CombatText.spawn(parent, at, "BLOCKED %d" % roundi(r.taken), Color(0.8, 0.82, 0.86))
		"dodged": CombatText.spawn(parent, at, "DODGED", Color(0.6, 0.95, 0.7))
		"guard_broken": CombatText.spawn(parent, at, "GUARD BROKEN %d" % roundi(r.taken), Color(1, 0.4, 0.3), true); _play("ual2/Idle_Shield_Break")
		"hit":
			CombatText.spawn(parent, at, str(roundi(r.taken)), Color(1, 0.35, 0.3), r.taken >= 25.0)
			if r.knockdown:
				_play("ual2/Hit_Knockback"); player.control_lock = 1.2
				var src: Node3D = attack.get("source"); if src: player.forced = (player.global_position - src.global_position).normalized() * 3.0
			else: _play("ual/Hit_Chest")
	if r.get("attacker_stun", 0.0) > 0.0:
		var src = attack.get("source")
		if src and is_instance_valid(src) and src.get_node_or_null("Fighter"): (src.get_node("Fighter") as Fighter).stun = maxf((src.get_node("Fighter") as Fighter).stun, r.attacker_stun)
	if r.stun > 0.0: player.control_lock = maxf(player.control_lock, r.stun); player.forced = Vector3.ZERO
	changed.emit()

func _on_died() -> void:
	engaged = false; player.auto_dir = Vector3.ZERO
	if _tree: _tree.active = false
	var ap: AnimationPlayer = player.get_node("Model/AnimationPlayer")
	if ap: ap.play("ual/Death01")
	changed.emit()

## testing: one of each enemy in front of the player
func spawn_test_enemies() -> void:
	var f := _fwd(); var side := f.cross(Vector3.UP)
	var at := [["husk", f * 9.0], ["brute", f * 13.0 + side * 4.0], ["thrower", f * 16.0 - side * 5.0]]
	for a in at:
		var e := FogEnemy.new(a[0]); e.target = player; player.get_parent().add_child(e)
		e.global_position = player.global_position + a[1] + Vector3(0, 0.5, 0)
