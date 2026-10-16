namespace MoriMonchiSimulator
{
public enum UIPanelType
{
    None             = 0,
    CreatureGrid     = 1,
    MorimonchiDetail = 2,
    Breeding         = 3,
    Storage          = 5,
    Store            = 6,
    Transaction      = 7,
    Expedition       = 8,
    ExpeditionReturn = 9,
    Pause            = 10,
    Settings         = 11,
}

public enum FocusPrompt
{
    None         = 0,
    Creature     = 1,
    Interactable = 2,
    Carrying     = 3,
    Item         = 4,
}

public enum PlayerStateType
{
    None      = 0,
    Exploring = 1,
    Menu      = 2,
}
}
