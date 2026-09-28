---
tags: [script, world, creature, orchestrator]
---

# EggLabBuilder.cs

**Ruta:** `World/Creatures/EggLabBuilder.cs`

**Responsabilidad:** Orquestador del laboratorio de huevos (`Resources/Scenes/EggLab.unity`). **S136 NUEVO.** Genera pares madre/padre aleatorios, breedea huevos, instancia visuales via EggLabAssembler, posiciona en grid, maneja interacción raycast, eventos de rebuild/select.

## Campos Serializados (Required)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `partDatabase` | `CreatureDatabaseSO` | Database de partes para GenerateRandom |
| `furDatabase` | `FurTypeDatabaseSO` | Database de pelajes para apariencia |
| `visualBank` | `MonchiVisualBankSO` | Banco visual (bodies, partes, gemas) |
| `odds` | `InheritanceOddsTableSO` | Tabla de probabilidades de breeding |
| `eggModel` | `GameObject` | Prefab base de huevo (modelo FBX) |
| `eggController` | `RuntimeAnimatorController` | Animator controller para huevos |
| `eggsRoot` | `Transform` | Raíz donde instanciar huevos |
| `worldCamera` | `Camera` | Cámara world (para raycast de picking) |

## Campos Serializados (Configuración)

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `count` | `int` | 24 | Cantidad de huevos a generar |
| `columns` | `int` | 6 | Columnas de grid (24 / 6 = 4 filas) |
| `spacing` | `float` | 0.55 | Distancia entre huevos |
| `faceYaw` | `float` | 180 | Rotación Y inicial de todos los huevos (hacia cámara) |

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Entries` | `IReadOnlyList<EggLabEntry>` | Lista de huevos generados (read-only) |

## Eventos Públicos

| Evento | Argumento | Disparado Cuando |
|--------|-----------|-----------------|
| `Rebuilt` | (sin argumentos) | Al terminar Rebuild() |
| `Selected` | `EggLabEntry` | Cuando usuario selecciona un huevo via raycast o Select() |

## Ciclo de Vida

| Evento | Acción |
|--------|--------|
| `Start()` | Llama `Rebuild()` para generar huevos iniciales |
| `Update()` | Raycast de picking: si click izquierdo sobre huevo, dispara `Selected` |
| `OnDestroy()` | Destruye `registry` (ScriptableObject temporal) |

## Métodos Públicos

### Rebuild()

```csharp
public void Rebuild()
```

**Responsabilidad:** Genera N huevos nuevos desde cero.

**Flujo:**
1. **Limpia escena:** Destruye todos los hijos de `eggsRoot`
2. **Reinicia listas:** entries.Clear()
3. **Crea registry temporal:** `ScriptableObject.CreateInstance<CreatureRegistrySO>()`
   - Necesario para guardar padres/madres durante breeding
   - Se destruye en OnDestroy
4. **Loop i=0..count-1:**
   - **Genera madre:** GenerateRandom → BodyShapeID, partes, color aleatorios
     - Gender = Female
     - Timestamp = ++nextTimestamp (secuencial)
     - CustomName = random via CreatureNameBank
     - Registry.Register(mother)
   - **Genera padre:** análogo, Gender = Male
   - **Breedea hijo:** `BreedingService.Breed(mother.UniqueID, father.UniqueID, registry, ...)`
     - Si retorna null → continúa (falla de breed, rare)
   - **Crea entry:** nuevo EggLabEntry con datos genéticos, Progress01=Random.value, HatchCost calculado
   - **Construye visual:** `EggLabAssembler.Build()` → GameObject instanciado
   - **Posiciona en grid:** x = (i % columns - (columns-1)/2) * spacing → centrado horizontal
     - z = -(i / columns) * spacing → filas hacia atrás
   - **Configura GameObject:**
     - name = "Egg_" + número
     - AddComponent<EggIdleShuffler> para animación automática
     - AddComponent<CapsuleCollider> (radio 0.13, altura 0.32, centro Y=0.16) para picking
   - **Almacena entry en lista**
5. **Dispara evento:** `Rebuilt?.Invoke()`

### Select(EggLabEntry)

```csharp
public void Select(EggLabEntry entry)
```

**Dispara:** `Selected?.Invoke(entry)` (usado por EggLabPanel para actualizar card UI)

## Métodos Privados

### Update()

Raycast picking:
1. Si no está Mouse.current (editor sin mouse) → return
2. Si no fue presionado botón izquierdo → return
3. Construye ray desde world camera en posición del mouse
4. Physics.Raycast(ray) → si hit
5. Itera entries buscando entry.Root.transform == hit.collider.transform
6. Si encuentra → `Select(entry)` y return

**Notas:** No diferencia entre raycast en huevo vs collider de otro GameObject (asume que solo existen colliders de huevos en eggsRoot y sus hijos)

## Campos Privados

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `entries` | `List<EggLabEntry>` | Lista de huevos generados acumulativos |
| `registry` | `CreatureRegistrySO` | Registro temporal que vive durante la sesión |
| `nextTimestamp` | `long` | Contador secuencial de timestamps (para padres únicos) |

## Cambios S136

**Nuevo script de orquestación:**
- Solo en escena EggLab (laboratorio de demostración)
- No interfiere con gameplay principal
- Patrón MVP: Rebuild() genera datos, events propagan a EggLabPanel/EggLabPortrait

**Interacción mouse en escena 3D:**
- Update raycast permite clicking en mundo 3D
- Desacopla picking de UI (EggLabPanel solo actualiza card, no maneja raycast)

**Generación determinista por timestamp:**
- nextTimestamp secuencial garantiza UniqueIDs únicos
- No usa DateTime.Now (reproducibilidad en debug)

## Notas S136

- No es parte del gameplay principal (escena EggLab aislada)
- Genera pares madre/padre en cada iteración (sin reutilizar genética)
- Progress01 es dummy (Random.value) para UI; no representa progreso real de incubación
- HatchCost es estimado vía odds table (puede variar en implementación real)
- ScriptableObject registry es temporal (creado en Start, destruido en OnDestroy)

## Invariantes

- entries nunca es null (inicializada en campo)
- Entries es read-only al público (no se puede reemplazar lista)
- count * 2 = cantidad de padres creados (2 por huevo)
- Grid centrado horizontalmente, expande hacia atrás (Z negativo)
- Colliders de huevos son CapsuleCollider (no BoxCollider, mejor para esferas)

## Dependencias

- GenerateRandom() → genetics aleatorios validos
- BreedingService.Breed() → puede retornar null (raro, pero manejado)
- CreatureNameBank.GetRandomName() → nombres únicos para UI
- InheritanceOddsTableSO → hatchCost, breeding probabilities
- EggLabAssembler.Build() → visual del huevo
- EggIdleShuffler → animación automática

## Vinculado a

- [[Index/31 - EggLab & Incubadora]]
- [[Resources/Scenes/EggLab.unity]] — escena única donde vive
- [[EggLabEntry]], [[EggLabAssembler]], [[EggIdleShuffler]]
- [[EggLabPanel]], [[EggLabPortrait]] — consumidores de eventos

## Conexiones

**Eventos publicos:**
- `Rebuilt` → EggLabPanel.OnRebuilt()
- `Selected` → EggLabPanel.OnSelected()

**Dependencias:**
- CreatureDatabaseSO, FurTypeDatabaseSO, MonchiVisualBankSO
- InheritanceOddsTableSO, GenerateRandom, BreedingService
- CreatureNameBank, CreatureRegistrySO
- EggLabAssembler, EggIdleShuffler

**Entrada:**
- Mouse input (raycast picking)
- Rearm button (desde EggLabPanel)

**Salida:**
- Lista de EggLabEntry
- Eventos Rebuilt, Selected para UI
