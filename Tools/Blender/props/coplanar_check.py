import math
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

DIST = 0.006
DOT = 0.9995
CELL = 0.5


def _islands(me):
    parent = list(range(len(me.vertices)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for p in me.polygons:
        vs = p.vertices
        r0 = find(vs[0])
        for v in vs[1:]:
            r = find(v)
            if r != r0:
                parent[r] = r0
    return [find(p.vertices[0]) for p in me.polygons]


def _basis(n):
    a = Vector((1, 0, 0)) if abs(n.x) < 0.9 else Vector((0, 1, 0))
    u = n.cross(a).normalized()
    return u, n.cross(u)


def _inside(p, a, b, c, n):
    tol = -1e-4
    for s, e in ((a, b), (b, c), (c, a)):
        if n.dot((e - s).cross(p - s)) < tol * (e - s).length:
            return False
    return True


def check(ob, label="", out_path=None, max_list=2000, solid=None):
    me = ob.data
    mw = ob.matrix_world
    co = [mw @ v.co for v in me.vertices]
    isl = _islands(me)
    mats = [m.name if m else "?" for m in me.materials]
    tris = []
    for p in me.polygons:
        vs = p.vertices
        for k in range(1, len(vs) - 1):
            a, b, c = co[vs[0]], co[vs[k]], co[vs[k + 1]]
            n = (b - a).cross(c - a)
            ar = n.length / 2
            if ar < 1e-6:
                continue
            n.normalize()
            tris.append((a, b, c, n, n.dot(a), (a + b + c) / 3, ar, isl[p.index], mats[p.material_index], p.index))
    grid = defaultdict(list)
    keyed = []
    for i, t in enumerate(tris):
        a, b, c, n = t[0], t[1], t[2], t[3]
        nk = (round(n.x * 40), round(n.y * 40), round(n.z * 40))
        u, v = _basis(Vector((nk[0], nk[1], nk[2])).normalized() if any(nk) else n)
        pu = [u.dot(q) for q in (a, b, c)]
        pv = [v.dot(q) for q in (a, b, c)]
        db = int(math.floor(t[4] / DIST))
        keyed.append((nk, db))
        for gx in range(int(math.floor(min(pu) / CELL)), int(math.floor(max(pu) / CELL)) + 1):
            for gy in range(int(math.floor(min(pv) / CELL)), int(math.floor(max(pv) / CELL)) + 1):
                grid[(nk, db, gx, gy)].append(i)
    pairs = set()
    for i, t in enumerate(tris):
        nk, db = keyed[i]
        u, v = _basis(Vector(nk).normalized() if any(nk) else t[3])
        cu, cv = u.dot(t[5]), v.dot(t[5])
        gx, gy = int(math.floor(cu / CELL)), int(math.floor(cv / CELL))
        for dd in (-1, 0, 1):
            for j in grid.get((nk, db + dd, gx, gy), ()):
                if j == i:
                    continue
                s = tris[j]
                if s[7] == t[7]:
                    continue
                if abs(s[4] - t[4]) >= DIST or s[3].dot(t[3]) < DOT:
                    continue
                cp = t[5] - s[3] * (s[3].dot(t[5]) - s[4])
                if _inside(cp, s[0], s[1], s[2], s[3]):
                    pairs.add((min(i, j), max(i, j)))
    vs, ps = co, [list(p.vertices) for p in me.polygons]
    bvh = BVHTree.FromPolygons(vs, ps)
    poly_isl = isl
    groups = {}
    for i, j in pairs:
        t, s = tris[i], tris[j]
        small = t if t[6] <= s[6] else s
        n = t[3]
        dmax = max(t[4], s[4])
        o = small[5] + n * (dmax - n.dot(small[5]) + 0.004)
        skip = {t[7], s[7]}
        vis = not (solid and solid(o))
        dist_left = 30.0 if vis else 0.0
        while dist_left > 0:
            hit = bvh.ray_cast(o, n, dist_left)
            if hit[0] is None:
                break
            if poly_isl[hit[2]] in skip:
                o = hit[0] + n * 1e-4
                dist_left -= hit[3] + 1e-4
                continue
            if hit[1].dot(n) > 0 or hit[3] < 0.012:
                vis = False
            break
        key = (min(t[7], s[7]), max(t[7], s[7]))
        g = groups.setdefault(key, [0, 0, small[5], sorted((t[8], s[8])), 0.0, n])
        g[0] += 1
        if vis:
            if g[1] == 0:
                g[2], g[5] = small[5], n
                g.append((t[8], t[5], s[8], s[5]))
            g[1] += 1
            g[4] += small[6]
    vis_groups = {k: g for k, g in groups.items() if g[1] > 0}
    lines = ["COPLANAR %s pairs=%d groups=%d visible_groups=%d visible_pairs=%d" % (
        label, len(pairs), len(groups), len(vis_groups), sum(g[1] for g in groups.values()))]
    for k, g in sorted(vis_groups.items(), key=lambda kv: -kv[1][4])[:max_list]:
        c = g[2]
        lines.append("  vis (%.2f, %.2f, %.2f) n=(%.2f,%.2f,%.2f) %s/%s pairs=%d area=%.4f   [%s %.2f,%.2f,%.2f | %s %.2f,%.2f,%.2f]" % (c.x, c.y, c.z, g[5].x, g[5].y, g[5].z, g[3][0], g[3][1], g[1], g[4], g[6][0], g[6][1].x, g[6][1].y, g[6][1].z, g[6][2], g[6][3].x, g[6][3].y, g[6][3].z))
    txt = "\n".join(lines)
    print(txt)
    if out_path:
        with open(out_path, "w") as f:
            f.write(txt + "\n")
    return len(groups), len(vis_groups)
