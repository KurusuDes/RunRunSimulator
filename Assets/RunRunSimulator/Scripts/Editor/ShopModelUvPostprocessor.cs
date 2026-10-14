using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
namespace MoriMonchiSimulator
{

public class ShopModelUvPostprocessor : AssetPostprocessor
{
    private const string ShopFolder = "Assets/RunRunSimulator/Resources/Models/Shop/";

    private void OnPreprocessModel()
    {
        if (!assetPath.StartsWith(ShopFolder)) return;
        ((ModelImporter)assetImporter).isReadable = true;
    }

    private void OnPostprocessModel(GameObject root)
    {
        if (!assetPath.StartsWith(ShopFolder)) return;

        foreach (var filter in root.GetComponentsInChildren<MeshFilter>(true))
        {
            var mesh = filter.sharedMesh;
            if (mesh == null || mesh.uv.Length > 0) continue;
            GenerateBoxUv(mesh);
        }
    }

    private static void GenerateBoxUv(Mesh mesh)
    {
        var srcVertices = mesh.vertices;
        var srcNormals = mesh.normals;
        bool hasNormals = srcNormals.Length == srcVertices.Length;
        int submeshCount = mesh.subMeshCount;

        var submeshIndices = new int[submeshCount][];
        int total = 0;
        for (int s = 0; s < submeshCount; s++)
        {
            submeshIndices[s] = mesh.GetTriangles(s);
            total += submeshIndices[s].Length;
        }

        var vertices = new Vector3[total];
        var normals = hasNormals ? new Vector3[total] : null;
        var uvs = new Vector2[total];
        var newIndices = new int[submeshCount][];

        int cursor = 0;
        for (int s = 0; s < submeshCount; s++)
        {
            var src = submeshIndices[s];
            var dst = new int[src.Length];

            for (int t = 0; t + 2 < src.Length; t += 3)
            {
                Vector3 a = srcVertices[src[t]];
                Vector3 b = srcVertices[src[t + 1]];
                Vector3 c = srcVertices[src[t + 2]];
                Vector3 n = Vector3.Cross(b - a, c - a);
                float ax = Mathf.Abs(n.x);
                float ay = Mathf.Abs(n.y);
                float az = Mathf.Abs(n.z);
                int axis = ax >= ay && ax >= az ? 0 : (ay >= az ? 1 : 2);

                for (int k = 0; k < 3; k++)
                {
                    int srcIndex = src[t + k];
                    Vector3 p = srcVertices[srcIndex];
                    vertices[cursor] = p;
                    if (hasNormals) normals[cursor] = srcNormals[srcIndex];
                    uvs[cursor] = axis == 0 ? new Vector2(p.z, p.y)
                                : axis == 1 ? new Vector2(p.x, p.z)
                                : new Vector2(p.x, p.y);
                    dst[t + k] = cursor;
                    cursor++;
                }
            }

            newIndices[s] = dst;
        }

        mesh.Clear();
        mesh.indexFormat = total > 65535 ? IndexFormat.UInt32 : IndexFormat.UInt16;
        mesh.vertices = vertices;
        if (hasNormals) mesh.normals = normals;
        mesh.uv = uvs;
        mesh.subMeshCount = submeshCount;
        for (int s = 0; s < submeshCount; s++) mesh.SetTriangles(newIndices[s], s);
        mesh.RecalculateBounds();
        mesh.RecalculateTangents();
    }
}

}
