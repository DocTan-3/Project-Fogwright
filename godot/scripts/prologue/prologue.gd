## The prologue: the fall of Farhallow (lore.md, "The start"; docs/design.md, "The opening"), played in voxel
## Farhallow. Each beat teaches by doing, with a hint at the side for a new control, never a wall of text:
##   1. the calm afternoon: Maren at the well asks for oil for Hollin's waystone lamp (moving, the camera, talking,
##      taking things), then sends bread down to Hew the net-mender;
##   2. the Fog: the gate bell, the colour going out of the world, villagers running for the ship (running);
##   3. the first weapon: Dunn the smith's hatchet in the chopping block, taken and equipped (the equipment screen);
##   4. the first fight: a Fog-warped dog (attack where you look, guard and parry, dodge);
##   5. Hew, half-changed (the grimdark moment, once);
##   6. the Wrought tearing down the gate, seen from the square (never fought: everyone runs);
##   7. the escape through the burning lower town to the last ship, Merrith's gold thread in the compass;
##   then the crossing and Hollin's Cross, as a card: the end of the demo.
## Merrith's touch: the first time the player falls, a warmth lifts them up again.
## For tests: -- auto=1 plays itself (teleporting between beats) and shots=<prefix> saves a frame at each beat.
extends Node

const FHV := preload("res://scripts/voxel/village_dress.gd")
var level: Node3D
var player: CharacterBody3D
var rig: Node3D
var cam: Camera3D
var hud: PrologueHUD
var eq: EquipmentScreen
var fighter: VoxelFighter
var walk: VoxelWalk
var env: Environment
var sun: DirectionalLight3D
var npcs := {}
var pickups := {}             # id -> {"node", "label", "taken"}
var talkable := {}            # npc name -> prompt label, while they have something to say
var _interacted := ""
var _skip := false
var auto := false
var shots := ""
var touched := false
var checkpoint := Vector3.ZERO
var people := "hrimfolk"; var sex := "m"; var face := 1
var dog: FogDog
var beat := 0
var from_beat := 1          # tests: start at a later beat

func O() -> Vector2: return level.fh.ORIGIN
## a spot `d` metres out from building i's door k, past everything the kit built on that side (porch, steps, yard)
func _door_out(i: int, k := 0, d := 1.6, side := 0.0) -> Vector3:
	var b: Dictionary = level.fh.BUILDINGS[i]; var c := Vector2(b.x, b.y); var a: float = b.a
	var dr: Array = b.doors[mini(k, b.doors.size() - 1)]; var l := (Vector2(dr[0], dr[1]) - c).rotated(-a)
	var f: Array = b.get("foot", [-b.w * 0.5, -b.h * 0.5, b.w * 0.5, b.h * 0.5])
	var q: Vector2
	if absf(l.x) / (b.w * 0.5) > absf(l.y) / (b.h * 0.5): q = Vector2((f[2] if l.x > 0 else f[0]) + signf(l.x) * d, l.y + side)
	else: q = Vector2(l.x + side, (f[3] if l.y > 0 else f[1]) + signf(l.y) * d)
	var w := c + q.rotated(a); return P(w.x, w.y)
func P(x: float, y: float) -> Vector3:   # plan metres -> the drawn ground there
	var p := Vector2(x, y); return Vector3(x - O().x, _ground(p), y - O().y)
func _ground(p: Vector2) -> float:
	var top: float = maxf(level.fh.height(p) + 2.5, 3.2)   # from just above the ground: never onto a roof or a porch
	var hit := player.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(Vector3(p.x - O().x, top, p.y - O().y), Vector3(p.x - O().x, top - 8.0, p.y - O().y), 1))
	return hit.position.y if hit else level.fh.height(p)

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1)
		if kv.size() < 2: continue
		match kv[0]:
			"auto": auto = kv[1] == "1"
			"shots": shots = kv[1]
			"people": people = kv[1]
			"sex": sex = kv[1]
			"face": face = int(kv[1])
			"from": from_beat = int(kv[1])
	for act in [["interact", KEY_E], ["inventory", KEY_I], ["dodge", KEY_C]]:
		if not InputMap.has_action(act[0]): InputMap.add_action(act[0])
		var ev := InputEventKey.new(); ev.physical_keycode = act[1]; InputMap.action_add_event(act[0], ev)
	if InputMap.has_action("skill_8"): InputMap.erase_action("skill_8")   # E talks and takes in the prologue
	var root := get_parent()
	level = root.get_node("Level"); player = root.get_node("Player"); rig = root.get_node("CameraRig"); cam = rig.get_node("SpringArm3D/Camera3D")
	env = (root.get_node("WorldEnvironment") as WorldEnvironment).environment; sun = root.get_node("Sun")
	walk = player.get_node("Walk")
	_dress_player(false)
	fighter = VoxelFighter.new(); fighter.name = "Fighter"; player.add_child(fighter)
	fighter.downed.connect(_on_downed); fighter.hurt.connect(func(_a): hud.flash_hurt(0.8))
	hud = PrologueHUD.new(); hud.camera = cam; root.add_child.call_deferred(hud)
	eq = EquipmentScreen.new(); root.add_child.call_deferred(eq)
	await get_tree().process_frame
	await get_tree().physics_frame; await get_tree().physics_frame
	eq.add_item("oil", "Jug of lamp oil", "", Color8(150, 110, 60), "Rendered from fish fat. Hollin's lamp burns it.")
	eq.add_item("bread", "Loaf of barley bread", "", Color8(170, 140, 90), "Still warm from Maren's oven.")
	eq.add_item("hatchet", "Woodsman's hatchet", "main_hand", Color8(110, 110, 120), "Dunn's hatchet, an iron head on an ash haft.\nMain hand. A light, quick weapon.")
	eq.equipped.connect(_on_equipped)
	eq.closed.connect(func(): player.frozen = false)
	_afternoon()
	_villagers()
	_world_items()
	_run()

# ---------------------------------------------------------------- the player
func _dress_player(armed: bool) -> void:
	var holder: Node3D = player.get_node("Model")
	for c in holder.get_children(): holder.remove_child(c); c.queue_free()
	holder.set_script(null)
	var worn := ["hatchet"] if armed else []
	var m := Equipment.dress(people, sex, worn, true, armed, face)
	if m == null: m = Equipment.dress("hrimfolk", "m", worn, true, armed, 1)
	holder.add_child(m)
	walk.model = holder
	walk.call_deferred("_ready")

func _on_equipped(id: String) -> void:
	fighter.weapon = id if id == "hatchet" else (fighter.weapon if id != "" else "")
	if id == "": fighter.weapon = "hatchet" if eq.worn.get("main_hand", "") == "hatchet" else ""
	_dress_player(fighter.weapon != "")
	hud.dot.visible = fighter.weapon != ""

# ---------------------------------------------------------------- light: late afternoon, then the Fog
func _afternoon() -> void:
	sun.rotation_degrees = Vector3(-24, -50, 0); sun.light_color = Color(1.0, 0.84, 0.64); sun.light_energy = 1.1
	env.fog_density = 0.006; env.fog_light_color = Color(0.86, 0.8, 0.72)
	env.adjustment_enabled = true; env.adjustment_saturation = 0.88; env.adjustment_brightness = 1.0; env.adjustment_contrast = 1.0
	var sky := env.sky.sky_material as ProceduralSkyMaterial
	sky.sky_top_color = Color(0.44, 0.56, 0.72); sky.sky_horizon_color = Color(0.9, 0.78, 0.62); sky.ground_horizon_color = Color(0.9, 0.78, 0.62)

func _fog_rolls_in(secs: float) -> void:
	var t := create_tween().set_parallel().set_trans(Tween.TRANS_SINE)
	t.tween_property(env, "fog_density", 0.032, secs)
	t.tween_property(env, "fog_light_color", Color(0.5, 0.53, 0.56), secs)
	t.tween_property(env, "adjustment_saturation", 0.3, secs)
	t.tween_property(env, "adjustment_brightness", 0.82, secs)
	t.tween_property(sun, "light_energy", 0.28, secs)
	t.tween_property(sun, "light_color", Color(0.75, 0.78, 0.82), secs)
	t.tween_property(env, "ambient_light_energy", 0.35, secs)
	var sky := env.sky.sky_material as ProceduralSkyMaterial
	t.tween_property(sky, "sky_top_color", Color(0.32, 0.34, 0.37), secs)
	t.tween_property(sky, "sky_horizon_color", Color(0.45, 0.47, 0.5), secs)
	t.tween_property(sky, "ground_horizon_color", Color(0.45, 0.47, 0.5), secs)
	var lh := level.find_child("LighthouseLamp", true, false) as OmniLight3D
	if lh: t.tween_property(lh, "light_energy", 2.5, secs)
	var gl := level.find_child("LighthouseGlass", true, false) as MeshInstance3D
	if gl: t.tween_property(gl.material_override, "emission_energy_multiplier", 2.0, secs)
	# mist drifting low through the streets round the player (not voxels: fog is never solid)
	var mist := CPUParticles3D.new(); mist.name = "Mist"; mist.amount = 90; mist.lifetime = 9.0; mist.preprocess = 9.0
	mist.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX; mist.emission_box_extents = Vector3(22, 0.8, 22)
	mist.direction = Vector3(-1, 0, -0.6); mist.spread = 15; mist.initial_velocity_min = 0.4; mist.initial_velocity_max = 1.1; mist.gravity = Vector3.ZERO
	mist.scale_amount_min = 3.0; mist.scale_amount_max = 6.0
	var qm := QuadMesh.new(); qm.size = Vector2(1, 1)
	var sh := Shader.new(); sh.code = """
shader_type spatial;
render_mode unshaded, depth_draw_never, cull_disabled;
void vertex() { MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0, 0, 0), vec4(0, length(MODEL_MATRIX[1].xyz), 0, 0), vec4(0, 0, length(MODEL_MATRIX[2].xyz), 0), vec4(0, 0, 0, 1)); }
void fragment() { float d = distance(UV, vec2(0.5)); ALBEDO = vec3(0.62, 0.64, 0.66); ALPHA = smoothstep(0.5, 0.05, d) * 0.22 * COLOR.a; }
"""
	var mm := ShaderMaterial.new(); mm.shader = sh; qm.material = mm; mist.mesh = qm
	var grad := Gradient.new(); grad.set_color(0, Color(1, 1, 1, 0)); grad.add_point(0.3, Color(1, 1, 1, 1)); grad.add_point(0.7, Color(1, 1, 1, 1)); grad.set_color(grad.get_point_count() - 1, Color(1, 1, 1, 0))
	mist.color_ramp = grad
	player.add_child(mist); mist.position = Vector3(0, 0.8, 0); mist.local_coords = false

# ---------------------------------------------------------------- the villagers
func _npc(id: String, people_: String, sex_: String, worn: Array, face_: int, at: Vector3, facing: float, work := "") -> PrologueVillager:
	var v := PrologueVillager.make(people_, sex_, worn, face_, id)
	level.add_child(v); v.global_position = at + Vector3(0, 0.05, 0); v.model.rotation.y = facing; v.player = player; v.working = work
	npcs[id] = v
	return v

func _villagers() -> void:
	_npc("Maren", "wayfolk", "f", [], 2, P(61.6, 48.2), 0.9)
	_npc("Brann", "hrimfolk", "m", [], 3, _door_out(0, 0, 1.4), 1.6)
	_npc("Hew", "ruadhan", "m", [], 4, _door_out(10, 0, 1.4, 1.5), 2.4, "mend")
	_npc("Dunn", "ferrin", "m", ["hammer"], 2, _door_out(4, 0, 1.8, 1.2), 0.6, "hammer")
	_npc("Garr", "hrimfolk", "f", ["spear"], 1, P(64.6, 8.2), 0.0)
	_npc("Ysolde", "ilvari", "f", [], 3, P(87.5, 90.0), PI * 0.5, "mend")
	_npc("Tamsin", "zarhim", "f", [], 2, P(66.5, 47.0), -2.3)
	_npc("Oro", "aurelan", "m", [], 1, P(57.5, 52.2), 2.0)

## the way down to the harbour along the roads, from the square (plan metres), then out along the pier to the ship
const TO_SHIP := [Vector2(64, 50), Vector2(72, 58), Vector2(80, 66), Vector2(84, 74), Vector2(86.6, 79.5), Vector2(87.5, 90), Vector2(87.8, 99.8), Vector2(92.5, 101.0), Vector2(92.5, 103.6)]
func _flee(id: String, from_index := 0, spd := 4.6) -> void:
	var pts := []
	for k in range(from_index, TO_SHIP.size()): pts.append(P(TO_SHIP[k].x, TO_SHIP[k].y))
	var v: PrologueVillager = npcs[id]; v.working = ""; v.go(pts, spd)

# ---------------------------------------------------------------- things to take
func _vbox_node(v: VBox) -> MeshInstance3D:
	var mi := MeshInstance3D.new(); mi.mesh = v.mesh(); mi.material_override = Vox.grain_material(v.size); return mi

func _world_items() -> void:
	var jug := VBox.new(0.025)   # a clay jug with a stopper and a rope handle
	jug.blob(Vector3(0, 0.14, 0), Vector3(0.1, 0.14, 0.1), Color8(150, 104, 70), 0.06); jug.box(Vector3(-0.035, 0.26, -0.035), Vector3(0.035, 0.33, 0.035), Color8(130, 90, 60))
	jug.box(Vector3(-0.025, 0.33, -0.025), Vector3(0.025, 0.36, 0.025), Color8(160, 130, 90)); jug.beam(Vector3(0.05, 0.3, 0), Vector3(0.1, 0.18, 0), 0.025, Color8(156, 138, 106))
	_pickup("oil", "Take the jug of lamp oil", _vbox_node(jug), _door_out(0, 0, 1.0, 1.2))
	var hat := VBox.new(0.025)   # the hatchet, its head bitten into the block
	hat.box(Vector3(-0.015, 0, -0.015), Vector3(0.015, 0.42, 0.015), Color8(150, 120, 80)); hat.box(Vector3(-0.02, 0.0, -0.06), Vector3(0.02, 0.1, 0.05), Color8(90, 92, 96))
	hat.box(Vector3(-0.012, -0.02, -0.08), Vector3(0.012, 0.11, -0.06), Color8(150, 152, 156))
	var hn := _vbox_node(hat)
	var block := level.find_child("ChoppingBlock", true, false) as Node3D
	var at := block.global_position + Vector3(0, 0.48, 0) if block else _door_out(4, 0, 2.6) + Vector3(0, 0.48, 0)
	_pickup("hatchet", "Take the hatchet", hn, at)
	hn.rotation = Vector3(0.0, 0.5, -0.6)

func _pickup(id: String, label: String, n: Node3D, at: Vector3) -> void:
	level.add_child(n); n.global_position = at
	pickups[id] = {"node": n, "label": label, "taken": false, "live": false}

# ---------------------------------------------------------------- interaction
func _process(_d: float) -> void:
	if hud == null or not is_instance_valid(hud) or hud.prompt == null: return
	var best := ""; var bd := 2.3; var label := ""
	var me := player.global_position
	for id in talkable:
		var v: Node3D = npcs[id]; var d := v.global_position.distance_to(me)
		if d < bd: bd = d; best = id; label = talkable[id]
	for id in pickups:
		var pk: Dictionary = pickups[id]
		if pk.taken or not pk.live: continue
		var d: float = (pk.node as Node3D).global_position.distance_to(me)
		if d < bd: bd = d; best = id; label = pk.label
	hud.show_prompt(("[E]  " + label) if best != "" and not player.frozen else "")
	if best != "" and not player.frozen and Input.is_action_just_pressed("interact"): _interacted = best
	if Input.is_action_just_pressed("interact"): _skip = true

func _wait(secs: float) -> void:
	if auto: secs = minf(secs, 0.6)
	await get_tree().create_timer(secs).timeout

func _until(cond: Callable) -> void:
	while not cond.call(): await get_tree().process_frame

## the player comes within r of a point (auto: they are put there)
func _reach(at: Vector3, r := 2.5) -> void:
	if auto:
		await _wait(0.3)
		player.global_position = at + Vector3(0, 0.4, 0); player.velocity = Vector3.ZERO
		await get_tree().physics_frame; await get_tree().physics_frame
	await _until(func():
		var d := player.global_position - at; d.y = 0
		return d.length() < r)

## the player uses E on a villager or a thing (auto: done for them)
func _interact(id: String) -> void:
	_interacted = ""
	if auto:
		var n: Node3D = npcs[id] if npcs.has(id) else pickups[id].node
		await _reach(n.global_position, 1.8); _interacted = id
	await _until(func(): return _interacted == id)
	_interacted = ""

## lines of speech, [who, line]; each holds long enough to read, E moves on
func _say(lines: Array) -> void:
	for l in lines:
		hud.say(l[0], l[1]); _skip = false
		if npcs.has(l[0]): (npcs[l[0]] as PrologueVillager).face(player.global_position)
		var t := 0.0; var need := clampf(String(l[1]).length() * 0.055, 2.0, 7.0) if not auto else 0.25
		while t < need and not (_skip and t > 0.3): await get_tree().process_frame; t += get_process_delta_time()
	hud.say("", "")

func _objective(text: String, at: Variant = null, label := "") -> void:
	hud.set_objective(text)
	if at is Vector3: hud.set_marker("objective", at, Color(0.95, 0.92, 0.82), label)
	else: hud.clear_marker("objective")

## a test frame: the game's own camera, or (looking at something) a camera behind and above the player framing both
func _shot(name_: String, look_at: Variant = null) -> void:
	if shots == "": return
	var sc: Camera3D = null
	if look_at is Vector3:
		_face_camera(look_at)
		sc = Camera3D.new(); sc.fov = 60.0; player.get_parent().add_child(sc)
		var at: Vector3 = look_at; var me := player.global_position + Vector3(0, 1.2, 0)
		var d := at - me; d.y = 0; d = d.normalized() if d.length() > 0.1 else Vector3.FORWARD
		var want := me - d * 4.5 + Vector3(0, 2.2, 0) + d.cross(Vector3.UP) * 1.2
		var hit := player.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(me, want, 1, [player.get_rid()]))
		if not hit.is_empty(): want = me.lerp(hit.position, 0.85)   # not inside a wall
		sc.global_position = want
		sc.look_at(me.lerp(at, 0.35)); sc.current = true
	for k in 12: await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s_%s.png" % [shots, name_])
	if sc: sc.queue_free(); cam.current = true
	print("SHOT ", name_)

func _face_camera(at: Vector3) -> void:
	var d := at - player.global_position; d.y = 0
	rig.yaw = atan2(-d.x, -d.z); rig.pitch = deg_to_rad(-14.0); rig.distance = 5.5
	rig.global_position = player.global_position + Vector3(0, 1.55, 0)

# ---------------------------------------------------------------- the beats
func _run() -> void:
	player.frozen = true
	hud.fade.color.a = 1.0
	hud.card("Farhallow", "The far coast, outside any god's circle.\nThe last afternoon of the year 312.")
	await _wait(3.5); hud.clear_card(); hud.fade_to(0.0, 2.0); await _wait(1.0)
	player.frozen = false
	checkpoint = player.global_position
	if from_beat <= 1: await _beat1()
	if from_beat <= 2: await _beat2()
	else: _fog_rolls_in(0.5); pickups.hatchet.live = true
	if from_beat <= 3: await _beat3()
	else: pickups.hatchet.taken = true; pickups.hatchet.node.visible = false; eq.give("hatchet"); eq.equip("hatchet"); player.global_position = pickups.hatchet.node.global_position + Vector3(2, 0.3, 0)
	if from_beat <= 4: await _beat4()
	if from_beat <= 5: await _beat5()
	if from_beat <= 6: await _beat6()
	await _beat7()
	await _ending()

func _beat1() -> void:
	beat = 1
	hud.show_hint("Move with W A S D.  The mouse turns the view; the wheel zooms.")
	_objective("Talk to Maren at the well", npcs.Maren.global_position + Vector3(0, 2, 0), "Maren")
	talkable["Maren"] = "Talk to Maren"
	await _shot("1a_start", npcs.Maren.global_position)
	await _interact("Maren"); hud.show_hint("")
	await _say([["Maren", "There you are. Hollin's lamp on the waystone has burned dry again, and the ship's due in tonight."],
		["Maren", "Brann has a jug of oil for it at the Gull & Lantern. Fetch it for me? It'll be by his door."]])
	talkable.erase("Maren")
	pickups.oil.live = true
	_objective("Fetch the oil jug from the Gull & Lantern", pickups.oil.node.global_position + Vector3(0, 1, 0), "Oil")
	hud.show_hint("E talks and takes.  Hold Shift to run, Ctrl walks.")
	talkable["Brann"] = "Talk to Brann"
	await _interact("oil"); hud.show_hint("")
	pickups.oil.taken = true; pickups.oil.node.visible = false; eq.give("oil"); talkable.erase("Brann")
	await _say([["Brann", "Mind you don't spill it. Tell Maren the ship's late if it's late - it always is."]])
	_objective("Bring the oil to Maren", npcs.Maren.global_position + Vector3(0, 2, 0), "Maren")
	talkable["Maren"] = "Give Maren the oil"
	await _shot("1b_oil", npcs.Maren.global_position)
	await _interact("Maren")
	eq.take("oil"); talkable.erase("Maren")
	await _say([["Maren", "Bless you. There. Hollin keeps the road, and the road keeps us."],
		["Maren", "One more thing. Take this loaf down to Hew, by the nets. He forgets to eat when he's mending."]])
	eq.give("bread")
	var hew: PrologueVillager = npcs.Hew
	_objective("Take the bread to Hew the net-mender", hew.global_position + Vector3(0, 2, 0), "Hew")
	talkable["Hew"] = "Give Hew the bread"
	await _interact("Hew")
	eq.take("bread"); talkable.erase("Hew")
	await _say([["Hew", "Barley bread. Maren spoils me."], ["Hew", "Listen to the gulls. They've gone quiet. They do that, lately, at dusk."]])
	await _shot("1c_hew", hew.global_position)

func _beat2() -> void:
	beat = 2
	var garr: PrologueVillager = npcs.Garr; garr.working = "ring"
	_bell(); _fog_rolls_in(22.0)
	await _say([["", "(A bell. The gate bell, ringing and ringing.)"], ["Hew", "That's Garr on the bell. That's the Fog."],
		["Hew", "Dunn keeps a hatchet in the block by the smithy. Take it. Then get to the ship - don't wait for me."]])
	var hew: PrologueVillager = npcs.Hew; hew.go([_door_out(10, 0, 0.6), _door_out(10, 0, -1.0)], 1.4)   # inside, to bar his door
	for id in ["Ysolde", "Tamsin", "Oro", "Brann"]: _flee(id, 0 if id != "Ysolde" else 6, 4.2)
	npcs.Dunn.working = ""; npcs.Maren.go([P(64.0, 51.6)], 1.2)
	pickups.hatchet.live = true
	_objective("Take the hatchet from the chopping block", pickups.hatchet.node.global_position + Vector3(0, 1, 0), "Hatchet")
	hud.show_hint("Hold Shift to run.")
	await _wait(6.0)
	await _shot("2a_fog", P(62, 20))

func _beat3() -> void:
	beat = 3
	await _interact("hatchet"); hud.show_hint("")
	pickups.hatchet.taken = true; pickups.hatchet.node.visible = false; eq.give("hatchet")
	_objective("Equip the hatchet (I)")
	hud.show_hint("Press I to open your equipment, then click the hatchet to take it in hand.")
	if auto:
		eq.open(); await _shot("3a_equipment"); eq.equip("hatchet"); eq.close()
	await _until(func(): return fighter.weapon == "hatchet")
	if eq.is_open: await _until(func(): return not eq.is_open)
	hud.show_hint("")
	await _shot("3b_armed", player.global_position + Vector3(4, 0, -4))

func _beat4() -> void:
	beat = 4
	hud.bars.visible = true
	dog = FogDog.new(); dog.name = "FogDog"; level.add_child(dog)
	dog.global_position = _open_spot(7.0, 13.0) + Vector3(0, 0.3, 0); dog.target = player; dog.fighter = fighter
	_objective("Survive", dog.global_position + Vector3(0, 1, 0), "")
	await _say([["", "(Something comes out of the mist, low to the ground. It was a dog, once.)"]])
	hud.show_hint("Left click strikes where you look.\nHold right click to guard: raised just before a bite, it parries.\nAlt or C dodges.")
	checkpoint = player.global_position
	var alive := [true]; dog.died.connect(func(): alive[0] = false)
	var shot_taken := false
	var t_fight := Time.get_ticks_msec()
	while alive[0]:
		if is_instance_valid(dog): hud.set_marker("objective", dog.global_position + Vector3(0, 1, 0))
		if auto:   # the autopilot fights: face the dog and swing when it is near
			if Time.get_ticks_msec() - t_fight > 90000 and is_instance_valid(dog): dog.take_hit(999.0, Vector3.FORWARD)
			var d := dog.global_position - player.global_position
			rig.yaw = atan2(-d.x, -d.z)
			if d.length() < 2.2 and fighter._swing < 0.0 and shot_taken: fighter.start_swing()
			d.y = 0; player.auto_dir = d.normalized() if d.length() > 1.6 else Vector3.ZERO
			if not shot_taken and d.length() < 4.0: shot_taken = true; await _shot("4a_fight", dog.global_position)
		hud.hp_bar.value = fighter.hp; hud.st_bar.value = fighter.stamina
		await get_tree().process_frame
	hud.show_hint(""); player.auto_dir = Vector3.ZERO
	await _wait(1.0)
	await _shot("4b_dead")
	await _say([["", "(It does not get up. Under the matted grey there is a collar.)"]])

func _beat5() -> void:
	beat = 5
	var hew: PrologueVillager = npcs.Hew
	hew.route.clear(); hew.global_position = _door_out(4, 0, 5.0, -2.0) + Vector3(0, 0.1, 0); hew.set_greyed(1.0); hew.working = ""
	hew.face(player.global_position)
	await _wait(0.5)
	await _say([["Hew", "...lad?"], ["Hew", "It's so quiet in here. Go home, lad. Go home. Home. Home."]])
	await _shot("5a_hew", hew.global_position)
	hew.go([player.global_position], 0.9)
	_objective("Get away. Find Maren in the square", P(64, 50) + Vector3(0, 2, 0), "Square")
	hud.show_hint("")
	await _reach(P(64.0, 50.0), 9.0)
	hew.route.clear()

func _beat6() -> void:
	beat = 6
	var w := Wrought.new(); w.name = "Wrought"; level.add_child(w)
	w.global_position = P(62.0, 0.5); w.rotation.y = 0.0; w.scale = Vector3.ONE * 1.5   # facing south, into the village: 16 m, over the roofs
	w.position.y -= 3.0; create_tween().tween_property(w, "position:y", w.position.y + 3.0, 2.5).set_trans(Tween.TRANS_SINE)
	var ft := create_tween(); ft.tween_property(env, "fog_density", 0.011, 2.0)   # the mist parts enough to see it
	player.frozen = true
	await _wait(0.6)
	_face_camera(P(62, 4) + Vector3(0, 6, 0)); rig.pitch = deg_to_rad(4.0)
	await _say([["Maren", "Gods. Oh, gods, look at it."]])
	w.smash()
	await w.smashed
	_gate_falls(); _crash(); _shake(0.8)
	await _shot("6a_wrought", P(62, 4) + Vector3(0, 9, 0))
	await _say([["Maren", "The ship! Run, child! Don't look back!"]])
	create_tween().tween_property(env, "fog_density", 0.03, 3.0)
	_flee("Maren", 0, 4.4); _flee("Dunn", 1, 4.4)
	player.frozen = false

func _beat7() -> void:
	beat = 7
	_fires()
	var ship_at := P(92.5, 103.6)
	_objective("Get to the last ship", ship_at + Vector3(0, 3, 0), "The ship")
	hud.set_marker("thread", ship_at + Vector3(0, 3, 0), PrologueHUD.GOLD)
	hud.show_hint("A thread of gold in the compass. Follow it.")
	checkpoint = player.global_position
	if auto:
		await _reach(P(65, 57), 3.0); await _shot("7a_fires", P(level.fh.BUILDINGS[10].x, level.fh.BUILDINGS[10].y) + Vector3(0, 4, 0))
		await _reach(P(87.5, 92), 3.0); await _shot("7b_pier", ship_at)
	await _reach(ship_at, 2.2)
	hud.show_hint(""); hud.clear_marker("objective"); hud.clear_marker("thread")

func _ending() -> void:
	player.frozen = true
	await _say([["", "(Hands pull you aboard. Ropes are cut. The last ship of Farhallow pulls away from a village on fire.)"]])
	await hud.fade_to(1.0, 2.5).finished
	hud.card("The crossing", "Through the night the Fog thinned behind you, and the colour came back into the world.\nAt dawn, Aldrath's glow rose over the sea.")
	await _wait(7.0); hud.clear_card(); await _wait(1.0)
	hud.card("Hollin's Cross", "Where the world opens.\n\nEnd of the demo. Thank you for playing.\n(Esc quits)")
	await _shot("8_end")
	if auto: get_tree().quit(); return
	await _until(func(): return Input.is_key_pressed(KEY_ESCAPE))
	get_tree().quit()

# ---------------------------------------------------------------- set pieces
func _on_downed() -> void:
	player.frozen = true
	if not touched:   # Merrith's touch: once, a warmth lifts them
		touched = true
		await _wait(1.2)
		hud.flash_glow(1.6)
		var l := OmniLight3D.new(); l.light_color = Color(1.0, 0.85, 0.5); l.light_energy = 3.0; l.omni_range = 5.0; player.add_child(l); l.position.y = 1.2
		create_tween().tween_property(l, "light_energy", 0.0, 3.0).finished.connect(l.queue_free)
		await _say([["", "(A warmth, out of nowhere, like a hand under your arm. You are lifted to your feet.)"]])
		fighter.revive(100.0); player.frozen = false
		hud.set_marker("thread", P(92.5, 103.6) + Vector3(0, 3, 0), PrologueHUD.GOLD)
		return
	await hud.fade_to(1.0, 1.0).finished
	player.global_position = checkpoint + Vector3(0, 0.5, 0); fighter.revive(100.0)
	if is_instance_valid(dog): dog.global_position = checkpoint + Vector3(8, 0.5, 0)
	await hud.fade_to(0.0, 1.0).finished
	player.frozen = false

## somewhere on the roads between `lo` and `hi` metres from the player that it can see (nothing solid between): where
## something comes at them from
func _open_spot(lo: float, hi: float) -> Vector3:
	var space := player.get_world_3d().direct_space_state
	var eye := player.global_position + Vector3(0, 1.0, 0)
	var best := player.global_position + Vector3(lo, 0, 0); var found := false
	for path in level.fh.PATHS:
		for q in path[0]:
			for k in 5:
				var p := (q as Vector2) + Vector2(randf_range(-1, 1), randf_range(-1, 1))
				var at := P(p.x, p.y); var d := at.distance_to(player.global_position)
				if d < lo or d > hi: continue
				var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(eye, at + Vector3(0, 0.6, 0), 1, [player.get_rid()]))
				if hit.is_empty(): return at
	for a in 16:   # else round the player, the first clear line
		var at := player.global_position + Vector3(cos(a * TAU / 16.0), 0, sin(a * TAU / 16.0)) * lo
		at = P(at.x + O().x, at.z + O().y)
		if space.intersect_ray(PhysicsRayQueryParameters3D.create(eye, at + Vector3(0, 0.6, 0), 1, [player.get_rid()])).is_empty(): return at
	return best

func _gate_falls() -> void:
	for k in 2:
		var h := level.find_child("Hinge%d" % k, true, false) as Node3D
		if h == null: continue
		var t := create_tween().set_parallel()
		t.tween_property(h, "rotation", Vector3(-1.45, h.rotation.y + (0.6 if k else -0.6), 0.3 * (1 if k else -1)), 0.6).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		t.tween_property(h, "position", h.position + Vector3(0, 0, 4.0), 0.6)
	for k in 14:   # splinters and stones flung
		var b := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(randf_range(0.2, 0.6), randf_range(0.1, 0.3), randf_range(0.6, 1.6)); b.mesh = bm
		var m := StandardMaterial3D.new(); m.albedo_color = Color8(72, 62, 54); b.material_override = m
		level.add_child(b); b.global_position = P(62, 4.3) + Vector3(randf_range(-3, 3), 2.0, 0)
		var to := b.global_position + Vector3(randf_range(-6, 6), 0, randf_range(3, 12)); to.y = _ground(Vector2(to.x, to.z) + O()) + 0.1
		var t2 := create_tween(); t2.tween_property(b, "global_position", to, randf_range(0.6, 1.1)).set_trans(Tween.TRANS_QUAD)
		create_tween().tween_property(b, "rotation", Vector3(randf() * 6, randf() * 6, randf() * 6), 1.0)

func _fires() -> void:
	# the lower town burns: thatch roofs along the way down (flames and smoke: not voxels)
	for i in [9, 10, 11, 6, 12]:
		var b := level.get_node_or_null("Building%d" % i) as Node3D
		if b == null: continue
		var box := AABB(); var first := true
		for mi in b.find_children("*", "MeshInstance3D", true, false):
			var a := (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
			box = a if first else box.merge(a); first = false
		for k in 3:
			var f := VoxelProps.flame(randf_range(0.9, 1.5), k == 0)
			level.add_child(f); f.global_position = Vector3(box.get_center().x + randf_range(-1.5, 1.5), box.end.y - randf_range(0.6, 1.4), box.get_center().z + randf_range(-1.5, 1.5))
			if k == 0: (f.get_child(f.get_child_count() - 1) as OmniLight3D).light_energy = 4.0; (f.get_child(f.get_child_count() - 1) as OmniLight3D).omni_range = 14.0
		var smoke := CPUParticles3D.new(); smoke.amount = 40; smoke.lifetime = 6.0; smoke.preprocess = 6.0
		smoke.direction = Vector3(-0.4, 1, -0.3); smoke.spread = 12; smoke.initial_velocity_min = 1.5; smoke.initial_velocity_max = 2.5; smoke.gravity = Vector3(-0.3, 0.2, -0.2)
		smoke.scale_amount_min = 1.5; smoke.scale_amount_max = 3.5
		var qm := QuadMesh.new(); var sm := StandardMaterial3D.new(); sm.albedo_color = Color(0.16, 0.15, 0.15, 0.35); sm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		sm.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED; sm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED; qm.material = sm; smoke.mesh = qm
		level.add_child(smoke); smoke.global_position = Vector3(box.get_center().x, box.end.y, box.get_center().z)

func _shake(secs: float) -> void:
	var t := 0.0
	while t < secs:
		cam.h_offset = randf_range(-0.12, 0.12) * (1.0 - t / secs); cam.v_offset = randf_range(-0.1, 0.1) * (1.0 - t / secs)
		await get_tree().process_frame; t += get_process_delta_time()
	cam.h_offset = 0.0; cam.v_offset = 0.0

# ---------------------------------------------------------------- sound, made here (no recordings yet)
func _play(samples: PackedFloat32Array, at: Vector3, db := 0.0) -> void:
	var wav := AudioStreamWAV.new(); wav.format = AudioStreamWAV.FORMAT_16_BITS; wav.mix_rate = 22050; wav.stereo = false
	var bytes := PackedByteArray(); bytes.resize(samples.size() * 2)
	for i in samples.size(): bytes.encode_s16(i * 2, int(clampf(samples[i], -1.0, 1.0) * 30000.0))
	wav.data = bytes
	var p := AudioStreamPlayer3D.new(); p.stream = wav; p.volume_db = db; p.unit_size = 25.0; level.add_child(p); p.global_position = at; p.play()
	p.finished.connect(p.queue_free)

func _bell() -> void:   # a bronze bell: a struck tone with its partials, ringing on, struck again and again
	var sr := 22050; var n := sr * 14; var s := PackedFloat32Array(); s.resize(n)
	var partials := [[1.0, 1.0], [2.0, 0.5], [2.4, 0.35], [3.0, 0.25], [4.2, 0.15]]
	for strike in 9:
		var t0 := int(strike * 1.4 * sr)
		for i in range(t0, mini(n, t0 + sr * 4)):
			var t := float(i - t0) / sr; var v := 0.0
			for p in partials: v += p[1] * sin(TAU * 440.0 * 0.75 * p[0] * t) * exp(-t * (1.2 + p[0] * 0.6))
			s[i] += v * 0.22
	_play(s, P(65.7, 7.1) + Vector3(0, 3, 0), 6.0)

func _crash() -> void:   # timber breaking and stone falling: noise, low and loud, with a few cracks in it
	var sr := 22050; var n := sr * 3; var s := PackedFloat32Array(); s.resize(n); var lp := 0.0
	for i in n:
		var t := float(i) / sr; lp = lerpf(lp, randf_range(-1, 1), 0.08)
		s[i] = lp * 2.2 * exp(-t * 1.6) + (randf_range(-1, 1) * exp(-fmod(t, 0.37) * 30.0) * 0.4 if t < 1.5 else 0.0)
	_play(s, P(62, 4.3) + Vector3(0, 2, 0), 10.0)
