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
const FACE := "res://assets/voxel/characters/peoples/faces/%s_%s_%d.vox"
const STYLE := "res://assets/voxel/characters/peoples/%s/%s_%s_%s.vox"
const FACES := "res://data/faces.json"
static var _faces := {}
static func faces() -> Dictionary:
	if _faces.is_empty(): _faces = JSON.parse_string(FileAccess.get_file_as_string(FACES))
	return _faces
static var _db := {}
## the drawn stances, by weapon class: degrees added to Vox.REST (game axes; negative x swings a limb forward)
const STANCES := {
	"one_hand": {"arm_upper_r": Vector3(-6, 0, 0), "arm_lower_r": Vector3(-40, 0, 0), "arm_lower_l": Vector3(-25, 0, 0),
		"leg_upper_l": Vector3(0, 0, 4), "leg_upper_r": Vector3(0, 0, -4)},
	# a spear carried low (the user's reference): the arm hangs nearly straight, a little forward, the fist at the hip;
	# the spear lies in the grip, slanting down and forward across the body (aimed in _aim)
	"polearm": {"arm_upper_r": Vector3(-10, 0, 4), "arm_lower_r": Vector3(-18, 0, 0), "arm_lower_l": Vector3(-30, 0, 0),
		"leg_upper_l": Vector3(0, 0, 4), "leg_upper_r": Vector3(0, 0, -4)},
	# the off hand: a shield or buckler held up on the forearm in front of the body; a bow held out level, upright
	# a walking staff planted beside the bearer, the arm a little forward
	"staff": {"arm_upper_r": Vector3(-8, 0, -4), "arm_lower_r": Vector3(-22, 0, 0)},
	"shield": {"arm_upper_l": Vector3(-20, 0, -6), "arm_lower_l": Vector3(-70, 0, 0)},
	"bow": {"arm_upper_l": Vector3(-82, 0, -4), "arm_lower_l": Vector3(-4, 0, 0), "arm_upper_r": Vector3(-40, 0, 8), "arm_lower_r": Vector3(-60, 0, 0),
		"leg_upper_l": Vector3(0, 0, 4), "leg_upper_r": Vector3(0, 0, -4)},
}
## stances that hold the off hand win over the main hand's for the left arm (a sword's stance with a shield's)
const OFF_STANCES := ["shield", "bow"]

## a drawn polearm, carried low: its point slants down and forward, turned this far across the body toward the off side,
## at most POLE_DOWN below level; the slant eases if the point would come within POLE_CLEAR of the ground (short bodies)
const POLE_ACROSS := 25.0      # toward the off (left) side: +X is the character's left (checked from above)
const POLE_DOWN := 22.0
const POLE_CLEAR := 0.12

static func _to_root(node: Node, root: Node) -> Transform3D:
	var t := Transform3D()
	while node != root and node != null:
		t = (node as Node3D).transform * t; node = node.get_parent()
	return t

static func _aim(root: Node3D) -> void:
	# the haft runs through the fist along the hand's own +Z (forward when the hand hangs); the wrist turns the hand the
	# least it must so the haft lies along the carry direction
	for node in root.find_children("weapon*", "Node3D", true, false):
		if not String(node.get_meta("piece", "")).ends_with("@hand_r"): continue   # only the main hand's polearm
		var hand := node.get_parent() as Node3D
		var arm := _to_root(hand.get_parent(), root)
		var rest := hand.basis
		for down in range(int(POLE_DOWN), -30, -2):
			# the character faces +Z and its left is +X
			var d := Vector3(sin(deg_to_rad(POLE_ACROSS)) * cos(deg_to_rad(down)), -sin(deg_to_rad(down)), cos(deg_to_rad(POLE_ACROSS)) * cos(deg_to_rad(down))).normalized()
			var now: Basis = arm.basis * rest
			hand.basis = arm.basis.inverse() * (Basis(Quaternion((now * Vector3.BACK).normalized(), d)) * now)
			var bb: AABB = (arm * hand.transform * (node as Node3D).transform) * (node as MeshInstance3D).get_aabb()
			var low := INF
			for k in 8: low = minf(low, bb.get_endpoint(k).y)
			if low >= POLE_CLEAR: break
		hand.set_meta("rest", hand.rotation_degrees)

## a walking staff stands upright whatever the arm does: the wrist turns the hand the least it must
static func _upright(root: Node3D) -> void:
	for node in root.find_children("weapon*", "Node3D", true, false):
		if not String(node.get_meta("piece", "")).ends_with("@hand_r"): continue
		var hand := node.get_parent() as Node3D
		var arm := _to_root(hand.get_parent(), root)
		var now: Basis = arm.basis * hand.basis
		hand.basis = arm.basis.inverse() * (Basis(Quaternion((now * Vector3.UP).normalized(), Vector3.UP)) * now)
		hand.set_meta("rest", hand.rotation_degrees)

static func db() -> Dictionary:
	if _db.is_empty(): _db = JSON.parse_string(FileAccess.get_file_as_string(DATA))
	return _db

## the items of a set, by its tier name (light, medium, heavy, plate, rig)
static func set_items(tier: String) -> Array: return db().sets[tier].items

## look: the creator's hair, beard and hair_col ([r, g, b] 0-255); anything left out comes from the face preset
## (data/faces.json). Hair "shaved" and beard null (clean-shaven) leave none.
static func dress(people: String, sex: String, worn: Array, wardrobe := true, drawn := true, face := 0, height := 0.0, bulk := 0.0, look := {}) -> Node3D:
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
	if face > 0: layers.append(FACE % [people, sex, face])   # a face preset (data/faces.json), before any helm
	var lk: Dictionary = faces().presets["%s_%s" % [people, sex]][face].duplicate(); lk.merge(look, true)
	if lk.hair != "shaved": layers.append(STYLE % ["hair", people, sex, lk.hair])
	if lk.beard != null: layers.append(STYLE % ["beard", people, sex, lk.beard])
	if wardrobe: layers.append(BODY % [people, sex, "_clothes"])
	var hides := []
	for n in order:
		var file: String = items[n].carried if (not drawn and items[n].has("carried")) else items[n].file
		layers.append(file % [people, sex])
		hides.append_array(items[n].hides)
	var hc: Array = lk.hair_col
	var root := Vox.character(BODY % [people, sex, ""], Vox.FINE, [], layers, Color8(hc[0], hc[1], hc[2]))
	for node in root.find_children("*", "Node3D", true, false):   # shaved, clean-shaven: the base's own go
		if not is_instance_valid(node) or not node.has_meta("piece"): continue
		var g := Vox.group(String(node.get_meta("piece")))
		if (g == "hair" and lk.hair == "shaved") or (g == "beard" and lk.beard == null): node.get_parent().remove_child(node); node.free()
	if height != 0.0 or bulk != 0.0: Vox.shape(root, height, bulk)   # the creator's body sliders
	if drawn:
		var st := {}; var kinds := []
		for n in order:
			if items[n].has("stance"): kinds.append(items[n].stance)
		kinds.sort_custom(func(a, b): return not (a in OFF_STANCES) and (b in OFF_STANCES))   # off-hand stances last
		for k in kinds: st.merge(STANCES[k], true)
		for node in root.find_children("*", "Node3D", true, false):
			if st.has(String(node.name)):
				node.rotation_degrees += st[String(node.name)]; node.set_meta("rest", node.rotation_degrees)
		if "polearm" in kinds: _aim(root)
		if "staff" in kinds: _upright(root)
	for node in root.find_children("*", "Node3D", true, false):
		if not node.has_meta("piece"): continue
		var bare := String(node.get_meta("piece")).get_slice("@", 0)
		for h in hides:   # an exact piece name, or "name*" for every piece it begins
			if bare == h or (String(h).ends_with("*") and bare.begins_with(String(h).trim_suffix("*"))): node.visible = false
	return root
