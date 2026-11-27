extends Node
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	await get_tree().process_frame
	for h in main.get_node("Level").houses: print("PROBE ", h[0], " centre ", h[1], " door ", h[2], " roof ", h[3])
	get_tree().quit()
