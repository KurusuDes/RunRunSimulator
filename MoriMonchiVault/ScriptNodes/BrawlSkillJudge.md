---
tags: [script, world, brawl, ai, decision]
---

# BrawlSkillJudge.cs

**Ruta:** `World/Brawl/BrawlSkillJudge.cs`

**Responsabilidad:** Juez singleton de decisiones de habilidades. Dado un slot (cuerno/espalda), retorna si caster quiere usarla y a qué objetivo. Toma en cuenta personalidad (boldness, sociability, osadía, paciencia), familia de habilidad, rango, línea de vista, salud del blanco.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Want(fighter, brain, slot, tuning, out target, out aim)` | Decide si y a dónde; True si quiere |

## Decisión por Familia

- **Mend:** Curación a aliados bajo hp (más agresivo si osado, más protector si sociable)
- **Ward:** Escudo defensivo (más agresivo si bajo hp propio, más protector si aliado bajo)
- **Zone:** Zonas de control (requerimientos de multitud/ubicación)
- **Pull:** Control aglomeración
- **Cone:** Control radial (requerimiento de multitud según boldness)
- **Nova:** Cercano (< 0,8 m)
- **Otros (Shot, Dash, etc.):** Único blanco; filtro por hp/rango

## Umbrales de Personalidad

| Parámetro | Bajo (cauto) | Alto (osado) |
|-----------|--------------|------------|
| **Boldness** | Espera multitud (2+) | Usa en blanco único |
| **Boldness** | Blanco debe ser débil | Cualquier blanco |
| **Boldness** | Espera 2+ s (paciencia) | Usa cuando ready |
| **Sociability** | Elige blanco más débil | Elige más cercano al equipo |

## Búsquedas

- `ReachableFoe()` — rival más cercano en rango
- `BrawlQuery.FoesWithin()` — enemigos en zona
- `BrawlQuery.HasLineOfSight()` — visión despejada
- Buffer reutilizable de búsquedas

## Constantes

| Constante | Valor | Uso |
|-----------|-------|-----|
| `BoldLine` | 0,5 | Umbral boldness (osado vs cauto) |
| `WeakFoeHp` | 0,5 | Enemigo débil (< 50 % vida) |
| `CrowdRadius` | 3 m | Radio aglomeración |
| `BuffThreatRange` | 8 m | Rango amenaza (trigger Ward/Mend) |

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Entrada:**
- [[BrawlBrain]] → `Want()` para cada slot

**Datos:**
- [[BrawlFighter]] → estadísticas (hp, posición)
- [[BrawlSkillSO]] → familia, rango, ángulo
- [[BrawlTuningSO]] → parámetros

**Consultas:**
- [[BrawlQuery]] — búsquedas espaciales

## Notas

- `Impatient()` en Brain: si ready > tuning.PatienceSeconds, ignora boldness lower bound
- LineOfSight solo para habilidades rectas (Shot, Dash)
- Multitud calculada antes de decidir (optimización)
