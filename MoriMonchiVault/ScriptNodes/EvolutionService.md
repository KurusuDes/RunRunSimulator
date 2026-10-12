---
tags: [script, system, evolution, static, economy]
---

# EvolutionService.cs

**Ruta:** `Systems/Evolution/EvolutionService.cs`

**Responsabilidad:** Orquesta una evolución de partes con Minerita: valida, cobra y aplica. Clase estática sin estado. Devuelve la parte que subió o `null`. No persiste: emite `GameEvents.RegistryChanged` y `GameManager` guarda.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Método Público

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `Evolve(dna, effect, registry)` | `PartRole?` | Valida, cobra y aplica un efecto de evolución |

## Flujo de `Evolve`

1. Si `dna`, `effect` o `registry` son null, devuelve `null`.
2. Si `effect.CanApply(dna)` es false, devuelve `null`.
3. `cost = effect.Cost(dna)` y `Wallet.TrySpend(Currency.Minerita, cost, "evolution")`. Si no alcanza, devuelve `null`.
4. `effect.Apply(dna)` cambia el tier y devuelve la parte.
5. Si hubo parte, `Debug.Log` con el ID, la parte, el nuevo tier y el costo.
6. `GameEvents.RegistryChanged(registry)`, siempre después de cobrar.
7. Devuelve la parte.

## Notas

- El cobro ocurre antes de `Apply`. Con `PartLevelUpEffectSO` no hay riesgo: su `Apply` vuelve a validar lo mismo que `CanApply`. Una implementación futura que pudiera devolver `null` tras cobrar perdería la Minerita sin subir la parte.
- El botón de la ficha (`DetailEvolutionBlock.BuildAction`) usa el mismo criterio: `CanApply` y saldo de Minerita mayor o igual al costo.
- Persistencia por evento (regla 2): no llama `SaveSystem` ni `PushToCloud`.

## Conexiones

- [[EvolutionEffectSO]], [[PartLevelUpEffectSO]] — reglas y aplicación del cambio
- [[DetailEvolutionBlock]] — llama `Evolve` desde el botón de la ficha
- [[Wallet]] — `TrySpend(Currency.Minerita)`
- [[GameEvents]] — `RegistryChanged`
- [[CreatureRegistrySO]] — registro que se notifica
- [[GameManager]] — persiste al recibir `RegistryChanged`
