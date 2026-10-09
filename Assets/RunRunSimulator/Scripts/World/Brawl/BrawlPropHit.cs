using MoreMountains.Feedbacks;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class BrawlPropHit : MonoBehaviour
{
    [SerializeField] private MMF_Player onHit;

    private BrawlFighter owner;

    private void OnEnable()
    {
        BrawlFighter.OnDamaged += HandleDamaged;
    }

    private void OnDisable()
    {
        BrawlFighter.OnDamaged -= HandleDamaged;
    }

    public void Bind(BrawlFighter fighter)
    {
        owner = fighter;
    }

    private void HandleDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (owner == null || victim != owner || onHit == null) return;
        onHit.PlayFeedbacks();
    }
}
}
