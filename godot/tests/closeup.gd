extends Node
## close-ups of the player and the nearest villagers, a few seconds in
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	var out := "/tmp/claude-0/-home-user/28227d4b-b333-5d02-966b-9f0af28e8773/scratchpad/g/cu"
	for i in 120: await get_tree().process_frame
	var rig = main.get_node("CameraRig"); rig.set_process(false)
	if "camera=high" in OS.get_cmdline_user_args(): pass
	else: rig.high = false; rig._apply_mode()   # tests place the close camera themselves unless asked for the high one
	var cam: Camera3D = rig.get_node("SpringArm3D/Camera3D")
	var targets := [main.get_node("Player")]
	for n in main.get_node("Level").get_children():
		if n.name.begins_with("Villager"): targets.append(n)
	for k in 4:
		var t: Node3D = targets[k]
		cam.global_position = t.global_position + t.get_child(0).global_transform.basis.z * 2.2 + Vector3(0.6, 1.3, 0); cam.look_at(t.global_position + Vector3(0, 1.0, 0))
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%d.png" % [out, k])
	get_tree().quit()
