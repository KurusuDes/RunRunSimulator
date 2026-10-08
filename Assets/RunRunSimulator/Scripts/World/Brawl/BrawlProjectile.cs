using System.Collections.Generic;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.Rendering;

namespace MoriMonchiSimulator
{

public struct BrawlShot
{
    public BrawlFighter Owner;
    public ExpeditionTeam Team;
    public Vector3 Origin, Direction;
    public float Speed, Range, Damage, Heal, Radius, Knockback;
    public float Slow, SlowSeconds, StunSeconds;
    public int Bounces;
    public bool Pierce, HealsAllies;
    public BrawlFighter Homing;
    public float HomingTurn;
    public bool Boomerang, Lob;
    public Vector3 LobTarget;
    public float LobSeconds, ExplodeRadius, Height, SpriteSize, Spin;
    public bool FromSkill;
    public BrawlTheme Theme;
}

public class BrawlProjectile : MonoBehaviour
{
    private const float DefaultHeight = 0.8f;
    private const float DefaultHomingTurn = 240f;
    private const float BoomerangCatchDistance = 0.8f;
    private const float BoomerangMaxSeconds = 4f;
    private const float WallBurstRadius = 0.6f;
    private const int IconSortingOrder = 10;
    private const float GlowScale = 2.2f;
    private const float GlowAlpha = 0.55f;
    private const float GlowPulseAmount = 0.1f;
    private const float GlowPulseHz = 8f;
    private const float RivalTrailWidth = 0.75f;

    private static readonly List<BrawlProjectile> active = new();
    private static readonly List<BrawlProjectile> pool = new();
    private static Transform root;

    public static IReadOnlyList<BrawlProjectile> Active => active;

    private readonly HashSet<BrawlFighter> struck = new();
    private readonly List<BrawlFighter> scratch = new();

    private BrawlShot shot;
    private Transform spriteTransform;
    private SpriteRenderer spriteRenderer;
    private Transform glowTransform;
    private SpriteRenderer glowRenderer;
    private TrailRenderer trail;
    private Vector3 planar, dir, lobStart, lobEnd;
    private float lobArc, lobT, groundY, height, traveled, age, spinAngle, iconSize;
    private int bouncesLeft;
    private bool returning, live, glowOn;

    public BrawlShot Shot => shot;

    public static BrawlProjectile Fire(BrawlShot shot)
    {
        var projectile = Acquire();
        projectile.Launch(shot);
        return projectile;
    }

    public static void ClearAll()
    {
        for (int i = active.Count - 1; i >= 0; i--)
        {
            var projectile = active[i];
            if (projectile != null) projectile.Release();
            else active.RemoveAt(i);
        }
    }

    private static BrawlProjectile Acquire()
    {
        while (pool.Count > 0)
        {
            var pooled = pool[pool.Count - 1];
            pool.RemoveAt(pool.Count - 1);
            if (pooled != null) return pooled;
        }
        return Create();
    }

    private static BrawlProjectile Create()
    {
        if (root == null) root = new GameObject("BrawlProjectiles").transform;
        var go = new GameObject("BrawlProjectile");
        go.transform.SetParent(root, false);
        var projectile = go.AddComponent<BrawlProjectile>();

        var spriteGo = new GameObject("Sprite");
        spriteGo.transform.SetParent(go.transform, false);
        projectile.spriteTransform = spriteGo.transform;
        projectile.spriteRenderer = spriteGo.AddComponent<SpriteRenderer>();
        projectile.spriteRenderer.sortingOrder = IconSortingOrder;
        projectile.spriteRenderer.shadowCastingMode = ShadowCastingMode.Off;

        var glowGo = new GameObject("Glow");
        glowGo.transform.SetParent(go.transform, false);
        projectile.glowTransform = glowGo.transform;
        projectile.glowRenderer = glowGo.AddComponent<SpriteRenderer>();
        projectile.glowRenderer.sortingOrder = IconSortingOrder - 1;
        projectile.glowRenderer.shadowCastingMode = ShadowCastingMode.Off;
        projectile.glowRenderer.enabled = false;

        projectile.trail = go.AddComponent<TrailRenderer>();
        projectile.trail.minVertexDistance = 0.05f;
        projectile.trail.shadowCastingMode = ShadowCastingMode.Off;
        projectile.trail.receiveShadows = false;
        return projectile;
    }

    private static Vector3 Flat(Vector3 v)
    {
        v.y = 0f;
        return v.sqrMagnitude > 0.0001f ? v.normalized : Vector3.zero;
    }

    private void OnDestroy()
    {
        active.Remove(this);
        pool.Remove(this);
    }

    private void Launch(BrawlShot s)
    {
        shot = s;
        live = true;
        age = traveled = lobT = spinAngle = 0f;
        returning = false;
        bouncesLeft = s.Bounces;
        struck.Clear();
        height = s.Height > 0f ? s.Height : DefaultHeight;

        groundY = s.Origin.y - height;
        if (NavMesh.SamplePosition(s.Origin, out var nav, 3f, NavMesh.AllAreas)) groundY = nav.position.y;
        planar = new Vector3(s.Origin.x, groundY, s.Origin.z);

        dir = Flat(s.Direction);
        if (s.Lob)
        {
            lobStart = planar;
            lobEnd = new Vector3(s.LobTarget.x, groundY, s.LobTarget.z);
            lobArc = Mathf.Max(2f, Vector3.Distance(lobStart, lobEnd) * 0.35f);
            dir = Flat(lobEnd - lobStart);
        }
        if (dir == Vector3.zero) dir = Vector3.forward;

        ApplyVisual();
        active.Add(this);
        Place(height);
        gameObject.SetActive(true);
        trail.Clear();
    }

    private void ApplyVisual()
    {
        var library = BrawlVfxLibrarySO.Current;
        iconSize = shot.SpriteSize * BrawlTeamLook.Size(shot.Team);
        glowOn = false;
        glowRenderer.enabled = false;
        spriteRenderer.enabled = library != null;
        trail.enabled = library != null && library.LineMaterial != null;
        if (library == null) return;

        bool ally = BrawlTeamLook.IsAlly(shot.Team);
        Color color = BrawlTeamLook.Wash(shot.Theme.Color, shot.Team);
        spriteRenderer.sprite = shot.Theme.Icon != null ? shot.Theme.Icon : library.SparkSprite;
        spriteRenderer.color = color;
        if (library.SpriteMaterial != null) spriteRenderer.sharedMaterial = library.SpriteMaterial;

        if (library.LineMaterial != null) trail.sharedMaterial = library.LineMaterial;
        BrawlProjectileTrail.Apply(trail, shot, library.ProjectileTrailTime, shot.SpriteSize * 0.45f * (ally ? 1f : RivalTrailWidth), color);

        glowOn = ally && library.GlowSprite != null;
        glowRenderer.enabled = glowOn;
        if (!glowOn) return;
        glowRenderer.sprite = library.GlowSprite;
        if (library.ParticleAdditiveMaterial != null) glowRenderer.sharedMaterial = library.ParticleAdditiveMaterial;
        Color glow = color;
        glow.a = GlowAlpha;
        glowRenderer.color = glow;
    }

    private void Place(float lift)
    {
        transform.position = planar + Vector3.up * lift;
    }

    private void Release()
    {
        if (!live) return;
        live = false;
        active.Remove(this);
        gameObject.SetActive(false);
        pool.Add(this);
    }

    private void Update()
    {
        if (!live) return;
        float dt = Time.deltaTime;
        age += dt;
        if (shot.Lob)
        {
            StepLob(dt);
            return;
        }
        if (shot.Boomerang)
        {
            if (!StepBoomerang(dt)) return;
        }
        else
        {
            Steer(dt);
            if (!StepStraight(dt)) return;
        }
        if (!ResolveHits()) return;
        if (!shot.Boomerang && traveled >= shot.Range)
        {
            if (shot.ExplodeRadius > 0f) Explode(planar);
            Release();
        }
    }

    private void LateUpdate()
    {
        if (!live) return;
        spinAngle += shot.Spin * Time.deltaTime;
        spriteTransform.localScale = Vector3.one * iconSize;
        var cam = Camera.main;
        Quaternion facing = Quaternion.identity;
        if (cam != null)
        {
            facing = cam.transform.rotation * Quaternion.AngleAxis(spinAngle, Vector3.forward);
            spriteTransform.rotation = facing;
        }
        if (!glowOn) return;
        float pulse = 1f + GlowPulseAmount * Mathf.Sin(Time.time * GlowPulseHz * Mathf.PI * 2f);
        glowTransform.localScale = Vector3.one * (iconSize * GlowScale * pulse);
        if (cam != null) glowTransform.rotation = facing;
    }

    private void StepLob(float dt)
    {
        lobT += dt / Mathf.Max(0.01f, shot.LobSeconds);
        float t = Mathf.Clamp01(lobT);
        planar = Vector3.Lerp(lobStart, lobEnd, t);
        Place(height + 4f * lobArc * t * (1f - t));
        if (lobT < 1f) return;
        Explode(lobEnd);
        Release();
    }

    private void Steer(float dt)
    {
        var target = shot.Homing;
        if (target == null || !target.IsAlive) return;
        Vector3 toward = Flat(target.Position - planar);
        if (toward == Vector3.zero) return;
        float turn = (shot.HomingTurn > 0f ? shot.HomingTurn : DefaultHomingTurn) * Mathf.Deg2Rad * dt;
        dir = Vector3.RotateTowards(dir, toward, turn, 0f);
    }

    private bool StepStraight(float dt)
    {
        float step = shot.Speed * dt;
        Vector3 next = planar + dir * step;
        if (NavMesh.Raycast(planar, next, out var wall, NavMesh.AllAreas))
        {
            if (bouncesLeft <= 0)
            {
                HitWall(wall.position);
                return false;
            }
            Bounce(wall);
            return true;
        }
        traveled += step;
        planar = next;
        Place(height);
        return true;
    }

    private void Bounce(NavMeshHit wall)
    {
        Vector3 normal = Flat(wall.normal);
        if (normal == Vector3.zero) normal = -dir;
        traveled += Vector3.Distance(planar, wall.position);
        dir = Flat(Vector3.Reflect(dir, normal));
        bouncesLeft--;
        planar = new Vector3(wall.position.x, groundY, wall.position.z) + dir * 0.05f;
        Place(height);
    }

    private void HitWall(Vector3 point)
    {
        Vector3 ground = new Vector3(point.x, groundY, point.z);
        if (shot.ExplodeRadius > 0f) Explode(ground);
        else EmitBurst(ground, WallBurstRadius);
        Release();
    }

    private bool StepBoomerang(float dt)
    {
        float step = shot.Speed * dt;
        if (!returning)
        {
            Vector3 next = planar + dir * step;
            if (NavMesh.Raycast(planar, next, out _, NavMesh.AllAreas))
            {
                TurnBack();
                return true;
            }
            traveled += step;
            planar = next;
            Place(height);
            if (traveled >= shot.Range) TurnBack();
            return true;
        }

        if (shot.Owner == null || !shot.Owner.IsAlive || age >= BoomerangMaxSeconds)
        {
            Release();
            return false;
        }
        Vector3 toOwner = shot.Owner.Center - planar;
        toOwner.y = 0f;
        float distance = toOwner.magnitude;
        if (distance < BoomerangCatchDistance)
        {
            Release();
            return false;
        }
        dir = toOwner / distance;
        planar += dir * Mathf.Min(step, distance);
        Place(height);
        return true;
    }

    private void TurnBack()
    {
        returning = true;
        struck.Clear();
    }

    private bool ResolveHits()
    {
        var all = BrawlFighter.All;
        bool any = false;
        for (int i = 0; i < all.Count; i++)
        {
            var f = all[i];
            if (f == null || !f.IsAlive || struck.Contains(f)) continue;
            if (BrawlQuery.Planar(f.Position, planar) >= shot.Radius + f.Radius) continue;

            if (ExpeditionTeams.AreRivals(shot.Team, f.Team))
            {
                if (shot.Damage <= 0f) continue;
                Strike(f, dir);
            }
            else if (f != shot.Owner && ExpeditionTeams.AreAllies(shot.Team, f.Team) && shot.HealsAllies && shot.Heal > 0f && f.Hp01 < 1f)
            {
                f.Heal(shot.Heal, shot.Owner);
            }
            else continue;

            struck.Add(f);
            any = true;
        }

        if (!any || shot.Pierce) return true;
        if (shot.ExplodeRadius > 0f) Explode(planar);
        Release();
        return false;
    }

    private void Strike(BrawlFighter target, Vector3 knockDir)
    {
        target.TakeDamage(new BrawlHit
        {
            Amount = shot.Damage, Source = shot.Owner, Point = target.Center, KnockDir = knockDir,
            Knockback = shot.Knockback, Theme = shot.Theme, FromSkill = shot.FromSkill
        });
        if (shot.Slow > 0f && shot.SlowSeconds > 0f) target.ApplySlow(shot.Slow, shot.SlowSeconds);
        if (shot.StunSeconds > 0f) target.ApplyStun(shot.StunSeconds);
    }

    private void Explode(Vector3 center)
    {
        if (shot.Damage > 0f)
        {
            BrawlQuery.FoesWithin(center, shot.ExplodeRadius, shot.Team, scratch);
            for (int i = 0; i < scratch.Count; i++)
            {
                var f = scratch[i];
                if (struck.Contains(f)) continue;
                Vector3 away = Flat(f.Position - center);
                Strike(f, away == Vector3.zero ? dir : away);
            }
        }

        if (shot.HealsAllies && shot.Heal > 0f)
        {
            BrawlQuery.AlliesWithin(center, shot.ExplodeRadius, shot.Team, scratch);
            for (int i = 0; i < scratch.Count; i++)
            {
                if (!struck.Contains(scratch[i])) scratch[i].Heal(shot.Heal, shot.Owner);
            }
        }

        EmitBurst(center, shot.ExplodeRadius);
    }

    private void EmitBurst(Vector3 point, float radius)
    {
        BrawlFx.Emit(new BrawlFxEvent
        {
            Kind = BrawlFxKind.Burst, From = point, To = point, Radius = radius,
            Theme = shot.Theme, Team = shot.Team, Source = shot.Owner
        });
    }
}
}
