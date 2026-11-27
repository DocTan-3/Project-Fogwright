## The first slice: a street, the player and the camera. The character model (Quaternius Universal Base Characters) and
## the animation library (Universal Animation Library) share one rig, so the library is added to the model as is.
extends Node3D

const ANIMS := "res://assets/animations/quaternius/UAL1_Standard.glb"

func _ready() -> void:
	var model: Node3D = $Player/Model
	var lib_scene: Node = load(ANIMS).instantiate()
	var src: AnimationPlayer = lib_scene.find_child("AnimationPlayer", true, false)
	var ap := AnimationPlayer.new()
	ap.name = "AnimationPlayer"
	model.add_child(ap)
	ap.root_node = NodePath("..")
	var lib: AnimationLibrary = src.get_animation_library("").duplicate()
	ap.add_animation_library("ual", lib)
	lib_scene.free()
	$Player._anim = ap
	ap.play("ual/Idle")
