extends Node
## renders the voxel Farhallow (scenes/farhallow_voxel.tscn) from the player's camera and from above
##   godot --path . --rendering-driver opengl3 res://tests/farhallow_voxel_shot.tscn -- out=<png prefix>
func _ready() -> void:
	var out := "/tmp/fhv"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var sc: Node = (load("res://scenes/farhallow_voxel.tscn") as PackedScene).instantiate(); add_child(sc)
	var rig = sc.get_node("CameraRig"); var pl: CharacterBody3D = sc.get_node("Player")
	for k in 30: await get_tree().physics_frame
	var cam: Camera3D = rig.get_node("SpringArm3D/Camera3D")
	var free := Camera3D.new(); sc.add_child(free)
	for sh in [["wow", 0.6, -14.0, 5.0], ["wow_far", 2.4, -24.0, 16.0], ["wow_look", -2.2, -8.0, 6.0]]:
		rig.yaw = sh[1]; rig.pitch = deg_to_rad(sh[2]); rig.distance = sh[3]
		pl.velocity = Vector3(0, 0, 0)
		for k in 40: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	free.current = true
	for sh in [["over", Vector3(-20, 70, 95), Vector3(5, 0, -5)], ["harbour", Vector3(40, 14, 52), Vector3(12, 2, 22)]]:
		free.position = sh[1]; free.look_at(sh[2]); free.fov = 55
		for k in 10: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
