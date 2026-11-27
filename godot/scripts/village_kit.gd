## Building villages from the Medieval Village MegaKit (2 m grid): pieces (with colliders made from their meshes, and the
## palette's materials), and whole houses from a short description. Layouts (a street, Farhallow) extend this.
class_name VillageKit
extends Node3D

const KIT := "res://assets/village/quaternius/%s.gltf"
const STREET_HALF := 4.0
const STOREY := 3.12

## a house with its front door's wall centred on `front`, facing `facing` (it extends behind, away from that direction).
## h: {"bays": width in 2 m bays, "deep": depth in bays, "storeys", "walls": [kind per storey], "door": [bay indices]}
func place_house(h: Dictionary, front: Vector3, facing: Vector3) -> void:
	var f := facing.normalized()
	var turn := atan2(f.x, f.z)
	var hh := h.duplicate(); hh.x = 0
	_house(hh, -1, turn if turn != 0.0 else 0.0001, front + f * STREET_HALF)

## any kit (village, props, nature): one model at a place, turned, optionally scaled, solid or not
func put(path: String, pos: Vector3, yaw := 0.0, scale_by := 1.0, solid := true, role := "clutter", purpose := "") -> Node3D:
	placed.append([path.get_file().get_basename(), pos, 0.5 * scale_by, role, purpose])
	var s: PackedScene = _cache.get(path)
	if s == null:
		s = load(path); _cache[path] = s
	if s == null:
		push_warning("missing " + path); return null
	var n: Node3D = s.instantiate()
	n.position = pos; n.rotation.y = yaw; n.scale = Vector3.ONE * scale_by
	(_into if _into else self).add_child(n)
	Palette.apply(n)
	if solid:
		for m in n.find_children("*", "MeshInstance3D", true, false):
			(m as MeshInstance3D).create_trimesh_collision()
	return n

var _cache := {}

func _scene(name: String) -> PackedScene:
	if not _cache.has(name):
		_cache[name] = load(KIT % name)
	return _cache[name]

var _into: Node3D = null
var last_roof := ""      # the roof the last house got (empty: none fitted)

## everything placed, for checking (tools: the city-planning skill): [model, world position, radius, role, purpose]
## role: "flora" (must stand on open ground), "clutter" (must not block paths or doors), "fixture" (placed by design)
var placed := []
func _piece(name: String, pos: Vector3, yaw: float) -> Node3D:
	var s := _scene(name)
	if s == null:
		push_warning("missing piece " + name)
		return null
	var n: Node3D = s.instantiate()
	n.position = pos; n.rotation.y = yaw
	(_into if _into else self).add_child(n)
	Palette.apply(n)
	if not name.begins_with("Floor_"):   # walls, roofs and doors block; the kit has no colliders, so make them from the meshes
		for m in n.find_children("*", "MeshInstance3D", true, false):
			(m as MeshInstance3D).create_trimesh_collision()
	return n

## side -1: the house is north of the street (its front faces south, +z); side 1: south of it, facing north
func _house(h: Dictionary, side: int, turn: float = 0.0, at: Vector3 = Vector3.ZERO) -> void:
	var root := self as Node3D
	if turn != 0.0 or at != Vector3.ZERO:   # build it in its own frame, then turn and place that frame
		root = Node3D.new(); add_child(root); root.rotation.y = turn; root.position = at
		var hh := h.duplicate(); hh.x = -h.bays; _house_into(root, hh, side); return
	_house_into(self, h, side)

func _house_into(root: Node3D, h: Dictionary, side: int) -> void:
	_into = root
	var front_z := -STREET_HALF if side < 0 else STREET_HALF
	var yaw := 0.0 if side < 0 else PI     # walls' outer face is +z in the kit
	var w: int = h.bays * 2
	var d: int = h.deep * 2
	var back_z := front_z + side * d
	for s in h.storeys:
		var y: float = s * STOREY
		var kind: String = h.walls[s]
		for b in h.bays:
			var cx: float = float(h.x) + b * 2 + 1
			var wide: bool = (b + s) % 2 == 0
			var name := "Wall_%s_Window_Wide_Round" % kind if wide else "Wall_%s_Window_Thin_Round" % kind
			var fill := "Window_Wide_Round1" if wide else "Window_Thin_Round1"
			if s == 0 and b in h.door:
				name = "Wall_%s_Door_Round" % kind; fill = "Door_1_Round"
			_piece(name, Vector3(cx, y, front_z), yaw)                  # the front
			# what fills the opening: a shuttered window, or a door (its hinge is at its left edge, 0.53 m off centre)
			var off := Vector3(-0.53, 0, 0).rotated(Vector3.UP, yaw) if fill.begins_with("Door") else Vector3.ZERO
			_piece(fill, Vector3(cx, y, front_z) + off, yaw)
			_piece(_plain(kind), Vector3(cx, y, back_z), yaw + PI)   # the back
		for b in h.deep:                                               # the sides
			var cz: float = front_z + side * (b * 2 + 1)
			_piece(_plain(kind), Vector3(float(h.x), y, cz), -PI / 2)
			_piece(_plain(kind), Vector3(float(h.x) + w, y, cz), PI / 2)
		# corners: a stone quoin on stone storeys, a timber post on plaster ones, covering where the walls meet
		var corner := "Corner_Exterior_Brick" if kind == "UnevenBrick" else "Corner_Exterior_Wood"
		for cxz in [[float(h.x), front_z, -1.0, -side], [float(h.x) + w, front_z, 1.0, -side], [float(h.x), back_z, -1.0, side], [float(h.x) + w, back_z, 1.0, side]]:
			_piece(corner, Vector3(cxz[0], y, cxz[1]), _corner_yaw(cxz[2], cxz[3]))
		if s > 0:                                                      # a floor between storeys, seen through windows
			for b in h.bays:
				for c in h.deep:
					_piece("Floor_WoodDark", Vector3(float(h.x) + b * 2 + 1, y, front_z + side * (c * 2 + 1)), 0.0)
	# the roof: a gable along the street, tiled, with brick gable ends
	var top: float = h.storeys * STOREY
	var cx: float = float(h.x) + w * 0.5
	var cz: float = front_z + side * d * 0.5
	# the roof: the kit's tiled roofs come in fixed sizes (span x length); try the ridge along the width, then along the
	# depth; the gable ends (plaster and timber triangles) close the roof at both ends of its ridge
	last_roof = ""
	if ResourceLoader.exists(KIT % ("Roof_RoundTiles_%dx%d" % [d, w])):
		last_roof = "Roof_RoundTiles_%dx%d" % [d, w]
		_piece(last_roof, Vector3(cx, top, cz), PI / 2)
		var gable := "Roof_Front_Brick%d" % clampi(d, 2, 8)
		_piece(gable, Vector3(float(h.x), top, cz), -PI / 2)
		_piece(gable, Vector3(float(h.x) + w, top, cz), PI / 2)
	elif ResourceLoader.exists(KIT % ("Roof_RoundTiles_%dx%d" % [w, d])):
		last_roof = "Roof_RoundTiles_%dx%d" % [w, d]
		_piece(last_roof, Vector3(cx, top, cz), 0.0)
		var gable := "Roof_Front_Brick%d" % clampi(w, 2, 8)
		_piece(gable, Vector3(cx, top, front_z), 0.0 if side < 0 else PI)
		_piece(gable, Vector3(cx, top, back_z), PI if side < 0 else 0.0)
	else:
		push_warning("no roof fits a %d x %d house" % [w, d])
	_into = null

## the plain wall of a kind, matching its window and door pieces (the plaster ones stand on a stone base)
func _plain(kind: String) -> String:
	return "Wall_Plaster_Straight_Base" if kind == "Plaster" else "Wall_%s_Straight" % kind

## the corner pieces point out toward (-x, +z); turn one to point toward (sx, sz)
func _corner_yaw(sx: float, sz: float) -> float:
	for t in [0.0, PI / 2, PI, -PI / 2]:
		var x := -cos(t) + sin(t); var z := sin(t) + cos(t)   # (-1, 1) turned by t
		if signf(x) == signf(sx) and signf(z) == signf(sz): return t
	return 0.0
