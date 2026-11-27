## A short test street from the Medieval Village MegaKit (2 m grid): cobbles down the middle, two-storey houses on both
## sides with doors and windows, gabled tiled roofs, and a house closing each end so the street feels enclosed.
## Built when the scene starts, from a plain list of houses, so the layout is easy to change.
extends Node3D

const KIT := "res://assets/village/quaternius/%s.gltf"
const STREET_HALF := 4.0      # the street is 8 m between house fronts
const STOREY := 3.12

# each house: where its front starts along the street (m), its width in 2 m bays, its depth in bays, its storeys,
# the wall kind for each storey, and which bays on the ground floor are doors
const NORTH := [
	{"x": -16, "bays": 2, "deep": 3, "storeys": 2, "walls": ["UnevenBrick", "Plaster"], "door": [0]},
	{"x": -12, "bays": 3, "deep": 3, "storeys": 2, "walls": ["Plaster", "Plaster"], "door": [1]},
	{"x": -6, "bays": 2, "deep": 3, "storeys": 3, "walls": ["UnevenBrick", "Plaster", "Plaster"], "door": [1]},
	{"x": -2, "bays": 3, "deep": 3, "storeys": 2, "walls": ["UnevenBrick", "UnevenBrick"], "door": [0]},
	{"x": 4, "bays": 2, "deep": 3, "storeys": 2, "walls": ["Plaster", "Plaster"], "door": [0]},
	{"x": 8, "bays": 4, "deep": 3, "storeys": 2, "walls": ["UnevenBrick", "Plaster"], "door": [1, 2]},
]
const SOUTH := [
	{"x": -16, "bays": 3, "deep": 3, "storeys": 2, "walls": ["Plaster", "Plaster"], "door": [1]},
	{"x": -10, "bays": 2, "deep": 3, "storeys": 2, "walls": ["UnevenBrick", "Plaster"], "door": [0]},
	{"x": -6, "bays": 4, "deep": 3, "storeys": 3, "walls": ["UnevenBrick", "Plaster", "Plaster"], "door": [1]},
	{"x": 2, "bays": 2, "deep": 3, "storeys": 2, "walls": ["Plaster", "Plaster"], "door": [1]},
	{"x": 6, "bays": 3, "deep": 3, "storeys": 2, "walls": ["UnevenBrick", "UnevenBrick"], "door": [1]},
	{"x": 12, "bays": 2, "deep": 3, "storeys": 2, "walls": ["Plaster", "Plaster"], "door": [0]},
]

var _cache := {}

func _ready() -> void:
	for x in range(-18, 18, 2):            # the street's cobbles
		for z in range(-4, 6, 2):
			_piece("Floor_UnevenBrick", Vector3(x + 1, 0, z - 1 + 1), 0.0)
	for h in NORTH:
		_house(h, -1)
	for h in SOUTH:
		_house(h, 1)
	# the street's ends: a house across each end closes it, so it reads as a street, not a stage set
	_house({"x": -22, "bays": 3, "deep": 4, "storeys": 2, "walls": ["UnevenBrick", "Plaster"], "door": [1]}, -1, -PI / 2, Vector3(-18, 0, 2))
	_house({"x": 18, "bays": 3, "deep": 4, "storeys": 3, "walls": ["UnevenBrick", "Plaster", "Plaster"], "door": [1]}, -1, PI / 2, Vector3(18, 0, -4))
	# beyond the cobbles: packed earth (one plane, so it costs nothing)
	var earth := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(160, 160); earth.mesh = pm
	var mat := StandardMaterial3D.new(); mat.albedo_color = Palette.col("earth"); mat.roughness = 1.0; earth.material_override = mat
	earth.position.y = -0.02; add_child(earth)
	var ground := StaticBody3D.new()    # one flat collider under the whole street
	var col := CollisionShape3D.new(); var box := BoxShape3D.new(); box.size = Vector3(80, 1, 80)
	col.shape = box; col.position = Vector3(0, -0.5, 0); ground.add_child(col); add_child(ground)

func _scene(name: String) -> PackedScene:
	if not _cache.has(name):
		_cache[name] = load(KIT % name)
	return _cache[name]

var _into: Node3D = null
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
			_piece("Wall_%s_Straight" % kind, Vector3(cx, y, back_z), yaw + PI)   # the back
		for b in h.deep:                                               # the sides
			var cz: float = front_z + side * (b * 2 + 1)
			_piece("Wall_%s_Straight" % kind, Vector3(float(h.x), y, cz), -PI / 2)
			_piece("Wall_%s_Straight" % kind, Vector3(float(h.x) + w, y, cz), PI / 2)
		if s > 0:                                                      # a floor between storeys, seen through windows
			for b in h.bays:
				for c in h.deep:
					_piece("Floor_WoodDark", Vector3(float(h.x) + b * 2 + 1, y, front_z + side * (c * 2 + 1)), 0.0)
	# the roof: a gable along the street, tiled, with brick gable ends
	var top: float = h.storeys * STOREY
	var cx: float = float(h.x) + w * 0.5
	var cz: float = front_z + side * d * 0.5
	var roof := "Roof_RoundTiles_%dx%d" % [d, w] if d <= 8 else "Roof_RoundTiles_6x8"
	var r := _piece(roof, Vector3(cx, top, cz), PI / 2)
	if r == null:
		_piece("Roof_RoundTiles_6x8", Vector3(cx, top, cz), PI / 2)
	_into = null
