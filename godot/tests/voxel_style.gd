extends Node3D
## a stylized voxel character (tools/voxel/make_stylized.py): close, three-quarter, full front, back and under the Albion
## camera, beside the realistic-proportioned 2.5 cm base for comparison; triangle count
##   godot --path . --rendering-driver opengl3 res://tests/voxel_style.tscn -- out=<png prefix> [model=hrim_stylized]
func _ready() -> void:
	var out := "/tmp/style"; var model := "hrim_stylized"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
		if a.begins_with("model="): model = a.split("=")[1]
	const D := "res://assets/voxel/characters/"
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sm.sky_top_color = Color("4f7fe0"); sm.sky_horizon_color = Color("8fb4f0"); sky.sky_material = sm
	env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.environment.ambient_light_energy = 0.85
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC; env.environment.ssao_enabled = true; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-45, -25, 0); sun.light_energy = 1.1; sun.shadow_enabled = true; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(40, 40); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color("6f86b8"); g.material_override = gm; add_child(g)
	var m := Vox.character(D + model + ".vox", Vox.FINE); add_child(m)
	var old := Vox.character(D + "hrim_body.vox", Vox.FINE, [], [D + "hrim_head_a.vox"]); add_child(old); old.position = Vector3(1.0, 0, 0)
	var tris := 0
	for mi in m.find_children("*", "MeshInstance3D", true, false): tris += (mi as MeshInstance3D).mesh.get_faces().size() / 3
	print("STYLE %s: %d triangles" % [model, tris])
	var cam := Camera3D.new(); add_child(cam)
	for sh in [["close", Vector3(0, 1.55, 1.5), Vector3(0, 1.45, 0), 40.0], ["threequarter", Vector3(-1.3, 1.5, 1.7), Vector3(0, 1.1, 0), 42.0],
			["full", Vector3(0.5, 1.0, 3.8), Vector3(0.5, 0.85, 0), 40.0], ["back", Vector3(0.5, 1.3, -3.4), Vector3(0.0, 0.9, 0), 40.0], ["albion", Vector3(0.5, 12.0, 13.0), Vector3(0.5, 0.8, 0), 45.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
