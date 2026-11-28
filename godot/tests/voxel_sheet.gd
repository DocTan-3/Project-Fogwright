extends Node3D
## the voxel character bases (assets/voxel/characters, scripts/voxel/vox.gd) beside the current Quaternius body, walking
## with rigid-part animation; pictures: under the Albion camera, close front and back, a turnaround. Prints the scale check.
##   godot --path . --rendering-driver opengl3 res://tests/voxel_sheet.tscn -- out=<png prefix>
var models := []
var t := 0.0

func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args(): args[a.split("=")[0]] = a.split("=")[1] if "=" in a else ""
	var out: String = args.get("out", "/tmp/voxel")
	for f in ["base_m", "base_f"]:
		var why := Vox.check("res://assets/voxel/characters/%s.vox" % f, "person")
		print("VOXEL-CHECK %s: %s" % [f, "ok" if why == "" else why])
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); sky.sky_material = ProceduralSkyMaterial.new(); env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.environment.ambient_light_energy = 0.75
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-48, -35, 0); sun.light_energy = 1.25; sun.shadow_enabled = true; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(40, 40); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color("5f7a3a"); g.material_override = gm; add_child(g)
	var xs := [-1.2, 0.0, 1.2]
	for i in 2:
		var m := Vox.character("res://assets/voxel/characters/%s.vox" % ["base_m", "base_f"][i])
		add_child(m); m.position = Vector3(xs[i], 0, 0); models.append(m)
	var q: Node3D = (load("res://assets/characters/quaternius/Superhero_Male_FullBody.gltf") as PackedScene).instantiate()
	add_child(q); q.position = Vector3(xs[2], 0, 0)
	var ap := CombatRig.animate(q); ap.play("ual/Idle")
	var l := Label3D.new(); l.text = "voxel man   voxel woman   current"; l.font_size = 40; l.pixel_size = 0.005; l.position = Vector3(0, 2.3, 0); add_child(l)
	var cam := Camera3D.new(); add_child(cam)
	var shots := [["albion", Vector3(0, 10.0, 8.4), Vector3(0, 0.9, 0), 45.0, false], ["front", Vector3(0, 1.4, 4.6), Vector3(0, 0.95, 0), 40.0, false],
		["back", Vector3(0, 1.6, -4.6), Vector3(0, 0.95, 0), 40.0, false], ["walk", Vector3(-3.6, 1.6, 3.2), Vector3(-0.6, 0.9, 0), 40.0, true]]
	for sh in shots:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 12:
			if sh[4]: _walk(0.06)
			await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]]); print("saved ", sh[0])
	get_tree().quit()

## the walk, as rigid parts: legs and arms swing from their joints, lower legs bend on the back swing, a little bob
func _walk(dt: float) -> void:
	t += dt
	for m in models:
		var s := sin(t * 7.0)
		for side in ["l", "r"]:
			var k := 1.0 if side == "l" else -1.0
			var ul: Node3D = m.get_node_or_null("leg_upper_" + side)
			if ul: ul.rotation.x = 0.55 * s * k; (ul.get_node("leg_lower_" + side) as Node3D).rotation.x = -maxf(0.0, -s * k) * 0.8
			var ua: Node3D = m.get_node_or_null("arm_upper_" + side)
			if ua: ua.rotation.x = -0.45 * s * k; (ua.get_node("arm_lower_" + side) as Node3D).rotation.x = 0.25
		m.position.y = absf(cos(t * 7.0)) * 0.04
