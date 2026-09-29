---
tags: [script, store, data]
---

# CreatureBoxSO

**Ruta:** `Data/Store/CreatureBoxSO.cs`

**Responsabilidad:** Definición de caja de MoriMonchis para venta. Especifica cantidad, forma de criaturas (Egg/Slime/Adult, S137) y metadatos display (Id, nombre, descripción).

## Campos Públicos

| Campo | Tipo | Descripción |
|-------|------|----------|
| `Id` | `string` | Identificador único de la caja |
| `Form` | `MonchiForm` | **(S137 NUEVO)** Forma de las criaturas en la caja (Egg/Slime/Adult, default Egg) |
| `DisplayName` | `string` | Nombre mostrado en UI |
| `Description` | `string` | Descripción larga (text area) |
| `Count` | `int` | Cantidad de MoriMonchis que contiene (mín. 1) |

## Uso

- **StoreManager.BuyCreatureBox()** → instancia `DeliveryBox`, llama `Configure(CreatureBoxSO)`
- **StoreRows.Collect()** → itera `ShopCatalogSO.CreatureBoxListings` para armar rows de tienda
- **DeliveryBox.Interact()** → abre caja, mintea `Count` criaturas con Form especificado (S137), dispara único `OnRegistryChanged`
- **UI Filters** → filtran cajas por Form (S137: mostrar caja de huevos o adultos según disponibilidad)

## Cambios S137

**Nuevo campo:**
```csharp
public MonchiForm Form = MonchiForm.Egg;
```

**Propósito:** Especificar qué forma tienen las criaturas al mintearlas. Default Egg (kit inicial).

**Consumidores:**
- `DeliveryBox.Interact()` → pasa Form a `GameManager.MintCreature(dna, Form)` (S137)
- `AutoPlayer.Step2_BuyEggBox()` → filtra cajas por `Form == MonchiForm.Egg`

## Integración S137

Ciclo de vida: Cajas de huevos (Form=Egg) son el entry point para nuevas criaturas. Los huevos necesitan incubadora (mueble F10) para eclosionar en slimes. Luego slimes exploran y evolucionan a adultos.

## Integración S130

Parte de la expansión C5 (catálogo de cajas de criaturas). Las cajas se venden como items entregables (`DeliveryBox`), similar a props del mundo (`ItemDefinitionSO`), pero en lugar de instanciar un prefab, mintean criaturas vía `GameManager.MintCreature()` y las lanzan por cañón.

## Vinculado a

- [[Index/04 - Store & Transactions]]
- [[Index/02 - Genetics & Breeding]] (S137: ciclo de vida)
- [[Index/09 - Active Context]] (S137: huevos iniciales)
- [[Index/28 - Cimientos y camino a Game Ready]]

**Conexiones:** [[StoreManager]], [[DeliveryBox]], [[ShopCatalogSO]], [[StoreRows]], [[GameManager]]
