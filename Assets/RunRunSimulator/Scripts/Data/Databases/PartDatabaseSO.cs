using System.Collections.Generic;
using System.Linq;
using Sirenix.OdinInspector;
using Sirenix.Serialization;
using UnityEngine;
namespace MoriMonchiSimulator
{

public abstract class PartDatabaseSO<T> : KeyedDatabaseSO<T> where T : BodyPart
{
    [Title("Parts Dictionary", "Primary data source — add and edit entries here.")]
    [Searchable]
    [DictionaryDrawerSettings(
        KeyLabel = "ID",
        ValueLabel = "Part",
        DisplayMode = DictionaryDisplayOptions.ExpandedFoldout)]
    [OdinSerialize]
    [PreviouslySerializedAs("_parts")]
    private Dictionary<string, T> parts = new Dictionary<string, T>();

    protected override Dictionary<string, T> Entries => parts;

    protected override void SetEntryID(T entry, string id) => entry.ID = id;

    public T GetPartByID(string id) => GetByID(id);

    public T GetRandomPart(Rarity? rarityFilter = null, PartSetSO setFilter = null)
    {
        var pool = parts.Values.Where(p => p != null);

        if (rarityFilter.HasValue) pool = pool.Where(p => p.Rarity == rarityFilter.Value);
        if (setFilter != null)     pool = pool.Where(p => p.Set    == setFilter);

        var list = pool.ToList();
        return list.Count > 0 ? list[Random.Range(0, list.Count)] : null;
    }

    public Dictionary<string, T> Parts => parts;

    [ShowInInspector, ReadOnly, LabelText("Total Parts")]
    public int PartCount => parts?.Count ?? 0;

    [Title("Parts Overview")]
    [ShowInInspector, ReadOnly]
    [TableList(AlwaysExpanded = false, DrawScrollView = true, MaxScrollViewHeight = 300)]
    public List<T> PartsTable => parts?.Values.Where(p => p != null).ToList() ?? new List<T>();
}
}
