using System.Collections.Generic;
using MoreMountains.Feedbacks;
using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class ShopZone : MonoBehaviour
{
    [Title("Rule")]
    [Required, SerializeField] private ShopUpgradeSO expansion;
    [Min(1), SerializeField] private int requiredLevel = 1;

    [Title("Content")]
    [Required, SerializeField] private GameObject openContent;
    [SerializeField] private GameObject lockedContent;
    [SerializeField] private List<GameObject> hideWhenOpen = new List<GameObject>();

    [Title("Feedback")]
    [SerializeField] private MMF_Player openFeedback;

    private bool initialized;
    private bool isOpen;

    public bool IsOpen => isOpen;

    private void OnEnable()
    {
        GameEvents.OnWorldStateReloaded += OnWorldStateReloaded;
        GameEvents.OnWorldStateChanged  += OnWorldStateChanged;
    }

    private void OnDisable()
    {
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
        GameEvents.OnWorldStateChanged  -= OnWorldStateChanged;
    }

    private void Start()
    {
        var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
        if (world != null) Apply(world, true);
    }

    private void OnWorldStateReloaded(WorldStateSO world) => Apply(world, true);

    private void OnWorldStateChanged(WorldStateSO world) => Apply(world, false);

    private void Apply(WorldStateSO world, bool silent)
    {
        if (world == null || expansion == null) return;

        int level = world.UpgradeLevel(expansion.Id);
        bool open = level >= requiredLevel;
        if (initialized && open == isOpen) return;

        bool openedNow = initialized && !isOpen && open && !silent;
        initialized = true;
        isOpen = open;

        openContent.SetActive(open);
        if (lockedContent != null) lockedContent.SetActive(!open);
        for (int i = 0; i < hideWhenOpen.Count; i++)
            if (hideWhenOpen[i] != null) hideWhenOpen[i].SetActive(!open);

        if (!openedNow) return;
        if (openFeedback != null) openFeedback.PlayFeedbacks();
        GameEvents.ShopZoneOpened(expansion, level);
    }
}
}
