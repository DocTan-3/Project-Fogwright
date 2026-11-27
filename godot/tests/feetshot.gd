extends Node
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	var pl: CharacterBody3D = main.get_node("Player"); var lv = main.get_node("Level")
	var rig = main.get_node("CameraRig")
	pl.global_position = lv.W(Vector2(84, 40), lv.height(Vector2(84, 40)) + 0.2)
	rig.yaw = deg_to_rad(-100)
	for i in 10: await get_tree().physics_frame
	Input.action_press("move_forward")
	var cam: Camera3D = rig.get_node("SpringArm3D/Camera3D")
	for f in 8:
		for k in 5: await get_tree().process_frame
		rig.set_process(false)
		var fwd: Vector3 = pl.get_node("Model").global_transform.basis.z
		var side := fwd.cross(Vector3.UP).normalized()
		cam.global_position = pl.global_position + side * 1.6 + Vector3(0, 0.35, 0); cam.look_at(pl.global_position + Vector3(0, 0.25, 0))
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("/tmp/claude-0/-home-user/28227d4b-b333-5d02-966b-9f0af28e8773/scratchpad/g/ft_%d.png" % f)
		rig.set_process(true)
	get_tree().quit()
