using System.Collections;
using UnityEngine;

namespace MoriMonchiSimulator
{
    public class EggIdleShuffler : MonoBehaviour
    {
        [SerializeField] private Animator animator;
        [SerializeField] private string[] variants = { "Wobble", "Hop", "Jingle" };
        [SerializeField] private Vector2 gapSeconds = new Vector2(2.5f, 7f);
        [SerializeField] private float crossFade = 0.12f;

        private Coroutine routine;

        private void Awake()
        {
            if (animator == null) animator = GetComponentInChildren<Animator>();
        }

        private void OnEnable()
        {
            routine = StartCoroutine(ShuffleRoutine());
        }

        private void OnDisable()
        {
            if (routine != null) StopCoroutine(routine);
            routine = null;
        }

        private IEnumerator ShuffleRoutine()
        {
            animator.Play("Idle", 0, Random.value);

            int lastIndex = -1;
            while (true)
            {
                yield return new WaitForSeconds(Random.Range(gapSeconds.x, gapSeconds.y));

                int index = Random.Range(0, variants.Length);
                if (variants.Length > 1)
                {
                    while (index == lastIndex) index = Random.Range(0, variants.Length);
                }
                lastIndex = index;

                animator.CrossFadeInFixedTime(variants[index], crossFade);
            }
        }
    }
}
