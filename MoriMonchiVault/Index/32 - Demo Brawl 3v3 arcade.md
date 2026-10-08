---
tags: [index, combat, brawl, demo, arena]
---

# 32 - Demo Brawl 3v3 arcade (S142)

**Estado:** demo jugable y automática, verificada en Play (S142). Escena aparte `Resources/Scenes/BrawlDemo.unity` (copia del mapa de `ArenaSandbox` sin la bajada). No toca la tienda, la bajada ni `MoriMochiAgent`.

**Regla (Juan, S142):** el **ala** define movilidad + ataque básico; **cuerno** y **espalda** son habilidades con anticipación (windup) y enfriamiento; la **personalidad** (osadía y sociabilidad del ADN) decide la postura; el **cuerpo** da vida y velocidad; gana el **último equipo en pie**; a los 90 s **muerte súbita** (la vida de todos baja) hasta que quede uno; los **VFX usan el ícono pixel art y el color del set** de cada parte; tiene que haber apoyo/curación para armar arquetipos.

Antecedente: experimento offline de S141 (`Tools/Balance/brawl_sim.py`), que repartía distinto (cuerno = ataque, espalda = súper). Este reparto lo reemplaza.

---

## 1 · Partida

| Regla | Valor (`BrawlTuning.asset`) |
|---|---|
| Vida base | 14000 × cuerpo (BS0 equilibrado 1,0 · BS1 robusto 1,15 / vel 0,93 · BS2 ágil 0,9 / 1,08 · BS3 pesado 1,25 / 0,88) |
| Cuenta regresiva · ronda | 3 s · 90 s |
| Muerte súbita | drena 2 % de la vida máx./s + 1 %/s por segundo transcurrido; curación ×0,5 |
| Último en pie (1 contra ≥2) | escudo 25 % de su vida, +30 % daño, +20 % velocidad por 5 s, recarga sus dos habilidades, deja de huir, cartel "¡ÚLTIMO EN PIE!" |
| Rampa por KO | cada KO suma +15 % de daño a todos los que quedan (el HUD lo muestra bajo el reloj) |
| Fin | 6 s de cartel con MVP (mayor daño) y nueva partida automática con otra semilla |

Elenco: 6 MoriMonchis al azar por semilla (`CreatureGenerator`), sin repetir ala dentro de un equipo cuando se puede. Mapa y paleta por semilla con `ArenaLayoutBuilder` y `ArenaPaletteApplier`.

## 2 · Alas (6) — básico + movilidad

| Ala | Básico | Movilidad |
|---|---|---|
| Murciélago (W4) | Mordisco: melé, 2 mordiscos en cono | Salto sobre el blanco con daño al caer |
| Cintas (W3) | Latigazo en línea que frena | Carrera (+60 % vel.) |
| Aletas (W2) | Chorro: escopeta de 5 gotas | Voltereta corta |
| Plumitas (W5) | Pluma certera: francotirador con mira láser | Salto hacia atrás |
| Colibrí (W1) | Néctar: ráfaga de 3 dardos; **cura** a aliados bajo 62 % de vida | Parpadeo; vuela siempre (Hover) |
| Vela (W0) | Bumerán: pega a la ida y a la vuelta | Planeo largo |

## 3 · Cuernos y espaldas (33) — 10 familias

| Familia | Qué hace | Partes |
|---|---|---|
| Dash | embestida en línea, empuja/aturde | Ariete, Carnero, Cuernitos, Rinoceronte, Triceratops |
| Chain | rayo que salta entre rivales | Rayo, Antenas |
| Cone | barrido en cono (360° = giro) | Astas, Hoz, Abanico (ventarrón), Cola (360°), Espuelas |
| Shot | proyectil fuerte (rebota / atraviesa / estalla) | Cometa, Cristal, Mechón, Tapones |
| Nova | púas en todas direcciones | Espinas, PuasFinas, PuasGruesas |
| Homing | proyectiles que persiguen | Cometitas |
| Pull | atrae y provoca | Señuelo |
| Zone | área con demora / duración (sueño, lluvia, curación) | Lana, Cristales, Malvaviscos, LomoLana |
| Ward | escudo propio o de aliado, espinas, provocación | AletasCara (burbuja a aliado), Coraza, Placas, PuasDobles |
| Mend | cura o potencia aliados | Unicornio (rayo), Alforja (merienda lanzada), Borla (pulso), Cresta (grito) |

Roles para armar arquetipos: **apoyo** (AletasCara, Unicornio, Alforja, Borla, LomoLana, Cresta + ala Colibrí), **tanque** (Coraza, Placas, PuasDobles, Señuelo), **control** (Lana, Carnero, Abanico, Cola, Espuelas, Malvaviscos), **daño** (el resto). Datos: `ScriptableObjects/Brawl/Wings/Wing_*.asset`, `Skills/Skill_*.asset`, `BrawlKitDatabase.asset` (parte → kit por `PartId`).

## 4 · Personalidad → postura (`BrawlBrain` + `BrawlSkillJudge`)

- **Osadía** alta: se acerca más, usa las habilidades apenas puede y la movilidad para enganchar, huye tarde (umbral de retirada 50 % → 15 % de vida). Baja: mantiene distancia, espera el buen momento (2+ rivales en el área o blanco < 50 %; tras 6 s listo la usa igual) y usa la movilidad para escapar.
- **Sociabilidad** alta: elige blancos cerca del equipo y al que amenaza a su aliado más débil, se mantiene junto al grupo y cura antes. Baja: caza al más débil donde esté.
- Los de rango se mueven de lado (strafe) mientras disparan. La etiqueta del HUD ("Osado · solitario", "Cauto · protector"…) sale de los diales.

## 5 · VFX temáticos

- Partículas **= íconos pixel art** de la parte (`BodyPart.Icon`, tintado con `PartSetSO.Color`): malvaviscos, plumas, púas, cristales y lana vuelan como los íconos. Proyectiles = el ícono en billboard + estela del color.
- Rayos, rayo arcoíris y latigazos con `LineRenderer`; escudos con íconos orbitando; destellos de suelo con `CueDrawer`.
- Telegrafías (regla S116): la plantilla del golpe en el suelo, del color del equipo, se llena al ritmo del windup, con borde del color de la parte. Apoyo (Ward/Mend) en el color de la parte.
- Las 7 partes originales (Ariete, Alforja, Coraza, Cresta, Cola, Vela, Colibrí) no tienen malla propia (en el modelo se ve la parte horneada del cuerpo: HornA-D, BackA/B, Wing_A). **Íconos propios desde S142** (segunda vuelta): se modelaron como módulos de parte `Tools/Blender/parts/p_{Ariete,Alforja,Coraza,Cresta,Cola,Vela,Colibri}.py` (conceptos: ariete con aros, alforja con hebilla, caparazón de tortuga, cresta de llamas, cola con maza, ala-vela, ala de colibrí) y se renderizaron con `icon_part.py` (entradas nuevas en sus tablas); `BodyPart.Icon` asignado. Los módulos sirven para exportarlas como mallas reales si Juan lo pide. Flojas según el agente: Cresta (a 32 px se acerca a Espinas) y Ariete (se lee como tronco con aros).

**Feedback de golpe y VFX en el aire (S142, segunda vuelta — pedido de Juan: "un mini tinte rojo" y depender menos de las plantillas):**
- **Destello de golpe parejo** (tercera vuelta; reemplazó al tinte por paleta, que solo teñía partes porque pasa por `MonchiTint.Fill` → paleta del pelaje y no toca patrones, cara ni dientes): `MonchiVisualizer.SetFlash(color, alpha)` agrega una capa (`flashMaterial`, `Resources/Materials/Brawl/BrawlFlash.mat`, shader `Sprites/Default`) al final de `sharedMaterials` de todos los renderers del cuerpo y la cara; sin `flashMaterial` es inerte (la tienda no lo usa). `BrawlBody`: **rojo cuando golpean a los nuestros (Player), blanco cuando golpean a los rivales** (0,85 fuerte / 0,6 liviano, cae en 0,2 s); curación en verde 0,35.
- **Lectura de equipo** (decisión de Juan S142): **todo lo enemigo va lavado en rojo conservando forma e ícono; lo nuestro con el color de su parte, más saturado, 20 % más grande y con halo**. Helper `BrawlTeamLook` (`IsAlly`, `Wash`, `Size`; knobs `FoeTint`/`FoeWash` 0,7/`AllySaturation`/`AllyMinValue`/`AllySizeBoost` y `GlowSprite` en `BrawlVfxLibrarySO`). Lo aplican `BrawlVfx` (lava todos los temas), `BrawlRainFx`, `BrawlProjectile` (halo aditivo en proyectiles aliados, estela rival más fina) y `BrawlTelegraphs` (bordes lavados + **línea de mira** punteada del lanzador al blanco durante el casteo, verde cuando el ala cura).
- **Firmas nuevas**: `BrawlBubbleFx` (burbuja de escudo para Ward), `BrawlVortexFx` (remolino en espiral para Pull), `BrawlLineFx` con capa de brillo en rayo/latigazo/rayo de curación y destellos en los nodos del rayo (`BrawlGlowFlashFx`).
- **Firmas de partes estrella (lote 4)**: enum `BrawlSignature { None, Rainbow, Storm, Cloud, Comet, Lure, Plates }` en `BrawlSkillSO.Signature` / `BrawlWingKitSO.Signature`, viaja en `BrawlTheme.Signature` (todo evento y proyectil la lleva). Reparto: Unicornio y Borla = arcoíris (rayo con gradiente arcoíris que corre, chispas de colores, anillos concéntricos) · Rayo y Antenas = tormenta (ramas en el relámpago, chisporroteo sobre la víctima y el lanzador) · Lana y LomoLana = nube (puffs mullidos sobre la zona) · Cometa y Cometitas = cometa (estela de fuego, chispas, estallido de fuego) · Señuelo = farol (orbe que late con **luz real** durante la carga y destello al lanzar) · Placas y Coraza = placas (6 placas grandes orbitando). Código: `BrawlSignatureFx` (enrutador + arcoíris) con clases planas `BrawlCometSparks`, `BrawlStormCrackle`, `BrawlCloudPuffs`, `BrawlLureLight`, `BrawlPlateOrbit`, `BrawlSignatureSprites` (pool); `BrawlLightningShapes`/`BrawlLightningBranches` (ramas), `BrawlProjectileTrail` (estela de fuego). Todo color pasa por `BrawlTeamLook.Wash`.
- **Micro congelado** (`BrawlAnimator`): `Animator.speed = 0` 0,05 s (≥ 600) / 0,1 s (≥ 1500) en víctima y atacante.
- **Sacudida de cámara** (`BrawlCamera` + `CinemachineImpulseSource`; `CinemachineImpulseListener` en `ObserverCamera`): golpes ≥ 1500, KO y último en pie.
- **Nuevos componentes** en el GO `BrawlVfx`: `BrawlSwooshFx` (arco de barrido procedural a la altura del pecho para mordiscos y conos), `BrawlTrailFx` (estela en embestidas y saltos), `BrawlImpactFx` (estrella + anillo de impacto en cada golpe), `BrawlRainFx` (íconos que caen sobre las zonas con demora — lluvia de cristales/malvaviscos — y ambiente de zonas: íconos que suben en curación, que caen en daño); `BrawlIconParticles.Spray` (abanico direccional de íconos en fogonazos y barridos).
- **Plantillas más sutiles** (valores de escena de `BrawlTelegraphs`): pista 0,06, relleno 0,2, borde 0,035 de grosor, base 0,22, zonas 0,09.
- **Cámara más cerca**: `CinemachineGroupFraming.FovRange` 18-50 (antes el mínimo de 32° impedía acercarse), `FramingSize` 0,6, y `BrawlCamera.idleWeight` 0,12 para quien no pelea en los últimos 1,5 s.

## 6 · Scripts

`Core/Enums/BrawlEnums.cs` · `Data/Brawl/`: `BrawlTheme`, `BrawlWingKitSO`, `BrawlSkillSO`, `BrawlKitDatabaseSO`, `BrawlTuningSO`, `BrawlVfxLibrarySO` · `World/Brawl/`: núcleo `BrawlFighter` (vida, estados, eventos estáticos) + `BrawlMotor` (NavMesh, dash, salto, empuje) + `BrawlWing` + `BrawlSkillCaster` + `BrawlBrain`/`BrawlSkillJudge`; ejecutores estáticos `BrawlSkillEffects`/`Offense`/`Support`; `BrawlProjectile` y `BrawlZone` (pools por código); `BrawlQuery` (consultas sobre `BrawlFighter.All`); bus `BrawlFx`; `BrawlMatch` (fases, último en pie, rampa); presentación `BrawlAnimator`, `BrawlBody`, `BrawlCamera`, `BrawlTelegraphs`, `BrawlVfx` + `BrawlIconParticles` + `BrawlLineFx` + `BrawlWardFx` · `UI/`: `BrawlHud`, `BrawlHudCard`, `BrawlOverheads` + `BrawlHud.uxml`/`BrawlHudStyle.uss`.

Prefab `Resources/Prefabs/Brawl/BrawlFighter.prefab` (derivado de `MorimonchiAgent`: modelo, pivote de squash y transición de cara; sin IA de tienda; `areaMask` = todas). Materiales `Resources/Materials/Brawl/`, chispa `Resources/Sprites/Brawl/BrawlSpark.png`.

**Invariantes:** la presentación solo lee y escucha eventos (`BrawlFighter.On*`, `BrawlWing.OnAttackFired`, `BrawlSkillCaster.OnCast*`, `BrawlMatch.On*`, `BrawlFx.Emitted`); números en SO, no en C#; nada persiste ni toca el registro (las criaturas se mintean en memoria).

## 7 · Medido (S142, partidas automáticas a 4×)

- Sin rampa ni último en pie: 8 partidas, 46-86 s, pero el 1 contra varios duraba 25-37 s (el último huía; dos tiradores en 1v1 se pegan ~450 de daño/s cada uno).
- Con último en pie + rampa: 12 partidas, **40-66 s (media 51)**, cola final ~15 s, remontadas 2/12, azul 6 - rojo 6. Ninguna llegó a muerte súbita en esa tanda (sí en una de las anteriores).
- Balance por ala (12 partidas, muestra chica): Colibrí ganó 6/6 (curación ~31 k por partida) → curación 320 → 250 y umbral 0,7 → 0,62; Bumerán 31 % → daño 400 → 460. Murciélago subido antes (560 × 2, salto cada 4,5 s).

## 8b · La bajada pasa a ser Brawl (decisiones de Juan ⭐, cierre de S142)

**El Brawl reemplaza al combate de la bajada** ("me gusta más, es más legible y la gente puede conectar"). La bajada queda como **run de salas** al estilo *Another Door*:

- **El jugador elige el equipo** que desciende (hasta 3 MoriMonchis propios). **Bajar cuesta dabloons.**
- **Antes de cada sala se muestra más o menos qué esperar** (vista previa del tipo de sala); **al terminar cada sala se elige si entrar a otra o salir** con lo juntado.
- **Tipos de sala** (lista abierta, "cosas así"):
  - **Combate** contra 1, 2 o 3 MoriMonchis rivales (el equipo propio puede quedar en superioridad o igualdad).
  - **Dummies**: muñecos que al pegarles curan al equipo (sala de recuperación).
  - **Minerales**: prueba de daño por tiempo: cuanto más daño en el tiempo fijo, más Minerita.
- **Perder un combate** = perder un **porcentaje** de lo juntado en la run (valor a calibrar).
- **KO sin penalidad** por ahora. **Al terminar cada combate el equipo se cura el 40 % de su vida** (a regular); la vida se arrastra entre salas de la misma run.
- Base existente a reusar: la run por pisos (`ArenaRun`, `ArenaRunDirector`, `ArenaFloorPanel` — `Index/26`, `Index/22` Parte 9) y el puente tienda ↔ arena (`ExpeditionHandoff`, `ExpeditionBridge`, `ExpeditionPanelUITK` — `Index/24`). `BrawlMatch.StartMatch(seed, roster)` ya acepta el ADN del equipo.

## 8 · Pendientes

- Veredicto de Juan sobre los 7 íconos nuevos (Cresta y Ariete flojos).
- `BrawlProjectile.cs` quedó en 431 líneas (sobre el tope de ~400): partir la parte visual si vuelve a crecer.
- Plantillas aún más finas cuando los VFX estén validados; globos de habilidad que se pisan cuando dos luchadores están pegados.
- Sonido; más tandas de balance por familia de habilidad (hoy solo por ala); pantalla para que el jugador arme su equipo.
- Árboles altos tapan a veces (se ve la silueta).
