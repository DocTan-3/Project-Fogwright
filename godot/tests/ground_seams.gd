extends Node
## close views of voxel Farhallow's ground where path cells (25 cm squares) meet plain cells, to check for dark seams
##   godot --path . --rendering-driver opengl3 res://tests/ground_seams.tscn -- out=<png prefix>
func _ready() -> void:
	var out := "/tmp/seams"
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var sc: Node = (load("res://scenes/farhallow_voxel.tscn") as PackedScene).instantiate(); add_child(sc)
	for k in 30: await get_tree().physics_frame
	var cam := Camera3D.new(); sc.add_child(cam); cam.current = true; cam.fov = 50
	for sh in [["a", Vector3(6.0, 8.0, -1.0), Vector3(6.0, 3.0, -8.0)], ["b", Vector3(-12.0, 7.5, -9.0), Vector3(-12.0, 2.5, -16.0)],
			["c", Vector3(0.0, 9.0, 4.0), Vector3(0.0, 3.0, -4.0)]]:
		cam.position = sh[1]; cam.look_at(sh[2])
		for k in 8: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%s.png" % [out, sh[0]])
	get_tree().quit()
