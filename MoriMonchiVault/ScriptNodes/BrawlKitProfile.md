---
tags: [script, data, brawl, kit, role, struct]
---

# BrawlKitProfile.cs

**Ruta:** `Data/Brawl/BrawlKitProfile.cs`

**Responsabilidad:** Struct de solo lectura que resuelve el kit de combate de un MoriMochi a partir de su DNA: ala (`BrawlWingKitSO`), cuerno y espalda (`BrawlSkillSO`), sus temas visuales (`BrawlTheme`), si la espalda está bloqueada y el rol de combate sugerido (único, doble mayoría-minoría o Equilibrado). Es el único cálculo del rol: lo consumen la ficha, la tarjeta de expedición, la vuelta de la bajada y el combatiente. No es MonoBehaviour, no guarda estado mutable y no toca escena ni persistencia.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Wing` | `BrawlWingKitSO` | Kit de ala (null si no hay) |
| `Horn` | `BrawlSkillSO` | Habilidad del cuerno |
| `Back` | `BrawlSkillSO` | Habilidad de la espalda; null si la espalda está bloqueada |
| `WingTheme`, `HornTheme`, `BackTheme` | `BrawlTheme` | Icono y color por parte; `BackTheme` queda en default si la espalda está bloqueada |
| `BackLocked` | `bool` | La espalda está bloqueada porque el MoriMochi no es adulto (`Form != Adult`) |
| `Primary` | `BrawlSkillRole` | Rol principal |
| `HasSecondary` | `bool` | Hay rol secundario (minoría) |
| `Secondary` | `BrawlSkillRole` | Rol secundario; válido si `HasSecondary` |
| `Balanced` | `bool` | Las tres partes aportan roles distintos (Equilibrado) |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `static Of(dna, kits, parts)` | Resuelve el perfil: kits por `WingID`, `HornID` y, si la espalda no está bloqueada, `BackID` en `BrawlKitDatabaseSO` (cuerno y espalda con `ClashSlot`); partes en `CreatureDatabaseSO` (`GetWing`, `GetHorn`, `GetBack`) para los temas (`BrawlTheme.Resolve`). Con `dna`, `kits` o `parts` nulos, deja las partes sin kit |
| `HasRole(role)` | True si alguna de las tres partes aporta ese rol |
| `static WingRole(wing)` | `Support` si `AllyHeal > 0`; si no, `Offense` |
| `static RoleKey(role)` | Clave de `Loc`: `ui.brawlrole.control`, `.support`, `.tank`, `.offense` (default offense) |
| `static RoleClass(role)` | Clase CSS: `control`, `support`, `tank`, `offense` |

## Regla de Rol (`Resolve`)

- **Las tres partes con rol:** si las tres coinciden, rol único. Si dos coinciden, ese es el primario y el tercero el secundario (cuerno = espalda, cuerno = ala o espalda = ala). Si las tres son distintas, `Balanced = true` y el primario es el del cuerno, sin secundario.
- **Partes faltantes** (incluida la espalda bloqueada): el primario es el primer rol disponible en orden cuerno, espalda, ala; el secundario es el siguiente distinto.

## Conexiones

- [[BrawlRolePill]] — pinta primario, secundario o Equilibrado
- [[ExpeditionCardBuilder]] — poderes de tarjeta y detalle (espalda bloqueada incluida); `HasRole(Support)` para el aviso del equipo
- [[ExpeditionPanelUITK]] — perfil por criatura en cada `Rebuild`
- [[ExpeditionReturnCardUITK]] — poder nuevo de la espalda al crecer; sin fila si `Back` es null
- [[DetailInfoTabPresenter]] — rol de combate sugerido de la ficha y fila de espalda bloqueada
- [[BrawlFighter]] — `Bind` toma kits, temas, habilidades y `BackLocked` del perfil
- [[BrawlHudCard]] — slot de espalda con "?" si `BackLocked`
- [[BrawlKitDatabaseSO]] — búsqueda de kits por ID de parte
- [[CreatureDatabaseSO]] — partes para los temas
- [[BrawlTheme]], [[BrawlSkillRole]]

## Notas

- Un único cálculo para ficha, tarjeta de expedición, vuelta y combatiente: el rol que se muestra sale del mismo perfil que usa la pelea.
- Sin persistencia. Los valores vienen de los SO de kit y de las partes.
- S146: espalda bloqueada para formas no adultas (`BackLocked`). Ficha, tarjeta, HUD y vuelta la muestran con "?" en lugar del poder.
