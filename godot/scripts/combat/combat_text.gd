## Floating combat text in the world: damage numbers and outcomes (PARRIED, BLOCKED ...), rising and fading.
class_name CombatText
extends Label3D

var _t := 0.0

static func spawn(parent: Node, at: Vector3, text: String, color: Color, big := false) -> void:
	var l := CombatText.new(); l.text = text; l.modulate = color; l.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	l.font_size = 64 if big else 44; l.pixel_size = 0.006; l.outline_size = 10; l.outline_modulate = Color(0, 0, 0, 0.8)
	l.no_depth_test = true; l.render_priority = 5
	parent.add_child(l); l.global_position = at + Vector3(randf_range(-0.25, 0.25), 0, randf_range(-0.25, 0.25))

func _process(delta: float) -> void:
	_t += delta; position.y += delta * 0.9
	modulate.a = clampf(1.6 - _t, 0.0, 1.0)
	if _t > 1.6: queue_free()
