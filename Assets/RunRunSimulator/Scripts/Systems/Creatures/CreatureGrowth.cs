namespace MoriMonchiSimulator
{

public static class CreatureGrowth
{
    public static void Lay(CreatureDNA dna)
    {
        if (dna == null) return;
        dna.Form = MonchiForm.Egg;
        dna.Explorations = 0;
    }

    public static void Hatch(CreatureDNA dna)
    {
        if (dna == null) return;
        dna.Form = MonchiForm.Slime;
        dna.Explorations = 0;
    }

    public static bool RecordExploration(CreatureDNA dna, int toEvolve)
    {
        if (dna == null || dna.IsDead || dna.Form != MonchiForm.Slime) return false;

        dna.Explorations++;
        if (dna.Explorations >= toEvolve)
        {
            dna.Form = MonchiForm.Adult;
            return true;
        }
        return false;
    }
}
}
