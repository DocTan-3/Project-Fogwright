extends Node3D
## the voxel building kit (tools/voxel/make_building_kit.py) laid out piece by piece with names, the stylized Hrimfolk
## (1.6 m) beside the door, the window and the stair for scale; prints each piece's size and triangles
##   godot --path . --rendering-driver opengl3 res://tests/building_kit_sheet.tscn -- out=<png prefix>
const KIT := "res://assets/voxel/buildings/kit_farhallow.vox"
func _ready() -> void:
	var out := "/tmp/kit"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sm.sky_top_color = Color(0.36, 0.55, 0.82); sm.sky_horizon_color = Color(0.72, 0.78, 0.86); sm.ground_horizon_color = Color(0.72, 0.78, 0.86); sm.ground_bottom_color = Color(0.3, 0.3, 0.32); sm.sun_angle_max = 20.0; sky.sky_material = sm
	env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	# lit as voxel Farhallow is (scenes/farhallow_voxel.tscn), so the colours read as they will in the village
	var e := env.environment
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_color = Color(0.86, 0.84, 0.8); e.ambient_light_energy = 0.55
	e.ambient_light_sky_contribution = 0.6; e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.ssao_enabled = true; e.ssao_radius = 0.3; e.ssao_intensity = 1.0
	add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-40, 50, 0)   # from the side, so faces read by their shade
	sun.light_energy = 1.15; sun.light_color = Color(1, 0.96, 0.88); sun.shadow_enabled = true; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(120, 60); g.mesh = pm; g.position = Vector3(25, 0, -10)
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color("5f7a3a"); gm.albedo_color = gm.albedo_color * gm.albedo_color; g.material_override = gm; add_child(g)
	var kit := Vox.pieces(KIT)
	var names := kit.keys(); names.sort()
	# rows: walls of 3 m, walls of 4.5 m, everything else
	var rows := [[], [], []]
	for n in names: rows[0 if n.ends_with("_30") and n.begins_with(("wall")) else (1 if n.ends_with("_45") else 2)].append(n)
	var at := {}; var tris := 0
	for r in rows.size():
		var x := 0.0
		for n in rows[r]:
			var mi := MeshInstance3D.new(); mi.mesh = kit[n]; mi.material_override = Vox.material(); add_child(mi)
			var bb: AABB = mi.mesh.get_aabb()
			mi.position = Vector3(x, 0, -r * 8.0); at[n] = mi.position
			var lb := Label3D.new(); lb.text = n; lb.font_size = 48; lb.pixel_size = 0.004; lb.position = mi.position + Vector3(bb.size.x * 0.5, -0.0, 0.6)
			lb.rotation_degrees = Vector3(-90, 0, 0); lb.modulate = Color(1, 1, 1); add_child(lb)
			if n.begins_with("wall_frame"):   # the next bay's post, which closes a timber bay on its right
				var post := MeshInstance3D.new(); post.mesh = kit["post_" + n.get_slice("_", n.get_slice_count("_") - 1)]
				post.material_override = Vox.material(); post.position = mi.position + Vector3(bb.size.x, 0, 0); add_child(post)
			var t: int = mi.mesh.get_faces().size() / 3; tris += t
			print("PIECE %-22s %.2f x %.2f x %.2f m  %d tris" % [n, bb.size.x, bb.size.y, bb.size.z, t])
			x += bb.size.x + 1.2
	print("KIT %d pieces, %d triangles" % [names.size(), tris])
	# the Hrimfolk at the 3 m door, the window and the stair
	for spot in [["wall_frame_door_30", Vector3(1.0, 0, 0.6)], ["wall_frame_window_30", Vector3(1.0, 0, 0.6)], ["stair_30", Vector3(-0.5, 0, -1.0)]]:
		var h := Vox.character("res://assets/voxel/characters/hrim_stylized.vox", Vox.FINE); add_child(h)
		h.position = at[spot[0]] + spot[1]
	var cam := Camera3D.new(); add_child(cam); cam.current = true
	var d: Vector3 = at["wall_frame_door_30"]; var w: Vector3 = at["wall_frame_window_30"]; var s: Vector3 = at["stair_30"]
	for sh in [["overview", Vector3(18, 14, 14), Vector3(18, 0, -6), 60.0], ["door", d + Vector3(1.0, 1.4, 4.2), d + Vector3(1.0, 1.1, 0), 50.0],
			["window", w + Vector3(1.8, 1.5, 3.6), w + Vector3(1.0, 1.2, 0), 50.0], ["stair", s + Vector3(4.0, 3.0, 2.5), s + Vector3(0.7, 1.4, -2.2), 50.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
