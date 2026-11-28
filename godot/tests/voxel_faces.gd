extends Node3D
## the face presets of one people (tools/voxel/make_character.py PRESETS, godot/data/faces.json): men above, women below,
## in their starting clothes, in the game's daylight; front and three-quarter close-ups
##   godot --path . --rendering-driver opengl3 res://tests/voxel_faces.tscn -- out=<png prefix> [people=hrimfolk]
func _ready() -> void:
	var out := "/tmp/faces"; var people := "hrimfolk"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
		if a.begins_with("people="): people = a.split("=")[1]
	var env := WorldEnvironment.new(); env.environment = Environment.new(); var e := env.environment   # as voxel_peoples.gd
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	sm.sky_top_color = Color(0.42, 0.56, 0.74); sm.sky_horizon_color = Color(0.93, 0.78, 0.6); sm.ground_horizon_color = Color(0.93, 0.78, 0.6)
	sm.ground_bottom_color = Color(0.3, 0.3, 0.32)
	e.background_mode = Environment.BG_SKY; e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_energy = 0.45; e.ambient_light_sky_contribution = 0.6
	e.ambient_light_color = Color(0.86, 0.84, 0.8); e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.tonemap_exposure = 0.9; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-30, -30, 0); sun.light_color = Color(1.0, 0.8, 0.58); sun.light_energy = 1.05
	sun.shadow_enabled = true; sun.shadow_bias = 0.25; sun.shadow_normal_bias = 3.0; add_child(sun)
	var row := 0
	for s in ["m", "f"]:
		var list: Array = Equipment.faces().presets["%s_%s" % [people, s]]
		for k in list.size():
			var m := Equipment.dress(people, s, [], true, false, k); add_child(m)
			m.position = Vector3(k * 0.8 + row * 20.0, 0, 0)
			var l := Label3D.new(); l.text = "%d %s" % [k, list[k].name]; l.font_size = 40; l.pixel_size = 0.0018; l.outline_size = 8
			l.position = Vector3(m.position.x, 0.62, 0.3); add_child(l)
		row += 1
	var cam := Camera3D.new(); add_child(cam)
	get_viewport().size = Vector2i(4400, 1800)
	var shots := []
	for r in 2:
		var x := 2.0 + r * 20.0; var sx: String = ["men", "women"][r]
		shots.append(["%s_front" % sx, Vector3(x, 1.2, 4.0), Vector3(x, 1.1, 0)]); shots.append(["%s_threequarter" % sx, Vector3(x + 2.4, 1.3, 3.3), Vector3(x, 1.1, 0)]); shots.append(["%s_back" % sx, Vector3(x, 1.3, -4.0), Vector3(x, 1.1, 0)])
	for sh in shots:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = 34.0
		for k in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
