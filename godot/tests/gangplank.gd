extends Node
## walks the player from the pier head up the gangplank onto the last ship and prints where they end up:
##   godot --headless --path . res://tests/gangplank.tscn
func _ready() -> void:
	var s: Node = load("res://scenes/farhallow_voxel.tscn").instantiate(); add_child(s)
	for k in 5: await get_tree().physics_frame
	var player := s.find_child("Player", true, false) as CharacterBody3D
	var ship := s.find_child("LastShip", true, false) as Node3D
	var start := ship.to_global(Vector3(1.0, 1.4, -4.6)); var goal := ship.to_global(Vector3(1.0, 1.6, 0.5))
	player.global_position = start
	var g := ship.find_child("Gangplank", true, false) as Node3D
	for cs in g.find_children("*", "CollisionShape3D", true, false):
		var c := cs as CollisionShape3D; var lo := ship.to_local(c.to_global(Vector3(0, 0.06, -(c.shape as BoxShape3D).size.z / 2))); var hi := ship.to_local(c.to_global(Vector3(0, 0.06, (c.shape as BoxShape3D).size.z / 2)))
		print("GANG plank top from ", lo, " to ", hi, " layer ", (c.get_parent() as CollisionObject3D).collision_layer)
	print("GANG player mask ", player.collision_mask, " ship ", ship.get_path(), " g ", g.get_path(), " kids ", g.get_children())
	for k in 30: await get_tree().physics_frame
	print("GANG start ", ship.to_local(player.global_position))
	var dir := (goal - start); dir.y = 0; dir = dir.normalized()
	for k in 240:
		player.set("auto_dir", dir if ship.to_local(player.global_position).z < 0.0 else Vector3.ZERO); await get_tree().physics_frame
		if k % 30 == 0: print("GANG ", k, " ", ship.to_local(player.global_position))
	var at := ship.to_local(player.global_position)
	print("GANG-RESULT ", "aboard" if at.z > -1.5 and at.y > 1.3 else "NOT aboard", " ", at)
	get_tree().quit()
