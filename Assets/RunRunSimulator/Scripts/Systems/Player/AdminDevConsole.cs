using Sirenix.OdinInspector;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class AdminDevConsole : MonoBehaviour
{
    [Required, SerializeField] private CloudSyncService cloudSync;
    [Required, SerializeField] private StarterKitService starterKit;
    [SerializeField] private UncleRescueService uncleRescue;

    [Button("Set Dabloons")]
    public void SetDabloons(int amount) => SetBalance(Currency.Dabloons, amount);

    [Button("Set Minerita")]
    public void SetMinerita(int amount) => SetBalance(Currency.Minerita, amount);

    [Button("Reset Save", ButtonSizes.Large), GUIColor(0.9f, 0.2f, 0.2f)]
    public async void ResetSave()
    {
        if (!CanMutate()) return;
        await cloudSync.ResetProgressAsync();
        bool applied = starterKit.TryApply();
        Debug.Log($"[AdminDev] ResetSave terminado, kit aplicado: {applied}. Si no hay sesion de UGS el reset no hizo nada.");
    }

    [Button("Force Uncle Call")]
    public void ForceUncleCall()
    {
        if (!CanMutate()) return;
        uncleRescue?.ForceCall();
    }

    [Button("Dump")]
    public string Dump()
    {
        var gm = GameManager.Instance;
        if (!Application.isPlaying || gm == null) return "[AdminDev] solo en Play.";

        int alive = 0, gone = 0;
        foreach (var dna in gm.Registry.GetAll().Values)
        {
            if (dna.IsDead || dna.IsSold) gone++;
            else alive++;
        }

        string text = $"[AdminDev] Dabloons={Wallet.Balance(Currency.Dabloons)} Minerita={Wallet.Balance(Currency.Minerita)} vivos={alive} idos={gone} TutorialStep={gm.WorldState.TutorialStep} Day={gm.WorldState.Day} StartupSyncDone={cloudSync.StartupSyncDone} SoftBlocked={uncleRescue != null && uncleRescue.IsSoftBlocked()}";
        Debug.Log(text);
        return text;
    }

    private void SetBalance(Currency currency, int amount)
    {
        if (!CanMutate()) return;
        amount = Mathf.Max(0, amount);
        int current = Wallet.Balance(currency);
        if (amount > current) Wallet.Add(currency, amount - current, "admin");
        else if (amount < current) Wallet.TrySpend(currency, current - amount, "admin");
    }

    private static bool CanMutate()
    {
        if (Application.isPlaying) return true;
        Debug.LogWarning("[AdminDev] solo funciona en Play.");
        return false;
    }
}
}
