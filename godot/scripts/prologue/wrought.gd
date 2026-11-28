## Beat 6: the Wrought at the gate (lore.md: big shapes the Fog builds from memories of many things, part beast, part
## wall, part ship). It is never fought. About 11 m tall, in 20 cm voxels: legs of broken masts bound with wall stones,
## a body that is a ship's ribs and planking over a heap of drystone, long arms, one ending in an anchor's flukes, a head
## like a beast's skull of stone with a gull's beak, and pale eyes. It looms out of the Fog, lifts its arms and brings
## them down on the gate, then stands and turns its head.
class_name Wrought
extends Node3D

var arms: Array[Node3D] = []
var head: Node3D
var eyes: OmniLight3D
var _t := 0.0
var smashing := -1.0
signal smashed

func _ready() -> void:
	var S := 0.2
	var stone := Color8(108, 108, 104); var stone_d := Color8(78, 78, 76); var tar := Color8(60, 52, 46); var drift := Color8(120, 110, 96)
	var grey := Color8(92, 96, 100); var bone := Color8(170, 166, 150)
	var body := VBox.new(S)
	for s in [-1, 1]:   # legs: masts, bound with stones
		body.beam(Vector3(s * 1.6, 0, 0), Vector3(s * 1.2, 4.6, -0.3), 0.6, tar)
		for k in 6: body.blob(Vector3(s * (1.55 - k * 0.07), 0.6 + k * 0.7, -0.05 * k), Vector3(0.6, 0.35, 0.55), stone if k % 2 else stone_d, 0.1, k)
	body.blob(Vector3(0, 5.6, 0.0), Vector3(2.4, 1.9, 1.8), stone_d, 0.1, 3)      # the heap of stone
	for k in 9:   # a hull's ribs and strakes over it, broken
		var z := -1.4 + k * 0.35
		body.beam(Vector3(-2.2, 4.4, z), Vector3(-1.4, 7.6, z * 0.8), 0.25, drift)
		body.beam(Vector3(2.2, 4.4, z), Vector3(1.4, 7.6, z * 0.8), 0.25, drift)
		if k % 2 == 0: body.beam(Vector3(-2.3, 5.0 + k * 0.25, z), Vector3(2.3, 5.0 + k * 0.25, z), 0.2, tar)
	body.blob(Vector3(0, 7.6, 0.4), Vector3(1.6, 1.0, 1.2), grey, 0.1, 5)        # shoulders hunched forward
	var bm := MeshInstance3D.new(); bm.mesh = body.mesh(); bm.material_override = Vox.grain_material(S); add_child(bm)
	for s in [-1, 1]:
		var arm := Node3D.new(); arm.position = Vector3(s * 2.0, 7.8, 0.4); add_child(arm)
		var a := VBox.new(S)
		a.beam(Vector3(0, 0, 0), Vector3(s * 0.4, -3.2, 0.6), 0.6, stone_d)
		a.beam(Vector3(s * 0.4, -3.2, 0.6), Vector3(s * 0.2, -6.0, 1.6), 0.5, tar)
		if s > 0:   # the anchor's flukes
			a.beam(Vector3(-0.8, -6.2, 1.6), Vector3(1.2, -6.2, 1.6), 0.25, Color8(70, 66, 64))
			a.beam(Vector3(-0.8, -6.2, 1.6), Vector3(-1.0, -5.4, 2.0), 0.25, Color8(70, 66, 64)); a.beam(Vector3(1.2, -6.2, 1.6), Vector3(1.4, -5.4, 2.0), 0.25, Color8(70, 66, 64))
		else:
			for k in 4: a.beam(Vector3(s * 0.2, -6.0, 1.6), Vector3(s * 0.2 + (k - 1.5) * 0.4, -6.9, 2.2), 0.2, bone)
		var am := MeshInstance3D.new(); am.mesh = a.mesh(); am.material_override = Vox.grain_material(S); arm.add_child(am)
		arms.append(arm)
	head = Node3D.new(); head.position = Vector3(0, 8.6, 1.2); add_child(head)
	var h := VBox.new(S)
	h.blob(Vector3(0, 0.4, 0.2), Vector3(0.9, 0.7, 0.9), stone, 0.08, 9)
	h.beam(Vector3(0, 0.2, 0.9), Vector3(0, -0.4, 2.2), 0.4, bone)             # the beak
	h.box(Vector3(-0.6, 0.5, 0.95), Vector3(-0.3, 0.75, 1.1), Color8(230, 236, 236), 0.0)
	h.box(Vector3(0.3, 0.5, 0.95), Vector3(0.6, 0.75, 1.1), Color8(230, 236, 236), 0.0)
	var hm := MeshInstance3D.new(); hm.mesh = h.mesh(); hm.material_override = Vox.grain_material(S); head.add_child(hm)
	var em := StandardMaterial3D.new(); em.emission_enabled = true; em.emission = Color(0.85, 0.92, 1.0); em.emission_energy_multiplier = 3.0; em.albedo_color = Color.WHITE
	for x in [-0.45, 0.45]:
		var e := MeshInstance3D.new(); var sm := SphereMesh.new(); sm.radius = 0.16; sm.height = 0.32; e.mesh = sm; e.material_override = em
		e.position = Vector3(x, 0.62, 1.12); head.add_child(e)
	eyes = OmniLight3D.new(); eyes.light_color = Color(0.8, 0.9, 1.0); eyes.light_energy = 2.0; eyes.omni_range = 12.0; eyes.position = Vector3(0, 0.6, 1.6); head.add_child(eyes)

func smash() -> void: smashing = 0.0

func _process(delta: float) -> void:
	_t += delta
	var breathe := sin(_t * 1.2)
	head.rotation = Vector3(0.1 * breathe, 0.4 * sin(_t * 0.37), 0.05 * sin(_t * 0.8))
	eyes.light_energy = 2.0 + 0.6 * sin(_t * 3.0)
	if smashing >= 0.0:
		smashing += delta
		var up := clampf(smashing / 1.6, 0.0, 1.0); var down := clampf((smashing - 1.8) / 0.25, 0.0, 1.0)
		for a in arms: a.rotation.x = lerpf(-2.4 * ease(up, 0.5), -0.9, down)
		if smashing > 2.05 and smashing - delta <= 2.05: smashed.emit()
		if smashing > 4.0:
			smashing = -1.0
	else:
		for k in arms.size(): arms[k].rotation.x = lerpf(arms[k].rotation.x, 0.15 * sin(_t * 0.9 + k), 1.0 - exp(-2.0 * delta))
