using System;
using System.Collections.Generic;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{
[CreateAssetMenu(fileName = "HumanBodyCatalog", menuName = "RunRunSimulator/Customers/Human Body Catalog")]
public class HumanBodyCatalogSO : SerializedScriptableObject
{
    [Serializable]
    public class Entry
    {
        public CustomerArchetypeSO Archetype;
        public GameObject Body;
        public List<Material> Skins = new();
    }

    [Title("Bodies")]
    public List<Entry> Bodies = new();

    public bool TryPick(CustomerArchetypeSO archetype, out GameObject body, out Material skin)
    {
        body = null;
        skin = null;

        var valid = new List<Entry>();
        var matching = new List<Entry>();
        if (Bodies != null)
        {
            foreach (var e in Bodies)
            {
                if (e == null || e.Body == null) continue;
                valid.Add(e);
                if (archetype != null && e.Archetype == archetype) matching.Add(e);
            }
        }

        if (matching.Count > 0) valid = matching;

        if (valid.Count == 0)
        {
            Debug.LogWarning("[HumanBodyCatalogSO] No valid bodies configured.");
            return false;
        }

        var pick = valid[UnityEngine.Random.Range(0, valid.Count)];
        body = pick.Body;

        if (pick.Skins != null && pick.Skins.Count > 0)
            skin = pick.Skins[UnityEngine.Random.Range(0, pick.Skins.Count)];

        return true;
    }
}
}
