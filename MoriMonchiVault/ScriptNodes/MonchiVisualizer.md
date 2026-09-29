---
tags: [script, visual, component]
---

# MonchiVisualizer.cs

**Ruta:** `World/Creatures/MonchiVisualizer.cs`

**Responsabilidad:** Visualizador del modelo Suriyun. Instancia body FBX por BodyShapeID (adulto) o por Form (Egg/Slime usando builders estáticos). Mapea renderers (Face, Wings, Arms, etc.), aplica tintado por ColorGenetics.BuildHarmony. **S61:** `Assemble()` ahora hace `SetActive(false)` a los hijos viejos antes de `Object.Destroy()` — Destroy es diferido a fin de frame y el fotomatón renderiza en el mismo frame, causando superposición del cuerpo viejo en headshots batch. **S110:** Nuevos métodos `SetRimOverride()` y `ClearRimOverride()` para controlar rim light genético (anulable con color/power/mask de rival). **S115:** Assemble() propaga la capa del Root (`modelRoot.gameObject.layer`) a todos los hijos del body instanciado; esto permite la pasada de renderer URP (RenderObjects de `PC_Renderer` con tags CreatureBodyMask/CreatureBodySilhouette sobre capa `CreatureBody`) que filtra por esa capa para dibujo de silueta/stencil. **S134:** Modular part assembly — Assemble ahora carga partes prefabricadas (HornID, BackID, WingID) desde el banco, desactiva renderers baked de esos prefijos, e injerta partes FBX con su propio Armature usando MonchiPartGrafter. **S136:** ApplyLook() refactorizado — tintado centralizado via MonchiTint.ColorFor() (determinismo nombre renderer) + MonchiTint.Fill() (paleta MPB). **S137:** Assemble() ahora soporta Form.Egg y Form.Slime usando MonchiEggBody/MonchiSlimeBody builders estáticos; adicionalmente suscribe a GameEvents.OnCreatureFormChanged para re-armar cuando forma cambia (Egg→Slime→Adult). **S139:** SetMood() refactorizado — material único (bank.FaceMaterial, shader MoriMonchi/MonchiFace) con MPB write (_MainTex/_PrevTex/_FaceT/_FaceMode índice material 0); obtiene set de ánimo por género via bank.MoodSetFor(Gender); integra MonchiFaceTransition para feedback sincronizado (blink/pop).

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `SetBank(MonchiVisualBankSO)` | Asigna banco visual |
| `SetFurDatabase(FurTypeDatabaseSO)` | Asigna database de pelajes |
| `Assemble(CreatureDNA dna)` | **S137 MODIFICADO:** Instancia body según Form (Egg/Slime usan builders, Adult usa prefab directo), grafia partes modulares (HornID/BackID/WingID) si adulto y existen en banco, mapea renderers, aplica look; desactiva hijos viejos antes de destruir; propaga capa Root a todos los hijos. Flujo: Instancia body según Form → SetActive(false)/Destroy hijos previos → PropagaCapa → GraftPart por slot (si adulto) → Recorre SkinnedMeshRenderers activos → ApplyLook → SetMood |
| `RefreshLook(CreatureDNA dna)` | Retinta sin re-instanciar; llama Assemble si bodyInstance es null o Form cambió |
| `SetMood(MonchiMood)` | **S139 MODIFICADO:** Material único (bank.FaceMaterial) + MPB write (_MainTex/_PrevTex/_FaceT/_FaceMode idx 0); interpola _FaceT 0→1 vía shader; llama bank.MoodSetFor(gender) para obtener set correcto; sincroniza MonchiFaceTransition feedback (blink/pop) si está activo |
| `SetRimOverride(Color color, float power, float insideMask)` | **S110 NUEVO** anula rim light genético con color/power/mask de rival |
| `ClearRimOverride()` | **S110 NUEVO** restaura rim light genético |

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
| `bank` | `MonchiVisualBankSO` | Visual bank |
| `furDatabase` | `FurTypeDatabaseSO` | Database de pelajes |
| `bodyInstance` | `GameObject` | Instancia del body prefab |
| `animator` | `Animator` | Animator del body |
| `faceRenderer` | `SkinnedMeshRenderer` | Renderer del rostro |
| `tintRenderers` | `List<SkinnedMeshRenderer>` | Renderers a teñir (alas, cuernos, espalda, etc.); **S134:** incluye renderers injertados de partes |
| `currentDna` | `CreatureDNA` | DNA vigente |
| `assembledForm` | `MonchiForm` | Forma del modelo instanciado (para detectar cambios en RefreshLook, S137) |
| `currentMood` | `MonchiMood` | Mood vigente |
| `currentFaceTexture` | `Texture` | **S139 NUEVO** Textura de cara actual (para detectar cambios) |
| `rimOverride` | `bool` | **S110 NUEVO** si se aplica override de rim |
| `rimOverrideColor` | `Color` | **S110 NUEVO** color override |
| `rimOverridePower` | `float` | **S110 NUEVO** power override |
| `rimOverrideInsideMask` | `float` | **S110 NUEVO** inside mask override |

## Flujo Assemble() S137 (Form-Aware Assembly)

1. **Limpia hijos previos:** desactiva visualmente (SetActive(false)), luego destruye diferido
2. **Reinicia estado:** bodyInstance=null, animator=null, faceRenderer=null, tintRenderers.Clear(), `assembledForm = dna.Form` (S137)
3. **Valida banco:** si no existe MonchiVisualBankSO → warning y return
4. **Elige constructor según Form (S137 NUEVO):**
   - **Form.Slime:** `bodyInstance = MonchiSlimeBody.Build(dna, bank, Root)` → slime model + cuerno injertado
   - **Form.Egg:** `bodyInstance = MonchiEggBody.Build(dna, bank, Root)` → egg model + espalda injertada
   - **Form.Adult (default):** `bodyInstance = Instantiate(bank.GetBody(dna.BodyShapeID), Root)` → body prefab adulto completo
5. **Propaga capa** a todos hijos (S115)
6. **Asigna Animator:** obtiene existente o crea; asigna RuntimeAnimatorController del banco (elegido según Form)
7. **Grafia partes modulares (S134, solo si Adult):**
   - `GraftPart(dna.HornID, "Horn")` → desactiva renderers "Horn*", injerta si partPrefab existe
   - `GraftPart(dna.BackID, "Back")` → desactiva renderers "Back*", injerta si partPrefab existe
   - `GraftPart(dna.WingID, "Wing")` → desactiva renderers "Wing*", injerta si partPrefab existe
8. **Recorre renderers activos:** busca Face, acumula resto en tintRenderers (solo componentes activos, ignora desactivados)
9. **Vincula MonchiFaceTransition (S139):** si faceRenderer != null y bank.FaceMaterial != null y faceTransition != null, llama `faceTransition.Bind(faceRenderer)` para vincular ShaderControllers
10. **Aplica look:** tintado de colores genéticos + override si existe (**S136 MODIFICADO:** usa MonchiTint)
11. **Aplica mood:** SetMood(currentMood) para sincronizar facial material

## Suscripción a OnCreatureFormChanged (S137 NUEVO)

```csharp
private void OnEnable()
{
    GameEvents.OnCreatureFormChanged += HandleFormChanged;
}

private void OnDisable()
{
    GameEvents.OnCreatureFormChanged -= HandleFormChanged;
}

private void HandleFormChanged(CreatureDNA dna)
{
    if (dna == currentDna)
    {
        RefreshLook(dna);  // Detecta Form cambió, re-arma
    }
}
```

**Contexto:** Cuando BreedingController o IncubationService dispara `GameEvents.CreatureFormChanged(egg)` (transición Egg→Slime), MonchiVisualizer suscrito re-arma el visual sin necesidad de llamada explícita.

## Método InstantiateBody(CreatureDNA dna) S137 (Form-Aware)

```csharp
private RuntimeAnimatorController InstantiateBody(CreatureDNA dna)
{
    if (dna.Form == MonchiForm.Slime)
    {
        bodyInstance = MonchiSlimeBody.Build(dna, bank, Root);
        return bodyInstance != null ? bank.SlimeAnimatorController : null;
    }
    if (dna.Form == MonchiForm.Egg)
    {
        bodyInstance = MonchiEggBody.Build(dna, bank, Root);
        return bodyInstance != null ? bank.EggAnimatorController : null;
    }
    // Form.Adult (default)
    var prefab = bank.GetBody(dna.BodyShapeID);
    bodyInstance = Object.Instantiate(prefab, Root);
    return bank.AnimatorController;
}
```

**Cambio S137:** Agregados bloques para Slime y Egg, usan builders estáticos + controladores específicos del banco.

## Método GraftPart() S134 (NUEVO, solo adulto)

```csharp
private void GraftPart(string partId, string prefix)
{
    var partPrefab = bank.GetPartMesh(partId);   // Obtiene FBX de parte
    if (partPrefab == null)
        return;                                   // Si no existe, skip
    
    // Desactiva renderers baked del prefijo
    foreach (var renderer in bodyInstance.GetComponentsInChildren<SkinnedMeshRenderer>(true))
    {
        if (renderer.gameObject.name.StartsWith(prefix))
            renderer.gameObject.SetActive(false);
    }
    
    // Injerta parte e inyecta renderers en tintRenderers
    var grafted = new List<SkinnedMeshRenderer>();
    MonchiPartGrafter.Graft(partPrefab, bodyInstance, grafted);
}
```

**Responsabilidad:**
- Obtiene prefab FBX de parte desde banco (identidad única + DNA determinístico)
- Desactiva los renderers "horneados" del body que coinciden con el prefijo (Horn*/Back*/Wing*)
- Llama MonchiPartGrafter.Graft() que:
  - Remapea huesos
  - Recalcula bindposes al espacio del cuerpo
  - Reparenta SkinnedMeshRenderers del prefab al bodyInstance
  - Recoge los renderers en lista `grafted` (actualmente unused, pero reservado para auditoría)

**Impacto visual:**
- Partes modulares reemplazan completamente los renderers baked (no se superponen)
- Posibilidad de no grafia (si partId empty o no en banco) → body queda con renderer baked
- Tintado unificado luego: Assemble() recorre solo renderers activos, incluye injertados

## Método SetMood() S139 (Material Único + MPB)

```csharp
public void SetMood(MonchiMood mood)
{
    currentMood = mood;
    if (faceRenderer == null || bank == null) return;

    var set = bank.MoodSetFor(currentDna != null ? currentDna.Gender : CreatureGender.Unknown);
    if (set == null) return;

    var face = set.GetFace(mood);           // Material con mainTexture = cara
    if (face == null) return;

    if (bank.FaceMaterial == null)          // Fallback: material viejo (legacy)
    {
        faceRenderer.sharedMaterial = face;
        return;
    }

    var tex = face.mainTexture;             // Textura de cara del mood
    if (tex == currentFaceTexture) return;  // Sin cambio = sin-op

    var prev = currentFaceTexture != null ? currentFaceTexture : tex;
    currentFaceTexture = tex;
    bool pop = set.IsPop(mood);             // Pop transition vs blink
    bool animate = faceTransition != null && faceTransition.isActiveAndEnabled && prev != tex;

    var mpb = new MaterialPropertyBlock();
    faceRenderer.GetPropertyBlock(mpb, 0);                       // Obtiene MPB actual idx 0
    mpb.SetTexture(MainTexId, tex);                              // _MainTex = textura nueva
    mpb.SetTexture(PrevTexId, prev);                             // _PrevTex = textura previa
    mpb.SetFloat(FaceModeId, pop ? 1f : 0f);                     // _FaceMode: 1=pop, 0=blink
    mpb.SetFloat(FaceTId, animate ? 0f : 1f);                    // _FaceT: 0=inicio anim, 1=fin
    faceRenderer.SetPropertyBlock(mpb, 0);                       // Escribe MPB idx 0

    if (animate)
        faceTransition.Play(pop);                                // Reproduce feedback blink/pop
}
```

**Cambio S139:**
- **Material único:** usa `bank.FaceMaterial` en lugar de swapear material completo
- **MPB write:** escribe _MainTex, _PrevTex, _FaceMode, _FaceT en índice material 0
- **Gender-aware set:** `bank.MoodSetFor(gender)` retorna moodSetFemale si existe y gender=Female, sino moodSet
- **Feedback sincronizado:** si MonchiFaceTransition está activo y hay cambio de textura, reproduce feedback (ShaderController anima _FaceT)
- **Shader-driven animation:** el shader MoriMonchi/MonchiFace interpola _MainTex (nueva) ← → _PrevTex (vieja) usando _FaceT y _FaceMode

## Cambios S137

**InstantiateBody() — Form-aware (línea 109-133 MODIFICADO):**
```csharp
if (dna.Form == MonchiForm.Slime)
{
    bodyInstance = MonchiSlimeBody.Build(dna, bank, Root);
    if (bodyInstance == null) { Debug.LogWarning(...); return null; }
    return bank.SlimeAnimatorController;
}

if (dna.Form == MonchiForm.Egg)
{
    bodyInstance = MonchiEggBody.Build(dna, bank, Root);
    if (bodyInstance == null) { Debug.LogWarning(...); return null; }
    return bank.EggAnimatorController;
}

// Form.Adult (default)
...
```

**Assemble() — savedForm y refresh check (línea 58 + RefreshLook NUEVO):**
```csharp
public void Assemble(CreatureDNA dna)
{
    // ...
    assembledForm = dna.Form;  // S137: recordar qué forma armamos
}

public void RefreshLook(CreatureDNA dna)
{
    currentDna = dna;
    if (bodyInstance == null || dna.Form != assembledForm)  // S137: si Form cambió
    {
        Assemble(dna);
        return;
    }
    // ... sino, retinta sin re-instanciar
}
```

**Suscripción a GameEvents (S137 NUEVO en OnEnable/OnDisable o en Awake):**
- OnEnable: suscribe `GameEvents.OnCreatureFormChanged += HandleFormChanged`
- OnDisable: desuscribe
- HandleFormChanged: si dna == currentDna, llama RefreshLook (que detecta cambio de Form y re-arma)

## Cambios S139

**SetMood() — Material único + MPB + Gender-aware (línea 208-243 COMPLETAMENTE REFACTORIZADO):**

Antes (S110-S136):
```csharp
public void SetMood(MonchiMood mood)
{
    currentMood = mood;
    if (faceRenderer == null || bank == null) return;
    var face = bank.MoodSet.GetFace(mood);  // Material directo, swapea sharedMaterial
    faceRenderer.sharedMaterial = face;
}
```

Ahora (S139):
```csharp
public void SetMood(MonchiMood mood)
{
    currentMood = mood;
    if (faceRenderer == null || bank == null) return;
    
    var set = bank.MoodSetFor(currentDna != null ? currentDna.Gender : CreatureGender.Unknown);
    if (set == null) return;
    
    var face = set.GetFace(mood);
    if (face == null) return;
    
    if (bank.FaceMaterial == null)  // Fallback legacy
    {
        faceRenderer.sharedMaterial = face;
        return;
    }
    
    var tex = face.mainTexture;
    if (tex == currentFaceTexture) return;  // Sin cambio
    
    var prev = currentFaceTexture != null ? currentFaceTexture : tex;
    currentFaceTexture = tex;
    bool pop = set.IsPop(mood);
    bool animate = faceTransition != null && faceTransition.isActiveAndEnabled && prev != tex;
    
    var mpb = new MaterialPropertyBlock();
    faceRenderer.GetPropertyBlock(mpb, 0);          // Lee MPB actual
    mpb.SetTexture(MainTexId, tex);                  // _MainTex = cara nueva
    mpb.SetTexture(PrevTexId, prev);                 // _PrevTex = cara previa
    mpb.SetFloat(FaceModeId, pop ? 1f : 0f);         // _FaceMode: 1=pop, 0=blink
    mpb.SetFloat(FaceTId, animate ? 0f : 1f);        // _FaceT: 0=anim, 1=fin
    faceRenderer.SetPropertyBlock(mpb, 0);          // Escribe MPB idx 0
    
    if (animate)
        faceTransition.Play(pop);  // Reproduce feedback
}
```

**Responsabilidad S139:**
- `bank.MoodSetFor(gender)` → retorna set correcto (female/male/neutral)
- Material único evita overhead de instantiate por mood
- MPB write permite shader-driven transitions sin material swap
- ShaderController (Feel) escribe en material durante feedback, sincronizado con _FaceT

**Impacto S139:**
- Animaciones faciales suaves (blink/pop) manejadas por shader + feedback
- Soporte de sets de ánimo por género (hembra diferente de macho)
- Performance: un material = cero allocations de material instantiation
- Quirk: ShaderController escribe `faceRenderer.material`, MPB escribe `faceRenderer.GetPropertyBlock()` — orden importa (MPB primero, luego feedback)

## Cambios S61

**Assemble() línea 40-45:**
```csharp
for (int i = modelRoot.childCount - 1; i >= 0; i--)
{
    var child = modelRoot.GetChild(i).gameObject;
    child.SetActive(false);              // NUEVO: desactiva antes de destruir
    Object.Destroy(child);
}
```

**Contexto:**
- Destroy() es una operación diferida que se ejecuta al fin del frame actual
- El fotomatón (headshot batch render) renderiza en el MISMO frame antes de que Destroy() se ejecute
- Sin SetActive(false), el body viejo sigue visible en el render, superponiéndose al cuerpo nuevo
- Con SetActive(false), el renderer se desactiva inmediatamente, saliendo de la vista del fotomatón

**Impacto:**
- Evita ghosting visual en headshots batch (artefactos de dos cabezas/cuerpos superpuestos)
- La instancia aún existe en memoria hasta fin de frame, pero es invisible

## Cambios S93

- **Removido:** método `SetGhost(float alpha)` (fue descartado; ghosting visual de cadáveres se maneja en otro lado o no se soporta más)

## Cambios S107

- Sin cambios en lógica del script
- MonchiTurntable (S107 NUEVO) usa MonchiVisualizer en sus booths para renderizar spinning 3D

## Cambios S110

**SetRimOverride(Color, float, float) — NUEVO (línea 109-115):**
```csharp
public void SetRimOverride(Color color, float power, float insideMask)
{
    rimOverride = true;
    rimOverrideColor = color;
    rimOverridePower = power;
    rimOverrideInsideMask = insideMask;
    ApplyLook();
}
```
- Activa override y guarda valores
- Llama `ApplyLook()` para retintar con nuevos valores de rim
- Usado por MonchiTeamRim cuando agent.Team == Rival

**ClearRimOverride() — NUEVO (línea 118-123):**
```csharp
public void ClearRimOverride()
{
    if (!rimOverride) return;
    rimOverride = false;
    ApplyLook();
}
```
- Desactiva override
- Llama `ApplyLook()` para restaurar rim genético
- Usado por MonchiTeamRim cuando agent.Team != Rival

**Tint() método — MODIFICADO para aplicar override (línea 176-195):**
- Si `rimOverride`:
  - Escribe en MPB: `_RimLightColor = rimOverrideColor`
  - Escribe en MPB: `_RimLight_Power = rimOverridePower`
  - Escribe en MPB: `_RimLight_InsideMask = rimOverrideInsideMask`
  - Escribe en MPB: `_Is_LightColor_RimLight = 0f` (switch a modo luz)
- Sino: usa rim genético `Lerp(color, Color.white, 0.65f)`

**Impacto S110:**
- Rivales tienen rim rojo (1, 0.3, 0.22) para identidad visual clara
- Aliados conservan rim genético por color de pelaje
- Override se aplica en tintado, no globalizado (cada criatura teñida independientemente)

## Cambios S115

**Assemble() — propagación de capa (línea 77-78 ACTUALIZADO):**
```csharp
foreach (var childTransform in bodyInstance.GetComponentsInChildren<Transform>(true))
    childTransform.gameObject.layer = Root.gameObject.layer;
```
- Tras instanciar body, propaga layer del Root (modelRoot) a todos los hijos del body instanciado
- URP PC_Renderer utiliza `RenderObjects` pass con tags CreatureBodyMask/CreatureBodySilhouette que filtra por capa `CreatureBody`
- Esto permite que la pasada de silueta/stencil (shaders `MonchiCue`, `MonchiRibbon` con ZTest Always + stencil NotEqual 1) dibuje correctamente solo cuando la capa coincide

**Impacto S115:**
- Guías visuales (rutas, telegrafía, etc.) se dibujan sobre MoriMonchis (prioridad shaders: criaturas > guías > escenario)
- La capa permite filtrado granular en pass URP para control de profundidad y stencil

## Cambios S134

**Assemble() — Modular Part Grafting (línea 86-88 NUEVO):**
```csharp
GraftPart(dna.HornID, "Horn");
GraftPart(dna.BackID, "Back");
GraftPart(dna.WingID, "Wing");
```
- Tras instanciar body y configurar Animator, injerta partes modulares
- Cada GraftPart desactiva renderers baked del prefijo, luego injerta si partPrefab existe en banco
- MonchiPartGrafter maneja remapeo de huesos, bindposes, rootBone y reparentación

**Assemble() — Recolecta renderers (línea 90-96 MODIFICADO):**
```csharp
foreach (var renderer in bodyInstance.GetComponentsInChildren<SkinnedMeshRenderer>(false))
{
    if (renderer.gameObject.name == "Face")
        faceRenderer = renderer;
    else
        tintRenderers.Add(renderer);
}
```
- Usa `GetComponentsInChildren(..., false)` → solo renderers ACTIVOS
- Incluye tanto renderers baked como injertados (ambos activos después de Assemble)
- Resultado: tintRenderers acumula todos excepto Face

**Impacto S134:**
- Sistema modular: HornID/BackID/WingID cargan FBX independientes (sin duplicar body base)
- Composición dinámica: no hay limitante de partes activas (nil ID = usa baked, else = injerta)
- Tintado unificado: ApplyLook() recorre tintRenderers que mezcla baked+injertados sin diferenciar
- DNA determinístico: cada criatura con mismo BodyShapeID+HornID+BackID+WingID renderiza idéntico

## Cambios S136

**ApplyLook() — Refactorización de tintado (línea 158-189 MODIFICADO):**

Antes (S110-S134):
```csharp
// Lógica inline de mapeo de colores por nombre renderer
if (rendererName.StartsWith("Wing")) { color = wing; }
else if (rendererName.StartsWith("Horn") || ...) { color = accent; }
// ... etc.
var palette = ColorGenetics.BuildFurPalette(...);
mpb.SetColor(_BaseColorId, palette.Base);
// ... etc.
```

Ahora (S136):
```csharp
var color = MonchiTint.ColorFor(partName, currentDna, wing, accent);
Tint(renderer, color);  // En Tint(), se llama MonchiTint.Fill()
```

**Método Tint() — Refactorizado (línea 191-203 MODIFICADO):**

Antes (S110-S134):
```csharp
private void Tint(Renderer renderer, Color color)
{
    var mpb = new MaterialPropertyBlock();
    // Inline: mpb.SetColor(_BaseColorId, palette.Base); etc.
}
```

Ahora (S136):
```csharp
private void Tint(Renderer renderer, Color color)
{
    var mpb = new MaterialPropertyBlock();
    MonchiTint.Fill(mpb, color);        // Centraliza paleta
    if (rimOverride)
    {
        mpb.SetColor(RimColorId, rimOverrideColor);
        // ... override rules
    }
    renderer.SetPropertyBlock(mpb);
}
```

**Responsabilidad de MonchiTint (S136 NUEVO):**
- `MonchiTint.ColorFor(name, dna, wing, accent)` → determina color por regla de nombre renderer (Deco_*, Wing*, Horn/Back, Teech, default)
- `MonchiTint.Fill(mpb, color)` → arma paleta 4-color (Base, Shade1, Shade2, Rim)
- Beneficio: lógica reutilizable en EggLabAssembler (mismo tintado para huevos)

**Impacto S136:**
- Desacoplamiento: lógica de color extraída a utilidad estática reutilizable
- Reducción de código: MonchiVisualizer ApplyLook/Tint más legibles
- Reutilización: EggLabAssembler.Build() usa MonchiTint sin duplicar lógica
- Determinismo: ColorFor() garantiza mismo resultado varias veces (nombre = determinista)

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

## Notas S61

- Assemble() desactiva hijos viejos inmediatamente, destroye diferido
- Fotomatón renderiza en mismo frame; desactivar antes de Destroy evita ghosting
- Previene artefactos visuales en headshot batch

## Notas S107

- MonchiTurntable crea booths con MonchiVisualizer instanciado dinámicamente
- SetBank() y SetFurDatabase() llamados desde MonchiTurntable.Awake()
- Assemble() llamado desde MonchiTurntable.Show() cuando preview debe renderizar

## Notas S110

- MonchiTeamRim (presentador) monitorea agent.Team y llama SetRimOverride/ClearRimOverride
- Rim override solo afecta rivales (ExpeditionTeam.Rival)
- Color/power/insideMask editables en MonchiTeamRim para tuning
- ApplyLook() recalcula todo el tintado; no es performance-critical (una vez per assembly o team change)

## Notas S115

- Layer propagation es parte del flujo Assemble(): se ejecuta inmediatamente tras instanciar, antes de ApplyLook()
- La capa Root debe estar configurada en el prefab del MoriMochiAgent (se heredará automáticamente)
- Este cambio es esencial para que URP RenderObjects pass con capa `CreatureBody` funcione correctamente en la pasada de silueta

## Notas S134

- **Modular assembly:** HornID/BackID/WingID cargan prefabs FBX independientes (sin duplicar body base)
- **Determinismo:** mismo DNA = misma composición visual (hash estable sobre IDs)
- **GetComponentsInChildren(false):** recorre solo activos, incluye partes injertadas automáticamente
- **GraftPart fallback:** si partPrefab nil o ID vacío → body mantiene renderer baked de ese slot
- **Tintado universal:** ApplyLook() no distingue entre baked/injertado, aplica mismo ColorGenetics
- **MonchiPartGrafter:** utilidad estática que maneja plomería de bindposes y huesos (sin estado, reusable)

## Notas S136

- **Refactorización de tintado:** lógica de color extraída a MonchiTint para reutilización
- **ColorFor() determinista:** mismo nombre renderer = mismo color (regla de mapeo fija)
- **Fill() centralizado:** paleta 4-color armada una sola vez (antes en Tint inline)
- **Reutilización:** EggLabAssembler.Build() llama MonchiTint sin duplicar código
- **Invariante de rim:** override de rim se aplica DESPUÉS de Fill() en Tint() (nivel de prioridad correcto)

## Notas S137

- **Form-aware assembly:** Egg/Slime usan builders estáticos (MonchiEggBody/MonchiSlimeBody), Adult usa prefab
- **Detecta cambios de Form:** assembledForm guarda qué forma se armó; RefreshLook compara y re-arma si cambió
- **OnCreatureFormChanged:** suscripción a evento GameEvents, permite re-armado automático sin llamada explícita
- **Builders estáticos:** MonchiEggBody.Build() y MonchiSlimeBody.Build() manejan inyección de partes (espalda para huevo, cuerno para slime)
- **Animators específicos:** bank.EggAnimatorController, bank.SlimeAnimatorController, bank.AnimatorController (adulto)

## Notas S139

- **Material único:** bank.FaceMaterial es el material shader MoriMonchi/MonchiFace que anima transiciones
- **MPB write:** _MainTex (nueva cara), _PrevTex (cara previa), _FaceT (interpolación 0→1), _FaceMode (0=blink, 1=pop)
- **Gender-aware set:** `bank.MoodSetFor(gender)` retorna moodSetFemale si existe y es Female, sino moodSet
- **Feedback sincronizado:** MonchiFaceTransition.Play(pop) reproduce feedback mientras shader anima _FaceT
- **Quirk:** ShaderController escribe en material completo; MPB escribe en índice 0. Orden: SetPropertyBlock primero (MPB), luego Play (ShaderController). Si ambos escriben al mismo tiempo, ShaderController puede pisar MPB en el frame de feedback — monitorear en QA.
- **Fallback legacy:** si bank.FaceMaterial null, swapea sharedMaterial directamente (compatibilidad backwards)

## Vinculado a

- [[Index/10 - Visualization]]
- [[Index/02 - Genetics & Breeding]] (S137: ciclo de vida)
- [[Index/23 - Arena Sandbox y Expedicion]]
- [[Index/31 - EggLab & Incubadora]] (S137: visual de huevos, S136 NUEVO: EggLabAssembler reutiliza MonchiTint)
- [[MonchiVisualBankSO]], [[ColorGenetics]]
- [[MonchiTint]] (S136 NUEVO) utilidad de mapeo de colores
- [[MonchiTeamRim]] (S110 NUEVO) llamador de SetRimOverride/ClearRimOverride
- [[MonchiPartGrafter]] (S134 NUEVO) utilidad de injerto de partes
- [[MonchiEggBody]] (S137 NUEVO) builder de huevo
- [[MonchiSlimeBody]] (S137 NUEVO) builder de slime
- [[MonchiFaceTransition]] (S139 NUEVO) coordinador de feedback blink/pop

## Conexiones

**Entrada:**
- Assemble/RefreshLook: CreatureDNA (incluyendo Form, S137)
- SetMood: MonchiMoodDriver (S139: ahora usa bank.MoodSetFor(gender))
- SetRimOverride/ClearRimOverride: MonchiTeamRim (S110)
- GameEvents.OnCreatureFormChanged: BreedingController/IncubationService (S137)

**Salida:**
- Modelo visual world-space con capa Root propagada a hijos (S115)
- Material Face único con MPB write (_MainTex/_PrevTex/_FaceT/_FaceMode, S139)
- MPB de rim light (genético u override)
- Partes injertadas integradas en tintRenderers (S134)
- Tintado determinístico via MonchiTint (S136)
- Form-aware visual: Egg/Slime/Adult (S137)
- Feedback blink/pop sincronizado vía MonchiFaceTransition (S139)

**Dependencias S134:**
- MonchiVisualBankSO.GetPartMesh(partId) → obtiene FBX de parte
- MonchiPartGrafter.Graft() → injerta y remapea huesos

**Dependencias S136:**
- MonchiTint.ColorFor() → mapeo determinístico de color por renderer name
- MonchiTint.Fill() → paleta 4-color en MPB

**Dependencias S137:**
- MonchiEggBody.Build() → constructor de visual huevo
- MonchiSlimeBody.Build() → constructor de visual slime
- GameEvents.OnCreatureFormChanged → suscripción para re-armado automático

**Dependencias S139:**
- MonchiVisualBankSO.FaceMaterial → material único shader-driven
- MonchiVisualBankSO.MoodSetFor(gender) → set de ánimo por género
- MonchiMoodSetSO.GetFace(mood) → obtiene material con mainTexture
- MonchiMoodSetSO.IsPop(mood) → determina tipo de transición (pop vs blink)
- MonchiFaceTransition → coordinador de feedback blink/pop
