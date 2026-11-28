extends Node3D
## the Medieval Voxel Assets (CC0) beside the stylized Hrimfolk, for scale and style: a little street, close and Albion shots
##   godot --path . --rendering-driver opengl3 res://tests/medieval_lineup.tscn -- out=<png prefix>
func _ready() -> void:
	var out := "/tmp/med"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	const M := "res://assets/buildings/medieval_voxel/"
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sm.sky_top_color = Color("4f7fe0"); sm.sky_horizon_color = Color("a9c4ee"); sky.sky_material = sm
	env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.environment.ambient_light_energy = 0.8
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC; env.environment.ssao_enabled = true; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-50, -35, 0); sun.light_energy = 1.15; sun.shadow_enabled = true; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(80, 80); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color("6d8a4a"); g.material_override = gm; add_child(g)
	for it in [["Houses/House_1", Vector3(-6, 0, -7), 0.0], ["Houses/House_2", Vector3(0.5, 0, -7.5), 0.0], ["Shops/Shop_Simple", Vector3(5, 0, -3), -20.0],
			["Houses/House_3", Vector3(9, 0, -6), 0.0], ["Lamps/Lamp_Ground_Large", Vector3(2.5, 0, -1.2), 0.0], ["Others/Cart_Straight", Vector3(-3.5, 0, 0.5), 70.0],
			["Others/Sing_Post", Vector3(-1.2, 0, 0.8), 15.0], ["Walls/Wall_Simple", Vector3(-1, 0, -14), 0.0], ["Towers/Tower_Simple", Vector3(-8, 0, -15), 0.0]]:
		var n := Vox.prop(M + it[0] + ".glb"); add_child(n); n.position = it[1]; n.rotation_degrees.y = it[2]
	const G := "res://assets/voxel/gear/"
	var kits := [[G + "hrim_pauldron_l.vox", G + "hrim_pauldron_r.vox", G + "hrim_goggles.vox", G + "hrim_toolbelt.vox"],
		[G + "hrim_cyberarm.vox", G + "hrim_pauldron_r.vox", G + "hrim_tank.vox"]]
	for i in 2:
		var c := Vox.character("res://assets/voxel/characters/hrim_stylized.vox", Vox.FINE, [], kits[i]); add_child(c)
		c.position = Vector3(0.2 + i * 1.3, 0, 0.6); c.rotation_degrees.y = 15 - i * 30
	var cam := Camera3D.new(); add_child(cam)
	for sh in [["street", Vector3(1.5, 2.2, 7.5), Vector3(0.8, 1.6, -2), 50.0], ["door", Vector3(0.5, 1.4, 3.2), Vector3(0.6, 1.3, -3), 50.0],
			["albion", Vector3(1, 17.0, 17.5), Vector3(1, 0.8, -3), 45.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 10: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
