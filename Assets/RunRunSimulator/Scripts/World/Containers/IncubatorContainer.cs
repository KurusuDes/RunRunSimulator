using System.Linq;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class IncubatorContainer : MoriMochiContainer, IInteractable
{
    [BoxGroup("Incubator")]
    [Tooltip("Outward (horizontal) impulse popping a freshly hatched creature out of the incubator.")]
    [SerializeField, Min(0f)] private float hatchPopOut = 5f;
    [BoxGroup("Incubator")]
    [Tooltip("Upward impulse blended into the hatch pop so it leaps out, not just slides.")]
    [SerializeField, Min(0f)] private float hatchPopUp = 4f;

    protected override bool Accepts(MoriMochiAgent agent) => agent.DNA != null && agent.DNA.Form == MonchiForm.Egg;

    public void Interact()
    {
        var controller = BreedingController.Instance;
        if (controller == null) { Debug.LogWarning("[IncubatorContainer] No hay BreedingController en escena."); return; }

        var eggAgent = Occupants.FirstOrDefault(a => a != null && a.DNA != null && a.DNA.Form == MonchiForm.Egg);
        if (eggAgent == null) { Debug.Log("[IncubatorContainer] No hay huevos en la incubadora."); return; }

        var result = controller.TryHatchEgg(eggAgent.DNA);
        switch (result)
        {
            case HatchResult.Hatched:
                Debug.Log($"[IncubatorContainer] ¡Eclosionó \"{eggAgent.DNA.CustomName}\"!");
                HatchOut(eggAgent);
                break;
            case HatchResult.InsufficientMinerita:
                Debug.Log($"[IncubatorContainer] No hay suficiente Minerita para eclosionar (cuesta {controller.EggHatchCost}).");
                break;
            default:
                Debug.Log($"[IncubatorContainer] No se pudo eclosionar el huevo ({result}).");
                break;
        }
    }

    private void HatchOut(MoriMochiAgent agent)
    {
        agent.RequestReleaseFromPen();
        Vector3 away = agent.transform.position - Center; away.y = 0f;
        away = away.sqrMagnitude > 0.01f ? away.normalized : Random.insideUnitSphere;
        agent.Knock(away * hatchPopOut + Vector3.up * hatchPopUp);
    }
}
}
