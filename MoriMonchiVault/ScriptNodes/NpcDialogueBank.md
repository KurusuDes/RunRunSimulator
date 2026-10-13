---
tags: [script, world, npc, data]
---

# NpcDialogueBank.cs

**Ruta:** `World/Npc/NpcDialogueBank.cs`

**Responsabilidad:** Clase estática pura que proporciona frases de diálogo para NPCs (S68: keys de localización en lugar de strings hardcodeados). Almacena arrays de keys (3-6 por situación; la resolución a idioma ocurre en `One()` via `Loc.Tr`). Sin estado mutable. **S151:** agrega el banco `dirty` (3 frases) que reemplaza al de aproximación y al de fila cuando el cliente vio la tienda sucia.

## Cambios S68 (Localization-ready)

**Antes:** Arrays de frases en español (e.g., `wandering[] = {"¿Qué tendrán hoy?", "A ver qué me encuentro…", ...}`)

**Ahora:** Arrays de keys de localización (e.g., `wandering[] = {"npc.wandering.01", "npc.wandering.02", ...}`)

**Método `One()`:**
```csharp
private static string One(string[] bank, string targetName) =>
    Loc.Tr(bank[Random.Range(0, bank.Length)], targetName);
```
- Elige una key aleatoria y la resuelve con `Loc.Tr(key, targetName)` → idioma activo + formato con {0}

**Datos privados (arrays de keys):**
- `wandering[]` (6 keys): vagando por la tienda sin objetivo.
- `inspecting[]` (6 keys): examinando una criatura en estante.
- `approaching[]` (5 keys): decidió comprar, va hacia caja. Usa `{0}` como placeholder del nombre MM.
- `queueing[]` (5 keys): espera en fila.
- `waiting[]` (5 keys): frente de fila, esperando respuesta del jugador.
- `negotiating[]` (5 keys): durante negociación con jugador. Usa `{0}` para nombre MM.
- `purchased[]` (5 keys): compró exitoso. Usa `{0}` para nombre MM.
- `outbid[]` (5 keys): otro cliente compró su objetivo. Usa `{0}` para nombre MM.
- `queueFull[]` (5 keys): no pudo entrar a la fila.
- `noDeal[]` (5 keys): se va sin comprar (rechazó contraoferta, timeout, etc.).
- `dirty[]` (3 keys, `npc.thought.dirty.*`) **(S151)**: queja por la tienda sucia. Se usa en lugar de `approaching[]` y `queueing[]`.

**Método público:**
- `Pick(NpcAgent.NpcState state, NpcAgent.LeaveReason reason, string targetName, bool complainedDirty = false) → string`: devuelve una frase aleatoria formateada con `targetName`, según el estado actual del cliente.
  - `Wandering` → `wandering[]`; `InspectingDisplay` → `inspecting[]`; `WaitingAtRegister` → `waiting[]`; `Negotiating` → `negotiating[]`.
  - `ApproachingRegister` y `Queueing` **(S151)**: `dirty[]` si `complainedDirty`, si no `approaching[]` / `queueing[]`.
  - `Leaving`: según `reason`: `Purchased` → `purchased[]`, `Outbid` → `outbid[]`, `QueueFull` → `queueFull[]`, otro (None) → `noDeal[]`.
  - Otro estado → cadena vacía.
  - Reemplaza `{0}` en la frase localizada con `targetName` usando parámetro args en `Loc.Tr(key, targetName)`.

**Datos por situación (resumen de contenido):**

| Situación | Estado | Clave | Contenido |
|-----------|--------|-------|----------|
| Explorando | Wandering | vagancia | Curiosidad, exploración, expectativa. |
| Inspeccionando | InspectingDisplay | análisis | Deliberación, indecisión, observación. |
| Yendo a caja | ApproachingRegister | decisión | Entusiasmo por la criatura elegida (con nombre). Si la tienda estaba sucia (S151): queja. |
| Fila de espera | Queueing | paciencia | Tolerancia, aburrimiento, impaciencia. Si la tienda estaba sucia (S151): queja. |
| Frente de caja | WaitingAtRegister | impotencia | Llamadas de atención, golpeteo, fastidio. |
| Negociando | Negotiating | regateador | Preguntas sobre precio (con nombre MM). |
| Compró feliz | Leaving + Purchased | victoria | Alegría, satisfacción, promesa de cuidado (con nombre). |
| Perdió subasta | Leaving + Outbid | derrota | Decepción, arrepentimiento, reclamo (con nombre). |
| Fila llena | Leaving + QueueFull | impotencia | Queja por aglomeración, sin nombre. |
| Se va vacío | Leaving + None/Other | resignación | Conformismo, próxima oportunidad, sin nombre. |

**Notas de implementación:**
- Cada array tiene 3-6 keys para evitar repetición (Random.Range sortea índice).
- Los placeholders `{0}` en frases se reemplazan via `Loc.Tr(key, targetName)` (Unity Localization resuelve args en la tabla).
- No hay estado privado ni inicialización: es puramente funcional.
- Consumidor único: [[NpcThoughtTag]] llama `Pick()` en `UpdateThought()` cuando detecta cambio de situación.

**Vinculado a:** [[Index/04 - Customer System]], [[Index/14 - Localization]]

**Conexiones:** [[NpcThoughtTag]] (único consumidor), [[NpcAgent]] (lee Estado, LeaveReason y ComplainedDirty), [[NpcNameBank]] (patrón paralelo), [[Loc]] (resolución localización), [[ShopCleanliness]] (origen de la suciedad, S151)
