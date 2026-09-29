using UnityEngine;

namespace MoriMonchiSimulator
{
    public static class MonchiSlimeBody
    {
        public static GameObject Build(CreatureDNA dna, MonchiVisualBankSO bank, Transform parent)
        {
            if (bank == null || bank.SlimeModel == null)
                return null;

            var instance = Object.Instantiate(bank.SlimeModel, parent);
            instance.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            instance.transform.localScale = Vector3.one * bank.SlimeScale;

            var bodyPrefab = bank.GetBody(dna.BodyShapeID);
            char bodyLetter = bodyPrefab != null && bodyPrefab.name.Length > 0
                ? bodyPrefab.name[bodyPrefab.name.Length - 1]
                : 'A';

            ApplyHornVariant(instance.transform, "Horn_" + bodyLetter);

            var part = bank.GetPartMesh(dna.HornID, MonchiForm.Slime);
            if (part != null)
                GraftHornPart(instance.transform, part);

            return instance;
        }

        private static void ApplyHornVariant(Transform root, string keep)
        {
            for (int i = 0; i < root.childCount; i++)
            {
                var child = root.GetChild(i);
                if (child.name.StartsWith("Horn_"))
                    child.gameObject.SetActive(child.name == keep);
            }
        }

        private static void GraftHornPart(Transform root, GameObject partMesh)
        {
            for (int i = 0; i < root.childCount; i++)
            {
                var child = root.GetChild(i);
                if (child.name.StartsWith("Horn_"))
                    child.gameObject.SetActive(false);
            }

            var top = FindChildByName(root, "Top");
            var instance = Object.Instantiate(partMesh, root);
            instance.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            instance.transform.localScale = Vector3.one;

            if (top != null)
                instance.transform.SetParent(top, true);
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
