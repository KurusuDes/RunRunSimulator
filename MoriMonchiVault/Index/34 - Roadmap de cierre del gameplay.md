---
tags: [index, roadmap, checklist]
---

# 34 - Roadmap de cierre del gameplay (S149)

> Pedido de Juan (2026-10-12): *"un roadmap de TODO lo que nos falta para cerrar el gameplay: más objetos y posiciones, mejorar los NPC, el tamaño de la tienda… vamos cerrando esos espacios a nivel de código y marcando lo completado"*. Auditado en S149 contra el código (`Assets/RunRunSimulator/Scripts/`) y las notas [[Index/25 - Hitos hasta el lanzamiento]], [[Index/28 - Cimientos y camino a Game Ready]] y [[Index/33 - Contenido para el core loop]]. **Esta nota es la lista viva**: al cerrar un ítem se marca `[x]` con la sesión. Las otras tres quedan como mapa y diseño.

## 0 · Regla y dirección

> **El gameplay está cerrado cuando alguien abre una build, empieza de cero y juega 2 horas de día (tienda) y noche (bajada) sin el editor, y cada vuelta cambia algo en la siguiente.**

**Dirección de Juan (S149): el corazón es el sim de crianza.** *"Centrarnos en el sim de crianza, ese es el feeling que quiero manejar."* La tienda crece por **expansiones** que se compran en la PC y ya traen su zona y su equipamiento; dentro de ellas se cría, se decora, se juega y se mantiene. La bajada (Brawl) sigue siendo la noche, pero la prioridad de contenido es la tienda.

Leyenda: `[x]` hecho · `[ ]` falta · ~~tachado~~ = se cae por una decisión. Orden de ataque: **A → D → E → F → G → C → B → H → I**. Si falta tiempo se corta I (audio y feel van con assets comprados).

---

## Ya hecho (base sobre la que se construye)

- [x] Limpieza del combate viejo, stats y equipo (C1, S128-S129)
- [x] Guardado con versión, migraciones, reconciliación por fecha y push agrupado (C2, S128)
- [x] Cartera de dos monedas, `Wallet` como única puerta (C3, S128)
- [x] Ciclo de vida: estantes vivos/idos, `Kill`/`Adopt` como únicas salidas (C4, S129)
- [x] Catálogo unificado: comprar un mueble lo habilita en construcción (C5, S130)
- [x] Reloj de juego con 4 bloques, cría local con costo de eclosión en Minerita (C6, S131)
- [x] Huevo → blobim → adulto (3 exploraciones)
- [x] Necesidades (vida, energía, afecto), estaciones de comida/juego/descanso, vida social (juego, siesta, peleas, afinidad), caricias y comer de la mano
- [x] Brawl 3v3: 33 habilidades, 6 alas, balance cerrado (S144)
- [x] Run por tramos: velo, botín, derrota (−50 %), retirarse (S144-S146)
- [x] Evolución de partes con Minerita + experiencia en batalla (P0.1-P0.2, S148)
- [x] Venta completa: negociación, fila, `CustomerSold`, competidores que se van

---

## A · Bloqueantes (sin esto no se puede jugar ni probar el loop)

- [x] **A0 · Consola de admin (dev)** ✅ S149 (`AdminDevConsole`: fijar dabloons/Minerita, reiniciar save + kit, forzar llamada del tío, volcado de estado) (Juan S149: *"puedes eliminar y reiniciar el save y cambiar las monedas… créate tu propia admin console"*): borrar y reiniciar el save, fijar dabloons y Minerita, y lo que pida el playtest. Componente dev aparte (regla 11), usable desde el MCP.
- [x] **A2 · Las 7 partes sin malla salen del pool** ✅ S149 (cuerno/espalda/ala sin malla adulta en el banco visual no salen al azar; al modelarlas vuelven solas; 600 sorteos sin ninguna) (decisión S148, sin ejecutar): Ariete, Alforja, Cola, Coraza, Cresta, Colibrí, Vela.
- [x] **A3 · Rescate del jugador trabado** ✅ S149 (`UncleRescueService`: ya tuvo criaturas + ninguna viva que no sea huevo + sin huevos o sin Minerita para eclosionar → caja de 5 adultos en la entrada y aviso) (Juan S149): si se detecta un soft block (sin criaturas que puedan bajar ni dabloons para conseguirlas), **llama el tío y le regala una caja de criaturas**.
- [x] **A4 · El stock de la tienda online se guarda en la partida** ✅ S149 (en el estado de mundo, junto al día del último restock) (hoy vive en el asset y se repone en cada sesión).
- [x] **A5 · Precios de venta reales** — revisado S149, sin cambio: una criatura nueva vale ~24 y evolucionada al máximo ~96, coherente con un catálogo de 3-50; se recalibra con el playtest y con H3 (valuación): la tabla quedó en 1/2/3/4 por nivel; hoy toda venta da ~24. Recalibrar con los niveles de parte que ya suben (S148).
- [x] **A6 · Cadencia de clientes de verdad** ✅ S149 (20-60 s, hasta 3 a la vez): la escena tiene valores de prueba (uno cada 2-5 s, hasta 15 a la vez).
- [ ] **A1 · Carrera del sync al arrancar (latente, baja prioridad).** Las dos PCs usan **cuentas distintas** (Juan S149), así que la nube no se pisa entre PCs. Queda la carrera dentro de una misma cuenta: el reloj regraba el save local antes de bajar la nube y el push de 5 s no espera al sync inicial.

## D · Expansiones de la tienda (reemplazan al modo construcción libre)

> Juan S149: *"la opción barata sería descartar esa manera de construir y tenerlo por expansiones: en la PC vas comprando mejoras a la tienda que ya vienen con zonas y furniture para poder utilizar"*. Confirmado: se descarta el modo libre y se decora en ranuras fijas.

- [x] D1 · ✅ S149 Retirar el modo construcción libre (grilla, fantasma, colocar y borrar; muebles fuera del save y de la nube). Con eso se caen ~~propiedad por cantidad~~, ~~zonas prohibidas~~, ~~precio duplicado~~ y ~~categorías mal puestas~~ del audit.
- [x] D2 · ✅ S149 La expansión como dato: es una mejora de la PC (`ShopUpgradeSO`, nivel en el estado de mundo) y la zona es un bloque fijo en escena (`ShopZone`: abierto / cerrado con cartel). 🟡 Faltan las ranuras de decoración (E3) y los ítems que desbloquea (llegan con F)
- [x] D3 · ✅ S149 Comprar una expansión en la PC abre el área: se levantan los muros (MMF de Feel) y el NavMesh se rehornea una vez (`NavMeshRebaker`). Pestaña de la PC: "Expansiones"
- [x] D4 · ✅ S149 Lista v1: **base** (local, patio, vitrina, incubadora, comedero, cama) · **Criadero** (lote oeste; 60 abre con 1 corral, 90/140/200 suman corrales) · **Sala de juegos** (lote este; 120, estación de juego). Precios provisionales de la IA
- [x] D5 · ✅ S149 Quitar el Ring
- [ ] D6 · Arte real del equipamiento de cada zona (hoy hay cubos de ProBuilder)

## E · Zona de breeding

- [x] E1 · ✅ S149 Se desbloquea como expansión (D)
- [ ] E2 · 🟡 S149 Tres mejoras de capacidad: los niveles 2-4 del Criadero suman un corral cada uno (verificado que aparecen); falta probar en juego que permitan más parejas criando a la vez
- [x] E3 · ✅ S149 Decoraciones compradas con dabloons (pestaña "Decoraciones" de la PC, se guardan por cantidad) y colocadas en **3 ranuras por corral** (Juan S149: las ranuras van en cada lugar de crianza); v1: E sobre la ranura rota entre las que tienes (el panel llega con la UI comprada)
- [x] E4 · ✅ S149 (8 decoraciones v1: Retrato, Lámpara de lava, Álbum, Cojín de mamá, Cojín de papá, Manta, Árbol genealógico, Móvil de estrellas; los efectos se suman y se pueden repetir; medido en 20.000 tiradas: retrato padres 40→50 %, dos retratos 57 %, lava mutación 20→33 %, manta 6 %, cojín de mamá 67 % a la madre) Cada decoración mueve los diales de la cría (Juan S149): subir o bajar probabilidades, forzar o bajar la mutación al azar, favorecer al padre, a la madre o a los abuelos (los diales 50/30/20 que ya existen). Da control al jugador sobre lo que cría. Una regla en una frase por decoración; catálogo v1 de 8-12
- [x] E5 · ✅ S149 (por cantidad de crías: la decoración se ve "???" hasta criar 1/2/3/4/6 MoriMonchis según cuál) **Descubrimiento:** al principio el jugador no sabe qué hace cada decoración; lo va desbloqueando con misiones o por cantidad de MoriMonchis criados
- [x] E6 · ✅ S151 La ficha (pestaña Linaje) muestra la **Herencia**: una línea por parte con su origen y la decoración que lo empujó ("Cuerno · de mamá Wiggly Droob — por Retrato familiar", "Alas · una mutación — por Lámpara de lava"). La cría guarda `Origins` en el save (no en el genetic string). E2: el servicio no limita parejas simultáneas (estado por madre); falta probarlo en juego con 2 machos libres y el Criadero nivel 2

**Rediseño de la cría (Juan S152, decidido):** los corrales son zonas de agrupación y el huevo vive en otro lugar.
- [ ] E7 · **Corrales grandes**: el Criadero arranca con 2 corrales y sus mejoras suman hasta 10. Cada corral aloja **2 adultos al inicio y sube hasta 6** con mejoras; ahí conviven, cortejan y se aparean
- [ ] E8 · **Puff a la Huevera**: las parejas se forman solas (como hoy); cuando terminan de aparearse, el jugador se acerca y con **E** la pareja se separa y el huevo hace *puff* y aparece en la repisa. En el corral ya no se eclosiona nada
- [ ] E9 · **Huevera = repisa sobre la incubadora**: el jugador elige qué huevo de la repisa pasa a la incubadora y decide si empezar la eclosión pagando Minerita (reusa `IncubatorContainer` y el modelo `ShopIncubator`, S152)
- [ ] E10 · **Repisa llena = sin cortejo**: si la repisa está llena, los MoriMonchis de los corrales dejan de cortejar hasta que haya lugar
- [ ] E11 · Arte: corral grande (sale de `Tools/Blender/props/shop_corral.py`, S152) + repisa de huevos

## F · Juguetes y vida social (lo más importante para Juan)

> Juan S149: *"poder comprarles juguetes y que puedan interactuar con ellos y con los demás"*.

- [x] F1 · ✅ S149 Los juguetes son objetos físicos que las criaturas usan solas (`Toy` + colaborador `AgentToys`, estado Playing; ajuste en `ToyTuning.asset`)
- [x] F2 · ✅ S149 **Pelota:** la golpean, rueda y le pega a los demás (reacción del golpeado) — video `Recordings/S149/ball.mp4`
- [x] F3 · ✅ S149 **Juguete de morder:** uno lo tiene, otros intentan quitárselo, persecución (5 robos en 6 s en el video `chew.mp4`)
- [x] F4 · ✅ S149 **Manguera:** la agarran y corren mojando todo; deja charcos (tope 25) que se secan con el trapeador — `hose.mp4`
- [x] F5 · ✅ S151 El jugador juega con ellas: **traer** (lo que tiras o sueltas lo traen a tus pies, aunque estén reaccionando a ti), **tironeo** con E rápido (barra en el HUD; si pierdes se lo llevan) y **pilla-pilla** (huyen con el juguete; quitárselo = E). Juan S151: "contigo, entre ellas o contra ellas"
- [x] F6 · ✅ S151 Catálogo v1 de 7 juguetes, grandes y exagerados (arte provisional): pelota 1 m, mordedor, manguera, trapeador, **cuerda** (tironeo entre dos), **peluche** (lo abrazan y descansan) y **máquina de burbujas** (las persiguen y revientan). Jugar juntos suma afinidad. Precios provisionales: cuerda 18, peluche 20, burbujas 35. Los juguetes viven en un área de juego (`ToyPlayArea`) y vuelven solos si quedan abandonados afuera
- [x] F7 · ✅ S149 Los juguetes se compran en la PC (pestaña Juguetes: pelota 15, mordedor 12, manguera 25) y solo aparecen con la Sala de juegos abierta

## G · Mantenimiento (el entretenimiento del día)

- [x] G1 · ✅ S149 Comederos que se vacían y hay que rellenar (E sobre el comedero; vacío = las criaturas no lo eligen)
- [x] G2 · ✅ S149 Bebederos con agua que se recarga (E o la manguera cerca; nuevo `Base_Bebedero` en el patio)
- [x] G3 · ✅ S149 Camas que se ensucian y hay que limpiar (sucia bajo 30 % = descansa a la mitad; E limpia)
- [x] G4 · ✅ S151 Charcos (S149) + **manchas de barro**: pelota, mordedor, cuerda y peluche dejan manchas al rodar o ir en la boca (`MessEmitter`, 15 % cada 3 m, tope 5 por juguete); el trapeador las limpia como a los charcos. Decisión de la IA (Juan no eligió entre popó y manchas)
- [x] G5 · ✅ S151 Quitarte el juguete de la mano pasó a ser el **tironeo** (F5); filmado en `Recordings/S151/toys.mp4`
- [x] G6 · ✅ S151 Tienda sucia (charcos + manchas) o estaciones vacías bajan las ofertas hasta ×0.75 (`ShopCleanliness`, campos en `CustomerPricing`) y el cliente se queja en su globo ("¡Qué sucio está esto!"). La cama sucia todavía no cuenta (su umbral es privado)

## C · Cáscara y arranque (C7 de `Index/28`)

- [x] C1 · ✅ S152 Pantalla de título: continuar / nueva partida (escena `Title` con diorama animado)
- [x] C2 · ✅ S151 v1 (plantilla; Juan: "aún no tenemos la UI oficial") **Pausa** con Esc (reanudar / ajustes / salir guardando; congela el tiempo; también en la arena) + **Ajustes por secciones**, guardados en el equipo (no en la partida): General (idioma), Video (modo, resolución, VSync, tope de FPS, calidad), Interfaz (nombres flotantes siempre / al mirar / nunca, escala del HUD, ayudas de teclas), Controles (sensibilidad, invertir Y, campo de visión), Audio (5 volúmenes, se oirán con el pack). Prefab `Prefabs/UI/PauseSettingsUI` en GameScene y ArenaSandbox. Juan pidió que sea "muy rico en opciones" e ir sumando secciones: siguen Accesibilidad (daltonismo, reducir movimiento, tamaño de texto), reasignar teclas, mando y balanceo de cámara (no existe todavía)
- [x] C3 · ✅ S152 Un solo dueño del flujo de escenas (título → tienda ↔ Brawl): `SceneFlow`
- [x] C4 · ✅ S152 Tutorial de 7 pasos hasta la primera bajada (guía en el piso, píldora, saltable); falta probar "Nueva partida" con cuenta vacía
- [x] C5 · ✅ S152 12 metas (pestaña "Metas" en la PC + aviso); abren Sala de juegos, Cuerda, Burbujas y Peluche
- [ ] C6 · Primera build de PC (destapa NavMesh, `Resources` y Odin)

## B · Run con decisiones (P0.3-P0.5 de `Index/33`)

- [ ] B1 · Bendiciones: elegir 1 de 3 al cerrar cada tramo (12-16 bendiciones)
- [ ] B2 · Sala de descanso (cura)
- [ ] B3 · Sala de tesoro y sala de evento (elegir entre dos)
- [ ] B4 · Élites con modificador: furioso, blindado, veloz, curandero (4-6)
- [ ] B5 · Jefes: un MoriMochi gigante con partes propias por paleta (4)
- [ ] B6 · Rivales que suben de nivel de partes con la profundidad (hoy siempre nivel 1 × multiplicador)
- [ ] B7 · La tarjeta de bajada y la vuelta muestran nivel y "+N combates"
- [ ] B8 · Permadeath encendida con aviso previo, despedida y memorial (hoy el flag está apagado y la run nunca reporta caídos)

## H · Clientes y valor de la criatura

- [x] H1 · ✅ S149 Cinco arquetipos: Fan de los roles, Artista (color), Coleccionista (set de partes, presupuesto alto), Ahorrador (barato) y Familia (paciente); presupuesto, gusto y paciencia propios
- [x] H2 · 🟡 S149 Eligen por gusto dentro de su presupuesto (si nada les gusta, a veces compran lo más barato y a veces se van); el globo dice qué buscan. ✅ S151 La contraoferta (una) se acepta según tolerancia + gusto (+40 % si le encanta) y el presupuesto que le queda; por encima del techo (presupuesto ×1.2) siempre la rechaza
- [x] H3 · ✅ S149 Valuación: nivel de partes + crías + rareza + shiny × cuidado (0.8-1.2) × gusto (+30-60 %); falta generación
- ~~H4 · Rareza real en las partes~~ — se cae (Juan S151): todas las partes son comunes; nada detrás de rarezas. La variedad viene del linaje y de buscar genes nuevos en el mercado
- [x] H5 · ✅ S151 **Pedidos**: 3 por día en la pestaña "Pedidos" de la PC ("Busco un MoriMochi de rol Protector · +15", "…con partes del set Carnero · +20"); vender a cualquier cliente uno que cumpla paga el extra y avisa ("Pedido cumplido"). Solo rol y set (el color no pasa el test del texto plano). Se guardan en el estado de mundo y se renuevan cada día (`OrderBoardService`)
- [ ] H6 · Modelo y animaciones de clientes: **pack comprado** (Juan S149)
- [x] H7 · ✅ S151 El cuidado paga (S149) y **Débil** (Juan S151): vida en 0 o anciano → se mueve a la mitad en la tienda y en la bajada pelea con −50 % de daño y velocidad (la vida no baja); la etiqueta dice "Débil" (`CreatureFrailty`)

## I · Audio y feel

- [ ] I1 · Pack de audio comprado: ~40 SFX + 3 pistas (tienda, run, jefe); hoy el juego es mudo
- [ ] I2 · Feedback MMF en la tienda (compra, venta, eclosión, evolución, juguetes)
- [ ] I3 · Textos del Brawl localizados (junto con la UI comprada)

---

## Fuera de este roadmap (después de cerrar el gameplay)

Trabajos asignables (E3 de `Index/28`) · linaje y Cutie Marks (H2) · rival real asíncrono y ferales (H3) · fenotipo, pelaje, formas de cuerpo (H4) · más partes · beta y lanzamiento (H9-H10). Siguen en [[Index/25 - Hitos hasta el lanzamiento]].

## Decisiones de Juan

**Resueltas (S149):** el corazón es el sim de crianza · la tienda crece por expansiones que desbloquean ítems · **se descarta el modo construcción libre: se decora en ranuras fijas por zona** · las decoraciones de breeding mueven probabilidades, mutación y peso de padre/madre/abuelos, y su efecto se descubre con misiones o criando · la manguera limpia y deja charcos, y los MoriMonchis pueden robar el trapeador · el Ring se quita · los clientes se compran en pack · rescate = llamada del tío con caja gratis · cada PC tiene su cuenta y su save · la IA tiene su propia consola de admin.

**Abiertas:** ninguna por ahora.
