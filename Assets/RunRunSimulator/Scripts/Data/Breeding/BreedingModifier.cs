using System;
namespace MoriMonchiSimulator
{

public enum BreedingStat
{
    ParentWeight,
    GrandparentWeight,
    GreatGrandparentWeight,
    MutationWeight,
    BaseWeight,
    MotherBias,
    FatherBias
}

[Serializable]
public struct BreedingModifier
{
    public BreedingStat Stat;
    public float        Delta;
}
}
