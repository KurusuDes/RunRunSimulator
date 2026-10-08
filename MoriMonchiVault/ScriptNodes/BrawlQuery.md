---
tags: [script, world, brawl, queries, spatial]
---

# BrawlQuery.cs

**Ruta:** `World/Brawl/BrawlQuery.cs`

**Responsabilidad:** Singleton de búsquedas espaciales sobre `BrawlFighter.All`. Sin allocación de listas (reutiliza buffer). Distancia planar XZ (ignorando Y). Búsquedas: enemigos/aliados en radio, cercano, más débil.

## Métodos Estáticos

| Método | Descripción |
|--------|-------------|
| `AreFoes(a, b)` | Son rivales (teams diferentes) |
| `Planar(a, b)` | Distancia XZ |
| `NearestFoe(self, maxDist)` | Enemigo más cercano |
| `NearestFoeTo(point, team, maxDist, exclude)` | Enemigo más cercano a punto |
| `LowestAlly(self, maxDist, includeSelf, below01)` | Aliado con mínima vida |
| `FoesWithin(center, radius, team, into)` | Enemigos en radio; populate buffer |
| `AlliesWithin(center, radius, team, into)` | Aliados en radio |
| `InCone(origin, dir, range, halfAngle, target)` | Target dentro de cono |
| `OnSegment(start, end, radius, target)` | Target sobre segmento |
| `HasLineOfSight(from, to)` | Raycast sin obstáculos |

## Filtros

- **IsAlive:** Solo vivos
- **Team:** Rivales o aliados según búsqueda
- **Distancia:** Planar XZ (ignorando Y)
- **Radio:** Incluye body radius del target

## Búsquedas Comunes

### Enemigos en radio
```
BrawlQuery.FoesWithin(center, radius, team, buffer);
// buffer poblado; count retornado
```

### Cono (Cone skill)
```
BrawlQuery.InCone(origin, direction, range, halfAngle, candidate)
// True si dentro del sector
```

### Segmento (Whip)
```
BrawlQuery.OnSegment(start, end, radius, target)
// True si target cercano a línea
```

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Datos:**
- [[BrawlFighter]].All — lista global de combatientes

**Usuarios:**
- [[BrawlBrain]] — target selection
- [[BrawlWing]] — búsqueda golpe melé/latigazo
- [[BrawlSkillOffense]], [[BrawlSkillSupport]] — búsqueda targets
- [[BrawlSkillJudge]] — evaluación de decisiones

## Notas

- Planar() optimizado (no sqrt si solo comparar distancias)
- Buffer reutilizable (evita GC)
- Raycast solo en HasLineOfSight (caro; opcional)
- Cono half-angle en radianes o grados según contexto (verificar usuario)
