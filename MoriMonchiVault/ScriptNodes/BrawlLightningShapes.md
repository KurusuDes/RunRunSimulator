---
tags: [script, world, brawl, vfx, presentation, helper]
---

# BrawlLightningShapes.cs

**Ruta:** `World/Brawl/BrawlLightningShapes.cs`

**Responsabilidad:** Clase estática pura. Constructor procedural de ramificaciones para rayos de tormenta. `BuildBranch(main[], branch[])` elige un punto aleatorio del rayo principal, genera dirección aleatoria con caída garantizada (Y negativa), e interpola 4 puntos Bezier lineales con jitter. Usado por `BrawlLightningBranches` para ramificar tormenta.

**Método público:**
- `BuildBranch(Vector3[] main, Vector3[] branch)` — itera los 4 puntos de la rama, los fija en el array dest

**Constantes:**
- `BranchPoints = 4` — puntos de la rama
- `BranchMinLength/MaxLength = 0.6-1.2` — longitud rama
- `BranchJitter = 0.1` — ruido esférico en cada punto
- `BranchMinDrop = 0.3` — Y negativa mínima para caída

**Notas:**
- Selecciona punto de inicio en `main[1..n-2]` para evitar extremos
- Dirección aleatoria en esfera, luego Y se reemplaza con -Random(0.3, 1.0) para caída
- Paso es inversamente proporcional a cantidad de puntos
- Jitter isótropo en los puntos internos (evita colineales)

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlLightningBranches]], [[BrawlLineFx]]
