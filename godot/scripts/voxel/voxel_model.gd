## The player's model as a voxel character: the stylized Hrimfolk with sample gear (docs/voxel-characters.md)
extends Node3D
@export var character := "res://assets/voxel/characters/hrim_stylized.vox"
@export var gear: PackedStringArray = ["res://assets/voxel/gear/hrim_pauldron_l.vox", "res://assets/voxel/gear/hrim_pauldron_r.vox",
	"res://assets/voxel/gear/hrim_goggles.vox", "res://assets/voxel/gear/hrim_toolbelt.vox"]
func _ready() -> void:
	add_child(Vox.character(character, Vox.FINE, [], Array(gear)))
