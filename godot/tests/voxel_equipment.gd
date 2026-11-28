extends Node3D
## the equipment system at work: each armour tier (light, medium, heavy, plate, the rig) on very different bodies, so a
## recipe-fitted item is seen to fit every people and both sexes; plus the wardrobe alone for comparison
##   godot --path . --rendering-driver opengl3 res://tests/voxel_equipment.tscn -- out=<png prefix>
const BODIES := [["hrimfolk", "m"], ["ilvari", "f"], ["ferrin", "m"], ["zarhim", "f"], ["aurelan", "m"]]
const TIERS := ["wardrobe", "light", "medium", "heavy", "plate", "rig", "colossus", "gauntlets", "arm_utility", "arm_combat", "arm_defence", "arm_cannons"]
func _ready() -> void:
	var out := "/tmp/equip"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var env := WorldEnvironment.new(); env.environment = Environment.new(); var e := env.environment
	var sky := Sky.new(); var sm := ProceduralSkyMaterial.new(); sky.sky_material = sm
	sm.sky_top_color = Color(0.42, 0.56, 0.74); sm.sky_horizon_color = Color(0.93, 0.78, 0.6); sm.ground_horizon_color = Color(0.93, 0.78, 0.6)
	e.background_mode = Environment.BG_SKY; e.sky = sky
	e.ambient_light_source = Environment.AMBIENT_SOURCE_SKY; e.ambient_light_energy = 0.45; e.ambient_light_sky_contribution = 0.6
	e.ambient_light_color = Color(0.86, 0.84, 0.8); e.tonemap_mode = Environment.TONE_MAPPER_ACES; e.tonemap_exposure = 0.9; add_child(env)
	var sun := DirectionalLight3D.new(); sun.rotation_degrees = Vector3(-30, -30, 0); sun.light_color = Color(1.0, 0.8, 0.58); sun.light_energy = 1.05
	sun.shadow_enabled = true; sun.shadow_bias = 0.25; sun.shadow_normal_bias = 3.0; add_child(sun)
	var g := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(300, 300); g.mesh = pm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color(0.36, 0.42, 0.26); g.material_override = gm; add_child(g)
	for t in TIERS.size():
		for b in BODIES.size():
			var worn: Array = [] if TIERS[t] == "wardrobe" else Equipment.set_items(TIERS[t])
			var m := Equipment.dress(BODIES[b][0], BODIES[b][1], worn)
			add_child(m); m.position = Vector3(b * 1.5 + t * 12.0, 0, 0)
			var tris := 0
			for mi in m.find_children("*", "MeshInstance3D", true, false): if (mi as MeshInstance3D).visible: tris += (mi as MeshInstance3D).mesh.get_faces().size() / 3
			print("EQUIP %s on %s_%s: %d triangles" % [TIERS[t], BODIES[b][0], BODIES[b][1], tris])
	var cam := Camera3D.new(); add_child(cam)
	get_viewport().size = Vector2i(2400, 1000)
	for t in TIERS.size():
		for view in [["front", Vector3(3.0, 1.4, 6.0)], ["back", Vector3(3.0, 1.6, -6.0)], ["side", Vector3(-1.5, 1.7, 4.5)]]:
			if view[0] == "back" and TIERS[t] in ["wardrobe", "light"]: continue
			if view[0] == "side" and not TIERS[t].begins_with("arm_"): continue
			cam.position = view[1] + Vector3(t * 12.0, 0, 0); cam.look_at(Vector3(3.0 + t * 12.0, 1.0, 0)); cam.fov = 42.0
			for k in 6: await get_tree().process_frame
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png("%s_%s_%s.png" % [out, TIERS[t], view[0]])
	get_tree().quit()
