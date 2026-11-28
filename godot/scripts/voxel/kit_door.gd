## a door of the voxel building kit (scripts/voxel/building_kit.gd): its leaf hangs on a hinge at this node's origin,
## running along +X, its inner side toward -Z. It swings 100 degrees inward when someone walks up to it and stays open:
## doors remember whether they are open (docs/design.md, Voxel buildings and interiors). `open` is the state to save.
class_name KitDoor
extends Node3D

const W := 1.4
const H := 2.2
const SWING := 100.0
var leaf_mesh: Mesh
var open := false
var _swing: Node3D
var _angle := 0.0

func _ready() -> void:
	_swing = Node3D.new(); _swing.name = "Swing"; add_child(_swing)
	var leaf := MeshInstance3D.new(); leaf.name = "Leaf"; leaf.mesh = leaf_mesh; leaf.material_override = Vox.material(); _swing.add_child(leaf)
	var body := AnimatableBody3D.new(); body.sync_to_physics = false; _swing.add_child(body)
	var cs := CollisionShape3D.new(); var sh := BoxShape3D.new(); sh.size = Vector3(W, H, 0.2); cs.shape = sh
	cs.position = Vector3(W * 0.5, H * 0.5, -0.1); body.add_child(cs)
	# the doorway, to the camera alone (layer 3): its spring arm stops here, so it never backs out through the door
	var cam := StaticBody3D.new(); cam.collision_layer = 4; cam.collision_mask = 0; add_child(cam)
	var cc := CollisionShape3D.new(); var csh := BoxShape3D.new(); csh.size = Vector3(W, H, 0.3); cc.shape = csh
	cc.position = Vector3(W * 0.5, H * 0.5, -0.05); cam.add_child(cc)
	# who comes near: 1.5 m either side of the opening
	var area := Area3D.new(); area.monitorable = false; add_child(area)
	var ac := CollisionShape3D.new(); var ash := BoxShape3D.new(); ash.size = Vector3(W, H, 3.0); ac.shape = ash
	ac.position = Vector3(W * 0.5, H * 0.5, -0.1); area.add_child(ac)
	area.body_entered.connect(func(b: Node) -> void: if b is CharacterBody3D: open = true)
	_angle = SWING if open else 0.0; _swing.rotation_degrees.y = _angle

func _physics_process(delta: float) -> void:
	var want := SWING if open else 0.0
	if absf(want - _angle) < 0.01: return
	_angle = move_toward(_angle, want, 160.0 * delta)
	_swing.rotation_degrees.y = _angle
