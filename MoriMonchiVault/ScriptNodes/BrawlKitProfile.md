---
tags: [script, data, brawl, kit, role, struct]
---

# BrawlKitProfile.cs

**Ruta:** `Data/Brawl/BrawlKitProfile.cs`

**Responsabilidad:** Struct de solo lectura que resuelve el kit de combate de un MoriMochi a partir de su DNA: ala (`BrawlWingKitSO`), cuerno y espalda (`BrawlSkillSO`), sus temas visuales (`BrawlTheme`) y el rol de combate sugerido (único, doble mayoría-minoría o Equilibrado). Es el único cálculo del rol: lo consumen la ficha, la tarjeta de expedición y el combatiente. No es MonoBehaviour, no guarda estado mutable y no toca escena ni persistencia.

## Propiedades Públicas

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Wing` | `BrawlWingKitSO` | Kit de ala (null si no hay) |
| `Horn` | `BrawlSkillSO` | Habilidad del cuerno |
| `Back` | `BrawlSkillSO` | Habilidad de la espalda |
| `WingTheme`, `HornTheme`, `BackTheme` | `BrawlTheme` | Icono y color por parte |
| `Primary` | `BrawlSkillRole` | Rol principal |
| `HasSecondary` | `bool` | Hay rol secundario (minoría) |
| `Secondary` | `BrawlSkillRole` | Rol secundario; válido si `HasSecondary` |
| `Balanced` | `bool` | Las tres partes aportan roles distintos (Equilibrado) |

## Métodos Públicos

| Método | Descripción |
|--------|-------------|
| `static Of(dna, kits, parts)` | Resuelve el perfil: kits por `WingID`, `HornID` y `BackID` en `BrawlKitDatabaseSO` (cuerno y espalda con `ClashSlot`); partes en `CreatureDatabaseSO` (`GetWing`, `GetHorn`, `GetBack`) para los temas (`BrawlTheme.Resolve`). Con `dna`, `kits` o `parts` nulos, deja las partes sin kit |
| `HasRole(role)` | True si alguna de las tres partes aporta ese rol |
| `static WingRole(wing)` | `Support` si `AllyHeal > 0`; si no, `Offense` |
| `static RoleKey(role)` | Clave de `Loc`: `ui.brawlrole.control`, `.support`, `.tank`, `.offense` (default offense) |
| `static RoleClass(role)` | Clase CSS: `control`, `support`, `tank`, `offense` |

## Regla de Rol (`Resolve`)

- **Las tres partes con rol:** si las tres coinciden, rol único. Si dos coinciden, ese es el primario y el tercero el secundario (cuerno = espalda, cuerno = ala o espalda = ala). Si las tres son distintas, `Balanced = true` y el primario es el del cuerno, sin secundario.
- **Partes faltantes:** el primario es el primer rol disponible en orden cuerno, espalda, ala; el secundario es el siguiente distinto.

## Conexiones

- [[BrawlRolePill]] — pinta primario, secundario o Equilibrado
- [[ExpeditionCardBuilder]] — poderes de tarjeta y detalle; `HasRole(Support)` para el aviso del equipo
- [[ExpeditionPanelUITK]] — perfil por criatura en cada `Rebuild`
- [[DetailInfoTabPresenter]] — rol de combate sugerido de la ficha
- [[BrawlFighter]] — `Bind` toma kits, temas y habilidades del perfil
- [[BrawlKitDatabaseSO]] — búsqueda de kits por ID de parte
- [[CreatureDatabaseSO]] — partes para los temas
- [[BrawlTheme]], [[BrawlSkillRole]]

## Notas

- Un único cálculo para ficha, tarjeta de bajada y combatiente: el rol que se muestra sale del mismo perfil que usa la pelea.
- Sin persistencia. Los valores vienen de los SO de kit y de las partes.
