---
tags: [script, data, configuration]
---

# StarterKitSO.cs

**Ruta:** `Data/Player/StarterKitSO.cs`

**Responsabilidad:** ScriptableObject que define lo que recibe el player en partida nueva: moneda inicial (Dabloons, Minerita). Data-only, sin lógica. Wired en `StarterKitService` que lo aplica al detectar tutorial=0 y registry vacío. **S149:** Se eliminó la lista de muebles preconfigurados; el kit ya no entrega muebles.

## Campos Públicos

- `Dabloons` (int, default 0) — cantidad de moneda premium inicial (S137: 0, sin valor)
- `Minerita` (int, default 30) — cantidad de moneda de gameplay inicial para eclosionar/comprar en tienda

## Cambios S149

- **ELIMINADO:** `Furniture` (`List<FurnitureDefinitionSO>`). El sistema de muebles se borró.

## Invariantes

- Read-only en gameplay (wired via ScriptableObject ref, no modificable en runtime salvo por admin)
- Valores default están configurados en el asset

## Uso

Referenced by [[StarterKitService]] al inicio de partida nueva. No hay broadcast de cambios — el SO es simplemente una configuración inerte.

## Vinculado a

- [[Index/06 - Gameplay Loop]]
- [[Index/09 - Active Context]] (S137: kit inicial)

## Conexiones

- [[StarterKitService]] (único lector, aplica valores)
- [[Currency]] (Dabloons, Minerita)
