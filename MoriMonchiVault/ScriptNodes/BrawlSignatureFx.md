---
tags: [script, world, brawl, vfx, presentation]
---

# BrawlSignatureFx.cs

**Ruta:** `World/Brawl/BrawlSignatureFx.cs`

**Responsabilidad:** Orquestador de VFX especiales por firma (BrawlSignature: Rainbow, Storm, Cloud, Comet, Lure, Plates). Enruta eventos de `BrawlFx.Emitted` a sub-sistemas especializados (`BrawlCometSparks`, `BrawlStormCrackle`, `BrawlCloudPuffs`, `BrawlLureLight`, `BrawlPlateOrbit`). Escucha daño/casteo para activar crackle de tormenta. Rainbow genera anillos concéntricos + chispas HSV animadas.

**Métodos públicos:**
- `OnFx(BrawlFxEvent)` — enruta Rainbow (Beam→chispas, Pulse→anillos) / Comet (Burst) / Cloud (Ring) / Plates (Ward)
- `OnDamaged(victim, hit)` — activa Storm crackle al golpear
- `OnCastStarted(caster, skill, aim)` — activa Storm/Lure crackle durante casteo
- `OnCastFired(caster, skill, aim)` — termina Lure flash

**Campos principales:**
- `icons` — acceso a `BrawlIconParticles` para Rainbow/Comet
- Listas y diccionarios de beams + rings (Rainbow)
- Sub-sistemas: `comet`, `storm`, `clouds`, `lure`, `plates`

**Firmas implementadas:**
- **Rainbow** (Unicornio, Borla): anillos pulsantes + chispas HSV que giran (BeamInterval 0.05s)
- **Storm** (Rayo, Antenas): crackle de bolts aleatorios, active en casteo + impacto
- **Cloud** (Lana, LomoLana): puffs mullidos en zona con fade
- **Comet** (Cometa, Cometitas): trail de chispas + anillos de explosión naranja/rojo
- **Lure** (Señuelo): orbe pulsante + luz real durante carga, flash destello al disparar
- **Plates** (Placas, Coraza): 6 placas orbitando, pop-in escalonado

**Notas:**
- Sub-sistemas creados en Awake (factory pattern con callbacks)
- Ring helper centralizado para Rainbow
- Frame-synced: polling de zonas en Step
- Paso a paso cada sub-sistema en LateUpdate

**Vinculado a:** [[Index/32 - Demo Brawl 3v3 arcade]]

**Conexiones:** [[BrawlCometSparks]], [[BrawlStormCrackle]], [[BrawlCloudPuffs]], [[BrawlLureLight]], [[BrawlPlateOrbit]], [[BrawlSignatureSprites]], [[BrawlFx]], [[BrawlFighter]], [[BrawlSkillCaster]], [[BrawlIconParticles]], [[CueDrawer]]
