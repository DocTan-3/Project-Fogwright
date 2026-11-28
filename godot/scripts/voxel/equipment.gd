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
	# a pistol held low at the side, the grip through the fist and the muzzle down at the ground
	"pistol": {"arm_upper_r": Vector3(-6, 0, 4), "arm_lower_r": Vector3(-22, 0, 0), "leg_upper_l": Vector3(0, 0, 4), "leg_upper_r": Vector3(0, 0, -4)},
	# a crossbow at rest in both hands (Doc Tan's references): the right fist at the grip before the right hip, the
	# stock level and pointing across toward the left, the left hand under the fore-stock (aimed in _hold_crossbow)
	"crossbow": {"arm_upper_r": Vector3(-14, 0, 0), "arm_lower_r": Vector3(-48, 0, 0), "arm_upper_l": Vector3(-30, 0, -4), "arm_lower_l": Vector3(-18, 0, 0),
		"leg_upper_l": Vector3(0, 0, 4), "leg_upper_r": Vector3(0, 0, -4)},
	# the off hand: a shield or tower shield held up on the forearm in front of the body; a bow at rest is
	# held low across the body (_rest_bow)
	"shield": {"arm_upper_l": Vector3(-20, 0, -6), "arm_lower_l": Vector3(-70, 0, 0)},
	"bow": {"arm_upper_l": Vector3(-12, 0, 0), "arm_lower_l": Vector3(-30, 0, 0), "arm_lower_r": Vector3(-8, 0, 0),
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

## a crossbow at rest: the stock runs through the right fist along the hand's own +Z; the wrist turns it level and
## across toward the left side, CROSS_ACROSS degrees from straight ahead
const CROSS_ACROSS := 55.0
## a pistol at rest: the muzzle forward and PISTOL_DOWN degrees down, the grip hanging below the barrel
const PISTOL_DOWN := 35.0
static func _hold_crossbow(root: Node3D, pistol := false) -> void:
	for node in root.find_children("weapon*", "Node3D", true, false):
		if not String(node.get_meta("piece", "")).ends_with("@hand_r"): continue
		var hand := node.get_parent() as Node3D
		var arm := _to_root(hand.get_parent(), root)
		var a := deg_to_rad(CROSS_ACROSS)
		var d := Vector3(sin(a), -0.05, cos(a)).normalized()
		if pistol: d = Vector3(0.05, -sin(deg_to_rad(PISTOL_DOWN)), cos(deg_to_rad(PISTOL_DOWN))).normalized()
		var now: Basis = arm.basis * hand.basis
		var aimed: Basis = Basis(Quaternion((now * Vector3.BACK).normalized(), d)) * now
		# then roll about the stock so the prod lies level and the grip hangs below the stock
		var mi := node as MeshInstance3D; var box: AABB = mi.get_aabb()
		var ax := [0, 1, 2]; ax.sort_custom(func(i, j): return box.size[i] > box.size[j])
		var pa := Vector3.ZERO; pa[ax[1]] = 1.0
		var gi: int = ax[1] if pistol else ax[2]                      # a pistol's grip is its second axis
		var ga := Vector3.ZERO; ga[gi] = 1.0 if box.end[gi] + box.position[gi] > 0.0 else -1.0   # the grip's side
		var M: Basis = aimed * mi.basis.orthonormalized()
		var best := aimed; var low := INF
		for k in 72:
			var r := Basis(d, deg_to_rad(k * 5.0)) * aimed
			var Mk: Basis = r * mi.basis.orthonormalized()
			var score: float = (0.0 if pistol else absf((Mk * pa).normalized().y) * 4.0) + (Mk * ga).normalized().y
			if score < low: low = score; best = r
		hand.basis = arm.basis.inverse() * best
		hand.set_meta("rest", hand.rotation_degrees)

## a bow at rest, held low across the body (the user's reference): the grip in the lowered off hand before the hip,
## the bow nearly level, its upper limb rising toward the far side, the string up and toward the body. The bow turns in
## the fist about its grip; the hand stays as the stance left it.
const BOW_RISE := 20.0     # degrees the upper limb rises above level
const BOW_OUT := 12.0      # degrees the bow turns forward, away from the body
## other rest holds to choose from (tests/bow_poses.tscn): the arms' degrees on top of the bow stance, the upper limb's
## direction and the string's side in root (the character faces +Z, its left is +X). "" keeps the hold above.
const BOW_POSES := {
	"A": {"arms": {"arm_upper_l": Vector3(-4, 0, 4), "arm_lower_l": Vector3(-8, 0, 0)}, "D": Vector3(0.12, 1, 0.18), "S": Vector3(-1, 0, 0)},
	"B": {"arms": {"arm_upper_l": Vector3(-14, 0, 4), "arm_lower_l": Vector3(-22, 0, 0)}, "D": Vector3(0.05, 1, -0.55), "S": Vector3(-1, 0, 0.3)},
	"C": {"arms": {"arm_upper_l": Vector3(-12, 0, 2), "arm_lower_l": Vector3(-78, 0, 0)}, "D": Vector3(-0.05, 1, -0.6), "S": Vector3(-1, 0, 0)},
	"D": {"arms": {"arm_upper_l": Vector3(-22, 0, -4), "arm_lower_l": Vector3(-38, 0, 0), "arm_upper_r": Vector3(-18, 0, 4), "arm_lower_r": Vector3(-40, 0, 0)},
		"D": Vector3(1, 0.12, 0.1), "S": Vector3(0, 0.4, -1)},
}
const BOW_REF := {
	"E": {"arms": {"arm_upper_l": Vector3(-2, 0, 4), "arm_lower_l": Vector3(-6, 0, 0)}, "D": Vector3(0, 0.04, 1), "S": Vector3(-0.55, 1, 0), "fist": true},
	"F": {"arms": {"arm_upper_l": Vector3(-6, 0, 2), "arm_lower_l": Vector3(-24, 0, 0)}, "D": Vector3(-0.15, 0.85, -0.5), "S": Vector3(-1, 0.2, -0.3)},
	"G": {"arms": {"arm_upper_l": Vector3(-10, 0, 0), "arm_lower_l": Vector3(-28, 0, 0)}, "D": Vector3(0.95, 0.15, -0.2), "S": Vector3(0, 1, -0.4)},
	"H": {"arms": {"arm_upper_l": Vector3(-4, 0, 4), "arm_lower_l": Vector3(-14, 0, 0)}, "D": Vector3(0.7, 0.6, -0.35), "S": Vector3(-0.2, 0.7, -1)},
}
static var bow_pose := "E"     # the hold Doc Tan chose (their side sketch); "" is the older low-across hold
static func _bp() -> Dictionary: return BOW_POSES[bow_pose] if BOW_POSES.has(bow_pose) else BOW_REF[bow_pose]

static func _rest_bow(root: Node3D) -> void:
	for node in root.find_children("weapon*", "Node3D", true, false):
		if not String(node.get_meta("piece", "")).ends_with("@hand_l"): continue
		var mi := node as MeshInstance3D; var box: AABB = mi.get_aabb()
		var hand := node.get_parent() as Node3D
		var B: Basis = (_to_root(hand.get_parent(), root) * hand.transform).basis.orthonormalized()
		var N: Basis = B * mi.basis.orthonormalized()
		# the limb runs along the box's longest axis, the string along the next (make_equipment.py draws it so)
		var ax := [0, 1, 2]; ax.sort_custom(func(i, j): return box.size[i] > box.size[j])
		var l := Vector3.ZERO; l[ax[0]] = 1.0
		var sv := Vector3.ZERO; sv[ax[1]] = 1.0
		if (N * sv).x > 0.0: sv = -sv                   # the string faces the body (inward from the left hand)
		var pivot := box.get_center(); pivot[ax[1]] = box.position[ax[1]] if sv[ax[1]] > 0.0 else box.end[ax[1]]   # the grip
		var r := deg_to_rad(BOW_RISE); var o := deg_to_rad(BOW_OUT)
		var D := Vector3(-cos(r) * cos(o), sin(r), sin(o)).normalized()     # the upper limb: across to the far side
		var S0 := Vector3(0, 1, -0.5)
		if bow_pose != "": D = (_bp().D as Vector3).normalized(); S0 = _bp().S
		var S := (S0 - D * D.dot(S0)).normalized()
		var target := Basis(D, S, D.cross(S)) * Basis(l, sv, l.cross(sv)).inverse()   # the bow's new frame in root
		var p: Vector3 = mi.transform * pivot
		if bow_pose != "" and _bp().get("fist", false):    # the riser's middle in the middle of the fist
			pivot += sv * box.size[ax[2]] * 0.5
			p = (hand as MeshInstance3D).get_aabb().get_center() if hand is MeshInstance3D else p
		mi.basis = (B.inverse() * target).scaled(mi.basis.get_scale())
		mi.position = p - mi.basis * pivot

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
		if "bow" in kinds and bow_pose != "": st.merge(_bp().arms, true)
		for node in root.find_children("*", "Node3D", true, false):
			if st.has(String(node.name)):
				node.rotation_degrees += st[String(node.name)]; node.set_meta("rest", node.rotation_degrees)
		if "polearm" in kinds: _aim(root)
		if "bow" in kinds: _rest_bow(root)
		if "crossbow" in kinds: _hold_crossbow(root)
	for node in root.find_children("*", "Node3D", true, false):
		if not node.has_meta("piece"): continue
		var bare := String(node.get_meta("piece")).get_slice("@", 0)
		for h in hides:   # an exact piece name, or "name*" for every piece it begins
			if bare == h or (String(h).ends_with("*") and bare.begins_with(String(h).trim_suffix("*"))): node.visible = false
	return root
