extends Node
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	for i in 25: await get_tree().process_frame
	var pl: CharacterBody3D = main.get_node("Player"); var lv = main.get_node("Level")
	var p: Vector2 = Vector2(pl.global_position.x, pl.global_position.z) + lv.ORIGIN
	print("PROBE player y=%.2f ground=%.2f floor=%s collisions=%d" % [pl.global_position.y, lv.height(p), pl.is_on_floor(), pl.get_slide_collision_count()])
	for i in pl.get_slide_collision_count(): print("PROBE hit ", pl.get_slide_collision(i).get_collider().get_parent().name, " ", pl.get_slide_collision(i).get_collider().name)
	var model = pl.get_node("Model")
	for m in model.find_children("*", "MeshInstance3D", true, false): print("PROBE mesh ", m.name, " parent ", m.get_parent().name)
	get_tree().quit()
