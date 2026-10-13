using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{
    public class TitleDiorama : MonoBehaviour
    {
        [Required, SerializeField] private GameObject monchiPrefab;
        [Required, SerializeField] private CreatureDatabaseSO database;
        [Required, SerializeField] private FurTypeDatabaseSO furDatabase;
        [Required, SerializeField] private MonchiVisualBankSO visualBank;
        [Required, SerializeField] private Transform center;
        [SerializeField] private int count = 5;
        [SerializeField] private float radius = 6f;

        private void Start()
        {
            for (int i = 0; i < count; i++)
                Spawn();
        }

        private void Spawn()
        {
            if (!TryFindPoint(out var point)) return;

            var dna = CreatureGenerator.GenerateRandom(database, furDatabase);
            dna.Form = MonchiForm.Adult;
            dna.Gender = Random.value < 0.5f ? CreatureGender.Male : CreatureGender.Female;
            dna.Element = CreatureGenerator.RandomElement();
            dna.Role = CreatureGenerator.RandomRole();
            dna.Generation = 1;
            dna.Sociability = CreatureGenerator.RandomDial();
            dna.Boldness = CreatureGenerator.RandomDial();
            dna.CustomName = CreatureNameBank.GetRandomName();
            dna.BirthDay = 1;
            dna.Stamp();

            var instance = Instantiate(monchiPrefab, point, Quaternion.Euler(0f, Random.Range(0f, 360f), 0f), transform);

            var visualizer = instance.GetComponentInChildren<MonchiVisualizer>();
            visualizer.SetBank(visualBank);
            visualizer.SetFurDatabase(furDatabase);
            visualizer.Assemble(dna);

            instance.GetComponent<TitleWanderer>().Init(center, radius);
        }

        private bool TryFindPoint(out Vector3 point)
        {
            for (int i = 0; i < 12; i++)
            {
                Vector2 offset = Random.insideUnitCircle * radius;
                var candidate = center.position + new Vector3(offset.x, 0f, offset.y);
                if (NavMesh.SamplePosition(candidate, out var hit, 2f, NavMesh.AllAreas))
                {
                    point = hit.position;
                    return true;
                }
            }

            point = default;
            return false;
        }
    }
}
