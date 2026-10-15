---
tags: [script, data, customers]
---

# HumanBodyCatalogSO.cs

**Ruta:** `Data/Customers/HumanBodyCatalogSO.cs`

**Responsabilidad:** ScriptableObject (`SerializedScriptableObject` de Odin) que guarda los cuerpos humanos de los clientes NPC y las pieles posibles de cada uno. Elige una combinación al azar. Es data pura: no tiene eventos ni persistencia. El editor `HumanBodyAssembler` lo escribe.

**Vinculado a:** [[Index/06 - Player & World]], [[NpcAgent]]

**Conexiones:** [[NpcBody]] (único consumidor, vía `TryPick`), [[HumanBodyAssembler]] (genera el asset), [[NpcAgent]] (los clientes que usan el cuerpo)

## Asset

- Creable desde el menú `RunRunSimulator/Customers/Human Body Catalog`.
- Asset generado en `Resources/Data/Humans/HumanBodyCatalog.asset`.

## Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `Bodies` | `List<Entry>` | Cuerpos disponibles (sección `[Title("Bodies")]`) |
| `Entry.Body` | `GameObject` | Prefab del cuerpo (Animator `HumanNpc`) |
| `Entry.Skins` | `List<Material>` | Pieles posibles para ese cuerpo |

## Método

**`TryPick(out GameObject body, out Material skin)`**: filtra las entradas nulas o sin cuerpo, elige una entrada al azar con `UnityEngine.Random` y luego elige una piel al azar dentro de esa entrada. Si la entrada no tiene pieles, `skin` queda null. Si no hay cuerpos válidos, loguea un warning y devuelve false.

## Quirks ⚠️

- La piel se elige dentro de la entrada del cuerpo, no globalmente. Con el catálogo actual, cada cuerpo tiene las 6 pieles, así que en la práctica es uniforme.
- Usa `UnityEngine.Random`, no el RNG de la partida: no es reproducible.
- No se espera que `Bodies` tenga entradas nulas, pero `TryPick` lo tolera.
