---
tags: [script, editor, modular, tooling, inspector]
---

# ModularBuildingEditor.cs

**Ruta:** `Editor/ModularBuildingEditor.cs`

**Responsabilidad:** Inspector custom (S165) de `ModularBuilding`, basado en `OdinEditor`. Dibuja el Inspector Odin normal y agrega dos botones, "Armar" y "Limpiar", que llaman a `ModularBuildingBuilder.Build` / `Clear` sobre todos los objetos seleccionados (multi-edicion). Cada accion se agrupa en un Undo colapsado con nombre propio. Solo tooling de editor.

## Comportamiento

- **Armar:** `Undo.SetCurrentGroupName("Armar edificio modular")`, recorre `targets` y ejecuta `ModularBuildingBuilder.Build`, luego `Undo.CollapseUndoOperations`.
- **Limpiar:** igual, con `ModularBuildingBuilder.Clear` y nombre "Limpiar edificio modular".

## Vinculado a

[[Index/09 - Active Context]] (Session 165)

## Conexiones

- [[ModularBuilding]] (`[CustomEditor(typeof(ModularBuilding))]`)
- [[ModularBuildingBuilder]] (ejecuta Build/Clear)
- Odin Inspector (`Sirenix.OdinInspector.Editor.OdinEditor` como base)
