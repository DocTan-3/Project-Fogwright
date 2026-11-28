extends Node
## renders voxel Farhallow (scenes/farhallow_voxel.tscn) from plan points, with its own camera:
##   godot --path . --rendering-driver opengl3 res://tests/village_look.tscn -- out=<prefix> "at=x,y,dist,yaw_deg,pitch_deg;..."
## yaw 0 looks from the south (the camera south of the point), 90 from the east; pitch is how far above it looks down
func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1); if kv.size() == 2: args[kv[0]] = kv[1]
	get_viewport().size = Vector2i(1600, 900)
	var main: Node3D = load("res://scenes/farhallow_voxel.tscn").instantiate(); add_child(main)
	for i in 30: await get_tree().process_frame
	var lv = main.get_node("Level"); var rig = main.get_node("CameraRig"); rig.set_process(false)
	var cam := Camera3D.new(); main.add_child(cam); cam.current = true; cam.fov = 60.0; cam.far = 600.0
	var k := 0
	for spec in args.get("at", "64,50,14,30,-25").split(";"):
		var v: PackedStringArray = spec.split(","); var p := Vector2(float(v[0]), float(v[1])); var dist := float(v[2]); var yaw := deg_to_rad(float(v[3])); var pitch := deg_to_rad(float(v[4]))
		var target := Vector3(p.x - 70, lv.fh.height(p) + 1.5, p.y - 55)
		var dir := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
		cam.global_position = target + dir * dist; cam.look_at(target)
		main.get_node("Player").global_position = target + Vector3(0, -1.4, 0) + dir * 2.0 * Vector3(1, 0, 1)
		for f in 4: await get_tree().process_frame
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%d.png" % [args.get("out", "/tmp/vlook"), k]); k += 1
	get_tree().quit()
