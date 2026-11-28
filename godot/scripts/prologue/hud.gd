## The prologue's screen (docs/design.md: the top compass, no tutorial text walls): built in code, so it is easy to read.
##   - the compass strip across the top: N E S W and ticks turning with the camera, the tracked objective's mark, and
##     Merrith's thread as a gold mark (lore.md: it guides the chosen);
##   - the objective under it, a hint at the left for a new control, the interaction prompt under the centre, and
##     subtitles at the bottom (who speaks, what they say);
##   - health and stamina, shown once there is danger; a red edge when hit; a dot where the aim is once armed;
##   - a fade and a title card for the opening and the end.
class_name PrologueHUD
extends CanvasLayer

var camera: Camera3D
var markers := {}             # id -> {"pos": Vector3, "col": Color, "label": String}
var compass: Control
var objective: Label
var prompt: Label
var hint: Label
var sub_panel: PanelContainer
var sub_name: Label
var sub_text: Label
var bars: Control
var hp_bar: ProgressBar
var st_bar: ProgressBar
var dot: Control
var fade: ColorRect
var title: Label
var subtitle_card: Label
var hurt: ColorRect
var glow: ColorRect
## over people and beasts in the world: a name (only those that matter), a small quest mark when they have something
## for you, a health bar on what you fight; each hidden when a wall or the land stands between it and the camera
var tags := {}                # id -> {"node": Node3D, "name": String, "up": float, "quest": bool, "hp": float (-1 none), "foe": bool}
var tag_layer: Control
var _tag_seen := {}           # id -> 0..1, eased, so a tag fades as it goes behind a wall
var _hurt := 0.0
var _glow := 0.0

const GOLD := Color(0.96, 0.78, 0.36)
const INK := Color(0.93, 0.9, 0.82)

func _ready() -> void:
	layer = 5
	var root := Control.new(); root.set_anchors_preset(Control.PRESET_FULL_RECT); root.mouse_filter = Control.MOUSE_FILTER_IGNORE; add_child(root)
	compass = Control.new(); compass.name = "Compass"; compass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	compass.set_anchors_preset(Control.PRESET_CENTER_TOP); compass.custom_minimum_size = Vector2(640, 40)
	compass.position = Vector2(-320, 14); compass.size = Vector2(640, 40); compass.draw.connect(_draw_compass); root.add_child(compass)
	objective = _label(root, 20, Control.PRESET_CENTER_TOP, Vector2(-400, 60), Vector2(800, 30), HORIZONTAL_ALIGNMENT_CENTER)
	prompt = _label(root, 22, Control.PRESET_CENTER, Vector2(-300, 70), Vector2(600, 34), HORIZONTAL_ALIGNMENT_CENTER)
	hint = _label(root, 19, Control.PRESET_CENTER_LEFT, Vector2(40, -60), Vector2(420, 120), HORIZONTAL_ALIGNMENT_LEFT)
	hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	sub_panel = PanelContainer.new(); sub_panel.set_anchors_preset(Control.PRESET_CENTER_BOTTOM)
	sub_panel.position = Vector2(-430, -190); sub_panel.size = Vector2(860, 90); sub_panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new(); sb.bg_color = Color(0.05, 0.05, 0.06, 0.55); sb.set_corner_radius_all(6); sb.content_margin_left = 18; sb.content_margin_right = 18; sb.content_margin_top = 10; sb.content_margin_bottom = 10
	sub_panel.add_theme_stylebox_override("panel", sb); root.add_child(sub_panel)
	var vb := VBoxContainer.new(); sub_panel.add_child(vb)
	sub_name = Label.new(); sub_name.add_theme_font_size_override("font_size", 18); sub_name.add_theme_color_override("font_color", GOLD); vb.add_child(sub_name)
	sub_text = Label.new(); sub_text.add_theme_font_size_override("font_size", 21); sub_text.add_theme_color_override("font_color", INK)
	sub_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; sub_text.custom_minimum_size = Vector2(820, 0); vb.add_child(sub_text)
	sub_panel.visible = false
	tag_layer = Control.new(); tag_layer.set_anchors_preset(Control.PRESET_FULL_RECT); tag_layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tag_layer.draw.connect(_draw_tags); root.add_child(tag_layer)
	bars = Control.new(); bars.set_anchors_preset(Control.PRESET_CENTER_BOTTOM); bars.position = Vector2(-180, -70); bars.size = Vector2(360, 40)
	bars.mouse_filter = Control.MOUSE_FILTER_IGNORE; root.add_child(bars)
	hp_bar = _bar(bars, Vector2(0, 0), Vector2(360, 14), Color(0.62, 0.16, 0.14)); st_bar = _bar(bars, Vector2(40, 20), Vector2(280, 8), Color(0.72, 0.62, 0.3))
	bars.visible = false
	dot = Control.new(); dot.set_anchors_preset(Control.PRESET_CENTER); dot.size = Vector2(8, 8); dot.position = Vector2(-4, -4); dot.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dot.draw.connect(func(): dot.draw_circle(Vector2(4, 4), 2.5, Color(1, 1, 1, 0.8)); dot.draw_arc(Vector2(4, 4), 4.5, 0, TAU, 16, Color(0, 0, 0, 0.5), 1.0))
	dot.visible = false; root.add_child(dot)
	hurt = ColorRect.new(); hurt.set_anchors_preset(Control.PRESET_FULL_RECT); hurt.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var hs := Shader.new(); hs.code = "shader_type canvas_item; uniform float a = 0.0; uniform vec3 col = vec3(0.6, 0.05, 0.05); void fragment() { float d = distance(UV, vec2(0.5)); COLOR = vec4(col, smoothstep(0.35, 0.75, d) * a); }"
	var hm := ShaderMaterial.new(); hm.shader = hs; hurt.material = hm; root.add_child(hurt)
	glow = ColorRect.new(); glow.set_anchors_preset(Control.PRESET_FULL_RECT); glow.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var gm := ShaderMaterial.new(); gm.shader = hs; gm.set_shader_parameter("col", Vector3(1.0, 0.85, 0.5)); glow.material = gm; root.add_child(glow)
	fade = ColorRect.new(); fade.set_anchors_preset(Control.PRESET_FULL_RECT); fade.color = Color(0, 0, 0, 1); fade.mouse_filter = Control.MOUSE_FILTER_IGNORE; root.add_child(fade)
	title = _label(root, 54, Control.PRESET_CENTER, Vector2(-600, -80), Vector2(1200, 70), HORIZONTAL_ALIGNMENT_CENTER)
	title.add_theme_color_override("font_color", INK)
	subtitle_card = _label(root, 22, Control.PRESET_CENTER, Vector2(-600, 0), Vector2(1200, 120), HORIZONTAL_ALIGNMENT_CENTER)
	subtitle_card.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

func _label(parent: Control, size: int, preset: int, pos: Vector2, sz: Vector2, align: int) -> Label:
	var l := Label.new(); l.set_anchors_preset(preset); l.position = pos; l.size = sz; l.horizontal_alignment = align
	l.add_theme_font_size_override("font_size", size); l.add_theme_color_override("font_color", INK)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.85)); l.add_theme_constant_override("outline_size", 6)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE; parent.add_child(l); return l

func _bar(parent: Control, pos: Vector2, sz: Vector2, col: Color) -> ProgressBar:
	var b := ProgressBar.new(); b.position = pos; b.size = sz; b.show_percentage = false; b.max_value = 100; b.value = 100
	var bg := StyleBoxFlat.new(); bg.bg_color = Color(0, 0, 0, 0.55); bg.set_corner_radius_all(3)
	var fg := StyleBoxFlat.new(); fg.bg_color = col; fg.set_corner_radius_all(3)
	b.add_theme_stylebox_override("background", bg); b.add_theme_stylebox_override("fill", fg); b.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(b); return b

func _process(delta: float) -> void:
	compass.queue_redraw(); tag_layer.queue_redraw()
	_hurt = maxf(0.0, _hurt - delta * 1.5); (hurt.material as ShaderMaterial).set_shader_parameter("a", _hurt)
	_glow = maxf(0.0, _glow - delta * 0.35); (glow.material as ShaderMaterial).set_shader_parameter("a", _glow)

## a lesson while the world is stopped: a title, what it is, and the key, in the middle of the screen
var _lesson: PanelContainer
func lesson(title_: String, text: String, key: String) -> void:
	if _lesson == null:
		_lesson = PanelContainer.new(); _lesson.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_lesson.set_anchors_preset(Control.PRESET_CENTER); _lesson.position = Vector2(-300, 90); _lesson.size = Vector2(600, 10)
		var sb := StyleBoxFlat.new(); sb.bg_color = Color(0.05, 0.05, 0.06, 0.72); sb.set_corner_radius_all(6); sb.border_color = GOLD; sb.set_border_width_all(1)
		for m in ["left", "right", "top", "bottom"]: sb.set("content_margin_" + m, 16)
		_lesson.add_theme_stylebox_override("panel", sb); tag_layer.get_parent().add_child(_lesson)
		var vb := VBoxContainer.new(); _lesson.add_child(vb)
		for k in 3:
			var l := Label.new(); l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			l.custom_minimum_size = Vector2(560, 0); l.add_theme_font_size_override("font_size", [26, 19, 22][k]); l.add_theme_color_override("font_color", [GOLD, INK, Color.WHITE][k])
			vb.add_child(l)
	var ls := _lesson.get_child(0).get_children()
	(ls[0] as Label).text = title_; (ls[1] as Label).text = text; (ls[2] as Label).text = "[ " + key + " ]" if key != "" else ""
	_lesson.visible = title_ != ""; _lesson.reset_size()
	var vp := get_viewport().get_visible_rect().size
	_lesson.set_anchors_preset(Control.PRESET_TOP_LEFT); _lesson.position = Vector2((vp.x - _lesson.size.x) * 0.5, vp.y * 0.5 + 70.0)

func set_tag(id: String, node: Node3D, name_: String, up := 2.05, foe := false) -> void:
	tags[id] = {"node": node, "name": name_, "up": up, "quest": tags.get(id, {}).get("quest", false), "hp": tags.get(id, {}).get("hp", -1.0), "foe": foe}
func clear_tag(id: String) -> void: tags.erase(id); _tag_seen.erase(id)
func tag_quest(id: String, on: bool) -> void: if tags.has(id): tags[id].quest = on
func tag_hp(id: String, frac: float) -> void: if tags.has(id): tags[id].hp = frac

func _physics_process(delta: float) -> void:   # which tags the camera can see (rays need the physics frame)
	if camera == null: return
	var space := camera.get_world_3d().direct_space_state; var eye := camera.global_position
	for id in tags.keys():
		var t: Dictionary = tags[id]; var n: Node3D = t.node
		if not is_instance_valid(n) or not n.is_visible_in_tree(): _tag_seen[id] = 0.0; continue
		var at: Vector3 = n.global_position + Vector3(0, t.up, 0)
		var far := eye.distance_to(at); var want := 1.0
		if far > (40.0 if t.foe or t.quest else 22.0) or camera.is_position_behind(at): want = 0.0
		else:
			var ex: Array[RID] = []
			if n is CollisionObject3D: ex.append((n as CollisionObject3D).get_rid())
			var hit := space.intersect_ray(PhysicsRayQueryParameters3D.create(eye, at, 1, ex))
			if not hit.is_empty() and (hit.collider as Node) != n and not ((hit.collider as Node) is CharacterBody3D): want = 0.0
		_tag_seen[id] = move_toward(_tag_seen.get(id, 0.0), want, delta * 6.0)

func _draw_tags() -> void:
	if camera == null: return
	var font := ThemeDB.fallback_font
	for id in tags:
		var a: float = _tag_seen.get(id, 0.0)
		if a <= 0.01: continue
		var t: Dictionary = tags[id]; var n: Node3D = t.node
		if not is_instance_valid(n): continue
		var at: Vector3 = n.global_position + Vector3(0, t.up, 0)
		var p := camera.unproject_position(at); var far := camera.global_position.distance_to(at)
		var k := clampf(1.2 - far / 40.0, 0.55, 1.0)   # smaller further off
		var y := p.y
		if t.hp >= 0.0:   # a health bar
			var w := 70.0 * k; var r := Rect2(p.x - w / 2, y - 6, w, 6.0 * k)
			tag_layer.draw_rect(r.grow(1.5), Color(0, 0, 0, 0.6 * a)); tag_layer.draw_rect(Rect2(r.position, Vector2(w * clampf(t.hp, 0, 1), r.size.y)), Color(0.75, 0.16, 0.12, a))
			y -= 10.0
		if t.name != "":
			var fs := int(15 * k); var sz := font.get_string_size(t.name, HORIZONTAL_ALIGNMENT_CENTER, -1, fs)
			var col := Color(0.95, 0.55, 0.45, a) if t.foe else Color(INK, a)
			tag_layer.draw_string_outline(font, Vector2(p.x - sz.x / 2, y), t.name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, 4, Color(0, 0, 0, 0.8 * a))
			tag_layer.draw_string(font, Vector2(p.x - sz.x / 2, y), t.name, HORIZONTAL_ALIGNMENT_LEFT, -1, fs, col)
			y -= sz.y + 2
		if t.quest:   # a small gold diamond
			var r2 := 5.0 * k + 1.0; var c := Vector2(p.x, y - r2)
			var pts := PackedVector2Array([c + Vector2(0, -r2), c + Vector2(r2 * 0.75, 0), c + Vector2(0, r2), c + Vector2(-r2 * 0.75, 0)])
			tag_layer.draw_colored_polygon(pts, Color(GOLD, a)); tag_layer.draw_polyline(pts + PackedVector2Array([pts[0]]), Color(0, 0, 0, 0.7 * a), 1.2)

func flash_hurt(a := 0.7) -> void: _hurt = a
func flash_glow(a := 1.4) -> void: _glow = a

func _yaw() -> float:
	if camera == null: return 0.0
	var f := -camera.global_transform.basis.z
	return atan2(f.x, -f.z)   # 0 facing north (-Z), positive turning east

func _draw_compass() -> void:
	var w := compass.size.x; var cx := w / 2.0; var span := deg_to_rad(150.0)   # degrees across the strip
	var bg := StyleBoxFlat.new(); bg.bg_color = Color(0.04, 0.04, 0.05, 0.42); bg.set_corner_radius_all(4)
	compass.draw_style_box(bg, Rect2(0, 6, w, 26))
	var yaw := _yaw()
	var font := ThemeDB.fallback_font
	for k in 24:
		var a := k * TAU / 24.0; var d := wrapf(a - yaw, -PI, PI)
		if absf(d) > span / 2: continue
		var x := cx + d / span * w
		var big := k % 6 == 0
		if big:
			var s: String = ["N", "E", "S", "W"][k / 6]
			compass.draw_string(font, Vector2(x - 7, 27), s, HORIZONTAL_ALIGNMENT_LEFT, -1, 18, INK)
		else: compass.draw_line(Vector2(x, 12 if k % 3 == 0 else 15), Vector2(x, 26 if k % 3 == 0 else 23), Color(INK, 0.6), 1.5)
	if camera == null: return
	var me := camera.global_position
	for id in markers:
		var m: Dictionary = markers[id]
		var v: Vector3 = m.pos - me
		var a := atan2(v.x, -v.z); var d := wrapf(a - yaw, -PI, PI)
		var x := cx + clampf(d / span, -0.5, 0.5) * w
		var col: Color = m.col
		if id == "thread":   # Merrith's thread: a soft gold flame
			compass.draw_circle(Vector2(x, 19), 7, Color(col, 0.35)); compass.draw_circle(Vector2(x, 19), 3.5, col)
		else:
			var pts := PackedVector2Array([Vector2(x, 9), Vector2(x + 7, 19), Vector2(x, 29), Vector2(x - 7, 19)])
			compass.draw_colored_polygon(pts, col); compass.draw_polyline(pts + PackedVector2Array([pts[0]]), Color(0, 0, 0, 0.6), 1.0)
		if m.get("label", "") != "" and absf(d) < 0.12:
			var dist := int(Vector2(v.x, v.z).length())
			compass.draw_string(font, Vector2(x - 40, 52), "%s  %d m" % [m.label, dist], HORIZONTAL_ALIGNMENT_CENTER, 80, 14, Color(INK, 0.9))

func set_marker(id: String, pos: Vector3, col := Color(0.92, 0.9, 0.8), label := "") -> void: markers[id] = {"pos": pos, "col": col, "label": label}
func clear_marker(id: String) -> void: markers.erase(id)

func set_objective(t: String) -> void:
	objective.text = ("◆  " + t) if t != "" else ""
	objective.modulate.a = 0.0; create_tween().tween_property(objective, "modulate:a", 1.0, 0.6)

func show_hint(t: String) -> void:
	hint.text = t; hint.modulate.a = 0.0
	if t != "": create_tween().tween_property(hint, "modulate:a", 1.0, 0.4)

func show_prompt(t: String) -> void: prompt.text = t

func say(who: String, line: String) -> void:
	sub_panel.visible = line != ""; sub_name.text = who; sub_text.text = line

func fade_to(a: float, secs := 1.0) -> Tween:
	var t := create_tween(); t.tween_property(fade, "color:a", a, secs); return t

func card(big: String, small := "", secs := 0.8) -> void:
	for l in [title, subtitle_card]: l.modulate.a = 0.0
	title.text = big; subtitle_card.text = small
	var t := create_tween(); t.set_parallel(); t.tween_property(title, "modulate:a", 1.0, secs); t.tween_property(subtitle_card, "modulate:a", 1.0, secs * 1.5)

func clear_card(secs := 0.8) -> void:
	var t := create_tween(); t.set_parallel(); t.tween_property(title, "modulate:a", 0.0, secs); t.tween_property(subtitle_card, "modulate:a", 0.0, secs)
