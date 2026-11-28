## Fogwright's voxel art (docs/design.md, Voxel art): reading MagicaVoxel .vox files into the game.
## - One size for everything seen together: CHAR (5 cm) for characters, weapons, armour and props; WORLD (10 cm, exactly two
##   of the small ones) for buildings, walls, terrain features and trees.
## - A file is a scene of models; each named model becomes a part. Character parts animate as rigid pieces: parts named
##   head and torso pivot at their bottom centre, limbs (arm_upper_l, arm_lower_l, leg_upper_l, leg_lower_l and _r) at their
##   top centre, and a lower limb hangs from its upper one.
## - Colours can be snapped to one palette (snap), so models from different packs match.
## - check(): the scale rule, as the city-planning checker does for buildings: a model's height against the real size of
##   what it is (a person 1.4 to 2.1 m by people, a door 2 m ...).
## Axes: MagicaVoxel x across, y front (0) to back, z up -> Godot y up, the front toward +Z (as the player's model faces).
class_name Vox
extends RefCounted

const CHAR := 0.05
const WORLD := 0.10

## the parsed file: {models: [{size: Vector3i, voxels: PackedByteArray (x, y, z, colour index per voxel)}],
##   palette: [Color x 256], shapes: [{name, model, offset: Vector3i (the model's corner in the file's voxel space)}]}
static func read(path: String) -> Dictionary:
	var b := FileAccess.get_file_as_bytes(path)
	if b.size() < 20 or b.slice(0, 4).get_string_from_ascii() != "VOX ": push_warning("not a .vox file: " + path); return {}
	var out := {"models": [], "palette": [], "shapes": []}
	var nodes := {}
	var p := 20   # past "VOX ", the version and MAIN's header
	var size := Vector3i.ZERO
	while p + 12 <= b.size():
		var id := b.slice(p, p + 4).get_string_from_ascii(); var n := b.decode_s32(p + 4); var c := p + 12
		match id:
			"SIZE": size = Vector3i(b.decode_s32(c), b.decode_s32(c + 4), b.decode_s32(c + 8))
			"XYZI":
				var cnt := b.decode_s32(c)
				out.models.append({"size": size, "voxels": b.slice(c + 4, c + 4 + cnt * 4)})
			"RGBA":
				for i in 256: out.palette.append(Color8(b[c + i * 4], b[c + i * 4 + 1], b[c + i * 4 + 2], b[c + i * 4 + 3]))
			"nTRN":
				var q := [c]; var nid := _i(b, q); var attr := _dict(b, q); var child := _i(b, q); _i(b, q); _i(b, q)
				var frames := _i(b, q); var fr := _dict(b, q) if frames > 0 else {}
				var t := Vector3i.ZERO
				if fr.has("_t"): var v: PackedStringArray = str(fr._t).split(" "); t = Vector3i(int(v[0]), int(v[1]), int(v[2]))
				nodes[nid] = {"kind": "t", "name": attr.get("_name", ""), "child": child, "t": t}
			"nGRP":
				var q := [c]; var nid := _i(b, q); _dict(b, q); var k := _i(b, q); var ch := []
				for i in k: ch.append(_i(b, q))
				nodes[nid] = {"kind": "g", "children": ch}
			"nSHP":
				var q := [c]; var nid := _i(b, q); _dict(b, q); _i(b, q); var mid := _i(b, q)
				nodes[nid] = {"kind": "s", "model": mid}
		p = c + n   # into children (MAIN's are read in sequence)
	if out.palette.is_empty():
		for i in 256: out.palette.append(Color(0.6, 0.6, 0.6))
	if nodes.is_empty():
		for i in out.models.size(): out.shapes.append({"name": "part%d" % i, "model": i, "offset": Vector3i.ZERO})
	else:
		_walk(nodes, 0, Vector3i.ZERO, "", out)
	return out

static func _i(b: PackedByteArray, q: Array) -> int:
	var v := b.decode_s32(q[0]); q[0] += 4; return v

static func _str(b: PackedByteArray, q: Array) -> String:
	var n := _i(b, q); var s := b.slice(q[0], q[0] + n).get_string_from_utf8(); q[0] += n; return s

static func _dict(b: PackedByteArray, q: Array) -> Dictionary:
	var d := {}; var n := _i(b, q)
	for i in n: var k := _str(b, q); d[k] = _str(b, q)
	return d

## walks the scene graph, adding translations (rotations in .vox scenes are not used by our parts)
static func _walk(nodes: Dictionary, id: int, t: Vector3i, name: String, out: Dictionary) -> void:
	if not nodes.has(id): return
	var nd: Dictionary = nodes[id]
	match nd.kind:
		"t": _walk(nodes, nd.child, t + nd.t, nd.name if nd.name != "" else name, out)
		"g":
			for ch in nd.children: _walk(nodes, ch, t, name, out)
		"s":
			var m: Dictionary = out.models[nd.model]; var sz: Vector3i = m.size
			out.shapes.append({"name": name if name != "" else "part%d" % out.shapes.size(), "model": nd.model, "offset": t - Vector3i(sz.x / 2, sz.y / 2, sz.z / 2)})

## the nearest palette colour (palette: Array of Color), by a weighted RGB distance close to how the eye judges it
static func snap(c: Color, palette: Array) -> Color:
	var best: Color = c; var bd := INF
	for p: Color in palette:
		var dr: float = c.r - p.r; var dg: float = c.g - p.g; var db: float = c.b - p.b
		var dd: float = 2.0 * dr * dr + 4.0 * dg * dg + 3.0 * db * db
		if dd < bd: bd = dd; best = p
	return best

## one part's mesh: every voxel face not covered by another voxel of the same part, coloured, with a little shade baked in
## (faces lit from above, darker below); vertices relative to `pivot` (in voxels, file space), at `size` metres per voxel
static func part_mesh(f: Dictionary, shape: Dictionary, pivot: Vector3, size: float, palette := []) -> ArrayMesh:
	var m: Dictionary = f.models[shape.model]; var v: PackedByteArray = m.voxels; var off: Vector3i = shape.offset
	var filled := {}
	for i in v.size() / 4: filled[Vector3i(v[i * 4], v[i * 4 + 1], v[i * 4 + 2])] = v[i * 4 + 3]
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	const DIRS := [[Vector3i(1, 0, 0), 0.86], [Vector3i(-1, 0, 0), 0.86], [Vector3i(0, 1, 0), 0.8], [Vector3i(0, -1, 0), 0.92], [Vector3i(0, 0, 1), 1.0], [Vector3i(0, 0, -1), 0.62]]
	for k in filled:
		var ci: int = filled[k]; var col: Color = f.palette[ci - 1]
		if not palette.is_empty(): col = snap(col, palette)
		for dd in DIRS:
			var n: Vector3i = dd[0]
			if filled.has(k + n): continue
			var shade: float = dd[1]
			var corners := _face(k, n)
			var gn := _g(Vector3(n))
			st.set_color(Color(col.r * shade, col.g * shade, col.b * shade)); st.set_normal(gn)
			var q := []
			for cr in corners: q.append(_g(Vector3(cr) + Vector3(off) - pivot) * size)
			for idx in [0, 1, 2, 0, 2, 3]: st.add_vertex(q[idx])
	return st.commit()

## a face's four corners (in voxel corner coordinates), wound to face outward after the axis change
static func _face(k: Vector3i, n: Vector3i) -> Array:
	var x := k.x; var y := k.y; var z := k.z
	var c: Array
	if n.x == 1: c = [Vector3i(x + 1, y, z), Vector3i(x + 1, y + 1, z), Vector3i(x + 1, y + 1, z + 1), Vector3i(x + 1, y, z + 1)]
	elif n.x == -1: c = [Vector3i(x, y, z), Vector3i(x, y, z + 1), Vector3i(x, y + 1, z + 1), Vector3i(x, y + 1, z)]
	elif n.y == 1: c = [Vector3i(x, y + 1, z), Vector3i(x, y + 1, z + 1), Vector3i(x + 1, y + 1, z + 1), Vector3i(x + 1, y + 1, z)]
	elif n.y == -1: c = [Vector3i(x, y, z), Vector3i(x + 1, y, z), Vector3i(x + 1, y, z + 1), Vector3i(x, y, z + 1)]
	elif n.z == 1: c = [Vector3i(x, y, z + 1), Vector3i(x + 1, y, z + 1), Vector3i(x + 1, y + 1, z + 1), Vector3i(x, y + 1, z + 1)]
	else: c = [Vector3i(x, y, z), Vector3i(x, y + 1, z), Vector3i(x + 1, y + 1, z), Vector3i(x + 1, y, z)]
	return c

## MagicaVoxel (x, y front-to-back, z up) -> Godot (y up, the front toward +Z): a rotation, so faces keep their winding
static func _g(p: Vector3) -> Vector3:
	return Vector3(-p.x, p.z, p.y)

static var _mat: StandardMaterial3D

## a character from a .vox: a Node3D (feet at y = 0, centred, facing +Z) with a node per part pivoting at its joint, lower
## limbs hanging from upper ones; parts are reachable by name (model.get_node("arm_upper_l"))
static func character(path: String, size := CHAR, palette := []) -> Node3D:
	var f := read(path)
	var root := Node3D.new(); root.name = path.get_file().get_basename()
	if f.is_empty(): return root
	if _mat == null:
		_mat = StandardMaterial3D.new(); _mat.vertex_color_use_as_albedo = true; _mat.vertex_color_is_srgb = true; _mat.roughness = 1.0   # .vox colours are sRGB
	var lo := Vector3(INF, INF, INF); var hi := -lo; var bounds := {}
	for sh in f.shapes:
		var m: Dictionary = f.models[sh.model]; var a := Vector3(sh.offset); var b := a + Vector3(m.size)
		bounds[sh.name] = [a, b]; lo = lo.min(a); hi = hi.max(b)
	var centre := Vector3((lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0, lo.z)   # the feet's centre
	var pivots := {}
	for sh in f.shapes:
		var a: Vector3 = bounds[sh.name][0]; var b: Vector3 = bounds[sh.name][1]
		var top: bool = sh.name.begins_with("arm_") or sh.name.begins_with("leg_")
		pivots[sh.name] = Vector3((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, b.z if top else a.z)
	var made := {}
	for sh in f.shapes:
		var node := MeshInstance3D.new(); node.name = sh.name
		node.mesh = part_mesh(f, sh, pivots[sh.name], size, palette); node.material_override = _mat
		made[sh.name] = node
	for sh in f.shapes:
		var nm: String = sh.name; var parent_name := nm.replace("_lower_", "_upper_") if "_lower_" in nm else ""
		var parent: Node3D = made.get(parent_name, root)
		parent.add_child(made[nm])
		var base: Vector3 = pivots[parent_name] if parent != root else centre
		made[nm].position = _g(pivots[nm] - base) * size
	return root

## the scale check: a model's height in metres against what it should be; returns "" if right, else what is wrong
static func check(path: String, kind: String, size := CHAR) -> String:
	const REAL := {"person": [1.35, 2.15], "door": [1.9, 2.3], "sword": [0.7, 1.2]}
	var f := read(path)
	if f.is_empty(): return "cannot read"
	var lo := INF; var hi := -INF
	for sh in f.shapes:
		var m: Dictionary = f.models[sh.model]; lo = minf(lo, sh.offset.z); hi = maxf(hi, sh.offset.z + m.size.z)
	var h := (hi - lo) * size; var r: Array = REAL.get(kind, [0.0, INF])
	return "" if h >= r[0] and h <= r[1] else "%.2f m tall, a %s should be %.2f to %.2f m" % [h, kind, r[0], r[1]]
