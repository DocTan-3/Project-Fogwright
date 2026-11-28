## Layouts for the voxel building kit's builder (scripts/voxel/building_kit.gd). Grid points and partitions are in 2 m
## modules; stairs, pieces and chimneys in 10 cm voxels; fittings and lights in metres. x runs along the front, y (depth)
## from the front (0) to the back; lights are in the building's Godot space (x, height, -depth).
class_name KitLayouts
extends RefCounted

## a 10 x 6 m house: a stone 4.4 m ground floor with a front door and a stair up to a 3.0 m timber-frame floor, thatched
const TEST_ROOM := {
	"size": Vector2i(5, 3),
	"storeys": [
		{"h": 44, "face": "stone", "walls": {"front": "wdpww", "right": "pwp", "back": "pwpwp", "left": "pwp"},
		 "stairs": [{"at": Vector2i(15, 42), "run": "+x"}],
		 "lights": [{"at": Vector3(4.0, 3.6, -2.2), "energy": 1.6, "range": 8.0}]},
		{"h": 30, "face": "frame", "walls": {"front": "pwpwp", "right": "pwp", "back": "pwpwp", "left": "pwp"},
		 "lights": [{"at": Vector3(4.0, 7.2, -1.8), "energy": 1.0, "range": 6.0}]},
	],
	"roof": "thatch",
}

## The Gull & Lantern, Farhallow's inn, 16 x 12 m, its front on the well square, built as the lore has Farhallow
## (lore.md): a poor freehold on the far coast with no big timber, where the Fog comes in at dusk. Drystone walls with
## rounded corners, salvaged ship timbers tarred dark, heather thatch roped and weighted against the wind, shutters, and
## the upper floor up in the roof behind a knee wall, lit by dormers. Over the door hangs the Vigil's lantern that names
## it, a lit wick the keeper bought, and by the door stands Hollin's waystone; a carved gull keeps the gable.
## Ground (4.4 m): the taproom (10 x 8) with the hearth on the gable wall, a bar made from a boat's keel, four tables with
## benches and a lantern; the hall (6 x 6) with the keeper's counter for rooms and the store; the kitchen (6 x 6) with
## its range, a work table, ale barrels and a side door to the yard; behind the taproom the stair hall (10 x 4), the stair
## climbing along the back wall. Upper (in the roof): the corridor the length of the house, lit from both gables, four
## front guest rooms of 4 x 4 each with a dormer on the square, a back guest room of 4 x 6 with two beds, the landing over
## the stair, and the keeper's room (6 x 6) over the kitchen, warm from its chimney.
const GULL_LANTERN := {
	"size": Vector2i(8, 6),
	"rounded": true,
	"floor": "salvage",
	"ground": "slabs",
	"door_leaf": "door_leaf_dry",
	"paint": "green", "seed": 17,
	"porch": {"from": 1, "to": 6, "depth": 18},
	"storeys": [
		{"h": 44, "face": "dry",
		 "walls": {"front": "wpdpwdwp", "right": "pwppdp", "back": "pwpppppp", "left": "pwpppw"},   # doors to the taproom and the hall
		 "inner": [
			{"at": Vector2i(5, 0), "dir": "y", "bays": "dpppdp", "face": "board"},   # taproom | hall, stair hall | kitchen
			{"at": Vector2i(0, 4), "dir": "x", "bays": "pdppp", "face": "board"},    # taproom | stair hall
			{"at": Vector2i(5, 3), "dir": "x", "bays": "pdp", "face": "board"}],     # hall | kitchen
		 "stairs": [{"at": Vector2i(27, 103), "run": "+x"}],
		 "posts": [{"at": Vector2i(20, 38), "h": 41}, {"at": Vector2i(60, 38), "h": 41}],   # carved masts under the gallery's edge
		 "firepit": {"at": Vector2i(40, 22), "r": 8},
		 "pieces": [{"p": "hearth", "at": Vector3i(3, 50, 0), "dir": "-y"},         # the taproom's, on the gable wall
			{"p": "hearth", "at": Vector3i(150, 117, 0), "dir": "-x"},               # the kitchen range
			{"p": "waystone", "at": Vector3i(8, -9, -5)}],                           # Hollin's, by the porch
		 "fittings": [
			{"p": "bar_keel", "at": Vector2(8.0, 7.0), "dir": "-y"}, {"p": "bar_keel", "at": Vector2(8.0, 5.0), "dir": "-y"},
			{"p": "shelf", "at": Vector2(9.85, 4.2), "dir": "+y"},
			{"p": "barrel", "at": Vector2(9.15, 6.0)}, {"p": "barrel", "at": Vector2(9.15, 6.8)},
			{"p": "table", "at": Vector2(0.9, 0.7)}, {"p": "bench", "at": Vector2(0.9, 0.3)}, {"p": "bench", "at": Vector2(0.9, 1.6)},
			{"p": "table", "at": Vector2(6.6, 0.7)}, {"p": "bench", "at": Vector2(6.6, 0.3)}, {"p": "bench", "at": Vector2(6.6, 1.6)},
			{"p": "table", "at": Vector2(2.2, 4.2)}, {"p": "bench", "at": Vector2(2.2, 3.8)}, {"p": "bench", "at": Vector2(2.2, 5.1)},
			{"p": "table", "at": Vector2(5.4, 4.6)}, {"p": "bench", "at": Vector2(5.4, 4.2)}, {"p": "bench", "at": Vector2(5.4, 5.5)},
			{"p": "sconce", "at": Vector2(1.9, 3.4), "z": 2.2}, {"p": "sconce", "at": Vector2(5.9, 3.4), "z": 2.2},
			{"p": "desk", "at": Vector2(12.0, 3.0)}, {"p": "shelf", "at": Vector2(15.6, 5.9), "dir": "-x"},
			{"p": "chest", "at": Vector2(14.6, 0.5)},
			{"p": "table", "at": Vector2(11.0, 9.6)},
			{"p": "barrel", "at": Vector2(15.2, 6.4)}, {"p": "barrel", "at": Vector2(15.2, 7.1)},
			{"p": "barrel", "at": Vector2(0.5, 8.5)}, {"p": "barrel", "at": Vector2(0.5, 9.2)},
			{"p": "vigil_lantern", "at": Vector2(6.4, 0.0), "dir": "-x", "z": 1.7},   # the Lantern, over the door
			{"p": "gull", "at": Vector2(-0.25, 5.7), "dir": "+y", "z": 11.9},          # the Gull, on the gable
			{"p": "sign_post", "at": Vector2(0.6, -3.0), "dir": "+x", "z": -0.5},      # its sign, by the square
			{"p": "barrel", "at": Vector2(1.2, -1.5)}, {"p": "barrel", "at": Vector2(1.9, -1.4)},
			{"p": "creels", "at": Vector2(17.0, 3.0), "dir": "+y", "z": -0.5},
			{"p": "woodpile", "at": Vector2(17.1, 8.0), "dir": "+y", "z": -0.5}, {"p": "woodpile", "at": Vector2(17.1, 9.3), "dir": "+y", "z": -0.5},
			{"p": "ivy", "at": Vector2(-0.1, 3.0), "dir": "-y", "z": 0.0}, {"p": "ivy", "at": Vector2(16.1, 6.0), "dir": "+y", "z": 0.0},
			{"p": "rocks", "at": Vector2(-0.9, 10.0), "dir": "+y", "z": -0.5}, {"p": "rocks", "at": Vector2(16.6, 1.0), "dir": "+y", "z": -0.5}],
		 "lights": [{"at": Vector3(1.6, 1.0, -4.0), "energy": 2.7, "range": 6.0, "color": Color(1.0, 0.62, 0.32)},   # the hearth
			{"at": Vector3(4.0, 1.2, -2.2), "energy": 3.6, "range": 9.0, "color": Color(1.0, 0.6, 0.3)},       # the fire pit
			{"at": Vector3(4.0, 3.6, -2.2), "energy": 2.6, "range": 9.0},                                       # the chandelier
			{"at": Vector3(4.0, 7.5, -2.0), "energy": 1.6, "range": 8.0, "color": Color(0.95, 0.85, 0.7)},       # light high in the roof, from the dormers
			{"at": Vector3(13.0, 3.4, -9.0), "energy": 1.9, "range": 6.0},                                      # the kitchen
			{"at": Vector3(6.15, 2.4, 0.3), "energy": 2.4, "range": 6.0, "color": Color(1.0, 0.72, 0.42)}]},    # the Vigil lantern
		{"h": 12, "face": "dry",
		 "voids": [Rect2i(3, 3, 76, 36)],   # the taproom open to the roof, the gallery along its back
		 "walls": {"front": "pDpDpDpD", "right": "pppppp", "back": "pDppppDp", "left": "pppppp"},
		 "inner": [
			{"at": Vector2i(0, 2), "dir": "x", "bays": "rrrrpdpd", "swing": -1, "face": "board", "h": 30},   # gallery rail | front rooms | corridor
			{"at": Vector2i(0, 3), "dir": "x", "bays": "pd...dpp", "face": "board", "h": 30},   # corridor | back room, landing, keeper
			{"at": Vector2i(4, 0), "dir": "y", "bays": "pp", "face": "board", "h": 30},
			{"at": Vector2i(6, 0), "dir": "y", "bays": "pp", "face": "board", "h": 30},
			{"at": Vector2i(2, 3), "dir": "y", "bays": "ppp", "face": "board", "h": 30}, {"at": Vector2i(5, 3), "dir": "y", "bays": "ppp", "face": "board", "h": 30}],
		 "fittings": [
			{"p": "shield", "at": Vector2(0.42, 0.5), "dir": "+y", "z": 0.9}, {"p": "shield", "at": Vector2(0.42, 1.5), "dir": "+y", "z": 1.3},
			{"p": "shield", "at": Vector2(0.42, 2.6), "dir": "+y", "z": 0.9}, {"p": "shield_b", "at": Vector2(0.42, 3.0), "dir": "+y", "z": 1.9},
			{"p": "chandelier", "at": Vector2(3.5, 1.7), "z": -1.4},
			{"p": "bed", "at": Vector2(8.4, 0.4)}, {"p": "chest", "at": Vector2(9.6, 0.4)},
			{"p": "bed", "at": Vector2(12.4, 0.4)}, {"p": "chest", "at": Vector2(13.6, 0.4)},
			{"p": "bed", "at": Vector2(0.4, 9.6)}, {"p": "bed", "at": Vector2(2.4, 9.6)},
			{"p": "bed", "at": Vector2(11.0, 9.6)}, {"p": "chest", "at": Vector2(12.4, 11.1)}],
		 "lights": [{"at": Vector3(8.0, 7.0, -5.0), "energy": 1.5, "range": 7.0}, {"at": Vector3(13.0, 7.0, -9.0), "energy": 1.5, "range": 5.0}]},
	],
	"roof": "heather",
	"gable_windows": [5.0],
	"chimneys": [{"at": Vector2i(3, 32), "from": 15, "above": 50}, {"at": Vector2i(136, 109), "from": 15, "above": 22}],
}

# ---------------------------------------------------------------- the rest of Farhallow, laid out from the plan
## A layout for one of the plan's buildings (data/farhallow.json), built the freehold's way (lore.md): Farhallow is home
## to freefolk of every people, so each house is built a little in its owners' own way on the same stone-and-salvage
## kit. Wayfolk and the farm: drystone under heather thatch. Hrimfolk fishers: drystone under turf, as at home. The Ferrin
## smith: a tall stone forge under slate. The merchants and the harbour master: two floors, the upper in the roof with
## dormers, under bought slate. Sheds, stores and smokehouses: plank walls on a stone footing. The Merrith shrine: a
## small stone cell lit by candles.
## w, h: the plot in metres (w along the door face); doors: the plot's doors in its own frame (x across, z from the
## centre, the door face at z = -h/2 being the front); key: a number to vary houses of one type by.
const STYLES := {
	"cottage": {"porch": true, "wing": true, "face": "dry", "roof": ["heather", "turf"], "hearth": true, "fit": "home", "upper": true},
	"street_house": {"porch": true, "face": "dry", "roof": ["heather"], "hearth": true, "fit": "home", "upper": true},
	"farmstead": {"porch": true, "wing": true, "face": "dry", "roof": ["heather"], "hearth": true, "fit": "farm", "upper": true},
	"merchant_house": {"face": "dry", "roof": ["slate"], "hearth": true, "fit": "hall", "upper": true},
	"merchant_house_small": {"face": "dry", "roof": ["slate"], "hearth": true, "fit": "hall", "upper": true},
	"workshop": {"face": "dry", "h": 44, "roof": ["slate"], "hearth": true, "fit": "forge"},
	"guard_post": {"face": "dry", "roof": ["slate"], "fit": "post"},
	"merrith_shrine": {"face": "dry", "roof": ["heather"], "fit": "shrine"},
	"smokehouse": {"face": "board", "roof": ["heather"], "hearth": true, "fit": "store", "shut": true},
	"salt_works": {"face": "board", "roof": ["heather"], "hearth": true, "fit": "store", "shut": true},
	"store": {"face": "board", "roof": ["heather"], "fit": "store", "shut": true},
	"granary": {"face": "board", "roof": ["heather"], "fit": "store", "shut": true},
	"boat_shed": {"face": "board", "roof": ["heather"], "fit": "shed", "shut": true},
	"hen_house": {"face": "board", "roof": ["turf"], "fit": "none", "shut": true},
}

static func for_plot(type: String, w: float, h: float, doors: Array, key: int) -> Dictionary:
	var st: Dictionary = STYLES.get(type, STYLES.cottage)
	var nx := maxi(2, roundi(w / 2.0)); var ny := maxi(2, roundi(h / 2.0))
	var W := nx * 20; var D := ny * 20
	var sides := {"front": [], "right": [], "back": [], "left": []}   # door bays per side
	for dp in doors:
		var p: Vector2 = dp
		var xk := float(nx) - p.x; var yk := p.y + float(ny)   # the kit's x (along the front) and depth, in metres
		var dist := {"front": absf(yk), "back": absf(yk - 2 * ny), "left": absf(xk), "right": absf(xk - 2 * nx)}
		var side := "front"
		for k in dist: if dist[k] < dist[side]: side = k
		var along: float = {"front": xk, "back": 2 * nx - xk, "right": yk, "left": 2 * ny - yk}[side]
		var n: int = nx if side in ["front", "back"] else ny
		sides[side].append(clampi(int(along / 2.0), 0, n - 1))
	if doors.is_empty(): sides.front.append(nx / 2)
	# the hearth goes on a side wall with no door, in its middle bay
	var hearth_side := ""
	if st.get("hearth", false): hearth_side = "left" if sides.left.is_empty() else ("right" if sides.right.is_empty() else "")
	var hb := ny / 2
	var walls := {}
	for side in sides:
		var n: int = nx if side in ["front", "back"] else ny
		var s := ""
		for i in n:
			if i in sides[side]: s += "d"
			elif side == hearth_side and i == hb: s += "p"
			elif st.get("shut", false): s += "w" if (side == "front" and i == n - 1 and n > 2) else "p"   # sheds: one small window
			else: s += "w" if (i % 2 == (1 if n > 2 else 0)) else "p"
		walls[side] = s
	var roofs: Array = st.roof; var roof: String = roofs[key % roofs.size()]
	var h0: int = st.get("h", 30)
	var g := {"h": h0, "face": st.face, "walls": walls, "pieces": [], "fittings": [], "lights": []}
	var layout := {"size": Vector2i(nx, ny), "storeys": [g], "roof": roof, "rounded": st.face == "dry", "floor": "salvage",
		"ground": "slabs", "door_leaf": "door_leaf_dry", "chimneys": [], "seed": key,
		"paint": PAINT_NAMES[(key * 7 + 3) % PAINT_NAMES.size()]}
	if st.get("upper", false):   # a floor up in the roof, with dormers on the front and back, and a stair to it
		var fr := ""; var bk := ""
		for i in nx: fr += "D" if i % 2 == 1 else "p"; bk += "D" if i % 2 == 0 and i > 0 else "p"
		layout.storeys.append({"h": 12, "face": "dry", "walls": {"front": fr, "back": bk, "left": "p".repeat(ny), "right": "p".repeat(ny)}})
		g.stairs = [{"at": Vector2i(10 if hearth_side != "left" else W - 10 - 45, D - 18), "run": "+x"}]
	# the hearth and its chimney
	var top := PLINTH_V + h0 + (12 if st.get("upper", false) else 0)
	if hearth_side == "left":
		g.pieces.append({"p": "hearth", "at": Vector3i(3, D - 20 * hb, 0), "dir": "-y"})
		var yc := D - 20 * hb - 10
		layout.chimneys.append({"at": Vector2i(3, yc - 4), "from": 15, "above": mini(yc, D - yc) + 10})
		g.lights.append({"at": Vector3(1.3, 0.9, -yc / 10.0), "energy": 1.6, "range": 5.0, "color": Color(1.0, 0.62, 0.32)})
	elif hearth_side == "right":
		g.pieces.append({"p": "hearth", "at": Vector3i(W - 3, 20 * hb, 0), "dir": "+y"})
		var yc := 20 * hb + 10
		layout.chimneys.append({"at": Vector2i(W - 11, yc - 4), "from": 15, "above": mini(yc, D - yc) + 10})
		g.lights.append({"at": Vector3(W / 10.0 - 1.3, 0.9, -yc / 10.0), "energy": 1.6, "range": 5.0, "color": Color(1.0, 0.62, 0.32)})
	_fit(g, st.fit, W / 10.0, D / 10.0, hearth_side, sides)
	if st.get("porch", false) and not sides.front.is_empty(): layout.porch = {"from": 0, "to": nx - 1, "depth": 16}
	var other := "right" if hearth_side == "left" else "left"
	var wing := ""
	if st.get("wing", false) and sides[other].is_empty() and ny >= 3: wing = other
	_yard(g, type, W / 10.0, D / 10.0, sides, hearth_side, key, layout.has("porch"), wing)
	if wing != "":   # a lower wing on that gable: the byre or the store, set back a module, its own door at the front
		var wd := ny - 1
		var wl := {"size": Vector2i(2, wd), "roof": "turf" if roof == "heather" else "heather", "floor": "salvage", "ground": "slabs",
			"door_leaf": "door_leaf_dry", "paint": layout.paint, "seed": key + 101, "attached": "right" if wing == "left" else "left",
			"storeys": [{"h": 30, "face": "dry", "walls": {"front": "dp" if wing == "left" else "pd", "right": "." .repeat(wd) if wing == "left" else "p".repeat(wd),
				"back": "pp", "left": "." .repeat(wd) if wing == "right" else "p".repeat(wd)}, "pieces": [], "lights": [],
				"fittings": [{"p": "barrel", "at": Vector2(0.5, wd * 2.0 - 1.0)}, {"p": "barrel", "at": Vector2(1.2, wd * 2.0 - 1.0)},
					{"p": "crate", "at": Vector2(2.6, wd * 2.0 - 0.9)}, {"p": "woodpile", "at": Vector2(0.4, wd * 2.0 - 0.1), "dir": "-x"}]}]}
		layout.wings = [{"layout": wl, "at": Vector2(-4.0 if wing == "left" else W / 10.0, 2.0)}]
	return layout

## what stands round a house outside (5 cm fittings, on the ground: z -0.5 under the floor): a woodpile by the hearth's
## wall, creels and a net rack and a little wattle-fenced garden on the other side, ivy, stones by the footing, a barrel
## by the door, and a sign on a post for the houses that sell. Sides with doors are left clear.
static func _yard(g: Dictionary, type: String, Wm: float, Dm: float, sides: Dictionary, hearth: String, key: int, porch: bool, wing := "") -> void:
	var f: Array = g.fittings
	if type in ["boat_shed", "hen_house", "guard_post", "granary"]: return
	# a side's item: along is the distance from the front of its far end, out the distance of its outer face from the wall
	var side := func(sd: String, p: String, along: float, out: float, z := -0.5) -> void:
		if sd == "left": f.append({"p": p, "at": Vector2(-out, along), "dir": "-y", "z": z})
		else: f.append({"p": p, "at": Vector2(Wm + out, along), "dir": "+y", "z": z})
	var other := "right" if hearth == "left" else "left"
	if hearth != "" and sides[hearth].is_empty():
		side.call(hearth, "woodpile", Dm - 0.4, 0.65)
		side.call(hearth, "ivy", 1.2, 0.1, 0.0)
	if sides[other].is_empty() and wing == "":
		if type in ["cottage", "street_house", "farmstead", "smokehouse", "salt_works"]:
			side.call(other, "net_rack", 2.6, 0.75)
			side.call(other, "creels", Dm - 0.3, 0.5)
		side.call(other, "ivy", Dm - 0.4, 0.1, 0.0)
		if type in ["cottage", "farmstead"] and Dm >= 6.0:   # a kitchen garden, fenced against the wind and the hens
			var n := int(Dm / 2.0)
			for i in n: side.call(other, "wattle", 2.0 + i * 2.0, 2.4)
		side.call(other, "rocks", 1.0, 0.5)
	f.append({"p": "rocks", "at": Vector2(Wm - 0.6, Dm + 0.3), "dir": "+x", "z": -0.5})
	if not sides.front.is_empty():
		var dx: float = sides.front[0] * 2.0
		var ox := dx + 1.85 if dx + 2.6 < Wm else dx - 0.45
		f.append({"p": "barrel", "at": Vector2(ox, -1.2 if porch else -0.8), "z": 0.0 if porch else -0.5})
		if type in ["merchant_house", "merchant_house_small", "workshop", "inn"]:
			f.append({"p": "sign_post", "at": Vector2(-1.0, -2.4), "dir": "+x", "z": -0.5})

const PLINTH_V := 5
const PAINT_NAMES := ["tar", "blue", "green", "red", "ochre"]

# the furniture of a house, along its back wall, kept clear of a back door and of the hearth's side
static func _fit(g: Dictionary, kind: String, Wm: float, Dm: float, hearth: String, sides: Dictionary) -> void:
	var f: Array = g.fittings
	var back_free_r: bool = not (0 in sides.back)                 # the back's first bay is at the right
	var back_free_l: bool = not ((int(Wm / 2.0) - 1) in sides.back)
	var corner_x := Wm - 1.45 if back_free_r and hearth != "right" else 0.45   # x of a corner by the back wall, away from the hearth
	match kind:
		"home", "farm":
			f.append({"p": "bed", "at": Vector2(corner_x, Dm - 2.45)})
			f.append({"p": "chest", "at": Vector2(corner_x + (-0.8 if corner_x > 1.0 else 1.1), Dm - 0.8)})
			f.append({"p": "table", "at": Vector2(Wm * 0.5 - 0.8, Dm * 0.5 - 0.4)})
			f.append({"p": "bench", "at": Vector2(Wm * 0.5 - 0.8, Dm * 0.5 - 0.85)})
			f.append({"p": "barrel", "at": Vector2(Wm - corner_x - 0.6 if corner_x > 1.0 else Wm - 1.0, Dm - 0.95)})
			if kind == "farm": f.append({"p": "shelf", "at": Vector2(Wm * 0.5 - 0.8, Dm - 0.3), "dir": "-x"})
		"hall":
			f.append({"p": "table", "at": Vector2(Wm * 0.5 - 0.8, Dm * 0.4)}); f.append({"p": "table", "at": Vector2(Wm * 0.5 - 0.8, Dm * 0.4 + 1.0)})
			f.append({"p": "desk", "at": Vector2(0.5 if hearth != "left" else Wm - 1.7, Dm * 0.5 - 0.3), "dir": "+x"})   # the stair has the back wall
			f.append({"p": "chest", "at": Vector2(0.5 if hearth != "left" else Wm - 1.2, Dm * 0.5 + 0.6)})
		"forge":
			f.append({"p": "table", "at": Vector2(Wm * 0.5 - 0.8, Dm * 0.5)})
			f.append({"p": "barrel", "at": Vector2(Wm - 1.0, Dm - 1.0)}); f.append({"p": "barrel", "at": Vector2(Wm - 1.7, Dm - 1.0)})
			f.append({"p": "shelf", "at": Vector2(Wm * 0.5 + 0.8, Dm - 0.3), "dir": "-x"})
		"store", "shed":
			for i in 3: f.append({"p": "barrel", "at": Vector2(0.5 + i * 0.7, Dm - 1.0)})
			if Wm >= 4.0 and hearth != "right": f.append({"p": "shelf", "at": Vector2(Wm - 0.3, Dm - 2.0), "dir": "+y"})
			if kind == "shed": f.append({"p": "table", "at": Vector2(Wm * 0.5 - 0.8, Dm * 0.5)})
		"shrine":
			f.append({"p": "table", "at": Vector2(Wm * 0.5 - 0.8, Dm - 1.4)})
			for i in 3: f.append({"p": "lantern", "at": Vector2(Wm * 0.5 - 0.6 + i * 0.45, Dm - 1.2), "z": 0.8})
			g.lights.append({"at": Vector3(Wm * 0.5, 1.3, -(Dm - 1.1)), "energy": 1.2, "range": 4.0, "color": Color(1.0, 0.8, 0.55)})
		"post":
			f.append({"p": "bench", "at": Vector2(0.4, Dm - 0.7)}); f.append({"p": "lantern", "at": Vector2(Wm * 0.5, Dm * 0.5), "z": 2.2})
