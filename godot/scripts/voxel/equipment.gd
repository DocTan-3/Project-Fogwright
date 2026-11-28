class_name Equipment
## Dresses a voxel character in equipment (docs/design.md, Equipment). Items are recipes fitted to each body offline
## (tools/voxel/make_equipment.py), one layer file per item and body; data/equipment.json lists each item's slots, its
## place in the layering order and what it hides.
##   - the base body (its underwear), then the wardrobe (starting clothes), then the items from the inside out: a later
##     layer's part replaces an earlier one of the same name (Vox.character's layers), so nothing pokes through;
##   - two items may not share a slot: dress() refuses and says which;
##   - what an item hides (a helm the hair and hanging beard, a hood the hair) is hidden;
##   - weapons are in hand when drawn, else carried where they belong (at the hip, across the back).
const DATA := "res://data/equipment.json"
const BODY := "res://assets/voxel/characters/peoples/%s_%s%s.vox"
static var _db := {}

static func db() -> Dictionary:
	if _db.is_empty(): _db = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	return _db

## the items of a set, by its tier name (light, medium, heavy, plate, rig)
static func set_items(tier: String) -> Array: return db().sets[tier].items

static func dress(people: String, sex: String, worn: Array, wardrobe := true, drawn := true) -> Node3D:
	var items: Dictionary = db().items
	var taken := {}
	for n in worn:
		if not items.has(n): push_error("no item " + n); return null
		for s in items[n].slots:
			if taken.has(s): push_error("%s and %s both take the %s slot" % [taken[s], n, s]); return null
			taken[s] = n
	var order := worn.duplicate()
	order.sort_custom(func(a, b): return items[a].order < items[b].order)
	var layers := []
	if wardrobe: layers.append(BODY % [people, sex, "_clothes"])
	var hides := []
	for n in order:
		var file: String = items[n].carried if (not drawn and items[n].has("carried")) else items[n].file
		layers.append(file % [people, sex])
		hides.append_array(items[n].hides)
	var root := Vox.character(BODY % [people, sex, ""], Vox.FINE, [], layers)
	for node in root.find_children("*", "Node3D", true, false):
		var bare := String(node.name).get_slice("@", 0).get_slice("_head", 0)
		if String(node.name).validate_node_name() in hides.map(func(h): return String(h).validate_node_name()) or bare in hides:
			node.visible = false
	return root
