using UnityEngine;
namespace MoriMonchiSimulator
{

[CreateAssetMenu(fileName = "BrawlRoomGlyphs", menuName = "MoriMonchi/Brawl/Room Glyphs")]
public class BrawlRoomGlyphsSO : ScriptableObject
{
    [SerializeField] private Sprite skull1, skull2, skull3, mineral, heal;

    public Sprite For(BrawlRoom room)
    {
        switch (room.Kind)
        {
            case BrawlRoomKind.Dummies:
                return heal;
            case BrawlRoomKind.Minerals:
                return mineral;
            default:
                switch (Mathf.Clamp(room.Rivals, 1, 3))
                {
                    case 1: return skull1;
                    case 2: return skull2;
                    default: return skull3;
                }
        }
    }
}
}
