---
tags: [script, world, npc, ui]
---

# NpcThoughtTag.cs

**Ruta:** `World/Npc/NpcThoughtTag.cs`

**Responsabilidad:** Burbuja de pensamiento world-space (UITK) sobre NPCs. Billboard hacia la cámara, con corte por distancia. Muestra diálogo dinámico en español de [[NpcDialogueBank]] según `NpcAgent.State` y `LeaveReason`. Cachea la frase y aplica el delay de reacción (`agent.ReactionDelay`) antes de mostrar una frase nueva, para evitar parpadeo. **S93:** usa `UiPanels.RootOf()` para resolver la raíz del UIDocument. **S149:** mientras el cliente recorre la tienda (Wandering o InspectingDisplay) muestra su gusto (`CustomerTaste.Describe()`) y lo tiñe si el gusto es de color.

**Propiedades serializadas:**
- `showDistance` (float, 12): distancia máxima a cámara para mostrar burbuja.
- `uprightOnly` (bool, true): si true, ignora camera pitch (mantiene etiqueta vertical).

**Ciclo:**
- `Awake()` → obtiene UIDocument, busca NpcAgent parent via `GetComponentInParent`, caché Camera.main.
- `LateUpdate()` → distance gate, billboard (LookRotation hacia cámara), `Refresh()`.
- `SetShown(bool)` → toggle display del root (Flex/None).
- `ResolveElements()` → queries UITK `npc-name-label` y `thought-label` del root.
- `Refresh()` → actualiza nameLabel, llama `UpdateThought()`.

**UpdateThought() - Lógica clave:**
- Detecta cambio de situación comparando tupla `(State, Reason)` contra `(lastState, lastReason)`.
- Al detectar cambio:
  - Extrae nombre target de `agent.TargetMM.CustomName` (fallback `npc.unnamed`).
  - Consulta `NpcDialogueBank.Pick(state, reason, name)` para obtener UNA frase random.
  - Cachea la frase en `pendingLine`.
  - Resetea `responseTimer = agent.ReactionDelay` (comienza cuenta atrás).
- Mientras `responseTimer > 0`: decrementa cada frame, mantiene `shownLine` con frase anterior (sin parpadeo).
- Cuando `responseTimer ≤ 0`: actualiza `shownLine = pendingLine`.
- **S149, navegando (Wandering o InspectingDisplay):** el texto es `agent.Taste.Describe()`, y si el gusto es de color el texto toma ese color. Fuera de navegación, muestra `shownLine` y quita el color.
- Renderiza `thoughtLabel.text` y oculta el label si el texto está vacío.

**nameLabel:**
- Muestra `agent.DisplayName` si no es vacío.
- Fallback: `agent.Archetype.DisplayName`.
- Fallback final: `npc.customer` (localizado).

**Requerimientos:**
- `[DisallowMultipleComponent]` — un nodo hijo del NPC por burbuja.
- `[RequireComponent(typeof(UIDocument))]` — necesita UIDocument en el mismo GameObject.

**Privados:**
- `lastState`, `lastReason` — cache de la última situación procesada.
- `situationInit` (bool) — flag para detectar primera vez.
- `pendingLine` (string) — frase nueva a mostrar (cached).
- `shownLine` (string) — frase visible actualmente (con delay aplicado).
- `responseTimer` (float) — cuenta atrás del delay de reacción.

**Vinculado a:** [[Index/06 - Player & World]]

**Conexiones:** [[NpcAgent]] (lee `State`, `Reason`, `ReactionDelay`, `TargetMM`, `DisplayName`, `Taste`), [[CustomerTaste]] (`Describe`, `Kind`, `Color`), [[NpcDialogueBank]] (consulta frases por situación), [[CreatureDNA]] (lee `CustomName`), [[CustomerArchetypeSO]] (fallback displayName), [[UiPanels]], [[Loc]]
