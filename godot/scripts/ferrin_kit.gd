## The Ferrin Quarter's buildings, ported from the three.js prototype (makehuman-bodies branch: game/index.html, models built
## by tools/blender/ferrin_forge.py and ferrin_kit.py). Each model carries its weathering baked into vertex colours (occlusion,
## soot, rust); its surfaces are named by material (F_stone, F_ashlar ...) and take CC0 Poly Haven textures and a tint here,
## as the prototype did at runtime. Each file also holds a decimated far version (<name>_LOD1), shown beyond 110 m.
##
## PENDING (do not place in a level yet): check these against the new assets and art direction - Palette's library
## materials and the "ember" palette (dark basalt, blackened iron and brass), the Medieval Village MegaKit, real model
## sizes (tools/assets/model_sizes.py) and the city-planning checker. See tools/assets/INVENTORY.md, "Pending checks".
class_name FerrinKit
extends RefCounted

const DIR := "res://assets/buildings/ferrin/"
const LOD_DISTANCE := 110.0

## material: [texture set (tex/<set>_diff|nor|rough.jpg), tint (sRGB), metallic]
const MATS := {
	"F_stone": ["rock_wall_05_desat", Color(0.15, 0.155, 0.17), 0.0],          # the body: dark coursed basalt rubble
	"F_ashlar": ["medieval_blocks_03_desat", Color(0.25, 0.255, 0.27), 0.0],   # dressed stone: plinth, quoins, sills, coping
	"F_brick": ["castle_brick_07", Color(0.62, 0.48, 0.42), 0.0],               # stacks and hearths
	"F_iron": ["metal_plate_02", Color(0.22, 0.22, 0.24), 0.25],                # roofs, doors, cornices
	"F_rust": ["rusty_metal_02", Color(0.30, 0.24, 0.20), 0.25],                # shutters, straps, signs
	"F_wood": ["dark_wooden_planks", Color(0.70, 0.62, 0.55), 0.0],
	"F_copper": ["rusty_metal_02", Color(0.78, 0.46, 0.30), 0.25],              # pipes
}

## each building, in its own frame: front door toward +Z, the ground at y = 0.
##   walls: the stone footprint (w, d); plot: the ground it takes with its battered base; door: [x, half width] on the
##   front face (keep it clear); vents: [x, y, z, size] where smoke leaves; canopy: the forge's iron canopy over the street
const BUILDINGS := {
	"forge": {"file": "ferrin_forge.glb", "node": "FerrinForge", "walls": Vector2(10.6, 11.0), "plot": Vector2(11.5, 11.9),
		"door": [2.575, 0.6], "vents": [[3.8, 17.6, -3.9, 1.6]], "canopy": {"x": -2.0, "z0": 5.5, "z1": 8.25, "hw": 3.0}},
	"shop": {"file": "ferrin_shop.glb", "node": "FerrinShop", "walls": Vector2(7.8, 10.0), "plot": Vector2(8.6, 10.8),
		"door": [2.25, 0.55], "vents": [[2.7, 11.7, -3.8, 0.9]]},
	"smelter": {"file": "ferrin_smelter.glb", "node": "FerrinSmelter", "walls": Vector2(12.4, 12.4), "plot": Vector2(13.2, 13.2),
		"door": [0.0, 2.6], "vents": [[4.1, 19.6, -4.1, 2.0], [1.3, 8.55, 0.0, 1.1]]},
	"shrine": {"file": "ferrin_shrine.glb", "node": "FerrinShrine", "walls": Vector2(6.0, 6.6), "plot": Vector2(7.6, 8.2),
		"door": [0.0, 0.8], "vents": [[0.0, 7.3, 0.0, 0.6]]},   # Ostrak's shrine: the brazier smokes
	"narrow": {"file": "ferrin_narrow.glb", "node": "FerrinNarrow", "walls": Vector2(5.6, 9.6), "plot": Vector2(6.4, 10.4),
		"door": [-1.275, 0.53], "vents": [[-1.7, 11.1, -3.7, 0.8]]},
	"toolmaker": {"file": "ferrin_toolmaker.glb", "node": "FerrinToolmaker", "walls": Vector2(7.4, 9.0), "plot": Vector2(9.0, 9.8),
		"door": [0.0, 0.55], "vents": [[4.06, 10.6, -1.2, 0.8]]},
	"stair": {"file": "ferrin_stair.glb", "node": "FerrinStair", "walls": Vector2(6.4, 9.4), "plot": Vector2(9.0, 10.2),
		"door": [-1.25, 1.25], "vents": [[-2.1, 10.2, -3.5, 0.8]]},   # the door is the workshop's; the house door is up the side stair
	"foundry": {"file": "ferrin_foundry.glb", "node": "FerrinFoundry", "walls": Vector2(16.0, 14.0), "plot": Vector2(21.0, 17.0),
		"door": [0.0, 1.8], "vents": [[-5.0, 17.1, -5.0, 1.6], [5.0, 17.1, -5.0, 1.6], [-9.3, 3.3, 2.0, 0.7]], "scale": 1.5},
		# the Ironway Foundry is built at 2/3 size and drawn at 1.5x (24 x 21 m); its doorway is a true opening into the hall
}

static var _mats := {}

static func _tex(path: String) -> Texture2D:
	return load(path) as Texture2D

## the material for one of the kit's surfaces, or null to keep the model's own
static func material(name: String) -> Material:
	var key := name.get_slice(".", 0)
	if _mats.has(key): return _mats[key]
	var m := StandardMaterial3D.new()
	m.resource_name = key
	m.vertex_color_use_as_albedo = true   # the baked occlusion, soot and rust
	m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS_ANISOTROPIC
	if key == "F_glow":                   # coals, lanterns, glowing hearths
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.vertex_color_use_as_albedo = false
		m.albedo_color = Color("ff5a14")
		m.emission_enabled = true; m.emission = Color("ff5a14"); m.emission_energy_multiplier = 1.4
	elif key == "F_glass":                # dark window glass
		m.albedo_color = Color("0d0f12"); m.roughness = 0.15; m.metallic = 0.2
	elif MATS.has(key):
		var d: Array = MATS[key]; var base := DIR + "tex/" + str(d[0]).trim_suffix("_desat")
		m.albedo_texture = _tex(DIR + "tex/" + d[0] + "_diff.jpg")
		m.albedo_color = (d[1] as Color) * 1.06
		m.normal_enabled = true; m.normal_texture = _tex(base + "_nor.jpg")
		m.roughness = 1.0; m.roughness_texture = _tex(base + "_rough.jpg")
		m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
		m.metallic = d[2]
	else:
		return null
	_mats[key] = m
	return m

## a ready building: its own materials, the far version swapped in beyond LOD_DISTANCE
static func instance(kind: String) -> Node3D:
	var b: Dictionary = BUILDINGS[kind]
	var root: Node3D = (load(DIR + b.file) as PackedScene).instantiate()
	root.name = "Ferrin_" + kind
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		var far := m.name.ends_with("_LOD1") or (m.get_parent() and str(m.get_parent().name).ends_with("_LOD1"))
		if far: m.visibility_range_begin = LOD_DISTANCE
		else: m.visibility_range_end = LOD_DISTANCE
		for s in m.mesh.get_surface_count():
			var orig := m.mesh.surface_get_material(s)
			var nm := orig.resource_name if orig else ""
			var lib := material(nm)
			if lib: m.set_surface_override_material(s, lib)
	if b.has("scale"): root.scale = Vector3.ONE * float(b.scale)
	return root
