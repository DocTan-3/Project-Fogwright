extends Node
## the Gull & Lantern on its plot in voxel Farhallow (scenes/farhallow_voxel.tscn): looks at it from the square, walks
## the voxel Hrimfolk in through its front door with the WoW camera, and prints the frame rate on the way
##   godot --path . --rendering-driver opengl3 res://tests/inn_village.tscn -- out=<png prefix>
func _ready() -> void:
	var out := "/tmp/innv"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var sc: Node = (load("res://scenes/farhallow_voxel.tscn") as PackedScene).instantiate(); add_child(sc)
	var rig = sc.get_node("CameraRig"); var pl: CharacterBody3D = sc.get_node("Player")
	var bk: Node3D = null
	for n in sc.get_node("Level").find_children("Building", "Node3D", true, false): bk = n
	for k in 30: await get_tree().physics_frame
	var door := bk.to_global(Vector3(5.05, 0.5, 0.0)); var into := -(bk.global_basis * Vector3(0, 0, 1)).normalized()
	var yaw := atan2(-into.x, -into.z)
	var shots := [["square", 15.0, -14.0, 9.0, 0.4], ["front", 6.5, -16.0, 4.5, -0.3]]
	for sh in shots:
		var at: Vector3 = door - into * sh[1] + bk.global_basis.x * sh[4] * 6.0
		var hit := pl.get_world_3d().direct_space_state.intersect_ray(PhysicsRayQueryParameters3D.create(at + Vector3(0, 30, 0), at - Vector3(0, 30, 0)))
		pl.global_position = (hit.position if hit else at) + Vector3(0, 0.2, 0); pl.velocity = Vector3.ZERO
		rig.yaw = yaw + sh[4]; rig.pitch = deg_to_rad(sh[2]); rig.distance = sh[3]
		await _shot(out, sh[0])
	# walk in
	Input.action_press("move_forward")
	var t := 0.0; var frames := 0
	while t < 4.0 and pl.global_position.distance_to(door + into * 2.5) > 0.4:
		var v := door + into * 2.5 - pl.global_position
		rig.yaw = lerp_angle(rig.yaw, atan2(-v.x, -v.z), 0.2)
		await get_tree().process_frame; t += get_process_delta_time(); frames += 1
	Input.action_release("move_forward")
	print("INN walked in: %s from the door, inside=%s, %.1f fps" % [(pl.global_position - door).length(), (pl.global_position - door).dot(into) > 0.5, frames / t])
	rig.distance = 4.0; rig.pitch = deg_to_rad(-12.0)
	await _shot(out, "inside")
	get_tree().quit()

func _shot(out: String, name: String) -> void:
	for k in 30: await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, name])
