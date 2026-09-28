---
tags: [script, world, creature, data]
---

# EggLabEntry.cs

**Ruta:** `World/Creatures/EggLabEntry.cs`

**Responsabilidad:** Data class que encapsula la información de un huevo en laboratorio. **S136 NUEVO.** No hereda de MonoBehaviour; estructura pura de datos. Usado por EggLabBuilder para pasar información a UI/visualización.

## Campos Públicos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Number` | `int` | Número de huevo (1-based) para UI |
| `Egg` | `CreatureDNA` | Genética del huevo hijo |
| `Mother` | `CreatureDNA` | Genética de la madre (referencia) |
| `Father` | `CreatureDNA` | Genética del padre (referencia) |
| `Progress01` | `float` | Progreso de incubación (0-1); usado por RadialSlot |
| `HatchCost` | `int` | Costo en Minerita para eclosionar |
| `Root` | `Transform` | Raíz del GameObject del huevo en escena |

## Notas S136

- Data class sin métodos (propiedades directas públicas)
- Contiene referencias a CreatureDNA (no copia)
- Progress01 es simulado (Random.value en EggLabBuilder.Rebuild) para propósito demostrativo
- HatchCost se calcula vía `InheritanceOddsTableSO.HatchCost(mother, father)`
- Root permite picking 3D en mundo (raycast en EggLabBuilder.Update)

## Invariantes

- Todos los campos pueden ser null (validación es responsabilidad del caller)
- CreatureDNA es inmutable (no mutar contenido de Egg/Mother/Father)
- Number es identidad local en lista EggLabBuilder.Entries (no global)

## Vinculado a

- [[EggLabBuilder]] — crea instancias, las acumula en lista, dispara eventos con ellas
- [[EggLabPanel]] — recibe en OnSelected para actualizar UI
- [[EggLabPortrait]] — renderiza visual del Root

## Conexiones

**Productores:**
- EggLabBuilder.Rebuild() → crea Entries, rellena con datos genéticos

**Consumidores:**
- EggLabPanel.OnSelected(entry) → actualiza card UI con nombres/colores padres
- EggLabPortrait.Show(entry.Root) → renderiza portrait del huevo
- EggLabBuilder.Update() → raycast sobre Root.gameObject
