# Fogwright base body from MakeHuman (CC0, through MPFB's data files), rigged to our skeleton and painted by code.
# usage (from tools/blender/, with Blender's bpy module and MPFB_DATA set, see mh.py):
#   SEX=m PEOPLE=Human  python mhbody.py -- human_m.glb
# then merge the peoples into one model with merge_peoples.py (every run shares one mesh, so they merge as morphs).
# Every body is MakeHuman's one base mesh moved by its shape targets: the peoples, Lean and Heavy are all the same
# vertices in the same order. The rig takes MakeHuman's joint positions and skin weights (its game_engine rig),
# merged onto our 19 bones, so the shoulders and armpits deform the way MakeHuman's artists weighted them.
import bpy, bmesh, math, os, sys
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mh

OUT = sys.argv[-1]
SEX = os.environ.get('SEX', 'm')
PEOPLE = os.environ.get('PEOPLE', 'Human')
OLD = os.environ.get('HAIR_FROM', os.path.join('..', '..', 'creator', 'male.gltf.json' if SEX == 'm' else 'female_cc.gltf.json'))
sm = lambda a, b, x: (lambda t: t * t * (3 - 2 * t))(min(1.0, max(0.0, (x - a) / (b - a))))

# ---------- the rig: our skeleton and its pose helpers, from tinker.py (its meshes are thrown away)
src = open('tinker.py').read(); src = src[:src.index('bpy.ops.export_scene')]
_argv = sys.argv; sys.argv = ['x', '--', '/tmp/_unused.glb']; g = {'__name__': 'x'}; exec(compile(src, 'tinker.py', 'exec'), g); sys.argv = _argv
arm, upd = g['arm'], g['upd']
for o in list(bpy.data.objects):
    if o.type == 'MESH': bpy.data.objects.remove(o, do_unlink=True)
arm.data.pose_position = 'REST'; upd()
col = bpy.context.scene.collection

# ---------- 1. the bodies, as MakeHuman shapes
M = {'m': dict(gender=1.0, muscle=0.62, weight=0.45, proportions=1.0),
     'f': dict(gender=0.0, muscle=0.5, weight=0.42, proportions=1.0, cupsize=0.55, firmness=0.65)}[SEX]
HEIGHT = {'m': 1.814, 'f': 1.722}[SEX]      # the Human body's height, as the old bodies (the creator's height slider scales from it)
def both(d):  # 'x-foo' -> l-x-foo and r-x-foo
    out = {}
    for k, v in d.items():
        if k.startswith('*'): out[k[1:].replace('*', 'l')] = v; out[k[1:].replace('*', 'r')] = v
        else: out[k] = v
    return out
PEOPLES = {  # macro changes (added to M) and region targets with weights
    'Human': ({}, {}),
    'Aurelan': ({'muscle': 0.04}, {'torso/torso-vshape-incr': 0.25 if SEX == 'm' else 0.0, 'head/head-oval': 0.4}),
    'Ilvari': ({'muscle': -0.12, 'weight': -0.2},
               both({'torso/torso-scale-horiz-decr': 0.35, 'neck/measure-neck-height-incr': 0.6, 'neck/neck-scale-horiz-decr': 0.3,
                     '*ears/*-ear-shape-pointed': 1.0, '*ears/*-ear-scale-vert-incr': 0.6, '*ears/*-ear-rot-backward': 0.3,
                     'legs/measure-upperleg-height-incr': 0.35, 'legs/measure-lowerleg-height-incr': 0.3,
                     'head/head-scale-horiz-decr': 0.2, 'head/head-invertedtriangular': 0.4})),
    'Ferrin': ({'muscle': 0.2, 'weight': 0.2, 'height': -0.25},
               both({'torso/torso-scale-horiz-incr': 0.55, 'torso/torso-scale-depth-incr': 0.4, 'torso/torso-vshape-incr': 0.3,
                     'legs/measure-upperleg-height-decr': 0.7, 'legs/measure-lowerleg-height-decr': 0.6,
                     'legs/upperlegs-height-decr': 0.6, 'legs/lowerlegs-height-decr': 0.6, 'torso/torso-scale-vert-decr': 0.3,
                     'neck/measure-neck-height-decr': 0.7, 'neck/neck-scale-horiz-incr': 0.5,
                     'arms/measure-upperarm-length-decr': 0.35, 'arms/measure-lowerarm-length-decr': 0.3,
                     '*hands/*-hand-scale-incr': 0.3, 'head/head-square': 0.5, 'head/head-scale-horiz-incr': 0.2})),
    'Zarhim': ({'muscle': 0.08, 'weight': -0.32},
               both({'torso/torso-scale-horiz-decr': 0.15, 'neck/measure-neck-height-incr': 0.25, 'head/head-rectangular': 0.4})),
}
# a smooth chest under the paint: the painted chest wrap and shirts cannot hide modelled nipples
SMOOTH = {'breast/nipple-point-decr': 1.0, 'breast/nipple-size-decr': 1.0, **({'breast/breast-point-decr': 0.6} if SEX == 'f' else {})}
BUILDS = {'Lean': {'muscle': -0.25, 'weight': -0.28}, 'Heavy': {'muscle': -0.04, 'weight': 0.45}}

V0, F, FG = mh.load_obj()
KEEP = ('body', 'helper-l-eye', 'helper-r-eye')
faces = [f for f, gname in zip(F, FG) if gname in KEEP]
used = sorted({v for f in faces for v in f}); remap = {v: k for k, v in enumerate(used)}
faces = [[remap[v] for v in f] for f in faces]
USED = np.array(used)
EYES = np.array([remap[v] for v in sorted(set(mh.group_verts('helper-l-eye')) | set(mh.group_verts('helper-r-eye')))])

def make(people, build=None):
    mac, tg = PEOPLES[people]
    d = dict(M)
    for k, v in mac.items(): d[k] = d.get(k, 0.5) + v
    if build:
        for k, v in BUILDS[build].items(): d[k] = d.get(k, 0.5) + v
    d = {k: min(1.0, max(0.0, v)) for k, v in d.items()}
    return mh.shape(V0, mh.macro_stack(**d) + list(tg.items()) + list(SMOOTH.items()))

# skin weights, MakeHuman's game_engine bones merged onto ours
MAP = {'Root': 'hips', 'pelvis': 'hips', 'spine_01': 'hips', 'spine_02': 'spine', 'spine_03': 'chest', 'neck_01': 'neck', 'head': 'head'}
for s, S in (('l', 'L'), ('r', 'R')):
    MAP.update({f'clavicle_{s}': f'shoulder.{S}', f'upperarm_{s}': f'upper_arm.{S}', f'lowerarm_{s}': f'forearm.{S}', f'hand_{s}': f'hand.{S}',
                f'thigh_{s}': f'thigh.{S}', f'calf_{s}': f'shin.{S}', f'foot_{s}': f'foot.{S}', f'ball_{s}': f'foot.{S}'})
    for fg in ('thumb', 'index', 'middle', 'ring', 'pinky'):
        for n in (1, 2, 3): MAP[f'{fg}_0{n}_{s}'] = f'hand.{S}'
OURS = [n for n, *_ in g['BONES']]
W = np.zeros((len(V0), len(OURS)))
for b, lst in mh.WEIGHTS.items():
    k = OURS.index(MAP[b])
    for vi, w in lst: W[vi, k] += w
W = W[USED]
_none = W.sum(1) < 1e-6
W[_none, OURS.index('head')] = 1.0          # eyes and anything unweighted ride on the head
W /= W.sum(1, keepdims=True)
def bw(*names): return W[:, [OURS.index(n) for n in names]].sum(1)

def joints_of(V):
    J = {}
    for b in mh.RIG:
        h, t = mh.bone(V, b); J[b] = (mh.to_blender(h), mh.to_blender(t))
    return J

# ---------- 2. into our space: scaled to our height, feet on the ground, arms hanging at our rig's angle
ARM_DIR = {'ua': np.array([0.0857, 0.0, -0.2514]), 'fa': np.array([0.0675, 0.0, -0.2134])}   # the old rig's upper arm and forearm
for k in ARM_DIR: ARM_DIR[k] /= np.linalg.norm(ARM_DIR[k])
def rot_between(a, b):
    a = a / np.linalg.norm(a); b = b / np.linalg.norm(b); v = np.cross(a, b); c = float(np.dot(a, b))
    if np.linalg.norm(v) < 1e-9: return np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * (1 / (1 + c))
SCALE = None
def place(V):
    """MakeHuman vertices -> our space (scaled, grounded, arms posed). Returns points (used verts) and joint dict."""
    global SCALE
    P = mh.to_blender(V); J = joints_of(V)
    if SCALE is None: SCALE = HEIGHT / (P[USED, 2].max() - P[USED, 2].min())
    z0 = P[USED, 2].min()
    tf = lambda p: (p - np.array([0, 0, z0])) * SCALE
    global FULL
    FULL = tf(P); P = FULL[USED].copy(); J = {k: (tf(h), tf(t)) for k, (h, t) in J.items()}
    if 'NIP' in globals(): P = smooth_nipples(P)
    for s, sx in (('l', 1), ('r', -1)):
        flip = np.array([sx, 1, 1])
        S_ = J[f'upperarm_{s}'][0]; E = J[f'lowerarm_{s}'][0]; Wr = J[f'hand_{s}'][0]
        R1 = rot_between(E - S_, ARM_DIR['ua'] * flip)
        E2 = S_ + R1 @ (E - S_)
        R2 = rot_between(R1 @ (Wr - E), ARM_DIR['fa'] * flip) @ R1
        Mu = lambda p: S_ + (p - S_) @ R1.T
        Mf = lambda p: E2 + (p - E) @ R2.T
        S = s.upper()
        wu = bw(f'upper_arm.{S}')[:, None]; wf = (bw(f'forearm.{S}') + bw(f'hand.{S}'))[:, None]
        P = P * (1 - wu - wf) + Mu(P) * wu + Mf(P) * wf
        for b in list(J):
            if b.startswith('upperarm_' + s): J[b] = (Mu(J[b][0]), Mu(J[b][1]))
            elif b.startswith(('lowerarm_' + s, 'hand_' + s)) or (b.endswith('_' + s) and b.split('_')[0] in ('thumb', 'index', 'middle', 'ring', 'pinky')):
                J[b] = (Mf(J[b][0]), Mf(J[b][1]))
    return P, J

place(make('Human'))                     # the scale comes from the Human body, so every people keeps its own height
# the nipples, smoothed away on every shape (same points on every shape, so the morphs stay clean)
_ref = mh.to_blender(make('Human'))[USED]
NBR = [set() for _ in range(len(USED))]
for f in faces:
    for k in range(len(f)): NBR[f[k]].add(f[k - 1]); NBR[f[k]].add(f[(k + 1) % len(f)])
NBR = [np.array(sorted(n)) for n in NBR]
NIP = []   # the points MakeHuman's own nipple shapes move, a little beyond, weighted by how far they move
_ti, _to = mh.target('breast/nipple-size-incr')
_w = np.zeros(len(V0)); _w[_ti] = np.linalg.norm(_to, axis=1); _w = _w[USED]; _w /= _w.max()
_reg = np.where(_w > 0.02)[0]
for _ in range(2): _reg = np.unique(np.concatenate([_reg] + [NBR[i] for i in _reg]))
NIP.append((_reg, np.clip(np.maximum(_w[_reg] * 3, 0.35), 0, 1)))
print('NIPPLES', len(_reg), 'points')
def smooth_nipples(P):
    for m_, w in NIP:
        for _ in range(12):
            avg = np.array([P[NBR[i]].mean(axis=0) for i in m_])
            P[m_] += (avg - P[m_]) * (0.6 * w)[:, None]
    return P
PB, JB = place(make(PEOPLE))
TEETH = (FULL[mh.group_verts('helper-upper-teeth'), 2].min() + FULL[mh.group_verts('helper-lower-teeth'), 2].max()) / 2
KEYS = {}
for b in BUILDS: KEYS[b], _ = place(make(PEOPLE, b))
print('BODY', PEOPLE, SEX, 'scale', round(SCALE, 4), 'height', round(PB[:, 2].max(), 3))

# ---------- 4. our bones on MakeHuman's joints
J = JB; V3 = lambda a: Vector(tuple(a))
crown = PB[:, 2].max()
POS = {'hips': (J['pelvis'][0], J['spine_02'][0]), 'spine': (J['spine_02'][0], J['spine_03'][0]), 'chest': (J['spine_03'][0], J['neck_01'][0]),
       'neck': (J['neck_01'][0], J['head'][0]), 'head': (J['head'][0], np.array([0, J['head'][0][1], crown]))}
for s, S in (('l', 'L'), ('r', 'R')):
    POS[f'shoulder.{S}'] = J[f'clavicle_{s}']; POS[f'upper_arm.{S}'] = J[f'upperarm_{s}']; POS[f'forearm.{S}'] = J[f'lowerarm_{s}']
    POS[f'hand.{S}'] = (J[f'hand_{s}'][0], J[f'middle_03_{s}'][1]); POS[f'thigh.{S}'] = J[f'thigh_{s}']; POS[f'shin.{S}'] = J[f'calf_{s}']
    POS[f'foot.{S}'] = (J[f'foot_{s}'][0], J[f'ball_{s}'][1])
for nm in POS:   # the body is symmetric; keep the spine on the centre line
    h, t = POS[nm]
    if '.' not in nm: POS[nm] = (np.array([0, h[1], h[2]]), np.array([0, t[1], t[2]]))
bpy.context.view_layer.objects.active = arm; bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones
for nm, *_ in g['BONES']:
    h, t = POS[nm]; eb[nm].head = V3(h); eb[nm].tail = V3(t); eb[nm].roll = 0
REST_ARM = {s: [eb[f'upper_arm.{s}'].tail.copy(), eb[f'forearm.{s}'].tail.copy(), eb[f'hand.{s}'].tail.copy()] for s in ('L', 'R')}
g['BONES'][:] = [(nm, tuple(eb[nm].head), tuple(eb[nm].tail), par) for nm, h, t, par in g['BONES']]
bpy.ops.object.mode_set(mode='OBJECT'); upd()
for nm in ('hips', 'neck', 'upper_arm.L', 'forearm.L', 'hand.L', 'thigh.L', 'shin.L', 'foot.L'):
    print('BONE', nm, [round(x, 3) for x in POS[nm][0]], '->', [round(x, 3) for x in POS[nm][1]])

# ---------- 6. paint coordinates: where each point sits on the painted template (see the PAINT shader in creator/index.html)
# The paint is drawn in a fixed layout (the old template body): torso bands, nipples, navel, knees and the face's features at
# set heights. Each MakeHuman point is carried there by its own landmarks, so the paint lands on this body's anatomy.
def pl(z, A, B):
    A = np.asarray(A); B = np.asarray(B); out = np.interp(z, A, B)
    lo = z < A[0]; hi = z > A[-1]
    out[lo] = B[0] + (z[lo] - A[0]) * (B[1] - B[0]) / (A[1] - A[0]); out[hi] = B[-1] + (z[hi] - A[-1]) * (B[-1] - B[-2]) / (A[-1] - A[-2])
    return out
X, Y, Z = PB[:, 0], PB[:, 1], PB[:, 2]
armw = bw('upper_arm.L', 'forearm.L', 'hand.L', 'upper_arm.R', 'forearm.R', 'hand.R')
headw = bw('head', 'neck')
eye_c = PB[EYES]; eye_z = eye_c[:, 2].mean(); eye_x = np.abs(eye_c[:, 0]).mean()
mid = (np.abs(X) < 0.004) & (headw > 0.5) & (Y < np.median(Y[headw > 0.5]))      # the face's centre line, front half
fz, fy = Z[mid], Y[mid]
nose = fz[np.argmin(np.where((fz < eye_z) & (fz > eye_z - 0.08), fy, 9))]
below = (fz < nose - 0.01) & (fz > nose - 0.1)
# the mouth: between the teeth (MakeHuman's helper teeth sit just behind the lips); the chin: the lowest point of the face's front
mouth_z = TEETH
chin_pts = (fz < mouth_z - 0.015) & (fz > mouth_z - 0.09) & (fy < np.median(fy[(fz < mouth_z) & (fz > mouth_z - 0.03)]) + 0.03)
chin_z = fz[chin_pts].min() if chin_pts.any() else mouth_z - 0.05
neck_z = J['neck_01'][0][2] - 0.02
head_y = Y[headw > 0.5]; Cy = (head_y.min() + head_y.max()) / 2 + 0.01
ZM = [neck_z, chin_z, mouth_z, eye_z, crown]; ZCAN = [1.45, 1.57, 1.6175, 1.6865, 1.815]
KX = 0.0338 / eye_x
# torso and leg landmarks: ankle, knee, hip joint, navel, chest, collarbone
torso = (armw < 0.5) & (headw < 0.5)
ftr = torso & (np.abs(X) < 0.006) & (Y < 0)
tz, ty = Z[ftr], Y[ftr]
hipz = J['thigh_l'][0][2]
navel_z = hipz + 0.16
_near = torso & (np.abs(Z - navel_z) < 0.06) & (np.abs(X) < 0.004) & (Y < 0)
if _near.any():  # the navel is the deepest dent in the belly's front
    cand = np.where(_near)[0]; navel_z = Z[cand[np.argmax(Y[cand] - np.array([Y[_near & (np.abs(Z - Z[c]) < 0.03)].min() for c in cand]))]]
chest = torso & (np.abs(X) > 0.06) & (np.abs(X) < 0.14) & (Z > navel_z + 0.12) & (Z < J['neck_01'][0][2] - 0.05)
ci = np.where(chest)[0][np.argmin(Y[chest])]
chest_z, chest_x = Z[ci], abs(X[ci])
coll_z = J['clavicle_l'][0][2]
ZA = [J['foot_l'][0][2], J['calf_l'][0][2], hipz, navel_z, chest_z, coll_z]
ZB = [0.08, 0.52, 0.92, 1.088, 1.30 if SEX == 'f' else 1.317, 1.452]
print('PAINT face: neck chin mouth eye top', [round(float(z), 3) for z in ZM], 'eye x', round(float(eye_x), 4))
print('PAINT body: ankle knee hip navel chest collar', [round(float(z), 3) for z in ZA], 'chest x', round(float(chest_x), 3))
zt = pl(Z, ZA, ZB)
# across: the chest's width onto the template's, the hips' onto its; legs keep their own axis, moved onto the template's
sx_chest = 0.084 / chest_x; sx_hip = 0.095 / abs(J['thigh_l'][0][0])
sx = np.interp(zt, [0.92, 1.317], [sx_hip, sx_chest])
xt = X * sx
legs = (bw('thigh.L', 'thigh.R', 'shin.L', 'shin.R', 'foot.L', 'foot.R') > 0.5) & (zt < 0.95)
if legs.any():
    LJ = [J['foot_l'][0], J['calf_l'][0], J['thigh_l'][0]]
    axis_mh = np.interp(Z[legs], [p[2] for p in LJ], [abs(p[0]) for p in LJ])
    axis_t = np.interp(zt[legs], [0.08, 0.52, 0.92], [0.117, 0.11, 0.095])
    xt[legs] = np.sign(X[legs]) * (np.abs(X[legs]) - axis_mh + axis_t)
yt = Y.copy()
# the arms: each point keeps its place along its bone and its offset from it, on the template's arm
TARM = [np.array(p) for p in [(0.2, 0.03, 1.43), (0.255, 0.05, 1.17), (0.296, 0.03, 0.95), (0.315, 0.01, 0.70)]]
ax_, ay_, az_ = xt.copy(), yt.copy(), zt.copy()
for s, sgn in (('l', 1), ('r', -1)):
    S = s.upper(); CH = [J[f'upperarm_{s}'][0], J[f'lowerarm_{s}'][0], J[f'hand_{s}'][0], J[f'middle_03_{s}'][1]]
    sel = np.where((armw > 0.02) & (np.sign(X) == sgn))[0]
    if not len(sel): continue
    p = PB[sel]
    best = None
    for k in range(3):
        a, b = CH[k], CH[k + 1]; d = b - a; L = np.linalg.norm(d); u = d / L
        t = np.clip((p - a) @ u / L, 0, 1); dist = np.linalg.norm(p - (a + np.outer(t * L, u)), axis=1)
        if best is None: best = (dist, np.full(len(p), k), t)
        else:
            m_ = dist < best[0]; best[0][m_] = dist[m_]; best[1][m_] = k; best[2][m_] = t[m_]
    out = np.zeros_like(p)
    for k in range(3):
        m_ = best[1] == k
        if not m_.any(): continue
        a, b = CH[k], CH[k + 1]; ta, tb = TARM[k] * np.array([sgn, 1, 1]), TARM[k + 1] * np.array([sgn, 1, 1])
        L, Lt = np.linalg.norm(b - a), np.linalg.norm(tb - ta)
        R = rot_between(b - a, tb - ta)
        q = p[m_] - a; along = (q @ ((b - a) / L))[:, None] * ((b - a) / L)
        out[m_] = ta + (along * (Lt / L)) @ R.T + (q - along) @ R.T
    ax_[sel], ay_[sel], az_[sel] = out[:, 0], out[:, 1], out[:, 2]
a = np.clip(armw, 0, 1)
xt = xt * (1 - a) + ax_ * a; yt = yt * (1 - a) + ay_ * a; zt = zt * (1 - a) + az_ * a
# the face layout, blended in up the neck
fz_ = pl(Z, ZM, ZCAN)
t = np.array([sm(1.47, 1.555, z) for z in zt]) * (1 - a)
xt = xt + (X * KX - xt) * t; yt = yt + ((Y - Cy) * KX + 0.004 - yt) * t; zt = zt + (fz_ - zt) * t
REST = np.stack([xt + 0.5, yt + 0.5, zt / 2, 1 - a], axis=1)

# ---------- 7. the light mesh: MakeHuman's body brought down to a game budget, most of it kept in the face
# The reduction runs once, on the Human body, so every people and build gets the same light mesh (and they stay morphs of
# each other). Each light point is pinned to a spot on the full MakeHuman surface; every shape, skin weight and paint
# coordinate is read from the full body at that spot.
TRIS = int(os.environ.get('TRIS', '6000'))
REF = place(make('Human'))[0]
tri = np.array([t for f in faces for t in ([f[0], f[1], f[2]], [f[0], f[2], f[3]])[:len(f) - 2]])
hw = bw('head')
FACE = float(os.environ.get('FACE', '0.99'))   # just under 1 is enough: the collapse cost is very sensitive to it
LIGHT = os.environ.get('LIGHT', f'light_{SEX}.npz')   # the light mesh and its pins, made once and shared by every people
_c = np.load(LIGHT) if os.path.exists(LIGHT) else None
if _c is not None and (int(_c['tris']) != TRIS or float(_c['face']) != FACE or int(_c['full']) != len(REF)): _c = None
if _c is not None:
    LV, BT, BW_ = _c['LV'], _c['BT'], _c['BW']; LF = [tuple(int(x) for x in f) for f in _c['LF']]
    print('LIGHT mesh from', LIGHT)
else:
    rme = bpy.data.meshes.new('ref'); rme.from_pydata([tuple(p) for p in REF], [], faces); rme.update()
    rob = bpy.data.objects.new('ref', rme); col.objects.link(rob)
    keep = rob.vertex_groups.new(name='keep')     # how freely each point may be collapsed: the face least
    for i in range(len(REF)): keep.add([i], float(1 - (1 - FACE) * min(1.0, hw[i])), 'REPLACE')
    def decimate(ratio):
        for m_ in list(rob.modifiers): rob.modifiers.remove(m_)
        d = rob.modifiers.new('dec', 'DECIMATE'); d.decimate_type = 'COLLAPSE'; d.ratio = ratio
        d.use_symmetry = True; d.symmetry_axis = 'X'; d.use_collapse_triangulate = True
        d.vertex_group = 'keep'; d.invert_vertex_group = False; d.vertex_group_factor = float(os.environ.get('FACE_KEEP', '1'))
        dg = bpy.context.evaluated_depsgraph_get(); ev = rob.evaluated_get(dg); m2 = ev.to_mesh()
        V_ = np.array([tuple(v.co) for v in m2.vertices]); F_ = [tuple(p.vertices) for p in m2.polygons]
        ev.to_mesh_clear(); return V_, F_
    lo, hi_ = 0.02, 0.6
    for _ in range(14):     # find the ratio that lands on the budget
        r_ = (lo + hi_) / 2; LV, LF = decimate(r_)
        if len(LF) > TRIS: hi_ = r_
        else: lo = r_
    LV, LF = decimate(lo)
    bpy.data.objects.remove(rob, do_unlink=True)
    # which full-body triangle each light point lies on (eyes bind only to the eyes, the body only to the body)
    iseye = np.zeros(len(REF), bool); iseye[EYES] = True
    tri_eye = iseye[tri].all(1)
    par = list(range(len(LV)))
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for f in LF:
        for v in f[1:]: par[find(v)] = find(f[0])
    comp = np.array([find(i) for i in range(len(LV))])
    from mathutils.kdtree import KDTree
    kd = KDTree(len(REF))
    for i, p in enumerate(REF): kd.insert(Vector(p), i)
    kd.balance()
    near_eye = np.array([iseye[kd.find(Vector(p))[1]] for p in LV])
    eye_comp = {c for c in set(comp) if near_eye[comp == c].mean() > 0.5}
    BT = np.zeros((len(LV), 3), int); BW_ = np.zeros((len(LV), 3))
    for want_eye in (False, True):
        ts = np.where(tri_eye == want_eye)[0]
        tb = BVHTree.FromPolygons([tuple(REF[k]) for k in range(len(REF))], [tuple(tri[t]) for t in ts])
        for i in np.where(np.array([c in eye_comp for c in comp]) == want_eye)[0]:
            loc, _, fi, _ = tb.find_nearest(Vector(LV[i])); t = tri[ts[fi]]
            a_, b_, c_ = REF[t[0]], REF[t[1]], REF[t[2]]; p_ = np.array(loc)
            v0, v1, v2 = b_ - a_, c_ - a_, p_ - a_
            d00, d01, d11, d20, d21 = v0 @ v0, v0 @ v1, v1 @ v1, v2 @ v0, v2 @ v1
            den = d00 * d11 - d01 * d01 or 1e-12
            v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den
            BT[i] = t; BW_[i] = np.clip([1 - v - w, v, w], 0, 1); BW_[i] /= BW_[i].sum()
    np.savez(LIGHT, LV=LV, LF=np.array(LF), BT=BT, BW=BW_, tris=TRIS, face=FACE, full=len(REF))
    print('LIGHT mesh saved to', LIGHT)
def bind(A): return np.einsum('ij,ij...->i...', BW_, A[BT])
LP = bind(PB); LK = {k: bind(P) for k, P in KEYS.items()}; LW = bind(W); LR = bind(REST)
_lh = bind(hw); headtris = sum(1 for f in LF if _lh[list(f)].mean() > 0.5)
print('LIGHT', len(LF), 'triangles,', headtris, 'on the head;', len(LV), 'points (full body', len(tri), 'triangles)')

me = bpy.data.meshes.new('Body'); me.from_pydata([tuple(p) for p in LP], [], LF); me.update()
body = bpy.data.objects.new('Body', me); col.objects.link(body)
for p in me.polygons: p.use_smooth = True
body.shape_key_add(name='Basis')
for nm, P in LK.items():
    k = body.shape_key_add(name=nm)
    for i, p in enumerate(P): k.data[i].co = Vector(p)
for nm in OURS: body.vertex_groups.new(name=nm)
top4 = np.argsort(-LW, axis=1)[:, :4]
for i in range(len(LP)):
    ks = [k for k in top4[i] if LW[i, k] > 1e-3]; tot = sum(LW[i, k] for k in ks)
    for k in ks: body.vertex_groups[k].add([i], float(LW[i, k] / tot), 'REPLACE')
body.parent = arm; body.modifiers.new('Armature', 'ARMATURE').object = arm
ca = me.color_attributes.new('rest', 'FLOAT_COLOR', 'POINT')
for i in range(len(LP)): ca.data[i].color = tuple(float(x) for x in LR[i])
me.color_attributes.active_color = ca
me.materials.append(bpy.data.materials.new('Body'))

# ---------- 8. hair, beards and moustaches: the old ones, carried onto this head by the same face landmarks
HAIRS = []
import tempfile, shutil
tmp = os.path.join(tempfile.mkdtemp(), 'old.gltf'); shutil.copy(OLD, tmp)
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=tmp)
new = [o for o in bpy.data.objects if o not in before]
oldbody = next(o for o in new if o.type == 'MESH' and o.data.shape_keys and 'Lean' in o.data.shape_keys.key_blocks)
def world_verts(o): return np.array([tuple(o.matrix_world @ v.co) for v in o.data.vertices])
OB = world_verts(oldbody)
oc = oldbody.data.color_attributes[0]
if oc.domain == 'POINT': OR = np.array([tuple(oc.data[i].color) for i in range(len(OB))])
else:
    OR = np.zeros((len(OB), 4))
    for lp in oldbody.data.loops: OR[lp.vertex_index] = tuple(oc.data[lp.index].color)
if OR is not None and OR.max() > 1.5: OR /= 255.0
def old_landmark(zc):   # the old body's height for a template height, on its face's front
    rz = OR[:, 2] * 2
    for tol in (0.004, 0.008, 0.015):
        m_ = (np.abs(rz - zc) < tol) & (np.abs(OR[:, 0] - 0.5) < 0.04) & (OR[:, 1] - 0.5 < -0.02)
        if m_.sum() >= 3: return float(np.median(OB[m_, 2]))
    raise SystemExit(f'old body has no face point at template height {zc}')
OZ = [old_landmark(z) for z in ZCAN[:-1]] + [float(OB[:, 2].max())]
print('OLD face heights', OZ)
def width_at(P, z, band=0.006, sel=None):
    m_ = np.abs(P[:, 2] - z) < band
    if sel is not None: m_ &= sel
    return (np.abs(P[m_, 0]).max(), P[m_, 1].min(), P[m_, 1].max()) if m_.any() else None
old_head = OB[:, 2] > OZ[0]; new_head = (headw > 0.5)
bvh = BVHTree.FromPolygons([tuple(p) for p in LP], LF)
for o in new:
    if o.type != 'MESH' or o is oldbody or not o.name.startswith(('Hair_', 'Beard_', 'Moustache_')): continue
    P = world_verts(o); Q = P.copy()
    zn = pl(pl(P[:, 2], OZ, ZCAN), ZCAN, ZM)            # old height -> template -> this head
    for i in range(len(P)):
        wo = width_at(OB, P[i, 2], sel=old_head) or width_at(OB, P[i, 2])
        wn = width_at(PB, zn[i], sel=new_head) or width_at(PB, zn[i])
        if wo and wn:
            sxx = wn[0] / max(wo[0], 1e-3); oc_ = (wo[1] + wo[2]) / 2; nc_ = (wn[1] + wn[2]) / 2
            syy = (wn[2] - wn[1]) / max(wo[2] - wo[1], 1e-3)
            Q[i] = (P[i, 0] * sxx, nc_ + (P[i, 1] - oc_) * syy, zn[i])
        else: Q[i, 2] = zn[i]
    for i in range(len(Q)):   # nothing may sink into the new head
        loc, nor, _, _ = bvh.find_nearest(Vector(Q[i]))
        if loc is not None and (Vector(Q[i]) - loc).dot(nor) < 0.002: Q[i] = tuple(loc + nor * 0.002)
    m2 = o.data.copy()
    _bm = bmesh.new(); _bm.from_mesh(m2)            # drop the old model's skin weights (stale group indices)
    for _l in list(_bm.verts.layers.deform): _bm.verts.layers.deform.remove(_l)
    _bm.to_mesh(m2); _bm.free()
    for v, q in zip(m2.vertices, Q): v.co = Vector(q)
    h = bpy.data.objects.new(o.name, m2); col.objects.link(h); h.vertex_groups.clear(); HAIRS.append(h)
for o in new: bpy.data.objects.remove(o, do_unlink=True)
for m_ in list(bpy.data.meshes):
    if m_.users == 0: bpy.data.meshes.remove(m_)
for h in HAIRS: h.name = h.name.split('.')[0]; h.data.name = h.name
body.data.name = 'Body'
for h in HAIRS:
    h.matrix_world = Matrix()
    dt = h.modifiers.new('DT', 'DATA_TRANSFER'); dt.object = body; dt.use_vert_data = True
    dt.data_types_verts = {'VGROUP_WEIGHTS'}; dt.vert_mapping = 'POLYINTERP_NEAREST'; dt.layers_vgroup_select_src = 'ALL'; dt.layers_vgroup_select_dst = 'NAME'
    with bpy.context.temp_override(object=h, active_object=h):
        bpy.ops.object.datalayout_transfer(modifier='DT'); bpy.ops.object.modifier_apply(modifier='DT')
    keep = {h.vertex_groups[n].index for n in ('head', 'neck') if n in h.vertex_groups}
    hi = h.vertex_groups['head'].index if 'head' in h.vertex_groups else h.vertex_groups.new(name='head').index
    for v in h.data.vertices:
        ws = {gv.group: gv.weight for gv in v.groups if gv.group in keep}; tot = sum(ws.values())
        for gv in list(v.groups):
            if gv.group not in keep and gv.group < len(h.vertex_groups): h.vertex_groups[gv.group].remove([v.index])
        if tot < 1e-4: h.vertex_groups[hi].add([v.index], 1.0, 'REPLACE')
        else:
            for gi, w in ws.items(): h.vertex_groups[gi].add([v.index], w / tot, 'REPLACE')
    h.modifiers.new('Armature', 'ARMATURE').object = arm; h.parent = arm
print('HAIR', [h.name for h in HAIRS])

# ---------- 9. idle and walk (as rpgbody.py): chest up, arms hanging out and down
for a_ in list(bpy.data.actions):
    if a_.name in ('Idle', 'Walk', 'Aim'): bpy.data.actions.remove(a_)
pose, bake = g['pose'], g['bake']
def arms(sw=0.0, br=0.0):
    out = []
    for sx_, side in ((1, 'L'), (-1, 'R')):
        k = sw * (1 if side == 'L' else -1)
        e, w, h = REST_ARM[side]
        out += [(f'upper_arm.{side}', (e[0] + 0.01 * sx_, e[1] + 0.07 * k, e[2] + br)),
                (f'forearm.{side}', (w[0] - 0.01 * sx_, w[1] + 0.14 * k - 0.04 * abs(sw), w[2] + br + 0.01)),
                (f'hand.{side}', (h[0] - 0.015 * sx_, h[1] + 0.18 * k - 0.05 * abs(sw), h[2] + br + 0.02))]
    return out
def idle2(f):
    ph = 2 * math.pi * f / 48; b = math.sin(ph)
    d = {'spine': (-0.02, 0, 0), 'chest': (-0.07 + 0.015 * b, 0, 0), 'neck': (0.07 - 0.012 * b, 0, 0), 'head': (0.01, 0, 0.04 * math.sin(ph * 0.5)),
         'thigh.L': (0.07, -0.07, 0), 'thigh.R': (0.07, -0.07, 0), 'shin.L': (-0.13, 0, 0), 'shin.R': (-0.13, 0, 0), 'foot.L': (0.06, 0.05, 0), 'foot.R': (0.06, 0.05, 0)}
    return d, -0.012 - 0.004 * (1 - math.cos(ph)) / 2, arms(0.0, 0.004 * b)
def walk2(f):
    ph = 2 * math.pi * f / 24; s, c = math.sin(ph), math.cos(ph)
    d = {'thigh.L': (0.5 * s, -0.03, 0), 'thigh.R': (-0.5 * s, -0.03, 0),
         'shin.L': (-(0.1 + 0.75 * max(0, c)), 0, 0), 'shin.R': (-(0.1 + 0.75 * max(0, -c)), 0, 0),
         'foot.L': (0.25 * max(0, -s) - 0.15 * max(0, s), 0, 0), 'foot.R': (0.25 * max(0, s) - 0.15 * max(0, -s), 0, 0),
         'hips': (0, 0, -0.08 * s), 'spine': (0.03, 0, 0.08 * s), 'chest': (-0.04, 0, 0.07 * s), 'neck': (0.03, 0, -0.1 * s)}
    return d, -0.03 * (1 - abs(c)), arms(s, 0.008 * abs(c))
arm.data.pose_position = 'POSE'
bake('Idle', range(0, 49, 4), idle2)
bake('Walk', range(0, 25, 2), walk2)
arm.animation_data.action = None; pose({})
bpy.ops.object.select_all(action='DESELECT'); body.select_set(True); arm.select_set(True)
for h in HAIRS: h.select_set(True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', use_selection=True, export_animations=True, export_animation_mode='ACTIONS',
                          export_skins=True, export_materials='EXPORT', export_force_sampling=True, export_vertex_color='ACTIVE',
                          export_morph=True, export_morph_normal=True)
print('EXPORTED', OUT)
