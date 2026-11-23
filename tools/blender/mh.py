# MakeHuman body data, read straight from MPFB's CC0 files (no Blender needed).
# The base mesh (hm08), its shape targets and the game_engine rig's joints and skin weights.
# Every body made here shares one mesh: same vertices, same order, so any two are morph targets of each other.
# MPFB_DATA points at mpfb2/src/mpfb/data (git clone https://github.com/makehumancommunity/mpfb2).
import os, gzip, json
import numpy as np

DATA = os.environ.get('MPFB_DATA', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'source', 'mpfb2', 'src', 'mpfb', 'data'))


def load_obj():
    """Vertices (MakeHuman units: decimetres, y up), faces as vertex index lists, and the face groups."""
    V, F, G = [], [], []
    grp = None
    for ln in open(os.path.join(DATA, '3dobjs', 'base.obj')):
        if ln.startswith('v '):
            V.append([float(t) for t in ln.split()[1:4]])
        elif ln.startswith('g '):
            grp = ln.split(None, 1)[1].strip()
        elif ln.startswith('f '):
            F.append([int(t.split('/')[0]) - 1 for t in ln.split()[1:]]); G.append(grp)
    return np.array(V, dtype=np.float64), F, G


_TCACHE = {}
def target(name):
    """A target file as (vertex indices, offsets)."""
    if name in _TCACHE: return _TCACHE[name]
    idx, off = [], []
    with gzip.open(os.path.join(DATA, 'targets', name + '.target.gz'), 'rt') as f:
        for ln in f:
            if not ln.strip() or ln.startswith('#'): continue
            t = ln.split(); idx.append(int(t[0])); off.append([float(t[1]), float(t[2]), float(t[3])])
    r = (np.array(idx, dtype=np.int64), np.array(off, dtype=np.float64).reshape(-1, 3)); _TCACHE[name] = r
    return r


MACRO = json.load(open(os.path.join(DATA, 'targets', 'macrodetails', 'macro.json')))['macrotargets']
def _parts(name, value):
    out = []
    for p in MACRO[name]['parts']:
        lo, hi = p['lowest'], p['highest']
        if lo < value < hi:
            t = (value - lo) / (hi - lo)
            if p['low']: out.append((p['low'], round(1 - t, 4)))
            if p['high']: out.append((p['high'], round(t, 4)))
    return out


def macro_stack(gender=1.0, age=0.5, muscle=0.5, weight=0.5, proportions=0.5, height=0.5, cupsize=0.5, firmness=0.5,
                race=None, cutoff=0.01):
    """The weighted target list for MakeHuman's macro sliders, as MPFB's TargetService computes it."""
    race = race or {'african': 1 / 3, 'asian': 1 / 3, 'caucasian': 1 / 3}
    c = {k: _parts(k, v) for k, v in dict(gender=gender, age=age, muscle=muscle, weight=weight, proportions=proportions,
                                           height=height, cupsize=cupsize, firmness=firmness).items()}
    out = []
    for r, rw in race.items():
        for a, aw in c['age']:
            for g, gw in c['gender']:
                w = rw * gw * aw
                if w > cutoff: out.append((f'macrodetails/{r}-{g}-{a}', w))
    for g, gw in c['gender']:
        for a, aw in c['age']:
            for m, mw in c['muscle']:
                for wt, ww in c['weight']:
                    base = gw * aw * mw * ww
                    if base > cutoff: out.append((f'macrodetails/universal-{g}-{a}-{m}-{wt}', base))
                    for h, hw in c['height']:
                        if base * hw > cutoff: out.append((f'macrodetails/height/{g}-{a}-{m}-{wt}-{h}', base * hw))
                    for pr, pw in c['proportions']:
                        if base * pw > cutoff: out.append((f'macrodetails/proportions/{g}-{a}-{m}-{wt}-{pr}', base * pw))
                    if g == 'female':
                        for cu, cw in c['cupsize']:
                            for fi, fw in c['firmness']:
                                w = aw * mw * ww * cw * fw
                                nm = f'breast/female-{a}-{m}-{wt}-{cu}-{fi}'
                                if w > cutoff and 'averagecup-averagefirmness' not in nm and '-baby-' not in nm: out.append((nm, w))
    return out


def shape(base, stack):
    """The base mesh with a list of (target, weight) applied."""
    V = base.copy()
    for nm, w in stack:
        i, o = target(nm); V[i] += w * o
    return V


GROUPS = json.load(open(os.path.join(DATA, 'mesh_metadata', 'basemesh_vertex_groups.json')))
def group_verts(name):
    out = []
    for a, b in GROUPS[name]: out.extend(range(a, b + 1))
    return out


RIG = json.load(open(os.path.join(DATA, 'rigs', 'standard', 'rig.game_engine.json')))
WEIGHTS = json.load(open(os.path.join(DATA, 'rigs', 'standard', 'weights.game_engine.json')))['weights']
def joint(V, spec):
    if spec['strategy'] == 'CUBE': return V[group_verts(spec['cube_name'])].mean(axis=0)
    if spec['strategy'] in ('MEAN', 'VERTEX'): return V[spec.get('vertex_indices') or [spec['vertex_index']]].mean(axis=0)
    raise ValueError(spec['strategy'])
def bone(V, name):
    b = RIG[name]; return joint(V, b['head']), joint(V, b['tail'])


def to_blender(P):
    """MakeHuman (decimetres, y up, facing +z) to Blender (metres, z up, facing -y)."""
    P = np.asarray(P) * 0.1
    return np.stack([P[..., 0], -P[..., 2], P[..., 1]], axis=-1)
