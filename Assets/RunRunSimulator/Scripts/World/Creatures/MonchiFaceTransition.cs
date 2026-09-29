using MoreMountains.Feedbacks;
using MoreMountains.Tools;
using Sirenix.OdinInspector;
using UnityEngine;

namespace MoriMonchiSimulator
{
    public class MonchiFaceTransition : MonoBehaviour
    {
        [Required, SerializeField] private MMF_Player onBlink;
        [Required, SerializeField] private MMF_Player onPop;
        [Required, SerializeField] private ShaderController blinkController;
        [Required, SerializeField] private ShaderController popController;

        public void Bind(Renderer face)
        {
            if (blinkController != null)
            {
                blinkController.TargetRenderer = face;
                blinkController.Initialization();
            }

            if (popController != null)
            {
                popController.TargetRenderer = face;
                popController.Initialization();
            }
        }

        public void Play(bool pop)
        {
            var stop = pop ? onBlink : onPop;
            var play = pop ? onPop : onBlink;
            if (stop != null) stop.StopFeedbacks();
            if (play != null) play.PlayFeedbacks();
        }

        private void OnDisable()
        {
            if (onBlink != null) onBlink.StopFeedbacks();
            if (onPop != null) onPop.StopFeedbacks();
        }
    }
}
