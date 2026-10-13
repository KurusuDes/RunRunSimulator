---
tags: [script, world, ai, toys, internal]
---

# ToyFreePlay.cs

**Ruta:** `World/AI/ToyFreePlay.cs`

**Responsabilidad:** Comportamiento de juego "libre" de un MoriMochi con juguetes sueltos en el mundo: patea pelotas (`Kicking`), lleva juguetes transportables a donde quiera (`Carrying`), y persigue a otro monchi o al que le acaba de pegar un pelotazo para robarle su juguete (`Chasing`). Clase `internal` que implementa `IToyBehavior`.

## Modos (`ToyMode`)

`None`, `GoToBall`, `Kicking`, `GoToCarry`, `Carrying`, `Chasing`.

## Reglas

- `TryEngage`: prioriza robar (juguete transportable en manos de otro, dentro de `NoticeRadius`); si no, toma el juguete libre más cercano (pelota → patear, otro transportable → cargar).
- Pelota: `KicksMin..KicksMax` patadas con dispersión `KickNoiseDegrees` 25°; si la pelota está fuera de su `HomeArea`, la patea de vuelta al centro.
- Cargando: si otro monchi la tiene en la boca y tira, la pausa; si pierde el juguete, emote molesto y persigue al ladrón.
- Persecución: roba con `StealChance` al llegar a `StealRange`; si no hay juguete, emote molesto y termina.
- `ReactToHit`: si está libre (sin juguete, puede jugar, estado Idle/Roaming/Playing), acepta persecución del kicker.

## Notas de código

- `TickSnatching` existe pero no tiene caso en `Tick` (código muerto; el arrebato al jugador vive en `ToyPlayerPlay`).
- `TickCarrying` usa el literal `0.3f` para el margen de llegada en vez de una constante.

## Conexiones

- [[IToyBehavior]] — implementa
- [[AgentToyMotor]] — motor compartido
- [[AgentToys]] — orquestador
- [[ToyTuningSO]] — `KickRange`, `KickForce`, `KickUp`, `KicksMin/Max`, `ChaseDuration`, `StealRange`, `StealChance`, `CarryDuration*`
- [[Toy]] — `IsKickable`, `IsCarriable`, `Kick`, `Holder`, `TuggedBy`, `HomeArea`
- [[SocialGraphService]] — registra `PlayChase` al robar
- [[CreatureIntent]] — intención expuesta
