using System;
namespace MoriMonchiSimulator
{

[Serializable]
public class PartOrigin
{
    public PartRole Role;
    public InheritanceOddsTableSO.Slot Slot;
    public bool MotherSide;
    public string AncestorID = "";
    public string DecorID = "";
}
}
