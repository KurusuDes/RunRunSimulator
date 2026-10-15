using Unity.Cinemachine;
using UnityEngine;
namespace MoriMonchiSimulator
{

public class FirstPersonNeck : MonoBehaviour
{
    [SerializeField] private CinemachinePanTilt panTilt;
    [SerializeField] private Vector3 neckPivot = new(0f, 1.45f, 0.26f);
    [SerializeField] private Vector3 eyeOffset = new(0f, 0.16f, 0.12f);

    private void Update()
    {
        if (panTilt == null) return;
        transform.localPosition = neckPivot + Quaternion.Euler(panTilt.TiltAxis.Value, 0f, 0f) * eyeOffset;
    }
}

}
