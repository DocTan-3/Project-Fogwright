extends Node
## loads a script in the running project (autoloads present) to surface parse errors fast:  -- script=res://...
func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("script="):
			var s = load(a.split("=")[1])
			print("PARSE ", "ok" if s and s.can_instantiate() else "FAILED")
	get_tree().quit()
