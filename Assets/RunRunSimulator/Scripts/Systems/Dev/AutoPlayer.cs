using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.SceneManagement;
namespace MoriMonchiSimulator
{

public class AutoPlayer : MonoBehaviour
{
    [SerializeField] private float arenaTimeScale = 4f;
    [SerializeField] private float stepTimeout = 60f;

    public static AutoPlayer Instance { get; private set; }

    public static int ResumeFromStep = 1;

    public string Status { get; internal set; } = "Idle";

    private bool running;
    private bool failed;
    private ArenaClockControl arenaClock;

    internal bool Failed      => failed;
    internal int  CurrentStep { get; set; }
    internal float StepTimeout => stepTimeout;

    internal readonly List<string> EggIds   = new List<string>();
    internal List<string>          SlimeIds = new List<string>();

    internal ExpeditionReturn? LastExpeditionReturn { get; private set; }
    internal int               LastRunMaterial      { get; private set; }
    internal bool              LastRunLost          { get; private set; }
    internal int               TotalExpeditions     { get; private set; }
    internal int               LostExpeditions      { get; private set; }

    internal CreatureDNA LastChild      { get; set; }
    internal CreatureDNA LastSoldDna    { get; set; }
    internal int         LastSalePrice  { get; private set; }

    private void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);
    }

    private void OnDestroy()
    {
        if (Instance == this) Instance = null;
    }

    private void OnEnable()
    {
        GameEvents.OnExpeditionReturned += HandleExpeditionReturned;
        GameEvents.OnBreedingCompleted  += HandleBreedingCompleted;
        GameEvents.OnCustomerSold       += HandleCustomerSold;
    }

    private void OnDisable()
    {
        GameEvents.OnExpeditionReturned -= HandleExpeditionReturned;
        GameEvents.OnBreedingCompleted  -= HandleBreedingCompleted;
        GameEvents.OnCustomerSold       -= HandleCustomerSold;
    }

    private void HandleExpeditionReturned(ExpeditionReturn r) => LastExpeditionReturn = r;

    private void HandleBreedingCompleted(CreatureDNA mother, CreatureDNA father, CreatureDNA child) => LastChild = child;

    private void HandleCustomerSold(NpcAgent agent, CreatureDNA dna, int finalPrice)
    {
        LastSoldDna   = dna;
        LastSalePrice = finalPrice;
    }

    private void Start()
    {
        if (!running) Run();
    }

    public void Run()
    {
        if (running) return;
        running = true;
        failed  = false;
        StartCoroutine(Sequence());
    }

    private IEnumerator Sequence()
    {
        var opening = new AutoPlayerOpeningSteps(this);
        var loop    = new AutoPlayerLoopSteps(this);

        int from = ResumeFromStep;

        if (from <= 1)  { yield return opening.Step1_Arrival();           if (failed) yield break; }
        if (from <= 2)  { yield return opening.Step2_BuyEggBox();         if (failed) yield break; }
        if (from <= 3)  { yield return opening.Step3_OpenBox();           if (failed) yield break; }
        if (from <= 4)  { yield return opening.Step4_PlaceIncubator();    if (failed) yield break; }
        if (from <= 5)  { yield return opening.Step5_EggsIntoIncubator(); if (failed) yield break; }
        if (from <= 6)  { yield return opening.Step6_HatchThree();        if (failed) yield break; }
        if (from <= 9)  { yield return opening.Step7to9_Expedition();     if (failed) yield break; }
        if (from <= 10) { yield return opening.Step10_HatchRemaining();   if (failed) yield break; }
        if (from <= 11) { yield return loop.Step11_BuyBreedingRoom();     if (failed) yield break; }
        if (from <= 12) { yield return loop.Step12_ExpeditionsUntilPair(); if (failed) yield break; }
        if (from <= 13) { yield return loop.Step13_Breed();               if (failed) yield break; }
        if (from <= 14) { yield return loop.Step14_Showcase();            if (failed) yield break; }
        if (from <= 15) { yield return loop.Step15_Sale();                if (failed) yield break; }
        if (from <= 16) { yield return loop.Step16_Upgrade();             if (failed) yield break; }
        loop.Step17_Fin();
        running = false;
    }

    internal IEnumerator PlayExpedition(List<string> teamIds)
    {
        LastExpeditionReturn = null;
        ExpeditionBridge.RequestDeparture(teamIds);

        yield return WaitFor(() => SceneManager.GetActiveScene().name == ExpeditionHandoff.ArenaScene, stepTimeout, "escena ArenaSandbox");
        if (failed) yield break;

        ArenaRound       round    = null;
        ArenaRunDirector director = null;
        yield return WaitFor(() =>
        {
            round    = FindFirstObjectByType<ArenaRound>();
            director = FindFirstObjectByType<ArenaRunDirector>();
            return round != null && director != null;
        }, stepTimeout, "ArenaRound/ArenaRunDirector en escena");
        if (failed) yield break;

        arenaClock = FindFirstObjectByType<ArenaClockControl>();
        SetSpeed(arenaTimeScale);

        if (!round.IsRunning && !round.IsOver) round.Launch();

        yield return WaitFor(() => director.FloorRecorded, 240f, "director.FloorRecorded");
        if (failed) yield break;

        LastRunMaterial = director.Run.Material;
        LastRunLost     = director.Run.Lost;
        Debug.Log($"[AutoPlayer] bajada · piso registrado · material={LastRunMaterial} perdida={LastRunLost}");

        RestoreSpeed();
        director.Retreat();

        yield return WaitFor(() => SceneManager.GetActiveScene().name == ExpeditionHandoff.StoreScene && LastExpeditionReturn.HasValue,
            stepTimeout, "vuelta a GameScene + OnExpeditionReturned");
        if (failed) yield break;

        Time.timeScale = 1f;

        TotalExpeditions++;
        if (LastRunLost) LostExpeditions++;
    }

    internal IEnumerator ExpeditionsUntil(Func<bool> goal, int maxRuns, string what, List<string> exclude = null)
    {
        int runs = 0;
        while (!goal())
        {
            var registry = GameManager.Instance.Registry;
            if (runs >= maxRuns)
            {
                Fail($"{what}: no se logro tras {runs} bajadas extra · minerita={Wallet.Balance(Currency.Minerita)} {AutoPlayerQuery.FormsSummary(registry)}");
                yield break;
            }

            var team = AutoPlayerQuery.BuildTeam(registry, 3, exclude);
            if (team.Count == 0)
            {
                Fail($"{what}: sin candidatos para bajar tras {runs} bajadas extra · minerita={Wallet.Balance(Currency.Minerita)} {AutoPlayerQuery.FormsSummary(registry)}");
                yield break;
            }

            yield return PlayExpedition(team);
            if (failed) yield break;

            runs++;
            Ok($"Bajada extra {runs}", $"equipo={string.Join(",", team)} material={LastRunMaterial} perdida={LastRunLost} minerita={Wallet.Balance(Currency.Minerita)} {AutoPlayerQuery.FormsSummary(GameManager.Instance.Registry)}");
        }
    }

    private void SetSpeed(float speed)
    {
        if (arenaClock != null) arenaClock.Set(speed);
        else Time.timeScale = speed;
    }

    private void RestoreSpeed()
    {
        SetSpeed(1f);
        arenaClock = null;
    }

    internal IEnumerator WaitFor(Func<bool> condition, float timeout, string what)
    {
        float elapsed = 0f;
        while (!condition())
        {
            if (elapsed >= timeout) { Fail($"{what} (timeout {timeout}s)"); yield break; }
            elapsed += Time.unscaledDeltaTime;
            yield return null;
        }
    }

    internal void Fail(string reason)
    {
        failed  = true;
        running = false;
        Status  = $"FALLA paso {CurrentStep} · {reason}";
        RestoreSpeed();
        Time.timeScale = 1f;
        Debug.LogError($"[AutoPlayer] FALLA paso {CurrentStep} · {reason}");
        Debug.Break();
    }

    internal void Ok(string name, string data)
    {
        Status = $"OK paso {CurrentStep} · {name} · {data}";
        Debug.Log($"[AutoPlayer] OK paso {CurrentStep} · {name} · {data}");
    }
}
}
