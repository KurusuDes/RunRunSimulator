---
tags: [script, core, interface, focus]
---

# IFocusLabel.cs

**Ruta:** `Core/IFocusLabel.cs`

**Responsabilidad:** Contrato de rótulo de foco. Un componente del mundo que implementa esta interfaz aporta un título y un detalle que `PlayerFocusProbe` expone al apuntar y `FocusPromptUITK` muestra en el aviso contextual. Reemplaza los TMP flotantes que tenían los muebles (S161).

**Vinculado a:** [[Index/05 - UI System]]

## Miembros

| Miembro | Tipo | Descripción |
|---------|------|-------------|
| `FocusTitle` | `string` (get) | Título del rótulo (nombre o estado del objeto). Puede ser `null` para no mostrar título |
| `FocusDetail` | `string` (get) | Línea secundaria opcional. Puede ser `null` |

## Implementadores

- [[StationSupply]] — título con el nivel de suministro (comida, agua, limpieza)
- [[DecorSlot]] — título con el nombre de la decoración (o "desconocida" / "vacía")

## Conexiones

- [[PlayerFocusProbe]] — lee la primera implementación encontrada en el raycast (`CurrentLabel`)
- [[FocusPromptUITK]] — pinta `FocusTitle` y `FocusDetail`

## Notas

- Namespace `MoriMonchiSimulator`, sin comentarios en código.
- Interfaz pura: no tiene estado ni dependencias.
