---
tags: [script, world, expedition, sandbox]
---

# ArenaSandbox.cs

**Ruta:** `World/Expedition/ArenaSandbox.cs`

**Responsabilidad:** Escena sandbox de arena que encapsula flujo completo: BuildRoom (layout, minerales, planner.Prepare) → SpawnCast → ResetRoom. Lee SelectedIds de ExpeditionHandoff; si no vacío, fuerza esas 3 criaturas del jugador. Asigna Role a rivales (abre bases). Expone FloorKind (Enemies/Buff) y AllMaterialTaken. Rivales minteados nacen con Generation=1 sin variación de stats. **S135:** pasa `creatureDatabase` a `abilityDatabase.Resolve()` para soporte de habilidades por partes modulares. **S151:** revisado; los tags de nombre de los elencos se crean sin atenuación por mirada (`FadeUnlessLooked = false`) con la distancia de muestra de `tagShowDistance` y `tagReferenceDistance`.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `creaturePrefab` | `MoriMonchiController` | Prefab de agente |
| `profileTable` | `RoleWorldProfileSO` | Tabla de roles de mundo |
| `socialTuning` | `SocialTuningSO` | Parámetros de interacción social |
| `expeditionRules` | `ExpeditionRulesSO` | Reglas de expedición (se activan en OnEnable) |
| `clashTuning` | `ClashTuningSO` | Parámetros de choque físico |
| `abilityDatabase` | `AbilityDatabaseSO` | DB de habilidades (S135: consultado con creatureDatabase) |
| `visualBank` | `MonchiVisualBankSO` | Banco de mallas visuales |
| `furDatabase` | `FurTypeDatabaseSO` | Base de pelajes |
| `creatureDatabase` | `CreatureDatabaseSO` | DB de partes (S135: pasado a abilityDatabase.Resolve()) |
| `roster` | `ArenaRosterSO` | Elenco de rivales pre-generados; null si `useRoster` es false |
| `castMode` | `ArenaCastMode` | Roster o LocalSave |
| `layout` | `ArenaLayoutBuilder` | Geometría de sala |
| `palette` | `ArenaPaletteApplier` | Texturas/paleta |
| `mineralPrefab`, `exitPrefab` | `MaterialPickup`, `ExitZone` | Minerales y salidas por equipo |
| `keepNeedsFull` | bool | Mantiene salud, energía y afecto de los spawneados en 100 (default true) |
| `tagShowDistance`, `tagReferenceDistance` | float | Distancia de muestra y de escala de las placas de nombre del elenco (60 y 14) |

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `void BuildRoom()` | Construye sala: layout, paleta, salidas, minerales, tableros de equipo y `planner.Prepare(activeSeed, castSeed, count)`; respeta SelectedIds |
| `void SpawnCast()` | Spawnea elenco planeado; asigna Role; invoca `abilityDatabase.Resolve(dna, creatureDatabase)` (S135) |
| `void ResetRoom(bool newSeed)` | Limpia cast/minerales/exits; genera nueva semilla si newSeed |
| `void SetFloor(int seed, ArenaFloorKind kind)` | Configura tipo piso (Enemies/Buff); `RivalsEnabled` solo en Enemies |
| `void SetCastMode(ArenaCastMode mode)` | Setter de modo (Roster vs LocalSave) |
| `void ShuffleCast()` / `SelectLocalCast(picks)` | Re-tira el elenco o fija la selección local |
| `void SetPaletteIndex(int)` / `CyclePalette()` | Paleta de la sala |
| `ReadRoom(team)` | Lectura de la sala para el equipo (distancias y vetas) |
| `Respawn()` / `Reseed()` | Botones de inspector: rehacen la sala y el elenco |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Spawned` | `IReadOnlyList<MoriMonchiController>` | Criaturas activas en escena |
| `Exits` | `IReadOnlyList<ExitZone>` | Salidas (Player, Rival si Enemies) |
| `PlannedCast` | `IReadOnlyList<ArenaCastEntry>` | Elenco planeado por Planner |
| `ActiveSeed` | `int` | Semilla activa |
| `CastMode` | `ArenaCastMode` | Modo (Roster/LocalSave) |
| `HasTeams` | `bool` | True si hay equipos |
| `TeamLocked` | `bool` | True si SelectedIds no vacío |
| `FloorKind` | `ArenaFloorKind` | Tipo piso (S124: Enemies/Buff) |
| `AllMaterialTaken` | `bool` | True si todos minerales recogidos y ningún material suelto ni cargado (S124) |
| `EntryName`, `PaletteName`, `ShapeName` | `string` | Datos de la sala para la UI |
| `ActiveShape`, `PlacedObstacles` | | Forma y obstáculos del layout |
| `BoardFor(team)` | `TeamBlackboard` | Pizarrón de equipo (se crea perezosamente) |
| `ExitFor(team)` | `ExitZone` | Salida de un equipo |

## Ciclo de Vida

```
OnEnable → ExpeditionRulesSO.Activate(expeditionRules)
Start()
  → CameFromStore? SetFloor(FloorSeedOf(RunSeed, 1), Enemies)
  → BuildRoom()
  → TeamLocked? SelectLocalCast(picks de SelectedIds)
  → SpawnCast() (si autoSpawnCast)
    → abilityDatabase.Resolve(dna, creatureDatabase) [S135]
  → AgentAbilities.Bind(abilities)

Durante ronda:
  → ArenaRound.Update() monitorea FloorKind + AllMaterialTaken

Fin piso:
  → ArenaRunDirector.Continue() llama SetFloor(nextFloorSeed, nextFloorKind)

OnDisable → ExpeditionRulesSO.Deactivate(expeditionRules)
```

## Cambios S135

**Firma Resolve() actualizada:**

```csharp
var abilities = abilityDatabase.Resolve(dna, creatureDatabase);
//                                        ↑   ↑
//                                        |   └── NUEVO S135
//                                        └── Permite BodyPart.Ability primero
```

Impacto: Ahora consulta BodyPart.Ability de partes modulares antes de fallback hash.

## Invariantes S120-S129-S135

- SelectedIds no vacío = elenco forzado
- Buff pisos: RivalsEnabled = false
- Rivales minteados: Generation = 1, sin variación de stats
- AllMaterialTaken evalúa cada frame (O(n) pequeño)
- FloorKind determina lógica de salidas y fin anticipado
- abilityDatabase siempre recibe creatureDatabase (S135)
- `keepNeedsFull` sobreescribe las necesidades cada frame (solo para pruebas de sala)

## Vinculado a

- [[Index/24 - Puente Tienda-Arena]]
- [[Index/22 - Bajada Nocturna y Linaje]]
- [[Index/26 - Plan H0 - Bajada por pisos]]

## Conexiones

[[AbilityDatabaseSO]], [[CreatureDatabaseSO]], [[ExpeditionHandoff]], [[ExpeditionRulesSO]], [[ArenaCastPlanner]], [[ArenaBases]], [[ArenaRound]], [[ArenaRunDirector]], [[ArenaLayoutBuilder]], [[MoriMochiAgent]], [[MoriMonchiController]], [[AgentAbilities]], [[NameTag]] (tags del elenco)
