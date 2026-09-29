using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.SceneManagement;
namespace MoriMonchiSimulator
{

public class AutoPlayer : MonoBehaviour
{
    [SerializeField] private float arenaTimeScale = 4f;
    [SerializeField] private float stepTimeout = 60f;

    public static AutoPlayer Instance { get; private set; }

    public string Status { get; private set; } = "Idle";

    private bool running;
    private bool failed;
    private int  currentStep;

    private readonly List<string> eggIds   = new List<string>();
    private List<string>          slimeIds = new List<string>();

    private ExpeditionReturn? lastExpeditionReturn;

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }

    private void OnEnable()  => GameEvents.OnExpeditionReturned += HandleExpeditionReturned;
    private void OnDisable() => GameEvents.OnExpeditionReturned -= HandleExpeditionReturned;

    private void HandleExpeditionReturned(ExpeditionReturn r) => lastExpeditionReturn = r;

    private void Start()
    {
        if (!running) Run();
    }

    public void Run()
    {
        if (running) return;
        running = true;
        failed  = false;
        StartCoroutine(Sequence());
    }

    private IEnumerator Sequence()
    {
        yield return Step1_Arrival();           if (failed) yield break;
        yield return Step2_BuyEggBox();         if (failed) yield break;
        yield return Step3_OpenBox();           if (failed) yield break;
        yield return Step4_PlaceIncubator();    if (failed) yield break;
        yield return Step5_EggsIntoIncubator(); if (failed) yield break;
        yield return Step6_HatchThree();        if (failed) yield break;
        yield return Step7_Departure();         if (failed) yield break;
        yield return Step8_ArenaRun();          if (failed) yield break;
        yield return Step9_Return();            if (failed) yield break;
        yield return Step10_HatchRemaining();   if (failed) yield break;
        Step11_Fin();
        running = false;
    }

    private IEnumerator Step1_Arrival()
    {
        currentStep = 1;

        var cloud = FindFirstObjectByType<CloudSyncService>();
        yield return WaitFor(() => cloud != null && cloud.StartupSyncDone, stepTimeout, "CloudSyncService.StartupSyncDone");
        if (failed) yield break;

        yield return WaitFor(() => GameManager.Instance != null && GameManager.Instance.WorldState != null && GameManager.Instance.WorldState.TutorialStep >= 1,
            stepTimeout, "TutorialStep >= 1 (kit inicial aplicado)");
        if (failed) yield break;

        int hatchCost = BreedingController.Instance != null ? BreedingController.Instance.EggHatchCost : 0;
        int minerita  = Wallet.Balance(Currency.Minerita);
        if (minerita < 3 * hatchCost) { Fail($"Minerita insuficiente: {minerita} < {3 * hatchCost}"); yield break; }

        var incubatorDef = FindIncubatorFurnitureDefinition();
        var inventory    = GameManager.CurrentInventory;
        if (incubatorDef == null || inventory == null || !inventory.HasFurniture(incubatorDef.Id))
        {
            Fail("El inventario no posee el mueble incubadora del kit inicial");
            yield break;
        }

        Ok("Llegada", $"minerita={minerita} hatchCost={hatchCost} incubadora={incubatorDef.Id}");
    }

    private IEnumerator Step2_BuyEggBox()
    {
        currentStep = 2;

        var store = FindFirstObjectByType<StoreManager>();
        if (store == null || store.Catalog == null) { Fail("No hay StoreManager/Catalog en escena"); yield break; }

        ShopCatalogSO.CreatureBoxListing listing = null;
        foreach (var l in store.Catalog.CreatureBoxListings)
            if (l != null && l.Box != null && l.Box.Form == MonchiForm.Egg) { listing = l; break; }

        if (listing == null) { Fail("No hay caja de huevos en el catalogo"); yield break; }

        int price = store.CreatureBoxPrice(listing.Box, listing.Shop);
        if (price != 0) { Fail($"Precio de la caja de huevos debia ser 0, es {price}"); yield break; }

        var result = store.BuyCreatureBox(listing.Box, listing.Shop);
        if (result != BuyResult.Success) { Fail($"BuyCreatureBox devolvio {result}"); yield break; }

        Ok("Compra caja de huevos", $"box={listing.Box.Id} precio={price}");
    }

    private IEnumerator Step3_OpenBox()
    {
        currentStep = 3;

        DeliveryBox box = null;
        yield return WaitFor(() => (box = FindFirstObjectByType<DeliveryBox>()) != null, stepTimeout, "DeliveryBox en escena");
        if (failed) yield break;

        var registry = GameManager.Instance.Registry;
        var before   = new HashSet<string>(registry.GetAll().Keys);

        box.Interact();

        yield return WaitFor(() => CountFormNotIn(MonchiForm.Egg, before) >= 5, stepTimeout, "5 huevos en el registro");
        if (failed) yield break;

        eggIds.Clear();
        foreach (var kv in registry.GetAll())
            if (!before.Contains(kv.Key) && kv.Value.Form == MonchiForm.Egg) eggIds.Add(kv.Key);

        yield return WaitFor(() => AllControllersSpawned(eggIds), stepTimeout, "controllers de los 5 huevos spawneados");
        if (failed) yield break;

        Ok("Abrir caja", $"huevos={eggIds.Count}");
    }

    private IEnumerator Step4_PlaceIncubator()
    {
        currentStep = 4;

        var furnitureService = FindFirstObjectByType<FurnitureService>();
        var grid              = FindFirstObjectByType<PlacementGrid>();
        if (furnitureService == null || grid == null) { Fail("No hay FurnitureService/PlacementGrid en escena"); yield break; }

        var def = FindIncubatorFurnitureDefinition();
        if (def == null) { Fail("No se encontro la FurnitureDefinitionSO de la incubadora"); yield break; }

        bool placed = false;
        foreach (var cell in SpiralCells(Vector2Int.zero, 25))
        {
            if (furnitureService.TryPlace(def, cell, 0)) { placed = true; break; }
        }
        if (!placed) { Fail("No se pudo colocar la incubadora en ninguna celda libre"); yield break; }

        yield return WaitFor(() => FindFirstObjectByType<IncubatorContainer>() != null, stepTimeout, "IncubatorContainer en escena");
        if (failed) yield break;

        Ok("Colocar incubadora", $"def={def.Id}");
    }

    private IEnumerator Step5_EggsIntoIncubator()
    {
        currentStep = 5;

        var incubator = FindFirstObjectByType<IncubatorContainer>();
        if (incubator == null) { Fail("No hay IncubatorContainer en escena"); yield break; }

        var spawner = MoriMochiSpawner.Instance;
        if (spawner == null) { Fail("No hay MoriMochiSpawner activo"); yield break; }

        foreach (var id in eggIds)
        {
            if (!TryFindController(spawner, id, out var controller) || controller == null)
            {
                Fail($"No se encontro el controller del huevo {id}");
                yield break;
            }
            controller.Launch(incubator.Center + Vector3.up * 1.2f, Vector3.down * 1f);
            yield return new WaitForSecondsRealtime(0.3f);
        }

        yield return WaitFor(() => CountOccupantsAmong(incubator, eggIds) >= eggIds.Count, stepTimeout, "5 huevos dentro de la incubadora");
        if (failed) yield break;

        Ok("Huevos a la incubadora", $"ocupantes={incubator.Occupants.Count}");
    }

    private IEnumerator Step6_HatchThree()
    {
        currentStep = 6;

        var incubator = FindFirstObjectByType<IncubatorContainer>();
        if (incubator == null) { Fail("No hay IncubatorContainer en escena"); yield break; }

        for (int i = 0; i < 3; i++)
        {
            incubator.Interact();
            yield return new WaitForSecondsRealtime(0.3f);
        }

        int slimes    = CountForm(MonchiForm.Slime, eggIds);
        int eggsLeft  = CountForm(MonchiForm.Egg, eggIds);
        if (slimes != 3 || eggsLeft != 2) { Fail($"Tras 3 eclosiones: slimes={slimes} huevos={eggsLeft} (esperado 3/2)"); yield break; }

        incubator.Interact();
        yield return new WaitForSecondsRealtime(0.3f);

        eggsLeft = CountForm(MonchiForm.Egg, eggIds);
        if (eggsLeft != 2) { Fail($"El 4to Interact eclosiono igual (huevos restantes={eggsLeft}, esperado 2)"); yield break; }

        Ok("Eclosionar 3", $"slimes={slimes} huevosRestantes={eggsLeft}");
    }

    private IEnumerator Step7_Departure()
    {
        currentStep = 7;

        var registry = GameManager.Instance.Registry;
        slimeIds = eggIds.Where(id => registry.TryGet(id, out var dna) && dna != null && dna.Form == MonchiForm.Slime).ToList();
        if (slimeIds.Count != 3) { Fail($"Se esperaban 3 slimes, hay {slimeIds.Count}"); yield break; }

        lastExpeditionReturn = null;
        ExpeditionBridge.RequestDeparture(slimeIds);

        yield return WaitFor(() => SceneManager.GetActiveScene().name == ExpeditionHandoff.ArenaScene, stepTimeout, "escena ArenaSandbox");
        if (failed) yield break;

        Ok("Bajada a la arena", $"ids={string.Join(",", slimeIds)}");
    }

    private IEnumerator Step8_ArenaRun()
    {
        currentStep = 8;
        Time.timeScale = arenaTimeScale;

        ArenaRound      round    = null;
        ArenaRunDirector director = null;
        yield return WaitFor(() =>
        {
            round    = FindFirstObjectByType<ArenaRound>();
            director = FindFirstObjectByType<ArenaRunDirector>();
            return round != null && director != null;
        }, stepTimeout, "ArenaRound/ArenaRunDirector en escena");
        if (failed) { Time.timeScale = 1f; yield break; }

        if (!round.IsRunning && !round.IsOver) round.Launch();

        yield return WaitFor(() => director.FloorRecorded, 240f, "director.FloorRecorded");
        if (failed) { Time.timeScale = 1f; yield break; }

        int  material = director.Run.Material;
        bool lost     = director.Run.Lost;
        Debug.Log($"[AutoPlayer] paso 8 · piso registrado · material={material} perdida={lost}");

        director.Retreat();

        Ok("Piso jugado", $"material={material} perdida={lost}");
    }

    private IEnumerator Step9_Return()
    {
        currentStep = 9;

        yield return WaitFor(() => SceneManager.GetActiveScene().name == ExpeditionHandoff.StoreScene && lastExpeditionReturn.HasValue,
            stepTimeout, "vuelta a GameScene + OnExpeditionReturned");
        if (failed) yield break;

        Time.timeScale = 1f;

        var result   = lastExpeditionReturn.Value;
        var registry = GameManager.Instance.Registry;

        if (!result.Lost)
        {
            foreach (var id in slimeIds)
            {
                if (!registry.TryGet(id, out var dna) || dna == null || dna.IsDead) continue;
                if (dna.Explorations != 1) { Fail($"{id} tiene Explorations={dna.Explorations}, esperado 1"); yield break; }
            }
        }

        Ok("Vuelta a la tienda", $"perdida={result.Lost} minerita={Wallet.Balance(Currency.Minerita)}");
    }

    private IEnumerator Step10_HatchRemaining()
    {
        currentStep = 10;

        var registry = GameManager.Instance.Registry;
        var remaining = eggIds.Where(id => registry.TryGet(id, out var dna) && dna != null && dna.Form == MonchiForm.Egg).ToList();

        IncubatorContainer incubator = null;
        yield return WaitFor(() =>
        {
            incubator = FindFirstObjectByType<IncubatorContainer>();
            return incubator != null && CountOccupantsAmong(incubator, remaining) >= remaining.Count;
        }, stepTimeout, "huevos persistidos de vuelta en la incubadora");
        if (failed) yield break;

        int cost     = BreedingController.Instance != null ? BreedingController.Instance.EggHatchCost : 0;
        int minerita = Wallet.Balance(Currency.Minerita);
        if (minerita < 2 * cost) { Fail($"Minerita insuficiente para eclosionar los 2 restantes: {minerita} < {2 * cost}"); yield break; }

        incubator.Interact();
        yield return new WaitForSecondsRealtime(0.3f);
        incubator.Interact();
        yield return new WaitForSecondsRealtime(0.3f);

        int eggsLeft = CountForm(MonchiForm.Egg, remaining);
        if (eggsLeft != 0) { Fail($"Quedan {eggsLeft} huevos tras eclosionar los 2 restantes"); yield break; }

        Ok("Eclosionar restantes", "huevos=0");
    }

    private void Step11_Fin()
    {
        currentStep = 11;
        Status = "FIN tanda 1";
        Debug.Log("[AutoPlayer] FIN tanda 1");
    }

    private IEnumerator WaitFor(Func<bool> condition, float timeout, string what)
    {
        float elapsed = 0f;
        while (!condition())
        {
            if (elapsed >= timeout) { Fail($"{what} (timeout {timeout}s)"); yield break; }
            elapsed += Time.unscaledDeltaTime;
            yield return null;
        }
    }

    private void Fail(string reason)
    {
        failed  = true;
        running = false;
        Status  = $"FALLA paso {currentStep} · {reason}";
        Time.timeScale = 1f;
        Debug.LogError($"[AutoPlayer] FALLA paso {currentStep} · {reason}");
        Debug.Break();
    }

    private void Ok(string name, string data)
    {
        Status = $"OK paso {currentStep} · {name} · {data}";
        Debug.Log($"[AutoPlayer] OK paso {currentStep} · {name} · {data}");
    }

    private static FurnitureDefinitionSO FindIncubatorFurnitureDefinition()
    {
        var database = Resources.FindObjectsOfTypeAll<FurnitureDatabaseSO>().FirstOrDefault();
        if (database == null) return null;
        foreach (var def in database.All)
            if (def != null && def.Prefab != null && def.Prefab.GetComponent<IncubatorContainer>() != null)
                return def;
        return null;
    }

    private static bool TryFindController(MoriMochiSpawner spawner, string id, out MoriMonchiController controller)
    {
        foreach (var kv in spawner.SpawnedEntries)
        {
            if (kv.Key != id) continue;
            controller = kv.Value;
            return true;
        }
        controller = null;
        return false;
    }

    private static bool AllControllersSpawned(List<string> ids)
    {
        var spawner = MoriMochiSpawner.Instance;
        if (spawner == null) return false;
        foreach (var id in ids)
            if (!TryFindController(spawner, id, out _)) return false;
        return true;
    }

    private static int CountFormNotIn(MonchiForm form, HashSet<string> exclude)
    {
        var registry = GameManager.Instance != null ? GameManager.Instance.Registry : null;
        if (registry == null) return 0;
        int count = 0;
        foreach (var kv in registry.GetAll())
            if (!exclude.Contains(kv.Key) && kv.Value.Form == form) count++;
        return count;
    }

    private static int CountForm(MonchiForm form, List<string> ids)
    {
        var registry = GameManager.Instance != null ? GameManager.Instance.Registry : null;
        if (registry == null) return 0;
        int count = 0;
        foreach (var id in ids)
            if (registry.TryGet(id, out var dna) && dna != null && dna.Form == form) count++;
        return count;
    }

    private static int CountOccupantsAmong(IncubatorContainer incubator, List<string> ids)
    {
        int count = 0;
        foreach (var agent in incubator.Occupants)
            if (agent != null && agent.DNA != null && ids.Contains(agent.DNA.UniqueID) && !string.IsNullOrEmpty(agent.DNA.LocationKey))
                count++;
        return count;
    }

    private static IEnumerable<Vector2Int> SpiralCells(Vector2Int center, int maxRadius)
    {
        yield return center;
        for (int r = 1; r <= maxRadius; r++)
        {
            for (int x = -r; x <= r; x++)
            {
                yield return new Vector2Int(center.x + x, center.y - r);
                yield return new Vector2Int(center.x + x, center.y + r);
            }
            for (int y = -r + 1; y <= r - 1; y++)
            {
                yield return new Vector2Int(center.x - r, center.y + y);
                yield return new Vector2Int(center.x + r, center.y + y);
            }
        }
    }
}
}
