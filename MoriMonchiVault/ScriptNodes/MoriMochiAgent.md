---
tags: [script, world, ai, agent, facade, expedition]
---

# MoriMochiAgent.cs

**Ruta:** `World/AI/MoriMochiAgent.cs`

**Responsabilidad:** Núcleo delgado que orquesta la vida en el mundo. Es `IThrowable` e `IInteractable`. Compone 10 colaboradores internos (`AgentContext`, `AgentBrain`, `AgentPhysics`, `AgentConfinement`, `AgentSenses`, `AgentSocial`, `AgentExpedition`, `AgentClash`, `AgentAbilities`, `AgentToys`) más el componente `Perceivable`. Cada frame elige qué colaborador ticka según `AgentState`. Puede ser Egg, Slime o Adult (`Form` en DNA, visual vía `MonchiVisualizer`). Sin partial class (regla 11).

## Composición (S149)

| Colaborador | Rol |
|-------------|-----|
| `AgentContext` | Estado compartido (sin lógica de transición) |
| `AgentBrain` | FSM NavMesh: necesidades, estaciones, reacción al jugador, petting, HandFeed |
| `AgentPhysics` | Grab, lanzamiento, ragdoll, rebote, recuperación, rejoin NavMesh |
| `AgentConfinement` | Corral de cría y cortejo |
| `AgentSenses` | Percepción (Percepts) |
| `AgentSocial` | Juego social, dormir, pelea entre monchis, `AdjustRoamForAvoidance` |
| `AgentExpedition` | Expedición de arena (recolectar, reportar, huir) |
| `AgentClash` | Choque físico 1v1 (golpes, tell, knock) |
| `AgentAbilities` | Habilidades de arena y buffs de movilidad |
| `AgentToys` **(S149)** | Juguetes: patear pelota, llevar en la boca, robar, quitar al jugador |
| `Perceivable` | Componente: equipo de expedición (`Team`) |

## Ciclo de Update

1. `DevTrackState()` (log y detección de snaps en dev).
2. Si `forceRagdoll` y está NavMesh-controlled, entra a ragdoll.
3. `physics.RecoverIfStuckOffMesh()`.
4. **Huevo:** si `Form == Egg` y no está Thrown, Recovering ni Carried, se frena (`SetStopped(true)`) y no ticka nada más.
5. `brain.TickAlways`, `senses.Tick`, `toys.TickAlways`.
6. `ApplyGaitSpeed(expedition.Carried > 0)`.
7. En Idle, Roaming o Expedition: `abilities.TickMobility()`.
8. Switch por estado:
   - Idle / Roaming: `brain.Tick*`; si sigue ahí, intenta en orden `clash.TryEngage`, `expedition.TryEngage`, `toys.TryEngage` y luego `social.TryEngage`.
   - Playing: `toys.TickPlaying()`.
   - Resto: Reacting, Thrown, Recovering, SeekingNeed, UsingStation, Courting, Socializing, HandFeed, Expedition, Clashing (cada uno a su colaborador).

`FixedUpdate` → `physics.FixedTick()`.

## Propiedades Públicas (Fachada)

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `DNA` | `CreatureDNA` | DNA vivo |
| `Intent` | `CreatureIntent` | Según estado: Clashing, Socializing, Expedition, Playing o brain |
| `Team` | `ExpeditionTeam` | Equipo de arena (vía `Perceivable`) |
| `Occupation` / `Orders` | `Occupation` / `ArenaOrders` | Ocupación y órdenes de arena |
| `IsPenned`, `IsForSale` | bool | En corral; en corral de tienda (`StoreContainer`) |
| `IsCourting`, `IsSocializing`, `IsRecovering` | bool | Estado actual |
| `IsPlayingWithToy` **(S149)** | bool | Estado `Playing` |
| `IsBeingPetted`, `CanBePetted`, `IsInFriendlyReaction` | bool | Desde `AgentBrain` |
| `Velocity`, `IsHeld`, `IsAirborne` | propiedades | Física |
| `Percepts`, `Stats`, `Carried`, `CarryCapacity` | | Expedición y percepción |

## Métodos Públicos Clave

| Método | Descripción |
|--------|-------------|
| `Initialize(CreatureDNA, RoleWorldProfileSO, Transform)` | Primer bind desde el spawner: perfil, jugador, áreas NavMesh, roaming |
| `Rebind(CreatureDNA, RoleWorldProfileSO)` | Cambia DNA y perfil sin reiniciar física |
| `PrepareForPool()` | Libera estación, corral, social y juguetes antes de volver al pool |
| `SetOrders(ArenaOrders)` | Órdenes de arena: fija `Occupation` y refresca stats |
| `Interact()`, `BeginPetting()`, `EndPetting()` | Petting por hold-E |
| `OnGrab(anchor)`, `OnRelease()`, `OnThrow(force)`, `Launch(...)`, `Knock(force)` | Física delegada |
| `ReactToToyHit(Toy, MoriMochiAgent)` **(S149)** | Golpe de juguete: delega a `AgentToys.ReactToHit` |
| `EnterConfinement`, `EnterCourtship`, `ExitCourtship` | Corral y cortejo |
| `SetAbilities(...)`, `RequestAbility(i)` | Habilidades de arena |
| `ForceClash(ClashMoveSO, MoriMochiAgent)` | Fuerza un movimiento de choque (dev) |

## Eventos

**C# events:**
- `OnEmote` (`Action<EmoteKind>`): lo emite cualquier colaborador con `EmitEmote`.

**UnityEvent (Feel-ready, para MMF_Player):**
- `onGrab`, `onThrow`, `onBounce`, `onLand`, `onGetUp`, `onPet`, `onPickup`, `onKnocked`
- `onClashTell`, `onClashHit`, `onDiveLaunch`, `onDiveSlam` (vuelo y picada de alas, S122)

Visuales solo vía MMFeedbacks (regla de juice).

## Suscripciones

`OnEnable` / `OnDisable` suscriben `confinement.OnNavMeshWillRebake` y `OnNavMeshRebaked` a `GameEvents`.

## Tuning (agrupado en el inspector)

- **References:** `nameTag`, `toyTuning` **(S149)** (`ToyTuningSO`).
- **Movement:** `sampleRadius` 4, `repathInterval` 0.35, `followDuration` 10, `reactCooldown` 15, `petRadius` 2.5, `petLookAngle` 20°, `breedingAreaName` ("BreedingRoom"), y los parámetros de cortejo (`courtSpeedMultiplier` 1.7, `courtOrbitRadius`, `courtAngularSpeed`, etc.).
- **Needs (decay por minuto de juego):** `healthDecayPerGameMinute` 0.5, `energyDecayPerGameMinute` 1 (solo al moverse), `affectDecayPerGameMinute` 0.5. Umbrales: `criticalHealth` 25, `criticalEnergy` 25, `criticalAffect` -75.
- **Needs (estrés):** `affectOnThrow` 8, `affectOnHardCollision` 5, `hardImpactThreshold` 4.
- **Needs (caricia):** `petAffectPerSecond` 6, `petRampPerSecond` 0.3, `petMaxDuration` 6, `petEmoteInterval` 1.5.
- **Needs (comer de la mano):** `feedNoticeRadius` 6, `feedDistance` 1.2, `feedShyBelow` 0.35, `feedShyDistance` 3, `feedHesitateSeconds` 2, `feedEatSeconds` 1.5, `feedHungerThreshold` 70, `feedHealthBoost` 35, `feedAffectBoost` 5, `feedCooldown` 20.
- **Physics:** hold, lanzamiento, rebote (`bounciness` 0.55, `maxBounces` 3), knock, recuperación.
- **Dev:** `CurrentState`, `NavStatus`, `forceRagdoll`, `logStateTransitions`, `snapWarnThreshold`.

`Condition` (Healthy, InNeed, Sick) se deriva de las necesidades y los umbrales.

## Cambios S149

- Se suma `AgentToys` como décimo colaborador y el estado `Playing`.
- `Update` ahora pasa por `toys.TickAlways` y `toys.TryEngage` (después de clash y expedición, antes de social).
- Se resetean los juguetes en `RestoreNavMeshControl` y `PrepareForPool`.
- El huevo queda congelado salvo en Thrown, Recovering o Carried.
- Campos de decay renombrados a `*PerGameMinute` con `FormerlySerializedAs` (migración desde `*PerSecond`).

## Cambios S137

MoriMochiAgent es Form-aware:
- **Egg:** incubable en incubadora, no se mueve.
- **Slime:** explorador, puede bajar a arena.
- **Adult:** puede reproducirse en BreedingContainer y bajar a arena.

**Ciclo de vida:** nace Egg (DeliveryBox) → Slime en IncubatorContainer (Minerita) → explora (ExpeditionBridge) → Adult cuando `Explorations >= threshold` → puede criar.

## Vinculado a

- [[Index/02 - Genetics & Breeding]] (ciclo de vida)
- [[Index/09 - Active Context]]
- [[Index/24 - Puente Tienda-Arena]]
- [[Index/22 - Bajada Nocturna y Linaje]]

## Conexiones

- Colaboradores: [[AgentContext]], [[AgentBrain]], [[AgentPhysics]], [[AgentConfinement]], [[AgentSenses]], [[AgentSocial]], [[AgentExpedition]], [[AgentClash]], [[AgentAbilities]], [[AgentToys]]
- [[ClashStrike]], [[MMFeedbacks]]
- [[Toy]], [[ToyTuningSO]] **(S149)**
- [[MonchiVisualizer]] (visual por Form)
- [[IncubatorContainer]] (Egg → Slime)
- [[ExpeditionBridge]] (Slime → Adult)
- [[BreedingContainer]] (solo Adult cría)
- [[StoreContainer]] (corral de venta)
- [[HotbarController]] (comida de la mano, juguete del jugador)
