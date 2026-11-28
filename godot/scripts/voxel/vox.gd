## Fogwright's voxel art (docs/design.md, Voxel art): reading MagicaVoxel .vox files into the game.
## - Voxel sizes, each a whole number of the smallest: FINE (2.5 cm) for characters, gear and weapons - steampunk needs its
##   tubes, hoses and buckles; CHAR (5 cm) for props; WORLD (10 cm) for buildings, walls, terrain features and trees.
## - A file is a scene of models; each named model becomes a part. Character parts animate as rigid pieces: parts named
##   head and torso pivot at their bottom centre, limbs (arm_upper_l, arm_lower_l, hand_l, leg_upper_l, leg_lower_l, foot_l
##   and _r) at their top centre; a lower limb hangs from its upper one, a hand from the lower arm, a foot from the lower leg.
##   A part may be finer than the rest, named "<part>#<k>" (head#2: half-size voxels), its voxels and offset in its own
##   units. Meshes are greedy-meshed: flat runs of one colour merge into large faces.
##   Modular gear is a part named "<piece>@<part>" (goggles@head, tank@torso): it rides on that part.
##   Any part may carry a tilt, "~" and degrees per axis in the game's axes (x pitch, y turn, z roll: braid@head~x-8z5):
##   it turns about the point of its box nearest its parent's joint (a braid from its top, a brow from its inner end) -
##   the off-grid angles that make voxel characters look alive (MagicaVoxel itself only stores quarter turns).
##   A character stands in a relaxed rest pose (REST), not stiffly straight. Armour that replaces a
##   part (boots for the feet) is a file whose parts take the body part's name, loaded over the base.
## - Colours can be snapped to one palette (snap), so models from different packs match.
## - check(): the scale rule, as the city-planning checker does for buildings: a model's height against the real size of
##   what it is (a person 1.4 to 2.1 m by people, a door 2 m ...).
## Axes: MagicaVoxel x across, y front (0) to back, z up -> Godot y up, the front toward +Z (as the player's model faces).
class_name Vox
extends RefCounted

const FINE := 0.025
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

## one part's mesh, greedy-meshed: for each of the six directions and each layer, the visible faces of one colour are
## merged into the largest rectangles, so a flat run of skin or brass is two triangles, not two per voxel. Shade is baked
## per direction (lit from above, darker below). Vertices relative to `pivot` (in base voxels, file space), `size` metres
## per base voxel; a part made at `fine` times the base resolution (a head at 1.25 cm on a 2.5 cm body) has its voxels and
## offset in its own finer units.
static func part_mesh(f: Dictionary, shape: Dictionary, pivot: Vector3, size: float, palette := [], fine := 1) -> ArrayMesh:
	var m: Dictionary = f.models[shape.model]; var v: PackedByteArray = m.voxels; var off: Vector3i = shape.offset
	var col_at := {}
	for i in v.size() / 4:
		var key := Vector3i(v[i * 4], v[i * 4 + 1], v[i * 4 + 2])
		var c: Color = m.colors[i] if m.has("colors") else f.palette[v[i * 4 + 3] - 1]
		if not palette.is_empty(): c = snap(c, palette)
		col_at[key] = c
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	const DIRS := [[0, 1, 0.86], [0, -1, 0.86], [1, 1, 0.8], [1, -1, 0.92], [2, 1, 1.0], [2, -1, 0.62]]   # axis, sign, shade
	for dd in DIRS:
		var ax: int = dd[0]; var sg: int = dd[1]; var shade: float = dd[2]
		var ua := (ax + 1) % 3; var va := (ax + 2) % 3
		var n := Vector3i.ZERO; n[ax] = sg
		var layers := {}   # layer -> {Vector2i(u, v): colour} of the visible faces in it
		for key in col_at:
			var k: Vector3i = key
			if col_at.has(k + n): continue
			if not layers.has(k[ax]): layers[k[ax]] = {}
			layers[k[ax]][Vector2i(k[ua], k[va])] = col_at[k]
		for L in layers:
			var mask: Dictionary = layers[L]
			var done := {}
			var cells := mask.keys(); cells.sort()
			for c0 in cells:
				var cv: Vector2i = c0
				if done.has(cv): continue
				var col: Color = mask[cv]
				var w := 1
				while mask.has(Vector2i(cv.x + w, cv.y)) and not done.has(Vector2i(cv.x + w, cv.y)) and mask[Vector2i(cv.x + w, cv.y)] == col: w += 1
				var h := 1
				var grow := true
				while grow:
					for du in w:
						var q := Vector2i(cv.x + du, cv.y + h)
						if not mask.has(q) or done.has(q) or mask[q] != col: grow = false; break
					if grow: h += 1
				for du in w:
					for dv in h: done[Vector2i(cv.x + du, cv.y + dv)] = true
				var corners := _rect(ax, sg, L, cv.x, cv.x + w, cv.y, cv.y + h)
				st.set_color(Color(col.r * shade, col.g * shade, col.b * shade)); st.set_normal(_g(Vector3(n)))
				var qv := []
				for cr in corners: qv.append(_g((Vector3(cr) + Vector3(off)) / float(fine) - pivot) * size)
				for idx in [0, 2, 1, 0, 3, 2]: st.add_vertex(qv[idx])   # Godot's front faces wind clockwise
	return st.commit()

## a merged face's corners: the layer L along `ax`, spanning u0..u1 and v0..v1 on the next two axes (x: y, z; y: z, x;
## z: x, y), wound outward the same way as _face
static func _rect(ax: int, sg: int, L: int, u0: int, u1: int, v0: int, v1: int) -> Array:
	var d := L + 1 if sg > 0 else L
	var P := func(u: int, vv: int) -> Vector3i:
		var r := Vector3i.ZERO; r[ax] = d; r[(ax + 1) % 3] = u; r[(ax + 2) % 3] = vv; return r
	if sg > 0: return [P.call(u0, v0), P.call(u1, v0), P.call(u1, v1), P.call(u0, v1)]
	return [P.call(u0, v0), P.call(u0, v1), P.call(u1, v1), P.call(u1, v0)]

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
	return Vector3(p.x, p.z, -p.y)

static var _mat: StandardMaterial3D
static var _cmap := {}

## a character from a .vox: a Node3D (feet at y = 0, centred, facing +Z) with a node per part pivoting at its joint, lower
## limbs hanging from upper ones; parts are reachable by name (model.get_node("arm_upper_l"))
## layers: further .vox files in the same frame (gear riding on parts, or parts that replace the base's by name)
static func character(path: String, size := CHAR, palette := [], layers := []) -> Node3D:
	var f := read(path)
	var root := Node3D.new(); root.name = path.get_file().get_basename()
	if f.is_empty(): return root
	for lp in layers:   # merge: one model list, one palette per model's colours baked in, shapes by name (replacing same names)
		var g := read(lp)
		if g.is_empty(): continue
		var base_n: int = f.models.size()
		for m in g.models:
			var v: PackedByteArray = m.voxels.duplicate()
			var cols := []
			for i in v.size() / 4: cols.append(g.palette[v[i * 4 + 3] - 1])
			f.models.append({"size": m.size, "voxels": v, "colors": cols})
		var face := false   # a face layer (it has a head): the base head's own pieces (brows, hair, beard) all go with it
		for sh in g.shapes: face = face or _bare(sh.name) == "head"
		var gone := {}
		for sh in g.shapes: gone[_bare(sh.name)] = true
		for k in range(f.shapes.size() - 1, -1, -1):
			var bn := _bare(f.shapes[k].name)
			if gone.has(bn) or (face and bn.ends_with("@head")): f.shapes.remove_at(k)
		for sh in g.shapes: f.shapes.append({"name": sh.name, "model": base_n + sh.model, "offset": sh.offset})
	if _mat == null:
		_mat = StandardMaterial3D.new(); _mat.vertex_color_use_as_albedo = true; _mat.vertex_color_is_srgb = true; _mat.roughness = 1.0   # .vox colours are sRGB
	var lo := Vector3(INF, INF, INF); var hi := -lo; var bounds := {}; var fine := {}; var tilts := {}
	var shapes := []   # names without the "#k" that marks a finer part; bounds in base voxels
	for sh0 in f.shapes:
		var sh: Dictionary = sh0.duplicate(); var full: String = sh.name
		var tilt := full.get_slice("~", 1) if "~" in full else ""; full = full.get_slice("~", 0)
		var k := int(full.get_slice("#", 1)) if "#" in full else 1
		sh.name = full.get_slice("#", 0); fine[sh.name] = maxi(1, k); shapes.append(sh)
		if tilt != "": tilts[sh.name] = _tilt(tilt)
		var m: Dictionary = f.models[sh.model]; var a := Vector3(sh.offset) / float(fine[sh.name]); var b := a + Vector3(m.size) / float(fine[sh.name])
		bounds[sh.name] = [a, b]; lo = lo.min(a); hi = hi.max(b)
	f = f.duplicate(); f.shapes = shapes
	var pivots := {}
	for sh in f.shapes:
		var a: Vector3 = bounds[sh.name][0]; var b: Vector3 = bounds[sh.name][1]
		var top: bool = sh.name.begins_with("arm_") or sh.name.begins_with("leg_") or sh.name.begins_with("hand_") or sh.name.begins_with("foot_")
		pivots[sh.name] = Vector3((a.x + b.x) / 2.0, (a.y + b.y) / 2.0, b.z if top else a.z)
	for sh in f.shapes:   # gear rides on its part: the same pivot, so it moves exactly with it
		if "@" in sh.name and pivots.has(sh.name.get_slice("@", 1)): pivots[sh.name] = pivots[sh.name.get_slice("@", 1)]
	for nm in tilts:   # a tilted piece turns about its own point nearest its parent's joint
		var pj: Vector3 = pivots.get(_parent(nm), Vector3.ZERO)
		pivots[nm] = pj.clamp(bounds[nm][0], bounds[nm][1])
	var outer := {}   # bounds from body parts only, so a tank on the back does not move the feet's centre
	lo = Vector3(INF, INF, INF); hi = -lo
	for sh in f.shapes:
		if "@" in sh.name: continue
		lo = lo.min(bounds[sh.name][0]); hi = hi.max(bounds[sh.name][1])
	var centre := Vector3((lo.x + hi.x) / 2.0, (lo.y + hi.y) / 2.0, lo.z)   # the feet's centre
	var made := {}
	for sh in f.shapes:
		var node := MeshInstance3D.new(); node.name = sh.name
		node.mesh = part_mesh(f, sh, pivots[sh.name], size, palette, fine[sh.name]); node.material_override = _mat
		made[sh.name] = node
	for sh in f.shapes:
		var nm: String = sh.name; var parent_name := _parent(nm)
		var parent: Node3D = made.get(parent_name, root)
		parent.add_child(made[nm])
		var base: Vector3 = pivots[parent_name] if parent != root else centre
		made[nm].position = _g(pivots[nm] - base) * size
		made[nm].rotation_degrees = tilts.get(nm, Vector3.ZERO) + REST.get(nm, Vector3.ZERO)
		made[nm].set_meta("rest", made[nm].rotation_degrees)   # animation adds to this
	return root

## the rest pose, degrees per part (game axes; the character faces +Z, its left is +X): arms hang a little away from the
## body and bent at the elbow, fists turned in, legs a little apart, feet turned out, the head tipped - as a person stands
const REST := {
	"arm_upper_l": Vector3(4, 0, 9), "arm_upper_r": Vector3(4, 0, -9), "arm_lower_l": Vector3(-10, 0, -2), "arm_lower_r": Vector3(-10, 0, 2),
	"hand_l": Vector3(-4, -14, 0), "hand_r": Vector3(-4, 14, 0), "leg_upper_l": Vector3(0, 0, 3), "leg_upper_r": Vector3(0, 0, -3),
	"leg_lower_l": Vector3(0, 0, -3), "leg_lower_r": Vector3(0, 0, 3), "foot_l": Vector3(0, 12, 0), "foot_r": Vector3(0, -12, 0),
	"head": Vector3(-3, 4, 2), "torso": Vector3(0, -2, 0)}

## a part's name without its finer-resolution mark and its tilt: the name that replaces and is replaced
static func _bare(n: String) -> String: return n.get_slice("~", 0).get_slice("#", 0)

## the part a part hangs from: gear from the part it rides on, lower limbs from upper ones, hands and feet from the lower
static func _parent(nm: String) -> String:
	if "@" in nm: return nm.get_slice("@", 1)
	if "_lower_" in nm: return nm.replace("_lower_", "_upper_")
	if nm.begins_with("hand_"): return "arm_lower_" + nm.substr(5)
	if nm.begins_with("foot_"): return "leg_lower_" + nm.substr(5)
	return ""

## "x-8z5" -> Vector3(-8, 0, 5)
static func _tilt(t: String) -> Vector3:
	var v := Vector3.ZERO; var re := RegEx.create_from_string("([xyz])(-?[0-9.]+)")
	for m in re.search_all(t): v["xyz".find(m.get_string(1))] = float(m.get_string(2))
	return v

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

## a voxel model exported from MagicaVoxel as .glb (packs such as Medieval Voxel Assets), ready to place: its palette
## texture read pixel-exact (no blending between neighbouring palette colours, which washes them out) and matte, as
## our own voxels are
static func prop(path: String) -> Node3D:
	var n: Node3D = (load(path) as PackedScene).instantiate()
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		for s in m.mesh.get_surface_count():
			var src := m.get_active_material(s)
			if not (src is StandardMaterial3D): continue
			var mat: StandardMaterial3D = src.duplicate()
			mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST; mat.roughness = 1.0; mat.metallic_specular = 0.2
			m.set_surface_override_material(s, mat)
	return n
