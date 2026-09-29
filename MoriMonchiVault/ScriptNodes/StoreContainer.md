---
tags: [script, world, container, store]
---

# StoreContainer.cs

**Ruta:** `World/Containers/StoreContainer.cs`

**Responsabilidad:** Vitrina de tienda exhibe criaturas. **S138:** Overridea Capacity para sumar bonus de mejora. Rechaza Eggs (Form=Egg). Restaura necesidades. Gestiona slots de NPCs para inspeccionar.

## S138 Cambios

**Capacidad dinámica:**
```csharp
protected override int Capacity => base.Capacity + (capacityUpgrade != null ? capacityUpgrade.CurrentBonus : 0);
```

**Accepts():**
```csharp
protected override bool Accepts(MoriMochiAgent agent) => agent.DNA == null || agent.DNA.Form != MonchiForm.Egg;
```

Rechaza Eggs (solo Slime/Adult). Vitrina es para criaturas vendibles, no incubables.

## Campos

| Campo | Tipo | Propósito |
|-------|------|----------|
| `capacityUpgrade` | ShopUpgradeSO | Mejora que suma ocupantes (upgrade bonus) |
| `restoreRate` | float | Necesidades restauradas/s |
| `usePoints` | List<Transform> | Puntos donde NPCs inspeccionan |

## API Pública

- `Capacity` (virtual override) — base + upgrade.CurrentBonus
- `HasFreeUsePoint` { get; } — hay slot disponible
- `TryReserveUsePoint()` — reserva slot cercano, snappea NavMesh
- `ReleaseUsePoint()` — libera slot

## Conexiones

- [[MoriMochiContainer]] (base), [[ShopUpgradeSO]], [[NpcAgent]], [[AnchorRegistry]]
