extends Node
## a dodge goes the way you move and the body faces that way for the whole roll (the roll clip only rolls forward):
## dodges left, right and back with a melee weapon and a gun; prints DODGE-DIR <n> failure(s)
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	for i in 30: await get_tree().process_frame
	var pc: PlayerCombat = main.get_node("Player/Combat"); var fails := 0
	for w in ["sword", "pistol"]:
		pc.equip(w)
		for k in [["move_left", "left"], ["move_right", "right"], ["move_back", "back"]]:
			pc.fighter.stamina = 100.0
			var start: Vector3 = pc.player.global_position
			Input.action_press(k[0]); await get_tree().physics_frame
			pc.dodge(); Input.action_release(k[0])
			var worst := 0.0
			for f in 45:
				await get_tree().physics_frame
				var v := pc.player.velocity; v.y = 0.0
				if v.length() > 1.0 and pc.fighter.dodging >= 0.0:   # during the roll (after it a shooter turns back to the crosshair)
					var yaw: float = pc.player.get_node("Model").rotation.y
					worst = maxf(worst, absf(angle_difference(yaw, atan2(v.x, v.z))))
			var moved := pc.player.global_position - start
			var ok := worst < 0.35 and moved.length() > 1.5
			if not ok: fails += 1
			print("%s %s: moved %.1f m, body off the roll's direction by up to %d deg %s" % [w, k[1], moved.length(), roundi(rad_to_deg(worst)), "ok" if ok else "FAIL"])
			for f in 40: await get_tree().physics_frame
	print("DODGE-DIR %d failure(s)" % fails)
	get_tree().quit(1 if fails else 0)
