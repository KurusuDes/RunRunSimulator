---
tags: [script, editor, humanos]
---

# HumanBodyAssembler.cs

**Ruta:** `Editor/HumanBodyAssembler.cs`

**Responsabilidad:** Herramienta de editor (menú `RunRunSimulator/Humans/Build Bodies`) que arma como assets los humanos del pack Sidekick (Synty): cuerpos NPC por rol, cuerpo del jugador, brazos de primera persona, pieles y catálogo. No corre en runtime. **S163:** los cuerpos NPC ya no son recetas Knight fijas; se arman por rol desde `ScriptableObjects/NPC/HumanRoles.json` (14 roles, incluye elfos) usando [[HumanRoleRecipes]].

**Vinculado a:** [[Index/06 - Player & World]], [[Index/04 - Customer System]]

**Conexiones:** [[HumanBodyCatalogSO]] (lo escribe), [[HumanRoleRecipes]] (lee el JSON de roles y el índice de partes), [[HumanNpcAnimatorBuilder]] (debe correr antes: genera el controller `HumanNpcSK`), [[HumanoidClipBaker]] (el controller `PlayerBody` y `FPArms` deben existir antes), [[PlayerAnimator]] (lo agrega al FPArms), [[NpcBody]] (consume los cuerpos del catálogo)

## Qué genera

| Salida | Ruta | Detalle |
|--------|------|---------|
| Cuerpos NPC | `Resources/Prefabs/Humans/Bodies/Human_<Rol>.prefab` | Uno por rol del JSON que tenga arquetipo o sea vecino. Animator `HumanNpcSK`; si `bodyType > 0` usa el override `HumanNpcSK_Femn`. |
| Texturas y materiales de rol | `Resources/Textures/Humans/T_Role_<Rol>_<i>.png`, `Resources/Materials/Humans/M_Role_<Rol>_<i>.mat` | Parte del ColorMap de la receta. Humanos: 4 pieles (Light Tan, Tan, Light Brown, Dark Brown). Elfos (`species = Elf`): 1 variante sin preset de piel. |
| Pieles del jugador | `Resources/Materials/Humans/M_Human_Sk01..06.mat` y `Resources/Textures/Humans/T_Human_Sk*.png` | 6 presets de piel de Sidekick con los colores de "Fantasy Knights NN" encima. Plantilla `SC_Burlap`, sin contorno. |
| Cuerpo del jugador | `Resources/Prefabs/Humans/PlayerBody.prefab` | Cabeza, orejas, nariz, pelo, torso y brazos desnudos más piernas civiles. SMR principal con sombra solo `ShadowsOnly`. Animator `PlayerBody` (controller propio), `AlwaysAnimate`. Suma el SMR hijo `BodyView` (ver Cambios S158). |
| Brazos FP | `Resources/Prefabs/Humans/FPArms.prefab` | Brazos desnudos sin sombra. Animator `FPArms`, `AlwaysAnimate`, con `PlayerAnimator`. |
| Catálogo | `Resources/Data/Humans/HumanBodyCatalog.asset` | Cada cuerpo de rol con arquetipo y sus variantes de piel. |
| Meshes | `Resources/Models/Humans/Mesh_<nombre>.asset` | Nombre `Mesh_<Rol>` para cuerpos de rol. Se sobreescriben con `CopySerialized` si ya existen. |

## Flujo de BuildBodies

1. Crea carpetas (`EnsureFolder`) y arma el índice de partes (`HumanRoleRecipes.BuildPartIndex`).
2. `BuildPresetMaterials`: copia el ColorMap de Starter y aplica por UV los presets de piel y los grupos Outfits, Attachments y Materials de "Fantasy Knights NN", leyendo la DB de Sidekick (`DatabaseManager`).
3. `HumanRoleRecipes.Load()` lee el JSON. Por cada rol: `BuildRoleMaterials` (textura y materiales) y `BuildRoleBody` (`Combine` + Animator + prefab).
4. Si el rol tiene `archetype`, lo busca por `DisplayName` en los `CustomerArchetypeSO` y lo suma al catálogo. Sin arquetipo = vecino: se construye el prefab pero no entra al catálogo. Arquetipo no encontrado = error y rol faltante.
5. `BuildArmsPrefab` y `BuildPlayerBodyPrefab`.
6. `Combine`: instancia cada FBX de `Assets/Synty/SidekickCharacters/Resources/Meshes` (por nombre de archivo), arma el personaje con `SidekickRuntime.CreateCharacter` y mueve el mesh a `Models/Humans`.
7. `UpdateCatalog`: reemplaza las entradas del catálogo.
8. Import forzado de Models y Prefabs, y log `Roles / Vecinos / Catalogo / Faltantes / FPArms`.

## Quirks ⚠️

- **Orden:** correr primero `RunRunSimulator/Humans/Build NPC Animator` (genera `HumanNpcSK` y su override) y `RunRunSimulator/Humans/Bake Clips` (genera `PlayerBody.controller`). Si el controller no existe, el Animator de los prefabs queda sin controller y solo se loguea `Controller no encontrado` una vez.
- **JSON faltante = catálogo vacío:** si `HumanRoles.json` no existe, `Load` devuelve lista vacía y `UpdateCatalog` igual reemplaza las entradas: el catálogo queda sin cuerpos sin frenar el proceso. Solo queda el error de `HumanRoleRecipes`.
- **Parte faltante:** `Combine` loguea `Parte no encontrada`, devuelve null y ese rol se omite (cuenta como faltante) sin frenar al resto.
- **Dependencia del pack:** el paquete Synty es gitignored; cada PC lo importa. `Resources.Load("Meshes/SK_BaseModel")` debe existir o `SidekickRuntime` falla.
- **Re-correr** sobreescribe prefabs, materiales, texturas y meshes existentes. El catálogo se reconstruye entero desde cero.
- **Elfos:** `species = Elf` no recibe preset de piel; su textura es el ColorMap tal cual.
- **Huesos por nombre (`BodyView`, S158):** `AttachSkin` busca cada hueso por `name` dentro de PlayerBody. Si no lo encuentra, loguea `Hueso no encontrado` y deja el hueso original, que pertenece a la instancia temporal que se destruye después. Ese error deja el BodyView roto.
- El cuerpo civil del jugador usa `SK_SCFI_CIVL_09_` para piernas.
- Cambiar de pack cambia el resultado: los números de partes del JSON son IDs del catálogo Sidekick.

## Cambios S163

- Los cuerpos NPC salen de `HumanRoles.json` (`HumanRoleRecipe`: nombre, ColorMap, arquetipo, especie, bodyType, bodySize, muscle, partes). Se reemplazaron las recetas Knight fijas.
- `BuildBodyPrefab` pasó a `BuildRoleBody`; el Animator de NPC pasó de `HumanNpc` (HumanoidClipBaker) a `HumanNpcSK` (HumanNpcAnimatorBuilder). `HumanNpc` queda solo para lo viejo.
- Forma por rol con `SetShape` (bodyType, bodySize, muscle) antes de combinar.

## Cambios S158

- `BuildPlayerBodyPrefab` arma además un personaje temporal `PlayerBodyView` (torso, brazos y piernas civiles, sin cabeza) con el mismo material. Lo adjunta a PlayerBody como hijo `BodyView` con `AttachSkin`: remapea los huesos por nombre, fija la raíz, no emite sombra, recibe sombras y se actualiza fuera de cámara. Después destruye la instancia temporal.
- El SMR principal de PlayerBody sigue en `ShadowsOnly`: proyecta sombra; el `BodyView` es el que se ve.
- El Animator de PlayerBody pasa de `HumanNpc` a `PlayerBody.controller` (generado por [[HumanoidClipBaker]]).

## Conexiones de datos

Los prefabs de cuerpos quedan referenciados por `HumanBodyCatalogSO`. `FPArms` se asigna como hijo de la Main Camera en escena (ver [[PlayerController]]) y `PlayerBody` va bajo `Player/ModelHolder`.
