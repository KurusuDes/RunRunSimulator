namespace MoriMonchiSimulator
{
public enum ItemType
{
    Furniture = 0,
    WorldProp = 1,
}

public enum WorldPropCategory
{
    Tool     = 0,
    Food     = 1,
    Medicine = 2,
    Toy      = 3,
}

public enum BuyResult
{
    Success           = 0,
    OutOfStock        = 1,
    InsufficientFunds = 2,
    AlreadyOwned      = 3,
    Locked            = 4,
}

public enum Currency
{
    Dabloons = 0,
    Minerita = 1,
}

public enum ToyKind
{
    Ball,
    Chew,
    Hose,
    Mop,
    Rope,
    Plush,
    Bubbles,
}

public enum TasteKind
{
    None    = 0,
    Role    = 1,
    Color   = 2,
    PartSet = 3,
}

[System.Flags]
public enum StoreItemTypeFilter
{
    None      = 0,
    Furniture = 1 << 0,
    WorldProp = 1 << 1,
}

}
