extends Node3D
## the Wayfolk common iron set (make_equipment.py IRON): every weapon drawn, a sword and shield and a mace and tower shield,
## then everything carried, on one body; prints GROUND FAIL for anything below the ground and the triangle counts
##   godot --path . --rendering-driver opengl3 res://tests/voxel_weapons.tscn -- out=<png prefix> [people=hrimfolk] [sex=m]
const KINDS := ["sword", "axe", "mace", "hammer", "dagger", "greatsword", "greataxe", "warhammer", "spear", "halberd", "glaive",
	"shortbow", "longbow", "heavy_crossbow", "shield", "tower_shield", "wand", "staff"]
func _ready() -> void:
	var out := "/tmp/weapons"; var people := "hrimfolk"; var sex := "m"
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=")
		match kv[0]:
			"out": out = kv[1]
			"people": people = kv[1]
			"sex": sex = kv[1]
	var env := WorldEnvironment.new(); env.environment = Environment.new(); var e := env.environment
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	sm.sky_top_color = Color(0.42, 0.56, 0.74); sm.sky_horizon_color = Color(0.93, 0.78, 0.6); sm.ground_horizon_color = Color(0.93, 0.78, 0.6)
	e.background_mode = Environment.BG_SKY; e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_energy = 0.45; e.ambient_light_sky_contribution = 0.6
	e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.tonemap_exposure = 0.9; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-30, -30, 0); sun.light_color = Color(1.0, 0.8, 0.58); sun.light_energy = 1.05
	sun.shadow_enabled = true; sun.shadow_bias = 0.25; sun.shadow_normal_bias = 3.0; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(200, 200); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color(0.36, 0.42, 0.26); g.material_override = gm; add_child(g)
	var rows := [[], []]
	for k in KINDS: rows[0].append([["iron_" + k], true])
	rows[0].append([["iron_sword", "iron_shield"], true]); rows[0].append([["iron_mace", "iron_tower_shield"], true])
	rows[0].append([["iron_shortbow", "quiver"], true]); rows[0].append([["iron_heavy_crossbow", "bolt_case"], true])
	for k in KINDS: rows[1].append([["iron_" + k], false])
	# the ammunition at the back of the belt, with a knapsack on the back to show both are worn
	rows[1].append([["iron_longbow", "quiver", "knapsack"], false]); rows[1].append([["iron_heavy_crossbow", "bolt_case", "knapsack"], false])
	rows[1].append([["quiver", "knapsack"], false]); rows[1].append([["bullet_pouch", "knapsack", "plain_belt"], false])
	for r in 2:
		for i in rows[r].size():
			var worn: Array = rows[r][i][0]
			var m := Equipment.dress(people, sex, worn, true, rows[r][i][1]); add_child(m)
			m.position = Vector3(i * 1.6, 0, r * 40.0)
			if r == 1: m.rotation_degrees.y = 180.0      # carried: seen from behind
			var low := INF; var tris := 0
			for mi in m.find_children("*", "MeshInstance3D", true, false):
				if not (mi as MeshInstance3D).is_visible_in_tree(): continue
				var bb: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
				for k in 8: low = minf(low, bb.get_endpoint(k).y)
				if String(mi.name).begins_with("weapon"): tris += (mi as MeshInstance3D).mesh.get_faces().size() / 3
			var tag := "+".join(worn) + (" carried" if r == 1 else "")
			if low < -0.01: print("GROUND FAIL %s on %s_%s: %.3f m below" % [tag, people, sex, -low])
			print("WEAPON %s: %d triangles" % [tag, tris])
			var l := Label3D.new(); l.text = " + ".join(worn.map(func(w): return w.trim_prefix("iron_"))); l.font_size = 36; l.pixel_size = 0.0025; l.outline_size = 8
			l.position = m.position + Vector3(0, 0.05, 0.9); add_child(l)
	var cam := Camera3D.new(); add_child(cam); get_viewport().size = Vector2i(3600, 1000)
	var n0: int = rows[0].size()
	var shots := []
	for a in range(0, n0, 6): shots.append(["drawn_%d" % (a / 6), 0, a, mini(a + 6, n0)])
	for a in range(0, rows[1].size(), 7): shots.append(["carried_%d" % (a / 7), 1, a, mini(a + 7, rows[1].size())])
	for sh in shots:
		var cx: float = (sh[2] + sh[3] - 1) * 0.8; var z: float = sh[1] * 40.0
		cam.position = Vector3(cx + 0.8, 1.5, z + 6.2); cam.look_at(Vector3(cx, 0.95, z)); cam.fov = 40.0
		for k in 6: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s_%s_%s.png" % [out, people, sex, sh[0]])
	print("WEAPONS done")
	get_tree().quit()
