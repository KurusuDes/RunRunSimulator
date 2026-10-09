---
tags: [script, data, brawl, run, config, scriptable-object]
---

# BrawlRunRulesSO.cs

**Ruta:** `Data/Brawl/BrawlRunRulesSO.cs`

**Responsabilidad:** ScriptableObject con los números de la bajada Brawl (costo, pérdida, curación, tramos, rivales, salas de prueba). Es data; su único estado estático es la instancia activa `Current`.

Menú de creación: `MoriMonchi/Brawl/Run Rules`. Asset: `ScriptableObjects/Brawl/BrawlRunRules.asset` (fuente de valores en runtime).

## Campos (agrupados por `[Title]`)

| Grupo | Campo | Default | Descripción |
|-------|-------|---------|-------------|
| Bajada | `DescentCost` | 10 | Dabloons que cuesta bajar |
| Bajada | `LossFraction` | 0.5 | Fracción del botín perdida en derrota |
| Bajada | `HealAfterCombat` | 0.4 | Curación a cada MoriMochi tras ganar un combate |
| Tramos | `MinRooms` / `MaxRooms` | 2 / 5 | Rango de salas por tramo |
| Tramos | `FirstTramoMaxRivals` | 2 | Rivales máximos en el tramo 1 |
| Tramos | `HardFromDepth` | 3 | Desde este tramo, mínimo 2 rivales por combate |
| Rivales | `RivalPowerBase` | 0.85 | Poder base de rivales |
| Rivales | `RivalPowerPerDepth` | 0.1 | Incremento de poder por tramo |
| Rivales | `RivalPowerMax` | 1.5 | Tope de poder |
| Rivales | `MaterialPerRival` | 1 | Botín por rival derrotado (× tramo) |
| Salas de prueba | `DummiesChance` | 0.15 | Probabilidad de sala de muñecos |
| Salas de prueba | `MineralsChance` | 0.15 | Probabilidad de sala de minerales |
| Salas de prueba | `TrialSeconds` | 20 | Duración de la sala de prueba |
| Salas de prueba | `DummyPower` | 2 | Poder de los muñecos |
| Salas de prueba | `DummyHealFraction` | 0.3 | Fracción del daño hecho a muñecos que cura a aliados vivos |
| Salas de prueba | `MineralDamagePerMaterial` | 4000 | Daño a muñecos por unidad de material en minerales |

## Métodos

| Método | Descripción |
|--------|-------------|
| `RivalPower(depth)` | `min(RivalPowerMax, RivalPowerBase + RivalPowerPerDepth × max(0, depth − 1))` |
| `static Activate(rules)` | Fija `Current` |
| `static Deactivate(rules)` | Limpia `Current` solo si es esa misma instancia |

## Estado Estático

- `Current`: instancia activa. Se activa en `ExpeditionBridge.OnEnable` (tienda, para mostrar y cobrar el costo) y en `BrawlRunDirector.Awake` (arena, si llegó desde la tienda).

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

- [[BrawlRun]] — tramos, salas, rivales, botín
- [[BrawlRunDirector]] — `Activate`/`Deactivate`, `DummyPower`
- [[BrawlTrialRoom]] — `TrialSeconds`, `DummyHealFraction`, `MineralDamagePerMaterial`
- [[ExpeditionBridge]] — `DescentCost`, activación en tienda
- [[ExpeditionPanelUITK]] — costo mostrado en el botón Bajar

## Notas

- Los valores de la tabla son los defaults del código; el asset puede diferir.
- Sin dependencias de UI ni de persistencia.
