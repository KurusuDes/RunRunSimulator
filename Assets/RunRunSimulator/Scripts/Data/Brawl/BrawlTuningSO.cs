using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BrawlTuning", menuName = "MoriMonchi/Brawl/Tuning")]
public class BrawlTuningSO : ScriptableObject
{
    [System.Serializable]
    public struct BodyStat
    {
        public string BodyId;
        public string Label;
        public float HpMul;
        public float SpeedMul;
    }

    [Title("Cuerpos")]
    [Min(1f)] public float BaseHp = 6000f;
    public List<BodyStat> Bodies = new();

    [Title("Partida")]
    [Min(0f)] public float CountdownSeconds = 3f;
    [Min(1f)] public float RoundSeconds = 90f;
    [Min(0f)] public float EndHoldSeconds = 6f;

    [Title("Último en pie")]
    [Range(0f, 1f)] public float LastStandShield = 0.25f;
    [Min(0f)] public float LastStandBoost = 0.3f;
    [Min(0f)] public float LastStandHaste = 0.2f;
    [Min(0f)] public float LastStandSeconds = 5f;

    [Title("Ritmo")]
    [Min(0f)] public float KoDamageRamp = 0.15f;

    [Title("Muerte súbita")]
    [Min(0f)] public float SuddenDeathStart = 0.02f;
    [Min(0f)] public float SuddenDeathRamp = 0.01f;
    [Range(0f, 1f)] public float SuddenDeathHealFactor = 0.5f;

    [Title("Equipos")]
    public Color AllyColor = new Color(0.34f, 0.55f, 0.84f);
    public Color FoeColor = new Color(0.84f, 0.36f, 0.36f);

    [Title("Personalidad (x = 0, y = 1)")]
    public Vector2 RetreatHp = new Vector2(0.5f, 0.15f);
    public Vector2 PreferredRange = new Vector2(0.9f, 0.55f);
    public Vector2 HealThreshold = new Vector2(0.55f, 0.85f);
    [Min(0f)] public float StrafeAngle = 30f;
    public Vector2 StrafeFlipSeconds = new Vector2(1.2f, 2.6f);
    [Min(0f)] public float PatienceSeconds = 6f;

    public BodyStat BodyFor(string bodyId)
    {
        for (int i = 0; i < Bodies.Count; i++)
            if (Bodies[i].BodyId == bodyId) return Bodies[i];
        return new BodyStat { BodyId = bodyId, Label = "", HpMul = 1f, SpeedMul = 1f };
    }

    public Color TeamColor(ExpeditionTeam team)
    {
        switch (team)
        {
            case ExpeditionTeam.Player: return AllyColor;
            case ExpeditionTeam.Rival: return FoeColor;
            default: return Color.white;
        }
    }
}
}
