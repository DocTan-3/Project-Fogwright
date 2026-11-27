## Dressing a character: outfits and hair from the Quaternius kits share the base body's 65-bone rig, so their skinned
## meshes are moved onto the body's own skeleton and play its animations as they are.
class_name Dress

static func skeleton_of(model: Node) -> Skeleton3D:
	return model.find_children("*", "Skeleton3D", true, false)[0] as Skeleton3D

static func wear(model: Node, path: String, tint := Color.WHITE) -> void:
	var skel := skeleton_of(model)
	var piece: Node = load(path).instantiate()
	for mi in piece.find_children("*", "MeshInstance3D", true, false):
		var m := mi as MeshInstance3D
		if tint != Color.WHITE:   # the kit's hair is grey, made to be tinted
			for sidx in m.mesh.get_surface_count():
				var mat := m.mesh.surface_get_material(sidx)
				if mat is StandardMaterial3D:
					var t := (mat as StandardMaterial3D).duplicate() as StandardMaterial3D; t.albedo_color = tint; m.set_surface_override_material(sidx, t)
		m.get_parent().remove_child(m)
		skel.add_child(m)
		m.skeleton = NodePath("..")
		m.transform = Transform3D.IDENTITY
	piece.free()

## the library's animations on a model: an AnimationPlayer beside its skeleton
static func animate(model: Node3D, library_path := "res://assets/animations/quaternius/UAL1_Standard.glb") -> AnimationPlayer:
	var lib_scene: Node = load(library_path).instantiate()
	var src: AnimationPlayer = lib_scene.find_child("AnimationPlayer", true, false)
	var ap := AnimationPlayer.new(); ap.name = "AnimationPlayer"; model.add_child(ap); ap.root_node = NodePath("..")
	ap.add_animation_library("ual", src.get_animation_library("").duplicate())
	lib_scene.free()
	return ap

## a soft dark disc under the feet, the WoW way: costs almost nothing, lies on the ground
static func blob(size := 0.9) -> MeshInstance3D:
	var img := Image.create(64, 64, false, Image.FORMAT_RGBA8)
	for y in 64:
		for x in 64:
			var d := Vector2(x - 31.5, y - 31.5).length() / 32.0
			img.set_pixel(x, y, Color(0, 0, 0, 0.55 * clampf(1.0 - d * d, 0.0, 1.0)))
	var mat := StandardMaterial3D.new(); mat.albedo_texture = ImageTexture.create_from_image(img)
	mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA; mat.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	var m := MeshInstance3D.new(); var pm := PlaneMesh.new(); pm.size = Vector2(size, size); m.mesh = pm; m.material_override = mat
	m.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF; m.name = "Blob"; m.add_to_group("blob"); m.position.y = 0.03
	return m
