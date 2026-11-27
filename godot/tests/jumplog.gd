extends Node
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	var pl = main.get_node("Player")
	for i in 30: await get_tree().physics_frame
	Input.action_press("jump")
	for f in 70:
		await get_tree().physics_frame
		if f == 1: Input.action_release("jump")
		var pb = pl._tree.get("parameters/playback")
		print("f%02d state=%-7s pos=%.2f len=%.2f y=%.2f vy=%.2f floor=%s" % [f, pb.get_current_node(), pb.get_current_play_position(), pb.get_current_length(), pl.global_position.y, pl.velocity.y, pl.is_on_floor()])
	get_tree().quit()
