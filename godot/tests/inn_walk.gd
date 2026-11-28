extends Node
## the Gull & Lantern (scenes/inn_gull_lantern.tscn, KitLayouts.GULL_LANTERN): walks the voxel Hrimfolk in through the
## front door, across the taproom, through the stair hall, up the stair, along the corridor and into a front guest room,
## with the WoW camera; in the taproom and the guest room turns the camera all the way round at its farthest zoom and
## checks it stays inside. Saves a few frames, the frame rate and the inn's triangles.
##   godot --path . --rendering-driver opengl3 res://tests/inn_walk.tscn -- out=<png prefix>
var out := "/tmp/inn"
var rig: Node3D; var pl: CharacterBody3D; var b: Node3D; var n := 0

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var sc: Node = (load("res://scenes/inn_gull_lantern.tscn") as PackedScene).instantiate(); add_child(sc)
	rig = sc.get_node("CameraRig"); pl = sc.get_node("Player"); b = sc.get_node("Level").building
	for k in 30: await get_tree().physics_frame
	var start := pl.global_position
	pl.global_position = b.global_position + Vector3(-6.0, 0.1, 12.0)
	rig.yaw = atan2(-14.0, 18.0); rig.pitch = deg_to_rad(-8.0); rig.distance = 12.0
	await _shot("outside")
	pl.global_position = start
	rig.yaw = 0.0; rig.pitch = deg_to_rad(-10.0); rig.distance = 6.0
	await _walk(Vector3(5.05, 0, -1.5), 0.4)
	var opened := 0
	for d in b.get_node("Doors").get_children():
		if d.open: opened += 1
	print("DOORS open %d of %d after the front door, player=%s" % [opened, b.get_node("Doors").get_child_count(), _local(pl.global_position)])
	await _walk(Vector3(5.0, 0, -3.0), 0.4)
	rig.yaw = atan2(1.0, 0.6); rig.pitch = deg_to_rad(-14.0); rig.distance = 5.0; await _shot("taproom")
	rig.yaw = atan2(-1.0, 0.2); await _shot("bar")
	await _spin("taproom", Rect2(0.3, -7.9, 9.6, 7.6), 4.9)
	for w in [Vector3(4.6, 0, -7.0), Vector3(3.05, 0, -7.0), Vector3(3.05, 0, -9.0), Vector3(1.5, 0, -9.3), Vector3(1.4, 0, -10.95)]:
		await _walk(w, 0.25)
	rig.pitch = deg_to_rad(-12.0)
	await _walk(Vector3(5.5, 0, -10.95), 0.3)
	rig.yaw = -PI * 0.5 - 0.5; rig.distance = 4.0; await _shot("stair")
	for w in [Vector3(9.5, 0, -10.95), Vector3(7.0, 0, -7.5), Vector3(7.0, 0, -5.0), Vector3(11.05, 0, -5.0)]:
		await _walk(w, 0.3)
	rig.yaw = PI * 0.5; rig.distance = 4.0; await _shot("corridor")
	await _walk(Vector3(11.05, 0, -2.0), 0.3)
	var op := []
	for d in b.get_node("Doors").get_children():
		if d.open: op.append(_local(d.global_position).snapped(Vector3.ONE * 0.1))
	print("DOORS opened on the way: %s" % [op])
	print("ROOM player=%s (upper floor at 4.9 m)" % [_local(pl.global_position)])
	rig.yaw = atan2(1.0, -1.0); rig.pitch = deg_to_rad(-14.0); rig.distance = 4.0; await _shot("guest_room")
	await _spin("guest room", Rect2(8.3, -3.9, 3.4, 3.6), 7.9)
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
