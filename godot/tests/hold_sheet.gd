extends Node3D
## how the characters hold their weapons: a row of characters in one pose, each holding the weapon with a different grip,
## so the right one can be picked by eye; then each weapon in its idle, attack and block poses.
##   godot --path . --rendering-driver opengl3 res://tests/hold_sheet.tscn -- out=<png prefix> mode=axes|weapons [weapon=sword]
const BODY := "res://assets/characters/quaternius/Superhero_Male_FullBody.gltf"
func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args(): args[a.split("=")[0]] = a.split("=")[1] if "=" in a else ""
	var out: String = args.get("out", "/tmp/hold")
	var env := WorldEnvironment.new(); env.environment = Environment.new(); env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color(0.72, 0.74, 0.76); env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color(0.8, 0.8, 0.82); env.environment.ambient_light_energy = 0.6; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-40, 30, 0); add_child(sun)
	var cam := Camera3D.new(); cam.fov = 40; add_child(cam)
	var rows: Array = []   # [label, clip, time, weapon id, grip (rotation, offset)]
	if args.get("mode", "axes") == "axes":
		var w: String = args.get("weapon", "sword")
		var rots := [Vector3(0, 0, 0), Vector3(0, 0, 180), Vector3(90, 0, 0), Vector3(-90, 0, 0), Vector3(0, 0, 90), Vector3(0, 0, -90)]
		if args.has("rots"): rots = []; for t in str(args.rots).split(";"): var v := t.split_floats(","); rots.append(Vector3(v[0], v[1], v[2]))
		var off := Vector3.ZERO
		if args.has("off"): var o := str(args.off).split_floats(","); off = Vector3(o[0], o[1], o[2])
		for r in rots:
			for sl in (str(args.get("slides", "0,0,0")).split(";")):
				var v2 := sl.split_floats(",")
				rows.append(["%s slide %s" % [r, sl], args.get("clip", "ual/Sword_Idle"), 0.3, w, {"rot": r, "off": off, "slide": Vector3(v2[0], v2[1], v2[2])}])
	else:
		for w in str(args.get("weapons", "sword,warhammer,pistol,shortbow,wand")).split(","):
			var D2: Dictionary = Weapons.DEFS[w] if Weapons.DEFS.has(w) else Weapons.ENEMY_ARMS[w]
			var g: Dictionary = D2.get("grip", {})
			var poses: Array = D2.get("check_poses", [[D2.get("idle", "ual/Sword_Idle"), 0.3], [D2.clips[0], float(D2.hit_at)], ["ual2/Sword_Block", 0.25]])
			for c in poses:
				rows.append([w + " " + str(c[0]).get_slice("/", 1), c[0], c[1], w, g])
	var x := 0.0
	for r in rows:
		var m: Node3D = (load(BODY) as PackedScene).instantiate(); add_child(m); m.position = Vector3(x, 0, 0); m.rotation_degrees.y = -35
		var ap := CombatRig.animate(m); ap.play(r[1]); ap.seek(r[2], true); ap.pause()
		var W: Dictionary = Weapons.DEFS[r[3]] if Weapons.DEFS.has(r[3]) else Weapons.ENEMY_ARMS[r[3]]
		var g: Dictionary = r[4]
		if args.get("mode", "axes") == "axes" and args.get("hand", "") == "l": CombatRig.hold_weapon(m, {"offhand": W.get("offhand", W.get("model")), "offgrip": g})
		else: CombatRig.hold_weapon(m, W, g)
		var l := Label3D.new(); l.text = r[0]; l.font_size = 28; l.pixel_size = 0.004; l.position = Vector3(x, 2.15, 0); l.modulate = Color(0.1, 0.1, 0.1); add_child(l)
		x += 1.6
	cam.position = Vector3((x - 1.6) / 2.0, 1.4, 3.6 + x * 0.33); cam.look_at(Vector3((x - 1.6) / 2.0, 1.1, 0))
	for i in 6: await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png(out + ".png"); print("saved ", out)
	get_tree().quit()
