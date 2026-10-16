using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

[DisallowMultipleComponent]
public class HotbarHUDUITK : MonoBehaviour
{
    [SerializeField] private UIDocument document;
    [SerializeField] private ItemDatabaseSO database;

    private const string SlotClass       = "hotbar-slot";
    private const string SlotActiveClass = "hotbar-slot--active";

    private readonly List<VisualElement> slotRoots = new List<VisualElement>();
    private readonly List<VisualElement> slotIcons = new List<VisualElement>();
    private readonly List<Label> slotNames = new List<Label>();
    private bool built;
    private PlayerInventorySO inventory;

    private void OnEnable()
    {
        inventory = GameManager.CurrentInventory;
        HotbarController.OnHotbarChanged       += Refresh;
        GameEvents.OnInventoryReloaded         += OnInventoryReloaded;
    }

    private void OnDisable()
    {
        HotbarController.OnHotbarChanged       -= Refresh;
        GameEvents.OnInventoryReloaded         -= OnInventoryReloaded;
    }

    private void Start()
    {
        BuildSlots();
        Refresh();
    }

    private void OnInventoryReloaded(PlayerInventorySO inv) { inventory = inv; Refresh(); }

    private void BuildSlots()
    {
        var root = UiPanels.RootOf(document);
        if (root == null) return;
        var container = root.Q<VisualElement>("slots");
        if (container == null) return;

        container.Clear();
        slotRoots.Clear();
        slotIcons.Clear();
        slotNames.Clear();

        for (int i = 0; i < PlayerInventorySO.HotbarSize; i++)
        {
            var slot = new VisualElement { name = $"slot-{i}" };
            slot.AddToClassList(SlotClass);
            slot.pickingMode = PickingMode.Ignore;

            var box = new VisualElement();
            box.AddToClassList("hotbar-slot__box");
            box.pickingMode = PickingMode.Ignore;
            slot.Add(box);

            var runes = new VisualElement();
            runes.AddToClassList("hotbar-slot__runes");
            runes.pickingMode = PickingMode.Ignore;
            box.Add(runes);

            var icon = new VisualElement();
            icon.AddToClassList("hotbar-slot__icon");
            icon.pickingMode = PickingMode.Ignore;
            box.Add(icon);

            var nameLabel = new Label("");
            nameLabel.AddToClassList("hotbar-slot__name");
            nameLabel.pickingMode = PickingMode.Ignore;
            box.Add(nameLabel);

            var frame = new VisualElement();
            frame.AddToClassList("hotbar-slot__frame");
            frame.pickingMode = PickingMode.Ignore;
            box.Add(frame);

            var key = new Label((i + 1).ToString());
            key.AddToClassList("hotbar-slot__key");
            key.pickingMode = PickingMode.Ignore;
            slot.Add(key);

            slotRoots.Add(slot);
            slotIcons.Add(icon);
            slotNames.Add(nameLabel);
            container.Add(slot);
        }
        built = true;
    }

    private void Refresh()
    {
        if (!built) BuildSlots();
        if (!built) return;

        var inv = inventory;
        int active = HotbarController.Instance != null ? HotbarController.Instance.ActiveSlot : -1;

        for (int i = 0; i < slotNames.Count; i++)
        {
            string id   = inv != null ? inv.GetHotbarSlot(i) : null;
            var def     = string.IsNullOrEmpty(id) || database == null ? null : database.GetByID(id);

            if (def != null && def.Icon != null)
            {
                slotIcons[i].style.backgroundImage = new StyleBackground(def.Icon);
                slotNames[i].text = "";
            }
            else
            {
                slotIcons[i].style.backgroundImage = StyleKeyword.None;
                slotNames[i].text = NameOf(id, def);
            }

            slotRoots[i].EnableInClassList(SlotActiveClass, i == active);
        }
    }

    private static string NameOf(string id, ItemDefinitionSO def)
    {
        if (string.IsNullOrEmpty(id)) return "";
        return def != null ? DataLoc.ItemName(def) : id;
    }
}
}
