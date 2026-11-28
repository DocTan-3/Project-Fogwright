## Fogwright's voxel building kit, step 2: the builder (docs/design.md, Voxel buildings and interiors). It assembles a
## building from the pieces in kit_farhallow.vox (tools/voxel/make_building_kit.py) on the 2 m module, from a layout:
##   {"size": Vector2i(8, 6),                       # modules (2 m) along the front (x) and in depth
##    "storeys": [{"h": 44,                         # floor to floor in voxels: 44 (4.4 m, inns and halls) or 30 (3.0 m)
##                 "face": "stone" | "frame",       # fieldstone or timber frame over limewash
##                 "walls": {"front": "pwdwp...", "right": "...", "back": "...", "left": "..."},
##                 "inner": [{"at": Vector2i(4, 0), "dir": "y", "bays": "ppdp"}],   # partitions from a grid point; their
##                                                  # doors swing to the wall's left ("swing": -1 for its right)
##                 "stairs": [{"at": Vector2i(4, 43), "run": "+x"}],                # voxel corner of its first step
##                 "lights": [{"at": Vector3(2, 3.2, -2), "energy": 1.4}]}, ...],   # metres, from the front-left corner
##    "roof": "thatch" | "slate"}                   # a 45 degree gable roof, ridge along x, 0.3 m overhang
## A bay letter per 2 m: p plain, d door, w window, . open. The front is the +Z side (the way characters face), walls run
## round it anticlockwise from above: front left to right, right side front to back, back right to left, left back to front.
## Each piece's voxels are stamped into one set per storey (and one for the roof), then greedy-meshed once: faces between
## pieces vanish, corners close themselves, and the building costs a draw call per storey. Collision is boxes, as the
## plan says: one per wall bay (a door bay leaves its opening), one per floor strip round a stair well, a ramp per stair
## and per door step, one per roof slope. Doors are their own leaves on a hinge (KitDoor) and swing open as you come.
## Node: the building, its origin the front-left corner at ground level; children "Storey0".., "Roof", "Doors", "Body".
class_name BuildingKit
extends RefCounted

const KIT := "res://assets/voxel/buildings/kit_farhallow.vox"
const V := 0.1            # metres per voxel
const BAY := 20
const WALL := 3
const PLINTH := 5
const DOOR := [4, 17, 0, 21]     # the opening in a door bay (x0, x1, z0, z1), as make_building_kit.py cuts it
const WIN := [7, 14, 9, 18]
const OVERHANG := 3
## bump when the builder or the kit changes what it makes: baked buildings with an older stamp are built again
const BAKE_VERSION := 1

static var _pieces := {}  # name -> {Vector3i: Color}, the kit's voxels in each piece's own box
static var _meshes := {}
static var _dormers := []
static var _openings := []   # [set, o, d, x0, x1, z0, z1, kind] of the outer doors and windows, for KitDress
static var _seed := 0
static var _attached := ""   # the gable side a wing leans on its house with
static var _porch_bays := Vector2i(-1, -2)   # the front bays under a porch (their doors get no hood)
static var _leaf := ""      # the layout's door leaf, if it names one   # [bay origin, direction, face] of the dormers this build, set into the roof once it is laid
static var _fittings := {}  # the 5 cm fittings (kit_fittings.vox): name -> {Vector3i: Color}
const FITTINGS := "res://assets/voxel/buildings/kit_fittings.vox"
const FV := 0.05
# fittings people bump into: their box is collision (a lantern or a chest underfoot is not)
const SOLID_FITTINGS := ["table", "bar_counter", "bed", "shelf", "barrel", "desk", "bench"]  # name -> ArrayMesh, for the pieces that move (the door leaf)

static func pieces() -> Dictionary:
	if _pieces.is_empty():
		var f := Vox.read(KIT)
		for sh in f.shapes:
			var m: Dictionary = f.models[sh.model]; var v: PackedByteArray = m.voxels; var d := {}
			for i in v.size() / 4: d[Vector3i(v[i * 4], v[i * 4 + 1], v[i * 4 + 2])] = f.palette[v[i * 4 + 3] - 1]
			_pieces[sh.name] = d
		_meshes = Vox.pieces(KIT)
	return _pieces

static func fittings() -> Dictionary:
	if _fittings.is_empty():
		var f := Vox.read(FITTINGS)
		for sh in f.shapes:
			var m: Dictionary = f.models[sh.model]; var v: PackedByteArray = m.voxels; var d := {}
			for i in v.size() / 4: d[Vector3i(v[i * 4], v[i * 4 + 1], v[i * 4 + 2])] = f.palette[v[i * 4 + 3] - 1]
			_fittings[sh.name] = d
	return _fittings

## a fitting at 5 cm: {"p": "table", "at": Vector2 (metres: x, and depth from the front), "dir": "+x", "z": metres up}
static func _fitting(fs: Dictionary, boxes: Array, ft: Dictionary, z: int) -> void:
	var p: Dictionary = fittings()[ft.p]; var d := _run_dir(ft.get("dir", "+x"))
	var at: Vector2 = ft.at; var o := Vector3i(roundi(at.x * 20), roundi(at.y * 20), z * 2 + roundi(ft.get("z", 0.0) * 20))
	var lo := Vector3i(1 << 20, 1 << 20, 1 << 20); var hi := -lo
	for k in p:
		var q: Vector3i = k; var c := _cell(o, d, q.x, q.y, q.z); fs[c] = p[k]
		lo = lo.min(c); hi = hi.max(c + Vector3i.ONE)
	if ft.p in SOLID_FITTINGS: boxes.append([Vector3(lo) * 0.5, Vector3(hi) * 0.5])

## a chimney stack of coursed stone, 0.8 m square, from z0 to z1 (voxels) at its corner at (x, y), its flue open at the top
static func _chimney(vs: Dictionary, boxes: Array, at: Vector2i, z0: int, z1: int, along := "") -> void:
	var p: Dictionary = pieces()["chimney"]
	if along != "":   # a chimney breast over the hearth: as wide as the hearth, stepping in to the flue's width as it rises
		for k in 4:
			var half := 10 - k * 2
			for zz in range(z0 + k * 3, z0 + k * 3 + 3):
				for a in range(4 - half, 4 + half):
					for b in 7:
						var c := Vector3i(at.x + a, at.y + b, zz) if along == "x" else Vector3i(at.x + b, at.y + a, zz)
						vs[c] = KitDress._tone(KitDress._h(a / 3, zz / 2, 77), false) if not (zz == z0 + k * 3 + 2) else KitDress.DRESSED_D
		boxes.append([Vector3(at.x - (6 if along == "x" else 0), at.y - (6 if along == "y" else 0), z0), Vector3(at.x + (14 if along == "x" else 7), at.y + (14 if along == "y" else 7), z0 + 12)])
	for z in range(z0, z1):
		var from_top := z1 - 1 - z
		var lz := 39 - from_top if from_top < 3 else (z - z0) % 36
		for x in 8:
			for y in 8:
				var k := Vector3i(x, y, lz)
				if p.has(k): vs[Vector3i(at.x + x, at.y + y, z)] = p[k]
				elif from_top >= 3: vs.erase(Vector3i(at.x + x, at.y + y, z))
	for x in range(-1, 9):   # a capstone course, proud all round, and soot at the flue
		for y in range(-1, 9):
			if x < 0 or x > 7 or y < 0 or y > 7:
				vs[Vector3i(at.x + x, at.y + y, z1 - 3)] = KitDress.DRESSED_D; vs[Vector3i(at.x + x, at.y + y, z1 - 2)] = KitDress.DRESSED
			elif (x < 2 or x > 5 or y < 2 or y > 5): vs[Vector3i(at.x + x, at.y + y, z1 - 1)] = Color8(46, 42, 40)
	boxes.append([Vector3(at.x, at.y, z0), Vector3(at.x + 8, at.y + 8, z1)])

# ---------------------------------------------------------------- placing on the grid
# A piece is placed by the corner its box starts at, O (file space voxels: x, y front to back, z up), running along d
# (a unit step in x or y) with its inner side to d's left. That maps its voxel (lx, ly, lz) to the cell whose centre is
# O + d (lx + 0.5) + n (ly + 0.5), n = left of d: a rigid quarter turn, so the grid stays exact.
static func _left(d: Vector2i) -> Vector2i: return Vector2i(-d.y, d.x)

static func _cell(o: Vector3i, d: Vector2i, lx: int, ly: int, lz: int) -> Vector3i:
	var n := _left(d)
	var cx := 2 * o.x + d.x * (2 * lx + 1) + n.x * (2 * ly + 1); var cy := 2 * o.y + d.y * (2 * lx + 1) + n.y * (2 * ly + 1)
	return Vector3i((cx - 1) / 2, (cy - 1) / 2, o.z + lz)

static func _stamp(into: Dictionary, name: String, o: Vector3i, d: Vector2i) -> void:
	var p: Dictionary = pieces()[name]
	for k in p:
		var q: Vector3i = k; into[_cell(o, d, q.x, q.y, q.z)] = p[k]

## a box given in a piece's own voxels (lo to hi corners) -> [min, max] corners in file space
static func _box(o: Vector3i, d: Vector2i, lo: Vector3i, hi: Vector3i) -> Array:
	var n := _left(d)
	var a := Vector3(o) + Vector3(d.x, d.y, 0) * lo.x + Vector3(n.x, n.y, 0) * lo.y + Vector3(0, 0, lo.z)
	var b := Vector3(o) + Vector3(d.x, d.y, 0) * hi.x + Vector3(n.x, n.y, 0) * hi.y + Vector3(0, 0, hi.z)
	return [a.min(b), a.max(b)]

## file space (voxels) -> the building's local Godot space (metres): x, z up -> y, y front to back -> -z
static func _g(p: Vector3) -> Vector3: return Vector3(p.x, p.z, -p.y) * V

# ---------------------------------------------------------------- the build
static func build(layout: Dictionary) -> Node3D:
	var t0 := Time.get_ticks_msec()
	pieces()
	_dormers = []; _openings = []; _seed = layout.get("seed", 0); _attached = layout.get("attached", "")
	_porch_bays = Vector2i(layout.porch.from, layout.porch.to) if layout.has("porch") else Vector2i(-1, -2)
	var root := Node3D.new(); root.name = "Building"
	var body := StaticBody3D.new(); body.name = "Body"; root.add_child(body)
	var doors := Node3D.new(); doors.name = "Doors"; root.add_child(doors)
	var size: Vector2i = layout.size
	var W := size.x * BAY; var D := size.y * BAY
	var boxes := []           # [min, max] file-space voxel boxes for collision
	var ramps := []           # [from, to, width] file-space top lines
	var z := PLINTH
	var storeys: Array = layout.storeys
	var sets := []
	for s in storeys.size(): sets.append({})
	# the plinth and the flagstone floor on it, with steps up to each front door
	var g0: Dictionary = sets[0]
	for i in size.x:
		for j in size.y: _stamp(g0, "plinth", Vector3i(i * BAY, j * BAY, 0), Vector2i(1, 0))
	var flags: Dictionary = pieces()["floor_" + layout.get("ground", "flags")]
	_leaf = layout.get("door_leaf", "")
	var paint: String = layout.get("paint", "tar")
	if _leaf != "" and pieces().has(_leaf + "_" + paint): _leaf += "_" + paint
	for i in size.x:
		for j in size.y:
			for k in flags: var q: Vector3i = k; g0[Vector3i(i * BAY + q.x, j * BAY + q.y, PLINTH - 1)] = flags[k]
	boxes.append([Vector3(0, 0, 0), Vector3(W, D, PLINTH)])
	var tris := 0; var parts := {}
	var floor_zs := []   # the top of each storey's floor, for the wainscot
	fittings()
	for s in storeys.size():
		var st: Dictionary = storeys[s]; var h: int = st.h; var vs: Dictionary = sets[s]
		var face: String = st.get("face", "frame")
		floor_zs.append(z)
		# the floor of this storey, if it is an upper one: boards over the room below, its joists that room's ceiling,
		# with a well cut where the stair below comes up
		if s > 0:
			var below: Dictionary = storeys[s - 1]
			var wells := []
			for sr in below.get("stairs", []): wells.append(_stair_well(sr, below.h))
			for vd in st.get("voids", []): wells.append([vd.position, vd.size])   # a hall open to the roof
			for vd in st.get("voids", []):   # a trimmer beam round the void's open edges, so the joists end on it
				var r2: Rect2i = vd
				for x in range(r2.position.x - 2, r2.end.x + 2):
					for y in range(r2.position.y - 2, r2.end.y + 2):
						var edge := x >= r2.end.x or y >= r2.end.y or x < r2.position.x or y < r2.position.y
						if edge and x >= WALL and y >= WALL and x < W - WALL and y < D - WALL:
							for zz in range(z - 4, z): vs[Vector3i(x, y, zz)] = Color8(72, 62, 54) if zz > z - 4 else Color8(62, 54, 46)
			_floor(vs, W, D, z - 3, wells, boxes, layout.get("floor", "boards"))
		# walls: the inner partitions first, so the outer walls win where they meet
		for iw in st.get("inner", []):
			var at: Vector2i = iw.at; var dd := Vector2i(1, 0) if iw.dir == "x" else Vector2i(0, 1)
			var o := Vector3i(at.x * BAY, at.y * BAY, z) - Vector3i(_left(dd).x, _left(dd).y, 0)   # centred on the line
			_wall_run(vs, boxes, doors, o, dd, iw.bays, iw.get("face", face), iw.get("h", h), true, iw.get("swing", 1))
		var runs := [["front", Vector3i(0, 0, z), Vector2i(1, 0)], ["right", Vector3i(W, 0, z), Vector2i(0, 1)],
			["back", Vector3i(W, D, z), Vector2i(-1, 0)], ["left", Vector3i(0, D, z), Vector2i(0, -1)]]
		for r in runs:
			var bays: String = st.walls.get(r[0], "p".repeat(size.x if r[0] in ["front", "back"] else size.y))
			_wall_run(vs, boxes, doors, r[1], r[2], bays, face, h, false)
			if s == 0 and PLINTH > 0:
				for b in bays.length():
					if bays[b] == "d" and not (r[0] == "front" and _porch_has(layout, b)): _door_steps(vs, ramps, r[1] - Vector3i(0, 0, z), r[2], b)
		if s == 0 and layout.has("porch"): _porch(vs, ramps, boxes, layout, st.walls.get("front", ""), z)
		for sr in st.get("stairs", []): _stair(vs, ramps, sr, z, h)
		for pc in st.get("pieces", []):   # kit pieces inside (a hearth): at is the piece's corner in voxels, z from the floor
			var at3: Vector3i = pc.at; _stamp(vs, pc.p, Vector3i(at3.x, at3.y, z + at3.z), _run_dir(pc.get("dir", "+x")))
		for pp in st.get("posts", []): _carved_post(vs, boxes, pp.at, z, pp.h)
		for bm in st.get("beams", []):   # [Vector3i from, Vector3i to] in voxels, z from the floor: a tarred timber
			var a: Vector3i = bm[0]; var b2: Vector3i = bm[1]
			for x in range(a.x, b2.x + 1):
				for y in range(a.y, b2.y + 1):
					for zz in range(a.z, b2.z + 1): vs[Vector3i(x, y, z + zz)] = Color8(72, 62, 54) if zz > a.z else Color8(62, 54, 46)
		if st.has("firepit"): _firepit(vs, boxes, st.firepit.at, st.firepit.get("r", 9), z)
		var fs := {}
		for ft in st.get("fittings", []): _fitting(fs, boxes, ft, z)
		if not fs.is_empty():
			var fm := MeshInstance3D.new(); fm.name = "Fittings%d" % s; fm.mesh = Vox.mesh(fs, Vector3i.ZERO, Vector3.ZERO, FV)
			fm.material_override = Vox.grain_material(FV); root.add_child(fm); tris += fm.mesh.get_faces().size() / 3; parts[fm.name] = fm.mesh.get_faces().size() / 3
		for lt in st.get("lights", []):
			var l := OmniLight3D.new(); l.position = lt.at; l.light_energy = lt.get("energy", 1.2)
			l.light_color = lt.get("color", Color(1.0, 0.78, 0.52)); l.omni_range = lt.get("range", 7.0); l.shadow_enabled = false
			root.add_child(l)
		z += h
	# the roof: the attic floor, gables on the side walls and two 45 degree slopes, one set
	var rf := {}
	var knee: bool = storeys[-1].h == 12   # the top floor up in the roof: open to the rafters, no attic floor
	if not knee: _floor(rf, W, D, z - 3, [], boxes, layout.get("floor", "boards"))
	else:   # partitions up there stop under the thatch, under a collar ceiling 3.0 m over the floor
		var top: Dictionary = sets[storeys.size() - 1]
		var cz := z - 12 + 27
		var opens := []
		for vd in storeys[-1].get("voids", []): opens.append([vd.position, vd.size])
		_floor(top, W, D, cz, opens, boxes, layout.get("floor", "boards"), cz - z + 3)
		for vd in storeys[-1].get("voids", []): _trusses(top, vd, z, D)
		for k in top.keys():
			var q: Vector3i = k
			if q.y >= 0 and q.y < D and q.z >= z + mini(q.y, D - 1 - q.y): top.erase(k)
	var top_face: String = storeys[-1].get("face", "frame")
	_roof(rf, ramps, W, D, z, layout.get("roof", "thatch"), top_face)
	if knee:   # over a hall open to the roof, the thatch's underside is boarded: pale wreck boards between the rafters
		for vd in storeys[-1].get("voids", []):
			var r2: Rect2i = vd
			for x in range(r2.position.x, r2.end.x):
				for y in range(WALL, D - WALL):
					var k := Vector3i(x, y, z + mini(y, D - 1 - y))
					if rf.has(k): rf[k] = Color8(160, 144, 120) if (x / 3) % 2 == 0 else Color8(146, 130, 108)
	for dm in _dormers: _dormer(rf, dm[0], dm[1], dm[2])
	for gy in layout.get("gable_windows", []): _gable_window(rf, W, D, z, int(gy * 10.0), top_face)
	var dressed: bool = layout.get("dress", true)
	if dressed: KitDress.dress(sets + [rf], W, D, _openings, PLINTH, KitDress.PAINTS.get(paint, KitDress.PAINTS.tar), _seed, floor_zs)
	if layout.get("rounded", false) and not dressed:   # corners rounded off, as drystone builders on a windy coast lay them
		for vset in sets + [rf]:
			for k in (vset as Dictionary).keys():
				var q: Vector3i = k
				if (q.x == 0 or q.x == W - 1) and (q.y == 0 or q.y == D - 1) and q.z < z: vset.erase(k)
	for ch in layout.get("chimneys", []): _chimney(rf, boxes, ch.at, PLINTH + ch.get("from", 15), z + ch.get("above", 0), ch.get("along", "y"))
	sets.append(rf)
	if layout.get("debug", false): root.set_meta("sets", sets)
	for s in sets.size():
		var vset: Dictionary = sets[s]
		if vset.is_empty(): continue
		var mi := MeshInstance3D.new(); mi.name = "Roof" if s == storeys.size() else "Storey%d" % s
		mi.mesh = Vox.mesh(vset, Vector3i.ZERO, Vector3.ZERO, V); mi.material_override = Vox.grain_material(V); root.add_child(mi)
		tris += mi.mesh.get_faces().size() / 3; parts[mi.name] = mi.mesh.get_faces().size() / 3
	for b in boxes:
		var a: Vector3 = b[0]; var c: Vector3 = b[1]
		if (c - a).x <= 0 or (c - a).y <= 0 or (c - a).z <= 0: continue
		var cs := CollisionShape3D.new(); var sh := BoxShape3D.new()
		var ga := _g(a); var gc := _g(c); sh.size = (gc - ga).abs(); cs.shape = sh; cs.position = (ga + gc) * 0.5
		body.add_child(cs)
	for r in ramps: body.add_child(_ramp(_g(r[0]), _g(r[1]), r[2] * V))
	for d in doors.get_children(): tris += (d as KitDoor).leaf_mesh.get_faces().size() / 3
	for wg in layout.get("wings", []):   # lower wings against a gable: their own buildings, set beside this one
		var saved := [_dormers, _openings, _seed, _porch_bays, _leaf]
		var wb := build(wg.layout); var at: Vector2 = wg.at
		wb.name = "Wing"; wb.position = Vector3(at.x, 0, -at.y); root.add_child(wb)
		tris += wb.get_meta("triangles")
		_dormers = saved[0]; _openings = saved[1]; _seed = saved[2]; _porch_bays = saved[3]; _leaf = saved[4]
	root.set_meta("triangles", tris); root.set_meta("parts", parts); root.set_meta("height", z * V)
	root.set_meta("build_ms", Time.get_ticks_msec() - t0)
	return root

# one run of wall bays from o along d: the bay pieces, their collision and the door leaves
static func _wall_run(vs: Dictionary, boxes: Array, doors: Node3D, o: Vector3i, d: Vector2i, bays: String, face: String, h: int, close: bool, swing := 1) -> void:
	for b in bays.length():
		var c := bays[b]
		var bo := o + Vector3i(d.x, d.y, 0) * (b * BAY)
		if c == ".": continue
		if c == "r":   # a gallery rail over a hall: a handrail at 1.0 m on turned posts every 0.5 m
			for lx in BAY:
				for lz in range(0, 11):
					var post := lx % 5 == 0
					if lz >= 9 or (post and lz < 9) or lz == 0: vs[_cell(bo, d, lx, 1, lz)] = Color8(86, 72, 60) if lz != 10 else Color8(104, 88, 72)
			boxes.append(_box(bo, d, Vector3i(0, 0, 0), Vector3i(BAY, WALL, 11)))
			continue
		if h == 12:   # a knee wall under the roof: plain, or a dormer over it (D)
			_stamp(vs, "wall_%s_12" % face, bo, d)
			boxes.append(_box(bo, d, Vector3i(0, 0, 0), Vector3i(BAY, WALL, 12)))
			if c == "D":
				_dormers.append([bo, d, face]); boxes.append(_box(bo, d, Vector3i(0, 0, 12), Vector3i(BAY, WALL, 29)))
			continue
		var kind: String = {"p": "", "d": "_door", "w": "_window"}[c]
		_stamp(vs, "wall_%s%s_%d" % [face, kind, h], bo, d)
		if not close and c in ["d", "w"]:
			var op: Array = DOOR if c == "d" else WIN
			_openings.append([vs, bo, d, op[0], op[1], op[2], op[3], ("door_porch" if d == Vector2i(1, 0) and bo.y == 0 and b >= _porch_bays.x and b <= _porch_bays.y else "door") if c == "d" else "window"])
		if c == "d":
			boxes.append(_box(bo, d, Vector3i(0, 0, 0), Vector3i(DOOR[0], WALL, h)))
			boxes.append(_box(bo, d, Vector3i(DOOR[1] + 1, 0, 0), Vector3i(BAY, WALL, h)))
			boxes.append(_box(bo, d, Vector3i(DOOR[0], 0, DOOR[3] + 1), Vector3i(DOOR[1] + 1, WALL, h)))
			doors.add_child(_door(bo, d, swing, _leaf if _leaf != "" else ("door_leaf_" + face if _meshes.has("door_leaf_" + face) else "door_leaf")))
		else:
			boxes.append(_box(bo, d, Vector3i(0, 0, 0), Vector3i(BAY, WALL, h)))
			if c == "w":
				_stamp(vs, "window_leaded", bo + Vector3i(d.x, d.y, 0) * WIN[0] + Vector3i(_left(d).x, _left(d).y, WIN[2]), d)
				if face == "dry" and not close:   # shutters, open, on the outer face of the outer walls
					_stamp(vs, "shutters", bo + Vector3i(d.x, d.y, 0) * (WIN[0] - 4) - Vector3i(_left(d).x, _left(d).y, -WIN[2]), d)
	if close and face in ["frame", "board"]:   # a partition's far end gets its post; outer runs are closed by the next run's
		_stamp(vs, ("post_%d" % h) if face == "frame" else ("post_%s_%d" % [face, h]), o + Vector3i(d.x, d.y, 0) * (bays.length() * BAY - 2), d)

# a floor of boards inside the outer walls at height z (its top at z + 3), with wells left open; collision strips round them
static func _floor(vs: Dictionary, W: int, D: int, z: int, wells: Array, boxes: Array, kind := "boards", ym := WALL) -> void:
	var fb: Dictionary = pieces()["floor_" + kind]
	for x in range(WALL, W - WALL):
		for y in range(ym, D - ym):
			var hole := false
			for w in wells:
				if Rect2i(w[0], w[1]).has_point(Vector2i(x, y)): hole = true
			if hole: continue
			for lz in 3:
				var k := Vector3i(x % BAY, y % BAY, lz)
				if fb.has(k): vs[Vector3i(x, y, z + lz)] = fb[k]
	# collision: the floor in rows of 10 cm, runs of floor merged along x, equal runs merged down the rows
	var open_rows := {}
	var prev := ""; var y0 := ym
	for y in range(ym, D - ym + 1):
		var runs := []
		if y < D - ym:
			var x := WALL
			while x < W - WALL:
				var hole := false
				for w in wells:
					if Rect2i(w[0], w[1]).has_point(Vector2i(x, y)): hole = true
				if hole: x += 1; continue
				var x1 := x
				while x1 < W - WALL:
					var h2 := false
					for w in wells:
						if Rect2i(w[0], w[1]).has_point(Vector2i(x1, y)): h2 = true
					if h2: break
					x1 += 1
				runs.append(Vector2i(x, x1)); x = x1
		var key := str(runs)
		if key != prev:
			if prev != "":
				for r in open_rows[prev]: boxes.append([Vector3(r.x, y0, z), Vector3(r.y, y, z + 3)])
			prev = key; y0 = y; open_rows[key] = runs

## the roof trusses over a hall open to the roof: a tie beam at the collar's height and two raking struts every 2 m
static func _trusses(vs: Dictionary, vd: Rect2i, z: int, D: int) -> void:
	var cz := z - 12 + 27
	for x in range(vd.position.x + 17, vd.end.x, 20):
		for xx in [x, x + 1]:
			for y in range(WALL, D - WALL):
				if z + mini(y, D - 1 - y) > cz + 1: vs[Vector3i(xx, y, cz)] = Color8(72, 62, 54); vs[Vector3i(xx, y, cz + 1)] = Color8(86, 72, 60)
			for k in range(0, 12):   # struts from the tie beam up toward the ridge
				vs[Vector3i(xx, D / 2 - 6 + k / 2, cz + 2 + k)] = Color8(72, 62, 54); vs[Vector3i(xx, D / 2 + 5 - k / 2, cz + 2 + k)] = Color8(72, 62, 54)
			for zz in range(cz + 2, cz + 14): vs[Vector3i(xx, D / 2, zz)] = Color8(86, 72, 60)   # the king post
	# the rafters under the thatch every 0.5 m, on a wall plate along the top of each knee wall, and a purlin halfway up
	for x in range(vd.position.x, vd.end.x):
		for y in range(WALL, D - WALL):
			var zr := z + mini(y, D - 1 - y) - 1
			if x % 5 == 0: vs[Vector3i(x, y, zr)] = Color8(78, 66, 56)
			elif mini(y, D - 1 - y) % 20 == 10: vs[Vector3i(x, y, zr)] = Color8(66, 56, 48)
		for y in [WALL, D - WALL - 1]:
			for zz in [z - 2, z - 1]: vs[Vector3i(x, y, zz)] = Color8(72, 62, 54)

# ---------------------------------------------------------------- stairs and steps
static func _run_dir(r: String) -> Vector2i:
	return {"+x": Vector2i(1, 0), "-x": Vector2i(-1, 0), "+y": Vector2i(0, 1), "-y": Vector2i(0, -1)}[r]

## a stair's footprint, as a rect in file space voxels: at is its min corner, the run is 3 per 0.2 m rise, 14 wide
static func _stair_rect(sr: Dictionary, h: int) -> Rect2i:
	var R := _run_dir(sr.run); var L := h / 2 * 3; var at: Vector2i = sr.at
	return Rect2i(at, Vector2i(L, 14)) if R.x != 0 else Rect2i(at, Vector2i(14, L))

## the hole in the floor over a stair: from where a 2.2 m head would meet the joists to the top
static func _stair_well(sr: Dictionary, h: int) -> Array:
	var r := _stair_rect(sr, h); var R := _run_dir(sr.run)
	var free_steps := (h - 3 - 22) / 2   # steps whose headroom under the floor is still 2.2 m
	var cut := free_steps * 3
	if R.x > 0: return [Vector2i(r.position.x + cut, r.position.y), Vector2i(r.size.x - cut, r.size.y)]
	if R.x < 0: return [r.position, Vector2i(r.size.x - cut, r.size.y)]
	if R.y > 0: return [Vector2i(r.position.x, r.position.y + cut), Vector2i(r.size.x, r.size.y - cut)]
	return [r.position, Vector2i(r.size.x, r.size.y - cut)]

static func _stair(vs: Dictionary, ramps: Array, sr: Dictionary, z: int, h: int) -> void:
	var r := _stair_rect(sr, h); var R := _run_dir(sr.run); var L := h / 2 * 3
	var p: Dictionary = pieces()["stair_%d" % h]
	for k in p:   # piece: x across (14), y along the run, z up
		var q: Vector3i = k; var x: int; var y: int
		if R.x > 0: x = r.position.x + q.y; y = r.position.y + q.x
		elif R.x < 0: x = r.end.x - 1 - q.y; y = r.position.y + q.x
		elif R.y > 0: x = r.position.x + q.x; y = r.position.y + q.y
		else: x = r.position.x + q.x; y = r.end.y - 1 - q.y
		vs[Vector3i(x, y, z + q.z)] = p[k]
	# the ramp the feet ride: from the foot of the first riser to the top step's nosing, along the stair's middle
	var mid := Vector2(r.position) + Vector2(r.size) * 0.5
	var a: Vector2; var b: Vector2
	if R.x != 0: a = Vector2(r.position.x if R.x > 0 else r.end.x, mid.y); b = a + Vector2(R) * (L - 3)
	else: a = Vector2(mid.x, r.position.y if R.y > 0 else r.end.y); b = a + Vector2(R) * (L - 3)
	ramps.append([Vector3(a.x, a.y, z), Vector3(b.x, b.y, z + h), 14])
	ramps.append([Vector3(b.x, b.y, z + h), Vector3(b.x + R.x * 3, b.y + R.y * 3, z + h), 14])   # the top tread, flat

# stone steps up the plinth outside a door: 0.2 m, 0.2 m, then the 0.1 m sill
static func _door_steps(vs: Dictionary, ramps: Array, o: Vector3i, d: Vector2i, bay: int) -> void:
	var out := -_left(d)
	var bo := o + Vector3i(d.x, d.y, 0) * (bay * BAY)
	for lx in range(DOOR[0] - 1, DOOR[1] + 2):
		for step in [[1, 4, 3], [4, 7, 1]]:   # [from, to] voxels out from the wall, height - 1
			for ly in range(step[0], step[1]):
				for lz in step[2] + 1:
					var c := _cell(bo, d, lx, -ly, lz)
					vs[c] = Color8(132, 129, 122) if lz == step[2] else Color8(112, 110, 104)
	var a := Vector3(bo) + Vector3(d.x, d.y, 0) * ((DOOR[0] + DOOR[1] + 1) * 0.5)
	ramps.append([a + Vector3(out.x, out.y, 0) * 8, Vector3(a.x, a.y, PLINTH), DOOR[1] - DOOR[0] + 3])

## a box whose top face runs from a to b (Godot metres), w wide, 0.3 m thick under it
static func _ramp(a: Vector3, b: Vector3, w: float) -> CollisionShape3D:
	var fwd := (b - a).normalized(); var side := fwd.cross(Vector3.UP).normalized(); var up := side.cross(fwd).normalized()
	if up.y < 0: up = -up; side = -side
	var cs := CollisionShape3D.new(); var sh := BoxShape3D.new(); const T := 0.3
	sh.size = Vector3(w, T, (b - a).length()); cs.shape = sh
	cs.transform = Transform3D(Basis(side, up, fwd), (a + b) * 0.5 - up * T * 0.5)
	return cs

# ---------------------------------------------------------------- the roof
static func _roof(vs: Dictionary, ramps: Array, W: int, D: int, z: int, mat: String, face := "frame") -> void:
	var slope: Dictionary = pieces()["roof_" + mat]; var ridge: Dictionary = pieces()["ridge_" + mat] if pieces().has("ridge_" + mat) else pieces()["ridge_thatch"]
	var run := D / 2 + OVERHANG; var L := W + 2 * OVERHANG
	for x in L:
		for r in run:
			for t in 3:
				var c: Color = slope.get(Vector3i(x % BAY, r % BAY, r % BAY + t), Color8(156, 122, 68))
				vs[Vector3i(x - OVERHANG, r - OVERHANG, z - OVERHANG + r + t)] = c          # the front slope
				vs[Vector3i(x - OVERHANG, D - 1 + OVERHANG - r, z - OVERHANG + r + t)] = c  # the back slope
		for k in ridge:
			var q: Vector3i = k
			if q.x == x % BAY: vs[Vector3i(x - OVERHANG, D / 2 - 2 + q.y, z - OVERHANG + run - 1 + q.z)] = ridge[k]
	# gables over the side walls, cut from the 12 m gable to this span (its top is min(x, span - 1 - x) at any span)
	var gb: Dictionary = pieces()["gable_%s_120" % face] if pieces().has("gable_%s_120" % face) else pieces()["gable_120"]
	if false and pieces().has("eave_weights") and mat == "heather":   # replaced by the rope bands of _roof_dress   # the stones that hold the ropes down, along both eaves
		for x0 in range(0, L - BAY + 1, BAY):
			_stamp(vs, "eave_weights", Vector3i(x0 - OVERHANG, -OVERHANG, z - OVERHANG - 6), Vector2i(1, 0))
			_stamp(vs, "eave_weights", Vector3i(W + OVERHANG - x0, D + OVERHANG, z - OVERHANG - 6), Vector2i(-1, 0))
	for y in D:
		var sx := y if y < D / 2 else 119 - (D - 1 - y)
		for k in gb:
			var q: Vector3i = k
			if q.x != sx: continue
			vs[Vector3i(q.y, D - 1 - y, z + q.z)] = gb[k]            # left gable, its outer face on x = 0
			vs[Vector3i(W - 1 - q.y, D - 1 - y, z + q.z)] = gb[k]    # right gable
	_roof_dress(vs, W, D, z, mat, _attached)
	# collision: each slope a sheet along its top, from the eave to the ridge
	var top := float(D) / 2.0
	ramps.append([Vector3(W * 0.5, -OVERHANG, z), Vector3(W * 0.5, top, z + top + OVERHANG), L])
	ramps.append([Vector3(W * 0.5, D + OVERHANG, z), Vector3(W * 0.5, top, z + top + OVERHANG), L])

## a dormer over a knee-wall bay: the roof is cleared where it stands (with the eave in front of its window), then the
## dormer, its glazing and its shutters are set in
static func _dormer(rf: Dictionary, bo: Vector3i, d: Vector2i, face: String) -> void:
	var n := _left(d)
	for lx in range(1, BAY):
		for ly in range(-OVERHANG - 1, 14):
			for lz in range(8, 32): rf.erase(_cell(bo, d, lx, ly, lz))
	_stamp(rf, "dormer_12", bo, d)
	_openings.append([rf, bo, d, WIN[0], WIN[1], WIN[2], WIN[3], "window"])
	_stamp(rf, "window_leaded", bo + Vector3i(d.x, d.y, 0) * WIN[0] + Vector3i(n.x, n.y, WIN[2]), d)
	if face == "dry": _stamp(rf, "shutters", bo + Vector3i(d.x, d.y, 0) * (WIN[0] - 4) - Vector3i(n.x, n.y, -WIN[2]), d)

## a window in both gables at depth y (voxels from the front), 1.3 to 2.3 m over the top floor's knee wall
static func _gable_window(rf: Dictionary, W: int, D: int, z: int, y: int, face: String) -> void:
	for side in [[Vector3i(0, y + 4, z + 1), Vector2i(0, -1)], [Vector3i(W, y - 4, z + 1), Vector2i(0, 1)]]:
		var o: Vector3i = side[0]; var d: Vector2i = side[1]
		for lx in range(0, 8):
			for ly in range(0, WALL):
				for lz in range(0, 10): rf.erase(_cell(o, d, lx, ly, lz))
		_stamp(rf, "window_leaded", o + Vector3i(_left(d).x, _left(d).y, 0), d)
		_openings.append([rf, o, d, 0, 7, 0, 9, "gable"])
		for lx in range(-1, 9):
			for ly in range(0, WALL):
				rf[_cell(o, d, lx, ly, 10)] = Color8(52, 44, 38); rf[_cell(o, d, lx, ly, 11)] = Color8(70, 60, 50)   # a timber lintel

# ---------------------------------------------------------------- doors
static func _door(bo: Vector3i, d: Vector2i, swing := 1, leaf := "door_leaf") -> Node3D:
	var n := _left(d)
	var hinge := Vector3(bo) + Vector3(d.x, d.y, 0) * DOOR[0] + Vector3(n.x, n.y, 0) * 1
	var dg := Vector3(d.x, 0, -d.y); var ng := Vector3(n.x, 0, -n.y)
	var door := KitDoor.new(); door.name = "Door"; door.leaf_mesh = _meshes[leaf]; door.swing_sign = swing
	door.transform = Transform3D(Basis(dg, Vector3.UP, -ng), _g(hinge))
	return door

## the detail on a roof (KitDress's part for roofs): thatch and turf get thick and lumpy, with a ragged hanging eave,
## dark rope bands across each slope, rolled verges that sweep up at the gable ends, a heavy ridge bound with sways,
## rafter ends under the eave and ship-rib bargeboards that run up the gables and cross over the ridge; slate gets
## its courses, one lip each, and quieter tones
static func _roof_dress(vs: Dictionary, W: int, D: int, z: int, mat: String, attached := "") -> void:
	var run := D / 2 + OVERHANG; var L := W + 2 * OVERHANG
	var soft := mat in ["heather", "thatch", "turf"]
	var band := Color8(78, 66, 56) if mat != "turf" else Color8(84, 90, 58)
	for side in 2:
		for x in L:
			var wx := x - OVERHANG
			for r in run:
				var y := r - OVERHANG if side == 0 else D - 1 + OVERHANG - r
				var zb := z - OVERHANG + r
				var top: Color = vs.get(Vector3i(wx, y, zb + 2), Color8(128, 112, 92))
				var edge := mini(x, L - 1 - x)   # columns from the verge
				if soft:
					var is_band := mat != "turf" and r % 7 == 3 and r < run - 2
					var lump := false
					if is_band:
						vs[Vector3i(wx, y, zb + 3)] = band; vs[Vector3i(wx, y, zb + 2)] = band.darkened(0.15)
					else:   # combed straws: streaks down the slope, a few shades of the thatch, no lumps
						var sk := KitDress._h(wx, r / 5 + side * 50, _seed + 31)
						vs[Vector3i(wx, y, zb + 2)] = top.darkened(0.08) if sk < 0.25 else (top.lightened(0.05) if sk > 0.8 else top)
					# the verges roll up and over, higher toward the gable end
					if edge < 3:
						for t in range(3, 3 + 3 - edge): vs[Vector3i(wx, y, zb + t + (1 if lump else 0))] = top
					if r == 0:   # the eave: thick, and ragged where the heather hangs
						vs[Vector3i(wx, y, zb - 1)] = top.darkened(0.12)
						var hang := KitDress._h(wx, side, _seed + 9)
						if hang > 0.45: vs[Vector3i(wx, y, zb - 2)] = top.darkened(0.2)
						if hang > 0.8: vs[Vector3i(wx, y, zb - 3)] = top.darkened(0.25)
				elif mat == "slate":
					var sl := KitDress._h(floori((wx + (r / 3) % 2 * 2) / 4.0), r / 3, _seed + 3)
					vs[Vector3i(wx, y, zb + 2)] = Color8(84, 90, 98) if sl < 0.7 else (Color8(72, 78, 86) if sl < 0.88 else Color8(98, 104, 112))
					if r % 3 == 0: vs[Vector3i(wx, y, zb + 3)] = Color8(70, 76, 84)
			# the rafter ends, every metre under the eave
			if wx % 10 == 5 and wx > 0 and wx < W:
				var ye := -OVERHANG - 1 if side == 0 else D + OVERHANG
				for k in 3:
					var yy := ye + (k if side == 0 else -k)
					vs[Vector3i(wx, yy, z - OVERHANG - 2)] = Color8(64, 54, 46); vs[Vector3i(wx, yy, z - OVERHANG - 1)] = Color8(72, 62, 54)
	if soft:   # the ridge: a heavy roll, bound with sways every 0.6 m
		var zr := z - OVERHANG + run - 1
		for x in range(-OVERHANG, W + OVERHANG):
			for y in range(D / 2 - 3, D / 2 + 3):
				var dy := absi(y * 2 + 1 - D)
				var col := band if (x + 600) % 6 == 0 else (Color8(108, 115, 75) if mat != "thatch" else Color8(170, 138, 84))
				for zz in range(zr + 1, zr + 4 - dy / 4): vs[Vector3i(x, y, zz)] = col
	# bargeboards of salvaged ship ribs along both gables, from the eave up past the ridge, where they cross like horns
	for gx in [-OVERHANG - 1, W + OVERHANG]:
		if (attached == "left" and gx < 0) or (attached == "right" and gx > 0): continue
		for side in 2:
			for r in range(0, run + 7):
				var y := r - OVERHANG if side == 0 else D - 1 + OVERHANG - r
				var zb := z - OVERHANG + r
				var curl := maxi(0, r - run - 4)   # the tips lift a little more as they end
				for t in range(-1, 2): vs[Vector3i(gx, y, zb + t + curl)] = Color8(64, 54, 46) if t < 1 else Color8(86, 72, 60)

# ---------------------------------------------------------------- the porch
static func _porch_has(layout: Dictionary, bay: int) -> bool:
	if not layout.has("porch"): return false
	var p: Dictionary = layout.porch
	return bay >= p.from and bay <= p.to

## a raised deck of salvaged boards along the front, from bay "from" to bay "to", "depth" voxels out, at the plinth's
## height: log rails between posts, steps down in front of each door, and a lean-to roof of the house's roof stuff
## over it from the wall at 2.9 m, falling one in two. The front doors under it lose their own steps and hoods.
static func _porch(vs: Dictionary, ramps: Array, boxes: Array, layout: Dictionary, front: String, z: int) -> void:
	var p: Dictionary = layout.porch; var dep: int = p.get("depth", 16)
	var x0: int = p.from * BAY; var x1: int = (p.to + 1) * BAY + (2 if p.to + 1 < front.length() else 0)
	var mat: String = layout.get("roof", "heather")
	var steps := []
	for b in range(p.from, p.to + 1):
		if b < front.length() and front[b] == "d": steps.append([b * BAY + DOOR[0] - 1, b * BAY + DOOR[1] + 1])
	var on_step := func(x: int) -> bool:
		for st in steps:
			if x >= st[0] and x <= st[1]: return true
		return false
	for x in range(x0, x1):
		for y in range(-dep, 0):
			for zz in PLINTH:
				var c: Color
				if zz == PLINTH - 1: c = Color8(150, 134, 112) if (y + 600) % 3 else Color8(124, 110, 92)   # deck boards
				elif y == -dep: c = KitDress._tone(KitDress._h(x / 6, zz / 2, _seed + 70), true)            # a drystone kerb
				else: c = Color8(90, 80, 70)
				vs[Vector3i(x, y, zz)] = c
		# posts at each end and every 2 m, a rail between them at 0.9 m, a lower rail at 0.45 m
		var post := (x - x0) % BAY < 2 or x >= x1 - 2
		if post and not on_step.call(x):
			for zz in range(PLINTH, z + 29 - (dep - 1) / 2):   # up to the lean-to roof over it
				for yy in [-dep, -dep + 1]: vs[Vector3i(x, yy, zz)] = Color8(72, 62, 54)
			boxes.append([Vector3(x, -dep, PLINTH), Vector3(x + 1, -dep + 2, PLINTH + 29)])
		elif not on_step.call(x):
			for zz in [PLINTH + 8, PLINTH + 9, PLINTH + 4]: vs[Vector3i(x, -dep, zz)] = Color8(96, 82, 68) if zz != PLINTH + 9 else Color8(110, 96, 80)
	boxes.append([Vector3(x0, -dep, 0), Vector3(x1, 0, PLINTH)])
	var rx := x0   # the rail, as a fence, in runs between the steps
	while rx < x1:
		var ex := rx
		while ex < x1 and not on_step.call(ex): ex += 1
		if ex > rx: boxes.append([Vector3(rx, -dep, PLINTH), Vector3(ex, -dep + 1, PLINTH + 10)])
		rx = ex + 1
	# the steps: two treads of boards on stone, down to the ground
	for st in steps:
		for x in range(st[0], st[1] + 1):
			for k in [[1, 3, 2], [4, 6, 0]]:
				for yy in range(-dep - k[1], -dep - k[0] + 1):
					for zz in k[2] + 1: vs[Vector3i(x, yy, zz)] = Color8(150, 134, 112) if zz == k[2] else Color8(110, 108, 102)
		var mx: float = (st[0] + st[1] + 1) * 0.5
		ramps.append([Vector3(mx, -dep - 8, 0), Vector3(mx, -dep + 1, PLINTH + 0.5), int(st[1]) - int(st[0]) + 1])
	# the lean-to roof, its edges ragged where it is heather or turf
	var top := z + 29
	for k in range(0, dep + 4):
		var zr := top - k / 2
		for x in range(x0 - 2, x1 + 2):
			var y := -1 - k
			for t in 2:
				var c: Color
				if mat == "slate": c = Color8(84, 90, 98) if t == 1 else Color8(66, 72, 80)
				elif mat == "turf": c = Color8(108, 115, 75) if KitDress._h(x / 2, k / 2, _seed) > 0.25 else Color8(88, 92, 62)
				else: c = Color8(150, 138, 114) if (k % 7) != 3 else Color8(78, 66, 56)
				if t == 0: c = Color8(72, 62, 54)
				vs[Vector3i(x, y, zr + t)] = c
			if false: vs[Vector3i(x, y, zr + 2)] = Color8(150, 138, 114) if mat != "turf" else Color8(118, 125, 82)
			if k == dep + 3 and mat != "slate" and KitDress._h(x, 3, _seed) > 0.5: vs[Vector3i(x, y, zr - 1)] = Color8(126, 114, 94)

# ---------------------------------------------------------------- hall pieces
## a carved post, 0.4 m square, from the floor up h voxels: a ship's mast cut down, tarred, with carved rings and a
## knot band every 0.6 m and a bracket head that spreads under the beam it holds
static func _carved_post(vs: Dictionary, boxes: Array, at: Vector2i, z: int, h: int) -> void:
	for zz in h:
		var ring := zz % 6 == 0; var band := zz % 12 == 6
		for x in range(-2, 2):
			for y in range(-2, 2):
				var corner := (x == -2 or x == 1) and (y == -2 or y == 1)
				if corner and not ring and zz < h - 3: continue   # rounded off between the rings
				var c := Color8(92, 78, 66)
				if ring: c = Color8(70, 60, 52)
				elif band and (x + y + zz) % 2 == 0: c = Color8(118, 100, 80)
				elif KitDress._h(x, y, zz / 3) > 0.8: c = Color8(80, 68, 58)
				vs[Vector3i(at.x + x, at.y + y, z + zz)] = c
	for k in 3:   # the bracket head
		for x in range(-3 - k, 3 + k):
			for y in range(-2, 2): vs[Vector3i(at.x + x, at.y + y, z + h - 3 + k)] = Color8(72, 62, 54)
	boxes.append([Vector3(at.x - 2, at.y - 2, z), Vector3(at.x + 2, at.y + 2, z + h)])

## a round fire pit in the middle of a hall: a ring of dressed stones 0.4 m high round a bed of embers and burning logs
static func _firepit(vs: Dictionary, boxes: Array, at: Vector2i, r: int, z: int) -> void:
	for x in range(-r - 1, r + 2):
		for y in range(-r - 1, r + 2):
			var d := sqrt(float(x * x + y * y))
			if d > r + 0.5: continue
			var p := Vector2i(at.x + x, at.y + y)
			if d > r - 2.0:
				for zz in 4: vs[Vector3i(p.x, p.y, z + zz)] = KitDress._tone(KitDress._h(int(atan2(y, x) * 3.0), zz / 2, 5), false) if zz < 3 else KitDress.DRESSED
			else:
				var e := KitDress._h(x, y, 9)
				vs[Vector3i(p.x, p.y, z)] = Color8(40, 34, 30)
				vs[Vector3i(p.x, p.y, z + 1)] = Color8(255, 140, 60) if e > 0.6 else (Color8(200, 80, 40) if e > 0.3 else Color8(56, 46, 40))
	for k in range(-r + 3, r - 2):   # two logs crossed over the embers
		vs[Vector3i(at.x + k, at.y, z + 2)] = Color8(88, 70, 54); vs[Vector3i(at.x, at.y + k, z + 3)] = Color8(76, 60, 48)
	boxes.append([Vector3(at.x - r, at.y - r, z), Vector3(at.x + r, at.y + r, z + 4)])

# ---------------------------------------------------------------- baking
## a layout's stamp: the builder's version and the layout itself, so a bake is used only for exactly what it was made from
static func stamp(layout: Dictionary) -> String: return "%d:%d" % [BAKE_VERSION, str(layout).hash()]

## the building for a layout from its bake at path if the bake is current, otherwise built now (and baked there if
## bake is true). A bake is the finished node tree saved as a scene: loading it skips all the stamping and meshing.
## Bake with a real renderer (not --headless): meshes keep their data only where a rendering server holds it.
static func load_or_build(layout: Dictionary, path: String, bake := false) -> Node3D:
	var st := stamp(layout)
	if not bake and ResourceLoader.exists(path):
		var ps := load(path) as PackedScene
		if ps:
			var n := ps.instantiate() as Node3D
			if n and n.get_meta("stamp", "") == st:
				n.set_meta("baked", true); return n
			if n: n.free()
	var b := build(layout); b.set_meta("stamp", st)
	if bake: save_bake(b, path)
	return b

## saves a freshly built building (before it enters the tree, so the doors' own runtime children are not in it)
static func save_bake(b: Node3D, path: String) -> void:
	var own := func(f: Callable, n: Node) -> void:
		for c in n.get_children():
			c.owner = b; f.call(f, c)
	own.call(own, b)
	var ps := PackedScene.new(); ps.pack(b)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(path.get_base_dir()))
	var err := ResourceSaver.save(ps, path, ResourceSaver.FLAG_COMPRESS)
	print("BAKE %s: %s" % [path, "ok" if err == OK else "error %d" % err])
