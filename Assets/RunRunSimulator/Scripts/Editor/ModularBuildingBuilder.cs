using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace MoriMonchiSimulator
{
    public static class ModularBuildingBuilder
    {
        public static void Clear(ModularBuilding b)
        {
            var existing = b.transform.Find(ModularBuilding.GeneratedName);
            if (existing != null) Undo.DestroyObjectImmediate(existing.gameObject);
        }

        public static void Build(ModularBuilding b)
        {
            var set = b.PieceSet;
            if (set == null)
            {
                Debug.LogWarning("ModularBuilding sin PieceSet asignado.", b);
                return;
            }

            Clear(b);

            var rootGo = new GameObject(ModularBuilding.GeneratedName);
            Undo.RegisterCreatedObjectUndo(rootGo, "Armar edificio modular");
            var root = rootGo.transform;
            root.SetParent(b.transform, false);
            root.localPosition = Vector3.zero;
            root.localRotation = Quaternion.identity;
            root.localScale = Vector3.one;

            int w = b.SizeCells.x;
            int d = b.SizeCells.y;
            float c = ModularPieceSetSO.Cell;
            float h = ModularPieceSetSO.Storey;
            float rise = ModularPieceSetSO.RoofRise;

            if (b.BuildFloor)
            {
                for (int i = 0; i < w; i++)
                {
                    for (int j = 0; j < d; j++)
                    {
                        var go = Spawn(set.Floor, root, "Floor_" + i + "_" + j, new Vector3((i + 1) * c, 0f, j * c), 0f, Vector3.one);
                        if (go != null && set.FloorMaterials != null && set.FloorMaterials.Length > 0)
                            SetMaterials(go, set.FloorMaterials);
                    }
                }
            }

            var sides = new[] { ModularSide.South, ModularSide.East, ModularSide.North, ModularSide.West };
            foreach (var side in sides)
            {
                int count = (side == ModularSide.South || side == ModularSide.North) ? w : d;
                for (int n = 0; n < count; n++)
                {
                    var opening = b.OpeningAt(side, n, out int v);
                    var (pos, yaw) = Place(w, d, side, n, 0f);
                    switch (opening)
                    {
                        case ModularOpening.Wall:
                            SpawnWall(set, set.Wall, root, side + "_Wall_" + n, pos, yaw, Vector3.one, true);
                            break;
                        case ModularOpening.Window:
                            Spawn(set.PickWindow(v), root, side + "_Window_" + n, pos, yaw, Vector3.one);
                            break;
                        case ModularOpening.Door:
                            Spawn(set.PickDoor(v), root, side + "_Door_" + n, pos, yaw, Vector3.one);
                            break;
                    }
                    if (b.BuildPlinth && opening != ModularOpening.Open)
                    {
                        var plinth = Spawn(set.Plinth, root, side + "_Plinth_" + n, pos + new Vector3(0f, -ModularPieceSetSO.PlinthHeight, 0f), yaw, Vector3.one);
                        if (plinth != null && set.PlinthMaterial != null)
                        {
                            foreach (var r in plinth.GetComponentsInChildren<Renderer>())
                            {
                                var mats = new Material[r.sharedMaterials.Length];
                                for (int m = 0; m < mats.Length; m++) mats[m] = set.PlinthMaterial;
                                r.sharedMaterials = mats;
                            }
                        }
                    }
                }
            }

            float halfY = -ModularPieceSetSO.PillarHalfHeight;
            for (int i = 0; i <= w; i++)
            {
                Spawn(set.Pillar, root, "Pillar_S_" + i, new Vector3(i * c, 0f, 0f), 0f, Vector3.one);
                Spawn(set.Pillar, root, "Pillar_N_" + i, new Vector3(i * c, 0f, d * c), 0f, Vector3.one);
                if (b.BuildPlinth)
                {
                    Spawn(set.PillarHalf, root, "PillarHalf_S_" + i, new Vector3(i * c, halfY, 0f), 0f, Vector3.one);
                    Spawn(set.PillarHalf, root, "PillarHalf_N_" + i, new Vector3(i * c, halfY, d * c), 0f, Vector3.one);
                }
            }
            for (int j = 1; j < d; j++)
            {
                Spawn(set.Pillar, root, "Pillar_W_" + j, new Vector3(0f, 0f, j * c), 0f, Vector3.one);
                Spawn(set.Pillar, root, "Pillar_E_" + j, new Vector3(w * c, 0f, j * c), 0f, Vector3.one);
                if (b.BuildPlinth)
                {
                    Spawn(set.PillarHalf, root, "PillarHalf_W_" + j, new Vector3(0f, halfY, j * c), 0f, Vector3.one);
                    Spawn(set.PillarHalf, root, "PillarHalf_E_" + j, new Vector3(w * c, halfY, j * c), 0f, Vector3.one);
                }
            }

            for (int i = 0; i < w; i++)
            {
                if (b.OpeningAt(ModularSide.South, i, out _) != ModularOpening.Open)
                    Spawn(set.Beam, root, "Beam_S_" + i, new Vector3((i + 1) * c, h, 0f), 0f, Vector3.one);
                if (b.OpeningAt(ModularSide.North, i, out _) != ModularOpening.Open)
                    Spawn(set.Beam, root, "Beam_N_" + i, new Vector3((i + 1) * c, h, d * c), 0f, Vector3.one);
            }
            for (int j = 0; j < d; j++)
            {
                if (b.OpeningAt(ModularSide.West, j, out _) != ModularOpening.Open)
                    Spawn(set.Beam, root, "Beam_W_" + j, new Vector3(0f, h, j * c), 90f, Vector3.one);
                if (b.OpeningAt(ModularSide.East, j, out _) != ModularOpening.Open)
                    Spawn(set.Beam, root, "Beam_E_" + j, new Vector3(w * c, h, j * c), 90f, Vector3.one);
            }

            if (b.BuildRoof)
            {
                var preset = b.UsePresetRoof ? set.RoofPresetFor(b.SizeCells) : null;
                if (preset != null) Spawn(preset, root, "RoofPreset", Vector3.zero, 0f, Vector3.one);
                else BuildRoof(b, set, root, w, d, c, h, rise);
            }

            EditorSceneManager.MarkSceneDirty(b.gameObject.scene);
        }

        private static void BuildRoof(ModularBuilding b, ModularPieceSetSO set, Transform root, int w, int d, float c, float h, float rise)
        {
            int rows = w / 2;
            bool odd = w % 2 != 0;

            for (int r = 0; r < rows; r++)
            {
                float y = h + rise * (r + 1);
                float xW = (r + 1) * c;
                float xE = w * c - (r + 1) * c;
                for (int j = 0; j < d; j++)
                {
                    Spawn(set.RoofRow, root, "RoofRow_W_" + r + "_" + j, new Vector3(xW, y, (j + 1) * c), 270f, Vector3.one);
                    Spawn(set.RoofRow, root, "RoofRow_E_" + r + "_" + j, new Vector3(xE, y, j * c), 90f, Vector3.one);
                }
                Spawn(set.RoofEnd, root, "RoofEnd_WS_" + r, new Vector3(xW, y, 0f), 270f, new Vector3(1f, 1f, 1f));
                Spawn(set.RoofEnd, root, "RoofEnd_WN_" + r, new Vector3(xW, y, d * c), 270f, new Vector3(-1f, 1f, 1f));
                Spawn(set.RoofEnd, root, "RoofEnd_ES_" + r, new Vector3(xE, y, 0f), 90f, new Vector3(-1f, 1f, 1f));
                Spawn(set.RoofEnd, root, "RoofEnd_EN_" + r, new Vector3(xE, y, d * c), 90f, new Vector3(1f, 1f, 1f));
            }

            if (odd)
            {
                float xc = w * c * 0.5f;
                float yTop = h + rise * rows + ModularPieceSetSO.RoofRiseHalf;
                for (int j = 0; j < d; j++)
                {
                    Spawn(set.RoofRowHalf, root, "RoofRowHalf_W_" + j, new Vector3(xc, yTop, (j + 1) * c), 270f, Vector3.one);
                    Spawn(set.RoofRowHalf, root, "RoofRowHalf_E_" + j, new Vector3(xc, yTop, j * c), 90f, Vector3.one);
                }
                Spawn(set.RoofEndHalf, root, "RoofEndHalf_WS", new Vector3(xc, yTop, 0f), 270f, new Vector3(1f, 1f, 1f));
                Spawn(set.RoofEndHalf, root, "RoofEndHalf_WN", new Vector3(xc, yTop, d * c), 270f, new Vector3(-1f, 1f, 1f));
                Spawn(set.RoofEndHalf, root, "RoofEndHalf_ES", new Vector3(xc, yTop, 0f), 90f, new Vector3(-1f, 1f, 1f));
                Spawn(set.RoofEndHalf, root, "RoofEndHalf_EN", new Vector3(xc, yTop, d * c), 90f, new Vector3(1f, 1f, 1f));
            }

            var gableExterior = set.GableExterior != null ? set.GableExterior : set.WallExterior;
            for (int r = 0; r < rows; r++)
            {
                float y = h + rise * r;
                for (int i = r; i <= w - 1 - r; i++)
                {
                    bool highEast = i == r;
                    bool highWest = i == w - 1 - r;
                    if (highEast == highWest)
                    {
                        var (pS, yS) = Place(w, d, ModularSide.South, i, y);
                        SpawnWall(set, set.Wall, root, "GableWall_S_" + r + "_" + i, pS, yS, Vector3.one, true, gableExterior);
                        var (pN, yN) = Place(w, d, ModularSide.North, i, y);
                        SpawnWall(set, set.Wall, root, "GableWall_N_" + r + "_" + i, pN, yN, Vector3.one, true, gableExterior);
                    }
                    else if (highEast)
                    {
                        var (pS, yS) = Place(w, d, ModularSide.South, i, y);
                        SpawnWall(set, set.GableAngle, root, "Gable_S_" + r + "_" + i, pS, yS, Vector3.one, true, gableExterior);
                        SpawnWall(set, set.GableAngle, root, "Gable_N_" + r + "_" + i, new Vector3((i + 1) * c, y, d * c), 0f, Vector3.one, false, gableExterior);
                    }
                    else
                    {
                        SpawnWall(set, set.GableAngle, root, "Gable_S_" + r + "_" + i, new Vector3(i * c, y, 0f), 180f, Vector3.one, false, gableExterior);
                        var (pN, yN) = Place(w, d, ModularSide.North, i, y);
                        SpawnWall(set, set.GableAngle, root, "Gable_N_" + r + "_" + i, pN, yN, Vector3.one, true, gableExterior);
                    }
                }
            }

            if (odd)
            {
                int i = rows;
                float y = h + rise * rows;
                float x = i * c + 1.25f;
                SpawnWall(set, set.GableAngleHalf, root, "GableHalf_S_W", new Vector3(x, y, 0f), 0f, Vector3.one, true, gableExterior);
                SpawnWall(set, set.GableAngleHalf, root, "GableHalf_S_E", new Vector3(x, y, 0f), 180f, Vector3.one, false, gableExterior);
                SpawnWall(set, set.GableAngleHalf, root, "GableHalf_N_W", new Vector3(x, y, d * c), 0f, Vector3.one, false, gableExterior);
                SpawnWall(set, set.GableAngleHalf, root, "GableHalf_N_E", new Vector3(x, y, d * c), 180f, Vector3.one, true, gableExterior);
            }
        }

        private static (Vector3 pos, float yaw) Place(int w, int d, ModularSide side, int index, float y)
        {
            float c = ModularPieceSetSO.Cell;
            switch (side)
            {
                case ModularSide.South: return (new Vector3((index + 1) * c, y, 0f), 0f);
                case ModularSide.North: return (new Vector3(index * c, y, d * c), 180f);
                case ModularSide.West: return (new Vector3(0f, y, index * c), 90f);
                default: return (new Vector3(w * c, y, (index + 1) * c), 270f);
            }
        }

        private static GameObject Spawn(GameObject prefab, Transform parent, string label, Vector3 pos, float yaw, Vector3 scale)
        {
            if (prefab == null) return null;
            var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, parent);
            go.name = prefab.name + "_" + label;
            go.transform.localPosition = pos;
            go.transform.localRotation = Quaternion.Euler(0f, yaw, 0f);
            go.transform.localScale = scale;
            Undo.RegisterCreatedObjectUndo(go, "Armar edificio modular");
            return go;
        }

        private static GameObject SpawnWall(ModularPieceSetSO set, GameObject prefab, Transform parent, string label, Vector3 pos, float yaw, Vector3 scale, bool exteriorOut, Material exterior = null)
        {
            var go = Spawn(prefab, parent, label, pos, yaw, scale);
            if (exterior == null) exterior = set.WallExterior;
            if (go == null || exterior == null || set.WallInterior == null) return go;
            bool firstOut = exteriorOut;
            var mf = go.GetComponentInChildren<MeshFilter>();
            if (mf != null && mf.sharedMesh != null && FirstSubmeshFacesPlusZ(mf.sharedMesh)) firstOut = !firstOut;
            var mats = firstOut
                ? new[] { exterior, set.WallInterior }
                : new[] { set.WallInterior, exterior };
            SetMaterials(go, mats);
            return go;
        }

        private static readonly Dictionary<Mesh, bool> facesPlusZCache = new Dictionary<Mesh, bool>();

        private static bool FirstSubmeshFacesPlusZ(Mesh mesh)
        {
            if (facesPlusZCache.TryGetValue(mesh, out bool cached)) return cached;
            bool result = false;
            if (mesh.isReadable && mesh.subMeshCount >= 2)
            {
                var normals = mesh.normals;
                var indices = mesh.GetIndices(0);
                if (normals.Length > 0 && indices.Length > 0)
                {
                    float sum = 0f;
                    for (int k = 0; k < indices.Length; k++) sum += normals[indices[k]].z;
                    result = sum / indices.Length > 0f;
                }
            }
            facesPlusZCache[mesh] = result;
            return result;
        }

        private static void SetMaterials(GameObject go, Material[] mats)
        {
            foreach (var r in go.GetComponentsInChildren<Renderer>())
                r.sharedMaterials = mats;
        }
    }
}
