---
tags: [script, world, brawl, match, game]
---

# BrawlMatch.cs

**Ruta:** `World/Brawl/BrawlMatch.cs`

**Responsabilidad:** Orquestación de partida 3v3. Generación de rosters (6 MoriMonchis aleatorios, sin wing repetido por equipo). Fases (Setup, Countdown, Fight, SuddenDeath, Results). Evento de Last Stand (1 vs ≥2). Rampa de daño por KO. Auto-restart. Seed aleatorio o configurable.

## Fases de Partida

| Fase | Duración | Evento |
|------|----------|--------|
| Setup | Instantánea | Spawn fighters |
| Countdown | 3 s | Countdown visual |
| Fight | 90 s | Combate normal |
| SuddenDeath | 10 s+ | Drenaje de vida (2% + 1%/s) |
| Results | 6 s | Cartel con MVP |

## Last Stand

Se activa cuando:
- Un equipo baja a 1 miembro vivo
- Equipo rival tiene ≥2 miembros vivos

Efectos (5 s):
- +25 % escudo de vida máxima
- +30 % daño
- +20 % velocidad
- Recarga habilidades
- Deja de huir (Motor.Rooted = false)

## Rampa de Daño

`DamageRamp = 1 + (tuning.KoDamageRamp × KnockOuts)`

- Cada KO suma +15 % daño a todos (acumula en `RoundDamageFactor`)
- Mostrado en HUD bajo reloj

## Muerte Súbita

Drenaje por segundo:
- Base: 2% vida máxima/s
- Escala: +1%/s por segundo transcurrido
- Curación reducida ×0,5

Termina cuando queda 1 combatiente.

## Eventos Estáticos

| Evento | Parámetros | Cuándo |
|--------|-----------|--------|
| `OnPhaseChanged` | `phase` | Cambio de fase |
| `OnMatchEnded` | `winner` (Player/Rival) | Victoria |
| `OnRosterSpawned` | `fighters` | Spawning inicial |
| `OnLastStand` | `survivor` | Último en pie activado |

## Generación de Roster

- `CreatureGenerator.Generate()` × 6 con seed
- Filtro: sin wing repetido por equipo (hasta 12 rerolls)
- Spawn aleatorio en radius 2,5 m
- Paleta por seed con `ArenaLayoutBuilder` + `ArenaPaletteApplier`

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]

## Conexiones

**Componentes escena:**
- [[ArenaLayoutBuilder]] — layout
- [[ArenaPaletteApplier]] — paleta visual
- [[BrawlFighter]] — prefab spawn
- [[BrawlTuningSO]] — parámetros

**Datos:**
- [[CreatureDatabaseSO]], [[BrawlKitDatabaseSO]] — assets
- [[MonchiVisualBankSO]], [[FurTypeDatabaseSO]] — visuals

**Suscriptores:**
- [[BrawlCamera]], [[BrawlAnimator]], [[BrawlHud]] → eventos

## Notas

- `Current` singleton (acceso vía BrawlMatch.Current)
- Seed aleatorio cada Play si randomizeEachPlay
- Prefab fighter derivado de MoriMochiAgent
- Sin persistencia; todo en memoria
