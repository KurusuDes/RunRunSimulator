---
tags: [enum, genetics, core]
---

# GeneticsEnums.cs

**Ruta:** `Core/Enums/GeneticsEnums.cs`

**Responsabilidad:** Enumeraciones para el sistema genético y visual. Contiene: `Rarity` (5 niveles), `PartRole` (5 tipos de parte: Body/Horn/Back/Wing/Face), `FurType` (33 patrones de pelaje heredables), `Element` (4 elementos de combate), `Role` (3 personalidades de combate).

**S93:** Consolidación de enums genéticos en archivo dedicado.
**S135:** Verificado sin cambios relevantes (MonchiForm en CreatureEnums.cs).

## Enumeraciones

| Enum | Valores | Descripción |
|------|---------|-------------|
| `Rarity` | Common (0), Uncommon (1), Rare (2), Epic (3), Legendary (4) | Rareza de partes/criaturas; define drop rates y valor visual |
| `PartRole` | Body (0), Horn (1), Back (2), Wing (3), Face (4) | Tipos/slots de partes en un MoriMochi |
| `FurType` | Pattern00-Pattern32 (33 valores, 0-32) | Patrones de pelaje heredables por genética |
| `Element` | Agua (0), Fuego (1), Electricidad (2), Planta (3) | Tipo elemental para combate/afinidades |
| `Role` | Protector (0), Agresivo (1), Empatico (2) | Rol de combate (defensa/ataque/soporte); abre bases en Arena (S118) |

## Rarity

| Rareza | Valor | Color UI | Significado |
|--------|-------|----------|-------------|
| Common | 0 | Blanco | Drop más común |
| Uncommon | 1 | Verde pastel | Menos común |
| Rare | 2 | Azul pastel | Raro |
| Epic | 3 | Morado pastel | Muy raro |
| Legendary | 4 | Dorado | Máxima rareza |

Usado en `BodyPart`, `PartDatabaseSO.GetRandomPart(Rarity?)`, UI badges.

## PartRole

| Rol | Valor | Slot Corporal | Descripción |
|-----|-------|---------------|-------------|
| `Body` | 0 | Cuerpo | Forma base (BodyShape) |
| `Horn` | 1 | Cuerno | Parte modular Horn (Adult/Egg/Slime) |
| `Back` | 2 | Espalda | Parte modular Back (Adult/Egg/Slime) |
| `Wing` | 3 | Ala | Parte modular Wing (Adult/Egg/Slime) |
| `Face` | 4 | Cara | Parte modular Face (opcional) |

Usado en `BodyPart.GetPartRole()` (abstracto), databases por slot, genetica.

## FurType

33 patrones (`Pattern00` a `Pattern32`):
- Heredable en `CreatureDNA.FurType`
- Determinista: DNA + seed → siempre mismo patrón visual
- Mapeo en `MonchiVisualizer.ApplyLook()` (shader _FurPattern param)

## Element (Combate S118)

| Elemento | Valor | Descripción |
|----------|-------|-------------|
| Agua | 0 | Ofensiva; débil a Electricidad |
| Fuego | 1 | Defensa; débil a Agua |
| Electricidad | 2 | Velocidad; débil a Planta |
| Planta | 3 | Apoyo; débil a Fuego |

Asignado a `CreatureDNA.Element`, usado en combate y UI badges.

## Role (Combate S118)

| Rol | Valor | Descripción |
|-----|-------|-------------|
| Protector | 0 | Defensa: abre Base defensiva, -Ataque |
| Agresivo | 1 | Ataque: abre Base ofensiva, +Ataque |
| Empatico | 2 | Apoyo: abre Base neutral/apoyo, +Velocidad |

Asignado a `CreatureDNA.Role`, abre bases de combate en Arena (S118: `ArenaMatrixDev.BaseFor(role)`).

## Uso

- `Rarity` — filtrado en `PartDatabaseSO.GetRandomPart(Rarity?, ...)`
- `PartRole` — enrutamiento a database correcta (HornDatabaseSO, BackDatabaseSO, etc.)
- `FurType` — heredable en breeding, determinista en visual
- `Element` → afiliación elemental en combate futuro
- `Role` → selección de base de batalla en Arena (S118+)

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/20 - Combate]]

## Conexiones

[[CreatureDNA]], [[PartDatabaseSO]], [[BodyPart]], [[PartSetSO]], [[ColorGenetics]], [[ArenaMatrixDev]], [[MonchiVisualizer]]
