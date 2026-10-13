using System;
using UnityEngine;
namespace MoriMonchiSimulator
{

public enum TutorialSignal
{
    Moved,
    ReachTarget,
    StorePanelOpened,
    BoxOrdered,
    CreatureArrived,
    FoodRefilled,
    ExpeditionReturned,
}

[Serializable]
public struct TutorialStep
{
    public string TextKey;
    public TutorialSignal Signal;
    public Transform Target;
    public float Radius;
}
}
