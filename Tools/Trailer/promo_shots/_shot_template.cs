var cam = UnityEngine.Camera.main;
foreach (var b in cam.GetComponents<UnityEngine.MonoBehaviour>())
    if (!(b is UnityEngine.Rendering.Universal.UniversalAdditionalCameraData) && !(b is MoriMonchiSimulator.TrailerCameraRig)) b.enabled = false;
if (cam.transform.parent != null) cam.transform.SetParent(null, true);
var rig = cam.gameObject.GetComponent<MoriMonchiSimulator.TrailerCameraRig>();
if (rig == null) rig = cam.gameObject.AddComponent<MoriMonchiSimulator.TrailerCameraRig>();
rig.enabled = true;
rig.Target = null;
UnityEngine.Rendering.Universal.DepthOfField dof = null;
foreach (var v in UnityEngine.Object.FindObjectsByType<UnityEngine.Rendering.Volume>(UnityEngine.FindObjectsSortMode.None))
    if (v.profile != null && v.profile.TryGet(out UnityEngine.Rendering.Universal.DepthOfField d)) { dof = d; }
rig.Dof = dof;
//PARAMS
rig.Restart();
string dir = "E:/GitHub/RunRunSimulator/Recordings/promo/" + SHOT;
System.IO.Directory.CreateDirectory(dir);
foreach (var f in System.IO.Directory.GetFiles(dir)) System.IO.File.Delete(f);
var rt = new UnityEngine.RenderTexture(1920, 1080, 24, UnityEngine.RenderTextureFormat.ARGB32);
rt.antiAliasing = 4;
var tex = new UnityEngine.Texture2D(1920, 1080, UnityEngine.TextureFormat.RGB24, false);
System.Collections.IEnumerator Run()
{
    UnityEngine.Time.captureFramerate = 30;
    for (int i = 0; i < WARM; i++) yield return null;
    rig.Restart();
    for (int f = 0; f < FRAMES; f++)
    {
        yield return new UnityEngine.WaitForEndOfFrame();
        var prev = cam.targetTexture;
        cam.targetTexture = rt;
        cam.Render();
        cam.targetTexture = prev;
        UnityEngine.RenderTexture.active = rt;
        tex.ReadPixels(new UnityEngine.Rect(0, 0, 1920, 1080), 0, 0);
        tex.Apply(false);
        UnityEngine.RenderTexture.active = null;
        System.IO.File.WriteAllBytes(dir + "/f_" + f.ToString("0000") + ".jpg", tex.EncodeToJPG(92));
    }
    UnityEngine.Time.captureFramerate = 0;
    System.IO.File.WriteAllText(dir + "/done.txt", FRAMES.ToString());
}
rig.StartCoroutine(Run());
return "started " + dir + " dof=" + (dof != null);
