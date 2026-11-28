## A telegraph on the ground: the shape an attack will hit, coloured by its kind (CombatRules.KINDS), the inner fill growing
## to the edge as the wind-up runs out, so the moment of the hit can be read.
class_name Telegraph
extends Node3D

var _fill: MeshInstance3D
var _t := 0.0
var _len := 1.0

static func _mat(c: Color, a: float) -> StandardMaterial3D:
	var m := StandardMaterial3D.new(); m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA; m.albedo_color = Color(c.r, c.g, c.b, a)
	m.cull_mode = BaseMaterial3D.CULL_DISABLED; m.no_depth_test = false; m.render_priority = 1
	return m

static func _shape_mesh(shape: Dictionary) -> Mesh:
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	match shape.type:
		"circle":
			var n := 40
			for i in n:
				var a0 := TAU * i / n; var a1 := TAU * (i + 1) / n
				st.add_vertex(Vector3.ZERO); st.add_vertex(Vector3(sin(a1), 0, cos(a1)) * shape.r); st.add_vertex(Vector3(sin(a0), 0, cos(a0)) * shape.r)
		"cone":
			var n := 20; var half: float = shape.angle / 2.0
			for i in n:
				var ang: float = shape.angle; var a0: float = -half + ang * i / n; var a1: float = -half + ang * (i + 1) / n
				st.add_vertex(Vector3.ZERO); st.add_vertex(Vector3(sin(a1), 0, cos(a1)) * shape.len); st.add_vertex(Vector3(sin(a0), 0, cos(a0)) * shape.len)
		"line":
			var w: float = shape.w / 2.0; var l: float = shape.len
			for v in [Vector3(-w, 0, 0), Vector3(w, 0, l), Vector3(w, 0, 0), Vector3(-w, 0, 0), Vector3(-w, 0, l), Vector3(w, 0, l)]: st.add_vertex(v)
	return st.commit()

## shape: {type: circle (r) | cone (len, angle) | line (len, w)}, pointing along the node's +Z
func setup(shape: Dictionary, kind: String, windup: float) -> void:
	var c: Color = CombatRules.KINDS[kind].color
	var edge := MeshInstance3D.new(); edge.mesh = _shape_mesh(shape); edge.material_override = _mat(c, 0.22); add_child(edge)
	_fill = MeshInstance3D.new(); _fill.mesh = edge.mesh; _fill.material_override = _mat(c, 0.42); add_child(_fill)
	_fill.position.y = 0.01; _fill.scale = Vector3(0.02, 1, 0.02); _len = maxf(windup, 0.05)

func _process(delta: float) -> void:
	_t += delta
	var k := clampf(_t / _len, 0.0, 1.0)
	if _fill: _fill.scale = Vector3(k, 1, k)

## is a point (world) inside the shape (this node's transform)?
static func contains(shape: Dictionary, origin: Vector3, forward: Vector3, p: Vector3, pad := 0.35) -> bool:
	var d := Vector3(p.x - origin.x, 0, p.z - origin.z); var f := Vector3(forward.x, 0, forward.z).normalized()
	match shape.type:
		"circle": return d.length() <= shape.r + pad
		"cone":
			if d.length() > shape.len + pad: return false
			return d.length() < 0.6 or absf(f.signed_angle_to(d.normalized(), Vector3.UP)) <= shape.angle / 2.0 + 0.08
		"line":
			var along := d.dot(f); var side := absf(d.dot(f.cross(Vector3.UP)))
			return along >= -pad and along <= shape.len + pad and side <= shape.w / 2.0 + pad
	return false
