using System.Collections.Generic;
using System.Globalization;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
public class BrawlHud : MonoBehaviour
{
    private const int FeedMax = 5;
    private const long FeedLifeMs = 7000;
    private const long PopReleaseMs = 60;
    private const float FightHold = 0.9f;
    private const float SuddenHold = 1.6f;

    private static readonly string[] BannerClasses = { "brawl-banner--ink", "brawl-banner--blue", "brawl-banner--red", "brawl-banner--coral" };
    private static readonly NumberFormatInfo GroupFormat = new NumberFormatInfo { NumberGroupSeparator = "." };

    [Required, SerializeField] private UIDocument document;
    [Required, SerializeField] private BrawlTuningSO tuning;
    [SerializeField] private ArenaClockControl clock;
    [SerializeField] private ArenaPaletteApplier palette;
    [SerializeField] private BrawlTrialRoom trial;

    private readonly Dictionary<BrawlFighter, BrawlHudCard> cards = new();

    private BrawlHudClock hudClock;
    private VisualElement boundRoot;
    private VisualElement root;
    private VisualElement blueCards;
    private VisualElement redCards;
    private VisualElement feed;
    private VisualElement bannerBox;
    private Label phaseLabel;
    private Label matchLabel;
    private Label banner;
    private Label bannerSub;
    private Button newButton;
    private Button rematchButton;
    private IVisualElementScheduledItem popRelease;
    private float bannerHideAt = float.PositiveInfinity;
    private bool rivalHidden;
    private int lastCount = -1;
    private int lastPhase = -1;
    private int lastMatchIndex = -1;
    private int lastSeed;
    private int lastPalette = -2;

    private void OnEnable()
    {
        BrawlMatch.OnRosterSpawned += HandleRoster;
        BrawlMatch.OnPhaseChanged += HandlePhase;
        BrawlMatch.OnMatchEnded += HandleEnded;
        BrawlFighter.OnKnockedOut += HandleKnockedOut;
        BrawlSkillCaster.OnCastFired += HandleCastFired;
        BrawlMatch.OnLastStand += HandleLastStand;
        TryBind();
    }

    private void OnDisable()
    {
        BrawlMatch.OnRosterSpawned -= HandleRoster;
        BrawlMatch.OnPhaseChanged -= HandlePhase;
        BrawlMatch.OnMatchEnded -= HandleEnded;
        BrawlFighter.OnKnockedOut -= HandleKnockedOut;
        BrawlSkillCaster.OnCastFired -= HandleCastFired;
        BrawlMatch.OnLastStand -= HandleLastStand;
        Unbind();
    }

    private bool TryBind()
    {
        var docRoot = document != null ? document.rootVisualElement : null;
        if (docRoot == null) return false;
        if (root != null && docRoot == boundRoot) return true;

        Unbind();
        var found = docRoot.Q("brawl-root");
        if (found == null) return false;

        boundRoot = docRoot;
        root = found;
        blueCards = root.Q("brawl-cards-blue");
        redCards = root.Q("brawl-cards-red");
        feed = root.Q("brawl-feed");
        bannerBox = root.Q("brawl-banner-box");
        phaseLabel = root.Q<Label>("brawl-phase");
        matchLabel = root.Q<Label>("brawl-match");
        banner = root.Q<Label>("brawl-banner");
        bannerSub = root.Q<Label>("brawl-banner-sub");
        newButton = root.Q<Button>("brawl-new");
        rematchButton = root.Q<Button>("brawl-rematch");

        newButton.clicked += OnNewClicked;
        rematchButton.clicked += OnRematchClicked;

        hudClock = new BrawlHudClock(clock, trial);
        hudClock.Bind(root);

        redCards.style.display = DisplayStyle.Flex;
        rivalHidden = false;
        lastCount = lastPhase = lastMatchIndex = -1;
        lastPalette = -2;
        bannerHideAt = float.PositiveInfinity;

        var match = BrawlMatch.Current;
        if (match != null) RebuildCards(match.Fighters);
        return true;
    }

    private void Unbind()
    {
        if (root != null)
        {
            newButton.clicked -= OnNewClicked;
            rematchButton.clicked -= OnRematchClicked;
            hudClock?.Unbind();
            blueCards.Clear();
            redCards.Clear();
            feed.Clear();
        }

        popRelease?.Pause();
        popRelease = null;
        hudClock = null;
        cards.Clear();
        boundRoot = null;
        root = null;
    }

    private void OnNewClicked() => BrawlMatch.Current?.NewMatch();

    private void OnRematchClicked() => BrawlMatch.Current?.Rematch();

    private void HandleRoster(IReadOnlyList<BrawlFighter> fighters)
    {
        if (!TryBind()) return;
        lastCount = -1;
        HideBanner();
        RebuildCards(fighters);
    }

    private void RebuildCards(IReadOnlyList<BrawlFighter> fighters)
    {
        var buttons = BrawlMatch.Current != null && BrawlMatch.Current.Driven ? DisplayStyle.None : DisplayStyle.Flex;
        newButton.style.display = buttons;
        rematchButton.style.display = buttons;
        cards.Clear();
        blueCards.Clear();
        redCards.Clear();
        feed.Clear();
        if (fighters == null) return;

        for (int i = 0; i < fighters.Count; i++)
        {
            var fighter = fighters[i];
            if (fighter == null) continue;

            VisualElement column;
            if (fighter.Team == ExpeditionTeam.Player) column = blueCards;
            else if (fighter.Team == ExpeditionTeam.Rival) column = redCards;
            else continue;

            var card = new BrawlHudCard(fighter, tuning);
            cards[fighter] = card;
            column.Add(card.Root);
        }
    }

    private void HandlePhase(BrawlMatchPhase phase)
    {
        if (!TryBind()) return;
        switch (phase)
        {
            case BrawlMatchPhase.Idle:
            case BrawlMatchPhase.Countdown:
                lastCount = -1;
                HideBanner();
                break;
            case BrawlMatchPhase.Fight:
                ShowBanner("¡A PELEAR!", "", "brawl-banner--ink", FightHold);
                break;
            case BrawlMatchPhase.SuddenDeath:
                ShowBanner("¡MUERTE SÚBITA!", "la vida baja para todos", "brawl-banner--coral", SuddenHold);
                break;
        }
    }

    private void HandleLastStand(BrawlFighter survivor)
    {
        if (!TryBind() || survivor == null) return;
        string colorClass = survivor.Team == ExpeditionTeam.Player ? "brawl-banner--blue" : "brawl-banner--red";
        ShowBanner("¡ÚLTIMO EN PIE!", survivor.DisplayName + " no se rinde", colorClass, SuddenHold);
    }

    private void HandleEnded(ExpeditionTeam winner)
    {
        if (!TryBind()) return;
        var (text, colorClass) = winner switch
        {
            ExpeditionTeam.Player => ("¡GANA AZUL!", "brawl-banner--blue"),
            ExpeditionTeam.Rival => ("¡GANA ROJO!", "brawl-banner--red"),
            _ => ("¡EMPATE!", "brawl-banner--ink")
        };
        ShowBanner(text, MvpText(BrawlMatch.Current), colorClass, float.PositiveInfinity);
    }

    private void HandleKnockedOut(BrawlFighter victim, BrawlFighter killer)
    {
        if (root == null || victim == null) return;

        var entry = Element("brawl-feed__entry");
        entry.Add(Element("brawl-bg"));
        if (killer != null)
        {
            entry.Add(NameLabel(killer));
            var theme = killer.WingTheme;
            if (theme.Icon != null)
            {
                var icon = new Image { sprite = theme.Icon, scaleMode = ScaleMode.ScaleToFit, tintColor = theme.Color, pickingMode = PickingMode.Ignore };
                icon.AddToClassList("brawl-feed__icon");
                entry.Add(icon);
            }
            entry.Add(MakeLabel("derribó a", "brawl-feed__verb"));
            entry.Add(NameLabel(victim));
        }
        else
        {
            entry.Add(NameLabel(victim));
            entry.Add(MakeLabel("cayó", "brawl-feed__verb"));
        }

        feed.Add(entry);
        while (feed.childCount > FeedMax) feed[0].RemoveFromHierarchy();
        entry.schedule.Execute(entry.RemoveFromHierarchy).StartingIn(FeedLifeMs);
    }

    private void HandleCastFired(BrawlFighter fighter, BrawlSkillSO skill, Vector3 aim)
    {
        if (fighter == null || !cards.TryGetValue(fighter, out var card)) return;
        card.PulseSkill(fighter.HornSkill == skill ? 0 : 1);
    }

    private Label NameLabel(BrawlFighter fighter)
    {
        var label = MakeLabel(fighter.DisplayName, "brawl-feed__name");
        label.style.color = tuning.TeamColor(fighter.Team);
        return label;
    }

    private void Update()
    {
        if (!TryBind()) return;

        var match = BrawlMatch.Current;
        if (match == null) return;

        hudClock.Refresh(match);
        RefreshRivalCards();
        RefreshPhase(match);
        RefreshMatch(match);
        RefreshCountdown(match);

        if (Time.unscaledTime >= bannerHideAt) HideBanner();

        foreach (var card in cards.Values) card.Refresh();
    }

    private void RefreshRivalCards()
    {
        bool hidden = trial != null && trial.Active;
        if (hidden == rivalHidden) return;
        rivalHidden = hidden;
        redCards.style.display = hidden ? DisplayStyle.None : DisplayStyle.Flex;
    }

    private void RefreshPhase(BrawlMatch match)
    {
        int phase = (int)match.Phase * 100 + match.KnockOuts;
        if (phase == lastPhase) return;
        lastPhase = phase;
        string label = match.Phase switch
        {
            BrawlMatchPhase.Countdown => "PREPARADOS",
            BrawlMatchPhase.Fight => "PELEA",
            BrawlMatchPhase.SuddenDeath => "MUERTE SÚBITA",
            BrawlMatchPhase.Ended => "FIN",
            _ => ""
        };
        bool live = match.Phase == BrawlMatchPhase.Fight || match.Phase == BrawlMatchPhase.SuddenDeath;
        if (live && match.KnockOuts > 0) label += " · daño ×" + match.DamageRamp.ToString("0.##");
        phaseLabel.text = label;
    }

    private void RefreshMatch(BrawlMatch match)
    {
        int paletteIndex = palette != null ? palette.CurrentIndex : -1;
        if (match.MatchIndex == lastMatchIndex && match.Seed == lastSeed && paletteIndex == lastPalette) return;
        lastMatchIndex = match.MatchIndex;
        lastSeed = match.Seed;
        lastPalette = paletteIndex;

        string biome = palette != null && palette.Current != null ? " · " + palette.Current.DisplayName : "";
        matchLabel.text = "Partida " + match.MatchIndex + " · semilla " + match.Seed + biome;
    }

    private void RefreshCountdown(BrawlMatch match)
    {
        if (match.Phase != BrawlMatchPhase.Countdown) return;
        int count = Mathf.Max(1, Mathf.CeilToInt(tuning.CountdownSeconds - match.PhaseTime));
        if (count == lastCount) return;
        lastCount = count;
        ShowBanner(count.ToString(), "", "brawl-banner--ink", float.PositiveInfinity);
    }

    private void ShowBanner(string text, string sub, string colorClass, float holdSeconds)
    {
        banner.text = text;
        bannerSub.text = sub;
        for (int i = 0; i < BannerClasses.Length; i++)
            banner.EnableInClassList(BannerClasses[i], BannerClasses[i] == colorClass);

        bannerBox.AddToClassList("brawl-banner-box--show");
        popRelease?.Pause();
        banner.AddToClassList("brawl-banner--pop");
        popRelease = banner.schedule.Execute(ReleasePop).StartingIn(PopReleaseMs);
        bannerHideAt = float.IsPositiveInfinity(holdSeconds) ? float.PositiveInfinity : Time.unscaledTime + holdSeconds;
    }

    private void ReleasePop() => banner.RemoveFromClassList("brawl-banner--pop");

    private void HideBanner()
    {
        bannerHideAt = float.PositiveInfinity;
        if (bannerBox != null) bannerBox.RemoveFromClassList("brawl-banner-box--show");
    }

    private static string MvpText(BrawlMatch match)
    {
        if (match == null) return "";

        BrawlFighter best = null;
        var fighters = match.Fighters;
        for (int i = 0; i < fighters.Count; i++)
        {
            var fighter = fighters[i];
            if (fighter == null) continue;
            if (best == null || fighter.DamageDealt > best.DamageDealt) best = fighter;
        }
        if (best == null) return "";

        return "MVP: " + best.DisplayName + " · " + Grouped(best.DamageDealt) + " de daño · " + Grouped(best.HealingDone) + " de curación · " + best.KOs + " KO";
    }

    private static string Grouped(float value) => Mathf.RoundToInt(value).ToString("N0", GroupFormat);

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
