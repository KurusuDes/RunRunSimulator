---
tags: [script, editor-tool, tooling]
---

# MonchiPartRegistrar.cs

**Ruta:** `Editor/MonchiPartRegistrar.cs`

**Responsabilidad:** Herramienta editor (MenuItem) que registra partes modulares en la MonchiVisualBank. Detecta prefabs de partes por slot (Horn/Back/Wing vía SkinnedMeshRenderer), crea/recupera assets BodyPart, asigna IDs automáticos en databases correspondientes, detecta y registra modelos Egg/Slime/iconos, configura importers de sprites pixel-art.

## Flujo Principal

Menu Item: `RunRunSimulator/Parts/Registrar partes modulares` → `RegisterAll()`

1. Carga prefabs de `Assets/RunRunSimulator/Resources/Prefabs/MoriMochi/Parts` con patrón `MonchiPart_*`
2. Detecta slot predominante (Horn/Back/Wing) por nombres SkinnedMeshRenderer
3. Para cada parte:
   - Busca o crea asset BodyPart en `ScriptableObjects/Parts/{Slot}s/`
   - Registra en database correspondiente (HornDatabaseSO, BackDatabaseSO, WingDatabaseSO)
   - Detecta y registra variantes: EggPart_, BlobimPart_, PartIcon_
   - Aplica config TextureImporter (pixel-art: Sprite Single, Point filter, Uncompressed, no mipmaps)
4. Resumen debug: total/nuevas partes, conteos de huevo/slime/icono

## Métodos Clave

| Método | Descripción |
|--------|-------------|
| `RegisterAll()` | Flujo principal: itera prefabs, registra en bank y databases |
| `DetectSlot(GameObject)` | Cuenta renderers por slot, retorna el predominante |
| `RegisterPart<TPart, TDatabase>()` | Genérico: busca/crea asset, registra en database, retorna ID |
| `EnsurePixelArtIcon(string path)` | Configura TextureImporter para iconos (filtro Point, sin compresión) |
| `ToReadableName(string)` | Convierte camelCase a espacios (ej: "Ariete" → "ariete") |

## Campos Privados (Constantes)

| Constante | Valor |
|-----------|-------|
| `PartsFolder` | `Assets/RunRunSimulator/Resources/Prefabs/MoriMochi/Parts` |
| `PartsPrefix` | `MonchiPart_` |
| `VisualBankPath` | `Assets/RunRunSimulator/ScriptableObjects/Visual/MonchiVisualBank.asset` |
| `EggFolder` | `Assets/RunRunSimulator/Resources/Models/MoriMochi/Parts/Egg` |
| `EggPrefix` | `EggPart_` |
| `BlobimFolder` | `Assets/RunRunSimulator/Resources/Models/MoriMochi/Parts/Blobim` |
| `BlobimPrefix` | `BlobimPart_` |
| `IconFolder` | `Assets/RunRunSimulator/Resources/Sprites/PartIcons` |
| `IconPrefix` | `PartIcon_` |

## Vinculado a

- [[Index/02 - Genetics & Breeding]] — pipe de registración de partes modulares

## Conexiones

[[MonchiVisualBankSO]], [[PartDatabaseSO]], [[HornDatabaseSO]], [[BackDatabaseSO]], [[WingDatabaseSO]], [[BodyPart]]
