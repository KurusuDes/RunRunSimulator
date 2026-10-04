var b = UnityEngine.Object.FindFirstObjectByType<MoriMonchiSimulator.EggLabBuilder>();
var bt = b.GetType();
var fl = System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public;
var partDb = (MoriMonchiSimulator.CreatureDatabaseSO)bt.GetField("partDatabase", fl).GetValue(b);
var furDb = (MoriMonchiSimulator.FurTypeDatabaseSO)bt.GetField("furDatabase", fl).GetValue(b);
var bank = (MoriMonchiSimulator.MonchiVisualBankSO)bt.GetField("visualBank", fl).GetValue(b);
var eggsRoot = (UnityEngine.Transform)bt.GetField("eggsRoot", fl).GetValue(b);
eggsRoot.gameObject.SetActive(false);
var old = UnityEngine.GameObject.Find("PromoStudio");
if (old != null) UnityEngine.Object.Destroy(old);
var studio = new UnityEngine.GameObject("PromoStudio").transform;
var ground = UnityEngine.GameObject.Find("Ground");
if (ground.transform.localScale.x < 5f) ground.transform.localScale = new UnityEngine.Vector3(ground.transform.localScale.x * 6f, ground.transform.localScale.y, ground.transform.localScale.z * 6f);
var gm = ground.GetComponent<UnityEngine.Renderer>().material;
var floorCol = new UnityEngine.Color(0.86f, 0.62f, 0.50f);
var skyCol = new UnityEngine.Color(0.98f, 0.84f, 0.70f);
gm.color = floorCol;
if (gm.HasProperty("_BaseColor")) gm.SetColor("_BaseColor", floorCol);
var cam = UnityEngine.Camera.main;
cam.clearFlags = UnityEngine.CameraClearFlags.SolidColor;
cam.backgroundColor = skyCol;
UnityEngine.RenderSettings.fog = true;
UnityEngine.RenderSettings.fogMode = UnityEngine.FogMode.Linear;
UnityEngine.RenderSettings.fogColor = skyCol;
UnityEngine.RenderSettings.fogStartDistance = 5f;
UnityEngine.RenderSettings.fogEndDistance = 16f;
var rnd = new System.Random(SEED);
UnityEngine.Random.InitState(SEED);
var json = new System.Text.StringBuilder("[");
MoriMonchiSimulator.MonchiVisualizer Spawn(MoriMonchiSimulator.CreatureDNA dna, UnityEngine.Vector3 pos, float yaw, MoriMonchiSimulator.MonchiMood mood, string group)
{
    var go = new UnityEngine.GameObject(group + "_" + dna.CustomName);
    go.transform.SetParent(studio, false);
    go.transform.SetLocalPositionAndRotation(pos, UnityEngine.Quaternion.Euler(0, yaw, 0));
    var v = go.AddComponent<MoriMonchiSimulator.MonchiVisualizer>();
    v.SetBank(bank);
    v.SetFurDatabase(furDb);
    v.Assemble(dna);
    v.SetMood(mood);
    json.Append("{\"group\":\"" + group + "\",\"name\":\"" + dna.CustomName + "\",\"dna\":\"" + dna.ToStringID() + "\",\"gender\":\"" + dna.Gender + "\",\"form\":\"" + dna.Form + "\",\"x\":" + pos.x.ToString(System.Globalization.CultureInfo.InvariantCulture) + "},");
    return v;
}
MoriMonchiSimulator.CreatureDNA Make(MoriMonchiSimulator.MonchiForm form, MoriMonchiSimulator.CreatureGender g)
{
    var d = MoriMonchiSimulator.CreatureGenerator.GenerateRandom(partDb, furDb);
    d.Form = form;
    d.Gender = g;
    d.CustomName = MoriMonchiSimulator.CreatureNameBank.GetRandomName();
    return d;
}
var moods = new[] { MoriMonchiSimulator.MonchiMood.Feliz, MoriMonchiSimulator.MonchiMood.Emocionado, MoriMonchiSimulator.MonchiMood.Neutral, MoriMonchiSimulator.MonchiMood.Amoroso, MoriMonchiSimulator.MonchiMood.Feliz, MoriMonchiSimulator.MonchiMood.Emocionado, MoriMonchiSimulator.MonchiMood.Neutral };
for (int i = 0; i < 7; i++)
    Spawn(Make(MoriMonchiSimulator.MonchiForm.Adult, rnd.Next(2) == 0 ? MoriMonchiSimulator.CreatureGender.Female : MoriMonchiSimulator.CreatureGender.Male), new UnityEngine.Vector3((i - 3) * LINE_SPACING, 0, 0), 180f + (i - 3) * -6f, moods[i], "line");
for (int i = 0; i < 5; i++)
    Spawn(Make(MoriMonchiSimulator.MonchiForm.Slime, rnd.Next(2) == 0 ? MoriMonchiSimulator.CreatureGender.Female : MoriMonchiSimulator.CreatureGender.Male), new UnityEngine.Vector3((i - 2) * 1.15f + (float)(rnd.NextDouble() - 0.5) * 0.2f, 0, 6f + (float)(rnd.NextDouble() - 0.5) * 0.8f), 180f + (float)(rnd.NextDouble() - 0.5) * 60f, moods[i], "slime");
var mom = Make(MoriMonchiSimulator.MonchiForm.Adult, MoriMonchiSimulator.CreatureGender.Female);
var dad = Make(MoriMonchiSimulator.MonchiForm.Adult, MoriMonchiSimulator.CreatureGender.Male);
Spawn(mom, new UnityEngine.Vector3(-0.75f, 0, 12f), 115f, MoriMonchiSimulator.MonchiMood.Amoroso, "pair");
Spawn(dad, new UnityEngine.Vector3(0.75f, 0, 12f), 245f, MoriMonchiSimulator.MonchiMood.Amoroso, "pair");
var kid = Make(MoriMonchiSimulator.MonchiForm.Egg, MoriMonchiSimulator.CreatureGender.Female);
var egg = Spawn(kid, new UnityEngine.Vector3(0f, 0, 11.75f), 180f, MoriMonchiSimulator.MonchiMood.Neutral, "pair");
egg.transform.localScale = UnityEngine.Vector3.one * EGG_SCALE;
var life = Make(MoriMonchiSimulator.MonchiForm.Egg, MoriMonchiSimulator.CreatureGender.Male);
var e1 = Spawn(life, new UnityEngine.Vector3(-1.1f, 0, 18f), 180f, MoriMonchiSimulator.MonchiMood.Neutral, "life");
e1.transform.localScale = UnityEngine.Vector3.one * EGG_SCALE;
var l2 = MoriMonchiSimulator.CreatureDNA.FromID(life.ToStringID()); l2.Form = MoriMonchiSimulator.MonchiForm.Slime; l2.Gender = life.Gender; l2.CustomName = life.CustomName;
Spawn(l2, new UnityEngine.Vector3(0f, 0, 18f), 180f, MoriMonchiSimulator.MonchiMood.Feliz, "life");
var l3 = MoriMonchiSimulator.CreatureDNA.FromID(life.ToStringID()); l3.Form = MoriMonchiSimulator.MonchiForm.Adult; l3.Gender = life.Gender; l3.CustomName = life.CustomName;
Spawn(l3, new UnityEngine.Vector3(1.3f, 0, 18f), 180f, MoriMonchiSimulator.MonchiMood.Emocionado, "life");
json.Length--; json.Append("]");
System.IO.File.WriteAllText("E:/GitHub/RunRunSimulator/Recordings/promo/studio.json", json.ToString());
var sb = new System.Text.StringBuilder();
foreach (UnityEngine.Transform t in studio)
{
    var rs = t.GetComponentsInChildren<UnityEngine.Renderer>();
    if (rs.Length == 0) { sb.Append(t.name + ":none|"); continue; }
    var bb = rs[0].bounds; foreach (var r in rs) bb.Encapsulate(r.bounds);
    var an = t.GetComponentInChildren<UnityEngine.Animator>();
    sb.Append(t.name + " c=" + bb.center.ToString("F2") + " s=" + bb.size.ToString("F2") + " an=" + (an != null && an.runtimeAnimatorController != null ? an.runtimeAnimatorController.name : "-") + "|");
}
return sb.ToString();
