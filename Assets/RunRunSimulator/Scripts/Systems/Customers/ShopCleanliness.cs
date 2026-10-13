using UnityEngine;

namespace MoriMonchiSimulator
{
    public static class ShopCleanliness
    {
        public static float Multiplier(CustomerPricingSO pricing)
        {
            if (pricing == null) return 1f;

            float dirt = Puddle.All.Count / Mathf.Max(1f, pricing.MessForFullPenalty);

            int emptyStations = 0;
            foreach (var station in StationSupply.All)
                if (station != null && station.IsEmpty) emptyStations++;
            dirt += emptyStations * pricing.EmptyStationPenalty;

            return 1f - (1f - pricing.DirtyMinMultiplier) * Mathf.Clamp01(dirt);
        }

        public static bool IsDirty(CustomerPricingSO pricing) =>
            pricing != null && Multiplier(pricing) < pricing.DirtyThoughtBelow;
    }
}
