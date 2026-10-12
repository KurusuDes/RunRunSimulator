---
tags: [scriptable-object, database, genetics]
---

# PartDatabaseSO.cs

**Ruta:** `Data/Databases/PartDatabaseSO.cs`

**Responsabilidad:** Base abstracta genérica `PartDatabaseSO<T> : KeyedDatabaseSO<T>` para databases de partes (Body, Horn, Back, Wing, Face). Hereda de KeyedDatabaseSO protocolo de ID auto-sync. Campo `parts` Dictionary<string, T> indexado por ID. Métodos: `GetPartByID()` (wrapper GetByID), `GetRandomPart(Rarity?, PartSetSO?, where?)` (filtrado por rareza, set y predicado). Propiedades: `Parts` (acceso al diccionario), `PartCount` (total), `PartsTable` (lista para la tabla Odin). Tabla visual en inspector Odin.

**S135:** Método `GetRandomPart()` acepta filtro `PartSetSO` además de `Rarity`. **S149:** Se agrega el parámetro `where` (`Func<T, bool>`) y la propiedad `PartsTable`.

## Campos Privados

| Campo | Tipo | Acceso | Descripción |
|-------|------|--------|-------------|
| `parts` | `Dictionary<string, T>` | [OdinSerialize] private | Todas las partes indexadas por ID |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetPartByID(id)` | `T` | Busca parte por ID (wrapper de GetByID) |
| `GetRandomPart(Rarity? rarityFilter, PartSetSO setFilter, Func<T,bool> where)` | `T` | Selecciona random parte con filtros opcionales por rareza, set y predicado (S135 set, S149 predicado) |
| `GetByID(id)` [inherited] | `T` | De KeyedDatabaseSO: búsqueda por ID |

## Propiedades

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Parts` | `Dictionary<string, T>` | Diccionario completo |
| `PartCount` | `int` | Total de partes registradas |
| `PartsTable` | `List<T>` | **(S149)** Vista de solo lectura de partes no nulas para la tabla del inspector |
| `Count` [inherited] | `int` | De KeyedDatabaseSO |

## Métodos Editor (Odin)

| Método | Descripción |
|--------|-------------|
| `PopulateFromBuffer()` [inherited] | Botón: arrastra assets, auto-asigna IDs |
| `SyncAllIDs()` [inherited] | Botón: renumera todas las partes con prefijo |

## Implementaciones Concretas

Clases que heredan `PartDatabaseSO<T>`:
- `BodyShapeDatabaseSO : PartDatabaseSO<BodyShapePart>`
- `HornDatabaseSO : PartDatabaseSO<BodyPart>` (role Horn)
- `BackDatabaseSO : PartDatabaseSO<BodyPart>` (role Back)
- `WingDatabaseSO : PartDatabaseSO<BodyPart>` (role Wing)
- `FaceDatabaseSO : PartDatabaseSO<BodyPart>` (role Face)

## Filtrado de Partes

`GetRandomPart()` soporta tres filtros opcionales (independientes, se aplican conjuntamente):

```csharp
// Solo raros
var rare = database.GetRandomPart(Rarity.Rare);

// Solo del set "Fuego"
var fireSet = database.GetRandomPart(setFilter: fireSetSO);

// Raros del set "Fuego"
var rareFireSet = database.GetRandomPart(Rarity.Rare, fireSetSO);

// Solo rolleables (S149: el predicado lo aporta PartPool)
var rollable = database.GetRandomPart(where: PartPool.Rollable);

// Sin filtro (cualquiera)
var any = database.GetRandomPart();
```

## Cambios S149

- Nuevo parámetro `where` (`System.Func<T, bool>`). Lo usa `CreatureGenerator` y `BreedingService` con `PartPool.Rollable`.
- Nueva propiedad `PartsTable` para la tabla del inspector.

## Cambios S135

**Filtro PartSetSO en GetRandomPart():**

```csharp
public T GetRandomPart(Rarity? rarityFilter = null, PartSetSO setFilter = null)
{
    var pool = parts.Values.Where(p => p != null);
    
    if (rarityFilter.HasValue) pool = pool.Where(p => p.Rarity == rarityFilter.Value);
    if (setFilter != null)     pool = pool.Where(p => p.Set    == setFilter);
    
    var list = pool.ToList();
    return list.Count > 0 ? list[Random.Range(0, list.Count)] : null;
}
```

**Impacto:** Permite seleccionar partes de un set específico vía PartSetSO, no solo por rareza.

## Vinculado a

- [[Index/02 - Genetics & Breeding]]

## Conexiones

[[KeyedDatabaseSO]], [[BodyPart]], [[BodyShapePart]], [[PartSetSO]], [[PartPool]], [[CreatureGenerator]], [[BreedingService]], [[HornDatabaseSO]], [[BackDatabaseSO]], [[WingDatabaseSO]], [[FaceDatabaseSO]]
