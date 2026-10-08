using System;
using UnityEngine;

namespace MoriMonchiSimulator
{

public struct BrawlFxEvent
{
    public BrawlFxKind Kind;
    public Vector3 From;
    public Vector3 To;
    public Vector3[] Path;
    public float Radius;
    public float Angle;
    public float Duration;
    public BrawlTheme Theme;
    public ExpeditionTeam Team;
    public BrawlFighter Source;
    public BrawlFighter Target;
}

public static class BrawlFx
{
    public static event Action<BrawlFxEvent> Emitted;

    public static void Emit(BrawlFxEvent e) => Emitted?.Invoke(e);
}
}
