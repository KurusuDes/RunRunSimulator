---
tags: [script, visual, ui]
---

# MonchiMoodSetSO.cs

**Ruta:** `Data/MonchiMoodSetSO.cs`

**Responsabilidad:** Tabla de emociones-a-materiales de caras. Mapea cada `MonchiMood` (12 valores) a una lista de materiales de caras que pueden renderizar ese humor. `GetFace(mood)` selecciona aleatoriamente una cara de la lista del mood; cae back a Neutral si no hay lista encontrada. **S139:** Material devuelto tiene `mainTexture` que contiene la textura de cara; MonchiVisualizer.SetMood() extrae esta textura y la escribe en MPB (_MainTex/_PrevTex). `IsPop(mood)` indica si la transición debe ser pop (abrupta) o blink (suave). Botón editor `PopulateFromEnum` precarga entradas vacías para cada valor del enum MonchiMood sin perder datos existentes. Es un SO puro de configuración, editado en el inspector para cambiar qué caras rotan por humor sin tocar código.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `GetFace(MonchiMood mood)` | Retorna un Material aleatorio de la lista del mood (o Neutral si no existe). Material tiene mainTexture = textura de cara. |
| `IsPop(MonchiMood mood)` | **S139:** Retorna `true` si el mood está en la lista `popMoods` (transición pop/abrupta), `false` = blink/suave. |

## Botones Editor

- `PopulateFromEnum()` — Precarga entradas vacías para cada valor de MonchiMood sin borrar datos existentes.

## Campos Serializados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `faces` | `Dictionary<MonchiMood, List<Material>>` | Mapeo mood → lista de materiales de caras (rotación aleatoria) |
| `popMoods` | `List<MonchiMood>` | **S139:** Lista de moods que disparan transición pop (abrupta); resto son blink (suave) |

## Cambios S139

**IsPop() — NUEVO (línea 18):**
```csharp
public bool IsPop(MonchiMood mood) => popMoods != null && popMoods.Contains(mood);
```

- Retorna `true` si mood está en popMoods (transición abrupta), `false` = transición suave
- Usado por MonchiVisualizer.SetMood() para determinar _FaceMode del shader (0=blink, 1=pop)
- Moods típicamente pop: Happy, Excited, Angry, Shocked
- Moods típicamente blink: Neutral, Sad, Confused, Tired

**GetFace() — MODIFICADO (línea 20-29, sin cambio de firma):**
- Retorna `material.mainTexture` vía MonchiVisualizer.SetMood() (no el material completo en S139)
- Material devuelto es un asset editado en inspector (no instantiate)
- mainTexture se extrae y escribe en MPB (_MainTex) sin swapear material

## Invariantes

- Rotación es random pero determinista (UnityEngine.Random es seeded)
- Fallback a Neutral si mood no tiene lista; si Neutral tampoco existe → retorna null
- IsPop() es estable (bool, sin interpolación)
- popMoods es editable en inspector para tuning de transiciones por mood

## Notas S139

- Separación blink/pop permite feedback diferente por ánimo (Feel ShaderController reproduce feedback diferente)
- Material unit (bank.FaceMaterial) permite reutilización; lista de moods controla qué texturas rotan
- Set de ánimo por género manejado en MonchiVisualBankSO.MoodSetFor(gender) — hay un set por género (moodSet, moodSetFemale)

## Vinculado a

- [[Index/10 - Visualization]]

## Conexiones

- [[MonchiVisualBankSO]] (contenedor de sets por género)
- [[MonchiVisualizer]] (consumidor: SetMood() lee GetFace + IsPop)
- Enums: `MonchiMood` (12 valores)
