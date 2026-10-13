using System;
using UnityEngine;

namespace MoriMonchiSimulator
{
    public enum NegotiationResult { Accept, Reject }

    [Serializable]
    public class NegotiationFlow
    {
        public int ComputeCounter(int currentOffer, CustomerPricingSO pricing)
        {
            if (pricing == null) return currentOffer;
            return Mathf.RoundToInt(currentOffer * (1f + pricing.RenegotiationStep));
        }

        public NegotiationResult EvaluateCounter(CustomerArchetypeSO archetype, int currentOffer, int candidate, int ceiling, float tasteMatch)
        {
            if (candidate > ceiling) return NegotiationResult.Reject;
            if (archetype == null) return NegotiationResult.Accept;

            float headroomUsed = Mathf.Clamp01((candidate - currentOffer) / (float)Mathf.Max(1, ceiling - currentOffer));
            float chance = Mathf.Clamp01(archetype.RenegotiationTolerance + 0.4f * tasteMatch) * (1f - 0.5f * headroomUsed);
            return UnityEngine.Random.value <= chance
                ? NegotiationResult.Accept
                : NegotiationResult.Reject;
        }
    }
}
