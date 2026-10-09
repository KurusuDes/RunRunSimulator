using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlTrialProps : MonoBehaviour
{
    [Required, SerializeField] private BrawlMatch match;
    [Required, SerializeField] private BrawlTrialRoom trial;
    [SerializeField] private GameObject dummyProp;
    [SerializeField] private GameObject mineralProp;
    [SerializeField, Min(0.1f)] private float propScale = 1f;

    private void OnEnable()
    {
        trial.Began += HandleBegan;
    }

    private void OnDisable()
    {
        trial.Began -= HandleBegan;
    }

    private void HandleBegan()
    {
        var prefab = trial.Kind == BrawlRoomKind.Dummies ? dummyProp : mineralProp;
        if (prefab == null) return;

        Vector3 center = Vector3.zero;
        int players = 0;
        foreach (var fighter in match.Fighters)
        {
            if (fighter == null || fighter.Team != ExpeditionTeam.Player) continue;
            center += fighter.Position;
            players++;
        }
        if (players > 0) center /= players;

        foreach (var fighter in match.Fighters)
        {
            if (fighter == null || fighter.Team != ExpeditionTeam.Rival) continue;

            foreach (var rend in fighter.Visualizer.GetComponentsInChildren<Renderer>(true)) rend.enabled = false;

            var prop = Instantiate(prefab, fighter.transform);
            var propTransform = prop.transform;
            propTransform.localPosition = Vector3.zero;
            propTransform.localRotation = Quaternion.identity;
            propTransform.localScale = Vector3.one * propScale;

            if (players > 0)
            {
                Vector3 toward = center - fighter.Position;
                toward.y = 0f;
                if (toward.sqrMagnitude > 0.0001f) propTransform.rotation = Quaternion.LookRotation(toward);
            }

            var hit = prop.GetComponentInChildren<BrawlPropHit>(true);
            if (hit != null) hit.Bind(fighter);
        }
    }
}
}
