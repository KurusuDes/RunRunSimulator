---
tags: [scriptable-object, visual-data, genetics]
---

# MonchiVisualBankSO.cs

**Ruta:** `Data/Databases/MonchiVisualBankSO.cs`

**Responsabilidad:** Banco visual centralizado del modelo Suriyun. Mantiene listas/diccionarios de cuerpos, partes modulares (Adult/Egg/Slime), materiales gemas, AnimatorController compartido y MoodSet. `GetBody()` retorna body por BodyShapeID con hash determinístico. `GetPartMesh()` retorna prefab FBX por Part ID y forma (Adult/Egg/Slime). `GetGem()` retorna material gema por hash estable de ID. Única fuente de verdad para instanciación visual multi-forma.

**S134:** Diccionario `partMeshes` para partes modulares adultas.
**S135:** Agregados diccionarios `eggPartMeshes` y `slimePartMeshes` + método editor `SetPartMesh()` multi-forma.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `bodies` | `List<GameObject>` | Pool de body FBX base (Suriyun); GetBody hace hash determinístico |
| `bodyOverrides` | `Dictionary<string, GameObject>` | Overrides explícitos por BodyShapeID; prioridad sobre bodies list |
| `partMeshes` | `Dictionary<string, GameObject>` | Part ID → prefab FBX adulto (S134) |
| `eggPartMeshes` | `Dictionary<string, GameObject>` | **S135 NUEVO** Part ID → prefab FBX forma Egg |
| `slimePartMeshes` | `Dictionary<string, GameObject>` | **S135 NUEVO** Part ID → prefab FBX forma Slime |
| `animatorController` | `RuntimeAnimatorController` | Controller compartido para Animator del body |
| `gemMaterials` | `List<Material>` | Pool de materiales brillantes; hash determinístico |
| `moodSet` | `MonchiMoodSetSO` | Referencia a MoodSet para swapeo de materiales Face |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `AnimatorController` | `RuntimeAnimatorController` | Getter del controller |
| `MoodSet` | `MonchiMoodSetSO` | Getter del mood set |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetBody(string bodyShapeId)` | `GameObject` | Body por BodyShapeID; override primero, sino hash sobre bodies list |
| `GetPartMesh(string partId, MonchiForm form)` | `GameObject` | Prefab FBX según forma (Adult/Egg/Slime); null si partId vacío o no existe |
| `GetGem(string uniqueId)` | `Material` | Material gema por hash FNV-1a estable |
| `SetPartMesh(string partId, GameObject prefab, MonchiForm form)` | `void` | [Editor] Registra prefab en diccionario según forma |

## Métodos Privados

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetPartMeshDictionary(MonchiForm)` | `Dictionary<string, GameObject>` | Retorna diccionario según forma; lazy-init si null |
| `StableHash(string s)` | `int` | FNV-1a hash: seed 2166136261u, XOR+mult 16777619u, resultado positivo (& 0x7FFFFFFF) |

## Formas Soportadas (MonchiForm enum)

| Forma | Valor | Diccionario | Descripción |
|-------|-------|-------------|-------------|
| `Adult` | 0 | `partMeshes` | Partes adultas normales |
| `Egg` | 1 | `eggPartMeshes` | Formas de huevo (modulares S135) |
| `Slime` | 2 | `slimePartMeshes` | Formas de slime (variantes babosas S135) |

## Cambios S135

**Diccionarios Egg/Slime y GetPartMesh() multi-forma:**

- Agregados `eggPartMeshes` y `slimePartMeshes` (Odin Dictionary)
- `GetPartMeshDictionary(form)` retorna diccionario según forma; lazy-init si null
- `GetPartMesh(partId, form=Adult)` busca en diccionario correspondiente
- `SetPartMesh(partId, prefab, form=Adult)` registra prefab en diccionario editor-time

**Propósito:**
- Soportar formas de MoriMochi: adulto, huevo (tutorial), slime (alternativa visual)
- Prefabs distintos por forma pero mismo Part ID (ej. "H1" adulto vs "H1" egg → modelos distintos, genética igual)
- MonchiPartRegistrar.RegisterAll() invoca SetPartMesh para cada forma detectada

## Invariantes

- `bodies` siempre ≥ 1 elemento (fallback si override falta)
- `bodyOverrides` prioridad máxima
- `partMeshes` vacío = sin partes adultas modulares
- `eggPartMeshes` / `slimePartMeshes` vacío = formas no disponibles (graceful fallback)
- `GetPartMesh(null|"", any)` → null
- `GetPartMesh("H0", Egg)` busca en eggPartMeshes; si no existe → null (no falla)

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/10 - Visualization]]

## Conexiones

[[MoriMonchiController]], [[MonchiPartRegistrar]], [[MonchiVisualizer]], [[BodyPart]], [[PartDatabaseSO]]
