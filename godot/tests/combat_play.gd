extends Node
## plays a fight in the real game with a bot that answers each telegraph with its natural counter (parry what can be parried,
## dodge the unblockable), attacking with each weapon in turn; prints what happened and saves screenshots:
##   godot --path . --rendering-driver opengl3 res://tests/combat_play.tscn -- out=<png prefix>
var out := "/tmp/combat"
var counts := {}
var dealt := {}
var main: Node3D
var pc: PlayerCombat
var shots := 0

func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("out="): out = a.split("=")[1]
	main = load("res://scenes/main.tscn").instantiate(); add_child(main)
	await _wait(2.5)
	pc = main.get_node("Player/Combat")
	pc.fighter.hit_taken.connect(func(r, a): counts[a.kind + ":" + r.outcome] = counts.get(a.kind + ":" + r.outcome, 0) + 1)
	var rig = main.get_node("CameraRig"); rig.pitch = deg_to_rad(-28); rig.distance = 5.5
	for w in (OS.get_environment("WEAPONS").split(",") if OS.get_environment("WEAPONS") != "" else Weapons.LIST):
		pc.equip(w); pc.fighter.hp = pc.fighter.max_hp; pc.fighter.stamina = 100.0; pc.fighter.energy = 100.0
		for e in get_tree().get_nodes_in_group("enemies"): e.queue_free()
		await _wait(0.2)
		var kinds := ["husk"] if w == "sword" else (["brute"] if w == "warhammer" else (["thrower"] if w == "pistol" else ["husk", "thrower"]))
		var f := Vector3(sin(main.get_node("Player/Model").rotation.y), 0, cos(main.get_node("Player/Model").rotation.y))
		for i in kinds.size():
			var e := FogEnemy.new(kinds[i]); e.target = pc.player; main.add_child(e)
			e.global_position = pc.player.global_position + f * (6.0 + 5.0 * i) + f.cross(Vector3.UP) * (2.0 * i) + Vector3(0, 0.6, 0)
			e.fighter.hit_taken.connect(func(r, _a): dealt[w] = dealt.get(w, 0.0) + r.taken)
		await _wait(0.3)
		pc.target = pc._nearest(); pc.engaged = true
		var t := 0.0; var used := false
		while t < 16.0 and not get_tree().get_nodes_in_group("enemies").is_empty() and not pc.fighter.dead:
			_bot()
			if not used and t > 2.0 and pc.target: pc.cast(pc.pages[0][0]); used = true
			if t > 2.0 and shots < 12 and fmod(t, 3.0) < get_process_delta_time(): await _shot(w)
			await get_tree().process_frame; t += get_process_delta_time()
			if not pc._target_ok(): pc.target = pc._nearest(); pc.engaged = pc.target != null
		var left := get_tree().get_nodes_in_group("enemies").size()
		print("COMBAT-PLAY %s: %.1fs, enemies left %d, hp %d, stamina %d, energy %d, ammo %d, momentum %d%%, shards %d" % [w, t, left, pc.fighter.hp, pc.fighter.stamina, pc.fighter.energy, pc.ammo, roundi(pc.momentum * 100), pc.shards])
	print("COMBAT-PLAY outcomes ", counts)
	print("COMBAT-PLAY damage dealt ", dealt)
	get_tree().quit()

## the counters a player would choose: parry a parryable blow (with a melee weapon), block it otherwise (held through a
## combo's hits), dodge what cannot be blocked, and raise the guard just before a projectile arrives
func _bot() -> void:
	var hold := false
	for e in get_tree().get_nodes_in_group("enemies"):
		var fe := e as FogEnemy
		var k: Dictionary = CombatRules.KINDS[fe._atk.kind] if not fe._atk.is_empty() else {}
		if fe._state == "strike" and fe._hits_left > 0 and k.get("block", false): hold = true   # the rest of a combo
		if fe._state != "windup" or fe._atk.kind == "projectile": continue
		var left: float = fe._atk.windup - fe._t
		if left < 0.14 and left > 0.0:
			if k.parry and pc.fighter.melee: pc.fighter.press_block()
			elif k.block: hold = true
			elif k.dodge and pc.player.control_lock <= 0.0: pc.dodge()
	for c in main.get_children():
		if c is FogProjectile and c._target_group == "player":
			var tti: float = (c.global_position - (pc.player.global_position + Vector3(0, 1, 0))).length() / maxf(c._v.length(), 0.1)
			if tti < 0.22: hold = true
	if hold: Input.action_press("block")
	else: Input.action_release("block")

func _shot(w: String) -> void:
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("%s_%02d_%s.png" % [out, shots, w]); shots += 1

func _wait(s: float) -> void:
	var t := 0.0
	while t < s: await get_tree().process_frame; t += get_process_delta_time()
