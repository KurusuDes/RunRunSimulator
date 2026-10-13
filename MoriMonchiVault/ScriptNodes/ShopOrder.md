---
tags: [script, data, store, orders, serializable]
---

# ShopOrder.cs

**Ruta:** `Data/Store/ShopOrder.cs`

**Responsabilidad:** Encargo diario de la tienda: pide un tipo de criatura por Role o por set de partes y ofrece una recompensa en dabloons. Serializable. Convierte el encargo en un `CustomerTaste` para que el match de clientes lo evalúe igual que un gusto normal.

## Campos publicos

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `Kind` | `TasteKind` | `PartSet` o `Role` |
| `Role` | `Role` | Rol pedido (si `Kind == Role`) |
| `SetName` | `string` | Nombre del set pedido (si `Kind == PartSet`) |
| `Reward` | `int` | Dabloons al completar |

## Metodos publicos

| Metodo | Descripcion |
|--------|-------------|
| `ToTaste(CreatureDatabaseSO db)` | Construye `CustomerTaste`; para `PartSet` busca el `PartSetSO` por nombre en Horns/Backs/Wings |
| `Describe()` | Texto localizado (`ui.orders.set` / `ui.orders.role`) |

## Conexiones

- [[OrderBoardService]] — genera, guarda y completa encargos
- [[WorldStateSO]] — persiste la lista `Orders`
- [[CreatureDatabaseSO]] — resuelve los sets por nombre
- [[CustomerTaste]] — destino del `ToTaste`
