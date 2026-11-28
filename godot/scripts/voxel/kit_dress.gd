## The detail pass of the voxel building kit (building_kit.gd calls it after the walls and the roof are stamped, before
## meshing). The kit's pieces are flat: their stones are only colours. This pass works on the whole building's outside,
## so the detail runs across bays and round corners the way a real wall does:
##  - drystone in irregular courses: each stone its own size and tone, the joints between them sunk 10 cm in shadow, and
##    some stones standing 10 cm proud;
##  - big dressed quoins at the corners, alternating long and short, proud on both faces;
##  - round each window and door: dressed jamb stones, a proud sill, a proud tarred ship-timber lintel, the shutters and
##    door painted in the house's faded colour, a little board hood over each outer door;
##  - a footing of big stones round the base, proud of the wall.
## Everything here is only looks: collision stays the builder's boxes.
class_name KitDress
extends RefCounted

const STONE_KEYS := [0x94918a, 0x7a7974, 0xa8a49b, 0x8a8e7d, 0xb6aa91]   # fst, fst_d, fst_l, fst_g, and daub where a corner shows it
const TONES := [   # weathered field and shore stone, with their share of the wall: close tones, as one shore gives
	[Color8(148, 145, 138), 0.30], [Color8(134, 132, 126), 0.20], [Color8(160, 156, 147), 0.15],
	[Color8(152, 145, 133), 0.12], [Color8(140, 142, 143), 0.10], [Color8(140, 143, 130), 0.08], [Color8(120, 118, 112), 0.05]]
const MOSS := Color8(126, 132, 108)
const JOINT := Color8(92, 88, 82)
const DRESSED := Color8(178, 173, 162)
const DRESSED_D := Color8(160, 156, 146)
const TAR := Color8(72, 62, 54)
const TAR_L := Color8(96, 82, 68)
const IRON := Color8(50, 50, 54)
## faded paints for doors and shutters, as poor folk on a salt coast keep them (make_building_kit.py has the same)
const PAINTS := {"tar": Color8(92, 78, 66), "blue": Color8(98, 114, 122), "green": Color8(102, 118, 104),
	"red": Color8(128, 92, 80), "ochre": Color8(150, 132, 96)}

static func _h(a: int, b: int, c: int) -> float:
	var n := (a * 73856093) ^ (b * 19349663) ^ (c * 83492791)
	n = (n ^ (n >> 13)) * 1274126177
	n = n ^ (n >> 16)
	return float(n & 0xffff) / 65536.0

static func _key(c: Color) -> int: return (c.r8 << 16) | (c.g8 << 8) | c.b8

static func _tone(r: float, low: bool) -> Color:
	if low and r < 0.3: return MOSS if r < 0.12 else TONES[5][0]
	var acc := 0.0
	for t in TONES:
		acc += t[1]
		if r < acc: return t[0]
	return TONES[0][0]

## sets: the storeys' voxel sets and the roof's (all in file space voxels); W, D: the footprint; openings: [set, o, d,
## x0, x1, z0, z1, kind] from the builder; plinth: its height; paint: the house's colour; seed: per house
static func dress(sets: Array, W: int, D: int, openings: Array, plinth: int, paint: Color, seed: int) -> void:
	# the courses run round the whole house at the same heights, so they meet at the corners
	var course_of := PackedInt32Array(); var start_of := PackedInt32Array()
	var z := plinth; var c := 0
	course_of.resize(400); start_of.resize(400)
	for zz in plinth: course_of[zz] = -1
	while z < 400:
		var hh := 3 + (0 if _h(c, seed, 1) < 0.35 else (1 if _h(c, seed, 1) < 0.8 else 2))
		for k in hh:
			if z + k < 400: course_of[z + k] = c
		start_of[c] = z; z += hh; c += 1
	# the openings' surrounds are left to their own dressing
	var keep := {}
	for op in openings:
		var o: Vector3i = op[1]; var d: Vector2i = op[2]
		for lx in range(op[3] - 2, op[4] + 3):
			for lz in range(maxi(op[5] - 2, 0), op[6] + 3): keep[BuildingKit._cell(o, d, lx, 0, lz)] = true
	var faces := [[0, Vector2i(0, -1)], [1, Vector2i(1, 0)], [2, Vector2i(0, 1)], [3, Vector2i(-1, 0)]]
	for vs in sets:
		var adds := {}; var sinks := {}
		for k in (vs as Dictionary).keys():
			var q: Vector3i = k
			if q.z < plinth or not _key(vs[k]) in STONE_KEYS: continue
			for f in faces:
				var fi: int = f[0]; var out: Vector2i = f[1]
				var on := (fi == 0 and q.y == 0) or (fi == 1 and q.x == W - 1) or (fi == 2 and q.y == D - 1) or (fi == 3 and q.x == 0)
				if not on or keep.has(q): continue
				var u := q.x if fi % 2 == 0 else q.y; var L := W if fi % 2 == 0 else D
				var cz := course_of[mini(q.z, 399)]; var bottom := q.z == start_of[cz]
				var dist := mini(u, L - 1 - u)
				var qlen := 7 if (cz + fi) % 2 == 0 else 4
				var proud := false; var col: Color; var joint := false
				if dist < qlen + 1:   # a quoin, or the joint just past it
					joint = bottom or dist == qlen
					col = DRESSED if _h(cz, fi, seed) > 0.4 else DRESSED_D; proud = true
				else:
					# stones along the course: lengths 4 to 9, each course offset by its own amount
					var off := int(_h(cz, fi, seed + 7) * 9.0)
					var s := 0; var x := -off; var ln := 0
					while true:
						ln = 4 + int(_h(cz, s, seed + fi * 31) * 6.0)
						if x + ln > u: break
						x += ln; s += 1
					joint = (bottom and _h(s, cz, seed + 23) < 0.7) or u == x
					var r := _h(cz * 131 + s, fi, seed + 3)
					col = _tone(r, q.z < plinth + 8)
					proud = _h(s, cz, seed + fi + 11) < 0.14
				if joint:
					sinks[q] = Vector3i(q.x - out.x, q.y - out.y, q.z)
				else:
					vs[q] = col
					if proud: adds[Vector3i(q.x + out.x, q.y + out.y, q.z)] = col
		for q in sinks:
			var inn: Vector3i = sinks[q]
			if vs.has(inn) and not keep.has(q):
				vs.erase(q); vs[inn] = JOINT
		for q in adds:
			if not vs.has(q): vs[q] = adds[q]
		# the corner columns: where both faces' quoins stand proud, fill the outside corner between them
		for cx in [[0, 0, -1, -1], [W - 1, 0, W, -1], [W - 1, D - 1, W, D], [0, D - 1, -1, D]]:
			for zz in range(plinth, 400):
				var a := Vector3i(cx[2], cx[1], zz); var b := Vector3i(cx[0], cx[3], zz)
				if vs.has(a) and vs.has(b) and vs.has(Vector3i(cx[0], cx[1], zz)): vs[Vector3i(cx[2], cx[3], zz)] = vs[a]
	_openings(openings, paint, seed)
	_footing(sets[0], W, D, plinth, seed)

static func _openings(openings: Array, paint: Color, seed: int) -> void:
	var paint_d := paint.darkened(0.15)
	for op in openings:
		var vs: Dictionary = op[0]; var o: Vector3i = op[1]; var d: Vector2i = op[2]
		var x0: int = op[3]; var x1: int = op[4]; var z0: int = op[5]; var z1: int = op[6]; var kind: String = op[7]
		var cell := func(lx: int, ly: int, lz: int) -> Vector3i: return BuildingKit._cell(o, d, lx, ly, lz)
		# dressed jambs: blocks three high, alternately long and short, light and a little darker
		for lz in range(z0, z1 + 1):
			var b := (lz - z0) / 3; var long := b % 2 == 0
			var col := DRESSED if b % 2 == 0 else DRESSED_D
			for side in [[x0 - 1, -1], [x1 + 1, 1]]:
				for w in (3 if long else 2):
					var lx: int = side[0] + side[1] * w
					var k: Vector3i = cell.call(lx, 0, lz)
					if vs.has(k): vs[k] = JOINT if (lz - z0) % 3 == 0 and w > 0 and lz > z0 else col
		# the lintel: a tarred ship timber, proud of the wall, wider than the opening
		for lx in range(x0 - 3, x1 + 4):
			for lz in [z1 + 1, z1 + 2]:
				var k: Vector3i = cell.call(lx, 0, lz)
				if vs.has(k): vs[k] = TAR if lz == z1 + 1 else TAR_L
				var p: Vector3i = cell.call(lx, -1, lz)
				if not vs.has(p): vs[p] = TAR if lz == z1 + 1 else TAR_L
		if kind != "door":
			for lx in range(x0 - 2, x1 + 3):   # a proud sill stone
				vs[cell.call(lx, -1, z0 - 1)] = DRESSED; vs[cell.call(lx, 0, z0 - 1)] = DRESSED
			# the shutters (on the wall's face, 0.1 m out): painted, plank by plank, with two iron straps each
			for lz in range(z0, z1 + 1):
				for lx in range(x0 - 4, x1 + 5):
					var k: Vector3i = cell.call(lx, -1, lz)
					if not vs.has(k) or (lx >= x0 and lx <= x1): continue
					var strap := lz == z0 + 1 or lz == z1 - 1
					vs[k] = IRON if strap and (lx == x0 - 1 or lx == x1 + 1 or lx == x0 - 2 or lx == x1 + 2) else (paint_d if lx % 2 == 0 else paint)
		elif kind == "door":
			# a hood of boards on two brackets over the door, sloping out, turf on top
			for k in 6:
				var ly := -1 - k; var lz := z1 + 6 - k / 2
				for lx in range(x0 - 3, x1 + 4):
					var p: Vector3i = cell.call(lx, ly, lz)
					if not vs.has(p): vs[p] = TAR_L if (lx - x0) % 3 == 0 else Color8(120, 104, 86)
					var t: Vector3i = cell.call(lx, ly, lz + 1)
					if not vs.has(t) and k < 5: vs[t] = Color8(108, 115, 75) if _h(lx, k, seed) > 0.25 else Color8(88, 92, 62)
			for lx in [x0 - 2, x1 + 2]:
				for k in 5:
					var p: Vector3i = cell.call(lx, -1 - k, z1 + 2 + k)
					if not vs.has(p): vs[p] = TAR
					p = cell.call(lx, -1, z1 + 2 + k)
					if not vs.has(p): vs[p] = TAR

## big footing stones round the base, standing 0.1 m out from the plinth, with gaps between them and moss low down
static func _footing(vs: Dictionary, W: int, D: int, plinth: int, seed: int) -> void:
	var sides := [[Vector2i(0, -1), W, func(u): return Vector2i(u, 0)], [Vector2i(1, 0), D, func(u): return Vector2i(W - 1, u)],
		[Vector2i(0, 1), W, func(u): return Vector2i(W - 1 - u, D - 1)], [Vector2i(-1, 0), D, func(u): return Vector2i(0, D - 1 - u)]]
	for si in sides.size():
		var sd: Array = sides[si]; var out: Vector2i = sd[0]; var L: int = sd[1]; var at: Callable = sd[2]
		for row in 2:
			var u := -1 - row * 3; var s := 0
			while u < L + 1:
				var ln := 5 + int(_h(s, row, seed + si) * 6.0)
				var col := _tone(_h(s, row, seed + si + 40), true).darkened(0.08)
				for uu in range(u + 1, u + ln):
					for zz in range(row * 2, row * 2 + 2):
						if zz >= plinth - 1: continue
						var w: Vector2i = at.call(clampi(uu, 0, L - 1)) + out
						var k := Vector3i(w.x, w.y, zz)
						if not vs.has(k): vs[k] = col
				u += ln; s += 1
