using UnityEngine;

namespace MoriMonchiSimulator
{

public static class BrawlLightningShapes
{
    public const int BranchPoints = 4;

    private const float BranchMinLength = 0.6f;
    private const float BranchMaxLength = 1.2f;
    private const float BranchJitter = 0.1f;
    private const float BranchMinDrop = 0.3f;

    public static void BuildBranch(Vector3[] main, Vector3[] branch)
    {
        Vector3 start = main[Random.Range(1, main.Length - 1)];
        Vector3 dir = new Vector3(Random.Range(-1f, 1f), -Random.Range(BranchMinDrop, 1f), Random.Range(-1f, 1f)).normalized;
        float step = Random.Range(BranchMinLength, BranchMaxLength) / (BranchPoints - 1);

        branch[0] = start;
        for (int i = 1; i < BranchPoints; i++)
            branch[i] = start + dir * (step * i) + Random.insideUnitSphere * BranchJitter;
    }
}
}
