## The equipment screen (I): what the player wears and holds on the left, by slot, and what they carry on the right.
## Click (or drag) an item from the bag onto the body to equip it in its slot; click a worn item to put it back in the
## bag. While it is open the cursor is free and the player stands still. The prologue teaches it with the first weapon.
class_name EquipmentScreen
extends CanvasLayer

signal equipped(item_id: String)
signal closed

const SLOTS := [["main_hand", "Main hand"], ["off_hand", "Off hand"], ["head", "Head"], ["chest", "Body"], ["legs", "Legs"], ["feet", "Feet"], ["waist", "Belt"], ["back", "Back"]]
var items := {}          # id -> {"name", "slot", "col", "desc"}
var bag: Array = []      # ids carried
var worn := {}           # slot -> id
var panel: PanelContainer
var slot_buttons := {}
var bag_box: GridContainer
var info: Label
var is_open := false

func _ready() -> void:
	layer = 8
	panel = PanelContainer.new(); panel.set_anchors_preset(Control.PRESET_CENTER); panel.position = Vector2(-430, -260); panel.size = Vector2(860, 520)
	var sb := StyleBoxFlat.new(); sb.bg_color = Color(0.08, 0.075, 0.07, 0.92); sb.border_color = Color(0.5, 0.42, 0.28); sb.set_border_width_all(2); sb.set_corner_radius_all(6)
	sb.content_margin_left = 22; sb.content_margin_right = 22; sb.content_margin_top = 16; sb.content_margin_bottom = 16
	panel.add_theme_stylebox_override("panel", sb); add_child(panel)
	var vb := VBoxContainer.new(); vb.add_theme_constant_override("separation", 12); panel.add_child(vb)
	var head := Label.new(); head.text = "Equipment"; head.add_theme_font_size_override("font_size", 28); head.add_theme_color_override("font_color", PrologueHUD.GOLD); vb.add_child(head)
	var hb := HBoxContainer.new(); hb.add_theme_constant_override("separation", 28); vb.add_child(hb)
	var left := VBoxContainer.new(); left.custom_minimum_size = Vector2(330, 0); hb.add_child(left)
	var lt := Label.new(); lt.text = "Worn and held"; lt.add_theme_color_override("font_color", Color(0.8, 0.76, 0.66)); left.add_child(lt)
	for s in SLOTS:
		var b := Button.new(); b.custom_minimum_size = Vector2(330, 40); b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.pressed.connect(_unequip.bind(s[0])); left.add_child(b); slot_buttons[s[0]] = b
		b.set_drag_forwarding(Callable(), _can_drop.bind(s[0]), _drop.bind(s[0]))
	var right := VBoxContainer.new(); right.custom_minimum_size = Vector2(440, 0); hb.add_child(right)
	var rt := Label.new(); rt.text = "Carried"; rt.add_theme_color_override("font_color", Color(0.8, 0.76, 0.66)); right.add_child(rt)
	bag_box = GridContainer.new(); bag_box.columns = 4; bag_box.add_theme_constant_override("h_separation", 8); bag_box.add_theme_constant_override("v_separation", 8); right.add_child(bag_box)
	info = Label.new(); info.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; info.custom_minimum_size = Vector2(440, 90); info.add_theme_color_override("font_color", PrologueHUD.INK); right.add_child(info)
	var foot := Label.new(); foot.text = "Click an item to equip it, or drag it onto its slot.   I or Esc closes."; foot.add_theme_color_override("font_color", Color(0.7, 0.66, 0.58)); vb.add_child(foot)
	panel.visible = false
	_refresh()

func add_item(id: String, name_: String, slot: String, col: Color, desc := "") -> void:
	items[id] = {"name": name_, "slot": slot, "col": col, "desc": desc}

func give(id: String) -> void:
	if not id in bag: bag.append(id)
	_refresh()

func take(id: String) -> void:
	bag.erase(id); _refresh()

func has(id: String) -> bool: return id in bag or id in worn.values()

func open() -> void:
	is_open = true; panel.visible = true; Input.mouse_mode = Input.MOUSE_MODE_VISIBLE; _refresh()

func close() -> void:
	is_open = false; panel.visible = false
	if DisplayServer.get_name() != "headless": Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	closed.emit()

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("inventory"):
		if is_open: close()
		else: open()
		get_viewport().set_input_as_handled()
	elif is_open and event is InputEventKey and event.pressed and event.physical_keycode == KEY_ESCAPE:
		close(); get_viewport().set_input_as_handled()

func equip(id: String) -> void:
	if not items.has(id): return
	var slot: String = items[id].slot
	if slot == "": info.text = "%s can't be worn or held." % items[id].name; return
	if worn.has(slot): bag.append(worn[slot])
	worn[slot] = id; bag.erase(id); _refresh(); equipped.emit(id)

func _unequip(slot: String) -> void:
	if not worn.has(slot): return
	bag.append(worn[slot]); worn.erase(slot); _refresh(); equipped.emit("")

func _can_drop(_pos: Vector2, data: Variant, slot: String) -> bool:
	return data is String and items.has(data) and items[data].slot == slot
func _drop(_pos: Vector2, data: Variant, _slot: String) -> void: equip(data)

func _refresh() -> void:
	if slot_buttons.is_empty(): return
	for s in SLOTS:
		var b: Button = slot_buttons[s[0]]
		b.text = "  %-10s   %s" % [s[1], items[worn[s[0]]].name if worn.has(s[0]) else "-"]
	for c in bag_box.get_children(): c.queue_free()
	for id in bag:
		var it: Dictionary = items[id]
		var b := Button.new(); b.custom_minimum_size = Vector2(100, 80); b.text = it.name; b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var st := StyleBoxFlat.new(); st.bg_color = Color(it.col, 0.55); st.border_color = it.col.lightened(0.3); st.set_border_width_all(2); st.set_corner_radius_all(4)
		b.add_theme_stylebox_override("normal", st)
		var sh := st.duplicate(); sh.bg_color = Color(it.col, 0.8); b.add_theme_stylebox_override("hover", sh)
		b.pressed.connect(equip.bind(id))
		b.mouse_entered.connect(func(): info.text = "%s\n%s" % [it.name, it.desc])
		b.set_drag_forwarding(func(_p): return id, Callable(), Callable())
		bag_box.add_child(b)
