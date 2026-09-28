---
tags: [scriptable-object, genetics, data]
---

# PartSetSO.cs

**Ruta:** `Data/Parts/PartSetSO.cs`

**Responsabilidad:** ScriptableObject ligero que define un conjunto/colección de partes (identidad visual y temática). Dos campos: `Name` (string identificable) y `Color` (identificador visual para UI). Usado para agrupar y filtrar partes en genetica y bases de datos.

**S135:** Reemplaza hardcoding de nombres en `PartNameBank` — sets ahora son primarios, nombres se asignan random en botón editor.

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Name` | `string` | Nombre temático del set (ej: "Fuego", "Hielo") |
| `Color` | `Color` | Color de UI asociado para identificar visualmente el set |

## Uso

- Referenciado desde `BodyPart.Set` (PartSetSO)
- Filtro en `PartDatabaseSO.GetRandomPart(Rarity?, PartSetSO?)`
- Identificador visual en inspectores Odin (color de fondo de field)

## Lifecycle

Creado via: `Right-click > Create > RunRunSimulator/Parts/Part Set`

## Vinculado a

- [[Index/02 - Genetics & Breeding]]

## Conexiones

[[BodyPart]], [[PartDatabaseSO]], [[PartNameBank]] (reemplazado por esta estructura)
