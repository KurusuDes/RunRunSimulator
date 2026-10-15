using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{

public static class MeadowFlowers
{
    private const int StemSegments = 2;
    private const int PetalCount = 5;
    private const float StemWidth = 0.018f;
    private const float MaxStemLean = 0.12f;
    private const float MaxHeadTilt = 20f;
    private const float PetalBaseRadius = 0.3f;
    private const float PetalHalfAngle = 28f * Mathf.Deg2Rad;
    private const float CoreRadius = 0.28f;
    private const float HeadLift = 0.005f;
    private const float CoreLift = 0.004f;

    private static readonly Color CoreColor = new Color(1f, 0.85f, 0.4f, 0f);

    public static Mesh Build(IReadOnlyList<Vector3> roots, IReadOnlyList<Color> colors, System.Random rng, Vector2 stemHeight, Vector2 headSize, Vector3 origin)
    {
        if (roots == null || roots.Count == 0) return null;

        int vertsPerFlower = StemSegments * 2 + 1 + 1 + PetalCount * 3 + PetalCount;
        int trisPerFlower = (StemSegments * 2 - 1) * 3 + PetalCount * 6 + PetalCount * 3;

        var vertices = new List<Vector3>(roots.Count * vertsPerFlower);
        var normals = new List<Vector3>(roots.Count * vertsPerFlower);
        var uvs = new List<Vector2>(roots.Count * vertsPerFlower);
        var vertexColors = new List<Color>(roots.Count * vertsPerFlower);
        var triangles = new List<int>(roots.Count * trisPerFlower);

        for (int i = 0; i < roots.Count; i++)
        {
            float height = (float)(rng.NextDouble() * (stemHeight.y - stemHeight.x) + stemHeight.x);
            float radius = (float)(rng.NextDouble() * (headSize.y - headSize.x) + headSize.x);
            float yaw = (float)(rng.NextDouble() * Mathf.PI * 2.0);
            var sideAxis = new Vector3(-Mathf.Sin(yaw), 0f, Mathf.Cos(yaw));

            float leanAmount = (float)(rng.NextDouble() * MaxStemLean * height);
            float leanDirection = (float)(rng.NextDouble() * Mathf.PI * 2.0);
            var tipOffset = new Vector3(Mathf.Cos(leanDirection), 0f, Mathf.Sin(leanDirection)) * leanAmount;

            var root = roots[i] - origin;
            var stemNormal = (Vector3.up + sideAxis * 0.25f).normalized;

            float hue = (float)(rng.NextDouble() * 0.2 + 0.4);
            var stemColor = new Color(hue, hue, hue, 1f);

            int stemBase = vertices.Count;
            for (int k = 0; k < StemSegments; k++)
            {
                float t = (float)k / StemSegments;
                var center = root + Vector3.up * (height * t) + tipOffset * (t * t);
                float halfWidth = StemWidth * 0.5f * (1f - t);
                vertices.Add(center + sideAxis * halfWidth);
                vertices.Add(center - sideAxis * halfWidth);
                uvs.Add(new Vector2(0f, t));
                uvs.Add(new Vector2(1f, t));
                normals.Add(stemNormal);
                normals.Add(stemNormal);
                vertexColors.Add(stemColor);
                vertexColors.Add(stemColor);
            }

            var tip = root + Vector3.up * height + tipOffset;
            vertices.Add(tip);
            uvs.Add(new Vector2(0.5f, 1f));
            normals.Add(stemNormal);
            vertexColors.Add(stemColor);

            for (int k = 0; k < StemSegments - 1; k++)
            {
                int bl = stemBase + k * 2;
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

            int last = stemBase + (StemSegments - 1) * 2;
            triangles.Add(last);
            triangles.Add(stemBase + StemSegments * 2);
            triangles.Add(last + 1);

            float tiltAngle = (float)(rng.NextDouble() * MaxHeadTilt);
            float tiltDirection = (float)(rng.NextDouble() * Mathf.PI * 2.0);
            var tiltTarget = new Vector3(Mathf.Cos(tiltDirection), 0f, Mathf.Sin(tiltDirection));
            var rotation = Quaternion.AngleAxis(tiltAngle, Vector3.Cross(Vector3.up, tiltTarget));
            var headNormal = rotation * Vector3.up;
            float startAngle = (float)(rng.NextDouble() * Mathf.PI * 2.0);

            var petalColor = i < colors.Count ? colors[i] : Color.white;
            petalColor.a = 0f;

            var headCenter = tip + Vector3.up * HeadLift;
            int centerIndex = vertices.Count;
            vertices.Add(headCenter);
            uvs.Add(new Vector2(0.5f, 1f));
            normals.Add(headNormal);
            vertexColors.Add(CoreColor);

            for (int p = 0; p < PetalCount; p++)
            {
                float angle = startAngle + p * Mathf.PI * 2f / PetalCount;
                int petalBase = vertices.Count;

                vertices.Add(headCenter + rotation * PlanarDirection(angle - PetalHalfAngle) * (radius * PetalBaseRadius));
                vertices.Add(headCenter + rotation * PlanarDirection(angle) * radius);
                vertices.Add(headCenter + rotation * PlanarDirection(angle + PetalHalfAngle) * (radius * PetalBaseRadius));

                for (int v = 0; v < 3; v++)
                {
                    uvs.Add(new Vector2(0.5f, 1f));
                    normals.Add(headNormal);
                    vertexColors.Add(petalColor);
                }

                triangles.Add(centerIndex);
                triangles.Add(petalBase);
                triangles.Add(petalBase + 1);
                triangles.Add(centerIndex);
                triangles.Add(petalBase + 1);
                triangles.Add(petalBase + 2);
            }

            int coreBase = vertices.Count;
            for (int p = 0; p < PetalCount; p++)
            {
                float angle = startAngle + p * Mathf.PI * 2f / PetalCount;
                vertices.Add(headCenter + rotation * PlanarDirection(angle) * (radius * CoreRadius) + headNormal * CoreLift);
                uvs.Add(new Vector2(0.5f, 1f));
                normals.Add(headNormal);
                vertexColors.Add(CoreColor);
            }

            for (int p = 0; p < PetalCount; p++)
            {
                triangles.Add(centerIndex);
                triangles.Add(coreBase + p);
                triangles.Add(coreBase + (p + 1) % PetalCount);
            }
        }

        var mesh = new Mesh
        {
            name = "MeadowFlowers",
            hideFlags = HideFlags.DontSave
        };

        mesh.indexFormat = vertices.Count > 65000 ? UnityEngine.Rendering.IndexFormat.UInt32 : UnityEngine.Rendering.IndexFormat.UInt16;
        mesh.SetVertices(vertices);
        mesh.SetNormals(normals);
        mesh.SetUVs(0, uvs);
        mesh.SetColors(vertexColors);
        mesh.SetTriangles(triangles, 0);
        mesh.RecalculateBounds();

        return mesh;
    }

    private static Vector3 PlanarDirection(float angle)
    {
        return new Vector3(Mathf.Cos(angle), 0f, Mathf.Sin(angle));
    }
}
}
