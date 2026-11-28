## Farhallow in the voxel style, on its real plan (scripts/farhallow.gd's land and data/farhallow.json): the ground kit
## (scripts/voxel/ground_kit.gd) laid over the village's terrain - the coast, the beach, the rise to the north-east, each
## building's level terrace - with its roads, lanes and trails worn into the turf, the sea, swaying grass that parts round
## the player, and the buildings: the inn from Fogwright's own voxel building kit, the rest still stand-ins from Medieval
## Voxel Assets (CC0), sized to each plot, until the kit has their types.
extends Node3D

const FH := preload("res://scripts/farhallow.gd")
const MED := "res://assets/buildings/medieval_voxel/"
# stand-in buildings and their footprints (metres, x by z), the nearest in shape is sized to each plan building
const STANDINS := [["Houses/House_1", 6.5, 6.4], ["Houses/House_2", 4.8, 6.1], ["Houses/House_3", 4.1, 4.0],
	["Shops/Shop_Closed", 2.8, 2.4], ["Towers/Tower_Simple", 6.0, 6.0]]
# plan building types built from the voxel building kit instead of a stand-in (scripts/voxel/kit_layouts.gd)
const KITS := {"inn": KitLayouts.GULL_LANTERN}
## the village's buildings baked (BuildingKit.load_or_build): run this scene with "-- bake" (not headless) to make them;
## tools/build/bake_farhallow.sh does it before an export. Missing or stale bakes are built live, which is slower.
const BAKED := "res://assets/voxel/baked/farhallow_%02d.scn"
var baking := OS.get_cmdline_user_args().has("bake")
const MR := 0.25             # the path mask's resolution (m)
var fh: Node3D
var mask := PackedByteArray()
var m0 := Vector2(-45, -45)  # the mask's corner, plan metres
var mw := 0; var mh := 0
var ground: Node3D
var player: Node3D

func _ready() -> void:
	fh = FH.new()
	fh._enter_tree()                                        # the plan: buildings, roads, lanes, trails
	fh.noise.seed = 7; fh.noise.frequency = 0.035           # as farhallow.gd shapes its land
	for b in fh.BUILDINGS:                                  # each building's terrace, as farhallow.gd cuts it
		var c := Vector2(b.x, b.y); var a: float = b.a; var corners := 0.0
		for k in 4:
			var u := (float(b.w) * 0.5) * (1 if k % 2 == 0 else -1); var v := (float(b.h) * 0.5) * (1 if k < 2 else -1)
			corners += fh._base(c + Vector2(u, v).rotated(a))
		fh.pads.append([c, Vector2(b.w, b.h) * 0.5, a, max(corners / 4.0, fh._base(c)) + 0.05])
	fh.pads.append([fh.WELL, Vector2(6, 6), 0.0, fh._base(fh.WELL)])
	_paths_mask()
	var t0 := Time.get_ticks_msec()
	var o: Vector2 = fh.ORIGIN; var M: float = fh.MARGIN
	ground = GroundKit.build(_height, Rect2(-M - o.x, -M - o.y, 140 + 2 * M, 110 + 2 * M), _kind, 4.0, 7)
	add_child(ground)
	print("FARHALLOW ground %d ms, %d grass tufts, pieces %s" % [Time.get_ticks_msec() - t0, ground.get_node("Grass").get_meta("tufts"), ground.get_meta("pieces")])
	_sea()
	var tb := Time.get_ticks_msec()
	_buildings(); _ready_kit_report()
	print("FARHALLOW buildings ready in %d ms" % (Time.get_ticks_msec() - tb))
	if baking: get_tree().quit()
	add_child(VillageDress.build(self))                     # the palisade, gate, harbour, well, plots, field, props, woods
	player = get_parent().get_node_or_null("Player")
	if player:
		var sp: Vector2 = fh.WELL + Vector2(2.5, 2.5)
		player.global_position = Vector3(sp.x - o.x, fh.height(sp) + 0.2, sp.y - o.y)

func _exit_tree() -> void:
	if fh: fh.free()

func _process(_d: float) -> void:
	if player: GroundKit.push(ground, [player.global_position])

func _plan(p: Vector2) -> Vector2: return p + fh.ORIGIN          # world x, z -> plan metres
func _height(p: Vector2) -> float: return fh.height(_plan(p))

func _kind(p: Vector2, _slope: float) -> String:
	var q := _plan(p)
	var c: float = fh._coast_signed(q)
	if c < 3.5 + 1.5 * fh.noise.get_noise_2d(q.x * 4.0, q.y * 4.0): return "sand"
	var i := int((q.x - m0.x) / MR); var j := int((q.y - m0.y) / MR)
	if i >= 0 and j >= 0 and i < mw and j < mh and mask[j * mw + i] > 0: return "path"
	return "grass"

## every road, lane, door path and trail stamped into a 25 cm mask, worn a little wider and narrower along its length
func _paths_mask() -> void:
	mw = int(230 / MR); mh = int(200 / MR); mask.resize(mw * mh); mask.fill(0)
	for path in fh.PATHS:
		var pts: Array = path[0]; var hw: float = float(path[1]) * 0.5
		for k in pts.size() - 1:
			var a: Vector2 = pts[k]; var b: Vector2 = pts[k + 1]
			var n := maxi(1, int(a.distance_to(b) / 0.2))
			for s in n + 1:
				var q := a.lerp(b, float(s) / n)
				var r: float = hw * (1.0 + 0.15 * fh.noise.get_noise_2d(q.x * 6.0, q.y * 6.0))
				var ri := int(ceil(r / MR))
				var ci := int((q.x - m0.x) / MR); var cj := int((q.y - m0.y) / MR)
				for dj in range(-ri, ri + 1):
					for di in range(-ri, ri + 1):
						if (di * di + dj * dj) * MR * MR > r * r: continue
						var x := ci + di; var y := cj + dj
						if x >= 0 and y >= 0 and x < mw and y < mh: mask[y * mw + x] = 1

func _sea() -> void:
	var m := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(900, 900); m.mesh = pm
	var mat := StandardMaterial3D.new(); var c := Palette.col("sea"); mat.albedo_color = Color(c.r, c.g, c.b, 0.85)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA; mat.roughness = 0.1; mat.metallic_specular = 0.8
	m.material_override = mat; m.position = Vector3(250, 0.0, 250); add_child(m)

## each plan building as the stand-in nearest its shape, scaled to its footprint, on its terrace, turned to its angle
var kit_tris := 0
func _buildings() -> void:
	var o: Vector2 = fh.ORIGIN
	for i in fh.BUILDINGS.size():
		var b: Dictionary = fh.BUILDINGS[i]
		if KITS.has(b.type) or KitLayouts.STYLES.has(b.type):   # from the voxel building kit: true size, rooms inside
			var kit_holder := Node3D.new(); kit_holder.name = "Building%d" % i; add_child(kit_holder)
			var lay: Dictionary
			if KITS.has(b.type): lay = KITS[b.type]
			else:   # laid out from the plan: its size and doors, in the plot's own frame
				var ca := cos(float(b.a)); var sa := sin(float(b.a)); var dl := []
				for dd in b.doors:
					var v := Vector2(dd[0] - b.x, dd[1] - b.y); dl.append(Vector2(v.x * ca + v.y * sa, -v.x * sa + v.y * ca))
				lay = KitLayouts.for_plot(b.type, float(b.w), float(b.h), dl, i)
			var bk := BuildingKit.load_or_build(lay, BAKED % i, baking); kit_holder.add_child(bk)
			var sz: Vector2i = lay.size
			# the kit's front (+Z) turned to face the plot's door side (its local -Z), centred on the plot
			bk.rotation.y = PI; bk.position = Vector3(sz.x, 0, -sz.y)
			kit_holder.position = Vector3(b.x - o.x, fh.pads[i][3], b.y - o.y); kit_holder.rotation.y = -float(b.a)
			kit_tris += bk.get_meta("triangles")
			print("FARHALLOW %s (%s) from the kit%s: %d triangles, %d ms" % [b.name, b.type, " (baked)" if bk.get_meta("baked", false) else "", bk.get_meta("triangles"), bk.get_meta("build_ms")])
			continue
		var w := float(b.w); var d := float(b.h)
		var best: Array = STANDINS[0]; var err := INF
		for s in STANDINS:
			var e := absf(log((w / d) / (s[1] / s[2])))
			if e < err: err = e; best = s
		var sc := clampf(minf(w / best[1], d / best[2]), 0.7, 2.2)
		var n := Vox.prop(MED + best[0] + ".glb")
		var box := _aabb(n)
		var holder := Node3D.new(); holder.name = "Building%d" % i; add_child(holder)
		holder.add_child(n); n.position = -Vector3(box.get_center().x, box.position.y, box.get_center().z)
		holder.scale = Vector3.ONE * sc
		holder.position = Vector3(b.x - o.x, fh.pads[i][3], b.y - o.y); holder.rotation.y = -float(b.a)
		var body := StaticBody3D.new(); var cs := CollisionShape3D.new(); var bs := BoxShape3D.new()
		bs.size = box.size; cs.shape = bs; cs.position = Vector3(0, box.size.y * 0.5, 0); body.add_child(cs); holder.add_child(body)

func _ready_kit_report() -> void:
	print("FARHALLOW kit buildings: %d triangles in all" % kit_tris)

func _aabb(n: Node3D) -> AABB:
	var box := AABB(); var first := true
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D; var t := Transform3D.IDENTITY; var x: Node = m
		while x != null and x != n: t = (x as Node3D).transform * t; x = x.get_parent()
		var a := t * m.mesh.get_aabb()
		box = a if first else box.merge(a); first = false
	return box
