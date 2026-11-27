## A short test street from the Medieval Village MegaKit (2 m grid): cobbles down the middle, two-storey houses on both
## sides with doors and windows, gabled tiled roofs, and a house closing each end so the street feels enclosed.
## Built when the scene starts, from a plain list of houses, so the layout is easy to change.
extends VillageKit

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

func _ready() -> void:
	for x in range(-18, 18, 2):            # the street's cobbles
		for z in range(-4, 6, 2):
			_piece("Floor_UnevenBrick", Vector3(x + 1, 0, z - 1 + 1), 0.0)
	for h in NORTH:
		_house(h, -1)
	for h in SOUTH:
		_house(h, 1)
	# the street's ends: a house across each end closes it, so it reads as a street, not a stage set
	# (built facing +z in their own frame, then turned so the front faces back up the street, and moved so the front stands
	# at the street's end: the west house's front at x = -18, the east house's at x = 18)
	_house({"x": 0, "bays": 4, "deep": 4, "storeys": 2, "walls": ["UnevenBrick", "Plaster"], "door": [1]}, -1, PI / 2, Vector3(-14, 0, 0))
	_house({"x": 0, "bays": 4, "deep": 4, "storeys": 3, "walls": ["UnevenBrick", "Plaster", "Plaster"], "door": [2]}, -1, -PI / 2, Vector3(14, 0, 0))
	# beyond the cobbles: packed earth (one plane, so it costs nothing)
	var earth := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(160, 160); earth.mesh = pm
	var mat := StandardMaterial3D.new(); mat.albedo_color = Palette.col("earth"); mat.roughness = 1.0; earth.material_override = mat
	earth.position.y = -0.02; add_child(earth)
	var ground := StaticBody3D.new()    # one flat collider under the whole street
	var col := CollisionShape3D.new(); var box := BoxShape3D.new(); box.size = Vector3(80, 1, 80)
	col.shape = box; col.position = Vector3(0, -0.5, 0); ground.add_child(col); add_child(ground)

