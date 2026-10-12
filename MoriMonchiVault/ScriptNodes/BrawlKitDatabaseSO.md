---
tags: [script, data, so]
---

# BrawlKitDatabaseSO.cs

**Ruta:** `Data/Brawl/BrawlKitDatabaseSO.cs`

**Responsabilidad:** Hub de lookup para alas, habilidades y escalones de mejora en Brawl. Contiene listas de `BrawlWingKitSO` (6 alas), `BrawlSkillSO` (33 habilidades) y `BrawlUpgradeStep` del cuerpo (`BodyUpgrades`). Métodos `Wing()` y `Skill()` resuelven por ID con fallback; `Upgrades()` resuelve los escalones de cualquier parte.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Estructura

```csharp
[CreateAssetMenu(fileName = "BrawlKitDatabase", menuName = "MoriMonchi/Brawl/Kit Database")]
public class BrawlKitDatabaseSO : ScriptableObject
{
    public List<BrawlWingKitSO> Wings = new();
    public List<BrawlSkillSO> Skills = new();
    public List<BrawlUpgradeStep> BodyUpgrades = new();

    public IReadOnlyList<BrawlUpgradeStep> Upgrades(CreatureDNA dna, PartRole role);
    public BrawlWingKitSO Wing(string partId);
    public BrawlSkillSO Skill(string partId, ClashSlot slot);
}
```

## Métodos Públicos

### Upgrades(CreatureDNA dna, PartRole role)

Devuelve los escalones de la parte indicada. Nunca devuelve null: si no hay escalones, una lista vacía de solo lectura.

| Rol | Fuente |
|-----|--------|
| `Body` | `BodyUpgrades` |
| `Horn` | `Skill(dna.HornID, ClashSlot.Horn)?.Upgrades` |
| `Back` | `Skill(dna.BackID, ClashSlot.Back)?.Upgrades` |
| `Wing` | `Wing(dna.WingID)?.Upgrades` |
| Otros (Face) | Vacío |

Si `dna` es null, devuelve vacío. Cuerno y espalda heredan el fallback de `Skill()`, y ala el de `Wing()`.

### Wing(string partId)

```csharp
public BrawlWingKitSO Wing(string partId)
{
    for (int i = 0; i < Wings.Count; i++)
    {
        var kit = Wings[i];
        if (kit != null && kit.PartId == partId) return kit;
    }
    return Wings.Count > 0 ? Wings[0] : null;  // Fallback a primer ala
}
```

**Búsqueda:**
- Itera sobre Wings por PartId (ej. "W0", "W1")
- Si encuentra, retorna inmediatamente
- Si no, retorna Wings[0] (fallback a primera ala) o null si lista vacía

**Casos de uso:**
- `BrawlKitProfile` (llamado desde `BrawlFighter.Bind`) → `Wing(dna.WingID)`

### Skill(string partId, ClashSlot slot)

```csharp
public BrawlSkillSO Skill(string partId, ClashSlot slot)
{
    // Búsqueda 1: por PartId exacto
    for (int i = 0; i < Skills.Count; i++)
    {
        var skill = Skills[i];
        if (skill != null && skill.PartId == partId) return skill;
    }

    // Búsqueda 2: fallback por Slot (cualquier skill con ese slot)
    for (int i = 0; i < Skills.Count; i++)
    {
        var skill = Skills[i];
        if (skill != null && skill.Slot == slot) return skill;
    }

    return null;  // No encontrado
}
```

**Búsqueda en dos fases:**
1. **Exacta:** PartId == (ej. "H1" Ariete → retorna skill del Ariete)
2. **Fallback:** Cualquier skill con Slot == (ej. ClashSlot.Horn → retorna cualquier skill de cuerno)

**Casos de uso:**
- `BrawlKitProfile` (llamado desde `BrawlFighter.Bind`) → `Skill(dna.HornID, ClashSlot.Horn)` y `Skill(dna.BackID, ClashSlot.Back)`
- Si partId no existe en DB, fallback a cualquier skill del slot

## Contenido Esperado S142

| Lista | Cantidad | Descripción |
|-------|----------|-------------|
| Wings | 6 | W0-W5 (Vela, Colibrí, Aletas, Cintas, Plumitas, Murciélago) |
| Skills | ~33 | Cuernos (H0-H14) + Espaldas (B0-B17) |
| BodyUpgrades | Lista de escalones | Escalones del cuerpo (HP y velocidad) |

## Dependencias

**Entrada:**
- Linkado en inspector en prefab de `BrawlFighter` (referencias `BrawlKitDatabase.asset`)
- Linkado en `BrawlMatch` para acceso global
- Linkado en `PartLevelUpEffectSO.Kits` y en `MorimonchiDetailInfoUITK.kits`

**Salida:**
- `BrawlKitProfile` (desde `BrawlFighter.Bind`) usa `Wing()` y `Skill()`
- `BrawlFighter.Bind` lee `BodyUpgrades` para `BrawlUpgrades.Body`
- `DetailEvolutionBlock` y `PartLevelUpEffectSO` usan `Upgrades()`
- `CreatureGenerator` (tienda) usa para traducir BodyPart ID → BrawlKit en arena

## Notas S142

- Asset único en el proyecto (`Assets/RunRunSimulator/Resources/Brawl/BrawlKitDatabase.asset`)
- Fallback a Wings[0] evita crash si partId inválido
- Fallback a Slot cualquier skill evita skill=null (siempre hay cuerno/espalda disponible)
- No hay validación: si Wings está vacía, Wing() retorna null
- Orden en listas no importa (búsqueda lineal por ID)
- Usar Create menu en inspector: `Create > MoriMonchi > Brawl > Kit Database`

## Notas S148

- `BodyUpgrades` es la lista de escalones del cuerpo. Solo afecta HP y velocidad.
- Los escalones de cuerno, espalda y ala viven en cada SO (`BrawlSkillSO.Upgrades`, `BrawlWingKitSO.Upgrades`), no aquí.
- `Upgrades()` solo lee. Las copias mejoradas las hace `BrawlUpgrades` sobre instancias en `BrawlFighter`.
