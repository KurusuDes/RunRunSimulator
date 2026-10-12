using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public abstract class EvolutionEffectSO : SerializedScriptableObject
{
    public string DisplayName;
    [TextArea] public string Description;

    public abstract bool CanApply(CreatureDNA dna);
    public abstract int Cost(CreatureDNA dna);
    public abstract int RequiredBattles(CreatureDNA dna);
    public abstract bool IsCandidate(CreatureDNA dna, PartRole role);
    public abstract PartRole? Apply(CreatureDNA dna);
}
}
