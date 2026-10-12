using System.Collections;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class StarterKitService : MonoBehaviour
{
    [Required, SerializeField] private StarterKitSO kit;
    [Required, SerializeField] private CloudSyncService cloudSync;
    [SerializeField] private float syncTimeoutSeconds = 20f;

    private void Start()
    {
        StartCoroutine(ApplyKitRoutine());
    }

    private IEnumerator ApplyKitRoutine()
    {
        float elapsed = 0f;
        while (cloudSync != null && !cloudSync.StartupSyncDone && elapsed < syncTimeoutSeconds)
        {
            elapsed += Time.unscaledDeltaTime;
            yield return null;
        }

        TryApply();
    }

    public bool TryApply()
    {
        var worldState = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
        var registry = GameManager.Instance != null ? GameManager.Instance.Registry : null;
        var inventory = GameManager.CurrentInventory;

        if (kit == null || worldState == null || registry == null || inventory == null)
        {
            Debug.LogWarning("[StarterKit] refs faltantes, no se aplica el kit.");
            return false;
        }

        bool isNewGame = worldState.TutorialStep == 0 && registry.Count == 0;
        if (!isNewGame)
        {
            Debug.Log("[StarterKit] partida existente, kit no aplicado.");
            return false;
        }

        if (kit.Minerita > 0) Wallet.Add(Currency.Minerita, kit.Minerita, "starter");
        if (kit.Dabloons > 0) Wallet.Add(Currency.Dabloons, kit.Dabloons, "starter");

        worldState.TutorialStep = 1;
        GameEvents.WorldStateChanged(worldState);

        Debug.Log($"[StarterKit] Kit inicial aplicado: +{kit.Minerita} Minerita, +{kit.Dabloons} Dabloons.");
        return true;
    }
}
}
