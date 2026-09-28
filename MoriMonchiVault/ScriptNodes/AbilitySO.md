---
tags: [scriptable-object, data, expedition]
---

# AbilitySO.cs

**Ruta:** `Data/Expedition/AbilitySO.cs`

**Responsabilidad:** ScriptableObject que define una habilidad individual (Damage, Mobility, Passive) de un MoriMochi. Mapea intención → ClashMove (Damage) o buff velocidad (Mobility), con cooldown y disparadores (RivalInReach, Fleeing, Chasing). Pasivas otorgan stats operacionales. Resolucionable por AbilityDatabaseSO vía PartIds explícitas O hash determinístico.

**S118:** Agregados `AbilityRole (Basic/Super)` y carga acumulable (ChargeOnHit/Mined/Secured).
**S135:** Ahora asignables directamente a partes vía `BodyPart.Ability`.

## Enums

| Enum | Valores | Descripción |
|------|---------|-------------|
| `AbilityKind` | Damage, Mobility, Passive | Tipo de habilidad |
| `AbilityRole` | Basic, Super | Clasificador de Damage (S118) |
| `AbilityChargeSource` | Hit, Mined, Secured | Fuentes de carga para Supers (S118) |
| `AbilityTrigger` [Flags] | None, RivalInReach, Fleeing, Chasing | Triggers automáticos |

## Campos Serializados

### General

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `Name` | `string` | | Nombre mostrado en HUD |
| `Description` | `TextArea` | | Tooltip/descripción larga |
| `Slot` | `ClashSlot` | | Horn, Wings, Back |
| `Kind` | `AbilityKind` | | Damage/Mobility/Passive |
| `Role` | `AbilityRole` | | Basic o Super (solo Damage) |
| `Cooldown` | `float` | Min 0 | Segundos entre disparos (Damage Basic) |
| `Trigger` | `AbilityTrigger` | [EnumToggleButtons] | Flags de activación |
| `Color` | `Color` | | Color renderizado en HUD |

### Daño

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `Move` | `ClashMoveSO` | | Movimiento de choque |
| `MinDistance` | `float` | Min 0 | Distancia mínima requerida |
| `MinRivalsNearby` | `int` | Min 0 | Rivales en rango requeridos |

### Carga (Super, S118)

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `ChargeOnHit` | `float` | 0-1 | Carga acumulada al golpear |
| `ChargeOnMined` | `float` | 0-1 | Carga acumulada al minar |
| `ChargeOnSecured` | `float` | 0-1 | Carga acumulada al asegurar |

### Movilidad

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `SpeedMultiplier` | `float` | Min 1 | Factor de velocidad (1.35 default) |
| `BoostSeconds` | `float` | Min 0 | Duración del buff |

### Pasiva (S109)

| Campo | Tipo | Rango | Descripción |
|-------|------|-------|-------------|
| `CarryCapacity` | `int` | Min 0 | Override capacidad (0 = sin cambio) |
| `LoadedSpeedFactor` | `float` | Min 0 | Multiplicador velocidad cargado |
| `KeepCarryOnKnock` | `bool` | | No suelta carga si golpeado |
| `GuardRadius` | `float` | Min 0 | Radio de custodio |
| `VisibleFrom` | `float` | Min 0 | Distancia visible para rivales |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Triggers(AbilityTrigger t)` | `bool` | Chequea si trigger t está activo |
| `ChargeFor(AbilityChargeSource s)` | `float` | Retorna carga acumulada según fuente (S118) |

## Resolución (S135)

Dos rutas para resolver qué habilidad usa una parte:

1. **Explícita (BodyPart.Ability):** Parte vinculada directamente en inspector (S135)
   - AbilityDatabaseSO.Resolve() consulta `parts.GetHorn(id).Ability` primero
   - Si null, fallback a búsqueda por hash

2. **Hash determinístico:** AbilityDatabaseSO.Pick() filtra por Slot y usa StableHash(partID) para índice
   - Garantiza reproducibilidad en replay/multiplayer
   - Permite variedad sin duplicar AbilitySOs

## Invariantes

- Una habilidad es solo Damage O Mobility O Passive (mutualmente excluyentes)
- Damage Basic requiere Cooldown > 0
- Damage Super no usa cooldown (Charge es mediador)
- Pasivas se aplican en Bind, no hay "disparo"
- CarryCapacity: si múltiples pasivas lo definen, gana el menor
- ChargeOnHit/Mined/Secured: solo consultados si Role == Super

## Cambios S135

**BodyPart.Ability agregado:**
- Partes ahora pueden referenciar AbilitySO directamente
- AbilityDatabaseSO.Resolve() prioriza parte.Ability sobre búsqueda por hash
- Permite habilidades únicas por parte modular sin duplicar lógica

## Vinculado a

- [[Index/23 - Arena Sandbox & Expedicion]]
- [[Index/22 - Bajada Nocturna y Linaje]]

## Conexiones

[[AbilityDatabaseSO]], [[BodyPart]], [[ClashMoveSO]], [[AgentAbilities]], [[ExpeditionStats]], [[CreatureDNA]], [[ClashSlot]]
