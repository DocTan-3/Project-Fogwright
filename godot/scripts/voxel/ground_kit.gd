## Fogwright's ground (docs/design.md, Voxel art: the ground kit). Not Minecraft cubes: the land is a grid of 1 m cells whose
## corners snap to 0.5 m height steps, so every cell is one of a small kit of "snapping pieces" - flat, a 27 degree slope
## (one step across a cell), a 45 degree bank (two steps), their corners and saddles - and where the ground drops more
## than that across a cell, a cliff of rock built from 25 cm voxel columns with ledges. The surfaces are flat-shaded facets
## coloured from the palette; a 10 cm speckle in the shader gives them the voxel grain of everything else, without steps.
## Grass is not voxels: low-poly tufts of blades that sway in the wind and bend away from whoever walks through them.
##   var g := GroundKit.build(height_fn, Rect2(x0, z0, w, d), kind_fn)   # height_fn(Vector2 xz) -> float metres
##   add_child(g); GroundKit.push(g, [player.global_position, ...])        # each frame: who is bending the grass
class_name GroundKit
extends RefCounted

const CELL := 1.0          # the kit's cell: half the 2 m building module
const STEP := 0.5          # a height step: one across a cell is a 27 degree slope, two a 45 degree bank
const ROCK := 0.25         # a cliff's rock columns
const COLS := {"grass": Color("5f7a3a"), "grass_d": Color("4e6a30"), "dirt": Color("7a6448"), "path": Color("9a7d58"),
	"sand": Color("c2ad80"), "rock": Color("77736b"), "rock_d": Color("5e5b55"), "moss": Color("5d6b3a")}
const MAX_PUSH := 8
const GRASS_CHUNK := 16.0
const GRASS_RANGE := 45.0   # grass is drawn this far from the camera (the Albion view's height reaches about this)
const SUB := 4            # where kinds meet, a cell is drawn in 4 x 4 squares (25 cm)

## kind_fn(Vector2 xz, slope_deg) -> "grass" | "dirt" | "path" | "sand" (what the ground is there); grass grows on "grass"
static func build(height_fn: Callable, rect: Rect2, kind_fn: Callable, grass_per_m2 := 9.0, seed := 1) -> Node3D:
	var root := Node3D.new(); root.name = "Ground"
	var nx := int(rect.size.x / CELL); var nz := int(rect.size.y / CELL)
	var H := PackedFloat32Array(); H.resize((nx + 1) * (nz + 1))
	for j in nz + 1:
		for i in nx + 1:
			H[j * (nx + 1) + i] = snappedf(height_fn.call(rect.position + Vector2(i, j) * CELL), STEP)
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var rock := SurfaceTool.new(); rock.begin(Mesh.PRIMITIVE_TRIANGLES)
	var grass_tris := []   # [a, b, c] world points of grassy triangles, where the tufts grow
	var counts := {}
	# first pass: which cells are cliffs, and which are drawn in 25 cm squares (where the ground's kind changes inside the
	# cell: a path's edge, the beach), so edges run in fine voxel-like steps rather than a 1 m saw-tooth
	var cliff := PackedByteArray(); cliff.resize(nx * nz)
	var mixed := PackedByteArray(); mixed.resize(nx * nz)
	for j in nz:
		for i in nx:
			var p0 := rect.position + Vector2(i, j) * CELL
			var h := [H[j * (nx + 1) + i], H[j * (nx + 1) + i + 1], H[(j + 1) * (nx + 1) + i + 1], H[(j + 1) * (nx + 1) + i]]
			if h.max() - h.min() > 2.0 * STEP + 0.001: cliff[j * nx + i] = 1; continue
			var k0: String = kind_fn.call(p0 + Vector2(0.5, 0.5) * CELL, 0.0)
			for q in [Vector2(0.1, 0.1), Vector2(0.9, 0.1), Vector2(0.9, 0.9), Vector2(0.1, 0.9)]:
				if kind_fn.call(p0 + q * CELL, 0.0) != k0: mixed[j * nx + i] = 1; break
	var fine := func(i: int, j: int) -> bool: return i >= 0 and j >= 0 and i < nx and j < nz and mixed[j * nx + i] == 1
	for j in nz:
		for i in nx:
			var p0 := rect.position + Vector2(i, j) * CELL
			var h := [H[j * (nx + 1) + i], H[j * (nx + 1) + i + 1], H[(j + 1) * (nx + 1) + i + 1], H[(j + 1) * (nx + 1) + i]]
			var mn: float = h.min()
			var c := [Vector3(p0.x, h[0], p0.y), Vector3(p0.x + CELL, h[1], p0.y), Vector3(p0.x + CELL, h[2], p0.y + CELL), Vector3(p0.x, h[3], p0.y + CELL)]
			if cliff[j * nx + i] == 0:
				var piece := _piece_name(h); counts[piece] = counts.get(piece, 0) + 1
				# the diagonal that keeps the piece's fold along its steps: across the pair of corners that differ least
				var d02 := absf(h[0] - h[2]) <= absf(h[1] - h[3])
				var q := func(u: float, v: float) -> Vector3: return Vector3(p0.x + u * CELL, _surf(h, d02, u, v), p0.y + v * CELL)
				var tris: Array = []
				if mixed[j * nx + i] == 1:
					for a in SUB:
						for b in SUB:
							var u0 := float(a) / SUB; var u1 := float(a + 1) / SUB; var v0 := float(b) / SUB; var v1 := float(b + 1) / SUB
							var Q := [q.call(u0, v0), q.call(u1, v0), q.call(u1, v1), q.call(u0, v1)]
							tris += [[Q[0], Q[1], Q[2]], [Q[0], Q[2], Q[3]]] if d02 else [[Q[0], Q[1], Q[3]], [Q[1], Q[2], Q[3]]]
				else:
					# a plain cell beside fine ones shares their 25 cm points along that edge, or the edge would be a T-junction
					# and crack open into a dark seam. It is fanned from its centre, which lies on the fold, so every
					# triangle stays on one of the cell's two planes.
					var edges := [[Vector2(0, 0), Vector2(1, 0), fine.call(i, j - 1)], [Vector2(1, 0), Vector2(1, 1), fine.call(i + 1, j)],
						[Vector2(1, 1), Vector2(0, 1), fine.call(i, j + 1)], [Vector2(0, 1), Vector2(0, 0), fine.call(i - 1, j)]]
					var any := false
					for e in edges: any = any or e[2]
					if not any:
						var Q := [q.call(0, 0), q.call(1, 0), q.call(1, 1), q.call(0, 1)]
						tris = [[Q[0], Q[1], Q[2]], [Q[0], Q[2], Q[3]]] if d02 else [[Q[0], Q[1], Q[3]], [Q[1], Q[2], Q[3]]]
					else:
						var ctr: Vector3 = q.call(0.5, 0.5)
						for e in edges:
							var n_seg: int = SUB if e[2] else 1
							for s in n_seg:
								var A: Vector2 = e[0].lerp(e[1], float(s) / n_seg); var B: Vector2 = e[0].lerp(e[1], float(s + 1) / n_seg)
								tris.append([q.call(A.x, A.y), q.call(B.x, B.y), ctr])
				for t in tris:
					var n: Vector3 = (t[2] - t[0]).cross(t[1] - t[0]).normalized()
					if n.y < 0: n = -n
					var slope := rad_to_deg(acos(clampf(n.y, -1.0, 1.0)))
					var mid: Vector3 = (t[0] + t[1] + t[2]) / 3.0
					var kind: String = kind_fn.call(Vector2(mid.x, mid.z), slope)
					var col: Color = COLS[kind]
					if kind == "grass":   # a darker turf on steep banks, patchy tones on the level
						col = col.lerp(COLS.grass_d, 0.35 * _hash2(floori(mid.x * 0.5), floori(mid.z * 0.5), seed) + clampf((slope - 20.0) / 40.0, 0.0, 0.65))
					_tri(st, t, n, col)
					if kind == "grass": grass_tris.append(t)
			else:
				counts["cliff"] = counts.get("cliff", 0) + 1
				_cliff(rock, c, h, mn, seed)
	var ground := MeshInstance3D.new(); ground.name = "Surface"; ground.mesh = st.commit(); ground.material_override = _surface_mat()
	var rocks := MeshInstance3D.new(); rocks.name = "Rock"; rocks.mesh = rock.commit(); rocks.material_override = _surface_mat()
	root.add_child(ground); root.add_child(rocks)
	var body := StaticBody3D.new(); body.name = "GroundBody"; root.add_child(body)
	for m in [ground, rocks]:
		if (m.mesh as ArrayMesh).get_surface_count() == 0: continue
		var cs := CollisionShape3D.new(); cs.shape = m.mesh.create_trimesh_shape(); body.add_child(cs)
	root.add_child(_grass(grass_tris, grass_per_m2, seed))
	root.set_meta("pieces", counts)
	return root

## the height inside a cell (u, v from 0 to 1 across it) on its two planes: the diagonal from corner 0 to 2, or 1 to 3
static func _surf(h: Array, d02: bool, u: float, v: float) -> float:
	if d02:
		if u >= v: return h[0] + (h[1] - h[0]) * u + (h[2] - h[1]) * v
		return h[0] + (h[2] - h[3]) * u + (h[3] - h[0]) * v
	if u + v <= 1.0: return h[0] + (h[1] - h[0]) * u + (h[3] - h[0]) * v
	return h[2] + (h[2] - h[3]) * (u - 1.0) + (h[2] - h[1]) * (v - 1.0)

## which kit piece a cell is, from its corners' steps above the lowest: flat, slope, bank, corner, saddle...
static func _piece_name(h: Array) -> String:
	var mn: float = h.min(); var s := []
	for v in h: s.append(int(round((v - mn) / STEP)))
	var hi := 0; for v in s: hi = maxi(hi, v)
	if hi == 0: return "flat"
	var up := 0; for v in s: up += 1 if v > 0 else 0
	var kind := "slope" if hi == 1 else "bank"
	if up == 2: return kind + (" (saddle)" if s[0] == s[2] else "")
	return kind + (" outer corner" if up == 1 else " inner corner") if up != 4 else kind + " mixed"

static func _tri(st: SurfaceTool, t: Array, n: Vector3, col: Color) -> void:
	_face(st, t, n, col)

## one triangle facing along n: Godot's front faces wind clockwise as seen from in front
static func _face(st: SurfaceTool, t: Array, n: Vector3, col: Color) -> void:
	var a: Vector3 = t[0]; var b: Vector3 = t[1]; var c: Vector3 = t[2]
	if (b - a).cross(c - a).dot(n) > 0.0: var sw := b; b = c; c = sw
	st.set_normal(n); st.set_color(col); st.add_vertex(a)
	st.set_normal(n); st.set_color(col); st.add_vertex(b)
	st.set_normal(n); st.set_color(col); st.add_vertex(c)

## a cliff cell: rock columns 25 cm across, each as tall as the ground would be there, with ledges (snapped heights and a
## little jitter), standing on the cell's lowest corner; mossy where a column's top is near level ground
static func _cliff(st: SurfaceTool, c: Array, h: Array, mn: float, seed: int) -> void:
	var k := int(CELL / ROCK)
	for a in k:
		for b in k:
			var u := (a + 0.5) / k; var v := (b + 0.5) / k
			var top: float = lerpf(lerpf(h[0], h[1], u), lerpf(h[3], h[2], u), v)
			var x0: float = c[0].x + a * ROCK; var z0: float = c[0].z + b * ROCK
			top = snappedf(top + (_hash2(floori(x0 * 4.0), floori(z0 * 4.0), seed + 3) - 0.5) * 0.7 + (_hash2(floori(x0), floori(z0), seed + 5) - 0.5) * 0.5, ROCK)
			var bot := mn - 0.3
			var tone := _hash2(floori(x0 * 4.0) + 11, floori(z0 * 4.0) - 7, seed)
			var side: Color = COLS.rock.lerp(COLS.rock_d, tone)
			var cap: Color = COLS.moss if tone < 0.45 else side.lightened(0.08)
			_box(st, Vector3(x0, bot, z0), Vector3(x0 + ROCK, top, z0 + ROCK), side, cap)

static func _box(st: SurfaceTool, lo: Vector3, hi: Vector3, side: Color, cap: Color) -> void:
	var P := func(x: int, y: int, z: int) -> Vector3: return Vector3(hi.x if x else lo.x, hi.y if y else lo.y, hi.z if z else lo.z)
	var quads := [[Vector3.UP, [P.call(0,1,0), P.call(1,1,0), P.call(1,1,1), P.call(0,1,1)], cap],
		[Vector3.RIGHT, [P.call(1,0,0), P.call(1,0,1), P.call(1,1,1), P.call(1,1,0)], side],
		[Vector3.LEFT, [P.call(0,0,1), P.call(0,0,0), P.call(0,1,0), P.call(0,1,1)], side],
		[Vector3.BACK, [P.call(1,0,1), P.call(0,0,1), P.call(0,1,1), P.call(1,1,1)], side.darkened(0.06)],
		[Vector3.FORWARD, [P.call(0,0,0), P.call(1,0,0), P.call(1,1,0), P.call(0,1,0)], side.darkened(0.1)]]
	for q in quads:
		var v: Array = q[1]
		for t in [[v[0], v[1], v[2]], [v[0], v[2], v[3]]]: _face(st, t, q[0], q[2])

static func _hash2(x: int, y: int, s: int) -> float:
	var n := (x * 374761393 + y * 668265263 + s * 2147483647) & 0x7fffffff
	n = ((n ^ (n >> 13)) * 1274126177) & 0x7fffffff
	return float(n % 10000) / 10000.0

static var _smat: ShaderMaterial
static func _surface_mat() -> ShaderMaterial:
	if _smat: return _smat
	var sh := Shader.new()
	sh.code = """
shader_type spatial;
varying vec3 wp;
varying vec3 wn;
void vertex() { wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; wn = (MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz; }
float h3(vec3 p) { return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453); }
void fragment() {
	// the voxel grain: a 10 cm speckle, laid from above on the ground and on the face's own plane on cliffs
	vec3 cell = abs(wn.y) > 0.6 ? vec3(floor(wp.x * 10.0), 0.0, floor(wp.z * 10.0)) : floor(wp * 10.0 + wn * 0.5);
	float k = h3(cell);
	float g = k < 0.18 ? 0.94 : (k > 0.86 ? 1.05 : 1.0);
	vec3 c = COLOR.rgb * g;
	ALBEDO = c * c * 1.0;   // the palette's colours are sRGB
	ROUGHNESS = 1.0;
}
"""
	_smat = ShaderMaterial.new(); _smat.shader = sh
	return _smat

# ---------------------------------------------------------------- grass: blades, not voxels
## tufts scattered over the grassy triangles; a tuft is five tapered blades (a few triangles), dark at the root and light at
## the tip, each a little different in height and lean. The shader sways them in the wind and bends them away from
## whoever is near (push()), springing back as they leave.
static var _clump := FastNoiseLite.new()
static func _grass(tris: Array, per_m2: float, seed: int) -> Node3D:
	_clump.seed = seed; _clump.frequency = 0.09
	var rng := RandomNumberGenerator.new(); rng.seed = seed * 7919 + 13
	var chunks := {}   # Vector2i -> [Transform3D]: grass is drawn in 16 m chunks, each only near the camera
	var total := 0
	for t in tris:
		var a: Vector3 = t[0]; var b: Vector3 = t[1]; var c: Vector3 = t[2]
		var area := (b - a).cross(c - a).length() * 0.5
		var mid: Vector3 = (a + b + c) / 3.0
		var patch := _clump.get_noise_2d(mid.x, mid.z) * 0.5 + 0.5          # meadow in drifts: thick, thin, bare
		var n := int(area * per_m2 * smoothstep(0.25, 0.75, patch) * 1.6 + rng.randf())
		for k in n:
			var r1 := rng.randf(); var r2 := rng.randf()
			if r1 + r2 > 1.0: r1 = 1.0 - r1; r2 = 1.0 - r2
			var p := a + (b - a) * r1 + (c - a) * r2
			var s := rng.randf_range(0.55, 1.1) * lerpf(0.7, 1.15, _clump.get_noise_2d(p.x * 2.0, p.z * 2.0) * 0.5 + 0.5)
			var key := Vector2i(floori(p.x / GRASS_CHUNK), floori(p.z / GRASS_CHUNK))
			if not chunks.has(key): chunks[key] = []
			chunks[key].append(Transform3D(Basis(Vector3.UP, rng.randf() * TAU).scaled(Vector3(s, s * rng.randf_range(0.8, 1.2), s)), p))
			total += 1
	var root := Node3D.new(); root.name = "Grass"
	var tuft := _tuft()
	for key in chunks:
		var xs: Array = chunks[key]
		var mm := MultiMesh.new(); mm.transform_format = MultiMesh.TRANSFORM_3D; mm.use_colors = true
		mm.mesh = tuft; mm.instance_count = xs.size()
		for i in xs.size():
			mm.set_instance_transform(i, xs[i])
			mm.set_instance_color(i, Color(1, 1, 1).lerp(Color(1.12, 1.05, 0.7) if rng.randf() < 0.3 else Color(0.82, 0.92, 0.78), rng.randf()))   # some sun-dried
		var mi := MultiMeshInstance3D.new(); mi.multimesh = mm; mi.material_override = _grass_mat()
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mi.visibility_range_end = GRASS_RANGE; mi.visibility_range_end_margin = 6.0
		root.add_child(mi)
	root.set_meta("tufts", total)
	return root

static func _tuft() -> ArrayMesh:
	var st := SurfaceTool.new(); st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var rng := RandomNumberGenerator.new(); rng.seed = 5
	var root_c := Color("3e5a26"); var tip_c := Color("9ab55a")
	for k in 5:
		var ang := TAU * k / 5.0 + rng.randf_range(-0.4, 0.4)
		var off := Vector3(cos(ang), 0, sin(ang)) * rng.randf_range(0.0, 0.07)
		var hgt := rng.randf_range(0.22, 0.4); var w := rng.randf_range(0.025, 0.04)
		var side := Vector3(-sin(ang), 0, cos(ang)) * w
		var lean := Vector3(cos(ang), 0, sin(ang)) * rng.randf_range(0.03, 0.1)
		var mid := off + lean * 0.4 + Vector3(0, hgt * 0.55, 0)
		var tip := off + lean + Vector3(0, hgt, 0)
		# a blade: a quad up to the middle, a point above; UV.y is how far up the blade (the shader bends by it)
		var quad := [[off - side, 0.0], [off + side, 0.0], [mid + side * 0.6, 0.55], [mid - side * 0.6, 0.55]]
		for t in [[quad[0], quad[1], quad[2]], [quad[0], quad[2], quad[3]], [quad[3], quad[2], [tip, 1.0]]]:
			for v in t:
				st.set_color(root_c.lerp(tip_c, v[1])); st.set_uv(Vector2(0, v[1])); st.set_normal(Vector3.UP)
				st.add_vertex(v[0])
	return st.commit()

static var _gmat: ShaderMaterial
static func _grass_mat() -> ShaderMaterial:
	if _gmat: return _gmat
	var sh := Shader.new()
	sh.code = """
shader_type spatial;
render_mode cull_disabled;
uniform vec4 pushers[%d];     // xyz position, w radius (0: unused)
uniform float wind_strength = 0.06;
uniform vec2 wind_dir = vec2(0.8, 0.6);
void vertex() {
	float up = UV.y;
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	vec3 root = (MODEL_MATRIX * vec4(0.0, 0.0, 0.0, 1.0)).xyz;
	// wind: gusts rolling across the field
	float gust = sin(TIME * 1.7 + dot(root.xz, wind_dir) * 0.6) * 0.6 + sin(TIME * 3.1 + root.x * 1.3) * 0.25;
	vec3 bend = vec3(wind_dir.x, 0.0, wind_dir.y) * gust * wind_strength;
	// whoever is near pushes the blades away and down, springing back as they pass
	for (int i = 0; i < %d; i++) {
		vec4 p = pushers[i];
		if (p.w <= 0.0) continue;
		vec2 d = root.xz - p.xz;
		float dist = length(d);
		float k = 1.0 - smoothstep(p.w * 0.35, p.w, dist);
		if (k > 0.0 && abs(root.y - p.y) < 1.5) {
			bend += vec3(d.x, 0.0, d.y) / max(dist, 0.05) * k * 0.28;
			bend.y -= k * 0.16;
		}
	}
	w += bend * up * up;
	VERTEX = (inverse(MODEL_MATRIX) * vec4(w, 1.0)).xyz;
}
void fragment() {
	vec3 c = COLOR.rgb;
	ALBEDO = c * c;
	ROUGHNESS = 1.0;
	BACKLIGHT = vec3(0.25);
}
""" % [MAX_PUSH, MAX_PUSH]
	_gmat = ShaderMaterial.new(); _gmat.shader = sh
	return _gmat

## who bends the grass this frame: up to MAX_PUSH world positions (feet), each with a radius of about 0.7 m
static func push(ground: Node3D, positions: Array, radius := 0.7) -> void:
	var arr := []
	for i in MAX_PUSH:
		if i < positions.size():
			var p: Vector3 = positions[i]; arr.append(Vector4(p.x, p.y, p.z, radius))
		else: arr.append(Vector4.ZERO)
	_grass_mat().set_shader_parameter("pushers", arr)
