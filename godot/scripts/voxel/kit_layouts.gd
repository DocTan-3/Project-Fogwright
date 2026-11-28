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

## The Gull & Lantern, Farhallow's inn (the kit plan's floor-by-floor table), 16 x 12 m, its front on the well square.
## Ground (4.4 m, fieldstone): the taproom (10 x 8) with the hearth on the gable wall, the bar along its partition, four
## tables with benches and a lantern; the hall (6 x 6) with the keeper's counter for rooms and the store; the kitchen
## (6 x 6) with its range, a work table, ale barrels and a side door to the yard; and behind the taproom the stair hall
## (10 x 4), the stair climbing along the back wall. Upper (3.0 m, timber frame): the corridor the length of the house,
## four front guest rooms of 4 x 4 on the square, a back guest room of 4 x 6 with two beds, the landing over the stair,
## and the keeper's room (6 x 6) over the kitchen, warm from its chimney. The attic is closed for now.
const GULL_LANTERN := {
	"size": Vector2i(8, 6),
	"storeys": [
		{"h": 44, "face": "stone",
		 "walls": {"front": "wpdpwpwp", "right": "pwppdp", "back": "pwpppppp", "left": "pwpppw"},
		 "inner": [
			{"at": Vector2i(5, 0), "dir": "y", "bays": "dpppdp", "face": "frame"},   # taproom | hall, stair hall | kitchen
			{"at": Vector2i(0, 4), "dir": "x", "bays": "pdppp", "face": "frame"},    # taproom | stair hall
			{"at": Vector2i(5, 3), "dir": "x", "bays": "pdp", "face": "frame"}],     # hall | kitchen
		 "stairs": [{"at": Vector2i(27, 103), "run": "+x"}],
		 "pieces": [{"p": "hearth", "at": Vector3i(3, 50, 0), "dir": "-y"},         # the taproom's, on the gable wall
			{"p": "hearth", "at": Vector3i(150, 117, 0), "dir": "-x"}],              # the kitchen range
		 "fittings": [
			{"p": "bar_counter", "at": Vector2(8.0, 7.0), "dir": "-y"}, {"p": "bar_counter", "at": Vector2(8.0, 5.0), "dir": "-y"},
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
			{"p": "barrel", "at": Vector2(0.5, 8.5)}, {"p": "barrel", "at": Vector2(0.5, 9.2)}],
		 "lights": [{"at": Vector3(1.6, 1.0, -4.0), "energy": 1.6, "range": 6.0, "color": Color(1.0, 0.62, 0.32)},   # the hearth
			{"at": Vector3(4.9, 3.3, -3.5), "energy": 1.3, "range": 8.0},                                       # the lantern
			{"at": Vector3(13.0, 3.4, -3.0), "energy": 1.0, "range": 6.0}, {"at": Vector3(13.0, 3.4, -9.0), "energy": 1.1, "range": 6.0}]},
		{"h": 30, "face": "frame",
		 "walls": {"front": "pwpwpwpw", "right": "pwwpwp", "back": "pwppwpwp", "left": "pwpwpw"},
		 "inner": [
			{"at": Vector2i(0, 2), "dir": "x", "bays": "pdpdpdpd", "swing": -1},     # front rooms | corridor, doors into the rooms
			{"at": Vector2i(0, 3), "dir": "x", "bays": "pd...dpp"},                  # corridor | back room, landing, keeper (doors inward)
			{"at": Vector2i(2, 0), "dir": "y", "bays": "pp"}, {"at": Vector2i(4, 0), "dir": "y", "bays": "pp"},
			{"at": Vector2i(6, 0), "dir": "y", "bays": "pp"},
			{"at": Vector2i(2, 3), "dir": "y", "bays": "ppp"}, {"at": Vector2i(5, 3), "dir": "y", "bays": "ppp"}],
		 "fittings": [
			{"p": "bed", "at": Vector2(0.4, 0.4)}, {"p": "chest", "at": Vector2(1.6, 0.4)},
			{"p": "bed", "at": Vector2(4.4, 0.4)}, {"p": "chest", "at": Vector2(5.6, 0.4)},
			{"p": "bed", "at": Vector2(8.4, 0.4)}, {"p": "chest", "at": Vector2(9.6, 0.4)},
			{"p": "bed", "at": Vector2(12.4, 0.4)}, {"p": "chest", "at": Vector2(13.6, 0.4)},
			{"p": "bed", "at": Vector2(0.4, 9.6)}, {"p": "bed", "at": Vector2(2.4, 9.6)},
			{"p": "bed", "at": Vector2(11.0, 9.6)}, {"p": "chest", "at": Vector2(12.4, 11.1)}],
		 "lights": [{"at": Vector3(8.0, 7.3, -5.0), "energy": 0.9, "range": 7.0}, {"at": Vector3(13.0, 7.3, -9.0), "energy": 0.9, "range": 5.0}]},
	],
	"roof": "thatch",
	"chimneys": [{"at": Vector2i(3, 32), "from": 15, "above": 52}, {"at": Vector2i(136, 109), "from": 15, "above": 30}],
}
