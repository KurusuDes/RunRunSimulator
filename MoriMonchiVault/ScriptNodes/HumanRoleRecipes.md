---
tags: [script, editor, humanos]
---

# HumanRoleRecipes.cs

**Ruta:** `Editor/HumanRoleRecipes.cs`

**Responsabilidad:** Lee las recetas de roles de NPC desde `ScriptableObjects/NPC/HumanRoles.json` y ofrece utilidades de resolución de assets para el ensamblado de cuerpos: índice de partes FBX del pack Synty y ruta del ColorMap de cada receta. Contiene también la clase DTO `HumanRoleRecipe`. No corre en runtime.

**Vinculado a:** [[Index/06 - Player & World]], [[Index/04 - Customer System]]

**Conexiones:** [[HumanBodyAssembler]] (único consumidor: llama `Load`, `BuildPartIndex` y `ColorMapTexturePath`), [[HumanBodyCatalogSO]] (el arquetipo de cada rol termina ahí)

## Clase `HumanRoleRecipe` (DTO)

Deserializada con Newtonsoft (`[JsonProperty]`):

| Campo | JSON | Descripción |
|-------|------|-------------|
| `Name` | `name` | Nombre del rol; base de nombres de prefab, material y mesh |
| `ColorMap` | `colorMap` | Ruta relativa del personaje Synty (`Characters/<colorMap>/Textures/T_<último>ColorMap.png`) |
| `Archetype` | `archetype` | `DisplayName` del `CustomerArchetypeSO`. Vacío = vecino (no entra al catálogo) |
| `Species` | `species` | `Elf` = una sola variante sin preset de piel; otro valor = 4 pieles humanas |
| `BodyType` | `bodyType` | > 0 usa el controller femenino (`HumanNpcSK_Femn`) |
| `BodySize` | `bodySize` | Negativo = delgado, positivo = pesado (se separa en blend shapes) |
| `Muscle` | `muscle` | Blend de músculo |
| `Parts` | `parts` | IDs de FBX de Sidekick que componen el cuerpo |

## Métodos

- **`Load()`**: lee `JsonPath`. Si el archivo no existe, loguea error y devuelve lista vacía.
- **`BuildPartIndex()`**: indexa por nombre de archivo todos los `Model` bajo `Assets/Synty/SidekickCharacters/Resources/Meshes`. Si hay nombres repetidos, gana el primero.
- **`ColorMapTexturePath(colorMap)`**: arma la ruta del PNG del ColorMap a partir del último segmento de la ruta del personaje.

## Constantes

- `JsonPath` = `Assets/RunRunSimulator/ScriptableObjects/NPC/HumanRoles.json`
- `SynRoot` = `Assets/Synty/SidekickCharacters/Resources/Meshes`
- `CharactersRoot` = `Assets/Synty/SidekickCharacters/Characters`

## Quirks ⚠️

- **Ruta del JSON:** `Load` usa `File.Exists` con ruta relativa al proyecto Unity; si se mueve el JSON, hay que cambiar `JsonPath`.
- **Paquete Synty:** `BuildPartIndex` y `ColorMapTexturePath` dependen del pack gitignored; sin él, el índice queda vacío y los roles fallan por parte faltante.
- **Nombres de parte:** los IDs del JSON son nombres de archivo de Sidekick, no rutas. Dos FBX con el mismo nombre en distintas carpetas se resuelven al primero.
- **Sin validación de campos:** un rol con `species` o `archetype` mal escritos no falla al cargar; el error aparece después en el ensamblado.
