using System;
using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class BreedingBreedTabPresenter : ITabPresenter
{
    private const string Focus = "breed-focus";
    private const string Chosen = "breed-tile--chosen";
    private const string Empty = "breed-slot--empty";
    private const string FilterOn = "mm-button--selected";
    private const int Columns = 4;

    private enum SubFocus { Grid, Button }

    private readonly Func<CreatureRegistrySO> getRegistry;
    private readonly CreatureDatabaseSO database;
    private readonly IncubationService incubation;
    private readonly Action onBred;

    private readonly VisualElement fatherSlot, motherSlot, fatherSlotImg, motherSlotImg, inheritList;
    private readonly Label fatherSlotName, motherSlotName, timeLabel, emptyLabel;
    private readonly Button breedButton, filterFathers, filterMothers;
    private readonly ScrollView grid;

    private string selectedFatherId = "", selectedMotherId = "";
    private readonly List<VisualElement> tiles = new List<VisualElement>();
    private CreatureGender filter = CreatureGender.Male;
    private int gridIndex;
    private bool focusVisible;
    private SubFocus focus = SubFocus.Grid;

    public BreedingBreedTabPresenter(VisualElement root, Func<CreatureRegistrySO> getRegistry,
        CreatureDatabaseSO database, IncubationService incubation, Action onBred)
    {
        this.getRegistry = getRegistry;
        this.database = database;
        this.incubation = incubation;
        this.onBred = onBred;

        fatherSlot     = root.Q<VisualElement>("father-slot");
        motherSlot     = root.Q<VisualElement>("mother-slot");
        fatherSlotImg  = root.Q<VisualElement>("father-slot-img");
        motherSlotImg  = root.Q<VisualElement>("mother-slot-img");
        inheritList    = root.Q<VisualElement>("inherit-list");
        fatherSlotName = root.Q<Label>("father-slot-name");
        motherSlotName = root.Q<Label>("mother-slot-name");
        timeLabel      = root.Q<Label>("time-label");
        emptyLabel     = root.Q<Label>("candidate-empty");
        breedButton    = root.Q<Button>("breed-button");
        filterFathers  = root.Q<Button>("filter-fathers");
        filterMothers  = root.Q<Button>("filter-mothers");
        grid           = root.Q<ScrollView>("candidate-grid");

        SetText(root.Q<Label>("inherit-title"), "ui.breeding.section.inheritance");
        SetText(root.Q<Label>("prompt-move"), "ui.prompt.move");
        SetText(root.Q<Label>("prompt-select"), "ui.prompt.select");
        SetText(root.Q<Label>("prompt-tab"), "ui.prompt.tab");
        SetText(root.Q<Label>("prompt-close"), "ui.prompt.close");
        SetText(emptyLabel, "ui.breeding.list.empty");
        if (filterFathers != null) filterFathers.text = Loc.Tr("ui.breeding.column.fathers");
        if (filterMothers != null) filterMothers.text = Loc.Tr("ui.breeding.column.mothers");

        if (breedButton != null) breedButton.clicked += TryBreed;
        if (filterFathers != null) filterFathers.clicked += OnFilterFathers;
        if (filterMothers != null) filterMothers.clicked += OnFilterMothers;
        fatherSlot?.RegisterCallback<ClickEvent>(_ => ChangeFilter(CreatureGender.Male));
        motherSlot?.RegisterCallback<ClickEvent>(_ => ChangeFilter(CreatureGender.Female));
    }

    public void Enter()
    {
        gridIndex = 0;
        focus = tiles.Count > 0 ? SubFocus.Grid : SubFocus.Button;
        ApplyFocus();
    }

    public bool Navigate(int h, int v)
    {
        if (focus == SubFocus.Button)
        {
            if (v >= 0) return true;
            if (tiles.Count == 0) { ClearFocus(); return false; }
            focus = SubFocus.Grid;
            gridIndex = Mathf.Clamp(gridIndex, 0, tiles.Count - 1);
            ApplyFocus();
            return true;
        }

        if (tiles.Count == 0) { focus = SubFocus.Button; ApplyFocus(); return true; }

        if (v < 0)
        {
            if (gridIndex < Columns) { ClearFocus(); return false; }
            gridIndex -= Columns;
        }
        else if (v > 0)
        {
            if (gridIndex + Columns < tiles.Count) gridIndex += Columns;
            else if (gridIndex / Columns == (tiles.Count - 1) / Columns) focus = SubFocus.Button;
            else gridIndex = tiles.Count - 1;
        }

        if (h != 0) gridIndex = Mathf.Clamp(gridIndex + h, 0, tiles.Count - 1);

        ApplyFocus();
        return true;
    }

    public void Submit()
    {
        if (focus == SubFocus.Button) { TryBreed(); return; }
        if (gridIndex >= 0 && gridIndex < tiles.Count) Assign((string)tiles[gridIndex].userData);
    }

    public bool Cancel()
    {
        if (focus != SubFocus.Button || tiles.Count == 0) return false;
        focus = SubFocus.Grid;
        gridIndex = Mathf.Clamp(gridIndex, 0, tiles.Count - 1);
        ApplyFocus();
        return true;
    }

    public void ClearFocus()
    {
        breedButton?.RemoveFromClassList(Focus);
        foreach (var t in tiles) t.RemoveFromClassList(Focus);
        focus = SubFocus.Grid;
        focusVisible = false;
    }

    public void Rebuild()
    {
        RebuildGrid();
        RefreshSlots();
    }

    public void Teardown()
    {
        if (breedButton != null) breedButton.clicked -= TryBreed;
        if (filterFathers != null) filterFathers.clicked -= OnFilterFathers;
        if (filterMothers != null) filterMothers.clicked -= OnFilterMothers;
    }

    private static void SetText(Label label, string key)
    {
        if (label != null) label.text = Loc.Tr(key);
    }

    private void OnFilterFathers() => ChangeFilter(CreatureGender.Male);
    private void OnFilterMothers() => ChangeFilter(CreatureGender.Female);

    private void ChangeFilter(CreatureGender gender)
    {
        if (filter == gender) return;
        filter = gender;
        gridIndex = 0;
        RebuildGrid();
    }

    private void RebuildGrid()
    {
        if (grid == null) return;
        grid.Clear();
        tiles.Clear();

        filterFathers?.EnableInClassList(FilterOn, filter == CreatureGender.Male);
        filterMothers?.EnableInClassList(FilterOn, filter == CreatureGender.Female);

        var registry = getRegistry();
        if (registry != null)
        {
            string chosenId = filter == CreatureGender.Male ? selectedFatherId : selectedMotherId;
            foreach (var dna in Eligible(registry.GetAll().Values, filter))
            {
                var tile = MakeTile(dna);
                tile.EnableInClassList(Chosen, dna.UniqueID == chosenId);
                grid.Add(tile);
                tiles.Add(tile);
            }
        }

        if (emptyLabel != null) emptyLabel.style.display = tiles.Count == 0 ? DisplayStyle.Flex : DisplayStyle.None;
        gridIndex = tiles.Count == 0 ? 0 : Mathf.Clamp(gridIndex, 0, tiles.Count - 1);
        ApplyFocusIfActive();
    }

    private static IEnumerable<CreatureDNA> Eligible(IEnumerable<CreatureDNA> all, CreatureGender gender) =>
        all.Where(d => CreatureAvailability.IsFree(d) && d.Gender == gender && d.BreedCount < BreedingService.MaxBreedCount)
           .OrderBy(d => d.CustomName);

    private VisualElement MakeTile(CreatureDNA dna)
    {
        var tile = new VisualElement();
        tile.AddToClassList("breed-tile");
        tile.userData = dna.UniqueID;

        var slot = new VisualElement();
        slot.AddToClassList("mm-slot");
        slot.AddToClassList("breed-tile__slot");
        slot.pickingMode = PickingMode.Ignore;

        var vignette = new VisualElement { pickingMode = PickingMode.Ignore };
        vignette.AddToClassList("mm-layer");
        vignette.AddToClassList("mm-slot__vignette");
        slot.Add(vignette);

        var img = new VisualElement { pickingMode = PickingMode.Ignore };
        img.AddToClassList("breed-tile__img");
        MonchiPortraitUI.Apply(img, dna);
        slot.Add(img);

        var frame = new VisualElement { pickingMode = PickingMode.Ignore };
        frame.AddToClassList("mm-layer");
        frame.AddToClassList("mm-slot__frame");
        slot.Add(frame);
        tile.Add(slot);

        var name = new Label(dna.CustomName) { pickingMode = PickingMode.Ignore };
        name.AddToClassList("breed-tile__name");
        tile.Add(name);

        var count = new Label($"{dna.BreedCount}/{BreedingService.MaxBreedCount}") { pickingMode = PickingMode.Ignore };
        count.AddToClassList("breed-tile__count");
        tile.Add(count);

        string id = dna.UniqueID;
        tile.RegisterCallback<ClickEvent>(_ => Assign(id));
        return tile;
    }

    private void RefreshSlots()
    {
        var registry = getRegistry();
        CreatureDNA father = null, mother = null;
        if (registry != null)
        {
            if (!string.IsNullOrEmpty(selectedFatherId)) registry.TryGet(selectedFatherId, out father);
            if (!string.IsNullOrEmpty(selectedMotherId)) registry.TryGet(selectedMotherId, out mother);
        }

        SetSlot(fatherSlot, fatherSlotName, fatherSlotImg, father);
        SetSlot(motherSlot, motherSlotName, motherSlotImg, mother);
        BreedingInheritanceView.Build(inheritList, database, father, mother);

        bool both = father != null && mother != null;
        breedButton?.SetEnabled(both);

        if (timeLabel == null) return;
        if (timeLabel.parent != null) timeLabel.parent.style.visibility = both ? Visibility.Visible : Visibility.Hidden;
        if (!both) { timeLabel.text = ""; return; }
        int mins = (BreedingController.Instance != null && BreedingController.Instance.InheritanceOdds != null) ? BreedingController.Instance.InheritanceOdds.BreedDurationMinutes : 360;
        timeLabel.text = Loc.Tr("ui.breeding.time.estimate.hours", FormatGameDuration(mins));
    }

    private static void SetSlot(VisualElement slot, Label nameLabel, VisualElement img, CreatureDNA dna)
    {
        slot?.EnableInClassList(Empty, dna == null);
        if (nameLabel != null) nameLabel.text = dna != null ? dna.CustomName : Loc.Tr("ui.breeding.slot.empty");
        if (img == null) return;
        if (dna != null) MonchiPortraitUI.Apply(img, dna);
        else
        {
            img.style.backgroundImage = StyleKeyword.Null;
            img.style.backgroundColor = Color.clear;
        }
    }

    private static string FormatGameDuration(int minutes)
    {
        minutes = Mathf.Max(0, minutes);
        int h = minutes / 60;
        int m = minutes % 60;
        return $"{h}h {m:00}m";
    }

    private void Assign(string id)
    {
        if (filter == CreatureGender.Male)
        {
            selectedFatherId = id;
            if (string.IsNullOrEmpty(selectedMotherId)) { filter = CreatureGender.Female; gridIndex = 0; }
        }
        else
        {
            selectedMotherId = id;
            if (string.IsNullOrEmpty(selectedFatherId)) { filter = CreatureGender.Male; gridIndex = 0; }
        }
        RebuildGrid();
        RefreshSlots();
    }

    private void TryBreed()
    {
        if (string.IsNullOrEmpty(selectedFatherId) || string.IsNullOrEmpty(selectedMotherId))
        {
            Debug.LogWarning("[BreedingPanel] Select a Father and a Mother first.");
            return;
        }
        if (incubation == null)
        {
            Debug.LogError("[BreedingPanel] IncubationService not assigned.");
            return;
        }

        string motherId = selectedMotherId, fatherId = selectedFatherId;

        bool started = incubation.StartBreeding(motherId, fatherId);

        if (started)
        {
            selectedFatherId = selectedMotherId = "";
            filter = CreatureGender.Male;
            gridIndex = 0;
            focus = SubFocus.Grid;
            RebuildGrid();
            RefreshSlots();
            onBred();
        }
    }

    private void ApplyFocusIfActive()
    {
        if (focusVisible) ApplyFocus();
    }

    private void ApplyFocus()
    {
        focusVisible = true;
        bool onGrid = focus == SubFocus.Grid;
        UiPanels.SetActiveIndex(tiles, onGrid ? gridIndex : -1, Focus);
        breedButton?.EnableInClassList(Focus, !onGrid);
        if (onGrid && gridIndex >= 0 && gridIndex < tiles.Count) grid?.ScrollTo(tiles[gridIndex]);
    }
}
}
