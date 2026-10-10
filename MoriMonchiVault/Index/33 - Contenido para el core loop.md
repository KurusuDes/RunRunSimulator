---
tags: [index, roadmap, contenido, core-loop]
---

# 33 - Contenido para el core loop (S147)

> Pedido de Juan (2026-10-10): *"arma una lista de todo lo que nos falta y necesitamos de contenido para tener un buen core loop"*. Inventario contado sobre `Assets/RunRunSimulator/` y el vault (S147). Complementa [[Index/28 - Cimientos y camino a Game Ready]] (obra) y [[Index/25 - Hitos hasta el lanzamiento]] (jugador). La UI se compra aparte (Juan, S147): acá no entra pulido de UI.

## 0 · El loop y dónde se corta

```
Día (tienda): cuidar → criar → vender ──► dabloons ──► muebles / mejoras / bajar (10)
Noche (bajada): run de Brawl por tramos ──► Minerita ──► eclosionar / breeding room
                                                    ✗ evolucionar partes / cambiar poderes
```

**Regla:** un buen core loop pide que cada vuelta cambie algo en la siguiente. Hoy la Minerita solo vuelve como huevos; ningún gasto hace al equipo más fuerte abajo ni más valioso arriba, y la run no tiene nada que decidir más allá de "seguir o salir".

## 1 · Inventario (lo que hay)

| Área | Hay | Nota |
|---|---|---|
| Partes | 16 cuernos · 16 espaldas · 6 alas · 4 cuerpos · 2 caras · 53 pelajes · 17 sets | 31/38 con malla; faltan Ariete, Alforja, Cola, Coraza, Cresta, Colibrí, Vela. Todas con `Rarity 0` |
| Brawl | 33 habilidades en 10 familias · 6 alas · 4 roles | Balance cerrado S144 |
| Run | 3 tipos de sala (combate, muñecos, minerales) · 5 formas · 4 paletas | Sin élites, jefes ni rivales con identidad |
| Economía | Dabloons: 9 muebles, 2 ítems, 2 cajas, 1 mejora (vitrina 3 niveles), bajar 10 · Minerita: eclosionar, breeding room | Sin sink de Minerita ligado al Brawl |
| Tienda | 3 clientes (idénticos) · 3 necesidades · 3 estaciones de cuidado | Sin encargos; trapeador sin efecto |
| Cría | huevo → blobim → adulto (3 exploraciones) · 6 genes · herencia 50/30/20 | Sin evolución de partes ni marcas |
| Progresión | Reloj de 4 bloques · kit inicial | 0 metas, 0 desbloqueos, tutorial = 1 número |
| Audio | **0 clips propios** | El juego es mudo |

## 2 · Lo que falta, por prioridad

### P0 · Cerrar el loop (sin esto no hay "una vuelta más")

| # | Contenido | Cantidad mínima | Por qué |
|---|---|---|---|
| 1 | **Gasto de Minerita en poderes** (E2.2): cambiar o rerollear el poder de una parte en la ficha | 1 regla + precios | Une bajada → cría → bajada; cambia el rol sugerido y balancea el equipo |
| 2 | **Evolución de partes** (E2.3): subir el nivel de una parte con Minerita = más poder en el Brawl y más valor en venta | 3 niveles por parte (techo = potencial) | Segundo sink; da progreso visible a la criatura |
| 3 | **Recompensas dentro de la run** (estilo Another Door): bendiciones o reliquias que se eligen tras ciertas salas y duran la run | 12-16 bendiciones | La run necesita decisiones además de "seguir o salir" |
| 4 | **Salas nuevas**: descanso (cura; el glifo corazón ya existe), tesoro (botín sin pelea con trampa o costo), élite (rival con un modificador), evento (elegir entre dos) | +4 tipos (de 3 → 7) | Variedad entre tramos; el plan pide ≥5 |
| 5 | **Rivales con identidad**: élites con modificador (furioso, blindado, veloz, curandero) y **un jefe por paleta** al cerrar el tramo 3 | 4-6 modificadores · 4 jefes | Hoy todos los rivales son MoriMonchis al azar escalados |
| 6 | **Encargos de clientes**: piden un rol, una parte o un color y pagan extra | 8-12 plantillas | Hace que criar tenga objetivo en la tienda |
| 7 | **Clientes distintos de verdad** (E1.2): presupuesto, gusto y paciencia diferentes | 3 arquetipos con datos propios (+2 nuevos) | Hoy los 3 son idénticos y eligen la más cara |
| 8 | **Audio mínimo del loop**: SFX de golpe, KO, habilidad por familia, botín, compra, venta, eclosión, UI; música de tienda, de run y de jefe | ~40 SFX + 3 pistas | Sin sonido no hay feel |
| 9 | **Mallas de las 7 partes que faltan** | 7 modelos (o sacarlas del pool) | Hoy pueden salir partes sin malla |

### P1 · Profundidad (la vuelta 10 se siente distinta de la 1)

| # | Contenido | Cantidad | Nota |
|---|---|---|---|
| 10 | Mejoras de tienda (E1.3): corrales, clientes simultáneos, segunda incubadora, almacén | 4-5 mejoras × 3 niveles | Hoy solo hay la vitrina |
| 11 | Muebles con efecto (E1.5) y decorativos | de 9 → ~20 | Cada categoría hace algo enunciable en una frase |
| 12 | Ítems y juguetes | de 2 → ~8 | Comida que sube afecto, juguete que entretiene sin el jugador |
| 13 | Rareza real en partes + valuación que la mire (E1.1) | 5 rarezas repartidas en las 38 partes | Hoy todas son `Rarity 0` |
| 14 | Metas y desbloqueos: paletas, salas y muebles que se abren al llegar a un tramo o a una venta | 10-15 metas | Da dirección a la sesión |
| 15 | Trabajos de criaturas (E3) | 5 trabajos | Lo que hace una criatura mientras no baja |
| 16 | Suciedad y limpieza (E1.6) | 1 sistema + trapeador con efecto | Entretenimiento de la tienda |
| 17 | Paletas de arena | de 4 → 6 (una nocturna de verdad, una de cueva) | Con la atmósfera de S147 cada una tiene su ambiente |
| 18 | Tutorial con pasos reales | 6-8 pasos hasta la primera bajada | Hoy es un número que solo usa el kit inicial |
| 19 | Formas de cuerpo adulto | +3 cuerpos (`Index/31`) | Fenotipo |

### P2 · Después del loop (ya planeado en los hitos)

Cutie Marks y linaje (H2) · rival real asíncrono y ferales (H3) · permadeath con despedida y memorial · localización de la arena · cosméticos · el ambiente moldea los rasgos.

## 3 · Orden propuesto

1. **P0.1 + P0.2** (sinks de Minerita en la ficha): una sesión; cierra el loop de dos monedas (H1 de `Index/28` §5).
2. **P0.3-P0.5** (run con decisiones): bendiciones + 2 salas nuevas + élites; después jefes. Dos o tres sesiones.
3. **P0.6-P0.7** (tienda con objetivos): encargos y clientes. Una o dos sesiones.
4. **P0.8** audio y **P0.9** mallas: en paralelo (assets externos o artista).
5. P1 por lotes según lo que pida el playtest.

## 4 · Decisiones de Juan (bloquean P0)

1. **Poderes (E2.2):** ¿el cambio de poder se hereda a las crías? ¿Cuántas opciones se ofrecen por parte (2 o 3)? Los precios los fija la IA.
2. **Bendiciones de run:** ¿se eligen tras cada combate ganado o solo al cerrar un tramo?
3. **Jefes:** ¿MoriMonchis gigantes con partes propias o criaturas de otra especie?
4. **Audio:** ¿se compra un pack (como la UI) o se sintetiza?
5. **Las 7 partes sin malla:** ¿se modelan ahora (Blender) o salen del pool hasta que lleguen?
