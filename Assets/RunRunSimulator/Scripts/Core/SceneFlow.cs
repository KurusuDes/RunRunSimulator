using UnityEngine;
using UnityEngine.SceneManagement;
namespace MoriMonchiSimulator
{

public static class SceneFlow
{
    public const string TitleScene = "Title";
    public const string StoreScene = "GameScene";
    public const string ArenaScene = "BrawlDemo";

    private static float defaultFixedDeltaTime;
    private static bool newGameRequested;

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
    private static void ResetState()
    {
        newGameRequested = false;
        defaultFixedDeltaTime = Time.fixedDeltaTime;
    }

    private static void ResetTime()
    {
        Time.timeScale = 1f;
        if (defaultFixedDeltaTime > 0f) Time.fixedDeltaTime = defaultFixedDeltaTime;
    }

    public static void Load(string scene)
    {
        ResetTime();
        SceneManager.LoadScene(scene);
    }

    public static void GoToTitle() => Load(TitleScene);
    public static void GoToStore() => Load(StoreScene);
    public static void GoToArena() => Load(ArenaScene);

    public static void RequestNewGame()
    {
        newGameRequested = true;
        GoToStore();
    }

    public static bool ConsumeNewGameRequest()
    {
        bool requested = newGameRequested;
        newGameRequested = false;
        return requested;
    }
}
}
