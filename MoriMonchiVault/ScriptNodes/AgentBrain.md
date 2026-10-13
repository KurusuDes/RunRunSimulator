---
tags: [script, world, agent, internal, brain, fsm]
---

# AgentBrain.cs

**Ruta:** `World/AI/AgentBrain.cs`

**Responsabilidad:** Orquestación de la máquina de estados NavMesh del MoriMochiAgent (comportamiento autónomo). Decae y recupera necesidades según el tiempo de juego, busca y usa estaciones de necesidad, reacciona al jugador (seguir, acercarse, huir, retirarse), gestiona la mecánica de caricia (petting) y de dar comida con la mano (HandFeed). Expone `Intent`. Es colaborador interno (`internal`) de `MoriMochiAgent`, no componente. Compone con `AgentContext`.

## Propiedades Consultables

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `IsBeingPetted` | bool | True mientras `pettingDisplayTimer > 0` (1.5 s tras una sesión, 0.3 s mientras dura) |
| `IsInFriendlyReaction` | bool | En Reacting y la reacción no es Flee |
| `CanBePetted` | bool | Reacting + reacción no Flee + el jugador mira al monchi (`IsPlayerFacingMe`) |
| `Intent` | `CreatureIntent` | Mapeo de estado a intención (Held, Tumbling, SeekingFood, Eating, Resting, Playing, Following, Fleeing, etc.) |

## Necesidades (decay y recuperación)

Los valores viven en `MoriMochiAgent` (`healthDecayPerGameMinute`, `energyDecayPerGameMinute`, `affectDecayPerGameMinute`, `affectRestValue`, `affectRecoveryPerGameMinute`, `energyRestPerGameMinute`, `energyRestCap`). `AgentBrain.TickNeeds(dt)` los aplica cada frame:

```
scaledDt = dt * GameClock.NeedsTimeScale   (1 en juego normal; 0 si pausa o no cargado)
Health  -= healthDecayPerGameMinute * scaledDt                 siempre
Affect  -> tiende hacia affectRestValue:
           si está arriba, baja hasta affectRestValue (decay)
           si está abajo, sube hasta affectRestValue (recovery)
Energy  -= energyDecayPerGameMinute * scaledDt                 solo si ctx.IsMoving
Energy  += energyRestPerGameMinute * scaledDt                  si está quieto y Energy < energyRestCap (sin pasar el cap)
```

Energía baja al moverse y se recupera en reposo hasta `energyRestCap`. Salud baja siempre. Afecto tiende al valor de reposo `affectRestValue`.

## Estados (FSM)

| Método | Descripción |
|--------|-------------|
| `TickIdle()` | Intenta buscar necesidad, dar comida o reaccionar al jugador. Si no, cuenta el tiempo y vuelve a roaming |
| `TickRoaming()` | Igual que Idle, y al llegar al destino tira entre quedarse en Idle (`IdleChance`) o seguir roaming |
| `TickReacting()` | Si hay petting, `TickPetting`. Si no: sale si la necesidad es crítica o si expira el tiempo de reacción; repath hacia el jugador según la reacción |
| `TickSeekingNeed()` | Avanza a la estación reservada; al llegar pasa a UsingStation |
| `TickUsingStation()` | `NeedStation.Refill` hasta llenar; luego roaming |
| `TickHandFeed()` | Se acerca al jugador, duda (si es tímido por `Sociability`), come y consume el alimento activo del hotbar |
| `TickAlways(dt)` | Decae/recupera necesidades y reduce timers (reacción, petting, feed) |

## Necesidad crítica

`TryGetCriticalNeed` compara Health, Energy y Affect con `criticalHealth`, `criticalEnergy` y `criticalAffect`. `TryEnterNeedSeeking` reserva la estación más cercana (`NeedStationRegistry.GetClosest`). Si no hay estación de ese tipo, emite emote Molesto cada 20 s y resta 5 de afecto.

## Dar comida con la mano (HandFeed)

Se activa si: el hotbar ofrece comida (`IsOfferingFood`), la salud está por debajo de `feedHungerThreshold`, el jugador está dentro de `feedNoticeRadius` y no hay cooldown.

- Si `Sociability >= feedShyBelow` el monchi duda `feedHesitateSeconds` antes de acercarse.
- Come durante `feedEatSeconds`, luego `TryConsumeActiveFood` suma `feedHealthBoost` a salud y `feedAffectBoost` a afecto.
- Cooldown `feedCooldown`; si el jugador se aleja, 5 s de cooldown.

## Reacción al jugador

`ReactIfPlayerNear` (dentro de `ProximityRadius`, sin cooldown): si el afecto es crítico, huye (Flee). Si no está sano o su perfil es Ignore, no reacciona. Si no, usa la reacción de su perfil (Approach, Follow, Retreat). Dentro de un corral no se acerca ni sigue.

## Petting

- `BeginPetSession()`: solo si `CanBePetted` y no hay sesión en curso. Frena al monchi.
- `TickPetting`: añade afecto (`petAffectPerSecond`, con rampa `petRampPerSecond`), gira hacia el jugador, emite corazones cada `petEmoteInterval`. Termina si expira `petMaxDuration`, si el jugador deja de mirar o si suelta E.
- `EndPetSession()`: pone cooldown de reacción, activa `pettingDisplayTimer` (1.5 s), dispara `onPet` y vuelve a roaming.
- `Interact()` llama `BeginPetSession()`.

## Métodos Públicos / Internos

| Método | Descripción |
|--------|-------------|
| `BeginPetSession()` | Entra en petting (bool) |
| `EndPetSession()` | Cancela petting |
| `ReleaseStation()` | Libera la reserva de estación |
| `EnterRoaming()` | Transición a roaming (no toca `Agent.speed`) |
| `IsPlayerFacingMe()` | Distancia `petRadius` y ángulo `petLookAngle` respecto a la mirada del jugador |
| `ResetForReuse()` | Limpia timers y banderas para pool |

## Cambios S151

- Recuperación de energía en reposo hasta `energyRestCap` (sin cama).
- Afecto con valor de reposo `affectRestValue`: baja si está arriba y sube si está abajo, sin pasarse.

## Cambios S149

- El decaimiento vive ahora en `MoriMochiAgent` (campos públicos) y `AgentBrain` solo lo aplica.
- Energía baja solo al moverse (`ctx.IsMoving`).
- `AgentState.Playing` es un estado navmesh (ver `AgentContext`); `AgentToys` lo usa para juguetes.

## Vinculado a

- [[Index/23 - Arena Sandbox & Expedicion (S102-S103)]]
- [[Index/09 - Active Context]]

## Conexiones

**Data:**
- [[CreatureDNA]] — necesidades mutables
- [[CreatureIntent]] — mapeo de estado
- [[RoleWorldProfile]] — perfil de reacción, radios y tasas

**Sistemas:**
- [[MoriMochiAgent]] — componente padre (decay, emotes, reacciones)
- [[AgentContext]] — estado compartido
- [[AgentToys]] — estado Playing
- [[GameClock]] — `NeedsTimeScale`
- [[NeedStation]], [[NeedStationRegistry]] — reserva y consumo
- [[HotbarController]] — `IsOfferingFood`, `TryConsumeActiveFood`
- [[AgentExpedition]] — estado de expedición

## Notas (S131 HC-4 + S149)

- **NeedsTimeScale:** 0 cuando GameClock no está cargado o en pausa; 1 en juego normal.
- **Clamp:** las necesidades se limitan a [0, 1] en `Needs`.
- **Game minutes:** `dt * NeedsTimeScale` convierte segundos reales a minutos de juego.
