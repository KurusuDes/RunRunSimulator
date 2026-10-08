using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using UnityEngine;
namespace MoriMonchiSimulator
{

[RequireComponent(typeof(BrawlBalanceRecorder))]
public class BrawlBalanceDev : MonoBehaviour
{
    private const float TimeoutMargin = 150f;
    private const int LogEvery = 10;

    private readonly List<Camera> disabledCameras = new();
    private readonly List<CreatureDNA> firstRoster = new();

    private BrawlBalanceRecorder recorder;
    private float previousCapture;
    private bool timeFixed;
    private float simTotal;
    private float realTotal;

    public bool IsRunning { get; private set; }
    public bool Done { get; private set; }
    public int Completed { get; private set; }
    public int Total { get; private set; }
    public string Folder { get; private set; }
    public string Progress { get; private set; }

    private void Awake()
    {
        recorder = GetComponent<BrawlBalanceRecorder>();
    }

    private void OnDisable()
    {
        if (!IsRunning) return;
        RestoreTime();
        IsRunning = false;
    }

    public void Run(string batch, int firstSeed, int seedCount, bool mirror = true, int simHz = 50, bool camerasOff = false)
    {
        if (IsRunning)
        {
            Debug.LogWarning("[BrawlBalanceDev] Ya hay una tanda corriendo.");
            return;
        }
        if (BrawlMatch.Current == null)
        {
            Debug.LogWarning("[BrawlBalanceDev] No hay BrawlMatch activo.");
            return;
        }
        StartCoroutine(Loop(BrawlMatch.Current, batch, firstSeed, seedCount, mirror, simHz, camerasOff));
    }

    public void Stop()
    {
        IsRunning = false;
    }

    private IEnumerator Loop(BrawlMatch match, string batch, int firstSeed, int seedCount, bool mirror, int simHz, bool camerasOff)
    {
        IsRunning = true;
        Done = false;
        Completed = 0;
        Total = seedCount * (mirror ? 2 : 1);
        Progress = "";
        simTotal = 0f;
        realTotal = 0f;

        Folder = Path.GetFullPath(Path.Combine(Application.dataPath, "..", "Recordings", "brawl_balance", batch));
        Directory.CreateDirectory(Folder);
        string matchesPath = Path.Combine(Folder, "matches.csv");
        string fightersPath = Path.Combine(Folder, "fighters.csv");
        if (!File.Exists(matchesPath))
            File.WriteAllText(matchesPath, BrawlBalanceRecorder.MatchHeader, Encoding.UTF8);
        if (!File.Exists(fightersPath))
            File.WriteAllText(fightersPath, BrawlBalanceRecorder.FighterHeader, Encoding.UTF8);

        FixTime(simHz, camerasOff);

        for (int seed = firstSeed; seed < firstSeed + seedCount && IsRunning; seed++)
        {
            yield return PlayMatch(match, batch, seed, false, matchesPath, fightersPath);
            yield return null;

            if (mirror && IsRunning)
            {
                yield return PlayMatch(match, batch, seed, true, matchesPath, fightersPath);
                yield return null;
            }
        }

        RestoreTime();
        IsRunning = false;
        Done = true;
        File.WriteAllText(Path.Combine(Folder, "done.txt"), Completed + " partidas · " + SpeedText(), Encoding.UTF8);
    }

    private IEnumerator PlayMatch(BrawlMatch match, string batch, int seed, bool mirrored, string matchesPath, string fightersPath)
    {
        float realStart = Time.realtimeSinceStartup;
        float simStart = Time.time;

        recorder.Arm(batch, seed, mirrored ? 1 : 0);
        if (mirrored)
        {
            match.StartMatch(seed, MirrorRoster());
        }
        else
        {
            match.StartMatch(seed);
            CaptureRoster(match);
        }

        float limit = match.Tuning.RoundSeconds + TimeoutMargin;
        while (IsRunning && !recorder.Done)
        {
            if (recorder.FightSeconds > limit)
            {
                recorder.ForceFinish();
                break;
            }
            yield return null;
        }
        if (!recorder.Done) yield break;

        float real = Time.realtimeSinceStartup - realStart;
        simTotal += Time.time - simStart;
        realTotal += real;

        File.AppendAllText(matchesPath, recorder.MatchLine(real), Encoding.UTF8);
        File.AppendAllText(fightersPath, recorder.FighterLines(), Encoding.UTF8);

        Completed++;
        Progress = Completed + "/" + Total + " · semilla " + seed;
        File.WriteAllText(Path.Combine(Folder, "progress.txt"), Progress, Encoding.UTF8);
        if (Completed % LogEvery == 0)
            Debug.Log("[BrawlBalanceDev] " + Progress + " · " + SpeedText());
    }

    private void CaptureRoster(BrawlMatch match)
    {
        firstRoster.Clear();
        foreach (var fighter in match.Fighters)
            firstRoster.Add(fighter.DNA);
    }

    private List<CreatureDNA> MirrorRoster()
    {
        int half = firstRoster.Count / 2;
        var mirrored = new List<CreatureDNA>(firstRoster.Count);
        for (int i = 0; i < half; i++)
            mirrored.Add(firstRoster[half + i]);
        for (int i = 0; i < half; i++)
            mirrored.Add(firstRoster[i]);
        return mirrored;
    }

    private void FixTime(int simHz, bool camerasOff)
    {
        previousCapture = Time.captureDeltaTime;
        Time.captureDeltaTime = 1f / Mathf.Max(1, simHz);
        Time.timeScale = 1f;
        Application.runInBackground = true;
        timeFixed = true;

        if (!camerasOff) return;
        foreach (var cam in Camera.allCameras)
        {
            if (!cam.enabled) continue;
            cam.enabled = false;
            disabledCameras.Add(cam);
        }
    }

    private void RestoreTime()
    {
        if (!timeFixed) return;
        Time.captureDeltaTime = previousCapture;
        foreach (var cam in disabledCameras)
            if (cam != null) cam.enabled = true;
        disabledCameras.Clear();
        timeFixed = false;
    }

    private string SpeedText()
    {
        float speed = realTotal > 0f ? simTotal / realTotal : 0f;
        return "velocidad x" + speed.ToString("0.0", CultureInfo.InvariantCulture);
    }
}
}
