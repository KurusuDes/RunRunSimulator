---
tags: [script, visual, component]
---

# MonchiVisualizer.cs

**Ruta:** `World/Creatures/MonchiVisualizer.cs`

**Responsabilidad:** Visualizador del modelo Suriyun. Instancia body FBX por BodyShapeID (adulto) o por Form (Egg/Slime usando builders estáticos). Mapea renderers (Face, Wings, Arms, etc.), aplica tintado por ColorGenetics.BuildHarmony. **S61:** `Assemble()` ahora hace `SetActive(false)` a los hijos viejos antes de `Object.Destroy()` — Destroy es diferido a fin de frame y el fotomatón renderiza en el mismo frame, causando superposición del cuerpo viejo en headshots batch. **S110:** Nuevos métodos `SetRimOverride()` y `ClearRimOverride()` para controlar rim light genético (anulable con color/power/mask de rival). **S115:** Assemble() propaga la capa del Root (`modelRoot.gameObject.layer`) a todos los hijos del body instanciado; esto permite la pasada de renderer URP (RenderObjects de `PC_Renderer` con tags CreatureBodyMask/CreatureBodySilhouette sobre capa `CreatureBody`) que filtra por esa capa para dibujo de silueta/stencil. **S134:** Modular part assembly — Assemble ahora carga partes prefabricadas (HornID, BackID, WingID) desde el banco, desactiva renderers baked de esos prefijos, e injerta partes FBX con su propio Armature usando MonchiPartGrafter. **S136:** ApplyLook() refactorizado — tintado centralizado via MonchiTint.ColorFor() (determinismo nombre renderer) + MonchiTint.Fill() (paleta MPB). **S137:** Assemble() ahora soporta Form.Egg y Form.Slime usando MonchiEggBody/MonchiSlimeBody builders estáticos; adicionalmente suscribe a GameEvents.OnCreatureFormChanged para re-armar cuando forma cambia (Egg→Slime→Adult). **S139:** SetMood() refactorizado — material único (bank.FaceMaterial, shader MoriMonchi/MonchiFace) con MPB write (_MainTex/_PrevTex/_FaceT/_FaceMode índice material 0); obtiene set de ánimo por género via bank.MoodSetFor(Gender); integra MonchiFaceTransition para feedback sincronizado (blink/pop). **S142:** `SetFlash(color, alpha)` agrega material de destello (`Resources/Materials/Brawl/BrawlFlash.mat`) al final de `sharedMaterials` de todos los renderers; `RemoveFlashLayer()` lo limpia. Sin `flashMaterial` asignado, inerte. Usado por `BrawlBody` para feedback de golpe (rojo cuando golpean Player, blanco cuando golpean rivales).

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `SetBank(MonchiVisualBankSO)` | Asigna banco visual |
| `SetFurDatabase(FurTypeDatabaseSO)` | Asigna database de pelajes |
| `Assemble(CreatureDNA dna)` | **S137 MODIFICADO:** Instancia body según Form (Egg/Slime usan builders, Adult usa prefab directo), grafia partes modulares (HornID/BackID/WingID) si adulto y existen en banco, mapea renderers, aplica look; desactiva hijos viejos antes de destruir; propaga capa Root a todos los hijos. **S142 MODIFICADO:** Llama `RemoveFlashLayer()` al inicio para limpiar destello previo. Flujo: RemoveFlash → SetActive(false)/Destroy hijos previos → PropagaCapa → GraftPart por slot (si adulto) → Recorre renderers activos → ApplyLook → SetMood |
| `RefreshLook(CreatureDNA dna)` | Retinta sin re-instanciar; llama Assemble si bodyInstance es null o Form cambió |
| `SetMood(MonchiMood)` | **S139 MODIFICADO:** Material único (bank.FaceMaterial) + MPB write (_MainTex/_PrevTex/_FaceT/_FaceMode idx 0); interpola _FaceT 0→1 vía shader; llama bank.MoodSetFor(gender) para obtener set correcto; sincroniza MonchiFaceTransition feedback (blink/pop) si está activo |
| `SetRimOverride(Color color, float power, float insideMask)` | **S110 NUEVO** anula rim light genético con color/power/mask de rival |
| `ClearRimOverride()` | **S110 NUEVO** restaura rim light genético |
| `SetFlash(Color color, float alpha)` | **S142 NUEVO** Agrega material de destello al final de sharedMaterials. Instancia flashMaterial si no existe; mapea todos los renderers del body. Si flashMaterial null, no-op |
| `RemoveFlashLayer()` | **S142 NUEVO** Desactiva/destruye flashInstance, limpia flashedRenderers. Llamado en Assemble() y OnDestroy() |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Animator` | `Animator` | Animator del body |
| `ModelRoot` | `Transform` | Raíz del modelo |

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `modelRoot` | `Transform` | Raíz del modelo (si null, usa transform) |
| `faceTransition` | `MonchiFaceTransition` | **S139 NUEVO** Coordinador de feedback blink/pop |
| `flashMaterial` | `Material` | **S142 NUEVO** Material de destello (BrawlFlash.mat, shader Sprites/Default). Inspector, serializado |
| `bank` | `MonchiVisualBankSO` | Visual bank |
| `furDatabase` | `FurTypeDatabaseSO` | Database de pelajes |
| `bodyInstance` | `GameObject` | Instancia del body prefab |
| `animator` | `Animator` | Animator del body |
| `faceRenderer` | `SkinnedMeshRenderer` | Renderer del rostro |
| `tintRenderers` | `List<Renderer>` | Renderers a teñir (alas, cuernos, espalda, etc.); **S134:** incluye renderers injertados de partes; **S142:** tipos cambió a Renderer (antes SkinnedMeshRenderer) para permitir otros tipos |
| `currentDna` | `CreatureDNA` | DNA vigente |
| `assembledForm` | `MonchiForm` | Forma del modelo instanciado (para detectar cambios en RefreshLook, S137) |
| `currentMood` | `MonchiMood` | Mood vigente |
| `currentFaceTexture` | `Texture` | **S139 NUEVO** Textura de cara actual (para detectar cambios) |
| `rimOverride` | `bool` | **S110 NUEVO** si se aplica override de rim |
| `rimOverrideColor` | `Color` | **S110 NUEVO** color override |
| `rimOverridePower` | `float` | **S110 NUEVO** power override |
| `rimOverrideInsideMask` | `float` | **S110 NUEVO** inside mask override |
| `flashInstance` | `Material` | **S142 NUEVO** Instancia de flashMaterial (destruida en OnDestroy) |
| `flashedRenderers` | `List<Renderer>` | **S142 NUEVO** Renderers con capa de destello |

## Método SetFlash() S142 (NUEVO)

```csharp
public void SetFlash(Color color, float alpha)
{
    if (flashMaterial == null || bodyInstance == null) return;
    
    if (flashInstance == null)
    {
        flashInstance = Object.Instantiate(flashMaterial);
    }
    
    var mpb = new MaterialPropertyBlock();
    mpb.SetColor("_Color", new Color(color.r, color.g, color.b, alpha));
    
    // Recorre todos los renderers del body
    var allRenderers = bodyInstance.GetComponentsInChildren<Renderer>(false);
    flashedRenderers.Clear();
    foreach (var renderer in allRenderers)
    {
        if (renderer == null) continue;
        
        // Agrega flashMaterial al final de sharedMaterials
        var mats = new List<Material>(renderer.sharedMaterials);
        mats.Add(flashInstance);
        renderer.sharedMaterials = mats.ToArray();
        renderer.SetPropertyBlock(mpb);
        
        flashedRenderers.Add(renderer);
    }
}
```

**Responsabilidad:**
- Valida flashMaterial exists
- Instancia flashMaterial una sola vez (almacena en flashInstance)
- Itera sobre todos los Renderers del body
- Agrega flashInstance al final de sharedMaterials[] (no reemplaza)
- Escribe color + alpha en MPB
- Registra renderers tocados en flashedRenderers para limpieza luego

**Efecto visual:**
- Capa adicional de destello sobre todos los renderers (blanco, rojo, verde según parámetro)
- Falloff en 0,2 s vía shader (tweens alpha en el shader, no en C#)
- Sin flashMaterial = no-op (inerte, la tienda no lo usa)

## Método RemoveFlashLayer() S142 (NUEVO)

```csharp
private void RemoveFlashLayer()
{
    if (flashedRenderers.Count == 0) return;
    
    foreach (var renderer in flashedRenderers)
    {
        if (renderer == null) continue;
        
        var mats = new List<Material>(renderer.sharedMaterials);
        if (mats.Contains(flashInstance))
        {
            mats.Remove(flashInstance);
            renderer.sharedMaterials = mats.ToArray();
        }
    }
    
    flashedRenderers.Clear();
}
```

**Responsabilidad:**
- Recorre flashedRenderers
- Remueve flashInstance de sharedMaterials[]
- Limpia lista para próximo Assemble()
- Llamado en Assemble() (inicio) y OnDestroy()

## Cambios S142

**Assemble() línea 64 (NUEVO):**
```csharp
public void Assemble(CreatureDNA dna)
{
    RemoveFlashLayer();  // S142: limpia destello previo
    
    for (int i = Root.childCount - 1; i >= 0; i--)
    {
        // ... resto del código
    }
}
```

**OnDestroy() línea 56-60 (NUEVO):**
```csharp
private void OnDestroy()
{
    if (flashInstance != null)
        Object.Destroy(flashInstance);
}
```

**Campos S142:**
- `flashMaterial` (Inspector, serialized, default null)
- `flashInstance` (privado, instancia de flashMaterial)
- `flashedRenderers` (privado, List<Renderer>)

## Invariantes

- Assemble() desactiva visualmente los hijos viejos inmediatamente (SetActive), luego los destruye diferido
- Fotomatón renderiza en el mismo frame; desactivar antes de Destroy evita ghosting
- Previene artefactos visuales en headshot batch (dos criaturas superpuestas)
- Override de rim es toggle (bool rimOverride) sin estado gradual — on/off nítido
- **S115:** Layer propagation es determinístico: todos los hijos heredan exactamente del Root
- **S134:** GraftPart solo actúa si partPrefab existe; partId nil o no en banco = body baked se mantiene
- **S136:** MonchiTint.ColorFor() es determinístico en nombre renderer; mismo nombre = mismo color
- **S137:** Form-aware assembly: Egg y Slime usan builders estáticos, Adult usa prefab. Cambios de Form disparan re-armado vía evento.
- **S139:** Material único + MPB: setea _MainTex/_PrevTex/_FaceT/_FaceMode en índice 0; fallback legacy si bank.FaceMaterial null. Gender-aware set: MoodSetFor(gender). Feedback sincronizado: animate solo si MonchiFaceTransition activo y cambio de textura.
- **S142:** flashMaterial es null por defecto (inerte). SetFlash() solo actúa si flashMaterial asignado. RemoveFlashLayer() limpia antes de cada Assemble(). flashInstance es singleton (instancia una sola vez, destruida en OnDestroy).

## Vinculado a

- [[Index/10 - Visualization]]
- [[Index/02 - Genetics & Breeding]] (S137: ciclo de vida)
- [[Index/23 - Arena Sandbox y Expedicion]]
- [[Index/31 - EggLab & Incubadora]] (S137: visual de huevos, S136 NUEVO: EggLabAssembler reutiliza MonchiTint)
- [[Index/32 - Demo Brawl 3v3 arcade]] (S142: SetFlash para feedback de golpe)
- [[MonchiVisualBankSO]], [[ColorGenetics]]
- [[MonchiTint]] (S136 NUEVO) utilidad de mapeo de colores
- [[MonchiTeamRim]] (S110 NUEVO) llamador de SetRimOverride/ClearRimOverride
- [[MonchiPartGrafter]] (S134 NUEVO) utilidad de injerto de partes
- [[MonchiEggBody]] (S137 NUEVO) builder de huevo
- [[MonchiSlimeBody]] (S137 NUEVO) builder de slime
- [[MonchiFaceTransition]] (S139 NUEVO) coordinador de feedback blink/pop
- [[BrawlBody]] (S142 NUEVO) llamador de SetFlash para feedback de golpe

## Conexiones

**Entrada:**
- Assemble/RefreshLook: CreatureDNA (incluyendo Form, S137)
- SetMood: MonchiMoodDriver (S139: ahora usa bank.MoodSetFor(gender))
- SetRimOverride/ClearRimOverride: MonchiTeamRim (S110)
- SetFlash: BrawlBody (S142, feedback de golpe)
- GameEvents.OnCreatureFormChanged: BreedingController/IncubationService (S137)

**Salida:**
- Modelo visual world-space con capa Root propagada a hijos (S115)
- Material Face único con MPB write (_MainTex/_PrevTex/_FaceT/_FaceMode, S139)
- MPB de rim light (genético u override)
- Partes injertadas integradas en tintRenderers (S134)
- Tintado determinístico via MonchiTint (S136)
- Form-aware visual: Egg/Slime/Adult (S137)
- Feedback blink/pop sincronizado vía MonchiFaceTransition (S139)
- Capa de destello en sharedMaterials si SetFlash() llamado (S142)
