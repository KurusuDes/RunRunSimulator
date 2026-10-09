using UnityEngine;

namespace MoriMonchiSimulator
{
public static class MonchiFraming
{
    public static bool TryWorldBounds(Transform root, Mesh scratch, out Bounds bounds)
    {
        bounds = new Bounds();

        if (root == null || scratch == null)
            return false;

        var renderers = root.GetComponentsInChildren<SkinnedMeshRenderer>(false);
        if (renderers.Length == 0)
            return false;

        bool initialized = false;

        for (int i = 0; i < renderers.Length; i++)
        {
            var r = renderers[i];
            r.BakeMesh(scratch, false);

            var local = scratch.bounds;
            var c = local.center;
            var e = local.extents;
            var t = r.transform;

            for (int s = 0; s < 8; s++)
            {
                var corner = c + new Vector3(
                    (s & 1) == 0 ? -e.x : e.x,
                    (s & 2) == 0 ? -e.y : e.y,
                    (s & 4) == 0 ? -e.z : e.z);
                var world = t.position + t.rotation * corner;

                if (!initialized)
                {
                    bounds = new Bounds(world, Vector3.zero);
                    initialized = true;
                }
                else
                {
                    bounds.Encapsulate(world);
                }
            }
        }

        return true;
    }
}
}
