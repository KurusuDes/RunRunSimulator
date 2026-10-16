---
tags: [script, data, customers]
---

# HumanBodyCatalogSO.cs

**Ruta:** `Data/Customers/HumanBodyCatalogSO.cs`

**Responsabilidad:** ScriptableObject (`SerializedScriptableObject` de Odin) que guarda los cuerpos humanos de los clientes NPC, el arquetipo al que pertenece cada uno y sus pieles posibles. Elige un cuerpo y una piel al azar filtrando por arquetipo. Es data pura: no tiene eventos ni persistencia. El editor `HumanBodyAssembler` lo escribe.

**Vinculado a:** [[Index/06 - Player & World]], [[Index/04 - Customer System]], [[NpcAgent]]

**Conexiones:** [[NpcBody]] (único consumidor, vía `TryPick`), [[HumanBodyAssembler]] (genera el asset), [[CustomerArchetypeSO]] (filtro de cada entrada), [[NpcAgent]] (los clientes que usan el cuerpo)

## Asset

- Creable desde el menú `RunRunSimulator/Customers/Human Body Catalog`.
- Asset generado en `Resources/Data/Humans/HumanBodyCatalog.asset`.

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Bodies` | `List<Entry>` | Cuerpos disponibles (sección `[Title("Bodies")]`) |
| `Entry.Archetype` | `CustomerArchetypeSO` | **S163:** arquetipo al que pertenece el cuerpo |
| `Entry.Body` | `GameObject` | Prefab del cuerpo (Animator `HumanNpcSK`, o `HumanNpcSK_Femn` si es femenino) |
| `Entry.Skins` | `List<Material>` | Variantes de piel posibles para ese cuerpo (1 para elfos) |

## Método

**`TryPick(CustomerArchetypeSO archetype, out GameObject body, out Material skin)`**: descarta entradas nulas o sin cuerpo y, si el arquetipo pedido tiene entradas propias, elige solo entre ellas; si no hay ninguna que coincida, elige entre todas las válidas. Elige una entrada al azar con `UnityEngine.Random` y luego una piel al azar dentro de esa entrada. Si la entrada no tiene pieles, `skin` queda null. Si no hay cuerpos válidos, loguea un warning y devuelve false.

## Quirks ⚠️

- **S163 fallback:** un arquetipo sin cuerpos propios cae a cualquier cuerpo del catálogo en vez de fallar. Un cliente puede verse con un cuerpo de otro arquetipo si falta el par en el catálogo.
- La piel se elige dentro de la entrada del cuerpo, no globalmente.
- Usa `UnityEngine.Random`, no el RNG de la partida: no es reproducible.
- No se espera que `Bodies` tenga entradas nulas, pero `TryPick` lo tolera.
