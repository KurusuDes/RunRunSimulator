---
tags: [script, world, ai, toys, motor, internal]
---

# AgentToyMotor.cs

**Ruta:** `World/AI/AgentToyMotor.cs`

**Responsabilidad:** Motor compartido de juego de juguetes de un `MoriMochiAgent`. Lo usan los tres comportamientos (`ToyFreePlay`, `ToyBuddyPlay`, `ToyPlayerPlay`) para: validar si la criatura puede jugar, aplicar/refrescar/limpiar el boost de velocidad, controlar el repath, arrancar cooldown, cargar juguetes en la boca (`ToyMouth`) y buscar juguetes libres cercanos. Clase `internal`, sin eventos propios.

## Reglas de elegibilidad (`CanPlay`)

No juega si: no hay `Dna`, está en un contenedor (`CurrentContainer`), está en cría (`IsBreeding`), es Egg, o pertenece a un equipo de expedición (`Team != None`).

## Métodos clave

| Método | Descripción |
|--------|-------------|
| `Enter()` | Estado `Playing`, desbloquea agente |
| `SetBoost` / `RefreshBoost` / `ClearBoost` | Multiplicador de velocidad con ventana `BoostRefresh` (0.25 s) |
| `Repath(dt)` | Temporizador de recálculo usando `owner.repathInterval` |
| `StartCooldown()` / `CooldownReady` | Cooldown desde `ToyTuningSO.Cooldown` |
| `Finish(completed)` | Emote feliz si completó, limpia boost, cooldown y pide `RequestRoam` |
| `TryCarry(toy, emote, t)` | Adjunta el juguete a la boca (`ToyMouth`), boost de carga, punto de paseo |
| `Drop(toy, velocity)` | Suelta si la criatura es el holder |
| `PickWanderPoint(toy, t)` | Punto dentro del `HomeArea` del juguete o círculo `WanderRadius` |
| `HeldToyOfPlayer()` | Juguete en la mano del jugador (vía `HotbarController`) |
| `NearestFreeCarriable(around, radius)` | Juguete transportable libre más cercano |

## Conexiones

- [[AgentToys]] — dueño que crea los comportamientos
- [[AgentContext]] — estado compartido (`Dna`, `Agent`, `Body`, `State`, `SpeedBoostUntil`)
- [[MoriMochiAgent]] — `toyTuning`, `repathInterval`, `Team`, `EmitEmote`, `RequestRoam`
- [[ToyTuningSO]] — números
- [[Toy]] — `TryAttach`, `Detach`, `Holder`, `HomeArea`, `Toy.All`
- [[ToyPlayArea]] — `RandomPoint`
- [[HotbarController]] — mano del jugador
- [[ToyFreePlay]], [[ToyBuddyPlay]], [[ToyPlayerPlay]] — consumidores
