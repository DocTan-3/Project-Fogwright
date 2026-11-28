extends Node
## the building kit's test room (scenes/kit_room.tscn): walks the voxel Hrimfolk up to the front door (it swings open),
## in, across the room, up the stair and into the upper room, with the WoW camera; at two stops turns the camera all the
## way round at its farthest zoom and checks it stays inside the room. Saves a few frames and prints the frame rate.
##   godot --path . --rendering-driver opengl3 res://tests/kit_room_walk.tscn -- out=<png prefix>
var out := "/tmp/kitroom"
var rig: Node3D; var pl: CharacterBody3D; var b: Node3D; var n := 0

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var sc: Node = (load("res://scenes/kit_room.tscn") as PackedScene).instantiate(); add_child(sc)
	rig = sc.get_node("CameraRig"); pl = sc.get_node("Player"); b = sc.get_node("Level").building
	for k in 30: await get_tree().physics_frame
	var start := pl.global_position
	pl.global_position = b.global_position + Vector3(-5.0, 0.1, 9.0)
	rig.yaw = atan2(-10.0, 12.0); rig.pitch = deg_to_rad(-6.0); rig.distance = 8.0
	await _shot("house")
	pl.global_position = start
	rig.yaw = 0.0; rig.pitch = deg_to_rad(-10.0); rig.distance = 6.0
	var door: KitDoor = b.get_node("Doors").get_child(0)
	await _walk(Vector3(3.1, 0, -1.6), 0.4, "door")
	print("DOOR open=%s player=%s" % [door.open, _local(pl.global_position)])
	await _walk(Vector3(4.5, 0, -2.6), 0.4)
	rig.distance = 4.0; await _shot("taproom")
	await _spin("ground", Rect2(0.3, -5.7, 9.4, 5.4), 4.9)
	await _walk(Vector3(1.0, 0, -3.2), 0.3)
	await _walk(Vector3(0.9, 0, -4.9), 0.25)
	rig.pitch = deg_to_rad(-12.0)
	await _walk(Vector3(4.6, 0, -4.9), 0.3)
	rig.yaw = -PI * 0.5 - 0.5; rig.pitch = deg_to_rad(-18.0); rig.distance = 4.0; await _shot("stair")
	await _walk(Vector3(9.0, 0, -4.9), 0.3)
	await _walk(Vector3(8.6, 0, -2.0), 0.3)
	print("UPSTAIRS player=%s (upper floor at 4.9 m)" % [_local(pl.global_position)])
	rig.distance = 4.0; rig.pitch = deg_to_rad(-12.0); await _walk(Vector3(5.0, 0, -2.0), 0.4); await _shot("upper")
	await _spin("upper", Rect2(0.3, -5.7, 9.4, 5.4), 7.9)
	get_tree().quit()

func _local(p: Vector3) -> Vector3: return p - b.global_position

## walks the player to a point (building-local, x and z), steering by turning the camera behind it
func _walk(to: Vector3, tol: float, shot := "") -> void:
	var t := 0.0; var frames := 0; var shot_done := shot == ""
	Input.action_press("move_forward")
	while t < 8.0:
		var p := _local(pl.global_position); var v := Vector3(to.x - p.x, 0, to.z - p.z)
		if v.length() < tol: break
		rig.yaw = lerp_angle(rig.yaw, atan2(-v.x, -v.z), 0.2)
		await get_tree().physics_frame
		t += get_physics_process_delta_time(); frames += 1
		if not shot_done and v.length() < 2.2: shot_done = true; Input.action_release("move_forward"); await _shot(shot); Input.action_press("move_forward")
	Input.action_release("move_forward")
	for k in 10: await get_tree().physics_frame
	print("WALK to %s: reached %s in %.1f s" % [to, _local(pl.global_position), t])

func _spin(where: String, room: Rect2, ceiling: float) -> void:
	var cam: Camera3D = rig.get_node("SpringArm3D/Camera3D"); var arm: SpringArm3D = rig.get_node("SpringArm3D")
	rig.distance = 18.0; var worst := 0.0; var bad := 0
	for i in 16:
		rig.yaw = TAU * i / 16.0
		for pitch in [-30.0, -5.0, 20.0]:
			rig.pitch = deg_to_rad(pitch)
			for k in 12: await get_tree().physics_frame
			var c := _local(cam.global_position)
			var outside := maxf(maxf(room.position.x - c.x, c.x - room.end.x), maxf(room.position.y - c.z, c.z - room.end.y))
			outside = maxf(outside, c.y - ceiling)
			worst = maxf(worst, outside); if outside > 0.0: bad += 1
	rig.distance = 4.0; rig.pitch = deg_to_rad(-12.0)
	print("CAMERA %s: %d of 48 views outside the room, worst %.2f m" % [where, bad, worst])

func _shot(name: String) -> void:
	for k in 20: await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s_%02d_%s.png" % [out, n, name]); n += 1
