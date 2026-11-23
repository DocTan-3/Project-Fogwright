# Merge per-people bodies into one model: the base body gains each people's shape as a morph target,
# and the file records each people's joint positions so the game can move the skeleton to match.
# usage: python merge_peoples.py base.glb out.glb Name=other.glb [Name=other.glb ...]
# Every body must come from the same rig script run (same vertices, same order).
import json, struct, sys, math

def load(f):
    d = open(f, 'rb').read(); ln, _ = struct.unpack('<II', d[12:20]); j = json.loads(d[20:20 + ln])
    o = 20 + ln; bl, _ = struct.unpack('<II', d[o:o + 8]); return j, bytearray(d[o + 8:o + 8 + bl])

def read(j, b, i):
    a = j['accessors'][i]; bv = j['bufferViews'][a['bufferView']]; off = bv.get('byteOffset', 0) + a.get('byteOffset', 0)
    n = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[a['type']]
    stride = bv.get('byteStride', 4 * n)
    return [struct.unpack_from('<' + 'f' * n, b, off + k * stride) for k in range(a['count'])]

def body_prim(j):
    for m in j['meshes']:
        p = m['primitives'][0]
        if p.get('targets'): return m, p
    raise SystemExit('no body mesh with morph targets')

def quat_mat(q):
    x, y, z, w = q
    return [[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
            [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
            [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]]

def joint_world(j):
    """World position of every named node, from the node hierarchy at rest."""
    parent = {}
    for i, n in enumerate(j['nodes']):
        for c in n.get('children', []): parent[c] = i
    cache = {}
    def world(i):
        if i in cache: return cache[i]
        n = j['nodes'][i]
        t = n.get('translation', [0, 0, 0]); r = quat_mat(n.get('rotation', [0, 0, 0, 1])); s = n.get('scale', [1, 1, 1])
        R = [[r[a][c] * s[c] for c in range(3)] for a in range(3)]
        if i in parent:
            PR, PT = world(parent[i])
            T = [sum(PR[a][c] * t[c] for c in range(3)) + PT[a] for a in range(3)]
            R = [[sum(PR[a][k] * R[k][c] for k in range(3)) for c in range(3)] for a in range(3)]
        else: T = list(t)
        cache[i] = (R, T); return cache[i]
    skin = j['skins'][0]['joints']
    return {j['nodes'][i]['name']: [round(v, 5) for v in world(i)[1]] for i in skin}

base, out = sys.argv[1], sys.argv[2]
others = [a.split('=', 1) for a in sys.argv[3:]]
J, B = load(base); M, P = body_prim(J)
pos0 = read(J, B, P['attributes']['POSITION']); nor0 = read(J, B, P['attributes']['NORMAL'])
names = M.setdefault('extras', {}).setdefault('targetNames', [])
joints = {'Human': joint_world(J)}

def add_accessor(vals, minmax):
    global B
    while len(B) % 4: B.append(0)
    off = len(B)
    for v in vals: B += struct.pack('<3f', *v)
    J['bufferViews'].append({'buffer': 0, 'byteOffset': off, 'byteLength': len(vals) * 12})
    a = {'bufferView': len(J['bufferViews']) - 1, 'componentType': 5126, 'count': len(vals), 'type': 'VEC3'}
    if minmax:
        a['min'] = [min(v[k] for v in vals) for k in range(3)]; a['max'] = [max(v[k] for v in vals) for k in range(3)]
    J['accessors'].append(a); return len(J['accessors']) - 1

for name, f in others:
    j, b = load(f); m, p = body_prim(j)
    pos = read(j, b, p['attributes']['POSITION']); nor = read(j, b, p['attributes']['NORMAL'])
    if len(pos) != len(pos0): raise SystemExit(f'{f}: {len(pos)} vertices, base has {len(pos0)}')
    dp = [tuple(a - c for a, c in zip(v, v0)) for v, v0 in zip(pos, pos0)]
    dn = [tuple(a - c for a, c in zip(v, v0)) for v, v0 in zip(nor, nor0)]
    P['targets'].append({'POSITION': add_accessor(dp, True), 'NORMAL': add_accessor(dn, False)})
    names.append(name); joints[name] = joint_world(j)
    print(name, 'max shift', round(max(math.sqrt(sum(c * c for c in d)) for d in dp), 3))

# a morph needs a weight on the mesh node too
for n in J['nodes']:
    if n.get('mesh') == J['meshes'].index(M) and 'weights' in n: n['weights'] += [0.0] * len(others)
if 'weights' in M: M['weights'] += [0.0] * len(others)
J['scenes'][J.get('scene', 0)].setdefault('extras', {})['peopleJoints'] = joints
J['buffers'][0]['byteLength'] = len(B)
js = json.dumps(J, separators=(',', ':')).encode()
while len(js) % 4: js += b' '
while len(B) % 4: B.append(0)
glb = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(B)) + struct.pack('<II', len(js), 0x4E4F534A) + js + struct.pack('<II', len(B), 0x004E4942) + bytes(B)
open(out, 'wb').write(glb)
print('targets', names, 'bytes', len(glb))
