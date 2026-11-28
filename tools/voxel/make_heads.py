# Two versions of one Hrimfolk head (docs/design.md, Voxel art; the user's viking references), on a Hrimfolk body in flat
# colours, to choose between: A oversized at the body's 2.5 cm voxels (stylized), B life-size at 1.25 cm (half-size voxels,
# a finer part named head#2). Both are sampled from the same design in centimetres, so only size and detail differ.
# The design: a shaved scalp with a knotwork tattoo, heavy brows set low (a stern look), a scar across the left eye, a
# broad nose, ears, a full dark beard with a moustache over the mouth and a braid with two iron beads.
#   python3 tools/voxel/make_heads.py   -> godot/assets/voxel/characters/hrim_body.vox, hrim_head_a.vox, hrim_head_b.vox
import math, os, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + '.py')); mod = importlib.util.module_from_spec(spec)
    src = open(spec.origin).read(); src = src[:src.rindex('\nOUT = ')]
    exec(compile(src, spec.origin, 'exec'), mod.__dict__); return mod
hd = load('make_base_hd'); mb = load('make_base')

PAL = dict(hd.PAL)
PAL.update({'tunic': (92, 102, 78), 'tunic_d': (72, 80, 60), 'tunic_l': (110, 120, 94), 'trousers': (60, 54, 44), 'trousers_d': (46, 41, 33),
            'tattoo': (44, 64, 60), 'scar': (236, 186, 164), 'beard': (68, 44, 28), 'beard_d': (50, 32, 20), 'bead': (132, 136, 140)})
NAMES = list(PAL)

# the Hrimfolk body: the detailed base in flat colours (no speckle), a green-grey tunic with leather lacing, iron buckle
hd.tone = lambda c, x, y, z: c
RECOL = {'shirt': 'tunic', 'shirt_d': 'tunic_d', 'shirt_l': 'tunic_l', 'button': 'leather', 'brass': 'iron'}
body = {p: {k: RECOL.get(c, c) for k, c in v.items()} for p, v in hd.body('m').items()}
del body['head']

CX, CY, HZ0 = 20, 8, 62    # where the base head sat: its bottom centre (in 2.5 cm voxels)

def head(scale, res):
    """the head sampled at `res` cm per voxel, `scale` times life size; coordinates in cm from the head's bottom centre:
    x across, y front (negative) to back, z up"""
    S = scale; R = {'rx': 10.5 * S, 'ry': 12.0 * S, 'rz': 13.0 * S}; cz = 12.0 * S
    P = {}
    n = int(math.ceil(18 * S / res)) + 2
    zmin = int(-24 * S / res) - 2
    for i in range(-n, n):
        for j in range(-n, n):
            for k in range(zmin, int(28 * S / res)):
                x, y, z = (i + 0.5) * res, (j + 0.5) * res, (k + 0.5) * res
                jaw = 0.78 + 0.22 * min(1.0, max(0.0, (z - 0) / (10 * S)))
                d = (x / (R['rx'] * jaw)) ** 2 + (y / R['ry']) ** 2 + ((z - cz) / R['rz']) ** 2
                c = None; front = y < -R['ry'] * 0.55
                if d <= 1:
                    surf = d > (1 - 2.2 * res / (R['rx']))
                    c = 'skin'
                    if surf:
                        u = x / S; w = (z - cz) / S   # face coordinates, life-size cm
                        # the scalp tattoo: two bands of knotwork over the crown
                        if w > 6.5 and not (front and w < 9) and (abs(math.sin(u * 0.55 + y / S * 0.35)) < 0.18 or abs(math.sin(u * 0.55 - y / S * 0.35 + 1.4)) < 0.14): c = 'tattoo'
                        if front:
                            if 1.2 < w < 3.6 and 1.0 < abs(u) < 6.2 and w < 1.6 + (abs(u) - 1.0) * 0.55 + 1.2: c = 'brow'        # heavy brows, low inside: stern
                            if -1.4 < w < 1.0 and 1.8 < abs(u) < 5.6: c = 'eye_w'
                            if -1.4 < w < 1.0 and 3.0 < abs(u) < 4.4: c = 'eye'
                            if abs((u + 3.6) * 0.8 - (w - 0.5) * 0.45) < 0.55 and -6 < w < 5 and u < -1.0: c = 'scar'            # across the left eye
                            if -8.5 < w < -6.6 and abs(u) < 2.6: c = 'lip'
                        if abs(abs(u) - R['rx'] / S) < 1.8 and -4 < w < 2 and abs(y / S) < 2.5: c = 'skin_d'                    # the ears' shadow
                # the nose: a broad wedge out of the face, its underside shaded
                u = x / S; w = (z - cz) / S; yf = -R['ry'] * math.sqrt(max(0.0, 1 - (u / R['rx'] * S) ** 2 * 0 - (w / (R['rz'] / S)) ** 2))
                if -6.2 < w < 0.5 and abs(u) < 1.8 - (w + 6.2) * 0.08 and yf - (3.0 - (0.5 - w) * 0.2) * S < y < yf + 1.5 * S:
                    c = 'skin_d' if w < -5.2 else 'skin'
                # the ears
                if abs(abs(x) - R['rx'] * jaw) < 2.0 * S and -4 * S < z - cz < 2.5 * S and abs(y) < 2.2 * S and d > 0.75: c = 'skin'
                # the beard: from the cheeks down past the chin; a moustache over the mouth; a braid with two beads
                bw = (abs(x) / (9.5 * S)) ** 2 + ((y + 3 * S) / (10.5 * S)) ** 2
                if z < cz - 4.5 * S and z > -9 * S and bw <= 1 and y < 4 * S and (d > 0.62 or z < 1 * S):
                    if not (front_lip(x, z, cz, S) and y < -R['ry'] * 0.6): c = 'beard' if (int((x + 50) / (1.6 * S)) + int((z + 50) / (2.4 * S))) % 5 else 'beard_d'
                if -6.6 * S < z - cz < -5.0 * S and abs(x) < 5.2 * S and y < -R['ry'] * 0.7 and y > -R['ry'] - 1.6 * S: c = 'beard_d'   # the moustache
                if abs(x) < 1.8 * S and -24 * S < z < -8 * S and -10.0 * S < y < -5.5 * S:
                    c = 'bead' if any(abs(z - zz * S) < 1.2 * S for zz in (-13, -20)) else ('beard' if int((z + 50) / (2.0 * S)) % 2 else 'beard_d')
                if c: P[(i, j, k)] = c
    return P

def front_lip(x, z, cz, S): return -8.5 * S < z - cz < -6.6 * S and abs(x) < 2.6 * S

def place(P, res, base_res=2.5):
    k = int(round(base_res / res))   # how many head voxels per body voxel
    return {(CX * k + i, CY * k + j, HZ0 * k + z): c for (i, j, z), c in P.items()}

OUT = os.path.join(HERE, '..', '..', 'godot', 'assets', 'voxel', 'characters')
mb.COL = PAL; mb.NAMES = NAMES
mb.write(os.path.join(OUT, 'hrim_body.vox'), body)
mb.write(os.path.join(OUT, 'hrim_head_a.vox'), {'head': place(head(1.35, 2.5), 2.5)})
mb.write(os.path.join(OUT, 'hrim_head_b.vox'), {'head#2': place(head(1.0, 1.25), 1.25)})
