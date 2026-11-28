extends Node3D
## the ground kit (scripts/voxel/ground_kit.gd) on a made-up hill with every piece: a 27 degree mound, a 45 degree bank on its
## east side, corners and saddles, a rock cliff up to a terrace with a house, a worn path, a beach edge; the Hrimfolk
## standing in the grass, which bends round him. Close (WoW camera), wide and Albion shots; piece counts and triangles.
##   godot --path . --rendering-driver opengl3 res://tests/ground_sheet.tscn -- out=<png prefix>
var noise := FastNoiseLite.new()
func height(p: Vector2) -> float:
	var h := 0.35 * noise.get_noise_2d(p.x, p.y)
	var r := p.length()
	var e := clampf(p.x / 6.0, 0.0, 1.0)                                     # the east side steeper
	h += clampf((7.5 - r) * lerpf(0.5, 1.0, e), 0.0, 3.0)                    # the mound: 27 degrees, 45 on the east
	if p.y < -11.0 + 1.5 * sin(p.x * 0.3): h = maxf(h, 3.2 + 0.2 * noise.get_noise_2d(p.x * 3.0, 0))   # the terrace, above a cliff
	if p.x > 15.0: h -= clampf((p.x - 15.0) * 0.12, 0.0, 0.9)              # down to the beach
	return h
func kind(p: Vector2, _slope: float) -> String:
	if p.x > 17.0: return "sand"
	if absf(p.y - 7.5 - 0.15 * p.x - 0.8 * sin(p.x * 0.25)) < 0.9: return "path"
	return "grass"
func _ready() -> void:
	var out := "/tmp/ground"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	noise.seed = 3; noise.frequency = 0.08
	var env := WorldEnvironment.new(); env.environment = Environment.new()
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sm.sky_top_color = Color("4f7fe0"); sm.sky_horizon_color = Color("a9c4ee"); sky.sky_material = sm
	env.environment.background_mode = Environment.BG_SKY; env.environment.sky = sky
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; env.environment.ambient_light_energy = 0.6
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC; env.environment.ssao_enabled = true; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-42, -35, 0); sun.light_energy = 1.0; sun.shadow_enabled = true; add_child(sun)
	var t0 := Time.get_ticks_msec()
	var g := GroundKit.build(height, Rect2(-24, -22, 48, 40), kind); add_child(g)
	var tris := 0
	for mi in g.find_children("*", "MeshInstance3D", true, false): tris += (mi as MeshInstance3D).mesh.get_faces().size() / 3
	var gm: MultiMeshInstance3D = g.get_node("Grass")
	print("GROUND built in %d ms: %d ground triangles, %d grass tufts (%d triangles), pieces %s" % [Time.get_ticks_msec() - t0, tris, gm.get_meta("tufts"), gm.get_meta("tufts") * 15, g.get_meta("pieces")])
	var house := Vox.prop("res://assets/buildings/medieval_voxel/Houses/House_3.glb"); add_child(house); house.position = Vector3(-4, height(Vector2(-4, -17)), -17)
	const G := "res://assets/voxel/gear/"
	var a := Vox.character("res://assets/voxel/characters/hrim_stylized.vox", Vox.FINE, [], [G + "hrim_pauldron_l.vox", G + "hrim_pauldron_r.vox", G + "hrim_toolbelt.vox"]); add_child(a)
	var pa := Vector2(-3.0, 4.2); a.position = Vector3(pa.x, GroundKit.STEP * round(height(pa) / GroundKit.STEP), pa.y); a.rotation_degrees.y = 20
	var b := Vox.character("res://assets/voxel/characters/hrim_stylized.vox", Vox.FINE, [], [G + "hrim_cyberarm.vox", G + "hrim_tank.vox"]); add_child(b)
	var pb := Vector2(-11.0, 2.0); b.position = Vector3(pb.x, GroundKit.STEP * round(height(pb) / GroundKit.STEP), pb.y); b.rotation_degrees.y = -30
	GroundKit.push(g, [a.position, b.position])
	var cam := Camera3D.new(); add_child(cam)
	for sh in [["close", a.position + Vector3(1.2, 2.0, 4.0), a.position + Vector3(0, 1.0, 0), 60.0],
			["wide", Vector3(14, 9, 22), Vector3(-2, 1.0, -3), 55.0], ["bank", Vector3(16, 4.5, 4), Vector3(4, 1.5, -2), 55.0],
			["albion", Vector3(0, 22.0, 20.0), Vector3(0, 0.5, -3), 45.0]]:
		cam.position = sh[1]; cam.look_at(sh[2]); cam.fov = sh[3]
		for k in 10: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
