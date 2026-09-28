---
tags: [script, genetics, deprecated]
---

# PartNameBank.cs

**Ruta:** `Data/Genetics/PartNameBank.cs` — ⚠️ ELIMINADO S135

**Estado:** BORRADO en S135. Los nombres de partes ahora son estáticos (campo `BodyPart.Name`), no procedurales por PartSet.

## Histórico

Antes de S135, `PartNameBank` mantenía un banco de palabras procedurales:
- `Dictionary<PartSet, Dictionary<PartRole, string[]>>`
- Mapeo: Set × Rol → array de palabras para generación de nombres random

**Cambios en S135:**

1. **Introducido `PartSetSO`:** Cada set es ahora ScriptableObject con `Name` + `Color`
2. **Nombres en BodyPart:** Campo `BodyPart.Name` asignado en inspector (o via editor button "RollAllNames()" que asigna random directo)
3. **Eliminada generación procedural:** No se invocan nombres procedurales por más

## Transición

- Antes: `PartNameBank.GetRandomName(set, role)` → string random
- Ahora: `BodyPart.Name` → string directo asignado en inspector

## Ficheros Afectados (Referencias Vivas)

Necesitan revisión para remover imports/referencias a `PartNameBank`:
- Buscar `using PartNameBank` o `PartNameBank.Get*`
- Remover todas las invocaciones

## Vinculado a

- [[Index/02 - Genetics & Breeding]]

**Conexiones Obsoletas:** ~~PartNameBank~~ → remplazado por [[PartSetSO]] + [[BodyPart]].Name
