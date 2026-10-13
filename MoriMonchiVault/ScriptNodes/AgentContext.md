---
tags: [script, world, ai, context, internal]
---

# AgentContext.cs

**Ruta:** `World/AI/AgentContext.cs`

**Responsabilidad:** Contenedor de estado puro compartido entre colaboradores (AgentBrain, AgentPhysics, AgentExpedition, AgentClash, AgentSenses, AgentSocial, AgentConfinement, AgentAbilities, AgentToys). Almacena refs de componentes, DNA/perfil, estado de juego, máscaras NavMesh, percepciones, pizarrón de equipo (S103), órdenes de arena (S104), buffs de velocidad por habilidades (S107), estadísticas operacionales (S109). **S149:** se agrega el estado `Playing` para juguetes. **S151:** la velocidad se reduce si la criatura es frágil. Sin lógica de estado; solo datos y helpers (SetDestinationSafe, IsMoving, PlanarDistance, etc.).

**Enum AgentState (S149):**
Idle, Roaming, Reacting, Carried, Thrown, Recovering, SeekingNeed, UsingStation, Courting, Socializing, HandFeed, Expedition, Clashing, Playing

**Campos Internos:**
- Refs: Owner, Body, Agent, Rb, Col (componentes)
- DNA, Profile (genética + rol)
- Player, HoldAnchor (refs externas)
- CurrentContainer (corral si confinado)
- State (AgentState actual)
- BaseSpeed (velocidad base NavMesh)
- **S107:**
  - `SpeedMultiplier` (float, default 1f) — factor multiplicador de velocidad (ej. 1.35 para boost de habilidad)
  - `SpeedBoostUntil` (float) — timestamp hasta el cual boost está activo. Si Time.time >= SpeedBoostUntil, el multiplicador no aplica
- **S109:**
  - `Stats` (ExpeditionStats) — estadísticas operacionales resueltas (CarryCapacity, LoadedSpeedFactor, KeepCarryOnKnock, GuardRadius, VisibleFrom). Actualizado por AgentAbilities.RefreshStats() en Bind y ResetForReuse; también por MoriMochiAgent.SetOrders()
- Occupation (S104) — ocupación arena derivada de Orders
- ArenaOrders Orders (S104) — órdenes vigentes (Loot/Contact/Posture)
- TeamBlackboard Board (S103) — pizarrón de equipo
- Ocupación/expedición: HomeExit, GuardPost
- Percepción: Percepts (List<Percept>)
- NavMesh: FreeAreaMask, ConfinedAreaMask, RebakeInProgress

**Métodos Públicos:**
- `bool IsNavMeshControlled()` — true si el state es controlado por NavMesh (Idle, Roaming, Reacting, SeekingNeed, UsingStation, Courting, Socializing, Expedition, Clashing, Playing)
- `bool IsBreeding { get; }` — si DNA.BusyState == Breeding
- `bool IsMoving { get; }` — si Agent activo y en movimiento
- `void SetStopped(bool stopped)` — Agent.isStopped
- `void SetDestinationSafe(Vector3 desired)` — SetDestination con sample check
- `void ApplyGaitSpeed(bool loaded)` — aplica factor velocidad según State/Profile + SpeedMultiplier si boost activo + LoadedSpeedFactor si cargado + penalización de fragilidad (S151). **S149:** no se aplica en Courting ni Clashing:
  - factor = Profile.RoamSpeedFactor si Roaming, sino 1f
  - target = BaseSpeed * factor
  - Si loaded: target *= Stats.LoadedSpeedFactor
  - Si Time.time < SpeedBoostUntil: target *= SpeedMultiplier
  - Si `CreatureFrailty.IsFrail(Dna)`: target *= `CreatureFrailty.Penalty` (0.5) (S151)
  - Sets Agent.speed = target
- `void SetColliderTrigger(bool isTrigger)`
- `float PlanarDistanceToPlayer()` — XZ distance al player (`float.MaxValue` si no hay player)
- `static Vector3 RandomPointInBounds(Bounds b)`

**S104 Cambios:**
- Campos `Occupation` y `ArenaOrders Orders` agregados
- Orders inyectado por ArenaCastPlanner vía `arenaCast.Orders`; clampeado por ArenaOrderRules.Clamp(DNA, rules, orders)
- Occupation derivado de Orders vía ArenaOrderRules.ToOccupation()
- Consulta en AgentClash.TryEngage(): Contact fuerza fight si Boldness alto O Posture bloquea Gather
- Consulta en AgentExpedition: ocupación elige colaborador, Orders pasa a loot bias en Gather

**S107 Cambios:**
- Campos `SpeedMultiplier` (default 1f) y `SpeedBoostUntil` (default 0)
- Estos son seteados por AgentAbilities.TickMobility() cuando habilidad Mobility se dispara
- SpeedMultiplier se aplica en ApplyGaitSpeed() si Time.time < SpeedBoostUntil
- Permite buffs de velocidad dinámicos por habilidades (ej. Fleeing → boost 1.35x por 3s)

**S109 Cambios:**
- Campo `Stats` (ExpeditionStats) almacena estadísticas operacionales
- Resuelto en AgentAbilities.RefreshStats() (Bind, ResetForReuse) y MoriMochiAgent.SetOrders()
- ApplyGaitSpeed() firma cambió: `ApplyGaitSpeed(bool loaded)` en lugar de sin parámetros
- Stats se usa en AgentGatherer, ExpeditionNav, Perceivable, PerceivableRegistry para deducir capacidad, radio, visibilidad

**S149 Cambios:**
- `AgentState.Playing` agregado. Lo usa `AgentToys` mientras el monchi juega con un juguete. Cuenta como estado controlado por NavMesh.
- `ApplyGaitSpeed` no cambia la velocidad en Courting ni Clashing.

**S151 Cambios:**
- `ApplyGaitSpeed` aplica `CreatureFrailty.Penalty` (0.5) cuando `CreatureFrailty.IsFrail(Dna)` es true: criaturas con salud en 0 o en etapa Elder van a mitad de velocidad.

**Invariantes:**
- Contenedor puro: sin lógica de transición de estado
- Ref compartida: todos los colaboradores leen/escriben ctx, no hay duplicación
- State autoridad única: solo colaboradores pueden cambiar State
- Board nullable: null si no en expedición
- Orders immutable dentro de expedición (derivado de Orders al inicio; si cambia → reset y re-engage)
- SpeedBoostUntil comparado contra Time.time en ApplyGaitSpeed(); auto-expira tras tiempo
- **Stats resuelto en Bind/SetOrders:** no cambia durante expedición; re-resolver si ocupación/órdenes cambian

**Vinculado a:** [[Index/22 - Arena (S103-S104)]], [[Index/23 - Arena Sandbox & Expedicion (S102-S103)]]

**Conexiones:** [[MoriMochiAgent]], [[AgentBrain]], [[AgentPhysics]], [[AgentExpedition]], [[AgentClash]], [[AgentAbilities]], [[AgentSenses]], [[AgentSocial]], [[AgentConfinement]], [[AgentToys]], [[TeamBlackboard]], [[CreatureDNA]], [[CreatureFrailty]] (S151), [[ArenaOrders]], [[ArenaOrderRules]], [[ExpeditionStats]]
