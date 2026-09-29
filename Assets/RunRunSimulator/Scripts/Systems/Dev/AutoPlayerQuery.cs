using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.AI;
namespace MoriMonchiSimulator
{

internal static class AutoPlayerQuery
{
    public static FurnitureDefinitionSO FindFurnitureDefinition<TComponent>() where TComponent : Component
    {
        var database = Resources.FindObjectsOfTypeAll<FurnitureDatabaseSO>().FirstOrDefault();
        if (database == null) return null;
        foreach (var def in database.All)
            if (def != null && def.Prefab != null && def.Prefab.GetComponent<TComponent>() != null)
                return def;
        return null;
    }

    public static bool TryFindController(MoriMochiSpawner spawner, string id, out MoriMonchiController controller)
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

    public static bool AllControllersSpawned(List<string> ids)
    {
        var spawner = MoriMochiSpawner.Instance;
        if (spawner == null) return false;
        foreach (var id in ids)
            if (!TryFindController(spawner, id, out _)) return false;
        return true;
    }

    public static int CountFormNotIn(MonchiForm form, HashSet<string> exclude)
    {
        var registry = GameManager.Instance != null ? GameManager.Instance.Registry : null;
        if (registry == null) return 0;
        int count = 0;
        foreach (var kv in registry.GetAll())
            if (!exclude.Contains(kv.Key) && kv.Value.Form == form) count++;
        return count;
    }

    public static int CountForm(MonchiForm form, List<string> ids)
    {
        var registry = GameManager.Instance != null ? GameManager.Instance.Registry : null;
        if (registry == null) return 0;
        int count = 0;
        foreach (var id in ids)
            if (registry.TryGet(id, out var dna) && dna != null && dna.Form == form) count++;
        return count;
    }

    public static int CountOccupantsAmong(MoriMochiContainer container, List<string> ids)
    {
        int count = 0;
        foreach (var agent in container.Occupants)
            if (agent != null && agent.DNA != null && ids.Contains(agent.DNA.UniqueID) && !string.IsNullOrEmpty(agent.DNA.LocationKey))
                count++;
        return count;
    }

    public static string DescribeForeignOccupants(MoriMochiContainer container, List<string> ids)
    {
        var parts = new List<string>();
        foreach (var agent in container.Occupants)
            if (agent != null && agent.DNA != null && !ids.Contains(agent.DNA.UniqueID))
                parts.Add($"{agent.DNA.UniqueID}({agent.DNA.Form})");
        return parts.Count == 0 ? "ninguno" : string.Join(",", parts);
    }

    public static IEnumerable<Vector2Int> SpiralCells(Vector2Int center, int maxRadius)
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

    public static bool TryPlaceInSpiral(FurnitureService service, FurnitureDefinitionSO def, Func<Vector2Int, bool> cellFilter = null, Vector2Int? center = null, int maxRadius = 25)
    {
        foreach (var cell in SpiralCells(center ?? Vector2Int.zero, maxRadius))
        {
            if (cellFilter != null && !cellFilter(cell)) continue;
            if (service.TryPlace(def, cell, 0)) return true;
        }
        return false;
    }

    public static int CustomerAreaMask()
    {
        int mask = 0;
        foreach (var areaName in new[] { "ShopFrontDesk", "Outside" })
        {
            int idx = NavMesh.GetAreaFromName(areaName);
            if (idx >= 0) mask |= 1 << idx;
        }
        return mask != 0 ? mask : NavMesh.AllAreas;
    }

    public static bool CellReachableByCustomers(PlacementGrid grid, Vector2Int cell, Vector2Int footprint, int mask)
    {
        if (!grid.CanPlace(cell, footprint, 0)) return false;
        return NavMesh.SamplePosition(grid.FootprintCenter(cell, footprint, 0), out _, 2.5f, mask);
    }

    public static bool IsReachableFromRegister(Vector3 center, int mask)
    {
        var register = CashRegister.Instance;
        if (register == null) return false;
        if (!NavMesh.SamplePosition(register.transform.position, out var from, 2.5f, mask)) return false;

        var offsets = new[] { Vector3.right, Vector3.left, Vector3.forward, Vector3.back };
        var path = new NavMeshPath();
        foreach (var offset in offsets)
        {
            if (!NavMesh.SamplePosition(center + offset * 2f, out var to, 1.5f, mask)) continue;
            if (NavMesh.CalculatePath(from.position, to.position, mask, path) && path.status == NavMeshPathStatus.PathComplete) return true;
        }
        return false;
    }

    public static List<string> BuildTeam(CreatureRegistrySO registry, int max, List<string> exclude = null)
    {
        var pool = registry.GetAll().Values
            .Where(d => d != null && !d.IsDead && !d.IsSold && !d.IsBusy && d.Form != MonchiForm.Egg && (exclude == null || !exclude.Contains(d.UniqueID)))
            .OrderByDescending(d => d.Form == MonchiForm.Slime ? 1 : 0)
            .ThenByDescending(d => d.Explorations)
            .ToList();

        var team   = new List<CreatureDNA>();
        var male   = pool.FirstOrDefault(d => d.Gender == CreatureGender.Male);
        var female = pool.FirstOrDefault(d => d.Gender == CreatureGender.Female);
        if (male != null)   team.Add(male);
        if (female != null) team.Add(female);

        foreach (var d in pool)
        {
            if (team.Count >= max) break;
            if (!team.Contains(d)) team.Add(d);
        }
        return team.Select(d => d.UniqueID).ToList();
    }

    public static bool TryFindAdultPair(CreatureRegistrySO registry, out CreatureDNA mother, out CreatureDNA father)
    {
        mother = registry.GetAll().Values.FirstOrDefault(d => IsBreedingAdult(d) && d.Gender == CreatureGender.Female);
        father = registry.GetAll().Values.FirstOrDefault(d => IsBreedingAdult(d) && d.Gender == CreatureGender.Male);
        if (mother != null && father != null) return true;

        mother = registry.GetAll().Values.FirstOrDefault(d => IsBreedableAdult(d) && d.Gender == CreatureGender.Female);
        father = registry.GetAll().Values.FirstOrDefault(d => IsBreedableAdult(d) && d.Gender == CreatureGender.Male);
        return mother != null && father != null;
    }

    private static bool IsBreedingAdult(CreatureDNA d) =>
        d != null && !d.IsDead && !d.IsSold && d.Form == MonchiForm.Adult && d.BusyState == BusyReason.Breeding;

    public static CreatureDNA PickSellable(CreatureRegistrySO registry, List<string> excludeIds, string preferredId)
    {
        if (!string.IsNullOrEmpty(preferredId) && registry.TryGet(preferredId, out var preferred) && IsSellable(preferred))
            return preferred;
        return registry.GetAll().Values.FirstOrDefault(d => IsSellable(d) && !excludeIds.Contains(d.UniqueID));
    }

    public static string FormsSummary(CreatureRegistrySO registry)
    {
        int eggs = 0, slimes = 0, adultsM = 0, adultsF = 0;
        foreach (var d in registry.GetAll().Values)
        {
            if (d == null || d.IsDead || d.IsSold) continue;
            if (d.Form == MonchiForm.Egg) eggs++;
            else if (d.Form == MonchiForm.Slime) slimes++;
            else if (d.Gender == CreatureGender.Male) adultsM++;
            else if (d.Gender == CreatureGender.Female) adultsF++;
        }
        return $"huevos={eggs} slimes={slimes} adultosM={adultsM} adultasF={adultsF}";
    }

    private static bool IsBreedableAdult(CreatureDNA d) =>
        CreatureAvailability.IsFree(d) && d.Form == MonchiForm.Adult && d.BreedCount < BreedingService.MaxBreedCount;

    private static bool IsSellable(CreatureDNA d) =>
        CreatureAvailability.IsFree(d) && d.Form != MonchiForm.Egg;
}
}
