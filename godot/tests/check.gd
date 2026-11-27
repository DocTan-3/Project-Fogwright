extends Node
## runs the city-planning check on the level and prints every problem (tools: .claude/skills/city-planning)
func _ready() -> void:
	var main: Node3D = load("res://scenes/main.tscn").instantiate(); add_child(main)
	await get_tree().process_frame
	var issues: Array = main.get_node("Level").check_plan()
	for i in issues: print("PLAN ", i)
	print("PLAN-RESULT %d problem(s)" % issues.size())
	get_tree().quit()
