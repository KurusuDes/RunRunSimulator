using UnityEngine;

namespace MoriMonchiSimulator
{
    public static class MonchiEggBody
    {
        public static GameObject Build(CreatureDNA dna, MonchiVisualBankSO bank, Transform parent)
        {
            if (bank == null || bank.EggModel == null)
                return null;

            var instance = Object.Instantiate(bank.EggModel, parent);
            instance.transform.SetLocalPositionAndRotation(Vector3.zero, Quaternion.identity);
            instance.transform.localScale = new Vector3(1f, bank.EggHeight, 1f);

            var bodyPrefab = bank.GetBody(dna.BodyShapeID);
            char bodyLetter = bodyPrefab != null && bodyPrefab.name.Length > 0
                ? bodyPrefab.name[bodyPrefab.name.Length - 1]
                : 'A';

            ApplyPrefixVariant(instance.transform, "Egg_Horn_", null);
            ApplyPrefixVariant(instance.transform, "Egg_Back_", bodyLetter == 'D' ? "Egg_Back_B" : "Egg_Back_A");

            var part = bank.GetPartMesh(dna.BackID, MonchiForm.Egg);
            if (part != null)
                GraftEggPart(instance.transform, part, "Egg_Back_");

            var scales = FindChildByName(instance.transform, "Egg_Scales");
            if (scales != null)
                scales.gameObject.SetActive(false);

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
