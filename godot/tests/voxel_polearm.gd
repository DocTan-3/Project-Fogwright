extends Node3D
## a close look at drawn polearms (the low carry from the user's reference): three-quarter, profile and from above
##   godot --path . --rendering-driver opengl3 res://tests/voxel_polearm.tscn -- out=<png prefix>
func _ready() -> void:
	var out: String = OS.get_cmdline_user_args()[0].split("=")[1]
	var env := WorldEnvironment.new(); env.environment = Environment.new(); var e := env.environment
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	e.background_mode = Environment.BG_SKY; e.sky = sky; e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_energy = 0.5
	e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.tonemap_exposure = 0.9; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-40, -30, 0); sun.light_color = Color(1.0, 0.85, 0.65); add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(20, 20); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color(0.36, 0.42, 0.26); g.material_override = gm; add_child(g)
	var a := Equipment.dress("ilvari", "f", ["plain_belt", "spear"], true, true); add_child(a)
	var b := Equipment.dress("aurelan", "m", ["plain_belt", "pitchfork"], true, true); add_child(b); b.position = Vector3(1.6, 0, 0)
	var cam := Camera3D.new(); add_child(cam); get_viewport().size = Vector2i(1600, 900)
	for sh in [["three_quarter", Vector3(2.6, 1.6, 3.2), Vector3(0.8, 0.9, 0.3)], ["profile", Vector3(-3.5, 1.0, 0.4), Vector3(0.8, 0.9, 0.4)], ["above", Vector3(0.8, 4.5, 1.2), Vector3(0.8, 0.8, 0.3)]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = 40
		for k in 6: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
