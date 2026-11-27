## Fogwright's controls, defined in code so they are easy to read and change: WASD or the arrows to move, Space to jump,
## Shift to sprint, Ctrl to toggle walking, Q and E to turn the camera, F2 to switch real-time shadows; the mouse wheel zooms; the right mouse button (held) turns the camera.
extends Node

const ACTIONS := {
	"move_forward": [KEY_W, KEY_UP],
	"move_back": [KEY_S, KEY_DOWN],
	"move_left": [KEY_A, KEY_LEFT],
	"move_right": [KEY_D, KEY_RIGHT],
	"jump": [KEY_SPACE],
	"sprint": [KEY_SHIFT],
	"walk_toggle": [KEY_CTRL],
	"turn_left": [KEY_Q],
	"turn_right": [KEY_E],
	"shadows_toggle": [KEY_F2],
}

func _enter_tree() -> void:
	for action in ACTIONS:
		if InputMap.has_action(action):
			continue
		InputMap.add_action(action)
		for key in ACTIONS[action]:
			var ev := InputEventKey.new()
			ev.physical_keycode = key
			InputMap.action_add_event(action, ev)
