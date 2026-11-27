extends Node3D
## a contact sheet of the props in assets/props/<folder>, palette applied, one picture per folder
##   godot --path . res://tests/props_sheet.tscn -- folders=docks,village2,fogwright out=<png prefix>
func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args(): args[a.split("=")[0]] = a.split("=")[1] if "=" in a else ""
	var out: String = args.get("out", "/tmp/props")
	Palette.current = "hearth"
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR; env.environment.background_color = Color(0.78, 0.8, 0.78)
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; env.environment.ambient_light_color = Color(0.75, 0.75, 0.78); env.environment.ambient_light_energy = 0.7
	add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-50, -35, 0); sun.light_energy = 1.2; add_child(sun)
	var cam := Camera3D.new(); add_child(cam)
	for folder in str(args.get("folders", "fogwright")).split(","):
		var holder := Node3D.new(); add_child(holder)
		var files := []
		for f in DirAccess.get_files_at("res://assets/props/" + folder):
			if f.ends_with(".glb"): files.append(f)
		files.sort()
		var cols := ceili(sqrt(files.size() * 1.6)); var cell := 4.2
		for i in files.size():
			var n: Node3D = load("res://assets/props/%s/%s" % [folder, files[i]]).instantiate()
			holder.add_child(n); Palette.apply(n)
			var aabb := AABB(); var first := true
			for mi in n.find_children("*", "MeshInstance3D", true, false):
				var b: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
				aabb = b if first else aabb.merge(b); first = false
			var s := 3.2 / maxf(maxf(aabb.size.x, aabb.size.z), maxf(aabb.size.y, 0.8)) if maxf(aabb.size.x, aabb.size.z) > 3.2 else 1.0
			n.scale = Vector3.ONE * s
			n.position = Vector3((i % cols) * cell, 0, (i / cols) * cell) - Vector3(aabb.get_center().x, 0, aabb.get_center().z) * s
			var l := Label3D.new(); l.text = files[i].trim_suffix(".glb") + ("  (x%.2f)" % s if s < 1.0 else ""); l.font_size = 40; l.pixel_size = 0.004
			l.position = Vector3((i % cols) * cell, 0.05, (i / cols) * cell + 1.9); l.rotation_degrees.x = -60; l.modulate = Color(0.1, 0.1, 0.1); l.outline_size = 0
			holder.add_child(l)
		var rows := ceili(files.size() / float(cols))
		var c := Vector3((cols - 1) * cell / 2.0, 0, (rows - 1) * cell / 2.0)
		cam.position = c + Vector3(0, maxf(cols, rows) * cell * 0.62, maxf(cols, rows) * cell * 0.55); cam.look_at(c + Vector3(0, 0.6, 0.4))
		cam.fov = 50
		for k in 6: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, folder])
		holder.queue_free()
	get_tree().quit()
