using System.Collections;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace MoriMonchiSimulator
{

internal class AutoPlayerLoopSteps
{
    private const int   MaxExpeditions   = 15;
    private const int   MaxClockAdvances = 4;
    private const float LongTimeout      = 180f;

    private readonly AutoPlayer core;

    private string motherId;
    private string fatherId;

    public AutoPlayerLoopSteps(AutoPlayer core)
    {
        this.core = core;
    }

    private static CreatureDNA Get(string id) =>
        GameManager.Instance != null && GameManager.Instance.Registry != null && GameManager.Instance.Registry.TryGet(id, out var dna) ? dna : null;

    public IEnumerator Step11_BuyBreedingRoom()
    {
        core.CurrentStep = 11;

        if (Object.FindFirstObjectByType<BreedingContainer>() != null)
        {
            core.Ok("Breeding room ya colocada", "se reutiliza el corral existente");
            yield break;
        }

        var store = Object.FindFirstObjectByType<StoreManager>();
        if (store == null || store.Catalog == null) { core.Fail("No hay StoreManager/Catalog en escena"); yield break; }

        ShopCatalogSO.FurnitureListing listing = null;
        foreach (var l in store.Catalog.FurnitureListings)
            if (l != null && l.Furniture != null && l.Furniture.Prefab != null && l.Furniture.Prefab.GetComponent<BreedingContainer>() != null) { listing = l; break; }

        if (listing == null) { core.Fail("No hay breeding room en el catalogo"); yield break; }
        if (listing.Shop.Currency != Currency.Minerita) { core.Fail($"La breeding room se cobra en {listing.Shop.Currency}, esperado Minerita"); yield break; }

        int day   = GameClock.Instance != null ? GameClock.Instance.Day : 1;
        int price = store.Catalog.FinalPrice(listing.Shop, day);

        if (Wallet.Balance(Currency.Minerita) < price)
        {
            yield return core.ExpeditionsUntil(() => Wallet.Balance(Currency.Minerita) >= price, 5, "Minerita para la breeding room");
            if (core.Failed) yield break;

            yield return core.WaitFor(() => (store = Object.FindFirstObjectByType<StoreManager>()) != null && store.Catalog != null, core.StepTimeout, "StoreManager tras la bajada");
            if (core.Failed) yield break;

            day   = GameClock.Instance != null ? GameClock.Instance.Day : 1;
            price = store.Catalog.FinalPrice(listing.Shop, day);
        }

        int balance = Wallet.Balance(Currency.Minerita);
        if (balance < price) { core.Fail($"Minerita insuficiente para la breeding room: {balance} < {price}"); yield break; }

        var result = store.BuyFurniture(listing.Furniture, listing.Shop);
        if (result != BuyResult.Success) { core.Fail($"BuyFurniture devolvio {result}"); yield break; }

        int after = Wallet.Balance(Currency.Minerita);
        if (balance - after != price) { core.Fail($"La Minerita bajo {balance - after}, esperado {price}"); yield break; }

        var inventory = GameManager.CurrentInventory;
        if (inventory == null || !inventory.HasFurniture(listing.Furniture.Id)) { core.Fail("El inventario no posee la breeding room comprada"); yield break; }

        var furnitureService = Object.FindFirstObjectByType<FurnitureService>();
        if (furnitureService == null) { core.Fail("No hay FurnitureService en escena"); yield break; }
        if (!AutoPlayerQuery.TryPlaceInSpiral(furnitureService, listing.Furniture)) { core.Fail("No se pudo colocar la breeding room en ninguna celda libre"); yield break; }

        yield return core.WaitFor(() => Object.FindFirstObjectByType<BreedingContainer>() != null, core.StepTimeout, "BreedingContainer en escena");
        if (core.Failed) yield break;

        core.Ok("Comprar breeding room", $"def={listing.Furniture.Id} precio={price} minerita={after}");
    }

    public IEnumerator Step12_ExpeditionsUntilPair()
    {
        core.CurrentStep = 12;

        yield return core.ExpeditionsUntil(() => AutoPlayerQuery.TryFindAdultPair(GameManager.Instance.Registry, out _, out _), MaxExpeditions, "Sin pareja adulta");
        if (core.Failed) yield break;

        AutoPlayerQuery.TryFindAdultPair(GameManager.Instance.Registry, out var mother, out var father);
        motherId = mother.UniqueID;
        fatherId = father.UniqueID;

        core.Ok("Pareja adulta", $"madre={motherId} padre={fatherId} bajadas={core.TotalExpeditions} minerita={Wallet.Balance(Currency.Minerita)}");
    }

    public IEnumerator Step13_Breed()
    {
        core.CurrentStep = 13;

        var pairIds = new List<string> { motherId, fatherId };

        var breedingController = BreedingController.Instance;
        if (breedingController == null || breedingController.Incubation == null) { core.Fail("No hay BreedingController.Incubation"); yield break; }

        int hatchCost = breedingController.Incubation.HatchCostFor(motherId, fatherId);
        yield return core.ExpeditionsUntil(() => Wallet.Balance(Currency.Minerita) >= hatchCost, 5, "Minerita para eclosionar la cria", pairIds);
        if (core.Failed) yield break;

        yield return core.WaitFor(() => AutoPlayerQuery.AllControllersSpawned(pairIds), core.StepTimeout, "controllers de la pareja spawneados");
        if (core.Failed) yield break;

        BreedingContainer pen = null;
        yield return core.WaitFor(() => (pen = Object.FindFirstObjectByType<BreedingContainer>()) != null, core.StepTimeout, "BreedingContainer en escena");
        if (core.Failed) yield break;

        var spawner = MoriMochiSpawner.Instance;
        if (spawner == null) { core.Fail("No hay MoriMochiSpawner activo"); yield break; }

        string foreign = AutoPlayerQuery.DescribeForeignOccupants(pen, pairIds);

        foreach (var id in pairIds)
        {
            if (AutoPlayerQuery.CountOccupantsAmong(pen, new List<string> { id }) > 0) continue;
            if (!AutoPlayerQuery.TryFindController(spawner, id, out var controller) || controller == null)
            {
                core.Fail($"No se encontro el controller de {id}");
                yield break;
            }
            controller.Launch(pen.Center + Vector3.up * 1.2f, Vector3.down);
            yield return new WaitForSecondsRealtime(0.3f);
        }

        yield return core.WaitFor(() => AutoPlayerQuery.CountOccupantsAmong(pen, pairIds) >= 2, core.StepTimeout, $"pareja dentro del corral de cria (ocupantes ajenos: {foreign})");
        if (core.Failed) yield break;

        yield return core.WaitFor(() =>
        {
            var m = Get(motherId);
            var f = Get(fatherId);
            return m != null && f != null && m.BusyState == BusyReason.Breeding && f.BusyState == BusyReason.Breeding;
        }, LongTimeout, "cria iniciada (ambos busy por breeding)");
        if (core.Failed) yield break;

        var breeding = BreedingController.Instance;
        var incubation = breeding != null ? breeding.Incubation : null;
        var clock = GameClock.Instance;
        if (incubation == null || clock == null) { core.Fail("No hay BreedingController.Incubation/GameClock"); yield break; }

        int advances = 0;
        while (!incubation.IsReady(Get(motherId)) && advances < MaxClockAdvances)
        {
            clock.AdvanceToNextBlock();
            advances++;
            yield return null;
        }
        if (!incubation.IsReady(Get(motherId))) { core.Fail($"El huevo no esta listo tras {advances} avances de bloque"); yield break; }

        int cost     = incubation.HatchCostFor(motherId, fatherId);
        int minerita = Wallet.Balance(Currency.Minerita);
        if (minerita < cost) { core.Fail($"Minerita insuficiente para eclosionar la cria: saldo={minerita} costo={cost}"); yield break; }

        core.LastChild = null;
        pen.Interact();

        yield return core.WaitFor(() => core.LastChild != null, core.StepTimeout, "OnBreedingCompleted");
        if (core.Failed) yield break;

        var child = Get(core.LastChild.UniqueID);
        if (child == null) { core.Fail("El hijo no quedo registrado"); yield break; }
        if (child.Form != MonchiForm.Slime) { core.Fail($"El hijo tiene Form={child.Form}, esperado Slime"); yield break; }

        int after = Wallet.Balance(Currency.Minerita);
        if (minerita - after != cost) { core.Fail($"La Minerita bajo {minerita - after}, esperado {cost}"); yield break; }

        core.Ok("Criar", $"hijo={child.UniqueID} genero={child.Gender} costo={cost} minerita={after} avancesBloque={advances} ocupantesAjenos={foreign}");
    }

    public IEnumerator Step14_Showcase()
    {
        core.CurrentStep = 14;

        var def = AutoPlayerQuery.FindFurnitureDefinition<StoreContainer>();
        if (def == null) { core.Fail("No hay definicion de vitrina en la FurnitureDatabase"); yield break; }

        StoreContainer display = AutoPlayer.ResumeFromStep > 1 ? Object.FindFirstObjectByType<StoreContainer>() : null;

        if (display == null)
        {
            var inventory = GameManager.CurrentInventory;
            if (inventory == null || !inventory.HasFurniture(def.Id)) { core.Fail("La vitrina no esta en el kit"); yield break; }

            var furnitureService = Object.FindFirstObjectByType<FurnitureService>();
            if (furnitureService == null) { core.Fail("No hay FurnitureService en escena"); yield break; }

            var existing = new HashSet<StoreContainer>(Object.FindObjectsByType<StoreContainer>(FindObjectsSortMode.None));

            var grid = Object.FindFirstObjectByType<PlacementGrid>();
            if (grid == null) { core.Fail("No hay PlacementGrid en escena"); yield break; }

            int customerMask = AutoPlayerQuery.CustomerAreaMask();
            var register = CashRegister.Instance;
            Vector2Int? searchCenter = register != null ? grid.WorldToCell(register.transform.position) : (Vector2Int?)null;

            bool rebaked = false;
            System.Action onRebaked = () => rebaked = true;
            GameEvents.OnNavMeshRebaked += onRebaked;

            bool placed = AutoPlayerQuery.TryPlaceInSpiral(furnitureService, def,
                cell => AutoPlayerQuery.CellReachableByCustomers(grid, cell, def.Footprint, customerMask)
                        && (register == null || Vector3.Distance(grid.FootprintCenter(cell, def.Footprint, 0), register.transform.position) >= 7f),
                searchCenter, 40);
            if (!placed)
            {
                GameEvents.OnNavMeshRebaked -= onRebaked;
                core.Fail("No se pudo colocar la vitrina en ninguna celda libre alcanzable por clientes");
                yield break;
            }

            yield return core.WaitFor(() => (display = Object.FindObjectsByType<StoreContainer>(FindObjectsSortMode.None).FirstOrDefault(s => !existing.Contains(s))) != null,
                core.StepTimeout, "StoreContainer nuevo en escena");
            if (core.Failed) { GameEvents.OnNavMeshRebaked -= onRebaked; yield break; }

            float waited = 0f;
            while (!rebaked && waited < 3f)
            {
                waited += Time.unscaledDeltaTime;
                yield return null;
            }
            GameEvents.OnNavMeshRebaked -= onRebaked;

            if (!AutoPlayerQuery.IsReachableFromRegister(display.Center, customerMask))
            {
                core.Fail($"La vitrina en la celda {grid.WorldToCell(display.Center)} no es alcanzable por los clientes desde la caja");
                yield break;
            }
        }

        var registry = GameManager.Instance.Registry;
        var sellable = AutoPlayerQuery.PickSellable(registry, new List<string> { motherId, fatherId }, core.LastChild != null ? core.LastChild.UniqueID : null);
        if (sellable == null) { core.Fail("No hay criatura vendible fuera de la pareja"); yield break; }

        var sellableIds = new List<string> { sellable.UniqueID };
        yield return core.WaitFor(() => AutoPlayerQuery.AllControllersSpawned(sellableIds), core.StepTimeout, "controller de la criatura a vender spawneado");
        if (core.Failed) yield break;

        AutoPlayerQuery.TryFindController(MoriMochiSpawner.Instance, sellable.UniqueID, out var controller);
        if (controller == null) { core.Fail($"No se encontro el controller de {sellable.UniqueID}"); yield break; }

        controller.Launch(display.Center + Vector3.up * 1.2f, Vector3.down);

        yield return core.WaitFor(() => AutoPlayerQuery.CountOccupantsAmong(display, sellableIds) >= 1, core.StepTimeout, "criatura dentro de la vitrina");
        if (core.Failed) yield break;

        core.Ok("Vitrina", $"def={def.Id} criatura={sellable.UniqueID} form={sellable.Form}");
    }

    public IEnumerator Step15_Sale()
    {
        core.CurrentStep = 15;

        var clock = GameClock.Instance;
        if (clock == null) { core.Fail("No hay GameClock"); yield break; }

        int advances = 0;
        while ((clock.Block == null || !clock.Block.CustomersOpen) && advances < MaxClockAdvances)
        {
            clock.AdvanceToNextBlock();
            advances++;
            yield return null;
        }
        if (clock.Block == null || !clock.Block.CustomersOpen) { core.Fail($"No abrio el bloque de clientes tras {advances} avances"); yield break; }

        NpcAgent customer = null;
        yield return core.WaitFor(() =>
        {
            var register = CashRegister.Instance;
            customer = register != null ? register.CurrentCustomer : null;
            return customer != null && customer.TargetMM != null
                && (customer.State == NpcAgent.NpcState.WaitingAtRegister || customer.State == NpcAgent.NpcState.Negotiating);
        }, LongTimeout, "cliente en caja con oferta");
        if (core.Failed) yield break;

        int dabloonsBefore = Wallet.Balance(Currency.Dabloons);
        core.LastSoldDna = null;

        customer.AcceptCurrentOffer();

        yield return core.WaitFor(() => core.LastSoldDna != null, core.StepTimeout, "OnCustomerSold");
        if (core.Failed) yield break;

        int dabloonsAfter = Wallet.Balance(Currency.Dabloons);
        if (dabloonsAfter - dabloonsBefore != core.LastSalePrice) { core.Fail($"Dabloons subieron {dabloonsAfter - dabloonsBefore}, esperado {core.LastSalePrice}"); yield break; }
        if (!core.LastSoldDna.IsSold) { core.Fail($"La criatura {core.LastSoldDna.UniqueID} no quedo vendida"); yield break; }

        core.Ok("Venta", $"criatura={core.LastSoldDna.UniqueID} precio={core.LastSalePrice} dabloons={dabloonsAfter} avancesBloque={advances}");
    }

    public IEnumerator Step16_Upgrade()
    {
        core.CurrentStep = 16;

        var store = Object.FindFirstObjectByType<StoreManager>();
        if (store == null || store.Catalog == null) { core.Fail("No hay StoreManager/Catalog en escena"); yield break; }

        ShopUpgradeSO upgrade = null;
        foreach (var u in store.Catalog.UpgradeListings)
            if (u != null && !u.IsMaxed(u.CurrentLevel)) { upgrade = u; break; }

        if (upgrade == null) { core.Fail("No hay mejora disponible en el catalogo"); yield break; }

        int level   = upgrade.CurrentLevel;
        int price   = upgrade.PriceFor(level);
        int balance = Wallet.Balance(Currency.Dabloons);
        if (balance < price) { core.Fail($"Dabloons insuficientes para la mejora {upgrade.Id}: saldo={balance} precio={price}"); yield break; }

        var result = store.BuyUpgrade(upgrade);
        if (result != BuyResult.Success) { core.Fail($"BuyUpgrade devolvio {result}"); yield break; }

        int after = Wallet.Balance(Currency.Dabloons);
        if (balance - after != price) { core.Fail($"Los Dabloons bajaron {balance - after}, esperado {price}"); yield break; }
        if (upgrade.CurrentLevel != level + 1) { core.Fail($"El nivel de {upgrade.Id} es {upgrade.CurrentLevel}, esperado {level + 1}"); yield break; }

        core.Ok("Mejora", $"id={upgrade.Id} nivel={level}->{upgrade.CurrentLevel} precio={price} dabloons={balance}->{after}");
    }

    public void Step17_Fin()
    {
        core.CurrentStep = 17;
        core.Status = $"FIN tanda 2 · bajadas={core.TotalExpeditions} perdidas={core.LostExpeditions}";
        Debug.Log($"[AutoPlayer] FIN tanda 2 · bajadas={core.TotalExpeditions} perdidas={core.LostExpeditions}");
    }
}
}
