---
tags: [script, ui, presenter]
---

# DetailInfoTabPresenter.cs

**Ruta:** `UI/DetailInfoTabPresenter.cs`

**Responsabilidad:** Presenter UITK para tab "Detalle" (muestra genética, necesidades, estado). Renderiza 5 filas de partes (BodyShape, Horn, Back, Wing, Face) con tier y potencial, 3 barras de necesidades (Health/Energy/Affect), badge de apta para exploración, y conteo de crianzas. **S129:** Eliminadas filas de stats operacionales. **S135:** Actualizado para partes modulares; BuildParts() invoca AddPartRow() y AddEvolvablePartRow() con acceso a BodyPart.Ability.

## Contenido del Tab

| Elemento | Descripción |
|----------|-------------|
| 5 filas de partes | BodyShape, Horn, Back, Wing, Face con tier/potencial |
| 3 barras de necesidades | Health/Energy/Affect con relleno + color |
| Badge apta | ✓ si CreatureAvailability.CanExplore(dna, careGate) |
| BreedCount | Contador de crianzas previas |

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `Rebuild(CreatureDNA dna)` | Punto de entrada: actualiza tab completo |
| `BuildParts(CreatureDNA dna)` | Itera slots y crea filas vía AddPartRow/AddEvolvablePartRow |
| `AddPartRow(PartRole slot, BodyPart part)` | Crea fila simple (BodyShape, Face) |
| `AddEvolvablePartRow(PartRole slot, BodyPart part, Tier tier, float potential)` | Crea fila con tier/potencial (Horn, Back, Wing) |
| `SetNeedBar(VisualElement fill, NeedType need, float value)` | Actualiza barra de necesidad |
| `SetNeedHighlight(VisualElement row, bool highlight)` | Resalta fila si necesidad crítica |
| `BuildPartSwatch(BodyPart part)` | [Privado] Crea icono+sprite de parte |

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `database` | `CreatureDatabaseSO` | Acceso a PartDatabases (Horn, Back, Wing, Face, Body) |
| `careGate` | `CareGateSO` | Verificación de disponibilidad para exploración |
| `partsContainer` | `VisualElement` | Contenedor dinámico de filas de partes |
| `needHealthFill` / `needEnergyFill` / `needAffectFill` | `VisualElement` | Barras de relleno |
| `exploreStatus` | `Label` | Badge "Apta" o "Bloqueada" |
| `roleElementLabel` | `Label` | Rol + Elemento genético |
| `progressionLabel` | `Label` | Contador BreedCount |

## Cambios S135

**BuildParts() actualizado:**
- Ahora llama `database.GetHorn(dna.HornID)` → retorna BodyPart modular (S135)
- AddEvolvablePartRow() recibe BodyPart con `part.Ability` asignada
- Renderiza habilidad junto a parte (icono/nombre)

**Acceso a Ability:**
```csharp
AddEvolvablePartRow(PartRole.Horn, database.GetHorn(dna.HornID), dna.HornTier, dna.HornPotential);
// BodyPart.Ability ahora visible en UI si asignada en inspector (S135)
```

## Integración

- Referenciado en `MorimonchiDetailInfoUITK` (instancia presenter)
- Constructor inyecta `database`, `careGate`, y referencias UI
- `Rebuild()` llamado desde panel al seleccionar criatura
- NeedsDisplay determina colores (good/warn/crit)
- CreatureAvailability verifica CareGateSO para apta

## Vinculado a

- [[Index/05 - UI System]]
- [[Index/28 - Cimientos y camino a Game Ready]]

## Conexiones

[[BodyPart]], [[CreatureDatabaseSO]], [[CreatureDNA]], [[NeedsDisplay]], [[CreatureAvailability]], [[CareGateSO]], [[MorimonchiDetailInfoUITK]]
