---
tags: [script, visualization, genetics]
---

# MonchiSlimeBody.cs

**Ruta:** `World/Creatures/MonchiSlimeBody.cs`

**Responsabilidad:** Clase estatica que arma el visual de un MoriMochi en forma Slime. `Build()` instancia el modelo base de slime, elige variante de cuerno según forma del cuerpo (letra de BodyShapeID → Horn_A/B/C/D), injerta la parte de cuerno desde el banco genético, y escala al tamaño de slime. Retorna null si banco es null. Llamado por `MonchiVisualizer` al cambiar a Form.Slime.

## Métodos Públicos

- `Build(CreatureDNA dna, MonchiVisualBankSO bank, Transform parent) → GameObject` — Instancia `bank.SlimeModel` bajo `parent`, escala a `bank.SlimeScale`. Busca el body del BodyShapeID para determinar letra (última char del name). Activa la variante Horn_[letra] y desactiva otras. Injerta la malla custom del HornID (via `bank.GetPartMesh(dna.HornID, MonchiForm.Slime)`). Devuelve el GameObject instanciado o null si falta el modelo.

## Estructura del Modelo Slime

El prefab en `bank.SlimeModel` contiene:
- Root (cuerpo base)
  - `Horn_A`, `Horn_B`, `Horn_C`, `Horn_D` — variantes built-in (solo una activa según body)
  - `Top` — anchor para injertar la parte genética de cuerno

## Lógica de Injerto

1. Determina letra del body: `bodyPrefab = bank.GetBody(dna.BodyShapeID)`, extrae última char del name (e.g. "BodyShape_A" → 'A')
2. Desactiva todas las `Horn_*` salvo Horn_[letra]
3. Obtiene el part mesh: `bank.GetPartMesh(dna.HornID, MonchiForm.Slime)`
4. Si existe, instancia bajo `Top`, resetea localTransform a identity, escala a 1

## Métodos Privados

- `ApplyHornVariant(Transform root, string keep)` — recorre hijos, desactiva si comienzan con "Horn_" y nombre ≠ keep
- `GraftHornPart(Transform root, GameObject partMesh)` — desactiva todos Horn_*, instancia partMesh bajo Top, resetea transform
- `FindChildByName(Transform root, string name) → Transform` — busca recursivamente por componente Transform exacto

## Vinculado a

- [[Index/10 - Visualization]]
- [[Index/02 - Genetics & Breeding]] (partes genéticas)

## Conexiones

- [[MonchiVisualizer]] (llamador: `Build()` al cambiar a Form.Slime)
- [[MonchiVisualBankSO]] (banco de modelos y partes)
- [[CreatureDNA]] (DNA.BodyShapeID, DNA.HornID)
- [[MonchiEggBody]] (análogo para huevo)
- [[MonchiForm]] (Enum)
