---
tags: [script, world, brawl, development, balance, testing]
---

# BrawlBalanceDev.cs

**Ruta:** `World/Brawl/BrawlBalanceDev.cs`

**Responsabilidad:** Arnés de desarrollo para ejecutar tandas automatizadas de partidas Brawl 3v3. Itera por semillas, ejecuta cada una con opción de espejo (swap de equipos), captura rosters para comparación, ajusta velocidad de simulación a tasa fija (Hz), volcándolas a CSV mediante `BrawlBalanceRecorder`. Mide velocidad de simulación (sim/real).

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `IsRunning` | bool | Tanda activa |
| `Done` | bool | Tanda completada (no falló) |
| `Completed` | int | Partidas procesadas |
| `Total` | int | Partidas totales (seedCount × 1 ó 2 con espejo) |
| `Folder` | string | Ruta absoluta de salida (`Recordings/brawl_balance/<batch>/`) |
| `Progress` | string | Línea de progreso para archivo `progress.txt` |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Run(batch, firstSeed, seedCount, mirror, simHz, camerasOff)` | Inicia tanda de `seedCount` semillas, opcionalmente con espejo; semilla inicial `firstSeed`; `simHz` es Time.captureDeltaTime (50 Hz por defecto); desactiva cámaras si `camerasOff` |
| `Stop()` | Para tanda actual (actúa en siguiente `null` yield) |

## Flujo de Ejecución

1. **Inicialización**: crea directorio `Folder`, escribe headers CSV de matches y fighters.
2. **Ajuste de tiempo**: `Time.captureDeltaTime = 1/simHz`, `runInBackground = true`, desactiva cámaras si aplica.
3. **Por cada semilla**:
   - Sin espejo: inicia partida con semilla, captura roster del primer equipo.
   - Con espejo: inicia con roster intercambiado (Player↔Rival), mismo seed.
4. **Espera**: poll `recorder.Done` (con timeout `RoundSeconds + 150s`); si timeout, `ForceFinish()`.
5. **Volcado**: `MatchLine()` y `FighterLines()` se appenden a CSV.
6. **Finalización**: restaura `Time.captureDeltaTime`, reactiva cámaras, escribe `done.txt` con recuento y velocidad.

## Campos Privados

- `recorder`: ref a `BrawlBalanceRecorder` (RequireComponent)
- `disabledCameras`: lista de cámaras desactivadas (para restaurar)
- `firstRoster`: captura de `CreatureDNA` × 6 del primer run (sin espejo) para intercambiar en segundo run
- `previousCapture`, `timeFixed`: estado de tiempo pre-sim
- `simTotal`, `realTotal`: segundos de simulación y real (para velocidad)

## Salidas de Datos

```
Recordings/brawl_balance/<batch>/
├── matches.csv       # 1 línea/partida
├── fighters.csv      # 6 líneas/partida
├── progress.txt      # actualizado cada partida
└── done.txt          # resumen final + velocidad
```

## Manejo de Errores

- Si ya corre una tanda: warning, retorna.
- Si no hay `BrawlMatch.Current`: warning, retorna.
- Timeout global: `RoundSeconds + 150s` → `ForceFinish()`.
- `OnDisable()` restaura tiempo si corre tanda.

## Vinculado a

- [[Index/32 - Demo Brawl 3v3 arcade]]
- [[Tools/Balance/brawl_report.py]] — procesa CSVs

## Conexiones

**Componentes escena:**
- [[BrawlMatch]] — instancia actual de partida (`Current` singleton)
- [[BrawlBalanceRecorder]] — almacenamiento de stats (RequireComponent)

**Generación de datos:**
- [[BrawlFighter]] — rosters, equipos
- [[CreatureGenerator]] — vía `BrawlMatch.StartMatch(seed)`

**Configuración:**
- [[BrawlTuningSO]] — `RoundSeconds` para timeout

## Notas

- **Espejo**: crucial para balance simétrico (comparar P vs R en el mismo set de MoriMonchis).
- **Hz configurable**: 50 Hz típico (Time.captureDeltaTime = 0,02); ajustar para trade-off velocidad/precisión.
- **Sin persistencia**: todo en memoria; datos viven solo durante la tanda.
- **Velocidad sim/real**: mide overhead de renderizado (cameras on/off impacta).
- Requiere `BrawlMatch` activo en escena antes de invocar `Run()`.
