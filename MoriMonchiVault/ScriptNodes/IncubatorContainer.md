---
tags: [script, gameplay, container]
---

# IncubatorContainer.cs

**Ruta:** `World/Containers/IncubatorContainer.cs`

**Responsabilidad:** Contenedor de MoriMonchis que acepta SOLO huevos (Form == Egg). Implementa `IInteractable`: `Interact()` busca el primer huevo en ocupantes, intenta eclosionarlo via `BreedingController.TryHatchEgg()`. Si éxito: despliega el slime con impulso (outward + upward), se sale del pen. Hereda ocupancia y física de `MoriMochiContainer`. Mueble F10 (S137).

## Herencia

- `MoriMochiContainer` (ocupancia, pen, fisicas)
- `IInteractable` (contrato UI/gameplay)

## Campos Serializados

- `hatchPopOut` (float, default 5) — impulso horizontal (salida) al eclosionar
- `hatchPopUp` (float, default 4) — impulso vertical (salto) al eclosionar

## Métodos Públicos

- `Interact()` — Busca primer huevo ocupante. Si existe, intenta `BreedingController.TryHatchEgg(eggAgent.DNA)`. Según resultado (Hatched/InsufficientMinerita/error), dispara `HatchOut()` o registra falla. Refs al gameObject físico + DNA.CustomName para debug.
- Hereda `Accepts()` — devuelve true si agent.DNA.Form == MonchiForm.Egg

## Métodos Privados

- `HatchOut(MoriMochiAgent agent)` — Solicita salida del pen (`RequestReleaseFromPen()`). Calcula impulso: vector away de center (y=0), normalizado si sqrMagnitude > 0.01, sino random. Aplica `away * hatchPopOut + Vector3.up * hatchPopUp` via `agent.Knock()`.

## Comportamiento

1. Spawn de huevo en incubadora: MoriMochiAgent entra a ocupancia (Form==Egg)
2. Player interactúa (Interact button)
3. BreedingController valida: ¿hay Minerita suficiente?
4. Si sí: TryHatchEgg() cambia Form.Egg → Form.Slime, dispara evento
5. HatchOut() suelta el agent con impulso diagonal, sale del pen
6. El slime ahora es controlable en la tienda
7. Si no: logging, se queda el huevo

## Invariantes

- Acepta SOLO huevos: el `Accepts()` heredado filtra por Form.Egg
- Interacción bloqueada si no hay huevos ocupantes o sin BreedingController
- HatchOut siempre usa Direction.Away from center (evita salida hacia pared)

## Vinculado a

- [[Index/02 - Genetics & Breeding]] (ciclo de vida S137)
- [[Index/06 - Gameplay Loop]] (incubadora como mueble)

## Conexiones

- [[MoriMochiContainer]] (ocupancia heredada)
- [[IInteractable]] (UI/gameplay)
- [[MoriMochiAgent]] (occupant, físicas)
- [[BreedingController]] (TryHatchEgg, costo)
- [[MonchiForm]] (Egg → Slime)
- [[GameEvents]] (OnCreatureFormChanged disparado por BreedingController)
