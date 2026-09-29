---
tags: [script, data, configuration]
---

# StarterKitSO.cs

**Ruta:** `Data/Player/StarterKitSO.cs`

**Responsabilidad:** ScriptableObject que define lo que recibe el player en partida nueva: moneda inicial (Dabloons, Minerita) y muebles preconfigurados. Data-only, sin lógica. Wired en `StarterKitService` que lo aplica al detectar tutorial=0 y registry vacío.

## Campos Públicos

- `Dabloons` (int, default 0) — cantidad de moneda premium inicial (S137: 0, sin valor)
- `Minerita` (int, default 30) — cantidad de moneda de gameplay inicial para eclosionar/comprar en tienda
- `Furniture` (List<FurnitureDefinitionSO>) — lista de muebles que se agregan al inventario (S137: contiene Incubadora F10)

## Invariantes

- Read-only en gameplay (wired via ScriptableObject ref, no modificable en runtime salvo por admin)
- Furniture list puede contener nulls (StarterKitService filtra)
- Valores default están configurados en el asset

## Uso

Referenced by [[StarterKitService]] al inicio de partida nueva. No hay broadcast de cambios — el SO es simplemente una configuración inerte.

## Vinculado a

- [[Index/06 - Gameplay Loop]]
- [[Index/09 - Active Context]] (S137: kit inicial)

## Conexiones

- [[StarterKitService]] (único lector, aplica valores)
- [[FurnitureDefinitionSO]] (lista de muebles)
- [[Currency]] (Dabloons, Minerita)
