import bpy
import sys
import addon_utils

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []

mod = None
for m in addon_utils.modules():
    if m.__name__.endswith("io_scene_fbx"):
        mod = m
        break
import importlib
parse_fbx = importlib.import_module(mod.__name__ + ".parse_fbx")


def describe(path):
    root, version = parse_fbx.parse(path)
    print("=== ", path, "version", version)
    objects = None
    for el in root.elems:
        if el.id == b"GlobalSettings":
            for p in el.elems:
                if p.id == b"Properties70":
                    for pp in p.elems:
                        name = pp.props[0].decode() if isinstance(pp.props[0], bytes) else pp.props[0]
                        if name in ("UpAxis", "UpAxisSign", "FrontAxis", "FrontAxisSign", "CoordAxis", "CoordAxisSign", "UnitScaleFactor", "OriginalUnitScaleFactor", "TimeMode", "CustomFrameRate"):
                            print("  GS", name, pp.props[-1])
        if el.id == b"Objects":
            objects = el
        if el.id == b"Takes":
            for t in el.elems:
                if t.id == b"Take":
                    print("  TAKE", t.props[0])
    counts = {}
    models = []
    for o in objects.elems:
        counts[o.id] = counts.get(o.id, 0) + 1
        if o.id == b"Model":
            models.append((o.props[1].split(b"\x00")[0].decode(), o.props[2].decode()))
        if o.id == b"AnimationStack":
            print("  STACK", o.props[1].split(b"\x00")[0].decode())
    print("  COUNTS", {k.decode(): v for k, v in counts.items()})
    print("  MODELS", len(models), models[:6])


for p in ARGS:
    describe(p)
