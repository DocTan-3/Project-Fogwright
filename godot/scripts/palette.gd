## Fogwright's material library: every surface in the world takes its colour from one palette, and its detail (grain,
## cracks, wood lines) from a greyscale map, so models from different packs match. Pick a palette with the project's
## command line (-- palette=fog) or by setting `current`.
extends Node

# the colour each surface should come out as (sRGB), per palette; plus the light that suits it
const PALETTES := {
	"hearth": {   # warm and sunlit: honey stone, cream plaster, terracotta roofs, bright brass
		"Plaster": "e6d6b8", "WoodTrim": "86522e", "RockTrim": "b9a98c", "Brick": "a89c8a", "RedBrick": "a4483a",
		"UnevenBrick": "a99f90", "RoundTiles": "b5532e", "MetalOrnaments": "c49a4a", "Thatch": "c9a660", "Cloth": "d8ccb4", "Rope": "a88c62", "Iron": "5a5856", "Fish": "a9b2b4", "Glow": "ffd27a", "earth": "7a6448", "grass": "5f7a3a", "sand": "c2ad80", "sea": "2a6478", "path": "9a7d58",
		"sun": "fff2dc", "sun_energy": 1.35, "sky_top": "5d8fd0", "sky_horizon": "c9d6e2"},
	"fog": {      # cool and muted: grey-blue stone, pale plaster, weathered wood, slate roofs, verdigris copper
		"Plaster": "c9cbc6", "WoodTrim": "5b5752", "RockTrim": "8d9395", "Brick": "877870", "RedBrick": "7a645e",
		"UnevenBrick": "7d8589", "RoundTiles": "4d5966", "MetalOrnaments": "6e8f84", "Thatch": "a39a80", "Cloth": "bdbab0", "Rope": "8a8170", "Iron": "4f5457", "Fish": "9aa5aa", "Glow": "e8e0c0", "earth": "5d5d55", "grass": "6c7a5e", "sand": "b9b4a2", "sea": "33505e", "path": "7d766a",
		"sun": "e4ebf2", "sun_energy": 1.05, "sky_top": "7d93a8", "sky_horizon": "c3ccd3"},
	"ember": {    # industrial: dark basalt, ochre plaster, dark timber, copper roofs gone green, blackened iron and brass
		"Plaster": "c9a46c", "WoodTrim": "4a2f22", "RockTrim": "4d4b4f", "Brick": "7a3628", "RedBrick": "6a2c22",
		"UnevenBrick": "58544f", "RoundTiles": "4f7f6c", "MetalOrnaments": "b07b3a", "Thatch": "8e7446", "Cloth": "a8947a", "Rope": "6e5a42", "Iron": "3a3634", "Fish": "8a8a86", "Glow": "ffb060", "earth": "3f362e", "grass": "6a6b45", "sand": "8f8470", "sea": "2e4a52", "path": "5e5040",
		"sun": "ffe0b8", "sun_energy": 1.25, "sky_top": "6f86a6", "sky_horizon": "d8c2a8"},
}
var current := "hearth"   # the district palette; Hearth for the first towns
## how deep into the Fog this place lies, 0 (clear) .. 1 (deep): every colour fades toward a cold, grey-blue mute
var fog := 0.0
const FOG_TINT := Color(0.47, 0.5, 0.53)
var _cache := {}

func _enter_tree() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("palette="):
			current = a.split("=")[1]
		elif a.begins_with("fog="):
			fog = clampf(float(a.split("=")[1]), 0.0, 1.0)

func col(key: String) -> Color:
	return _fogged(_raw(key))

func _fogged(c: Color) -> Color:   # desaturate and cool toward the Fog's grey, keeping some of the colour's lightness
	if fog <= 0.0: return c
	var grey := Color(c.get_luminance(), c.get_luminance(), c.get_luminance())
	return c.lerp(grey, fog * 0.7).lerp(FOG_TINT * (0.6 + 0.6 * c.get_luminance()), fog * 0.35)

func _raw(key: String) -> Color:
	if not PALETTES.has(current): return Color.html({"earth": "6b5e4a", "sun": "fff4e0", "sky_top": "5c8cd1", "sky_horizon": "b8c7d6"}.get(key, "808080"))
	return Color.html(PALETTES.get(current, PALETTES.hearth).get(key, "808080"))

func value(key: String):
	if not PALETTES.has(current): return 1.3
	return PALETTES.get(current, PALETTES.hearth).get(key)

## the library material for one of the kit's materials (by its name, e.g. "MI_WoodTrim_Wear"), or null to keep it
func material_for(name: String, original: Material) -> Material:
	var key := name.trim_prefix("MI_").trim_suffix("_Wear").trim_suffix("_Dark").trim_suffix("_Light")
	if not PALETTES.has(current) or not PALETTES.hearth.has(key):   # an unknown palette ("original") keeps the kit's own
		return null
	var ck := current + ":" + str(fog) + ":" + name
	if _cache.has(ck):
		return _cache[ck]
	var m: StandardMaterial3D = (original as StandardMaterial3D).duplicate() if original is StandardMaterial3D else StandardMaterial3D.new()
	m.albedo_texture = load("res://assets/library/%s_detail.png" % key)
	var c := col(key) / 0.78
	if name.ends_with("_Wear"):
		c = c.lerp(Color(0.62, 0.6, 0.56) / 0.78, 0.25)   # worn wood: paler, greyer
	elif name.ends_with("_Dark"):
		c = c * 0.72                                       # the darker shade of the same surface
	elif name.ends_with("_Light"):
		c = c * 1.15
	if key == "Glow":                                      # lamp glass and candle flames give light
		m.emission_enabled = true; m.emission = col(key); m.emission_energy_multiplier = 1.5
	m.albedo_color = Color(minf(c.r, 1.0), minf(c.g, 1.0), minf(c.b, 1.0))
	_cache[ck] = m
	return m

## give every mesh under a node its library materials
func apply(root: Node) -> void:
	for mi in root.find_children("*", "MeshInstance3D", true, false):
		var mesh: Mesh = (mi as MeshInstance3D).mesh
		if mesh == null: continue
		for s in mesh.get_surface_count():
			var orig := mesh.surface_get_material(s)
			if orig == null: continue
			var lib := material_for(orig.resource_name, orig)
			if lib: (mi as MeshInstance3D).set_surface_override_material(s, lib)
