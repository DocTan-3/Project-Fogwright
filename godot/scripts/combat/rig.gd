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
