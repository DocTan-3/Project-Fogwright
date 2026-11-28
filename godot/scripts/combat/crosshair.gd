## The crosshair: four ticks round the centre of the screen, their gap the spread shots can land in (PlayerCombat.spread,
## in degrees, turned into pixels by the camera's field of view). Wide from the hip, narrow when aimed, blooming with each
## shot. Melee weapons show a small dot only.
class_name Crosshair
extends Control

var pc: PlayerCombat

func _ready() -> void:
	set_anchors_preset(Control.PRESET_FULL_RECT); mouse_filter = Control.MOUSE_FILTER_IGNORE

func _process(_d: float) -> void:
	queue_redraw()

func _draw() -> void:
	if pc == null or pc.W.is_empty(): return
	var vs := get_viewport_rect().size; var c := vs / 2.0
	var cam := get_viewport().get_camera_3d()
	var col := Color(1, 1, 1, 0.9); var sh := Color(0, 0, 0, 0.6)
	if pc.W.melee or cam == null:
		draw_circle(c, 3.5, sh); draw_circle(c, 2.2, col); return
	var px := (vs.y / 2.0) / tan(deg_to_rad(cam.fov) / 2.0) * tan(deg_to_rad(pc.spread))
	var gap := maxf(4.0, px); var len := 9.0
	if pc.aiming: col = Color(1, 0.95, 0.75, 0.95)
	for d in [Vector2(1, 0), Vector2(-1, 0), Vector2(0, 1), Vector2(0, -1)]:
		draw_line(c + d * gap, c + d * (gap + len), sh, 4.0); draw_line(c + d * gap, c + d * (gap + len), col, 2.0)
	draw_circle(c, 1.6, col)
	if pc.W.family == "bow" and pc.drawing >= 0.0:   # the draw, as an arc filling round the crosshair
		var k := clampf(pc.drawing / float(pc.W.draw), 0.0, 1.0)
		draw_arc(c, gap + len + 6.0, -PI / 2.0, -PI / 2.0 + TAU * k, 32, Color(1, 0.85, 0.4, 0.9), 3.0)
