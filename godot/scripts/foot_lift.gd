## Keeps the feet out of the ground: after the animation has posed the skeleton each frame, looks at the ground under
## each foot and ankle and lifts the model just enough that no sole goes under (on slopes the downhill foot would
## otherwise sink; some walk poses dip a foot lower too). Eased, so it never pops.
extends Node

var model: Node3D
var skel: Skeleton3D
var ground: Callable          # (world position) -> ground height there
var bones := []               # [bone index, its rest height above the soles]
var lift := 0.0

func setup(m: Node3D, g: Callable) -> void:
	model = m; ground = g
	skel = m.find_children("*", "Skeleton3D", true, false)[0]
	for n in ["foot_l", "foot_r", "ball_l", "ball_r"]:
		var i := skel.find_bone(n)
		if i >= 0: bones.append([i, (skel.global_transform.basis * skel.get_bone_global_rest(i).origin).y + 0.0])
	process_priority = 1000        # after the animation has run

var _hooked: AnimationMixer
var _last := 0

func _process(_delta: float) -> void:   # find the model's animation (it may be added after this) and follow its updates
	if _hooked or not model: return
	for m in model.get_parent().find_children("*", "AnimationMixer", true, false):
		var mixer := m as AnimationMixer
		if mixer is AnimationTree or not _hooked:
			if _hooked: _hooked.mixer_applied.disconnect(_apply)
			_hooked = mixer
	if _hooked: _hooked.mixer_applied.connect(_apply)

func _apply() -> void:   # right after the animation has posed the skeleton
	var now := Time.get_ticks_usec(); var delta := clampf((now - _last) / 1000000.0, 0.0, 0.1); _last = now
	if bones.is_empty(): return
	var need := 0.0
	for b in bones:
		var p: Vector3 = skel.global_transform * skel.get_bone_global_pose(b[0]).origin
		var sole: float = p.y - b[1] - lift           # where this sole would be without the current lift
		need = maxf(need, ground.call(p) - sole)
	need = clampf(need, 0.0, 0.3)
	lift = lerpf(lift, need, 1.0 - exp(-20.0 * delta)) if need < lift else need   # up at once, down gently
	model.position.y = lift
