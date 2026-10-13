---
tags: [script, world, props, toys, area]
---

# ToyPlayArea.cs

**Ruta:** `World/Props/ToyPlayArea.cs`

**Responsabilidad:** Zona circular de juego de juguetes (radio plano). Define el área donde los juguetes "viven" (`HomeArea`): los monchis pasean y patean dentro de ella y el juguete vuelve ahí si queda fuera. Registro estático `All`.

## Campos serializados

`radius` (≥ 0.5, default 6). Gizmo de círculo cian en selección.

## API pública

| Miembro | Descripción |
|---------|-------------|
| `All` (static) | Zonas activas |
| `Center` | Posición del transform |
| `Contains(p)` | Distancia plana ≤ radio |
| `RandomPoint(margin)` | Punto aleatorio dentro del radio menos el margen |
| `Nearest(p)` (static) | Zona más cercana a un punto |

## Conexiones

- [[Toy]] — `HomeArea` de cada juguete; vuelta a casa tras 25 s fuera
- [[AgentToyMotor]], [[ToyFreePlay]], [[ToyPlayerPlay]], [[ToyBuddyPlay]] — `RandomPoint`, `Contains`, `Center`
