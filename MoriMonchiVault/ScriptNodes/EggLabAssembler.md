---
tags: [script, world, creature, visual]
---

# EggLabAssembler.cs

**Ruta:** `World/Creatures/EggLabAssembler.cs`

**Responsabilidad:** Utilidad estática que ensambla visualmente un huevo a partir de CreatureDNA. **S136 NUEVO.** Análogo a MonchiVisualizer.Assemble() pero para forma Egg (bebé). Instancia modelo base, injerta partes modulares (Horn, Back), aplica animador, colorea vía MonchiTint, retorna GameObject listo para render.

## Método Público

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Build(CreatureDNA dna, MonchiVisualBankSO bank, FurTypeDatabaseSO furDb, GameObject eggModel, RuntimeAnimatorController controller, Transform parent)` | `GameObject` | Ensambla huevo: instancia, injerta partes, tinta colores, retorna root |

## Firma Build()

```csharp
public static GameObject Build(
    CreatureDNA dna,
    MonchiVisualBankSO bank,
    FurTypeDatabaseSO furDb,
    GameObject eggModel,
    RuntimeAnimatorController controller,
    Transform parent
)
```

## Flujo Build()

1. **Instancia modelo base:** `Object.Instantiate(eggModel, parent)` (transform identity)
2. **Configura Animator:**
   - Obtiene Animator existente o crea uno
   - Asigna RuntimeAnimatorController si existe
3. **Determina variante de partes por BodyShape:**
   - Obtiene `bank.GetBody(dna.BodyShapeID)` para buscar letra de variante (último char del nombre prefab)
   - Ej: prefab "DragonBody_A" → letra = 'A', prefab "DragonBody_D" → letra = 'D'
   - Default: 'A' si no hay prefab o nombre vacío
4. **Activa variantes de partes baked:**
   - `ApplyPrefixVariant(root, "Egg_Horn_", "Egg_Horn_" + bodyLetter)` — solo mantiene el GameObject que coincide
   - `ApplyPrefixVariant(root, "Egg_Back_", bodyLetter == 'D' ? "Egg_Back_B" : "Egg_Back_A")` — lógica especial para Back (D→B, else→A)
5. **Injerta partes modulares (si existen):**
   - `GraftEggPart(root, bank.GetPartMesh(dna.HornID, MonchiForm.Egg), "Egg_Horn_")`
   - `GraftEggPart(root, bank.GetPartMesh(dna.BackID, MonchiForm.Egg), "Egg_Back_")`
6. **Obtiene colores harmónicos:**
   - `ColorGenetics.BuildHarmony(dna.BaseColor, out var wing, out var accent)`
7. **Selecciona material de pelaje:**
   - Si Shiny y existe gem en banco: `bank.GetGem(dna.ToStringID())`
   - Sino: `furDb.GetMaterial(dna.FurType)`
8. **Tiñe renderers activos:**
   - Itera `GetComponentsInChildren<Renderer>()` (solo activos)
   - Salta "Egg_Scales" (material especial)
   - Asigna shared material (pelaje o gema)
   - Si no Shiny: calcula color vía `MonchiTint.ColorFor()` + rellena MPB vía `MonchiTint.Fill()`
   - Si Shiny: usa gem material directamente, MPB vacío
9. **Retorna root del instancia**

## Métodos Privados

### ApplyPrefixVariant()

```csharp
private static void ApplyPrefixVariant(Transform root, string prefix, string keep)
```

**Responsabilidad:** Desactiva todos los GameObjects hijos que comienzan con `prefix` excepto el que se llama exactamente `keep`.

**Uso:** Seleccionar variantes de partes baked (Egg_Horn_A vs Egg_Horn_B, etc.)

### GraftEggPart()

```csharp
private static void GraftEggPart(Transform root, GameObject partMesh, string prefix)
```

**Responsabilidad:**
1. Si partMesh es null → return (sin error)
2. Desactiva todos los hijos que comienzan con `prefix`
3. Busca u obtiene Transform "Body" del root
4. Instancia partMesh como hijo del root (transform identity)
5. Reparenta a Body si existe
6. No recalcula bindposes (esto es asunto del modelo FBX, no del assembler)

**Diferencia con MonchiVisualizer.GraftPart():**
- EggLabAssembler NO llama MonchiPartGrafter.Graft() (ese hace remapeo de huesos complejos)
- EggLabAssembler hace reparentación simple (asume que partMesh ya tiene su propia armadura)

### FindChildByName()

```csharp
private static Transform FindChildByName(Transform root, string name)
```

**Busca** el primer hijo (recursivo) cuyo nombre coincida exactamente. Retorna null si no existe.

## Cambios S136

**Nuevo script dedicado a ensamblaje de huevos:**
- Patrón: utilidad estática reutilizable (como ColorGenetics, MonchiTint)
- Reduce complejidad de EggLabBuilder (que solo orquesta llamadas)
- Reutilizable si futuros sistemas necesitan ensamblar huevos

**Uso de MonchiTint (S136 NUEVO):**
- ColorFor() determina color por renderer name
- Fill() rellena MPB con paleta

**Variantes de partes baked por BodyShape:**
- `ApplyPrefixVariant()` activa solo la variante que coincida con letra del body
- Permite economía de meshes: un modelo base puede tener 3-4 variantes de cuerno/espalda prebaked

**Inyeccion de partes modulares:**
- GraftEggPart() más simple que MonchiPartGrafter.Graft() (no remapea huesos complejos)
- Asume que partes modular FBX para Egg son auto-contenidas (su propia armadura si es necesario)

## Notas S136

- Utilidad sin estado (static)
- No hereda de MonoBehaviour
- Independiente de EggLabBuilder (puede usarse desde otro contexto)
- Tintado igual que MonchiVisualizer (ColorGenetics + MonchiTint)
- Gem para Shiny reemplaza material de pelaje completamente (sin tintado MPB)

## Invariantes

- Si MonchiVisualBankSO es null → solo instancia el modelo base (sin partes ni tintado)
- Si partMesh es null → mantiene renderer baked del prefijo
- Egg_Scales renderer es ignorado en tintado (material especial preservado)
- Rigging de huevos es simple (no requiere remapeo complejo de armadura como adultos)

## Vinculado a

- [[MonchiTint]] — ColorFor, Fill (S136)
- [[ColorGenetics]] — BuildHarmony, DeriveSecondary, BuildFurPalette
- [[MonchiVisualBankSO]] — GetBody, GetPartMesh, GetGem
- [[FurTypeDatabaseSO]] — GetMaterial
- [[EggLabBuilder]] — llamador único actual

## Conexiones

**Entrada:**
- CreatureDNA (BodyShapeID, HornID, BackID, BaseColor, FurType, IsShiny)
- MonchiVisualBankSO (body, partes modulares, gems, animator controller)
- FurTypeDatabaseSO (materiales de pelaje)
- GameObject eggModel (prefab base)
- RuntimeAnimatorController (animador de huevo)
- Transform parent (dónde instanciar)

**Salida:**
- GameObject instanciado con renderers teñidos, partes injertadas, animator asignado
- Listo para posicionar, agregar collider, añadir EggIdleShuffler
