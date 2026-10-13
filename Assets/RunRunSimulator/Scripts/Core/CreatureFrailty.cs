namespace MoriMonchiSimulator
{

public static class CreatureFrailty
{
    public const float Penalty = 0.5f;

    public static bool IsFrail(CreatureDNA dna)
    {
        if (dna == null) return false;
        if (dna.Needs != null && dna.Needs.Health <= 0f) return true;

        var table = BreedingController.Instance != null ? BreedingController.Instance.LifeStageTable : null;
        if (table == null || GameClock.Instance == null) return false;
        return table.GetStage(dna.AgeDays(GameClock.Instance.Day)) == LifeStage.Elder;
    }
}
}
