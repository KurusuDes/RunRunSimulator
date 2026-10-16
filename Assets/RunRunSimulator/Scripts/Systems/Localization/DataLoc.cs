namespace MoriMonchiSimulator
{
    public static class DataLoc
    {
        public static string PartName(BodyPart p) => p == null ? "" : TrOr("part." + p.ID + ".name", p.Name);

        public static string UpgradeName(ShopUpgradeSO u) => u == null ? "" : TrOr("upgrade." + u.Id + ".name", NameOf(u.DisplayName, u.Id));

        public static string ItemName(ItemDefinitionSO i) => i == null ? "" : TrOr("item." + i.Id + ".name", NameOf(i.DisplayName, i.Id));

        public static string DecorName(BreedingDecorSO d) => d == null ? "" : TrOr("decor." + d.Id + ".name", NameOf(d.DisplayName, d.Id));

        public static string BoxName(CreatureBoxSO b) => b == null ? "" : TrOr("box." + b.Id + ".name", NameOf(b.DisplayName, b.Id));

        static string NameOf(string display, string id) => string.IsNullOrEmpty(display) ? id : display;

        static string TrOr(string key, string fallback)
        {
            string text = Loc.Tr(key);
            return text == key ? fallback ?? "" : text;
        }
    }
}
