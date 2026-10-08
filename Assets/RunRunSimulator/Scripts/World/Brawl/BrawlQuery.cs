using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;

namespace MoriMonchiSimulator
{

public static class BrawlQuery
{
    public static bool AreFoes(BrawlFighter a, BrawlFighter b)
    {
        return a != null && b != null && ExpeditionTeams.AreRivals(a.Team, b.Team);
    }

    public static float Planar(Vector3 a, Vector3 b)
    {
        float dx = a.x - b.x;
        float dz = a.z - b.z;
        return Mathf.Sqrt(dx * dx + dz * dz);
    }

    public static BrawlFighter NearestFoe(BrawlFighter self, float maxDistance = float.PositiveInfinity)
    {
        if (self == null)
            return null;
        return NearestFoeTo(self.Position, self.Team, maxDistance);
    }

    public static BrawlFighter NearestFoeTo(Vector3 point, ExpeditionTeam team, float maxDistance, BrawlFighter exclude = null)
    {
        var all = BrawlFighter.All;
        BrawlFighter best = null;
        float bestDistance = float.PositiveInfinity;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (f == exclude || !f.IsAlive || !ExpeditionTeams.AreRivals(team, f.Team))
                continue;
            float d = Planar(point, f.Position);
            if (d > maxDistance || d >= bestDistance)
                continue;
            bestDistance = d;
            best = f;
        }
        return best;
    }

    public static BrawlFighter LowestAlly(BrawlFighter self, float maxDistance, bool includeSelf, float below01 = 1f)
    {
        if (self == null)
            return null;

        var all = BrawlFighter.All;
        BrawlFighter best = null;
        float bestHp = float.PositiveInfinity;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (!f.IsAlive || !ExpeditionTeams.AreAllies(self.Team, f.Team))
                continue;
            if (f == self && !includeSelf)
                continue;
            float hp = f.Hp01;
            if (hp >= below01 || hp >= bestHp)
                continue;
            if (Planar(self.Position, f.Position) > maxDistance)
                continue;
            bestHp = hp;
            best = f;
        }
        return best;
    }

    public static int FoesWithin(Vector3 center, float radius, ExpeditionTeam team, List<BrawlFighter> into = null)
    {
        into?.Clear();
        var all = BrawlFighter.All;
        int count = 0;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (!f.IsAlive || !ExpeditionTeams.AreRivals(team, f.Team))
                continue;
            if (Planar(center, f.Position) > radius + f.Radius)
                continue;
            count++;
            into?.Add(f);
        }
        return count;
    }

    public static int AlliesWithin(Vector3 center, float radius, ExpeditionTeam team, List<BrawlFighter> into = null)
    {
        into?.Clear();
        var all = BrawlFighter.All;
        int count = 0;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (!f.IsAlive || !ExpeditionTeams.AreAllies(team, f.Team))
                continue;
            if (Planar(center, f.Position) > radius + f.Radius)
                continue;
            count++;
            into?.Add(f);
        }
        return count;
    }

    public static Vector3 FoeClusterPoint(BrawlFighter self, float radius, float maxRange, out int count)
    {
        count = 0;
        if (self == null)
            return Vector3.zero;

        var all = BrawlFighter.All;
        Vector3 bestPoint = self.Position;
        float bestDistance = float.PositiveInfinity;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (!f.IsAlive || !ExpeditionTeams.AreRivals(self.Team, f.Team))
                continue;
            float distance = Planar(self.Position, f.Position);
            if (distance > maxRange)
                continue;
            int around = FoesWithin(f.Position, radius, self.Team);
            if (around > count || (around == count && distance < bestDistance))
            {
                count = around;
                bestDistance = distance;
                bestPoint = f.Position;
            }
        }
        return bestPoint;
    }

    public static Vector3 AlliesCentroid(BrawlFighter self, bool includeSelf, out int count)
    {
        count = 0;
        if (self == null)
            return Vector3.zero;

        var all = BrawlFighter.All;
        Vector3 sum = Vector3.zero;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (!f.IsAlive || !ExpeditionTeams.AreAllies(self.Team, f.Team))
                continue;
            if (f == self && !includeSelf)
                continue;
            sum += f.Position;
            count++;
        }
        return count > 0 ? sum / count : self.Position;
    }

    public static int AliveCount(ExpeditionTeam team)
    {
        var all = BrawlFighter.All;
        int count = 0;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (f.IsAlive && f.Team == team)
                count++;
        }
        return count;
    }

    public static bool InCone(Vector3 origin, Vector3 forward, float range, float halfAngleDeg, BrawlFighter target)
    {
        if (target == null || !target.IsAlive)
            return false;

        float dx = target.Position.x - origin.x;
        float dz = target.Position.z - origin.z;
        float distance = Mathf.Sqrt(dx * dx + dz * dz);
        if (distance < target.Radius)
            return true;
        if (distance > range + target.Radius)
            return false;
        if (halfAngleDeg >= 180f)
            return true;

        float forwardLength = Mathf.Sqrt(forward.x * forward.x + forward.z * forward.z);
        if (forwardLength < 0.0001f)
            return true;

        float cos = (dx * forward.x + dz * forward.z) / (distance * forwardLength);
        return cos >= Mathf.Cos(halfAngleDeg * Mathf.Deg2Rad);
    }

    public static bool OnSegment(Vector3 a, Vector3 b, float halfWidth, BrawlFighter target)
    {
        if (target == null || !target.IsAlive)
            return false;

        float abx = b.x - a.x;
        float abz = b.z - a.z;
        float apx = target.Position.x - a.x;
        float apz = target.Position.z - a.z;
        float lengthSqr = abx * abx + abz * abz;
        float t = lengthSqr > 0.000001f ? Mathf.Clamp01((apx * abx + apz * abz) / lengthSqr) : 0f;
        float cx = apx - abx * t;
        float cz = apz - abz * t;
        float limit = halfWidth + target.Radius;
        return cx * cx + cz * cz <= limit * limit;
    }

    public static bool HasLineOfSight(Vector3 from, Vector3 to)
    {
        return !NavMesh.Raycast(from, to, out _, NavMesh.AllAreas);
    }
}
}
