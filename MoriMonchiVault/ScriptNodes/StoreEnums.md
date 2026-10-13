---
tags: [enum, store, economy]
---

# StoreEnums

**Ruta:** `Core/Enums/StoreEnums.cs`

**Responsabilidad:** Enumeraciones para tienda, props y juguetes. Contiene: `ItemType` (2 tipos), `WorldPropCategory` (4 categorías), `BuyResult` (5 resultados), `Currency` (2 monedas), `ToyKind` (7 tipos de juguete), `TasteKind` (4 tipos de gusto de cliente), `StoreItemTypeFilter` (flags de filtro). **S151:** se retiró `FurnitureCategory` (ya no existe en el archivo; el sistema de muebles se borró en S149) y `WorldPropCategory` gana `Toy`; `ToyKind` y `TasteKind` viven aquí. **S152:** `BuyResult` gana `Locked`.

## Enumeraciones Vigentes

| Enum | Valores | Descripción |
|------|---------|-------------|
| `ItemType` | Furniture (0), WorldProp (1) | Tipo de item |
| `WorldPropCategory` | Tool (0), Food (1), Medicine (2), Toy (3) | Categoría de prop spawnable (Toy: S151) |
| `BuyResult` | Success (0), OutOfStock (1), InsufficientFunds (2), AlreadyOwned (3), Locked (4) | Resultado de compra (Locked: S152) |
| `Currency` | Dabloons (0), Minerita (1) | Moneda (S127) |
| `ToyKind` | Ball, Chew, Hose, Mop, Rope, Plush, Bubbles | Tipo de juguete (S151) |
| `TasteKind` | None (0), Role (1), Color (2), PartSet (3) | Tipo de gusto de cliente / encargo (S151) |
| `StoreItemTypeFilter` | Flags: Furniture (1), WorldProp (2), None (0) | Filtro de búsqueda |

## Historial

**S93:** Consolidación en archivo dedicado.
**S128:** ItemTriggerKind eliminado.
**S131:** DiscountDay/Month/RestockPeriod eliminados (simplificación a calendario de juego). Reemplazados por aritmética de día (`day % N`).
**S149:** Sistema de muebles borrado; `FurnitureCategory` queda fuera del archivo desde entonces.
**S151:** Agregados `ToyKind`, `TasteKind` y `WorldPropCategory.Toy`. Retirado `FurnitureCategory` del archivo.
**S152:** `BuyResult.Locked`: compra rechazada porque una meta (`GoalSO`) aún no se cumple.

## Vinculado a

- [[Index/04 - Store & Transactions]]
- [[Index/09 - Active Context]]

## Conexiones

**Data:**
- [[ItemDatabaseSO]], [[ItemDefinitionSO]]
- [[ToyTuningSO]] — los juguetes usan `ToyKind`
- [[ShopOrder]] — usa `TasteKind` y `Role`

**Sistemas:**
- [[ShopCatalogSO]] — consume Currency, BuyResult, Filter
- [[StoreManager]] — retorna BuyResult (incluye `Locked` por metas, S152)
- [[StorePanelUITK]] — filtra con StoreItemTypeFilter; muestra aviso para `Locked`
- [[OrderBoardService]] — genera encargos con `TasteKind`
- [[GoalService]] — origen de `Locked` (S152)

## Notas (S131 HC-4)

- **Simplificación:** Calendario real (mes/semana) → días de juego (0, 1, 2, ...).
- **Módulo:** `day % N == 0` es patrón para repetición de eventos cada N días.
- **Currency:** Dabloons (abundante) vs Minerita (escaso) para economía dual S127+.
