## Voxel models built in code for the prologue (the gate, the pier, the boat, the Fog dog, the Wrought, props): boxes of
## voxels are filled into a set in Godot axes (x, y up, z) and meshed once with Vox.mesh, so one model or part costs one
## draw call. A little colour jitter per voxel keeps big faces from reading as plastic.
class_name VBox
extends RefCounted

var cells := {}      # Vector3i (Vox.mesh's file space) -> Color
var size := 0.1

func _init(voxel := 0.1) -> void: size = voxel

## a box in metres (Godot axes), corners lo and hi; jitter: how much each voxel's brightness may vary
func box(lo: Vector3, hi: Vector3, col: Color, jitter := 0.04, seed_ := 0) -> VBox:
	var a := Vector3i((lo / size).floor()); var b := Vector3i((hi / size).ceil())
	for x in range(a.x, b.x):
		for y in range(a.y, b.y):
			for z in range(a.z, b.z): put(Vector3i(x, y, z), col, jitter, seed_)
	return self

## one voxel by its Godot-axes index
func put(g: Vector3i, col: Color, jitter := 0.0, seed_ := 0) -> void:
	var c := col
	if jitter > 0.0:
		var h := float(hash(g * 7 + Vector3i(seed_, 0, 0)) % 1000) / 1000.0
		var f := 1.0 + (h - 0.5) * 2.0 * jitter; c = Color(clampf(c.r * f, 0, 1), clampf(c.g * f, 0, 1), clampf(c.b * f, 0, 1))
	cells[Vector3i(g.x, -g.z - 1, g.y)] = c

func erase(g: Vector3i) -> void: cells.erase(Vector3i(g.x, -g.z - 1, g.y))

## a filled ellipsoid (centre, radii in metres)
func blob(c: Vector3, r: Vector3, col: Color, jitter := 0.06, seed_ := 0) -> VBox:
	var a := Vector3i(((c - r) / size).floor()); var b := Vector3i(((c + r) / size).ceil())
	for x in range(a.x, b.x):
		for y in range(a.y, b.y):
			for z in range(a.z, b.z):
				var p := (Vector3(x, y, z) + Vector3.ONE * 0.5) * size - c
				if (p / r).length_squared() <= 1.0: put(Vector3i(x, y, z), col, jitter, seed_)
	return self

## a beam from a to b, w metres thick
func beam(a: Vector3, b: Vector3, w: float, col: Color, jitter := 0.04) -> VBox:
	var n := maxi(1, int(a.distance_to(b) / (size * 0.5)))
	for i in n + 1:
		var p := a.lerp(b, float(i) / n)
		box(p - Vector3.ONE * w * 0.5, p + Vector3.ONE * w * 0.5, col, jitter)
	return self

## the mesh, with vertices relative to `pivot` (metres, Godot axes)
func mesh(pivot := Vector3.ZERO) -> ArrayMesh:
	var pf := Vector3(pivot.x, -pivot.z, pivot.y) / size
	return Vox.mesh(cells, Vector3i.ZERO, pf, size)

func node(pivot := Vector3.ZERO, nm := "VBox") -> MeshInstance3D:
	var mi := MeshInstance3D.new(); mi.name = nm; mi.mesh = mesh(pivot); mi.material_override = Vox.grain_material(size)
	mi.position = pivot
	return mi

static func hexc(s: String) -> Color: return Color(s)

## a box collider in a static body
static func collider(parent: Node3D, centre: Vector3, sz: Vector3, rot_y := 0.0) -> StaticBody3D:
	var sb := StaticBody3D.new(); var cs := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = sz
	cs.shape = bs; sb.add_child(cs); sb.position = centre; sb.rotation.y = rot_y; parent.add_child(sb)
	return sb
