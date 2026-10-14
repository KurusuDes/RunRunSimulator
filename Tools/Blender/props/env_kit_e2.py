import sys, random
sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
from props_common import *
from mathutils.bvhtree import BVHTree

SCRATCH = r"C:\Users\Docente\AppData\Local\Temp\claude\C--Users-Docente-Desktop-UnityProyects-RunRunSimulator\4d55ec4f-97d7-4ab7-b7aa-aab8024c682a\scratchpad"
OBJ_PATH = os.path.join(SCRATCH, "shop_env", "shop_env.obj")
MARKERS_PATH = os.path.join(SCRATCH, "shop_env", "markers.csv")

EXTRA = {"SH_Grass": "A8D477"}

ZOC_H = 0.12
FRISO_H = 0.90
PIL_OUT = 0.035


def add_mat(name, hx):
    rgb = [srgb_to_linear(int(hx[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = next((n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
    MATS[name] = m


def begin_env():
    begin()
    for k, v in EXTRA.items():
        add_mat(k, v)


class Bins(dict):
    def __missing__(self, k):
        self[k] = bmesh.new()
        return self[k]

    def done(self, prefix, angle=40.0):
        obs = []
        for k, bm in list(self.items()):
            if len(bm.verts) == 0:
                bm.free()
                continue
            obs.append(finish(prefix + "_" + k, bm, k, angle=angle))
        self.clear()
        return obs


def wbox(bm, mn, mx, r=0.0, segs=1):
    c = [(a + b) / 2 for a, b in zip(mn, mx)]
    s = [abs(b - a) for a, b in zip(mn, mx)]
    if r > 0:
        r = min(r, min(s) / 2 - 0.0015)
        return rbox_bm(c, s, r, segs, bm=bm)
    before = set(bm.verts)
    bmesh.ops.create_cube(bm, size=1.0)
    for v in [v for v in bm.verts if v not in before]:
        v.co = Vector((c[0] + v.co.x * s[0], c[1] + v.co.y * s[1], c[2] + v.co.z * s[2]))
    return bm


def oface(bm, pts, want):
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    f.normal_update()
    if f.normal.dot(Vector(want)) < 0:
        f.normal_flip()
    return f


def disc(bm, x, y, r0, r1, ztop, zbot, n=16):
    top = [(x + r0 * math.cos(2 * math.pi * k / n), y + r0 * math.sin(2 * math.pi * k / n), ztop) for k in range(n)]
    bot = [(x + r1 * math.cos(2 * math.pi * k / n), y + r1 * math.sin(2 * math.pi * k / n), zbot) for k in range(n)]
    oface(bm, top, (0, 0, 1))
    for k in range(n):
        k1 = (k + 1) % n
        oface(bm, [bot[k], bot[k1], top[k1], top[k]], ((top[k][0] - x), (top[k][1] - y), 0.3))
    return bm


def quad_z(bm, x0, x1, y0, y1, z):
    return oface(bm, [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], (0, 0, 1))


def chamfer_tile(bm, x0, x1, y0, y1, ztop, ch=0.012, dz=0.008):
    a = [(x0, y0, ztop - dz), (x1, y0, ztop - dz), (x1, y1, ztop - dz), (x0, y1, ztop - dz)]
    b = [(x0 + ch, y0 + ch, ztop), (x1 - ch, y0 + ch, ztop), (x1 - ch, y1 - ch, ztop), (x0 + ch, y1 - ch, ztop)]
    oface(bm, b, (0, 0, 1))
    outs = [(0, -1, 1), (1, 0, 1), (0, 1, 1), (-1, 0, 1)]
    for k in range(4):
        k1 = (k + 1) % 4
        oface(bm, [a[k], a[k1], b[k1], b[k]], outs[k])
    return bm


class Wall:
    def __init__(self, axis, a0, a1, plane, inward, T, zt, fin, gout):
        self.axis, self.a0, self.a1 = axis, a0, a1
        self.plane, self.inward, self.T, self.zt = plane, inward, T, zt
        self.fin, self.gout = fin, gout
        self.n = Vector((0, inward, 0)) if axis == "x" else Vector((inward, 0, 0))

    def P(self, u, v, z):
        w = self.plane - self.inward * v
        return Vector((u, w, z)) if self.axis == "x" else Vector((w, u, z))

    def box(self, bm, u0, u1, v0, v1, z0, z1, r=0.0, segs=1):
        a = self.P(u0, v0, z0)
        b = self.P(u1, v1, z1)
        return wbox(bm, [min(a[i], b[i]) for i in range(3)], [max(a[i], b[i]) for i in range(3)], r, segs)

    def face(self, bm, pts, want):
        return oface(bm, [self.P(*p) for p in pts], want)

    def boards(self, bl, bd, u0, u1, z0, z1, outer=False, bw=0.17, depth=0.02, groove=0.011, ch=0.014):
        n = max(1, int(round((u1 - u0) / bw)))
        bw = (u1 - u0) / n
        if outer:
            vf, vg, want = self.T + depth, self.T + depth - groove, -self.n
        else:
            vf, vg, want = -depth, -depth + groove, self.n
        for i in range(n):
            a = u0 + i * bw
            b = a + bw
            self.face(bd, [(a, vg, z0), (a + ch, vf, z0), (a + ch, vf, z1), (a, vg, z1)], want)
            self.face(bl, [(a + ch, vf, z0), (b - ch, vf, z0), (b - ch, vf, z1), (a + ch, vf, z1)], want)
            self.face(bd, [(b - ch, vf, z0), (b, vg, z0), (b, vg, z1), (b - ch, vf, z1)], want)
        vb = self.T if outer else 0.0
        ud = Vector((1, 0, 0)) if self.axis == "x" else Vector((0, 1, 0))
        self.face(bd, [(u0, vb, z0), (u0, vg, z0), (u0, vg, z1), (u0, vb, z1)], -ud)
        self.face(bd, [(u1, vb, z0), (u1, vg, z0), (u1, vg, z1), (u1, vb, z1)], ud)
        self.face(bd, [(u0, vb, z1), (u1, vb, z1), (u1, vf, z1), (u0, vf, z1)], (0, 0, 1))


def wall_body(B, w, inner="SH_Cream", outer="SH_Coral", u0=None, u1=None):
    u0 = w.a0 if u0 is None else u0
    u1 = w.a1 if u1 is None else u1
    w.box(B[inner], u0, u1, 0.0, w.T / 2, w.fin - 0.02, w.zt)
    w.box(B[outer], u0, u1, w.T / 2, w.T, w.gout - 0.01, w.zt)


def wall_inner(B, w, u0, u1, friso, style="plain", dark=None):
    f = w.fin
    if style == "boards":
        w.boards(B[friso], B[dark or friso], u0, u1, f + ZOC_H - 0.02, f + FRISO_H - 0.03)
    else:
        w.box(B[friso], u0, u1, -0.016, 0.004, f, f + FRISO_H - 0.02, r=0.006)
    w.box(B["SH_WoodDark"], u0, u1, -0.04, 0.0, f - 0.01, f + ZOC_H, r=0.016, segs=1)
    w.box(B["SH_Wood"], u0, u1, -0.045, 0.0, f + FRISO_H - 0.05, f + FRISO_H + 0.03, r=0.022, segs=2)


def wall_outer(B, w, u0, u1, trim="SH_Cream", style="plaster", siding="SH_Coral", dark="SH_Peach"):
    g = w.gout
    if style == "boards":
        w.boards(B[siding], B[dark], u0, u1, g + 0.26, w.zt - 0.24, outer=True, bw=0.2)
    w.box(B[trim], u0, u1, w.T - 0.004, w.T + 0.035, g - 0.01, g + 0.28, r=0.016, segs=1)
    w.box(B[trim], u0, u1, w.T - 0.004, w.T + 0.03, w.zt - 0.26, w.zt - 0.18, r=0.015, segs=1)


def wall_cap(B, w, u0, u1, mat="SH_WoodDark", over=0.05):
    w.box(B[mat], u0, u1, -over, w.T + over, w.zt - 0.07, w.zt + 0.09, r=0.04, segs=2)


def pillar_box(B, mn, mx, mat="SH_Wood", cap="SH_WoodDark"):
    wbox(B[mat], mn, mx, r=0.05, segs=2)
    wbox(B[cap], (mn[0] - 0.015, mn[1] - 0.015, mx[2] - 0.03), (mx[0] + 0.015, mx[1] + 0.015, mx[2] + 0.07), r=0.035, segs=1)


def wall_pillar(B, w, uc, width=0.32, u0=None, u1=None, mat="SH_Wood"):
    if u0 is None:
        u0, u1 = uc - width / 2, uc + width / 2
    a = w.P(u0, -PIL_OUT, min(w.fin, w.gout) - 0.01)
    b = w.P(u1, w.T + PIL_OUT, w.zt + 0.15)
    pillar_box(B, [min(a[i], b[i]) for i in range(3)], [max(a[i], b[i]) for i in range(3)], mat)


def corner_pillar(B, x0, x1, y0, y1, z0, z1, mat="SH_Wood"):
    pillar_box(B, (x0 - PIL_OUT, y0 - PIL_OUT, z0), (x1 + PIL_OUT, y1 + PIL_OUT, z1), mat)


def star_local(w, bm, uc, zc, R, r, depth, outer=False):
    vbase = w.T if outer else 0.0
    sgn = 1 if outer else -1
    want = -w.n if outer else w.n
    prof = [(1.0, 0.004), (1.0, depth * 0.55), (0.84, depth * 0.9), (0.6, depth)]
    rings = []
    for s, d in prof:
        ring = []
        for k in range(10):
            a = math.pi / 2 + math.pi * k / 5
            rad = (R if k % 2 == 0 else r) * s
            ring.append(bm.verts.new(w.P(uc + rad * math.cos(a), vbase + sgn * d - sgn * 0.004, zc + rad * math.sin(a))))
        rings.append(ring)
    faces = []
    for A, Bv in zip(rings, rings[1:]):
        for k in range(10):
            faces.append(bm.faces.new((A[k], A[(k + 1) % 10], Bv[(k + 1) % 10], Bv[k])))
    top = bm.faces.new(rings[-1])
    top.normal_update()
    if top.normal.dot(want) < 0:
        top.normal_flip()
    for f in faces:
        f.normal_update()
        c = f.calc_center_median()
        cen = w.P(uc, vbase, zc)
        radial = (c - cen)
        radial = radial - want * radial.dot(want)
        if f.normal.dot(radial + want * 0.3) < 0:
            f.normal_flip()
    return bm


def dot_local(w, bm, uc, zc, R, depth, outer=False, segs=14):
    vbase = w.T if outer else 0.0
    sgn = 1 if outer else -1
    want = -w.n if outer else w.n
    prof = [(R, 0.004), (R, depth * 0.5), (R * 0.82, depth)]
    rings = []
    for rr, d in prof:
        rings.append([bm.verts.new(w.P(uc + rr * math.cos(2 * math.pi * k / segs), vbase + sgn * d - sgn * 0.004,
                                       zc + rr * math.sin(2 * math.pi * k / segs))) for k in range(segs)])
    for A, Bv in zip(rings, rings[1:]):
        for k in range(segs):
            f = bm.faces.new((A[k], A[(k + 1) % segs], Bv[(k + 1) % segs], Bv[k]))
            f.normal_update()
            c = f.calc_center_median() - w.P(uc, vbase, zc)
            if f.normal.dot(c - want * c.dot(want) + want * 0.3) < 0:
                f.normal_flip()
    top = bm.faces.new(rings[-1])
    top.normal_update()
    if top.normal.dot(want) < 0:
        top.normal_flip()
    return bm


def tuft(bm, x, y, z, rng, h=0.13):
    for k in range(3):
        a = rng.uniform(0, 2 * math.pi)
        lean = Vector((math.cos(a), math.sin(a), 0)) * rng.uniform(0.02, 0.05)
        hb = h * rng.uniform(0.7, 1.1)
        base = Vector((x + math.cos(a) * 0.025, y + math.sin(a) * 0.025, z - 0.01))
        tip = base + lean + Vector((0, 0, hb))
        rb = 0.03
        b = [bm.verts.new(base + Vector((math.cos(a + j * math.pi / 2) * rb, math.sin(a + j * math.pi / 2) * rb, 0))) for j in range(4)]
        t = bm.verts.new(tip)
        for j in range(4):
            f = bm.faces.new((b[j], b[(j + 1) % 4], t))
            f.normal_update()
            if f.normal.dot(f.calc_center_median() - Vector((base.x, base.y, f.calc_center_median().z))) < 0:
                f.normal_flip()
    return bm


def flower(bp, bc, x, y, z, rng, R=0.075):
    rot = rng.uniform(0, 2 * math.pi)
    pts = []
    for k in range(10):
        a = rot + 2 * math.pi * k / 10
        lob = 0.62 + 0.38 * abs(math.cos(5 * (a - rot) / 2))
        pts.append((x + R * lob * math.cos(a), y + R * lob * math.sin(a)))
    top = [bp.verts.new((px, py, z + 0.02)) for px, py in pts]
    bot = [bp.verts.new((px, py, z)) for px, py in pts]
    c = bp.verts.new((x, y, z + 0.02))
    n = len(pts)
    for k in range(n):
        f = bp.faces.new((top[k], top[(k + 1) % n], c))
        f.normal_update()
        if f.normal.z < 0:
            f.normal_flip()
        f2 = bp.faces.new((bot[k], bot[(k + 1) % n], top[(k + 1) % n], top[k]))
        f2.normal_update()
        m = f2.calc_center_median()
        if f2.normal.dot(Vector((m.x - x, m.y - y, 0))) < 0:
            f2.normal_flip()
    ellipsoid_bm((x, y, z + 0.03), (R * 0.4, R * 0.4, R * 0.3), 6, 3, bm=bc)


def stone(bm, x, y, z, rng, w=0.5, d=0.42, ch=0.02, dz=0.012, rot=None):
    rot = rng.uniform(-0.35, 0.35) if rot is None else rot
    w *= rng.uniform(0.85, 1.12)
    d *= rng.uniform(0.85, 1.12)
    m = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rot, 4, "Z")
    r = min(w, d) * 0.42
    loft([(w, d, r, z - dz), (w - 2 * ch, d - 2 * ch, r - ch, z)], 1, cap0=False, bm=bm, matrix=m)
    return bm


def markers():
    out = {}
    for line in open(MARKERS_PATH):
        if line.startswith("#") or not line.strip():
            continue
        t = [s.strip() for s in line.split(",")]
        out[t[0]] = tuple(float(v) for v in t[1:])
    return out


def in_rects(x, y, rects, pad=0.0):
    for x0, x1, y0, y1 in rects:
        if x0 - pad <= x <= x1 + pad and y0 - pad <= y <= y1 + pad:
            return True
    return False


def seg_dist(p, a, b):
    p, a, b = Vector(p), Vector(a), Vector(b)
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (a + ab * t - p).length


def poly_dist(p, poly):
    return min(seg_dist(p, a, b) for a, b in zip(poly, poly[1:]))


def path_stones(bm, poly, z, rng, step=0.72, w=0.52, d=0.44):
    pts = []
    for a, b in zip(poly, poly[1:]):
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        n = max(1, int(L / step))
        for i in range(n):
            pts.append((a + (b - a) * (i + 0.5) / n, (b - a).normalized()))
    for k, (p, t) in enumerate(pts):
        side = Vector((-t.y, t.x)) * (0.09 if k % 2 == 0 else -0.09)
        q = p + side
        stone(bm, q.x, q.y, z, rng, w, d, rot=math.atan2(t.y, t.x) + rng.uniform(-0.25, 0.25))
    return bm


def bvh_of(objs):
    dg = bpy.context.evaluated_depsgraph_get()
    return [BVHTree.FromObject(o, dg) for o in objs]


def ray_min(trees, o, d, maxd=10.0):
    best = None
    for t in trees:
        hit = t.ray_cast(Vector(o), Vector(d), maxd)
        if hit[0] is not None and (best is None or hit[3] < best):
            best = hit[3]
    return best


def check_floor(objs, rects, ztarget, step=0.37, label=""):
    trees = bvh_of(objs)
    worst = 0.0
    n = miss = 0
    for x0, x1, y0, y1 in rects:
        nx = max(1, int((x1 - x0) / step))
        ny = max(1, int((y1 - y0) / step))
        for i in range(nx):
            for j in range(ny):
                x = x0 + (i + 0.5) * (x1 - x0) / nx
                y = y0 + (j + 0.5) * (y1 - y0) / ny
                d = ray_min(trees, (x, y, ztarget + 2.0), (0, 0, -1), 4.0)
                if d is None:
                    miss += 1
                    continue
                n += 1
                worst = max(worst, abs((ztarget + 2.0 - d) - ztarget))
    print("CHECK_FLOOR %s samples=%d miss=%d max_dev=%.4f" % (label, n, miss, worst))
    return worst


def check_wall(objs, w, u0, u1, skip=(), label=""):
    trees = bvh_of(objs)
    worst = 0.0
    n = 0
    u = u0 + 0.12
    while u < u1 - 0.12:
        if not any(abs(u - s) < 0.28 for s in skip):
            for dz in (0.5, 1.2):
                z = w.fin + dz
                if z > w.zt - 0.3:
                    continue
                o = w.P(u, -1.0, z)
                dvec = w.P(u, 1.0, z) - w.P(u, 0.0, z)
                d = ray_min(trees, o, dvec, 3.0)
                if d is None:
                    continue
                n += 1
                worst = max(worst, abs(d - 1.0))
        u += 0.23
    print("CHECK_WALL %s samples=%d max_dev=%.4f" % (label, n, worst))
    return worst


def import_ctx(piece_keys, wire=True):
    before = set(bpy.data.objects)
    bpy.ops.wm.obj_import(filepath=OBJ_PATH, forward_axis="Y", up_axis="Z")
    new = [o for o in bpy.data.objects if o not in before]
    ctx = bpy.data.materials.new("Ctx")
    ctx.diffuse_color = (0.62, 0.62, 0.64, 1)
    mag = bpy.data.materials.new("Wire")
    mag.diffuse_color = (1.0, 0.0, 0.85, 1)
    mine, others = [], []
    for o in new:
        o.data.materials.clear()
        if any(k in o.name for k in piece_keys):
            o.data.materials.append(mag)
            if wire:
                mod = o.modifiers.new("w", "WIREFRAME")
                mod.thickness = 0.035
            mine.append(o)
        else:
            o.data.materials.append(ctx)
            others.append(o)
    return mine, others


def setup_env_scene():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light = "STUDIO"
    sh.color_type = "MATERIAL"
    sh.show_cavity = True
    sh.cavity_type = "BOTH"
    sh.show_object_outline = True
    sh.object_outline_color = (0.12, 0.1, 0.09)
    sh.show_backface_culling = True
    sh.show_shadows = True
    sh.shadow_intensity = 0.35
    sc.display.light_direction = (0.35, -0.45, 0.82)
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.35
    sc.world = sc.world or bpy.data.worlds.new("World")
    sc.world.color = (0.42, 0.45, 0.48)


def render_cam(path, az, el, target, ortho, res=(640, 640), dist=90.0):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ortho
    cd.clip_start = 0.5
    cd.clip_end = 300
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    a, e = math.radians(az), math.radians(el)
    t = Vector(target)
    cam.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def outline_composite(base_path, mask_path, out_path, col=(1.0, 0.0, 0.85)):
    A = read_png(base_path)
    M = read_png(mask_path)
    m = (M[..., 0] > 0.8) & (M[..., 1] < 0.3) & (M[..., 2] > 0.6)
    er = m.copy()
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0), (0, 2), (0, -2)):
        er &= np.roll(np.roll(m, dy, 0), dx, 1)
    edge = m & ~er
    A[edge, 0], A[edge, 1], A[edge, 2] = col
    h, w = A.shape[:2]
    img = bpy.data.images.new("ov", w, h, alpha=True)
    img.pixels.foreach_set(A.ravel())
    img.filepath_raw = out_path
    img.file_format = "PNG"
    img.save()
    print("OVERLAY", out_path)


def env_preview(ob, out, piece_keys, views, dragons, top_center, top_ortho, sheet_name=None):
    if not out:
        return
    os.makedirs(out, exist_ok=True)
    setup_env_scene()
    mine, others = import_ctx(piece_keys, wire=False)
    drag = []
    for d in dragons:
        drag += load_dragon(d[:3], d[3] if len(d) > 3 else -20.0)
    n = ob.name
    sc = bpy.context.scene
    sh = sc.display.shading
    sh.light = "FLAT"
    for o in others + mine + drag:
        o.hide_render = True
    base = os.path.join(out, n + "_top_base.png")
    render_cam(base, 0, 90, top_center, top_ortho, res=(1400, 1400))
    for o in mine:
        o.hide_render = False
    ob.hide_render = True
    sh.show_object_outline = False
    sh.show_cavity = False
    sc.view_settings.exposure = 0.0
    mask = os.path.join(out, n + "_top_mask.png")
    render_cam(mask, 0, 90, top_center, top_ortho, res=(1400, 1400))
    sh.show_object_outline = True
    sh.show_cavity = True
    sc.view_settings.exposure = 0.35
    outline_composite(base, mask, os.path.join(out, n + "_overlay_top.png"))
    ob.hide_render = False
    sh.light = "STUDIO"
    for o in others + drag:
        o.hide_render = False
    for o in mine:
        o.hide_render = True
    cells = []
    for tag, az, el, target, ortho in views:
        f = "%s_%s.png" % (n, tag)
        render_cam(os.path.join(out, f), az, el, target, ortho)
        cells.append(f)
    contact_sheet(out, cells, os.path.join(out, (sheet_name or n) + "_sheet.png"))


def parts_report():
    tot = 0
    for o in PARTS:
        t = sum(len(p.vertices) - 2 for p in o.data.polygons)
        tot += t
        print("PART %-28s %6d" % (o.name, t))
    print("PART total", tot)


def rotbox(w, bm, uc, vc, zc, L, thick, h, ang, r=0.02, segs=1):
    c = w.P(uc, vc, zc)
    if w.axis == "x":
        return rbox_bm(c, (L, thick, h), r, segs, bm=bm, matrix=Matrix.Rotation(-ang, 4, "Y"))
    return rbox_bm(c, (thick, L, h), r, segs, bm=bm, matrix=Matrix.Rotation(ang, 4, "X"))


def inner3(B, w, u0, u1, accent, board="SH_Honey", groove="SH_Walnut", bw=0.17):
    f = w.fin
    w.boards(B[board], B[groove], u0, u1, f + ZOC_H - 0.02, f + FRISO_H - 0.04, bw=bw)
    w.box(B["SH_Walnut"], u0, u1, -0.04, 0.0, f - 0.01, f + ZOC_H, r=0.016, segs=1)
    w.box(B[accent], u0, u1, -0.03, 0.0, f + FRISO_H - 0.06, f + FRISO_H - 0.01, r=0.008, segs=1)
    w.box(B["SH_Timber"], u0, u1, -0.045, 0.0, f + FRISO_H - 0.015, f + FRISO_H + 0.07, r=0.022, segs=2)


def girt3(B, w, u0, u1, z, outer=False):
    v0, v1 = (w.T, w.T + 0.04) if outer else (-0.04, 0.0)
    w.box(B["SH_Timber"], u0, u1, v0, v1, z, z + 0.11, r=0.025, segs=1)


def knee_braces(B, w, posts, z_lo, z_hi, half=0.15, outer=False):
    v = w.T + 0.022 if outer else -0.022
    dz = z_hi - z_lo
    L = math.hypot(dz, dz)
    for i, p in enumerate(posts):
        for sgn in (1, -1):
            if (i == 0 and sgn < 0) or (i == len(posts) - 1 and sgn > 0):
                continue
            uc = p + sgn * (half + dz / 2)
            rotbox(w, B["SH_Timber"], uc, v, z_lo + dz / 2, L + 0.06, 0.04, 0.12, math.radians(45 * sgn), r=0.018)


def stone_base(B, w, u0, u1, h=0.3, step=0.62, rng=None):
    g = w.gout
    w.box(B["SH_StoneDark"], u0, u1, w.T - 0.004, w.T + 0.03, g - 0.01, g + h, r=0.02, segs=1)
    rng = rng or random.Random(int(abs(u0) * 100))
    n = max(1, int((u1 - u0) / step))
    st = (u1 - u0) / n
    for i in range(n):
        uc = u0 + (i + 0.5) * st + rng.uniform(-0.05, 0.05)
        zc = g + h * (0.33 if i % 2 == 0 else 0.68)
        rr = st * rng.uniform(0.36, 0.44)
        c = w.P(uc, w.T + 0.03, zc)
        rad = (rr, 0.035, h * 0.3) if w.axis == "x" else (0.035, rr, h * 0.3)
        ellipsoid_bm(c, rad, 6, 3, bm=B["SH_Stone"])


def outer3(B, w, u0, u1, rng, board="SH_Honey", groove="SH_Walnut", stone_h=0.32, bw=0.22):
    g = w.gout
    stone_base(B, w, u0, u1, stone_h, rng=rng)
    w.boards(B[board], B[groove], u0, u1, g + stone_h - 0.02, w.zt - 0.24, outer=True, bw=bw)
    w.box(B["SH_Timber"], u0, u1, w.T - 0.004, w.T + 0.04, w.zt - 0.27, w.zt - 0.17, r=0.02, segs=1)


def cap3(B, w, u0, u1, over=0.05):
    w.box(B["SH_Timber"], u0, u1, -over, w.T + over, w.zt - 0.07, w.zt + 0.09, r=0.045, segs=2)


def post3(B, mn, mx):
    wbox(B["SH_Timber"], mn, mx, r=0.05, segs=1)
    cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
    r = min(mx[0] - mn[0], mx[1] - mn[1]) / 2 + 0.01
    z = mx[2]
    lathe_bm([(0.0, z - 0.03), (r + 0.015, z - 0.01), (r * 0.75, z + 0.07), (0.0, z + 0.11)],
             8, bm=B["SH_Walnut"], matrix=Matrix.Translation((cx, cy, 0)))


def wall_post3(B, w, uc=0.0, width=0.3, u0=None, u1=None, z0=None, z1=None):
    if u0 is None:
        u0, u1 = uc - width / 2, uc + width / 2
    a = w.P(u0, -PIL_OUT, (min(w.fin, w.gout) - 0.01) if z0 is None else z0)
    b = w.P(u1, w.T + PIL_OUT, (w.zt + 0.15) if z1 is None else z1)
    post3(B, [min(a[i], b[i]) for i in range(3)], [max(a[i], b[i]) for i in range(3)])


def corner_post3(B, x0, x1, y0, y1, z0, z1):
    post3(B, (x0 - PIL_OUT, y0 - PIL_OUT, z0), (x1 + PIL_OUT, y1 + PIL_OUT, z1))


def lantern(B, base, out_vec):
    o = Vector(out_vec).normalized()
    p = Vector(base)
    arm_end = p + o * 0.24
    tube_bm([p, p + o * 0.12 + Vector((0, 0, 0.05)), arm_end + Vector((0, 0, 0.02))], 0.02, 6, bm=B["SH_Timber"])
    c = arm_end + Vector((0, 0, -0.17))
    tube_bm([arm_end + Vector((0, 0, 0.02)), c + Vector((0, 0, 0.12))], 0.01, 4, bm=B["SH_Timber"])
    lathe_bm([(0.0, 0.09), (0.085, 0.09), (0.1, 0.075), (0.04, 0.13), (0.0, 0.14)], 8, bm=B["SH_Timber"], matrix=Matrix.Translation(c))
    ellipsoid_bm(c + Vector((0, 0, 0.0)), (0.072, 0.072, 0.1), 7, 4, bm=B["SH_Gold"])
    lathe_bm([(0.0, -0.11), (0.06, -0.09), (0.065, -0.07), (0.0, -0.06)], 8, bm=B["SH_Timber"], matrix=Matrix.Translation(c))


def ivy(B, w, u0, u1, rng, step=0.5, outer=True):
    u = u0
    k = 0
    while u < u1:
        for j in range(rng.choice((2, 3))):
            r = rng.uniform(0.07, 0.13)
            c = w.P(u + rng.uniform(-0.12, 0.12), w.T * rng.uniform(0.15, 0.85), w.zt + 0.07 + r * 0.5)
            ellipsoid_bm(c, (r, r * rng.uniform(0.8, 1.1), r * 0.7), 6, 3, bm=B["SH_Leaf" if (k + j) % 3 else "SH_Moss"])
        if outer and k % 2 == 0:
            n = rng.choice((1, 2, 3))
            for j in range(n):
                r = 0.075 - 0.012 * j
                ellipsoid_bm(w.P(u + rng.uniform(-0.05, 0.05), w.T + 0.075, w.zt - 0.06 - 0.15 * j), (r, r, r * 0.9), 6, 4,
                             bm=B["SH_Leaf" if j % 2 else "SH_Moss"])
        u += step * rng.uniform(0.7, 1.4)
        k += 1


def mushroom(B, x, y, z, s=1.0, cap="SH_Plum"):
    m = Matrix.Translation((x, y, 0))
    lathe_bm([(0.0, z - 0.01), (0.05 * s, z - 0.01), (0.04 * s, z + 0.1 * s), (0.045 * s, z + 0.16 * s), (0.0, z + 0.16 * s)], 8,
             bm=B["SH_Parchment"], matrix=m)
    lathe_bm([(0.0, z + 0.12 * s), (0.13 * s, z + 0.12 * s), (0.145 * s, z + 0.155 * s), (0.11 * s, z + 0.22 * s), (0.05 * s, z + 0.26 * s),
              (0.0, z + 0.27 * s)], 10, bm=B[cap], matrix=m)
    for a in (0.3, 2.4, 4.2):
        ellipsoid_bm((x + math.cos(a) * 0.075 * s, y + math.sin(a) * 0.075 * s, z + 0.235 * s), (0.024 * s, 0.024 * s, 0.014 * s), 5, 3,
                     bm=B["SH_Parchment"])


def hedge(bm, w, u0, u1, zb, ztop, rng, v0=0.0, v1=None, step=0.6, k=4):
    v1 = w.T if v1 is None else v1
    vm = (v0 + v1) / 2
    secs = []
    n = max(2, int((u1 - u0) / step) + 1)
    for i in range(n):
        u = u0 + (u1 - u0) * i / (n - 1)
        zt = ztop + (0.0 if i in (0, n - 1) else rng.uniform(-0.04, 0.05))
        sec = []
        for j in range(k + 1):
            t = math.pi * j / k
            sec.append(w.P(u, vm - math.cos(t) * (v1 - v0) / 2 * 1.05, zb + math.sin(t) * (zt - zb)))
        secs.append((u, sec))
    for (ua, A), (ub, Bs) in zip(secs, secs[1:]):
        for j in range(k):
            q = [A[j], A[j + 1], Bs[j + 1], Bs[j]]
            c = sum(q, Vector()) / 4
            oface(bm, [tuple(p) for p in q], c - w.P((ua + ub) / 2, vm, zb))
    ud = Vector((1, 0, 0)) if w.axis == "x" else Vector((0, 1, 0))
    oface(bm, [tuple(p) for p in secs[0][1]], -ud)
    oface(bm, [tuple(p) for p in secs[-1][1]], ud)
    return bm


def fence_face(B, w, u0, u1, z0, hb, outer, rng, bw=0.28, light="SH_Honey", alt="SH_Oak", dark="SH_Walnut", thick=0.05, back=True):
    n = max(1, int(round((u1 - u0) / bw)))
    bw = (u1 - u0) / n
    if outer:
        vf, vb, want = w.T + 0.02, w.T + 0.02 - thick, -w.n
        vg = vf - 0.012
    else:
        vf, vb, want = -0.02, -0.02 + thick, w.n
        vg = vf + 0.012
    ch = 0.018
    ud = Vector((1, 0, 0)) if w.axis == "x" else Vector((0, 1, 0))
    i = 0
    while i < n:
        g = min(n - i, rng.choice((1, 2, 2, 3)))
        h = hb + rng.choice((0.0, 0.05, 0.1, -0.03, 0.07))
        ga, gb = u0 + i * bw, u0 + (i + g) * bw
        for j in range(g):
            a = ga + j * bw
            b = a + bw
            mat = light if (i + j) % 3 else alt
            w.face(B[mat], [(a, vf, z0), (b - ch, vf, z0), (b - ch, vf, h), (a, vf, h)], want)
            w.face(B[dark], [(b - ch, vf, z0), (b, vg, z0), (b, vg, h), (b - ch, vf, h)], want)
            w.face(B[mat], [(a, vg, h), (b, vg, h), (b, vb, h), (a, vb, h)], (0, 0, 1))
        if back:
            w.face(B[dark], [(ga, vb, z0), (gb, vb, z0), (gb, vb, h), (ga, vb, h)], -want)
        w.face(B[dark], [(ga, vg, z0), (ga, vb, z0), (ga, vb, h), (ga, vg, h)], -ud)
        w.face(B[dark], [(gb, vg, z0), (gb, vb, z0), (gb, vb, h), (gb, vg, h)], ud)
        i += g


def flag_stones(bm, x0, x1, y0, y1, ztop, rng, cell=0.95, gap=0.05):
    ny = max(1, int(round((y1 - y0) / cell)))
    ch = (y1 - y0) / ny
    for j in range(ny):
        nx = max(1, int(round((x1 - x0) / cell)))
        cw = (x1 - x0) / nx
        off = (cw * 0.5) if j % 2 else 0.0
        cuts = [x0] + [x0 + off + i * cw for i in range(nx + 1) if x0 + 0.25 < x0 + off + i * cw < x1 - 0.25] + [x1]
        for xa, xb in zip(cuts, cuts[1:]):
            w = (xb - xa) - gap - rng.uniform(0.0, 0.14)
            d = ch - gap - rng.uniform(0.0, 0.14)
            cx = (xa + xb) / 2 + rng.uniform(-0.015, 0.015)
            cy = y0 + (j + 0.5) * ch + rng.uniform(-0.015, 0.015)
            r = min(w, d) * rng.uniform(0.18, 0.32)
            m = Matrix.Translation((cx, cy, 0)) @ Matrix.Rotation(rng.uniform(-0.03, 0.03), 4, "Z")
            loft([(w, d, r, ztop - 0.008), (w - 0.03, d - 0.03, r - 0.015, ztop)], 1, cap0=False, bm=bm, matrix=m)
    return bm


def irr_stone(bm, cx, cy, w, d, ztop, rng, n=6, dz=0.008, ins=0.016):
    a0 = rng.uniform(0, 2 * math.pi)
    pts = []
    for k in range(n):
        a = a0 + 2 * math.pi * (k + rng.uniform(-0.22, 0.22)) / n
        s = rng.uniform(0.86, 1.0)
        pts.append((math.cos(a) * w / 2 * s, math.sin(a) * d / 2 * s))
    bot = [(cx + x, cy + y, ztop - dz) for x, y in pts]
    top = [(cx + x * (1 - 2 * ins / w), cy + y * (1 - 2 * ins / d), ztop) for x, y in pts]
    oface(bm, top, (0, 0, 1))
    for k in range(n):
        k1 = (k + 1) % n
        oface(bm, [bot[k], bot[k1], top[k1], top[k]], (top[k][0] - cx, top[k][1] - cy, 0.4))
    return bm


def flag_stones2(bm, x0, x1, y0, y1, ztop, rng, cell=1.0, gap=0.03):
    ny = max(1, int(round((y1 - y0) / cell)))
    ch = (y1 - y0) / ny
    for j in range(ny):
        nx = max(1, int(round((x1 - x0) / cell)))
        cw = (x1 - x0) / nx
        off = (cw * 0.5) if j % 2 else 0.0
        cuts = [x0] + [x0 + off + i * cw for i in range(nx + 1) if x0 + 0.3 < x0 + off + i * cw < x1 - 0.3] + [x1]
        for xa, xb in zip(cuts, cuts[1:]):
            irr_stone(bm, (xa + xb) / 2, y0 + (j + 0.5) * ch, (xb - xa) * 1.12 - gap, ch * 1.12 - gap, ztop, rng)
    return bm


def path_stones2(bm, poly, z, rng, step=0.72, w=0.58, d=0.48):
    for a, b in zip(poly, poly[1:]):
        a, b = Vector(a), Vector(b)
        L = (b - a).length
        n = max(1, int(L / step))
        t = (b - a).normalized()
        for i in range(n):
            p = a + (b - a) * (i + 0.5) / n + Vector((-t.y, t.x)) * (0.09 if i % 2 == 0 else -0.09)
            irr_stone(bm, p.x, p.y, z, rng=rng, w=w * rng.uniform(0.85, 1.1), d=d * rng.uniform(0.85, 1.1), ztop=z) if False else \
                irr_stone(bm, p.x, p.y, w * rng.uniform(0.85, 1.1), d * rng.uniform(0.85, 1.1), z, rng)
    return bm
