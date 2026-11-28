extends SceneTree
## the size of each Medieval Voxel Assets model in metres, and the voxel size it implies (its smallest step)
func _init() -> void:
	var d := "res://assets/buildings/medieval_voxel/"
	for sub in ["Houses", "Shops", "Towers", "Walls", "Others", "Lamps", "Bridges"]:
		for f in DirAccess.get_files_at(d + sub):
			if not f.ends_with(".glb"): continue
			var n: Node = (load(d + sub + "/" + f) as PackedScene).instantiate()
			var box := AABB(); var first := true; var xs := {}
			for mi in n.find_children("*", "MeshInstance3D", true, false):
				var m := mi as MeshInstance3D; var t: Transform3D = m.get_global_transform() if m.is_inside_tree() else _xf(m)
				var a := t * m.mesh.get_aabb()
				box = a if first else box.merge(a); first = false
				for v in m.mesh.get_faces(): xs[snappedf((t * v).y, 0.0001)] = true
			var ys := xs.keys(); ys.sort(); var step := INF
			for i in range(1, ys.size()): step = minf(step, ys[i] - ys[i - 1])
			print("%-28s %5.2f x %5.2f x %5.2f m  step %.3f" % [sub + "/" + f.get_basename(), box.size.x, box.size.y, box.size.z, step])
			n.free()
	quit()
func _xf(n: Node) -> Transform3D:
	var t := Transform3D.IDENTITY
	while n != null and n is Node3D: t = (n as Node3D).transform * t; n = n.get_parent()
	return t
