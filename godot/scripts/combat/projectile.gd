## A thrown stone or a shot: flies straight at where its target stood when it was let go, so stepping aside works; it hits
## when it reaches the target, and the rules decide (dodge, block; only "deflect" lets a parry turn it).
class_name FogProjectile
extends MeshInstance3D

var _v := Vector3.ZERO
var _life := 0.0
var _atk: Dictionary
var _src: Node
var _hit_player := true
var _target_group := "player"

func launch(from: Vector3, to: Vector3, atk: Dictionary, src: Node, at_group := "player") -> void:
	var s := SphereMesh.new(); s.radius = 0.14; s.height = 0.28; mesh = s
	var m := StandardMaterial3D.new(); m.albedo_color = CombatRules.KINDS.projectile.color if at_group == "player" else Color(1, 0.85, 0.5)
	m.emission_enabled = true; m.emission = m.albedo_color; m.emission_energy_multiplier = 0.8; material_override = m
	global_position = from; _v = (to - from).normalized() * float(atk.get("speed", 13.0)); _atk = atk; _src = src; _target_group = at_group
	_life = (to - from).length() / _v.length() + 0.6

func _process(delta: float) -> void:
	var a := global_position; var b := a + _v * delta
	global_position = b; _life -= delta
	for n in get_tree().get_nodes_in_group(_target_group):
		var t := n as Node3D
		if t == null: continue
		# the whole stretch flown this frame is checked, from where it was let go: point-blank shots and fast ones still hit
		var c := t.global_position + Vector3(0, 1.0, 0)
		var seg := b - a; var k := clampf((c - a).dot(seg) / maxf(seg.length_squared(), 1e-6), 0.0, 1.0)
		if (a + seg * k).distance_to(c) < 0.75:
			var f: Fighter = t.get_node_or_null("Fighter")
			if f: f.receive({"dmg": _atk.dmg, "kind": _atk.get("kind", "projectile"), "source": _src})
			queue_free(); return
	if _life <= 0.0: queue_free()
