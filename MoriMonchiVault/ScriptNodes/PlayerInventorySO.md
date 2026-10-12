---
tags: [scriptable-object, inventory, persistence]
---

# PlayerInventorySO

**Ruta:** `Data/Player/PlayerInventorySO.cs`

**Responsabilidad:** Dato persistente del jugador (SO). Contiene dos monedas (`Dabloons`, `Minerita`), decoraciones de cría en stock (sin colocar), props del mundo y 6 slots de hotbar. **S128:** métodos públicos `Balance()`, `Add()`, `TrySpend()`, `ResetCurrency()`; `adventureMaterial` renombrada a `minerita` con `[PreviouslySerializedAs]`. Nunca llama `SaveSystem` ni dispara eventos; lo hace [[Wallet]] (puerta única de mutaciones). **S129:** Eliminadas grillas de equipo y métodos de equipo (HC-1). **S149:** Eliminados los muebles del inventario (`furnitureOwned` y sus métodos). Se agrega el stock de decoraciones `decorOwned`.

## Campos Públicos (Serializados Odin)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `worldPropsStored` | `List<string>` | IDs de props del mundo (list: permite dupes) |
| `hotbarSlots` | `string[6]` | 6 slots hotbar (I# ids, persisten) |
| `dabloons` | `int` | Primera moneda (compras, venta, reembolso) |
| `minerita` | `int` | Segunda moneda (exploración, evolución); migrada de `adventureMaterial` (v1→v2) |
| `decorOwned` | `Dictionary<string, int>` | **(S149)** Decoraciones de cría sin colocar (id → cantidad) |

## Métodos Públicos

### Monedas (S128+)

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `Balance(Currency c)` | `int` | Lee saldo de moneda (Dabloons o Minerita) |
| `Add(Currency c, int amount)` | `void` | Suma cantidad a moneda (ignora amount <= 0; la validación de negocio la hace [[Wallet]]) |
| `TrySpend(Currency c, int amount)` | `bool` | Intenta gastar; si saldo < amount o amount <= 0 → false; si ok → gasta, retorna true |
| `ResetCurrency(Currency c)` | `void` | Pone la moneda en 0 (S149: sin parámetro de valor) |

### Decoraciones (S149)

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `DecorOwned` (property) | `IReadOnlyDictionary<string, int>` | Stock de decoraciones |
| `DecorCount(string id)` | `int` | Cantidad en stock (0 si no hay) |
| `AddDecor(string id, int amount = 1)` | `void` | Suma al stock |
| `TryTakeDecor(string id)` | `bool` | Saca una unidad; false si no hay |

Uso: `DecorSlot` devuelve la decoración actual con `AddDecor` y toma la siguiente con `TryTakeDecor`. `StoreManager.BuyDecor` suma al stock.

### Props del Mundo

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `AddWorldProp(string id)` | `void` | Añade prop (permite dupes) |
| `RemoveWorldProp(string id)` | `bool` | Remueve primera instancia de prop |
| `ClearWorldPropsStored()` | `void` | Vacía los props guardados |
| `WorldPropsStored` (property) | `IReadOnlyList<string>` | Read-only lista de props |

### Hotbar

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `SetHotbarSlot(int slot, string id)` | `void` | Setea ID en slot 0-5; ignora si fuera de rango (S149: antes devolvía bool) |
| `GetHotbarSlot(int slot)` | `string` | Lee ID del slot (null si vacío o fuera de rango) |
| `ClearHotbarSlot(int slot)` | `void` | Vacía slot |
| `ClearHotbar()` | `void` | Vacía los 6 slots |
| `HotbarSlots` (property) | `string[]` | Arreglo de slots |

### Persistencia

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `LoadFrom(InventoryData data)` | `void` | Carga desde [[SaveSystem]]; null → valores por defecto |
| `GetData()` | `InventoryData` | Retorna struct serializable para guardar (copias) |
| `MarkDirty()` | `void` | Privado en S149. Marca el SO como sucio en el editor |

## InventoryData (S149)

Campos: `WorldPropsStored`, `HotbarSlots`, `Dabloons`, `Minerita`, `DecorOwned`. Ya no tiene campo de muebles.

## Monedas S128

```csharp
public enum Currency { Dabloons, Minerita }
```

**Dabloons:** compras en tienda, venta de criaturas, reembolso de muebles.

**Minerita:** ganada en expediciones, usada en evolución. Antes `AdventureMaterial` (v1, migrada a v2).

## Migración v1 → v2

```csharp
[OdinSerialize, ReadOnly, PreviouslySerializedAs("adventureMaterial")]
private int minerita;
```

Odin `[PreviouslySerializedAs]` + [[SaveMigrations]] v1→v2 renombran `AdventureMaterial` → `Minerita`.

**Borrados:** `PassiveMaterial`, `EvolutionEssence` (v1 solo).

## Cambios S129

- **ELIMINADO:** Campo `equipmentGrids` y métodos de equipo (HC-1)
- **ELIMINADO:** `AddEquipment()`, `RemoveEquipmentAt()`, `EquipmentAt()`, `GridFor()`, `CellCountOf()`

## Cambios S149

- **ELIMINADO:** `furnitureOwned`, `AddFurniture()`, `HasFurniture()`, `FurnitureOwned`, y el campo de muebles en `InventoryData`.
- **AGREGADO:** `decorOwned` con `DecorOwned`, `DecorCount`, `AddDecor`, `TryTakeDecor`.
- **CAMBIO DE FIRMA:** `ResetCurrency` sin valor; `SetHotbarSlot` void; `HotbarSlot` renombrado a `GetHotbarSlot`.

## Patrón de Acceso

**Nunca mutación directa:**

```csharp
// ❌ NO:
GameManager.CurrentInventory.dabloons -= 50;

// ✅ SÍ:
Wallet.TrySpend(Currency.Dabloons, 50, "buy_ring");
```

[[Wallet]] es la puerta única. Registra en log, dispara `GameEvents.InventoryChanged`, persiste.

## CreateAssetMenu

**Menu path:** `RunRunSimulator/Player/Player Inventory`

## Vinculado a

[[Index/28 - Cimientos y camino a Game Ready]] (§3 · dos monedas)
[[Index/29 - Plan HC - Cimientos (ejecutable)]] (§5 · C3 cartera)

**Conexiones:** [[Wallet]], [[GameManager]], [[SaveSystem]], [[StoreManager]], [[GameEvents]], [[DecorSlot]], [[BreedingDecorSO]], [[StoreRows]]
