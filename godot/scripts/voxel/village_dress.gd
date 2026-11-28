## The rest of voxel Farhallow beyond its buildings, from the same plan (data/farhallow.json, scripts/farhallow.gd), all
## solids in voxels as the art direction says (crops, flowers, the wash and flames stay low-poly):
##   - the palisade of sharpened stakes and the north gate: timber towers with lookouts, the lintel, the leaves open by day,
##     torches on the posts;
##   - the harbour: the sea wall running on as the breakwater, the lighthouse at its end, the pier (a T on posts), two
##     fishing boats at anchor and the last ship moored along the pier's head (the trader from Hollin's Cross);
##   - the well in the square, the plots' walls and fences, the field's fence and barley, the vegetable plots;
##   - the plan's doodads, each with its purpose (VoxelProps), less those the building kit's yards already place
##     (woodpiles and net racks against houses) and those hung on the old buildings' walls (the kit hangs its own);
##   - the woods beyond the palisade: wind-bent coastal pines and gorse, batched by 24 m block, solid near the village.
## Village.build(level) adds it all under one node; level is farhallow_voxel.gd (its fh: the plan, heights, coast).
class_name VillageDress
extends RefCounted

const PROP_SKIP := ["smithy door", "lamp", "sign", "candles", "torch", "old blade"]   # hung on the old walls, or doors the kit has
const KIT_YARD := ["woodpile", "net rack"]                                           # the kit's yards place these by each house
var fh: Node3D
var root: Node3D
var o: Vector2
var rng := RandomNumberGenerator.new()
var placed := []        # [kind, Vector2 plan, radius, purpose]: for the dress check
var stats := {}

static func build(level: Node3D) -> Node3D:
	var d := VillageDress.new(); d.fh = level.fh; d.o = level.fh.ORIGIN; d.rng.seed = 3131
	d.root = Node3D.new(); d.root.name = "VillageDress"
	var t0 := Time.get_ticks_msec()
	d._palisade(); d._gate(); d._harbour(); d._well(); d._plots(); d._field(); d._doodads(); d._woods()
	d.root.set_meta("placed", d.placed)
	print("VILLAGE dress %d ms: %s" % [Time.get_ticks_msec() - t0, d.stats])
	return d.root

func W(p: Vector2, y: float) -> Vector3: return Vector3(p.x - o.x, y, p.y - o.y)
## the ground as the ground kit draws it (scripts/voxel/ground_kit.gd): 1 m cells on whole world metres, their corners
## snapped to 0.5 m steps, each cell split along its flatter diagonal; props stand on this, not on the smooth plan height
func H(p: Vector2) -> float:
	var w := p - o; var i := floorf(w.x); var j := floorf(w.y); var u := w.x - i; var v := w.y - j
	var cs := func(x: float, z: float) -> float: return snappedf(fh.height(Vector2(x, z) + o), GroundKit.STEP)
	var h := [cs.call(i, j), cs.call(i + 1, j), cs.call(i + 1, j + 1), cs.call(i, j + 1)]
	return GroundKit._surf(h, absf(h[0] - h[2]) <= absf(h[1] - h[3]), u, v)

func _add(n: Node3D, at: Vector3, yaw := 0.0) -> Node3D:
	root.add_child(n); n.position = at; n.rotation.y = yaw; return n

func _mesh_node(m: Mesh, size: float, at: Vector3, yaw := 0.0, nm := "Prop") -> MeshInstance3D:
	var mi := MeshInstance3D.new(); mi.name = nm; mi.mesh = m; mi.material_override = Vox.grain_material(size)
	_add(mi, at, yaw); return mi

## a box collider round a placed mesh (its AABB, in its own frame)
func _solid(mi: MeshInstance3D, shrink := 0.0) -> void:
	var bb := mi.mesh.get_aabb().grow(-shrink)
	var sb := StaticBody3D.new(); var cs := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = bb.size
	cs.shape = bs; cs.position = bb.get_center(); sb.add_child(cs); mi.add_child(sb)

func _count(k: String, n := 1) -> void: stats[k] = stats.get(k, 0) + n

# ---------------------------------------------------------------- the palisade
## stakes of split pine, 30 cm, sharpened, 3.2 m out of the ground, set close and a little crooked; three kinds drawn as
## batches; a rail along the inside at chest height; a box collider per run
func _stake(seed_: int) -> ArrayMesh:
	var v := VBox.new(0.05); var r := RandomNumberGenerator.new(); r.seed = seed_
	var cols := [VoxelProps.C.tar, VoxelProps.C.tar_d, VoxelProps.C.drift_d, VoxelProps.C.bark]
	var top := 3.4 + r.randf_range(-0.15, 0.2)
	for y in int(top / 0.05) + 16:
		var yy := y * 0.05 - 0.8                    # 0.8 m in the ground
		var rad := 3 if yy < top - 0.45 else maxi(0, int(3.0 * (top - yy) / 0.45))
		for i in range(-3, 3):
			for k in range(-3, 3):
				if absi(i * 2 + 1) > rad * 2 or absi(k * 2 + 1) > rad * 2: continue
				if (i == -3 or i == 2) and (k == -3 or k == 2): continue   # round off the square
				var c: Color = cols[(int(yy * 3.0) + i * 5 + seed_) % 4 if (i + y) % 7 == 0 else seed_ % 3]
				v.put(Vector3i(i, y - 16, k), c, 0.06, seed_)
	return v.mesh()

func _palisade() -> void:
	var meshes := [_stake(1), _stake(2), _stake(3)]
	var xf := [[], [], []]
	for wl in fh.PLAN.walls:
		if wl.name != "palisade": continue
		var pts: Array = wl.pts
		for i in pts.size() - 1:
			var a := Vector2(pts[i][0], pts[i][1]); var b := Vector2(pts[i + 1][0], pts[i + 1][1])
			var n := int(a.distance_to(b) / 0.32)
			for k in n:
				var p := a.lerp(b, (k + 0.5) / n)
				var tilt := Basis(Vector3(rng.randf_range(-1, 1), 0, rng.randf_range(-1, 1)).normalized(), rng.randf_range(0.0, 0.05))
				xf[rng.randi() % 3].append(Transform3D(tilt.rotated(Vector3.UP, rng.randf() * TAU), W(p, H(p) + rng.randf_range(-0.15, 0.1))))
			# the rail on the inside (toward the village), and the run's collider
			var d := (b - a).normalized(); var inside := Vector2(-d.y, d.x)
			if (fh.WELL - a).dot(inside) < 0: inside = -inside
			var rail := VBox.new(0.1); var L := a.distance_to(b)
			rail.box(Vector3(0, 1.3, -0.1), Vector3(L, 1.5, 0.1), VoxelProps.C.tar_d, 0.05)
			var mi := _mesh_node(rail.mesh(), 0.1, W(a + inside * 0.3, H(a)), -atan2(d.y, d.x), "Rail")
			mi.position.y = (H(a) + H(b)) * 0.5 - 0.2
			VBox.collider(root, W((a + b) * 0.5, (H(a) + H(b)) * 0.5 + 1.5), Vector3(L, 3.0, 0.45), -atan2(d.y, d.x))
			_count("palisade m", int(L))
	for i in 3:
		var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = meshes[i]; mm.instance_count = xf[i].size()
		for k in xf[i].size(): mm.set_instance_transform(k, xf[i][k])
		var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm; mmi.material_override = Vox.grain_material(0.05); root.add_child(mmi)
		_count("stakes", xf[i].size())

# ---------------------------------------------------------------- the north gate
## two square timber towers either side of the 7 m opening, each on four posts with a lookout platform, a rail and a
## board roof; a lintel and a carved board over the opening; the two leaves standing open, swung inward
func _gate() -> void:
	var gp := Vector2(62, 4.3); var y0: float = minf(H(gp + Vector2(-4.5, 0)), H(gp + Vector2(4.5, 0)))
	var v := VBox.new(0.05); var C := VoxelProps.C
	for side in [-1, 1]:
		var cx: float = side * 4.75   # tower centres: the opening is 7 m, the towers 2.5 m square
		for px in [cx - 1.1, cx + 1.1]:
			for pz in [-1.1, 1.1]: v.box(Vector3(px - 0.15, -1.0, pz - 0.15), Vector3(px + 0.15, 6.2, pz + 0.15), C.tar, 0.05)
		for y in [1.2, 3.6]:   # cross braces and beams
			for pz in [-1.1, 1.1]: v.box(Vector3(cx - 1.25, y, pz - 0.1), Vector3(cx + 1.25, y + 0.2, pz + 0.1), C.tar_d)
			for px in [cx - 1.1, cx + 1.1]: v.box(Vector3(px - 0.1, y, -1.25), Vector3(px + 0.1, y + 0.2, 1.25), C.tar_d)
		v.beam(Vector3(cx - 1.1, 0.0, -1.2), Vector3(cx + 1.1, 3.6, -1.2), 0.12, C.tar_d)
		v.beam(Vector3(cx + 1.1, 0.0, 1.2), Vector3(cx - 1.1, 3.6, 1.2), 0.12, C.tar_d)
		# the lookout: a plank floor at 3.8 m, a breastwork of boards, a ladder inside
		for k in int(2.6 / 0.2): v.box(Vector3(cx - 1.3 + k * 0.2, 3.8, -1.3), Vector3(cx - 1.12 + k * 0.2, 3.9, 1.3), C.drift if k % 2 else C.drift_d)
		for pz in [-1.3, 1.25]: v.box(Vector3(cx - 1.3, 3.9, pz), Vector3(cx + 1.3, 4.9, pz + 0.05), C.board_d)
		for px in [cx - 1.3, cx + 1.25]: v.box(Vector3(px, 3.9, -1.3), Vector3(px + 0.05, 4.9, 1.3), C.board_d)
		for r in 8:
			var ry := r * 0.47
			v.box(Vector3(cx - 0.35, ry, 1.0), Vector3(cx + 0.35, ry + 0.05, 1.05), C.drift_d)
		for px in [cx - 0.35, cx + 0.3]: v.box(Vector3(px, 0, 1.0), Vector3(px + 0.05, 3.8, 1.05), C.drift_d)
		for k in 9:   # a board roof, gabled along the palisade
			var yy := 6.2 + k * 0.08
			v.box(Vector3(cx - 1.6, yy, -1.6 + k * 0.17), Vector3(cx + 1.6, yy + 0.06, -1.4 + k * 0.17), C.drift_d)
			v.box(Vector3(cx - 1.6, yy, 1.4 - k * 0.17), Vector3(cx + 1.6, yy + 0.06, 1.6 - k * 0.17), C.drift_d)
		var t := VoxelProps.flame(0.18)   # the torch on the post toward the road, lit at dusk
		var tx: float = cx - side * 1.3
		v.box(Vector3(tx - 0.04, 2.3, -1.35), Vector3(tx + 0.04, 2.8, -1.27), C.oak_d)
		_add(t, W(gp, y0) + Vector3(tx, 2.8, -1.31)); t.name = "GateTorch"
		VBox.collider(root, W(gp, y0) + Vector3(cx, 2.5, 0), Vector3(2.6, 5.0, 2.6))
	v.box(Vector3(-3.6, 4.4, -0.2), Vector3(3.6, 4.75, 0.2), C.tar)        # the lintel
	v.box(Vector3(-1.6, 4.75, -0.25), Vector3(1.6, 5.25, -0.2), C.drift)   # the board over it, Hollin's mark burnt in
	for k in 12: v.put(Vector3i(-6 + k, int(5.0 / 0.05), -5), C.soot)
	for k in 10: v.put(Vector3i(0, int(4.78 / 0.05) + k, -5), C.soot)
	root.add_child(_named(v.node(Vector3.ZERO, "Gate"), W(gp, y0)))
	# the leaves: planks on three ledges, swung inward (toward the village, +plan y) and standing open
	for side in [-1, 1]:
		var lf := VBox.new(0.05)
		for k in 17: lf.box(Vector3(0.0 + k * 0.2, 0, 0), Vector3(0.18 + k * 0.2, 3.4, 0.1), C.tar if k % 3 else C.tar_d)
		for y in [0.4, 1.7, 3.0]: lf.box(Vector3(0.1, y, 0.1), Vector3(3.3, y + 0.25, 0.18), C.oak_d)
		lf.beam(Vector3(0.2, 0.6, 0.16), Vector3(3.2, 2.9, 0.16), 0.15, C.oak_d)
		var leaf := lf.node(Vector3.ZERO, "GateLeaf%d" % (0 if side < 0 else 1))
		var hinge := Node3D.new(); hinge.name = "Hinge%d" % (0 if side < 0 else 1)
		hinge.position = W(gp, y0) + Vector3(side * 3.5, 0.05, 0.25); root.add_child(hinge); hinge.add_child(leaf)
		if side > 0: leaf.rotation.y = PI; leaf.position = Vector3.ZERO
		hinge.rotation.y = -side * deg_to_rad(80.0)    # open, against the inside of the palisade
		var sb := StaticBody3D.new(); var cs := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(3.4, 3.4, 0.2)
		cs.shape = bs; cs.position = Vector3(-1.7 if side > 0 else 1.7, 1.7, 0.1); sb.add_child(cs); hinge.add_child(sb)
	placed.append(["gate", gp, 4.0, "the village gate, open by day"])
	_count("gate", 1)

func _named(n: Node3D, at: Vector3) -> Node3D:
	n.position = at; return n

# ---------------------------------------------------------------- the harbour
## the sea wall running on as the breakwater: a causeway of big drystone blocks (20 cm voxels), battered sides down to the
## seabed, a level top, laid along the plan's curve
func _harbour() -> void:
	var pts := [Vector2(80, 82), Vector2(92, 76), Vector2(100, 70), Vector2(106, 62), Vector2(116, 64), Vector2(126, 70), Vector2(131, 78)]
	var curve := Curve2D.new()
	for i in pts.size():
		var tn: Vector2 = (pts[mini(i + 1, pts.size() - 1)] - pts[maxi(i - 1, 0)]) * 0.3
		curve.add_point(pts[i], -tn, tn)
	curve.bake_interval = 0.2
	var baked := curve.get_baked_points()
	var v := VBox.new(0.2); var S := 0.2; var top := 0.9
	var done := {}
	for i in baked.size():
		var p: Vector2 = baked[i]; var d: Vector2 = (baked[mini(i + 1, baked.size() - 1)] - baked[maxi(i - 1, 0)]).normalized()
		var side := Vector2(-d.y, d.x)
		for s in range(-9, 10):
			var q: Vector2 = p + side * s * S * 0.5
			var w := W(q, 0)
			var gi := Vector3i(floori(w.x / S), 0, floori(w.z / S))
			var key := Vector2i(gi.x, gi.z)
			if done.has(key): continue
			done[key] = true
			var off := absf(s * S * 0.5)
			var tp := top if off <= 1.2 else top - (off - 1.2) * 1.6     # battered sides
			tp = maxf(tp, H(q) + 0.1) if off <= 1.2 else tp
			var low := minf(H(q), 0.0) - 1.6
			for y in range(floori(low / S), floori(tp / S)):
				var course := y + (gi.x + gi.z * 3) / 3
				var r := float(hash(Vector3i(gi.x / 3, y, gi.z / 2)) % 100) / 100.0
				var c: Color = VoxelProps.C.stone_d if r < 0.3 else (VoxelProps.C.stone_l if r > 0.8 else (VoxelProps.C.lichen if r > 0.72 and y * S > 0.2 else VoxelProps.C.stone))
				if y * S < 0.3 and y * S > -0.2 and r > 0.5: c = Color8(84, 92, 70)   # weed at the tide line
				v.put(Vector3i(gi.x, y, gi.z), c, 0.05, course)
		if i % 10 == 0 and i + 10 < baked.size():   # colliders: the walkable top, in 2 m pieces
			var b: Vector2 = baked[i + 10]; var mid := (p + b) * 0.5
			VBox.collider(root, W(mid, top - 0.5), Vector3(p.distance_to(b) + 0.3, 1.0, 2.6), -atan2(b.y - p.y, b.x - p.x))
	root.add_child(v.node(Vector3.ZERO, "SeaWall"))
	_lighthouse(Vector2(132.5, 80.5))
	_pier()
	_boat(Vector2(96, 92), -0.3, 7.0, 1)
	_boat(Vector2(76, 94), 0.4, 5.5, 2)
	_ship(Vector2(91.5, 104.3), 0.0)
	placed.append(["sea wall", Vector2(106, 66), 0.0, "the sea wall and breakwater"])
	_count("sea wall voxels", v.cells.size())

## the harbour master's lighthouse at the breakwater's end: a round drystone tower with a door and slit windows, the
## lantern room on top behind glass and iron, its light lit at dusk
func _lighthouse(p: Vector2) -> void:
	var v := VBox.new(0.1); var C := VoxelProps.C; var R := 1.8; var top := 9.0
	for i in range(-20, 21):
		for k in range(-20, 21):
			var d := Vector2(i + 0.5, k + 0.5).length() * 0.1
			var r_at := func(y: float) -> float: return R - y * 0.04
			for y in range(-10, int(top / 0.1)):
				var rr: float = r_at.call(y * 0.1)
				if d > rr or d < rr - 0.3: continue
				var ang := atan2(k, i)
				if y >= 0 and y < 22 and absf(ang - PI / 2) < 0.28: continue                       # the door, toward the breakwater
				if (y % 30 > 18 and y % 30 < 26) and absf(fmod(ang + TAU, PI) - 1.0) < 0.06: continue    # slit windows
				var row := y / 4; var r := float(hash(Vector3i(int(ang * 9 + row % 2), row, 0)) % 100) / 100.0
				var lime := Color8(212, 204, 182) if r > 0.12 else Color8(190, 181, 158)
				v.put(Vector3i(i, y, k), (C.stone_d if r < 0.5 else C.stone) if y < 8 else (C.tar if (y > 40 and y < 52) else lime), 0.05, row)
	for i in range(-21, 22):   # the gallery floor and its rail, the lantern room, the cap
		for k in range(-21, 22):
			var d := Vector2(i + 0.5, k + 0.5).length() * 0.1
			if d < 2.0: v.put(Vector3i(i, int(top / 0.1), k), C.stone_d)
			if d < 2.05 and d > 1.95: for y in 8: if y == 7 or (i + k) % 4 == 0: v.put(Vector3i(i, int(top / 0.1) + 1 + y, k), C.iron)
			if d < 1.0 and d > 0.9:
				for y in 16: if (i * 3 + k) % 5 == 0 or y == 0 or y == 15: v.put(Vector3i(i, int(top / 0.1) + 1 + y, k), C.iron)
			if d < 1.15: for y in 6: if d < 1.15 - y * 0.18: v.put(Vector3i(i, int(top / 0.1) + 17 + y, k), C.iron_l)
	var mi := v.node(Vector3.ZERO, "Lighthouse"); root.add_child(mi); mi.position = W(p, 0.8)
	var glass := MeshInstance3D.new(); var cm := CylinderMesh.new(); cm.top_radius = 0.9; cm.bottom_radius = 0.9; cm.height = 1.4; glass.mesh = cm
	var gm := StandardMaterial3D.new(); gm.albedo_color = Color(0.85, 0.8, 0.6, 0.35); gm.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	gm.emission_enabled = true; gm.emission = Color(1.0, 0.75, 0.4); gm.emission_energy_multiplier = 0.0; glass.material_override = gm
	glass.name = "LighthouseGlass"; mi.add_child(glass); glass.position = Vector3(0, top + 0.8, 0)
	var lamp := OmniLight3D.new(); lamp.name = "LighthouseLamp"; lamp.light_color = Color(1, 0.8, 0.5); lamp.light_energy = 0.0; lamp.omni_range = 22
	lamp.position = Vector3(0, top + 0.8, 0); mi.add_child(lamp)
	VBox.collider(root, W(p, 0.8 + top * 0.5), Vector3(3.4, top, 3.4))
	placed.append(["lighthouse", p, 2.0, "the harbour master's lighthouse"])

## the pier, built as a timber pier is (the plan's two rectangles, a T): bents of paired piles every 2.4 m driven into the
## seabed, X-braced below the deck and topped by a cap beam; four stringers along the caps; deck planks laid across them
## edge to edge (a dark seam between, never a gap), each plank its own weathered tone and length, nailed at each stringer;
## a curb along both edges; a stone abutment where it leaves the beach. At the head: mooring piles standing proud along
## the ship's side with rope fenders, bollards with coiled rope, mooring lines to the ship, a ladder down to the boats on
## the north side, the lamp post. 5 cm voxels throughout.
const DECK := 1.0
func _pier() -> void:
	_pier_run(Vector2(87.5, 79.0), Vector2(87.5, 99.5), 2.2, 41, false)
	_pier_run(Vector2(78.0, 100.6), Vector2(104.0, 100.6), 2.2, 42, true)
	var lamp := MeshInstance3D.new(); lamp.mesh = VoxelProps.mesh("lamp", 0.4, 0.4); lamp.material_override = Vox.grain_material(0.05)
	_add(lamp, W(Vector2(88.7, 99.2), DECK), PI)
	var fl := VoxelProps.flame(0.08); fl.name = "PierLamp"; lamp.add_child(fl); fl.position = Vector3(0.35, 1.8, 0)

func _pier_run(a: Vector2, b: Vector2, w: float, seed_: int, head: bool) -> void:
	var v := VBox.new(0.05); var C := VoxelProps.C; var L := a.distance_to(b); var d := (b - a).normalized()
	var yaw := -atan2(d.y, d.x)
	var at := func(x: float, z: float) -> Vector2: return a + d * x + Vector2(-d.y, d.x) * z   # local (along, across) -> plan
	var tones := [C.drift, C.drift_l, C.drift_d, Color8(150, 132, 108), C.tar_l]
	var hw := w * 0.5
	# deck planks across the run, 25 cm wide, butted: the first voxel of each plank darker on top (the seam)
	var plank := 0; var x := 0.0
	while x < L:
		var r := RandomNumberGenerator.new(); r.seed = seed_ * 1000 + plank
		var tone: Color = tones[r.randi() % tones.size()]
		var over_l := r.randi_range(0, 2) * 0.05; var over_r := r.randi_range(0, 2) * 0.05   # ragged ends
		v.box(Vector3(x, DECK - 0.1, -hw - over_l), Vector3(x + 0.25, DECK, hw + over_r), tone, 0.03, plank)
		v.box(Vector3(x, DECK - 0.05, -hw - over_l), Vector3(x + 0.05, DECK, hw + over_r), tone.darkened(0.35), 0.0)
		for sz in [-0.85, -0.3, 0.3, 0.85]:   # nail heads over the stringers, flush, rusted into the wood
			if plank % 2 == 0: v.put(Vector3i(int((x + 0.15) / 0.05), int(DECK / 0.05) - 1, int(floor(sz / 0.05))), tone.darkened(0.25).lerp(C.rust, 0.3), 0.0)
		if r.randf() < 0.12: v.box(Vector3(x + 0.1, DECK - 0.05, -0.4), Vector3(x + 0.2, DECK, 0.1), tone.darkened(0.2), 0.0)   # a worn knot
		x += 0.25; plank += 1
	# curbs along both edges (open at the ladder and the gangplank on the head)
	for s in [-1, 1]:
		var cx := 0.0
		while cx < L:
			var seg := minf(2.4, L - cx)
			var skip: bool = head and ((s < 0 and absf(cx - 9.6) < 0.1) or (s > 0 and absf(cx - 12.0) < 0.1))
			if not skip: v.box(Vector3(cx, DECK, s * hw - 0.075), Vector3(cx + seg - 0.05, DECK + 0.15, s * hw + 0.075), C.tar, 0.04)
			cx += 2.4
	# stringers under the planks
	for sz in [-0.85, -0.3, 0.3, 0.85]: v.box(Vector3(0, DECK - 0.3, sz - 0.075), Vector3(L, DECK - 0.1, sz + 0.075), C.tar_d, 0.03)
	# bents: pile pairs, a cap beam, X braces; mooring piles proud of the deck along the head's ship side
	var bx := 0.3
	var bent := 0
	while bx < L:
		var ground: float = H(at.call(bx, 0.0))
		var foot := ground - 1.2
		v.box(Vector3(bx - 0.1, DECK - 0.5, -hw - 0.1), Vector3(bx + 0.15, DECK - 0.3, hw + 0.1), C.tar_d, 0.03)   # the cap
		for s in [-1, 1]:
			var pz: float = s * (hw - 0.2)
			v.blob(Vector3(bx + 0.025, (foot + DECK - 0.5) * 0.5, pz), Vector3(0.15, (DECK - 0.5 - foot) * 0.5, 0.15), C.tar if bent % 2 else C.tar_d, 0.05, bent)
			v.box(Vector3(bx - 0.1, -0.15, pz - 0.15), Vector3(bx + 0.15, 0.25, pz + 0.15), Color8(84, 92, 70), 0.08)   # weed at the tide line
		if DECK - 0.5 - ground > 0.6:
			v.beam(Vector3(bx, DECK - 0.55, -hw + 0.2), Vector3(bx, maxf(ground, -0.6), hw - 0.2), 0.1, C.tar_d)
			v.beam(Vector3(bx, DECK - 0.55, hw - 0.2), Vector3(bx, maxf(ground, -0.6), -hw + 0.2), 0.1, C.tar_d)
		if head and bent % 2 == 0 and bx > 8.0:   # mooring piles on the ship's side (+z: south), rope fenders on them
			v.blob(Vector3(bx, (foot + DECK + 0.9) * 0.5, hw + 0.2), Vector3(0.17, (DECK + 0.9 - foot) * 0.5, 0.17), C.tar, 0.05, bent)
			v.blob(Vector3(bx, DECK - 0.2, hw + 0.4), Vector3(0.22, 0.25, 0.12), C.rope, 0.08)
		bent += 1; bx += 2.4
	if head:   # bollards with coiled rope, the ladder down on the north side
		for bxp in [10.8, 15.6, 20.4]:
			v.blob(Vector3(bxp, DECK + 0.25, hw - 0.35), Vector3(0.14, 0.25, 0.14), C.iron, 0.04)
			v.box(Vector3(bxp - 0.18, DECK + 0.45, hw - 0.53), Vector3(bxp + 0.18, DECK + 0.52, hw - 0.17), C.iron, 0.0)
			for k in 18:
				var t := k * TAU / 18.0
				v.put(Vector3i(int((bxp + 0.55 + cos(t) * 0.22) / 0.05), int(DECK / 0.05), int(floor((hw - 0.5 + sin(t) * 0.22) / 0.05))), C.rope, 0.05)
		for y in 9:   # the ladder at 9.6 m on the north side (-z), down to the water
			var ly := DECK - 0.25 - y * 0.3
			v.box(Vector3(9.55, ly, -hw - 0.25), Vector3(10.15, ly + 0.05, -hw - 0.15), C.drift_d)
		for lx in [9.5, 10.15]: v.box(Vector3(lx, -0.6, -hw - 0.25), Vector3(lx + 0.06, DECK + 0.6, -hw - 0.15), C.drift_d)
	else:   # the abutment: big shore stones under the first 2.5 m, up to the deck
		for k in 14:
			var r := RandomNumberGenerator.new(); r.seed = seed_ + k * 17
			var c := Vector3(r.randf_range(0.0, 2.5), 0, r.randf_range(-hw, hw))
			var gy := H(at.call(c.x, c.z))
			c.y = (gy + DECK - 0.1) * 0.5
			v.blob(c, Vector3(r.randf_range(0.4, 0.6), maxf(0.2, (DECK - 0.1 - gy) * 0.5 + 0.2), r.randf_range(0.35, 0.55)), C.stone if k % 3 else C.stone_d, 0.06, k)
	var mi := v.node(Vector3.ZERO, "Pier"); root.add_child(mi); mi.position = W(a, 0.0); mi.rotation.y = yaw
	VBox.collider(root, W((a + b) * 0.5, DECK - 0.15), Vector3(L, 0.3, w + 0.1), yaw)
	_count("pier voxels", v.cells.size())

## a hull's half-breadth at a point along it (t 0 stern .. 1 bow) and height up from the keel (0..1)
func _half(t: float, h: float, beam: float) -> float:
	var along := pow(sin(PI * clampf(t * 0.92 + 0.04, 0, 1)), 0.6) * (1.0 - 0.35 * pow(t, 3))
	return beam * 0.5 * along * (0.35 + 0.65 * sqrt(h))

## a clinker fishing boat at anchor: planked hull (tarred below, painted strake at the gunwale), bottom boards just above
## its waterline (the sea is one flat surface: nothing inside dips below it), thwarts, a mast with its sail furled
func _boat(c: Vector2, a: float, length: float, seed_: int) -> void:
	var v := VBox.new(0.05); var C := VoxelProps.C; var beam := length * 0.32; var depth := length * 0.13
	var paint: Color = [Color8(92, 116, 128), Color8(138, 88, 72), Color8(96, 122, 104)][seed_ % 3]
	var nl := int(length / 0.05); var nh := int(depth / 0.05)
	for i in nl:
		var t := float(i) / nl
		var keel := 0.06 * pow((t - 0.5) * 2.0, 4) * 6.0      # the sheer: ends rise
		for j in nh + 1:
			var h := float(j) / nh
			var hb := _half(t, h, beam)
			for s in [-1, 1]:
				var z: float = s * hb
				var y := j * 0.05 + keel
				var col: Color = paint if j >= nh - 1 else (C.tar if j < nh * 0.5 else (C.tar_l if j % 3 == 0 else C.drift_d))
				v.put(Vector3i(i - nl / 2, int(y / 0.05), int(round(z / 0.05))), col, 0.04, seed_)
				if absf(hb) < 0.06: break
		for k in range(-int(_half(t, 0.0, beam) / 0.05), int(_half(t, 0.0, beam) / 0.05) + 1):   # the keel's bottom
			v.put(Vector3i(i - nl / 2, int(keel / 0.05), k), C.tar, 0.03)
		var wl := 0.3 * depth + 0.05                      # bottom boards just above the waterline
		var bb := _half(t, 0.3, beam) - 0.06
		if t > 0.12 and t < 0.88: for k in range(-int(bb / 0.05), int(bb / 0.05) + 1): v.put(Vector3i(i - nl / 2, int(wl / 0.05) + 1, k), C.drift if (i / 3) % 2 else C.drift_d, 0.03)
		if i % int(nl / 4.0) == 0 and t > 0.15 and t < 0.85:   # thwarts
			var tb := _half(t, 0.7, beam)
			for k in range(-int(tb / 0.05), int(tb / 0.05) + 1): for di in 4: v.put(Vector3i(i - nl / 2 + di, int(depth * 0.7 / 0.05), k), C.drift, 0.03)
	v.box(Vector3(-0.08, depth * 0.3, -0.08), Vector3(0.08, depth + length * 0.55, 0.08), C.drift_d)   # the mast
	v.box(Vector3(-length * 0.3, depth + 0.6, -0.04), Vector3(length * 0.25, depth + 0.7, 0.04), C.drift_d)   # the boom
	var mi := v.node(Vector3.ZERO, "Boat"); root.add_child(mi)
	mi.position = W(c, -0.3 * depth); mi.rotation.y = -a
	# the furled sail: cloth, so low-poly, lashed along the boom
	var sail := MeshInstance3D.new(); var cm := CapsuleMesh.new(); cm.radius = 0.14; cm.height = length * 0.5; cm.radial_segments = 6; cm.rings = 2
	sail.mesh = cm; var sm := StandardMaterial3D.new(); sm.albedo_color = Color8(176, 160, 130); sm.roughness = 1.0; sail.material_override = sm
	sail.rotation.z = PI / 2; sail.position = Vector3(-length * 0.03, depth + 0.82, 0); mi.add_child(sail)
	placed.append(["boat", c, length * 0.5, "a fishing boat at anchor"])
	_count("boats", 1)

## the last ship out: the trader's brig from Hollin's Cross, moored along the pier's head (16 m, 10 cm voxels): a deep
## tarred hull with a painted band, a deck with a raised stern castle and its cabin, rails, two masts with their yards and
## sails furled, the rigging as rope lines, and a gangplank to the pier
func _ship(c: Vector2, a: float) -> void:
	var v := VBox.new(0.1); var C := VoxelProps.C; var L := 16.0; var beam := 4.6; var depth := 3.2
	var nl := int(L / 0.1); var nh := int(depth / 0.1); var band := Color8(150, 112, 62)
	var deck_y := 2.4
	for i in nl:
		var t := float(i) / nl
		var rise := 0.6 * pow(absf(t - 0.45) * 2.0, 3)
		for j in nh + 1:
			var h := float(j) / nh
			var hb := _half(t, h, beam)
			for s in [-1, 1]:
				var col: Color = C.tar_d if j < 12 else (band if j > nh - 4 and j < nh - 1 else (C.tar if j % 4 else C.tar_l))
				v.put(Vector3i(i - nl / 2, j + int(rise / 0.1) - 10, int(round(s * hb / 0.1))), col, 0.03, 9)
		var db := _half(t, deck_y / depth, beam)
		for k in range(-int(db / 0.1), int(db / 0.1) + 1):   # the deck
			v.put(Vector3i(i - nl / 2, int(deck_y / 0.1) - 10, k), C.drift if (k / 2) % 2 else C.drift_d, 0.03)
			if t < 0.22: v.put(Vector3i(i - nl / 2, int(deck_y / 0.1) - 10 + 10, k), C.drift_d, 0.03)   # the stern castle's deck
		for s in [-1, 1]:   # rails
			if s < 0 and i - nl / 2 >= 5 and i - nl / 2 <= 15 and t >= 0.22: continue   # the gangway: a gap in the rail where the plank comes aboard
			for y in 5: if y == 4 or i % 6 == 0: v.put(Vector3i(i - nl / 2, int(deck_y / 0.1) - 10 + 1 + y + (10 if t < 0.22 else 0), int(round(s * db / 0.1))), C.tar_l, 0.03)
	for i in int(0.22 * nl):   # the stern castle's walls and a door forward
		var t := float(i) / nl; var db := _half(t, deck_y / depth, beam) - 0.2
		for y in 10:
			for s in [-1, 1]: v.put(Vector3i(i - nl / 2, int(deck_y / 0.1) - 9 + y, int(round(s * db / 0.1))), C.board_d, 0.03)
	for k in range(-18, 19):
		for y in 10:
			if absi(k) < 4 and y < 8: continue
			v.put(Vector3i(int(0.22 * nl) - nl / 2, int(deck_y / 0.1) - 9 + y, k), C.board, 0.03)
	for mx in [-1.5, 3.5]:   # two masts with yards
		v.box(Vector3(mx - 0.12, deck_y - 1.0, -0.12), Vector3(mx + 0.12, deck_y + 11.0, 0.12), C.drift_d)
		for yy in [deck_y + 4.0, deck_y + 8.0]: v.box(Vector3(mx - 0.08, yy, -3.0), Vector3(mx + 0.08, yy + 0.16, 3.0), C.drift_d)
	v.box(Vector3(L * 0.45, deck_y + 0.4, -0.08), Vector3(L * 0.45 + 3.0, deck_y + 0.56, 0.08), C.drift_d)   # the bowsprit
	var mi := v.node(Vector3.ZERO, "LastShip"); root.add_child(mi)
	mi.position = W(c, -0.0); mi.rotation.y = -a
	# sails furled on the yards (cloth, low-poly) and the rigging (rope lines)
	var sm := StandardMaterial3D.new(); sm.albedo_color = Color8(186, 170, 140); sm.roughness = 1.0
	for mx in [-1.5, 3.5]:
		for yy in [deck_y + 4.0, deck_y + 8.0]:
			var s := MeshInstance3D.new(); var cm := CapsuleMesh.new(); cm.radius = 0.22; cm.height = 5.6; cm.radial_segments = 6; cm.rings = 2
			s.mesh = cm; s.material_override = sm; s.rotation.x = PI / 2; s.position = Vector3(mx, yy + 0.32, 0); mi.add_child(s)
	var rope := ImmediateMesh.new(); rope.surface_begin(Mesh.PRIMITIVE_LINES)
	for mx in [-1.5, 3.5]:
		for k in 5:
			for s in [-1, 1]:
				rope.surface_add_vertex(Vector3(mx, deck_y + 10.5, 0)); rope.surface_add_vertex(Vector3(mx - 1.2 + k * 0.6, deck_y + 0.5, s * 2.2))
	rope.surface_add_vertex(Vector3(3.5, deck_y + 10.8, 0)); rope.surface_add_vertex(Vector3(L * 0.45 + 3.0, deck_y + 0.5, 0))
	rope.surface_add_vertex(Vector3(-1.5, deck_y + 10.8, 0)); rope.surface_add_vertex(Vector3(3.5, deck_y + 10.8, 0))
	rope.surface_end()
	var rm := MeshInstance3D.new(); rm.mesh = rope; var rmat := StandardMaterial3D.new(); rmat.albedo_color = Color8(60, 52, 44); rmat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	rm.material_override = rmat; mi.add_child(rm)
	# collision: the hull as a box, the deck walkable, the stern castle
	var sb := StaticBody3D.new(); mi.add_child(sb)
	var top := (int(deck_y / 0.1) - 10 + 1) * 0.1   # the deck's walking surface (the deck voxels' top)
	for bx in [[Vector3(0, top - 1.0, 0), Vector3(L * 0.85, 2.0, beam * 0.75)], [Vector3(-L * 0.39, top + 0.5, 0), Vector3(L * 0.2, 1.0, beam * 0.7)]]:
		var cs := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = bx[1]; cs.shape = bs; cs.position = bx[0]; sb.add_child(cs)
	for rail in [[-L * 0.42, L * 0.43, 1], [-L * 0.42, 0.5, -1], [1.5, L * 0.43, -1]]:   # the rails: you cannot walk off, but in at the gangway
		var cs := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(rail[1] - rail[0], 1.0, 0.15); cs.shape = bs
		cs.position = Vector3((rail[0] + rail[1]) * 0.5, top + 0.5, rail[2] * beam * 0.375); sb.add_child(cs)
	# the gangplank: from the pier's boards (1.2 m in from its edge) through the gap in the rail onto the deck, a gentle
	# slope you walk up, with cleats across it for the feet and a rope rail on the sea side
	var z0 := -3.85; var z1 := -1.9; var rise := top - (DECK + 0.08); var run := z1 - z0; var lp := sqrt(rise * rise + run * run)
	var gp := VBox.new(0.05)
	gp.box(Vector3(-0.4, 0, 0), Vector3(0.4, 0.08, lp), C.drift_d)
	for k in int(lp / 0.3): gp.box(Vector3(-0.38, 0.08, 0.15 + k * 0.3), Vector3(0.38, 0.12, 0.2 + k * 0.3), C.tar_d)
	var g := gp.node(Vector3.ZERO, "Gangplank"); mi.add_child(g); g.position = Vector3(1.0, DECK, z0); g.rotation.x = -atan2(rise, run)
	var gsb := StaticBody3D.new(); var gcs := CollisionShape3D.new(); var gbs := BoxShape3D.new(); gbs.size = Vector3(0.8, 0.12, lp + 0.9)
	# the collision runs on under the pier's boards, so there is no lip to stub a toe on
	gcs.shape = gbs; gcs.position = Vector3(0, 0.0, (lp - 0.9) * 0.5); gsb.add_child(gcs); g.add_child(gsb)
	mi.set_meta("deck_y", deck_y)
	placed.append(["ship", c, 8.0, "the last ship out"])
	_count("ship voxels", v.cells.size())

# ---------------------------------------------------------------- the square's well
func _well() -> void:
	var p: Vector2 = fh.WELL; var y0 := H(p)
	var mi := _mesh_node(VoxelProps.mesh("well", 2.25, 1.8), 0.05, W(p, y0), 0.3, "Well")
	VBox.collider(root, W(p, y0 + 0.4), Vector3(1.6, 0.8, 1.6), 0.3)
	# the square is worn bare round the well (the paths mask paints it); round the well head itself an apron of flat
	# stones, laid flush, where people stand to draw water and spill it
	var v := VBox.new(0.05); var C := VoxelProps.C
	for i in range(-50, 51):
		for k in range(-50, 51):
			var d := Vector2(i + 0.5, k + 0.5).length() * 0.05
			if d < 0.8 or d > 2.4 + 0.15 * sin(atan2(k, i) * 5.0): continue
			var stone := Vector2i(int(floor((d - 0.8) / 0.4)), int(floor(atan2(k, i) * (3.0 + d * 2.0))))
			var r := float(hash(stone) % 100) / 100.0
			var seam := fmod(d - 0.8, 0.4) < 0.05 or fmod(atan2(k, i) * (3.0 + d * 2.0) + 10.0, 1.0) < 0.06
			var c: Color = C.stone_d if r < 0.3 else (C.stone_l if r > 0.75 else (C.lichen if r > 0.68 else C.stone))
			var gy := roundi((H(p + Vector2(i + 0.5, k + 0.5) * 0.05) - y0) / 0.05)   # laid on the ground as it falls
			v.put(Vector3i(i, gy, k), c.darkened(0.3) if seam else c, 0.03, stone.x); v.put(Vector3i(i, gy - 1, k), c.darkened(0.2), 0.0)
	var ap := v.node(Vector3.ZERO, "WellApron"); root.add_child(ap); ap.position = W(p, y0 + 0.03)
	placed.append(["well", p, 1.0, "the village well, the old spring"])

# ---------------------------------------------------------------- plots: walled gardens and fenced yards
## the well-off's gardens behind a drystone wall with a gate at the back; the poor's yards behind a wattle fence
func _plots() -> void:
	var wattle: Dictionary = BuildingKit.fittings().get("wattle", {})
	var wm: ArrayMesh = Vox.mesh(wattle, Vector3i.ZERO, Vector3.ZERO, 0.05) if not wattle.is_empty() else null
	var wlen := 2.0
	if wm: wlen = wm.get_aabb().size.x
	for pl in fh.PLAN.plots:
		var c := Vector2(pl.x, pl.y); var a: float = pl.a; var hw: float = pl.w * 0.5; var hh: float = pl.h * 0.5
		var P := func(u: float, vv: float) -> Vector2: return c + Vector2(u, vv).rotated(a)
		var walled: bool = pl.label == "walled garden"
		var sides := [[P.call(-hw, -hh), P.call(-hw, hh)], [P.call(-hw, hh), P.call(hw, hh)], [P.call(hw, hh), P.call(hw, -hh)]]
		for si in sides.size():
			var p0: Vector2 = sides[si][0]; var p1: Vector2 = sides[si][1]
			var dir := (p1 - p0).normalized()
			if si == 0: p0 += dir * 0.6
			if si == 2: p1 -= dir * 0.6
			var L := p0.distance_to(p1)
			if walled:
				var v := VBox.new(0.1); var gate_at := L * 0.5
				for k in int(L / 0.1):
					var x := k * 0.1
					if si == 1 and absf(x - gate_at) < 0.6: continue
					var q := p0 + dir * x; var yb := H(q) - H(p0)
					for y in range(-3, 10 + (1 if (k / 4) % 2 else 0)):
						for z in 4:
							var r := float(hash(Vector3i(k / 4, y / 2 + (k / 4) % 2, si)) % 100) / 100.0
							v.put(Vector3i(k, y + int(yb / 0.1), z - 2), VoxelProps.C.stone_d if r < 0.3 else (VoxelProps.C.stone_l if r > 0.8 else VoxelProps.C.stone), 0.05)
				var wmi := _mesh_node(v.mesh(), 0.1, W(p0, H(p0)), -atan2(dir.y, dir.x), "GardenWall")
				VBox.collider(root, W((p0 + p1) * 0.5, H((p0 + p1) * 0.5) + 0.5), Vector3(L, 1.0, 0.4), -atan2(dir.y, dir.x))
				if si == 1:   # the garden gate, a little boarded door
					var gv := VBox.new(0.05)
					for k in 6: gv.box(Vector3(-0.55 + k * 0.19, 0, -0.03), Vector3(-0.38 + k * 0.19, 0.95, 0.03), VoxelProps.C.tar)
					gv.box(Vector3(-0.55, 0.2, 0.03), Vector3(0.55, 0.3, 0.07), VoxelProps.C.oak_d); gv.box(Vector3(-0.55, 0.7, 0.03), Vector3(0.55, 0.8, 0.07), VoxelProps.C.oak_d)
					var gq := p0 + dir * gate_at
					_mesh_node(gv.mesh(), 0.05, W(gq, H(gq)), -atan2(dir.y, dir.x), "GardenGate")
			elif wm:
				var n := maxi(1, int(round(L / wlen)))
				for k in n:
					var q0 := p0 + dir * (L * k / n); var q1 := p0 + dir * (L * (k + 1) / n)
					var fm := _mesh_node(wm, 0.05, W(q0, H((q0 + q1) * 0.5)), -atan2(dir.y, dir.x), "Wattle")
					fm.scale.x = (L / n) / wlen
				VBox.collider(root, W((p0 + p1) * 0.5, H((p0 + p1) * 0.5) + 0.5), Vector3(L, 1.0, 0.2), -atan2(dir.y, dir.x))
		placed.append(["plot", c, 0.0, pl.label])
		_count("plots", 1)

# ---------------------------------------------------------------- the field and the vegetable plots
## the infield's fence (rails on posts, a gate gap where the field lane comes in) and its barley (flora: low-poly tufts
## that sway); the vegetable plots in rows of cabbages and beans (voxels, they are solid heads)
func _field() -> void:
	var v := VBox.new(0.05); var C := VoxelProps.C
	var corners := [Vector2(14, 14), Vector2(37, 14), Vector2(37, 34), Vector2(14, 34)]
	for e in 4:
		var a: Vector2 = corners[e]; var b: Vector2 = corners[(e + 1) % 4]; var n := int(a.distance_to(b) / 2.0)
		for k in n:
			var p0 := a.lerp(b, float(k) / n); var p1 := a.lerp(b, float(k + 1) / n)
			if absf(p0.x - 37) < 0.1 and absf((p0.y + p1.y) * 0.5 - 27) < 1.6: continue   # the field gate
			var fv := VBox.new(0.05); var L := p0.distance_to(p1); var dh := H(p1) - H(p0)
			fv.box(Vector3(0, -0.3, -0.05), Vector3(0.12, 1.15, 0.07), C.drift_d)
			fv.beam(Vector3(0.06, 0.45, 0), Vector3(L, 0.45 + dh, 0), 0.07, C.drift)
			fv.beam(Vector3(0.06, 0.95, 0), Vector3(L, 0.95 + dh, 0), 0.07, C.drift)
			var d := (p1 - p0).normalized()
			_mesh_node(fv.mesh(), 0.05, W(p0, H(p0)), -atan2(d.y, d.x), "FieldFence")
	# barley: thin crossed blades in tufts, swaying
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for b in 3:
		var ang := b * PI / 3.0; var dx := Vector3(cos(ang), 0, sin(ang)) * 0.16
		for q in [[-1, 0], [1, 0], [0.6, 1], [-1, 0], [0.6, 1], [-0.6, 1]]:
			st.set_color(Color8(176, 152, 92).lerp(Color8(206, 184, 120), q[1]))
			st.set_uv(Vector2(0, q[1])); st.add_vertex(dx * q[0] + Vector3(0, q[1] * 0.85, 0))
	var tuft := st.commit()
	var sh := Shader.new(); sh.code = """
shader_type spatial;
render_mode cull_disabled;
void vertex() { vec3 w = (MODEL_MATRIX * vec4(0,0,0,1)).xyz; float s = sin(TIME * 1.6 + w.x * 0.3 + w.z * 0.2) * 0.12 * UV.y; VERTEX.x += s; VERTEX.z += s * 0.5; }
void fragment() { ALBEDO = COLOR.rgb * COLOR.rgb; ROUGHNESS = 1.0; }
"""
	var mat := ShaderMaterial.new(); mat.shader = sh
	var xs := []
	for i in 58:
		for j in 50:
			var p := Vector2(14.5 + i * 0.39 + rng.randf_range(-0.12, 0.12), 14.5 + j * 0.39 + rng.randf_range(-0.12, 0.12))
			if absf(p.x - 37) < 1.0 and absf(p.y - 27) < 2.0: continue
			xs.append(Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3.ONE * rng.randf_range(0.8, 1.2)), W(p, H(p))))
	var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = tuft; mm.instance_count = xs.size()
	for k in xs.size(): mm.set_instance_transform(k, xs[k])
	var mmi := MultiMeshInstance3D.new(); mmi.name = "Barley"; mmi.multimesh = mm; mmi.material_override = mat; mmi.visibility_range_end = 90.0; root.add_child(mmi)
	_count("barley tufts", xs.size())
	# the vegetable plots: cabbages in rows, bean poles at one end
	var cab := VBox.new(0.05)
	cab.blob(Vector3(0, 0.12, 0), Vector3(0.2, 0.14, 0.2), C.leaf, 0.08); cab.blob(Vector3(0, 0.16, 0), Vector3(0.12, 0.12, 0.12), Color8(120, 138, 92), 0.05)
	var cm := cab.mesh(); var cx := []
	for i in 5:
		for j in 9:
			for k in 6:
				var p := Vector2(17.0 + i * 3.0 + k * 0.42, 39.5 + j * 0.75)
				cx.append(Transform3D(Basis(Vector3.UP, rng.randf() * TAU), W(p, H(p) - 0.02)))
	var mm2 := MultiMesh.new(); mm2.transform_format = MultiMesh.TRANSFORM_3D; mm2.mesh = cm; mm2.instance_count = cx.size()
	for k in cx.size(): mm2.set_instance_transform(k, cx[k])
	var mmi2 := MultiMeshInstance3D.new(); mmi2.name = "Cabbages"; mmi2.multimesh = mm2; mmi2.material_override = Vox.grain_material(0.05); root.add_child(mmi2)
	var bv := VBox.new(0.05)
	for k in 7:
		bv.beam(Vector3(k * 0.4, 0, 0), Vector3(k * 0.4 + 0.2, 1.8, 0.0), 0.04, C.drift_d)
		for y in 12: bv.blob(Vector3(k * 0.4 + y * 0.016, 0.2 + y * 0.13, 0.02), Vector3(0.08, 0.07, 0.06), C.leaf_d if y % 2 else C.leaf, 0.08)
	_mesh_node(bv.mesh(), 0.05, W(Vector2(17, 46.2), H(Vector2(17, 46.2))), 0.0, "BeanPoles")
	placed.append(["field", Vector2(25, 24), 0.0, "the infield: barley"]); placed.append(["plots", Vector2(23, 42), 0.0, "the vegetable plots"])
	_count("cabbages", cx.size())

# ---------------------------------------------------------------- the plan's doodads
func _doodads() -> void:
	var items: Dictionary = BuildingKit.fittings()
	var kit_mesh := {}
	for dd in fh.PLAN.doodads:
		var kind: String = dd.kind
		if kind in PROP_SKIP: continue
		if kind in KIT_YARD and int(dd.owner) >= 0: continue
		var p := Vector2(dd.x, dd.y)
		if kind == "chopping block":   # the first weapon's block stands in the smithy's yard, outside its door, where beat 3 needs it
			p = _outside_door(4, 0, 2.6, 1.4)
		elif _in_building(p, 0.4): _count("inside a building, left to the kit"); continue
		var yaw := -float(dd.a) + (PI / 2.0 if dd.get("turn", false) else 0.0) + deg_to_rad(float(dd.get("spin", 0)))
		var y: float = 1.0 if fh._on_pier(p) else H(p)
		var m: ArrayMesh
		var fit := {"barrel": "barrel", "crate": "crate", "bench": "bench", "chest": "chest"}
		if fit.has(kind) and items.has(fit[kind]):   # the kit's own fittings where it has them
			if not kit_mesh.has(kind):
				var cells: Dictionary = items[fit[kind]]; var lo := Vector3i(1 << 20, 1 << 20, 1 << 20); var hi := -lo
				for k in cells: lo = lo.min(k); hi = hi.max(k + Vector3i.ONE)
				kit_mesh[kind] = Vox.mesh(cells, Vector3i.ZERO, Vector3((lo.x + hi.x) * 0.5, (lo.y + hi.y) * 0.5, lo.z), 0.05)
			m = kit_mesh[kind]
		else:
			m = VoxelProps.mesh(kind, float(dd.w), float(dd.h))
		if m == null: push_warning("no voxel prop for " + kind); _count("missing " + kind); continue
		var mi := _mesh_node(m, 0.05, W(p, y), yaw, kind.replace(" ", "_"))
		mi.set_meta("purpose", dd.purpose)
		if not kind in ["washing line", "fruit tree", "flower bed", "manure heap", "haystack"]: _solid(mi, 0.02)
		if kind == "washing line": mi.add_child(VoxelProps.washing_cloth(float(dd.w)))
		if kind == "flower bed": mi.add_child(_flowers(float(dd.w), float(dd.h)))
		if kind == "forge":
			var f := VoxelProps.flame(0.2); f.name = "ForgeFire"; mi.add_child(f); f.position = Vector3(0, 0.82, -0.1)
		if kind == "chopping block": mi.name = "ChoppingBlock"
		placed.append([kind, p, maxf(float(dd.w), float(dd.h)) * 0.5, dd.purpose])
		_count("props")

## is a plan point inside one of the kit's buildings (its plot's footprint, grown by `grow`)
func _in_building(p: Vector2, grow := 0.0) -> bool:
	for k in fh.BUILDINGS.size():
		var pad: Array = fh.pads[k]
		var q: Vector2 = (p - pad[0]).rotated(-pad[2]); var e: Vector2 = pad[1]
		if absf(q.x) < e.x + grow and absf(q.y) < e.y + grow: return true
	return false

## a point out in front of building b's door d: `out` metres from the door, `side` to its right
func _outside_door(b: int, d: int, out: float, side: float) -> Vector2:
	# `out` metres past what the kit built on the door's side (its real footprint), `side` along that wall
	var bd: Dictionary = fh.BUILDINGS[b]; var c := Vector2(bd.x, bd.y); var a: float = bd.a
	var l := (Vector2(bd.doors[d][0], bd.doors[d][1]) - c).rotated(-a)
	var f: Array = bd.get("foot", [-bd.w * 0.5, -bd.h * 0.5, bd.w * 0.5, bd.h * 0.5]); var q: Vector2
	if absf(l.x) / (bd.w * 0.5) > absf(l.y) / (bd.h * 0.5): q = Vector2((f[2] if l.x > 0 else f[0]) + signf(l.x) * (out - 1.4), l.y + side)
	else: q = Vector2(l.x + side, (f[3] if l.y > 0 else f[1]) + signf(l.y) * (out - 1.4))
	return c + q.rotated(a)

## flowers in a bed: flora, so low-poly heads on stalks
func _flowers(w: float, h: float) -> MultiMeshInstance3D:
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for q in [[-0.06, 0.25], [0.06, 0.25], [0.0, 0.33], [-0.06, 0.25], [0.0, 0.33], [0.0, 0.18]]:
		st.set_color(Color.WHITE); st.add_vertex(Vector3(q[0], q[1], 0))
	var m := st.commit()
	var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.use_colors = true; mm.mesh = m; mm.instance_count = 60
	var cols := [Color8(190, 160, 70), Color8(150, 90, 120), Color8(200, 190, 170), Color8(170, 80, 60)]
	for k in 60:
		mm.set_instance_transform(k, Transform3D(Basis(Vector3.UP, rng.randf() * TAU), Vector3(rng.randf_range(-w * 0.45, w * 0.45), 0.0, rng.randf_range(-h * 0.4, h * 0.4))))
		mm.set_instance_color(k, cols[k % 4])
	var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm
	var mat := StandardMaterial3D.new(); mat.vertex_color_use_as_albedo = true; mat.cull_mode = BaseMaterial3D.CULL_DISABLED; mat.roughness = 1.0
	mmi.material_override = mat
	return mmi

# ---------------------------------------------------------------- the woods
## wind-bent coastal pines (lore.md: the far coast's wind-bent pines and gorse): the trunk leans and the crown streams
## away from the sea wind (from the south-east, so they lean north-west); four shapes at 10 cm for the edge, two coarse
## ones at 25 cm for the depth; gorse bushes at the edge; batched by 24 m block with draw distances, solid near the village
func _pine(seed_: int, size: float, tall: float) -> ArrayMesh:
	var v := VBox.new(size); var r := RandomNumberGenerator.new(); r.seed = seed_
	var lean := Vector3(-0.55, 0, -0.45).normalized() * r.randf_range(0.6, 1.4)
	var top := Vector3(0, tall, 0) + lean
	v.beam(Vector3.ZERO + Vector3(0, -0.3, 0), top, maxf(size, 0.3), VoxelProps.C.bark)
	var tiers := r.randi_range(5, 7)
	for k in tiers:   # tiers of needles from a third of the way up, narrowing to a spire, streaming leeward
		var t := 0.3 + 0.62 * float(k) / tiers
		var c := top * t + lean * 0.5 * t
		var rad := lerpf(1.9, 0.45, float(k) / tiers) * r.randf_range(0.85, 1.15)
		v.blob(c + lean * 0.35 * (1.0 - t), Vector3(rad * 1.2, maxf(rad * 0.38, 0.3), rad), Color8(96, 116, 76) if k % 2 == 0 else Color8(110, 128, 84), 0.1, seed_)
	v.blob(top, Vector3(0.35, 0.6, 0.35), Color8(104, 122, 80), 0.1, seed_)
	return v.mesh()

func _woods() -> void:
	var near := [_pine(11, 0.1, 6.5), _pine(12, 0.1, 7.5), _pine(13, 0.1, 5.5), _pine(14, 0.1, 8.0)]
	var far := [_pine(21, 0.25, 7.0), _pine(22, 0.25, 8.0)]
	var gorse := VBox.new(0.1)
	gorse.blob(Vector3(0, 0.3, 0), Vector3(0.9, 0.55, 0.8), Color8(76, 92, 52), 0.12)
	for k in 14: gorse.put(Vector3i(randi_range(-8, 8), randi_range(3, 8), randi_range(-7, 7)), Color8(206, 172, 60))
	var gm := gorse.mesh()
	var blocks := {}   # Vector2i block -> {mesh_index: [Transform3D]}
	var add := func(k: int, t: Transform3D) -> void:
		var b := Vector2i(floori(t.origin.x / 24.0), floori(t.origin.z / 24.0))
		if not blocks.has(b): blocks[b] = {}
		if not blocks[b].has(k): blocks[b][k] = []
		blocks[b][k].append(t)
	var gr := RandomNumberGenerator.new(); gr.seed = 4242
	var trees := 0; var solid := 0
	for pass_ in [[2.6, 0.0, 22.0], [4.0, 22.0, 999.0]]:
		var sp: float = pass_[0]; var y: float = -fh.MARGIN
		while y < 110 + fh.MARGIN:
			var x: float = -fh.MARGIN
			while x < 140 + fh.MARGIN:
				var p := Vector2(x + gr.randf_range(-sp * 0.4, sp * 0.4), y + gr.randf_range(-sp * 0.4, sp * 0.4))
				var dp: float = fh._woods_depth(p)
				if dp >= pass_[1] and dp < pass_[2] and fh._coast_signed(p) > 4.0 and fh._path_dist(p) > 3.0 and fh._palisade_dist(p) > 3.2:
					var t := Transform3D(Basis(Vector3.UP, gr.randf_range(-0.3, 0.3)).scaled(Vector3.ONE * gr.randf_range(0.85, 1.25)), W(p, H(p)))
					add.call(gr.randi() % 4 if dp < 24.0 else 4 + gr.randi() % 2, t); trees += 1
					if dp < 10.0:
						var body := StaticBody3D.new(); var col := CollisionShape3D.new(); var cyl := CylinderShape3D.new(); cyl.radius = 0.35; cyl.height = 4.0
						col.shape = cyl; body.add_child(col); body.position = t.origin + Vector3(0, 2.0, 0); root.add_child(body); solid += 1
					if dp < 6.0 and gr.randf() < 0.5:
						var q := p + Vector2(gr.randf_range(-1.5, 1.5), gr.randf_range(-1.5, 1.5))
						if fh._path_dist(q) > 1.0: add.call(6, Transform3D(Basis(Vector3.UP, gr.randf() * TAU).scaled(Vector3.ONE * gr.randf_range(0.7, 1.2)), W(q, H(q))))
				x += sp
			y += sp
	var meshes := near + far + [gm]
	var ranges := [70.0, 70.0, 70.0, 70.0, 160.0, 160.0, 45.0]
	for b in blocks:
		for k in blocks[b]:
			var xs: Array = blocks[b][k]; var centre := Vector3.ZERO
			for t in xs: centre += t.origin
			centre /= xs.size()
			var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.mesh = meshes[k]; mm.instance_count = xs.size()
			for i in xs.size(): mm.set_instance_transform(i, Transform3D(xs[i].basis, xs[i].origin - centre))
			var mmi := MultiMeshInstance3D.new(); mmi.multimesh = mm; mmi.position = centre
			mmi.material_override = Vox.grain_material(0.25 if k in [4, 5] else 0.1)
			mmi.visibility_range_end = ranges[k]; mmi.visibility_range_end_margin = 8.0
			root.add_child(mmi)
	_count("trees", trees); _count("solid trunks", solid)

## the dress check (part of the city-planning check): every placed thing has a purpose and sits on sensible ground,
## clear of roads and doorways (props only)
func check() -> Array:
	var out := []
	for pl in placed:
		if String(pl[3]).strip_edges() == "": out.append("WHY %s at %s" % [pl[0], pl[1]])
	return out
