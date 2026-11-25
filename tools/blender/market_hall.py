# The Market Ward's covered market hall: an open arcade of round sandstone arches where the stalls trade, a jettied timber-framed
# hall above with plastered panels and leaded windows, a steep hipped roof of clay tiles with dormers, a clock lantern on the
# ridge. Built at true size (22 x 11 m). Same building blocks and finish as the Ferrin kit (the head of ferrin_forge.py), with
# the market's own CC0 textures (game/tex/market). One GLB: MarketHall and MarketHall_LOD1.
#
#   python3.11 market_hall.py -- out.glb          (RENDER=shot.png for a Cycles beauty shot)
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'ferrin_forge.py')).read()
exec(compile(src[:src.index('# ---------------------------------------------------------------- the forge-house')], 'ferrin_forge_head', 'exec'))
random.seed(5)
MTEX = os.path.abspath(os.path.join(HERE, '..', '..', 'game', 'tex', 'market'))
MATS['M_ashlar'] = ('white_sandstone_blocks_02', 2.0, (0.95, 0.92, 0.86), 0.0, 1.0)
MATS['M_plaster'] = ('painted_plaster_wall', 2.6, (1.12, 1.07, 0.96), 0.0, 1.0)
MATS['M_wood'] = ('medieval_wood', 1.4, (0.72, 0.62, 0.52), 0.0, 1.0)
MATS['M_tile'] = ('clay_roof_tiles_02', 1.6, (0.92, 0.78, 0.68), 0.0, 1.0)
MAT_LIST[:] = list(MATS.keys())
SAT = {'M_ashlar': 0.7, 'M_plaster': 0.6, 'M_wood': 0.9, 'M_tile': 0.95}

L, Wd = 22.0, 11.0                 # length along the avenue (x), depth (y); the avenue side is -y
NB, NS = 6, 3                      # bays along the long and short sides
G = 4.6                            # the upper floor's level
P = 0.95                           # pier size
SPR = 2.55                         # the arches' springing

def piers_and_arches():
    xs = [-L / 2 + i * L / NB for i in range(NB + 1)]; ys = [-Wd / 2 + j * Wd / NS for j in range(NS + 1)]
    pts = sorted({(x, y) for x in xs for y in (ys[0], ys[-1])} | {(x, y) for x in (xs[0], xs[-1]) for y in ys})
    box((0, 0, 0.15), (L + 1.6, Wd + 1.6, 0.3), 'M_ashlar', 0.03)                                       # the hall's floor, a step above the square
    box((0, 0, 0.31), (L + 1.0, Wd + 1.0, 0.02), 'M_ashlar', 0.0)
    for (x, y) in pts:
        box((x, y, 0.42), (P + 0.25, P + 0.25, 0.24), 'M_ashlar', 0.04)                                    # base
        box((x, y, (0.54 + SPR - 0.25) / 2), (P, P, SPR - 0.25 - 0.54), 'M_ashlar', 0.03)
        box((x, y, SPR - 0.12), (P + 0.22, P + 0.22, 0.24), 'M_ashlar', 0.04)                               # capital
    def arch_run(a0, a1, fixed, along_x):
        n = NB if along_x else NS; span = (a1 - a0) / n
        for i in range(n):
            c = a0 + (i + 0.5) * span; R = (span - P) / 2
            for k in range(13):   # voussoirs
                t0 = math.pi * k / 13; t1 = math.pi * (k + 1) / 13
                p = lambda t, r: (c + r * math.cos(t), SPR + 0.12 + r * math.sin(t))
                q = [p(t0, R), p(t1, R), p(t1, R + 0.42), p(t0, R + 0.42)]
                V = [Vector((u, fixed - P / 2, z)) if along_x else Vector((fixed - P / 2, u, z)) for (u, z) in q]
                prism(V, -P, (0, -1, 0) if along_x else (-1, 0, 0), 'M_ashlar', 0.012)
            for k in range(12):   # the spandrel wall above the arch, cut round it
                t0 = math.pi * k / 12; t1 = math.pi * (k + 1) / 12
                q = [(c + (R + 0.42) * math.cos(t0), SPR + 0.12 + (R + 0.42) * math.sin(t0)), (c + (R + 0.42) * math.cos(t1), SPR + 0.12 + (R + 0.42) * math.sin(t1)),
                     (c + (R + 0.42) * math.cos(t1), G - 0.3), (c + (R + 0.42) * math.cos(t0), G - 0.3)]
                V = [Vector((u, fixed - P / 2 + 0.08, z)) if along_x else Vector((fixed - P / 2 + 0.08, u, z)) for (u, z) in q]
                prism(V, -(P - 0.16), (0, -1, 0) if along_x else (-1, 0, 0), 'M_ashlar', 0.0)
    for y in (-Wd / 2, Wd / 2): arch_run(-L / 2, L / 2, y, True)
    for x in (-L / 2, L / 2): arch_run(-Wd / 2, Wd / 2, x, False)
    for (cx, cy, sx, sy) in [(0, -Wd / 2, L + P + 0.3, P + 0.3), (0, Wd / 2, L + P + 0.3, P + 0.3), (-L / 2, 0, P + 0.3, Wd - P - 0.3), (L / 2, 0, P + 0.3, Wd - P - 0.3)]:
        box((cx, cy, G - 0.2), (sx, sy, 0.3), 'M_ashlar', 0.04, tag='course')                               # the string course the timber hall stands on (the short runs stop at the long ones)
    box((0, 0, G - 0.32), (L, Wd, 0.25), 'M_wood', 0.0)                                                      # the hall's floor, seen as a timber ceiling from below
    for i in range(1, NB):
        box((-L / 2 + i * L / NB, 0, G - 0.52), (0.32, Wd, 0.4), 'M_wood', 0.01)                              # its great beams

def timber_hall():
    J = 0.45; H = 3.4; x0, x1, y0, y1 = -L / 2 - J, L / 2 + J, -Wd / 2 - J, Wd / 2 + J; z0 = G
    for (a, b, c2, n) in [((x0, y0), (x1, y0), 'x', 12), ((x0, y1), (x1, y1), 'x', 12), ((x0, y0), (x0, y1), 'y', 6), ((x1, y0), (x1, y1), 'y', 6)]:
        along = Vector((b[0] - a[0], b[1] - a[1], 0)); Ln = along.length; along.normalize(); nrm = Vector((-along.y, along.x, 0))
        out = Vector((a[0] + b[0], a[1] + b[1], 0)) / 2; out = out.normalized() if out.length > 0 else nrm
        if nrm.dot(out) < 0: nrm = -nrm
        base = Vector((a[0], a[1], z0))
        def at(u, z, d=0.0): return base + along * u + nrm * d + Vector((0, 0, z))
        mid = (base + along * (Ln / 2)); mid.z = z0 + H / 2
        box(mid - nrm * 0.12, (Ln if c2 == 'x' else 0.24, 0.24 if c2 == 'x' else Ln, H), 'M_plaster', 0.0)   # the plastered infill
        for zz in (0.0, H - 0.18): bx = mid.copy(); bx.z = z0 + zz + 0.09; box(bx + nrm * 0.02, (Ln if c2 == 'x' else 0.2, 0.2 if c2 == 'x' else Ln, 0.2), 'M_wood', 0.01)   # sill and plate
        mrail = mid.copy(); mrail.z = z0 + 0.95; box(mrail + nrm * 0.03, (Ln if c2 == 'x' else 0.14, 0.14 if c2 == 'x' else Ln, 0.14), 'M_wood', 0.005)
        for i in range(n + 1):
            u = i * Ln / n; pz = at(u, H / 2, 0.03)
            box(pz, (0.2, 0.14, H) if c2 == 'x' else (0.14, 0.2, H), 'M_wood', 0.01)                          # studs
            if i < n:
                if i % 2 == 0:   # windows in alternate panels: leaded glass, a mullion, a timber head
                    wc = at(u + Ln / n / 2, 1.95, 0.012)
                    box(wc, ((Ln / n) - 0.5, 0.03, 1.3) if c2 == 'x' else (0.03, (Ln / n) - 0.5, 1.3), 'F_glass', 0.0, tag='glass')
                    for m in (-0.5, 0.0, 0.5):
                        mc = at(u + Ln / n / 2 + m * ((Ln / n) - 0.5) / 1.0 * 0.5, 1.95, 0.04)
                        box(mc, (0.06, 0.06, 1.3) if c2 == 'x' else (0.06, 0.06, 1.3), 'M_wood', 0.0)
                    hc = at(u + Ln / n / 2, 2.68, 0.04); box(hc, ((Ln / n) - 0.3, 0.16, 0.14) if c2 == 'x' else (0.16, (Ln / n) - 0.3, 0.14), 'M_wood', 0.005)
                else:            # a pair of curved braces
                    for sgn in (0, 1):
                        p0 = at(u + (Ln / n if sgn else 0), 1.0, 0.035); p1 = at(u + Ln / n / 2, H - 0.25, 0.035)
                        pipe(p0, p1, 0.07, 'M_wood', seg=4)
    for (cx, cy) in [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]:                                                  # the jetty's corner brackets
        pipe((cx * 0.97, cy * 0.94, G - 1.1), (cx, cy, G), 0.1, 'M_wood', seg=5)
    for i in range(NB + 1):
        x = -L / 2 + i * L / NB
        for y, s2 in ((y0, -1), (y1, 1)): pipe((x, s2 * Wd / 2, G - 0.9), (x, y + s2 * 0.0, G - 0.05), 0.08, 'M_wood', seg=4)
    return x0, x1, y0, y1, z0 + H

def roof(x0, x1, y0, y1, zt):
    o = 0.55; ex0, ex1, ey0, ey1 = x0 - o, x1 + o, y0 - o, y1 + o; pitch = math.radians(52); hr = (ey1 - ey0) / 2 * math.tan(pitch); rx = (ey1 - ey0) / 2
    zr = zt + hr - 0.3
    bm = bmesh.new(); v = [bm.verts.new(p) for p in [(ex0, ey0, zt - 0.3), (ex1, ey0, zt - 0.3), (ex1, ey1, zt - 0.3), (ex0, ey1, zt - 0.3), (ex0 + rx, 0, zr), (ex1 - rx, 0, zr)]]
    for f in [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4)]: bm.faces.new([v[i] for i in f])
    bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=3, use_grid_fill=True); add_bm(bm, 'M_tile', 'roof')
    bm = bmesh.new(); v = [bm.verts.new(p) for p in [(ex0, ey0, zt - 0.5), (ex1, ey0, zt - 0.5), (ex1, ey1, zt - 0.5), (ex0, ey1, zt - 0.5)]]; bm.faces.new(list(reversed(v))); add_bm(bm, 'M_wood', '')   # the eaves' soffit
    pipe((ex0 + rx, 0, zr + 0.06), (ex1 - rx, 0, zr + 0.06), 0.12, 'M_tile', seg=6)                                    # ridge tiles
    for (a, b) in [((ex0, ey0), (ex0 + rx, 0)), ((ex1, ey0), (ex1 - rx, 0)), ((ex1, ey1), (ex1 - rx, 0)), ((ex0, ey1), (ex0 + rx, 0))]:
        pipe((a[0], a[1], zt - 0.24), (b[0], b[1], zr + 0.04), 0.1, 'M_tile', seg=6)                                   # hips
    for sy in (-1, 1):   # dormers, two each way
        for dxm in (-5.5, 5.5):
            d = 1.6; fy2 = sy * ((ey1 - ey0) / 2 - 1.4); zb = zt - 0.3 + 1.4 * math.tan(pitch) - 0.2
            box((dxm, fy2, zb + 0.75), (d, 0.2, 1.5), 'M_wood', 0.01); box((dxm, fy2 + sy * 0.0, zb + 0.75), (d - 0.4, 0.22, 1.0), 'F_glass', 0.0, tag='glass')
            for sx2 in (-1, 1): box((dxm + sx2 * d / 2, fy2 - sy * 0.9, zb + 0.75), (0.15, 1.8, 1.5), 'M_plaster', 0.0)
            bm = bmesh.new(); h2 = 0.9
            v = [bm.verts.new(p) for p in [(dxm - d / 2 - 0.15, fy2 + sy * 0.15, zb + 1.5), (dxm + d / 2 + 0.15, fy2 + sy * 0.15, zb + 1.5), (dxm, fy2 + sy * 0.15, zb + 1.5 + h2),
                                           (dxm - d / 2 - 0.15, fy2 - sy * 1.9, zb + 1.5), (dxm + d / 2 + 0.15, fy2 - sy * 1.9, zb + 1.5), (dxm, fy2 - sy * 1.9, zb + 1.5 + h2)]]
            for f in [(0, 3, 5, 2), (1, 2, 5, 4), (0, 1, 2)]: bm.faces.new([v[i] for i in f])
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, 'M_tile', 'roof')
    # the clock lantern on the ridge: a timber stage with clock faces, an open belfry, a lead spire and a vane
    cz = zr - 0.2; s = 1.5
    box((0, 0, cz + 0.9), (2 * s, 2 * s, 1.8), 'M_plaster', 0.0)
    for (a2, c2) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]: box((a2 * s, c2 * s, cz + 0.9), (0.2, 0.2, 1.8), 'M_wood', 0.01)
    for (px, py, nx, ny) in [(0, -s, 0, -1), (0, s, 0, 1), (s, 0, 1, 0), (-s, 0, -1, 0)]:
        cyl((px + nx * 0.03, py + ny * 0.03, cz + 1.0), 0.55, 0.55, 0.06, 'M_ashlar', seg=20, axis='Y' if ny else 'X')
        cyl((px + nx * 0.07, py + ny * 0.07, cz + 1.0), 0.47, 0.47, 0.04, 'F_iron', seg=20, axis='Y' if ny else 'X')
        for k in range(12): a3 = k / 12 * 2 * math.pi; box((px + nx * 0.1 + (0 if nx else math.cos(a3) * 0.4), py + ny * 0.1 + (math.cos(a3) * 0.4 if nx else 0), cz + 1.0 + math.sin(a3) * 0.4), (0.05, 0.05, 0.05), 'M_ashlar', 0.0)
        box((px + nx * 0.1, py + ny * 0.1, cz + 1.12), (0.04 if ny else 0.03, 0.03 if ny else 0.04, 0.3), 'M_ashlar', 0.0)
    box((0, 0, cz + 1.9), (2 * s + 0.3, 2 * s + 0.3, 0.2), 'M_wood', 0.01)
    for (a2, c2) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]: box((a2 * (s - 0.25), c2 * (s - 0.25), cz + 2.6), (0.18, 0.18, 1.3), 'M_wood', 0.01)
    box((0, 0, cz + 3.3), (2 * s + 0.2, 2 * s + 0.2, 0.18), 'M_wood', 0.01)
    bm = bmesh.new(); b = [bm.verts.new((a2 * (s + 0.05), c2 * (s + 0.05), cz + 3.38)) for a2, c2 in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]; t = bm.verts.new((0, 0, cz + 6.2))
    bm.faces.new(list(reversed(b)))
    for i in range(4): bm.faces.new([b[i], b[(i + 1) % 4], t])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, 'F_iron', 'roof')
    cyl((0, 0, cz + 2.4), 0.35, 0.35, 0.55, 'F_copper', seg=12)                                                      # the bell
    pipe((0, 0, cz + 6.2), (0, 0, cz + 7.0), 0.03, 'F_iron', seg=6); box((0.25, 0, cz + 6.85), (0.6, 0.02, 0.2), 'F_copper', 0.0)
    return cz

piers_and_arches(); x0, x1, y0, y1, zt = timber_hall(); roof(x0, x1, y0, y1, zt)
NAME = 'MarketHall'

me = bpy.data.meshes.new(NAME); obj = bpy.data.objects.new(NAME, me); scene.collection.objects.link(obj)
for nm in MAT_LIST:
    if nm.startswith('M_'):
        g = globals(); old = g['TEX']; g['TEX'] = MTEX; mm = make_material(nm); g['TEX'] = old
        for nd in mm.node_tree.nodes:
            if nd.type == 'HUE_SAT': nd.inputs['Saturation'].default_value = SAT[nm]
    else: mm = make_material(nm)
    mm.use_backface_culling = nm not in ('F_iron', 'M_wood'); me.materials.append(mm)
bm = bmesh.new()
for vs, fs, mat, tag in PARTS:
    base = [bm.verts.new(p) for p in vs]
    for f in fs:
        try: face = bm.faces.new([base[i] for i in f])
        except ValueError: continue
        face.material_index = MAT_LIST.index(mat)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
uvl = bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    tile = MATS[MAT_LIST[f.material_index]][1]; n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
    roofy = MAT_LIST[f.material_index] == 'M_tile' and abs(n.z) < 0.95
    for l in f.loops:
        p = l.vert.co
        if roofy:   # tiles run down the slope
            if abs(n.x) > abs(n.y): u, v = p.y, (p.z / max(0.2, abs(n.x))) * 0.62
            else: u, v = p.x, (p.z / max(0.2, abs(n.y))) * 0.62
        else: u, v = ((p.y, p.z) if ax == 0 else (p.x, p.z) if ax == 1 else (p.x, p.y))
        l[uvl].uv = (u / tile, v / tile)
bm.to_mesh(me); bm.free()
col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); me.color_attributes.active_color = col
for d in col.data: d.color = (1, 1, 1, 1)
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 64; scene.render.bake.target = 'VERTEX_COLORS'; scene.world = bpy.data.worlds.new('w')
ground = bpy.data.objects.new('ground', bpy.data.meshes.new('g')); scene.collection.objects.link(ground)
gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=1, y_segments=1, size=40); gb.to_mesh(ground.data); gb.free()
bpy.context.view_layer.objects.active = obj; obj.select_set(True); bpy.ops.object.bake(type='AO')
for i, v in enumerate(me.vertices):
    ao = 0.4 + 0.6 * col.data[i].color[0]; grime = max(0.0, 0.18 - v.co.z * 0.06)   # a little grime at the foot of the piers
    k = ao * (1 - grime); col.data[i].color = (k, k * 0.985, k * 0.96, 1)
bpy.data.objects.remove(ground)
print('%s: %d verts, %d tris' % (NAME, len(me.vertices), sum(len(p.vertices) - 2 for p in me.polygons)))
lod = obj.copy(); lod.data = obj.data.copy(); lod.name = NAME + '_LOD1'; scene.collection.objects.link(lod)
dm = lod.modifiers.new('dec', 'DECIMATE'); dm.ratio = 0.2
bpy.context.view_layer.objects.active = lod; bpy.ops.object.select_all(action='DESELECT'); lod.select_set(True); bpy.ops.object.modifier_apply(modifier='dec')
print('LOD1: %d tris' % sum(len(p.vertices) - 2 for p in lod.data.polygons))
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); lod.select_set(True)
kw = dict(filepath=OUT, use_selection=True, export_format='GLB', export_image_format='NONE', export_materials='EXPORT', export_yup=True)
try: bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError: bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('EXPORTED', OUT)
if RENDER:
    lod.hide_render = True
    world = scene.world; world.use_nodes = True; nt = world.node_tree; sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(28)
    nt.links.new(sky.outputs['Color'], nt.nodes['Background'].inputs['Color']); nt.nodes['Background'].inputs['Strength'].default_value = 0.35
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 2.4; sun.rotation_euler = (math.radians(55), 0, math.radians(-40)); scene.collection.objects.link(sun)
    g = bpy.data.objects.new('sq', bpy.data.meshes.new('sq')); scene.collection.objects.link(g)
    gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=2, y_segments=2, size=60); gb.to_mesh(g.data); gb.free()
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam; cam.data.lens = 26
    cp = Vector(tuple(float(v) for v in os.environ.get('CAM', '17,-24,7').split(','))); tgt = Vector((0, 0, 5.5)); cam.location = cp; cam.rotation_euler = (tgt - cp).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1280, 800; scene.cycles.samples = 48; scene.view_settings.view_transform = 'AgX'; scene.render.filepath = RENDER
    bpy.ops.render.render(write_still=True); print('RENDERED', RENDER)
