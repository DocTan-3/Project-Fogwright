extends Node
## cut-through views of the Gull & Lantern (orthographic, near plane inside a wall) to check the interior is put
## together right: from the front cut just behind the front wall, and from the left cut just inside the gable.
var out := "/tmp/sec"; var n := 0; var cam: Camera3D

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var sc := (load("res://scenes/kit_room.tscn") as PackedScene).instantiate()
	sc.get_node("Level").layout_name = "none"; add_child(sc)
	var inn := BuildingKit.build(KitLayouts.GULL_LANTERN); add_child(inn)
	sc.get_node("Player").global_position = Vector3(-10, 0.1, 10)
	for p in [Vector3(4, 3, -3), Vector3(12, 3, -3), Vector3(4, 7, -4), Vector3(12, 7, -6), Vector3(4, 3, -10), Vector3(13, 3, -10)]:
		var l := OmniLight3D.new(); l.position = p; l.omni_range = 9.0; l.light_energy = 1.2; inn.add_child(l)
	cam = Camera3D.new(); add_child(cam); cam.current = true; cam.projection = Camera3D.PROJECTION_ORTHOGONAL; cam.size = 13.0
	for k in 10: await get_tree().physics_frame
	cam.size = 9.0
	await _shot("hall_front_wall", Vector3(5, 5, -33), Vector3(5, 5, 0), 30.0)   # from behind, cut 3 m from the front: the front wall's inside
	get_tree().quit()

func _shot(name: String, from: Vector3, at: Vector3, near: float) -> void:
	cam.global_position = from; cam.look_at(at); cam.near = near; cam.far = near + 30.0
	for k in 10: await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s_%02d_%s.png" % [out, n, name]); n += 1
