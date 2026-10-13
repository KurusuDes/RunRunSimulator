---
tags: [script, world, ai, toys, interface, internal]
---

# IToyBehavior.cs

**Ruta:** `World/AI/IToyBehavior.cs`

**Responsabilidad:** Contrato interno de un comportamiento de juego con juguetes. Cada comportamiento es una máquina de estados propia que `AgentToys` consulta y ticka. Sin lógica.

## Miembros

| Miembro | Descripción |
|---------|-------------|
| `bool IsActive` | Si el comportamiento está en un modo distinto de None |
| `CreatureIntent Intent` | Intención que expone al resto de la IA (Wandering / Approaching / Playing) |
| `bool TryEngage(ToyTuningSO t)` | Intenta arrancar; devuelve si lo logró |
| `void Tick(ToyTuningSO t, float dt)` | Avanza el estado |
| `bool ReactToHit(Toy hitToy, MoriMochiAgent kicker)` | Reacción a un pelotazo/golpe de otro monchi |
| `void Clear()` | Corta el comportamiento y suelta lo que tenga |

## Implementaciones

- [[ToyFreePlay]] — pelota, cargar juguetes libres, robar a otro monchi
- [[ToyBuddyPlay]] — jugar con otro monchi (cuerda, peluche, abrazo, burbujas)
- [[ToyPlayerPlay]] — jugar con el jugador (lanzamientos, tirón, tease)

## Conexiones

- [[AgentToys]] — orquesta las implementaciones
- [[AgentToyMotor]] — motor compartido que usan las implementaciones
- [[CreatureIntent]] — enum de intención
