extends Node3D
## one weapon type at every tier (make_equipment.py TIERS): drawn in a row from the front, a close shot of the weapons,
## and carried from behind; prints GROUND FAIL for anything below the ground and the triangle counts
##   godot --path . --rendering-driver opengl3 res://tests/voxel_tiers.tscn -- type=sword out=<png prefix> [people=] [sex=]
func _ready() -> void:
	var out := "/tmp/tiers"; var people := "hrimfolk"; var sex := "m"; var type := "sword"
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
	var rack_len := 0.0; var rack_x := 0.0
	var names := ["iron_" + type]
	for t in range(2, 6): names.append("%s_t%d" % [type, t])
	for r in 2:
		for i in names.size():
			var m := Equipment.dress(people, sex, [names[i]], true, r == 0); add_child(m)
			m.position = Vector3(i * 1.3, 0, r * 30.0)
			if r == 1: m.rotation_degrees.y = 180.0
			var low := INF; var tris := 0
			for mi in m.find_children("*", "MeshInstance3D", true, false):
				if not (mi as MeshInstance3D).is_visible_in_tree(): continue
				var bb: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
				for k in 8: low = minf(low, bb.get_endpoint(k).y)
				if String(mi.name).begins_with("weapon"): tris += (mi as MeshInstance3D).mesh.get_faces().size() / 3
			if low < -0.01: print("GROUND FAIL %s on %s_%s: %.3f m below" % [names[i], people, sex, -low])
			print("TIER %s%s: %d triangles" % [names[i], " carried" if r == 1 else "", tris])
			if r == 0:      # the weapon alone on a rack, its flat to the camera, to compare the tiers' detail
				for w in m.find_children("weapon*", "MeshInstance3D", true, false):
					var mi := (w as MeshInstance3D).duplicate() as MeshInstance3D; add_child(mi)
					var box: AABB = mi.get_aabb(); var ax := [0, 1, 2]
					ax.sort_custom(func(a, b): return box.size[a] > box.size[b])
					var lo := Vector3.ZERO; lo[ax[0]] = 1.0; var wi := Vector3.ZERO; wi[ax[1]] = 1.0
					var bs := Basis(lo, wi, lo.cross(wi)); var sc: float = (w as MeshInstance3D).global_transform.basis.get_scale().x
					mi.transform = Transform3D(Basis(Vector3.UP, Vector3.RIGHT, Vector3.UP.cross(Vector3.RIGHT)) * bs.inverse(), Vector3.ZERO).scaled(Vector3.ONE * sc)
					var half: float = box.size[ax[0]] * sc * 0.5; rack_len = maxf(rack_len, 2.0 * half)
					var wide: float = box.size[ax[1]] * sc
					rack_x += maxf(0.45, wide + 0.15) * 0.5
					mi.position = Vector3(rack_x, half + 0.15, -60.0) - mi.transform.basis * box.get_center()
					rack_x += maxf(0.45, wide + 0.15) * 0.5
			var l := Label3D.new(); l.text = "T%d" % (i + 1); l.font_size = 48; l.pixel_size = 0.0025; l.outline_size = 8
			l.position = m.position + Vector3(0, 0.05, 0.8 if r == 0 else -0.8); add_child(l)
	var cam := Camera3D.new(); add_child(cam); get_viewport().size = Vector2i(2400, 1000)
	var cx := (names.size() - 1) * 0.65
	for sh in [["drawn", Vector3(cx + 0.5, 1.3, 5.6), Vector3(cx, 0.9, 0), 40.0],
			["close", Vector3(cx - 0.6, 1.1, 2.6), Vector3(cx - 0.6, 0.95, 0), 40.0],
			["carried", Vector3(cx - 0.5, 1.3, 30.0 + 5.6), Vector3(cx, 0.9, 30.0), 40.0],
			["rack", Vector3(rack_x * 0.5, rack_len * 0.5 + 0.15, -60.0 + maxf(2.1, maxf(rack_len * 1.75, rack_x * 0.9))), Vector3(rack_x * 0.5, rack_len * 0.5 + 0.15, -60.0), 40.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 6: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	print("TIERS done")
	get_tree().quit()
