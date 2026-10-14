using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public static class ArenaGrassBlades
{
    public static Mesh Build(IReadOnlyList<Vector3> roots, System.Random rng, Vector2 heightRange, Vector2 widthRange, float tilt, Vector3 origin, IReadOnlyList<float> heightScales = null, int segments = 1)
    {
        if (roots == null || roots.Count == 0) return null;

        segments = Mathf.Max(1, segments);
        int vertsPerBlade = segments * 2 + 1;
        int trisPerBlade = (segments * 2 - 1) * 3;

        var vertices = new List<Vector3>(roots.Count * vertsPerBlade);
        var normals = new List<Vector3>(roots.Count * vertsPerBlade);
        var uvs = new List<Vector2>(roots.Count * vertsPerBlade);
        var colors = new List<Color>(roots.Count * vertsPerBlade);
        var triangles = new List<int>(roots.Count * trisPerBlade);

        for (int i = 0; i < roots.Count; i++)
        {
            float height = (float)(rng.NextDouble() * (heightRange.y - heightRange.x) + heightRange.x);
            if (heightScales != null && i < heightScales.Count) height *= heightScales[i];
            float width = (float)(rng.NextDouble() * (widthRange.y - widthRange.x) + widthRange.x);
            float yaw = (float)(rng.NextDouble() * Mathf.PI * 2.0);
            float side = Mathf.Cos(yaw);
            float forward = Mathf.Sin(yaw);
            var sideAxis = new Vector3(-forward, 0f, side);

            float leanAngle = (float)(rng.NextDouble() * tilt);
            float leanDirection = (float)(rng.NextDouble() * Mathf.PI * 2.0);
            var leanAxis = new Vector3(Mathf.Cos(leanDirection), 0f, Mathf.Sin(leanDirection));

            var root = roots[i] - origin;

            var tipOffset = leanAxis * (Mathf.Sin(leanAngle) * height);

            var normal = (Vector3.up + sideAxis * 0.25f).normalized;

            float hue = (float)rng.NextDouble();
            var bladeColor = new Color(hue, hue, hue, 1f);

            int baseIndex = vertices.Count;
            for (int k = 0; k < segments; k++)
            {
                float t = (float)k / segments;
                var center = root + Vector3.up * (height * t) + tipOffset * (t * t);
                float halfWidth = width * 0.5f * (1f - t);
                vertices.Add(center + sideAxis * halfWidth);
                vertices.Add(center - sideAxis * halfWidth);
                uvs.Add(new Vector2(0f, t));
                uvs.Add(new Vector2(1f, t));
                normals.Add(normal);
                normals.Add(normal);
                colors.Add(bladeColor);
                colors.Add(bladeColor);
            }

            vertices.Add(root + Vector3.up * height + tipOffset);
            uvs.Add(new Vector2(0.5f, 1f));
            normals.Add(normal);
            colors.Add(bladeColor);

            for (int k = 0; k < segments - 1; k++)
            {
                int bl = baseIndex + k * 2;
                int br = bl + 1;
                int tl = bl + 2;
                int tr = bl + 3;
                triangles.Add(bl);
                triangles.Add(tl);
                triangles.Add(br);
                triangles.Add(br);
                triangles.Add(tl);
                triangles.Add(tr);
            }

            int last = baseIndex + (segments - 1) * 2;
            triangles.Add(last);
            triangles.Add(baseIndex + segments * 2);
            triangles.Add(last + 1);
        }

        var mesh = new Mesh
        {
            name = "ArenaGrassBlades",
            hideFlags = HideFlags.DontSave
        };

        mesh.indexFormat = vertices.Count > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16;
        mesh.SetVertices(vertices);
        mesh.SetNormals(normals);
        mesh.SetUVs(0, uvs);
        mesh.SetColors(colors);
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateBounds();

        return mesh;
    }
}
}
