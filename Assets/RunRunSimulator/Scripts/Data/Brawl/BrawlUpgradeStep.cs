using System;
using System.Collections.Generic;
namespace MoriMonchiSimulator
{

[Serializable]
public struct BrawlUpgradeMod
{
    public BrawlUpgradeStat Stat;
    public BrawlUpgradeOp Op;
    public float Value;
}

[Serializable]
public class BrawlUpgradeStep
{
    public List<BrawlUpgradeMod> Mods = new();
}
}
