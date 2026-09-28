using UnityEngine;

namespace MoriMonchiSimulator
{
    public static class EggLabAssembler
    {
        public static GameObject Build(CreatureDNA dna, MonchiVisualBankSO bank, FurTypeDatabaseSO furDb, GameObject eggModel, RuntimeAnimatorController controller, Transform parent)
        {
            var instance = Object.Instantiate(eggModel, parent);

            var animator = instance.GetComponent<Animator>();
            if (animator == null)
                animator = instance.AddComponent<Animator>();
            if (controller != null)
                animator.runtimeAnimatorController = controller;

            var bodyPrefab = bank != null ? bank.GetBody(dna.BodyShapeID) : null;
            char bodyLetter = bodyPrefab != null && bodyPrefab.name.Length > 0
                ? bodyPrefab.name[bodyPrefab.name.Length - 1]
                : 'A';

            ApplyPrefixVariant(instance.transform, "Egg_Horn_", "Egg_Horn_" + bodyLetter);
            ApplyPrefixVariant(instance.transform, "Egg_Back_", bodyLetter == 'D' ? "Egg_Back_B" : "Egg_Back_A");

            if (bank != null)
            {
                GraftEggPart(instance.transform, bank.GetPartMesh(dna.HornID, MonchiForm.Egg), "Egg_Horn_");
                GraftEggPart(instance.transform, bank.GetPartMesh(dna.BackID, MonchiForm.Egg), "Egg_Back_");
            }

            ColorGenetics.BuildHarmony(dna.BaseColor, out var wing, out var accent);

            Material gemMat = dna.IsShiny && bank != null ? bank.GetGem(dna.ToStringID()) : null;
            Material material = gemMat != null ? gemMat : (furDb != null ? furDb.GetMaterial(dna.FurType) : null);

            foreach (var renderer in instance.GetComponentsInChildren<Renderer>(false))
            {
                if (renderer.gameObject.name == "Egg_Scales")
                    continue;

                if (material != null)
                    renderer.sharedMaterial = material;

                var mpb = new MaterialPropertyBlock();
                if (!dna.IsShiny)
                {
                    string name = renderer.gameObject.name;
                    if (name.StartsWith("Egg_"))
                        name = name.Substring(4);
                    MonchiTint.Fill(mpb, MonchiTint.ColorFor(name, dna, wing, accent));
                }
                renderer.SetPropertyBlock(mpb);
            }

            return instance;
        }

        private static void ApplyPrefixVariant(Transform root, string prefix, string keep)
        {
            for (int i = 0; i < root.childCount; i++)
            {
                var child = root.GetChild(i);
                if (child.name.StartsWith(prefix))
                    child.gameObject.SetActive(child.name == keep);
            }
        }

        private static void GraftEggPart(Transform root, GameObject partMesh, string prefix)
        {
            if (partMesh == null)
                return;

            for (int i = 0; i < root.childCount; i++)
            {
                var child = root.GetChild(i);
                if (child.name.StartsWith(prefix))
                    child.gameObject.SetActive(false);
            }

            var body = FindChildByName(root, "Body");
            var instance = Object.Instantiate(partMesh, root);
            instance.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            instance.transform.localScale = Vector3.one;

            if (body != null)
                instance.transform.SetParent(body, true);
        }

        private static Transform FindChildByName(Transform root, string name)
        {
            foreach (var candidate in root.GetComponentsInChildren<Transform>(true))
            {
                if (candidate.name == name)
                    return candidate;
            }
            return null;
        }
    }
}
