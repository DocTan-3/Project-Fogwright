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
	for p in PATHS: _path(p[0], p[1])
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
	curve.bake_interval = 0.5
	var baked := curve.get_baked_points()
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var dirt := Palette.col("path")
	var verts := []; var tris := []
	for i in baked.size():
		var p: Vector2 = baked[i]; var d: Vector2 = (baked[min(i + 1, baked.size() - 1)] - baked[max(i - 1, 0)]).normalized()
		var side := Vector2(-d.y, d.x)
		var hw := width * 0.5 * (1.0 + 0.18 * noise.get_noise_2d(p.x * 6.0, p.y * 6.0))   # ragged, worn edges
		for s in [-1.0, 0.0, 1.0]:
			var q: Vector2 = p + side * hw * s
			st.set_color(dirt.lerp(dirt.darkened(0.15), 0.5 + 0.5 * noise.get_noise_2d(q.x * 9.0, q.y * 9.0)) * shade(q))
			var v := W(q, _ground_top(q, 0.6) + 0.04)        # above the highest ground round it, so the terrain never shows through
			st.add_vertex(v); verts.append(v)
	for i in baked.size() - 1:
		var a := i * 3
		for k in 2:
			for t in [[a + k, a + 3 + k, a + k + 1], [a + k + 1, a + 3 + k, a + 4 + k]]:
				st.add_index(t[0]); st.add_index(t[1]); st.add_index(t[2]); tris.append(t)
	path_surfaces.append([verts, tris])
	st.generate_normals()
	var mi := MeshInstance3D.new(); mi.mesh = st.commit(); mi.add_to_group("path_mesh")
	var mat := StandardMaterial3D.new(); mat.vertex_color_use_as_albedo = true; mat.roughness = 1.0; mi.material_override = mat
	add_child(mi)

# ---------------------------------------------------------------- buildings, built from their floorplans
# Each building is its type's floorplan (tools/map/building_types.py), placed whole: the kit's 2 m wall pieces run along
# every outside edge of its roofed rooms, fitted to the edge's real length, with a door or window where the floorplan
# has one; each wing (roofed rooms that make a rectangle) gets a roof fitted to it, with gable ends; yards get fences or
# walls. Floorplan coordinates: x across the front, y back from the street (y = 0 is the street side).
const STOREYS := {"street_house": 2, "merchant_house": 2, "merchant_house_small": 2, "inn": 2}
const LOW := {"hen_house": 0.55, "salt_works": 0.8, "guard_post": 0.85, "smokehouse": 0.9}   # small sheds: lower walls
const THATCH_TYPES := ["cottage", "farmstead", "hen_house", "smokehouse", "boat_shed", "salt_works", "granary"]
const ROOF_SIZES := {4: [4, 6, 8], 6: [4, 6, 8, 10, 12, 14], 8: [8, 10, 12, 14]}

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
	# yards: a wall round the well-off's, a fence round the others, open where a building or a gate meets them
	for r in rooms:
		if r[5] == "yard" and not str(r[4]).begins_with("arch"):
			for e in _edges(r, roofs):
				_fence_run(e, ty, L, b.zone == "rich", mir)
	# wings and roofs
	var wings := _wings(roofs)
	for wg in wings: _roof(wg, storeys * STOREY * low, L, b.type in THATCH_TYPES or b.zone == "poor", kinds)
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
			plinth.position = L.call(r[0] + r[2] * 0.5, r[1] + r[3] * 0.5, -(level - lowest + 0.4) * 0.5 + 0.0)
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

func _wall_run(e: Array, r: Array, ty: Dictionary, storeys: int, low: float, kinds: Array, L: Callable, mir: bool) -> void:
	var a: Vector2 = e[0]; var bb: Vector2 = e[1]; var n: Vector2 = e[2]
	var length := a.distance_to(bb); var cnt := maxi(1, roundi(length / 2.0)); var seg := length / cnt
	var nn := Vector2(-n.x if mir else n.x, n.y)
	var yaw := atan2(nn.x, nn.y)
	var front := n.y < 0 and absf(a.y) < 0.05          # the street front
	for s in storeys:
		var kind: String = kinds[mini(s, kinds.size() - 1)]
		for k in cnt:
			var p0 := a.lerp(bb, float(k) / cnt); var p1 := a.lerp(bb, float(k + 1) / cnt); var mid := (p0 + p1) * 0.5
			var pos: Vector3 = L.call(mid.x, mid.y, s * STOREY * low)
			var name := ("Wall_Plaster_Straight_Base" if s == 0 else "Wall_Plaster_Straight") if kind == "Plaster" else "Wall_%s_Straight" % kind
			var fill := ""
			if s == 0:
				var op := _opening(ty, p0, p1, n)
				if op.size() > 0:
					if op[0] in ["g", "o", "s"]: continue           # a gate, an archway or an open front: no wall
					if op[0] == "d": name = "Wall_%s_Door_Flat" % kind; fill = "Door_1_Flat"
					elif op[0] == "w":
						name = "Wall_%s_Window_Wide_Round" % kind if op[1] >= 1.2 else "Wall_%s_Window_Thin_Round" % kind
						fill = "Window_Wide_Round1" if op[1] >= 1.2 else "Window_Thin_Round1"
			elif front or (n.y > 0):                               # upper storeys: windows along the front and back
				var wide := (k + s) % 2 == 0
				name = "Wall_%s_Window_Wide_Round" % kind if wide else "Wall_%s_Window_Thin_Round" % kind
				fill = "Window_Wide_Round1" if wide else "Window_Thin_Round1"
			var piece := _piece(name, pos, yaw)
			if piece: piece.scale = Vector3(seg / 2.0, low, 1.0)
			if fill != "":
				var off := Vector3(-0.53, 0, 0).rotated(Vector3.UP, yaw) if fill.begins_with("Door") else Vector3.ZERO
				var f := _piece(fill, pos + off, yaw)
				if f and not fill.begins_with("Door"): f.scale = Vector3(1.0, low, 1.0)

func _fence_run(e: Array, ty: Dictionary, L: Callable, wall: bool, mir: bool) -> void:
	var a: Vector2 = e[0]; var bb: Vector2 = e[1]; var n: Vector2 = e[2]
	var length := a.distance_to(bb); var cnt := maxi(1, roundi(length / 2.0)); var seg := length / cnt
	for k in cnt:
		var p0 := a.lerp(bb, float(k) / cnt); var p1 := a.lerp(bb, float(k + 1) / cnt); var mid := (p0 + p1) * 0.5
		var op := _opening(ty, p0, p1, n)
		if op.size() > 0 and op[0] != "w": continue                # the gate
		var pos: Vector3 = L.call(mid.x, mid.y)
		var yaw := atan2(-n.x if mir else n.x, n.y)
		if wall:
			var mi := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(seg, 1.7, 0.4); mi.mesh = bm
			var m := StandardMaterial3D.new(); m.albedo_texture = load("res://assets/library/RockTrim_detail.png"); m.albedo_color = Palette.col("RockTrim") / 0.78
			m.uv1_triplanar = true; mi.material_override = m; mi.position = pos + Vector3(0, 0.85, 0); mi.rotation.y = yaw; _into.add_child(mi)
			var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = bm.size; col.shape = bs
			body.add_child(col); body.transform = mi.transform; _into.add_child(body)
		else:
			var f := _piece("Prop_WoodenFence_Single", pos, yaw)
			if f: f.scale = Vector3(seg / 2.0, 1.0, 1.0)

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
	var sides := [[P.call(-hw, -hh), P.call(-hw, hh)], [P.call(-hw, hh), P.call(hw, hh)], [P.call(hw, hh), P.call(hw, -hh)]]
	for si in sides.size():
		var e: Array = sides[si]; var p0: Vector2 = e[0]; var p1: Vector2 = e[1]; var length := p0.distance_to(p1); var cnt := maxi(1, roundi(length / 2.0))
		for k in cnt:
			var q0 := p0.lerp(p1, float(k) / cnt); var q1 := p0.lerp(p1, float(k + 1) / cnt); var mid := (q0 + q1) * 0.5
			if si == 1 and k == cnt / 2: continue      # the back gate
			var yaw := -atan2(q1.y - q0.y, q1.x - q0.x)
			if walled:
				var mi := MeshInstance3D.new(); var bm := BoxMesh.new(); bm.size = Vector3(q0.distance_to(q1), 1.7, 0.4); mi.mesh = bm
				var m := StandardMaterial3D.new(); m.albedo_texture = load("res://assets/library/RockTrim_detail.png"); m.albedo_color = Palette.col("RockTrim") / 0.78
				m.uv1_triplanar = true; mi.material_override = m; mi.position = W(mid, height(mid) + 0.75); mi.rotation.y = yaw; add_child(mi)
				var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = bm.size; col.shape = bs
				body.add_child(col); body.transform = mi.transform; add_child(body)
			else:
				var f := put(VILLAGE % "Prop_WoodenFence_Single", W(mid, height(mid)), yaw, 1.0, true, "fixture", "the plot's fence")
				if f: f.scale = Vector3(q0.distance_to(q1) / 2.0, 1.0, 1.0)

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

func _well() -> void:
	var y := height(WELL)
	var ring := MeshInstance3D.new(); var cm := CylinderMesh.new(); cm.top_radius = 1.0; cm.bottom_radius = 1.1; cm.height = 0.9
	ring.mesh = cm; var m := StandardMaterial3D.new(); m.albedo_texture = load("res://assets/library/UnevenBrick_detail.png")
	m.albedo_color = Palette.col("UnevenBrick") / 0.78; m.uv1_triplanar = true; ring.material_override = m
	ring.position = W(WELL, y + 0.45); add_child(ring)
	var water := MeshInstance3D.new(); var wm := CylinderMesh.new(); wm.top_radius = 0.85; wm.bottom_radius = 0.85; wm.height = 0.05
	water.mesh = wm; var wmat := StandardMaterial3D.new(); wmat.albedo_color = Palette.col("sea").darkened(0.4); wmat.roughness = 0.05
	water.material_override = wmat; water.position = W(WELL, y + 0.7); add_child(water)
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
	put(VILLAGE % "Roof_Tower_RoundTiles", W(lh, 13.7), 0.0, 0.9, false, "fixture", "the lighthouse's roof")
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
	var runs := []
	for wl in PLAN.walls:
		if wl.name != "palisade": continue
		var run := []; for q in wl.pts: run.append(Vector2(q[0], q[1]))
		runs.append(run)
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
		put(VILLAGE % "Roof_Tower_RoundTiles", W(p, height(p) + 6.0), 0.0, 0.55, false, "fixture", "a gate tower's roof")
	var gate := MeshInstance3D.new(); var gm := BoxMesh.new(); gm.size = Vector3(8.0, 3.6, 0.3); gate.mesh = gm; gate.material_override = mat
	gate.position = W(Vector2(62, 4), height(Vector2(62, 4)) + 1.8); add_child(gate)

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
	for kind in by_kind: scatter(NATURE % kind, by_kind[kind], Vector2(0.9, 1.35), ["grass", "woods"])
	scatter(NATURE % "Grass_Common_Short", _ground_pts(1400, func(p): return _coast_signed(p) > 5.0 and not _near_built(p) and not (p.x > 14 and p.x < 37 and p.y > 14 and p.y < 47)))
	scatter(NATURE % "Flower_3_Group", _ground_pts(140, func(p): return _in_clearing(p) and _coast_signed(p) > 6.0 and not _near_built(p, 1.5)), Vector2(0.28, 0.4))
	scatter(NATURE % "Fern_1", _ground_pts(260, func(p): return not _in_clearing(p) and _coast_signed(p) > 6.0), Vector2(0.9, 1.1), ["woods"])
	for i in 14:
		var p := Vector2(rng.randf_range(60, 130), rng.randf_range(70, 105))
		if _coast_signed(p) < -1.0 and _coast_signed(p) > -9.0: put(NATURE % ("Rock_Medium_%d" % (i % 3 + 1)), W(p, height(p)), rng.randf() * TAU, rng.randf_range(1.2, 2.2), true, "fixture", "rocks in the shallows")

# ---------------------------------------------------------------- life: the plan's doodads, each with its purpose
const FW := "res://assets/props/fogwright/%s.glb"
const DOCK := "res://assets/props/docks/%s.glb"
const V2 := "res://assets/props/village2/%s.glb"
## kind -> [model, scale, extra height (for things hung on walls or posts), solid]
const DOODAD_MODELS := {
	"bench": [PROPS % "Bench", 1.0, 0.0, true], "barrel": [PROPS % "Barrel", 1.0, 0.0, true], "crate": [PROPS % "Crate_Wooden", 1.0, 0.0, true],
	"woodpile": [FW % "Woodpile", 1.0, 0.0, true], "washing line": [FW % "Washing_Line", 1.0, 0.0, false],
	"well": [V2 % "Prop_Well_1", 0.8, 0.0, true], "fruit tree": [NATURE % "CommonTree_2", 0.55, 0.0, true],
	"flower bed": [NATURE % "Flower_4_Group", 0.9, 0.0, false], "lamp": [PROPS % "Lantern_Wall", 1.0, 2.1, false],
	"sign": [V2 % "Wall_Prop_Sign_1", 0.8, 2.4, false], "trough": [FW % "Trough", 1.0, 0.0, true], "cart": [V2 % "Prop_Cart_1", 0.9, 0.0, true],
	"net rack": [FW % "Net_Rack", 1.0, 0.0, true], "lobster pots": [FW % "Lobster_Pots", 1.0, 0.0, true],
	"gutting table": [DOCK % "Props_Table_1", 1.0, 0.0, true], "scarecrow": [FW % "Scarecrow", 1.0, 0.0, false],
	"haystack": [V2 % "Prop_Hay_1", 1.3, 0.0, true], "notice post": [FW % "Notice_Post", 1.0, 0.0, true],
	"torch": [PROPS % "Torch_Metal", 1.0, 2.6, false], "bell frame": [FW % "Bell_Frame", 1.0, 0.0, true],
	"anvil": [PROPS % "Anvil", 1.0, 0.0, true], "quench trough": [FW % "Quench_Trough", 1.0, 0.0, true],
	"grindstone": [PROPS % "Whetstone", 1.4, 0.0, false], "charcoal": [FW % "Charcoal_Heap", 1.0, 0.0, false],
	"candles": [PROPS % "CandleStick_Triple", 1.0, 0.0, false], "sacks": [PROPS % "Bag", 1.2, 0.0, false],
	"manure heap": [FW % "Manure_Heap", 1.0, 0.0, false], "drying rack": [DOCK % "Props_Rack_Fish", 1.0, 0.0, true],
	"hen coop": [FW % "Hen_Coop", 1.0, 0.0, true], "boat hull": [DOCK % "Boat_Stand", 0.7, 0.0, true],
	"chopping block": [PROPS % "Anvil_Log", 1.0, 0.0, true],
}

func _doodads() -> void:
	for dd in PLAN.doodads:
		var m: Array = DOODAD_MODELS.get(dd.kind, [])
		if m.is_empty(): push_warning("no model for " + dd.kind); continue
		var p := Vector2(dd.x, dd.y)
		var owner: int = int(dd.owner)
		# hung on a wall or post, or standing inside its own open workshop: a fixture, not clutter in the way
		var role := "fixture" if dd.mounted or (owner >= 0 and _in_roofed(p, -0.1)) else "clutter"
		var y: float = (1.0 if _on_pier(p) else height(p)) + float(m[2])   # on the pier's deck, or on the ground

		var n := put(m[0], W(p, y), -float(dd.a), m[1], m[3], role, dd.purpose)
		if n == null: continue
		if dd.kind == "boat hull":   # a hull, half built, on its trestles
			put(DOCK % "Boat_B_1", W(p, y + 0.45), -float(dd.a), 0.7, false, "fixture", "the hull on its trestles")
		if dd.kind == "chopping block":   # beat B: the first weapon waits here
			put(PROPS % "Axe_Bronze", W(p, y + 0.5), -float(dd.a) + 0.6, 1.0, false, "fixture", "the hatchet in the chopping block: the first weapon")

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
	for g in [WELL, Vector2(87.5, 99), Vector2(96, 100.5)] + bdoors.reduce(func(acc, ds): return acc + ds, []):
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
	var issues := check_paths() + check_ground()
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
