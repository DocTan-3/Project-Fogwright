## A humanoid that plays the shared animation libraries: the Quaternius base character (one rig with the libraries), with
## both libraries added as "ual" (UAL1) and "ual2" (UAL2). Godot's importer drops a clip's "_Loop" suffix and loops it.
class_name CombatRig
extends RefCounted

const LIBS := {"ual": "res://assets/animations/quaternius/UAL1_Standard.glb", "ual2": "res://assets/animations/quaternius/UAL2_Standard.glb"}
static var _libs := {}

static func library(key: String) -> AnimationLibrary:
	if not _libs.has(key):
		var scene: Node = (load(LIBS[key]) as PackedScene).instantiate()
		var src: AnimationPlayer = scene.find_child("AnimationPlayer", true, false)
		_libs[key] = src.get_animation_library("").duplicate()
		scene.free()
	return _libs[key]

## add the libraries to a model: returns its AnimationPlayer
static func animate(model: Node3D, keys := ["ual", "ual2"]) -> AnimationPlayer:
	var ap := model.get_node_or_null("AnimationPlayer") as AnimationPlayer
	if ap == null:
		ap = AnimationPlayer.new(); ap.name = "AnimationPlayer"; model.add_child(ap); ap.root_node = NodePath("..")
	for k in keys:
		if not ap.has_animation_library(k): ap.add_animation_library(k, library(k))
	return ap

## something held in a hand (a BoneAttachment3D on hand_r or hand_l)
static func hold(model: Node3D, bone: String, path: String, scale := 1.0, rot := Vector3(0, 0, 0)) -> Node3D:
	var skel := model.find_children("*", "Skeleton3D", true, false)
	if skel.is_empty() or not ResourceLoader.exists(path): return null
	var att := BoneAttachment3D.new(); att.bone_name = bone; (skel[0] as Skeleton3D).add_child(att)
	var item: Node3D = (load(path) as PackedScene).instantiate(); att.add_child(item)
	item.scale = Vector3.ONE * scale; item.rotation_degrees = rot
	Palette.apply(item)
	return item

## a weapon in the hands as its definition says (scripts/combat/weapons.gd): "model" in the right hand, "offhand" in the
## left, each with its "grip" (rotation in degrees and offset in metres, in the hand bone's frame; measured by eye with
## tests/hold_sheet.tscn)
static func hold_weapon(model: Node3D, W: Dictionary, grip := {}) -> Array:
	var held := []
	var g: Dictionary = grip if not grip.is_empty() else W.get("grip", {})
	if W.has("model"):
		var n := hold(model, W.get("hand", "hand_r"), W.model, float(W.get("model_scale", 1.0)), g.get("rot", Vector3.ZERO))
		if n:
			n.position = g.get("off", Vector3.ZERO); held.append(n)
			if g.has("basis"):   # a grip given as where the model's axes go in the hand (x, y, z), when no rotation reads clearly
				var b: Array = g.basis; n.basis = Basis(b[0], b[1], b[2]).scaled(Vector3.ONE * float(W.get("model_scale", 1.0)))
			if g.has("slide"):   # the model moved along its own axes, for models whose origin is not at the grip (the bronze axe: its middle)
				n.position += n.basis * (g.slide as Vector3)
	if W.has("offhand"):
		var og: Dictionary = W.get("offgrip", {})
		var n2 := hold(model, "hand_l", W.offhand, float(W.get("offhand_scale", 1.0)), og.get("rot", Vector3.ZERO))
		if n2:
			n2.position = og.get("off", Vector3.ZERO); held.append(n2)
			if og.has("slide"): n2.position += n2.basis * (og.slide as Vector3)
	return held
