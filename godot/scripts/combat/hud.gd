## The combat HUD: health, energy and stamina; the target; the six skills of the page in use (and which page); the
## weapon's quirk (loads, momentum, draw, Fog shards); the perks switched on for testing; the keys.
class_name CombatHud
extends CanvasLayer

var pc: PlayerCombat
var _bars := {}
var _target: Label
var _tbar: ProgressBar
var _slots := []
var _quirk: Label
var _perks: Label

func _bar(parent: Control, color: Color, w := 260.0) -> ProgressBar:
	var b := ProgressBar.new(); b.custom_minimum_size = Vector2(w, 16); b.show_percentage = false
	var fg := StyleBoxFlat.new(); fg.bg_color = color; fg.corner_radius_top_left = 3; fg.corner_radius_bottom_right = 3
	var bg := StyleBoxFlat.new(); bg.bg_color = Color(0, 0, 0, 0.55)
	b.add_theme_stylebox_override("fill", fg); b.add_theme_stylebox_override("background", bg); parent.add_child(b)
	return b

func _label(parent: Control, size := 16) -> Label:
	var l := Label.new(); l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9)); l.add_theme_constant_override("outline_size", 5); parent.add_child(l)
	return l

func _ready() -> void:
	var root := Control.new(); root.set_anchors_preset(Control.PRESET_FULL_RECT); root.mouse_filter = Control.MOUSE_FILTER_IGNORE; add_child(root)
	var bars := VBoxContainer.new(); bars.position = Vector2(24, 24); root.add_child(bars)
	for k in [["hp", Color(0.78, 0.2, 0.18)], ["energy", Color(0.25, 0.5, 0.95)], ["stamina", Color(0.95, 0.75, 0.2)]]:
		_bars[k[0]] = _bar(bars, k[1])
	_quirk = _label(bars, 16); _perks = _label(bars, 14); _perks.modulate = Color(0.75, 1, 0.8)
	var tbox := VBoxContainer.new(); tbox.set_anchors_preset(Control.PRESET_CENTER_TOP); tbox.position = Vector2(-160, 20); root.add_child(tbox)
	_target = _label(tbox, 20); _tbar = _bar(tbox, Color(0.75, 0.15, 0.12), 320.0)
	var ch := Crosshair.new(); ch.pc = pc; root.add_child(ch)
	# on PC both pages show at once: two rows of six (1-6, then Q E R T Z V)
	var rows := VBoxContainer.new(); rows.set_anchors_preset(Control.PRESET_CENTER_BOTTOM); rows.position = Vector2(-300, -150); rows.add_theme_constant_override("separation", 6); root.add_child(rows)
	for r in 2:
		var bar := HBoxContainer.new(); bar.add_theme_constant_override("separation", 8); rows.add_child(bar)
		for i in 6:
			var p := PanelContainer.new(); p.custom_minimum_size = Vector2(92, 56)
			var sb := StyleBoxFlat.new(); sb.bg_color = Color(0.08, 0.08, 0.1, 0.72); sb.border_color = Color(0.7, 0.6, 0.4); sb.set_border_width_all(2); sb.set_corner_radius_all(6)
			p.add_theme_stylebox_override("panel", sb); bar.add_child(p)
			var l := _label(p, 13); l.autowrap_mode = TextServer.AUTOWRAP_WORD; l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER; l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
			_slots.append(l)
	var keys := _label(root, 13); keys.set_anchors_preset(Control.PRESET_BOTTOM_LEFT); keys.position = Vector2(24, -64); keys.modulate = Color(1, 1, 1, 0.75)
	keys.text = "left click attack  right click block (just before a hit: parry) - guns and bows: aim  Alt dodge  Tab lock target  1-6, Q E R T Z V skills  Esc frees the mouse\ntesting: G weapon  F9 enemies  F5 iron guard  F6 slip  F7 deflect  F8 dash  F10 dash reload  F11 steady guard"

func _process(_d: float) -> void:
	if pc == null or pc.fighter == null: return
	var f := pc.fighter
	_bars.hp.max_value = f.max_hp; _bars.hp.value = f.hp
	_bars.energy.max_value = CombatRules.ENERGY_MAX; _bars.energy.value = f.energy
	_bars.stamina.max_value = CombatRules.STAMINA_MAX; _bars.stamina.value = f.stamina
	var W := pc.W
	var q: String = W.name
	match W.family:
		"gun": q += "   loads %d/%d%s" % [pc.ammo, W.ammo, "  reloading" if pc.reloading > 0.0 else ""]
		"heavy": q += "   momentum +%d%%" % roundi(pc.momentum * 100.0)
		"bow": q += "   draw %d%%" % roundi(clampf(pc.drawing / float(W.draw), 0.0, 1.0) * 100.0) if pc.drawing >= 0.0 else "   draw -"
		"focus": q += "   Fog shards %d   Fog pressure %d" % [pc.shards, pc.fog_pressure]
	q += "   (block, parry)" if W.melee else ("   (block, no parry)" if W.get("block", true) else "   (no block: right click aims)")
	_quirk.text = q
	_perks.text = "perks: " + (", ".join(f.perks.keys()) if not f.perks.is_empty() else "none") + ("" if not f.dead else "   - you have fallen")
	if pc._target_ok():
		var tf: Fighter = pc.target.get_node("Fighter")
		_target.text = pc.target.display_name() + ("  (attacking)" if pc.engaged else ""); _tbar.max_value = tf.max_hp; _tbar.value = tf.hp; _target.visible = true; _tbar.visible = true
	else:
		_target.visible = false; _tbar.visible = false
	const KEYS := ["1", "2", "3", "4", "5", "6", "Q", "E", "R", "T", "Z", "V"]
	for i in 12:
		var id: String = pc.pages[i / 6][i % 6]
		if id == "": _slots[i].text = "%s\n-" % KEYS[i]; _slots[i].modulate = Color(1, 1, 1, 0.4); continue
		var M: Dictionary = Weapons.MOVES[id]; var cd: float = pc.cds.get(id, 0.0)
		_slots[i].text = "%s  %s\n%s" % [KEYS[i], M.name, ("%.1fs" % cd) if cd > 0.0 else "%d energy" % roundi(M.energy)]
		_slots[i].modulate = Color(1, 1, 1, 0.55 if cd > 0.0 or f.energy < M.energy else 1.0)
