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
	"storeys": [
		{"h": 44, "face": "dry",
		 "walls": {"front": "wpdpwpwp", "right": "pwppdp", "back": "pwpppppp", "left": "pwpppw"},
		 "inner": [
			{"at": Vector2i(5, 0), "dir": "y", "bays": "dpppdp", "face": "board"},   # taproom | hall, stair hall | kitchen
			{"at": Vector2i(0, 4), "dir": "x", "bays": "pdppp", "face": "board"},    # taproom | stair hall
			{"at": Vector2i(5, 3), "dir": "x", "bays": "pdp", "face": "board"}],     # hall | kitchen
		 "stairs": [{"at": Vector2i(27, 103), "run": "+x"}],
		 "pieces": [{"p": "hearth", "at": Vector3i(3, 50, 0), "dir": "-y"},         # the taproom's, on the gable wall
			{"p": "hearth", "at": Vector3i(150, 117, 0), "dir": "-x"},               # the kitchen range
			{"p": "waystone", "at": Vector3i(33, -7, -5)}],                          # Hollin's, by the door
		 "fittings": [
			{"p": "bar_keel", "at": Vector2(8.0, 7.0), "dir": "-y"}, {"p": "bar_keel", "at": Vector2(8.0, 5.0), "dir": "-y"},
			{"p": "shelf", "at": Vector2(9.85, 4.2), "dir": "+y"},
			{"p": "barrel", "at": Vector2(9.15, 6.0)}, {"p": "barrel", "at": Vector2(9.15, 6.8)},
			{"p": "table", "at": Vector2(1.2, 1.2)}, {"p": "bench", "at": Vector2(1.2, 0.8)}, {"p": "bench", "at": Vector2(1.2, 2.1)},
			{"p": "table", "at": Vector2(6.2, 1.2)}, {"p": "bench", "at": Vector2(6.2, 0.8)}, {"p": "bench", "at": Vector2(6.2, 2.1)},
			{"p": "table", "at": Vector2(2.2, 4.2)}, {"p": "bench", "at": Vector2(2.2, 3.8)}, {"p": "bench", "at": Vector2(2.2, 5.1)},
			{"p": "table", "at": Vector2(5.4, 4.6)}, {"p": "bench", "at": Vector2(5.4, 4.2)}, {"p": "bench", "at": Vector2(5.4, 5.5)},
			{"p": "lantern", "at": Vector2(4.8, 3.4), "z": 3.0},
			{"p": "desk", "at": Vector2(12.0, 3.0)}, {"p": "shelf", "at": Vector2(15.6, 5.9), "dir": "-x"},
			{"p": "chest", "at": Vector2(14.6, 0.5)},
			{"p": "table", "at": Vector2(11.0, 9.6)},
			{"p": "barrel", "at": Vector2(15.2, 6.4)}, {"p": "barrel", "at": Vector2(15.2, 7.1)},
			{"p": "barrel", "at": Vector2(0.5, 8.5)}, {"p": "barrel", "at": Vector2(0.5, 9.2)},
			{"p": "vigil_lantern", "at": Vector2(6.4, 0.0), "dir": "-x", "z": 1.7},   # the Lantern, over the door
			{"p": "gull", "at": Vector2(-0.25, 5.7), "dir": "+y", "z": 11.9}],        # the Gull, on the gable
		 "lights": [{"at": Vector3(1.6, 1.0, -4.0), "energy": 1.6, "range": 6.0, "color": Color(1.0, 0.62, 0.32)},   # the hearth
			{"at": Vector3(4.9, 3.3, -3.5), "energy": 1.3, "range": 8.0},                                       # the lantern
			{"at": Vector3(13.0, 3.4, -9.0), "energy": 1.1, "range": 6.0},                                      # the kitchen
			{"at": Vector3(6.15, 2.4, 0.3), "energy": 1.4, "range": 6.0, "color": Color(1.0, 0.72, 0.42)}]},    # the Vigil lantern
		{"h": 12, "face": "dry",
		 "walls": {"front": "pDpDpDpD", "right": "pppppp", "back": "pDppppDp", "left": "pppppp"},
		 "inner": [
			{"at": Vector2i(0, 2), "dir": "x", "bays": "pdpdpdpd", "swing": -1, "face": "board", "h": 30},   # front rooms | corridor
			{"at": Vector2i(0, 3), "dir": "x", "bays": "pd...dpp", "face": "board", "h": 30},   # corridor | back room, landing, keeper
			{"at": Vector2i(2, 0), "dir": "y", "bays": "pp", "face": "board", "h": 30}, {"at": Vector2i(4, 0), "dir": "y", "bays": "pp", "face": "board", "h": 30},
			{"at": Vector2i(6, 0), "dir": "y", "bays": "pp", "face": "board", "h": 30},
			{"at": Vector2i(2, 3), "dir": "y", "bays": "ppp", "face": "board", "h": 30}, {"at": Vector2i(5, 3), "dir": "y", "bays": "ppp", "face": "board", "h": 30}],
		 "fittings": [
			{"p": "bed", "at": Vector2(0.4, 0.4)}, {"p": "chest", "at": Vector2(1.6, 0.4)},
			{"p": "bed", "at": Vector2(4.4, 0.4)}, {"p": "chest", "at": Vector2(5.6, 0.4)},
			{"p": "bed", "at": Vector2(8.4, 0.4)}, {"p": "chest", "at": Vector2(9.6, 0.4)},
			{"p": "bed", "at": Vector2(12.4, 0.4)}, {"p": "chest", "at": Vector2(13.6, 0.4)},
			{"p": "bed", "at": Vector2(0.4, 9.6)}, {"p": "bed", "at": Vector2(2.4, 9.6)},
			{"p": "bed", "at": Vector2(11.0, 9.6)}, {"p": "chest", "at": Vector2(12.4, 11.1)}],
		 "lights": [{"at": Vector3(8.0, 7.0, -5.0), "energy": 0.9, "range": 7.0}, {"at": Vector3(13.0, 7.0, -9.0), "energy": 0.9, "range": 5.0}]},
	],
	"roof": "heather",
	"gable_windows": [5.0],
	"chimneys": [{"at": Vector2i(3, 32), "from": 15, "above": 50}, {"at": Vector2i(136, 109), "from": 15, "above": 22}],
}
