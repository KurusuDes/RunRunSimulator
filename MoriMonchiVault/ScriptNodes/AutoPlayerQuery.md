---
tags: [script, dev, autoplayer, query, utility]
---

# AutoPlayerQuery.cs

**Ruta:** `Systems/Dev/AutoPlayerQuery.cs`

**Responsabilidad:** Utilidad estática: búsqueda de muebles, controllers spawneados, criaturas por forma, ocupantes en contenedores, colocación en espiral, alcance NavMesh. Desacopla lógica de búsqueda del bot.

**S138:** Nuevo ; agrupa todas las queries reutilizables del AutoPlayer.

## Métodos Principales

### Búsqueda de Definiciones

- `FindFurnitureDefinition<TComponent>()` — Encuentra FurnitureDefinitionSO cuyo prefab tiene componente TComponent

### Controllers & Ocupantes

- `TryFindController(spawner, id, out controller)` — Busca MoriMonchiController por ID en spawner
- `AllControllersSpawned(ids)` — Verifica si todos los IDs tienen controller spawneado
- `CountOccupantsAmong(container, ids)` — Cuántos ocupantes del container están en la lista ids
- `DescribeForeignOccupants(container, ids)` — String debug de ocupantes ajenos

### Contas por Forma

- `CountFormNotIn(form, exclude)` — Cuenta criaturas con Form X que NO están en exclude
- `CountForm(form, ids)` — Cuenta cuántas de ids tienen forma dada

### Colocación & NavMesh

- `SpiralCells(center, maxRadius)` — Genera celdas en espiral desde un centro
- `TryPlaceInSpiral(service, def, cellFilter, center, maxRadius)` — Coloca mueble en espiral con filtro opcional
- `CustomerAreaMask()` — Bitmask NavMesh para zonas de cliente (ShopFrontDesk, Outside)
- `CellReachableByCustomers(grid, cell, footprint, mask)` — Valida celda alcanzable por NavMesh
- `IsReachableFromRegister(center, mask)` — Valida punto alcanzable desde caja registradora

### Equipos & Parejas

- `BuildTeam(registry, max, exclude)` — Arma equipo de hasta `max` criaturas (prioriza 1M + 1F, luego slimes)
- `TryFindAdultPair(registry, out mother, out father)` — Encuentra adultos criables (Form=Adult, no dead/sold)
- `PickSellable(registry, excludeIds, preferredId)` — Elige criatura vendible (Form != Egg, libre)

### Resúmenes

- `FormsSummary(registry)` — String debug: "huevos=X slimes=Y adultosM=Z adultasF=W"

## Vinculado a

- [[AutoPlayer]]
- [[AutoPlayerOpeningSteps]]
- [[AutoPlayerLoopSteps]]

**Conexiones:** [[MoriMochiSpawner]], [[CreatureRegistrySO]], [[FurnitureService]], [[PlacementGrid]], [[CreatureAvailability]], [[BreedingService]], [[CashRegister]]
