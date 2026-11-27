extends Node
## renders the level from given plan points: -- out=<prefix> at=x,y,dist,yaw_deg,pitch_deg;...
func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1); if kv.size() == 2: args[kv[0]] = kv[1]
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	for i in 90: await get_tree().process_frame
	var lv = main.get_node("Level"); var rig = main.get_node("CameraRig"); rig.set_process(false)
	var cam: Camera3D = rig.get_node("SpringArm3D/Camera3D")
	var k := 0
	for spec in args.get("at", "64,50,14,30,-25").split(";"):
		var v: PackedStringArray = spec.split(","); var p := Vector2(float(v[0]), float(v[1])); var dist := float(v[2]); var yaw := deg_to_rad(float(v[3])); var pitch := deg_to_rad(float(v[4]))
		var target: Vector3 = lv.W(p, lv.height(p) + 1.5)
		var dir := Vector3(sin(yaw) * cos(pitch), -sin(pitch), cos(yaw) * cos(pitch))
		cam.global_position = target + dir * dist; cam.look_at(target)
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%d.png" % [args.get("out", "/tmp/look"), k]); k += 1
	get_tree().quit()
