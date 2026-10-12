using System.Collections;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using Unity.AI.Navigation;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class NavMeshRebaker : MonoBehaviour
{
    [SerializeField] private List<NavMeshSurface> surfaces = new List<NavMeshSurface>();

    private const float RebakeDebounce = 0.4f;

    private Coroutine debounce;
    private bool running;
    private bool pending;

    private void OnEnable()
    {
        GameEvents.OnWorldStateReloaded += OnWorldStateReloaded;
        GameEvents.OnShopZoneOpened     += OnShopZoneOpened;
    }

    private void OnDisable()
    {
        GameEvents.OnWorldStateReloaded -= OnWorldStateReloaded;
        GameEvents.OnShopZoneOpened     -= OnShopZoneOpened;
        StopAllCoroutines();
        debounce = null;
        running = false;
        pending = false;
    }

    private void Start() => ScheduleRebake();

    private void OnWorldStateReloaded(WorldStateSO world) => ScheduleRebake();

    private void OnShopZoneOpened(ShopUpgradeSO expansion, int level) => ScheduleRebake();

    [Button("Rebake NavMesh", ButtonSizes.Large), GUIColor(0.6f, 0.8f, 1f)]
    private void ScheduleRebake()
    {
        if (!isActiveAndEnabled || surfaces.Count == 0) return;
        if (running)
        {
            pending = true;
            return;
        }
        if (debounce != null) StopCoroutine(debounce);
        debounce = StartCoroutine(RebakeAfterDebounce());
    }

    private IEnumerator RebakeAfterDebounce()
    {
        yield return new WaitForSeconds(RebakeDebounce);
        debounce = null;
        running = true;
        yield return RebakeRoutine();
        running = false;
        if (!pending) yield break;
        pending = false;
        ScheduleRebake();
    }

    private IEnumerator RebakeRoutine()
    {
        GameEvents.NavMeshWillRebake();

        var operations = new List<AsyncOperation>();
        foreach (var surface in surfaces)
        {
            if (surface == null) continue;
            if (surface.navMeshData != null) operations.Add(surface.UpdateNavMesh(surface.navMeshData));
            else surface.BuildNavMesh();
        }

        foreach (var op in operations) yield return op;

        GameEvents.NavMeshRebaked();
    }
}
}
