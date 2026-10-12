---
tags: [world, props, hose, water, puddle]
---

# HoseSpray.cs

**Ruta:** `World/Props/HoseSpray.cs`

**Responsabilidad:** Manguera. Mientras un MoriMochi la lleva (`Toy.Holder != null`), deja charcos (`Puddle`) cada `spacing` metros recorridos en planta. Ademas rellena las estaciones de agua (`StationSupply` tipo Water) que estan a `refillRadius`.

## Reglas

| Parametro | Default | Descripcion |
|-----------|---------|-------------|
| `spacing` | 1.2 | Distancia planar entre charcos |
| `minGap` | 0.8 | Distancia minima a un charco existente |
| `maxPuddles` | 25 | Tope de charcos vivos (`Puddle.All`) |
| `groundMask` | todas | Raycast hacia abajo, 3 m |
| `refillRadius` | 1.5 | Radio de recarga de agua |
| `refillPerSecond` | 25 | Puntos de agua por segundo |

## Flujo

1. `Update`: si `toy.Holder == null`, deja de rastrear.
2. Recarga agua cercana cada frame.
3. Acumula distancia planar; al superar `spacing`, `TrySpawn`.
4. `TrySpawn`: respeta el tope y `minGap`, raycast al suelo e `Instantiate(puddlePrefab)`.

**Conexiones:** [[Toy]] (requerido), [[Puddle]], [[StationSupply]], [[MoriMochiAgent]] (indirecto, via `Toy.Holder`), [[WorldPropInstance]]
