using UnityEngine;

namespace MoriMonchiSimulator
{

public class BrawlLightningBranches
{
    private const int MinCount = 3;
    private const int MaxCount = 4;
    private const float Width = 0.1f;
    private const float Alpha = 0.8f;

    private readonly LineRenderer[] lines = new LineRenderer[MaxCount];
    private readonly Vector3[][] points = new Vector3[MaxCount][];
    private int active;

    public BrawlLightningBranches(Transform parent, int sortingOrder)
    {
        for (int i = 0; i < MaxCount; i++)
        {
            var go = new GameObject("Branch");
            go.transform.SetParent(parent, false);
            var line = BrawlLineFx.Setup(go.AddComponent<LineRenderer>(), sortingOrder);
            line.widthCurve = AnimationCurve.Constant(0f, 1f, 1f);
            line.enabled = false;
            lines[i] = line;
            points[i] = new Vector3[BrawlLightningShapes.BranchPoints];
        }
    }

    public void Arm(Material material, Color color)
    {
        color.a = Alpha;
        active = Random.Range(MinCount, MaxCount + 1);
        for (int i = 0; i < active; i++)
        {
            var line = lines[i];
            line.sharedMaterial = material;
            line.positionCount = 0;
            line.startColor = color;
            line.endColor = color;
            line.enabled = true;
        }
    }

    public void Rebuild(Vector3[] main)
    {
        for (int i = 0; i < active; i++)
        {
            BrawlLightningShapes.BuildBranch(main, points[i]);
            lines[i].positionCount = BrawlLightningShapes.BranchPoints;
            lines[i].SetPositions(points[i]);
        }
    }

    public void Fade(float fade)
    {
        for (int i = 0; i < active; i++) lines[i].widthMultiplier = Width * fade;
    }

    public void Disable()
    {
        for (int i = 0; i < MaxCount; i++) lines[i].enabled = false;
        active = 0;
    }
}
}
