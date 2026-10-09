import bpy, bmesh, math, os, sys, random
import numpy as np
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FBX_OUT = os.path.join(ROOT, "Assets", "RunRunSimulator", "Resources", "Models", "Brawl", "BrawlScarecrow.fbx")
DRAGON_FBX = os.path.join(ROOT, "Assets", "Suriyun", "Dragons_SD", "FBX", "DragonSD_A.fbx")

PALETTE = {
    "SC_Burlap": "E2C391",
    "SC_Stitch": "3A2418",
    "SC_Straw": "F2CF63",
    "SC_Cloth": "7F8F45",
    "SC_Patch": "D69E3A",
    "SC_Wood": "8B5A36",
    "SC_Helmet": "F7F4EE",
    "SC_Cross": "3DBE5A",
    "SC_Cheek": "F4A3A8",
}

HEAD_C = 1.05
HEAD_RX = 0.335
HEAD_RZ = 0.30
HEAD_SY = 0.92
NECK_Z = 0.80
HEAD_TILT = 16.0
HELM_Z = 1.215
HELM_R = 0.318
HELM_H = 0.28
DROP = 0.035
ARM_Z = 0.66
BODY_SY = 0.84

UP = Vector((0, 0, 1))
MATS = {}
PARTS = []
HEAD_PARTS = []


def cli():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = a[0] if a else ""
    return out, set(a[1:])


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def make_materials():
    for name, hx in PALETTE.items():
        rgb = [srgb_to_linear(int(hx[i:i + 2], 16) / 255.0) for i in (0, 2, 4)]
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
        m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
        m.roughness = 0.85
        MATS[name] = m


def orient(face, direction):
    face.normal_update()
    if face.normal.dot(direction) < 0:
        face.normal_flip()


def finish(name, bm, mat, smooth=True, angle=40.0, head=False):
    for f in bm.faces:
        f.smooth = smooth
    if smooth and angle is not None:
        thr = math.radians(angle)
        for e in bm.edges:
            if e.is_manifold and e.calc_face_angle(0.0) > thr:
                e.smooth = False
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(MATS[mat])
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    (HEAD_PARTS if head else PARTS).append(ob)
    return ob


def lathe_bm(prof, segs, sy=1.0, tweak=None, bm=None, matrix=None):
    bm = bm or bmesh.new()
    rings = []
    for i, (r, z) in enumerate(prof):
        if r <= 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
            continue
        ring = []
        for k in range(segs):
            a = 2 * math.pi * k / segs
            x, y, zz = r * math.cos(a), r * math.sin(a) * sy, z
            if tweak:
                x, y, zz = tweak(i, a, x, y, zz)
            ring.append(bm.verts.new((x, y, zz)))
        rings.append(ring)
    new_verts = [v for ring in rings for v in ring]
    for A, B in zip(rings, rings[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for k in range(segs):
            k1 = (k + 1) % segs
            if len(A) == 1:
                bm.faces.new((A[0], B[k1], B[k]))
            elif len(B) == 1:
                bm.faces.new((A[k], A[k1], B[0]))
            else:
                bm.faces.new((A[k], A[k1], B[k1], B[k]))
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=new_verts)
    return bm


def ellipsoid_bm(center, radii, useg=20, vseg=10, bm=None, matrix=None):
    bm = bm or bmesh.new()
    before = set(bm.verts)
    res = bmesh.ops.create_uvsphere(bm, u_segments=useg, v_segments=vseg, radius=1.0)
    verts = [v for v in bm.verts if v not in before]
    for v in verts:
        v.co = Vector((v.co.x * radii[0], v.co.y * radii[1], v.co.z * radii[2])) + Vector(center)
    if matrix is not None:
        bmesh.ops.transform(bm, matrix=matrix, verts=verts)
    return bm


def tube_bm(points, radii, sides=8, bm=None, side_hint=None):
    bm = bm or bmesh.new()
    pts = [Vector(p) for p in points]
    n = len(pts)
    rings = []
    prev_side = None
    for i, (p, r) in enumerate(zip(pts, radii)):
        if i == 0:
            t = (pts[1] - p).normalized()
        elif i == n - 1:
            t = (p - pts[i - 1]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        if prev_side is None:
            h = Vector(side_hint) if side_hint is not None else (UP if abs(t.z) < 0.9 else Vector((1, 0, 0)))
            side = (h - t * h.dot(t)).normalized()
        else:
            side = (prev_side - t * prev_side.dot(t)).normalized()
        prev_side = side
        up = t.cross(side).normalized()
        rx, ry = (r, r) if not isinstance(r, (tuple, list)) else r
        ring = []
        for k in range(sides):
            a = 2 * math.pi * k / sides
            ring.append(bm.verts.new(p + side * math.cos(a) * rx + up * math.sin(a) * ry))
        rings.append(ring)
    faces = []
    for a, b in zip(rings, rings[1:]):
        for k in range(sides):
            faces.append(bm.faces.new((a[k], a[(k + 1) % sides], b[(k + 1) % sides], b[k])))
    faces.append(bm.faces.new(list(reversed(rings[0]))))
    faces.append(bm.faces.new(rings[-1]))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def torus_bm(R, r, z, sy=1.0, segs=32, sides=8, bm=None):
    bm = bm or bmesh.new()
    rings = []
    for k in range(segs):
        a = 2 * math.pi * k / segs
        c = Vector((R * math.cos(a), R * math.sin(a) * sy, z))
        out = Vector((math.cos(a) * sy, math.sin(a), 0)).normalized()
        ring = []
        for j in range(sides):
            b = 2 * math.pi * j / sides
            ring.append(bm.verts.new(c + out * math.cos(b) * r + UP * math.sin(b) * r))
        rings.append(ring)
    faces = []
    for k in range(segs):
        A, B = rings[k], rings[(k + 1) % segs]
        for j in range(sides):
            faces.append(bm.faces.new((A[j], A[(j + 1) % sides], B[(j + 1) % sides], B[j])))
    bmesh.ops.recalc_face_normals(bm, faces=faces)
    return bm


def frame(p, n, up=UP):
    z = Vector(n).normalized()
    x = up.cross(z)
    if x.length < 1e-4:
        x = Vector((1, 0, 0))
    x.normalize()
    y = z.cross(x).normalized()
    m = Matrix((x, y, z)).transposed().to_4x4()
    m.translation = Vector(p)
    return m


def bvh_of(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    return BVHTree.FromObject(ob, dg)


def ray(bvh, origin, direction, outward=None):
    loc, nor, idx, dist = bvh.ray_cast(Vector(origin), Vector(direction).normalized())
    if loc is None:
        return None, None
    if outward is not None and nor.dot(outward) < 0:
        nor = -nor
    return loc, nor.normalized()


def front_hit(bvh, x, z):
    return ray(bvh, (x, -3.0, z), (0, 1, 0), Vector((0, -1, 0)))


def decal_bm(us, vs, mask, proj, h_out, h_in, bm=None):
    bm = bm or bmesh.new()
    top, bot, nrm = {}, {}, {}

    def V(key):
        if key not in top:
            p, n = proj(us[key[0]], vs[key[1]])
            top[key] = bm.verts.new(p + n * h_out)
            bot[key] = bm.verts.new(p - n * h_in)
            nrm[key] = n
        return top[key], bot[key]

    cells = set()
    for i in range(len(us) - 1):
        for j in range(len(vs) - 1):
            if mask(0.5 * (us[i] + us[i + 1]), 0.5 * (vs[j] + vs[j + 1])):
                cells.add((i, j))
    for (i, j) in sorted(cells):
        corners = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
        tv = [V(c)[0] for c in corners]
        bv = [V(c)[1] for c in corners]
        n = sum((nrm[c] for c in corners), Vector()).normalized()
        orient(bm.faces.new(tv), n)
        orient(bm.faces.new(bv), -n)
        cc = sum((v.co for v in tv), Vector()) / 4
        for a, b, nb in (((i, j), (i + 1, j), (i, j - 1)), ((i + 1, j), (i + 1, j + 1), (i + 1, j)),
                         ((i + 1, j + 1), (i, j + 1), (i, j + 1)), ((i, j + 1), (i, j), (i - 1, j))):
            if nb not in cells:
                ta, ba = V(a)
                tb, bb = V(b)
                f = bm.faces.new((ta, tb, bb, ba))
                orient(f, (ta.co + tb.co) / 2 - cc)
    return bm


def lin(a, b, n):
    return [a + (b - a) * i / (n - 1) for i in range(n)]


def build_base():
    prof = [(0.0, 0.0), (0.30, 0.0), (0.305, 0.05), (0.282, 0.085), (0.0, 0.09)]
    finish("Base", lathe_bm(prof, 14), "SC_Wood", smooth=False)
    prof = [(0.0, 0.06), (0.085, 0.06), (0.078, 0.2), (0.072, 0.62), (0.0, 0.62)]
    finish("Post", lathe_bm(prof, 8), "SC_Wood", smooth=False)
    bm = tube_bm([(-0.56, 0, ARM_Z), (0.56, 0, ARM_Z)], [0.042, 0.042], 8)
    finish("Crossbar", bm, "SC_Wood", smooth=False)


def build_body():
    prof = [(0.0, 0.47), (0.15, 0.46), (0.235, 0.435), (0.285, 0.395), (0.29, 0.43), (0.275, 0.50),
            (0.255, 0.575), (0.245, 0.64), (0.232, 0.70), (0.20, 0.755), (0.145, 0.795), (0.08, 0.815),
            (0.0, 0.82)]
    teeth = 9
    amount = {2: 1.0, 3: 1.0, 4: 0.55}

    def tweak(i, a, x, y, z):
        if i in amount:
            ph = ((a + math.pi / 2) / (2 * math.pi) * teeth + 0.5) % 1.0
            tri = 1.0 - abs(2.0 * ph - 1.0)
            z -= 0.05 * tri * amount[i]
        return x, y, z

    body = finish("Shirt", lathe_bm(prof, 36, sy=BODY_SY, tweak=tweak), "SC_Cloth", angle=55)
    bm = bmesh.new()
    for s in (1, -1):
        xs = [0.08, 0.18, 0.28, 0.36, 0.415, 0.445, 0.452]
        rs = [0.105, 0.100, 0.092, 0.090, 0.100, 0.116, 0.085]
        pts = [(s * x, 0, ARM_Z + 0.008) for x in xs]
        tube_bm(pts, rs, 12, bm=bm)
    finish("Sleeves", bm, "SC_Cloth", angle=60)
    return body


def build_patches(body):
    bvh = bvh_of(body)
    bm = bmesh.new()
    sbm = bmesh.new()
    for cx, cz, hw, hh, rot, side in ((-0.085, 0.53, 0.068, 0.058, 0.14, -1), (0.115, 0.675, 0.05, 0.044, -0.2, -1),
                                      (-0.07, 0.6, 0.06, 0.052, -0.12, 1)):
        c, s = math.cos(rot), math.sin(rot)

        def proj(u, v, cx=cx, cz=cz, c=c, s=s, side=side):
            return ray(bvh, (cx + u * c - v * s, side * 3.0, cz + u * s + v * c), (0, -side, 0), Vector((0, side, 0)))

        decal_bm(lin(-hw, hw, 4), lin(-hh, hh, 4), lambda u, v: True, proj, 0.009, 0.012, bm=bm)
        for side in range(4):
            for t in (-0.5, 0.0, 0.5):
                if side < 2:
                    u, v = t * hw * 1.4, (hh if side == 0 else -hh)
                    du, dv = 0.0, 1.0
                else:
                    u, v = (hw if side == 2 else -hw), t * hh * 1.4
                    du, dv = 1.0, 0.0
                pts = []
                for k in (-1, 0, 1):
                    p, n = proj(u + du * k * 0.018, v + dv * k * 0.018)
                    pts.append(p + n * 0.012)
                tube_bm(pts, [0.006, 0.008, 0.006], 5, bm=sbm)
    finish("Patches", bm, "SC_Patch", angle=35)
    finish("PatchStitches", sbm, "SC_Stitch", angle=70)


def strand(bm, base, direction, length, r0, droop=0.0, sides=5):
    d = Vector(direction).normalized()
    b = Vector(base)
    p1 = b + d * length * 0.35
    p2 = b + d * length * 0.70 - UP * droop * 0.35
    p3 = b + d * length - UP * droop
    tube_bm([b, p1, p2, p3], [r0, r0 * 0.85, r0 * 0.6, r0 * 0.2], sides, bm=bm)


def build_straw():
    rng = random.Random(11)
    bm = bmesh.new()
    for s in (1, -1):
        base = Vector((s * 0.40, 0, ARM_Z + 0.005))
        strand(bm, base, (s, 0, 0.05), 0.24, 0.042, 0.01)
        n = 10
        for k in range(n):
            phi = 2 * math.pi * k / n + rng.uniform(-0.2, 0.2)
            th = math.radians(rng.uniform(26, 44))
            d = Vector((s * math.cos(th), math.sin(th) * math.cos(phi), math.sin(th) * math.sin(phi)))
            strand(bm, base, d, rng.uniform(0.18, 0.23), 0.04, rng.uniform(0.0, 0.03))
    n = 11
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n + rng.uniform(-0.12, 0.12)
        rad = Vector((math.cos(a), math.sin(a) * BODY_SY, 0))
        base = Vector((0, 0, 0.47)) + rad * 0.17
        d = rad * 0.55 - UP * 0.85
        strand(bm, base, d, rng.uniform(0.15, 0.19), 0.032, 0.0)
    n = 12
    for k in range(n):
        a = 2 * math.pi * (k + 0.25) / n + rng.uniform(-0.1, 0.1)
        rad = Vector((math.cos(a), math.sin(a) * HEAD_SY, 0))
        front = max(0.0, -math.sin(a))
        base = Vector((0, 0, NECK_Z - 0.005)) + rad * 0.07
        d = rad * 0.9 - UP * 0.3
        strand(bm, base, d, rng.uniform(0.19, 0.23) - 0.05 * front, 0.034, 0.015)
    finish("Straw", bm, "SC_Straw", angle=70)


def build_head():
    prof = [(0.0, 0.77), (0.085, 0.775), (0.108, 0.795), (0.125, 0.815)]
    for deg in range(-48, 91, 9):
        t = math.radians(deg)
        prof.append((max(0.0, HEAD_RX * math.cos(t)), HEAD_C + HEAD_RZ * math.sin(t)))
    if prof[-1][0] > 1e-6:
        prof.append((0.0, HEAD_C + HEAD_RZ))
    folds = {1: 0.05, 2: 0.08, 3: 0.08, 4: 0.07, 5: 0.035}

    def tweak(i, a, x, y, z):
        if i in folds:
            f = 1.0 + folds[i] * math.cos(10 * a)
            return x * f, y * f, z
        return x, y, z

    head = finish("Head", lathe_bm(prof, 40, sy=HEAD_SY, tweak=tweak), "SC_Burlap", angle=60, head=True)
    finish("Rope", torus_bm(0.118, 0.032, NECK_Z + 0.005, HEAD_SY, 32, 8), "SC_Wood", angle=70, head=True)
    return head


def build_face(head):
    bvh = bvh_of(head)
    dark = bmesh.new()
    white = bmesh.new()
    cheek = bmesh.new()
    eye_prof = [(0.0, -0.014), (0.058, -0.014), (0.064, 0.0), (0.06, 0.012), (0.048, 0.019), (0.0, 0.021)]
    for s in (1, -1):
        p, n = front_hit(bvh, s * 0.138, 1.105)
        m = frame(p, n)
        lathe_bm(eye_prof, 18, bm=dark, matrix=m)
        ellipsoid_bm((-0.022, 0.024, 0.019), (0.018, 0.018, 0.008), 10, 6, bm=white, matrix=m)
        p, n = front_hit(bvh, s * 0.228, 1.02)
        ellipsoid_bm((0, 0, 0.0), (0.052, 0.036, 0.013), 16, 8, bm=cheek, matrix=frame(p, n))
    pts, nrms = [], []
    for k in range(15):
        x = -0.145 + 0.29 * k / 14
        z = 0.958 + 0.066 * (x / 0.145) ** 2
        p, n = front_hit(bvh, x, z)
        pts.append(p + n * 0.006)
        nrms.append(n)
    tube_bm(pts, [0.016] + [0.02] * 13 + [0.016], 8, bm=dark)
    for k in (2, 5, 7, 9, 12):
        t = (pts[k + 1] - pts[k - 1]).normalized()
        n = nrms[k]
        d = n.cross(t).normalized()
        p = pts[k]
        tube_bm([p - d * 0.036, p, p + d * 0.036], [0.01, 0.013, 0.01], 6, bm=dark)
    pts = []
    for k in range(10):
        z = 0.89 + (HELM_Z - 0.02 - 0.89) * k / 9
        p, n = ray(bvh, (0, 3.0, z), (0, -1, 0), Vector((0, 1, 0)))
        pts.append((p + n * 0.004, n))
    tube_bm([p for p, n in pts], [0.008] + [0.012] * 8 + [0.008], 6, bm=dark)
    for k in (1, 3, 5, 7):
        p, n = pts[k]
        tube_bm([p + Vector((-0.03, 0, 0)), p + n * 0.002, p + Vector((0.03, 0, 0))], [0.008, 0.01, 0.008], 6, bm=dark)
    finish("FaceStitch", dark, "SC_Stitch", angle=50, head=True)
    finish("EyeShine", white, "SC_Helmet", angle=80, head=True)
    finish("Cheeks", cheek, "SC_Cheek", angle=80, head=True)


def build_helmet():
    prof = [(0.0, HELM_Z - 0.04), (HELM_R - 0.04, HELM_Z - 0.04)]
    for deg in range(0, 91, 9):
        t = math.radians(deg)
        prof.append((max(0.0, HELM_R * math.cos(t)), HELM_Z + HELM_H * math.sin(t)))
    if prof[-1][0] > 1e-6:
        prof.append((0.0, HELM_Z + HELM_H))
    dome = finish("Helmet", lathe_bm(prof, 40, sy=HEAD_SY), "SC_Helmet", angle=60, head=True)
    bm = torus_bm(HELM_R + 0.004, 0.028, HELM_Z + 0.004, HEAD_SY, 40, 8)
    finish("HelmetRim", bm, "SC_Helmet", angle=60, head=True)
    bvh = bvh_of(dome)
    centre = Vector((0, 0, HELM_Z - 0.02))
    bm = bmesh.new()
    for az, tdeg, L, W in ((-90, 31, 0.122, 0.049), (0, 47, 0.08, 0.033), (180, 36, 0.1, 0.04), (90, 47, 0.08, 0.033)):
        a = math.radians(az)
        t = math.radians(tdeg)
        target = Vector((HELM_R * math.cos(t) * math.cos(a), HELM_R * math.cos(t) * math.sin(a) * HEAD_SY,
                         HELM_Z + HELM_H * math.sin(t)))
        p0, n0 = ray(bvh, centre, target - centre, target - centre)
        m = frame(p0, n0)
        t1 = m.col[0].xyz
        t2 = m.col[1].xyz

        def proj(u, v, p0=p0, t1=t1, t2=t2):
            q = p0 + t1 * u + t2 * v
            return ray(bvh, centre, q - centre, q - centre)

        cs = [-L, -(L + W) / 2, -W, 0.0, W, (L + W) / 2, L]
        decal_bm(cs, cs, lambda u, v, W=W: abs(u) < W or abs(v) < W, proj, 0.012, 0.012, bm=bm)
    finish("Cross", bm, "SC_Cross", angle=35, head=True)


def tilt_head():
    piv = Vector((0, 0, NECK_Z))
    m = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-HEAD_TILT), 4, "X") @ Matrix.Translation(-piv)
    for ob in HEAD_PARTS:
        ob.data.transform(m)
        ob.data.update()


def join_all():
    objs = PARTS + HEAD_PARTS
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "Scarecrow"
    ob.data.name = "Scarecrow"
    return ob


def export(ob):
    os.makedirs(os.path.dirname(FBX_OUT), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=FBX_OUT, use_selection=True, object_types={"MESH"},
                             apply_scale_options="FBX_SCALE_ALL", axis_forward="-Z", axis_up="Y",
                             apply_unit_scale=True, use_mesh_modifiers=True, bake_space_transform=True,
                             mesh_smooth_type="FACE", add_leaf_bones=False, bake_anim=False)


def setup_scene():
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
    sc.render.film_transparent = False
    sc.world = sc.world or bpy.data.worlds.new("World")
    sc.world.color = (0.42, 0.45, 0.48)
    fl = bpy.data.materials.new("Floor")
    fl.diffuse_color = (0.33, 0.36, 0.38, 1)
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.data.materials.append(fl)


def render(path, az, el, target, ortho, res):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cd.type = "ORTHO"
    cd.ortho_scale = ortho
    cd.clip_end = 100
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    a, e = math.radians(az), math.radians(el)
    t = Vector(target)
    cam.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * 10
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.filepath = path
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


def load_dragon(x_offset):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=DRAGON_FBX)
    new = [o for o in bpy.data.objects if o not in before]
    body = bpy.data.materials.new("DragonRef")
    body.diffuse_color = (0.80, 0.78, 0.86, 1)
    for o in new:
        if o.parent is None:
            o.location.x += x_offset
        if o.type == "MESH":
            if o.name == "Face":
                o.hide_render = True
            o.data.materials.clear()
            o.data.materials.append(body)
    bpy.context.view_layer.update()
    zs = [(o.matrix_world @ Vector(c)).z for o in new if o.type == "MESH" and not o.hide_render for c in o.bound_box]
    print("DRAGON_HEIGHT", round(max(zs) - min(zs), 3), "min", round(min(zs), 3))


def read_png(path):
    img = bpy.data.images.load(path, check_existing=False)
    w, h = img.size
    arr = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(arr)
    bpy.data.images.remove(img)
    return arr.reshape(h, w, 4)


def paste(canvas, img, left, top):
    H = canvas.shape[0]
    h, w = img.shape[:2]
    canvas[H - top - h:H - top, left:left + w] = img


def contact_sheet(out_dir, cells, game_imgs, path):
    cell = 600
    pad = 8
    W = 3 * cell + 4 * pad
    H = 2 * cell + 3 * pad
    canvas = np.ones((H, W, 4), dtype=np.float32)
    canvas[..., :3] = 0.16
    for idx, name in enumerate(cells):
        r, c = divmod(idx, 3)
        paste(canvas, read_png(os.path.join(out_dir, name)), pad + c * (cell + pad), pad + r * (cell + pad))
    left = pad + 2 * (cell + pad)
    top = pad + (cell + pad)
    g1 = read_png(os.path.join(out_dir, game_imgs[0]))
    g2 = read_png(os.path.join(out_dir, game_imgs[1]))
    canvas[H - top - cell:H - top, left:left + cell, :3] = 0.42
    paste(canvas, g1, left + 10, top + 10)
    paste(canvas, g2, left + 30 + g1.shape[1], top + 10)
    big = np.repeat(np.repeat(g1, 3, axis=0), 3, axis=1)
    paste(canvas, big, left + (cell - big.shape[1]) // 2, top + cell - big.shape[0] - 6)
    img = bpy.data.images.new("sheet", W, H, alpha=True)
    img.pixels.foreach_set(canvas.ravel())
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()


def main():
    out_dir, flags = cli()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    make_materials()
    build_base()
    body = build_body()
    build_patches(body)
    build_straw()
    head = build_head()
    build_face(head)
    build_helmet()
    tilt_head()
    drop = Matrix.Translation((0, 0, -DROP))
    for o in PARTS + HEAD_PARTS:
        if o.name not in ("Base", "Post"):
            o.data.transform(drop)
    ob = join_all()
    bpy.context.view_layer.update()
    xs = [v.co.x for v in ob.data.vertices]
    ys = [v.co.y for v in ob.data.vertices]
    zs = [v.co.z for v in ob.data.vertices]
    print("SCARECROW verts=%d faces=%d" % (len(ob.data.vertices), len(ob.data.polygons)))
    print("SCARECROW size x=%.3f y=%.3f z=%.3f zmin=%.3f" % (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs), min(zs)))
    print("SCARECROW mats", [m.name for m in ob.data.materials])
    if "noexport" not in flags:
        export(ob)
        print("EXPORTED", FBX_OUT)
    if not out_dir:
        return
    os.makedirs(out_dir, exist_ok=True)
    setup_scene()
    tz = 0.72
    render(os.path.join(out_dir, "v_front.png"), 0, 4, (0, 0, tz), 1.75, (600, 600))
    render(os.path.join(out_dir, "v_34.png"), 35, 14, (0, 0, tz), 1.75, (600, 600))
    render(os.path.join(out_dir, "v_side.png"), 90, 4, (0, 0, tz), 1.75, (600, 600))
    render(os.path.join(out_dir, "v_iso.png"), 20, 57, (0, 0, tz), 1.75, (600, 600))
    render(os.path.join(out_dir, "x_back.png"), 200, 25, (0, 0, tz), 1.75, (400, 400))
    render(os.path.join(out_dir, "x_iso_side.png"), 100, 57, (0, 0, tz), 1.75, (400, 400))
    render(os.path.join(out_dir, "g_120.png"), 20, 57, (0, 0, 0.62), 1.55, (140, 140))
    render(os.path.join(out_dir, "g_75.png"), 20, 57, (0, 0, 0.62), 1.55, (88, 88))
    load_dragon(1.25)
    render(os.path.join(out_dir, "v_dragon.png"), 18, 12, (0.62, 0, 0.68), 2.6, (600, 600))
    contact_sheet(out_dir, ["v_front.png", "v_34.png", "v_side.png", "v_iso.png", "v_dragon.png"],
                  ["g_120.png", "g_75.png"], os.path.join(out_dir, "scarecrow_sheet.png"))
    print("SHEET", os.path.join(out_dir, "scarecrow_sheet.png"))


main()
