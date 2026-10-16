using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class DecorSlot : MonoBehaviour, IInteractable, IFocusLabel
{
    private static readonly int BaseColorId = Shader.PropertyToID("_BaseColor");
    private const float FallbackCubeSize = 0.4f;

    [Required, SerializeField] private BreedingContainer owner;
    [SerializeField, Min(0)] private int index;
    [SerializeField] private Transform anchor;

    private MaterialPropertyBlock block;

    public string SlotId => $"{owner.name}_{index}";

    public string DecorId
    {
        get
        {
            var world = GameManager.Instance != null ? GameManager.Instance.WorldState : null;
            return world != null ? world.GetDecorSlot(SlotId) ?? "" : "";
        }
    }

    private void OnEnable()
    {
        GameEvents.OnWorldStateChanged  += OnWorldState;
        GameEvents.OnWorldStateReloaded += OnWorldState;
    }

    private void OnDisable()
    {
        GameEvents.OnWorldStateChanged  -= OnWorldState;
        GameEvents.OnWorldStateReloaded -= OnWorldState;
    }

    private void Start() => Refresh();

    private void OnWorldState(WorldStateSO state) => Refresh();

    public void Interact()
    {
        if (!Application.isPlaying || owner == null) return;
        var gm = GameManager.Instance;
        if (gm == null) return;
        var world     = gm.WorldState;
        var inventory = gm.Inventory;
        var database  = BreedingController.Instance != null ? BreedingController.Instance.DecorDatabase : null;
        if (world == null || inventory == null || database == null) return;

        string slotId  = SlotId;
        string current = world.GetDecorSlot(slotId) ?? "";
        var    all     = database.All;

        int start = 0;
        if (!string.IsNullOrEmpty(current))
        {
            inventory.AddDecor(current);
            for (int i = 0; i < all.Count; i++)
                if (all[i] != null && all[i].Id == current) { start = i + 1; break; }
        }

        string next = "";
        for (int i = start; i < all.Count; i++)
        {
            var decor = all[i];
            if (decor == null || string.IsNullOrEmpty(decor.Id) || inventory.DecorCount(decor.Id) <= 0) continue;
            if (!inventory.TryTakeDecor(decor.Id)) continue;
            next = decor.Id;
            break;
        }

        if (string.IsNullOrEmpty(current) && string.IsNullOrEmpty(next)) return;

        world.SetDecorSlot(slotId, next);
        GameEvents.InventoryChanged(inventory);
        GameEvents.WorldStateChanged(world);
    }

    public void Refresh()
    {
        var root = anchor != null ? anchor : transform;
        for (int i = root.childCount - 1; i >= 0; i--)
            Destroy(root.GetChild(i).gameObject);

        var database = BreedingController.Instance != null ? BreedingController.Instance.DecorDatabase : null;
        var decor    = database != null ? database.Get(DecorId) : null;

        if (decor == null) return;

        SpawnVisual(decor, root);
    }

    public string FocusTitle
    {
        get
        {
            var gm       = GameManager.Instance;
            var world    = gm != null ? gm.WorldState : null;
            var database = BreedingController.Instance != null ? BreedingController.Instance.DecorDatabase : null;
            var decor    = database != null ? database.Get(DecorId) : null;
            if (decor == null) return Loc.Tr("ui.decor.slot.empty");
            int bred = world != null ? world.BredTotal : 0;
            return decor.IsDiscovered(bred) ? decor.DisplayName : Loc.Tr("ui.store.decor.unknown");
        }
    }

    public string FocusDetail => null;

    private void SpawnVisual(BreedingDecorSO decor, Transform root)
    {
        if (decor.Prefab != null)
        {
            Instantiate(decor.Prefab, root);
            return;
        }

        var cube = GameObject.CreatePrimitive(PrimitiveType.Cube);
        var col  = cube.GetComponent<Collider>();
        if (col != null) Destroy(col);
        cube.transform.SetParent(root, false);
        cube.transform.localScale = Vector3.one * FallbackCubeSize;

        block ??= new MaterialPropertyBlock();
        var rend = cube.GetComponent<Renderer>();
        rend.GetPropertyBlock(block);
        block.SetColor(BaseColorId, decor.Tint);
        rend.SetPropertyBlock(block);
    }
}
}
