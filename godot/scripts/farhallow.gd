## Farhallow at peace, built from its plan (tools/map/farhallow_plan.py; plan metres: x east, y south, 140 x 110 m). The
## ground is real terrain: low by the harbour, a beach shelving into the sea, rising toward the north-east where the smithy
## and the shrine stand. Buildings stand at any angle, each on its own level terrace cut into the slope with a stone
## foundation where the ground falls away; paths are smooth curves laid on the ground, not tiles.
extends VillageKit

const PROPS := "res://assets/props/quaternius/%s.gltf"
const NATURE := "res://assets/nature/quaternius/%s.gltf"
const VILLAGE := "res://assets/village/quaternius/%s.gltf"
const ORIGIN := Vector2(70, 55)        # plan metres at the world's origin
const MARGIN := 45.0                   # terrain beyond the plan on every side

# the coastline (plan metres), land to the north-west of it; extended past the plan's edges
const COAST := [Vector2(48, 200), Vector2(55, 110), Vector2(62, 96), Vector2(74, 88), Vector2(86, 84), Vector2(96, 76),
	Vector2(104, 64), Vector2(112, 58), Vector2(124, 56), Vector2(140, 52), Vector2(220, 40)]
# paths: (points, width)
const PATHS := [
	[[Vector2(62, -20), Vector2(62, 0), Vector2(61, 8), Vector2(60, 16), Vector2(58, 26), Vector2(60, 40), Vector2(64, 50)], 4.0],
	[[Vector2(64, 50), Vector2(72, 58), Vector2(80, 66), Vector2(84, 74), Vector2(87, 81)], 3.4],
	[[Vector2(64, 50), Vector2(52, 54), Vector2(40, 58), Vector2(30, 64), Vector2(24, 70)], 2.8],
	[[Vector2(60, 30), Vector2(48, 30), Vector2(42, 26)], 2.2],
	[[Vector2(64, 50), Vector2(78, 44), Vector2(92, 38), Vector2(100, 30), Vector2(103, 23)], 2.6],
	[[Vector2(80, 66), Vector2(70, 72), Vector2(62, 80)], 2.0],
]
# buildings: centre (plan m), width, depth, plan angle (rad), storeys, kind
const BUILDINGS := [
	[Vector2(30, 62), 14, 10, -0.12, 2, "tavern"], [Vector2(46, 70), 6, 6, 0.25, 1, "house"], [Vector2(36, 78), 6, 6, -0.3, 1, "house"],
	[Vector2(72, 63), 6, 4, 0.5, 2, "house"], [Vector2(74, 72), 6, 4, -0.4, 1, "store"], [Vector2(92, 64), 8, 6, 0.35, 2, "house"],
	[Vector2(52, 40), 6, 6, -0.15, 2, "house"], [Vector2(70, 36), 6, 6, 0.2, 1, "house"], [Vector2(96, 34), 8, 6, 0.15, 1, "smithy"],
	[Vector2(104, 22), 4, 4, -0.1, 1, "shrine"], [Vector2(44, 12), 6, 4, 0.05, 1, "granary"], [Vector2(30, 48), 4, 4, 0.3, 1, "shed"],
	[Vector2(56, 46), 4, 4, 0.1, 2, "house"], [Vector2(70, 45), 4, 6, -0.25, 1, "house"], [Vector2(56, 57), 4, 4, 0.6, 1, "house"],
	[Vector2(78, 52), 4, 4, 0.4, 2, "house"], [Vector2(84, 58), 4, 4, 0.5, 1, "house"], [Vector2(62, 68), 4, 4, -0.5, 1, "house"],
	[Vector2(66, 26), 4, 4, 0.1, 2, "house"], [Vector2(52, 24), 4, 6, -0.2, 1, "house"],
]
const WELL := Vector2(64, 50)
const PIER := [Vector2(87, 81), Vector2(87.5, 90), Vector2(87.5, 99), Vector2(96, 100.5)]
# where villagers go: the well, the tavern, the cottages, the field, the gate road, the harbour, the pier, the smithy, the shrine
const GOAL_POINTS := [Vector2(64, 50), Vector2(30, 64), Vector2(24, 70), Vector2(42, 26), Vector2(58, 26), Vector2(87.5, 99),
	Vector2(96, 100.5), Vector2(92, 38), Vector2(103, 23), Vector2(62, 80), Vector2(70, 72), Vector2(40, 58)]
var GOALS := []
var graph := {}
var shade_grid: PackedFloat32Array
var trees := []        # [position (world), scale]

var rng := RandomNumberGenerator.new()
var noise := FastNoiseLite.new()
var pads := []          # [centre (plan), half extents, angle, level]

func _enter_tree() -> void:
	Palette.current = "hearth"
	Palette.fog = 0.2

static func W(p: Vector2, y := 0.0) -> Vector3:    # plan metres to world
	return Vector3(p.x - ORIGIN.x, y, p.y - ORIGIN.y)

func _ready() -> void:
	rng.seed = 1207
	noise.seed = 7; noise.frequency = 0.035
	for b in BUILDINGS:                                 # terraces first: the ground is shaped around them
		var c: Vector2 = b[0]; var corners := 0.0
		for k in 4:
			var u := (float(b[1]) * 0.5) * (1 if k % 2 == 0 else -1); var v := (float(b[2]) * 0.5) * (1 if k < 2 else -1)
			corners += _base(c + Vector2(u, v).rotated(b[3]))
		pads.append([c, Vector2(b[1], b[2]) * 0.5, b[3], max(corners / 4.0, _base(c)) + 0.05])
	pads.append([WELL, Vector2(5, 5), 0.0, _base(WELL)])     # the plaza round the well is level
	_terrain()
	_sea()
	for p in PATHS: _path(p[0], p[1])
	for b in BUILDINGS.size(): _building(b)
	_well()
	_harbour()
	_palisade()
	_field()
	_woods()
	_clutter()
	_graph()
	_villagers()
	_dress_player()
	call_deferred("_light")
	_bake_when_ready()
	var pl: Node3D = get_parent().get_node_or_null("Player")
	if pl: pl.global_position = W(WELL + Vector2(2.5, 2.5), height(WELL + Vector2(2.5, 2.5)) + 0.1)

# ---------------------------------------------------------------- the ground
func _coast_signed(p: Vector2) -> float:   # distance to the coastline: positive on land (north-west), negative at sea
	var best := INF; var sign_ := 1.0
	for i in COAST.size() - 1:
		var a: Vector2 = COAST[i]; var b: Vector2 = COAST[i + 1]
		var t := clampf((p - a).dot(b - a) / (b - a).length_squared(), 0.0, 1.0)
		var q := a + (b - a) * t; var d := p.distance_to(q)
		if d < best:
			best = d; sign_ = -1.0 if (b - a).cross(p - a) > 0.0 else 1.0
	return best * sign_

func _base(p: Vector2) -> float:          # the land before any terraces
	var c := _coast_signed(p)
	var hill := 7.5 * exp(-(pow((p.x - 100.0) / 38.0, 2) + pow((p.y - 24.0) / 28.0, 2)))
	var land := 1.4 + hill + 0.6 * noise.get_noise_2d(p.x, p.y)
	if c >= 0.0:
		return lerpf(0.25, land, smoothstep(0.0, 7.0, c))       # the beach rises from the waterline
	return lerpf(0.25, -2.6, smoothstep(0.0, 9.0, -c))          # the seabed falls away

func height(p: Vector2) -> float:          # with the terraces cut in
	var h := _base(p)
	for pad in pads:
		var q: Vector2 = (p - pad[0]).rotated(-pad[2]); var e: Vector2 = pad[1]
		var out := Vector2(maxf(absf(q.x) - e.x, 0.0), maxf(absf(q.y) - e.y, 0.0)).length()
		var w := 1.0 - smoothstep(0.0, 3.5, out)
		if w > 0.0: h = lerpf(h, pad[3], w)
	return h

func _terrain() -> void:
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var x0 := -MARGIN; var y0 := -MARGIN; var nx := int((140 + 2 * MARGIN) / 1.0); var ny := int((110 + 2 * MARGIN) / 1.0)
	var grass := Palette.col("grass"); var sand := Palette.col("sand"); var wet := sand.darkened(0.35)
	for j in ny + 1:
		for i in nx + 1:
			var p := Vector2(x0 + i, y0 + j); var h := height(p); var c := _coast_signed(p)
			var col := grass.lerp(grass.darkened(0.18), 0.5 + 0.5 * noise.get_noise_2d(p.x * 3.0, p.y * 3.0))
			col = col.lerp(sand, 1.0 - smoothstep(2.5, 6.5, c)); if c < 0.5: col = wet
			st.set_color(col * shade(p)); st.add_vertex(W(p, h))
	for j in ny:
		for i in nx:
			var a := j * (nx + 1) + i
			st.add_index(a); st.add_index(a + 1); st.add_index(a + nx + 1)
			st.add_index(a + 1); st.add_index(a + nx + 2); st.add_index(a + nx + 1)
	st.generate_normals()
	var mi := MeshInstance3D.new(); mi.mesh = st.commit(); mi.name = "Terrain"
	var mat := StandardMaterial3D.new(); mat.vertex_color_use_as_albedo = true; mat.roughness = 1.0; mi.material_override = mat
	add_child(mi)
	if not has_node("TerrainBody"):
		mi.create_trimesh_collision(); mi.get_child(0).name = "TerrainBody"; mi.get_child(0).reparent(self)
	if not shade_grid.is_empty(): return
	# land beyond the terrain's edges, to the horizon: four planes round it (north and west; the sea fills the south-east)
	var fm := StandardMaterial3D.new(); fm.albedo_color = grass.darkened(0.15); fm.roughness = 1.0
	var e0 := W(Vector2(x0, y0)); var e1 := W(Vector2(x0 + nx, y0 + ny))
	for r in [Rect2(e0.x - 400, e0.z - 400, (e1.x - e0.x) + 400, 400), Rect2(e0.x - 400, e0.z, 400, 600)]:
		var far := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = r.size; far.mesh = pm; far.material_override = fm
		far.position = Vector3(r.position.x + r.size.x * 0.5, 1.2, r.position.y + r.size.y * 0.5); add_child(far)

func _sea() -> void:
	var m := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(900, 900); m.mesh = pm
	var mat := StandardMaterial3D.new(); var c := Palette.col("sea"); mat.albedo_color = Color(c.r, c.g, c.b, 0.82)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA; mat.roughness = 0.06; mat.metallic = 0.15; mat.metallic_specular = 0.9
	m.material_override = mat; m.position = Vector3(300, 0.0, 300); add_child(m)

# ---------------------------------------------------------------- paths: smooth curves laid on the ground
func _path(pts: Array, width: float) -> void:
	var curve := Curve2D.new()
	for i in pts.size():
		var p: Vector2 = pts[i]
		var prev: Vector2 = pts[max(i - 1, 0)]; var next: Vector2 = pts[min(i + 1, pts.size() - 1)]
		var tan := (next - prev) * 0.25
		curve.add_point(p, -tan, tan)
	curve.bake_interval = 0.6
	var baked := curve.get_baked_points()
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var dirt := Palette.col("path")
	for i in baked.size():
		var p: Vector2 = baked[i]; var d: Vector2 = (baked[min(i + 1, baked.size() - 1)] - baked[max(i - 1, 0)]).normalized()
		var side := Vector2(-d.y, d.x)
		var hw := width * 0.5 * (1.0 + 0.18 * noise.get_noise_2d(p.x * 6.0, p.y * 6.0))   # ragged, worn edges
		for s in [-1.0, 1.0]:
			var q: Vector2 = p + side * hw * s
			st.set_color(dirt.lerp(dirt.darkened(0.15), 0.5 + 0.5 * noise.get_noise_2d(q.x * 9.0, q.y * 9.0)) * shade(q))
			st.add_vertex(W(q, height(q) + 0.05))
	for i in baked.size() - 1:
		var a := i * 2
		st.add_index(a); st.add_index(a + 2); st.add_index(a + 1); st.add_index(a + 1); st.add_index(a + 2); st.add_index(a + 3)
	st.generate_normals()
	var mi := MeshInstance3D.new(); mi.mesh = st.commit(); mi.add_to_group("path_mesh")
	var mat := StandardMaterial3D.new(); mat.vertex_color_use_as_albedo = true; mat.roughness = 1.0; mi.material_override = mat
	add_child(mi)

# ---------------------------------------------------------------- buildings, each on its terrace
func _building(i: int) -> void:
	var b: Array = BUILDINGS[i]; var c: Vector2 = b[0]; var a: float = b[3]; var level: float = pads[i][3]
	var e1 := Vector2(cos(a), sin(a)); var e2 := Vector2(-sin(a), cos(a))
	var to_path := (_nearest_path_point(c) - c).normalized()
	var faces := [[e2, b[1], b[2]], [-e2, b[1], b[2]], [e1, b[2], b[1]], [-e1, b[2], b[1]]]   # (facing, front width, depth)
	if b[5] == "shrine": faces = [[Vector2(0, 1).rotated(a), b[1], b[2]]]
	var best = faces[0]
	for f in faces:
		if (f[0] as Vector2).dot(to_path) > (best[0] as Vector2).dot(to_path): best = f
	var facing: Vector2 = best[0]; var bays := int(round(float(best[1]) / 2.0)); var deep := int(round(float(best[2]) / 2.0))
	var kinds := {"tavern": ["UnevenBrick", "Plaster"], "smithy": ["UnevenBrick", "UnevenBrick"], "shrine": ["UnevenBrick"],
		"granary": ["Plaster"], "store": ["UnevenBrick"], "shed": ["Plaster"]}
	var walls: Array = kinds.get(b[5], ["UnevenBrick", "Plaster"] if rng.randf() < 0.6 else ["Plaster", "Plaster"])
	var storeys: int = b[4]
	var w := []; for s in storeys: w.append(walls[min(s, walls.size() - 1)])
	var front := c + facing * (deep * 1.0)
	place_house({"bays": bays, "deep": deep, "storeys": storeys, "walls": w, "door": [bays / 2]}, W(front, level), Vector3(facing.x, 0, facing.y))
	# a stone foundation where the ground falls away below the terrace
	var low := level
	for k in 4:
		var u := (bays * 1.0 + 0.3) * (1 if k % 2 == 0 else -1); var v := (deep * 1.0 + 0.3) * (1 if k < 2 else -1)
		low = minf(low, _base(c + facing.orthogonal() * u + facing * v))
	if level - low > 0.15:
		var plinth := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(bays * 2.0 + 0.6, level - low + 0.4, deep * 2.0 + 0.6)
		plinth.mesh = bm; var pmat := StandardMaterial3D.new(); pmat.albedo_texture = load("res://assets/library/UnevenBrick_detail.png")
		pmat.albedo_color = Palette.col("UnevenBrick") / 0.78; pmat.uv1_triplanar = true; pmat.uv1_scale = Vector3(0.5, 0.5, 0.5); plinth.material_override = pmat
		plinth.position = W(c, (level + low - 0.4) * 0.5); plinth.rotation.y = -atan2(facing.y, facing.x) + PI / 2
		add_child(plinth)

func _nearest_path_point(p: Vector2) -> Vector2:
	var best := p; var bd := INF
	for path in PATHS:
		var pts: Array = path[0]
		for i in pts.size() - 1:
			var a: Vector2 = pts[i]; var b: Vector2 = pts[i + 1]
			var t := clampf((p - a).dot(b - a) / (b - a).length_squared(), 0.0, 1.0); var q := a + (b - a) * t
			if p.distance_to(q) < bd: bd = p.distance_to(q); best = q
	return best

func _well() -> void:
	var y := height(WELL)
	var ring := MeshInstance3D.new(); var cm := CylinderMesh.new(); cm.top_radius = 1.0; cm.bottom_radius = 1.1; cm.height = 0.9
	ring.mesh = cm; var m := StandardMaterial3D.new(); m.albedo_texture = load("res://assets/library/UnevenBrick_detail.png")
	m.albedo_color = Palette.col("UnevenBrick") / 0.78; m.uv1_triplanar = true; ring.material_override = m
	ring.position = W(WELL, y + 0.45); add_child(ring)
	var water := MeshInstance3D.new(); var wm := CylinderMesh.new(); wm.top_radius = 0.85; wm.bottom_radius = 0.85; wm.height = 0.05
	water.mesh = wm; var wmat := StandardMaterial3D.new(); wmat.albedo_color = Palette.col("sea").darkened(0.4); wmat.roughness = 0.05
	water.material_override = wmat; water.position = W(WELL, y + 0.7); add_child(water)
	put(PROPS % "Bucket_Wooden_1", W(WELL + Vector2(1.6, 0.8), y), 0.3)
	var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var cyl := CylinderShape3D.new(); cyl.radius = 1.1; cyl.height = 1.0
	col.shape = cyl; body.add_child(col); body.position = W(WELL, y + 0.5); add_child(body)

# ---------------------------------------------------------------- the harbour: sea wall, breakwater, lighthouse, pier, boats
func _stone_run(pts: Array, width: float, top: float) -> void:
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]; var b: Vector2 = pts[i + 1]; var mid := (a + b) * 0.5; var L := a.distance_to(b)
		var low := minf(_base(a), _base(b)) - 2.0
		var mi := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(L + 0.6, top - low, width); mi.mesh = bm
		var m := StandardMaterial3D.new(); m.albedo_texture = load("res://assets/library/RockTrim_detail.png")
		m.albedo_color = Palette.col("RockTrim") / 0.78; m.uv1_triplanar = true; m.uv1_scale = Vector3(0.35, 0.35, 0.35); mi.material_override = m
		mi.position = W(mid, (top + low) * 0.5); mi.rotation.y = -atan2(b.y - a.y, b.x - a.x); add_child(mi)
		var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = bm.size
		col.shape = bs; body.add_child(col); body.transform = mi.transform; add_child(body)

func _harbour() -> void:
	_stone_run([Vector2(80, 82), Vector2(92, 76), Vector2(100, 70), Vector2(106, 62)], 2.2, 0.9)       # the sea wall
	_stone_run([Vector2(106, 62), Vector2(116, 64), Vector2(126, 70), Vector2(132, 79)], 2.6, 0.9)     # the breakwater
	var lh := Vector2(132.5, 80.5)                                                                      # the lighthouse
	for k in 4:
		var t := MeshInstance3D.new(); var cm := CylinderMesh.new(); cm.top_radius = 1.9 - k * 0.25; cm.bottom_radius = 2.2 - k * 0.25; cm.height = 3.2
		t.mesh = cm; var m := StandardMaterial3D.new(); m.albedo_texture = load("res://assets/library/Plaster_detail.png")
		m.albedo_color = (Palette.col("Plaster") if k % 2 == 0 else Palette.col("RedBrick")) / 0.78; m.uv1_triplanar = true; t.material_override = m
		t.position = W(lh, 0.9 + 1.6 + k * 3.2); add_child(t)
	var lamp := OmniLight3D.new(); lamp.light_color = Color(1, 0.8, 0.5); lamp.light_energy = 2.0; lamp.omni_range = 18
	lamp.position = W(lh, 15.0); add_child(lamp)
	put(VILLAGE % "Roof_Tower_RoundTiles", W(lh, 13.7), 0.0, 0.9, false)
	# the pier: a T of planks on posts, its deck above the water
	var deck_y := 1.0
	_pier_run(Vector2(87.5, 80), Vector2(87.5, 100), deck_y); _pier_run(Vector2(78, 100.5), Vector2(106, 100.5), deck_y)
	_boat(Vector2(96, 92), -0.3, 7.0); _boat(Vector2(76, 94), 0.4, 5.5); _boat(Vector2(120, 100), 0.05, 15.0, true)

func _pier_run(a: Vector2, b: Vector2, y: float) -> void:
	var d := (b - a).normalized(); var L := a.distance_to(b); var n := int(L / 2.0)
	for k in n + 1:
		var p := a + d * (k * 2.0)
		_piece("Floor_WoodDark", W(p, y), -atan2(d.y, d.x) + PI / 2)
		for s in [-1.0, 1.0]:
			var q: Vector2 = p + d.orthogonal() * 1.0 * s
			var post := MeshInstance3D.new(); var cm := CylinderMesh.new(); cm.top_radius = 0.12; cm.bottom_radius = 0.14; cm.height = 4.0
			post.mesh = cm; var m := StandardMaterial3D.new(); m.albedo_color = Palette.col("WoodTrim").darkened(0.25); post.material_override = m
			post.position = W(q, y - 1.8); add_child(post)
	var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(L + 2.0, 0.3, 2.2)
	col.shape = bs; body.add_child(col); body.position = W((a + b) * 0.5, y - 0.15); body.rotation.y = -atan2(d.y, d.x); add_child(body)

func _boat(c: Vector2, a: float, length: float, ship := false) -> void:
	var root := Node3D.new(); root.position = W(c, 0.05); root.rotation.y = -a; add_child(root)
	var wood := StandardMaterial3D.new(); wood.albedo_texture = load("res://assets/library/WoodTrim_detail.png"); wood.albedo_color = Palette.col("WoodTrim") / 0.78
	wood.uv1_triplanar = true
	var hull := MeshInstance3D.new(); var pm := PrismMesh.new(); pm.size = Vector3(length * 0.32, length * (0.13 if ship else 0.12), length)
	hull.mesh = pm; hull.rotation.z = PI; hull.position.y = pm.size.y * 0.35; hull.material_override = wood; root.add_child(hull)
	if ship:
		var mast := MeshInstance3D.new(); var cm := CylinderMesh.new(); cm.top_radius = 0.12; cm.bottom_radius = 0.18; cm.height = length * 0.9
		mast.mesh = cm; mast.material_override = wood; mast.position.y = cm.height * 0.5; root.add_child(mast)
		var sail := MeshInstance3D.new(); var qm := QuadMesh.new(); qm.size = Vector2(length * 0.42, length * 0.5); sail.mesh = qm
		var sm := StandardMaterial3D.new(); sm.albedo_color = Color(0.86, 0.82, 0.72); sm.cull_mode = BaseMaterial3D.CULL_DISABLED; sail.material_override = sm
		sail.position = Vector3(0, length * 0.5, 0.2); sail.rotation.y = PI / 2; root.add_child(sail)

# ---------------------------------------------------------------- the palisade and its north gate
func _palisade() -> void:
	var runs := [[Vector2(57, 4), Vector2(40, 6), Vector2(10, 8), Vector2(6, 40), Vector2(8, 70), Vector2(20, 92)],
		[Vector2(67, 4), Vector2(92, 8), Vector2(112, 18), Vector2(118, 40)]]
	var cm := CylinderMesh.new(); cm.top_radius = 0.16; cm.bottom_radius = 0.2; cm.height = 3.2
	var mat := StandardMaterial3D.new(); mat.albedo_color = Palette.col("WoodTrim").darkened(0.1); cm.material = mat
	var xf := []
	for run in runs:
		for i in run.size() - 1:
			var a: Vector2 = run[i]; var b: Vector2 = run[i + 1]; var n := int(a.distance_to(b) / 0.42)
			for k in n:
				var p := a.lerp(b, float(k) / n)
				xf.append(Transform3D(Basis(Vector3(rng.randf_range(-1, 1), 0, rng.randf_range(-1, 1)).normalized(), rng.randf_range(0.0, 0.05)), W(p, height(p) + 1.4 + rng.randf_range(-0.2, 0.2))))
			var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(a.distance_to(b), 3.0, 0.5)
			col.shape = bs; body.add_child(col); body.position = W((a + b) * 0.5, height((a + b) * 0.5) + 1.4); body.rotation.y = -atan2(b.y - a.y, b.x - a.x); add_child(body)
	var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = cm; mm.instance_count = xf.size()
	for i in xf.size(): mm.set_instance_transform(i, xf[i])
	var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm; add_child(mmi)
	for x in [57.5, 66.5]:   # the gate's towers
		var p := Vector2(x, 4.0); var t := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(2.0, 6.0, 2.0); t.mesh = bm
		t.material_override = mat; t.position = W(p, height(p) + 3.0); add_child(t)
		put(VILLAGE % "Roof_Tower_RoundTiles", W(p, height(p) + 6.0), 0.0, 0.55, false)
	var gate := MeshInstance3D.new(); var gm := BoxMesh.new(); gm.size = Vector3(8.0, 3.6, 0.3); gate.mesh = gm; gate.material_override = mat
	gate.position = W(Vector2(62, 4), height(Vector2(62, 4)) + 1.8); add_child(gate)

# ---------------------------------------------------------------- the field, the plots and the woods (batched)
func scatter(path: String, points: Array, scale_range := Vector2(0.9, 1.1)) -> void:
	var s: PackedScene = load(path)
	if s == null or points.is_empty(): return
	var proto: Node3D = s.instantiate()
	for mi in proto.find_children("*", "MeshInstance3D", true, false):
		var src := mi as MeshInstance3D
		var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = src.mesh; mm.instance_count = points.size()
		for i in points.size():
			var t := Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * rng.randf_range(scale_range.x, scale_range.y)), points[i])
			mm.set_instance_transform(i, t * src.transform)
		var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm; add_child(mmi)
	proto.free()

func _ground_pts(n: int, inside: Callable) -> Array:
	var out := []
	var tries := 0
	while out.size() < n and tries < n * 30:
		tries += 1
		var p := Vector2(rng.randf_range(-MARGIN, 140 + MARGIN), rng.randf_range(-MARGIN, 110 + MARGIN))
		if inside.call(p): out.append(W(p, height(p)))
	return out

func _in_clearing(p: Vector2) -> bool:
	return pow((p.x - 62) / 54.0, 2) + pow((p.y - 50) / 44.0, 2) < 1.0 or (p.x > 50 and p.y > 76) or (p.x > 95 and p.y > 46)

func _near_built(p: Vector2, r := 2.5) -> bool:
	for pad in pads:
		var q: Vector2 = (p - pad[0]).rotated(-pad[2]); var e: Vector2 = pad[1]
		if absf(q.x) < e.x + r and absf(q.y) < e.y + r: return true
	return p.distance_to(_nearest_path_point(p)) < 2.6

func _field() -> void:
	var wheat := []
	for i in 34: for j in 24:
		var p := Vector2(15 + i * 0.8 + rng.randf_range(-0.2, 0.2), 15 + j * 0.8 + rng.randf_range(-0.2, 0.2)); wheat.append(W(p, height(p)))
	scatter(NATURE % "Grass_Wispy_Tall", wheat, Vector2(1.1, 1.5))
	for edge in [[Vector2(14, 14), Vector2(42, 14)], [Vector2(42, 14), Vector2(42, 34)], [Vector2(42, 34), Vector2(14, 34)], [Vector2(14, 34), Vector2(14, 14)]]:
		var a: Vector2 = edge[0]; var b: Vector2 = edge[1]; var n := int(a.distance_to(b) / 2.0)
		for k in n:
			var p := a.lerp(b, (k + 0.5) / n)
			if absf(p.x - 42) < 0.1 and absf(p.y - 27) < 2.5: continue        # the gap where the path comes in
			put(VILLAGE % "Prop_WoodenFence_Single", W(p, height(p)), -atan2(b.y - a.y, b.x - a.x), 1.0, true)
	var plots := []
	for i in 5: for j in 9:
		var p := Vector2(17.5 + i * 3.0, 39.5 + j * 0.75); plots.append(W(p, height(p)))
	scatter(NATURE % "Plant_1", plots, Vector2(0.5, 0.7))

func _woods() -> void:
	var pts := _ground_pts(260, func(p): return not _in_clearing(p) and _coast_signed(p) > 6.0)
	var by_kind := {}
	for i in pts.size():
		var kind := ("CommonTree_%d" % (i % 5 + 1)) if i % 3 != 0 else ("Pine_%d" % (i % 5 + 1))
		if not by_kind.has(kind): by_kind[kind] = []
		by_kind[kind].append(pts[i])
		trees.append([pts[i], 1.12])
		var body := StaticBody3D.new(); body.collision_layer = 2; body.collision_mask = 0   # trunks block walking, not the shadow rays
		var col := CollisionShape3D.new(); var cyl := CylinderShape3D.new(); cyl.radius = 0.35; cyl.height = 4.0; col.shape = cyl
		body.add_child(col); body.position = pts[i] + Vector3(0, 2.0, 0); add_child(body)
	for kind in by_kind: scatter(NATURE % kind, by_kind[kind], Vector2(0.9, 1.35))
	scatter(NATURE % "Grass_Common_Short", _ground_pts(1400, func(p): return _coast_signed(p) > 5.0 and not _near_built(p) and not (p.x > 14 and p.x < 42 and p.y > 14 and p.y < 47)))
	scatter(NATURE % "Flower_3_Group", _ground_pts(140, func(p): return _in_clearing(p) and _coast_signed(p) > 6.0 and not _near_built(p, 1.5)), Vector2(0.28, 0.4))
	scatter(NATURE % "Fern_1", _ground_pts(260, func(p): return not _in_clearing(p) and _coast_signed(p) > 6.0))
	for i in 14:
		var p := Vector2(rng.randf_range(60, 130), rng.randf_range(70, 105))
		if _coast_signed(p) < -1.0 and _coast_signed(p) > -9.0: put(NATURE % ("Rock_Medium_%d" % (i % 3 + 1)), W(p, height(p)), rng.randf() * TAU, rng.randf_range(1.2, 2.2))

# ---------------------------------------------------------------- life: around the well, the smithy, the shore
func _at(p: Vector2, name: String, yaw := 0.0, path := PROPS) -> void:
	put(path % name, W(p, height(p)), yaw)

func _clutter() -> void:
	_at(Vector2(68, 54), "Barrel"); _at(Vector2(68.8, 54.8), "Barrel"); _at(Vector2(55, 52), "Crate_Wooden", 0.4); _at(Vector2(66, 46), "Bench", 0.3)
	_at(Vector2(60, 53.5), "Stall_Cart_Empty", 0.9); _at(Vector2(61.5, 55.5), "FarmCrate_Apple", 0.2); _at(Vector2(69.5, 49.5), "Barrel_Apples")
	_at(Vector2(87, 45), "Anvil_Log", 0.3); _at(Vector2(89.5, 41.5), "Anvil", 0.2); _at(Vector2(92, 43.5), "Workbench", -0.3)
	_at(Vector2(86.2, 46.2), "Axe_Bronze", 1.1)                                     # B: the hatchet at the woodpile
	_at(Vector2(84, 78), "Barrel"); _at(Vector2(82.5, 79.5), "Crate_Wooden"); _at(Vector2(78, 76), "Rope_2")
	_at(Vector2(33, 56), "Barrel"); _at(Vector2(34, 56.8), "Barrel"); _at(Vector2(24, 60), "Crate_Wooden", 0.7)
	_at(Vector2(44, 64), "Bucket_Wooden_1"); _at(Vector2(31, 50), "Chest_Wood", 0.4)

# ---------------------------------------------------------------- late afternoon
func _light() -> void:
	var sun: DirectionalLight3D = get_parent().get_node_or_null("Sun")
	if sun:
		sun.rotation_degrees = Vector3(-17, -62, 0); sun.light_color = Color(1.0, 0.8, 0.58); sun.light_energy = 1.05
		sun.directional_shadow_max_distance = 30.0
		sun.shadow_enabled = false          # baked; F2 turns on live shadows for characters
	var env: Environment = get_parent().get_node("WorldEnvironment").environment
	env.tonemap_exposure = 0.9; env.ambient_light_energy = 0.45
	var sky: ProceduralSkyMaterial = env.sky.sky_material
	sky.sky_top_color = Color(0.42, 0.56, 0.74); sky.sky_horizon_color = Color(0.93, 0.78, 0.6)
	sky.ground_horizon_color = Color(0.93, 0.78, 0.6); sky.sun_angle_max = 30.0


# ---------------------------------------------------------------- villagers
func _graph() -> void:
	var key := func(p: Vector2) -> String: return "%d,%d" % [roundi(p.x), roundi(p.y)]
	var ids := {}
	var add := func(p: Vector2) -> int:
		var k: String = key.call(p)
		if not ids.has(k): ids[k] = ids.size(); graph[ids[k]] = [p, []]
		return ids[k]
	var runs := []
	for path in PATHS: runs.append((path[0] as Array).slice(1) if (path[0][0] as Vector2).y < 0 else path[0])
	runs.append(PIER)
	for run in runs:
		var prev := -1
		for p in run:
			var id: int = add.call(p)
			if prev >= 0 and not (graph[prev][1] as Array).has(id): graph[prev][1].append(id); graph[id][1].append(prev)
			prev = id
	for g in GOAL_POINTS:
		var k: String = key.call(g)
		if ids.has(k): GOALS.append(ids[k])

const LOOKS := [
	{"body": "res://assets/characters/quaternius/Superhero_Male_Head.gltf", "outfit": "res://assets/characters/quaternius/outfits/Male_Peasant.gltf", "hair": "res://assets/characters/quaternius/hair/Hair_SimpleParted.gltf"},
	{"body": "res://assets/characters/quaternius/Superhero_Female_Head.gltf", "outfit": "res://assets/characters/quaternius/outfits/Female_Peasant.gltf", "hair": "res://assets/characters/quaternius/hair/Hair_Long.gltf"},
	{"body": "res://assets/characters/quaternius/Superhero_Male_Head.gltf", "outfit": "res://assets/characters/quaternius/outfits/Male_Peasant.gltf", "hair": "res://assets/characters/quaternius/hair/Hair_Buzzed.gltf"},
	{"body": "res://assets/characters/quaternius/Superhero_Female_Head.gltf", "outfit": "res://assets/characters/quaternius/outfits/Female_Peasant.gltf", "hair": "res://assets/characters/quaternius/hair/Hair_Buns.gltf"},
	{"body": "res://assets/characters/quaternius/Superhero_Male_Head.gltf", "outfit": "res://assets/characters/quaternius/outfits/Male_Peasant.gltf", "hair": "res://assets/characters/quaternius/hair/Hair_Beard.gltf"},
]

func _villagers() -> void:
	var keys := graph.keys()
	for i in 9:
		var v := Node3D.new(); v.set_script(load("res://scripts/villager.gd")); v.name = "Villager%d" % i
		add_child(v)
		v.setup(self, graph, keys[(i * 5 + 3) % keys.size()], LOOKS[i % LOOKS.size()], 100 + i)

func _dress_player() -> void:
	var model: Node = get_parent().get_node_or_null("Player/Model")
	if model == null: return
	Dress.wear(model, "res://assets/characters/quaternius/outfits/Male_Peasant.gltf")
	Dress.wear(model, "res://assets/characters/quaternius/hair/Hair_SimpleParted.gltf", Color(0.3, 0.19, 0.11))
	var pl: Node3D = get_parent().get_node("Player")
	pl.add_child(Dress.blob(1.0))
	(pl as CollisionObject3D).collision_mask = 1 | 2

# ---------------------------------------------------------------- shadows, baked once (the WoW way)
const SHADE := 0.62    # how dark the ground is in shadow
var _x0 := -MARGIN
var _y0 := -MARGIN
var _nx := int(140 + 2 * MARGIN)
var _ny := int(110 + 2 * MARGIN)

func shade(p: Vector2) -> float:
	if shade_grid.is_empty(): return 1.0
	var i := clampi(int(p.x - _x0), 0, _nx - 1); var j := clampi(int(p.y - _y0), 0, _ny - 1)
	return shade_grid[j * _nx + i]

func _bake_when_ready() -> void:
	await get_tree().physics_frame
	await get_tree().physics_frame
	var sun: DirectionalLight3D = get_parent().get_node("Sun")
	var travel := -sun.global_transform.basis.z         # the direction the sunlight travels
	var to_sun := -travel
	var space := get_world_3d().direct_space_state
	var raw := PackedFloat32Array(); raw.resize(_nx * _ny); raw.fill(1.0)
	var q := PhysicsRayQueryParameters3D.new(); q.collision_mask = 1
	for j in _ny:
		for i in _nx:
			var p := Vector2(_x0 + i + 0.5, _y0 + j + 0.5)
			if _coast_signed(p) < -2.0: continue
			var from := W(p, height(p) + 0.25)
			q.from = from; q.to = from + to_sun * 70.0
			if not space.intersect_ray(q).is_empty(): raw[j * _nx + i] = SHADE
	var horiz := Vector2(travel.x, travel.z).normalized(); var stretch := 1.0 / maxf(0.2, -travel.y)
	for t in trees:                                     # tree crowns: a soft oval along the light
		var base: Vector3 = t[0]; var sc: float = t[1]; var top: Vector3 = base + Vector3(0, 4.0 * sc, 0)
		var hit: Vector3 = top + travel * ((top.y - base.y) / -travel.y)
		var c := Vector2(hit.x, hit.z) + Vector2(ORIGIN.x, ORIGIN.y)
		for dj in range(-5, 6):
			for di in range(-5, 6):
				var off := Vector2(di, dj); var along := off.dot(horiz) / stretch; var across := off.dot(horiz.orthogonal())
				if along * along + across * across < pow(2.0 * sc, 2):
					var ii := int(c.x - _x0) + di; var jj := int(c.y - _y0) + dj
					if ii >= 0 and jj >= 0 and ii < _nx and jj < _ny: raw[jj * _nx + ii] = minf(raw[jj * _nx + ii], 0.7)
	shade_grid = raw.duplicate()                        # soften the edges a little
	for j in range(1, _ny - 1):
		for i in range(1, _nx - 1):
			var acc := 0.0
			for dj in [-1, 0, 1]: for di in [-1, 0, 1]: acc += raw[(j + dj) * _nx + i + di]
			shade_grid[j * _nx + i] = acc / 9.0
	get_node("Terrain").queue_free()
	for m in get_tree().get_nodes_in_group("path_mesh"): m.queue_free()
	await get_tree().process_frame
	_terrain()
	for p in PATHS: _path(p[0], p[1])
	_world_casts_no_shadows(self)

func _world_casts_no_shadows(n: Node) -> void:      # the world's shadows are baked; only characters may cast live ones
	for c in n.get_children():
		if c.name.begins_with("Villager"): continue
		if c is GeometryInstance3D: (c as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_world_casts_no_shadows(c)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("shadows_toggle"):        # F2: live character shadows on or off (the world's stay baked)
		var sun: DirectionalLight3D = get_parent().get_node("Sun")
		sun.shadow_enabled = not sun.shadow_enabled
		for b in get_tree().get_nodes_in_group("blob"): b.visible = not sun.shadow_enabled
