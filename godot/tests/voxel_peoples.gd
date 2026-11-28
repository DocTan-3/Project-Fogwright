extends Node3D
## the lineup: every playable people, man and woman (tools/voxel/make_character.py), beside a 2.2 x 1.4 m doorway frame
##   godot --path . --rendering-driver opengl3 res://tests/voxel_peoples.tscn -- out=<png prefix>
const PEOPLES := ["hrimfolk", "ruadhan", "aurelan", "zarhim", "ilvari", "ferrin", "wayfolk", "penitent"]
func _ready() -> void:
	var out := "/tmp/peoples"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	const D := "res://assets/voxel/characters/peoples/"
	# the game's own daylight (scenes/main.tscn with Farhallow's late afternoon, scripts/farhallow.gd _light), so colours read as in play
	var env := WorldEnvironment.new(); env.environment = Environment.new(); var e := env.environment
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	sm.sky_top_color = Color(0.42, 0.56, 0.74); sm.sky_horizon_color = Color(0.93, 0.78, 0.6); sm.ground_horizon_color = Color(0.93, 0.78, 0.6)
	sm.ground_bottom_color = Color(0.3, 0.3, 0.32); sm.sun_angle_max = 30.0
	e.background_mode = Environment.BG_SKY; e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_energy = 0.45; e.ambient_light_sky_contribution = 0.6
	e.ambient_light_color = Color(0.86, 0.84, 0.8); e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.tonemap_exposure = 0.9; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-30, -30, 0); sun.light_color = Color(1.0, 0.8, 0.58); sun.light_energy = 1.05
	sun.shadow_enabled = true; sun.shadow_bias = 0.25; sun.shadow_normal_bias = 3.0; add_child(sun)   # no acne on flat voxel faces
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(60, 60); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color(0.36, 0.42, 0.26); g.material_override = gm; add_child(g)
	var fm := StandardMaterial3D.new(); fm.albedo_color = Color("5a3a22")
	for side in [-1, 1]:   # the doorway: 1.4 m wide, 2.2 m tall
		var post := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(0.1, 2.2, 0.1); post.mesh = bm; post.material_override = fm
		post.position = Vector3(-1.4 + side * 0.75, 1.1, 0); add_child(post)
	var lintel := MeshInstance3D.new(); var lm := BoxMesh.new(); lm.size = Vector3(1.6, 0.1, 0.1); lintel.mesh = lm; lintel.material_override = fm
	lintel.position = Vector3(-1.4, 2.25, 0); add_child(lintel)
	var i := 0
	for p in PEOPLES:
		for s in ["m", "f"]:
			var m := Vox.character(D + "%s_%s.vox" % [p, s], Vox.FINE); add_child(m)
			m.position = Vector3(i * 0.95, 0, 0)
			var tris := 0
			for mi in m.find_children("*", "MeshInstance3D", true, false): tris += (mi as MeshInstance3D).mesh.get_faces().size() / 3
			print("PEOPLE %s_%s: %d triangles" % [p, s, tris]); i += 1
	var cam := Camera3D.new(); add_child(cam)
	get_viewport().size = Vector2i(2400, 900)
	for sh in [["front", Vector3(6.0, 1.1, 9.5), Vector3(6.0, 0.9, 0), 40.0], ["left", Vector3(2.2, 1.3, 3.6), Vector3(2.2, 1.0, 0), 40.0],
			["right", Vector3(10.6, 1.3, 3.6), Vector3(10.6, 1.0, 0), 40.0], ["back", Vector3(6.0, 1.2, -9.5), Vector3(6.0, 0.9, 0), 40.0],
			["faces1", Vector3(1.42, 1.35, 2.3), Vector3(1.42, 1.3, 0), 36.0], ["faces2", Vector3(5.22, 1.35, 2.3), Vector3(5.22, 1.3, 0), 36.0],
			["faces3", Vector3(9.02, 1.3, 2.3), Vector3(9.02, 1.25, 0), 36.0], ["faces4", Vector3(12.82, 1.35, 2.3), Vector3(12.82, 1.3, 0), 36.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
