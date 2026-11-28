## Fogwright's controls, defined in code so they are easy to read and change: WASD or the arrows to move, Space to jump,
## Shift to sprint, Ctrl to toggle walking, F2 to switch real-time shadows; the mouse turns the camera (Esc frees the cursor), the wheel zooms.
## Combat: left click attacks, right click (or F) held blocks - a block raised just before a hit parries - Alt dodges, Tab locks a target,
## 1-6 and Q E R T Z V cast the twelve skills.
extends Node

const ACTIONS := {
	"move_forward": [KEY_W, KEY_UP],
	"move_back": [KEY_S, KEY_DOWN],
	"move_left": [KEY_A, KEY_LEFT],
	"move_right": [KEY_D, KEY_RIGHT],
	"jump": [KEY_SPACE],
	"sprint": [KEY_SHIFT],
	"walk_toggle": [KEY_CTRL],
	"turn_left": [],          # the mouse turns the camera now; Q and E cast skills
	"turn_right": [],
	"shadows_toggle": [KEY_F2],
	"camera_mode": [KEY_F3],     # the high (Albion-style) camera or the close third-person one
	# combat (docs/design.md, Combat), PC: the mouse attacks (left) and blocks (right, held; a well-timed block parries);
	# both skill pages show at once on PC, on 1-6 and Q E R T Z V
	"target_nearest": [KEY_TAB],
	"attack": [MOUSE_BUTTON_LEFT],
	"block": [MOUSE_BUTTON_RIGHT, KEY_F],
	"skill_1": [KEY_1], "skill_2": [KEY_2], "skill_3": [KEY_3], "skill_4": [KEY_4], "skill_5": [KEY_5], "skill_6": [KEY_6],
	"skill_7": [KEY_Q], "skill_8": [KEY_E], "skill_9": [KEY_R], "skill_10": [KEY_T], "skill_11": [KEY_Z], "skill_12": [KEY_V],
	"dodge": [KEY_ALT],
	"weapon_next": [KEY_G],       # testing
	"spawn_enemies": [KEY_F9],    # testing
}

func _enter_tree() -> void:
	for action in ACTIONS:
		if InputMap.has_action(action):
			continue
		InputMap.add_action(action)
		for key in ACTIONS[action]:
			if action in ["attack"] or (action == "block" and key == MOUSE_BUTTON_RIGHT):
				var mb := InputEventMouseButton.new(); mb.button_index = key; InputMap.action_add_event(action, mb)
				continue
			var ev := InputEventKey.new()
			ev.physical_keycode = key
			InputMap.action_add_event(action, ev)
