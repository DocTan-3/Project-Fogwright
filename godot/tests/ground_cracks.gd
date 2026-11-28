extends Node
## counts the open edges in voxel Farhallow's ground surface: an edge only one triangle uses, away from the land's border
## and from cliffs, is a crack (a T-junction) that shows as a dark seam; edges whose ends differ in the last bit are
## slivers that show as dotted lines. Prints OPEN, CRACKS and SLIVERS; CRACKS 0 and SLIVERS 0 are right.
##   godot --headless --path . res://tests/ground_cracks.tscn
func _ready() -> void:
	var sc: Node = (load("res://scenes/farhallow_voxel.tscn") as PackedScene).instantiate(); add_child(sc)
	await get_tree().process_frame
	var surf: MeshInstance3D = sc.find_child("Surface", true, false)
	var v: PackedVector3Array = (surf.mesh as ArrayMesh).surface_get_arrays(0)[Mesh.ARRAY_VERTEX]
	var key := func(p: Vector3) -> Vector3i: return Vector3i(roundi(p.x * 1000), roundi(p.y * 1000), roundi(p.z * 1000))
	var exact := {}   # edges by their exact floats: an edge whose ends match to the millimetre but not exactly is a sliver
	var uses := {}; var pts := {}
	for t in range(0, v.size(), 3):
		for e in [[0, 1], [1, 2], [2, 0]]:
			var a: Vector3i = key.call(v[t + e[0]]); var b: Vector3i = key.call(v[t + e[1]])
			var k := [a, b] if [a.x, a.z] < [b.x, b.z] else [b, a]
			uses[k] = uses.get(k, 0) + 1
			var ea: Vector3 = v[t + e[0]]; var eb: Vector3 = v[t + e[1]]
			var ek := [ea, eb] if [ea.x, ea.z] < [eb.x, eb.z] else [eb, ea]
			exact[ek] = exact.get(ek, 0) + 1
	# an open edge that has another open edge lying along it (a vertex in its middle) is a T-junction
	var open := []
	for k in uses: if uses[k] == 1: open.append(k)
	var verts := {}
	for k in open: verts[k[0]] = true; verts[k[1]] = true
	var cracks := 0
	for k in open:
		var a := Vector3(k[0]); var b := Vector3(k[1])
		for d in [0.25, 0.5, 0.75]:
			if verts.has(key.call(a.lerp(b, d) / 1000.0)): cracks += 1; break
	var exact_open := 0
	for k in exact: if exact[k] == 1: exact_open += 1
	print("OPEN %d CRACKS %d SLIVERS %d" % [open.size(), cracks, exact_open - open.size()])
	get_tree().quit()
