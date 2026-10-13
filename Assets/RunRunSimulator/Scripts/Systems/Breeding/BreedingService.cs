using System.Collections.Generic;
using System.Linq;
using UnityEngine;
namespace MoriMonchiSimulator
{

public static class BreedingService
{
    public const int MaxBreedCount = 4;

    public static CreatureDNA Breed(
        string                 motherID,
        string                 fatherID,
        CreatureRegistrySO     registry,
        CreatureDatabaseSO     partDb,
        InheritanceOddsTableSO odds,
        IReadOnlyList<BreedingDecorSO> decors = null)
    {
        var modifiers = new List<BreedingModifier>();
        if (decors != null)
            foreach (var decor in decors)
                if (decor != null && decor.Modifiers != null) modifiers.AddRange(decor.Modifiers);

        var effective = BreedingOdds.From(odds, modifiers);

        if (!registry.TryGet(motherID, out var mother))
        {
            Debug.LogError($"[BreedingService] Mother ID '{motherID}' not found in registry.");
            return null;
        }
        if (!registry.TryGet(fatherID, out var father))
        {
            Debug.LogError($"[BreedingService] Father ID '{fatherID}' not found in registry.");
            return null;
        }
        if (mother.IsDead || father.IsDead)
        {
            Debug.LogError("[BreedingService] Cannot breed: one or both creatures are dead.");
            return null;
        }
        if (mother.IsBusy || father.IsBusy)
        {
            Debug.LogError("[BreedingService] Cannot breed: one or both creatures are busy (queued for async combat).");
            return null;
        }
        if (mother.Gender != CreatureGender.Female || father.Gender != CreatureGender.Male)
        {
            Debug.LogError("[BreedingService] Breeding requires one Female (mother) and one Male (father).");
            return null;
        }
        if (mother.BreedCount >= MaxBreedCount)
        {
            Debug.LogError($"[BreedingService] Mother has reached max breeds ({MaxBreedCount}).");
            return null;
        }
        if (father.BreedCount >= MaxBreedCount)
        {
            Debug.LogError($"[BreedingService] Father has reached max breeds ({MaxBreedCount}).");
            return null;
        }

        var childBase = ColorGenetics.Inherit(mother.BaseColor, father.BaseColor);

        var origins = new List<PartOrigin>();
        string bodyID = ResolveSlot(PartRole.Body, motherID, fatherID, registry, partDb, effective, decors, origins);
        string hornID = ResolveSlot(PartRole.Horn, motherID, fatherID, registry, partDb, effective, decors, origins);
        string backID = ResolveSlot(PartRole.Back, motherID, fatherID, registry, partDb, effective, decors, origins);
        string wingID = ResolveSlot(PartRole.Wing, motherID, fatherID, registry, partDb, effective, decors, origins);
        string faceID = ResolveSlot(PartRole.Face, motherID, fatherID, registry, partDb, effective, decors, origins);

        var child = new CreatureDNA
        {
            BodyShapeID    = bodyID,
            HornID         = hornID,
            BackID         = backID,
            WingID         = wingID,
            FaceID         = faceID,
            Origins        = origins,
            BaseColor      = childBase,
            SecondaryColor = ColorGenetics.DeriveSecondary(childBase),
            FurType        = ColorGenetics.Inherit(mother.FurType, father.FurType),
            IsShiny        = ColorGenetics.RollShiny(),
            Gender       = Random.value < 0.5f ? CreatureGender.Male : CreatureGender.Female,
            Role         = Random.value < 0.5f ? mother.Role : father.Role,
            Element      = Random.value < odds.ElementMutationChance
                ? CreatureGenerator.RandomElement()
                : (Random.value < 0.5f ? mother.Element : father.Element),
            MotherID     = motherID,
            FatherID     = fatherID,
            Generation   = Mathf.Max(mother.Generation, father.Generation) + 1,
            HornPotential    = InheritPotential(mother.HornPotential, father.HornPotential),
            BackPotential    = InheritPotential(mother.BackPotential, father.BackPotential),
            WingPotential    = InheritPotential(mother.WingPotential, father.WingPotential),
            Sociability = InheritDial(mother.Sociability, father.Sociability, odds),
            Boldness    = InheritDial(mother.Boldness,    father.Boldness,    odds),
        };

        mother.BreedCount++;
        father.BreedCount++;

        return child;
    }

    private static string ResolveSlot(
        PartRole               role,
        string                 motherID,
        string                 fatherID,
        CreatureRegistrySO     registry,
        CreatureDatabaseSO     partDb,
        BreedingOdds           effective,
        IReadOnlyList<BreedingDecorSO> decors,
        List<PartOrigin>       origins)
    {
        var slot = effective.Roll();

        (string PartID, string AncestorID, bool MotherSide)? picked = slot switch
        {
            InheritanceOddsTableSO.Slot.Parent           => PickFromLevel(role, 0, motherID, fatherID, registry, effective),
            InheritanceOddsTableSO.Slot.Grandparent      => PickFromLevel(role, 1, motherID, fatherID, registry, effective),
            InheritanceOddsTableSO.Slot.GreatGrandparent => PickFromLevel(role, 2, motherID, fatherID, registry, effective),
            _                                            => null
        };

        var origin = new PartOrigin { Role = role };
        string partID;

        if (picked.HasValue)
        {
            partID            = picked.Value.PartID;
            origin.Slot       = slot;
            origin.MotherSide = picked.Value.MotherSide;
            origin.AncestorID = picked.Value.AncestorID;
        }
        else
        {
            partID      = RandomPartID(role, partDb);
            origin.Slot = slot == InheritanceOddsTableSO.Slot.Mutation
                ? InheritanceOddsTableSO.Slot.Mutation
                : InheritanceOddsTableSO.Slot.Base;
        }

        origin.DecorID = BreedingAttribution.CreditFor(origin.Slot, origin.MotherSide, decors);
        origins.Add(origin);
        return partID;
    }

    private static (string PartID, string AncestorID, bool MotherSide)? PickFromLevel(
        PartRole           role,
        int                levels,
        string             motherID,
        string             fatherID,
        CreatureRegistrySO registry,
        BreedingOdds       effective)
    {
        var motherCandidates = SideCandidates(role, motherID, levels, registry);
        var fatherCandidates = SideCandidates(role, fatherID, levels, registry);

        bool useMother = effective.PickMotherSide();
        var chosen = useMother ? motherCandidates : fatherCandidates;
        if (chosen.Count == 0)
        {
            useMother = !useMother;
            chosen    = useMother ? motherCandidates : fatherCandidates;
        }
        if (chosen.Count == 0) return null;

        var pick = chosen[Random.Range(0, chosen.Count)];
        return (pick.PartID, pick.AncestorID, useMother);
    }

    private static List<(string PartID, string AncestorID)> SideCandidates(PartRole role, string originID, int levels, CreatureRegistrySO registry)
    {
        var result = new List<(string PartID, string AncestorID)>();
        foreach (var id in ExpandGenerations(new[] { originID }, levels, registry))
        {
            if (!registry.TryGet(id, out var c)) continue;
            string part = SlotPartID(c, role);
            if (!string.IsNullOrEmpty(part)) result.Add((part, id));
        }
        return result;
    }

    private static List<string> ExpandGenerations(
        IEnumerable<string> origins,
        int                 levels,
        CreatureRegistrySO    registry)
    {
        var current = origins.Where(id => !string.IsNullOrEmpty(id)).Distinct().ToList();

        for (int i = 0; i < levels; i++)
        {
            var next = new List<string>();
            foreach (var id in current)
                if (registry.TryGet(id, out var c))
                {
                    if (!string.IsNullOrEmpty(c.MotherID)) next.Add(c.MotherID);
                    if (!string.IsNullOrEmpty(c.FatherID)) next.Add(c.FatherID);
                }
            current = next;
        }
        return current;
    }

    private static string SlotPartID(CreatureDNA dna, PartRole role) => role switch
    {
        PartRole.Body => dna.BodyShapeID,
        PartRole.Horn => dna.HornID,
        PartRole.Back => dna.BackID,
        PartRole.Wing => dna.WingID,
        PartRole.Face => dna.FaceID,
        _             => ""
    };

    private static string RandomPartID(PartRole role, CreatureDatabaseSO partDb) => role switch
    {
        PartRole.Body => partDb.BodyShapes?.GetRandomPart(where: PartPool.Rollable)?.ID ?? "",
        PartRole.Horn => partDb.Horns?.GetRandomPart(where: PartPool.Rollable)?.ID      ?? "",
        PartRole.Back => partDb.Backs?.GetRandomPart(where: PartPool.Rollable)?.ID      ?? "",
        PartRole.Wing => partDb.Wings?.GetRandomPart(where: PartPool.Rollable)?.ID      ?? "",
        PartRole.Face => partDb.Faces?.GetRandomPart(where: PartPool.Rollable)?.ID      ?? "",
        _             => ""
    };

    private static int InheritPotential(int motherPotential, int fatherPotential)
    {
        int average = (motherPotential + fatherPotential + Random.Range(0, 2)) / 2;
        return Mathf.Clamp(average + Random.Range(-1, 2), CreatureGenerator.PotentialMin, CreatureGenerator.PotentialMax);
    }

    private static float InheritDial(float motherDial, float fatherDial, InheritanceOddsTableSO odds)
    {
        float value = odds.RollDial() switch
        {
            InheritanceOddsTableSO.DialSlot.Average  => (motherDial + fatherDial) * 0.5f + Random.Range(-odds.DialJitter, odds.DialJitter),
            InheritanceOddsTableSO.DialSlot.Copy     => Random.value < 0.5f ? motherDial : fatherDial,
            _                                        => CreatureGenerator.RandomDial(),
        };
        return Mathf.Clamp01(value);
    }
}
}
