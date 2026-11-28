extends Node3D
## bow rest holds A-D side by side (Equipment.BOW_POSES) (make_equipment.py TIERS): drawn in a row from the front, a close shot of the weapons,
## and carried from behind; prints GROUND FAIL for anything below the ground and the triangle counts
##   godot --path . --rendering-driver opengl3 res://tests/bow_poses.tscn -- type=bow_t3 out=<png prefix> [people=] [sex=]
func _ready() -> void:
	var out := "/tmp/tiers"; var people := "hrimfolk"; var sex := "m"; var type := "bow_t3"
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=")
		match kv[0]:
			"out": out = kv[1]
			"people": people = kv[1]
			"sex": sex = kv[1]
			"type": type = kv[1]
	var env := WorldEnvironment.new(); env.environment = Environment.new(); var e := env.environment
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	sm.sky_top_color = Color(0.42, 0.56, 0.74); sm.sky_horizon_color = Color(0.93, 0.78, 0.6); sm.ground_horizon_color = Color(0.93, 0.78, 0.6)
	e.background_mode = Environment.BG_SKY; e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_energy = 0.5; e.ambient_light_sky_contribution = 0.6
	e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.tonemap_exposure = 0.9; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-35, -25, 0); sun.light_color = Color(1.0, 0.82, 0.62); sun.light_energy = 1.05
	sun.shadow_enabled = true; sun.shadow_bias = 0.25; sun.shadow_normal_bias = 3.0; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(200, 200); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color(0.36, 0.42, 0.26); g.material_override = gm; add_child(g)
	var poses := ["E", "F", "G", "H"]
	for r in 2:
		for i in poses.size():
			Equipment.bow_pose = poses[i]
			var m := Equipment.dress(people, sex, [type, "quiver"], true, true); add_child(m)
			m.position = Vector3(i * 1.4, 0, r * 30.0)
			if r == 1: m.rotation_degrees.y = -60.0      # the bow side toward the camera
			var l := Label3D.new(); l.text = poses[i]; l.font_size = 64; l.pixel_size = 0.0025; l.outline_size = 8
			l.position = m.position + Vector3(0, 0.05, 0.8); add_child(l)
	Equipment.bow_pose = ""
	var cam := Camera3D.new(); add_child(cam); get_viewport().size = Vector2i(2400, 1000)
	var cx := 2.1
	for sh in [["front", Vector3(cx + 1.2, 1.3, 5.4), Vector3(cx, 0.85, 0)], ["turned", Vector3(cx + 1.2, 1.3, 30.0 + 5.4), Vector3(cx, 0.85, 30.0)]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = 40.0
		for k in 6: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	print("POSES done")
	get_tree().quit()
