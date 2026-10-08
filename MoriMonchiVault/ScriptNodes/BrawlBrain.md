---
tags: [script, world, brawl, ai, brain]
---

# BrawlBrain.cs

**Ruta:** `World/Brawl/BrawlBrain.cs`

**Responsabilidad:** IA autónoma. Personalidad (boldness, sociability) del DNA. Intención (Idle, Engage, Retreat, Cast, Heal). Think cada 0,2 s. Elige blanco, postura, habilidades a usar. Cohesión con aliados. Retirada cuando dañado bajo umbral.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Target` | `BrawlFighter` | Enemigo elegido |
| `Intent` | `BrawlIntent` | Estado decisión (Idle, Engage, Retreat, Cast, Heal) |
| `PostureLabel` | string | "Osado · protector" etc. |
| `Boldness` | float | 0-1; osadía del DNA |
| `Sociability` | float | 0-1; socialidad del DNA |

## Método Think

Cada 0,2 s:
1. Selecciona blanco (enemy más cercano / amenazador)
2. Decide postura (lejano = strafe, melé = acercarse)
3. Intenta habilidades (cuerno, espalda) según juez
4. Retreat si dañado bajo umbral (50 % → 15 % según boldness)

## Comportamientos

### Engage (Ataque)
- Blanco vivo y cercano
- Acercamiento directo o strafe (si rango)
- Intenta ataque básico + habilidades

### Retreat (Retirada)
- Dañado bajo hp umbral (HP01 < 0,15-0,5)
- Se aleja del blanco
- Mantiene distancia hasta recuperarse

### Heal (Curación)
- Busca aliado bajo vida
- Intenta habilidades de soporte
- Protege aliado más débil

### Idle (Espera)
- Sin blanco vivo
- Movimiento pausado

## Strafe (Esgrima)

- Lado aleatorio ±meleeStrafeScale (40 %)
- Cambia dirección cada 0.5-1 s
- Acercamiento circular alrededor de blanco

## Cohesión

- Si `Sociability` alta: atrae a centroide del equipo
- Si baja: caza independiente
- Umbral postura 0,65 (osado) / 0,35 (cauto)

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Dueño:**
- [[BrawlFighter]] — propietario

**Entrada:**
- [[BrawlFighter]] — DNA para personalidad

**Salida:**
- [[BrawlMotor]] → `MoveTo()`
- [[BrawlWing]] → `TryAttack()`, `TryMobility()`
- [[BrawlSkillCaster]] → `TryCast()`
- [[BrawlSkillJudge]] → `Want()` para decisiones

**Consultas:**
- [[BrawlQuery]] — búsquedas

## Notas

- thinkInterval 0,2 s por defecto (configurable)
- PostureLabel se forma en Init según boldness/sociability
- closeRange 2,6 m (distancia de cuerpo a cuerpo)
- RetreatDistance 6 m; RetreatFoeRange 6 m
- Solo piensa si vivo, no congelado, no forzado
