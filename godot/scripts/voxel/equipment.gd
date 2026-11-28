class_name Equipment
## Dresses a voxel character in equipment (docs/design.md, Equipment). Items are recipes fitted to each body offline
## (tools/voxel/make_equipment.py), one layer file per item and body; data/equipment.json lists each item's slots, its
## place in the layering order and what it hides.
##   - the base body (its underwear), then the wardrobe (starting clothes), then the items from the inside out: a later
##     layer's part replaces an earlier one of the same name (Vox.character's layers), so nothing pokes through;
##   - two items may not share a slot: dress() refuses and says which;
##   - what an item hides (a helm the hair and hanging beard, a hood the hair) is hidden;
##   - two idle stances: weapons put away (the relaxed rest pose, weapons carried at the hip or across the back) and
##     drawn (the weapon in hand and its class's stance, degrees added to the rest pose; animation adds to the result).
const DATA := "res://data/equipment.json"
const BODY := "res://assets/voxel/characters/peoples/%s_%s%s.vox"
static var _db := {}
## the drawn stances, by weapon class: degrees added to Vox.REST (game axes; negative x swings a limb forward)
const STANCES := {
	"one_hand": {"arm_upper_r": Vector3(-6, 0, 0), "arm_lower_r": Vector3(-40, 0, 0), "arm_lower_l": Vector3(-25, 0, 0),
		"leg_upper_l": Vector3(0, 0, 4), "leg_upper_r": Vector3(0, 0, -4)},
	"polearm": {"arm_upper_r": Vector3(-10, 0, 0), "arm_lower_r": Vector3(-65, 0, 0), "arm_lower_l": Vector3(-20, 0, 0),
		"leg_upper_l": Vector3(0, 0, 4), "leg_upper_r": Vector3(0, 0, -4)},
}

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
	if drawn:
		for n in order:
			if not items[n].has("stance"): continue
			var st: Dictionary = STANCES[items[n].stance]
			for node in root.find_children("*", "Node3D", true, false):
				if st.has(String(node.name)):
					node.rotation_degrees += st[String(node.name)]; node.set_meta("rest", node.rotation_degrees)
	for node in root.find_children("*", "Node3D", true, false):
		var bare := String(node.name).get_slice("@", 0).get_slice("_head", 0)
		if String(node.name).validate_node_name() in hides.map(func(h): return String(h).validate_node_name()) or bare in hides:
			node.visible = false
	return root
