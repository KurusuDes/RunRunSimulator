var sbx = UnityEngine.Object.FindFirstObjectByType<MoriMonchiSimulator.ArenaSandbox>();
var dev = UnityEngine.Object.FindFirstObjectByType<MoriMonchiSimulator.ArenaClashDev>();
var tun = (MoriMonchiSimulator.ClashTuningSO)dev.GetType().GetField("tuning", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance).GetValue(dev);
var movesC = new[] { tun.Horn, tun.Wings, tun.Back };
var focusGo = UnityEngine.GameObject.Find("PromoFocus") ?? new UnityEngine.GameObject("PromoFocus");
UnityEngine.Vector3 Mid()
{
    float best = 1e9f; var m = focusGo.transform.position;
    var l = sbx.Spawned;
    for (int i = 0; i < l.Count; i++) for (int j = i + 1; j < l.Count; j++)
    {
        var a = l[i] != null ? l[i].Agent : null; var c = l[j] != null ? l[j].Agent : null;
        if (a == null || c == null || !MoriMonchiSimulator.ExpeditionTeams.AreRivals(a.Team, c.Team)) continue;
        var d = (a.transform.position - c.transform.position); d.y = 0;
        if (d.sqrMagnitude < best) { best = d.sqrMagnitude; m = (a.transform.position + c.transform.position) * 0.5f; }
    }
    return m;
}
focusGo.transform.position = Mid();
System.Collections.IEnumerator Drive()
{
    int k = 0;
    while (UnityEngine.Time.captureFramerate > 0 || k < 10)
    {
        focusGo.transform.position = UnityEngine.Vector3.Lerp(focusGo.transform.position, Mid(), 0.06f);
        if (k % FIRE_EVERY == 5) dev.FireClosestPair(movesC[(k / FIRE_EVERY) % 3], 14f);
        k++;
        yield return null;
    }
}
rig.StartCoroutine(Drive());
rig.Target = focusGo.transform;
