import sys
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from env_kit_e2 import *
from collections import defaultdict


def _tri_arrays(obs):
    A, Bv, C, M = [], [], [], []
    names = []
    for ob in obs:
        me = ob.data
        mw = ob.matrix_world
        me.calc_loop_triangles()
        slot = {}
        for i, m in enumerate(me.materials):
            nm = m.name if m else "?"
            nm = nm.split(".")[0]
            if nm not in names:
                names.append(nm)
            slot[i] = names.index(nm)
        vs = np.array([tuple(mw @ v.co) for v in me.vertices], dtype=np.float64)
        for lt in me.loop_triangles:
            a, b, c = lt.vertices
            A.append(vs[a])
            Bv.append(vs[b])
            C.append(vs[c])
            M.append(slot.get(lt.material_index, 0))
    return np.array(A), np.array(Bv), np.array(C), np.array(M), names


def coplanar_report(obs, label, tol=0.006, cos_min=0.995, cell=0.3, show=14, ground=-0.405, floor_z=-0.405):
    A, B, C, M, names = _tri_arrays(obs)
    allv = np.concatenate([A, B, C]).tolist()
    nA = len(A)
    tree = BVHTree.FromPolygons(allv, [(i, i + nA, i + 2 * nA) for i in range(nA)], all_triangles=True)
    N = np.cross(B - A, C - A)
    ar = np.linalg.norm(N, axis=1)
    keep = ar > 4e-6
    idx = np.nonzero(keep)[0]
    N = N[idx] / ar[idx, None]
    A, B, C, M = A[idx], B[idx], C[idx], M[idx]
    G = (A + B + C) / 3.0
    lo = np.floor(np.minimum(np.minimum(A, B), C) / cell).astype(int)
    hi = np.floor(np.maximum(np.maximum(A, B), C) / cell).astype(int)
    grid = defaultdict(list)
    for i in range(len(A)):
        for ax in range(3):
            for sg in (1, -1):
                if N[i, ax] * sg > 0.45:
                    key = ax * 2 + (0 if sg > 0 else 1)
                    for x in range(lo[i, 0], hi[i, 0] + 1):
                        for y in range(lo[i, 1], hi[i, 1] + 1):
                            for z in range(lo[i, 2], hi[i, 2] + 1):
                                grid[(key, x, y, z)].append(i)
    pairs = set()
    nT = len(A)
    for lst in grid.values():
        k = len(lst)
        if k < 2:
            continue
        for p in range(k):
            ip = lst[p]
            for q in range(p + 1, k):
                iq = lst[q]
                pairs.add(ip * nT + iq if ip < iq else iq * nT + ip)
    if not pairs:
        print("COPLANAR %s tris=%d pairs=0 visible=0" % (label, nT))
        return 0, 0
    P = np.fromiter(pairs, dtype=np.int64)
    I, J = P // nT, P % nT
    dn = np.einsum("ij,ij->i", N[I], N[J])
    s = dn > cos_min
    I, J = I[s], J[s]
    d1 = np.abs(np.einsum("ij,ij->i", G[I] - A[J], N[J]))
    d2 = np.abs(np.einsum("ij,ij->i", G[J] - A[I], N[I]))
    s = (d1 < tol) & (d2 < tol)
    I, J = I[s], J[s]

    def inside(Pp, a, b, c, eps=1e-3):
        v0, v1, v2 = c - a, b - a, Pp - a
        d00 = np.einsum("ij,ij->i", v0, v0)
        d01 = np.einsum("ij,ij->i", v0, v1)
        d02 = np.einsum("ij,ij->i", v0, v2)
        d11 = np.einsum("ij,ij->i", v1, v1)
        d12 = np.einsum("ij,ij->i", v1, v2)
        den = d00 * d11 - d01 * d01
        den = np.where(np.abs(den) < 1e-14, 1e-14, den)
        u = (d11 * d02 - d01 * d12) / den
        v = (d00 * d12 - d01 * d02) / den
        return (u > eps) & (v > eps) & (u + v < 1 - eps)

    arI = np.linalg.norm(np.cross(B[I] - A[I], C[I] - A[I]), axis=1) / 2
    arJ = np.linalg.norm(np.cross(B[J] - A[J], C[J] - A[J]), axis=1) / 2
    swap = arI > arJ
    I2 = np.where(swap, J, I)
    J2 = np.where(swap, I, J)
    I, J = I2, J2
    nsub = np.clip(np.ceil(np.sqrt(np.minimum(arI, arJ) * 2) / 0.05), 3, 14).astype(int)
    hit = np.zeros(len(I), dtype=bool)
    S1 = np.array(G[I])
    for nv in np.unique(nsub):
        sel = np.nonzero(nsub == nv)[0]
        Wg = np.array([(i_ + 1 / 3, j_ + 1 / 3, nv - i_ - j_ - 2 / 3) for i_ in range(nv) for j_ in range(nv - i_)]) / nv
        Wg = Wg[(Wg > 0).all(axis=1)]
        for wa, wb, wc in Wg:
            Pi = wa * A[I[sel]] + wb * B[I[sel]] + wc * C[I[sel]]
            h = inside(Pi, A[J[sel]], B[J[sel]], C[J[sel]], eps=1e-4) & ~hit[sel]
            S1[sel[h]] = Pi[h]
            hit[sel[h]] = True
    I, J, S1 = I[hit], J[hit], S1[hit]
    in1 = np.ones(len(I), dtype=bool)
    S2 = S1
    vis = []
    for k in range(len(I)):
        i, j = (I[k], J[k]) if in1[k] else (J[k], I[k])
        pk = S1[k] if in1[k] else S2[k]
        n = Vector(N[i])
        hi_ = max(float(np.dot(pk - A[j], N[j])), 0.0)
        o = Vector(pk) + n * (hi_ + 0.0065)
        hidden = o.z < ground or (o.z < floor_z + 0.025 and n.z < -0.5)
        if not hidden:
            pos, bal, first = o, 0, True
            for _ in range(40):
                h = tree.ray_cast(pos, n, 30.0)
                if h[0] is None:
                    break
                back = h[1].dot(n) > 0
                if first and not back and (h[0] - o).length < 0.012:
                    bal = 1
                    break
                first = False
                bal += 1 if back else -1
                pos = h[0] + n * 1e-4
            hidden = bal > 0
        vis.append(not hidden)
    vis = np.array(vis, dtype=bool)
    print("COPLANAR %s tris=%d overlaps=%d visible=%d" % (label, nT, len(I), int(vis.sum())))
    bym = defaultdict(int)
    for k in range(len(I)):
        if vis[k]:
            a, b = sorted((names[M[I[k]]], names[M[J[k]]]))
            bym[(a, b)] += 1
    for (a, b), c in sorted(bym.items(), key=lambda x: -x[1]):
        print("  COPLANAR_MAT %s %s / %s : %d" % (label, a, b, c))
    cl = defaultdict(list)
    for k in range(len(I)):
        if not vis[k]:
            continue
        g = S1[k] if in1[k] else S2[k]
        a_, b_ = sorted((names[M[I[k]]], names[M[J[k]]]))
        cl[(tuple(np.round(g / 0.4).astype(int)), a_, b_)].append((g, N[I[k]], float(np.dot(G[I[k]] - A[J[k]], N[J[k]]))))
    for (key, a_, b_), gs in sorted(cl.items(), key=lambda x: -len(x[1]))[:show]:
        g = np.mean([x[0] for x in gs], axis=0)
        nn, dd = gs[0][1], gs[0][2]
        print("  COPLANAR_AT %s (%.2f, %.2f, %.2f) x%d %s/%s n=(%.2f,%.2f,%.2f) d=%.4f" % (
            label, g[0], g[1], g[2], len(gs), a_, b_, nn[0], nn[1], nn[2], dd))
    return len(I), int(vis.sum())


def outer3s(B, w, u0, u1, rng, posts=(), board="SH_Honey", groove="SH_Walnut", stone_h=0.32, bw=0.22, step=0.62):
    g = w.gout
    w.box(B["SH_StoneDark"], u0, u1, w.T - 0.004, w.T + 0.03, g - 0.01, g + stone_h, r=0.02, segs=1)
    n = max(1, int((u1 - u0) / step))
    st = (u1 - u0) / n
    for i in range(n):
        uc = u0 + (i + 0.5) * st + rng.uniform(-0.05, 0.05)
        rr = st * rng.uniform(0.36, 0.44)
        if any(a - rr - 0.02 < uc < b + rr + 0.02 for a, b in posts):
            continue
        zc = g + stone_h * (0.33 if i % 2 == 0 else 0.68)
        c = w.P(uc, w.T + 0.03, zc)
        rad = (rr, 0.035, stone_h * 0.3) if w.axis == "x" else (0.035, rr, stone_h * 0.3)
        ellipsoid_bm(c, rad, 6, 3, bm=B["SH_Stone"])
    w.boards(B[board], B[groove], u0, u1, g + stone_h - 0.02, w.zt - 0.24, outer=True, bw=bw)
    w.box(B["SH_Timber"], u0, u1, w.T - 0.004, w.T + 0.04, w.zt - 0.27, w.zt - 0.17, r=0.02, segs=1)


def cut_window(B, w, u0, u1, z0, z1, vpad=0.16):
    ua = 0 if w.axis == "x" else 1
    pa = 1 - ua
    lo, hi = sorted((w.P(0, -vpad, 0)[pa], w.P(0, w.T + vpad, 0)[pa]))
    for bm in B.values():
        def near():
            return [f for f in bm.faces if all(lo <= v.co[pa] <= hi for v in f.verts)]
        for val, k in ((u0, ua), (u1, ua), (z0, 2), (z1, 2)):
            fs = []
            for f in near():
                cs = [v.co[k] for v in f.verts]
                if not (min(cs) < val - 1e-5 and max(cs) > val + 1e-5):
                    continue
                c = f.calc_center_median()
                if k == 2:
                    if max(v.co[ua] for v in f.verts) <= u0 or min(v.co[ua] for v in f.verts) >= u1:
                        continue
                else:
                    if max(v.co.z for v in f.verts) <= z0 or min(v.co.z for v in f.verts) >= z1:
                        continue
                fs.append(f)
            if not fs:
                continue
            es = list({e for f in fs for e in f.edges})
            vs = list({v for f in fs for v in f.verts})
            co, no = [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
            co[k], no[k] = val, 1.0
            bmesh.ops.bisect_plane(bm, geom=vs + es + fs, dist=1e-6, plane_co=co, plane_no=no)
        dead = []
        for f in near():
            c = f.calc_center_median()
            if u0 < c[ua] < u1 and z0 < c.z < z1:
                dead.append(f)
        if dead:
            bmesh.ops.delete(bm, geom=dead, context="FACES")


def frame_ring(bm, w, uc, zc, hw, hh, prof, r0=0.03, m=2):
    loops = []
    for o, v in prof:
        pts = rrect(2 * (hw + o), 2 * (hh + o), r0 + max(o, 0.0), m, uc, zc)
        loops.append([bm.verts.new(w.P(u, v, z)) for u, z in pts])
    n = len(loops[0])
    faces = []
    for a in range(len(loops)):
        L0, L1 = loops[a], loops[(a + 1) % len(loops)]
        for k in range(n):
            faces.append(bm.faces.new((L0[k], L0[(k + 1) % n], L1[(k + 1) % n], L1[k])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def ring_prof(o0, o1, v0, v1, ch):
    return [(o0, v0 + ch), (o0 + ch, v0), (o1 - ch, v0), (o1, v0 + ch), (o1, v1 - ch), (o1 - ch, v1), (o0 + ch, v1), (o0, v1 - ch)]


WIN_HW, WIN_HH, WIN_FW = 0.5, 0.6, 0.1


def cross_window(B, w, uc, z_sill, glass_log=None, hood=True):
    hw, hh, fw = WIN_HW, WIN_HH, WIN_FW
    zb = z_sill + fw - 0.02
    zc = zb + hh
    T = w.T
    frame_ring(B["SH_Timber"], w, uc, zc, hw, hh, ring_prof(0.0, fw, -0.05, T + 0.05, 0.018))
    frame_ring(B["SH_Walnut"], w, uc, zc, hw, hh, ring_prof(fw - 0.03, fw + 0.03, -0.072, T + 0.072, 0.012), r0=0.03, m=2)
    vm = T / 2
    g0, g1 = w.P(uc - hw - 0.012, vm - 0.005, zb - 0.012), w.P(uc + hw + 0.012, vm + 0.005, zb + 2 * hh + 0.012)
    gb = B["SH_Glass"]
    for vv, want in ((vm - 0.005, w.n), (vm + 0.005, -w.n)):
        w.face(gb, [(uc - hw - 0.012, vv, zb - 0.012), (uc + hw + 0.012, vv, zb - 0.012),
                    (uc + hw + 0.012, vv, zb + 2 * hh + 0.012), (uc - hw - 0.012, vv, zb + 2 * hh + 0.012)], want)
    if glass_log is not None:
        c = w.P(uc, vm, zc)
        size = (2 * hw, 0.01, 2 * hh) if w.axis == "x" else (0.01, 2 * hw, 2 * hh)
        glass_log.append((tuple(round(x, 3) for x in c), size))
    w.box(B["SH_Timber"], uc - 0.042, uc + 0.042, vm - 0.045, vm + 0.045, zb - 0.015, zb + 2 * hh + 0.015, r=0.02, segs=1)
    w.box(B["SH_Timber"], uc - hw - 0.015, uc + hw + 0.015, vm - 0.033, vm + 0.033, zc - 0.04, zc + 0.04, r=0.016, segs=1)
    for v, d in ((vm - 0.043, w.n), (vm + 0.043, -w.n)):
        M = Matrix.Translation(w.P(uc, v, zc)) @ Vector(d).to_track_quat("Z", "Y").to_matrix().to_4x4()
        lathe_bm([(0.0, 0.0), (0.062, 0.0), (0.066, 0.014), (0.05, 0.028), (0.0, 0.034)], 8, bm=B["SH_Walnut"], matrix=M)
    zs = zb - fw
    w.box(B["SH_Walnut"], uc - hw - fw - 0.1, uc + hw + fw + 0.1, -0.17, 0.03, zs - 0.07, zs + 0.03, r=0.028, segs=2)
    w.box(B["SH_Timber"], uc - hw - 0.02, uc + hw + 0.02, -0.11, -0.03, zs - 0.2, zs - 0.065, r=0.025, segs=1)
    w.box(B["SH_Walnut"], uc - hw - fw - 0.08, uc + hw + fw + 0.08, T - 0.03, T + 0.15, zs - 0.08, zs + 0.012, r=0.028, segs=2)
    if hood:
        zt = zb + 2 * hh + fw
        for v0, v1 in ((-0.115, 0.02), (T - 0.02, T + 0.115)):
            w.box(B["SH_Walnut"], uc - hw - fw - 0.06, uc + hw + fw + 0.06, v0, v1, zt - 0.005, zt + 0.075, r=0.03, segs=2)
    return (uc - hw, uc + hw, zb, zb + 2 * hh)


def persp_cam(path, loc, look, lens=20.0, res=(960, 640)):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("pcam")
    cd.type = "PERSP"
    cd.lens = lens
    cd.clip_start = 0.05
    cd.clip_end = 300
    cam = bpy.data.objects.new("pcam", cd)
    sc.collection.objects.link(cam)
    cam.location = Vector(loc)
    cam.rotation_euler = (Vector(look) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def sheet_any(out_dir, cells, path, cw, ch, cols=3):
    pad = 8
    rows = (len(cells) + cols - 1) // cols
    W = cols * cw + (cols + 1) * pad
    H = rows * ch + (rows + 1) * pad
    canvas = np.ones((H, W, 4), dtype=np.float32)
    canvas[..., :3] = 0.16
    for idx, name in enumerate(cells):
        img = read_png(os.path.join(out_dir, name))
        h, w_ = img.shape[:2]
        r, c = idx // cols, idx % cols
        top = H - pad - (r + 1) * ch - r * pad
        left = pad + c * (cw + pad)
        canvas[top:top + h, left:left + w_] = img
    img = bpy.data.images.new("sheet", W, H, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    print("SHEET", path)


class Shed:
    def __init__(self, x_hi, x_wall, eave, zc_wall, zc_hi, y0, y1, rake):
        self.sx = 1.0 if x_hi > x_wall else -1.0
        self.x_hi, self.x_wall = x_hi, x_wall
        self.x_e = x_wall - self.sx * eave
        slope = (zc_hi - zc_wall) / abs(x_hi - x_wall)
        self.th = math.atan(slope)
        self.slope = slope
        self.zc_e = zc_wall - eave * slope
        c, s = math.cos(self.th), math.sin(self.th)
        self.d = Vector((self.sx * c, 0, s))
        self.nrm = Vector((-self.sx * s, 0, c))
        self.S_hi = abs(x_hi - self.x_e) / c
        self.Y0, self.Y1 = y0 - rake, y1 + rake

    def R(self, s, y, t):
        return Vector((self.x_e, 0.0, self.zc_e)) + self.d * s + Vector((0, y, 0)) + self.nrm * t

    def s_of_x(self, x):
        return abs(x - self.x_e) / math.cos(self.th)

    def zc(self, x):
        return self.zc_e + abs(x - self.x_e) * self.slope

    def quad(self, bm, pts, want):
        return oface(bm, [tuple(self.R(*p)) for p in pts], want)

    def prism_y(self, bm, prof, y0, y1, caps=(True, True), skip=()):
        F = [bm.verts.new(self.R(s, y0, t)) for s, t in prof]
        K = [bm.verts.new(self.R(s, y1, t)) for s, t in prof]
        n = len(prof)
        cs = sum((Vector((s, t)) for s, t in prof), Vector((0, 0))) / n
        for k in range(n):
            if k in skip:
                continue
            k1 = (k + 1) % n
            f = bm.faces.new((F[k], F[k1], K[k1], K[k]))
            f.normal_update()
            mid = Vector(((prof[k][0] + prof[k1][0]) / 2, (prof[k][1] + prof[k1][1]) / 2))
            dd = mid - cs
            want = self.d * dd.x + self.nrm * dd.y
            if f.normal.dot(want) < 0:
                f.normal_flip()
        if caps[0]:
            f = bm.faces.new(F)
            f.normal_update()
            if f.normal.y > 0:
                f.normal_flip()
        if caps[1]:
            f = bm.faces.new(K)
            f.normal_update()
            if f.normal.y < 0:
                f.normal_flip()
        return bm


def rafter_profile(L, depth, tail_r, head_cut=0.0, n=4):
    pts = [(L, 0.0), (L, -depth)]
    for k in range(n + 1):
        a = math.pi / 2 * k / n
        pts.append((tail_r - tail_r * math.sin(a) + 0.0, -depth + tail_r - tail_r * math.cos(a)))
    pts.append((0.0, 0.0))
    out = []
    for p in pts:
        if not out or (Vector(p) - Vector(out[-1])).length > 1e-5:
            out.append(p)
    return out


def build_shed_roof(S, rafters_y, ledger_y, wall_y, wall_T, gables, cap_top, rng, honey_every=4, lanterns=(), lintel=None):
    B = Bins()
    S_hi = S.S_hi
    nb = max(1, int(round(S_hi / 0.22)))
    bw = S_hi / nb
    ch, dz = 0.016, 0.009
    for i in range(nb):
        a, b = i * bw, (i + 1) * bw
        S.quad(B["SH_Oak"], [(a + ch, S.Y0, 0.0), (b - ch, S.Y0, 0.0), (b - ch, S.Y1, 0.0), (a + ch, S.Y1, 0.0)], -S.nrm)
        S.quad(B["SH_Honey"], [(a, S.Y0, dz), (a + ch, S.Y0, 0.0), (a + ch, S.Y1, 0.0), (a, S.Y1, dz)], -S.nrm - S.d)
        S.quad(B["SH_Honey"], [(b - ch, S.Y0, 0.0), (b, S.Y0, dz), (b, S.Y1, dz), (b - ch, S.Y1, 0.0)], -S.nrm + S.d)
    t0, t1 = dz, 0.11
    S.prism_y(B["SH_Timber"], [(0.0, t0), (S_hi, t0), (S_hi, t1), (0.0, t1)], S.Y0, S.Y1)
    row, lap = 0.4, 0.13
    s = -0.035
    k = 0
    prev = []
    while s < S_hi - 0.05:
        cuts = []
        s1 = min(s + row + lap, S_hi + 0.02)
        prof = [(s, t1 - 0.004), (s1, t1 - 0.004), (s1, t1 + 0.03), (s + 0.03, t1 + 0.068), (s, t1 + 0.042)]
        mat = "SH_Honey" if k % honey_every == honey_every - 1 else "SH_Walnut"
        skip = (() if k == 0 else (0,)) + ((1,) if s1 < S_hi else ())
        y = S.Y0 + 0.004
        first = True
        while y < S.Y1 - 0.004:
            L = rng.uniform(0.35, 0.7) if (first and k % 2) else rng.uniform(0.8, 1.5)
            first = False
            yb = y + L
            while any(abs(yb - c) < 0.07 or abs(yb + 0.032 - c) < 0.07 for c in prev):
                yb += 0.05
            yb = min(yb, S.Y1 - 0.004)
            if S.Y1 - 0.004 - yb < 0.15:
                yb = S.Y1 - 0.004
            S.prism_y(B[mat], prof, y, yb, skip=skip)
            cuts += [y, yb]
            y = yb + 0.032
        prev = cuts
        s += row
        k += 1
    top = S_hi - 0.06
    tube_bm([tuple(S.R(top, S.Y0 - 0.03, t1 + 0.06)), tuple(S.R(top, S.Y1 + 0.03, t1 + 0.06))], 0.07, 8, bm=B["SH_Walnut"])
    for yb0, yb1 in ((S.Y0 - 0.055, S.Y0), (S.Y1, S.Y1 + 0.055)):
        prof = [(S_hi, -0.06), (S_hi, t1 + 0.1), (0.12, t1 + 0.1)]
        for k2 in range(1, 5):
            a = math.pi / 2 * k2 / 4
            prof.append((0.12 - 0.17 * math.sin(a), t1 + 0.1 - 0.17 * (1 - math.cos(a))))
        prof += [(-0.05, -0.04), (0.08, -0.06)]
        S.prism_y(B["SH_Walnut"], prof, yb0, yb1)
    dep = 0.17
    s_head, s_tail = S_hi + 0.01, 0.1
    for y in rafters_y:
        prof = [(p0 + s_tail, p1 + 0.004) for p0, p1 in rafter_profile(s_head - s_tail, dep, 0.11)]
        S.prism_y(B["SH_Timber"], prof, y - 0.055, y + 0.055, skip=(len(prof) - 1,))
    xh = S.x_hi
    zt = S.zc(xh)
    a0, a1 = sorted((xh, xh - S.sx * 0.17))
    wbox(B["SH_Timber"], (a0, ledger_y[0], zt - 0.27), (a1, ledger_y[1], zt + 0.02), r=0.035, segs=2)
    xw = S.x_wall
    xi = xw + S.sx * wall_T
    a0, a1 = sorted((xw + S.sx * 0.02, xi + S.sx * 0.02))
    wbox(B["SH_Timber"], (a0, wall_y[0], cap_top - 0.03), (a1, wall_y[1], S.zc(xi) + 0.006), r=0.02, segs=1)
    for g in gables:
        gable(B, S, *g)
    if lintel is not None:
        x0, x1, ys = lintel
        for y_in, y_out in ys:
            ya, yb = sorted((y_in, y_out))
            wbox(B["SH_Timber"], (x0, ya - 0.05, cap_top - 0.22), (x1, yb + 0.05, cap_top + 0.01), r=0.04, segs=2)
    for lx, ly in lanterns:
        hang_lantern(B, S, lx, ly)
    return B


def gable(B, S, y_in, y_out, x_end, cap_top, studs, battens=()):
    inward = 1.0 if y_out < y_in else -1.0
    T = abs(y_out - y_in)
    xa, xb = sorted((S.x_hi, x_end))
    w = Wall("x", xa, xb, y_in, inward, T, 0.0, 0.0, 0.0)

    def ztop(x, dzz=0.016):
        return S.zc(x) + dzz

    z0 = cap_top - 0.012
    for v0, v1, mat in ((0.0, T / 2, "SH_Parchment"), (T / 2, T, "SH_Honey")):
        w.face(B[mat], [(xa, v0, z0), (xb, v0, z0), (xb, v0, ztop(xb)), (xa, v0, ztop(xa))], w.n)
        w.face(B[mat], [(xa, v1, z0), (xb, v1, z0), (xb, v1, ztop(xb)), (xa, v1, ztop(xa))], -w.n)
        for x, sg in ((xa, -1), (xb, 1)):
            w.face(B[mat], [(x, v0, z0), (x, v1, z0), (x, v1, ztop(x)), (x, v0, ztop(x))], Vector((sg, 0, 0)))
    nbd = max(1, int(round((xb - xa) / 0.22)))
    bwid = (xb - xa) / nbd
    depth, groove, chh = 0.013, 0.008, 0.014
    vf, vg = T + depth, T + depth - groove
    for i in range(nbd):
        a = xa + i * bwid
        b = a + bwid
        za, zb_ = ztop(a, -0.01), ztop(b, -0.01)
        zam, zbm = ztop(a + chh, -0.01), ztop(b - chh, -0.01)
        w.face(B["SH_Walnut"], [(a, vg, z0), (a + chh, vf, z0), (a + chh, vf, zam), (a, vg, za)], -w.n)
        w.face(B["SH_Honey"], [(a + chh, vf, z0), (b - chh, vf, z0), (b - chh, vf, zbm), (a + chh, vf, zam)], -w.n)
        w.face(B["SH_Walnut"], [(b - chh, vf, z0), (b, vg, z0), (b, vg, zb_), (b - chh, vf, zbm)], -w.n)
        w.face(B["SH_Walnut"], [(a, vg, za), (a + chh, vf, zam), (b - chh, vf, zbm), (b, vg, zb_)], Vector((0, 0, 1)))
    w.box(B["SH_Timber"], xa, xb, -0.035, 0.004, cap_top - 0.01, cap_top + 0.1, r=0.022, segs=1)
    L = abs(xb - xa) / math.cos(S.th)
    xm = (xa + xb) / 2
    c = w.P(xm, -0.02, S.zc(xm) - 0.06)
    rbox_bm(c, (L, 0.05, 0.12), 0.02, 1, bm=B["SH_Timber"], matrix=Matrix.Rotation(-S.sx * S.th, 4, "Y"))
    for x in studs:
        w.box(B["SH_Timber"], x - 0.06, x + 0.06, -0.058, 0.004, cap_top + 0.05, S.zc(x) - 0.09, r=0.022, segs=1)
    for x in battens:
        w.box(B["SH_Timber"], x - 0.07, x + 0.07, T + 0.004, T + 0.05, cap_top + 0.04, S.zc(x) - 0.03, r=0.022, segs=1)


def hang_lantern(B, S, x, y):
    zc_ = S.zc(x)
    top = Vector((x, y, zc_ - 0.17))
    c = Vector((x, y, zc_ - 0.85))
    tube_bm([top + Vector((0, 0, 0.02)), c + Vector((0, 0, 0.17))], 0.012, 4, bm=B["SH_Timber"])
    lathe_bm([(0.0, 0.13), (0.11, 0.12), (0.125, 0.1), (0.05, 0.18), (0.0, 0.2)], 8, bm=B["SH_Timber"], matrix=Matrix.Translation(c))
    ellipsoid_bm(c, (0.095, 0.095, 0.13), 8, 5, bm=B["SH_Gold"])
    lathe_bm([(0.0, -0.15), (0.08, -0.12), (0.085, -0.095), (0.0, -0.085)], 8, bm=B["SH_Timber"], matrix=Matrix.Translation(c))
    torus_bm(0.035, 0.012, 8, 4, bm=B["SH_Timber"], matrix=Matrix.Translation(c + Vector((0, 0, 0.215))) @ Matrix.Rotation(math.pi / 2, 4, "X"))
