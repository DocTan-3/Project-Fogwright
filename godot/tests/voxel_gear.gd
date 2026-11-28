extends Node3D
## sample equipment on the stylized Hrimfolk (tools/voxel/make_gear_stylized.py), three loadouts side by side:
##   A pauldrons; B pauldrons, goggles and a toolbelt; C the cyberarm (raised, to show it moves as parts) with its chest
##   implant, a steam tank, goggles, toolbelt and the right pauldron. Front, three-quarter, back, close and Albion shots.
##   godot --path . --rendering-driver opengl3 res://tests/voxel_gear.tscn -- out=<png prefix>
func _ready() -> void:
	var out := "/tmp/gear"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	const C := "res://assets/voxel/characters/"
	const G := "res://assets/voxel/gear/"
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sm.sky_top_color = Color("4f7fe0"); sm.sky_horizon_color = Color("8fb4f0"); sky.sky_material = sm
	env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.environment.ambient_light_energy = 0.85
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC; env.environment.ssao_enabled = true; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-45, -25, 0); sun.light_energy = 1.1; sun.shadow_enabled = true; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(40, 40); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color("6f86b8"); g.material_override = gm; add_child(g)
	var kits := [[G + "hrim_pauldron_l.vox", G + "hrim_pauldron_r.vox"],
		[G + "hrim_pauldron_l.vox", G + "hrim_pauldron_r.vox", G + "hrim_goggles.vox", G + "hrim_toolbelt.vox"],
		[G + "hrim_cyberarm.vox", G + "hrim_pauldron_r.vox", G + "hrim_goggles.vox", G + "hrim_toolbelt.vox", G + "hrim_tank.vox"]]
	var ms := []
	for i in kits.size():
		var m := Vox.character(C + "hrim_stylized.vox", Vox.FINE, [], kits[i]); add_child(m); m.position.x = (i - 1) * 1.1; ms.append(m)
		var tris := 0
		for mi in m.find_children("*", "MeshInstance3D", true, false): tris += (mi as MeshInstance3D).mesh.get_faces().size() / 3
		print("GEAR kit %d: %d triangles, parts %s" % [i, tris, ", ".join(m.find_children("*", "MeshInstance3D", true, false).map(func(n): return n.get_parent().name if n.get_parent() != m else n.name))])
	var arm: Node3D = ms[2].find_child("arm_upper_l", true, false)
	if arm: arm.rotation_degrees.x = -70.0
	var low: Node3D = ms[2].find_child("arm_lower_l", true, false)
	if low: low.rotation_degrees.x = -30.0
	var cam := Camera3D.new(); add_child(cam)
	for sh in [["front", Vector3(0, 1.0, 4.4), Vector3(0, 0.8, 0), 40.0], ["threequarter", Vector3(-2.2, 1.6, 3.2), Vector3(0, 0.8, 0), 40.0],
			["back", Vector3(2.0, 1.5, -3.6), Vector3(0, 0.85, 0), 40.0], ["close", Vector3(0.2, 1.4, 1.6), Vector3(1.15, 1.1, 0), 40.0],
			["albion", Vector3(0, 12.0, 13.0), Vector3(0, 0.8, 0), 45.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
