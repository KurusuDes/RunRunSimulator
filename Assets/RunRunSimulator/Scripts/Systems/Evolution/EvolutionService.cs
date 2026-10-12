using UnityEngine;
namespace MoriMonchiSimulator
{

public static class EvolutionService
{
    public static PartRole? Evolve(CreatureDNA dna, EvolutionEffectSO effect, CreatureRegistrySO registry)
    {
        if (dna == null || effect == null || registry == null) return null;
        if (!effect.CanApply(dna)) return null;

        int cost = effect.Cost(dna);
        if (!Wallet.TrySpend(Currency.Minerita, cost, "evolution")) return null;

        var role = effect.Apply(dna);
        if (role.HasValue) Debug.Log($"[Evolution] {dna.UniqueID} {role.Value} → {dna.TierOf(role.Value)} (-{cost} Minerita)");

        GameEvents.RegistryChanged(registry);
        return role;
    }
}
}
