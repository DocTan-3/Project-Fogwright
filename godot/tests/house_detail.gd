extends Node
## close shots of the building kit's detail (KitDress, BuildingKit._roof_dress): a cottage from a plot and the Gull &
## Lantern side by side on flat turf, from a free camera, with the Hrimfolk by the cottage door for scale.
##   godot --path . --rendering-driver opengl3 res://tests/house_detail.tscn -- out=<png prefix>
var out := "/tmp/hd"; var n := 0; var cam: Camera3D

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	var ps := load("res://scenes/kit_room.tscn") as PackedScene; var sc := ps.instantiate()
	sc.get_node("Level").layout_name = "none"; add_child(sc)
	var lay := KitLayouts.for_plot("cottage", 8.0, 6.0, [Vector2(0.4, -3.0)], 2)
	var co := BuildingKit.build(lay); add_child(co); co.position = Vector3(0, 0, 0)
	var inn := BuildingKit.build(KitLayouts.GULL_LANTERN); add_child(inn); inn.position = Vector3(20, 0, 0)
	print("DETAIL cottage %d tris %d ms, inn %d tris %d ms" % [co.get_meta("triangles"), co.get_meta("build_ms"), inn.get_meta("triangles"), inn.get_meta("build_ms")])
	var pl := sc.get_node("Player") as Node3D; pl.global_position = Vector3(3.0, 0.1, 3.4)
	cam = Camera3D.new(); add_child(cam); cam.fov = 55; cam.current = true
	for k in 20: await get_tree().physics_frame
	if not OS.get_cmdline_user_args().has("inside"):
		await _shot("cottage", Vector3(-5.5, 3.2, 9.0), Vector3(4.0, 2.4, -3.0))
		await _shot("cottage_close", Vector3(1.0, 1.8, 4.2), Vector3(4.0, 2.0, 0.0))
		await _shot("cottage_wing", Vector3(15.0, 3.0, 7.0), Vector3(8.0, 2.2, -3.0))
		await _shot("inn", Vector3(15.0, 4.5, 16.0), Vector3(28.0, 3.5, -6.0))
		await _shot("inn_close", Vector3(23.5, 2.0, 5.5), Vector3(26.0, 2.6, 0.0))
	await _shot("hearth_wall", Vector3(27.5, 2.0, -2.0), Vector3(20.3, 4.4, -2.0))
	await _shot("hall_up", Vector3(28.6, 1.7, -0.9), Vector3(21.5, 5.6, -4.5))
	await _shot("hall", Vector3(29.4, 2.3, -7.4), Vector3(21.0, 4.6, -1.0))
	await _shot("gallery", Vector3(21.2, 1.6, -0.9), Vector3(27.5, 5.0, -4.2))
	get_tree().quit()

func _shot(name: String, from: Vector3, at: Vector3) -> void:
	cam.global_position = from; cam.look_at(at)
	for k in 12: await get_tree().process_frame
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s_%02d_%s.png" % [out, n, name]); n += 1
