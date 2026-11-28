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
# the plan (tools/map/farhallow_plan.py writes it): buildings from their floorplans (tools/map/building_types.py), plots,
# roads, lanes, a path from every door, and every doodad with its purpose
const PLAN_JSON := "res://data/farhallow.json"
const TYPES_JSON := "res://data/building_types.json"
var PLAN := {}
var TYPES := {}
var PATHS := []        # [points, width, purpose]; each must lead somewhere, avoid walls but at doors, and not duplicate another
var BUILDINGS := []    # the plan's buildings
var bdoors := []       # each building's street doors (plan)
var roofed := []       # [centre, half extents, angle] of every roofed room: "inside a building" means in one of these
const WELL := Vector2(64, 50)
const PIER := [Vector2(87, 81), Vector2(87.5, 90), Vector2(87.5, 99), Vector2(96, 100.5)]
var GOALS := []
var graph := {}
var shade_grid: PackedFloat32Array
var trees := []        # [position (world), scale]
var houses := []       # [kind, centre (plan), door (plan), roof]

var rng := RandomNumberGenerator.new()
var path_surfaces := []   # [vertices (world), triangles] of every path strip, for the ground check
var noise := FastNoiseLite.new()
var pads := []          # [centre (plan), half extents, angle, level]

func _enter_tree() -> void:
	Palette.current = "hearth"
	Palette.fog = 0.2
	PLAN = JSON.parse_string(FileAccess.get_file_as_string(PLAN_JSON))
	TYPES = JSON.parse_string(FileAccess.get_file_as_string(TYPES_JSON))
	BUILDINGS = PLAN.buildings
	for r in PLAN.roads:
		var pts := []; for q in r.pts: pts.append(Vector2(q[0], q[1]))
		if r.name == "gate road": pts.push_front(Vector2(62, -20))          # on through the gate, out of the village
		PATHS.append([pts, float(r.width), "the " + r.name])
	for r in PLAN.lanes:
		var pts := []; for q in r.pts: pts.append(Vector2(q[0], q[1]))
		PATHS.append([pts, float(r.width), "the " + r.name])
	for sp in PLAN.spurs:
		var b: Dictionary = BUILDINGS[int(sp.owner)]
		PATHS.append([[Vector2(sp.door[0], sp.door[1]), Vector2(sp.to[0], sp.to[1])], 1.2, "the path to the door of %s" % (b.name if b.name != "" else b.type)])
	for t in PLAN.trails:   # worn footpaths from back doors, side doors, yard gates and plot gates
		var pts := []; for q in t.pts: pts.append(Vector2(q[0], q[1]))
		PATHS.append([pts, float(t.width), t.purpose, "trail"])
	for b in BUILDINGS:
		var ds := []; for d in b.doors: ds.append(Vector2(d[0], d[1]))
		bdoors.append(ds)

static func W(p: Vector2, y := 0.0) -> Vector3:    # plan metres to world
	return Vector3(p.x - ORIGIN.x, y, p.y - ORIGIN.y)

func _ready() -> void:
	rng.seed = 1207
	noise.seed = 7; noise.frequency = 0.035
	for b in BUILDINGS:                                 # terraces first: the ground is shaped around them
		var c := Vector2(b.x, b.y); var a: float = b.a; var corners := 0.0
		for k in 4:
			var u := (float(b.w) * 0.5) * (1 if k % 2 == 0 else -1); var v := (float(b.h) * 0.5) * (1 if k < 2 else -1)
			corners += _base(c + Vector2(u, v).rotated(a))
		pads.append([c, Vector2(b.w, b.h) * 0.5, a, max(corners / 4.0, _base(c)) + 0.05])
	pads.append([WELL, Vector2(6, 6), 0.0, _base(WELL)])     # the square round the well is level
	_terrain()
	_sea()
	for b in BUILDINGS.size(): _build(b)
	for pl in PLAN.plots: _plot(pl)
	_well()
	var ws := Vector2(PLAN.waystone.x, PLAN.waystone.y)
	put("res://assets/props/fogwright/Waystone_Village.glb", W(ws, height(ws)), -float(PLAN.waystone.a), 1.0, true, "fixture", "the old waystone, older than the village")
	_harbour()
	_palisade()
	_field()
	_woods()
	_doodads()
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
		var q: Vector2 = (p - pad[0]).rotated(-pad[2]); var e: Vector2 = pad[1] + Vector2(1.5, 1.5)   # a level apron round it
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
			st.set_color(col / 0.8); st.set_uv(_light_uv(p)); st.set_uv2(p * 0.45); st.add_vertex(W(p, h))
	for j in ny:
		for i in nx:
			var a := j * (nx + 1) + i
			st.add_index(a); st.add_index(a + 1); st.add_index(a + nx + 1)
			st.add_index(a + 1); st.add_index(a + nx + 2); st.add_index(a + nx + 1)
	st.generate_normals()
	var mi := MeshInstance3D.new(); mi.mesh = st.commit(); mi.name = "Terrain"
	mi.material_override = _ground_shader()
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
func _path(pts: Array, width: float, trail := false) -> void:
	var curve := Curve2D.new()
	for i in pts.size():
		var p: Vector2 = pts[i]
		var prev: Vector2 = pts[max(i - 1, 0)]; var next: Vector2 = pts[min(i + 1, pts.size() - 1)]
		var tan := (next - prev) * 0.25
		curve.add_point(p, -tan, tan)
	curve.bake_interval = 0.4
	var baked := curve.get_baked_points()
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var dirt := Palette.col("path")
	if trail: dirt = dirt.lerp(Palette.col("grass"), 0.35)      # a trail: worn into the grass, not a made path
	var verts := []; var tris := []
	for i in baked.size():
		var p: Vector2 = baked[i]; var d: Vector2 = (baked[min(i + 1, baked.size() - 1)] - baked[max(i - 1, 0)]).normalized()
		var side := Vector2(-d.y, d.x)
		var hw := width * 0.5 * (1.0 + 0.18 * noise.get_noise_2d(p.x * 6.0, p.y * 6.0))   # ragged, worn edges
		for s in [-1.0, -0.5, 0.0, 0.5, 1.0]:
			var q: Vector2 = p + side * hw * s
			st.set_color(dirt.lerp(dirt.darkened(0.15), 0.5 + 0.5 * noise.get_noise_2d(q.x * 9.0, q.y * 9.0)) / 0.8)
			st.set_uv(_light_uv(q)); st.set_uv2(q * 0.4)
			var v := W(q, _ground_top(q, 0.3) + 0.03)        # draped on the drawn ground, just above its highest point close by
			st.add_vertex(v); verts.append(v)
	for i in baked.size() - 1:
		var a := i * 5
		for k in 4:
			for t in [[a + k, a + 5 + k, a + k + 1], [a + k + 1, a + 5 + k, a + 6 + k]]:
				st.add_index(t[0]); st.add_index(t[1]); st.add_index(t[2]); tris.append(t)
	path_surfaces.append([verts, tris])
	st.generate_normals()
	var mi := MeshInstance3D.new(); mi.mesh = st.commit(); mi.add_to_group("path_mesh")
	mi.material_override = _ground_material("Path")
	add_child(mi)

# ---------------------------------------------------------------- buildings, built from their floorplans
# Each building is its type's floorplan (tools/map/building_types.py), placed whole: the kit's 2 m wall pieces run along
# every outside edge of its roofed rooms, fitted to the edge's real length, with a door or window where the floorplan
# has one; each wing (roofed rooms that make a rectangle) gets a roof fitted to it, with gable ends; yards get fences or
# walls. Floorplan coordinates: x across the front, y back from the street (y = 0 is the street side).
const STOREYS := {"street_house": 2, "merchant_house": 2, "merchant_house_small": 2, "inn": 2}
const LOW := {"hen_house": 0.55, "salt_works": 0.8, "guard_post": 0.85, "smokehouse": 0.9}   # small sheds: lower walls
const THATCH_TYPES := ["cottage", "farmstead", "hen_house", "smokehouse", "boat_shed", "salt_works", "granary"]
const ROOF_SIZES := {4: [4, 6, 8], 6: [6, 8, 10, 12, 14], 8: [8, 10, 12, 14]}   # (the kit's 6x4 is a single slope, not a roof)

func _wall_kinds(b: Dictionary) -> Array:
	match b.zone:
		"rich": return ["UnevenBrick", "Plaster", "Plaster"]
		"middling": return ["Plaster", "Plaster"]
		"poor": return ["Plaster"]
		"trade": return ["UnevenBrick"] if b.type != "boat_shed" else ["Plaster"]
	return ["UnevenBrick", "Plaster"]   # the inn, the guard post, the shrine

func _is_roofed(r: Array) -> bool:
	return r[5] in ["room", "shop", "out"] or str(r[4]).begins_with("arch")

func _build(i: int) -> void:
	var b: Dictionary = BUILDINGS[i]; var ty: Dictionary = TYPES[b.type]
	var c := Vector2(b.x, b.y); var level: float = pads[i][3]
	if b.type == "granary": level += 0.55                  # it stands on staddle stones
	var root := Node3D.new(); root.position = W(c, level); root.rotation.y = -float(b.a); add_child(root)
	var fw: float = b.w; var fh: float = b.h; var mir: bool = b.mirror
	var L := func(x: float, y: float, h := 0.0) -> Vector3: return Vector3((fw - x if mir else x) - fw * 0.5, h, y - fh * 0.5)
	var rooms: Array = ty.rooms
	# the roofed rooms, leaving out any set inside another (an alcove)
	var roofs := []
	for r in rooms:
		if not _is_roofed(r): continue
		var inside := false
		for o in rooms:
			if o != r and _is_roofed(o) and r[0] >= o[0] - 0.01 and r[1] >= o[1] - 0.01 and r[0] + r[2] <= o[0] + o[2] + 0.01 and r[1] + r[3] <= o[1] + o[3] + 0.01 and (r[2] * r[3] < o[2] * o[3]): inside = true
		if not inside: roofs.append(r)
	for r in roofs:
		var cc: Vector2 = c + Vector2((fw - (r[0] + r[2] * 0.5) if mir else r[0] + r[2] * 0.5) - fw * 0.5, r[1] + r[3] * 0.5 - fh * 0.5).rotated(b.a)
		roofed.append([cc, Vector2(r[2], r[3]) * 0.5, float(b.a)])
	var storeys: int = STOREYS.get(b.type, 1); var low: float = LOW.get(b.type, 1.0); var kinds := _wall_kinds(b)
	_into = root
	for r in roofs:
		for e in _edges(r, roofs):
			_wall_run(e, r, ty, storeys, low, kinds, L, mir)
	# most buildings are closed shells, as in any MMO: only the ones the story opens (smithy, boat shed) get an inside
	var inside: bool = ty.get("interior", false)
	if inside:
		for e in _inner_edges(roofs):                        # partitions between rooms, with the floorplan's inner doors
			_wall_run(e, [], ty, 1, low, kinds, L, mir, true)
	for r in rooms:                                          # floors: inside only where there is an inside; earth in yards
		if r[5] == "garden" or (not inside and r[5] != "yard"): continue
		var fl := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(r[2], 0.1, r[3]); fl.mesh = bm
		var key: String = {"room": "WoodTrim", "shop": "RockTrim", "out": "RockTrim", "stone": "RockTrim", "yard": "path"}.get(r[5], "WoodTrim")
		if b.type == "workshop": key = "path"                # a smithy's floor is earth, against sparks (docs/research/smithy.md)
		var fm := StandardMaterial3D.new(); fm.albedo_color = Palette.col(key) / (0.78 if key != "path" else 0.8)
		fm.albedo_texture = load("res://assets/library/%s_detail.png" % ({"WoodTrim": "WoodTrim", "RockTrim": "RockTrim", "path": "Path"}[key]))
		fm.uv1_triplanar = true; fm.uv1_scale = Vector3(0.5, 0.5, 0.5); fl.material_override = fm
		fl.position = L.call(r[0] + r[2] * 0.5, r[1] + r[3] * 0.5, -0.03 if r[5] == "yard" else -0.02); root.add_child(fl)
		if inside and _is_roofed(r) and r in roofs:          # the floors of the storeys above
			for st in range(1, storeys):
				var up := MeshInstance3D.new(); var um := BoxMesh.new(); um.size = Vector3(r[2], 0.12, r[3]); up.mesh = um
				var wm := StandardMaterial3D.new(); wm.albedo_texture = load("res://assets/library/WoodTrim_detail.png"); wm.albedo_color = Palette.col("WoodTrim") / 0.78
				wm.uv1_triplanar = true; wm.uv1_scale = Vector3(0.5, 0.5, 0.5); up.material_override = wm
				up.position = L.call(r[0] + r[2] * 0.5, r[1] + r[3] * 0.5, st * STOREY * low - 0.07); root.add_child(up)
	# yards: a wall round the well-off's, a fence round the others, open where a building or a gate meets them
	for r in rooms:
		if r[5] == "yard" and not str(r[4]).begins_with("arch"):
			for e in _edges(r, roofs):
				_fence_run(e, ty, L, b.zone, mir)
	# wings and roofs
	var wings := _wings(roofs)
	for wg in wings: _roof(wg, storeys * STOREY * low, L, b.type in THATCH_TYPES or b.zone == "poor", kinds)
	for wg in wings:   # corner posts or quoins: the walls overlap at the corners, and these cover the join
		for cn in [[wg[0], wg[1]], [wg[0] + wg[2], wg[1]], [wg[0], wg[1] + wg[3]], [wg[0] + wg[2], wg[1] + wg[3]]]:
			var sx := signf(cn[0] - (wg[0] + wg[2] * 0.5)) * (-1.0 if mir else 1.0); var sz := signf(cn[1] - (wg[1] + wg[3] * 0.5))
			for st in storeys:
				var kind: String = kinds[mini(st, kinds.size() - 1)]
				var cp := _piece("Corner_Exterior_Brick" if kind == "UnevenBrick" else "Corner_Exterior_Wood", L.call(cn[0], cn[1], st * STOREY * low), _corner_yaw(sx, sz))
				if cp: cp.scale = Vector3(1.0, low, 1.0)
	_into = null
	if b.type == "granary":
		for k in 6:
			var p := Vector2(fw * (0.15 + 0.35 * (k % 3)), fh * (0.2 if k < 3 else 0.8))
			var q: Vector3 = root.transform * L.call(p.x, p.y, -0.6)
			put("res://assets/props/fogwright/Staddle_Stone.glb", q, 0.0, 1.0, true, "fixture", "a staddle stone under the granary")
	var main: Vector2 = bdoors[i][0] if bdoors[i].size() > 0 else c
	houses.append([b.name if b.name != "" else b.type, c, main, "roof" if wings.size() > 0 else ""])
	# a stone foundation where the ground falls away below the terrace
	var lowest := level
	for k in 4:
		var u := (fw * 0.5 + 0.3) * (1 if k % 2 == 0 else -1); var v := (fh * 0.5 + 0.3) * (1 if k < 2 else -1)
		lowest = minf(lowest, _base(c + Vector2(u, v).rotated(b.a)))
	if level - lowest > 0.15:
		for r in roofs:
			var plinth := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(r[2] + 0.3, level - lowest + 0.4, r[3] + 0.3)
			plinth.mesh = bm; var pmat := StandardMaterial3D.new(); pmat.albedo_texture = load("res://assets/library/UnevenBrick_detail.png")
			pmat.albedo_color = Palette.col("UnevenBrick") / 0.78; pmat.uv1_triplanar = true; pmat.uv1_scale = Vector3(0.5, 0.5, 0.5); plinth.material_override = pmat
			plinth.position = L.call(r[0] + r[2] * 0.5, r[1] + r[3] * 0.5, -(level - lowest + 0.4) * 0.5 - 0.03)   # its top just under the floor: no flicker
			root.add_child(plinth)

## the outside parts of a room's four edges: [from (x,y), to (x,y), outward normal (x,y)], minus where another roofed room
## lies against it
func _edges(r: Array, roofs: Array) -> Array:
	var x0: float = r[0]; var y0: float = r[1]; var x1: float = r[0] + r[2]; var y1: float = r[1] + r[3]
	var sides := [[Vector2(x0, y0), Vector2(x1, y0), Vector2(0, -1)], [Vector2(x0, y1), Vector2(x1, y1), Vector2(0, 1)],
		[Vector2(x0, y0), Vector2(x0, y1), Vector2(-1, 0)], [Vector2(x1, y0), Vector2(x1, y1), Vector2(1, 0)]]
	var out := []
	for sd in sides:
		var a: Vector2 = sd[0]; var bb: Vector2 = sd[1]; var n: Vector2 = sd[2]; var horiz := n.x == 0.0
		var segs := [[a.x if horiz else a.y, bb.x if horiz else bb.y]]
		for o in roofs:
			if o == r: continue
			var line := a.y if horiz else a.x
			var o_near: float = (o[1] + o[3] if n.y < 0 else o[1]) if horiz else (o[0] + o[2] if n.x < 0 else o[0])
			if absf(o_near - line) > 0.02: continue
			var lo: float = o[0] if horiz else o[1]; var hi: float = (o[0] + o[2]) if horiz else (o[1] + o[3])
			var keep := []
			for sg in segs:
				if hi <= sg[0] or lo >= sg[1]: keep.append(sg); continue
				if lo > sg[0]: keep.append([sg[0], lo])
				if hi < sg[1]: keep.append([hi, sg[1]])
			segs = keep
		for sg in segs:
			if sg[1] - sg[0] < 0.3: continue
			out.append([Vector2(sg[0], a.y) if horiz else Vector2(a.x, sg[0]), Vector2(sg[1], a.y) if horiz else Vector2(a.x, sg[1]), n])
	return out

## the type's door or window on this edge piece, if any: [kind ("d" door, "g" gate, "o" open, "s" shop front, "w" window), width].
## A door or gate opens every piece it overlaps; a window sits in the piece its centre falls in.
func _opening(ty: Dictionary, p0: Vector2, p1: Vector2, n: Vector2) -> Array:
	var horiz := n.x == 0.0
	var line: float = p0.y if horiz else p0.x
	var lo: float = minf(p0.x, p1.x) if horiz else minf(p0.y, p1.y); var hi: float = maxf(p0.x, p1.x) if horiz else maxf(p0.y, p1.y)
	for d in ty.doors:
		if (d[2] == "h") != horiz or absf((d[1] if horiz else d[0]) - line) > 0.05: continue
		var t: float = d[0] if horiz else d[1]; var half: float = d[3] * 0.5
		if minf(hi, t + half) - maxf(lo, t - half) > 0.3: return [d[4], d[3]]
	for w in ty.windows:
		if w[3] <= 0.0 or (w[2] == "h") != horiz or absf((w[1] if horiz else w[0]) - line) > 0.05: continue
		var t: float = w[0] if horiz else w[1]
		if t >= lo - 0.01 and t <= hi + 0.01: return ["w", w[3]]
	return []

## a wall line cut into pieces round its openings: [from, to, kind ("d" door, "g"/"o"/"s" open, "w" window, "" plain), width].
## Every door gets one 2 m piece centred on it (so the door sits in the middle of its frame, never two leaves for one door);
## gates, archways and open fronts are gaps exactly their width; the rest is plain pieces of about 2 m, a window in the
## piece where the floorplan has one
func _segments(a: Vector2, bb: Vector2, n: Vector2, ty: Dictionary) -> Array:
	var horiz := n.x == 0.0
	var line: float = a.y if horiz else a.x
	var lo: float = a.x if horiz else a.y; var hi: float = bb.x if horiz else bb.y
	var at := func(t: float) -> Vector2: return Vector2(t, line) if horiz else Vector2(line, t)
	var spans := []
	for d in ty.doors:
		if (d[2] == "h") != horiz or absf((d[1] if horiz else d[0]) - line) > 0.05: continue
		var t: float = d[0] if horiz else d[1]
		if t < lo - 0.01 or t > hi + 0.01: continue
		var hw: float = 1.0 if d[4] == "d" else float(d[3]) * 0.5
		var s0 := clampf(t - hw, lo, hi); var s1 := clampf(t + hw, lo, hi)
		if d[4] == "d" and s1 - s0 < 2.0 and hi - lo >= 2.0:            # a door near a corner: its piece slides in, still 2 m
			if s0 <= lo + 0.01: s1 = lo + 2.0
			else: s0 = hi - 2.0
		spans.append([s0, s1, d[4], d[3]])
	spans.sort_custom(func(p, q): return p[0] < q[0])
	var out := []; var cur := lo
	var plain := func(from: float, to: float) -> void:
		var cnt := maxi(1, roundi((to - from) / 2.0))
		for k in cnt:
			var p0: float = from + (to - from) * k / cnt; var p1: float = from + (to - from) * (k + 1) / cnt
			var kind := ""; var wdt := 0.0
			for w in ty.windows:
				if w[3] <= 0.0 or (w[2] == "h") != horiz or absf((w[1] if horiz else w[0]) - line) > 0.05: continue
				var tw: float = w[0] if horiz else w[1]
				if tw >= p0 - 0.01 and tw <= p1 + 0.01: kind = "w"; wdt = w[3]
			out.append([at.call(p0), at.call(p1), kind, wdt])
	for sp in spans:
		var s0: float = maxf(sp[0], cur)
		if s0 - cur > 0.25: plain.call(cur, s0)
		elif s0 > cur and out.size() > 0: out[-1][1] = at.call(s0)     # a sliver: the piece before stretches over it
		else: s0 = cur
		out.append([at.call(s0), at.call(sp[1]), sp[2], sp[3]]); cur = sp[1]
	if hi - cur > 0.25: plain.call(cur, hi)
	elif hi > cur and out.size() > 0: out[-1][1] = at.call(hi)
	return out

func _wall_run(e: Array, r: Array, ty: Dictionary, storeys: int, low: float, kinds: Array, L: Callable, mir: bool, inner := false) -> void:
	var a: Vector2 = e[0]; var bb: Vector2 = e[1]; var n: Vector2 = e[2]
	var length := a.distance_to(bb); var cnt := maxi(1, roundi(length / 2.0)); var seg := length / cnt
	var nn := Vector2(-n.x if mir else n.x, n.y)
	var yaw := atan2(nn.x, nn.y)
	var front := n.y < 0 and absf(a.y) < 0.05          # the street front
	for s in storeys:
		var kind: String = "Plaster" if inner else kinds[mini(s, kinds.size() - 1)]
		var pieces := []
		if s == 0: pieces = _segments(a, bb, n, ty)
		else:
			for k in cnt:
				var wide := (k + s) % 2 == 0
				pieces.append([a.lerp(bb, float(k) / cnt), a.lerp(bb, float(k + 1) / cnt), "w" if (front or n.y > 0) else "", 1.4 if wide else 0.9])
		for pc in pieces:
			var p0: Vector2 = pc[0]; var p1: Vector2 = pc[1]; var op: String = pc[2]; var len := p0.distance_to(p1)
			if op in ["g", "o", "s"]: continue                       # a gate, an archway or an open front: a gap its own width
			var mid := (p0 + p1) * 0.5
			var pos: Vector3 = L.call(mid.x, mid.y, s * STOREY * low)
			var name := ("Wall_Plaster_Straight_Base" if s == 0 else "Wall_Plaster_Straight") if kind == "Plaster" else "Wall_%s_Straight" % kind
			var fill := ""; var frame := ""
			if op == "d": name = "Wall_%s_Door_Flat" % kind; fill = "Door_1_Flat"; frame = "DoorFrame_Flat_WoodDark"
			elif op == "w":
				name = "Wall_%s_Window_Wide_Round" % kind if pc[3] >= 1.2 else "Wall_%s_Window_Thin_Round" % kind
				fill = "Window_Wide_Round1" if pc[3] >= 1.2 else "Window_Thin_Round1"
			var sx := len / 2.0
			var piece := _piece(name, pos, yaw)
			if piece: piece.scale = Vector3(sx, low, 1.0)
			if frame != "":
				var fr := _piece(frame, pos, yaw)
				if fr: fr.scale = Vector3(sx, low, 1.0)
			if fill != "":
				var off := Vector3(-0.53, 0, 0).rotated(Vector3.UP, yaw) if fill.begins_with("Door") else Vector3.ZERO
				var f := _piece(fill, pos + off * sx, yaw)
				if f: f.scale = Vector3(sx, low, 1.0)

## the walls between two roofed rooms that share an edge: [from, to, normal] in floorplan metres
func _inner_edges(roofs: Array) -> Array:
	var out := []
	for i in roofs.size():
		var r: Array = roofs[i]
		for j in range(i + 1, roofs.size()):
			var o: Array = roofs[j]
			for side in [[r[1] + r[3], o[1], true, Vector2(0, 1)], [r[1], o[1] + o[3], true, Vector2(0, -1)], [r[0] + r[2], o[0], false, Vector2(1, 0)], [r[0], o[0] + o[2], false, Vector2(-1, 0)]]:
				if absf(float(side[0]) - float(side[1])) > 0.02: continue
				var lo: float; var hi: float
				if side[2]: lo = maxf(r[0], o[0]); hi = minf(r[0] + r[2], o[0] + o[2])
				else: lo = maxf(r[1], o[1]); hi = minf(r[1] + r[3], o[1] + o[3])
				if hi - lo < 0.3: continue
				var ln: float = side[0]
				out.append([Vector2(lo, ln) if side[2] else Vector2(ln, lo), Vector2(hi, ln) if side[2] else Vector2(ln, hi), side[3]])
	return out

func _fence_run(e: Array, ty: Dictionary, L: Callable, zone: String, mir: bool) -> void:
	var a: Vector2 = e[0]; var bb: Vector2 = e[1]; var n: Vector2 = e[2]
	for pc in _segments(a, bb, n, ty):
		if pc[2] in ["d", "g", "o", "s"]: continue                     # the gate
		var p0: Vector2 = pc[0]; var p1: Vector2 = pc[1]; var mid := (p0 + p1) * 0.5; var seg := p0.distance_to(p1)
		var yaw := atan2(-n.x if mir else n.x, n.y)
		var f := _piece_any(_fence_model(zone), L.call(mid.x, mid.y), yaw)
		if f:
			f.scale = Vector3((seg + 0.35) / 2.0, 1.0, 1.0)            # overlapping a little at the joins and corners
			_on_ground(f, seg + 0.35)

## a fence or wall piece set on the ground under it: at the drawn ground's height, tilted from one end to the other
func _on_ground(f: Node3D, length: float) -> void:
	var e0: Vector3 = f.global_transform * Vector3(-1, 0, 0); var e1: Vector3 = f.global_transform * Vector3(1, 0, 0)
	var h0 := terrain_surface(Vector2(e0.x, e0.z) + ORIGIN); var h1 := terrain_surface(Vector2(e1.x, e1.z) + ORIGIN)
	var parent_y: float = (f.get_parent() as Node3D).global_position.y
	f.position.y = (h0 + h1) * 0.5 - parent_y - 0.12
	f.rotation.z = atan2(h1 - h0, length)

## who lives there decides the fence: dry stone for the well-off, woven wattle for the poor, the kit's rails for the rest
func _fence_model(zone: String) -> String:
	match zone:
		"rich": return "res://assets/props/fogwright/Drystone_Wall.glb"
		"poor": return "res://assets/props/fogwright/Wattle_Fence.glb"
	return VILLAGE % "Prop_WoodenFence_Single"

## a model by path inside the building being built (put() places it; the builder's frame is _into)
func _piece_any(path: String, pos: Vector3, yaw: float) -> Node3D:
	var n := put(path, pos, yaw, 1.0, true, "fixture", "a yard's wall or fence")
	if n: placed[-1][1] = n.global_position          # placed holds world positions; pos was in the building's frame
	return n

## roofed rooms merged into wings: two rooms that share a whole edge become one rectangle, until none do
func _wings(roofs: Array) -> Array:
	var ws := []
	for r in roofs: ws.append([float(r[0]), float(r[1]), float(r[2]), float(r[3])])
	var merged := true
	while merged:
		merged = false
		for i in ws.size():
			for j in ws.size():
				if i == j: continue
				var p: Array = ws[i]; var q: Array = ws[j]
				var side := absf(p[0] + p[2] - q[0]) < 0.02 and absf(p[1] - q[1]) < 0.02 and absf(p[3] - q[3]) < 0.02
				var below := absf(p[1] + p[3] - q[1]) < 0.02 and absf(p[0] - q[0]) < 0.02 and absf(p[2] - q[2]) < 0.02
				if side or below:
					ws[i] = [p[0], p[1], p[2] + q[2] if side else p[2], p[3] if side else p[3] + q[3]]
					ws.remove_at(j); merged = true; break
			if merged: break
	return ws

func _roof(wg: Array, top: float, L: Callable, thatch: bool, kinds: Array) -> void:
	var ww: float = wg[2]; var dd: float = wg[3]
	var span := minf(ww, dd); var length := maxf(ww, dd)
	var S := 4 if span < 5.0 else (6 if span < 7.0 else 8)
	var best := 0; for l in ROOF_SIZES[S]: if best == 0 or absf(l - length) < absf(best - length): best = l
	var name := "Roof_RoundTiles_%dx%d" % [S, best]
	var centre: Vector3 = L.call(wg[0] + ww * 0.5, wg[1] + dd * 0.5, top)
	var along_z := ww <= dd                                        # the ridge runs along the longer side
	var yaw := 0.0 if along_z else PI / 2
	var piece := _piece(name, centre, yaw)
	if piece == null: return
	piece.scale = Vector3(span / S, span / S, length / best)
	if thatch: _thatch(piece)
	var gable := "Roof_Front_Brick%d" % S
	for sgn in [-1.0, 1.0]:
		var end: Vector3 = centre + (Vector3(0, 0, sgn * dd * 0.5) if along_z else Vector3(sgn * ww * 0.5, 0, 0))
		var gy := (0.0 if sgn > 0 else PI) if along_z else (PI / 2 if sgn > 0 else -PI / 2)
		var g := _piece(gable, end, gy)
		if g: g.scale = Vector3(span / S, span / S, 1.0)

## a roof thatched instead of tiled: the same piece with the Thatch material
func _thatch(n: Node) -> void:
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = (mi as MeshInstance3D).mesh
		for s in mesh.get_surface_count():
			var orig := mesh.surface_get_material(s)
			if orig and orig.resource_name.contains("RoundTiles"):
				(mi as MeshInstance3D).set_surface_override_material(s, Palette.material_for("Thatch", orig))

## the plot behind a house: a fence on the three sides away from it (a wall for a walled garden), a gate at the back
func _plot(pl: Dictionary) -> void:
	var c := Vector2(pl.x, pl.y); var a: float = pl.a; var hw: float = pl.w * 0.5; var hh: float = pl.h * 0.5
	var P := func(u: float, v: float) -> Vector2: return c + Vector2(u, v).rotated(a)
	var walled: bool = pl.label == "walled garden"
	var zone: String = BUILDINGS[int(pl.owner)].zone
	var sides := [[P.call(-hw, -hh), P.call(-hw, hh)], [P.call(-hw, hh), P.call(hw, hh)], [P.call(hw, hh), P.call(hw, -hh)]]
	for si in sides.size():
		var e: Array = sides[si]; var p0: Vector2 = e[0]; var p1: Vector2 = e[1]; var length := p0.distance_to(p1); var cnt := maxi(1, roundi(length / 2.0))
		for k in cnt:
			var q0 := p0.lerp(p1, float(k) / cnt); var q1 := p0.lerp(p1, float(k + 1) / cnt); var mid := (q0 + q1) * 0.5
			var yaw := -atan2(q1.y - q0.y, q1.x - q0.x)
			var gate := si == 1 and k == cnt / 2                  # the back gate
			if gate and not walled: continue
			var path := "res://assets/props/fogwright/Garden_Gate.glb" if gate else _fence_model(zone)
			var len := q0.distance_to(q1)
			var f := put(path, W(mid, height(mid)), yaw, 1.0, true, "fixture", "the plot's gate" if gate else "the plot's wall or fence")
			if f:
				f.scale = Vector3((len + (0.0 if gate else 0.35)) / (2.06 if gate else 2.0), 1.0, 1.0)   # a little overlap closes the corners
				_on_ground(f, len)                            # on the drawn ground, tilted with the slope

func _in_roofed(p: Vector2, grow := 0.0) -> bool:
	for r in roofed:
		var q: Vector2 = (p - r[0]).rotated(-r[2]); var e: Vector2 = r[1]
		if absf(q.x) < e.x + grow and absf(q.y) < e.y + grow: return true
	return false

func _nearest_path_point(p: Vector2) -> Vector2:
	var best := p; var bd := INF
	for path in PATHS:
		var pts: Array = path[0]
		for i in pts.size() - 1:
			var a: Vector2 = pts[i]; var b: Vector2 = pts[i + 1]
			var t := clampf((p - a).dot(b - a) / (b - a).length_squared(), 0.0, 1.0); var q := a + (b - a) * t
			if p.distance_to(q) < bd: bd = p.distance_to(q); best = q
	return best

func _well() -> void:   # the village well in the square (the Modular Village Pack's, in our palette), solid
	put("res://assets/props/village2/Prop_Well_1.glb", W(WELL, height(WELL)), 0.3, 1.65, true, "fixture", "the village well, the old spring")

# ---------------------------------------------------------------- the harbour: sea wall, breakwater, lighthouse, pier, boats
## a stone causeway along a smooth curve through the points: a level top and sloping sides down to the seabed, one mesh
## (the breakwater out to the lighthouse, the sea wall), with a collider from the same mesh
func _stone_run(pts: Array, width: float, top: float) -> void:
	var curve := Curve2D.new()
	for i in pts.size():
		var p: Vector2 = pts[i]
		var prev: Vector2 = pts[max(i - 1, 0)]; var next: Vector2 = pts[min(i + 1, pts.size() - 1)]
		var tan := (next - prev) * 0.3
		curve.add_point(p, -tan, tan)
	curve.bake_interval = 0.8
	var baked := curve.get_baked_points()
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var hw := width * 0.5; var foot := hw + 0.9          # the sides batter outward toward the bottom
	var along := 0.0
	for i in baked.size():
		var p: Vector2 = baked[i]; var d: Vector2 = (baked[min(i + 1, baked.size() - 1)] - baked[max(i - 1, 0)]).normalized()
		var side := Vector2(-d.y, d.x)
		if i > 0: along += p.distance_to(baked[i - 1])
		var low := minf(_base(p), 0.0) - 2.0
		var tp := top                                       # where it runs over the shore, its top stays above the ground
		for s_ in [-hw, 0.0, hw]: tp = maxf(tp, terrain_surface(p + side * s_) + 0.12)
		for v in [[-foot, low], [-hw, tp], [hw, tp], [foot, low]]:   # a cross-section: bottom left, top left, top right, bottom right
			var q: Vector2 = p + side * float(v[0])
			st.set_uv(Vector2(along, float(v[0]) + (top - float(v[1]))) * 0.35)
			st.add_vertex(W(q, float(v[1])))
	for i in baked.size() - 1:
		var a := i * 4
		for k in 3:
			st.add_index(a + k); st.add_index(a + 4 + k); st.add_index(a + k + 1)
			st.add_index(a + k + 1); st.add_index(a + 4 + k); st.add_index(a + 5 + k)
	st.generate_normals()
	var mi := MeshInstance3D.new(); mi.mesh = st.commit()
	var m := StandardMaterial3D.new(); m.albedo_texture = load("res://assets/library/RockTrim_detail.png")
	m.albedo_color = Palette.col("RockTrim") / 0.78; m.cull_mode = BaseMaterial3D.CULL_DISABLED; mi.material_override = m
	add_child(mi); mi.create_trimesh_collision()

func _harbour() -> void:
	_stone_run([Vector2(80, 82), Vector2(92, 76), Vector2(100, 70), Vector2(106, 62), Vector2(116, 64), Vector2(126, 70), Vector2(131, 78)], 2.4, 0.9)   # the sea wall running on as the breakwater, one causeway
	var lh := Vector2(132.5, 80.5)                                                                      # the lighthouse
	put("res://assets/props/fogwright/Lighthouse.glb", W(lh, 0.8), PI * 0.7, 1.0, true, "fixture", "the harbour master's lighthouse")
	var lamp := OmniLight3D.new(); lamp.light_color = Color(1, 0.8, 0.5); lamp.light_energy = 2.0; lamp.omni_range = 18
	lamp.position = W(lh, 11.2); add_child(lamp)
	# the pier: a T of planks on posts, its deck above the water
	var deck_y := 1.0
	_pier_run(Vector2(87.5, 80), Vector2(87.5, 100), deck_y); _pier_run(Vector2(78, 100.5), Vector2(106, 100.5), deck_y)
	_boat(Vector2(96, 92), -0.3, 7.0); _boat(Vector2(76, 94), 0.4, 5.5); _boat(Vector2(117.5, 100.5), 0.0, 16.0, true)   # moored just off the pier's end

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

## a boat on the water: the sailboat remade from the reference (tools/blender/make_boat.py), its hull `length` metres
## long; the last ship is, for now, the same boat built larger
func _boat(c: Vector2, a: float, length: float, ship := false) -> void:
	if ship:   # the trader's brig from Hollin's Cross (made with Meshy, tools/blender/import_ship.py): its keel in the water
		put("res://assets/props/fogwright/Last_Ship.glb", W(c, 0.0), -a, 1.0, true, "fixture", "the last ship out")
		return
	put("res://assets/props/fogwright/Sailboat.glb", W(c, 0.25 * length / 6.0), -a, length / 6.0, ship, "fixture", "the last ship out" if ship else "a fishing boat at anchor")   # floating: the waterline 0.25 below its origin, under its bottom boards

# ---------------------------------------------------------------- the palisade and its north gate
func _palisade() -> void:
	var runs := []
	for wl in PLAN.walls:
		if wl.name != "palisade": continue
		var run := []; for q in wl.pts: run.append(Vector2(q[0], q[1]))
		runs.append(run)
	var cm := CylinderMesh.new(); cm.top_radius = 0.17; cm.bottom_radius = 0.2; cm.height = 3.2; cm.radial_segments = 7
	var mat := StandardMaterial3D.new(); mat.albedo_texture = load("res://assets/library/WoodTrim_detail.png")
	mat.albedo_color = Palette.col("WoodTrim").darkened(0.15) / 0.78; mat.uv1_scale = Vector3(1.0, 2.0, 1.0); cm.material = mat
	var tip := CylinderMesh.new(); tip.top_radius = 0.0; tip.bottom_radius = 0.17; tip.height = 0.45; tip.radial_segments = 7; tip.material = mat   # sharpened tops
	var tips := []
	var xf := []
	for run in runs:
		for i in run.size() - 1:
			var a: Vector2 = run[i]; var b: Vector2 = run[i + 1]; var n := int(a.distance_to(b) / 0.42)
			for k in n:
				var p := a.lerp(b, float(k) / n)
				var t3 := Transform3D(Basis(Vector3(rng.randf_range(-1, 1), 0, rng.randf_range(-1, 1)).normalized(), rng.randf_range(0.0, 0.05)), W(p, height(p) + 1.4 + rng.randf_range(-0.2, 0.2)))
				xf.append(t3); tips.append(t3 * Transform3D(Basis(), Vector3(0, 1.6 + 0.22, 0)))
			var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(a.distance_to(b), 3.0, 0.5)
			col.shape = bs; body.add_child(col); body.position = W((a + b) * 0.5, height((a + b) * 0.5) + 1.4); body.rotation.y = -atan2(b.y - a.y, b.x - a.x); add_child(body)
	var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = cm; mm.instance_count = xf.size()
	for i in xf.size(): mm.set_instance_transform(i, xf[i])
	var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm; add_child(mmi)
	var tm := MultiMesh.new(); tm.transform_format = MultiMesh.TRANSFORM_3D; tm.mesh = tip; tm.instance_count = tips.size()
	for i in tips.size(): tm.set_instance_transform(i, tips[i])
	var tmi := MultiMeshInstance3D.new(); tmi.multimesh = tm; add_child(tmi)
	# the gate: timber towers with lookouts, a lintel over the 7 m opening, the leaves standing open (tools/blender/make_props.py)
	var gp := Vector2(62, 4.6)
	put("res://assets/props/fogwright/Village_Gate.glb", W(gp, height(gp) - 0.05), 0.0, 1.0, true, "fixture", "the village gate, open by day")


# ---------------------------------------------------------------- the field, the plots and the woods (batched)
func scatter(path: String, points: Array, scale_range := Vector2(0.9, 1.1), ground := ["grass"]) -> void:
	var kept := []
	for p in points:   # flora only grows on the ground it belongs on: never on paths, the plaza, terraces or stone
		if ground.has(ground_at(Vector2(p.x, p.z) + ORIGIN)): kept.append(p)
	points = kept
	for p in points: placed.append([path.get_file().get_basename(), p, 0.3, "flora", "scattered"])
	var s: PackedScene = load(path)
	if s == null or points.is_empty(): return
	var proto: Node3D = s.instantiate()
	for mi in proto.find_children("*", "MeshInstance3D", true, false):
		var src := mi as MeshInstance3D
		var mesh: Mesh = src.mesh
		for si in mesh.get_surface_count():   # palette-named materials (our own models) get the palette's colours
			var orig := mesh.surface_get_material(si)
			if orig and Palette.material_for(orig.resource_name, orig):
				if mesh == src.mesh: mesh = src.mesh.duplicate()
				mesh.surface_set_material(si, Palette.material_for(orig.resource_name, orig))
		var centre := Vector3.ZERO                      # the batch sits at its points' centre: draw distances are measured from there
		for pt in points: centre += pt
		centre /= points.size()
		var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = mesh; mm.instance_count = points.size()
		for i in points.size():
			var t := Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * rng.randf_range(scale_range.x, scale_range.y)), points[i] - centre)
			mm.set_instance_transform(i, t * src.transform)
		var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm; mmi.position = centre; add_child(mmi)
	proto.free()

func _ground_pts(n: int, inside: Callable) -> Array:
	var out := []
	var tries := 0
	while out.size() < n and tries < n * 30:
		tries += 1
		var p := Vector2(rng.randf_range(-MARGIN, 140 + MARGIN), rng.randf_range(-MARGIN, 110 + MARGIN))
		if inside.call(p): out.append(W(p, height(p)))
	return out

## the village's ground, where no woods grow: inside the palisade (closed down to the shore), the shore itself, and the
## old oval clearing
const VILLAGE_LINE := [Vector2(20, 92), Vector2(8, 70), Vector2(6, 40), Vector2(10, 8), Vector2(40, 6), Vector2(56, 4), Vector2(68, 4),
	Vector2(92, 6), Vector2(114, 13), Vector2(121, 40), Vector2(126, 56), Vector2(90, 84), Vector2(55, 110)]
func _in_clearing(p: Vector2) -> bool:
	return Geometry2D.is_point_in_polygon(p, PackedVector2Array(VILLAGE_LINE)) or pow((p.x - 62) / 54.0, 2) + pow((p.y - 50) / 44.0, 2) < 1.0 \
		or (p.x > 50 and p.y > 76) or (p.x > 95 and p.y > 46)

func _near_built(p: Vector2, r := 2.5) -> bool:
	for pad in pads:
		var q: Vector2 = (p - pad[0]).rotated(-pad[2]); var e: Vector2 = pad[1]
		if absf(q.x) < e.x + r and absf(q.y) < e.y + r: return true
	return p.distance_to(_nearest_path_point(p)) < 2.6

func _field() -> void:
	var wheat := []
	for i in 28: for j in 24:
		var p := Vector2(15 + i * 0.8 + rng.randf_range(-0.2, 0.2), 15 + j * 0.8 + rng.randf_range(-0.2, 0.2)); wheat.append(W(p, height(p)))
	scatter(NATURE % "Grass_Wispy_Tall", wheat, Vector2(1.1, 1.5), ["field"])
	for edge in [[Vector2(14, 14), Vector2(37, 14)], [Vector2(37, 14), Vector2(37, 34)], [Vector2(37, 34), Vector2(14, 34)], [Vector2(14, 34), Vector2(14, 14)]]:
		var a: Vector2 = edge[0]; var b: Vector2 = edge[1]; var n := int(a.distance_to(b) / 2.0)
		for k in n:
			var p := a.lerp(b, (k + 0.5) / n)
			if absf(p.x - 37) < 0.1 and absf(p.y - 27) < 2.5: continue        # the field gate, where the field lane comes in
			put(VILLAGE % "Prop_WoodenFence_Single", W(p, height(p)), -atan2(b.y - a.y, b.x - a.x), 1.0, true, "fixture", "the field's fence")
	var plots := []
	for i in 5: for j in 9:
		var p := Vector2(17.5 + i * 3.0, 39.5 + j * 0.75); plots.append(W(p, height(p)))
	scatter(NATURE % "Plant_1", plots, Vector2(0.5, 0.7), ["plots"])

## how far out of the clearing a point is: 0 at its edge, growing outward (the clearing is an ellipse, plus the shore)
## the way big games draw forests: the trees in 24 m blocks, each block one batch per model that the engine skips when
## it is off screen, and stops drawing beyond a distance (the haze hides where); thousands of trees cost a few batches
func _scatter_chunked(path: String, points: Array, scale_range: Vector2, cell: float, draw_to: float) -> void:
	var blocks := {}
	for pt in points:
		var k := Vector2i(floori(pt.x / cell), floori(pt.z / cell))
		if not blocks.has(k): blocks[k] = []
		blocks[k].append(pt)
	for k in blocks:
		var before := get_child_count()
		scatter(path, blocks[k], scale_range, ["grass", "woods"])
		for i in range(before, get_child_count()):
			var mmi := get_child(i) as MultiMeshInstance3D
			if mmi: mmi.visibility_range_end = draw_to; mmi.visibility_range_end_margin = 8.0

func _palisade_dist(p: Vector2) -> float:   # how far from the palisade
	var best := INF
	for wl in PLAN.walls:
		if wl.name != "palisade": continue
		for i in wl.pts.size() - 1:
			var a := Vector2(wl.pts[i][0], wl.pts[i][1]); var b := Vector2(wl.pts[i + 1][0], wl.pts[i + 1][1])
			var t := clampf((p - a).dot(b - a) / (b - a).length_squared(), 0.0, 1.0); best = minf(best, p.distance_to(a + (b - a) * t))
	return best

func _woods_depth(p: Vector2) -> float:
	if _in_clearing(p): return -1.0
	return (sqrt(pow((p.x - 62) / 54.0, 2) + pow((p.y - 50) / 44.0, 2)) - 1.0) * 49.0

## the woods: the wall of the world beyond the palisade. A dense band of cheap low-poly trees (60-130 triangles) packed
## 2.4 m apart near the clearing, thinner beyond, with the kit's detailed trees only along the edge where they are seen
## up close; ferns between them; solid trunks, so nobody walks out
func _woods() -> void:
	var cheap := {}; var hero := {}
	var gr := RandomNumberGenerator.new(); gr.seed = 4242
	for pass_ in [[2.4, 0.0, 22.0], [3.6, 22.0, 999.0]]:   # spacing, from depth, to depth
		var sp: float = pass_[0]
		var y := -MARGIN
		while y < 110 + MARGIN:
			var x := -MARGIN
			while x < 140 + MARGIN:
				var p := Vector2(x + gr.randf_range(-sp * 0.4, sp * 0.4), y + gr.randf_range(-sp * 0.4, sp * 0.4))
				var dp := _woods_depth(p)
				if dp >= pass_[1] and dp < pass_[2] and _coast_signed(p) > 4.0 and _path_dist(p) > 1.5 and _palisade_dist(p) > 3.2:   # never on the road out, never against the palisade
					var at := W(p, height(p))
					if dp < 4.0 and gr.randf() < 0.35:          # the edge: the kit's detailed trees, seen up close
						var kind := ("CommonTree_%d" % (gr.randi() % 5 + 1)) if gr.randf() < 0.6 else ("Pine_%d" % (gr.randi() % 5 + 1))
						if not hero.has(kind): hero[kind] = []
						hero[kind].append(at)
					else:
						var kind: String = ["Forest_Pine_1", "Forest_Pine_2", "Forest_Broadleaf_1", "Forest_Broadleaf_2"][gr.randi() % 4]
						if not cheap.has(kind): cheap[kind] = []
						cheap[kind].append(at)
					if dp < 22.0:
						trees.append([at, 1.12])                # its crown's shade is baked onto the ground
					if dp < 10.0:                               # the trunks nearest the village are solid
						var body := StaticBody3D.new(); body.collision_layer = 2; body.collision_mask = 0
						var col := CollisionShape3D.new(); var cyl := CylinderShape3D.new(); cyl.radius = 0.4; cyl.height = 4.0; col.shape = cyl
						body.add_child(col); body.position = at + Vector3(0, 2.0, 0); add_child(body)
				x += sp
			y += sp
	for kind in hero: _scatter_chunked(NATURE % kind, hero[kind], Vector2(0.95, 1.35), 24.0, 70.0)
	for kind in cheap: _scatter_chunked("res://assets/props/fogwright/%s.glb" % kind, cheap[kind], Vector2(0.85, 1.3), 24.0, 120.0)
	var ferns := _ground_pts(700, func(p): return _woods_depth(p) >= 0.0 and _woods_depth(p) < 25.0 and _coast_signed(p) > 4.0)
	_scatter_chunked(NATURE % "Fern_1", ferns, Vector2(0.9, 1.3), 24.0, 45.0)
	scatter(NATURE % "Grass_Common_Short", _ground_pts(1400, func(p): return _coast_signed(p) > 5.0 and not _near_built(p) and not (p.x > 14 and p.x < 37 and p.y > 14 and p.y < 47)))
	scatter(NATURE % "Flower_3_Group", _ground_pts(140, func(p): return _in_clearing(p) and _coast_signed(p) > 6.0 and not _near_built(p, 1.5)), Vector2(0.28, 0.4))
	for i in 14:
		var p := Vector2(rng.randf_range(60, 130), rng.randf_range(70, 105))
		if _coast_signed(p) < -1.0 and _coast_signed(p) > -9.0: put(NATURE % ("Rock_Medium_%d" % (i % 3 + 1)), W(p, height(p)), rng.randf() * TAU, rng.randf_range(1.2, 2.2), true, "fixture", "rocks in the shallows")

# ---------------------------------------------------------------- life: the plan's doodads, each with its purpose
const DOCK := "res://assets/props/docks/%s.glb"
## kind -> model, scale, extra height (for things hung on walls or posts), solid: godot/data/doodad_models.json, shared with
## the plan (which reserves each prop's real size, measured in godot/data/model_sizes.json)
var DOODAD_MODELS := {}
var doodad_nodes := []   # [node, kind, purpose], for the collision check

func _doodads() -> void:
	DOODAD_MODELS = JSON.parse_string(FileAccess.get_file_as_string("res://data/doodad_models.json"))
	for dd in PLAN.doodads:
		var md: Dictionary = DOODAD_MODELS.get(dd.kind, {})
		if md.is_empty(): push_warning("no model for " + dd.kind); continue
		var m := [md.model, md.scale, md.lift, md.solid]
		var p := Vector2(dd.x, dd.y)
		var owner: int = int(dd.owner)
		# hung on a wall or post, or standing inside its own open workshop: a fixture, not clutter in the way
		var role := "fixture" if dd.mounted or (owner >= 0 and _in_roofed(p, -0.1)) else "clutter"
		var y: float = (1.12 if _on_pier(p) else height(p)) + float(m[2])   # on the pier's planks, or on the ground

		var yaw := -float(dd.a) + (PI / 2.0 if dd.get("turn", false) else 0.0) + deg_to_rad(float(dd.get("spin", 0)))   # turned to fit its spot, or faced by hand
		var n := put(m[0], W(p, y), yaw, m[1], m[3], role, dd.purpose)
		if n == null: continue
		if not dd.mounted and not dd.kind in ["fruit tree", "flower bed"]: doodad_nodes.append([n, dd.kind, dd.purpose])
		if dd.kind == "boat hull":   # a hull, half built, on its trestles
			put(DOCK % "Boat_B_1", W(p, y + 0.45), yaw, 0.7, false, "fixture", "the hull on its trestles")
		if dd.kind == "forge":   # the fire: the smithy's main light (few windows, so the smith can judge the iron's colour)
			var fire := OmniLight3D.new(); fire.light_color = Color(1.0, 0.55, 0.25); fire.light_energy = 1.6; fire.omni_range = 6.0
			fire.position = W(p, y + 1.1); add_child(fire)
		if dd.kind == "chopping block":   # beat B: the first weapon waits here
			put(PROPS % "Axe_Bronze", W(p, y + 0.62), yaw + 0.6, 1.0, false, "fixture", "the hatchet in the chopping block: the first weapon")

# ---------------------------------------------------------------- late afternoon
func _light() -> void:
	var sun: DirectionalLight3D = get_parent().get_node_or_null("Sun")
	if sun:
		sun.rotation_degrees = Vector3(-17, -62, 0); sun.light_color = Color(1.0, 0.8, 0.58); sun.light_energy = 1.05
		sun.directional_shadow_max_distance = 30.0
		sun.shadow_enabled = false          # baked; F2 turns on live shadows for characters
	var env: Environment = get_parent().get_node("WorldEnvironment").environment
	env.tonemap_exposure = 0.9; env.ambient_light_energy = 0.45
	env.fog_enabled = true; env.fog_mode = Environment.FOG_MODE_DEPTH; env.fog_light_color = Color(0.72, 0.75, 0.74)
	env.fog_depth_begin = 30.0; env.fog_depth_end = 150.0; env.fog_depth_curve = 1.4; env.fog_density = 0.85; env.fog_sky_affect = 0.2   # the woods fade into haze; the village stays clear
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
	# the roads meet at the well: villagers walk round it on a ring, never through it
	var ring := []
	for k in 10: ring.append(add.call(WELL + Vector2(3.2, 0).rotated(k * TAU / 10.0)))
	for k in 10:
		var a_: int = ring[k]; var b_: int = ring[(k + 1) % 10]
		graph[a_][1].append(b_); graph[b_][1].append(a_)
	for ri in runs.size():
		var run: Array = runs[ri].duplicate()
		for pi in run.size():
			var p: Vector2 = run[pi]
			if p.distance_to(WELL) < 3.0:   # a point at the well moves out to the nearest spot on the ring
				var best: Vector2 = graph[ring[0]][0]
				for r_ in ring: if p.distance_to(graph[r_][0]) < p.distance_to(best): best = graph[r_][0]
				run[pi] = best
		runs[ri] = run
	for run in runs:
		var prev := -1
		for p in run:
			var id: int = add.call(p)
			if prev >= 0 and not (graph[prev][1] as Array).has(id): graph[prev][1].append(id); graph[id][1].append(prev)
			prev = id
	for g in [WELL + Vector2(3.2, 0), Vector2(87.5, 99), Vector2(96, 100.5)] + bdoors.reduce(func(acc, ds): return acc + ds, []):
		var k: String = key.call(g)
		if ids.has(k) and not GOALS.has(ids[k]): GOALS.append(ids[k])

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
	var fl := Node.new(); fl.set_script(load("res://scripts/foot_lift.gd")); pl.add_child(fl)
	fl.setup(model, func(p: Vector3) -> float:   # the player can stand on anything solid: ask the physics world
		var q := PhysicsRayQueryParameters3D.create(p + Vector3(0, 0.6, 0), p - Vector3(0, 1.0, 0), 1)
		q.exclude = [pl.get_rid()]
		var hit := get_world_3d().direct_space_state.intersect_ray(q)
		return hit.position.y if not hit.is_empty() else -1000.0)
	(pl as CollisionObject3D).collision_mask = 1 | 2

# ---------------------------------------------------------------- shadows, baked once (the WoW way)
const SHADE := 0.62    # how dark the ground is in shadow
var _x0 := -MARGIN
var _y0 := -MARGIN
var _nx := int(140 + 2 * MARGIN)
var _ny := int(110 + 2 * MARGIN)

func shade(p: Vector2) -> float:   # the baked light at a plan point (1 before the bake)
	if shade_grid.is_empty(): return 1.0
	var i := clampi(int((p.x - _x0) * TEXELS), 0, _nx * TEXELS - 1); var j := clampi(int((p.y - _y0) * TEXELS), 0, _ny * TEXELS - 1)
	return shade_grid[j * _nx * TEXELS + i]

const TEXELS := 2                  # light-map texels per metre
var light_tex: ImageTexture        # the baked light: sun shadows, tree shade and ambient occlusion, white where lit

func _light_uv(p: Vector2) -> Vector2:   # plan metres to the light map
	return (p - Vector2(_x0, _y0)) / Vector2(_nx, _ny)

## the ground's shader (shaders/ground.gdshader): grass, and the paths painted in from the plan's path mask
func _ground_shader() -> ShaderMaterial:
	var m := ShaderMaterial.new(); m.shader = load("res://shaders/ground.gdshader")
	if light_tex: m.set_shader_parameter("light_map", light_tex)
	m.set_shader_parameter("path_mask", load("res://data/farhallow_paths.png"))
	m.set_shader_parameter("grass_detail", load("res://assets/library/Grass_detail.png"))
	m.set_shader_parameter("path_detail", load("res://assets/library/Path_detail.png"))
	var c: Color = Palette.col("path") / 0.8
	m.set_shader_parameter("path_col", Vector3(c.r, c.g, c.b))
	return m

func _ground_material(detail: String) -> StandardMaterial3D:
	var m := StandardMaterial3D.new(); m.vertex_color_use_as_albedo = true; m.roughness = 1.0
	if light_tex: m.albedo_texture = light_tex
	m.detail_enabled = true; m.detail_albedo = load("res://assets/library/%s_detail.png" % detail)
	m.detail_uv_layer = BaseMaterial3D.DETAIL_UV_2; m.detail_blend_mode = BaseMaterial3D.BLEND_MODE_MUL
	return m

## baked once at load, the WoW way: a ray toward the sun from every texel of the village (shadow or not), soft ovals
## under tree crowns, and near buildings and props a few short rays round the sky (how much of it walls and things hide:
## the ground darkens where it meets them, so nothing looks pasted on)
func _bake_when_ready() -> void:
	await get_tree().physics_frame
	await get_tree().physics_frame
	var sun: DirectionalLight3D = get_parent().get_node("Sun")
	var travel := -sun.global_transform.basis.z         # the direction the sunlight travels
	var to_sun := -travel
	var space := get_world_3d().direct_space_state
	var W_ := _nx * TEXELS; var H_ := _ny * TEXELS; var t0 := Time.get_ticks_msec()
	var raw := PackedFloat32Array(); raw.resize(W_ * H_); raw.fill(1.0)
	var q := PhysicsRayQueryParameters3D.new(); q.collision_mask = 1
	var near := {}                                      # props, fences and fixtures (not plants), by 2 m cell: where to bake occlusion
	for it in placed:
		if it[3] == "flora": continue
		var np := Vector2(it[1].x, it[1].z) + ORIGIN
		near[Vector2i(floori(np.x / 2.0), floori(np.y / 2.0))] = true
	var sky := []
	for k in 8: sky.append(Vector3(cos(k * TAU / 8.0), 0.85, sin(k * TAU / 8.0)).normalized())
	for j in H_:
		for i in W_:
			var p := Vector2(_x0 + (i + 0.5) / TEXELS, _y0 + (j + 0.5) / TEXELS)
			if p.x < -6 or p.x > 146 or p.y < -6 or p.y > 112 or _coast_signed(p) < -2.0: continue
			var from := W(p, terrain_surface(p) + 0.15)
			var light := 1.0
			q.from = from; q.to = from + to_sun * 70.0
			if not space.intersect_ray(q).is_empty(): light = SHADE
			var close := _in_pad(p, 3.0)
			if not close:
				var cell := Vector2i(floori(p.x / 2.0), floori(p.y / 2.0))
				for dj in [-1, 0, 1]:
					for di in [-1, 0, 1]:
						if near.has(cell + Vector2i(di, dj)): close = true
			if close:                                   # ambient occlusion: how much of the sky is hidden
				var hidden := 0
				for d in sky:
					q.from = from; q.to = from + d * 2.5
					if not space.intersect_ray(q).is_empty(): hidden += 1
				light *= 1.0 - 0.5 * hidden / 8.0
			raw[j * W_ + i] = light
	var horiz := Vector2(travel.x, travel.z).normalized(); var stretch := 1.0 / maxf(0.2, -travel.y)
	for t in trees:                                     # tree crowns: a soft oval along the light
		var base: Vector3 = t[0]; var sc: float = t[1]; var top: Vector3 = base + Vector3(0, 4.0 * sc, 0)
		var hit: Vector3 = top + travel * ((top.y - base.y) / -travel.y)
		var c := Vector2(hit.x, hit.z) + Vector2(ORIGIN.x, ORIGIN.y)
		var R := int(ceil(2.0 * sc * stretch * TEXELS)) + 1
		for dj in range(-R, R + 1):
			for di in range(-R, R + 1):
				var off := Vector2(di, dj) / float(TEXELS); var along := off.dot(horiz) / stretch; var across := off.dot(horiz.orthogonal())
				if along * along + across * across < pow(2.0 * sc, 2):
					var ii := int((c.x - _x0) * TEXELS) + di; var jj := int((c.y - _y0) * TEXELS) + dj
					if ii >= 0 and jj >= 0 and ii < W_ and jj < H_: raw[jj * W_ + ii] = minf(raw[jj * W_ + ii], 0.72)
	var img := Image.create(W_, H_, false, Image.FORMAT_L8)   # soften the edges a little
	for j in H_:
		for i in W_:
			var acc := 0.0; var n := 0
			for dj in [-1, 0, 1]:
				for di in [-1, 0, 1]:
					var ii: int = i + di; var jj: int = j + dj
					if ii >= 0 and jj >= 0 and ii < W_ and jj < H_: acc += raw[jj * W_ + ii]; n += 1
			var v := acc / n
			img.set_pixel(i, j, Color(v, v, v))
	light_tex = ImageTexture.create_from_image(img)
	print("baked the light in %d ms" % (Time.get_ticks_msec() - t0))
	if OS.get_cmdline_user_args().has("dump_light"): img.save_png("user://light.png")
	shade_grid = raw                                    # (kept for anything still asking shade())
	get_node("Terrain").queue_free()
	for m in get_tree().get_nodes_in_group("path_mesh"): m.queue_free()
	path_surfaces.clear()
	await get_tree().process_frame
	_terrain()
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


# ---------------------------------------------------------------- what the ground is, and the city-planning check
func _in_pad(p: Vector2, grow := 0.0, only_buildings := false) -> bool:
	for k in pads.size():
		if only_buildings and k >= BUILDINGS.size(): continue
		var pad: Array = pads[k]
		var q: Vector2 = (p - pad[0]).rotated(-pad[2]); var e: Vector2 = pad[1]
		if absf(q.x) < e.x + grow and absf(q.y) < e.y + grow: return true
	return false

func _path_dist(p: Vector2) -> float:   # how far outside the nearest path's edge (negative: on it)
	var best := INF
	for path in PATHS:
		var pts: Array = path[0]; var hw: float = path[1] * 0.5
		for i in pts.size() - 1:
			var a: Vector2 = pts[i]; var b: Vector2 = pts[i + 1]
			var t := clampf((p - a).dot(b - a) / (b - a).length_squared(), 0.0, 1.0)
			best = minf(best, p.distance_to(a + (b - a) * t) - hw)
	return best

## the kind of ground at a plan point: sea, beach, path, plaza, building, field, plots, woods or grass
func ground_at(p: Vector2) -> String:
	if _on_pier(p): return "pier"
	var c := _coast_signed(p)
	if c < 0.0: return "sea"
	if c < 6.5: return "beach"
	if _in_roofed(p, 0.3): return "building"
	if p.distance_to(WELL) < 8.2: return "plaza"
	if _path_dist(p) < 0.4: return "path"
	if p.x > 14 and p.x < 37 and p.y > 14 and p.y < 34: return "field"
	if p.x > 16 and p.x < 30 and p.y > 38 and p.y < 46: return "plots"
	if not _in_clearing(p): return "woods"
	return "grass"

## the city-planning check: every clutter prop has a purpose, stands on sensible ground, keeps paths and doorways clear;
## every flora instance grows on open ground; every building has a roof. Returns the problems found.
func check_plan() -> Array:
	var issues := check_paths() + check_ground() + check_clip() + check_roofs()
	var doors := []
	for h in houses:
		if h[3] == "": issues.append("ROOF   %s at %s has no roof" % [h[0], h[1]])
	for ds in bdoors: doors.append_array(ds)
	for it in placed:
		var p := Vector2(it[1].x, it[1].z) + ORIGIN; var r: float = it[2]; var ground := ground_at(p)
		match it[3]:
			"flora":
				if not ["grass", "woods", "field", "plots"].has(ground): issues.append("GROUND %s on %s at %s" % [it[0], ground, p.round()])
			"clutter":
				if it[4] == "": issues.append("WHY    %s at %s has no purpose" % [it[0], p.round()])
				if ground == "sea": issues.append("GROUND %s in the sea at %s" % [it[0], p.round()])
				if ground != "plaza" and _path_dist(p) < r - 0.15: issues.append("PATH   %s stands in a path at %s" % [it[0], p.round()])
				for d in doors:
					if p.distance_to(d) < 1.3 + r: issues.append("DOOR   %s blocks a doorway at %s" % [it[0], p.round()])
				if _in_roofed(p, -0.2): issues.append("INSIDE %s is inside a building at %s" % [it[0], p.round()])
	return issues


# ---------------------------------------------------------------- the path check (part of the city-planning skill)
## places a path may lead to: doors, the plaza, the gate, the pier's head, the field's gate, or another path
func _destinations() -> Array:
	var out := [[WELL, "the square", 8.6], [Vector2(62, -20), "beyond the gate", 2.0], [Vector2(87, 81), "the pier's head", 2.5]]
	for d in PLAN.destinations: out.append([Vector2(d.x, d.y), "the " + d.name, 3.0])
	for t in PLAN.trails: out.append([Vector2(t.pts[0][0], t.pts[0][1]), t.purpose, 1.0])   # a trail starts at its door or gate
	for k in houses.size():
		for d in bdoors[k]: out.append([d, "a door of the %s at %s" % [houses[k][0], (houses[k][1] as Vector2).round()], 3.0])
	return out

func _path_points(path: Array, step := 0.5) -> Array:
	var pts: Array = path[0]; var out := []
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]; var b: Vector2 = pts[i + 1]; var n := maxi(1, int(a.distance_to(b) / step))
		for k in n: out.append(a.lerp(b, float(k) / n))
	out.append(pts[-1]); return out

func check_paths() -> Array:
	var issues := []
	var dests := _destinations()
	for pi in PATHS.size():
		var path: Array = PATHS[pi]; var pts: Array = path[0]; var name := "path %d (%s)" % [pi, path[2] if path.size() > 2 else "?"]
		if path.size() < 3 or path[2] == "": issues.append("PATH-WHY  %s has no purpose" % name)
		for end in [pts[0], pts[-1]]:   # (1) does it lead somewhere: both ends at a destination or on another path
			var ok := false
			for d in dests:
				if (end as Vector2).distance_to(d[0]) <= d[2]: ok = true
			for pj in PATHS.size():
				if pj == pi: continue
				for q in _path_points(PATHS[pj]):
					if (end as Vector2).distance_to(q) < (PATHS[pj][1] as float) * 0.5 + 0.5: ok = true
			if not ok: issues.append("PATH-END  %s ends at %s, which leads nowhere" % [name, (end as Vector2).round()])
		var hw: float = path[1] * 0.5
		for q in _path_points(path):   # (2) does it run into a building other than at its door
			for k in houses.size():
				var pad: Array = pads[k]; var r: Vector2 = ((q as Vector2) - pad[0]).rotated(-pad[2]); var e: Vector2 = pad[1]
				var near_door := false
				for d in bdoors[k]: if (q as Vector2).distance_to(d) <= 2.6: near_door = true
				if path.size() > 3 and (q as Vector2).distance_to(pts[0]) <= 2.6: near_door = true   # a trail leaving its own back door
				if absf(r.x) < e.x + hw * 0.6 and absf(r.y) < e.y + hw * 0.6 and not near_door:
					issues.append("PATH-WALL %s runs into the %s at %s" % [name, houses[k][0], (q as Vector2).round()]); break
	for pi in PATHS.size():   # (4) is it redundant: running alongside another path for a long stretch
		for pj in range(pi + 1, PATHS.size()):
			var close := 0; var a_pts := _path_points(PATHS[pi]); var b_pts := _path_points(PATHS[pj])
			for q in a_pts:
				for r in b_pts:
					if (q as Vector2).distance_to(r) < 4.0: close += 1; break
			if close * 0.5 > 12.0: issues.append("PATH-DUP  paths %d and %d run side by side for %.0f m" % [pi, pj, close * 0.5])
	return issues

func _on_pier(p: Vector2) -> bool:   # the pier's deck (the plan's pier rectangles)
	for r in PLAN.rects:
		if r.name == "pier" and p.x >= r.x0 and p.x <= r.x1 and p.y >= r.y0 and p.y <= r.y1: return true
	return false

# ---------------------------------------------------------------- the ground check: paths lie on the ground, never under it
## the terrain mesh's own height at a plan point: its 1 m grid of flat triangles, exactly as drawn (not the smooth height())
func terrain_surface(p: Vector2) -> float:
	var gx := p.x + MARGIN; var gy := p.y + MARGIN; var i := floorf(gx); var j := floorf(gy); var fx := gx - i; var fy := gy - j
	var o := Vector2(i - MARGIN, j - MARGIN)
	var h00 := height(o); var h10 := height(o + Vector2(1, 0)); var h01 := height(o + Vector2(0, 1)); var h11 := height(o + Vector2(1, 1))
	if fx + fy <= 1.0: return h00 + (h10 - h00) * fx + (h01 - h00) * fy
	return h11 + (h01 - h11) * (1.0 - fx) + (h10 - h11) * (1.0 - fy)

## the highest the drawn ground gets within r of a point (sampled), so a path laid there stays above it
func _ground_top(p: Vector2, r: float) -> float:
	var top := terrain_surface(p)
	for k in 8: top = maxf(top, terrain_surface(p + Vector2(r, 0).rotated(k * TAU / 8.0)))
	for k in 4: top = maxf(top, terrain_surface(p + Vector2(r * 0.5, 0).rotated(k * TAU / 4.0 + 0.4)))
	return top

## every path triangle, sampled across its face: the path's surface must stay above the drawn ground (no clipping)
func check_ground() -> Array:
	var issues := []
	for pi in path_surfaces.size():
		var verts: Array = path_surfaces[pi][0]; var worst := 0.0; var at := Vector2.ZERO
		for t in path_surfaces[pi][1]:
			var a: Vector3 = verts[t[0]]; var b: Vector3 = verts[t[1]]; var c: Vector3 = verts[t[2]]
			for w in [[1, 0, 0], [0, 1, 0], [0, 0, 1], [0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5], [0.34, 0.33, 0.33], [0.6, 0.2, 0.2], [0.2, 0.6, 0.2], [0.2, 0.2, 0.6]]:
				var q: Vector3 = a * w[0] + b * w[1] + c * w[2]
				var pp := Vector2(q.x, q.z) + ORIGIN
				var under := terrain_surface(pp) - q.y
				if under > worst: worst = under; at = pp
		if worst > 0.005:
			issues.append("GROUND-CLIP %s: the ground shows through by %.0f cm at %s" % [PATHS[pi][2] if pi < PATHS.size() else "path %d" % pi, worst * 100.0, at.round()])
	return issues

## the collision check: each prop's real box (from its meshes, a few centimetres smaller) asked of the physics world:
## anything solid it reaches into (a wall, a fence, another prop) other than itself and the ground is a clip
func check_clip() -> Array:
	var issues := []
	var space := get_world_3d().direct_space_state
	var ground_rids := []
	for b in find_children("TerrainBody*", "CollisionObject3D", true, false): ground_rids.append((b as CollisionObject3D).get_rid())
	for d in doodad_nodes:
		var n: Node3D = d[0]
		var own := ground_rids.duplicate()
		for b in n.find_children("*", "CollisionObject3D", true, false): own.append((b as CollisionObject3D).get_rid())
		var box := AABB(); var first := true
		for mi in n.find_children("*", "MeshInstance3D", true, false):
			var m := mi as MeshInstance3D
			var bb: AABB = n.global_transform.affine_inverse() * m.global_transform * m.get_aabb()
			box = bb if first else box.merge(bb); first = false
		if first: continue
		var gt := n.global_transform; var sc := gt.basis.get_scale()
		var shape := BoxShape3D.new(); shape.size = (box.size * sc - Vector3(0.1, 0.1, 0.1)).max(Vector3(0.04, 0.04, 0.04))
		var q := PhysicsShapeQueryParameters3D.new(); q.shape = shape; q.collision_mask = 1; q.exclude = own
		q.transform = Transform3D(gt.basis.orthonormalized(), gt * (box.get_center() + Vector3(0, 0.05, 0)))   # lifted off the ground a hair
		for hit in space.intersect_shape(q, 4):
			var other: Node = hit.collider
			if d[1] == "forge" and _under_roof_piece(other): continue     # a chimney passes through its roof
			var what := str(other.get_parent().get_parent().name) if other.get_parent() and other.get_parent().get_parent() else str(other.name)
			var p := Vector2(gt.origin.x, gt.origin.z) + ORIGIN
			var where := ""
			if other is Node3D: where = " (%s, its origin %s)" % [other.get_path(), ((other as Node3D).global_position).round()]
			issues.append("CLIP   the %s (%s) reaches into %s at %s%s" % [d[1], d[2], what, p.round(), where])
	return issues

## every roofed room is under a roof: a ray down through its middle must meet a roof piece first
func check_roofs() -> Array:
	var issues := []
	var space := get_world_3d().direct_space_state
	for r in roofed:
		for off in [Vector2.ZERO, Vector2(0.6, 0.6), Vector2(-0.6, -0.6)]:
			var p: Vector2 = r[0] + (off * r[1]).rotated(r[2])
			var q := PhysicsRayQueryParameters3D.create(W(p, 40.0), W(p, -5.0), 1)
			var hit := space.intersect_ray(q)
			var roof := false; var n: Node = hit.collider if not hit.is_empty() else null
			while n and n != self:
				if str(n.name).begins_with("Roof_"): roof = true; break
				n = n.get_parent()
			if not roof:
				issues.append("ROOF   no roof over the room at %s (the ray met %s)" % [p.round(), hit.collider.get_parent().name if not hit.is_empty() and hit.collider.get_parent() else "nothing"]); break
	return issues

func _under_roof_piece(n: Node) -> bool:   # is this collider part of a roof piece
	while n and n != self:
		if str(n.name).begins_with("Roof_"): return true
		n = n.get_parent()
	return false
