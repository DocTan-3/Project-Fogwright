## A test room from the voxel building kit (scripts/voxel/building_kit.gd): a 10 x 6 m house of two storeys, a 4.4 m
## stone ground floor with a front door and a stair up to a 3.0 m timber-frame floor under a thatch roof, on flat turf.
## Walk in through the door with the WoW camera. With layout_name "gull_lantern" (scenes/inn_gull_lantern.tscn) it
## builds the inn instead. Play it: godot --path godot res://scenes/kit_room.tscn
extends Node3D

## which layout of KitLayouts to build: "test_room" or "gull_lantern"
@export var layout_name := "test_room"
var building: Node3D

func _ready() -> void:
	var g := StaticBody3D.new(); var cs := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(60, 1, 60)
	cs.shape = bs; cs.position = Vector3(0, -0.5, 0); g.add_child(cs); add_child(g)
	var gm := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(60, 60); gm.mesh = pm
	var mat := StandardMaterial3D.new(); var c := Color("5f7a3a"); mat.albedo_color = c * c; mat.roughness = 1.0; gm.material_override = mat; g.add_child(gm)
	building = BuildingKit.build(KitLayouts.TEST_ROOM if layout_name == "test_room" else KitLayouts.GULL_LANTERN); building.position = Vector3(-4, 0, 3); add_child(building)
	print("KIT %s %d triangles, %d ms, %.1f m tall" % [layout_name, building.get_meta("triangles"), building.get_meta("build_ms"), building.get_meta("height")])
	print("KIT parts %s" % [building.get_meta("parts")])
	var pl := get_parent().get_node_or_null("Player") as Node3D
	if pl: pl.global_position = building.position + (Vector3(3.1, 0.1, 5.0) if layout_name == "test_room" else Vector3(5.05, 0.1, 5.0))
