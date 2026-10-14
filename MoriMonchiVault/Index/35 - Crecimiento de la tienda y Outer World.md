---
tags: [index, design, roadmap, tienda, outer-world]
---

# 35 - Crecimiento de la tienda y Outer World (S153)

> Juan S153: *"podrían haber 4 etapas marcadas en el crecimiento de la tienda y a su vez cada etapa con zonas que tienen mejoras internas; el dinero es todo lo relacionado a la tienda, mejoras e ítems, y la Minerita es todo lo que tiene que ver con los MoriMonchis (sus mejoras, evolución, hatchear)"*. Propuesta presentada en el artifact **Crecimiento de la tienda** (https://claude.ai/artifact/Rmzss7PkezmcKob4M5KE4N) y aprobada: *"me encantan, lograste alinearte con la visión que tengo del juego"*.
> Pedido de cierre S153: *"preparar lo que será el outer world, que es donde estarán las misiones y los NPCs"* → Parte 2 (DRAFT, sin decisiones de Juan todavía).

Relacionado: [[Index/34 - Roadmap de cierre del gameplay]] (lista viva; D = expansiones), [[Index/28 - Cimientos y camino a Game Ready]] (dos monedas, trabajos E3), arte en `Tools/Blender/props/README_props.md` (tandas 1-3, kit de madera de cuento).

---

## Parte 1 · Crecimiento de la tienda (APROBADO S153)

### 1.1 Regla de las monedas
**Si lo dejas en la tienda son dabloons; si lo llevas en el MoriMochi es Minerita.** Ninguna mejora de zona cuesta Minerita.
- Dabloons: abrir etapas y zonas, sus niveles, comida, juguetes, decoraciones, muebles, cajas de la tienda online. Se ganan vendiendo, con pedidos, metas y misiones.
- Minerita: eclosionar, evolucionar partes, reroll/cambio de habilidad, tratamientos que cambian al MoriMochi para siempre. Solo se gana bajando de noche.

### 1.2 Etapas y zonas (cada zona tiene 3 niveles; N1 = al abrirla)
Pasar de etapa: **cumplir las metas de la etapa** (reusa `GoalService`/`GoalSO`) **+ pagar la ampliación** en la PC (pestaña Expansiones, `ShopUpgradeSO`). Precios provisionales de la IA.

| Etapa | Nombre | Puerta | Zonas (N1 → N2 → N3) |
|---|---|---|---|
| 1 | El puestito | inicio | **Mostrador** 1→2→3 clientes · **Vitrina** 3→5→8 lugares · **Rincón de cuidado** 1 de cada → comedero/bebedero dobles → 2.ª cama y menos suciedad · **Incubadora** repisa 3 → repisa 6 → 2.ª incubadora · **Oficina (PC)** 3 → 4 pedidos/día y restock más seguido → 5 + pedido especial |
| 2 | Tienda del barrio | metas E1 + ~300 | **Criadero** 2 corrales×2 adultos → 6×4 → 10×6 + ranura de deco (E7) · **Sala de juegos** 1 estación → área grande + cuerda/peluche → 2.ª estación + burbujas · **Patio** bebedero → arenero (trabajo Escarbar) → manguera fija y charcos que se secan |
| 3 | Tienda famosa | metas E2 + ~1.200 | **Guardería** 3 cunas + trabajo Cuidar crías → 6 cunas, nacen con más afecto → la cría hereda un rasgo del cuidador · **Baño y peluquería** bañera sube cuidado → bono de un día → accesorios visibles · **Cocina de snacks** llena el doble → recetas de afecto/energía → golosina favorita · **Almacén** inventario +50 % → entregas al instante → inventario ×2 |
| 4 | Emporio MoriMonchi | metas E3 + ~3.000 | **Escenario** 1 exhibición/día → concursos por rol/set → coleccionista famoso · **Gimnasio** trabajo Entrenar (baja con súper) → 2 lugares → sparring sin riesgo · **Clínica** reposo (Débil en un día) → tratamiento instantáneo → retiro de veteranos con bono · **Sala del linaje** árbol gigante → decoraciones de cría avanzadas → ver genes de abuelos |

Ya existen hoy (E1 y E2 completas como zonas, sin niveles todavía salvo el Criadero). Nuevas: 8 (etapas 3 y 4).

### 1.3 Mapa de lotes
Local al centro junto a la calle (sur) · Criadero oeste · Sala de juegos este · patio detrás (todo ya en escena) · etapa 3 alrededor (Guardería noroeste, Almacén oeste del Criadero, Baño este de la Sala, Cocina noreste) · etapa 4 al fondo del terreno o en un segundo piso (decisión 3).

### 1.4 Decisiones abiertas (Juan no las respondió en S153; valores por defecto de la IA entre paréntesis)
1. ¿Las 16 zonas se quedan así? (sí)
2. ¿Pasar de etapa = metas + pago? (sí)
3. ¿Etapa 4 al fondo del terreno o segundo piso? (fondo del terreno: no exige escaleras ni NavMesh en altura)
4. Clínica: ¿reposo con dabloons y tratamiento instantáneo con Minerita? (sí, aplica la regla 1.1)

### 1.5 Material a crear (siguiente sesión) — orden sugerido
**Código (morimonchi-coder):**
- [ ] Etapa como dato: `ShopStageSO` (metas requeridas + precio + zonas que habilita) y nivel de etapa en `WorldState`; la pestaña Expansiones muestra la etapa actual, lo que falta y la ampliación.
- [ ] Niveles de zona como dato: cada `ShopUpgradeSO` de zona con 3 niveles (efecto en una frase + piezas de escena que aparecen por nivel). Hoy solo el Criadero tiene niveles.
- [ ] Aplicar los efectos de N2/N3 de las 8 zonas existentes (vitrina, mostrador, cuidado, incubadora, oficina, criadero, sala, patio). E7-E10 (cría rediseñada) entra aquí.
**Arte (Blender, agentes Opus, kit de `README_props.md` tanda 3):**
- [ ] Kit modular de zona: piso de tablones, pared de entramado (lisa / ventana / puerta), esquina, remate con hiedra, cartel de lote bloqueado (ya existe `ShopLockedSign`).
- [ ] Piezas por nivel de las zonas existentes: vitrina ampliada (5 y 8 lugares), segunda cama, comedero/bebedero grandes, segunda incubadora, arenero y manguera fija del patio, segunda estación de juego.
- [ ] Equipamiento de las 8 zonas nuevas (por zona ~3-5 props): cunas; bañera, secador, silla de peluquería; cocina, horno, frascos de recetas; estanterías de almacén; escenario con telón; aparatos de gimnasio; camilla y botiquín; árbol genealógico tallado.
- [ ] Arquitectura de los lotes nuevos (pisos y paredes) con el mismo método de la tanda 2 (OBJ de referencia + colliders de ProBuilder que no cambian).

---

## Parte 2 · Outer World: misiones y NPCs (DRAFT, para decidir con Juan)

> Uso del término: en S151 "outer world" se usó para el mundo de día (la tienda) frente a la bajada. Desde S153 Juan lo define como **el lugar fuera de la tienda donde están las misiones y los NPCs**.

### 2.1 Qué ya existe y se reutiliza
- La **calle** frente a la tienda ya tiene arte (`ShopStreet`, vereda, cruce, faroles, bancas) y es el NavMesh de los clientes (`NavMeshSurfaceStreet`).
- **NPCs**: `NpcAgent`/`NpcController`/`CustomerService` con 5 arquetipos (gusto, presupuesto, paciencia), globo de pensamiento (`NpcThoughtTag`), diálogos (`NpcDialogueBank`), nombres (`NpcNameBank`). Modelo y animaciones: pack comprado (H6, pendiente).
- **Encargos**: Pedidos de la PC (`OrderBoardService`, 3 por día, rol o set) y Metas (`GoalService`, 12 `GoalSO` con premio y desbloqueo).
- **El tío** (`UncleRescueService`) como personaje que ya "llama".
- **Reloj** con 4 bloques (`GameClock`): base para rutinas de NPC y misiones que duran bloques.
- **Bajada** (Brawl) y su entrada (`ExpeditionHandoff`, `SceneFlow`).

### 2.2 Propuesta
**Regla:** el barrio es un lugar al que sales de la tienda; ahí viven vecinos con nombre que te piden misiones, y cumplirlas trae dabloons, objetos y avanza las metas de etapa.

- **Espacio**: el barrio frente a la tienda (extensión de la calle actual): una plaza con el **tablero de misiones**, 4-6 casas o puestos de vecinos y, en un extremo, la **entrada a la bajada** (cueva / puerta de la noche). Mismo kit de madera de cuento.
- **Vecinos (4-6, con nombre y rutina por bloque del reloj)**: cada uno pide un tipo de misión y tiene amistad que sube al cumplirle. Ideas: el tío (historia y tutoriales de etapa), la veterinaria (cuidado y clínica), la panadera (snacks y recetas), el coleccionista (sets y partes raras), la niña del barrio (juegos y juguetes), el vendedor de genes del mercado (genes nuevos para el linaje; H4 de `Index/34` dijo que la variedad sale del mercado).
- **Tipos de misión** (todas enunciables en una frase):
  1. *Entrega*: traer un MoriMochi con rol/set/color (extiende los Pedidos).
  2. *Préstamo*: prestar un MoriMochi uno o más bloques (usa los trabajos E3 de `Index/28`).
  3. *Búsqueda*: traer algo de la bajada (ítem o Minerita) → une el día y la noche.
  4. *Cuidado*: dejar a un MoriMochi feliz/limpio/alimentado para una visita.
  5. *Historia*: cadena del tío, una por etapa, que presenta la ampliación.
- **Recompensas**: dabloons, decoraciones, recetas, juguetes, descubrir el efecto de una decoración (E5) y **contar como meta de etapa** (las misiones alimentan la Parte 1).
- **Los clientes** siguen llegando a la tienda por la calle; los vecinos son NPCs fijos distintos de los clientes de paso.

### 2.3 Decisiones para Juan (abrir la sesión con esto)
1. ¿El barrio es la misma escena que la tienda (se sale caminando por la calle) o una escena aparte (`SceneFlow`)?
2. ¿Cuántos vecinos en la v1 y cuáles? (propuesta: 4 — tío, veterinaria, coleccionista, vendedor de genes)
3. ¿Las misiones se toman en un tablero de la plaza, hablando con cada vecino, o las dos?
4. ¿La entrada a la bajada se mueve al barrio (caminar hasta la cueva) o sigue saliendo desde la tienda?
5. ¿Los vecinos usan el pack de NPCs comprado (H6) o se modelan estilo MoriMonchis/KayKit?

### 2.4 Material a crear para el Outer World (después de decidir)
- Arte: plaza, tablero de misiones, 4-6 fachadas de casas/puestos (mismo kit), entrada a la bajada, mobiliario de calle extra.
- Código: `QuestSO` (tipo, pedido, premio, vecino) + servicio de misiones dueño de su estado en `WorldState` (como `OrderBoardService`); `NeighborSO` (nombre, rutina por bloque, amistad); panel de misiones; integración con metas de etapa.
