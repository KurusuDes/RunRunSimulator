---
tags: [scriptable-object, database, expedition]
---

# AbilityDatabaseSO.cs

**Ruta:** `Data/Expedition/AbilityDatabaseSO.cs`

**Responsabilidad:** Base de datos que resuelve habilidades de un agente según genética (Horn/Wings/Back). Mapea DNA → array [HornAbility, WingAbility, BackAbility]. Resolución en dos niveles: (1) consulta BodyPart.Ability si existe, (2) fallback a selección determinística por StableHash(partID) filtrando por Slot.

**S118:** Introducida lógica de habilidades dinámicas.
**S135:** Ahora consulta BodyPart.Ability primero (creando nexo con PartDatabaseSO).

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Abilities` | `List<AbilitySO>` | Pool de habilidades disponibles (~20, una por variante/slot) |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Resolve(CreatureDNA dna, CreatureDatabaseSO parts)` | `AbilitySO[]` | Resuelve array [Horn, Wing, Back] según genética y PartDatabase |

## Flujo de Resolve (S135)

```
Para cada slot (Horn, Wing, Back):
  1. dna.HornID/WingID/BackID → parts.GetHorn/GetWing/GetBack(id)
  2. Si parte != null y parte.Ability != null → retorna parte.Ability
  3. Si no → fallback: Pick(partID, slot)
    - Filtra Abilities por Slot == slot
    - StableHash(partID) % candidates.Count → índice determinístico
    - Retorna candidates[index] o null
```

## Métodos Privados

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Pick(string partId, ClashSlot slot)` | `AbilitySO` | Fallback hash: selecciona habilidad determinísticamente por slot |
| `StableHash(string s)` | `int` | Hash determinista (h = h*31 + c, máscara 0x7fffffff) |

## Parámetros Resolve (S135)

Ahora acepta `CreatureDatabaseSO parts` como segundo parámetro:
- Permite acceso a partes específicas y sus AbilitySOs
- Si parte.Ability asignada → usa esa (prioridad máxima)
- Si no → fallback hash

## Invariantes

- **Determinismo:** mismo DNA/partID → siempre misma habilidad (replay, multiplayer)
- **Prioridad:** BodyPart.Ability > hash fallback
- **Null-safe:** si partId null o no hay candidatos → retorna null
- **Un slot por tipo:** exactamente 3 abilities (una por Horn/Wing/Back) en el array resuelto

## Ejemplo S135

```csharp
// DNA: "BS0-H1-BK2-W0-RRGGBB"
// HornDatabase.GetHorn("H1") → HornPart con Ability = AbilityFireStrike
// abilityDatabase.Resolve(dna, partDatabase)
// → [FireStrike, [fallback Wings], [fallback Back]]
```

## Integración

- Referenciado en `ArenaSandbox` (campo `abilityDatabase`)
- Llamado en `ArenaSandbox.SpawnAgent()` antes de `AgentAbilities.Bind()`
- Array resuelto pasa directamente a Bind() para asignación a agente

## Cambios S135

**Firma Resolve() actualizada:**
- Antes: `Resolve(CreatureDNA dna)` → solo usaba Pick/hash
- Ahora: `Resolve(CreatureDNA dna, CreatureDatabaseSO parts)` → consulta partes primero

**Impacto:** Permite habilidades únicas por parte modular sin duplicar en pool Abilities

## Vinculado a

- [[Index/23 - Arena Sandbox & Expedicion]]
- [[Index/02 - Genetics & Breeding]]

## Conexiones

[[AbilitySO]], [[BodyPart]], [[PartDatabaseSO]], [[CreatureDatabaseSO]], [[CreatureDNA]], [[AgentAbilities]], [[ArenaSandbox]], [[ClashSlot]]
