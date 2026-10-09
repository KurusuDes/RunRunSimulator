using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
public class BrawlOverheads : MonoBehaviour
{
    private const int PoolSize = 40;
    private const float AnchorHalf = 120f;
    private const float FloatSeconds = 0.8f;
    private const float FloatRise = 50f;
    private const float FloatJitter = 34f;
    private const float FloatLane = 18f;
    private const float BigDamage = 1000f;
    private const float BubbleTail = 0.7f;
    private const float PopHalf = 0.12f;
    private const string VariantHit = "brawl-float--hit";
    private const string VariantSkill = "brawl-float--skill";
    private const string VariantBig = "brawl-float--big";
    private const string VariantHeal = "brawl-float--heal";
    private const string VariantShield = "brawl-float--shield";

    private class Plate
    {
        public BrawlFighter Fighter;
        public VisualElement Anchor;
        public VisualElement Body;
        public VisualElement Fill;
        public VisualElement Shield;
        public Label Status;
        public VisualElement Bubble;
        public Image BubbleIcon;
        public Label BubbleText;
        public Vector2 LastPos;
        public float LastHp = -1f;
        public float LastShield = -1f;
        public float LastScale = 1f;
        public int LastStatus;
        public bool Shown;
        public bool Alive = true;
        public float BubbleStart;
        public float BubbleEnd = -1f;
    }

    private class FloatText
    {
        public VisualElement Anchor;
        public Label Label;
        public string Variant;
        public Vector3 World;
        public float Start;
        public float Jitter;
        public float Lane;
        public bool Active;
    }

    [Required, SerializeField] private UIDocument document;
    [Required, SerializeField] private BrawlTuningSO tuning;
    [SerializeField] private float headOffset = 1.5f;

    private readonly Dictionary<BrawlFighter, Plate> plates = new();
    private readonly FloatText[] pool = new FloatText[PoolSize];

    private VisualElement layer;
    private VisualElement platesGroup;
    private VisualElement floatsGroup;
    private int spawned;

    private void OnEnable()
    {
        BrawlMatch.OnRosterSpawned += HandleRoster;
        BrawlFighter.OnDamaged += HandleDamaged;
        BrawlFighter.OnHealed += HandleHealed;
        BrawlFighter.OnShielded += HandleShielded;
        BrawlSkillCaster.OnCastStarted += HandleCastStarted;
        TryBind();
    }

    private void OnDisable()
    {
        BrawlMatch.OnRosterSpawned -= HandleRoster;
        BrawlFighter.OnDamaged -= HandleDamaged;
        BrawlFighter.OnHealed -= HandleHealed;
        BrawlFighter.OnShielded -= HandleShielded;
        BrawlSkillCaster.OnCastStarted -= HandleCastStarted;
        Unbind();
    }

    private bool TryBind()
    {
        var docRoot = document != null ? document.rootVisualElement : null;
        if (docRoot == null) return false;
        if (layer != null && layer.parent == docRoot) return true;

        Unbind();
        layer = new VisualElement { name = "brawl-overheads", pickingMode = PickingMode.Ignore };
        layer.AddToClassList("mm-theme");
        layer.AddToClassList("mm-theme--night");
        layer.AddToClassList("brawl-overheads");
        platesGroup = Element("brawl-overheads__group");
        floatsGroup = Element("brawl-overheads__group");
        layer.Add(platesGroup);
        layer.Add(floatsGroup);
        for (int i = 0; i < pool.Length; i++) pool[i] = BuildFloat();
        docRoot.Insert(0, layer);

        var match = BrawlMatch.Current;
        if (match != null) Rebuild(match.Fighters);
        return true;
    }

    private void Unbind()
    {
        plates.Clear();
        if (layer != null) layer.RemoveFromHierarchy();
        layer = null;
        platesGroup = null;
        floatsGroup = null;
        System.Array.Clear(pool, 0, pool.Length);
    }

    private void HandleRoster(IReadOnlyList<BrawlFighter> fighters)
    {
        if (!TryBind()) return;
        Rebuild(fighters);
    }

    private void Rebuild(IReadOnlyList<BrawlFighter> fighters)
    {
        plates.Clear();
        platesGroup.Clear();
        for (int i = 0; i < pool.Length; i++) HideFloat(pool[i]);
        if (fighters == null) return;

        for (int i = 0; i < fighters.Count; i++)
        {
            var fighter = fighters[i];
            if (fighter == null) continue;
            var plate = BuildPlate(fighter);
            plates[fighter] = plate;
            platesGroup.Add(plate.Anchor);
        }
    }

    private Plate BuildPlate(BrawlFighter fighter)
    {
        Color team = tuning.TeamColor(fighter.Team);
        var plate = new Plate { Fighter = fighter };

        plate.Anchor = Element("brawl-anchor");
        plate.Anchor.visible = false;
        plate.Body = Element("brawl-plate");

        if (!fighter.Dummy)
        {
            var name = MakeLabel(fighter.DisplayName, "brawl-plate__name");
            name.style.color = team;
            plate.Body.Add(name);
        }

        var bar = Element("brawl-obar");
        plate.Fill = Element("brawl-obar__fill");
        plate.Fill.style.backgroundColor = team;
        plate.Shield = Element("brawl-obar__shield");
        bar.Add(plate.Fill);
        bar.Add(plate.Shield);
        plate.Body.Add(bar);

        plate.Status = MakeLabel("", "brawl-plate__status");
        plate.Body.Add(plate.Status);
        plate.Anchor.Add(plate.Body);

        var row = Element("brawl-bubble-row");
        plate.Bubble = Element("brawl-bubble");
        plate.BubbleIcon = new Image { scaleMode = ScaleMode.ScaleToFit, pickingMode = PickingMode.Ignore };
        plate.BubbleIcon.AddToClassList("brawl-bubble__icon");
        plate.BubbleText = MakeLabel("", "brawl-bubble__text");
        plate.Bubble.Add(plate.BubbleIcon);
        plate.Bubble.Add(plate.BubbleText);
        row.Add(plate.Bubble);
        plate.Anchor.Add(row);

        return plate;
    }

    private FloatText BuildFloat()
    {
        var item = new FloatText { Anchor = Element("brawl-anchor"), Label = MakeLabel("", "brawl-float") };
        item.Label.style.opacity = 0f;
        item.Anchor.Add(item.Label);
        floatsGroup.Add(item.Anchor);
        return item;
    }

    private void HandleDamaged(BrawlFighter victim, BrawlHit hit)
    {
        if (hit.IsDrain || victim == null) return;
        int amount = Mathf.RoundToInt(hit.Amount);
        if (amount <= 0) return;

        string variant = hit.Amount >= BigDamage ? VariantBig : hit.FromSkill ? VariantSkill : VariantHit;
        SpawnFloat(hit.Point != Vector3.zero ? hit.Point : victim.Center, "-" + amount, variant);
    }

    private void HandleHealed(BrawlFighter target, float amount, BrawlFighter source)
    {
        int value = Mathf.RoundToInt(amount);
        if (target != null && value > 0) SpawnFloat(target.Center, "+" + value, VariantHeal);
    }

    private void HandleShielded(BrawlFighter target, float amount)
    {
        if (target != null) SpawnFloat(target.Center, "escudo", VariantShield);
    }

    private void HandleCastStarted(BrawlFighter fighter, BrawlSkillSO skill, Vector3 aim)
    {
        if (skill == null || fighter == null || !plates.TryGetValue(fighter, out var plate)) return;

        var theme = fighter.HornSkill == skill ? fighter.HornTheme : fighter.BackTheme;
        var border = theme.Color;
        border.a = 1f;

        plate.BubbleIcon.sprite = theme.Icon;
        plate.BubbleIcon.tintColor = theme.Color;
        plate.BubbleIcon.style.display = theme.Icon != null ? DisplayStyle.Flex : DisplayStyle.None;
        plate.BubbleText.text = skill.Title + "!";
        plate.Bubble.style.borderTopColor = border;
        plate.Bubble.style.borderRightColor = border;
        plate.Bubble.style.borderBottomColor = border;
        plate.Bubble.style.borderLeftColor = border;

        plate.LastScale = PopScale(0f);
        plate.Bubble.style.scale = new Scale(new Vector3(plate.LastScale, plate.LastScale, 1f));
        plate.BubbleStart = Time.unscaledTime;
        plate.BubbleEnd = plate.BubbleStart + skill.Windup + BubbleTail;
        plate.Bubble.AddToClassList("brawl-bubble--show");
    }

    private void SpawnFloat(Vector3 world, string text, string variant)
    {
        if (layer == null) return;

        var item = pool[spawned % pool.Length];
        spawned++;
        if (item.Variant != variant)
        {
            if (item.Variant != null) item.Label.RemoveFromClassList(item.Variant);
            item.Label.AddToClassList(variant);
            item.Variant = variant;
        }

        item.Label.text = text;
        item.Label.style.opacity = 0f;
        item.World = world;
        item.Start = Time.unscaledTime;
        item.Jitter = (Mathf.Repeat(spawned * 0.618034f, 1f) * 2f - 1f) * FloatJitter;
        item.Lane = (spawned % 3) * FloatLane;
        item.Active = true;
    }

    private void LateUpdate()
    {
        if (!TryBind()) return;

        var cam = Camera.main;
        var panel = layer.panel;
        if (cam == null || panel == null) return;

        var camTransform = cam.transform;
        Vector3 camPos = camTransform.position;
        Vector3 camFwd = camTransform.forward;
        float now = Time.unscaledTime;

        foreach (var plate in plates.Values) UpdatePlate(plate, cam, panel, camPos, camFwd, now);
        for (int i = 0; i < pool.Length; i++)
        {
            if (pool[i].Active) UpdateFloat(pool[i], cam, panel, camPos, camFwd, now);
        }
    }

    private void UpdatePlate(Plate plate, Camera cam, IPanel panel, Vector3 camPos, Vector3 camFwd, float now)
    {
        var fighter = plate.Fighter;
        bool present = fighter != null;
        Vector3 world = present ? fighter.Center + Vector3.up * headOffset : Vector3.zero;
        bool front = present && Vector3.Dot(camFwd, world - camPos) > 0.1f;
        if (front != plate.Shown)
        {
            plate.Shown = front;
            plate.Anchor.visible = front;
        }
        if (!front) return;

        Vector2 pos = RuntimePanelUtils.CameraTransformWorldToPanel(panel, world, cam);
        pos.x -= AnchorHalf;
        if ((pos - plate.LastPos).sqrMagnitude > 0.04f)
        {
            plate.LastPos = pos;
            plate.Anchor.style.translate = new Translate(pos.x, pos.y);
        }

        bool alive = fighter.IsAlive;
        if (alive != plate.Alive)
        {
            plate.Alive = alive;
            plate.Body.EnableInClassList("brawl-plate--ko", !alive);
        }

        float hp01 = fighter.Hp01;
        if (Changed(hp01, plate.LastHp))
        {
            plate.LastHp = hp01;
            plate.Fill.style.width = Length.Percent(hp01 * 100f);
        }

        float shield01 = fighter.MaxHp > 0f ? Mathf.Clamp01(fighter.Shield / fighter.MaxHp) : 0f;
        if (Changed(shield01, plate.LastShield))
        {
            plate.LastShield = shield01;
            plate.Shield.style.width = Length.Percent(shield01 * 100f);
        }

        int status = fighter.IsStunned ? 1 : fighter.Taunter != null ? 2 : 0;
        if (status != plate.LastStatus)
        {
            plate.LastStatus = status;
            plate.Status.text = status == 1 ? "aturdido" : status == 2 ? "provocado" : "";
        }

        UpdateBubble(plate, alive, now);
    }

    private void UpdateBubble(Plate plate, bool alive, float now)
    {
        if (plate.BubbleEnd < 0f) return;

        if (!alive || now >= plate.BubbleEnd)
        {
            plate.BubbleEnd = -1f;
            plate.Bubble.RemoveFromClassList("brawl-bubble--show");
            return;
        }

        float scale = PopScale(now - plate.BubbleStart);
        if (Mathf.Abs(scale - plate.LastScale) < 0.005f) return;
        plate.LastScale = scale;
        plate.Bubble.style.scale = new Scale(new Vector3(scale, scale, 1f));
    }

    private void UpdateFloat(FloatText item, Camera cam, IPanel panel, Vector3 camPos, Vector3 camFwd, float now)
    {
        float t = (now - item.Start) / FloatSeconds;
        if (t >= 1f)
        {
            HideFloat(item);
            return;
        }

        if (Vector3.Dot(camFwd, item.World - camPos) <= 0.1f)
        {
            item.Label.style.opacity = 0f;
            return;
        }

        Vector2 pos = RuntimePanelUtils.CameraTransformWorldToPanel(panel, item.World, cam);
        float rise = FloatRise * (1f - (1f - t) * (1f - t));
        item.Anchor.style.translate = new Translate(pos.x - AnchorHalf + item.Jitter, pos.y - rise - item.Lane);
        item.Label.style.opacity = t < 0.5f ? 1f : 1f - (t - 0.5f) * 2f;
    }

    private static void HideFloat(FloatText item)
    {
        item.Active = false;
        item.Label.style.opacity = 0f;
    }

    private static float PopScale(float age)
    {
        if (age < PopHalf) return Mathf.Lerp(0.6f, 1.1f, age / PopHalf);
        if (age < PopHalf * 2f) return Mathf.Lerp(1.1f, 1f, (age - PopHalf) / PopHalf);
        return 1f;
    }

    private static bool Changed(float value, float last) => Mathf.Abs(value - last) > 0.001f || (value <= 0f) != (last <= 0f);

    private static VisualElement Element(string className)
    {
        var element = new VisualElement { pickingMode = PickingMode.Ignore };
        element.AddToClassList(className);
        return element;
    }

    private static Label MakeLabel(string text, string className)
    {
        var label = new Label(text) { pickingMode = PickingMode.Ignore };
        label.AddToClassList(className);
        return label;
    }
}
}
