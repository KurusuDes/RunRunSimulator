---
tags: [world, props, puddle, static-registry]
---

# Puddle.cs

**Ruta:** `World/Props/Puddle.cs`

**Responsabilidad:** Charco en el suelo. Se registra en una lista estatica al activarse (`All`) para que `HoseSpray` (tope y separacion) y `MopCleaner` (limpieza) lo encuentren sin `Find`. `Clean()` es idempotente: reproduce `onClean`, desactiva colliders, sale del registro y se destruye a los 0.4 s.

## Metodos Publicos

| Metodo | Descripcion |
|--------|-------------|
| `Clean()` | Limpia una sola vez (flag `cleaned`) |
| `static All` | `IReadOnlyList<Puddle>` |

**Conexiones:** [[HoseSpray]] (instancia y cuenta), [[MopCleaner]] (limpia), `MMF_Player` (`onClean`)
