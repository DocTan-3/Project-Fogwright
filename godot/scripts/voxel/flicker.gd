## a fire's light: its energy and range waver as a flame does
extends OmniLight3D
var base := 0.0
var t := 0.0
func _ready() -> void: base = light_energy; t = randf() * 10.0
func _process(d: float) -> void:
	t += d
	light_energy = base * (0.85 + 0.1 * sin(t * 11.0) + 0.06 * sin(t * 23.0 + 1.3) + 0.04 * sin(t * 37.0))
