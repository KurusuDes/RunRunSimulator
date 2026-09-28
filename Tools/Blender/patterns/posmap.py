import os
import sys
import bpy
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), "parts"))
import part_common as pc

ARGS = pc.args()
OUT = ARGS[0]
RES = int(ARGS[1]) if len(ARGS) > 1 else 2048
MARGIN = 6


def raster(body):
    dg = bpy.context.evaluated_depsgraph_get()
    ev = body.evaluated_get(dg)
    me = ev.to_mesh()
    me.calc_loop_triangles()
    mw = body.matrix_world
    nm = mw.to_3x3().inverted().transposed()
    uv = me.uv_layers.active.data
    pos = np.full((RES, RES, 3), np.nan, dtype=np.float32)
    nor = np.zeros((RES, RES, 3), dtype=np.float32)
    vco = np.array([tuple(mw @ v.co) for v in me.vertices], dtype=np.float64)
    vno = np.array([tuple((nm @ v.normal).normalized()) for v in me.vertices], dtype=np.float64)
    for tri in me.loop_triangles:
        uvs = np.array([tuple(uv[l].uv) for l in tri.loops], dtype=np.float64)
        px = uvs[:, 0] * RES - 0.5
        py = (1 - uvs[:, 1]) * RES - 0.5
        x0, x1 = int(max(0, np.floor(px.min()))), int(min(RES - 1, np.ceil(px.max())))
        y0, y1 = int(max(0, np.floor(py.min()))), int(min(RES - 1, np.ceil(py.max())))
        if x1 < x0 or y1 < y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1), np.arange(y0, y1 + 1))
        d = (py[1] - py[2]) * (px[0] - px[2]) + (px[2] - px[1]) * (py[0] - py[2])
        if abs(d) < 1e-12:
            continue
        a = ((py[1] - py[2]) * (gx - px[2]) + (px[2] - px[1]) * (gy - py[2])) / d
        b = ((py[2] - py[0]) * (gx - px[2]) + (px[0] - px[2]) * (gy - py[2])) / d
        c = 1 - a - b
        inside = (a >= -1e-4) & (b >= -1e-4) & (c >= -1e-4)
        if not inside.any():
            continue
        vi = list(tri.vertices)
        w = np.stack([a[inside], b[inside], c[inside]], axis=1)
        p = w @ vco[vi]
        n = w @ vno[vi]
        n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-9
        pos[gy[inside], gx[inside]] = p
        nor[gy[inside], gx[inside]] = n
    ev.to_mesh_clear()
    return pos, nor


def dilate(pos, nor, steps):
    island = ~np.isnan(pos[..., 0])
    for _ in range(steps):
        valid = ~np.isnan(pos[..., 0])
        acc = np.zeros_like(pos)
        accn = np.zeros_like(nor)
        cnt = np.zeros(valid.shape, dtype=np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sv = np.roll(valid, (dy, dx), axis=(0, 1))
            sp = np.roll(np.nan_to_num(pos), (dy, dx), axis=(0, 1))
            sn = np.roll(nor, (dy, dx), axis=(0, 1))
            acc += sp * sv[..., None]
            accn += sn * sv[..., None]
            cnt += sv
        grow = (~valid) & (cnt > 0)
        pos[grow] = acc[grow] / cnt[grow][:, None]
        nor[grow] = accn[grow] / cnt[grow][:, None]
    return island


pc.load_dragon("A")
body = pc.mesh("Dragon_body")
pos, nor = raster(body)
island = dilate(pos, nor, MARGIN)
os.makedirs(OUT, exist_ok=True)
np.save(os.path.join(OUT, "pos.npy"), pos)
np.save(os.path.join(OUT, "nor.npy"), nor)
np.save(os.path.join(OUT, "island.npy"), island)
valid = ~np.isnan(pos[..., 0])
print("POSMAP_DONE", RES, int(island.sum()), int(valid.sum()),
      np.nanmin(pos, axis=(0, 1)).round(3).tolist(), np.nanmax(pos, axis=(0, 1)).round(3).tolist())
