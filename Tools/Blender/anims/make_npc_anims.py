import bpy
import math
import os
import sys
from mathutils import Matrix, Quaternion, Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
GENDER = ARGS[0] if ARGS else "Masc"
OUT_DIR = ARGS[1] if len(ARGS) > 1 else os.path.dirname(os.path.abspath(__file__))
ONLY = ARGS[2].split(",") if len(ARGS) > 2 and ARGS[2] else None

SYNTY = "E:/GitHub/RunRunSimulator/Assets/Synty"
FOLDER = "Masculine" if GENDER == "Masc" else "Feminine"
IDLE = f"{SYNTY}/AnimationIdles/Animations/Sidekick/{FOLDER}/Base/Stances/A_MOD_IDL_Base_{GENDER}.fbx"
FPS = 30
FINGERS = ["index", "middle", "ring", "pinky"]


def smooth(a, b, x):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def bump(t, a, b):
    if t <= a or t >= b:
        return 0.0
    return math.sin(math.pi * (t - a) / (b - a))


def lerp(a, b, w):
    return a + (b - a) * w


def side_vec(v, side):
    return Vector((v[0] if side == "l" else -v[0], v[1], v[2]))


bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=IDLE, automatic_bone_orientation=False)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "Armature"
idle = arm.animation_data.action
I0, I1 = int(idle.frame_range[0]), int(idle.frame_range[1])
ILEN = I1 - I0
scene = bpy.context.scene
scene.render.fps = FPS

bones = sorted(arm.data.bones, key=lambda b: len(b.parent_recursive))
NAMES = [b.name for b in bones]
PARENT = {b.name: (b.parent.name if b.parent else None) for b in bones}
REST = {b.name: b.matrix_local.copy() for b in bones}
REL = {n: (REST[PARENT[n]].inverted() @ REST[n]) if PARENT[n] else REST[n] for n in NAMES}
AW = arm.matrix_world.copy()
AWI = AW.inverted()
AQ = AW.to_quaternion()
AQI = AQ.inverted()


def sample_idle(f):
    arm.animation_data.action = idle
    fi = int(math.floor(f))
    scene.frame_set(fi, subframe=f - fi)
    return {n: arm.pose.bones[n].matrix_basis.copy() for n in NAMES}


def fk(basis):
    P = {}
    for n in NAMES:
        p = PARENT[n]
        P[n] = (P[p] @ REL[n] @ basis[n]) if p else (REL[n] @ basis[n])
    return P


def set_pose_matrix(basis, P, n, M):
    p = PARENT[n]
    basis[n] = ((P[p] @ REL[n]).inverted() @ M) if p else (REL[n].inverted() @ M)


def world_pos(P, n):
    return AW @ P[n].translation


def rotate_world(basis, n, axis, deg):
    if abs(deg) < 1e-6:
        return
    P = fk(basis)
    qa = AQI @ Quaternion(Vector(axis).normalized(), math.radians(deg)) @ AQ
    M = P[n]
    head = M.translation.copy()
    R = qa.to_matrix().to_4x4()
    M2 = Matrix.Translation(head) @ R @ Matrix.Translation(-head) @ M
    set_pose_matrix(basis, P, n, M2)


def translate_world(basis, n, d):
    P = fk(basis)
    M = P[n].copy()
    M.translation = M.translation + (AWI.to_3x3() @ Vector(d))
    set_pose_matrix(basis, P, n, M)


CHAINS = {"hand_l": ("upperarm_l", "lowerarm_l", "hand_l"), "hand_r": ("upperarm_r", "lowerarm_r", "hand_r"),
          "foot_l": ("thigh_l", "calf_l", "foot_l"), "foot_r": ("thigh_r", "calf_r", "foot_r")}
POLES = {"hand_l": Vector((0.7, 0.45, -0.55)), "hand_r": Vector((-0.7, 0.45, -0.55)),
         "foot_l": Vector((0.1, -1.0, 0.15)), "foot_r": Vector((-0.1, -1.0, 0.15))}


def rotate_world_q(basis, n, q):
    P = fk(basis)
    qa = AQI @ q @ AQ
    M = P[n]
    head = M.translation.copy()
    M2 = Matrix.Translation(head) @ qa.to_matrix().to_4x4() @ Matrix.Translation(-head) @ M
    set_pose_matrix(basis, P, n, M2)


def two_bone(basis, key, target, pole_hint):
    up, lo, end = CHAINS[key]
    P = fk(basis)
    S, E, Wp = world_pos(P, up), world_pos(P, lo), world_pos(P, end)
    a, b = (E - S).length, (Wp - E).length
    T = Vector(target)
    d_vec = T - S
    d = min(max(d_vec.length, abs(a - b) + 1e-4), a + b - 1e-4)
    u = d_vec.normalized()
    cur = (E - S) - u * (E - S).dot(u)
    cur = cur.normalized() if cur.length > 1e-5 else pole_hint.normalized()
    w = min(1.0, (T - Wp).length / 0.12)
    hint = pole_hint - u * pole_hint.dot(u)
    hint = hint.normalized() if hint.length > 1e-5 else cur
    v = (cur * (1 - w) + hint * w)
    v = (v - u * v.dot(u)).normalized()
    cos_a = (a * a + d * d - b * b) / (2 * a * d)
    sin_a = math.sqrt(max(0.0, 1 - cos_a * cos_a))
    E2 = S + (u * cos_a + v * sin_a) * a
    rotate_world_q(basis, up, (E - S).rotation_difference(E2 - S))
    P = fk(basis)
    E1, W1 = world_pos(P, lo), world_pos(P, end)
    T2 = S + u * d
    rotate_world_q(basis, lo, (W1 - E1).rotation_difference(T2 - E1))


def solve_ik(basis, targets):
    for key in ("foot_l", "foot_r", "hand_l", "hand_r"):
        if targets.get(key) is not None:
            two_bone(basis, key, targets[key], POLES[key])
    return basis


def hand_frame(P, side):
    h = world_pos(P, "hand_" + side)
    m = world_pos(P, "middle_01_" + side)
    f = (m - h).normalized()
    Mw = AW @ P["hand_" + side]
    n = (Mw.to_3x3().normalized() @ Vector((0, 1, 0))).normalized()
    n = (n - f * n.dot(f)).normalized()
    return f, n


def hand_adjust(basis, side, sup, flex):
    if abs(sup) < 1e-6 and abs(flex) < 1e-6:
        return
    P = fk(basis)
    f, n = hand_frame(P, side)
    axis_sup = f if side == "r" else -f
    if abs(sup) > 1e-6:
        rotate_world(basis, "hand_" + side, axis_sup, sup)
        P = fk(basis)
        f, n = hand_frame(P, side)
    if abs(flex) > 1e-6:
        rotate_world(basis, "hand_" + side, f.cross(n), flex)


def curl_fingers(basis, side, amount):
    if amount <= 1e-6:
        return
    for fn in FINGERS:
        for i, k in ((1, 0.8), (2, 1.0), (3, 0.7)):
            n = f"{fn}_0{i}_{side}"
            basis[n] = basis[n] @ Quaternion((0, 0, 1), math.radians(70 * amount * k)).to_matrix().to_4x4()
    for i, k in ((2, 0.6), (3, 0.6)):
        n = f"thumb_0{i}_{side}"
        basis[n] = basis[n] @ Quaternion((0, 1, 0), math.radians(45 * amount * k)).to_matrix().to_4x4()


X = (1, 0, 0)
Y = (0, 1, 0)
Z = (0, 0, 1)

COUNTER = Vector((0.11, -0.40, 1.00))
CARRY = Vector((0.12, -0.21, 1.05))
FLOOR = Vector((0.12, -0.34, 0.22))
THIGH = Vector((0.15, -0.03, 0.55))
PAY = Vector((-0.05, -0.40, 1.02))
CARRY_CURL = 0.55
CARRY_SUP = 35.0
CARRY_HEAD = 8.0
SIT_PELVIS = Vector((0.0, 0.22, -0.43))
SIT_TILT = -8.0
SIT_LEAN = 14.0
SIT_SUP = -75.0


def spine_lean(deg):
    return [("spine_01", X, deg * 0.35), ("spine_02", X, deg * 0.35), ("spine_03", X, deg * 0.30)]


def clip_receive(t, ctx):
    wr = smooth(0.05, 0.42, t)
    wl = smooth(0.55, 0.95, t)
    lean = 14 * wr * (1 - wl)
    head = 12 * wr * (1 - wl) + CARRY_HEAD * wl
    hands = {}
    for s in "lr":
        a = lerp(ctx["wrist_" + s], side_vec(COUNTER, s), wr)
        a = a + Vector((0, 0, 0.04)) * bump(t, 0.5, 0.8)
        hands["hand_" + s] = lerp(a, side_vec(CARRY, s), wl)
    curl = 0.15 + (CARRY_CURL - 0.15) * smooth(0.32, 0.52, t)
    return dict(rots=spine_lean(lean) + [("neck_01", X, head * 0.4), ("head", X, head * 0.6)],
                hands=hands, curl=(curl, curl), sup=(CARRY_SUP * wl, CARRY_SUP * wl))


def clip_carry(t, ctx):
    rock = math.sin(2 * math.pi * t)
    bob = math.sin(4 * math.pi * t)
    hands = {}
    for s in "lr":
        hands["hand_" + s] = side_vec(CARRY, s) + Vector((0.012 * rock, 0, 0.005 * bob))
    return dict(rots=[("neck_01", X, CARRY_HEAD * 0.4), ("head", X, CARRY_HEAD * 0.6), ("head", Z, 3 * rock)],
                hands=hands, curl=(CARRY_CURL, CARRY_CURL), sup=(CARRY_SUP, CARRY_SUP))


def clip_handover(t, ctx):
    w1 = smooth(0.0, 0.42, t)
    w2 = smooth(0.58, 0.97, t)
    lean = 14 * w1 * (1 - w2)
    head = (CARRY_HEAD + 6 * w1) * (1 - w2)
    hands = {}
    for s in "lr":
        a = lerp(side_vec(CARRY, s), side_vec(COUNTER, s), w1)
        hands["hand_" + s] = lerp(a, ctx["wrist_" + s], w2)
    curl = CARRY_CURL - (CARRY_CURL - 0.12) * smooth(0.40, 0.58, t)
    curl = curl * (1 - w2) + 0.0 * w2
    sup = CARRY_SUP * (1 - w1)
    return dict(rots=spine_lean(lean) + [("neck_01", X, head * 0.4), ("head", X, head * 0.6)],
                hands=hands, curl=(curl, curl), sup=(sup, sup))


def clip_pay(t, ctx):
    w = smooth(0.05, 0.40, t) * (1 - smooth(0.62, 0.97, t))
    hands = {"hand_r": lerp(ctx["wrist_r"], PAY, w)}
    return dict(rots=spine_lean(6 * w) + [("neck_01", X, 4 * w), ("head", X, 6 * w)],
                hands=hands, curl=(0.0, 0.3 * w), sup=(0.0, 75 * w), flex=(0.0, -10 * w))


def sit_state(w, lean_extra):
    return dict(pelvis=SIT_PELVIS * w,
                rots=[("pelvis", X, SIT_TILT * w)] + spine_lean(SIT_LEAN * w + lean_extra))


def clip_sit_enter(t, ctx):
    w = smooth(0.06, 0.88, t)
    lean = 22 * bump(w, 0.0, 1.0)
    d = sit_state(w, lean)
    wh = smooth(0.35, 0.95, t)
    d["hands"] = {"hand_" + s: lerp(ctx["wrist_" + s], side_vec(THIGH, s), wh) for s in "lr"}
    d["feet"] = True
    d["sup"] = (SIT_SUP * wh, SIT_SUP * wh)
    d["curl"] = (0.25 * wh, 0.25 * wh)
    return d


def clip_sit_loop(t, ctx):
    sway = math.sin(2 * math.pi * t)
    d = sit_state(1.0, 0.0)
    d["rots"] += [("head", Z, 2.5 * sway), ("spine_03", Y, 1.0 * sway)]
    d["hands"] = {"hand_" + s: side_vec(THIGH, s) for s in "lr"}
    d["feet"] = True
    d["sup"] = (SIT_SUP, SIT_SUP)
    d["curl"] = (0.25, 0.25)
    return d


def clip_sit_exit(t, ctx):
    w = 1 - smooth(0.12, 0.92, t)
    lean = 30 * bump(1 - w, 0.0, 1.0)
    d = sit_state(w, lean)
    wh = 1 - smooth(0.05, 0.6, t)
    d["hands"] = {"hand_" + s: lerp(ctx["wrist_" + s], side_vec(THIGH, s), wh) for s in "lr"}
    d["feet"] = True
    d["sup"] = (SIT_SUP * wh, SIT_SUP * wh)
    d["curl"] = (0.25 * wh, 0.25 * wh)
    return d


def clip_pickup_floor(t, ctx):
    down = smooth(0.0, 0.40, t) * (1 - smooth(0.52, 0.95, t))
    wr = smooth(0.08, 0.40, t)
    wl = smooth(0.52, 0.95, t)
    lean = 55 * down
    head = -18 * down + CARRY_HEAD * wl
    hands = {}
    for s in "lr":
        a = lerp(ctx["wrist_" + s], side_vec(FLOOR, s), wr)
        hands["hand_" + s] = lerp(a, side_vec(CARRY, s), wl)
    curl = 0.15 + (CARRY_CURL - 0.15) * smooth(0.36, 0.50, t)
    return dict(pelvis=Vector((0, 0.14, -0.48)) * down,
                rots=spine_lean(lean) + [("neck_01", X, head * 0.4), ("head", X, head * 0.6)],
                hands=hands, feet=True, curl=(curl, curl), sup=(CARRY_SUP * wl, CARRY_SUP * wl))


CLIPS = [
    ("A_MM_Receive", 36, False, clip_receive),
    ("A_MM_Carry_Loop", 60, True, clip_carry),
    ("A_MM_HandOver", 36, False, clip_handover),
    ("A_MM_Pay", 30, False, clip_pay),
    ("A_MM_PickUp_Floor", 48, False, clip_pickup_floor),
    ("A_MM_Sit_Enter", 36, False, clip_sit_enter),
    ("A_MM_Sit_Loop", 60, True, clip_sit_loop),
    ("A_MM_Sit_Exit", 36, False, clip_sit_exit),
]


def build_clip(name, nframes, loop, fn):
    full = f"{name}_{GENDER}"
    act = bpy.data.actions.new(full)
    frames = []
    for i in range(nframes + 1):
        t = i / nframes
        src = I0 + (t * ILEN if loop else (i % ILEN))
        base = sample_idle(src)
        P0 = fk(base)
        ctx = {"wrist_l": world_pos(P0, "hand_l"), "wrist_r": world_pos(P0, "hand_r")}
        d = fn(t, ctx)
        basis = dict(base)
        if d.get("pelvis") is not None and Vector(d["pelvis"]).length > 1e-6:
            translate_world(basis, "pelvis", d["pelvis"])
        for bn, ax, deg in d.get("rots", []):
            rotate_world(basis, bn, ax, deg)
        P1 = fk(basis)
        d = fn(t, {"wrist_l": world_pos(P1, "hand_l"), "wrist_r": world_pos(P1, "hand_r")})
        targets = dict(d.get("hands", {}))
        if d.get("feet"):
            targets["foot_l"] = world_pos(P0, "foot_l")
            targets["foot_r"] = world_pos(P0, "foot_r")
        if targets:
            basis = solve_ik(basis, targets)
        if d.get("feet"):
            for s in "lr":
                P = fk(basis)
                M = P0["foot_" + s].copy()
                M.translation = P["foot_" + s].translation
                set_pose_matrix(basis, P, "foot_" + s, M)
        sup = d.get("sup", (0, 0))
        flex = d.get("flex", (0, 0))
        curl = d.get("curl", (0, 0))
        for k, s in enumerate("lr"):
            hand_adjust(basis, s, sup[k], flex[k])
            curl_fingers(basis, s, curl[k])
        frames.append(basis)
    arm.animation_data.action = act
    prev = {}
    for i, basis in enumerate(frames):
        f = i + 1
        for n in NAMES:
            pb = arm.pose.bones[n]
            loc, rot, scl = basis[n].decompose()
            if n in prev and prev[n].dot(rot) < 0:
                rot = -rot
            prev[n] = rot
            pb.location = loc
            pb.rotation_quaternion = rot
            pb.scale = scl
            pb.keyframe_insert("location", frame=f, group=n)
            pb.keyframe_insert("rotation_quaternion", frame=f, group=n)
            pb.keyframe_insert("scale", frame=f, group=n)
    return act, nframes + 1


def export_clip(act, last, full):
    arm.animation_data.action = act
    scene.frame_start = 1
    scene.frame_end = last
    scene.name = full
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    path = os.path.join(OUT_DIR, full + ".fbx")
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'ARMATURE'},
                             add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False,
                             bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                             bake_anim_simplify_factor=0.0, apply_unit_scale=True, global_scale=1.0,
                             axis_forward='-Z', axis_up='Y', primary_bone_axis='Y', secondary_bone_axis='X',
                             armature_nodetype='NULL', use_armature_deform_only=False)
    print("EXPORTED", path, "frames", last)


for name, nframes, loop, fn in CLIPS:
    if ONLY and name not in ONLY:
        continue
    act, last = build_clip(name, nframes, loop, fn)
    export_clip(act, last, f"{name}_{GENDER}")

arm.animation_data.action = idle
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, f"A_MM_NpcAnims_{GENDER}.blend"))
