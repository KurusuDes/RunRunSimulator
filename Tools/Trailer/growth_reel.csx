const int FPS = 30, TOTAL = 1440, CHUNK = 160, W = 1920, H = 1080;
int chunk = EditorPrefs.GetInt("MM_GrowthChunk", 0);
int f0 = chunk * CHUNK, f1 = Mathf.Min(TOTAL, f0 + CHUNK);
if (f0 >= TOTAL) return "done";
var outDir = System.IO.Path.Combine(System.IO.Directory.GetParent(Application.dataPath).FullName, "Tools/Trailer/growth/frames");
System.IO.Directory.CreateDirectory(outDir);

var items = new System.Collections.Generic.List<(Transform t, float t0, int kind)>();
var touched = new System.Collections.Generic.Dictionary<Transform, (Vector3 s, bool a)>();
void Touch(Transform t) { if (t != null && !touched.ContainsKey(t)) touched[t] = (t.localScale, t.gameObject.activeSelf); }
void Add(Transform t, float t0, int kind) { if (t == null) return; Touch(t); items.Add((t, t0, kind)); }
Transform F(string p) { var g = GameObject.Find(p); return g == null ? null : g.transform; }
Transform C(Transform p, string n) { return p == null ? null : p.Find(n); }
void Group(Transform g, float t0, float step) { if (g == null) return; Touch(g); int i = 0; foreach (Transform c in g) Add(c, t0 + step * i++, 0); items.Add((g, t0, 3)); }

var hide = new System.Collections.Generic.List<Transform>();
var tmpType = System.Type.GetType("TMPro.TextMeshPro, Unity.TextMeshPro");
foreach (var root in UnityEngine.SceneManagement.SceneManager.GetActiveScene().GetRootGameObjects()) {
  if (root.GetComponent<Canvas>() != null) continue;
  foreach (var tm in root.GetComponentsInChildren<TextMesh>(true)) hide.Add(tm.transform);
  if (tmpType != null) foreach (var tm in root.GetComponentsInChildren(tmpType, true)) hide.Add(((Component)tm).transform);
  foreach (var cv in root.GetComponentsInChildren<Canvas>(true)) if (cv.renderMode == RenderMode.WorldSpace) hide.Add(cv.transform);
}
foreach (var h in hide) Touch(h);

Add(F("ENVIROMENT/ShopBuilding"), 3.0f, 1);
Add(F("ENVIROMENT/ShopYard"), 3.5f, 1);
Group(F("ENVIROMENT/ShopFacade"), 4.2f, 0.14f);
var furn = F("WORLD/Furniture");
string[] e1 = { "CashRegister", "Base_Vitrina", "Base_Comedero", "Base_Bebedero", "Base_Cama", "Base_Incubadora", "ShopCorkBoard", "ShopPC_Desk", "ShopSideTable_Ledger", "ShopSideTable_Radio", "ShopSideTable_Crate", "StoragePanel" };
for (int i = 0; i < e1.Length; i++) Add(C(furn, e1[i]), 5.8f + 0.3f * i, 0);
Add(F("EXPANSIONS/ZONE_Criadero/Locked"), 9.9f, 0);
Add(F("EXPANSIONS/ZONE_SalaJuegos/Locked"), 10.2f, 0);

Group(F("WORLD/Furniture/CashRegister/Level2"), 12.0f, 0.1f);
Group(F("WORLD/Furniture/CashRegister/Level3"), 12.45f, 0.1f);
Add(F("WORLD/Furniture/Base_Vitrina/ShopModel"), 12.85f, 2);
Group(F("WORLD/Furniture/Base_Vitrina/Level2"), 13.0f, 0.1f);
items.Add((F("WORLD/Furniture/Base_Vitrina/Level2"), 13.75f, 4));
Group(F("WORLD/Furniture/Base_Vitrina/Level3"), 13.9f, 0.1f);
Add(F("WORLD/Furniture/Base_Comedero/ShopModel"), 14.35f, 2);
Group(F("WORLD/Furniture/Base_Comedero/Level2"), 14.5f, 0.1f);
Add(F("WORLD/Furniture/Base_Bebedero/ShopModelWater"), 14.75f, 2);
Group(F("WORLD/Furniture/Base_Bebedero/Level2"), 14.9f, 0.1f);
Group(F("WORLD/Furniture/Base_Cama/Level3"), 15.3f, 0.1f);
Group(F("WORLD/Furniture/Base_Incubadora/Level3"), 15.65f, 0.1f);
Group(F("WORLD/Furniture/ShopPC_Desk/Level2"), 16.0f, 0.1f);

Add(F("EXPANSIONS/ZONE_Criadero/Locked"), 17.0f, 2);
var cOpen = F("EXPANSIONS/ZONE_Criadero/Open");
Touch(cOpen); items.Add((cOpen, 17.1f, 3));
Add(C(cOpen, "ShopZoneCriadero"), 17.15f, 1);
int k = 0; foreach (var tr in cOpen.GetComponentsInChildren<Transform>(true)) if (tr.name.StartsWith("Corral_")) Add(tr, 18.0f + 0.35f * k++, 0);
Add(F("EXPANSIONS/ZONE_SalaJuegos/Locked"), 20.0f, 2);
var sOpen = F("EXPANSIONS/ZONE_SalaJuegos/Open");
Touch(sOpen); items.Add((sOpen, 20.1f, 3));
Add(C(sOpen, "ShopZoneSalaJuegos"), 20.15f, 1);
Add(C(sOpen, "PlayStation"), 21.0f, 0);
Add(C(sOpen, "ToyPlayArea"), 21.3f, 0);
Group(C(sOpen, "Level2"), 21.8f, 0.1f);
Group(C(sOpen, "Level3"), 22.3f, 0.1f);
Group(F("WORLD/Furniture/Patio/Level2"), 23.2f, 0.1f);
Group(F("WORLD/Furniture/Patio/Level3"), 23.8f, 0.25f);

void Lot(string name, float t0) {
  var lt = F("PREVIEW_ETAPAS/" + name); if (lt == null) return;
  var arch = lt.Find("Arquitectura"); var piso = arch.Find("Piso");
  int i = 0; foreach (Transform c in piso) Add(c, t0 + 0.04f * i++, 0);
  i = 0; foreach (Transform c in arch) { if (c == piso || !c.gameObject.activeSelf) continue; bool trim = c.name.StartsWith("ZoneKitTrimIvy"); Add(c, t0 + 0.45f + (trim ? 0.5f : 0f) + 0.03f * i++, trim ? 0 : 1); }
  i = 0; foreach (Transform c in lt.Find("Equipamiento")) Add(c, t0 + 1.0f + 0.1f * i++, 0);
}
Lot("Lote_Almacen_E3", 26.0f); Lot("Lote_Guarderia_E3", 28.1f); Lot("Lote_Bano_E3", 30.2f); Lot("Lote_Cocina_E3", 32.3f);
Lot("Lote_Escenario_E4", 35.0f); Lot("Lote_Gimnasio_E4", 37.0f); Lot("Lote_Clinica_E4", 39.0f); Lot("Lote_Linaje_E4", 41.0f);

if (chunk == 0) {
  var ts = new System.Collections.Generic.List<float>(); foreach (var it in items) if (it.kind <= 1) ts.Add(it.t0); ts.Sort();
  var pops = new System.Text.StringBuilder(); float last = -1f; foreach (var x in ts) if (x - last >= 0.09f) { pops.AppendLine(x.ToString("F3", System.Globalization.CultureInfo.InvariantCulture)); last = x; }
  System.IO.File.WriteAllText(System.IO.Path.Combine(outDir, "../pops.txt"), pops.ToString());
}
float EaseBack(float u) { u = Mathf.Clamp01(u); float c1 = 1.70158f, c3 = c1 + 1f; return 1f + c3 * Mathf.Pow(u - 1f, 3) + c1 * Mathf.Pow(u - 1f, 2); }
float EaseCubic(float u) { u = Mathf.Clamp01(u); return 1f - Mathf.Pow(1f - u, 3); }

var keys = new (float t, Vector3 focus, float dist)[] {
  (0f, new Vector3(-30f,0f,20f), 70f), (3f, new Vector3(-29f,0f,18f), 46f), (11.5f, new Vector3(-29f,0f,19f), 40f),
  (16.5f, new Vector3(-30f,0f,20f), 44f), (17.5f, new Vector3(-31f,0f,19f), 52f), (25.5f, new Vector3(-31f,0f,21f), 54f),
  (26.5f, new Vector3(-31f,0f,21f), 64f), (34.5f, new Vector3(-31f,0f,23f), 66f), (35.5f, new Vector3(-31f,0f,27f), 68f),
  (43f, new Vector3(-31f,0f,26f), 72f), (48f, new Vector3(-31f,0f,24f), 92f) };
void Cam(float t, out Vector3 focus, out float dist) {
  int i = 0; while (i < keys.Length - 2 && t > keys[i + 1].t) i++;
  float u = Mathf.SmoothStep(0, 1, Mathf.InverseLerp(keys[i].t, keys[i + 1].t, t));
  focus = Vector3.Lerp(keys[i].focus, keys[i + 1].focus, u); dist = Mathf.Lerp(keys[i].dist, keys[i + 1].dist, u);
}

var camGo = new GameObject("TMP_GrowthCam"); var cam = camGo.AddComponent<Camera>(); cam.CopyFrom(Camera.main); cam.fieldOfView = 42; cam.farClipPlane = 600;
var rt = new RenderTexture(W, H, 24); rt.antiAliasing = 4; cam.targetTexture = rt;
var tex = new Texture2D(W, H, TextureFormat.RGB24, false);
try {
  foreach (var h in hide) h.gameObject.SetActive(false);
  for (int f = f0; f < f1; f++) {
    float t = f / (float)FPS;
    foreach (var kv in touched) { if (hide.Contains(kv.Key)) continue; kv.Key.localScale = kv.Value.s; kv.Key.gameObject.SetActive(kv.Value.a); }
    foreach (var it in items) {
      var o = touched[it.t];
      if (it.kind == 3) { it.t.gameObject.SetActive(t >= it.t0); continue; }
      if (it.kind == 4) { if (t >= it.t0) it.t.gameObject.SetActive(false); continue; }
      if (it.kind == 2) { float u = (t - it.t0) / 0.3f; if (u >= 1f) it.t.gameObject.SetActive(false); else if (u > 0f) it.t.localScale = o.s * (1f - EaseCubic(u)); continue; }
      if (t < it.t0) { it.t.gameObject.SetActive(false); continue; }
      it.t.gameObject.SetActive(true);
      if (it.kind == 0) { float u = (t - it.t0) / 0.45f; if (u < 1f) it.t.localScale = o.s * Mathf.Max(0.001f, EaseBack(u)); }
      else { float u = (t - it.t0) / 0.6f; if (u < 1f) it.t.localScale = new Vector3(o.s.x, o.s.y * Mathf.Max(0.001f, EaseCubic(u)), o.s.z); }
    }
    Cam(t, out var focus, out var dist);
    float yaw = Mathf.Lerp(160f, 235f, t / 48f) * Mathf.Deg2Rad; float pitch = 44f * Mathf.Deg2Rad;
    camGo.transform.position = focus + new Vector3(Mathf.Sin(yaw) * Mathf.Cos(pitch), Mathf.Sin(pitch), Mathf.Cos(yaw) * Mathf.Cos(pitch)) * dist;
    camGo.transform.LookAt(focus);
    Shader.SetGlobalFloat("_GrowthTime", t);
    cam.Render(); RenderTexture.active = rt; tex.ReadPixels(new Rect(0, 0, W, H), 0, 0); tex.Apply(); RenderTexture.active = null;
    System.IO.File.WriteAllBytes(System.IO.Path.Combine(outDir, "f_" + f.ToString("0000") + ".jpg"), tex.EncodeToJPG(90));
  }
} finally {
  foreach (var kv in touched) { kv.Key.localScale = kv.Value.s; kv.Key.gameObject.SetActive(kv.Value.a); }
  cam.targetTexture = null; UnityEngine.Object.DestroyImmediate(camGo); UnityEngine.Object.DestroyImmediate(rt); UnityEngine.Object.DestroyImmediate(tex);
}
EditorPrefs.SetInt("MM_GrowthChunk", chunk + 1);
return "chunk " + chunk + " frames " + f0 + "-" + (f1 - 1) + " items=" + items.Count + " hidden=" + hide.Count;
