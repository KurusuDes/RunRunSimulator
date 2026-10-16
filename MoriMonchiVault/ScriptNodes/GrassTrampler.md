---
tags: [script, world, store, grass, trample]
---

# GrassTrampler.cs

**Ruta:** `World/Store/GrassTrampler.cs`

**Responsabilidad:** Marca un objeto que pisa el pasto tienda (MoriMochi, cliente, etc.). Se registra en una lista estática y expone posición, radio y factor de rastro. No dibuja nada: [[ShopTrampleMap]] lee la lista cada frame para estampar el pisado.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `All` | `IReadOnlyList<GrassTrampler>` (static) | Pisadores activos |
| `Position` | `Vector3` | `transform.position` |
| `Radius` | `float` | Radio de pisado (default 0.5) |
| `Trail` | `float` | Multiplicador del rastro (default 1) |

## Campos Serializados

| Campo | Default | Descripción |
|-------|---------|-------------|
| `radius` | 0.5 | Radio de la huella en metros |
| `trail` | 1 | Ganancia del rastro persistente |

## Conexiones

**Salida:** [[ShopTrampleMap]] lee `All` en `CollectStamps`.

## Invariantes

- Se agrega en `OnEnable` y se quita en `OnDisable` (sin leak de la lista estática).
- Sin eventos: la lectura es por lista estática, no por bus.
