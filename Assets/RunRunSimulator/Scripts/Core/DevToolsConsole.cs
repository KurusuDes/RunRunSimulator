using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class DevToolsConsole : MonoBehaviour
{

    [BoxGroup("Setup"), Required]
    [SerializeField] private GameManager gameManager;

    [BoxGroup("Expedition (DEV)"), SerializeField]
    private ExpeditionBridge expeditionBridge;

    [Title("Dev Tools")]
    [BoxGroup("Dev Tools"), SerializeField, LabelText("Dabloons to add")]
    private int devDabloonsAmount = 500;

    [Button("Add Dabloons (DEV)", ButtonSizes.Medium), GUIColor(0.9f, 0.75f, 0.2f), BoxGroup("Dev Tools")]
    private void DevAddDabloons()
    {
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var inventory = gameManager.Inventory;
        if (inventory == null) { Debug.LogWarning("[DevToolsConsole] No inventory assigned."); return; }
        Wallet.Add(Currency.Dabloons, devDabloonsAmount, "dev");
        Debug.Log($"[DevToolsConsole] +{devDabloonsAmount} Dabloons → total: {inventory.Balance(Currency.Dabloons)}");
    }

    [Button("Reset Dabloons (DEV)", ButtonSizes.Medium), GUIColor(1f, 0.5f, 0.3f), BoxGroup("Dev Tools")]
    private void DevResetDabloons()
    {
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var inventory = gameManager.Inventory;
        if (inventory == null) { Debug.LogWarning("[DevToolsConsole] No inventory assigned."); return; }
        inventory.ResetCurrency(Currency.Dabloons);
        GameEvents.InventoryChanged(inventory);
        Debug.Log("[DevToolsConsole] Dabloons reset to 0.");
    }

    [Button("Clear Furniture Owned (DEV)", ButtonSizes.Medium), GUIColor(1f, 0.5f, 0.3f), BoxGroup("Dev Tools")]
    private void DevClearFurnitureOwned()
    {
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var inventory = gameManager.Inventory;
        if (inventory == null) { Debug.LogWarning("[DevToolsConsole] No inventory assigned."); return; }
        inventory.ClearFurnitureOwned();
        GameEvents.InventoryChanged(inventory);
        Debug.Log("[DevToolsConsole] Furniture owned list cleared.");
    }

    [Button("Clear World Props (DEV)", ButtonSizes.Medium), GUIColor(1f, 0.5f, 0.3f), BoxGroup("Dev Tools")]
    private void DevClearWorldProps()
    {
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var inventory = gameManager.Inventory;
        if (inventory == null) { Debug.LogWarning("[DevToolsConsole] No inventory assigned."); return; }
        inventory.ClearWorldPropsStored();
        inventory.ClearHotbar();
        GameEvents.InventoryChanged(inventory);
        Debug.Log("[DevToolsConsole] World props and hotbar cleared.");
    }

    [Button("Reroll Potentials (DEV)", ButtonSizes.Medium), GUIColor(0.9f, 0.75f, 0.2f), BoxGroup("Genetics (DEV)")]
    private void DevRerollPotentials()
    {
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var registry = gameManager.Registry;
        if (registry == null) { Debug.LogWarning("[DevToolsConsole] No registry assigned."); return; }
        int touched = 0;
        foreach (var dna in registry.GetAll().Values)
        {
            if (dna.IsDead || dna.IsSold) continue;
            dna.HornPotential = CreatureGenerator.RandomMintPotential();
            dna.BackPotential = CreatureGenerator.RandomMintPotential();
            dna.WingPotential = CreatureGenerator.RandomMintPotential();
            touched++;
        }
        GameEvents.RegistryChanged(registry);
        Debug.Log($"[DevToolsConsole] Rerolled potentials on {touched} creatures.");
    }

    [BoxGroup("MoriMonchis (DEV)"), SerializeField, LabelText("Adultos a crear"), Min(1)]
    private int devAdultCount = 3;

    [Button("Crear adultos (DEV)", ButtonSizes.Medium), GUIColor(0.55f, 1f, 0.7f), BoxGroup("MoriMonchis (DEV)")]
    private void DevCreateAdults()
    {
        if (!Application.isPlaying) { Debug.LogWarning("[DevToolsConsole] Solo en Play."); return; }
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var registry = gameManager.Registry;
        if (registry == null) { Debug.LogWarning("[DevToolsConsole] No registry assigned."); return; }
        int created = 0;
        for (int i = 0; i < devAdultCount; i++)
        {
            var dna = gameManager.MintCreature();
            if (dna == null) continue;
            dna.Form = MonchiForm.Adult;
            if (dna.Needs != null)
            {
                dna.Needs.Health = 100f;
                dna.Needs.Energy = 100f;
                dna.Needs.Affect = 100f;
            }
            created++;
        }
        if (created == 0) return;
        GameEvents.RegistryChanged(registry);
        Debug.Log($"[DevToolsConsole] Created {created} adult creatures.");
    }

    [Button("Pasar Slimes a adultos (DEV)", ButtonSizes.Medium), GUIColor(0.9f, 0.75f, 0.2f), BoxGroup("MoriMonchis (DEV)")]
    private void DevSlimesToAdults()
    {
        if (!Application.isPlaying) { Debug.LogWarning("[DevToolsConsole] Solo en Play."); return; }
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var registry = gameManager.Registry;
        if (registry == null) { Debug.LogWarning("[DevToolsConsole] No registry assigned."); return; }
        int touched = 0;
        foreach (var dna in registry.GetAll().Values)
        {
            if (dna.IsDead || dna.IsSold) continue;
            if (dna.Form != MonchiForm.Slime) continue;
            dna.Form = MonchiForm.Adult;
            touched++;
        }
        if (touched == 0) return;
        GameEvents.RegistryChanged(registry);
        Debug.Log($"[DevToolsConsole] Slimes turned adult: {touched}.");
    }

    [Button("Cuidar a todos (DEV)", ButtonSizes.Medium), GUIColor(0.9f, 0.75f, 0.2f), BoxGroup("MoriMonchis (DEV)")]
    private void DevCareForAll()
    {
        if (!Application.isPlaying) { Debug.LogWarning("[DevToolsConsole] Solo en Play."); return; }
        if (gameManager == null) { Debug.LogWarning("[DevToolsConsole] No GameManager assigned."); return; }
        var registry = gameManager.Registry;
        if (registry == null) { Debug.LogWarning("[DevToolsConsole] No registry assigned."); return; }
        int touched = 0;
        foreach (var dna in registry.GetAll().Values)
        {
            if (dna.IsDead || dna.IsSold || dna.Needs == null) continue;
            dna.Needs.Health = 100f;
            dna.Needs.Energy = 100f;
            dna.Needs.Affect = 100f;
            touched++;
        }
        if (touched == 0) return;
        GameEvents.RegistryChanged(registry);
        Debug.Log($"[DevToolsConsole] Cared for {touched} creatures.");
    }

    [Button("Salir de expedición (DEV)", ButtonSizes.Medium), GUIColor(0.6f, 0.9f, 1f), BoxGroup("Expedition (DEV)")]
    private void DevDepartExpedition()
    {
        if (!Application.isPlaying) { Debug.LogWarning("[DevToolsConsole] Solo en Play."); return; }
        if (expeditionBridge == null) { Debug.LogWarning("[DevToolsConsole] No ExpeditionBridge assigned."); return; }
        expeditionBridge.Depart();
    }

    [Button("Siguiente bloque (DEV)", ButtonSizes.Medium), GUIColor(0.6f, 0.9f, 1f), BoxGroup("Reloj (DEV)")]
    private void DevNextBlock()
    {
        if (!Application.isPlaying) { Debug.LogWarning("[DevToolsConsole] Solo en Play."); return; }
        if (GameClock.Instance == null) { Debug.LogWarning("[DevToolsConsole] No hay GameClock en la escena."); return; }
        GameClock.Instance.AdvanceToNextBlock();
    }

    [Button("Siguiente día (DEV)", ButtonSizes.Medium), GUIColor(0.6f, 0.9f, 1f), BoxGroup("Reloj (DEV)")]
    private void DevNextDay()
    {
        if (!Application.isPlaying) { Debug.LogWarning("[DevToolsConsole] Solo en Play."); return; }
        if (GameClock.Instance == null) { Debug.LogWarning("[DevToolsConsole] No hay GameClock en la escena."); return; }
        GameClock.Instance.AdvanceToNextDay();
    }

    [Button("Ir a la noche (DEV)", ButtonSizes.Medium), GUIColor(0.6f, 0.9f, 1f), BoxGroup("Reloj (DEV)")]
    private void DevGoToNight()
    {
        if (!Application.isPlaying) { Debug.LogWarning("[DevToolsConsole] Solo en Play."); return; }
        if (GameClock.Instance == null) { Debug.LogWarning("[DevToolsConsole] No hay GameClock en la escena."); return; }
        var clock = GameClock.Instance;
        if (clock.Block != null && clock.Block.ExpeditionOpen) { Debug.Log("[DevToolsConsole] Ya es de noche."); return; }
        for (int i = 0; i < 8; i++)
        {
            clock.AdvanceToNextBlock();
            if (clock.Block != null && clock.Block.ExpeditionOpen)
            {
                Debug.Log($"[DevToolsConsole] Llegó la noche tras {i + 1} bloques.");
                return;
            }
        }
        Debug.LogWarning("[DevToolsConsole] No se llegó a un bloque con expedición abierta tras 8 avances.");
    }
}
}
