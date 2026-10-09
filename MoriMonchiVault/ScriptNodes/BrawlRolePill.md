---
tags: [script, ui, brawl, role, uitk]
---

# BrawlRolePill.cs

**Ruta:** `UI/BrawlRolePill.cs`

**Responsabilidad:** Builder estático de la píldora de rol de combate (UITK). Arma un `VisualElement` con uno o dos segmentos: rol primario, rol secundario en menor tamaño, o un único segmento "Equilibrado" cuando las tres partes aportan roles distintos. No tiene estado, no suscribe eventos y no decide el rol: lo recibe de `BrawlKitProfile`.

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `Build(in BrawlKitProfile profile)` | Si `Balanced`: un segmento `ui.brawlrole.balanced` (clase `balanced`). Si no: segmento primario y, si `HasSecondary`, segmento secundario con `--minor` |
| `Build(BrawlSkillRole role)` | Píldora de un solo segmento con ese rol |

## Clases CSS

| Clase | Uso |
|-------|-----|
| `mm-rolepill` | Contenedor de la píldora (los llamantes añaden su clase extra) |
| `mm-rolepill__seg` | Segmento |
| `mm-rolepill__seg--minor` | Segmento secundario |
| `mm-role--{control, support, tank, offense, balanced}` | Color del rol |

## Conexiones

- [[BrawlKitProfile]] — rol primario, secundario y `Balanced`; claves y clases por rol
- [[ExpeditionCardBuilder]] — pill en tarjeta, detalle y fila de equipo
- [[DetailInfoTabPresenter]] — rol de combate sugerido de la ficha
- [[Loc]] — textos de rol

## Notas

- Textos por `Loc`, a diferencia de `BrawlHud` y `BrawlRunPanel`, que siguen hardcodeados.
