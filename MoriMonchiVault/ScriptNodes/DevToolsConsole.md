---
tags: [script, dev-tools, utility]
---

# DevToolsConsole.cs

**Ruta:** `Core/DevToolsConsole.cs`

**Responsabilidad:** Componente de desarrollo con botones de Odin (`[Button]`) agrupados por `BoxGroup`. Opera sobre `GameManager` (inventario y registro de MoriMonchis), `GameClock` y `ExpeditionBridge`. Solo para desarrollo, no es gameplay. Cuando cambia el inventario o el registro, emite `GameEvents.InventoryChanged` o `GameEvents.RegistryChanged`; no guarda nada por sí mismo.

Los botones que tocan MoriMonchis, el reloj y la expedición exigen Play (`Application.isPlaying`). Los de Dabloons y genética no.

## Campos Serializados

| Campo | Tipo | Grupo | Descripción |
|-------|------|-------|-------------|
| `gameManager` | `GameManager` | Setup | Required. Fuente de `Inventory`, `Registry` y `MintCreature()` |
| `expeditionBridge` | `ExpeditionBridge` | Expedition (DEV) | Destino de "Salir de expedición" |
| `devDabloonsAmount` | `int` (default 500) | Dev Tools | Dabloons que suma "Add Dabloons" |
| `devAdultCount` | `int` (default 3, mín. 1) | MoriMonchis (DEV) | Adultos que crea "Crear adultos" |

## Botones

| Grupo | Botón | Acción |
|-------|-------|--------|
| Dev Tools | Add Dabloons (DEV) | `Wallet.Add(Currency.Dabloons, devDabloonsAmount, "dev")` |
| Dev Tools | Reset Dabloons (DEV) | `inventory.ResetCurrency(Dabloons)` y `GameEvents.InventoryChanged` |
| Dev Tools | Clear Furniture Owned (DEV) | `inventory.ClearFurnitureOwned()` y `InventoryChanged` |
| Dev Tools | Clear World Props (DEV) | `ClearWorldPropsStored()`, `ClearHotbar()` y `InventoryChanged` |
| Genetics (DEV) | Reroll Potentials (DEV) | Nuevos `HornPotential`, `BackPotential` y `WingPotential` (`CreatureGenerator.RandomMintPotential()`) en vivos no vendidos, y `RegistryChanged` |
| MoriMonchis (DEV) | Crear adultos (DEV) | `gameManager.MintCreature()` × `devAdultCount`, con `Form = Adult` y necesidades a 100, y `RegistryChanged` |
| MoriMonchis (DEV) | Pasar Slimes a adultos (DEV) | `Slime` → `Adult` en vivos no vendidos, y `RegistryChanged` |
| MoriMonchis (DEV) | Cuidar a todos (DEV) | Salud, energía y afecto a 100 en vivos no vendidos, y `RegistryChanged` |
| Expedition (DEV) | Salir de expedición (DEV) | `expeditionBridge.Depart()` |
| Reloj (DEV) | Siguiente bloque (DEV) | `GameClock.Instance.AdvanceToNextBlock()` |
| Reloj (DEV) | Siguiente día (DEV) | `GameClock.Instance.AdvanceToNextDay()` |
| Reloj (DEV) | Ir a la noche (DEV) | Avanza bloques hasta `Block.ExpeditionOpen`, con máximo 8. Si ya es de noche, no hace nada |

## Conexiones

- [[GameManager]] — `Inventory`, `Registry`, `MintCreature()`
- [[GameClock]] — `Instance`, `Block`, `AdvanceToNextBlock()`, `AdvanceToNextDay()`
- [[ExpeditionBridge]] — `Depart()`
- [[GameEvents]] — `InventoryChanged`, `RegistryChanged`
- [[CreatureGenerator]] — `RandomMintPotential()`
- [[Wallet]] — `Add`
- [[CreatureDNA]] — `Form`, `Needs`, `IsDead`, `IsSold`, potenciales

## Cambios

- S131: grupo de reloj con "Siguiente bloque" y "Siguiente día".
- S146: grupo MoriMonchis (DEV) (crear adultos, pasar slimes a adultos, cuidar a todos) y "Ir a la noche (DEV)" en el grupo de reloj.

## Notas

- Los botones de genética y cuidado solo tocan MoriMonchis vivos y no vendidos (`IsDead`, `IsSold`).
- "Ir a la noche" busca el bloque con `ExpeditionOpen` y avisa si no lo encuentra en 8 avances.
