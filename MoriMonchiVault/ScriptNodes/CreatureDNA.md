---
tags: [data, genetics, serializable]
---

# CreatureDNA

**Ruta:** `Data/Genetics/CreatureDNA.cs`

**Responsabilidad:** Dato serializable que representa genética y estado de un MoriMochi. Contiene: partes genéticas (BodyShapeID/HornID/BackID/WingID/FaceID con tiers), colores (BaseColor/SecondaryColor), pelaje (FurType 33 patrones, IsShiny), identidad (CustomName, Timestamp, BirthDate, UniqueID), parentesco (MotherID/FatherID/ChildrenIDs), demografía (Gender), rol/elemento (Role, Element), personalidad (Sociability, Boldness), potenciales de partes, necesidades (Needs), estado (BusyReason, IsDead, BreedCount, SaleDate), reproducción (BreedReadyAt, BreedPartnerID), ubicación (LocationKey, LocationSlot), BirthDay (S131: día del juego de nacimiento), forma y exploración (S137: Form, Explorations).

## Campos Principales

| Campo | Tipo | Propósito |
|-------|------|----------|
| `BodyShapeID` / `HornID` / `BackID` / `WingID` / `FaceID` | string | IDs de partes (keys a PartDatabaseSO) |
| `BaseColor` / `SecondaryColor` | Color | Colores (derivados genéticamente) |
| `FurType` | FurType | Patrón de pelaje (Pattern00-32) |
| `IsShiny` | bool | Variante shiny (0.5% rareza) |
| `CustomName` | string | Nombre asignado jugador |
| `Timestamp` | long | Ticks UTC (identidad inmutable) |
| `BirthDate` | DateTime | Nacimiento real (DateTime.UtcNow al Stamp) |
| `BirthDay` | int | **(S131)** Día del juego de nacimiento (GameClock.Instance.Day) |
| `MotherID` / `FatherID` / `ChildrenIDs` | string / List | Genealogía |
| `Gender` | CreatureGender | Unknown/Male/Female |
| `Role` | Role | Protector/Agresivo/Empático |
| `Element` | Element | Agua/Fuego/Electricidad/Planta |
| `Sociability` / `Boldness` | float | Diales (0-1) |
| `BreedCount` | int | Cantidad reproducida |
| `Generation` | int | Generación (HC tracking) |
| `{Body/Horn/Back/Wing}Tier` | Tier | Rareza (Tier1/2/3) |
| `{Horn/Back/Wing}Potential` | int | Techo de nivel de parte (1-10, evolución HC) |
| `IsDead` | bool | Muerte permanente |
| `Form` | MonchiForm | **(S137)** Etapa de vida (Egg/Slime/Adult) — determina visual |
| `Explorations` | int | **(S137)** Contador de exploraciones (slime → adult cuando ≥ threshold) |
| `Needs` | NeedsState | Health/Energy/Affect |
| `BusyReason` | BusyReason | None/Breeding/Sold |
| `SaleDate` | DateTime | Cuándo vendida |
| `BreedReadyAt` / `BreedPartnerID` | long / string | Reproducción (reloj game, partner ID) |
| `LocationKey` / `LocationSlot` | string / int | Ubicación mundo |

## Métodos & Propiedades

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Stamp()` | `void` | Asigna Timestamp (UTC ticks) + BirthDate = DateTime.UtcNow |
| `ToStringID()` | `string` | `"BODYSHAPE-HORN-BACK-WING-FACE-RRGGBB"` (genetic string) |
| `FromID(string id)` [static] | `CreatureDNA` | Parsea genetic string → new DNA |
| `UniqueID` [property] | `string` | `"{ToStringID()}-{Timestamp}"` (identidad única inmutable) |
| `AgeDays(int today)` | `int` | `Max(0, today - BirthDay)` días desde nacimiento (game days) |
| `GetDisplayName(db)` | `string` | "BodyShape Horn Back Wing" (nombres de partes) |
| `IsBusy` / `IsSold` [property] | `bool` | Derived: `BusyReason != None` / `== Sold` |

## Ciclo de Vida (S137)

### Form

**Enum MonchiForm:** `Egg`, `Slime`, `Adult` (default)

- **Egg**: Recién puesto por breeding. No vivo, incubable. Visual: huevo con variantes de espalda.
- **Slime**: Eclosionado. Vivo, explorador. Visual: slime con cuernos. Acumula Explorations.
- **Adult**: Evoluciona cuando Explorations >= `CreatureAvailability.ExplorationSteps` (default 3). Reproducible. Visual: adulto completo.

### Explorations

**Contador:** Incrementado por `CreatureGrowth.RecordExploration()` cuando slime vuelve vivo de expedición.
- Slime con Explorations < threshold: no reproducible
- Slime con Explorations >= threshold: `CreatureGrowth.RecordExploration()` → Form=Adult, Explorations persiste
- Adult: puede reproducirse

### Transiciones

```
[Breed] → Lay() → Form=Egg, Explorations=0
  ↓
[Incubator] → Hatch() → Form=Slime, Explorations=0
  ↓
[Expedición 1] → RecordExploration() → Explorations++
  ↓
[Expedición 2] → RecordExploration() → Explorations++
  ↓
[Expedición 3] → RecordExploration() → Explorations=3, Form=Adult (si threshold=3)
```

## Contrato de Red

**ToStringID()** es lo único serializado a servidor (sin Timestamp, sin Form/Explorations). Invariantes:
- Ningún token contiene `-` (separador)
- BaseColor derivado de hex final (RRGGBB)
- Timestamp genera UniqueID única (evita colisiones)
- Form y Explorations son metadata local (no en genetic string)

## S137 Cambios: Form + Explorations

**Nuevos campos:**
- `Form: MonchiForm` (default Adult para backward compat) — etapa de vida visual
- `Explorations: int` (default 0) — contador de expediciones como slime

**Asignación:**
- `Lay()`: Form=Egg, Explorations=0 (breeding)
- `Hatch()`: Form=Slime, Explorations=0 (incubación)
- `RecordExploration()`: Explorations++, si ≥ threshold → Form=Adult (expedición)

**Persistencia:** Ambos campos se serializar en RegistryData, persisten con creature.

## S131 Cambios: BirthDay

**Nuevo campo:** `BirthDay: int` — día del juego de nacimiento (obtenido de `GameClock.Instance.Day`).

**Propósito:** 
- Seguimiento de edad en días de juego (no UTC)
- Usado por `CreatureLifeStageTableSO` para determinar etapa de vida (Newborn/Child/Teen/Adult/Elder)
- NameTag muestra edad: `AgeDays(GameClock.Instance.Day)` = `today - BirthDay`

**Asignación:**
```csharp
// En IncubationService.HatchLocally():
child.BirthDay = GameClock.Instance != null ? GameClock.Instance.Day : 1;

// En BreedingController.BreedCreatures():
child.BirthDay = GameClock.Instance != null ? GameClock.Instance.Day : 1;

// En GameManager.MintCreature():
dna.BirthDay = GameClock.Instance != null ? GameClock.Instance.Day : 1;
```

## Cambios S129

- **Eliminados:** Stats base (`BaseConstitution/Attack/Speed/Defense/Luck/Evasion`), campo `Equipped`
- **Agregado:** `int Generation` (tracking de generación, usado en `ReconcileColors()`)
- **Mantiene:** `{Horn/Back/Wing}Potential` como techo de evolución (HC-2)

## Cambios Históricos

**S75:** Genetic string refactorizado (5 partes + color).
**S93:** Enums a archivos dedicados.
**S95:** Potenciales de combate agregados.
**S128:** Cooldown y HeldItem borrados (RPS demolido).
**S129:** Stats y Equipped borrados (demolición HC-1).
**S131:** BirthDay agregado para seguimiento de edad en días de juego.
**S137:** Form + Explorations agregados para ciclo de vida (Egg→Slime→Adult).

## Vinculado a

- [[Index/01 - Creature Genetics & System]]
- [[Index/02 - Genetics & Breeding]]
- [[Index/09 - Active Context]] (S137: ciclo de vida)
- [[Index/28 - Cimientos y camino a Game Ready]]

## Conexiones

**Data:**
- [[CreatureRegistrySO]], [[CreatureGenerator]], [[NeedsState]], [[PartDatabaseSO]]

**Sistemas:**
- [[CreatureGrowth]] — modifica Form/Explorations (S137)
- [[BreedingService]], [[CreatureDisplay]], [[CreatureLifecycle]], [[CreatureAvailability]]
- [[NameTag]] — muestra edad via AgeDays
- [[GameClock]] — proporciona día actual
- [[CreatureLifeStageTableSO]] — mapea edad → etapa

**Visualización:**
- [[MonchiVisualizer]] — suscribe OnCreatureFormChanged, re-arma visual según Form (S137)
- [[MonchiEggBody]], [[MonchiSlimeBody]] — constructores de visuales por Form

## Notas (S137 HC-4 + Ciclo de Vida)

- **BirthDay vs BirthDate:** BirthDay es int (días de juego), BirthDate es DateTime (UTC real). BirthDay para gameplay, BirthDate para auditoría.
- **AgeDays:** Safe: `Max(0, today - BirthDay)` — nunca negativa.
- **Inicial:** Si no hay GameClock al minter, fallback a BirthDay=1.
- **Form default Adult:** backward compat con criaturas existentes que no tienen Form explícito
- **Explorations default 0:** safe, se incrementa solo en expediciones exitosas
- **Persistencia:** Form, Explorations, BirthDay se serializar en RegistryData, persisten con creature.
- **ToStringID immutable:** Form y Explorations NO forman parte del genetic string (no son heredables)
