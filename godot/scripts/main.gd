## The first slice: a street, the player and the camera. The character model (Quaternius Universal Base Characters) and
## the animation library (Universal Animation Library) share one rig, so the library is added to the model as is.
extends Node3D

const ANIMS := "res://assets/animations/quaternius/UAL1_Standard.glb"

func _ready() -> void:
	var sun: DirectionalLight3D = $Sun   # the palette's light
	sun.light_color = Palette.col("sun"); sun.light_energy = float(Palette.value("sun_energy"))
	var sky: ProceduralSkyMaterial = $WorldEnvironment.environment.sky.sky_material
	sky.sky_top_color = Palette.col("sky_top"); sky.sky_horizon_color = Palette.col("sky_horizon"); sky.ground_horizon_color = Palette.col("sky_horizon")
	var model: Node3D = $Player/Model
	var lib_scene: Node = load(ANIMS).instantiate()
	var src: AnimationPlayer = lib_scene.find_child("AnimationPlayer", true, false)
	var ap := AnimationPlayer.new()
	ap.name = "AnimationPlayer"
	model.add_child(ap)
	ap.root_node = NodePath("..")
	var lib: AnimationLibrary = src.get_animation_library("").duplicate()
	ap.add_animation_library("ual", lib)
	lib_scene.free()
	$Player.setup_animation(ap, _build_tree(model, ap))

## Movement is blended, not switched: idle, walk, run and sprint are mixed by the player's speed in one blend space (kept in
## step, so the feet never restart), and a small state machine adds the jump - take-off, falling, landing - with crossfades.
func _build_tree(model: Node3D, ap: AnimationPlayer) -> AnimationTree:
	var clip := func(n: String) -> AnimationNodeAnimation:
		var a := AnimationNodeAnimation.new(); a.animation = "ual/" + n; return a
	var loco := AnimationNodeBlendSpace1D.new()
	loco.min_space = 0.0; loco.max_space = 9.0; loco.sync = true
	loco.add_blend_point(clip.call("Idle"), 0.0)
	loco.add_blend_point(clip.call("Walk"), $Player.WALK_SPEED)
	loco.add_blend_point(clip.call("Jog_Fwd"), $Player.RUN_SPEED)
	loco.add_blend_point(clip.call("Sprint"), $Player.SPRINT_SPEED)
	var ground := AnimationNodeBlendTree.new()
	ground.add_node("loco", loco); ground.add_node("rate", AnimationNodeTimeScale.new())
	ground.connect_node("rate", 0, "loco"); ground.connect_node("output", 0, "rate")
	# the library's falling loop throws both arms straight out (it reads as a T-pose at the top of a jump): mixed about half
	# with the idle pose, the arms stay lower and the body still reads as airborne
	var fall := AnimationNodeBlendTree.new()
	fall.add_node("air", clip.call("Jump")); fall.add_node("calm", clip.call("Idle"))
	var mix := AnimationNodeBlend2.new(); fall.add_node("mix", mix)
	fall.connect_node("mix", 0, "air"); fall.connect_node("mix", 1, "calm"); fall.connect_node("output", 0, "mix")
	var sm := AnimationNodeStateMachine.new()
	sm.add_node("ground", ground); sm.add_node("takeoff", clip.call("Jump_Start")); sm.add_node("fall", fall); sm.add_node("land", clip.call("Jump_Land"))
	var link := func(a: String, b: String, fade: float, at_end := false):
		var t := AnimationNodeStateMachineTransition.new(); t.xfade_time = fade
		if at_end:
			t.switch_mode = AnimationNodeStateMachineTransition.SWITCH_MODE_AT_END
			t.advance_mode = AnimationNodeStateMachineTransition.ADVANCE_MODE_AUTO
		sm.add_transition(a, b, t)
	var start := AnimationNodeStateMachineTransition.new(); start.advance_mode = AnimationNodeStateMachineTransition.ADVANCE_MODE_AUTO
	sm.add_transition("Start", "ground", start)
	link.call("ground", "takeoff", 0.08); link.call("ground", "fall", 0.25)
	link.call("takeoff", "fall", 0.2); link.call("takeoff", "ground", 0.15)
	link.call("fall", "ground", 0.12); link.call("fall", "land", 0.08); link.call("land", "ground", 0.22)
	var tree := AnimationTree.new()
	tree.name = "AnimationTree"
	model.add_child(tree)
	tree.anim_player = tree.get_path_to(ap)
	tree.tree_root = sm
	tree.active = true
	tree.set("parameters/fall/mix/blend_amount", 0.6)
	return tree
