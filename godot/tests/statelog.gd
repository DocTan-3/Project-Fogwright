extends Node
## a scripted run for checking animation: logs the state, blend and rate every few frames
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	var pl = main.get_node("Player"); main.get_node("CameraRig").yaw = PI / 2; var plan := [[0.6,""],[1.0,"w"],[0.8,"wS"],[0.3,"wj"],[1.2,"w"],[0.3,"j"],[1.6,""]]
	for st in plan:
		for k in ["move_forward","sprint","jump"]: Input.action_release(k)
		for c in st[1]: Input.action_press({"w":"move_forward","S":"sprint","j":"jump"}[c])
		var t := 0.0; var n := 0
		while t < st[0]:
			await get_tree().physics_frame; t += get_physics_process_delta_time(); n += 1
			if n % 6 == 0:
				var pb = pl._tree.get("parameters/playback")
				print("t%.1f %-3s state=%-7s blend=%.2f pos=(%.1f,%.1f) wall=%s" % [t, st[1], pb.get_current_node(), pl._blend, pl.global_position.x, pl.global_position.z, pl.get_last_slide_collision().get_collider().get_parent().get_parent().name if pl.get_slide_collision_count() > 0 else "-"])
	get_tree().quit()
