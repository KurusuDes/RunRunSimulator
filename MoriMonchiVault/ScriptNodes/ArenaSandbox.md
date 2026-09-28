---
tags: [script, world, expedition, sandbox]
---

# ArenaSandbox.cs

**Ruta:** `World/Expedition/ArenaSandbox.cs`

**Responsabilidad:** Escena sandbox de arena que encapsula flujo completo: BuildRoom (layout, minerales, planner.Prepare) → SpawnCast → ResetRoom. Lee SelectedIds de ExpeditionHandoff; si no vacío, fuerza esas 3 criaturas del jugador. Asigna Role a rivales (abre bases). Expone FloorKind (Enemies/Buff) y AllMaterialTaken. Rivales minteados nacen con Generation=1 sin variación de stats. **S135:** Ahora pasa `creatureDatabase` a `abilityDatabase.Resolve()` para soporte de habilidades por partes modulares.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `creaturePrefab` | `MoriMonchiController` | Prefab de agente |
| `profileTable` | `RoleWorldProfileSO` | Tabla de roles de mundo |
| `socialTuning` | `SocialTuningSO` | Parámetros de interacción social |
| `expeditionRules` | `ExpeditionRulesSO` | Reglas de expedición |
| `clashTuning` | `ClashTuningSO` | Parámetros de choque físico |
| `abilityDatabase` | `AbilityDatabaseSO` | DB de habilidades (S135: consultado con creatureDatabase) |
| `visualBank` | `MonchiVisualBankSO` | Banco de mallas visuales |
| `furDatabase` | `FurTypeDatabaseSO` | Base de pelajes |
| `creatureDatabase` | `CreatureDatabaseSO` | DB de partes (S135: pasado a abilityDatabase.Resolve()) |
| `roster` | `ArenaRosterSO` | Elenco de rivales pre-generados; null si LocalSave |
| `layout` | `ArenaLayoutBuilder` | Geometría de sala |
| `palette` | `ArenaPaletteApplier` | Texturas/paleta |

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `void BuildRoom()` | Construye sala: layout, minerales, planner.Prepare(activeSeed, castSeed, count); respeta SelectedIds |
| `void SpawnCast()` | Spawnea elenco + equipos; asigna Role; invoca abilityDatabase.Resolve(dna, creatureDatabase) (S135) |
| `void ResetRoom(bool newSeed)` | Limpia cast/minerales/exits; genera nueva semilla si newSeed |
| `void SetFloor(int seed, ArenaFloorKind kind)` | Configura tipo piso (Enemies/Buff); controla spawning de rivales |
| `void SetCastMode(ArenaCastMode mode)` | Setter de modo (Roster vs LocalSave) |

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
| `AllMaterialTaken` | `bool` | True si todos minerales recogidos (S124) |
| `EntryName` | `string` | Nombre de entrada (layout) |
| `PaletteName` | `string` | Nombre de paleta |
| `ShapeName` | `string` | Nombre de forma de sala |

## Ciclo de Vida

```
Start() 
  → CameFromStore? SetFloor(FloorSeedOf(RunSeed, 1), Enemies)
  → BuildRoom()
  → SpawnCast()
    → abilityDatabase.Resolve(dna, creatureDatabase) [S135]
  → AgentAbilities.Bind(abilities)
  
Durante ronda:
  → ArenaRound.Update() monitorea FloorKind + AllMaterialTaken
  
Fin piso:
  → ArenaRunDirector.Continue() llama SetFloor(nextFloorSeed, nextFloorKind)
```

## Cambios S135

**Firma Resolve() actualizada:**

```csharp
// En SpawnAgent/SpawnCast:
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

## Vinculado a

- [[Index/24 - Puente Tienda-Arena]]
- [[Index/22 - Bajada Nocturna y Linaje]]
- [[Index/26 - Plan H0 - Bajada por pisos]]

## Conexiones

[[AbilityDatabaseSO]], [[CreatureDatabaseSO]], [[ExpeditionHandoff]], [[ArenaCastPlanner]], [[ArenaBases]], [[ArenaRound]], [[ArenaRunDirector]], [[MoriMochiAgent]], [[MoriMonchiController]], [[AgentAbilities]]
