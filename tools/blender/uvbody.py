# Give a finished body model a texture layout, so its paint (skin, face, clothes, painted armour) can be baked into
# one texture per character, the way World of Warcraft composites its character skins.
# usage (Blender's bpy module): python uvbody.py in.gltf.json [out.gltf.json]
# The body (the mesh with morph targets) is unwrapped on its base shape. Points on a seam are split in two, and every
# attribute, morph target and the index list follow, so the model still works everywhere it did. The head gets more
# texture space than the rest of the body, because the face carries the finest paint.
import sys, json, base64, struct
import numpy as np
import bpy, bmesh

src = sys.argv[sys.argv.index('--') + 1] if '--' in sys.argv else sys.argv[1]
dst = (sys.argv[sys.argv.index('--') + 2] if '--' in sys.argv and len(sys.argv) > sys.argv.index('--') + 2 else
       sys.argv[2] if '--' not in sys.argv and len(sys.argv) > 2 else src)
HEAD_SCALE = 1.8          # the head's texture space, relative to the body's
J = json.load(open(src))
BUF = bytearray(base64.b64decode(J['buffers'][0]['uri'].split(',', 1)[1]))

CT = {5126: ('f', 4, np.float32), 5125: ('I', 4, np.uint32), 5123: ('H', 2, np.uint16), 5121: ('B', 1, np.uint8)}
NC = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
def _view(vi, off0, count, ct, n):
    v = J['bufferViews'][vi]; _, sz, dt = CT[ct]
    off = v.get('byteOffset', 0) + off0; stride = v.get('byteStride', sz * n)
    raw = np.frombuffer(bytes(BUF[off:off + stride * (count - 1) + sz * n]), dtype=np.uint8)
    return np.lib.stride_tricks.as_strided(raw, shape=(count, sz * n), strides=(stride, 1)).copy().view(dt).reshape(count, n)
def read(i):
    a = J['accessors'][i]; n = NC[a['type']]; dt = CT[a['componentType']][2]
    out = _view(a['bufferView'], a.get('byteOffset', 0), a['count'], a['componentType'], n) if 'bufferView' in a else np.zeros((a['count'], n), dtype=dt)
    sp = a.get('sparse')
    if sp:   # sparse storage (Blender writes morph targets this way): a few points carry values, the rest are zero
        ix = _view(sp['indices']['bufferView'], sp['indices'].get('byteOffset', 0), sp['count'], sp['indices']['componentType'], 1)[:, 0]
        out = out.copy(); out[ix.astype(np.int64)] = _view(sp['values']['bufferView'], sp['values'].get('byteOffset', 0), sp['count'], a['componentType'], n)
    return out
NEW = []   # (accessor dict, bytes) to append
def write(arr, like=None, ctype=None, minmax=False):
    arr = np.ascontiguousarray(arr); n = arr.shape[1] if arr.ndim > 1 else 1
    ct = ctype if ctype else {np.float32: 5126, np.uint32: 5125, np.uint16: 5123, np.uint8: 5121}[arr.dtype.type]
    a = {'componentType': ct, 'count': len(arr), 'type': {1: 'SCALAR', 2: 'VEC2', 3: 'VEC3', 4: 'VEC4'}[n]}
    if like is not None and J['accessors'][like].get('normalized'): a['normalized'] = True
    if minmax: a['min'] = arr.min(0).tolist() if n > 1 else [float(arr.min())]; a['max'] = arr.max(0).tolist() if n > 1 else [float(arr.max())]
    NEW.append((a, arr.tobytes())); return len(J['accessors']) + len(NEW) - 1

mesh = next(m for m in J['meshes'] if m['primitives'][0].get('targets'))
prim = mesh['primitives'][0]
if 'TEXCOORD_0' in prim['attributes']: raise SystemExit(src + ' already has a texture layout')
P = read(prim['attributes']['POSITION']).astype(np.float64)
TRI = read(prim['indices']).reshape(-1, 3).astype(np.int64)
REST = read(prim['attributes']['COLOR_0'])
REST = REST.astype(np.float64) / (65535.0 if REST.dtype == np.uint16 else 255.0 if REST.dtype == np.uint8 else 1.0)
restz = REST[:, 2] * 2                                   # paint template height (see preparePainted)

# ---------- unwrap in Blender: the head and the body separately (so the head can take more space), then packed together
bpy.ops.wm.read_factory_settings(use_empty=True)
me = bpy.data.meshes.new('b'); me.from_pydata([(x, -z, y) for x, y, z in P], [], [tuple(t) for t in TRI]); me.update()
ob = bpy.data.objects.new('b', me); bpy.context.collection.objects.link(ob); bpy.context.view_layer.objects.active = ob; ob.select_set(True)
# Seams are cut the way a texture artist would: around the neck, wrists, hips and ankles where the parts meet, down the
# middle of the back and the back of the head, along the inner side of each arm and leg, and round each hand's edge. Positions are the paint
# template's (rest coordinates), so the cuts land in the same places on every body.
C = REST[TRI].mean(1); cx, cy, cz, tor = C[:, 0] - 0.5, C[:, 1] - 0.5, C[:, 2] * 2, C[:, 3]
ARM = np.array([(0.2, 0.03, 1.43), (0.255, 0.05, 1.17), (0.296, 0.03, 0.95), (0.315, 0.01, 0.70)])
arm_x = lambda z: np.interp(-z, -ARM[:, 2], ARM[:, 0])
region = np.empty(len(TRI), dtype=object)
for f in range(len(TRI)):
    sd = 'L' if cx[f] > 0 else 'R'
    if tor[f] < 0.5: region[f] = ('hand' if cz[f] < 0.95 else 'arm') + sd
    elif cz[f] > 1.53: region[f] = 'head'
    elif cz[f] < 0.12: region[f] = 'foot' + sd
    elif cz[f] < 0.92 and not (cz[f] > 0.8 and abs(cx[f]) < 0.035): region[f] = 'leg' + sd
    else: region[f] = 'torso'
head = region == 'head'
bm = bmesh.new(); bm.from_mesh(me); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
nseam = 0
for e in bm.edges:
    fs = [f.index for f in e.link_faces]
    if len(fs) != 2: continue
    a, b = fs; ra, rb = region[a], region[b]; cut = ra != rb
    if not cut and ra in ('torso', 'head'):                   # down the middle of the back
        cut = cy[a] > 0 and cy[b] > 0 and (cx[a] > 0) != (cx[b] > 0)
    elif not cut and ra.startswith('arm'):                    # along the inner side of the arm
        cut = abs(cx[a]) < arm_x(cz[a]) and abs(cx[b]) < arm_x(cz[b]) and (cy[a] > 0.03) != (cy[b] > 0.03)
    elif not cut and ra.startswith('hand'):                   # the hand opens into its palm and its back
        cut = (abs(cx[a]) < arm_x(cz[a])) != (abs(cx[b]) < arm_x(cz[b]))
    elif not cut and ra.startswith('leg'):                    # along the inner side of the leg
        cut = abs(cx[a]) < 0.11 and abs(cx[b]) < 0.11 and (cy[a] > 0.0) != (cy[b] > 0.0)
    e.seam = bool(cut); nseam += int(bool(cut))
bm.to_mesh(me); bm.free()
print('SEAMS', nseam, 'edges;', 'regions', {r: int((region == r).sum()) for r in sorted(set(region))})
uvl = me.uv_layers.new(name='UV')
for d_ in uvl.data: d_.uv = (0.0, 0.0)       # so any face the unwrap cannot solve shows up as empty
bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.0)
bpy.ops.object.mode_set(mode='OBJECT')
# closed pieces with no seam (the eyeballs) cannot be unwrapped that way: project those
def tri_area(poly):
    u = [me.uv_layers.active.data[li].uv for li in poly.loop_indices]
    return abs((u[1][0] - u[0][0]) * (u[2][1] - u[0][1]) - (u[2][0] - u[0][0]) * (u[1][1] - u[0][1]))
failed = [p_.index for p_ in me.polygons if tri_area(p_) < 1e-12]
if failed:
    # each is mapped flat along the way it faces (the eyes from the front, the soles from below); each direction is its
    # own island, so front and back never overlap
    for fi in failed:
        poly = me.polygons[fi]; n_ = poly.normal; ax_ = int(np.argmax(np.abs(n_))); sg = 1 if n_[ax_] > 0 else 0
        a_, b_ = [(1, 2), (0, 2), (0, 1)][ax_]; off = (ax_ * 2 + sg) * 3.0
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers.active.data[li].uv = (co[a_] * (1 if sg else -1) + off, co[b_])
    print('PROJECTED', len(failed), 'faces the unwrap could not solve (eyes, soles), flat along the way each faces')
# scale the head's islands, then pack everything
bpy.ops.object.mode_set(mode='EDIT'); bm = bmesh.from_edit_mesh(me); uv = bm.loops.layers.uv.active
for f in bm.faces:
    if head[f.index]:
        for l in f.loops: l[uv].uv = l[uv].uv * HEAD_SCALE
    f.select = True
bmesh.update_edit_mesh(me)
bpy.ops.uv.select_all(action='SELECT')
bpy.ops.uv.pack_islands(rotate=True, margin=0.006)
bpy.ops.object.mode_set(mode='OBJECT')
LUV = np.zeros((len(TRI), 3, 2))
for poly in me.polygons:
    for k, li in enumerate(poly.loop_indices): LUV[poly.index, k] = me.uv_layers.active.data[li].uv
# Blender keeps each face's corner order, so LUV[f, k] belongs to TRI[f, k]

# ---------- split the points that sit on a seam
key = {}; src_of = []; nuv = []; NT = np.zeros_like(TRI)
for f in range(len(TRI)):
    for k in range(3):
        v = int(TRI[f, k]); u = (round(LUV[f, k, 0], 5), round(LUV[f, k, 1], 5)); kk = (v, u)
        if kk not in key: key[kk] = len(src_of); src_of.append(v); nuv.append(u)
        NT[f, k] = key[kk]
src_of = np.array(src_of); UV = np.array(nuv, dtype=np.float32); UV[:, 1] = 1.0 - UV[:, 1]   # glTF: v runs down
print('UV', src, 'points', len(P), '->', len(src_of), 'seams split', len(src_of) - len(P), 'head scale', HEAD_SCALE)

def remap(i, minmax=False):
    a = J['accessors'][i]; arr = read(i)[src_of]
    return write(arr, like=i, ctype=a['componentType'], minmax=minmax or ('min' in a))
attrs = {k: remap(v, k == 'POSITION') for k, v in prim['attributes'].items()}
attrs['TEXCOORD_0'] = write(UV)
idx_t = np.uint16 if len(src_of) < 65536 else np.uint32
prim['indices'] = write(NT.reshape(-1, 1).astype(idx_t))
prim['attributes'] = attrs
prim['targets'] = [{k: remap(v, k == 'POSITION') for k, v in t.items()} for t in prim['targets']]

# ---------- write the new accessors and repack the buffer with only what is still used
for a, b in NEW:
    while len(BUF) % 4: BUF.append(0)
    J['bufferViews'].append({'buffer': 0, 'byteOffset': len(BUF), 'byteLength': len(b)}); BUF += b
    a['bufferView'] = len(J['bufferViews']) - 1; J['accessors'].append(a)
used_acc = set()
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ('POSITION', 'NORMAL', 'COLOR_0', 'JOINTS_0', 'WEIGHTS_0', 'TEXCOORD_0', 'indices', 'input', 'output', 'inverseBindMatrices') and isinstance(v, int): used_acc.add(v)
            else: walk(v)
    elif isinstance(o, list):
        for v in o: walk(v)
walk({k: J[k] for k in ('meshes', 'animations', 'skins') if k in J})
acc_map = {}; accs = []
for i in sorted(used_acc): acc_map[i] = len(accs); accs.append(J['accessors'][i])
views = []; out = bytearray(); view_map = {}
def keep(vi):
    if vi not in view_map:
        v = dict(J['bufferViews'][vi]); s = v.get('byteOffset', 0)
        while len(out) % 4: out.append(0)
        chunk = BUF[s:s + v['byteLength']]; v['byteOffset'] = len(out); out.extend(chunk); view_map[vi] = len(views); views.append(v)
    return view_map[vi]
for a in accs:
    if 'bufferView' in a: a['bufferView'] = keep(a['bufferView'])
    if 'sparse' in a: a['sparse']['indices']['bufferView'] = keep(a['sparse']['indices']['bufferView']); a['sparse']['values']['bufferView'] = keep(a['sparse']['values']['bufferView'])
def fix(o):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if k in ('POSITION', 'NORMAL', 'COLOR_0', 'JOINTS_0', 'WEIGHTS_0', 'TEXCOORD_0', 'indices', 'input', 'output', 'inverseBindMatrices') and isinstance(v, int): o[k] = acc_map[v]
            else: fix(v)
    elif isinstance(o, list):
        for v in o: fix(v)
fix({k: J[k] for k in ('meshes', 'animations', 'skins') if k in J})
J['accessors'] = accs; J['bufferViews'] = views
J['buffers'][0] = {'byteLength': len(out), 'uri': 'data:application/octet-stream;base64,' + base64.b64encode(bytes(out)).decode()}
json.dump(J, open(dst, 'w'), separators=(',', ':'))
print('wrote', dst)
