# Ferrin forge-house: the hero building of the Ferrin Quarter kit.
#
# Real geometry (thick walls with true reveals, bevelled dressed stone, a voussoir arch, a lived-in forge bay), CC0 PBR
# materials from Poly Haven (game/tex/ferrin), and weathering baked into vertex colours: ambient occlusion, soot where smoke
# and heat would put it, rust streaks under the ironwork. Exports a GLB (materials by name, no images: the game loads the
# shared textures) and, with RENDER set, a Cycles beauty shot.
#
#   python3.11 ferrin_forge.py -- out.glb          (RENDER=shot.png TEX=<the Poly Haven 1K maps: godot/assets/buildings/ferrin/tex, plus
#   rock_wall_05_diff.jpg and medieval_blocks_03_diff.jpg from polyhaven.com for the renders>)
import bpy, bmesh, math, random, sys, os
from mathutils import Vector, Matrix

OUT = sys.argv[-1]
RENDER = os.environ.get('RENDER')
TEX = os.path.abspath(os.environ.get('TEX', os.path.join(os.path.dirname(__file__), '..', '..', 'game', 'tex', 'ferrin')))
random.seed(11)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------------------------------------------------------------- materials
# name: (texture set, metres per texture repeat, tint, metallic, roughness scale)
MATS = {
    'F_stone':  ('rock_wall_05',       2.2, (0.15, 0.155, 0.17), 0.0, 1.0),   # the body: dark coursed rubble, basalt from home
    'F_ashlar': ('medieval_blocks_03', 1.6, (0.25, 0.255, 0.27), 0.0, 1.0),   # dressed stone: plinth, quoins, arch, sills, coping
    'F_brick':  ('castle_brick_07',    1.4, (0.62, 0.48, 0.42), 0.0, 1.0),   # the stack and the hearth
    'F_iron':   ('metal_plate_02',     1.6, (0.22, 0.22, 0.24), 0.6, 0.85),  # roof plates, doors, anchors, hood
    'F_rust':   ('rusty_metal_02',     1.0, (0.30, 0.24, 0.20), 0.45, 1.0),  # shutters, straps, sign
    'F_wood':   ('dark_wooden_planks', 1.4, (0.70, 0.62, 0.55), 0.0, 1.0),   # beams, stump, barrel, racks
    'F_copper': ('rusty_metal_02',     0.8, (0.78, 0.46, 0.30), 0.6, 0.7),   # pipes
    'F_glow':   (None, 1, (1.0, 0.22, 0.03), 0.0, 1.0),                      # coals and the lantern
    'F_glass':  (None, 1, (0.05, 0.06, 0.07), 0.0, 0.15),                    # dark window glass
}

def make_material(name):
    tex, tile, tint, metal, rs = MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
    bsdf = N['Principled BSDF']; bsdf.inputs['Metallic'].default_value = metal
    vc = N.new('ShaderNodeVertexColor'); vc.layer_name = 'Col'
    if tex:
        def img(kind, non_color=False):
            n = N.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(TEX, f'{tex}_{kind}.jpg'))
            if non_color: n.image.colorspace_settings.name = 'Non-Color'
            return n
        d = img('diff'); r = img('rough', True); nm = img('nor', True)
        mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 1.0
        hsv = N.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = 0.3 if name in ('F_stone', 'F_ashlar') else 1.0
        L.new(d.outputs['Color'], hsv.inputs['Color']); L.new(hsv.outputs['Color'], mix.inputs[6]); L.new(vc.outputs['Color'], mix.inputs[7])
        tn = N.new('ShaderNodeMix'); tn.data_type = 'RGBA'; tn.blend_type = 'MULTIPLY'; tn.inputs['Factor'].default_value = 1.0
        tn.inputs[7].default_value = (*tint, 1)
        L.new(mix.outputs[2], tn.inputs[6]); L.new(tn.outputs[2], bsdf.inputs['Base Color'])
        mr = N.new('ShaderNodeMath'); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = rs
        L.new(r.outputs['Color'], mr.inputs[0]); L.new(mr.outputs[0], bsdf.inputs['Roughness'])
        nmap = N.new('ShaderNodeNormalMap'); L.new(nm.outputs['Color'], nmap.inputs['Color']); L.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
    else:
        tn = N.new('ShaderNodeMix'); tn.data_type = 'RGBA'; tn.blend_type = 'MULTIPLY'; tn.inputs['Factor'].default_value = 1.0
        tn.inputs[7].default_value = (*tint, 1); L.new(vc.outputs['Color'], tn.inputs[6]); L.new(tn.outputs[2], bsdf.inputs['Base Color'])
        bsdf.inputs['Roughness'].default_value = rs
        if name == 'F_glow':
            bsdf.inputs['Emission Color'].default_value = (*tint, 1); bsdf.inputs['Emission Strength'].default_value = 2.2
    return m

MAT_LIST = list(MATS.keys())

# ---------------------------------------------------------------- geometry
# Everything is gathered as (verts, faces, material, tag) and built into one mesh at the end. Tags drive weathering.
PARTS = []

def add_bm(bm, mat, tag=''):
    bm.verts.ensure_lookup_table()
    vs = [v.co.copy() for v in bm.verts]; idx = {v: i for i, v in enumerate(bm.verts)}
    fs = [[idx[v] for v in f.verts] for f in bm.faces]
    PARTS.append((vs, fs, mat, tag)); bm.free()

def bevel_all(bm, off):
    if off > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=off, segments=1, affect='EDGES', clamp_overlap=True)

def box(c, s, mat, bev=0.02, rz=0.0, tag='', rx=0.0):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(s), verts=bm.verts)
    bevel_all(bm, min(bev, min(s) * 0.3))
    M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rz, 4, 'Z') @ Matrix.Rotation(rx, 4, 'X')
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts); add_bm(bm, mat, tag)

def cyl(c, r1, r2, h, mat, seg=12, axis='Z', bev=0.0, tag=''):
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=h)
    bevel_all(bm, bev)
    R = {'Z': Matrix.Identity(4), 'X': Matrix.Rotation(math.pi / 2, 4, 'Y'), 'Y': Matrix.Rotation(math.pi / 2, 4, 'X')}[axis]
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(c)) @ R, verts=bm.verts); add_bm(bm, mat, tag)

def prism(pts_front, depth, n, mat, bev=0.02, tag=''):
    """A convex outline (in a plane) pushed back along -n by depth: wedges, hips, caps."""
    bm = bmesh.new(); f = [bm.verts.new(p) for p in pts_front]; b = [bm.verts.new(Vector(p) - Vector(n) * depth) for p in pts_front]
    bm.faces.new(f); bm.faces.new(list(reversed(b)))
    k = len(f)
    for i in range(k):
        bm.faces.new([f[i], b[i], b[(i + 1) % k], f[(i + 1) % k]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bevel_all(bm, bev); add_bm(bm, mat, tag)

def pipe(a, b, r, mat, seg=10, tag=''):
    a, b = Vector(a), Vector(b); d = b - a; L = d.length
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=L)
    q = Vector((0, 0, 1)).rotation_difference(d.normalized())
    bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4(), verts=bm.verts); add_bm(bm, mat, tag)

def rivet(c, normal, mat='F_iron'):
    n = Vector(normal); cyl(Vector(c) + n * 0.012, 0.03, 0.022, 0.024, mat, seg=6, axis={(0, -1, 0): 'Y', (0, 1, 0): 'Y', (1, 0, 0): 'X', (-1, 0, 0): 'X'}.get(tuple(round(x) for x in n), 'Z'))

# ---- a wall panel with real openings: a fine grid on both faces, true reveals round every opening
def wall_panel(origin, U, N, length, height, thick, openings, mat='F_stone', cell=0.8, tag='wall'):
    """origin: outer bottom-left corner; U: along the wall; N: outward normal. Openings: dicts u0,u1,z0,z1 and optional arch rise."""
    O, U, N, Z = Vector(origin), Vector(U), Vector(N), Vector((0, 0, 1))
    us, zs = {0.0, length}, {0.0, height}
    for k in range(1, int(length / cell)): us.add(round(k * cell, 3))
    for k in range(1, int(height / cell)): zs.add(round(k * cell, 3))
    for o in openings:
        us |= {o['u0'], o['u1']}; zs |= {o['z0'], o['z1']}
        if o.get('rise'):   # a finer grid round an arch, so the voussoirs cover the cut cleanly
            for k in range(int((o['u1'] - o['u0'] + 1.2) / 0.18)): us.add(round(o['u0'] - 0.6 + k * 0.18, 3))
            for k in range(int((o['rise'] + 0.9) / 0.18)): zs.add(round(o['z1'] + k * 0.18, 3))
    us = sorted(u for u in us if 0 <= u <= length); zs = sorted(z for z in zs if 0 <= z <= height)
    def hole(uc, zc):
        for o in openings:
            if o['u0'] < uc < o['u1'] and o['z0'] < zc < o['z1']: return True
            if o.get('rise'):
                c = (o['u1'] - o['u0']) / 2; h = o['rise']; R = (c * c + h * h) / (2 * h); cu = o['u0'] + c; cz = o['z1'] + h - R
                if zc >= o['z1'] and math.hypot(uc - cu, zc - cz) < R + 0.2: return True
        return False
    nu, nz = len(us) - 1, len(zs) - 1
    keep = [[not hole((us[i] + us[i + 1]) / 2, (zs[j] + zs[j + 1]) / 2) for j in range(nz)] for i in range(nu)]
    vs, fs = [], []
    def P(u, z, d): return O + U * u + Z * z - N * d
    vid = {}
    def v(u, z, d):
        key = (round(u, 4), round(z, 4), d)
        if key not in vid: vid[key] = len(vs); vs.append(P(u, z, d))
        return vid[key]
    for i in range(nu):
        for j in range(nz):
            if not keep[i][j]: continue
            u0, u1, z0, z1 = us[i], us[i + 1], zs[j], zs[j + 1]
            fs.append([v(u0, z0, 0), v(u1, z0, 0), v(u1, z1, 0), v(u0, z1, 0)])                  # outer face
            fs.append([v(u0, z1, 1), v(u1, z1, 1), v(u1, z0, 1), v(u0, z0, 1)])                  # inner face
            # reveals where a kept cell meets a hole
            if i > 0 and not keep[i - 1][j]: fs.append([v(u0, z0, 0), v(u0, z1, 0), v(u0, z1, 1), v(u0, z0, 1)])
            if i < nu - 1 and not keep[i + 1][j]: fs.append([v(u1, z0, 1), v(u1, z1, 1), v(u1, z1, 0), v(u1, z0, 0)])
            if j > 0 and not keep[i][j - 1]: fs.append([v(u0, z0, 1), v(u1, z0, 1), v(u1, z0, 0), v(u0, z0, 0)])
            if j < nz - 1 and not keep[i][j + 1]: fs.append([v(u0, z1, 0), v(u1, z1, 0), v(u1, z1, 1), v(u0, z1, 1)])
    # depth index 1 means "thick" inward
    vs = [p if True else p for p in vs]
    real = []
    for k, p in enumerate(vs): real.append(p)
    # replace unit depth by the real thickness
    out = []
    for (u, z, d), i in sorted(vid.items(), key=lambda t: t[1]): out.append(P(u, z, d * thick))
    PARTS.append((out, fs, mat, tag))

# ---------------------------------------------------------------- the forge-house
W, D, T = 10.6, 11.0, 0.6          # footprint and wall thickness
H1, H2, PAR = 4.3, 2.9, 0.8       # ground storey (forge height), upper storey, parapet
HT = H1 + H2 + PAR
fy = -D / 2                         # the front face (toward the street) is at -y
BAY = dict(u0=1.0, u1=5.6, z0=0.0, z1=2.45, rise=0.8)   # the forge bay, measured along the front from its left corner
DOOR = dict(u0=7.3, u1=8.45, z0=0.0, z1=2.25)
WIN_U = [1.6, 3.6, 7.0, 9.0]; WIN = (0.66, 0.95, H1 + 0.8)  # upper windows: centres, width, height, sill height

front_open = [BAY, DOOR] + [dict(u0=c - WIN[0] / 2, u1=c + WIN[0] / 2, z0=WIN[2], z1=WIN[2] + WIN[1]) for c in WIN_U]
wall_panel((-W / 2, fy, 0), (1, 0, 0), (0, -1, 0), W, HT, T, front_open)
side_open = lambda: [dict(u0=4.6, u1=5.4, z0=WIN[2], z1=WIN[2] + WIN[1]), dict(u0=4.7, u1=5.3, z0=1.6, z1=2.5)]
wall_panel((W / 2, fy, 0), (0, 1, 0), (1, 0, 0), D, HT, T, side_open())                                   # right (full depth: the corners close)
wall_panel((-W / 2, D / 2, 0), (0, -1, 0), (-1, 0, 0), D, HT, T, side_open())                              # left
wall_panel((W / 2, D / 2, 0), (-1, 0, 0), (0, 1, 0), W, HT, T, [dict(u0=2.0, u1=2.8, z0=WIN[2], z1=WIN[2] + WIN[1]), dict(u0=5.9, u1=7.0, z0=0, z1=2.2)])   # back

FX = lambda u: -W / 2 + u        # front u -> world x

# plinth: a course of dressed blocks, broken by the bay and the door
def course(x0, x1, y, z0, h, depth_out, mat='F_ashlar', ln=(0.7, 1.3), axis='x', tag='plinth'):
    x = x0
    while x < x1 - 0.05:
        L = min(random.uniform(*ln), x1 - x)
        if axis == 'x': box(((x + x + L) / 2, y - depth_out / 2 + 0.05, z0 + h / 2), (L - 0.012, depth_out + 0.1, h), mat, 0.035, tag=tag)
        else: box((y + depth_out / 2 - 0.05, (x + x + L) / 2, z0 + h / 2), (depth_out + 0.1, L - 0.012, h), mat, 0.035, tag=tag)
        x += L
def batter(x0, x1, face, n, along_x, hb=1.25, out=0.42):
    # a sloping skirt of dressed stone: out at the ground, flush with the wall at hb; one sloped block per metre or so
    x = x0
    while x < x1 - 0.05:
        L = min(random.uniform(0.8, 1.3), x1 - x)
        if along_x:
            pts = [Vector((x + 0.006, face, 0)), Vector((x + L - 0.006, face, 0)), Vector((x + L - 0.006, face, hb)), Vector((x + 0.006, face, hb))]
            sl = lambda p: Vector((p.x, p.y + n * out * (1 - p.z / hb), p.z))
            bm = bmesh.new(); f = [bm.verts.new(sl(p)) for p in pts]; b = [bm.verts.new(Vector((p.x, face - n * 0.15, p.z))) for p in pts]
        else:
            pts = [Vector((face, x + 0.006, 0)), Vector((face, x + L - 0.006, 0)), Vector((face, x + L - 0.006, hb)), Vector((face, x + 0.006, hb))]
            sl = lambda p: Vector((p.x + n * out * (1 - p.z / hb), p.y, p.z))
            bm = bmesh.new(); f = [bm.verts.new(sl(p)) for p in pts]; b = [bm.verts.new(Vector((face - n * 0.15, p.y, p.z))) for p in pts]
        bm.faces.new(f); bm.faces.new(list(reversed(b)))
        for k in range(4): bm.faces.new([f[k], b[k], b[(k + 1) % 4], f[(k + 1) % 4]])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bevel_all(bm, 0.03); add_bm(bm, 'F_ashlar', 'plinth'); x += L
for (a, b) in [(-W / 2 - 0.42, FX(BAY['u0']) - 0.62), (FX(BAY['u1']) + 0.62, FX(DOOR['u0']) - 0.32), (FX(DOOR['u1']) + 0.32, W / 2 + 0.42)]:
    if b - a > 1.4: batter(a, b, fy, -1, True)
batter(-D / 2, D / 2 + 0.42, W / 2, 1, False); batter(-D / 2, D / 2 + 0.42, -W / 2, -1, False); batter(-W / 2, W / 2, D / 2, 1, True)

# quoins: long and short dressed stones, turning each corner in turn
for cx, cy, sx, sy in [(-W / 2, fy, 1, 1), (W / 2, fy, -1, 1), (-W / 2, D / 2, 1, -1), (W / 2, D / 2, -1, -1)]:
    z = 0.6; k = 0
    while z < H1 + H2 - 0.1:
        h = 0.42; Lf, Ls = (0.95, 0.5) if k % 2 == 0 else (0.5, 0.95)
        box((cx + sx * (Lf / 2 - 0.04), cy - sy * 0.03 + sy * 0.0, z + h / 2), (Lf, 0.14, h - 0.015), 'F_ashlar', 0.035, tag='quoin')
        box((cx - sx * 0.03, cy + sy * (Ls / 2 - 0.04), z + h / 2), (0.14, Ls, h - 0.015), 'F_ashlar', 0.035, tag='quoin')
        z += h; k += 1


# the string course between the storeys, with a weathered drip
for (c, s) in [((0, fy - 0.07, H1), (W + 0.3, 0.26, 0.3)), ((0, D / 2 + 0.07, H1), (W + 0.3, 0.26, 0.3)),
               ((W / 2 + 0.07, 0, H1), (0.26, D + 0.3, 0.3)), ((-W / 2 - 0.07, 0, H1), (0.26, D + 0.3, 0.3))]:
    box(c, s, 'F_ashlar', 0.05, tag='course')

# a corbel table under the parapet: stepped stone brackets and an iron cornice plate, the parapet's weight shown
def corbels(a0, a1, face, n, along_x):
    k = a0 + 0.45
    while k < a1 - 0.3:
        for step, (dz, out) in enumerate([(0.0, 0.16), (0.2, 0.3)]):
            c = (k, face + n * out / 2, H1 + H2 - 0.25 + dz) if along_x else (face + n * out / 2, k, H1 + H2 - 0.25 + dz)
            s3 = (0.36, out, 0.2) if along_x else (out, 0.36, 0.2)
            box(c, s3, 'F_ashlar', 0.02, tag='corbel')
        k += 0.85
    c = ((a0 + a1) / 2, face + n * 0.2, H1 + H2 + 0.08) if along_x else (face + n * 0.2, (a0 + a1) / 2, H1 + H2 + 0.08)
    s3 = (a1 - a0 + 0.8, 0.42, 0.12) if along_x else (0.42, a1 - a0 + 0.8, 0.12)
    box(c, s3, 'F_iron', 0.01, tag='cornice')
corbels(-W / 2, W / 2, fy, -1, True); corbels(-W / 2, W / 2, D / 2, 1, True); corbels(-D / 2, D / 2, W / 2, 1, False); corbels(-D / 2, D / 2, -W / 2, -1, False)

cgx, cgz, cr = FX(5.3), H1 + 1.25, 0.5   # Ostrak's cog: the cast tie-plate of the floor beams, between the middle windows, clear of every course
cyl((cgx, fy - 0.07, cgz), cr, cr, 0.1, 'F_iron', seg=28, axis='Y', bev=0.015, tag='cog')
for t in range(14):   # teeth, each a trapezoid turned to its own angle on the rim
    a = t / 14 * math.pi * 2; h0, h1 = 0.14, 0.09
    P = lambda r, s2: Vector((cgx + math.cos(a) * r - math.sin(a) * s2, fy - 0.025, cgz + math.sin(a) * r + math.cos(a) * s2))
    prism([P(cr - 0.04, -h0), P(cr - 0.04, h0), P(cr + 0.17, h1), P(cr + 0.17, -h1)], 0.09, (0, -1, 0), 'F_iron', 0.01, tag='cog')
cyl((cgx, fy - 0.13, cgz), 0.2, 0.2, 0.08, 'F_iron', seg=16, axis='Y', bev=0.012)
for t in range(5):
    a = t / 5 * math.pi * 2 + math.pi / 2; pipe((cgx + math.cos(a) * 0.19, fy - 0.12, cgz + math.sin(a) * 0.19), (cgx + math.cos(a) * 0.44, fy - 0.12, cgz + math.sin(a) * 0.44), 0.04, 'F_iron', seg=6)
cyl((cgx, fy - 0.19, cgz), 0.09, 0.09, 0.1, 'F_iron', seg=6, axis='Y')                            # the tie-rod's nut
cyl((cgx, fy - 0.25, cgz), 0.035, 0.035, 0.06, 'F_rust', seg=6, axis='Y')

# coping on the parapet, on each wall's centre line, overhanging both faces
def coping(a0, a1, fixed, along_x):
    x = a0
    while x < a1 - 0.05:
        L = min(random.uniform(0.9, 1.2), a1 - x)
        if along_x: box(((2 * x + L) / 2, fixed, HT + 0.09), (L - 0.01, T + 0.18, 0.18), 'F_ashlar', 0.04, tag='coping')
        else: box((fixed, (2 * x + L) / 2, HT + 0.09), (T + 0.18, L - 0.01, 0.18), 'F_ashlar', 0.04, tag='coping')
        x += L
coping(-W / 2, W / 2, fy + T / 2, True); coping(-W / 2, W / 2, D / 2 - T / 2, True)
coping(fy + T, D / 2 - T, W / 2 - T / 2, False); coping(fy + T, D / 2 - T, -W / 2 + T / 2, False)

# ---- the forge bay: a segmental arch of voussoirs and a keystone, dressed jambs, an iron-bound timber lintel inside
c = (BAY['u1'] - BAY['u0']) / 2; h = BAY['rise']; R = (c * c + h * h) / (2 * h); cu = FX(BAY['u0']) + c; cz = BAY['z1'] + h - R
a0 = math.atan2(BAY['z1'] - cz, -c); a1 = math.atan2(BAY['z1'] - cz, c)
NV = 9
for i in range(NV):
    t0 = a0 + (a1 - a0) * i / NV; t1 = a0 + (a1 - a0) * (i + 1) / NV; key = i == NV // 2
    r0, r1 = R, R + (0.85 if key else 0.68) + (0.05 if i % 2 else 0)
    pts = [Vector((cu + math.cos(t) * r, fy - (0.1 if key else 0.06), cz + math.sin(t) * r)) for (t, r) in [(t0 + 0.004, r0), (t1 - 0.004, r0), (t1 - 0.004, r1), (t0 + 0.004, r1)]]
    prism(pts, T + (0.1 if key else 0.06) - 0.02, (0, -1, 0), 'F_ashlar', 0.025, tag='arch')
for side in (0, 1):   # jambs: alternating long and short dressed blocks, beside the opening
    z = 0.6; k = 0
    while z < BAY['z1'] - 0.05:
        hh = min(0.42, BAY['z1'] - z); Lb = 0.62 if k % 2 == 0 else 0.4
        x = FX(BAY['u0']) - Lb / 2 if side == 0 else FX(BAY['u1']) + Lb / 2
        box((x, fy - 0.035 + T / 2, z + hh / 2), (Lb, T + 0.07, hh - 0.015), 'F_ashlar', 0.03, tag='jamb')
        z += hh; k += 1

CD, slope = 2.6, math.radians(14)                      # deep enough to shoe a horse or quench a bar out of the rain
cz0 = H1 + 0.3; czf = cz0 - CD * math.tan(slope); cw = FX(BAY['u1']) - FX(BAY['u0']) + 1.2; cl, cr2 = cu - cw / 2, cu + cw / 2
Z = lambda y: cz0 + (y - fy) * math.tan(slope)          # the sheet's height at a distance out from the wall (y < fy)
box((cu, fy - 0.06, cz0 + 0.06), (cw + 0.2, 0.12, 0.22), 'F_iron', 0.01, tag='canopy')                       # the wall plate, bolted on
for k in range(10): rivet((cl + 0.1 + k * (cw) / 9, fy - 0.12, cz0 + 0.08), (0, -1, 0))
prism([Vector((cl, fy, cz0)), Vector((cr2, fy, cz0)), Vector((cr2, fy - CD, czf)), Vector((cl, fy - CD, czf))], 0.05, (0, 0, 1), 'F_iron', 0.008, tag='canopy')   # the sheet
for k in range(int(cw / 0.6) + 1):                                                                            # its standing seams
    x = cl + 0.05 + k * (cw - 0.1) / int(cw / 0.6); pipe((x, fy - 0.02, cz0 + 0.03), (x, fy - CD + 0.02, czf + 0.03), 0.016, 'F_iron', seg=4)
box((cu, fy - CD - 0.02, czf - 0.06), (cw + 0.04, 0.05, 0.16), 'F_iron', 0.006, tag='canopy')                # front fascia
for x in (cl, cr2): prism([Vector((x, fy, cz0 - 0.16)), Vector((x, fy - CD, czf - 0.16)), Vector((x, fy - CD, czf + 0.02)), Vector((x, fy, cz0 + 0.02))], 0.05, (1 if x > cu else -1, 0, 0), 'F_iron', 0.004)
for k in range(12): rivet((cl + 0.15 + k * (cw - 0.3) / 11, fy - CD - 0.05, czf - 0.06), (0, -1, 0))
for y in (fy - 0.9, fy - 1.8): box((cu, y, Z(y) - 0.09), (cw - 0.1, 0.1, 0.12), 'F_wood', 0.01)            # purlins under the sheet
for x in (cl + 0.12, cu, cr2 - 0.12): prism([Vector((x - 0.05, fy, cz0 - 0.02)), Vector((x + 0.05, fy, cz0 - 0.02)), Vector((x + 0.05, fy - CD + 0.05, czf - 0.02)), Vector((x - 0.05, fy - CD + 0.05, czf - 0.02))], 0.16, (0, 0, 1), 'F_wood', 0.01)   # rafters
for x in (cl + 0.2, cr2 - 0.2):                                                                              # knee braces at each end, from the wall
    pipe((x, fy - 0.05, cz0 - 1.35), (x, fy - 1.55, Z(fy - 1.55) - 0.05), 0.045, 'F_iron', seg=6)
    box((x, fy - 0.06, cz0 - 1.35), (0.18, 0.12, 0.3), 'F_iron', 0.01)
for x in (cl + 0.3, cr2 - 0.3):                                                                              # tie-rods from anchor plates under the corbels
    pipe((x, fy - 0.06, H1 + H2 - 0.45), (x, fy - CD + 0.08, czf + 0.06), 0.022, 'F_iron', seg=5)
    box((x, fy - 0.05, H1 + H2 - 0.45), (0.2, 0.1, 0.2), 'F_iron', 0.01); cyl((x, fy - CD + 0.08, czf + 0.09), 0.05, 0.05, 0.06, 'F_iron', seg=6)
pipe((cl - 0.05, fy - CD - 0.08, czf - 0.12), (cr2 + 0.05, fy - CD - 0.08, czf - 0.04), 0.075, 'F_iron', seg=8)   # the gutter, falling to the left end
pipe((cl - 0.07, fy - CD - 0.08, czf - 0.12), (cl - 0.07, fy - 0.2, Z(fy - 0.2) - 0.25), 0.05, 'F_iron', seg=6)   # its pipe back to the wall
pipe((cl - 0.07, fy - 0.2, Z(fy - 0.2) - 0.25), (cl - 0.07, fy - 0.2, 0.35), 0.05, 'F_iron', seg=6, tag='downpipe')
pipe((cl - 0.07, fy - 0.2, 0.35), (cl - 0.07, fy - 0.45, 0.12), 0.05, 'F_iron', seg=6)
for z in (1.2, 2.4, 3.4): box((cl - 0.07, fy - 0.1, z), (0.16, 0.22, 0.05), 'F_iron', 0.004)
km = (a0 + a1) / 2; kx = cu + math.cos(km) * (R + 0.45); kz = cz + math.sin(km) * (R + 0.45)
box((kx, fy - 0.14, kz + 0.05), (0.34, 0.06, 0.12), 'F_iron', 0.01); box((kx, fy - 0.14, kz - 0.07), (0.16, 0.06, 0.14), 'F_iron', 0.01)   # Ostrak's anvil on the keystone

# the recess behind the bay: floor, sides, back, a beamed ceiling; the hearth, its hood, the anvil, the barrel, the tools
RD = 2.6; bx0, bx1 = FX(BAY['u0']), FX(BAY['u1']); by0 = fy + T; by1 = by0 + RD; top = BAY['z1'] + BAY['rise'] + 0.1
box(((bx0 + bx1) / 2, (by0 + by1) / 2, 0.05), (bx1 - bx0 + 0.1, RD + 0.2, 0.1), 'F_ashlar', 0.0, tag='inside')
box((bx0 - 0.1, (by0 + by1) / 2, top / 2), (0.2, RD, top), 'F_stone', 0.0, tag='inside')
box((bx1 + 0.1, (by0 + by1) / 2, top / 2), (0.2, RD, top), 'F_stone', 0.0, tag='inside')
box(((bx0 + bx1) / 2, by1 + 0.1, top / 2), (bx1 - bx0 + 0.4, 0.2, top), 'F_stone', 0.0, tag='inside')
box(((bx0 + bx1) / 2, (by0 + by1) / 2, top + 0.1), (bx1 - bx0 + 0.4, RD + 0.4, 0.2), 'F_wood', 0.0, tag='inside')
for k in range(4): box((bx0 + 0.5 + k * (bx1 - bx0 - 1) / 3, (by0 + by1) / 2, top - 0.12), (0.22, RD, 0.26), 'F_wood', 0.02, tag='inside')
hx = (bx0 + bx1) / 2 - 0.3
box((hx, by1 - 0.55, 0.45), (1.9, 0.9, 0.9), 'F_brick', 0.03, tag='hearth')                     # the hearth
box((hx, by1 - 0.55, 0.92), (1.5, 0.6, 0.06), 'F_glow', 0.0, tag='glow')                          # its coals
prism([Vector((hx - 1.05, by1 - 1.1, 1.75)), Vector((hx + 1.05, by1 - 1.1, 1.75)), Vector((hx + 0.35, by1 - 0.45, 2.7)), Vector((hx - 0.35, by1 - 0.45, 2.7))], 0.0001, (0, 0, 1), 'F_iron', 0.0)
for (a, b) in [((hx - 1.05, by1 - 1.1, 1.75), (hx - 1.05, by1 - 0.05, 1.75)), ((hx + 1.05, by1 - 1.1, 1.75), (hx + 1.05, by1 - 0.05, 1.75))]: pipe(a, b, 0.03, 'F_iron')
# the hood as a proper frustum
bm = bmesh.new(); lo = [(hx - 1.05, by1 - 1.15), (hx + 1.05, by1 - 1.15), (hx + 1.05, by1 - 0.05), (hx - 1.05, by1 - 0.05)]; hi = [(hx - 0.35, by1 - 0.65), (hx + 0.35, by1 - 0.65), (hx + 0.35, by1 - 0.2), (hx - 0.35, by1 - 0.2)]
vl = [bm.verts.new((x, y, 1.72)) for x, y in lo]; vh = [bm.verts.new((x, y, 2.75)) for x, y in hi]
for i in range(4): bm.faces.new([vl[i], vl[(i + 1) % 4], vh[(i + 1) % 4], vh[i]])
bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, 'F_iron', 'hood')
cyl((hx, by1 - 0.42, (2.75 + top) / 2), 0.22, 0.22, top - 2.75, 'F_iron', seg=10)
ax = (bx0 + bx1) / 2 + 1.1; ay = by0 + 1.0
cyl((ax, ay, 0.35), 0.32, 0.36, 0.7, 'F_wood', seg=10, bev=0.02)                                  # the stump
box((ax, ay, 0.82), (0.62, 0.24, 0.12), 'F_iron', 0.02); box((ax, ay, 0.92), (0.4, 0.17, 0.1), 'F_iron', 0.02)
prism([Vector((ax + 0.31, ay - 0.1, 0.97)), Vector((ax + 0.62, ay - 0.06, 0.94)), Vector((ax + 0.62, ay + 0.06, 0.94)), Vector((ax + 0.31, ay + 0.1, 0.97))], 0.07, (0, 0, 1), 'F_iron', 0.01)   # the horn
box((ax - 0.2, ay, 0.98), (0.68, 0.26, 0.1), 'F_iron', 0.02)                                       # the face
cyl((bx0 + 0.5, by1 - 0.5, 0.42), 0.36, 0.33, 0.84, 'F_wood', seg=12, bev=0.01)                    # the quench barrel
for zz in (0.15, 0.7): cyl((bx0 + 0.5, by1 - 0.5, zz), 0.37, 0.37, 0.05, 'F_rust', seg=12)
box((bx1 - 0.15, by0 + 1.3, 1.55), (0.06, 1.5, 0.12), 'F_wood', 0.01)                             # the tool rack and its tongs
for k in range(5): box((bx1 - 0.2, by0 + 0.75 + k * 0.28, 1.2), (0.03, 0.04, 0.75), 'F_iron', 0.0)

# ---- the door: an iron-studded leaf in a dressed frame, strap hinges, a ring
dx0, dx1 = FX(DOOR['u0']), FX(DOOR['u1'])
box(((dx0 + dx1) / 2, fy + 0.28, DOOR['z1'] / 2), (dx1 - dx0, 0.08, DOOR['z1']), 'F_wood', 0.01, tag='door')
for z in (0.45, 1.85): box(((dx0 + dx1) / 2 - 0.12, fy + 0.235, z), (0.85, 0.02, 0.09), 'F_iron', 0.005)
for i in range(4):
    for j in range(6): rivet(((dx0 + 0.18 + i * (dx1 - dx0 - 0.36) / 3), fy + 0.235, 0.3 + j * 0.36), (0, -1, 0))
cyl(((dx0 + dx1) / 2 + 0.33, fy + 0.22, 1.1), 0.08, 0.08, 0.02, 'F_iron', seg=10, axis='Y')
box(((dx0 + dx1) / 2, fy - 0.04, DOOR['z1'] + 0.22), (dx1 - dx0 + 0.6, T + 0.08, 0.44), 'F_ashlar', 0.035, tag='lintel')
for x in (dx0 - 0.16, dx1 + 0.16):
    z = 0.6
    while z < DOOR['z1'] - 0.05:
        hh = min(0.42, DOOR['z1'] - z); box((x, fy - 0.035 + T / 2, z + hh / 2), (0.32, T + 0.07, hh - 0.015), 'F_ashlar', 0.03, tag='jamb2'); z += hh
box(((dx0 + dx1) / 2, fy + 0.05, 0.07), (dx1 - dx0 + 0.4, 0.5, 0.14), 'F_ashlar', 0.03)              # the step

# ---- the upper windows: stone sills and lintels, dark glass deep in the reveal, a bar, riveted iron shutters thrown open
def window(x, y, n, along, w, hgt, z0):
    n = Vector(n); a = Vector(along); ax = abs(a.x) > 0.5
    dims = lambda la, ln, lz: (la, ln, lz) if ax else (ln, la, lz)
    base = Vector((x, y, 0))
    box(base + n * 0.06 + Vector((0, 0, z0 - 0.07)), dims(w + 0.32, 0.34, 0.14), 'F_ashlar', 0.025, tag='sill')
    box(base + n * 0.03 + Vector((0, 0, z0 + hgt + 0.16)), dims(w + 0.42, 0.28, 0.32), 'F_ashlar', 0.03, tag='lintel')
    box(base - n * 0.34 + Vector((0, 0, z0 + hgt / 2)), dims(w, 0.03, hgt), 'F_glass', 0.0, tag='glass')
    for k in (-1, 1): box(base - n * 0.3 + a * (k * w / 6) + Vector((0, 0, z0 + hgt / 2)), dims(0.035, 0.035, hgt), 'F_iron', 0.0)
    box(base - n * 0.3 + Vector((0, 0, z0 + hgt * 0.55)), dims(w, 0.035, 0.035), 'F_iron', 0.0)
    th = math.radians(18); lw = w / 2 + 0.04
    for k in (-1, 1):   # the shutters, thrown back almost flat to the wall
        hinge = base + a * (k * (w / 2 + 0.03)) + n * 0.03
        d = a * (k * math.cos(th)) + n * math.sin(th)
        ctr = hinge + d * (lw / 2)
        box((ctr.x, ctr.y, z0 + hgt / 2), (lw, 0.05, hgt + 0.04), 'F_iron', 0.008, rz=math.atan2(d.y, d.x), tag='shutter')
        for zz in (z0 + 0.2, z0 + hgt - 0.2):
            box(((hinge + d * lw * 0.45).x + n.x * 0.03, (hinge + d * lw * 0.45).y + n.y * 0.03, zz), (lw * 0.9, 0.02, 0.07), 'F_iron', 0.004, rz=math.atan2(d.y, d.x))

for c in WIN_U: window(FX(c), fy, (0, -1, 0), (1, 0, 0), WIN[0], WIN[1], WIN[2])
for (x, y, n, a) in [(W / 2, fy + 5.0, (1, 0, 0), (0, 1, 0)), (-W / 2, D / 2 - 5.0, (-1, 0, 0), (0, -1, 0))]:
    window(x, y, n, a, 0.8, WIN[1], WIN[2])
window(W / 2 - 2.4, D / 2, (0, 1, 0), (-1, 0, 0), 0.8, WIN[1], WIN[2])

# ---- iron wall anchors at the floor line: the beams within are tied to the walls
for x in (-W / 2 + 0.75, W / 2 - 0.75):
    box((x, fy - 0.03, H1 + 0.42), (0.7, 0.04, 0.09), 'F_iron', 0.01, rz=0, tag='anchor', rx=0)
    box((x, fy - 0.03, H1 + 0.42), (0.09, 0.04, 0.7), 'F_iron', 0.01, tag='anchor')
    cyl((x, fy - 0.06, H1 + 0.42), 0.08, 0.06, 0.06, 'F_iron', seg=8, axis='Y')

# ---- the roof: low iron plates with raised seams, behind the parapet
rz0 = H1 + H2 + 0.05; rz1 = rz0 + 0.75; ix0, ix1, iy0, iy1 = -W / 2 + T, W / 2 - T, fy + T, D / 2 - T; ry = (iy0 + iy1) / 2
bm = bmesh.new()
v = [bm.verts.new(p) for p in [(ix0, iy0, rz0), (ix1, iy0, rz0), (ix1, iy1, rz0), (ix0, iy1, rz0), (ix0 + 1.2, ry, rz1), (ix1 - 1.2, ry, rz1)]]
for f in [(0, 1, 5, 4), (2, 3, 4, 5), (1, 2, 5), (3, 0, 4)]: bm.faces.new([v[i] for i in f])
bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=3, use_grid_fill=True)
add_bm(bm, 'F_iron', 'roof')
for k in range(1, 12):   # standing seams down the long slopes
    x = ix0 + (ix1 - ix0) * k / 12
    if ix0 + 1.0 < x < ix1 - 1.0:
        for (ya, yb) in [(iy0, ry), (iy1, ry)]: pipe((x, ya, rz0 + 0.03), (x, yb, rz1 + 0.03), 0.025, 'F_iron', seg=4)
pipe((ix0 + 1.2, ry, rz1 + 0.04), (ix1 - 1.2, ry, rz1 + 0.04), 0.05, 'F_iron', seg=6)

# ---- the stack: brick, stone bands, a corbelled crown, an iron rain cap; soot thickens toward the top
sx, sy, SH = W / 2 - 1.5, D / 2 - 1.6, 16.5
box((sx, sy, (rz0 + SH) / 2), (1.8, 1.8, SH - rz0), 'F_brick', 0.02, tag='stack')
for z in (rz0 + 1.8, rz0 + 4.2, rz0 + 6.6): box((sx, sy, z), (1.94, 1.94, 0.18), 'F_ashlar', 0.02, tag='stack')
for z in (rz0 + 3.0, rz0 + 5.4): box((sx, sy, z), (1.86, 1.86, 0.08), 'F_iron', 0.005, tag='stack')
for k, g in enumerate((0.06, 0.12, 0.18)): box((sx, sy, SH + 0.1 + k * 0.17), (1.8 + 2 * g, 1.8 + 2 * g, 0.17), 'F_brick', 0.015, tag='stack')
box((sx, sy, SH + 0.62), (1.4, 1.4, 0.06), 'F_glass', 0.0)   # the flue's dark mouth
for (a, b) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]: box((sx + a * 0.62, sy + b * 0.62, SH + 0.95), (0.08, 0.08, 0.7), 'F_iron', 0.0, tag='stack')
prism([Vector((sx - 0.95, sy - 0.95, SH + 1.32)), Vector((sx + 0.95, sy - 0.95, SH + 1.32)), Vector((sx + 0.95, sy + 0.95, SH + 1.32)), Vector((sx - 0.95, sy + 0.95, SH + 1.32))], 0.05, (0, 0, 1), 'F_iron', 0.01, tag='stack')

# ---- rainwater: iron spouts through the parapet feed downpipes with brackets and a shoe at the foot
for sgn in (-1, 1):   # spouts out through the side parapets, downpipes down the side walls clear of the corner stones
    x = sgn * (W / 2); y = fy + 1.25
    pipe((x - sgn * 0.3, y, rz0 + 0.12), (x + sgn * 0.45, y, rz0 + 0.12), 0.07, 'F_iron', seg=8)
    box((x + sgn * 0.46, y, rz0 + 0.02), (0.3, 0.3, 0.3), 'F_iron', 0.02)
    pipe((x + sgn * 0.46, y, rz0 - 0.1), (x + sgn * 0.46, y, 1.4), 0.06, 'F_iron', seg=8, tag='downpipe')
    pipe((x + sgn * 0.46, y, 1.4), (x + sgn * 0.8, y, 0.15), 0.06, 'F_iron', seg=8)
    for z in (2.0, 3.6, 5.6): box((x + sgn * 0.24, y, z), (0.48, 0.18, 0.05), 'F_iron', 0.005)
# a copper steam line down the right side from the roof tank to the yard (it goes somewhere: the boiler at the back)
cyl((W / 2 - 1.5, fy + 2.2, rz0 + 0.5), 0.45, 0.45, 0.9, 'F_copper', seg=14, bev=0.01, tag='tank')
pipe((W / 2 - 1.05, fy + 2.2, rz0 + 0.5), (W / 2 + 0.18, fy + 2.2, rz0 + 0.5), 0.05, 'F_copper', seg=8)
pipe((W / 2 + 0.18, fy + 2.2, rz0 + 0.5), (W / 2 + 0.18, fy + 2.2, 0.9), 0.05, 'F_copper', seg=8)
pipe((W / 2 + 0.18, fy + 2.2, 0.9), (W / 2 + 0.18, D / 2 + 0.2, 0.9), 0.05, 'F_copper', seg=8)
for y in (fy + 2.2, fy + 5, fy + 8): box((W / 2 + 0.1, y, 0.9 if y > fy + 3 else 3), (0.2, 0.12, 0.05), 'F_iron', 0.005)
cyl((W / 2 + 0.28, fy + 2.2, 2.0), 0.14, 0.14, 0.03, 'F_rust', seg=10, axis='X')                  # a valve wheel

# ---- the sign: a wrought bracket over the bay with a hanging hammer-and-anvil plate; a lantern by the door
sxp = (cr2 + FX(DOOR['u0']) - 0.16) / 2
box((sxp, fy - 0.55, 3.55), (0.06, 1.1, 0.06), 'F_iron', 0.0); pipe((sxp, fy - 0.02, 3.1), (sxp, fy - 0.85, 3.55), 0.025, 'F_iron', seg=6)
for y in (fy - 0.35, fy - 0.85): pipe((sxp, y, 3.52), (sxp, y, 3.3), 0.012, 'F_iron', seg=4)
box((sxp, fy - 0.6, 2.95), (0.05, 0.7, 0.62), 'F_rust', 0.01, tag='sign')
box((sxp - 0.03, fy - 0.6, 2.82), (0.03, 0.42, 0.18), 'F_iron', 0.005); box((sxp - 0.03, fy - 0.5, 3.08), (0.03, 0.08, 0.36), 'F_iron', 0.005)
lx = FX(DOOR['u1']) + 0.55
box((lx, fy - 0.18, 2.6), (0.05, 0.36, 0.05), 'F_iron', 0.0)
box((lx, fy - 0.36, 2.38), (0.22, 0.22, 0.32), 'F_iron', 0.01); box((lx, fy - 0.36, 2.38), (0.16, 0.24, 0.24), 'F_glow', 0.0, tag='glow')
prism([Vector((lx - 0.15, fy - 0.51, 2.56)), Vector((lx + 0.15, fy - 0.51, 2.56)), Vector((lx, fy - 0.36, 2.72))], 0.3, (0, -1, 0), 'F_iron', 0.0)

# ---------------------------------------------------------------- one mesh, UVs by world projection, weathering
me = bpy.data.meshes.new('FerrinForge'); obj = bpy.data.objects.new('FerrinForge', me); scene.collection.objects.link(obj)
for name in MAT_LIST:
    mm = make_material(name); mm.use_backface_culling = name != 'F_iron'; me.materials.append(mm)
bm = bmesh.new(); tagl = bm.faces.layers.int.new('tag'); TAGS = {}
for vs, fs, mat, tag in PARTS:
    base = [bm.verts.new(p) for p in vs]
    for f in fs:
        try: face = bm.faces.new([base[i] for i in f])
        except ValueError: continue
        face.material_index = MAT_LIST.index(mat); face[tagl] = TAGS.setdefault(tag, len(TAGS))
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
uvl = bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    tile = MATS[MAT_LIST[f.material_index]][1]; n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
    for l in f.loops:
        p = l.vert.co
        u, v = ((p.y, p.z) if ax == 0 else (p.x, p.z) if ax == 1 else (p.x, p.y))
        if ax == 0 and n.x < 0: u = -u
        if ax == 1 and n.y > 0: u = -u
        l[uvl].uv = (u / tile, v / tile)
bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth = False
col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); me.color_attributes.active_color = col
for d in col.data: d.color = (1, 1, 1, 1)

# ambient occlusion, baked by Cycles into the vertex colours
scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 64
ground = bpy.data.objects.new('ground', bpy.data.meshes.new('g')); scene.collection.objects.link(ground)
gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=1, y_segments=1, size=30); gb.to_mesh(ground.data); gb.free()
bpy.context.view_layer.objects.active = obj; obj.select_set(True)
scene.render.bake.target = 'VERTEX_COLORS'; scene.world = bpy.data.worlds.new('w')
bpy.ops.object.bake(type='AO')
# soot and rust over the occlusion, where smoke and water would put them
def smooth(a, b, x): t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)
bayx = ((FX(BAY['u0']) + FX(BAY['u1'])) / 2, (BAY['u1'] - BAY['u0']) / 2)
rust_src = []
for vs, fs, mat, tag in PARTS:
    if tag in ('shutter', 'anchor', 'downpipe', 'sign'):
        xs = [p.x for p in vs]; ys = [p.y for p in vs]; zs = [p.z for p in vs]
        rust_src.append((min(xs), max(xs), min(ys), max(ys), min(zs)))
for i, v in enumerate(me.vertices):
    ao = col.data[i].color[0]; ao = 0.35 + 0.65 * ao
    p = v.co; r, g, b = ao, ao, ao
    soot = 0.0
    soot = max(soot, smooth(HT - 1.6, HT + 0.3, p.z) * 0.35)                                      # the parapet and coping, under the smoke
    soot = max(soot, smooth(rz0 + 3, SH + 1.2, p.z) * 0.75 if abs(p.x - sx) < 1.2 and abs(p.y - sy) < 1.2 else 0)   # the stack's crown
    if p.y < fy + 0.4 and abs(p.x - bayx[0]) < bayx[1] + 0.9 and p.z > BAY['z1']:                 # the plume above the forge bay
        soot = max(soot, (1 - smooth(BAY['z1'], BAY['z1'] + 4.8, p.z)) * (1 - smooth(bayx[1] * 0.5, bayx[1] + 1.2, abs(p.x - bayx[0]))) * 0.85)
    if fy + T < p.y < fy + T + 2.7 and FX(BAY['u0']) < p.x < FX(BAY['u1']): soot = max(soot, 0.55)   # inside the bay
    rust = 0.0
    for (x0, x1, y0, y1, z0) in rust_src:
        if x0 - 0.05 < p.x < x1 + 0.05 and y0 - 0.25 < p.y < y1 + 0.25 and z0 - 1.4 < p.z < z0:
            rust = max(rust, (1 - smooth(0, 1.4, z0 - p.z)) * 0.55 * (0.6 + 0.4 * math.sin(p.x * 37.0) ** 2))
    k = 1 - soot
    r, g, b = r * k, g * k, b * k * 0.97
    r, g, b = r * (1 - rust) + rust * 0.42 * ao, g * (1 - rust) + rust * 0.24 * ao, b * (1 - rust) + rust * 0.13 * ao
    col.data[i].color = (r, g, b, 1)
bpy.data.objects.remove(ground)
ntri = sum(len(p.vertices) - 2 for p in me.polygons)
print('FERRIN FORGE: %d verts, %d tris, %d parts' % (len(me.vertices), ntri, len(PARTS)))

# ---------------------------------------------------------------- the mid-distance version: the same building, decimated
lod = obj.copy(); lod.data = obj.data.copy(); lod.name = 'FerrinForge_LOD1'; scene.collection.objects.link(lod)
dm = lod.modifiers.new('dec', 'DECIMATE'); dm.ratio = float(os.environ.get('LOD1', '0.14'))
bpy.context.view_layer.objects.active = lod; bpy.ops.object.select_all(action='DESELECT'); lod.select_set(True); bpy.ops.object.modifier_apply(modifier='dec')
print('LOD1: %d tris' % sum(len(p.vertices) - 2 for p in lod.data.polygons))
# ---------------------------------------------------------------- export, and a beauty shot
bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True); lod.select_set(True)
kw = dict(filepath=OUT, use_selection=True, export_format='GLB', export_image_format='NONE', export_materials='EXPORT', export_yup=True)
try: bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError: bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('EXPORTED', OUT)

if RENDER:
    lod.hide_render = True
    world = scene.world; world.use_nodes = True; nt = world.node_tree
    sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(float(os.environ.get('SUNEL', '9'))); sky.sun_rotation = math.radians(210)
    nt.links.new(sky.outputs['Color'], nt.nodes['Background'].inputs['Color']); nt.nodes['Background'].inputs['Strength'].default_value = float(os.environ.get('SKY', '0.22'))
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = float(os.environ.get('SUNE', '2.2')); sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(58), 0, math.radians(-35)); scene.collection.objects.link(sun)
    g = bpy.data.objects.new('street', bpy.data.meshes.new('street')); scene.collection.objects.link(g)
    gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=40, y_segments=40, size=18); gb.to_mesh(g.data); gb.free()
    gm = make_material('F_ashlar'); g.data.materials.append(gm)
    guv = g.data.uv_layers.new();
    for l in g.data.loops: co = g.data.vertices[l.vertex_index].co; guv.data[l.index].uv = (co.x / 2.5, co.y / 2.5)
    gc = g.data.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    for d in gc.data: d.color = (0.55, 0.52, 0.5, 1)
    fl = bpy.data.objects.new('forgelight', bpy.data.lights.new('forgelight', 'POINT')); fl.data.energy = 900; fl.data.color = (1.0, 0.5, 0.2); fl.data.shadow_soft_size = 0.4
    fl.location = (hx, by1 - 0.9, 1.4); scene.collection.objects.link(fl)
    ll = bpy.data.objects.new('lamp', bpy.data.lights.new('lamp', 'POINT')); ll.data.energy = 60; ll.data.color = (1.0, 0.7, 0.4); ll.location = (lx, fy - 0.5, 2.3); scene.collection.objects.link(ll)
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
    cam.data.lens = float(os.environ.get('LENS', '30'))
    cp = Vector(tuple(float(v) for v in os.environ.get('CAM', '-9.5,-15.5,4.2').split(','))); tgt = Vector(tuple(float(v) for v in os.environ.get('TGT', '0.6,-2.0,4.6').split(',')))
    cam.location = cp; cam.rotation_euler = (tgt - cp).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1280, 800; scene.cycles.samples = int(os.environ.get('SAMPLES', '96'))
    scene.view_settings.view_transform = 'AgX'; scene.view_settings.exposure = float(os.environ.get('EXPO', '0')); scene.render.filepath = RENDER
    try: scene.cycles.use_denoising = True
    except Exception: pass
    bpy.ops.render.render(write_still=True); print('RENDERED', RENDER)
