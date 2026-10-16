using System;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public static class StoreTileView
{
    private static readonly StoreRows.Tab[] Tabs = (StoreRows.Tab[])Enum.GetValues(typeof(StoreRows.Tab));

    public static string IconClass(StoreRows.Tab tab) => "store-icon--" + tab.ToString().ToLowerInvariant();

    public static void ApplyIcon(VisualElement el, StoreRows.Tab tab, Sprite sprite)
    {
        foreach (var t in Tabs) el.RemoveFromClassList(IconClass(t));
        if (sprite != null)
        {
            el.style.backgroundImage = new StyleBackground(sprite);
            return;
        }
        el.style.backgroundImage = StyleKeyword.Null;
        el.AddToClassList(IconClass(tab));
    }

    public static VisualElement Build(StoreRows.Tab tab, StoreRows.Row row, bool discountActive, Action onSelect, Action onBuy)
    {
        var tile = new VisualElement();
        tile.AddToClassList("store-tile");

        var slot = new VisualElement();
        slot.AddToClassList("mm-slot");
        slot.AddToClassList("store-tile__slot");
        var icon = new VisualElement { pickingMode = PickingMode.Ignore };
        icon.AddToClassList("store-icon");
        icon.AddToClassList("store-tile__icon");
        ApplyIcon(icon, tab, row.Icon);
        slot.Add(icon);
        tile.Add(slot);

        var name = new Label(row.Name);
        name.AddToClassList("store-tile__name");
        tile.Add(name);

        tile.Add(BuildPill(row, discountActive, tile));

        tile.RegisterCallback<ClickEvent>(e =>
        {
            if (e.clickCount >= 2) onBuy();
            else onSelect();
        });
        return tile;
    }

    public static VisualElement BuildEmpty()
    {
        var tile = new VisualElement { pickingMode = PickingMode.Ignore };
        tile.AddToClassList("store-tile");
        tile.AddToClassList("store-tile--empty");
        var runes = new VisualElement { pickingMode = PickingMode.Ignore };
        runes.AddToClassList("store-tile__runes");
        tile.Add(runes);
        return tile;
    }

    private static VisualElement BuildPill(StoreRows.Row row, bool discountActive, VisualElement tile)
    {
        var pill = new VisualElement { pickingMode = PickingMode.Ignore };
        pill.AddToClassList("store-tile__pill");
        var label = new Label { pickingMode = PickingMode.Ignore };
        pill.Add(label);

        if (!string.IsNullOrEmpty(row.LockedBy))
        {
            tile.AddToClassList("store-tile--locked");
            label.text = Loc.Tr("ui.store.locked.short");
            label.AddToClassList("store-tile__tag");
            return pill;
        }

        if (row.Buy == null)
        {
            label.text = row.Reward;
            label.AddToClassList("store-price__now");
            return pill;
        }

        if (StorePrice.IsMaxed(row))
        {
            label.text = Loc.Tr("ui.store.max");
            label.AddToClassList("store-tile__tag");
            return pill;
        }

        var info = StorePrice.Resolve(row, discountActive);
        label.text = StorePrice.Text(info.Final, info.Minerita);
        label.AddToClassList(info.Discounted ? "store-price__now--sale" : "store-price__now");
        if (info.Minerita) label.AddToClassList("store-price__now--minerita");
        if (!StorePrice.CanBuy(row)) tile.AddToClassList("store-tile--soldout");
        return pill;
    }
}
}
