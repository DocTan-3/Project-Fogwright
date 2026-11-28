extends Node3D
## the ported Ferrin buildings (scripts/ferrin_kit.gd) in a row on open ground, a picture of the row and one of each
##   godot --path . --rendering-driver opengl3 res://tests/ferrin_sheet.tscn -- out=<png prefix> [only=forge,shop]
func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args(): args[a.split("=")[0]] = a.split("=")[1] if "=" in a else ""
	var out: String = args.get("out", "/tmp/ferrin")
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.environment.ambient_light_energy = 0.8
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-38, -40, 0); sun.light_energy = 1.3; sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 120.0; add_child(sun)
	var ground := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(260, 80); ground.mesh = pm
	var gmat := StandardMaterial3D.new(); gmat.albedo_color = Color("5e554b"); ground.material_override = gmat; add_child(ground)
	var kinds: Array = Array(str(args.get("only", "")).split(",", false)) if args.get("only", "") != "" else FerrinKit.BUILDINGS.keys()
	var x := 0.0; var at := {}
	for k in kinds:
		var w: float = (FerrinKit.BUILDINGS[k].plot as Vector2).x * float(FerrinKit.BUILDINGS[k].get("scale", 1.0))
		var b := FerrinKit.instance(k); add_child(b)
		x += w / 2.0; b.position = Vector3(x, 0, 0); at[k] = x; x += w / 2.0 + 3.0
		var l := Label3D.new(); l.text = k; l.font_size = 96; l.pixel_size = 0.01; l.position = Vector3(at[k], 0.05, 13.5)
		l.rotation_degrees.x = -90; l.modulate = Color(0.95, 0.92, 0.85); add_child(l)
	var cam := Camera3D.new(); cam.fov = 50; add_child(cam)
	var shots := [["row", Vector3(x / 2.0, 26.0, 62.0), Vector3(x / 2.0, 4.0, 0.0)]]
	for k in kinds:
		var s := float(FerrinKit.BUILDINGS[k].get("scale", 1.0)); var d := maxf((FerrinKit.BUILDINGS[k].plot as Vector2).x, 8.0) * s
		shots.append([k, Vector3(at[k] + d * 0.7, d * 0.45 + 2.0, d * 1.35 + 4.0), Vector3(at[k], d * 0.28 + 1.5, 0.0)])
	for sh in shots:
		cam.position = sh[1]; cam.look_at(sh[2])
		for i in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
		print("saved ", out, "_", sh[0])
	get_tree().quit()
