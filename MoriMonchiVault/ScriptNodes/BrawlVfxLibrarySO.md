---
tags: [script, data, so]
---

# BrawlVfxLibrarySO.cs

**Ruta:** `Data/Brawl/BrawlVfxLibrarySO.cs`

**Responsabilidad:** Banco de referencias de materiales, sprites, prefabs y knobs de VFX para batalla 3v3. Static property `Current` centraliza acceso global. Usado por `BrawlVfx`, `BrawlProjectile`, `BrawlRainFx`, `BrawlTeamLook` (lava de équipo) y otros ejecutores de VFX.

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]] (sección "5 · VFX temáticos")

## Estructura

```csharp
[CreateAssetMenu(fileName = "BrawlVfxLibrary", menuName = "MoriMonchi/Brawl/Vfx Library")]
public class BrawlVfxLibrarySO : ScriptableObject
{
    public static BrawlVfxLibrarySO Current { get; private set; }
    
    public static void Activate(BrawlVfxLibrarySO library) => Current = library;
    public static void Deactivate(BrawlVfxLibrarySO library)
    {
        if (Current == library) Current = null;
    }

    // Materiales, sprites, prefabs, tuneo...
}
```

## Campos Principales

| Sección | Campo | Tipo | Descripción |
|---------|-------|------|-------------|
| **Materiales** | `SpriteMaterial` | Material | Shader para sprites (Sprites/Default) |
| | `ParticleMaterial` | Material | Shader para partículas (multiplica color) |
| | `ParticleAdditiveMaterial` | Material | Shader aditivo para brillo/chispas |
| | `LineMaterial` | Material | Shader para LineRenderer (rayos, látigos) |
| **Sprites** | `SparkSprite` | Sprite | Chispa pixel art (reutilizada en VFX) |
| **Prefabs** | `HitFx` | GameObject | Prefab de impacto (estrella, anillo) |
| | `KnockOutFx` | GameObject | Prefab de KO (explosión, flash) |
| | `DustFx` | GameObject | Prefab de polvo (dash, aterrizaje) |
| **Proyectiles** | `ProjectileTrailTime` | float | Duración de estela tras proyectil (0,25s) |
| **Lectura de equipo** | `FoeTint` | Color | Tinte para enemigos (rojo) |
| | `FoeWash` | float | Factor de lavado para enemigos (0-1) |
| | `AllySaturation` | float | Factor de saturación para aliados (0-1) |
| | `AllyMinValue` | float | Valor mínimo en HSV para aliados (0,85) |
| | `AllySizeBoost` | float | Multiplicador de tamaño para aliados (1,2 = +20%) |
| | `GlowSprite` | Sprite | Halo/brillo que orbita aliados |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Activate(BrawlVfxLibrarySO library)` | Asigna `Current = library` (llamado al iniciar escena Brawl) |
| `Deactivate(BrawlVfxLibrarySO library)` | Si `Current == library`, pone `Current = null` |

## Lectura de Equipo (S142)

**Parámetros de BrawlTeamLook:**
- **Enemigos (Foe):** Tintado rojo conservando forma + ícono
  - `FoeTint = (1, 0.22, 0.18)` → rojo oscuro
  - `FoeWash = 0.7` → 70% lavado (opaco)
- **Aliados (Ally):** Color de parte más saturado, 20% más grande con halo
  - `AllySaturation = 0.25` → boost de saturación
  - `AllyMinValue = 0.85` → mínimo brillo (no oscuro)
  - `AllySizeBoost = 1.2` → +20% tamaño
  - `GlowSprite` → halo aditivo orbitando

## Referencia de Valores Default S142

```
Materiales: 4 estándar (Sprites/Default, partículas, aditivo, LineRenderer)
Sprites: 1 (chispa común)
Prefabs: 3 (hit, KO, dust)
ProjectileTrailTime: 0,25s (suave)
Lectura equipo:
- FoeTint (rojo lavado): RGB(1.0, 0.22, 0.18)
- FoeWash: 0.7 (muy opaco)
- AllySaturation: 0.25 (color más vivo)
- AllyMinValue: 0.85 (siempre brillante)
- AllySizeBoost: 1.2 (20% más grande)
```

## Dependencias

**Entrada:**
- Linkado en inspector en `BrawlMatch` o autolocalizador (Resources)
- Llamado `Activate()` al iniciar `BrawlMatch.Awake()`
- Llamado `Deactivate()` al destruir `BrawlMatch`

**Salida:**
- `BrawlVfx.CreateProjectile()` → usa `Current.SpriteMaterial`, `ParticleMaterial`, `HitFx`
- `BrawlProjectile` → usa `Current.ProjectileTrailTime`
- `BrawlTeamLook.Wash()` → usa `FoeTint`, `FoeWash`, tintado lavado
- `BrawlTeamLook` (aliados) → usa `AllySaturation`, `AllyMinValue`, `AllySizeBoost`, `GlowSprite`
- `BrawlRainFx` → usa `ParticleMaterial` para lluvia de partículas
- Ejecutores de VFX globales (rayos, zonas, etc.)

## Notas S142

- Asset único en proyecto (`BrawlVfxLibrary.asset`)
- Static `Current` permite acceso sin pasarle referencias a todos los VFX
- `Activate()/Deactivate()` evita leak si escena se recarga
- Materiales son reutilizables (instanciados por ejecutor individual)
- Sprites y prefabs son pooled por sus propios managers (no instantiados por VFX central)
- Parámetros de lectura de equipo se editan aquí (no hardcodeados)
- SpriteSize en cada skill/wing permite override local (este es global fallback)
