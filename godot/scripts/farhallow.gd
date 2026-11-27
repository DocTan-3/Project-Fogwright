## Farhallow at peace: a fishing and farming village on the far coast, the first scene of the game (the prologue's calm
## before the Fog). A cobbled square with houses around it, fishers' cottages and a pier on the shore, a wheat field behind,
## trees and pines around, a late-afternoon sun low over the sea. Colours are a little faded: Farhallow lies far from Aldrath.
extends VillageKit

const PROPS := "res://assets/props/quaternius/%s.gltf"
const NATURE := "res://assets/nature/quaternius/%s.gltf"
const SHORE := 14.0      # where the grass gives way to the beach (z, metres; the sea lies south, +z)
const SEA_Y := -0.45

var rng := RandomNumberGenerator.new()

func _enter_tree() -> void:
	Palette.current = "hearth"
	Palette.fog = 0.2          # far from Aldrath: the colours are already a little faded

func _ready() -> void:
	rng.seed = 1207
	_ground()
	_square()
	_houses()
	_pier()
	_field()
	_greenery()
	_props()
	call_deferred("_light")   # after the main scene has set its defaults

func _light() -> void:
	var sun: DirectionalLight3D = get_parent().get_node_or_null("Sun")
	if sun:   # late afternoon: low in the west-south-west, warm
		sun.rotation_degrees = Vector3(-17, -62, 0)
		sun.light_color = Color(1.0, 0.8, 0.58)
		sun.light_energy = 1.05
	var env: Environment = get_parent().get_node("WorldEnvironment").environment
	env.tonemap_exposure = 0.88
	env.ambient_light_energy = 0.45
	var sky: ProceduralSkyMaterial = env.sky.sky_material   # a warm, hazy late-afternoon sky
	sky.sky_top_color = Color(0.42, 0.56, 0.74); sky.sky_horizon_color = Color(0.93, 0.78, 0.6)
	sky.ground_horizon_color = Color(0.93, 0.78, 0.6); sky.sun_angle_max = 30.0

# ---------------------------------------------------------------- ground, beach and sea
func _plane(size: Vector2, pos: Vector3, col: Color, rough := 1.0, tilt := 0.0, alpha := 1.0) -> MeshInstance3D:
	var m := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = size; m.mesh = pm
	var mat := StandardMaterial3D.new(); mat.albedo_color = Color(col.r, col.g, col.b, alpha); mat.roughness = rough
	if alpha < 1.0:
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA; mat.metallic = 0.15; mat.metallic_specular = 0.8
	m.material_override = mat; m.position = pos; m.rotation.x = tilt; add_child(m)
	return m

func _ground() -> void:
	_plane(Vector2(240, 140), Vector3(0, 0, SHORE - 70), Palette.col("grass"))                    # the land
	var beach_len := 12.0; var drop := 1.6
	var b := _plane(Vector2(240, beach_len), Vector3(0, -drop * 0.5, SHORE + beach_len * 0.5), Palette.col("sand"), 1.0, -atan2(drop, beach_len))
	b.scale.z = sqrt(beach_len * beach_len + drop * drop) / beach_len
	_plane(Vector2(400, 300), Vector3(0, SEA_Y, SHORE + 150), Palette.col("sea"), 0.06, 0.0, 0.86)  # the sea
	_plane(Vector2(400, 300), Vector3(0, SEA_Y - 2.5, SHORE + 150), Palette.col("sand").darkened(0.45))  # its floor, seen through the shallows
	var body := StaticBody3D.new(); add_child(body)   # colliders: the land, and the beach's slope
	var c1 := CollisionShape3D.new(); var s1 := BoxShape3D.new(); s1.size = Vector3(240, 1, 140); c1.shape = s1
	c1.position = Vector3(0, -0.5, SHORE - 70); body.add_child(c1)
	var c2 := CollisionShape3D.new(); var s2 := BoxShape3D.new(); s2.size = Vector3(240, 1, beach_len * 1.02); c2.shape = s2
	c2.position = Vector3(0, -drop * 0.5 - 0.5, SHORE + beach_len * 0.5); c2.rotation.x = -atan2(drop, beach_len); body.add_child(c2)

# ---------------------------------------------------------------- the village
func _square() -> void:
	for x in range(-6, 6, 2):
		for z in range(-6, 8, 2):
			if abs(x + 1) + abs(z + 1) > 11: continue         # a rough, rounded edge
			_piece("Floor_UnevenBrick", Vector3(x + 1, 0.01, z + 1), 0.0)
	for z in range(8, 16, 2):                               # a lane down to the shore
		_piece("Floor_UnevenBrick", Vector3(3, 0.01, z + 1), 0.0)
		_piece("Floor_UnevenBrick", Vector3(5, 0.01, z + 1), 0.0)

func _houses() -> void:
	# around the square
	place_house({"bays": 3, "deep": 3, "storeys": 2, "walls": ["UnevenBrick", "Plaster"], "door": [1]}, Vector3(0, 0, -9), Vector3(0, 0, 1))
	place_house({"bays": 3, "deep": 3, "storeys": 1, "walls": ["Plaster"], "door": [1]}, Vector3(-10, 0, -1), Vector3(1, 0, 0))
	place_house({"bays": 2, "deep": 3, "storeys": 2, "walls": ["UnevenBrick", "Plaster"], "door": [0]}, Vector3(10, 0, -2), Vector3(-1, 0, 0))
	# fishers' cottages by the shore, facing the sea
	place_house({"bays": 2, "deep": 2, "storeys": 1, "walls": ["UnevenBrick"], "door": [0]}, Vector3(-12, 0, 8), Vector3(0, 0, 1))
	place_house({"bays": 2, "deep": 2, "storeys": 1, "walls": ["Plaster"], "door": [1]}, Vector3(14, 0, 7), Vector3(0, 0, 1))

func _pier() -> void:
	var y := 0.25
	for z in range(int(SHORE) + 2, int(SHORE) + 26, 2):
		_piece("Floor_WoodDark", Vector3(4, y, z + 1), 0.0)
		if z > int(SHORE) + 6:     # posts down into the water every few metres
			for x in [3.1, 4.9]:
				var post := put(PROPS % "Barrel_Holder", Vector3(x, y - 1.4, z + 1), 0.0, 1.0, false) if false else null
				_post(Vector3(x, y, z + 1))
	var deck := StaticBody3D.new(); add_child(deck)
	var c := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(2, 0.4, 24); c.shape = bs
	c.position = Vector3(4, y - 0.2, SHORE + 14); deck.add_child(c)

func _post(top: Vector3) -> void:
	var m := MeshInstance3D.new(); var cm := CylinderMesh.new(); cm.top_radius = 0.11; cm.bottom_radius = 0.13; cm.height = 2.4
	m.mesh = cm; var mat := StandardMaterial3D.new(); mat.albedo_color = Palette.col("WoodTrim").darkened(0.2); mat.roughness = 0.9
	m.material_override = mat; m.position = top - Vector3(0, 1.2, 0); add_child(m)

# ---------------------------------------------------------------- the field and the greenery (batched: one draw per kind)
func scatter(path: String, points: Array, yaw_jitter := TAU, scale_range := Vector2(0.9, 1.1)) -> void:
	var s: PackedScene = load(path)
	if s == null: return
	var proto: Node3D = s.instantiate()
	for mi in proto.find_children("*", "MeshInstance3D", true, false):
		var src := mi as MeshInstance3D
		var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = src.mesh
		mm.instance_count = points.size()
		var local := (proto.global_transform.affine_inverse() * src.global_transform) if src.is_inside_tree() else src.transform
		for i in points.size():
			var t := Transform3D(Basis(Vector3.UP, rng.randf() * yaw_jitter).scaled(Vector3.ONE * rng.randf_range(scale_range.x, scale_range.y)), points[i])
			mm.set_instance_transform(i, t * local)
		var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm; add_child(mmi)
	proto.free()

func _field() -> void:
	var pts := []
	for x in range(-22, 23):
		for z in range(-34, -16):
			pts.append(Vector3(x * 0.9 + rng.randf_range(-0.2, 0.2), 0, z * 0.75 + rng.randf_range(-0.15, 0.15)))
	scatter(NATURE % "Grass_Wispy_Tall", pts, TAU, Vector2(1.1, 1.5))
	for x in range(-21, 22, 2):                              # the fence along the field's front
		put(VILLAGE_FENCE, Vector3(x, 0, -15.2), 0.0)

const VILLAGE_FENCE := "res://assets/village/quaternius/Prop_WoodenFence_Single.gltf"

func _greenery() -> void:
	var trees := []
	for i in 34:   # a loose ring of trees round the village, thicker toward the hills (north)
		var a := rng.randf_range(-PI * 0.95, PI * 0.05); var r := rng.randf_range(26, 48)
		trees.append(Vector3(cos(a) * r, 0, sin(a) * r * 0.8 - 6))
	for i in trees.size():
		put(NATURE % ("CommonTree_%d" % (i % 5 + 1)), trees[i], rng.randf() * TAU, rng.randf_range(0.9, 1.25))
	for i in 22:
		var a := rng.randf_range(-PI, 0); var r := rng.randf_range(52, 80)
		put(NATURE % ("Pine_%d" % (i % 5 + 1)), Vector3(cos(a) * r, 0, sin(a) * r * 0.7 - 10), rng.randf() * TAU, rng.randf_range(1.0, 1.4))
	var grass := []
	var flowers := []
	for i in 900:
		var p := Vector3(rng.randf_range(-40, 40), 0, rng.randf_range(-45, SHORE - 0.5))
		if abs(p.x) < 13 and p.z > -12 and p.z < SHORE: continue        # not on the square or among the houses
		if p.z < -15.5 and p.z > -35 and abs(p.x) < 21: continue       # not in the field
		(flowers if i % 7 == 0 else grass).append(p)
	scatter(NATURE % "Grass_Common_Short", grass)
	scatter(NATURE % "Flower_3_Group", flowers)
	for p in [Vector3(-7, 0, -8), Vector3(7.5, 0, -9), Vector3(-15, 0, 4), Vector3(17, 0, 2), Vector3(-3, 0, 10)]:
		put(NATURE % "Bush_Common_Flowers", p, rng.randf() * TAU, 1.0, false)
	for p in [Vector3(-8, -0.8, 21), Vector3(12, -1.0, 23), Vector3(-20, -0.6, 19), Vector3(20, -1.1, 24)]:
		put(NATURE % ("Rock_Medium_%d" % (rng.randi() % 3 + 1)), p, rng.randf() * TAU, rng.randf_range(1.0, 1.8))

# ---------------------------------------------------------------- life in the square, and on the shore
func _props() -> void:
	put(PROPS % "Stall_Cart_Empty", Vector3(3.5, 0, 1.5), -0.4)
	put("res://assets/village/quaternius/Prop_Wagon.gltf", Vector3(-5.5, 0, -2.5), 0.8)
	for p in [Vector3(-3.6, 0, 3.2), Vector3(-3.0, 0, 3.9), Vector3(-4.2, 0, 4.1)]:
		put(PROPS % "Barrel", p, rng.randf() * TAU)
	put(PROPS % "Barrel_Apples", Vector3(4.6, 0, -1.0), 0.3)
	put(PROPS % "FarmCrate_Apple", Vector3(2.4, 0, 2.6), 0.2)
	put(PROPS % "FarmCrate_Carrot", Vector3(2.0, 0, 3.4), -0.3)
	put(PROPS % "Crate_Wooden", Vector3(-6.4, 0, 0.6), 0.5)
	put(PROPS % "Bench", Vector3(0.5, 0, 5.0), PI)
	put(PROPS % "Bucket_Wooden_1", Vector3(-1.5, 0, -6.6), 0.0)
	put(PROPS % "Workbench", Vector3(-12.5, 0, 10.5), PI, 1.0)
	for p in [Vector3(4.4, 0.25, 24.0), Vector3(3.6, 0.25, 31.5)]:
		put(PROPS % "Barrel", p, rng.randf() * TAU)
	put(PROPS % "Rope_2", Vector3(3.5, 0.25, 27), 0.0, 1.0, false)
	put(PROPS % "Crate_Wooden", Vector3(4.5, 0.25, 34.2), 0.2)
