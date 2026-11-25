# The Ferrin Quarter's yards and street fronts: what a working smiths' quarter leaves lying about. Same materials, building
# blocks and baked occlusion as the buildings (the head of ferrin_forge.py). One GLB, one object per prop.
#
#   python3.11 ferrin_props.py -- out.glb          (RENDER=sheet.png for a Cycles contact sheet)
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'ferrin_forge.py')).read()
exec(compile(src[:src.index('# ---------------------------------------------------------------- the forge-house')], 'ferrin_forge_head', 'exec'))
random.seed(99)

def lump(c, r, mat, sq=0.7, tag='', sub=2):   # a rough stone, a lump of coal or slag: a squashed, jittered icosahedron
    bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    for v in bm.verts: v.co = Vector((v.co.x * random.uniform(0.75, 1.2), v.co.y * random.uniform(0.75, 1.2), v.co.z * sq * random.uniform(0.8, 1.2)))
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(random.uniform(0, 6.28), 3, 'Z'))
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector(c)); add_bm(bm, mat, tag)

def mound(c, rx, ry, h, mat, rough=0.18, tag='', lumps=0, lmat=None, lr=(0.06, 0.13)):
    """A heap at its angle of repose: a cone with a rounded crown, ragged in plan and in surface, strewn with loose lumps."""
    bm = bmesh.new(); R, A = 10, 32; ph = [random.uniform(0, 6.28) for _ in range(7)]
    def edge(a): return 1 + rough * sum(math.sin(a * k + ph[k]) * (0.6 / k) for k in range(2, 7))
    def zf(r, a): return h * max(0.0, 1 - r) ** 1.0 * (1 - 0.35 * max(0.0, 1 - r * 4) ** 2)
    top = bm.verts.new((c[0], c[1], c[2] + zf(0, 0) * 0.9))
    rings = []
    for i in range(1, R + 1):
        ring = []
        for j in range(A):
            a = j * 6.2832 / A; r = i / R; e = edge(a)
            jit = 0 if i == R else h * 0.07 * random.uniform(-1, 1)
            ring.append(bm.verts.new((c[0] + rx * r * e * math.cos(a), c[1] + ry * r * e * math.sin(a), c[2] + (zf(r, a) + jit if i < R else -0.04))))
        rings.append(ring)
    for j in range(A): bm.faces.new([top, rings[0][j], rings[0][(j + 1) % A]])
    for i in range(R - 1):
        for j in range(A): bm.faces.new([rings[i][j], rings[i + 1][j], rings[i + 1][(j + 1) % A], rings[i][(j + 1) % A]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, mat, tag)
    for k in range(lumps):   # loose pieces lying on the slope and rolled off its foot
        a = random.uniform(0, 6.28); r = min(1.15, random.uniform(0, 1.0) ** 0.6 * 1.15); e = edge(a)
        lump((c[0] + rx * r * e * math.cos(a), c[1] + ry * r * e * math.sin(a), c[2] + zf(min(r, 1), a)), random.uniform(*lr), lmat or mat, 0.75, sub=1)

def barrel(x, y, z=0, r=0.33, h=0.95, lay=False, rz=0.0):
    ax = 'X' if lay else 'Z'
    c = (x, y, z + (r if lay else h / 2))
    if lay:
        cyl(c, r, r, h, 'F_wood', seg=12, axis='X')
        for k in (-0.38, 0, 0.38): cyl((x + k * h, y, z + r), r + 0.012, r + 0.012, 0.05, 'F_iron', seg=12, axis='X')
    else:
        cyl(c, r * 0.92, r * 0.92, h, 'F_wood', seg=12)
        cyl((x, y, z + h / 2), r, r, h * 0.5, 'F_wood', seg=12)
        for k in (0.12, 0.5, 0.88): cyl((x, y, z + h * k), r + 0.012, r + 0.012, 0.05, 'F_iron', seg=12)

def crate(x, y, z, s, rz=0.0):
    box((x, y, z + s / 2), (s, s, s), 'F_wood', 0.015, rz=rz)
    for (a, b) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        c, sn = math.cos(rz), math.sin(rz); px, py = a * s / 2, b * s / 2
        box((x + px * c - py * sn, y + px * sn + py * c, z + s / 2), (0.07, 0.07, s + 0.01), 'F_iron', 0.0, rz=rz)

def anvil(x, y, z=0.0, rz=0.0):
    cyl((x, y, z + 0.35), 0.3, 0.34, 0.7, 'F_wood', seg=10, bev=0.02)
    box((x, y, z + 0.78), (0.6, 0.24, 0.12), 'F_iron', 0.02, rz=rz); box((x, y, z + 0.88), (0.38, 0.16, 0.1), 'F_iron', 0.02, rz=rz)
    box((x - 0.18 * math.cos(rz), y - 0.18 * math.sin(rz), z + 0.97), (0.64, 0.25, 0.1), 'F_iron', 0.02, rz=rz)
    cyl((x + 0.42 * math.cos(rz), y + 0.42 * math.sin(rz), z + 0.97), 0.1, 0.02, 0.35, 'F_iron', seg=8, axis='X')

PROPS = {}
def yard_forge():   # an open-air forge: a brick hearth under an iron hood and flue, bellows, an anvil, a quench trough, tools
    box((0, 0, 0.05), (3.4, 2.6, 0.1), 'F_ashlar', 0.02)
    box((-0.6, 0.5, 0.48), (1.5, 1.05, 0.86), 'F_brick', 0.03, tag='hearth'); box((-0.6, 0.5, 0.92), (1.1, 0.7, 0.04), 'F_glow', 0.0, tag='glow')
    for (a, b) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]: box((-0.6 + a * 0.62, 0.5 + b * 0.42, 1.55), (0.06, 0.06, 1.3), 'F_iron', 0.0)
    bm = bmesh.new(); lo = [(-1.32, -0.08), (0.12, -0.08), (0.12, 1.08), (-1.32, 1.08)]; hi = [(-0.85, 0.32), (-0.35, 0.32), (-0.35, 0.68), (-0.85, 0.68)]
    vl = [bm.verts.new((x, y, 2.2)) for x, y in lo]; vh = [bm.verts.new((x, y, 2.85)) for x, y in hi]
    for i in range(4): bm.faces.new([vl[i], vl[(i + 1) % 4], vh[(i + 1) % 4], vh[i]])
    add_bm(bm, 'F_iron', 'hood')
    cyl((-0.6, 0.5, 3.9), 0.2, 0.2, 2.1, 'F_iron', seg=10, tag='flue'); cyl((-0.6, 0.5, 5.0), 0.32, 0.1, 0.25, 'F_iron', seg=10)
    prism([Vector((0.25, 0.25, 0.55)), Vector((1.25, 0.35, 0.55)), Vector((1.25, 0.65, 0.55)), Vector((0.25, 0.75, 0.55))], 0.32, (0, 0, -1), 'F_wood', 0.01)   # the bellows
    prism([Vector((0.25, 0.3, 0.6)), Vector((1.2, 0.38, 0.75)), Vector((1.2, 0.62, 0.75)), Vector((0.25, 0.7, 0.6))], 0.06, (0, 0, -1), 'F_rust', 0.0)
    pipe((1.2, 0.5, 0.78), (1.2, 0.5, 1.6), 0.03, 'F_wood', seg=5); pipe((1.2, 0.5, 1.6), (0.4, 0.5, 1.75), 0.03, 'F_wood', seg=5)
    pipe((0.25, 0.5, 0.42), (0.1, 0.5, 0.42), 0.06, 'F_copper', seg=8)
    anvil(0.4, -0.65)
    box((-0.95, -0.75, 0.3), (1.1, 0.5, 0.6), 'F_wood', 0.02); box((-0.95, -0.75, 0.59), (1.0, 0.4, 0.02), 'F_glass', 0.0)   # the quench trough
    box((1.45, 0.4, 1.0), (0.08, 1.2, 0.08), 'F_wood', 0.0);
    for k in range(4): box((1.45, 0.0 + k * 0.27, 0.72), (0.03, 0.03, 0.55), 'F_iron', 0.0)
PROPS['FerrinYardForge'] = yard_forge

def coal():         # a coal bunker: three dressed-stone walls round a heap of coal, a shovel left in it
    box((0, 1.0, 0.5), (2.6, 0.3, 1.0), 'F_ashlar', 0.025); box((-1.15, 0.1, 0.5), (0.3, 2.1, 1.0), 'F_ashlar', 0.025); box((1.15, 0.1, 0.5), (0.3, 2.1, 1.0), 'F_ashlar', 0.025)
    mound((0, 0.3, 0), 0.95, 0.75, 0.75, 'F_glass', 0.15, lumps=45, lr=(0.05, 0.11))
    pipe((0.3, -0.4, 0.4), (0.7, -0.9, 1.2), 0.025, 'F_wood', seg=5); box((0.25, -0.33, 0.33), (0.25, 0.04, 0.3), 'F_iron', 0.0, rz=0.6)
PROPS['FerrinCoal'] = coal

def slag():         # a heap of slag and clinker, a broken barrow beside it
    mound((0, 0, 0), 1.6, 1.25, 1.1, 'F_rust', 0.2, lumps=40, lmat='F_glass', lr=(0.08, 0.18))
    mound((1.05, 0.75, 0), 0.85, 0.7, 0.5, 'F_stone', 0.25, lumps=14, lmat='F_rust', lr=(0.08, 0.15))
PROPS['FerrinSlag'] = slag

def cart():         # an ore cart: a tapered wooden box on iron-rimmed wheels, full of ore
    bm = bmesh.new(); lo = [(-0.8, -0.5), (0.8, -0.5), (0.8, 0.5), (-0.8, 0.5)]; hi = [(-1.0, -0.65), (1.0, -0.65), (1.0, 0.65), (-1.0, 0.65)]
    vl = [bm.verts.new((x, y, 0.45)) for x, y in lo]; vh = [bm.verts.new((x, y, 1.15)) for x, y in hi]
    bm.faces.new(vl)
    for i in range(4): bm.faces.new([vl[i], vl[(i + 1) % 4], vh[(i + 1) % 4], vh[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, 'F_wood', 'cart')
    for (x, y) in [(-0.55, -0.62), (0.55, -0.62), (-0.55, 0.62), (0.55, 0.62)]:
        cyl((x, y, 0.32), 0.32, 0.32, 0.08, 'F_wood', seg=14, axis='Y'); cyl((x, y, 0.32), 0.34, 0.34, 0.05, 'F_iron', seg=14, axis='Y')
    for z in (0.6, 1.0): box((0, -0.6, z), (1.9, 0.04, 0.06), 'F_iron', 0.0)
    mound((0, 0, 0.95), 0.85, 0.55, 0.3, 'F_stone', 0.15, lumps=18, lr=(0.07, 0.12))
    pipe((1.0, 0.3, 0.95), (1.6, 0.3, 0.7), 0.035, 'F_wood', seg=5); pipe((1.0, -0.3, 0.95), (1.6, -0.3, 0.7), 0.035, 'F_wood', seg=5)
PROPS['FerrinCart'] = cart

def barrels():
    barrel(-0.4, 0.1); barrel(0.3, 0.25, r=0.3, h=0.85); barrel(-0.05, -0.5, lay=True, h=0.9, r=0.3)
    cyl((-0.4, 0.1, 0.97), 0.3, 0.3, 0.03, 'F_wood', seg=12)
PROPS['FerrinBarrels'] = barrels

def crates():
    crate(-0.35, 0.0, 0, 0.75, 0.1); crate(0.5, 0.1, 0, 0.65, -0.2); crate(-0.25, 0.05, 0.75, 0.6, 0.4); crate(0.4, -0.55, 0, 0.5, 0.6)
PROPS['FerrinCrates'] = crates

def ingots():       # cast ingots stacked crosswise on a pallet
    box((0, 0, 0.08), (1.3, 1.0, 0.16), 'F_wood', 0.01)
    for layer in range(4):
        for k in range(4):
            if layer % 2 == 0: c = (-0.45 + k * 0.3, 0, 0.22 + layer * 0.11); s = (0.24, 0.85, 0.1)
            else: c = (0, -0.36 + k * 0.24, 0.22 + layer * 0.11); s = (1.1, 0.2, 0.1)
            box(c, s, 'F_iron', 0.02)
    for x in (-0.55, 0.55): box((x, 0, 0.45), (0.04, 1.02, 0.04), 'F_rust', 0.0)
PROPS['FerrinIngots'] = ingots

def workbench():    # a heavy bench, a vice, tools, a grindstone on its frame
    box((0, 0, 0.85), (2.0, 0.75, 0.12), 'F_wood', 0.015)
    for (a, b) in [(-1, -1), (1, -1), (-1, 1), (1, 1)]: box((a * 0.88, b * 0.3, 0.4), (0.12, 0.12, 0.8), 'F_wood', 0.01)
    box((0, 0, 0.25), (1.85, 0.6, 0.05), 'F_wood', 0.0)
    box((0.75, -0.3, 0.98), (0.2, 0.22, 0.15), 'F_iron', 0.01); box((0.75, -0.45, 0.98), (0.2, 0.06, 0.18), 'F_iron', 0.005); pipe((0.62, -0.5, 1.0), (0.88, -0.5, 1.0), 0.015, 'F_iron', seg=4)
    for k in range(3): box((-0.6 + k * 0.25, 0.1, 0.93), (0.05, 0.4, 0.04), 'F_iron', 0.0, rz=0.2 * k)
    cyl((-1.45, 0, 0.75), 0.4, 0.4, 0.14, 'F_ashlar', seg=18, axis='Y'); pipe((-1.45, -0.15, 0.75), (-1.45, 0.25, 0.75), 0.03, 'F_iron', seg=5)
    for s2 in (-1, 1): pipe((-1.45, s2 * 0.15, 0.75), (-1.45 + s2 * 0.25, s2 * 0.15, 0.0), 0.04, 'F_wood', seg=5); pipe((-1.45, s2 * 0.15, 0.75), (-1.45 - s2 * 0.25, s2 * 0.15, 0.0), 0.04, 'F_wood', seg=5)
PROPS['FerrinWorkbench'] = workbench

def course(x0, x1, y0, y1, z0, z1, mat, n=None, gap=0.012, bev=0.025, jit=0.01):   # a run of separate dressed stones
    L = x1 - x0; n = n or max(1, round(L / 0.7)); w = L / n
    for i in range(n): box((x0 + w * (i + 0.5), (y0 + y1) / 2, (z0 + z1) / 2 + random.uniform(-jit, jit)), (w - gap, y1 - y0, z1 - z0), mat, bev)

def yard_wall():   # 2 m of yard wall between two smiths' houses: basalt rubble on a dressed plinth, a ridged coping
    box((0, 0, 0.12 - 0.6), (2.0, 0.62, 1.44), 'F_ashlar', 0.02)
    box((0, 0, 0.24 + 0.9), (2.0, 0.5, 1.8), 'F_stone', 0.0)
    course(-1.0, 1.0, -0.33, 0.33, 2.04, 2.2, 'F_ashlar', n=3)
    for i in range(3): prism([Vector((-1.0 + i * 0.667 + 0.006, -0.3, 2.2)), Vector((-1.0 + i * 0.667 + 0.006, 0.3, 2.2)), Vector((-1.0 + i * 0.667 + 0.006, 0, 2.38))], 0.655, (-1, 0, 0), 'F_ashlar', 0.01)
PROPS['FerrinYardWall'] = yard_wall

def yard_gate():   # a cart gate into a yard: two dressed piers, a pair of iron gates, an iron overthrow with the cog of the Ferrin
    W = 3.6; gw = 2.3
    for sx in (-1, 1):
        cx = sx * (gw / 2 + 0.33)
        box((cx, 0, 0.12 - 0.6), (0.72, 0.72, 1.44), 'F_ashlar', 0.02)
        for k in range(5): box((cx, 0, 0.12 + k * 0.5 + 0.25), (0.66 if k % 2 else 0.6, 0.66 if k % 2 == 0 else 0.6, 0.49), 'F_ashlar', 0.025)
        box((cx, 0, 2.76), (0.8, 0.8, 0.16), 'F_ashlar', 0.03); prism([Vector((cx - 0.38, -0.38, 2.84)), Vector((cx + 0.38, -0.38, 2.84)), Vector((cx, 0, 3.12))], 0.0, (0, 0, 1), 'F_ashlar', 0.0) if False else None
        bm = bmesh.new(); b = [bm.verts.new((cx + a * 0.38, c * 0.38, 2.84)) for a, c in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]; t = bm.verts.new((cx, 0, 3.14))
        bm.faces.new(list(reversed(b)))
        for i in range(4): bm.faces.new([b[i], b[(i + 1) % 4], t])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, 'F_ashlar', '')
    for leaf in (-1, 1):   # the two leaves, standing a little ajar
        x0 = leaf * 0.02; x1 = leaf * gw / 2
        for z in (0.18, 1.0, 1.85): box(((x0 + x1) / 2, 0, z), (abs(x1 - x0), 0.06, 0.07), 'F_iron', 0.0)
        for k in range(9):
            x = x0 + (x1 - x0) * (k + 0.5) / 9; box((x, 0, 1.0), (0.03, 0.03, 1.75), 'F_iron', 0.0); cyl((x, 0, 1.92), 0.03, 0.0, 0.12, 'F_iron', seg=4)
        box((x1 - leaf * 0.04, 0, 1.0), (0.07, 0.07, 1.9), 'F_iron', 0.0)
        pipe((x0, 0, 0.25), (x1 - leaf * 0.05, 0, 1.8), 0.02, 'F_iron', seg=4)
    pipe((-gw / 2, 0, 2.55), (gw / 2, 0, 2.55), 0.03, 'F_iron', seg=6)   # the overthrow
    for i in range(12):
        a0 = math.pi * i / 12; a1 = math.pi * (i + 1) / 12
        pipe((math.cos(a0) * gw / 2, 0, 2.55 + math.sin(a0) * 0.45), (math.cos(a1) * gw / 2, 0, 2.55 + math.sin(a1) * 0.45), 0.025, 'F_iron', seg=4)
    cyl((0, 0, 2.78), 0.26, 0.26, 0.06, 'F_rust', seg=12, axis='Y')
    for i in range(8):
        a = i / 8 * 2 * math.pi; box((math.cos(a) * 0.3, 0, 2.78 + math.sin(a) * 0.3), (0.09, 0.07, 0.09), 'F_rust', 0.0, rx=0)
PROPS['FerrinYardGate'] = yard_gate

def ostrak():   # Ostrak's Anvil: the god's anvil on a stepped basalt plinth, a hammer laid against it, braziers at its feet
    for k, (r, h) in enumerate([(3.5, 0.36), (2.95, 0.36), (2.35, 0.5)]):
        z0 = sum(hh for _, hh in [(3.5, 0.36), (2.95, 0.36), (2.35, 0.5)][:k])
        cyl((0, 0, z0 + h / 2 - (0.4 if k == 0 else 0)), r, r, h + (0.8 if k == 0 else 0), 'F_stone', seg=8, bev=0.02)
        cyl((0, 0, z0 + h - 0.03), r + 0.04, r + 0.04, 0.06, 'F_ashlar', seg=8)                                   # a dressed nosing on each step
    zt = 1.22
    for i in range(4):                                                                                           # bronze plaques round the top step
        a = i / 4 * 2 * math.pi + math.pi / 8 + math.pi / 4
        box((math.cos(a) * 2.37, math.sin(a) * 2.37, zt - 0.25), (0.04, 0.9, 0.26), 'F_copper', 0.01, rz=a)
    # the anvil: a waisted foot, the body, a long horn and a square heel, the face polished bright
    prism([Vector((-1.0, -0.65, zt)), Vector((1.0, -0.65, zt)), Vector((0.55, -0.38, zt + 0.95)), Vector((-0.55, -0.38, zt + 0.95))], -1.3, (0, 1, 0), 'F_iron', 0.03)
    box((0, 0, zt + 0.2), (2.1, 1.4, 0.4), 'F_iron', 0.04)
    box((0, 0, zt + 1.3), (2.4, 0.95, 0.75), 'F_iron', 0.05)
    box((-1.55, 0, zt + 1.42), (0.8, 0.8, 0.5), 'F_iron', 0.04)                                                   # the heel
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=14, radius1=0.42, radius2=0.03, depth=1.7)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'Y'))
    bmesh.ops.scale(bm, vec=(1, 1, 0.9), verts=bm.verts); bmesh.ops.translate(bm, verts=bm.verts, vec=(2.05, 0, zt + 1.48)); add_bm(bm, 'F_iron', 'horn')
    box((0, 0, zt + 1.69), (2.3, 0.86, 0.04), 'F_iron', 0.01)                                                    # the worn face
    box((-1.0, 0, zt + 1.73), (0.12, 0.12, 0.02), 'F_iron', 0.0)                                                  # the hardy hole
    # the hammer, laid against the anvil, its handle on the step
    hb, ht = Vector((1.7, -2.3, 0.74)), Vector((0.35, -0.2, zt + 1.86))                                        # the hammer: its head resting on the face, the haft down to the step
    pipe(hb, ht, 0.08, 'F_wood', seg=8)
    d = (ht - hb).normalized(); rz = math.atan2(d.y, d.x) + math.pi / 2
    box((ht.x, ht.y, ht.z + 0.02), (1.05, 0.46, 0.46), 'F_iron', 0.05, rz=rz)
    for k in (-0.38, 0.38): box((ht.x + math.cos(rz) * k, ht.y + math.sin(rz) * k, ht.z + 0.02), (0.07, 0.5, 0.5), 'F_copper', 0.01, rz=rz)
    for i in range(4):                                                                                           # braziers at the four quarters of the lowest step
        a = i / 4 * 2 * math.pi + math.pi / 4; x, y = math.cos(a) * 3.15, math.sin(a) * 3.15; zb = 0.36
        for k in range(3):
            b = k / 3 * 2 * math.pi; pipe((x + math.cos(b) * 0.35, y + math.sin(b) * 0.35, zb), (x + math.cos(b) * 0.18, y + math.sin(b) * 0.18, zb + 0.95), 0.03, 'F_iron', seg=5)
        cyl((x, y, zb + 1.05), 0.42, 0.24, 0.26, 'F_iron', seg=12); cyl((x, y, zb + 1.16), 0.37, 0.37, 0.03, 'F_glow', seg=12)
        for k in range(7): lump((x + random.uniform(-0.22, 0.22), y + random.uniform(-0.22, 0.22), zb + 1.2), random.uniform(0.06, 0.1), 'F_glow' if k % 2 else 'F_glass', 0.6, sub=1)
PROPS['FerrinAnvil'] = ostrak

# ---- things fixed to the houses: their origin is the point on the wall face they hang from; the street is -y
def wall_lamp():   # an iron lantern on a scrolled bracket
    box((0, -0.03, 0), (0.22, 0.06, 0.4), 'F_iron', 0.01)
    pipe((0, -0.05, 0.12), (0, -0.55, 0.12), 0.025, 'F_iron', seg=5); pipe((0, -0.05, -0.12), (0, -0.4, 0.1), 0.02, 'F_iron', seg=4)
    cyl((0, -0.55, 0.05), 0.04, 0.04, 0.14, 'F_iron', seg=6)
    cyl((0, -0.55, -0.05), 0.15, 0.15, 0.04, 'F_iron', seg=8); box((0, -0.55, -0.27), (0.22, 0.22, 0.36), 'F_glow', 0.0, tag='glow')
    for (a2, c2) in [(-1, -1), (1, -1), (1, 1), (-1, 1)]: box((a2 * 0.12, -0.55 + c2 * 0.12, -0.27), (0.03, 0.03, 0.4), 'F_iron', 0.0)
    cyl((0, -0.55, -0.48), 0.14, 0.08, 0.06, 'F_iron', seg=8)
    bm = bmesh.new(); b = [bm.verts.new((a2 * 0.16, -0.55 + c2 * 0.16, -0.07)) for a2, c2 in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]; t = bm.verts.new((0, -0.55, 0.12))
    bm.faces.new(list(reversed(b)))
    for i in range(4): bm.faces.new([b[i], b[(i + 1) % 4], t])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); add_bm(bm, 'F_iron', '')
PROPS['FerrinWallLamp'] = wall_lamp

def sign(kind):
    def make():   # a trade sign: an iron arm out from the wall, a plate hung on rings, the trade cut out of it
        box((0, -0.03, 0), (0.16, 0.06, 0.5), 'F_iron', 0.01)
        pipe((0, -0.04, 0.2), (0, -1.05, 0.2), 0.03, 'F_iron', seg=6); pipe((0, -0.04, -0.2), (0, -0.7, 0.2), 0.022, 'F_iron', seg=5)
        cyl((0, -1.07, 0.2), 0.05, 0.05, 0.06, 'F_iron', seg=6)
        for y in (-0.35, -0.9): box((0, y, 0.1), (0.02, 0.05, 0.18), 'F_iron', 0.0)
        z0 = -0.55
        if kind == 'anvil':
            box((0, -0.62, z0 + 0.12), (0.06, 0.75, 0.2), 'F_rust', 0.01); box((0, -0.62, z0 - 0.05), (0.06, 0.3, 0.18), 'F_rust', 0.01)
            box((0, -0.62, z0 - 0.2), (0.06, 0.55, 0.1), 'F_rust', 0.01)
            bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.09, radius2=0.01, depth=0.3)
            bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X')); bmesh.ops.translate(bm, verts=bm.verts, vec=(0, -1.12, z0 + 0.15)); add_bm(bm, 'F_rust', 'sign')
        elif kind == 'tongs':
            for sgn in (-1, 1):
                pipe((0, -0.62 + sgn * 0.06, z0 + 0.3), (0, -0.62 - sgn * 0.12, z0 - 0.25), 0.025, 'F_rust', seg=5)
                pipe((0, -0.62 - sgn * 0.12, z0 - 0.25), (0, -0.62 - sgn * 0.05, z0 - 0.36), 0.025, 'F_rust', seg=5)
            cyl((0, -0.62, z0 + 0.12), 0.05, 0.05, 0.08, 'F_iron', seg=8, axis='X')
        else:
            cyl((0, -0.62, z0), 0.26, 0.26, 0.05, 'F_rust', seg=16, axis='X'); cyl((0, -0.62, z0), 0.1, 0.1, 0.07, 'F_iron', seg=10, axis='X')
            for i in range(10):
                a2 = i / 10 * 2 * math.pi; box((0, -0.62 + math.cos(a2) * 0.3, z0 + math.sin(a2) * 0.3), (0.05, 0.08, 0.08), 'F_rust', 0.0, rx=a2)
    return make
PROPS['FerrinSignAnvil'] = sign('anvil'); PROPS['FerrinSignTongs'] = sign('tongs'); PROPS['FerrinSignCog'] = sign('cog')

def butt():   # a water butt under a downpipe: staves, iron hoops, a lid, a tap
    cyl((0, 0, 0.55), 0.36, 0.36, 1.1, 'F_wood', seg=14); cyl((0, 0, 0.55), 0.39, 0.39, 0.55, 'F_wood', seg=14)
    for z in (0.12, 0.55, 0.98): cyl((0, 0, z), 0.395, 0.395, 0.05, 'F_iron', seg=14)
    cyl((0.05, 0.03, 1.12), 0.34, 0.34, 0.04, 'F_wood', seg=14); cyl((0, -0.38, 0.2), 0.03, 0.03, 0.12, 'F_copper', seg=6, axis='Y')
    box((0, 0, 0.03), (0.9, 0.9, 0.06), 'F_ashlar', 0.02)
PROPS['FerrinButt'] = butt

def pump():   # the public pump: an iron column and handle over a stone trough
    box((0, -0.55, 0.32), (2.2, 0.8, 0.64), 'F_ashlar', 0.03); box((0, -0.55, 0.6), (2.0, 0.6, 0.04), 'F_glass', 0.0)
    box((0, 0.25, 0.2), (0.7, 0.7, 0.4), 'F_ashlar', 0.03)
    cyl((0, 0.25, 1.05), 0.15, 0.13, 1.3, 'F_iron', seg=12); cyl((0, 0.25, 1.75), 0.2, 0.2, 0.12, 'F_iron', seg=12); cyl((0, 0.25, 1.88), 0.12, 0.02, 0.2, 'F_iron', seg=10)
    for z in (0.55, 1.4): cyl((0, 0.25, z), 0.17, 0.17, 0.05, 'F_copper', seg=12)
    pipe((0, 0.15, 1.3), (0, -0.25, 1.15), 0.05, 'F_iron', seg=8); cyl((0, -0.27, 1.08), 0.06, 0.04, 0.12, 'F_iron', seg=8)
    pipe((0, 0.35, 1.7), (0, 1.05, 2.0), 0.035, 'F_iron', seg=6); pipe((0, 1.05, 2.0), (0, 1.2, 1.9), 0.035, 'F_iron', seg=6)
PROPS['FerrinPump'] = pump

def bollard():   # a cast-iron bollard, ringed, a chain eye at each side
    cyl((0, 0, 0.45), 0.13, 0.16, 0.9, 'F_iron', seg=12); cyl((0, 0, 0.95), 0.17, 0.12, 0.12, 'F_iron', seg=12)
    for z in (0.2, 0.75): cyl((0, 0, z), 0.18, 0.18, 0.05, 'F_iron', seg=12)
    cyl((0, 0, 1.04), 0.09, 0.02, 0.1, 'F_iron', seg=10)
    for sx in (-1, 1): cyl((sx * 0.17, 0, 0.8), 0.05, 0.05, 0.03, 'F_iron', seg=8, axis='X')
PROPS['FerrinBollard'] = bollard

def build(name, maker):
    PARTS.clear(); maker()
    me = bpy.data.meshes.new(name); obj = bpy.data.objects.new(name, me); scene.collection.objects.link(obj)
    for nm in MAT_LIST:
        mm = bpy.data.materials.get(nm) or make_material(nm); mm.use_backface_culling = nm != 'F_iron'; me.materials.append(mm)
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
        tile = MATS[MAT_LIST[f.material_index]][1] * 0.6; n = f.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            p = l.vert.co; u, v = ((p.y, p.z) if ax == 0 else (p.x, p.z) if ax == 1 else (p.x, p.y)); l[uvl].uv = (u / tile, v / tile)
    bm.to_mesh(me); bm.free()
    col = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT'); me.color_attributes.active_color = col
    for d in col.data: d.color = (1, 1, 1, 1)
    return obj

scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 48; scene.render.bake.target = 'VERTEX_COLORS'; scene.world = bpy.data.worlds.new('w')
ground = bpy.data.objects.new('ground', bpy.data.meshes.new('g')); scene.collection.objects.link(ground)
gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=1, y_segments=1, size=12); gb.to_mesh(ground.data); gb.free()
objs = []
for name, maker in PROPS.items():
    o = build(name, maker)
    bpy.ops.object.select_all(action='DESELECT'); bpy.context.view_layer.objects.active = o; o.select_set(True); bpy.ops.object.bake(type='AO')
    col = o.data.color_attributes['Col']
    for i, v in enumerate(o.data.vertices):
        ao = 0.4 + 0.6 * col.data[i].color[0]; soot = 0.0
        if name == 'FerrinYardForge': soot = max(0.0, 0.5 - 0.12 * math.hypot(v.co.x + 0.6, v.co.y - 0.5)) if v.co.z > 0.9 else 0.0
        k = ao * (1 - soot) * (0.62 if name == 'FerrinSlag' else 1.0); col.data[i].color = (k, k, k * 0.97, 1)
    print('%s: %d tris' % (name, sum(len(p.vertices) - 2 for p in o.data.polygons))); objs.append(o)
bpy.data.objects.remove(ground)
bpy.ops.object.select_all(action='DESELECT')
for o in objs: o.select_set(True)
kw = dict(filepath=OUT, use_selection=True, export_format='GLB', export_image_format='NONE', export_materials='EXPORT', export_yup=True)
try: bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError: bpy.ops.export_scene.gltf(**kw, export_colors=True)
print('EXPORTED', OUT)
if RENDER:   # a contact sheet: the props in a row
    for i, o in enumerate(objs): o.location.x = (i % 4) * 4.5 - 6.75; o.location.y = (i // 4) * 4.5
    world = scene.world; world.use_nodes = True; nt = world.node_tree; sky = nt.nodes.new('ShaderNodeTexSky'); sky.sky_type = 'NISHITA'; sky.sun_elevation = math.radians(20)
    nt.links.new(sky.outputs['Color'], nt.nodes['Background'].inputs['Color']); nt.nodes['Background'].inputs['Strength'].default_value = 0.3
    sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sun.data.energy = 2.0; sun.rotation_euler = (math.radians(50), 0, math.radians(-35)); scene.collection.objects.link(sun)
    g = bpy.data.objects.new('street', bpy.data.meshes.new('street')); scene.collection.objects.link(g)
    gb = bmesh.new(); bmesh.ops.create_grid(gb, x_segments=4, y_segments=4, size=30); gb.to_mesh(g.data); gb.free()
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam; cam.data.lens = 28
    cp = Vector((0, -11, 7)); tgt = Vector((0, 2.2, 0.5)); cam.location = cp; cam.rotation_euler = (tgt - cp).to_track_quat('-Z', 'Y').to_euler()
    scene.render.resolution_x, scene.render.resolution_y = 1280, 720; scene.cycles.samples = 40; scene.view_settings.view_transform = 'AgX'; scene.render.filepath = RENDER
    bpy.ops.render.render(write_still=True); print('RENDERED', RENDER)
