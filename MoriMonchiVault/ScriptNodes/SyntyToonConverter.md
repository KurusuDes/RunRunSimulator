---
tags: [script, editor, art, synty, toon, materials]
---

# SyntyToonConverter.cs

**Ruta:** `Scripts/Editor/SyntyToonConverter.cs`

**Responsabilidad:** Herramienta de editor (estática, sin MonoBehaviour). Convierte los materiales Synty originales en materiales `_Toon` basados en el template `PolygonNature_Tree_01_Pal.mat`, copiando la textura base y el color del shader de origen. No corre en runtime.

## Menús

| Menú | Método | Qué hace |
|------|--------|----------|
| `RunRunSimulator/Art/Toonify Synty Selection` | `ToonifySelection` | Reemplaza en la selección los materiales Synty por sus `_Toon` (Undo + SaveAssets) |
| `RunRunSimulator/Art/Build Synty Toon Materials` | `BuildAll` | Crea en lote los `_Toon` de todas las carpetas Synty y loguea creados / ya existían / no convertibles |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `ToonFor(Material src)` | `Material` | Devuelve el `_Toon` existente o lo crea. `null` si el shader no es convertible o ya es `_Toon` |
| `ToonifyHierarchy(GameObject root)` | `int` | Reemplaza materiales de todos los Renderer hijos. Devuelve cantidad cambiada |

## Shaders soportados

| Shader de origen | Textura | Color |
|------------------|---------|-------|
| `Synty/Foliage` | `_Leaf_Texture` | `_Leaf_Base_Color` (follaje, alpha clip) |
| `Synty/Generic_Basic`, `Synty/Generic_Standard` | `_Albedo_Map` | `_BaseColor` |
| `Universal Render Pipeline/Lit` | `_BaseMap` | `_BaseColor` (alpha clip si `_AlphaClip > 0.5`) |

Otros shaders → `null` (no se tocan).

## Salida

- Carpeta: `Assets/RunRunSimulator/Resources/Materials/SyntyToon/`
- Nombre: `{original}_Toon.mat`
- Follaje: `_AlphaClip` 1, keyword `_ALPHACLIP_ON`, cutoff 0.5, cull off, viento (strength 0.06, speed 1.2, scale 0.35).
- Resto: sin alpha clip, cull back, sin viento.

## Conexiones

**Entrada:** menús del editor (selección o lote). Carpetas fuente: PolygonNatureBiomes, PolygonFantasyVillage, PolygonDungeonRealms, PolygonDungeon, PolygonFantasyKingdom, PolygonDog.

**Salida:** assets `.mat` en `Resources/Materials/SyntyToon/`. Ningún script de runtime la referencia.

## Invariantes

- Solo editor: vive en `Scripts/Editor/`, no entra al build.
- Idempotente: si el `_Toon` ya existe lo reutiliza.
- Un material cuyo nombre termina en `_Toon` nunca se reconvierte.
- Si falta el template, loguea error y devuelve `null`.
