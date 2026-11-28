## The first fight (beat 4): a Fog-warped dog (lore.md: the Fog's beasts). Somebody's dog once, a big grey herding dog,
## now thin as a rack, its coat gone to ash-grey mats with the skin showing, ribs and spine standing out, grey veins, a
## jaw that hangs too wide, pale eyes that glow. Voxels (5 cm), in parts that move: body, head and jaw, four legs, tail.
## It circles, then telegraphs a lunge (a crouch, a growl, a mark on the ground the way it will go) and leaps; after a
## lunge it is open for a moment. Close up it snaps. Hits stagger it; a parried lunge throws it down.
class_name FogDog
extends CharacterBody3D

signal died
signal lunging                # it has left the ground: the tutorial stops the world here to teach the guard and the dodge
var target: Node3D            # the player
var fighter: VoxelFighter
const MAX_HP := 170.0         # five clean hits: long enough a fight to learn in
var hp := MAX_HP
var hold := false             # the tutorial keeps it circling, never committing, until the player has struck it
var min_hp := 0.0             # and it cannot die before the lessons are done
var radius := 0.5
var state := "stalk"          # stalk, windup, lunge, recover, snap, stagger, dead
var _t := 0.0
var _phase := 0.0
var _circle := 1.0
var _hit_this := false
var _lunge_dir := Vector3.ZERO
var parts := {}
var telegraph: MeshInstance3D
var _mat_flash := 0.0
const GRAVITY := 14.0

func _ready() -> void:
	add_to_group("fog_enemy")
	var cs := CollisionShape3D.new(); var bs := BoxShape3D.new(); bs.size = Vector3(0.5, 0.7, 1.1); cs.shape = bs; cs.position.y = 0.45; add_child(cs)
	collision_layer = 1; collision_mask = 1
	_build()
	telegraph = MeshInstance3D.new(); var qm := QuadMesh.new(); qm.size = Vector2(1.0, 4.6); qm.orientation = PlaneMesh.FACE_Y; telegraph.mesh = qm
	var sh := Shader.new(); sh.code = """
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;
uniform float fill = 0.0;
void fragment() { float y = 1.0 - UV.y; float edge = smoothstep(0.5, 0.42, abs(UV.x - 0.5));
	float a = edge * (0.25 + 0.55 * step(y, fill)) * (1.0 - y * 0.5);
	ALBEDO = vec3(0.75, 0.2, 0.12); ALPHA = a * 0.8; }
"""
	var m := ShaderMaterial.new(); m.shader = sh; telegraph.material_override = m; telegraph.visible = false
	telegraph.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(telegraph); telegraph.top_level = true

func _part(nm: String, v: VBox, pivot: Vector3, parent: Node3D) -> Node3D:
	var n := Node3D.new(); n.name = nm; n.position = pivot - (parent.get_meta("pivot", Vector3.ZERO) if parent.has_meta("pivot") else Vector3.ZERO)
	n.set_meta("pivot", pivot); parent.add_child(n)
	var mi := MeshInstance3D.new(); mi.mesh = v.mesh(pivot); mi.material_override = Vox.grain_material(0.05); n.add_child(mi)
	parts[nm] = n; return n

func _build() -> void:
	var fur := Color8(118, 116, 112); var fur_d := Color8(86, 84, 82); var skin := Color8(150, 128, 122); var vein := Color8(60, 62, 70)
	var bone := Color8(196, 188, 170); var eye := Color8(230, 236, 230)
	var root := Node3D.new(); root.name = "Body"; add_child(root); root.set_meta("pivot", Vector3.ZERO)
	# the body: a deep chest tapering to a thin waist, the spine ridged, ribs showing through bald patches
	var b := VBox.new(0.05)
	for i in 22:
		var z := 0.55 - i * 0.05; var t := float(i) / 21.0
		var ry := lerpf(0.2, 0.13, t); var rx := lerpf(0.17, 0.1, t); var cy := lerpf(0.62, 0.6, t)
		for x in range(-4, 5):
			for y in range(-5, 6):
				var p := Vector2(x * 0.05 / rx, y * 0.05 / ry)
				if p.length() > 1.0: continue
				var c := fur if (hash(Vector3i(x, y, i)) % 5) else fur_d
				if t < 0.6 and absi(x) >= 3 and y < 2 and i % 3 == 0: c = bone            # ribs
				if t < 0.6 and absi(x) >= 3 and y < 2 and i % 3 == 1: c = skin            # the bald skin between
				if (hash(Vector3i(x, y, i * 7)) % 11) == 0: c = vein
				b.put(Vector3i(x, int(cy / 0.05) + y, int(z / 0.05)), c, 0.05)
		if i % 2 == 0: b.put(Vector3i(0, int((cy + ry) / 0.05) + 1, int(z / 0.05)), bone)   # the spine
	var body := _part("torso", b, Vector3(0, 0.6, 0), root)
	# the head on a thin neck: a long muzzle, ears torn, the eyes pale and glowing
	var h := VBox.new(0.05)
	h.box(Vector3(-0.06, 0.62, 0.5), Vector3(0.06, 0.8, 0.72), fur_d)
	h.box(Vector3(-0.11, 0.72, 0.66), Vector3(0.11, 0.92, 0.88), fur)
	h.box(Vector3(-0.07, 0.72, 0.88), Vector3(0.07, 0.84, 1.08), fur_d)        # the muzzle
	h.box(Vector3(-0.04, 0.8, 1.06), Vector3(0.04, 0.84, 1.1), Color8(30, 28, 28))
	h.box(Vector3(-0.1, 0.92, 0.7), Vector3(-0.05, 1.02, 0.76), fur_d); h.box(Vector3(0.05, 0.92, 0.7), Vector3(0.1, 0.98, 0.76), fur_d)
	for x in [-0.1, 0.06]: h.box(Vector3(x, 0.84, 0.86), Vector3(x + 0.04, 0.88, 0.9), eye, 0.0)
	var head := _part("head", h, Vector3(0, 0.72, 0.52), body)
	var jw := VBox.new(0.05)
	jw.box(Vector3(-0.06, 0.66, 0.8), Vector3(0.06, 0.71, 1.04), fur_d); jw.box(Vector3(-0.05, 0.71, 0.84), Vector3(0.05, 0.74, 1.02), Color8(120, 50, 50))
	for k in 4: jw.put(Vector3i(-1 + (k % 2) * 2 - (k % 2), 14, 17 + k), bone)
	_part("jaw", jw, Vector3(0, 0.7, 0.82), head)
	var eyes := OmniLight3D.new(); eyes.light_color = Color(0.8, 0.9, 1.0); eyes.light_energy = 0.4; eyes.omni_range = 1.2; eyes.position = Vector3(0, 0.15, 0.4); head.add_child(eyes)
	# legs, long and thin, the joints knobbed
	for leg in [["leg_fl", -0.1, 0.42], ["leg_fr", 0.1, 0.42], ["leg_bl", -0.09, -0.42], ["leg_br", 0.09, -0.42]]:
		var l := VBox.new(0.05); var x: float = leg[1]; var z: float = leg[2]
		l.box(Vector3(x - 0.05, 0.3, z - 0.05), Vector3(x + 0.05, 0.62, z + 0.06), fur)
		l.box(Vector3(x - 0.03, 0.05, z - 0.03), Vector3(x + 0.03, 0.32, z + 0.03), fur_d)
		l.box(Vector3(x - 0.04, 0.28, z - 0.04), Vector3(x + 0.04, 0.34, z + 0.04), bone)
		l.box(Vector3(x - 0.04, 0.0, z - 0.02), Vector3(x + 0.04, 0.05, z + 0.08), fur_d)
		_part(leg[0], l, Vector3(x, 0.6, z), body)
	var tl := VBox.new(0.05)
	for k in 7: tl.box(Vector3(-0.025, 0.66 - k * 0.04, -0.52 - k * 0.05), Vector3(0.025, 0.71 - k * 0.04, -0.47 - k * 0.05), fur_d)
	_part("tail", tl, Vector3(0, 0.66, -0.5), body)

func display_name() -> String: return "Fog-warped dog"

func _physics_process(delta: float) -> void:
	_t += delta
	if target == null: return
	var to := target.global_position - global_position; to.y = 0
	var dist := to.length(); var dir := to.normalized() if dist > 0.01 else Vector3.FORWARD
	var want := Vector3.ZERO
	match state:
		"stalk":   # circle at 4-5 m, closing slowly, then commit
			var side := Vector3(-dir.z, 0, dir.x) * _circle
			want = (side * 3.2 + dir * (dist - 4.2) * 1.5).limit_length(4.0)
			_face(dir, delta)
			if _t > 1.8 and dist < 6.5 and not hold: _go("windup")
			elif dist < 1.6: _go("snap")
		"windup":
			_face(dir, delta, 14.0); _lunge_dir = dir
			telegraph.visible = true
			telegraph.global_position = global_position + _lunge_dir * 2.4 + Vector3(0, 0.06, 0)
			telegraph.global_rotation = Vector3(0, atan2(_lunge_dir.x, _lunge_dir.z), 0)
			(telegraph.material_override as ShaderMaterial).set_shader_parameter("fill", clampf(_t / 0.75, 0, 1))
			if _t > 0.75: telegraph.visible = false; _hit_this = false; _go("lunge"); lunging.emit()
		"lunge":
			want = _lunge_dir * 11.0
			if not _hit_this and dist < 1.15:
				_hit_this = true
				var r := fighter.take_hit(16.0, global_position, self) if fighter else "hit"
				if r == "parried": return
			if _t > 0.38: _go("recover")
		"recover":
			if _t > 1.1: _circle = -_circle; _go("stalk")
		"snap":
			_face(dir, delta, 12.0)
			if _t > 0.4 and not _hit_this:
				_hit_this = true
				if dist < 1.5 and fighter: fighter.take_hit(9.0, global_position, self)
			if _t > 0.8: _go("stalk")
		"stagger":
			want = -dir * maxf(0.0, 2.5 - _t * 6.0)
			if _t > 0.55: _go("stalk")
		"dead":
			want = Vector3.ZERO
	velocity.x = lerpf(velocity.x, want.x, 1.0 - exp(-12.0 * delta)); velocity.z = lerpf(velocity.z, want.z, 1.0 - exp(-12.0 * delta))
	velocity.y = 0.0 if is_on_floor() else velocity.y - GRAVITY * delta
	move_and_slide()
	_animate(delta)

func _go(s: String) -> void:
	state = s; _t = 0.0; _hit_this = false
	if s != "windup": telegraph.visible = false

func _face(dir: Vector3, delta: float, rate := 8.0) -> void:
	parts.torso.get_parent().rotation.y = lerp_angle(parts.torso.get_parent().rotation.y, atan2(dir.x, dir.z), 1.0 - exp(-rate * delta))

func _animate(delta: float) -> void:
	var sp := Vector2(velocity.x, velocity.z).length()
	_phase += delta * sp * 3.2
	var s := sin(_phase); var a := clampf(sp / 4.0, 0.0, 1.2)
	var body: Node3D = parts.torso
	parts.leg_fl.rotation.x = s * 0.6 * a; parts.leg_br.rotation.x = s * 0.6 * a
	parts.leg_fr.rotation.x = -s * 0.6 * a; parts.leg_bl.rotation.x = -s * 0.6 * a
	parts.tail.rotation.x = -0.6 + 0.2 * sin(_t * 9.0)
	var jaw := 0.15 + 0.1 * sin(_t * 17.0)
	match state:
		"windup": body.rotation.x = 0.15; body.position.y = 0.6 - 0.12 * clampf(_t * 3.0, 0, 1); jaw = 0.5
		"lunge": body.rotation.x = -0.25; jaw = 0.8; parts.leg_fl.rotation.x = -1.0; parts.leg_fr.rotation.x = -1.0; parts.leg_bl.rotation.x = 0.9; parts.leg_br.rotation.x = 0.9
		"snap": jaw = 0.9 if _t > 0.3 and _t < 0.5 else 0.3; body.rotation.x = 0.1 if _t < 0.35 else -0.1
		"stagger": body.rotation.z = 0.3 * sin(_t * 20.0)
		"dead": body.rotation.z = lerpf(body.rotation.z, 1.5, 1.0 - exp(-6.0 * delta)); body.position.y = lerpf(body.position.y, 0.25, 1.0 - exp(-6.0 * delta)); jaw = 0.6
		_: body.rotation.x = lerpf(body.rotation.x, 0.0, 0.2); body.rotation.z = lerpf(body.rotation.z, 0.0, 0.2); body.position.y = lerpf(body.position.y, 0.6, 0.2)
	parts.jaw.rotation.x = jaw
	parts.head.rotation.x = 0.1 * sin(_t * 3.0) + (0.25 if state == "stalk" else 0.0)
	if _mat_flash > 0.0:
		_mat_flash -= delta

func take_hit(amount: float, from_dir: Vector3) -> void:
	if state == "dead": return
	hp = maxf(hp - amount, min_hp if min_hp > 0.0 else -1.0)
	velocity += from_dir * 3.0
	if hp <= 0.0:
		_go("dead"); remove_from_group("fog_enemy"); died.emit()
		var t := create_tween(); t.tween_interval(2.5); t.tween_property(self, "scale", Vector3(1, 0.05, 1), 1.5); t.tween_callback(queue_free)
		return
	if state != "lunge": _go("stagger")

func stagger(_k := 1.0) -> void:
	if state != "dead": _go("stagger"); _t = -0.4   # a parried lunge: thrown down, open for longer
