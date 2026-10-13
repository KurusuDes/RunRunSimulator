---
tags: [script, world, title, decorative, spawn]
---

# TitleDiorama.cs

**Ruta:** `World/Title/TitleDiorama.cs`

**Responsabilidad:** Escenografía viva de la pantalla de título. Al arrancar spawnea varios MoriMonchis adultos aleatorios en puntos del NavMesh dentro de un radio y les pasa el centro al [[TitleWanderer]] de cada uno. Es decorativo: no escribe en el registro, en el inventario ni en `WorldStateSO`.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `monchiPrefab` | `GameObject` (Required) | — | Prefab de MoriMonchi con `TitleWanderer` |
| `database` | `CreatureDatabaseSO` (Required) | — | Base para generar el ADN |
| `furDatabase` | `FurTypeDatabaseSO` (Required) | — | Tipos de pelaje |
| `visualBank` | `MonchiVisualBankSO` (Required) | — | Banco visual del `MonchiVisualizer` |
| `center` | `Transform` (Required) | — | Centro del paseo |
| `count` | `int` | 5 | Cantidad de criaturas |
| `radius` | `float` | 6 | Radio de paseo |

## Spawn

1. Busca un punto en el NavMesh (hasta 12 intentos, `SamplePosition` con radio 2).
2. Genera ADN con `CreatureGenerator.GenerateRandom`: `Form = Adult`, género aleatorio, elemento, rol, `Generation = 1`, sociabilidad y audacia aleatorias, nombre de `CreatureNameBank`, `BirthDay = 1`, `Stamp()`.
3. Instancia el prefab con rotación Y aleatoria bajo `transform`.
4. Configura `MonchiVisualizer` (`SetBank`, `SetFurDatabase`, `Assemble`).
5. Llama `TitleWanderer.Init(center, radius)`.

## Conexiones

- [[TitleWanderer]] — comportamiento de paseo de cada criatura
- [[MonchiVisualizer]] — arma el visual con el ADN
- [[CreatureDatabaseSO]], [[FurTypeDatabaseSO]], [[MonchiVisualBankSO]] — datos
- [[CreatureGenerator]], [[CreatureNameBank]] — generación de ADN y nombres
- [[TitleScreenUITK]] — escena compartida (pantalla de título)
