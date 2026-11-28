extends Node
## walks the voxel Hrimfolk through Farhallow with the WoW camera, saving frames and the frame rate
##   godot --path . --rendering-driver opengl3 res://tests/farhallow_voxel_walk.tscn -- out=<png prefix>
func _ready() -> void:
	var out := "/tmp/fhw"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var sc: Node = (load("res://scenes/farhallow_voxel.tscn") as PackedScene).instantiate(); add_child(sc)
	var rig = sc.get_node("CameraRig"); var pl: CharacterBody3D = sc.get_node("Player")
	for k in 60: await get_tree().physics_frame
	var cam: Camera3D = rig.get_node("SpringArm3D/Camera3D")
	# legs: [yaw, pitch deg, distance, seconds walking, frames saved]
	var legs := [[0.6, -14.0, 5.0, 3.0, 3], [2.0, -10.0, 4.0, 3.0, 3], [-1.2, -20.0, 7.0, 3.0, 3], [-2.2, -8.0, 6.0, 2.0, 2], [-2.2, -45.0, 2.6, 1.0, 1], [-2.2, -45.0, 2.6, 0.6, 1]]
	var n := 0
	var space := pl.get_world_3d().direct_space_state
	for leg in legs:
		rig.yaw = leg[0]; rig.pitch = deg_to_rad(leg[1]); rig.distance = leg[2]
		Input.action_press("move_forward")
		var t := 0.0; var frames := 0; var every: float = leg[3] / leg[4]; var next := every
		while t < leg[3]:
			await get_tree().process_frame
			var d := get_process_delta_time(); t += d; frames += 1
			if t >= next:
				next += every
				await RenderingServer.frame_post_draw
				get_viewport().get_texture().get_image().save_png("%s_%02d.png" % [out, n]); n += 1
		Input.action_release("move_forward")
		# is the camera under the ground?
		var cp := cam.global_position
		var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(cp + Vector3(0, 50, 0), cp - Vector3(0, 50, 0)))
		var gy: float = hit.position.y if hit else -999.0
		print("LEG yaw=%.1f fps=%.1f player=%s cam_y=%.2f ground_below_cam=%.2f arm=%.2f" % [leg[0], frames / t, pl.global_position, cp.y, gy, rig.get_node("SpringArm3D").get_hit_length()])
	get_tree().quit()
