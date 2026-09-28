---
tags: [scriptable-object, genetics, data]
---

# BodyPart.cs

**Ruta:** `Data/Parts/BodyPart.cs`

**Responsabilidad:** Clase base abstracta de partes del cuerpo (Cuerno, Espalda, Ala, Cara). Propiedades visuales e identidad: `Icon`, `ID`, `Name`, `Rarity`, `Tier`. Referencia a `PartSetSO` para agrupar visualmente. Stats de combate: `HP`, `Attack`, `Speed`. Habilidad asociada: `AbilitySO Ability`. Métodos estáticos `RarityColor()` y propiedades de color por Set. Método abstracto `GetPartRole()` para diferenciar roles (Horn/Back/Wing/Face).

**S135:** Campo `Set` ahora es `PartSetSO` (antes string). Campo `Ability` agregado para combate.

## Campos Públicos Serializados

| Campo | Tipo | Inspector | Descripción |
|-------|------|-----------|-------------|
| `Icon` | `Sprite` | Preview 55px | Icono de parte |
| `ID` | `string` | [ReadOnly] | Identificador único (asignado por database) |
| `Name` | `string` | | Nombre legible |
| `Rarity` | `Rarity` | [GUIColor por rareza] | Common/Uncommon/Rare/Epic/Legendary |
| `Tier` | `Tier` | | Tier1/Tier2/Tier3 |
| `Set` | `PartSetSO` | [GUIColor por set.Color] | Conjunto temático de la parte (S135: ScriptableObject, antes string) |
| `HP` | `float` | [Range 0-10] | Bonificación de salud |
| `Attack` | `float` | [Range 0-10] | Bonificación de ataque |
| `Speed` | `float` | [Range 0-10] | Bonificación de velocidad |
| `Ability` | `AbilitySO` | [AssetsOnly] | Habilidad de combate asociada (S135) |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetPartRole()` | `PartRole` | Abstracto: retorna rol de la parte (Horn/Back/Wing/Face) |
| `RarityColor(Rarity)` | `Color` | Estático: color por rareza (blanco=Common, verde=Uncommon, azul=Rare, morado=Epic, dorado=Legendary) |

## Propiedades Privadas

| Propiedad | Retorna | Descripción |
|-----------|---------|-------------|
| `GetRarityColor()` | `Color` | GUIColor para inspector (delega a RarityColor) |
| `GetSetColor()` | `Color` | GUIColor para inspector (color del Set o gris si null) |

## Colores Rareza

| Rareza | Color RGB |
|--------|-----------|
| Common | (1, 1, 1) blanco |
| Uncommon | (0.5, 1, 0.5) verde pastel |
| Rare | (0.4, 0.65, 1) azul pastel |
| Epic | (0.85, 0.45, 1) morado pastel |
| Legendary | (1, 0.75, 0.2) dorado |

## Cambios S135

**Campo Set: string → PartSetSO**
- Antes: `Set` era `string` con nombre de set (hardcodeado)
- Ahora: `Set` es referencia `PartSetSO` (ScriptableObject con Name + Color)
- Impacto: visualmente, SetColor() ahora retorna `Set.Color` o gris; más flexible para tematización

**Campo Ability: NUEVO**
- Agregado `AbilitySO Ability` para vincular habilidad de combate
- Usado por: `AbilityDatabaseSO.Resolve()` (toma Ability de partes)
- Permite: habilidades únicas por parte modular

## Ciclo de Vida

1. Editor: crear ScriptableObject vía `Right-click > Create > RunRunSimulator/Parts/[TipoParte]`
2. Asignar Icon, Name, Rarity, Tier, Set (PartSetSO), Stats (HP/Attack/Speed), Ability
3. Arrastrar a PartDatabase buffer → PopulateFromBuffer → SyncAllIDs (auto-asigna ID)
4. Runtime: CreatureDNA.HornID/BackID/WingID → database.GetHorn/Back/Wing(id) → retorna BodyPart instancia

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/20 - Combate]]

## Conexiones

[[PartSetSO]], [[PartDatabaseSO]], [[AbilitySO]], [[HornPart]], [[BackPart]], [[WingPart]], [[FacePart]], [[CreatureGenerator]], [[MonchiPartRegistrar]]
