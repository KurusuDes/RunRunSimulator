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

## 7b · Balance con datos (S143)

**Arnés:** `BrawlBalanceDev` (corre la tanda) + `BrawlBalanceRecorder` (escucha los eventos de la partida y arma las filas), en `World/Brawl/`. Se crean en Play por código: `new GameObject("BrawlBalanceDev").AddComponent<BrawlBalanceDev>().Run(tanda, primeraSemilla, semillas, espejo, simHz, camarasOff)`. Cada semilla se juega dos veces con los lados cambiados (espejo). Salida en `Recordings/brawl_balance/<tanda>/`: `matches.csv`, `fighters.csv`, `progress.txt`, `done.txt`. **Reporte:** `py -3 Tools/Balance/brawl_report.py <carpeta> [--vs <base>]` → `report.md` por ala, familia, rol, habilidad, osadía, sociabilidad, cuerpo y sanadores por equipo.

**Metas (Juan, S143):** alas y familias 40-60 % de victorias · habilidades 35-65 % · partidas 45-70 s · muerte súbita en 5-15 % · remontadas (gana el equipo del primer KO) ≥ 15 %. Un equipo sin sanador puede perder seguido (Juan ✅).

**Cómo se mide:** paso fijo `Time.captureDeltaTime = 1/40` (los proyectiles chocan por punto-en-radio sin barrido; con `timeScale` alto atraviesan). Game view maximizado y cámara apagada: ~3× real. Mismas semillas entre tandas = comparación pareada.

**Base (`s143_base`, 200 partidas):** 57,9 s de media (p90 89), muerte súbita 8,5 %, remontadas 18 %, 69 % de los espejos los gana la misma composición. Fuera: Colibrí 61 %, Lanza de cristal 67 %, Tapón rebotín 34 %; ágil 41 %, pesado 56 %; 0 sanadores → 29 %, 2 → 60 %. **Vuelta 1:** Colibrí 250 → 215 · Arcoíris sanador 2240 → 2050 · Plumitas 950 → 1040 · Cintas 600 → 640 · Lanza de cristal 1000 → 880 · Tapón rebotín 650 → 760 · ágil ×0,96 · pesado ×1,20.

**Vuelta 1 verificada (`s143_v1_full`) y vuelta 2 (S144):** quedaban fuera Plumitas 38,7 % (más daño no servía: es el que más daña y más KOs saca, pero muere tarde y queda último en pie) y Erizo 31 %. Vuelta 2: Plumitas recarga 2,4 → 2,15 s · Erizo daño 330 → 370. **`s144_v2_full`: ninguna parte fuera de meta** (Plumitas 45,8 %, Erizo 40 %, Colibrí 54,6 %, Bumerán 57,3 %; 59,3 s de media, muerte súbita 10,5 %, remontadas 18 %). Balance cerrado hasta que cambien las partes.

## 8b · La bajada pasa a ser Brawl (decisiones de Juan ⭐, cierre de S142)

**El Brawl reemplaza al combate de la bajada** ("me gusta más, es más legible y la gente puede conectar"). La bajada queda como **run de salas** al estilo *Another Door*:

- **El jugador elige el equipo** que desciende (hasta 3 MoriMonchis propios). **Bajar cuesta dabloons.**
- **La decisión es por tramo, no por sala** (aclaración de Juan): antes de bajar se muestra **la secuencia completa del tramo con íconos** (ej.: combate difícil → combate fácil → curación → combate → minerales) y el jugador decide si hace ese tramo. **Al terminarlo se muestra el tramo siguiente** y vuelve a elegir si lo enfrenta o sale con lo juntado.
- **Tipos de sala** (lista abierta, "cosas así"):
  - **Combate** contra 1, 2 o 3 MoriMonchis rivales (el equipo propio puede quedar en superioridad o igualdad).
  - **Dummies**: muñecos que al pegarles curan al equipo (sala de recuperación).
  - **Minerales**: prueba de daño por tiempo: cuanto más daño en el tiempo fijo, más Minerita.
- **Perder un combate** = perder un **porcentaje** de lo juntado en la run (valor a calibrar).
- **KO sin penalidad** por ahora. **Al terminar cada combate el equipo se cura el 40 % de su vida** (a regular); la vida se arrastra entre salas de la misma run.
- **Provisorios que fijó la IA (S144, Juan: "decidilo vos, anotalo; falta toda la economía")** — viven en `ScriptableObjects/Brawl/BrawlRunRules.asset`: bajar cuesta **10 dabloons** · perder un combate = perder el **50 %** del botín y termina la run · **2-5 salas por tramo** al azar (Juan), la última siempre combate con el máximo de rivales · rivales: tramo 1 de 1 a 2, desde el tramo 3 de 2 a 3 · poder del rival ×0,85 en el tramo 1, +0,1 por tramo, tope ×1,5 (vida y daño) · botín = 1 por rival vencido × número de tramo (el puente lo paga ×5 en Minerita) · salas de prueba 15 % muñecos y 15 % minerales, 20 s; los muñecos curan al equipo el 30 % del daño que reciben; minerales: 1 de botín cada 4000 de daño. La arena vieja (`ArenaSandbox`) queda como escena de dev, desconectada de la bajada (Juan).
- Base existente a reusar: la run por pisos (`ArenaRun`, `ArenaRunDirector`, `ArenaFloorPanel` — `Index/26`, `Index/22` Parte 9) y el puente tienda ↔ arena (`ExpeditionHandoff`, `ExpeditionBridge`, `ExpeditionPanelUITK` — `Index/24`). `BrawlMatch.StartMatch(seed, roster)` ya acepta el ADN del equipo.

## 8c · Run de Brawl por tramos (implementada S144)

**Flujo:** terminal de expedición en la tienda → elegir hasta 3 → `ExpeditionBridge` cobra `DescentCost` dabloons (si no alcanza, no baja; el panel lo muestra y deshabilita el botón) → `ExpeditionHandoff.GoToArena` carga `BrawlDemo` → `BrawlRunDirector` (solo si `CameFromStore`; si no, la demo sigue igual) arma la run → al salir `ReturnToStore(run.ToResult())` → el puente paga `PlayerSecured × 5` Minerita (ya no lo pone a 0 al perder: la run aplica la pérdida).

**Piezas:** `BrawlRun` (Data, pura: tramos con 2-5 salas por semilla, vida 0-1 por id, botín, pérdida, `ToResult`) · `BrawlRoom` + `BrawlRoomKind {Combat, Dummies, Minerals}` + `BrawlRunState {Planning, Fighting, RoomResult, Over}` · `BrawlRunRulesSO` (todos los números; activo por `Activate/Current`, lo activan el puente en la tienda y el director en el Brawl) · `BrawlRunDirector` (World, único dueño; `AcceptTramo`/`NextRoom`/`Leave`, evento `Changed`) · `BrawlTrialRoom` (World: reloj de las salas de prueba, cura por golpe a muñecos, daño → botín) · `BrawlRunPanel` (UI, `BrawlRunPanel.uxml`/`BrawlRunPanelStyle.uss`).

**Cambios al Brawl:** `BrawlMatch.Driven` (sin partida al arrancar ni revancha automática; el HUD oculta Nueva/Revancha), `StartMatch(seed, players, rivalCount)` (equipo propio de 1-3 + rivales minteados), `EndNow(winner)`; `BrawlFighter.Prime(power, health01)` (escala vida y daño, fija la vida inicial), `Dummy` (siempre congelado). El `StartMatch(seed, roster)` del arnés conserva el orden de azar.

**Reglas:** se decide por tramo (no se sale a mitad); al cerrar el tramo se muestra el siguiente con "Enfrentar" o "Salir con X". Vida arrastrada, +40 % tras cada combate ganado, KO sin penalidad. Perder un combate termina la run y quita el 50 % del botín. Números provisorios en 8b. (Entre salas ya no hay tarjeta: ver 8e.)

## 8d · Tienda ↔ Brawl con UI (S145)

- **Rol sugerido** (Juan ⭐: "una guía para balancear el equipo, no un rol cerrado"): sale de los 3 poderes. Ala = Apoyo si cura (Colibrí), si no Daño; cuerno y espalda = `BrawlSkillSO.Role`. 3 iguales → rol único; 2 + 1 → "Mayoría/Minoría"; 3 distintos → **Equilibrado**. Dueño: `BrawlKitProfile` (Data, puro); píldora `BrawlRolePill`.
- **Terminal de bajada = armar equipo** (`ExpeditionCardBuilder`): tarjeta con retrato, rol y 3 poderes; aviso "Sin apoyo" si nadie cura. **Ficha**: rol sugerido + poder de cada parte. **Vuelta**: `ExpeditionReturnCardUITK` (panel `ExpeditionReturn = 9`), Minerita ganada/perdida, salas, pips de exploración de cada blobim o "¡Creció!".
- **Salas de prueba**: muñecos = espantapájaros (`BrawlScarecrowProp`, `BrawlTrialProps`); minerales = bonus de daño, la prueba arranca con el primer golpe o a los 15 s, piso 1 de botín. **Empate = victoria.** Tasa `MineritaPerLoot = 5` en `BrawlRunRulesSO`.

## 8e · Flujo estilo Another Door (S146)

- **Blobims** (Juan ⭐: "solo el ataque básico y el cuernito"): `BrawlKitProfile.BackLocked` → sin espalda hasta crecer; "?" en tarjeta, ficha y HUD; la vuelta muestra "Nuevo poder: X" al que creció (verificado en S147).
- **Sin tarjeta entre salas** (Juan: "una vez te comiteas al tramo no es necesario mostrarlo"): estado `Transition`; Planning → Transition (`VeilCoverSeconds` 1,1) → Fighting → RoomResult (`LootBeatSeconds` 1,6) → Transition… → Planning al cerrar el tramo; derrota → Over. `BrawlRunVeil` (velo "Sala N de M" con glifo) y `BrawlRunHud` ("Faltan N salas", mochila con Minerita, cristales que vuelan al ganar). Glifos por sala: `BrawlRoomGlyphsSO` (calavera 1/2/3 rivales, mineral, corazón).
- Los tiempos 1,1 s y 1,6 s quedan como provisorios de la IA (S147).

## 8f · Atmósfera por paleta (S147)

**Regla:** la paleta de la sala decide el ambiente. Pradera y Otoño = día con halos de sol y polvo de hada dorado/ámbar; **Crepúsculo = noche con luciérnagas** (sin halos ni polvo); Nevado = halos y polvo helado. Flags en `ArenaPaletteSO` (sección Ambiente: `Fireflies`, `LightShafts`, `FairyDust`, `DustColor`); `ArenaPaletteApplier.Applied` avisa; `ArenaAmbience` (en `Environment/ArenaPalette` de `BrawlDemo`) prende/apaga y hace que luciérnagas y polvo sigan a `ArenaTargetGroup` (la cámara del Brawl encuadra ~15-25 m, el anillo viejo de 16-44 m nunca entraba en cuadro).

- **Luciérnagas**: círculo r 14 lleno, 20/s, máx 220, tamaño 0,2-0,4, prewarm. **Polvo de hada** (Juan: "cúmulos de brillitos"): `Environment/FairyDust` = emisor invisible (caja 26×2,2×26, 2,4/s, vida 6-9 s) con sub-emisor de nacimiento `Sparkles` (22/s, esfera 0,45, tamaño 0,12-0,26, titila) y material `ArenaFirefly`. **Halos**: `ArenaShapeShafts` en las 5 formas con 3-5 rayos, escala 0,45-0,7, margen 4.
- **Post proceso "triple A"** (perfil compartido `ArenaAtmosphere`, Juan: mantenerlo): DOF **Bokeh** foco 30 m, focal 80, f/3,2 (miniatura: primer plano y fondo suaves, la pelea nítida); bloom umbral 0,9, intensidad 0,75, tinte cálido; contraste 12, saturación 8, viñeta 0,3; **Shadows/Midtones/Highlights** nuevo (sombras frías, luces cálidas). Ya había SSAO y sombras suaves en `PC_Renderer`.

## 8 · Pendientes

- Veredicto de Juan sobre los 7 íconos nuevos (Cresta y Ariete flojos).
- `BrawlProjectile.cs` quedó en 431 líneas (sobre el tope de ~400): partir la parte visual si vuelve a crecer.
- Plantillas aún más finas cuando los VFX estén validados; globos de habilidad que se pisan cuando dos luchadores están pegados.
- Sonido; más tandas de balance por familia de habilidad (hoy solo por ala); pantalla para que el jugador arme su equipo.
- Árboles altos tapan a veces (se ve la silueta); en Pradera la copa tapó la pelea en una captura de S147.
- Halos amarillos en todas las paletas (el material es compartido); teñirlos con `SunColor` si en Nevado se ven fuera de tono.
- Textos del Brawl sin localizar: se posterga hasta que entre la UI comprada (Juan, S147: la UI actual es temporal).
