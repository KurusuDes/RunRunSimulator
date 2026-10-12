using System;
using UnityEngine;
using UnityEngine.UIElements;
namespace MoriMonchiSimulator
{

public class DetailEvolutionBlock
{
    private readonly BrawlKitDatabaseSO kits;
    private readonly EvolutionEffectSO effect;
    private readonly Func<CreatureRegistrySO> registry;
    private readonly Action onChanged;

    private string resultId;
    private PartRole resultRole;
    private string resultText;

    public DetailEvolutionBlock(BrawlKitDatabaseSO kits, EvolutionEffectSO effect, Func<CreatureRegistrySO> registry, Action onChanged)
    {
        this.kits = kits;
        this.effect = effect;
        this.registry = registry;
        this.onChanged = onChanged;
    }

    public VisualElement Build(CreatureDNA dna, PartRole role, BrawlSkillFamily? family)
    {
        if (kits == null || effect == null || dna == null || dna.Form != MonchiForm.Adult) return null;

        var steps = kits.Upgrades(dna, role);
        if (steps == null || steps.Count == 0) return null;

        int max = BrawlUpgrades.MaxLevel(steps);
        int level = Mathf.Clamp((int)dna.TierOf(role), 1, max);

        var block = new VisualElement();
        block.AddToClassList("part-evo");
        block.EnableInClassList("part-evo--fresh", HasResult(dna) && resultRole == role);

        block.Add(BuildHead(level, max));

        for (int i = 0; i < level - 1; i++)
            block.Add(NewLabel("part-evo__done", Loc.Tr("ui.evo.done", BrawlUpgradeText.Describe(steps[i], family))));

        if (level < max)
        {
            if (effect.IsCandidate(dna, role))
            {
                block.AddToClassList("part-evo--candidate");
                block.Add(NewLabel("part-evo__next", Loc.Tr("ui.evo.next", BrawlUpgradeText.Describe(steps[level - 1], family))));
            }
        }
        else
        {
            block.Add(NewLabel("part-evo__max", Loc.Tr("ui.evo.max")));
        }

        return block;
    }

    public VisualElement BuildAction(CreatureDNA dna)
    {
        if (kits == null || effect == null || dna == null || dna.Form == MonchiForm.Egg) return null;

        var container = new VisualElement();
        container.AddToClassList("evo-action");

        if (dna.Form != MonchiForm.Adult)
        {
            container.Add(NewLabel("evo-action__hint", Loc.Tr("ui.evo.needsadult")));
            return container;
        }

        if (HasResult(dna))
            container.Add(NewLabel("evo-action__result", Loc.Tr("ui.evo.result", PartName(resultRole), resultText)));

        if (!HasCandidate(dna))
        {
            container.Add(NewLabel("evo-action__max", Loc.Tr("ui.evo.allmax")));
            return container;
        }

        int cost = effect.Cost(dna);
        int required = effect.RequiredBattles(dna);

        container.Add(NewLabel("evo-action__xp", Loc.Tr("ui.evo.xp", dna.Battles, required)));

        var button = new Button(() => Evolve(dna));
        button.AddToClassList("evo-action__button");
        button.text = Loc.Tr("ui.evo.action", cost);
        button.SetEnabled(effect.CanApply(dna) && Wallet.Balance(Currency.Minerita) >= cost);
        container.Add(button);

        string hint = dna.Battles < required
            ? Loc.Tr("ui.evo.needbattles", required - dna.Battles)
            : Loc.Tr("ui.evo.action.hint");
        container.Add(NewLabel("evo-action__hint", hint));
        return container;
    }

    private bool HasCandidate(CreatureDNA dna) =>
        effect.IsCandidate(dna, PartRole.Body) || effect.IsCandidate(dna, PartRole.Horn) ||
        effect.IsCandidate(dna, PartRole.Back) || effect.IsCandidate(dna, PartRole.Wing);

    private void Evolve(CreatureDNA dna)
    {
        var role = EvolutionService.Evolve(dna, effect, registry());
        if (!role.HasValue) return;

        var steps = kits.Upgrades(dna, role.Value);
        int index = (int)dna.TierOf(role.Value) - 2;
        if (steps == null || index < 0 || index >= steps.Count) return;

        resultId = dna.UniqueID;
        resultRole = role.Value;
        resultText = BrawlUpgradeText.Describe(steps[index], FamilyOf(dna, role.Value));
        onChanged?.Invoke();
    }

    private bool HasResult(CreatureDNA dna) => resultText != null && resultId == dna.UniqueID;

    private BrawlSkillFamily? FamilyOf(CreatureDNA dna, PartRole role)
    {
        switch (role)
        {
            case PartRole.Horn: return kits.Skill(dna.HornID, ClashSlot.Horn)?.Family;
            case PartRole.Back: return kits.Skill(dna.BackID, ClashSlot.Back)?.Family;
            default: return null;
        }
    }

    private static string PartName(PartRole role) => Loc.Tr("ui.detail.slot." + role.ToString().ToLowerInvariant());

    private static VisualElement BuildHead(int level, int max)
    {
        var head = new VisualElement();
        head.AddToClassList("part-evo__head");

        var pips = new VisualElement();
        pips.AddToClassList("part-evo__pips");
        for (int i = 0; i < max - 1; i++)
        {
            var pip = new VisualElement();
            pip.AddToClassList("part-evo__pip");
            pip.EnableInClassList("part-evo__pip--on", i < level - 1);
            pips.Add(pip);
        }
        head.Add(pips);

        head.Add(NewLabel("part-evo__level", Loc.Tr("ui.evo.level", level, max)));
        return head;
    }

    private static Label NewLabel(string cls, string text)
    {
        var label = new Label(text);
        label.AddToClassList(cls);
        return label;
    }
}
}
