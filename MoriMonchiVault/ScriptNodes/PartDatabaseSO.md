---
tags: [scriptable-object, database, genetics]
---

# PartDatabaseSO.cs

**Ruta:** `Data/Databases/PartDatabaseSO.cs`

**Responsabilidad:** Base abstracta genérica `PartDatabaseSO<T> : KeyedDatabaseSO<T>` para databases de partes (Body, Horn, Back, Wing, Face). Hereda de KeyedDatabaseSO protocolo de ID auto-sync. Campo `parts` Dictionary<string, T> indexado por ID. Métodos: `GetPartByID()` (wrapper GetByID), `GetRandomPart(Rarity?, PartSetSO?)` (filtrado por rareza y/o set), `GetByID()` (heredado). Propiedades: `Parts` (acceso al diccionario), `PartCount` (total). Tabla visual en inspector Odin.

**S135:** Método `GetRandomPart()` ahora acepta filtro `PartSetSO` además de `Rarity`.

## Campos Privados

| Campo | Tipo | Acceso | Descripción |
|-------|------|--------|-------------|
| `parts` | `Dictionary<string, T>` | [OdinSerialize] private | Todas las partes indexadas por ID |

## Métodos Públicos

| Método | Retorna | Descripción |
|--------|---------|-------------|
| `GetPartByID(id)` | `T` | Busca parte por ID (wrapper de GetByID) |
| `GetRandomPart(Rarity?, PartSetSO?)` | `T` | Selecciona random parte, con filtros opcionales por rareza y/o set (S135) |
| `GetByID(id)` [inherited] | `T` | De KeyedDatabaseSO: búsqueda por ID |

## Propiedades

| Propiedad | Tipo | Descripción |
|-----------|------|-------------|
| `Parts` | `Dictionary<string, T>` | Diccionario completo |
| `PartCount` | `int` | Total de partes registradas |
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

`GetRandomPart()` soporta dos filtros opcionales (independientes, se aplican conjuntamente):

```csharp
// Solo raros
var rare = database.GetRandomPart(Rarity.Rare);

// Solo del set "Fuego"
var fireSet = database.GetRandomPart(setFilter: fireSetSO);

// Raros del set "Fuego"
var rareFireSet = database.GetRandomPart(Rarity.Rare, fireSetSO);

// Sin filtro (cualquiera)
var any = database.GetRandomPart();
```

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

[[KeyedDatabaseSO]], [[BodyPart]], [[BodyShapePart]], [[PartSetSO]], [[CreatureGenerator]], [[HornDatabaseSO]], [[BackDatabaseSO]], [[WingDatabaseSO]], [[FaceDatabaseSO]]
