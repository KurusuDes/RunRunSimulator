---
tags: [script, world, ai, toys, player, internal]
---

# ToyPlayerPlay.cs

**Ruta:** `World/AI/ToyPlayerPlay.cs`

**Responsabilidad:** Comportamiento de juego entre el MoriMochi y el jugador. Cuatro juegos: recoger un juguete que el jugador lanzó y devolvérselo (`FetchGo` → `FetchReturn`), tirar de un juguete que el jugador sostiene con `PlayerToyTug` (`TugApproach` → `Tugging`), arrebatarle el juguete de la mano, y pasearse con él fuera de su alcance (`Tease`). Clase `internal` que implementa `IToyBehavior`.

## Modos (`PlayMode`)

`None`, `FetchGo`, `FetchReturn`, `TugApproach`, `Tugging`, `Tease`.

## Flujos

- **Fetch**: `FindThrown` busca un juguete lanzado por el jugador (`ThrownByPlayer`, libre, no burbuja). Al llegar, lo adjunta a la boca (`TryAttach` con `true`), vuelve al jugador y lo suelta a sus pies. Suma `FetchAffect`.
- **Tirón**: juguete transportable en la mano del jugador a `NoticeRadius`. Al llegar a `TugRange` llama `PlayerToyTug.Instance.TryBegin(owner, TugPullPerSecond + TugBoldnessPull * boldness)`. Según el resultado: `PlayerWon` suma `TugWinAffect` y termina; `CreatureWon` suelta el juguete del jugador y pasa a `Tease`.
- **Arrebato**: si está en `TugRange` y el tirón no está disponible, con prob. `SnatchChancePerSecond` * dt le quita el juguete activo del hotbar (`DropActive`) y entra en `Tease`.
- **Tease**: se aleja del jugador (`TeaseKeepAway`) durante `TeaseDuration`; si el jugador lo agarra suma `CaughtAffect`; si lo deja, lo suelta frente al jugador.

## Conexiones

- [[IToyBehavior]] — implementa
- [[AgentToyMotor]] — motor compartido
- [[AgentToys]] — orquestador
- [[ToyTuningSO]] — `TugPullPerSecond`, `TugBoldnessPull`, `TugWinAffect`, `TeaseSpeedMultiplier`, `TeaseDuration`, `TeaseKeepAway`, `FetchDropRange`, `FetchAffect`, `CaughtAffect`
- [[PlayerToyTug]] — `Instance`, `TryBegin`, `Release`, `State`, `Puller`
- [[HotbarController]] — `ActiveHeldObject`, `DropActive`
- [[Toy]] — `ThrownByPlayer`, `IsHeldByPlayer`, `TryAttach`, `Kind`
