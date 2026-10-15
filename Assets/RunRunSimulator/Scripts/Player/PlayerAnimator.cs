using UnityEngine;
namespace MoriMonchiSimulator
{

public class PlayerAnimator : MonoBehaviour
{
    [SerializeField] private Animator animator;
    [SerializeField] private Animator bodyAnimator;

    [Header("Locomotion")]
    [SerializeField] private float speedDampTime = 0.1f;
    [SerializeField] private float bodyTopSpeed = 3.6f;

    [Header("IK Blend")]
    [SerializeField] private float ikBlendSpeed = 4f;

    [Header("Pet IK")]
    [SerializeField] private float petHeight = 0.35f;
    [SerializeField] private float petStrokeSpeed = 7f;
    [SerializeField] private float petStrokeAmplitude = 0.08f;
    [Range(0f, 1f)]
    [SerializeField] private float petMaxWeight = 0.85f;

    [Header("Hold IK")]
    [SerializeField] private float holdHandSpread = 0.18f;
    [SerializeField] private float holdUnder = 0.12f;
    [Range(0f, 1f)]
    [SerializeField] private float holdMaxWeight = 0.7f;

    private static readonly int SpeedHash    = Animator.StringToHash("Speed");
    private static readonly int HoldingHash  = Animator.StringToHash("Holding");
    private static readonly int PettingHash  = Animator.StringToHash("Petting");
    private static readonly int ThrowHash    = Animator.StringToHash("Throw");
    private static readonly int InteractHash = Animator.StringToHash("Interact");
    private static readonly int JumpHash     = Animator.StringToHash("Jump");

    private Vector2 moveInput;
    private Transform holdTarget;
    private Transform petTarget;
    private float holdWeight;
    private float petWeight;

    private void Awake()
    {
        if (animator == null) animator = GetComponent<Animator>();
    }

    private void OnEnable()
    {
        PlayerInputs.MoveChanged       += OnMoveChanged;
        PlayerInputs.Jumped            += OnJump;
        PlayerController.HeldChanged   += OnHeldChanged;
        PlayerController.PetChanged    += OnPetChanged;
        PlayerController.Threw         += OnThrew;
        PlayerController.Interacted    += OnInteracted;
    }

    private void OnDisable()
    {
        PlayerInputs.MoveChanged       -= OnMoveChanged;
        PlayerInputs.Jumped            -= OnJump;
        PlayerController.HeldChanged   -= OnHeldChanged;
        PlayerController.PetChanged    -= OnPetChanged;
        PlayerController.Threw         -= OnThrew;
        PlayerController.Interacted    -= OnInteracted;
    }

    private void OnMoveChanged(Vector2 move) => moveInput = move;

    private void OnHeldChanged(Transform target)
    {
        holdTarget = target;
        if (animator != null) animator.SetBool(HoldingHash, target != null);
    }

    private void OnPetChanged(Transform target)
    {
        petTarget = target;
        if (animator != null) animator.SetBool(PettingHash, target != null);
    }

    private void Update()
    {
        float step = ikBlendSpeed * Time.deltaTime;
        petWeight  = Mathf.MoveTowards(petWeight,  petTarget  != null ? 1f : 0f, step);
        holdWeight = Mathf.MoveTowards(holdWeight, holdTarget != null ? 1f : 0f, step);

        if (bodyAnimator != null) bodyAnimator.SetFloat(SpeedHash, moveInput.magnitude * bodyTopSpeed, speedDampTime, Time.deltaTime);
        if (animator == null) return;
        animator.SetFloat(SpeedHash, moveInput.magnitude, speedDampTime, Time.deltaTime);
    }

    private void OnAnimatorIK(int layerIndex)
    {
        if (animator == null) return;

        if (petWeight > 0f && petTarget != null)
        {
            Vector3 stroke = transform.right * (Mathf.Sin(Time.time * petStrokeSpeed) * petStrokeAmplitude);
            Vector3 pos = petTarget.position + Vector3.up * petHeight + stroke;
            animator.SetIKPositionWeight(AvatarIKGoal.RightHand, petWeight * petMaxWeight);
            animator.SetIKPosition(AvatarIKGoal.RightHand, pos);
        }
        else
        {
            animator.SetIKPositionWeight(AvatarIKGoal.RightHand, 0f);
        }

        if (holdWeight > 0f && holdTarget != null)
        {
            Vector3 under = Vector3.down * holdUnder;
            Vector3 side  = transform.right * holdHandSpread;
            float w = holdWeight * holdMaxWeight;
            animator.SetIKPositionWeight(AvatarIKGoal.LeftHand, w);
            animator.SetIKPosition(AvatarIKGoal.LeftHand, holdTarget.position - side + under);
            animator.SetIKPositionWeight(AvatarIKGoal.RightHand, Mathf.Max(w, petTarget != null ? petWeight * petMaxWeight : 0f));
            animator.SetIKPosition(AvatarIKGoal.RightHand, holdTarget.position + side + under);
        }
        else
        {
            animator.SetIKPositionWeight(AvatarIKGoal.LeftHand, 0f);
        }
    }

    private void OnJump()      { if (animator != null) animator.SetTrigger(JumpHash); }
    private void OnThrew()     { if (animator != null) animator.SetTrigger(ThrowHash); }
    private void OnInteracted(){ if (animator != null) animator.SetTrigger(InteractHash); }
}
}
