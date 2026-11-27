## A villager going about the day: walks the village's paths from place to place (the well, the tavern, the pier, the
## smithy, the field), pauses there a while, sometimes talking. Stays on the ground of the level it belongs to.
extends Node3D

const WALK := 1.25        # m/s; the walk clip travels 0.97 m/s, so it plays a little faster
var level                  # the Farhallow node (height(), the path graph)
var graph: Dictionary      # node id -> [Vector2 position, [neighbour ids]]
var route: Array = []
var here := 0
var wait := 0.0
var ap: AnimationPlayer
var model: Node3D
var blob: MeshInstance3D
var rng := RandomNumberGenerator.new()

func setup(lv, g: Dictionary, start: int, look: Dictionary, seed_: int) -> void:
	level = lv; graph = g; here = start; rng.seed = seed_
	model = load(look.body).instantiate(); add_child(model)
	Dress.wear(model, look.outfit)
	if look.has("hair"):
		var cols := [Color(0.32, 0.2, 0.12), Color(0.18, 0.12, 0.08), Color(0.62, 0.42, 0.2), Color(0.45, 0.16, 0.08), Color(0.78, 0.66, 0.42), Color(0.7, 0.7, 0.68)]
		Dress.wear(model, look.hair, cols[rng.randi() % cols.size()])
	ap = Dress.animate(model); ap.playback_default_blend_time = 0.3
	blob = Dress.blob(); add_child(blob)

	position = _w(graph[here][0]); wait = rng.randf_range(0.5, 6.0)
	ap.play("ual/Idle" if rng.randf() < 0.6 else "ual/Idle_Talking")
	ap.seek(rng.randf() * 2.0)

func _w(p: Vector2) -> Vector3:
	return level.W(p, level.height(p))

func _process(delta: float) -> void:
	if wait > 0.0:
		wait -= delta
		if wait <= 0.0: _new_route()
		return
	if route.is_empty():
		wait = rng.randf_range(4.0, 14.0)
		ap.play("ual/Idle_Talking" if rng.randf() < 0.4 else "ual/Idle"); ap.speed_scale = 1.0
		return
	var target: Vector2 = graph[route[0]][0]
	var p := Vector2(position.x, position.z) + Vector2(level.ORIGIN.x, level.ORIGIN.y)
	var to := target - p
	if to.length() < 0.25:
		here = route.pop_front(); return
	var step := to.normalized() * minf(WALK * delta, to.length())
	var np := p + step
	position = _w(np)
	model.rotation.y = lerp_angle(model.rotation.y, atan2(step.x, step.y), 1.0 - exp(-8.0 * delta))
	if ap.current_animation != "ual/Walk": ap.play("ual/Walk")
	ap.speed_scale = WALK / 0.97

func _new_route() -> void:
	var goals: Array = level.GOALS
	var goal: int = goals[rng.randi() % goals.size()]
	route = _bfs(here, goal)

func _bfs(a: int, b: int) -> Array:
	var prev := {a: -1}; var q := [a]
	while not q.is_empty():
		var n: int = q.pop_front()
		if n == b: break
		for m in graph[n][1]:
			if not prev.has(m): prev[m] = n; q.append(m)
	var out := []; var c := b
	while prev.has(c) and c != a: out.push_front(c); c = prev[c]
	return out
