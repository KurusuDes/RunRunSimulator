---
tags: [core, genetics, parts, filter, static]
---

# PartPool.cs

**Ruta:** `Core/PartPool.cs`

**Responsabilidad:** Filtro estatico que decide si una parte puede salir en una tirada (breeding, generacion inicial). Las partes de rol Horn, Back y Wing solo son rolleables si el banco visual tiene su malla (`MonchiVisualBankSO.HasPartMesh`). Body, Face y el resto siempre son rolleables. Sin `GameManager` o sin banco, devuelve true (fail-open).

## Metodos Publicos

| Metodo | Retorna | Descripcion |
|--------|---------|-------------|
| `Rollable(BodyPart part)` | `bool` | Predicado para `GetRandomPart(where: ...)`. Null = false |

## Consumidores

- `CreatureGenerator` (generacion inicial)
- `BreedingService` (tirada de cada rol al cruzar)

**Conexiones:** [[GameManager]], [[MonchiVisualBankSO]], [[BodyPart]], [[CreatureGenerator]], [[BreedingService]]
