extends Node
## runs the city-planning check on the level and prints every problem (tools: .claude/skills/city-planning)
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	for i in 4: await get_tree().physics_frame   # colliders registered with the physics world
	var issues: Array = main.get_node("Level").check_plan()
	for i in issues: print("PLAN ", i)
	print("PLAN-RESULT %d problem(s)" % issues.size())
	get_tree().quit()
