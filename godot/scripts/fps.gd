## A tiny frames-per-second counter in the bottom-right corner, updated twice a second.
extends CanvasLayer

var _label: Label
var _t := 0.0

func _ready() -> void:
	layer = 100
	_label = Label.new()
	_label.anchor_left = 1.0; _label.anchor_top = 1.0; _label.anchor_right = 1.0; _label.anchor_bottom = 1.0
	_label.offset_left = -90; _label.offset_top = -26; _label.offset_right = -8; _label.offset_bottom = -6
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_label.add_theme_font_size_override("font_size", 13)
	_label.add_theme_color_override("font_color", Color(1, 1, 1, 0.75))
	_label.add_theme_color_override("font_shadow_color", Color(0, 0, 0, 0.6))
	_label.add_theme_constant_override("shadow_offset_x", 1); _label.add_theme_constant_override("shadow_offset_y", 1)
	add_child(_label)

func _process(delta: float) -> void:
	_t += delta
	if _t >= 0.5:
		_t = 0.0
		_label.text = "%d fps" % Engine.get_frames_per_second()
