---
tags: [script, editor, humanos]
---

# HumanBodyAssembler.cs

**Ruta:** `Editor/HumanBodyAssembler.cs`

**Responsabilidad:** Herramienta de editor (menú `RunRunSimulator/Humans/Build Bodies`) que arma como assets los humanos del pack Sidekick (Synty): cuerpos NPC, cuerpo del jugador, brazos de primera persona, pieles y catálogo. No corre en runtime.

**Vinculado a:** [[Index/06 - Player & World]]

**Conexiones:** [[HumanBodyCatalogSO]] (lo escribe), [[HumanoidClipBaker]] (los controllers `HumanNpc`, `FPArms` y `PlayerBody` deben existir antes), [[PlayerAnimator]] (lo agrega al FPArms), [[NpcBody]] (consume los cuerpos del catálogo)

## Qué genera

| Salida | Ruta | Detalle |
|--------|------|---------|
| Cuerpos NPC | `Resources/Prefabs/Humans/Bodies/Human_Knight_01..05.prefab` | 5 recetas (`Recipes`) de cabeza, nariz, pelo, barba y atuendo Knight. Animator `HumanNpc`. |
| Pieles | `Resources/Materials/Humans/M_Human_Sk01..06.mat` y `Resources/Textures/Humans/T_Human_Sk*.png` | 6 presets de piel de Sidekick ("Human - Light Tan" a "Human - Dark Brown") con los colores de "Fantasy Knights NN" encima. Plantilla `SC_Burlap`, sin contorno. |
| Cuerpo del jugador | `Resources/Prefabs/Humans/PlayerBody.prefab` | Cabeza, orejas, nariz, pelo, torso y brazos desnudos más piernas civiles. SMR principal con sombra solo `ShadowsOnly`. Animator `PlayerBody` (controller propio), `AlwaysAnimate`. **S158:** suma el SMR hijo `BodyView` (ver Cambios S158). |
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

- **Orden:** correr primero `RunRunSimulator/Humans/Bake Clips` (`HumanoidClipBaker`). Si el controller no existe, el Animator de los prefabs queda sin controller, sin error. Eso incluye `PlayerBody.controller`.
- **Dependencia del pack:** el paquete Synty es gitignored; cada PC lo importa. `Resources.Load("Meshes/SK_BaseModel")` debe existir o `SidekickRuntime` falla.
- **Parte faltante:** `Combine` loguea `Parte no encontrada`, devuelve null y ese prefab se omite sin frenar al resto.
- **Re-correr** sobreescribe prefabs, materiales, texturas y meshes existentes. El catálogo se reconstruye entero desde cero.
- Los números de partes (`Recipes`, `KnightBody`, `BareArms`) son IDs fijos del catálogo Sidekick. Cambiar de pack cambia el resultado.
- El cuerpo civil del jugador usa `SK_SCFI_CIVL_09_` para piernas, mientras que los NPC usan el atuendo Knight.
- **Huesos por nombre (`BodyView`, S158):** `AttachSkin` busca cada hueso por `name` dentro de PlayerBody. Si no lo encuentra, loguea `Hueso no encontrado` y deja el hueso original, que pertenece a la instancia temporal que se destruye después. Ese error deja el BodyView roto.

## Cambios S158

- `BuildPlayerBodyPrefab` arma además un personaje temporal `PlayerBodyView` (torso, brazos y piernas civiles, sin cabeza) con el mismo material. Lo adjunta a PlayerBody como hijo `BodyView` con `AttachSkin`: remapea los huesos por nombre, fija la raíz, no emite sombra, recibe sombras y se actualiza fuera de cámara. Después destruye la instancia temporal.
- El SMR principal de PlayerBody sigue en `ShadowsOnly`: proyecta sombra; el `BodyView` es el que se ve.
- El Animator de PlayerBody pasa de `HumanNpc` a `PlayerBody.controller` (generado por [[HumanoidClipBaker]]).

## Conexiones de datos

Los prefabs de cuerpos quedan referenciados por `HumanBodyCatalogSO`. `FPArms` se asigna como hijo de la Main Camera en escena (ver [[PlayerController]]) y `PlayerBody` va bajo `Player/ModelHolder`.
