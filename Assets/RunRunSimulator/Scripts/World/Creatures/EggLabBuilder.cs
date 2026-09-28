using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.InputSystem;

namespace MoriMonchiSimulator
{
    public class EggLabBuilder : MonoBehaviour
    {
        [Required, SerializeField] private CreatureDatabaseSO partDatabase;
        [Required, SerializeField] private FurTypeDatabaseSO furDatabase;
        [Required, SerializeField] private MonchiVisualBankSO visualBank;
        [Required, SerializeField] private InheritanceOddsTableSO odds;
        [Required, SerializeField] private GameObject eggModel;
        [Required, SerializeField] private RuntimeAnimatorController eggController;
        [Required, SerializeField] private Transform eggsRoot;
        [Required, SerializeField] private Camera worldCamera;

        [SerializeField] private int count = 24;
        [SerializeField] private int columns = 6;
        [SerializeField] private float spacing = 0.55f;
        [SerializeField] private float faceYaw = 180f;

        private readonly List<EggLabEntry> entries = new List<EggLabEntry>();
        private CreatureRegistrySO registry;
        private long nextTimestamp;

        public IReadOnlyList<EggLabEntry> Entries => entries;

        public event Action Rebuilt;
        public event Action<EggLabEntry> Selected;

        private void Start()
        {
            Rebuild();
        }

        private void Update()
        {
            if (Mouse.current == null || !Mouse.current.leftButton.wasPressedThisFrame)
                return;

            var ray = worldCamera.ScreenPointToRay(Mouse.current.position.ReadValue());
            if (!Physics.Raycast(ray, out var hit))
                return;

            foreach (var entry in entries)
            {
                if (entry.Root != null && hit.collider.transform == entry.Root)
                {
                    Select(entry);
                    return;
                }
            }
        }

        public void Rebuild()
        {
            for (int i = eggsRoot.childCount - 1; i >= 0; i--)
                Destroy(eggsRoot.GetChild(i).gameObject);

            entries.Clear();

            if (registry != null)
                Destroy(registry);
            registry = ScriptableObject.CreateInstance<CreatureRegistrySO>();

            nextTimestamp = 0;

            for (int i = 0; i < count; i++)
            {
                var mother = CreatureGenerator.GenerateRandom(partDatabase, furDatabase);
                mother.Gender = CreatureGender.Female;
                mother.Timestamp = ++nextTimestamp;
                mother.CustomName = CreatureNameBank.GetRandomName();
                registry.Register(mother);

                var father = CreatureGenerator.GenerateRandom(partDatabase, furDatabase);
                father.Gender = CreatureGender.Male;
                father.Timestamp = ++nextTimestamp;
                father.CustomName = CreatureNameBank.GetRandomName();
                registry.Register(father);

                var child = BreedingService.Breed(mother.UniqueID, father.UniqueID, registry, partDatabase, odds);
                if (child == null)
                    continue;

                var entry = new EggLabEntry
                {
                    Number = i + 1,
                    Egg = child,
                    Mother = mother,
                    Father = father,
                    Progress01 = UnityEngine.Random.value,
                    HatchCost = odds.HatchCost(mother, father),
                };

                var root = EggLabAssembler.Build(child, visualBank, furDatabase, eggModel, eggController, eggsRoot);
                float x = (i % columns - (columns - 1) / 2f) * spacing;
                float z = -(i / columns) * spacing;
                root.transform.SetLocalPositionAndRotation(new Vector3(x, 0f, z), Quaternion.Euler(0f, faceYaw, 0f));
                root.name = $"Egg_{entry.Number}";
                root.AddComponent<EggIdleShuffler>();

                var collider = root.AddComponent<CapsuleCollider>();
                collider.center = new Vector3(0f, 0.16f, 0f);
                collider.radius = 0.13f;
                collider.height = 0.32f;

                entry.Root = root.transform;
                entries.Add(entry);
            }

            Rebuilt?.Invoke();
        }

        public void Select(EggLabEntry entry)
        {
            Selected?.Invoke(entry);
        }

        private void OnDestroy()
        {
            if (registry != null)
                Destroy(registry);
        }
    }
}
