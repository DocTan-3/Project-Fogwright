## Farhallow's props as voxels (5 cm, Vox.CHAR), made in code: the plan's doodads (data/farhallow.json) that the building
## kit's own fittings (kit_fittings.vox: barrel, bench, crate, chest, woodpile, net rack, lantern) do not cover, in the
## kit's faded salt-coast palette. Each prop is built in its own frame: centred on its footprint on the ground, its long
## side along X (the plan's w), its depth along Z (the plan's h), up +Y. Meshes are made once per kind and shared.
## What is not solid stays non-voxel, as the art direction says: the flames, the wash on the line, flowers, hay wisps.
class_name VoxelProps
extends RefCounted

const S := 0.05
static var _cache := {}

# the kit's palette (tools/voxel/make_building_kit.py), sRGB
const C := {
	"tar": Color8(92, 78, 66), "tar_d": Color8(72, 62, 54), "tar_l": Color8(112, 96, 80),
	"drift": Color8(158, 142, 122), "drift_d": Color8(130, 118, 100), "drift_l": Color8(178, 162, 140),
	"board": Color8(146, 108, 70), "board_d": Color8(124, 90, 58), "oak": Color8(104, 76, 50), "oak_d": Color8(78, 56, 36),
	"stone": Color8(148, 145, 138), "stone_d": Color8(122, 121, 116), "stone_l": Color8(168, 164, 155), "lichen": Color8(138, 142, 125),
	"iron": Color8(64, 64, 68), "iron_l": Color8(96, 96, 100), "rust": Color8(120, 78, 52), "soot": Color8(46, 42, 40),
	"rope": Color8(156, 138, 106), "straw": Color8(196, 168, 104), "straw_d": Color8(160, 134, 80), "hay": Color8(176, 160, 100),
	"sack": Color8(170, 152, 120), "sack_d": Color8(146, 128, 98), "soil": Color8(92, 74, 56), "manure": Color8(74, 60, 44),
	"water": Color8(70, 96, 104), "leaf": Color8(84, 104, 62), "leaf_d": Color8(66, 84, 50), "bark": Color8(88, 72, 58),
	"fish": Color8(170, 176, 172), "fish_d": Color8(140, 120, 96), "cloth": Color8(120, 46, 40), "linen": Color8(200, 192, 170),
	"bronze": Color8(150, 112, 62), "coal": Color8(40, 38, 38), "ember": Color8(200, 90, 40), "paper": Color8(214, 204, 176),
	"pear": Color8(176, 170, 80), "apple": Color8(160, 64, 48), "brick": Color8(138, 96, 80),
}

## a prop's mesh by kind (cached); empty if the kind has none here
static func mesh(kind: String, w: float, h: float) -> ArrayMesh:
	var key := "%s_%.2f_%.2f" % [kind, w, h]
	if _cache.has(key): return _cache[key]
	var v := VBox.new(S)
	if not _build(v, kind, w, h): return null
	var m := v.mesh(); _cache[key] = m
	return m

static func _b(v: VBox, x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, c: String, j := 0.05) -> void:
	v.box(Vector3(x0, y0, z0), Vector3(x1, y1, z1), C[c], j)

static func _post(v: VBox, x: float, z: float, h: float, c := "tar", t := 0.1) -> void:
	_b(v, x - t / 2, x + t / 2, 0, h, z - t / 2, z + t / 2, c)

## a stave barrel or tub: radius r, height h, hoops
static func _tub(v: VBox, cx: float, cz: float, r: float, h: float, open := false, fill := "") -> void:
	var n := int(ceil(r / S)) + 1
	for i in range(-n, n + 1):
		for k in range(-n, n + 1):
			var d := Vector2(i + 0.5, k + 0.5).length() * S
			if d > r: continue
			var rim := d > r - S * 1.2
			for y in int(h / S):
				var yy := y * S
				var bulge := r * (1.0 - 0.08 * pow((yy / h - 0.5) * 2.0, 2))
				if d > bulge: continue
				if open and not rim and y > 0:
					if fill != "" and y == int(h / S) - 2: v.put(Vector3i(int(floor(cx / S)) + i, y, int(floor(cz / S)) + k), C[fill], 0.03)
					continue
				var hoop := (y == 2 or y == int(h / S) - 3) and rim
				var stave := (i + k * 3) % 4 == 0
				v.put(Vector3i(int(floor(cx / S)) + i, y, int(floor(cz / S)) + k), C["iron"] if hoop else (C["board_d"] if stave else C["board"]), 0.04)

static func _build(v: VBox, kind: String, w: float, h: float) -> bool:
	var hw := w / 2.0; var hd := h / 2.0
	match kind:
		"bench":   # a plank on two trestles, knee high
			_b(v, -hw, hw, 0.4, 0.45, -0.15, 0.15, "drift")
			for x in [-hw + 0.15, hw - 0.2]: _b(v, x, x + 0.05, 0, 0.4, -0.15, 0.15, "drift_d")
		"barrel":
			_tub(v, 0, 0, 0.3, 0.85)
		"keg":
			_tub(v, 0, 0, 0.2, 0.5)
		"crate":
			_b(v, -hw, hw, 0, 0.75, -hd, hd, "board")
			for x in [-hw, hw - 0.05]: _b(v, x, x + 0.05, 0, 0.75, -hd, hd, "board_d")
			_b(v, -hw, hw, 0.35, 0.4, -hd - 0.025, hd + 0.025, "board_d")
		"chest":
			_b(v, -hw, hw, 0, 0.45, -hd, hd, "oak"); _b(v, -hw, hw, 0.45, 0.55, -hd, hd, "oak_d")
			for x in [-hw + 0.1, hw - 0.15]: _b(v, x, x + 0.05, 0, 0.56, -hd - 0.02, hd + 0.02, "iron")
			_b(v, -0.05, 0.05, 0.3, 0.45, -hd - 0.05, -hd, "iron_l")
		"sacks":
			v.blob(Vector3(-0.15, 0.22, 0), Vector3(0.24, 0.24, 0.2), C["sack"], 0.06)
			v.blob(Vector3(0.18, 0.2, 0.05), Vector3(0.2, 0.22, 0.2), C["sack_d"], 0.06)
			v.blob(Vector3(0.0, 0.5, 0.0), Vector3(0.18, 0.16, 0.16), C["sack"], 0.06)
		"woodpile":   # split logs stacked between two stakes, a board on top against the rain
			for y in 5:
				for x in int(w / 0.15):
					var c := "bark" if (x + y) % 3 else "board"
					v.blob(Vector3(-hw + 0.08 + x * 0.15, 0.08 + y * 0.15, 0), Vector3(0.075, 0.075, hd * 0.95), C[c], 0.08)
			for x in [-hw - 0.03, hw + 0.03]: _post(v, x, 0, 0.9, "tar_d", 0.05)
			_b(v, -hw - 0.05, hw + 0.05, 0.8, 0.85, -hd - 0.05, hd + 0.05, "drift_d")
		"trough":   # a long stone trough, water in it
			var lx := hw; var lz := hd
			_b(v, -lx, lx, 0, 0.55, -lz, lz, "stone")
			_b(v, -lx + 0.1, lx - 0.1, 0.45, 0.55, -lz + 0.1, lz - 0.1, "water", 0.0)
		"washing line":   # two forked posts and a rope; the wash itself is cloth (washing_cloth adds it)
			for x in [-hw, hw - 0.1]:
				_b(v, x, x + 0.1, 0, 1.9, -0.05, 0.05, "drift_d")
				_b(v, x - 0.05, x + 0.15, 1.85, 1.9, -0.05, 0.05, "drift_d")
			_b(v, -hw, hw, 1.8, 1.85, -0.025, 0.025, "rope", 0.02)
		"flower bed":   # a raised bed edged with stones, its soil; the flowers are flora (low-poly)
			_b(v, -hw, hw, 0, 0.2, -hd, hd, "soil")
			for x in int(w / 0.25):
				for side in [-hd, hd - 0.15]: v.blob(Vector3(-hw + 0.12 + x * 0.25, 0.1, side + 0.07), Vector3(0.12, 0.12, 0.1), C["stone"], 0.1)
		"fruit tree":   # a small wind-bent orchard tree, fruit in its crown
			v.beam(Vector3(0, 0, 0), Vector3(0.15, 1.4, 0.1), 0.15, C["bark"])
			v.beam(Vector3(0.15, 1.3, 0.1), Vector3(0.6, 1.9, 0.3), 0.1, C["bark"])
			v.beam(Vector3(0.1, 1.3, 0.1), Vector3(-0.5, 1.8, -0.2), 0.1, C["bark"])
			for k in 6:
				var a := k * TAU / 6.0
				v.blob(Vector3(cos(a) * 0.55 + 0.05, 2.0 + sin(k * 1.7) * 0.2, sin(a) * 0.55), Vector3(0.55, 0.42, 0.55), C["leaf" if k % 2 else "leaf_d"], 0.1)
			v.blob(Vector3(0.05, 2.45, 0), Vector3(0.6, 0.4, 0.6), C["leaf"], 0.1)
			for k in 9:
				var a := k * 2.4
				v.put(Vector3i(int(cos(a) * 18), int(1.9 / S + sin(a * 1.3) * 5), int(sin(a) * 18)), C["pear" if w < 2.21 else "apple"])
		"well":   # a drystone well head, a timber frame over it, roofed in boards, the windlass and bucket
			var r := 0.75
			for i in range(-17, 18):
				for k in range(-17, 18):
					var d := Vector2(i + 0.5, k + 0.5).length() * S
					if d > r or d < r - 0.25: continue
					for y in 16: v.put(Vector3i(i, y, k), C["stone_d" if (i + y / 3 * 2) % 5 == 0 else "stone"], 0.06)
			_b(v, -0.5, 0.5, 0.05, 0.1, -0.5, 0.5, "water", 0.0)
			for x in [-0.9, 0.8]: _b(v, x, x + 0.1, 0, 2.1, -0.05, 0.05, "tar")
			_b(v, -0.9, 0.9, 1.5, 1.6, -0.05, 0.05, "oak_d")
			_b(v, 0.9, 1.05, 1.5, 1.55, -0.02, 0.03, "iron")
			for k in 8:   # a boarded roof, two slopes
				var y := 2.1 + k * 0.05
				_b(v, -1.0, 1.0, y, y + 0.05, -0.45 + k * 0.05, -0.35 + k * 0.05, "drift_d")
				_b(v, -1.0, 1.0, y, y + 0.05, 0.35 - k * 0.05, 0.45 - k * 0.05, "drift_d")
			_b(v, -0.1, 0.1, 0.85, 1.1, -0.1, 0.1, "board")
			_b(v, -0.02, 0.02, 1.1, 1.5, -0.02, 0.02, "rope", 0.0)
		"candles":
			_b(v, -0.2, 0.2, 0, 0.05, -0.2, 0.2, "stone")
			for k in 5: _b(v, -0.15 + k * 0.07, -0.12 + k * 0.07, 0.05, 0.15 + (k % 3) * 0.05, -0.02, 0.02, "linen", 0.0)
		"forge":   # the hearth: a stone table, the fire bed, a hood and chimney up the wall
			_b(v, -hw, hw, 0, 0.8, -hd, hd, "stone")
			_b(v, -hw + 0.2, hw - 0.2, 0.7, 0.82, -hd + 0.2, hd - 0.4, "coal")
			_b(v, -0.25, 0.25, 0.79, 0.84, -0.2, 0.15, "ember", 0.15)
			_b(v, -hw, hw, 1.6, 2.0, hd - 0.7, hd, "stone_d")
			_b(v, -0.4, 0.4, 2.0, 3.2, hd - 0.6, hd, "brick")
			for x in [-hw, hw - 0.15]: _b(v, x, x + 0.15, 0.8, 1.6, hd - 0.4, hd, "stone_d")
		"bellows":   # the great bellows: two boards and the leather between, on a frame, the lever arm up
			_b(v, -hw, hw, 0, 0.6, -0.05, 0.05, "tar_d"); _b(v, -hw, hw, 0, 0.6, hd - 0.2, hd - 0.1, "tar_d")
			_b(v, -hw + 0.1, hw - 0.2, 0.6, 0.65, -hd + 0.1, hd - 0.1, "oak")
			_b(v, -hw + 0.15, hw - 0.25, 0.65, 0.85, -hd + 0.2, hd - 0.2, "fish_d", 0.1)
			_b(v, -hw + 0.1, hw - 0.2, 0.85, 0.9, -hd + 0.1, hd - 0.1, "oak")
			_b(v, hw - 0.2, hw, 0.7, 0.8, -0.05, 0.05, "iron")
			v.beam(Vector3(-hw + 0.1, 0.9, 0), Vector3(-hw + 0.2, 1.8, 0), 0.06, C["oak_d"])
		"coal bin":
			_b(v, -hw, hw, 0, 0.5, -hd, hd, "board_d"); _b(v, -hw + 0.05, hw - 0.05, 0.3, 0.5, -hd + 0.05, hd - 0.05, "coal", 0.15)
		"charcoal":   # a heap of charcoal under a lean-to of boards
			v.blob(Vector3(0, 0, 0), Vector3(hw, 0.55, hd), C["coal"], 0.15)
			_b(v, -hw, hw, 1.0, 1.05, -hd, hd, "drift_d")
			for x in [-hw, hw - 0.08]: for z in [-hd, hd - 0.08]: _b(v, x, x + 0.08, 0, 1.0, z, z + 0.08, "tar_d")
		"slack tub":
			_tub(v, 0, 0, minf(hw, hd), 0.6, true, "water")
		"anvil":   # the anvil on its stump
			_tub(v, 0, 0, 0.26, 0.5)
			_b(v, -0.15, 0.15, 0.5, 0.6, -0.1, 0.1, "iron"); _b(v, -0.3, 0.25, 0.6, 0.75, -0.11, 0.11, "iron")
			_b(v, 0.25, 0.4, 0.65, 0.73, -0.05, 0.05, "iron")
		"tool rack":
			_b(v, -hw, hw, 0.9, 1.0, -0.05, 0.05, "oak_d")
			for k in 6: _b(v, -hw + 0.1 + k * 0.14, -hw + 0.13 + k * 0.14, 0.35, 0.95, -0.03, 0.03, "iron_l" if k % 2 else "iron")
			for x in [-hw, hw - 0.06]: _b(v, x, x + 0.06, 0, 1.2, -0.05, 0.05, "oak_d")
		"swage block":
			_b(v, -0.25, 0.25, 0, 0.35, -0.2, 0.2, "oak_d"); _b(v, -0.22, 0.22, 0.35, 0.5, -0.17, 0.17, "iron")
			_b(v, 0.3, 0.36, 0, 0.7, -0.03, 0.03, "iron")
		"bench vise":
			_b(v, -hw, hw, 0.8, 0.88, -hd, hd, "oak"); for x in [-hw + 0.05, hw - 0.1]: for z in [-hd + 0.05, hd - 0.1]: _b(v, x, x + 0.05, 0, 0.8, z, z + 0.05, "oak_d")
			_b(v, -hw + 0.1, -hw + 0.18, 0.2, 1.05, -hd - 0.05, -hd + 0.03, "iron")
		"grindstone":
			for i in range(-8, 9):
				for y in range(-8, 9):
					if Vector2(i, y).length() <= 8.5: for k in range(-2, 2): v.put(Vector3i(i, 13 + y, k), C["stone_l"], 0.05)
			for x in [-0.5, 0.45]: _b(v, x, x + 0.05, 0, 0.7, -0.15, 0.15, "oak_d")
			_b(v, -0.5, 0.5, 0.63, 0.68, -0.02, 0.02, "iron")
			_tub(v, 0.0, 0.3, 0.15, 0.3, true, "water")
		"stock rack":
			for x in [-hw, hw - 0.06]: _b(v, x, x + 0.06, 0, 1.4, -0.15, 0.15, "oak_d")
			_b(v, -hw, hw, 0.0, 0.08, -0.15, 0.15, "oak_d"); _b(v, -hw, hw, 1.0, 1.06, -0.15, -0.1, "oak_d")
			for k in 12: v.beam(Vector3(-hw + 0.1 + k * 0.08, 0.08, 0.05), Vector3(-hw + 0.12 + k * 0.08, 1.3 - (k % 3) * 0.15, -0.1), 0.04, C["iron" if k % 2 else "rust"])
		"smith goods":   # chain, boat hooks, rings and a small anchor laid out on a board
			_b(v, -hw, hw, 0, 0.08, -hd, hd, "drift_d")
			for k in 10: _b(v, -hw + 0.1 + k * 0.06, -hw + 0.14 + k * 0.06, 0.08, 0.11, -0.05 + (k % 2) * 0.03, 0.0 + (k % 2) * 0.03, "iron")
			v.beam(Vector3(0.1, 0.1, 0), Vector3(0.6, 0.1, 0.05), 0.04, C["iron_l"])
			_b(v, 0.45, 0.75, 0.08, 0.13, -0.1, 0.1, "iron"); _b(v, 0.58, 0.62, 0.08, 0.13, -0.12, 0.12, "iron")
		"old blade":   # an old sword on two pegs (hung by the plan on the smithy wall)
			_b(v, -0.45, 0.35, 0, 0.06, -0.02, 0.02, "iron_l"); _b(v, 0.35, 0.4, -0.08, 0.14, -0.03, 0.03, "bronze"); _b(v, 0.4, 0.55, 0, 0.06, -0.025, 0.025, "oak_d")
		"chopping block":   # a stump with the hatchet in it (the hatchet itself is the item: added apart)
			_tub(v, 0, 0, 0.28, 0.5)
			for i in range(-5, 6):
				for k in range(-5, 6):
					if Vector2(i, k).length() < 5.0: v.put(Vector3i(i, 9, k), C["board" if Vector2(i, k).length() > 3.5 else "drift"], 0.0)
		"boat hull":   # a hull on trestles, half built: the keel, ribs, a few strakes
			for x in [-1.2, 0.0, 1.2]: for z in [-0.45, 0.4]: _b(v, x, x + 0.08, 0, 0.5, z, z + 0.08, "drift_d")
			for x in [-1.2, 0.0, 1.2]: _b(v, x - 0.04, x + 0.12, 0.45, 0.5, -0.5, 0.5, "drift_d")
			_b(v, -hw, hw, 0.5, 0.6, -0.05, 0.05, "oak")
			for k in 9:
				var x := -hw + 0.3 + k * (w - 0.6) / 8.0; var half := 0.65 * sin(PI * (k + 0.5) / 9.0) + 0.1
				for s_ in [-1, 1]: v.beam(Vector3(x, 0.6, 0), Vector3(x, 1.25, s_ * half), 0.06, C["board_d"])
			for st in 3:
				for k in 40:
					var x := -hw + 0.2 + k * (w - 0.4) / 40.0; var t := float(k) / 40.0
					var half := (0.65 * sin(PI * t) + 0.1) * (0.5 + st * 0.2)
					for s_ in [-1, 1]: _b(v, x, x + 0.1, 0.65 + st * 0.15, 0.75 + st * 0.15, s_ * half - 0.03, s_ * half + 0.03, "board")
		"bell frame":   # an A-frame of timbers, the bell under a little gable, its rope down
			for x in [-hw, hw - 0.12]:
				v.beam(Vector3(x + 0.06, 0, -hd + 0.1), Vector3(x + 0.06, 3.0, 0), 0.12, C["tar"])
				v.beam(Vector3(x + 0.06, 0, hd - 0.1), Vector3(x + 0.06, 3.0, 0), 0.12, C["tar"])
			_b(v, -hw, hw, 2.9, 3.05, -0.08, 0.08, "tar_d")
			for k in 6:
				_b(v, -hw - 0.1, hw + 0.1, 3.05 + k * 0.05, 3.1 + k * 0.05, -0.35 + k * 0.06, -0.29 + k * 0.06, "drift_d")
				_b(v, -hw - 0.1, hw + 0.1, 3.05 + k * 0.05, 3.1 + k * 0.05, 0.29 - k * 0.06, 0.35 - k * 0.06, "drift_d")
			for y in 7:
				var r := 0.1 + y * 0.03
				for i in range(-6, 7): for k in range(-6, 7):
					var d := Vector2(i, k).length() * S
					if d <= r and d > r - 0.08: v.put(Vector3i(i, int(2.9 / S) - 1 - y, k), C["bronze"], 0.05)
			_b(v, -0.02, 0.02, 0.9, 2.5, -0.02, 0.02, "rope", 0.0)
		"cart":   # a two-wheeled farm cart, shafts down
			_b(v, -0.6, 0.6, 0.6, 0.66, -0.9, 0.9, "board"); for x in [-0.62, 0.56]: _b(v, x, x + 0.06, 0.66, 0.95, -0.9, 0.9, "board_d")
			_b(v, -0.6, 0.6, 0.66, 0.95, 0.84, 0.9, "board_d")
			for x in [-0.72, 0.66]:
				for a in 32:
					var t := a * TAU / 32.0
					v.put(Vector3i(int(x / S), int((0.5 + sin(t) * 0.45) / S), int(cos(t) * 0.45 / S)), C["tar_d"], 0.04)
				for sp in 4: v.beam(Vector3(x + 0.03, 0.5, 0), Vector3(x + 0.03, 0.5 + sin(sp * PI / 4) * 0.42, cos(sp * PI / 4) * 0.42), 0.04, C["tar_d"])
				for sp in 4: v.beam(Vector3(x + 0.03, 0.5, 0), Vector3(x + 0.03, 0.5 - sin(sp * PI / 4) * 0.42, -cos(sp * PI / 4) * 0.42), 0.04, C["tar_d"])
			_b(v, -0.72, 0.72, 0.47, 0.53, -0.03, 0.03, "iron")
			for x in [-0.45, 0.4]: v.beam(Vector3(x, 0.6, -0.9), Vector3(x, 0.05, -hd), 0.06, C["drift_d"])
		"manure heap":
			v.blob(Vector3(0, 0, 0), Vector3(hw, 0.5, hd), C["manure"], 0.12)
			v.blob(Vector3(0.2, 0.25, 0.1), Vector3(0.25, 0.2, 0.2), C["straw_d"], 0.1)
		"hen coop":   # a little boarded coop on legs, a slanted roof, a ramp
			for x in [-hw + 0.05, hw - 0.1]: for z in [-hd + 0.05, hd - 0.1]: _b(v, x, x + 0.06, 0, 0.4, z, z + 0.06, "tar_d")
			_b(v, -hw, hw, 0.4, 1.0, -hd + 0.1, hd - 0.1, "drift"); _b(v, -0.15, 0.1, 0.4, 0.65, -hd + 0.05, -hd + 0.1, "soot", 0.0)
			for k in 4: _b(v, -hw - 0.05, hw + 0.05, 1.0 + k * 0.05, 1.05 + k * 0.05, -hd + k * 0.25, hd, "drift_d")
			v.beam(Vector3(-0.02, 0.4, -hd + 0.05), Vector3(-0.02, 0.0, -hd - 0.5), 0.12, C["drift_d"])
		"notice post":   # a post with a board, notices pinned, a little roof
			_post(v, 0, 0, 1.8, "tar", 0.12)
			_b(v, -hw, hw, 1.1, 1.75, -0.04, 0.04, "drift")
			for k in 3: _b(v, -hw + 0.1 + k * 0.3, -hw + 0.35 + k * 0.3, 1.25 + (k % 2) * 0.1, 1.6 + (k % 2) * 0.05, -0.06, -0.04, "paper", 0.03)
			_b(v, -hw - 0.05, hw + 0.05, 1.8, 1.85, -0.15, 0.15, "drift_d")
		"scarecrow":   # a cross of sticks, an old coat and a sack head
			_post(v, 0, 0, 1.9, "drift_d", 0.06)
			_b(v, -hw * 0.7, hw * 0.7, 1.45, 1.5, -0.03, 0.03, "drift_d")
			_b(v, -0.25, 0.25, 0.9, 1.55, -0.12, 0.12, "cloth"); _b(v, -hw * 0.6, hw * 0.6, 1.35, 1.5, -0.08, 0.08, "cloth")
			v.blob(Vector3(0, 1.75, 0), Vector3(0.14, 0.15, 0.14), C["sack"], 0.06)
			_b(v, -0.2, 0.2, 1.88, 1.92, -0.2, 0.2, "straw_d")
		"haystack":
			v.blob(Vector3(0, 0, 0), Vector3(hw, 1.1, hd), C["hay"], 0.1)
			_b(v, -0.02, 0.02, 1.0, 1.4, -0.02, 0.02, "drift_d", 0.0)
		"net rack":   # poles with the nets hung over them to dry
			for x in [-hw, 0, hw - 0.08]: _b(v, x, x + 0.08, 0, 1.7, -0.04, 0.04, "drift_d")
			_b(v, -hw, hw, 1.6, 1.66, -0.03, 0.03, "drift_d")
			for x in int(w / S):
				var sag := sin(x * 0.4) * 0.06
				for y in int((0.9 + sag) / S):
					if (x + y) % 3 == 0 or y % 3 == 0: v.put(Vector3i(int(-hw / S) + x, int(1.6 / S) - y, 1), C["rope"], 0.05)
		"drying rack":   # fish hung in rows on a rack of poles
			for x in [-hw, hw - 0.08]: for z in [-hd, hd - 0.08]: _b(v, x, x + 0.08, 0, 1.6, z, z + 0.08, "drift_d")
			for z in [-hd + 0.25, 0.0, hd - 0.3]:
				_b(v, -hw, hw, 1.55, 1.6, z, z + 0.05, "drift_d")
				for k in int(w / 0.18): _b(v, -hw + 0.12 + k * 0.18, -hw + 0.18 + k * 0.18, 1.15, 1.55, z, z + 0.04, "fish" if k % 3 else "fish_d")
		"gutting table":
			_b(v, -hw, hw, 0.85, 0.92, -hd, hd, "drift"); for x in [-hw + 0.05, hw - 0.1]: for z in [-hd + 0.05, hd - 0.1]: _b(v, x, x + 0.06, 0, 0.85, z, z + 0.06, "drift_d")
			for k in 4: _b(v, -0.4 + k * 0.25, -0.2 + k * 0.25, 0.92, 0.96, -0.1 + (k % 2) * 0.2, -0.04 + (k % 2) * 0.2, "fish")
			_tub(v, hw - 0.3, hd + 0.0, 0.2, 0.4, true, "fish_d")
		"lobster pots":   # creels of withy, stacked
			for k in 3:
				var at := Vector3(-0.3 + k * 0.32, 0.0, 0.0) if k < 2 else Vector3(-0.15, 0.32, 0.0)
				for i in 6: for y in 6: for z in 10:
					if i == 0 or i == 5 or y == 0 or y == 5 or z == 0 or z == 9:
						if (i + y + z) % 2 == 0: v.put(Vector3i(int(at.x / S) + i - 3, int(at.y / S) + y, z - 5), C["drift_d"], 0.05)
		"torch":   # a bracket and the torch's head (the flame is added as fire)
			_b(v, -0.03, 0.03, 0, 0.5, -0.03, 0.03, "oak_d"); _b(v, -0.05, 0.05, 0.45, 0.6, -0.05, 0.05, "soot")
		"lamp":   # a lantern on a post, for the gate and the pier's head
			_post(v, 0, 0, 2.2, "tar", 0.1)
			_b(v, 0, 0.4, 2.1, 2.15, -0.025, 0.025, "iron")
			_b(v, 0.27, 0.43, 1.75, 1.95, -0.08, 0.08, "iron"); _b(v, 0.29, 0.41, 1.78, 1.92, -0.06, 0.06, "straw", 0.0)
		_: return false
	return true

## the wash on a line: cloth, so not voxels: a few low-poly sheets that sway in the wind (a vertex shader)
static func washing_cloth(w: float) -> MeshInstance3D:
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var cols := [Color8(200, 192, 170), Color8(120, 46, 40), Color8(110, 120, 130), Color8(170, 150, 110)]
	var x := -w / 2.0 + 0.3
	var k := 0
	while x < w / 2.0 - 0.6:
		var cw := 0.4 + (k % 3) * 0.15; var ch := 0.5 + (k % 2) * 0.25
		st.set_color(cols[k % cols.size()])
		for q in [[0, 0], [1, 0], [1, 1], [0, 0], [1, 1], [0, 1]]:
			st.set_uv(Vector2(q[0], q[1])); st.add_vertex(Vector3(x + q[0] * cw, 1.82 - q[1] * ch, 0))
		x += cw + 0.15; k += 1
	var mi := MeshInstance3D.new(); mi.mesh = st.commit()
	var sh := Shader.new(); sh.code = """
shader_type spatial;
render_mode cull_disabled;
void vertex() { float d = UV.y; VERTEX.z += sin(TIME * 2.3 + VERTEX.x * 3.0) * 0.08 * d; VERTEX.x += sin(TIME * 1.7 + VERTEX.x) * 0.03 * d; }
void fragment() { ALBEDO = COLOR.rgb * COLOR.rgb; ROUGHNESS = 1.0; }
"""
	var m := ShaderMaterial.new(); m.shader = sh; mi.material_override = m
	return mi

## a flame: not voxels; two crossed low-poly cones, flickering, unshaded, with a warm light
static func flame(size := 0.25, light := true) -> Node3D:
	var n := Node3D.new(); n.name = "Flame"
	var sh := Shader.new(); sh.code = """
shader_type spatial;
render_mode unshaded, cull_disabled, blend_add;
void vertex() { float t = TIME * 9.0 + VERTEX.x * 7.0; VERTEX.xz *= 1.0 + 0.18 * sin(t); VERTEX.y *= 1.0 + 0.2 * sin(t * 1.3 + 1.0); }
void fragment() { float h = clamp(UV.y, 0.0, 1.0); ALBEDO = mix(vec3(1.0, 0.85, 0.4), vec3(1.0, 0.35, 0.08), 1.0 - h); ALPHA = 0.9; }
"""
	var mat := ShaderMaterial.new(); mat.shader = sh
	for k in 2:
		var cm := CylinderMesh.new(); cm.top_radius = 0.0; cm.bottom_radius = size * (0.5 if k == 0 else 0.32); cm.height = size * (1.6 if k == 0 else 2.2)
		cm.radial_segments = 5; cm.rings = 1
		var mi := MeshInstance3D.new(); mi.mesh = cm; mi.material_override = mat; mi.position.y = cm.height / 2.0
		mi.rotation.y = k * 0.6; mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF; n.add_child(mi)
	if light:
		var l := OmniLight3D.new(); l.light_color = Color(1.0, 0.62, 0.3); l.light_energy = 1.2; l.omni_range = 6.0; l.position.y = size
		l.set_script(preload("res://scripts/voxel/flicker.gd")); n.add_child(l)
	return n
