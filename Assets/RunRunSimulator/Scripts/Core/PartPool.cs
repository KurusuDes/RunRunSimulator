namespace MoriMonchiSimulator
{

public static class PartPool
{
    public static bool Rollable(BodyPart part)
    {
        if (part == null) return false;

        switch (part.GetPartRole())
        {
            case PartRole.Horn:
            case PartRole.Back:
            case PartRole.Wing:
                var bank = GameManager.Instance != null ? GameManager.Instance.MonchiVisualBank : null;
                return bank == null || bank.HasPartMesh(part.ID);
            default:
                return true;
        }
    }
}
}
