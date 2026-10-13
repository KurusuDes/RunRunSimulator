---
tags: [script, system, customer]
---

# NegotiationFlow.cs

**Ruta:** `Systems/Customers/NegotiationFlow.cs`

**Responsabilidad:** Clase pura (serializable, sin MonoBehaviour) que gestiona el flujo de negociación (cliente vs. jugador). Enum `NegotiationResult` (Accept/Reject). API: `ComputeCounter(int, CustomerPricingSO)` calcula contraoferta aumentando el precio en `RenegotiationStep`. **S151:** `EvaluateCounter` recibe ahora la oferta actual, el tope y el gusto: rechaza de entrada lo que supera el tope y, dentro del tope, decide por probabilidad.

## API

| Método | Retorno | Descripción |
|--------|---------|-------------|
| `ComputeCounter(int currentOffer, CustomerPricingSO pricing)` | `int` | `round(currentOffer * (1 + RenegotiationStep))`; si no hay pricing devuelve la oferta igual |
| `EvaluateCounter(CustomerArchetypeSO archetype, int currentOffer, int candidate, int ceiling, float tasteMatch)` | `NegotiationResult` | Ver regla abajo |

## Regla de EvaluateCounter (S151)

1. Si `candidate > ceiling` → **Reject** sin tirar dados.
2. Si no hay arquetipo → **Accept**.
3. `headroomUsed` = fracción del margen (`ceiling - currentOffer`) que consume la contraoferta, en 0..1.
4. `chance` = `clamp01(RenegotiationTolerance + 0.4 * tasteMatch) * (1 - 0.5 * headroomUsed)`.
5. Tira `Random.value <= chance` → Accept, si no → Reject.

Cuanto más gusto y más tolerancia, más probable aceptar; cuanto más cerca del tope, menos.

## Conexiones

- [[CustomerPricingSO]] — `RenegotiationStep`
- [[CustomerArchetypeSO]] — `RenegotiationTolerance`
- [[CustomerTaste]] — origen de `tasteMatch` (vía `ValuationHandler`/`NpcAgent`)
- [[CustomerService]], [[NpcAgent]] — consumidores

**Vinculado a:** [[Index/04 - Customer System]]
