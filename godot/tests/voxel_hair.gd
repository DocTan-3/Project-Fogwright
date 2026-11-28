extends Node3D
## hair and beards as the creator's own choices (data/faces.json styles and hair_colours): one people's face 0 with each
## hair style in turn, each beard, and each hair colour; front and back
##   godot --path . --rendering-driver opengl3 res://tests/voxel_hair.tscn -- out=<png prefix> [people=hrimfolk]
func _ready() -> void:
	var out := "/tmp/hair"; var people := "hrimfolk"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
		if a.begins_with("people="): people = a.split("=")[1]
	var env := WorldEnvironment.new(); env.environment = Environment.new(); var e := env.environment
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	sm.sky_top_color = Color(0.42, 0.56, 0.74); sm.sky_horizon_color = Color(0.93, 0.78, 0.6); sm.ground_horizon_color = Color(0.93, 0.78, 0.6)
	e.background_mode = Environment.BG_SKY; e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_energy = 0.45; e.ambient_light_sky_contribution = 0.6
	e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.tonemap_exposure = 0.9; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-30, -30, 0); sun.light_color = Color(1.0, 0.8, 0.58); sun.light_energy = 1.05
	sun.shadow_enabled = true; sun.shadow_bias = 0.25; sun.shadow_normal_bias = 3.0; add_child(sun)
	var st: Dictionary = Equipment.faces().styles[people]; var cols: Array = Equipment.faces().hair_colours[people]
	var rows := [["m", "hair"], ["m", "beard"], ["f", "hair"], ["f", "colour"]]
	var r := 0
	for row in rows:
		var looks := []
		match row[1]:
			"hair": for h in st.hair + ([] if "shaved" in st.hair else ["shaved"]): looks.append({"hair": h})
			"beard": for b in st.beard: looks.append({"beard": b})
			"colour": for c in cols: looks.append({"hair_col": c})
		for k in looks.size():
			var m := Equipment.dress(people, row[0], [], true, false, 0, 0.0, 0.0, looks[k]); add_child(m)
			m.position = Vector3(k * 0.75 + r * 50.0, 0, 0)
			var l := Label3D.new(); l.text = str(looks[k].values()[0]); l.font_size = 36; l.pixel_size = 0.0018; l.outline_size = 8
			l.position = m.position + Vector3(0, 0.55, 0.4); add_child(l)
		r += 1
	var cam := Camera3D.new(); add_child(cam); get_viewport().size = Vector2i(3600, 900)
	for i in rows.size():
		for side in [["front", 1.0], ["back", -1.0]]:
			cam.position = Vector3(2.6 + i * 50.0, 1.3, side[1] * 3.4); cam.look_at(Vector3(2.6 + i * 50.0, 1.15, 0)); cam.fov = 34.0
			for k in 6: await get_tree().process_frame
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png("%s_%s_%d_%s.png" % [out, people, i, side[0]])
	print("HAIR done")
	get_tree().quit()
