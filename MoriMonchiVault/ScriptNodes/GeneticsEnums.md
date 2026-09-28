---
tags: [enum, genetics, core]
---

# GeneticsEnums.cs

**Ruta:** `Core/Enums/GeneticsEnums.cs`

**Responsabilidad:** Enumeraciones para el sistema genético y visual. Contiene: `Rarity` (5 niveles), `PartRole` (5 tipos de parte: Body/Horn/Back/Wing/Face), `FurType` (53 patrones de pelaje heredables), `Element` (4 elementos de combate), `Role` (3 personalidades de combate).

**S93:** Consolidación de enums genéticos en archivo dedicado.
**S135:** Verificado sin cambios relevantes (MonchiForm en CreatureEnums.cs).
**S136:** FurType aumenta de 33 a 53 patrones (Pattern33-Pattern52 añadidos).

## Enumeraciones

| Enum | Valores | Descripción |
|------|---------|-------------|
| `Rarity` | Common (0), Uncommon (1), Rare (2), Epic (3), Legendary (4) | Rareza de partes/criaturas; define drop rates y valor visual |
| `PartRole` | Body (0), Horn (1), Back (2), Wing (3), Face (4) | Tipos/slots de partes en un MoriMochi |
| `FurType` | Pattern00-Pattern52 (53 valores, 0-52) | **S136 MODIFICADO:** Patrones de pelaje heredables por genética (aumentado de 33 a 53) |
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

**S136 MODIFICADO:** 53 patrones (`Pattern00` a `Pattern52`):
- Heredable en `CreatureDNA.FurType`
- Determinista: DNA + seed → siempre mismo patrón visual
- Mapeo en `MonchiVisualizer.ApplyLook()` (shader _FurPattern param) y `EggLabAssembler.Build()`
- Aumento de 20 patrones adicionales (33→53) para diversidad visual mayor

**Antes (S135):** Pattern00-Pattern32 (33 valores)
**Ahora (S136):** Pattern00-Pattern52 (53 valores)

```csharp
public enum FurType
{
    Pattern00 = 0,   Pattern01 = 1,   Pattern02 = 2,   Pattern03 = 3,   Pattern04 = 4,
    Pattern05 = 5,   Pattern06 = 6,   Pattern07 = 7,   Pattern08 = 8,   Pattern09 = 9,
    Pattern10 = 10,  Pattern11 = 11,  Pattern12 = 12,  Pattern13 = 13,  Pattern14 = 14,
    Pattern15 = 15,  Pattern16 = 16,  Pattern17 = 17,  Pattern18 = 18,  Pattern19 = 19,
    Pattern20 = 20,  Pattern21 = 21,  Pattern22 = 22,  Pattern23 = 23,  Pattern24 = 24,
    Pattern25 = 25,  Pattern26 = 26,  Pattern27 = 27,  Pattern28 = 28,  Pattern29 = 29,
    Pattern30 = 30,  Pattern31 = 31,  Pattern32 = 32,
    // S136 NUEVO: 20 patrones adicionales
    Pattern33 = 33,  Pattern34 = 34,  Pattern35 = 35,  Pattern36 = 36,  Pattern37 = 37,
    Pattern38 = 38,  Pattern39 = 39,  Pattern40 = 40,  Pattern41 = 41,  Pattern42 = 42,
    Pattern43 = 43,  Pattern44 = 44,  Pattern45 = 45,  Pattern46 = 46,  Pattern47 = 47,
    Pattern48 = 48,  Pattern49 = 49,  Pattern50 = 50,  Pattern51 = 51,  Pattern52 = 52,
}
```

## Cambios S136

**FurType aumenta de 33 a 53 patrones:**
- Pattern33 a Pattern52 agregados (20 nuevos valores)
- Impacto: BreedingService.InheritFurType() puede retornar valores 33-52 (antes máximo era 32)
- Impacto: FurTypeDatabaseSO debe tener 53 materiales configurados (antes 33)
- Reutilizado en: MonchiVisualizer, EggLabAssembler (ambos usan FurTypeDatabaseSO.GetMaterial(furType))

**Contexto:**
- S136 introduce laboratorio de huevos (EggLab.unity)
- Más patrones = más diversidad visual sin requetir más modelos 3D
- Generación pseudoaleatoria determinista: `Random.Range(0, 53)` en BreedingService

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
- `FurType` — **S136:** heredable en breeding, determinista en visual, 53 patrones totales
- `Element` → afiliación elemental en combate futuro
- `Role` → selección de base de batalla en Arena (S118+)

## Cambios de Impacto S136

| Sistema | Cambio | Notas |
|---------|--------|-------|
| BreedingService | Random.Range(0, 53) en InheritFurType() | Antes 33, ahora 53 |
| FurTypeDatabaseSO | Debe tener 53 materiales | Antes 33 slots; need +20 nuevos |
| MonchiVisualizer.ApplyLook() | Misma lógica, más opciones | FurTypeDatabaseSO.GetMaterial() retorna para 0-52 |
| EggLabAssembler.Build() | Misma lógica, más opciones | Usa FurTypeDatabaseSO.GetMaterial(dna.FurType) |
| CreatureDNA.Inherit() | Herencia biparental, 50/50 | Sin cambios, retorna 0-52 (antes 0-32) |

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/20 - Combate]]
- [[Index/31 - EggLab & Incubadora]] — S136 NUEVO, usa FurType expandido

## Conexiones

[[CreatureDNA]], [[PartDatabaseSO]], [[BodyPart]], [[PartSetSO]], [[ColorGenetics]], [[ArenaMatrixDev]], [[MonchiVisualizer]], [[FurTypeDatabaseSO]], [[EggLabAssembler]]
