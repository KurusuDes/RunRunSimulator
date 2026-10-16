using System;
using UnityEngine;

namespace MoriMonchiSimulator
{
public class PlayerFocusProbe : MonoBehaviour
{
    public static event Action<FocusPrompt> Changed;
    public static FocusPrompt Current { get; private set; }
    public static IFocusLabel CurrentLabel { get; private set; }

    [SerializeField] private Transform cameraTransform;
    [SerializeField] private float range = 2.5f;
    [SerializeField] private LayerMask mask = ~0;
    [SerializeField] private float interval = 0.1f;

    private bool holding;
    private bool petting;
    private bool uiFocused;
    private float nextProbeTime;

    private void OnEnable()
    {
        PlayerController.HeldChanged += OnHeldChanged;
        PlayerController.PetChanged += OnPetChanged;
        UIManager.OnUIFocusChanged += OnUIFocusChanged;
        nextProbeTime = 0f;
    }

    private void OnDisable()
    {
        PlayerController.HeldChanged -= OnHeldChanged;
        PlayerController.PetChanged -= OnPetChanged;
        UIManager.OnUIFocusChanged -= OnUIFocusChanged;
        holding = false;
        petting = false;
        Set(FocusPrompt.None, null);
    }

    private void Update()
    {
        if (Time.unscaledTime < nextProbeTime) return;
        nextProbeTime = Time.unscaledTime + interval;
        var prompt = Compute(out var label);
        Set(prompt, label);
    }

    private void OnHeldChanged(Transform t) => holding = t != null;
    private void OnPetChanged(Transform t) => petting = t != null;
    private void OnUIFocusChanged(bool focused) => uiFocused = focused;

    private FocusPrompt Compute(out IFocusLabel label)
    {
        label = null;
        if (cameraTransform == null) return FocusPrompt.None;
        if (uiFocused || petting) return FocusPrompt.None;
        if (holding) return FocusPrompt.Carrying;

        var hits = Physics.RaycastAll(cameraTransform.position, cameraTransform.forward, range, mask, QueryTriggerInteraction.Collide);
        Array.Sort(hits, (a, b) => a.distance.CompareTo(b.distance));
        foreach (var hit in hits)
        {
            if (hit.collider.transform.IsChildOf(transform)) continue;
            label ??= hit.collider.GetComponentInParent<IFocusLabel>();
            if (hit.collider.GetComponentInParent<MoriMochiAgent>() != null) return FocusPrompt.Creature;
            if (hit.collider.GetComponentInParent<IInteractable>() != null) return FocusPrompt.Interactable;
            if (!hit.collider.isTrigger) break;
        }

        if (HotbarController.Instance != null && HotbarController.Instance.HasActiveItem) return FocusPrompt.Item;
        return FocusPrompt.None;
    }

    private static void Set(FocusPrompt value, IFocusLabel label)
    {
        bool same = Current == value && ReferenceEquals(CurrentLabel, label);
        Current = value;
        CurrentLabel = label;
        if (same) return;
        Changed?.Invoke(value);
    }
}
}
