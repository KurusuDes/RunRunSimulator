---
tags: [script, editor, humanos]
---

# HumanBodyAssembler.cs

**Ruta:** `Editor/HumanBodyAssembler.cs`

**Responsabilidad:** Herramienta de editor (menú `RunRunSimulator/Humans/Build Bodies`) que arma como assets los humanos del pack Sidekick (Synty): cuerpos NPC, cuerpo del jugador, brazos de primera persona, pieles y catálogo. No corre en runtime.

**Vinculado a:** [[Index/06 - Player & World]]

**Conexiones:** [[HumanBodyCatalogSO]] (lo escribe), [[HumanoidClipBaker]] (los controllers `HumanNpc` y `FPArms` deben existir antes), [[PlayerAnimator]] (lo agrega al FPArms), [[NpcBody]] (consume los cuerpos del catálogo)

## Qué genera

| Salida | Ruta | Detalle |
|--------|------|---------|
| Cuerpos NPC | `Resources/Prefabs/Humans/Bodies/Human_Knight_01..05.prefab` | 5 recetas (`Recipes`) de cabeza, nariz, pelo, barba y atuendo Knight. Animator `HumanNpc`. |
| Pieles | `Resources/Materials/Humans/M_Human_Sk01..06.mat` y `Resources/Textures/Humans/T_Human_Sk*.png` | 6 presets de piel de Sidekick ("Human - Light Tan" a "Human - Dark Brown") con los colores de "Fantasy Knights NN" encima. Plantilla `SC_Burlap`, sin contorno. |
| Cuerpo del jugador | `Resources/Prefabs/Humans/PlayerBody.prefab` | Cabeza, torso y brazos desnudos más piernas civiles. Sombra solo `ShadowsOnly`. Animator `HumanNpc`, `AlwaysAnimate`. |
| Brazos FP | `Resources/Prefabs/Humans/FPArms.prefab` | Brazos desnudos sin sombra. Animator `FPArms`, `AlwaysAnimate`, con `PlayerAnimator`. |
| Catálogo | `Resources/Data/Humans/HumanBodyCatalog.asset` | Cada cuerpo NPC con las 6 pieles. |
| Meshes | `Resources/Models/Humans/Mesh_<nombre>.asset` | Se sobreescriben con `CopySerialized` si ya existen. |

## Flujo de BuildBodies

1. Crea carpetas (`EnsureFolder`).
2. `BuildPresetMaterials`: copia el ColorMap de Starter y aplica por UV los presets de piel y los grupos Outfits, Attachments y Materials de "Fantasy Knights NN", leyendo la DB de Sidekick (`DatabaseManager`).
3. `BuildBodyPrefab` por receta, `BuildArmsPrefab` y `BuildPlayerBodyPrefab`.
4. `Combine`: instancia cada FBX de `Assets/Synty/SidekickCharacters/Resources/Meshes`, arma el personaje con `SidekickRuntime.CreateCharacter` y mueve el mesh a `Models/Humans`.
5. `UpdateCatalog`: reemplaza las entradas del catálogo (cuerpos × pieles).
6. Import forzado de Models y Prefabs, y log con el conteo.

## Quirks ⚠️

- **Orden:** correr primero `RunRunSimulator/Humans/Bake Clips` (`HumanoidClipBaker`). Si el controller no existe, el Animator de los prefabs queda sin controller, sin error.
- **Dependencia del pack:** el paquete Synty es gitignored; cada PC lo importa. `Resources.Load("Meshes/SK_BaseModel")` debe existir o `SidekickRuntime` falla.
- **Parte faltante:** `Combine` loguea `Parte no encontrada`, devuelve null y ese prefab se omite sin frenar al resto.
- **Re-correr** sobreescribe prefabs, materiales, texturas y meshes existentes. El catálogo se reconstruye entero desde cero.
- Los números de partes (`Recipes`, `KnightBody`, `BareArms`) son IDs fijos del catálogo Sidekick. Cambiar de pack cambia el resultado.
- El cuerpo civil del jugador usa `SK_SCFI_CIVL_09_` para piernas, mientras que los NPC usan el atuendo Knight.

## Conexiones de datos

Los prefabs de cuerpos quedan referenciados por `HumanBodyCatalogSO`. `FPArms` se asigna como hijo de la Main Camera en escena (ver [[PlayerController]]) y `PlayerBody` va bajo `Player/ModelHolder`.
