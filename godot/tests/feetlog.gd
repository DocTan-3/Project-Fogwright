extends Node
## walks the player down the slope from the smithy toward the well and logs how far each sole is from the ground
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	var pl: CharacterBody3D = main.get_node("Player"); var lv = main.get_node("Level")
	pl.global_position = lv.W(Vector2(86, 40), lv.height(Vector2(86, 40)) + 0.2)
	main.get_node("CameraRig").yaw = deg_to_rad(-100)
	for i in 10: await get_tree().physics_frame
	Input.action_press("move_forward")
	var skel: Skeleton3D = pl.get_node("Model").find_children("*", "Skeleton3D", true, false)[0]
	var worst := 0.0
	for f in 90:
		await get_tree().process_frame
		for n in ["foot_l", "foot_r", "ball_l", "ball_r"]:
			var p := skel.global_transform * skel.get_bone_global_pose(skel.find_bone(n)).origin
			var rest := (skel.global_transform.basis * skel.get_bone_global_rest(skel.find_bone(n)).origin).y
			var under: float = lv.height(Vector2(p.x, p.z) + lv.ORIGIN) - (p.y - rest)
			worst = maxf(worst, under)
	print("FEET worst sink below ground: %.3f m" % worst)
	get_tree().quit()
