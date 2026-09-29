using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace MoriMonchiSimulator
{

internal class AutoPlayerOpeningSteps
{
    private readonly AutoPlayer core;

    public AutoPlayerOpeningSteps(AutoPlayer core)
    {
        this.core = core;
    }

    public IEnumerator Step1_Arrival()
    {
        core.CurrentStep = 1;

        var cloud = Object.FindFirstObjectByType<CloudSyncService>();
        yield return core.WaitFor(() => cloud != null && cloud.StartupSyncDone, core.StepTimeout, "CloudSyncService.StartupSyncDone");
        if (core.Failed) yield break;

        yield return core.WaitFor(() => GameManager.Instance != null && GameManager.Instance.WorldState != null && GameManager.Instance.WorldState.TutorialStep >= 1,
            core.StepTimeout, "TutorialStep >= 1 (kit inicial aplicado)");
        if (core.Failed) yield break;

        int hatchCost = BreedingController.Instance != null ? BreedingController.Instance.EggHatchCost : 0;
        int minerita  = Wallet.Balance(Currency.Minerita);
        if (minerita < 3 * hatchCost) { core.Fail($"Minerita insuficiente: {minerita} < {3 * hatchCost}"); yield break; }

        var incubatorDef = AutoPlayerQuery.FindFurnitureDefinition<IncubatorContainer>();
        var inventory    = GameManager.CurrentInventory;
        if (incubatorDef == null || inventory == null || !inventory.HasFurniture(incubatorDef.Id))
        {
            core.Fail("El inventario no posee el mueble incubadora del kit inicial");
            yield break;
        }

        core.Ok("Llegada", $"minerita={minerita} hatchCost={hatchCost} incubadora={incubatorDef.Id}");
    }

    public IEnumerator Step2_BuyEggBox()
    {
        core.CurrentStep = 2;

        var store = Object.FindFirstObjectByType<StoreManager>();
        if (store == null || store.Catalog == null) { core.Fail("No hay StoreManager/Catalog en escena"); yield break; }

        ShopCatalogSO.CreatureBoxListing listing = null;
        foreach (var l in store.Catalog.CreatureBoxListings)
            if (l != null && l.Box != null && l.Box.Form == MonchiForm.Egg) { listing = l; break; }

        if (listing == null) { core.Fail("No hay caja de huevos en el catalogo"); yield break; }

        int price = store.CreatureBoxPrice(listing.Box, listing.Shop);
        if (price != 0) { core.Fail($"Precio de la caja de huevos debia ser 0, es {price}"); yield break; }

        var result = store.BuyCreatureBox(listing.Box, listing.Shop);
        if (result != BuyResult.Success) { core.Fail($"BuyCreatureBox devolvio {result}"); yield break; }

        core.Ok("Compra caja de huevos", $"box={listing.Box.Id} precio={price}");
    }

    public IEnumerator Step3_OpenBox()
    {
        core.CurrentStep = 3;

        DeliveryBox box = null;
        yield return core.WaitFor(() => (box = Object.FindFirstObjectByType<DeliveryBox>()) != null, core.StepTimeout, "DeliveryBox en escena");
        if (core.Failed) yield break;

        var registry = GameManager.Instance.Registry;
        var before   = new HashSet<string>(registry.GetAll().Keys);

        box.Interact();

        yield return core.WaitFor(() => AutoPlayerQuery.CountFormNotIn(MonchiForm.Egg, before) >= 5, core.StepTimeout, "5 huevos en el registro");
        if (core.Failed) yield break;

        core.EggIds.Clear();
        foreach (var kv in registry.GetAll())
            if (!before.Contains(kv.Key) && kv.Value.Form == MonchiForm.Egg) core.EggIds.Add(kv.Key);

        yield return core.WaitFor(() => AutoPlayerQuery.AllControllersSpawned(core.EggIds), core.StepTimeout, "controllers de los 5 huevos spawneados");
        if (core.Failed) yield break;

        core.Ok("Abrir caja", $"huevos={core.EggIds.Count}");
    }

    public IEnumerator Step4_PlaceIncubator()
    {
        core.CurrentStep = 4;

        var furnitureService = Object.FindFirstObjectByType<FurnitureService>();
        var grid             = Object.FindFirstObjectByType<PlacementGrid>();
        if (furnitureService == null || grid == null) { core.Fail("No hay FurnitureService/PlacementGrid en escena"); yield break; }

        var def = AutoPlayerQuery.FindFurnitureDefinition<IncubatorContainer>();
        if (def == null) { core.Fail("No se encontro la FurnitureDefinitionSO de la incubadora"); yield break; }

        if (!AutoPlayerQuery.TryPlaceInSpiral(furnitureService, def)) { core.Fail("No se pudo colocar la incubadora en ninguna celda libre"); yield break; }

        yield return core.WaitFor(() => Object.FindFirstObjectByType<IncubatorContainer>() != null, core.StepTimeout, "IncubatorContainer en escena");
        if (core.Failed) yield break;

        core.Ok("Colocar incubadora", $"def={def.Id}");
    }

    public IEnumerator Step5_EggsIntoIncubator()
    {
        core.CurrentStep = 5;

        var incubator = Object.FindFirstObjectByType<IncubatorContainer>();
        if (incubator == null) { core.Fail("No hay IncubatorContainer en escena"); yield break; }

        var spawner = MoriMochiSpawner.Instance;
        if (spawner == null) { core.Fail("No hay MoriMochiSpawner activo"); yield break; }

        foreach (var id in core.EggIds)
        {
            if (!AutoPlayerQuery.TryFindController(spawner, id, out var controller) || controller == null)
            {
                core.Fail($"No se encontro el controller del huevo {id}");
                yield break;
            }
            controller.Launch(incubator.Center + Vector3.up * 1.2f, Vector3.down * 1f);
            yield return new WaitForSecondsRealtime(0.3f);
        }

        yield return core.WaitFor(() => AutoPlayerQuery.CountOccupantsAmong(incubator, core.EggIds) >= core.EggIds.Count, core.StepTimeout, "5 huevos dentro de la incubadora");
        if (core.Failed) yield break;

        core.Ok("Huevos a la incubadora", $"ocupantes={incubator.Occupants.Count}");
    }

    public IEnumerator Step6_HatchThree()
    {
        core.CurrentStep = 6;

        var incubator = Object.FindFirstObjectByType<IncubatorContainer>();
        if (incubator == null) { core.Fail("No hay IncubatorContainer en escena"); yield break; }

        for (int i = 0; i < 3; i++)
        {
            incubator.Interact();
            yield return new WaitForSecondsRealtime(0.3f);
        }

        int slimes   = AutoPlayerQuery.CountForm(MonchiForm.Slime, core.EggIds);
        int eggsLeft = AutoPlayerQuery.CountForm(MonchiForm.Egg, core.EggIds);
        if (slimes != 3 || eggsLeft != 2) { core.Fail($"Tras 3 eclosiones: slimes={slimes} huevos={eggsLeft} (esperado 3/2)"); yield break; }

        incubator.Interact();
        yield return new WaitForSecondsRealtime(0.3f);

        eggsLeft = AutoPlayerQuery.CountForm(MonchiForm.Egg, core.EggIds);
        if (eggsLeft != 2) { core.Fail($"El 4to Interact eclosiono igual (huevos restantes={eggsLeft}, esperado 2)"); yield break; }

        core.Ok("Eclosionar 3", $"slimes={slimes} huevosRestantes={eggsLeft}");
    }

    public IEnumerator Step7to9_Expedition()
    {
        core.CurrentStep = 7;

        var registry = GameManager.Instance.Registry;
        core.SlimeIds = core.EggIds.Where(id => registry.TryGet(id, out var dna) && dna != null && dna.Form == MonchiForm.Slime).ToList();
        if (core.SlimeIds.Count != 3) { core.Fail($"Se esperaban 3 slimes, hay {core.SlimeIds.Count}"); yield break; }

        yield return core.PlayExpedition(core.SlimeIds);
        if (core.Failed) yield break;

        core.CurrentStep = 9;

        var result = core.LastExpeditionReturn.Value;

        if (!result.Lost)
        {
            foreach (var id in core.SlimeIds)
            {
                if (!registry.TryGet(id, out var dna) || dna == null || dna.IsDead) continue;
                if (dna.Explorations != 1) { core.Fail($"{id} tiene Explorations={dna.Explorations}, esperado 1"); yield break; }
            }
        }

        core.Ok("Bajada y vuelta", $"ids={string.Join(",", core.SlimeIds)} material={core.LastRunMaterial} perdida={result.Lost} minerita={Wallet.Balance(Currency.Minerita)}");
    }

    public IEnumerator Step10_HatchRemaining()
    {
        core.CurrentStep = 10;

        var registry  = GameManager.Instance.Registry;
        var remaining = core.EggIds.Where(id => registry.TryGet(id, out var dna) && dna != null && dna.Form == MonchiForm.Egg).ToList();

        int cost = BreedingController.Instance != null ? BreedingController.Instance.EggHatchCost : 0;

        yield return core.ExpeditionsUntil(() => Wallet.Balance(Currency.Minerita) >= 2 * cost, 5, "Minerita para eclosionar los 2 restantes");
        if (core.Failed) yield break;

        IncubatorContainer incubator = null;
        yield return core.WaitFor(() =>
        {
            incubator = Object.FindFirstObjectByType<IncubatorContainer>();
            return incubator != null && AutoPlayerQuery.CountOccupantsAmong(incubator, remaining) >= remaining.Count;
        }, core.StepTimeout, "huevos persistidos de vuelta en la incubadora");
        if (core.Failed) yield break;

        int minerita = Wallet.Balance(Currency.Minerita);
        if (minerita < 2 * cost) { core.Fail($"Minerita insuficiente para eclosionar los 2 restantes: {minerita} < {2 * cost}"); yield break; }

        incubator.Interact();
        yield return new WaitForSecondsRealtime(0.3f);
        incubator.Interact();
        yield return new WaitForSecondsRealtime(0.3f);

        int eggsLeft = AutoPlayerQuery.CountForm(MonchiForm.Egg, remaining);
        if (eggsLeft != 0) { core.Fail($"Quedan {eggsLeft} huevos tras eclosionar los 2 restantes"); yield break; }

        core.Ok("Eclosionar restantes", "huevos=0");
    }
}
}
