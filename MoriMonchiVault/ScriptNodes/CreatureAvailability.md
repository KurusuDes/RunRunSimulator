---
tags: [utility, static, lifecycle]
---

# CreatureAvailability

**Ruta:** `Data/Genetics/CreatureAvailability.cs`

**Responsabilidad:** Utilidad estática que responde si se puede usar una criatura en diferentes contextos. Tres preguntas: libre (sin restricciones), bien cuidada (cumple umbrales de necesidades), apta para explorar (ambas + no es huevo). Calcula cuál es la necesidad más crítica. S137: `CanExplore()` ahora excluye Eggs (Form != MonchiForm.Egg).

## Métodos Públicos

| Método | Parámetros | Retorna | Descripción |
|--------|-----------|---------|-------------|
| `IsFree` | `CreatureDNA dna` | `bool` | ¿No está muerta, vendida ni ocupada (BusyReason)? |
| `IsWellCared` | `CreatureDNA dna`, `CareGateSO gate` | `bool` | ¿Cumple umbrales de `gate` en Health/Energy/Affect?` |
| `CanExplore` | `CreatureDNA dna`, `CareGateSO gate` | `bool` | `IsFree && IsWellCared && Form != Egg` (S137) — lista apta para bajada a arena |
| `WeakestNeed` | `CreatureDNA dna`, `CareGateSO gate` | `NeedType?` | Cuál necesidad está más deficiente (null si bien cuidada) |

## Lógica

**IsFree:** `!IsDead && !IsSold && !IsBusy` (verifica campos de DNA)

**IsWellCared:** Compara `dna.Needs.{Health/Energy/Affect}` contra `gate.{MinHealth/MinEnergy/MinAffect}`. null gate = siempre true.

**CanExplore (S137 MODIFICADO):** 
```csharp
public static bool CanExplore(CreatureDNA dna, CareGateSO gate) =>
    IsFree(dna) && IsWellCared(dna, gate) && dna.Form != MonchiForm.Egg;
```

Cambio: agregado check `dna.Form != MonchiForm.Egg` al final. Razón: huevos no son explorables (no son vivos). Solo slimes y adultos pueden expedición.

**WeakestNeed:** Calcula brecha = `MinX - Needs.X` para cada necesidad, retorna la de mayor brecha. Null si gate=null, dna=null, dna.Needs=null, o ya IsWellCared.

## Caso de uso

- UI: mostrar si criatura puede bajar (CanExplore → mostrar botón)
- UI: hint de qué necesidad cuidar (WeakestNeed → texto "Necesita energía")
- Bajada: filtrar elenco antes de depart (CanExplore, S137: excluye eggs)

## Cambios S137

**CanExplore() — Egg check (línea 18-19 MODIFICADO):**
```csharp
public static bool CanExplore(CreatureDNA dna, CareGateSO gate) =>
    IsFree(dna) && IsWellCared(dna, gate) && dna.Form != MonchiForm.Egg;
```

**Contexto:** Ciclo de vida S137 introduce Eggs (incubable, no vivo) y Slimes (explorador). CanExplore ahora rechaza Eggs explícitamente.

**Impacto:**
- Huevos en incubadora no listados en "criaturas para expedición"
- Solo Slimes y Adults pueden partir
- UI de expedición filtra automáticamente (CanExplore devuelve false para eggs)

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/23 - Arena y bajada nocturna]]
- [[Index/09 - Active Context]] (S137: ciclo de vida)

**Conexiones:** [[CreatureDNA]], [[CareGateSO]], [[NeedsState]], [[MonchiForm]]
