---
tags: [scriptable-object, visual-data, genetics]
---

# MonchiVisualBankSO.cs

**Ruta:** `Data/Databases/MonchiVisualBankSO.cs`

**Responsabilidad:** Banco visual centralizado: body FBX, partes modulares (Adult/Egg/Slime), modelos base, AnimatorControllers, material de cara único (S139), sets de ánimo por género (S139). **S138:** Agregado `eggScale` (default 3.4 en asset). **S139:** Agregados FaceMaterial (shader MoriMonchi/MonchiFace) y MoodSetFemale; nuevo método MoodSetFor(gender) para obtener set correcto según género.

## Campos Públicos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `bodies` | `List<GameObject>` | Body prefabs adultos (rotación aleatoria por BodyShapeID) |
| `bodyOverrides` | `Dictionary<string, GameObject>` | Body overrides por BodyShapeID |
| `partMeshes` | `Dictionary<string, GameObject>` | Partes modulares adultas (Horn/Back/Wing prefabs FBX) |
| `eggPartMeshes` | `Dictionary<string, GameObject>` | Partes modulares huevo (S137) |
| `slimePartMeshes` | `Dictionary<string, GameObject>` | Partes modulares slime (S137) |
| `animatorController` | `RuntimeAnimatorController` | Animator adulto |
| `gemMaterials` | `List<Material>` | Materiales gema shiny |
| `moodSet` | `MonchiMoodSetSO` | Set de ánimos default (macho/neutral) |
| `moodSetFemale` | `MonchiMoodSetSO` | **S139 NUEVO** Set de ánimos hembra (si existe, MoodSetFor(Female) lo retorna) |
| `faceMaterial` | `Material` | **S139 NUEVO** Material único shader MoriMonchi/MonchiFace (anima transiciones de cara) |
| `slimeModel` | `GameObject` | Slime model base (S137) |
| `slimeAnimatorController` | `RuntimeAnimatorController` | Animator slime (S137) |
| `slimeScale` | `float` | Escala slime (default 3.4) |
| `eggModel` | `GameObject` | Egg model base (S137) |
| `eggAnimatorController` | `RuntimeAnimatorController` | Animator huevo (S137) |
| `eggScale` | `float` | Escala huevo (default 3.4, S138) |
| `eggHeight` | `float` | Alto huevo (default 1.15) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `AnimatorController` | `RuntimeAnimatorController` | Animator adulto |
| `MoodSet` | `MonchiMoodSetSO` | Set default (macho/neutral) |
| `FaceMaterial` | `Material` | **S139 NUEVO** Material único cara (shader-driven) |
| `MoodSetFor(gender)` | `MonchiMoodSetSO` | **S139 NUEVO** Retorna moodSetFemale si gender==Female y moodSetFemale!=null, sino moodSet |
| `SlimeModel` | `GameObject` | Slime model base |
| `SlimeAnimatorController` | `RuntimeAnimatorController` | Animator slime |
| `SlimeScale` | `float` | Escala slime |
| `EggModel` | `GameObject` | Egg model base |
| `EggAnimatorController` | `RuntimeAnimatorController` | Animator huevo |
| `EggScale` | `float` | Escala huevo (S138) |
| `EggHeight` | `float` | Alto huevo |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `GetBody(bodyShapeId)` | Retorna body adulto: override si existe, sino rotación aleatoria de lista bodies por hash estable |
| `GetPartMesh(partId, form)` | Retorna parte FBX modulada por Form (Adult/Egg/Slime) |
| `GetGem(uniqueId)` | Retorna material gema shiny por hash estable de ID único |
| `SetPartMesh(partId, prefab, form)` | Editor: registra parte en diccionario |

## Cambios S138

**Nuevo campo:**
```csharp
[SerializeField] private float eggScale = 3.4f;
public float EggScale => eggScale;
```

**Propósito:** MonchiEggBody.Build() escala huevo con `eggScale` en X/Z y `eggScale * eggHeight` en Y. Asset 2.6 utiliza 3.4.

## Cambios S139

**Nuevos campos:**
```csharp
[SerializeField] private MonchiMoodSetSO moodSetFemale;
[SerializeField] private Material faceMaterial;
```

**Nuevo método:**
```csharp
public MonchiMoodSetSO MoodSetFor(CreatureGender gender) 
    => gender == CreatureGender.Female && moodSetFemale != null ? moodSetFemale : moodSet;
```

**Responsabilidad S139:**
- `FaceMaterial` es material único shader `MoriMonchi/MonchiFace` (no swapea por mood)
- `moodSetFemale` permite sets de ánimo diferentes por género (hembra vs macho)
- `MoodSetFor(gender)` centraliza lógica de selección de set (fallback a moodSet si moodSetFemale no existe)

**Impacto S139:**
- MonchiVisualizer.SetMood() llama `bank.MoodSetFor(currentDna.Gender)` en lugar de `bank.MoodSet`
- Material único reduce overhead de instantiation por mood
- MPB write (_MainTex/_PrevTex/_FaceT/_FaceMode) permite shader-driven transiciones blink/pop

## Escalas y Modelos por Forma

| Forma | Campos | Propiedades | Uso |
|-------|--------|-------------|-----|
| Adult | animatorController, faceMaterial (S139) | AnimatorController, FaceMaterial | Adulto Suriyun, cara shader-driven |
| Egg | eggModel, eggAnimatorController, eggScale (S138), eggHeight | EggAnimatorController, EggScale, EggHeight | Huevo modular, escala configurable |
| Slime | slimeModel, slimeAnimatorController, slimeScale | SlimeAnimatorController, SlimeScale | Slime modular |
| Mood | moodSet, moodSetFemale (S139) | MoodSet, MoodSetFor(gender) | Caras por ánimo, diferenciadas por género |

## Métodos Internos

| Método | Descripción |
|--------|-------------|
| `GetPartMeshDictionary(form)` | Retorna diccionario correcto de partes por Form |
| `StableHash(string s)` | Hash FNV-1a determinístico para rotación reproducible |

## Invariantes

- `GetBody()` retorna nil si no hay bodies registrados (warning)
- `MoodSetFor()` fallback a moodSet si moodSetFemale no existe o gender != Female
- `GetGem()` nil si no hay gemMaterials (shiny sin gem = no render)
- Diccionarios de partes se crean si no existen (lazy init)
- StableHash() es determinístico: mismo string = mismo índice

## Notas S138

- EggScale configurable para ajustar tamaño visual de huevos sin afectar adultos
- MonchiEggBody.Build() usa `bank.EggScale` y `bank.EggHeight` para dimensionar

## Notas S139

- **Material único:** FaceMaterial es shader-driven, no swapea por mood
- **Gender-aware:** MoodSetFemale permite diferenciación visual por género (anis diferentes para macho/hembra)
- **MPB write:** SetMood() escribe _MainTex/_PrevTex/_FaceT/_FaceMode en índice 0 sin tocar sharedMaterial
- **Fallback:** Si FaceMaterial null, SetMood() swapea sharedMaterial (legacy)
- **Transiciones:** IsPop() de MonchiMoodSetSO determina tipo (0=blink suave, 1=pop abrupto)

## Vinculado a

- [[Index/10 - Visualization]]

## Conexiones

- [[MonchiVisualizer]] (SetBank, SetMood consume MoodSetFor + FaceMaterial)
- [[MonchiMoodSetSO]] (obtiene caras por mood, S139: por género via moodSetFemale)
- [[MonchiEggBody]] (consume EggScale, EggHeight, EggAnimatorController, S137)
- [[MonchiSlimeBody]] (consume SlimeScale, SlimeAnimatorController, S137)
