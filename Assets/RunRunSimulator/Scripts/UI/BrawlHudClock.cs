using System;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
public class BrawlHudClock
{
    private static readonly float[] SpeedValues = { 1f, 2f, 4f };
    private static readonly string[] SpeedNames = { "brawl-speed-1", "brawl-speed-2", "brawl-speed-4" };

    private readonly ArenaClockControl clock;
    private readonly BrawlTrialRoom trial;
    private readonly Button[] speedButtons = new Button[3];
    private readonly Action[] speedHandlers = new Action[3];

    private Label timerLabel;
    private int lastSeconds = -1;
    private int lastSpeed = -1;
    private bool lastSudden;

    public BrawlHudClock(ArenaClockControl clock, BrawlTrialRoom trial)
    {
        this.clock = clock;
        this.trial = trial;
    }

    public void Bind(VisualElement root)
    {
        timerLabel = root.Q<Label>("brawl-timer");
        for (int i = 0; i < speedButtons.Length; i++)
        {
            speedButtons[i] = root.Q<Button>(SpeedNames[i]);
            if (clock == null)
            {
                speedButtons[i].style.display = DisplayStyle.None;
                continue;
            }
            float value = SpeedValues[i];
            speedHandlers[i] = () => clock.Set(value);
            speedButtons[i].clicked += speedHandlers[i];
        }

        lastSeconds = lastSpeed = -1;
        lastSudden = false;
    }

    public void Unbind()
    {
        for (int i = 0; i < speedButtons.Length; i++)
        {
            if (speedButtons[i] != null && speedHandlers[i] != null) speedButtons[i].clicked -= speedHandlers[i];
            speedHandlers[i] = null;
            speedButtons[i] = null;
        }
        timerLabel = null;
    }

    public void Refresh(BrawlMatch match)
    {
        RefreshTime(match);
        RefreshSpeed();
    }

    private void RefreshTime(BrawlMatch match)
    {
        bool inTrial = trial != null && trial.Active;
        bool sudden = !inTrial && (match.Phase == BrawlMatchPhase.SuddenDeath || (match.Phase == BrawlMatchPhase.Ended && match.TimeLeft <= 0f));
        if (sudden != lastSudden)
        {
            lastSudden = sudden;
            lastSeconds = -1;
            timerLabel.EnableInClassList("brawl-timer--sudden", sudden);
        }

        int seconds;
        if (inTrial) seconds = Mathf.CeilToInt(Mathf.Max(0f, trial.TimeLeft));
        else if (sudden) seconds = Mathf.FloorToInt(match.SuddenDeathElapsed);
        else seconds = Mathf.CeilToInt(Mathf.Max(0f, match.TimeLeft));

        if (seconds == lastSeconds) return;
        lastSeconds = seconds;
        timerLabel.text = (sudden ? "+" : "") + seconds / 60 + ":" + (seconds % 60).ToString("00");
    }

    private void RefreshSpeed()
    {
        if (clock == null) return;
        int active = Mathf.RoundToInt(ArenaClockControl.Speed);
        if (active == lastSpeed) return;
        lastSpeed = active;
        for (int i = 0; i < speedButtons.Length; i++)
            speedButtons[i].EnableInClassList("brawl-btn--on", Mathf.RoundToInt(SpeedValues[i]) == active);
    }
}
}
