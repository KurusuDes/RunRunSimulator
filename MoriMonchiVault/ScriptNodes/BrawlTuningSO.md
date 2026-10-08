---
tags: [script, data, so]
---

# BrawlTuningSO.cs

**Ruta:** `Data/Brawl/BrawlTuningSO.cs`

**Responsabilidad:** Hub de tuneos globales de Brawl 3v3: vida base, contador, fases, último en pie, rampa KO, muerte súbita, personalidad (osadía/sociabilidad), colores de equipo. Un asset único (`BrawlTuning.asset`) editado en inspector.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

## Nested Struct: BodyStat

```csharp
public struct BodyStat
{
    public string BodyId;      // Identificador del cuerpo (ej. "BS0", "BS1")
    public string Label;       // Etiqueta legible (ej. "Equilibrado")
    public float HpMul;        // Multiplicador de vida (ej. 1.0, 1.15)
    public float SpeedMul;     // Multiplicador de velocidad (ej. 1.0, 0.93)
}
```

## Campos Principales

| Sección | Campo | Tipo | Descripción |
|---------|-------|------|-------------|
| **Cuerpos** | `BaseHp` | float | Vida base (antes de BodyStat.HpMul) |
| | `Bodies` | List<BodyStat> | Tabla de stats por cuerpo |
| **Partida** | `CountdownSeconds` | float | Duración cuenta regresiva antes de pelea |
| | `RoundSeconds` | float | Duración ronda (90s) |
| | `EndHoldSeconds` | float | Pausa tras finalizar antes de nuevo match |
| **Último en pie** | `LastStandShield` | float | % escudo cuando queda 1 vs 2+ (0,25 = 25%) |
| | `LastStandBoost` | float | % daño bonus (0,3 = +30%) |
| | `LastStandHaste` | float | % velocidad bonus (0,2 = +20%) |
| | `LastStandSeconds` | float | Duración del buff |
| **Ritmo** | `KoDamageRamp` | float | % daño bonus por cada KO previo (0,15 = +15%/KO) |
| **Muerte súbita** | `SuddenDeathStart` | float | % vida/s drenada al iniciar (0,02 = 2%) |
| | `SuddenDeathRamp` | float | % vida/s adicional por segundo transcurrido (0,01 = +1%/s) |
| | `SuddenDeathHealFactor` | float | Factor de curación en muerte súbita (0,5 = ×0,5) |
| **Equipos** | `AllyColor` | Color | Color del equipo Player (azul) |
| | `FoeColor` | Color | Color del equipo Rival (rojo) |
| **Personalidad** | `RetreatHp` | Vector2 | Rango de vida para retirada: (x=osado bajo, y=cauto alto) |
| | `PreferredRange` | Vector2 | Rango preferido: (x=osado cerca, y=cauto lejos) |
| | `HealThreshold` | Vector2 | Threshold para curación: (x=osado alto, y=cauto bajo) |
| | `StrafeAngle` | float | Ángulo de strafe mientras ataca (30°) |
| | `StrafeFlipSeconds` | Vector2 | Rango de cambio de dirección strafe (1,2s a 2,6s) |
| | `PatienceSeconds` | float | Segundos en espera antes de usar habilidad sin buen momento |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `BodyFor(string bodyId)` | Busca BodyStat por ID; retorna fallback (HpMul=1, SpeedMul=1) si no encontrado |
| `TeamColor(ExpeditionTeam team)` | Retorna color del equipo (Player=AllyColor, Rival=FoeColor, default=White) |

## Referencia: Valores Default S142

**Vida y cuerpos (BaseHp 14000):**
- BS0 (Equilibrado): HpMul=1,0, SpeedMul=1,0 → 14000 HP, vel normal
- BS1 (Robusto): HpMul=1,15, SpeedMul=0,93 → 16100 HP, vel -7%
- BS2 (Ágil): HpMul=0,9, SpeedMul=1,08 → 12600 HP, vel +8%
- BS3 (Pesado): HpMul=1,25, SpeedMul=0,88 → 17500 HP, vel -12%

**Partida:**
- Countdown: 3s, Round: 90s, End: 6s

**Último en pie (activa a 1 vs 2+):**
- Shield: 25% de vida máx, Boost: +30% daño, Haste: +20% velocidad, Duración: 5s

**Ritmo:** +15% daño por KO

**Muerte súbita (90s):**
- Inicia: 2% vida/s, Rampa: +1% vida/s por segundo, Curación: ×0,5

**Personalidad (X=osadía 0, Y=sociabilidad 1):**
- Retirada: 50% (osado) → 15% (cauto)
- Rango: 90% (osado cerca) → 55% (cauto lejos)
- Curación: 55% (osado tarda) → 85% (cauto cura antes)
- Strafe: 30°, Flip: 1,2s a 2,6s, Paciencia: 6s

## Dependencias

**Entrada:**
- Vinculado en inspector en `BrawlMatch`, `BrawlHudCard`, `BrawlOverheads`

**Salida:**
- `BrawlFighter.MaxHp` (calcula BaseHp × BodyStat.HpMul)
- `BrawlFighter.MoveSpeed` (BrawlWingKitSO.MoveSpeed × BodyStat.SpeedMul)
- `BrawlMatch.LastStand` (activa buff)
- `BrawlMatch.DamageRamp` (multiplier)
- `BrawlBrain.Intent`, `Range`, `RetreatHp` (decisiones de IA)
- `BrawlHudCard.Refresh()` (color de equipo)
- UI team colors (HUD, overhead plates)

## Notas S142

- Todos los valores editables en inspector
- No hay cambios en runtime (solo lectura)
- Vector2 se usa para rangos osadía (x) vs sociabilidad (y)
- BodyStat sirve para balanceo por forma corporal (los 4 BS de la tienda)
- Valores defaults se fijaron tras ~12 partidas automáticas de medición (S142 medido)
