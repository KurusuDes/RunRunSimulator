namespace MoriMonchiSimulator
{
    public static class BrawlLoc
    {
        public static string Title(BrawlSkillSO s) => s == null ? "" : TrOr("brawl.skill." + s.name + ".title", s.Title);

        public static string Description(BrawlSkillSO s) => s == null ? "" : TrOr("brawl.skill." + s.name + ".desc", s.Description);

        public static string Title(BrawlWingKitSO w) => w == null ? "" : TrOr("brawl.wing." + w.name + ".title", w.Title);

        public static string Description(BrawlWingKitSO w) => w == null ? "" : TrOr("brawl.wing." + w.name + ".desc", w.Description);

        public static string Body(string bodyId, string fallback) => TrOr("brawl.body." + bodyId, fallback);

        public static string Posture(string stance, string bond) => Loc.Tr("brawl.stance." + stance) + " · " + Loc.Tr("brawl.bond." + bond);

        static string TrOr(string key, string fallback)
        {
            string text = Loc.Tr(key);
            return text == key ? fallback ?? "" : text;
        }
    }
}
