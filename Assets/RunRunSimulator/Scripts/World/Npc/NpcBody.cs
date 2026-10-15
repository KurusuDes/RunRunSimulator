using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{
    public class NpcBody : MonoBehaviour
    {
        private static readonly int SpeedHash = Animator.StringToHash("Speed");
        private static readonly int TalkingHash = Animator.StringToHash("Talking");

        [SerializeField] private HumanBodyCatalogSO catalog;
        [SerializeField] private Transform bodyAnchor;
        [SerializeField] private float speedDamp = 0.1f;

        private NavMeshAgent agent;
        private NpcAgent npc;
        private Animator animator;

        private void Awake()
        {
            agent = GetComponent<NavMeshAgent>();
            npc = GetComponent<NpcAgent>();
        }

        private void Start()
        {
            if (catalog == null || !catalog.TryPick(out var body, out var skin)) return;

            var anchor = bodyAnchor != null ? bodyAnchor : transform;
            var instance = Instantiate(body, anchor);
            instance.transform.localPosition = Vector3.zero;
            instance.transform.localRotation = Quaternion.identity;

            if (skin != null)
            {
                foreach (var smr in instance.GetComponentsInChildren<SkinnedMeshRenderer>(true))
                {
                    var slots = new Material[smr.sharedMaterials.Length];
                    for (int i = 0; i < slots.Length; i++) slots[i] = skin;
                    smr.sharedMaterials = slots;
                }
            }

            animator = instance.GetComponentInChildren<Animator>();
            if (animator == null || animator.runtimeAnimatorController == null)
            {
                animator = null;
                return;
            }

            animator.applyRootMotion = false;
            animator.cullingMode = AnimatorCullingMode.CullUpdateTransforms;
            animator.Update(0f);
            animator.Play(animator.GetCurrentAnimatorStateInfo(0).fullPathHash, 0, Random.value);
        }

        private void Update()
        {
            if (animator == null) return;

            var v = agent.velocity;
            var planar = new Vector2(v.x, v.z).magnitude;
            animator.SetFloat(SpeedHash, planar, speedDamp, Time.deltaTime);

            var talking = npc.State == NpcAgent.NpcState.Negotiating || npc.State == NpcAgent.NpcState.WaitingAtRegister;
            animator.SetBool(TalkingHash, talking);
        }
    }
}
