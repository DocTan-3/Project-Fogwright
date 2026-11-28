## A Farhallow villager in the prologue: a voxel person of their people (Equipment.dress), walking with VoxelWalk,
## standing at their work, turning their head to the player nearby, and, when told, walking or running a route
## (go). `greyed` is the half-changed look of beat 5: grey veins over the skin, the colour going out of them, and
## a body that moves wrongly (twitches, a dragged step, the head at an angle).
class_name PrologueVillager
extends CharacterBody3D

signal arrived
var display_name := ""
var model: Node3D
var walk: VoxelWalk
var route: Array = []        # Vector3 points still to walk
var speed := 1.6
var player: Node3D
var working := ""            # "hammer", "mend", "": an idle motion at their work
var greyed := 0.0            # 0..1
var _t := 0.0
var _twitch := 0.0
var _head: Node3D
const GRAVITY := 14.0

static func make(people: String, sex: String, worn: Array, face: int, name_: String, look := {}) -> PrologueVillager:
	var v := PrologueVillager.new(); v.name = name_.replace(" ", ""); v.display_name = name_
	var cs := CollisionShape3D.new(); var cap := CapsuleShape3D.new(); cap.radius = 0.28; cap.height = 1.6; cs.shape = cap; cs.position.y = 0.8; v.add_child(cs)
	var holder := Node3D.new(); holder.name = "Model"; v.add_child(holder)
	var m := Equipment.dress(people, sex, worn, true, true, face, 0.0, 0.0, look)
	if m: holder.add_child(m)
	v.model = holder
	v.walk = VoxelWalk.new(); v.walk.name = "Walk"; v.add_child(v.walk)
	v.collision_layer = 1; v.collision_mask = 1
	return v

func _ready() -> void:
	_head = model.find_child("head", true, false) as Node3D
	_t = randf() * 10.0

func go(points: Array, spd := 1.6) -> void:
	route = points.duplicate(); speed = spd

func face(p: Vector3) -> void:
	var d := p - global_position; if Vector2(d.x, d.z).length() > 0.05: model.rotation.y = atan2(d.x, d.z)

func _physics_process(delta: float) -> void:
	_t += delta
	var v := Vector3.ZERO
	if not route.is_empty():
		var to: Vector3 = route[0] - global_position; to.y = 0
		if to.length() < 0.4:
			route.pop_front()
			if route.is_empty(): arrived.emit()
		else:
			var sp := speed
			if greyed > 0.5: sp *= 0.55 + 0.45 * absf(sin(_t * 2.1))   # a dragged, uneven step
			v = to.normalized() * sp
			model.rotation.y = lerp_angle(model.rotation.y, atan2(v.x, v.z), 1.0 - exp(-8.0 * delta))
	velocity.x = lerpf(velocity.x, v.x, 1.0 - exp(-10.0 * delta)); velocity.z = lerpf(velocity.z, v.z, 1.0 - exp(-10.0 * delta))
	velocity.y = 0.0 if is_on_floor() else velocity.y - GRAVITY * delta
	move_and_slide()
	_pose(delta)

func _pose(delta: float) -> void:
	var ex := {}
	if route.is_empty() and player and greyed < 0.5 and _head:   # turn the head toward the player close by
		var d := player.global_position - global_position
		if d.length() < 4.5:
			var local := wrapf(atan2(d.x, d.z) - model.rotation.y, -PI, PI)
			ex["head"] = Vector3(0, clampf(rad_to_deg(local), -60, 60), 0)
	match working:
		"hammer":
			var k := maxf(0.0, sin(_t * 4.0)); ex["arm_upper_r"] = Vector3(-60.0 - 60.0 * k, 0, 0); ex["arm_lower_r"] = Vector3(-40.0 * k, 0, 0)
		"mend":
			ex["arm_upper_r"] = Vector3(-35 + 8 * sin(_t * 3.0), 0, -8); ex["arm_upper_l"] = Vector3(-35 + 8 * sin(_t * 3.0 + 1.5), 0, 8)
			ex["arm_lower_r"] = Vector3(-50, 0, 0); ex["arm_lower_l"] = Vector3(-50, 0, 0)
		"wave":
			ex["arm_upper_r"] = Vector3(-150, 0, -10 + 25 * sin(_t * 7.0)); ex["arm_lower_r"] = Vector3(-30, 0, 0)
		"ring":
			var k := sin(_t * 5.0); ex["arm_upper_r"] = Vector3(-140 + 30 * k, 0, 0); ex["arm_upper_l"] = Vector3(-140 + 30 * k, 0, 0)
	if greyed > 0.5:   # moving wrongly: the head lolls, then jerks; an arm hangs; now and then the whole body twitches
		_twitch -= delta
		if _twitch <= 0.0: _twitch = randf_range(0.25, 1.1)
		var j := 1.0 if _twitch < 0.12 else 0.0
		ex["head"] = Vector3(10 + 25 * j, 18 * sin(_t * 0.7) + 40 * j * signf(sin(_t * 13.0)), 28 + 10 * sin(_t * 1.3))
		ex["arm_upper_l"] = Vector3(-15 + 70 * j, 0, 4); ex["arm_lower_l"] = Vector3(-5, 0, 0)
		ex["arm_upper_r"] = Vector3(-50 - 40 * absf(sin(_t * 0.9)), 0, -10); ex["arm_lower_r"] = Vector3(-60, 0, 0)
		ex["torso"] = Vector3(15 + 10 * j, 0, 8 * sin(_t * 0.6))
	walk.extra = ex

## the Fog's mark: grey veins spreading over the body and the colour draining out (an overlay on every voxel mesh)
func set_greyed(a: float) -> void:
	greyed = a
	var sh := Shader.new(); sh.code = """
shader_type spatial;
render_mode blend_mix, depth_draw_never;
uniform float amount = 0.0;
varying vec3 wp;
float h(vec3 p) { return fract(sin(dot(floor(p), vec3(12.9, 78.2, 37.7))) * 43758.5); }
float n(vec3 p) { vec3 i = floor(p); vec3 f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(h(i), h(i + vec3(1,0,0)), f.x), mix(h(i + vec3(0,1,0)), h(i + vec3(1,1,0)), f.x), f.y),
		mix(mix(h(i + vec3(0,0,1)), h(i + vec3(1,0,1)), f.x), mix(h(i + vec3(0,1,1)), h(i + vec3(1,1,1)), f.x), f.y), f.z); }
void vertex() { wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	float v = abs(n(wp * 9.0) - 0.5) + abs(n(wp * 21.0) - 0.5) * 0.5;
	float vein = 1.0 - smoothstep(0.03, 0.09, v);
	ALBEDO = mix(vec3(0.34, 0.35, 0.37), vec3(0.12, 0.12, 0.14), vein);
	ALPHA = clamp(amount * (0.55 + vein * 0.45), 0.0, 1.0);
	EMISSION = vec3(0.35, 0.38, 0.42) * vein * amount * 0.4;
	ROUGHNESS = 1.0;
}
"""
	var m := ShaderMaterial.new(); m.shader = sh; m.set_shader_parameter("amount", a)
	for mi in model.find_children("*", "MeshInstance3D", true, false): (mi as MeshInstance3D).material_overlay = m
