using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public static class SettingsRows
{
    private const string RowClass     = "set-row";
    private const string LabelClass   = "set-row__label";
    private const string ControlClass = "set-row__control";
    private const string ValueClass   = "set-row__value";

    public static string Percent(float value) => $"{Mathf.RoundToInt(value * 100f)} %";

    public static void AddHeader(VisualElement content, string titleKey)
    {
        var header = new Label(Loc.Tr(titleKey));
        header.AddToClassList("set-header");
        content.Add(header);
    }

    public static void AddNote(VisualElement content, string noteKey)
    {
        var note = new Label(Loc.Tr(noteKey));
        note.AddToClassList("set-note");
        content.Add(note);
    }

    public static void AddDropdown(VisualElement content, string labelKey, IList<string> choices, int index, Action<int> onChange)
    {
        if (choices == null || choices.Count == 0) return;

        var control = NewRow(content, labelKey);
        var field = new DropdownField(new List<string>(choices), Mathf.Clamp(index, 0, choices.Count - 1));
        field.AddToClassList("set-dropdown");
        field.RegisterValueChangedCallback(_ => onChange(field.index));
        control.Add(field);
    }

    public static void AddSlider(VisualElement content, string labelKey, float min, float max, float step,
                                 float value, Func<float, string> format, Action<float> onChange)
    {
        var control = NewRow(content, labelKey);

        var slider = new Slider(min, max);
        slider.AddToClassList("set-slider");
        slider.SetValueWithoutNotify(Snap(value, step, min, max));

        var valueLabel = new Label(format(slider.value));
        valueLabel.AddToClassList(ValueClass);

        slider.RegisterValueChangedCallback(evt =>
        {
            float snapped = Snap(evt.newValue, step, min, max);
            if (!Mathf.Approximately(snapped, evt.newValue)) slider.SetValueWithoutNotify(snapped);
            valueLabel.text = format(snapped);
            onChange(snapped);
        });

        control.Add(slider);
        control.Add(valueLabel);
    }

    public static void AddToggle(VisualElement content, string labelKey, bool value, Action<bool> onChange)
    {
        var control = NewRow(content, labelKey);
        var toggle = new Toggle();
        toggle.AddToClassList("set-toggle");
        toggle.SetValueWithoutNotify(value);
        toggle.RegisterValueChangedCallback(evt => onChange(evt.newValue));
        control.Add(toggle);
    }

    private static VisualElement NewRow(VisualElement content, string labelKey)
    {
        var row = new VisualElement();
        row.AddToClassList(RowClass);

        var label = new Label(Loc.Tr(labelKey));
        label.AddToClassList(LabelClass);
        row.Add(label);

        var control = new VisualElement();
        control.AddToClassList(ControlClass);
        row.Add(control);

        content.Add(row);
        return control;
    }

    private static float Snap(float value, float step, float min, float max)
    {
        float snapped = Mathf.Round(value / step) * step;
        return Mathf.Clamp(Mathf.Round(snapped * 1000f) / 1000f, min, max);
    }
}
}
