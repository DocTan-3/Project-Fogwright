extends Node3D
## the two Hrimfolk heads on one body (tools/voxel/make_heads.py): A oversized at 2.5 cm, B life-size at 1.25 cm; pictures
## close up, three-quarter and under the Albion camera; triangle counts after greedy meshing
##   godot --path . --rendering-driver opengl3 res://tests/voxel_heads.tscn -- out=<png prefix>
func _ready() -> void:
	var out := "/tmp/heads"
	for a in OS.get_cmdline_user_args(): if a.begins_with("out="): out = a.split("=")[1]
	const D := "res://assets/voxel/characters/"
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); sky.sky_material = ProceduralSkyMaterial.new(); env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.environment.ambient_light_energy = 0.8
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC; env.environment.ssao_enabled = true; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-42, -28, 0); sun.light_energy = 1.15; sun.shadow_enabled = true; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(40, 40); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color("5f7a3a"); g.material_override = gm; add_child(g)
	var xs := [-0.6, 0.6]
	for i in 2:
		var m := Vox.character(D + "hrim_body.vox", Vox.FINE, [], [D + ["hrim_head_a.vox", "hrim_head_b.vox"][i]])
		add_child(m); m.position = Vector3(xs[i], 0, 0)
		var tris := 0; var htris := 0
		for mi in m.find_children("*", "MeshInstance3D", true, false):
			var t: int = (mi as MeshInstance3D).mesh.get_faces().size() / 3; tris += t
			if mi.name == "head": htris = t
		print("HEADS %s: whole character %d triangles, head %d" % [["A oversized 2.5 cm", "B life-size 1.25 cm"][i], tris, htris])
	var l := Label3D.new(); l.text = "A: big head, 2.5 cm          B: life-size, 1.25 cm"; l.font_size = 34; l.pixel_size = 0.004; l.position = Vector3(0, 2.25, 0); add_child(l)
	var cam := Camera3D.new(); add_child(cam)
	for sh in [["close", Vector3(0, 1.7, 1.9), Vector3(0, 1.58, 0), 38.0], ["threequarter", Vector3(1.4, 1.75, 1.6), Vector3(0, 1.5, 0), 38.0],
			["full", Vector3(0, 1.2, 4.2), Vector3(0, 1.0, 0), 40.0], ["albion", Vector3(0, 13.0, 15.0), Vector3(0, 0.9, 0), 45.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
