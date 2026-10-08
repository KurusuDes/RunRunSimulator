import sys, os, glob, importlib, math

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
OUT_DIR = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Sprites", "PartIcons")

N = 32
SS = 16
FILL = 26
COVER = 0.3
LIGHT_DIR = (-0.55, 0.7, 0.55)
TONES = (0.94, 0.72, 0.48)
SHARE = (0.35, 0.25)
OUTLINE = 0.10
INNER = 0.22
DEPTH_JUMP = (0.04, 0.25)
MIN_BLOB = 3
CLEAN = 2

LATERAL = (1.0, -0.15, 0.2)
VIEWS = {
    "Horn": (0.6, -1.0, 0.45),
    "Back": (1.0, 0.0, 0.3),
    "Wing": (0.8, -0.2, -0.4),
}
OVERRIDES = {
    "Alforja": (1.0, 0.0, 0.0),
    "Antenas": (0.3, -1.0, 0.2),
    "Ariete": LATERAL,
    "Astas": (0.8, 0.8, 0.4),
    "Cometa": LATERAL,
    "Coraza": (1.0, -0.1, 0.5),
    "Cuernitos": (0.5, -1.0, 0.05),
    "Carnero": (1.0, -0.35, 0.05),
    "Senuelo": (1.0, -0.35, 0.05),
    "Hoz": (1.0, 0.0, 0.0),
    "Mechon": LATERAL,
    "Rayo": (-1.0, -0.7, 0.1),
    "Rinoceronte": LATERAL,
    "Tapones": LATERAL,
    "Triceratops": (1.0, 0.0, 0.0),
}
SIDE = 0.06
HORN_DIR = 135
BURY = 0.02
TRIM = {"Carnero", "Ariete"}
HORN_FIX = {"AletasCara": (45, False), "Cometa": (35, False), "Carnero": (-60, True)}
RIGID_BASE = {"Abanico": "INNER", "Cometitas": "ICON_BASE", "Coraza": "ICON_BASE", "Alforja": "ICON_BASE", "Cola": "ICON_BASE"}
BASE_ROW = 29.5
UNITS = 3
UNIT_GAP = (0.45, 1.0)
KMAX = {"Placas": 2.2, "PuasGruesas": 3.0, "PuasFinas": 2.2, "PuasDobles": 2.2, "Cristales": 1.5, "Malvaviscos": 1.8, "Abanico": 2.0, "LomoLana": 1.9, "Cresta": 1.65, "Coraza": 1.9, "Alforja": 1.0}
PUFFS = {"LomoLana": "R0"}
WIDEN = {"PuasGruesas": 1.45, "Placas": 1.3, "Malvaviscos": 1.1}
BACK_ASPECT = 0.85
MID_FWD = 0.08
LOBED = {}
PAIRED_UNITS = {"PuasDobles": 2}
WINDOW = {"Cresta": ("front", 3.0)}
TUFT = {"Borla": ((2, 0, 4), 20.0)}
THIN = 12
PAIR = set()
EXCLUDE = {"Unicornio": "mane", "Cresta": "core", "Alforja": "strap"}
OPTS = {
    "Placas": {"idlines": True},
    "PuasFinas": {"thin": 4},
    "Ariete": {"idlines": True},
}
GROOVES = {"Unicornio": (0.2, 0.2)}
STAGE = {
    "Placas": ("plates", 1.0),
    "Unicornio": ("point", 0.0),
    "Antenas": ("bulb", 2.8),
}


def islands(bm):
    seen, out = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        st, isl = [f], []
        seen.add(f.index)
        while st:
            g = st.pop()
            isl.append(g)
            for e in g.edges:
                for h in e.link_faces:
                    if h.index not in seen:
                        seen.add(h.index)
                        st.append(h)
        out.append(isl)
    return out


def keep_one_side(objs):
    import bmesh
    data = []
    for o in objs:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        bm.faces.ensure_lookup_table()
        mw = o.matrix_world
        isl = [(i, sum(((mw @ v.co).x for f in fs for v in f.verts)) / sum(len(f.verts) for f in fs)) for i, fs in enumerate(islands(bm))]
        data.append((o, bm, isl))
    xs = [x for _, _, isl in data for _, x in isl]
    if not (any(x > SIDE for x in xs) and any(x < -SIDE for x in xs)):
        for _, bm, _ in data:
            bm.free()
        return objs
    kept = []
    for o, bm, isl in data:
        groups = islands(bm)
        dead = [f for i, x in isl if x < -SIDE for f in groups[i]]
        bmesh.ops.delete(bm, geom=dead, context="FACES")
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()
        if len(o.data.polygons):
            kept.append(o)
        else:
            o.hide_render = True
    return kept


def all_names():
    return sorted(os.path.basename(p)[2:-3] for p in glob.glob(os.path.join(HERE, "p_*.py")))


def view_basis(d):
    from mathutils import Vector
    f = -Vector(d).normalized()
    r = f.cross(Vector((0, 0, 1))).normalized()
    u = r.cross(f).normalized()
    return f, r, u


def vertex_islands(me):
    import numpy as np
    ev = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ev)
    ev = ev.reshape(-1, 2)
    lab = np.arange(len(me.vertices))
    while True:
        m = np.minimum(lab[ev[:, 0]], lab[ev[:, 1]])
        new = lab.copy()
        np.minimum.at(new, ev[:, 0], m)
        np.minimum.at(new, ev[:, 1], m)
        new = new[new]
        if (new == lab).all():
            break
        lab = new
    return np.unique(lab, return_inverse=True)[1]


def phase(wp, allw, pitch):
    import numpy as np
    c = allw.mean(0)
    w, v = np.linalg.eigh(np.cov((allw - c).T))
    ax = v[:, -1] * (1 if v[2, -1] > 0 else -1)
    e1 = np.cross(ax, (1.0, 0.0, 0.0))
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(ax, e1)
    d = wp - c
    return np.arctan2(d @ e2, d @ e1) / (2 * np.pi) + (d @ ax) / pitch


def edit_islands(objs, fn):
    import bmesh
    for o in objs:
        mw = o.matrix_world.copy()
        inv = mw.inverted()
        bm = bmesh.new()
        bm.from_mesh(o.data)
        for fs in islands(bm):
            vs = list({v for f in fs for v in f.verts})
            ws = fn([mw @ v.co for v in vs])
            for v, w in zip(vs, ws):
                v.co = inv @ w
        bm.to_mesh(o.data)
        bm.free()
        o.data.update()


def plates(k):
    def fn(ws):
        base = min(w.z for w in ws)
        span = max(w.z for w in ws) - base
        cy = sum(w.y for w in ws) / len(ws)
        bins = [1e-6] * 11
        for w in ws:
            i = int(10 * (w.z - base) / span)
            bins[i] = max(bins[i], abs(w.y - cy))
        full = max(bins)
        out = []
        for w in ws:
            h = (w.z - base) / span
            hw = max(bins[int(10 * h)], full * 0.25)
            prof = 1.0 if h < 0.45 else max(0.06, 1 - (h - 0.45) / 0.55)
            out.append(w.__class__((w.x, cy + (w.y - cy) / hw * full * prof, base + (w.z - base) * k)))
        return out
    return fn


def bulb(k):
    def fn(ws):
        root = min(ws, key=lambda w: w.z)
        d = [(w - root).length for w in ws]
        far = max(d)
        tip = [w for w, x in zip(ws, d) if x > 0.84 * far]
        c = sum(tip, ws[0].__class__()) / len(tip)
        return [c + (w - c) * k if x > 0.84 * far else w for w, x in zip(ws, d)]
    return fn


def point(objs):
    import numpy as np
    from mathutils import Vector
    allw = np.array([tuple(o.matrix_world @ v.co) for o in objs for v in o.data.vertices])
    c = allw.mean(0)
    w, v = np.linalg.eigh(np.cov((allw - c).T))
    ax = v[:, -1] * (1 if v[2, -1] > 0 else -1)
    t = (allw - c) @ ax
    t0, t1 = t.min(), t.max()
    for o in objs:
        mw = o.matrix_world.copy()
        inv = mw.inverted()
        for vert in o.data.vertices:
            p = np.array(tuple(mw @ vert.co))
            s = (p - c) @ ax
            u = (s - t0) / (t1 - t0)
            q = c + ax * s + (p - c - ax * s) * max(0.0, (1 - 0.97 * u) / (1 - 0.55 * u))
            vert.co = inv @ Vector(tuple(q))
        o.data.update()


def stage(objs, kind, k):
    if kind == "plates":
        edit_islands(objs, plates(k))
    elif kind == "bulb":
        edit_islands(objs, bulb(k))
    elif kind == "point":
        point(objs)


def gather(objs):
    import bpy, numpy as np
    dg = bpy.context.evaluated_depsgraph_get()
    out, base = [], 1
    for o in objs:
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        mw = np.array(ev.matrix_world, dtype=np.float64)
        nl = len(me.loops)
        vi = np.empty(nl, dtype=np.int32)
        me.loops.foreach_get("vertex_index", vi)
        co = np.empty(len(me.vertices) * 3)
        me.vertices.foreach_get("co", co)
        cn = np.empty(nl * 3)
        me.corner_normals.foreach_get("vector", cn)
        isl = vertex_islands(me)
        ev.to_mesh_clear()
        wp = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
        wn = cn.reshape(-1, 3) @ np.linalg.inv(mw[:3, :3])
        wn /= np.maximum(np.linalg.norm(wn, axis=1, keepdims=True), 1e-9)
        out.append((o, wp, wn, vi, isl + base))
        base += isl.max() + 1
    return out


def bake_attrs(data, f, r, u, name, flip=False):
    import numpy as np
    L = np.array(LIGHT_DIR, dtype=np.float64) * ((-1 if flip else 1), 1, 1)
    L /= np.linalg.norm(L)
    R = np.array([r, u, -f], dtype=np.float64)
    pts_all = []
    allw = np.concatenate([d[1] for d in data])
    for o, wp, wn, vi, isl in data:
        lam = np.clip((wn @ R.T) @ L, 0, 1)
        if name in GROOVES:
            ph = 2 * np.pi * phase(wp, allw, GROOVES[name][0])[vi]
            pc = np.stack([np.cos(ph), np.sin(ph), np.zeros_like(ph), np.ones_like(ph)], 1)
            b = o.data.color_attributes.new("icon_ph", "FLOAT_COLOR", "CORNER")
            b.data.foreach_set("color", pc.ravel())
        col = np.zeros((len(vi), 4))
        col[:, 0] = lam
        col[:, 1] = (wp @ R.T)[vi, 2]
        col[:, 2] = isl[vi]
        col[:, 3] = 1
        a = o.data.color_attributes.new("icon", "FLOAT_COLOR", "CORNER")
        a.data.foreach_set("color", col.ravel())
        o.data.color_attributes.active_color = a
        o.data.color_attributes.render_color_index = o.data.color_attributes.find("icon")
        pts_all.append(wp @ R.T)
    return np.concatenate(pts_all)


def world_edit(objs, fn):
    import numpy as np
    from mathutils import Matrix
    for o in objs:
        mw = np.array(o.matrix_world)
        co = np.empty(len(o.data.vertices) * 3)
        o.data.vertices.foreach_get("co", co)
        w = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
        w = fn(o, w)
        inv = np.linalg.inv(mw)
        o.data.vertices.foreach_set("co", (w @ inv[:3, :3].T + inv[:3, 3]).ravel())
        o.data.update()


def spine_frame():
    import numpy as np
    sys.path.insert(0, HERE)
    import part_common as pc
    pts = []
    for k in range(260):
        y = -0.8 + 2.3 * k / 259
        hit, _ = pc.surface_point((0, y, 3.0), (0, 0, -1))
        if hit is not None:
            pts.append((hit.y, hit.z))
    P = np.array(pts)
    arc = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True)
    Nn = np.stack([-T[:, 1], T[:, 0]], 1)
    Nn *= np.where(Nn[:, 1:] < 0, -1, 1)
    return P, arc, T, Nn


def unbend(objs):
    import numpy as np
    P, arc, T, Nn = spine_frame()

    def fn(o, w):
        yz = w[:, 1:]
        k = np.argmin(((yz[:, None, :] - P[None]) ** 2).sum(2), 1)
        d = yz - P[k]
        t = (d * T[k]).sum(1)
        h = (d * Nn[k]).sum(1)
        return np.stack([w[:, 0], arc[k] + t, h], 1)
    world_edit(objs, fn)


def island_sets(o):
    import numpy as np
    me = o.data
    ev = np.empty(len(me.edges) * 2, dtype=np.int64)
    me.edges.foreach_get("vertices", ev)
    ev = ev.reshape(-1, 2)
    lab = np.arange(len(me.vertices))
    while True:
        m = np.minimum(lab[ev[:, 0]], lab[ev[:, 1]])
        new = lab.copy()
        np.minimum.at(new, ev[:, 0], m)
        np.minimum.at(new, ev[:, 1], m)
        new = new[new]
        if (new == lab).all():
            break
        lab = new
    return np.unique(lab, return_inverse=True)[1]


def delete_verts(o, mask):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[bm.verts[i] for i in range(len(mask)) if mask[i]], context="VERTS")
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()


def cut(o, co, no):
    import bmesh
    from mathutils import Vector
    mw = o.matrix_world
    bm = bmesh.new()
    bm.from_mesh(o.data)
    lco = mw.inverted() @ Vector(co)
    lno = (mw.to_3x3().transposed() @ Vector(no)).normalized()
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces), plane_co=lco, plane_no=lno, clear_inner=True)
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()


def pick_units(objs, name):
    import numpy as np
    items = []
    for o in objs:
        co = np.empty(len(o.data.vertices) * 3)
        o.data.vertices.foreach_get("co", co)
        mw = np.array(o.matrix_world)
        w = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
        lab = island_sets(o)
        for i in range(lab.max() + 1):
            sel = lab == i
            items.append((w[sel, 1].mean(), o, i, w[sel, 1].min(), w[sel, 1].max(), w[sel, 2].max()))
    items.sort(key=lambda t: t[0])
    per = PAIRED_UNITS.get(name)
    groups = []
    for it in items:
        if per and groups and len(groups[-1]) < per:
            groups[-1].append(it)
        elif not per and groups and it[0] - groups[-1][-1][0] < 0.05:
            groups[-1].append(it)
        else:
            groups.append([it])
    if len(groups) <= UNITS:
        chosen = list(range(len(groups)))
    else:
        score = [sum(max(t[5] for t in groups[j]) for j in range(i, i + UNITS)) for i in range(len(groups) - UNITS + 1)]
        i0 = int(np.argmax(score))
        chosen = list(range(i0, i0 + UNITS))
    sw = WIDEN.get(name, 1.0)
    width = sw * max(max(t[4] for t in groups[j]) - min(t[3] for t in groups[j]) for j in chosen)
    uh = max(t[5] for j in chosen for t in groups[j])
    gap = (uh * KMAX.get(name, 1.5) / (BACK_ASPECT * width) - 1) / 2
    gap = min(max(gap, UNIT_GAP[0]), UNIT_GAP[1])
    shift_of = {}
    for n, j in enumerate(chosen):
        c = (max(t[4] for t in groups[j]) + min(t[3] for t in groups[j])) / 2
        for t in groups[j]:
            shift_of[(t[1].name, t[2])] = (c, n * width * gap, MID_FWD if n == 1 else 0.0)
    for o in objs:
        lab = island_sets(o)
        sh = np.array([shift_of.get((o.name, i), (np.nan, 0.0, 0.0)) for i in range(lab.max() + 1)])[lab]
        dy = sh[:, 0]

        def fn(ob, w, sh=sh):
            w = w.copy()
            ok = ~np.isnan(sh[:, 0])
            w[ok, 1] = (w[ok, 1] - sh[ok, 0]) * sw + sh[ok, 1]
            w[:, 0] += sh[:, 2]
            return w
        world_edit([o], fn)
        delete_verts(o, np.isnan(dy))
    return [o for o in objs if len(o.data.polygons)]


def tuft(objs, pick, spread):
    import numpy as np
    locks = sorted(objs, key=lambda o: o.name[-1])
    keep = [locks[i] for i in pick if i < len(locks)]
    for o in objs:
        if o not in keep:
            o.hide_render = True
    k = len(keep)
    for n, o in enumerate(keep):
        th = math.radians(spread * (n - (k - 1) / 2))

        def fn(ob, w, th=th):
            root = w[np.argmin(w[:, 1])]
            tip = w[np.argmax(((w - root) ** 2).sum(1))]
            d = tip - root
            a = math.atan2(d[1], d[2]) - th
            ca, sa = math.cos(a), math.sin(a)
            q = w - root
            y, z = q[:, 1] * ca - q[:, 2] * sa, q[:, 1] * sa + q[:, 2] * ca
            return np.stack([q[:, 0] * 0.4, y, z - 0.04], 1)
        world_edit([o], fn)
    return keep


def rigid_base(objs, a, b):
    import numpy as np
    a, b = np.array((0.0,) + tuple(a)), np.array((0.0,) + tuple(b))
    t = (b - a) / np.linalg.norm(b - a)
    ang = math.atan2(t[2], t[1])
    ca, sa = math.cos(-ang), math.sin(-ang)

    def fn(o, w):
        q = w - a
        return np.stack([q[:, 0], q[:, 1] * ca - q[:, 2] * sa, q[:, 1] * sa + q[:, 2] * ca], 1)
    world_edit(objs, fn)


def puffs(objs, R):
    import bmesh
    for o in objs:
        o.hide_render = True
    out = []
    for i in range(UNITS):
        for j, (dy, dz, k) in enumerate(((-0.55, 0.5, 0.58), (0.55, 0.5, 0.58), (0.0, 0.95, 0.72), (-0.3, 1.55, 0.5), (0.35, 1.5, 0.46))):
            bm = bmesh.new()
            bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=10, radius=R * k)
            for v in bm.verts:
                v.co.y += i * 1.9 * R + dy * R
                v.co.z += dz * R
                v.co.x += (MID_FWD if i == 1 else 0.0) + 0.02 * j
            ob = pc_new_object("Back_puff%d_%d" % (i, j), bm)
            for f in ob.data.polygons:
                f.use_smooth = True
            out.append(ob)
    return out


def back_setup(objs, name, mod=None):
    if name in PUFFS:
        objs = puffs(objs, getattr(mod, PUFFS[name]))
    elif name in TUFT:
        objs = tuft(objs, *TUFT[name])
    elif name in RIGID_BASE:
        rigid_base(objs, *getattr(mod, RIGID_BASE[name]))
    else:
        unbend(objs)
        if name in WINDOW:
            mode, L = WINDOW[name]
            W = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
            y0 = min(w.y for w in W) if mode == "front" else max(W, key=lambda w: w.z).y - L / 2
            for o in objs:
                cut(o, (0, y0, 0), (0, 1, 0))
                cut(o, (0, y0 + L, 0), (0, -1, 0))
        else:
            objs = pick_units(objs, name)
    for o in objs:
        cut(o, (0, 0, 0), (0, 0, 1))
    objs = [o for o in objs if len(o.data.polygons)]
    return fit_box(objs)


CURRENT = [""]


def fit_box(objs):
    import numpy as np
    import bmesh
    W = np.array([tuple(o.matrix_world @ v.co) for o in objs for v in o.data.vertices])
    y0, y1, h = W[:, 1].min(), W[:, 1].max(), W[:, 2].max()
    w = y1 - y0
    k = min(BACK_ASPECT * w / max(h, 1e-6), KMAX.get(CURRENT[0], 1.5))
    world_edit(objs, lambda o, q: q * (1, 1, k))
    return objs


def pc_new_object(name, bm):
    import bpy
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def lobed(objs, mod, k):
    import bmesh
    for o in objs:
        o.hide_render = True
    out = []
    for i, (x, y, r, lift) in enumerate(mod.LOBES):
        r *= 0.95
        c = mod.lobe_center(x, y, r, lift)
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=r * k)
        for v in bm.verts:
            v.co += c
        ob = pc_new_object("Horn_Lana_lobe%d" % i, bm)
        for f in ob.data.polygons:
            f.use_smooth = True
        out.append(ob)
    return out


def body_side(objs):
    import numpy as np
    import bpy
    from mathutils.bvhtree import BVHTree
    body = bpy.data.objects["Dragon_body"]
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    inv = body.matrix_world.inverted()
    out = []
    for o in objs:
        sd = []
        for v in o.data.vertices:
            q = inv @ (o.matrix_world @ v.co)
            loc, nrm, _, _ = tree.find_nearest(q)
            sd.append((q - loc).dot(nrm) if loc is not None else 9.0)
        out.append(np.array(sd))
    return out


def trim_buried(objs, depth):
    for o, sd in zip(objs, body_side(objs)):
        if (sd >= -depth).sum() > 8:
            delete_verts(o, sd < -depth)
    return [o for o in objs if len(o.data.polygons)]


def horn_dir(objs, r, u):
    import numpy as np
    from mathutils.bvhtree import BVHTree
    import bpy
    body = bpy.data.objects["Dragon_body"]
    dg = bpy.context.evaluated_depsgraph_get()
    tree = BVHTree.FromObject(body, dg)
    inv = body.matrix_world.inverted()
    W = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    side = []
    for w in W:
        loc, nrm, _, dist = tree.find_nearest(inv @ w)
        side.append(((inv @ w) - loc).dot(nrm) if loc is not None else 9.0)
    side = np.array(side)
    A = np.array([tuple(w) for w in W])
    inside = side <= np.quantile(side, 0.05) if (side < 0).sum() < 3 else side < 0
    base = A[inside].mean(0)
    d = A[np.argmax(((A - base) ** 2).sum(1))] - base
    return math.atan2(d @ np.array(u), d @ np.array(r))


def render_part(name, tmp):
    import bpy
    from mathutils import Vector, Matrix
    sys.path.insert(0, HERE)
    import part_common as pc
    mod = importlib.import_module("p_" + name)
    arm = pc.load_dragon("A")
    objs = mod.build(arm)
    if name in EXCLUDE:
        for o in objs:
            if EXCLUDE[name] in o.name:
                o.hide_render = True
        objs = [o for o in objs if EXCLUDE[name] not in o.name]
    slot = mod.SLOTS[0]
    CURRENT[0] = name
    if name in LOBED:
        objs = lobed(objs, mod, LOBED[name])
    if name not in PAIR and slot != "Back":
        objs = keep_one_side(objs)
    if slot == "Back":
        objs = back_setup(objs, name, mod)
    if name in TRIM:
        objs = trim_buried(objs, BURY)
    if name in STAGE:
        stage(objs, *STAGE[name])
    keep = set(o.name for o in objs)
    for o in bpy.data.objects:
        if o.name not in keep:
            o.hide_render = True
    bpy.context.view_layer.update()
    f, r, u = view_basis(OVERRIDES.get(name, VIEWS[slot]))
    bpy.context.view_layer.update()
    data = gather(objs)
    flip, a = False, 0.0
    if slot == "Horn":
        ang = math.degrees(horn_dir(objs, r, u))
        tw, inv = HORN_FIX.get(name, (0, False))
        wrap = lambda x: (x + 180) % 360 - 180
        flip = (abs(wrap(ang - (180 - HORN_DIR))) < abs(wrap(ang - HORN_DIR))) != inv
        a = math.radians(wrap(ang + tw - (180 - HORN_DIR)) if flip else wrap(ang - tw - HORN_DIR))
    r, u = r * math.cos(a) + u * math.sin(a), -r * math.sin(a) + u * math.cos(a)
    P = bake_attrs(data, f, r, u, name, flip)
    lo, hi = P.min(0), P.max(0)
    cx, cy = (lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2
    ext = max(hi[0] - lo[0], hi[1] - lo[1])
    if slot == "Back":
        ext = max(hi[0] - lo[0], (hi[1] - lo[1]) * FILL / (2 * BASE_ROW - N))
        ps = ext / FILL
        cy = lo[1] + (BASE_ROW - N / 2) * ps
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "FLAT"
    sh.color_type = "VERTEX"
    sh.show_cavity = False
    sh.show_object_outline = False
    sh.show_shadows = False
    sh.show_specular_highlight = False
    sh.show_xray = False
    sc.display.render_aa = "OFF"
    sc.render.dither_intensity = 0
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = N * SS
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = "OPEN_EXR"
    sc.render.image_settings.color_depth = "32"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    cd = bpy.data.cameras.new("icon_cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ext * N / FILL
    cd.clip_start = 0.01
    cd.clip_end = 100
    cam = bpy.data.objects.new("icon_cam", cd)
    sc.collection.objects.link(cam)
    center = Vector(r) * cx + Vector(u) * cy - Vector(f) * (hi[2] + 10)
    m = Matrix((r, u, -f)).transposed().to_4x4()
    m.translation = center
    cam.matrix_world = m
    sc.camera = cam
    paths = [os.path.join(tmp, "raw_%s.exr" % name)]
    sc.render.filepath = paths[0]
    bpy.ops.render.render(write_still=True)
    if name in GROOVES:
        for o in objs:
            ca = o.data.color_attributes
            ca.active_color = ca["icon_ph"]
            ca.render_color_index = ca.find("icon_ph")
        paths.append(os.path.join(tmp, "ph_%s.exr" % name))
        sc.render.filepath = paths[1]
        bpy.ops.render.render(write_still=True)
    return paths, flip


def load_exr(path):
    import bpy, numpy as np
    img = bpy.data.images.load(path)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    bpy.data.images.remove(img)
    return px.reshape(h, w, 4)[::-1]


def shift(a, dy, dx):
    import numpy as np
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[yd, xd] = a[ys, xs]
    return out


N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))
N8 = N4 + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def components(mask):
    import numpy as np
    lab = np.zeros(mask.shape, dtype=np.int32)
    k = 0
    for y, x in zip(*np.nonzero(mask)):
        if lab[y, x]:
            continue
        k += 1
        st = [(y, x)]
        lab[y, x] = k
        while st:
            cy, cx = st.pop()
            for dy, dx in N8:
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < mask.shape[0] and 0 <= nx < mask.shape[1] and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = k
                    st.append((ny, nx))
    return lab, k


def grow(A, chans, steps):
    for _ in range(steps):
        new = A.copy()
        for dy, dx in N8:
            sm = shift(A, dy, dx)
            add = sm & ~new
            for c in chans:
                c[add] = shift(c, dy, dx)[add]
            new |= add
        A = new
    return A


def erode(A, steps):
    for _ in range(steps):
        B = A.copy()
        for dy, dx in N8:
            B &= shift(A, dy, dx)
        A = B
    return A


def thicken(A, chans, r):
    thin = A & ~grow(erode(A, r), [], r)
    tmp = [c.copy() for c in chans]
    extra = grow(thin, tmp, r) & ~A
    res = [c.copy() for c in chans]
    for c, t in zip(res, tmp):
        c[extra] = t[extra]
    return A | extra, res


def process(raw, opts, ph=None, groove_w=0.0):
    import numpy as np
    A = raw[..., 3] > 0.5
    lam, dep, oid = raw[..., 0].copy(), raw[..., 1].copy(), np.rint(raw[..., 2]).astype(np.int32)
    lam[~A], dep[~A], oid[~A] = 0, -1e9, 0
    grv = np.zeros(A.shape)
    if ph is not None:
        grv = ((np.arctan2(ph[..., 1], ph[..., 0]) / (2 * np.pi)) % 1.0 < groove_w) & A
        grv = grv.astype(np.float64)
    thin = opts.get("thin", THIN)
    if thin:
        A, (lam, dep, oid, grv) = thicken(A, [lam, dep, oid, grv], thin)
    B = lambda a: a.reshape(N, SS, N, SS)
    cnt = B(A.astype(np.float64)).sum((1, 3))
    cov = cnt / (SS * SS)
    safe = np.maximum(cnt, 1)
    shade = B(lam * A).sum((1, 3)) / safe
    groove = B(grv * A).sum((1, 3)) / safe > 0.3
    near = np.where(A, dep, -1e9)
    depth = B(near).max((1, 3))
    ids = oid * A
    best = np.zeros((N, N), dtype=np.int32)
    bestc = np.zeros((N, N))
    for i in range(1, ids.max() + 1):
        c = B((ids == i).astype(np.float64)).sum((1, 3))
        upd = c > bestc
        best[upd], bestc[upd] = i, c[upd]
    mask = cov > COVER
    lab, k = components(mask)
    for i in range(1, k + 1):
        if (lab == i).sum() < MIN_BLOB:
            mask[lab == i] = False
    holes = ~mask
    nb = sum(shift(mask.astype(np.int32), dy, dx) for dy, dx in N4)
    fill = holes & (nb >= 3)
    mask |= fill
    for dy, dx in N4:
        src = shift(shade, dy, dx)
        shade = np.where(fill & (shift(mask.astype(np.int32), dy, dx) > 0), src, shade)
    sv = shade[mask]
    c0 = np.clip(np.quantile(sv, 1 - SHARE[0]), 0.45, 0.9)
    c1 = np.clip(np.quantile(sv, SHARE[1]), 0.15, c0 - 0.08)
    t = np.where(shade > c0, 0, np.where(shade > c1, 1, 2))
    for _ in range(CLEAN):
        cnt = np.zeros((3, N, N), dtype=np.int32)
        for dy, dx in N8:
            st = shift(t + 1, dy, dx) * shift(mask.astype(np.int32), dy, dx)
            for k in range(3):
                cnt[k] += st == k + 1
        own = np.take_along_axis(cnt, t[None], 0)[0]
        top = cnt.argmax(0)
        t = np.where(mask & (own == 0) & (cnt.max(0) >= 3), top, t)
    g = np.array(TONES)[t]
    inner = np.zeros((N, N), dtype=bool)
    for dy, dx in N4:
        nd = shift(depth, dy, dx)
        nm = shift(mask.astype(np.int32), dy, dx) > 0
        ni = shift(best, dy, dx)
        jump = 0.0 if opts.get("idlines") else DEPTH_JUMP[0]
        inner |= mask & nm & (((nd > depth + jump) & (ni != best)) | (nd > depth + DEPTH_JUMP[1]))
    inner |= groove & mask
    g = np.where(inner, INNER, g)
    grow = np.zeros((N, N), dtype=bool)
    for dy, dx in N8:
        grow |= shift(mask.astype(np.int32), dy, dx) > 0
    outline = grow & ~mask
    out = np.zeros((N, N, 4), dtype=np.float32)
    out[mask, :3] = g[mask, None]
    out[mask, 3] = 1
    out[outline, :3] = OUTLINE
    out[outline, 3] = 1
    return out


def save_png(arr, path):
    import bpy
    img = bpy.data.images.new("icon_out", N, N, alpha=True)
    img.pixels.foreach_set(arr[::-1].ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    bpy.data.images.remove(img)


def blender_main(a):
    names = [n for n in a[0].split(",") if n] if a and a[0] not in ("", "*") else all_names()
    tmp = a[1] if len(a) > 1 else os.path.join(os.environ.get("TEMP", "."), "monchi_icons")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    for name in names:
        try:
            paths, flip = render_part(name, tmp)
            raw = load_exr(paths[0])
            ph = load_exr(paths[1]) if len(paths) > 1 else None
            gw = GROOVES[name][1] if name in GROOVES else 0.0
            opts = dict(OPTS.get(name, {}))
            if name in LOBED or importlib.import_module("p_" + name).SLOTS[0] == "Back":
                opts["idlines"] = True
            icon = process(raw, opts, ph, gw)
            save_png(icon[:, ::-1] if flip else icon, os.path.join(OUT_DIR, "PartIcon_%s.png" % name))
            print("ICON_DONE", name)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("ICON_FAIL", name, e)


SLOT_TINT = {
    "Horn": ((233, 161, 31), (245, 185, 72)),
    "Back": ((31, 158, 138), (51, 191, 166)),
    "Wing": ((158, 79, 178), (194, 115, 212)),
}
BG_LIGHT, BG_DARK = (251, 240, 220), (51, 38, 36)


def contact_main(tmp):
    from PIL import Image, ImageDraw, ImageChops
    groups = {s: [] for s in SLOT_TINT}
    for n in all_names():
        if not os.path.exists(os.path.join(OUT_DIR, "PartIcon_%s.png" % n)):
            continue
        src = open(os.path.join(HERE, "p_%s.py" % n), encoding="utf-8").read()
        groups[next((s for s in SLOT_TINT if '("%s",)' % s in src), "Horn")].append(n)
    Z, cols, pad = 4, 8, 8
    S = N * Z
    cw, ch = S + pad, 2 * S + 22
    rows = [(s, groups[s][i:i + cols]) for s in SLOT_TINT for i in range(0, len(groups[s]), cols)]
    H = pad + sum(ch + (22 if i == 0 or rows[i - 1][0] != s else 0) for i, (s, _) in enumerate(rows))
    sheet = Image.new("RGB", (cols * cw + pad, H), (90, 84, 80))
    d = ImageDraw.Draw(sheet)
    y = pad
    for i, (s, names) in enumerate(rows):
        if i == 0 or rows[i - 1][0] != s:
            d.text((pad, y + 4), s.upper(), fill=(255, 255, 255))
            y += 22
        for j, n in enumerate(names):
            ic = Image.open(os.path.join(OUT_DIR, "PartIcon_%s.png" % n)).convert("RGBA").resize((S, S), Image.NEAREST)
            x = pad + j * cw
            for k, (bg, tint) in enumerate(((BG_LIGHT, SLOT_TINT[s][0]), (BG_DARK, SLOT_TINT[s][1]))):
                im = ImageChops.multiply(ic, Image.new("RGBA", ic.size, tint + (255,)))
                d.rectangle((x, y + k * S, x + S - 1, y + (k + 1) * S - 1), fill=bg)
                sheet.paste(im, (x, y + k * S), im)
            d.text((x, y + 2 * S + 4), n, fill=(255, 255, 255))
        y += ch
    out = os.path.join(tmp, "contact.png")
    sheet.save(out)
    print("CONTACT", out, sheet.size)


try:
    import bpy
except ImportError:
    bpy = None

if bpy is not None:
    blender_main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
elif __name__ == "__main__":
    contact_main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.environ.get("TEMP", "."), "monchi_icons"))
