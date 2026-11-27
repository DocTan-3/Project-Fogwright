## Renders screenshots of the slice for checking without a person at the keyboard:
##   godot --path . --rendering-driver opengl3 res://tests/shot.tscn -- out=/tmp/x steps=<plan>
## The plan is a list of "seconds:keys:yaw:pitch:dist" steps; at the end of each, a screenshot is saved.
extends Node

func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.split("=", true, 1)
		if kv.size() == 2: args[kv[0]] = kv[1]
	var out: String = args.get("out", "/tmp/shot")
	var main: Node3D = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	var rig = main.get_node("CameraRig")
	var steps: PackedStringArray = args.get("steps", "1::0:-12:3.6").split(",")
	var i := 0
	for st in steps:
		var p := st.split(":")
		var secs := float(p[0]); var keys := p[1]
		rig.yaw = deg_to_rad(float(p[2])); rig.pitch = deg_to_rad(float(p[3])); rig.distance = float(p[4])
		rig.get_node("SpringArm3D").collision_mask = 0 if rig.distance >= 20.0 else 1   # an overview sees past roofs
		for k in ["move_forward", "move_back", "move_left", "move_right", "sprint", "jump"]:
			Input.action_release(k)
		for c in keys:
			var act: String = {"w": "move_forward", "s": "move_back", "a": "move_left", "d": "move_right", "S": "sprint", "j": "jump"}.get(c, "")
			if act != "": Input.action_press(act)
		var t := 0.0
		while t < secs:
			await get_tree().process_frame
			t += get_process_delta_time()
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("%s_%d.png" % [out, i])
		i += 1
	get_tree().quit()
