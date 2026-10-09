using MoreMountains.Feedbacks;
using Sirenix.OdinInspector;
using UnityEngine;
using UnityEngine.UIElements;

namespace MoriMonchiSimulator
{
public class BrawlRunVeil : MonoBehaviour
{
    private const string FoeClass = "run-glyph--foe";
    private const string HealClass = "run-glyph--heal";
    private const string MineralClass = "run-glyph--mineral";

    [Required, SerializeField] private UIDocument document;
    [Required, SerializeField] private BrawlRunDirector director;
    [Required, SerializeField] private BrawlRoomGlyphsSO glyphs;
    [SerializeField] private MMF_Player onShow;
    [SerializeField] private MMF_Player onHide;

    private VisualElement boundRoot;
    private VisualElement root;
    private VisualElement glyph;
    private VisualElement pips;
    private Label title;
    private Label left;
    private BrawlRunState previousState;

    private void OnEnable()
    {
        previousState = director != null ? director.State : BrawlRunState.Planning;
        if (director != null) director.Changed += HandleChanged;
        TryBind();
    }

    private void OnDisable()
    {
        if (director != null) director.Changed -= HandleChanged;
        Unbind();
    }

    private bool TryBind()
    {
        var docRoot = document != null ? document.rootVisualElement : null;
        if (docRoot == null || director == null) return false;
        if (root != null && docRoot == boundRoot) return true;

        Unbind();
        var found = docRoot.Q("run-root");
        if (found == null) return false;

        boundRoot = docRoot;
        root = found;
        glyph = root.Q("run-veil-glyph");
        title = root.Q<Label>("run-veil-title");
        pips = root.Q("run-veil-pips");
        left = root.Q<Label>("run-veil-left");
        return true;
    }

    private void Unbind()
    {
        if (root != null) pips.Clear();

        boundRoot = null;
        root = null;
    }

    private void HandleChanged()
    {
        var state = director.State;
        var before = previousState;
        previousState = state;

        if (!TryBind()) return;

        bool entering = state == BrawlRunState.Transition && before != BrawlRunState.Transition;
        bool leaving = before == BrawlRunState.Transition && state != BrawlRunState.Transition;

        if (entering)
        {
            var run = director.Active ? director.Run : null;
            if (run == null) return;
            Fill(run);
            if (onShow != null) onShow.PlayFeedbacks();
        }
        else if (leaving && onHide != null)
        {
            onHide.PlayFeedbacks();
        }
    }

    private void Fill(BrawlRun run)
    {
        var room = run.CurrentRoom;
        int count = run.Rooms.Count;

        glyph.style.backgroundImage = new StyleBackground(glyphs.For(room));
        glyph.RemoveFromClassList(FoeClass);
        glyph.RemoveFromClassList(HealClass);
        glyph.RemoveFromClassList(MineralClass);
        glyph.AddToClassList(room.Kind switch
        {
            BrawlRoomKind.Combat => FoeClass,
            BrawlRoomKind.Dummies => HealClass,
            _ => MineralClass
        });

        title.text = "Sala " + (run.RoomIndex + 1) + " de " + count;

        pips.Clear();
        for (int i = 0; i < count; i++)
        {
            var pip = new VisualElement { pickingMode = PickingMode.Ignore };
            pip.AddToClassList("run-pip");
            pip.AddToClassList(i < run.RoomIndex ? "run-pip--done" : i == run.RoomIndex ? "run-pip--current" : "run-pip--upcoming");
            pips.Add(pip);
        }

        int remaining = count - run.RoomIndex - 1;
        left.text = remaining <= 0 ? "Última sala del tramo" : remaining == 1 ? "Queda 1 más" : "Quedan " + remaining + " más";
    }
}
}
