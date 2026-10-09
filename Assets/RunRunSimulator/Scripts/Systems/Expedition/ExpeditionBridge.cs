using System;
using System.Collections;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class ExpeditionBridge : MonoBehaviour
{
    [SerializeField] private CloudSyncService cloudSync;
    [SerializeField, Min(1f)] private float syncTimeoutSeconds = 20f;
    [SerializeField, Min(0f)] private float departFlushTimeout = 5f;
    [SerializeField] private bool permadeathEnabled = false;
    [SerializeField, Min(1)] private int mineritaPerMaterial = 5;
    [SerializeField] private BrawlRunRulesSO runRules;

    private bool departing;

    public static event Action<IReadOnlyList<string>> OnDepartureRequested;
    public static void RequestDeparture(IReadOnlyList<string> ids) => OnDepartureRequested?.Invoke(ids);

    private void OnEnable()
    {
        OnDepartureRequested += Depart;
        if (runRules != null) BrawlRunRulesSO.Activate(runRules);
    }

    private void OnDisable()
    {
        OnDepartureRequested -= Depart;
        BrawlRunRulesSO.Deactivate(runRules);
    }

    private void Start()
    {
        if (ExpeditionHandoff.HasResult) StartCoroutine(ApplyResult());
    }

    [Button("Salir de expedición"), EnableIf("@UnityEngine.Application.isPlaying")]
    public void Depart()
    {
        Depart(null);
    }

    public void Depart(IReadOnlyList<string> ids)
    {
        if (departing) return;
        int cost = runRules != null ? runRules.DescentCost : 0;
        if (cost > 0 && !Wallet.TrySpend(Currency.Dabloons, cost, "expedition"))
        {
            Debug.LogWarning($"[ExpeditionBridge] Dabloons insuficientes para bajar ({cost})");
            return;
        }
        departing = true;
        StartCoroutine(DepartRoutine(ids));
    }

    private IEnumerator DepartRoutine(IReadOnlyList<string> ids)
    {
        if (GameManager.Instance != null)
        {
            var task = GameManager.Instance.FlushToCloudAsync();
            float elapsed = 0f;
            while (!task.IsCompleted && elapsed < departFlushTimeout)
            {
                elapsed += Time.unscaledDeltaTime;
                yield return null;
            }
        }

        Cursor.lockState = CursorLockMode.None;
        Cursor.visible = true;
        ExpeditionHandoff.GoToArena(ids);
        departing = false;
    }

    private IEnumerator ApplyResult()
    {
        float elapsed = 0f;
        while (cloudSync != null && !cloudSync.StartupSyncDone && elapsed < syncTimeoutSeconds)
        {
            elapsed += Time.unscaledDeltaTime;
            yield return null;
        }

        if (!ExpeditionHandoff.TryConsumeResult(out ExpeditionResult result)) yield break;

        int material = result.PlayerSecured;
        int minerita = material * mineritaPerMaterial;
        if (minerita > 0) Wallet.Add(Currency.Minerita, minerita, "expedition");

        var registry = GameManager.Instance != null ? GameManager.Instance.Registry : null;
        bool touched = false;

        if (permadeathEnabled && registry != null)
        {
            if (result.FallenIds != null)
            {
                foreach (var id in result.FallenIds)
                {
                    if (!registry.TryGet(id, out var dna) || dna == null || dna.IsDead) continue;
                    CreatureLifecycle.Kill(dna);
                    touched = true;
                }
            }

            if (result.Lost && result.TeamIds != null)
            {
                foreach (var id in result.TeamIds)
                {
                    if (!registry.TryGet(id, out var dna) || dna == null || dna.IsDead) continue;
                    CreatureLifecycle.Kill(dna);
                    touched = true;
                }
            }
        }

        int evolved = 0;
        var evolvedDnas = new List<CreatureDNA>();

        if (registry != null && !result.Lost && result.TeamIds != null)
        {
            int toEvolve = BreedingController.Instance != null && BreedingController.Instance.LifeStageTable != null
                ? BreedingController.Instance.LifeStageTable.ExplorationsToEvolve
                : 3;

            foreach (var id in result.TeamIds)
            {
                if (!registry.TryGet(id, out var dna) || dna == null || dna.IsDead) continue;
                if (result.FallenIds != null && result.FallenIds.Contains(id)) continue;

                bool wasSlime = dna.Form == MonchiForm.Slime;
                if (CreatureGrowth.RecordExploration(dna, toEvolve))
                {
                    evolved++;
                    evolvedDnas.Add(dna);
                }
                if (wasSlime) touched = true;
            }
        }

        if (touched) GameEvents.RegistryChanged(registry);

        foreach (var dna in evolvedDnas) GameEvents.CreatureFormChanged(dna);

        GameEvents.ExpeditionReturned(new ExpeditionReturn
        {
            Seed = result.Seed,
            Winner = result.Winner,
            PlayerSecured = material,
            RivalSecured = result.RivalSecured,
            MineritaGained = minerita,
            Fallen = result.Fallen,
            Floors = result.Floors,
            Lost = result.Lost
        });

        Debug.Log($"[ExpeditionBridge] run {result.Seed}: {result.Floors} pisos, perdida={result.Lost} → +{material} material, +{minerita} Minerita, {result.Fallen} caídas, {evolved} evolucionan");
    }
}
}
