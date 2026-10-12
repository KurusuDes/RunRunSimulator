using System;
using System.Collections.Generic;
using UnityEngine;

namespace MoriMonchiSimulator
{
    [Serializable]
    public class ValuationHandler
    {
        public int Estimate(CreatureDNA dna, CustomerArchetypeSO archetype, CustomerPricingSO pricing, float tasteMatch = 0f)
        {
            if (dna == null || pricing == null) return 0;

            int basePrice =
                pricing.BasePricePerTier.GetValueOrDefault(dna.BodyTier, 0)
              + pricing.BasePricePerTier.GetValueOrDefault(dna.HornTier, 0)
              + pricing.BasePricePerTier.GetValueOrDefault(dna.BackTier, 0)
              + pricing.BasePricePerTier.GetValueOrDefault(dna.WingTier, 0);

            float wBreed    = archetype != null ? archetype.WeightBreed    : 1f;
            float wTier     = archetype != null ? archetype.WeightTier     : 1f;
            float budgetMul = archetype != null ? archetype.BudgetMultiplier : 1f;

            float breedBonus  = dna.BreedCount * wBreed * pricing.BreedCountMultiplier;
            float tierBonus   = ((int)dna.BodyTier + (int)dna.HornTier + (int)dna.BackTier + (int)dna.WingTier) * wTier * pricing.TierMultiplier;
            float rarityBonus = RarityLevels(dna) * pricing.RarityBonusPerLevel;

            float objective = basePrice + breedBonus + tierBonus + rarityBonus;

            if (dna.IsShiny) objective *= pricing.ShinyMultiplier;

            var needs = dna.Needs;
            if (needs != null)
            {
                float care = (Mathf.Clamp(needs.Health, 0f, 100f) + Mathf.Clamp(needs.Energy, 0f, 100f) + Mathf.Clamp(needs.Affect, 0f, 100f)) / 300f;
                objective *= Mathf.Lerp(pricing.CareMinMultiplier, pricing.CareMaxMultiplier, care);
            }

            if (archetype != null) objective *= 1f + archetype.TasteBonus * tasteMatch;

            return Mathf.Max(0, Mathf.RoundToInt(objective * budgetMul));
        }

        private static int RarityLevels(CreatureDNA dna)
        {
            var db = GameManager.Instance != null ? GameManager.Instance.Database : null;
            if (db == null) return 0;
            int levels = 0;
            var horn = db.GetHorn(dna.HornID);
            var back = db.GetBack(dna.BackID);
            var wing = db.GetWing(dna.WingID);
            if (horn != null) levels += (int)horn.Rarity;
            if (back != null) levels += (int)back.Rarity;
            if (wing != null) levels += (int)wing.Rarity;
            return levels;
        }
    }
}
