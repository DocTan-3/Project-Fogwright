extends Node
## measures each kit building's real footprint in its plot's frame (plan metres: x along w, z along h, centred on the
## plot) and writes data/kit_footprints.json, so the plan and the terraces can make room for what the kit really builds:
##   godot --headless --path . res://tests/footprints.tscn
func _ready() -> void:
	var lvl: Node3D = load("res://scenes/farhallow_voxel.tscn").instantiate(); add_child(lvl)
	for k in 3: await get_tree().process_frame
	print("FOOTSTART ", lvl.get_child_count(), " ", lvl.get_child(0).name if lvl.get_child_count() else "")
	var out := {}
	for i in 40:
		var h := lvl.find_child("Building%d" % i, true, false) as Node3D
		if h == null: continue
		var inv := h.global_transform.affine_inverse()
		var lo := Vector3(INF, INF, INF); var hi := -lo; var wlo := lo; var whi := hi
		for mi in h.find_children("*", "MeshInstance3D", true, false):
			var m := mi as MeshInstance3D
			var a: AABB = (inv * m.global_transform) * m.get_aabb()
			lo = lo.min(a.position); hi = hi.max(a.end)
		for cs in h.find_children("*", "CollisionShape3D", true, false):   # what you walk into
			var c := cs as CollisionShape3D
			if c.shape == null: continue
			var a2: AABB = (inv * c.global_transform) * _shape_aabb(c.shape)
			if a2.size.y < 0.3: continue
			wlo = wlo.min(a2.position); whi = whi.max(a2.end)
		out[str(i)] = {"min": [lo.x, lo.z], "max": [hi.x, hi.z], "solid_min": [wlo.x, wlo.z], "solid_max": [whi.x, whi.z], "top": hi.y}
		print("FOOT %d  x %.1f..%.1f  z %.1f..%.1f   solid x %.1f..%.1f z %.1f..%.1f" % [i, lo.x, hi.x, lo.z, hi.z, wlo.x, whi.x, wlo.z, whi.z])
	var f := FileAccess.open("res://data/kit_footprints.json", FileAccess.WRITE); f.store_string(JSON.stringify(out, " ")); f.close()
	get_tree().quit()

func _shape_aabb(s: Shape3D) -> AABB:
	if s is BoxShape3D: return AABB(-(s as BoxShape3D).size * 0.5, (s as BoxShape3D).size)
	if s is ConcavePolygonShape3D or s is ConvexPolygonShape3D:
		var pts: PackedVector3Array = (s as ConcavePolygonShape3D).get_faces() if s is ConcavePolygonShape3D else (s as ConvexPolygonShape3D).points
		var a := AABB(pts[0], Vector3.ZERO) if pts.size() > 0 else AABB()
		for p in pts: a = a.expand(p)
		return a
	return AABB()
