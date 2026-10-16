---
tags: [script, ui, uitk, store]
---

# TransactionPanelUITK.cs

**Ruta:** `UI/TransactionPanelUITK.cs`

**Responsabilidad:** Panel UITK de negociación de venta con tres columnas: cliente | MoriMochi (retrato real + runas + info) | oferta. Se abre cuando hay un cliente en el mostrador (`NpcAgent`) y actualiza sus labels al cambiar de cliente. Presentación pura: las acciones de Aceptar, Contraofertar y Rechazar las resuelve el sistema de clientes.

**Vinculado a:** [[Index/04 - Store & Transactions]], [[Index/05 - UI System]]

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `document` | `UIDocument` | Documento del panel (serializado) |
| `root` | `VisualElement` | Raíz del panel |
| `mmPortrait` | `VisualElement` | Retrato real del MoriMochi en venta (S161) |
| `mmRunes` | `VisualElement` | Runas que enmarcan el retrato (S161; reemplazan el gris anterior) |
| `currentCustomer` | `NpcAgent` | Cliente actual en el mostrador |

## Métodos

| Método | Descripción |
|--------|-------------|
| `OnEnable` / `OnDisable` | Suscribe y desuscribe el cambio de cliente |
| `Update()` | Revisa si el panel debe estar visible (`IsShown`) y dispara `OnShown` / `OnHidden` |
| `EnsureBound()` | Resuelve los elementos del UXML una sola vez |
| `HandleCustomerChanged(next)` | Cambia el cliente actual y refresca |
| `Refresh()` | Llena retrato, runas, información del MoriMochi y oferta. Edad en días con `CreatureDNA.AgeDays(GameClock.Instance.Day)` (S131) |
| `OnAccept()` / `OnCounter()` / `OnReject()` | Botones: aceptar la oferta, pedir más (una sola vez) o rechazar |

## Botones

| Botón | Acción |
|-------|--------|
| Accept | Acepta la oferta y cierra |
| Counter | Pide más (si no contraofertó antes) |
| Reject | Rechaza y cierra |

## Conexiones

- [[GameClock]] — `Day` para la edad
- [[CreatureDNA]] — `AgeDays`, género y datos del MoriMochi
- [[NpcAgent]] — cliente en el mostrador
- [[CustomerService]] — ofertas y decisiones del cliente
- [[MonchiPortraitUI]] — retrato

## Notas

- Edad en días ("Xd") desde S131.
- S161: retrato real y runas en la columna central, con el kit de Synty.
