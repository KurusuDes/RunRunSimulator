---
tags: [scriptable-object, visual-data, genetics]
---

# MonchiVisualBankSO.cs

**Ruta:** `Data/Databases/MonchiVisualBankSO.cs`

**Responsabilidad:** Banco visual centralizado del modelo Suriyun. Mantiene listas/diccionarios de cuerpos, partes modulares (Adult/Egg/Slime), modelos base Egg/Slime, AnimatorControllers, materiales gemas, y MoodSet. `GetBody()` retorna body por BodyShapeID con hash determinístico. `GetPartMesh(partId, form)` retorna prefab FBX por Part ID y forma (Adult/Egg/Slime). Propiedades `SlimeModel`, `SlimeAnimatorController`, `SlimeScale`, `EggModel`, `EggAnimatorController`, `EggHeight` **(S137 NUEVO)** permiten builders estáticos MonchiSlimeBody/MonchiEggBody instanciar formas sin herencia de body adulto. Única fuente de verdad para instanciación visual multi-forma.

**S134:** Diccionario `partMeshes` para partes modulares adultas.
**S135:** Agregados diccionarios `eggPartMeshes` y `slimePartMeshes` + método editor `SetPartMesh()` multi-forma.
**S137:** Agregados campos `slimeModel`, `eggModel`, y sus respectivos AnimatorControllers + escales.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|----------|
| `bodies` | `List<GameObject>` | Pool de body FBX base (Suriyun); GetBody hace hash determinístico |
| `bodyOverrides` | `Dictionary<string, GameObject>` | Overrides explícitos por BodyShapeID; prioridad sobre bodies list |
| `partMeshes` | `Dictionary<string, GameObject>` | Part ID → prefab FBX adulto (S134) |
| `eggPartMeshes` | `Dictionary<string, GameObject>` | **S135 NUEVO** Part ID → prefab FBX forma Egg |
| `slimePartMeshes` | `Dictionary<string, GameObject>` | **S135 NUEVO** Part ID → prefab FBX forma Slime |
| `animatorController` | `RuntimeAnimatorController` | Controller compartido para Animator del body adulto |
| `slimeModel` | `GameObject` | **(S137 NUEVO)** Prefab base del slime (forma Slime) |
| `slimeAnimatorController` | `RuntimeAnimatorController` | **(S137 NUEVO)** Controller para slime animator |
| `slimeScale` | `float` | **(S137 NUEVO)** Escala del slime (default 3.4) |
| `eggModel` | `GameObject` | **(S137 NUEVO)** Prefab base del huevo (forma Egg) |
| `eggAnimatorController` | `RuntimeAnimatorController` | **(S137 NUEVO)** Controller para egg animator |
| `eggHeight` | `float` | **(S137 NUEVO)** Altura del huevo (scale Y, default 1.15) |
| `gemMaterials` | `List<Material>` | Pool de materiales brillantes; hash determinístico |
| `moodSet` | `MonchiMoodSetSO` | Referencia a MoodSet para swapeo de materiales Face |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|----------|
| `AnimatorController` | `RuntimeAnimatorController` | Getter del controller adulto |
| `SlimeModel` | `GameObject` | **(S137 NUEVO)** Getter del prefab slime |
| `SlimeAnimatorController` | `RuntimeAnimatorController` | **(S137 NUEVO)** Getter del controller slime |
| `SlimeScale` | `float` | **(S137 NUEVO)** Getter escala slime |
| `EggModel` | `GameObject` | **(S137 NUEVO)** Getter del prefab huevo |
| `EggAnimatorController` | `RuntimeAnimatorController` | **(S137 NUEVO)** Getter del controller egg |
| `EggHeight` | `float` | **(S137 NUEVO)** Getter altura huevo |
| `MoodSet` | `MonchiMoodSetSO` | Getter del mood set |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetBody(string bodyShapeId)` | `GameObject` | Body por BodyShapeID; override primero, sino hash sobre bodies list |
| `GetPartMesh(string partId, MonchiForm form=Adult)` | `GameObject` | Prefab FBX según forma (Adult/Egg/Slime, S137); null si partId vacío o no existe |
| `GetGem(string uniqueId)` | `Material` | Material gema por hash FNV-1a estable |
| `SetPartMesh(string partId, GameObject prefab, MonchiForm form=Adult)` | `void` | [Editor] Registra prefab en diccionario según forma (S135) |

## Métodos Privados

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetPartMeshDictionary(MonchiForm)` | `Dictionary<string, GameObject>` | Retorna diccionario según forma; lazy-init si null |
| `StableHash(string s)` | `int` | FNV-1a hash: seed 2166136261u, XOR+mult 16777619u, resultado positivo (& 0x7FFFFFFF) |

## Formas Soportadas (MonchiForm enum)

| Forma | Valor | Diccionario | Modelo | Descripción |
|-------|-------|-------------|--------|-------------|
| `Adult` | 0 | `partMeshes` | bodies | Partes adultas normales, cuerpo Suriyun |
| `Egg` | 1 | `eggPartMeshes` | eggModel (S137) | Huevo con partes modulares (espalda injertada) |
| `Slime` | 2 | `slimePartMeshes` | slimeModel (S137) | Slime con partes modulares (cuerno injertado) |

## Ciclo de Instanciación S137

**Form.Adult:**
- MonchiVisualizer.InstantiateBody() → `GetBody(dna.BodyShapeID)` instancia
- GraftPart(HornID) / GraftPart(BackID) / GraftPart(WingID) → GetPartMesh(id, Adult)
- Animator: `bank.AnimatorController`

**Form.Egg:** (S137 NUEVO)
- MonchiEggBody.Build() → instancia `EggModel`, escala altura `EggHeight`
- GraftPart(BackID) → GetPartMesh(id, Egg) inyecta espalda
- Animator: `bank.EggAnimatorController`

**Form.Slime:** (S137 NUEVO)
- MonchiSlimeBody.Build() → instancia `SlimeModel`, escala `SlimeScale`
- GraftPart(HornID) → GetPartMesh(id, Slime) inyecta cuerno
- Animator: `bank.SlimeAnimatorController`

## Cambios S137

**Nuevos campos y propiedades (línea 33-48):**

```csharp
[SerializeField] private GameObject slimeModel;
[SerializeField] private RuntimeAnimatorController slimeAnimatorController;
[SerializeField] private float slimeScale = 3.4f;

[SerializeField] private GameObject eggModel;
[SerializeField] private RuntimeAnimatorController eggAnimatorController;
[SerializeField] private float eggHeight = 1.15f;

public GameObject SlimeModel => slimeModel;
public RuntimeAnimatorController SlimeAnimatorController => slimeAnimatorController;
public float SlimeScale => slimeScale;
public GameObject EggModel => eggModel;
public RuntimeAnimatorController EggAnimatorController => eggAnimatorController;
public float EggHeight => eggHeight;
```

**Contexto:** MonchiSlimeBody.Build() y MonchiEggBody.Build() (builders estáticos nuevos en S137) obtienen modelos base del banco vía estas propiedades. Permite ciclo de vida Form-aware sin crear subclases complejas.

**Impacto:**
- Builders estaticosno necesitan inyección de dependencias
- Modelos descentralizados: huevo, slime, adulto pueden ser prefabs totalmente distintos
- Scales y AnimatorControllers específicos por forma
- Reutilizable por EggLabVisualizer (futuro) o MonchiTurntable si soporta formas

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
- `slimeModel` y `eggModel` requeridos para instanciación (pero tolerados null con warning)
- `partMeshes` / `eggPartMeshes` / `slimePartMeshes` vacío = formas no disponibles (graceful fallback)
- `GetPartMesh(null|"", any)` → null
- `GetPartMesh("H0", Egg)` busca en eggPartMeshes; si no existe → null (no falla)
- **S137:** Escalas y heights son multiplicadores puros (sin validación min/max) — seteadas por diseño

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/09 - Active Context]] (S137: ciclo de vida)
- [[Index/10 - Visualization]]
- [[Index/31 - EggLab & Incubadora]] (S137: modelos egg/slime)

## Conexiones

- [[MoriMonchiController]], [[MonchiPartRegistrar]]
- [[MonchiVisualizer]] (GetBody, GetPartMesh, AnimatorController)
- [[MonchiEggBody]] (S137 NUEVO: EggModel, EggAnimatorController, EggHeight)
- [[MonchiSlimeBody]] (S137 NUEVO: SlimeModel, SlimeAnimatorController, SlimeScale)
- [[BodyPart]], [[PartDatabaseSO]]
