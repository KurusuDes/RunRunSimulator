---
tags: [script, visualization, genetics]
---

# MonchiEggBody.cs

**Ruta:** `World/Creatures/MonchiEggBody.cs`

**Responsabilidad:** Clase estatica que arma el visual de un MoriMochi en forma Egg. `Build()` instancia el modelo base de huevo, escala altura según `bank.EggHeight`, elige variante de espalda según forma del cuerpo (BodyShapeID → Egg_Back_A/B), injerta la parte genética de espalda, y desactiva `Egg_Scales`. Retorna null si banco es null. Llamado por `MonchiVisualizer` al cambiar a Form.Egg.

## Métodos Públicos

- `Build(CreatureDNA dna, MonchiVisualBankSO bank, Transform parent) → GameObject` — Instancia `bank.EggModel` bajo `parent`, escala a (1, bank.EggHeight, 1). Busca el body del BodyShapeID para determinar letra. Activa la variante Egg_Back_A/B (A si body es D, B si body es A/B/C). Injerta la malla custom del BackID (via `bank.GetPartMesh(dna.BackID, MonchiForm.Egg)`). Desactiva `Egg_Scales`. Devuelve el GameObject o null si falta el modelo.

## Estructura del Modelo Egg

El prefab en `bank.EggModel` contiene:
- Root (cuerpo de huevo)
  - `Egg_Horn_*` — variantes no usadas en huevo (todas desactivadas)
  - `Egg_Back_A`, `Egg_Back_B` — variantes de espalda (solo una activa según body)
  - `Egg_Scales` — detalle visual (desactivado)
  - `Body` — anchor para injertar la parte genética de espalda

## Lógica de Injerto

1. Determina letra del body: `bodyPrefab = bank.GetBody(dna.BodyShapeID)`, extrae última char (e.g. "BodyShape_D" → 'D')
2. Desactiva todos Egg_Horn_* (siempre)
3. Elige variante de espalda: si body es D → Egg_Back_B, sino → Egg_Back_A
4. Desactiva todas salvo la elegida
5. Obtiene el part mesh: `bank.GetPartMesh(dna.BackID, MonchiForm.Egg)`
6. Si existe, instancia bajo Body, resetea localTransform a identity, escala a 1
7. Desactiva Egg_Scales

## Métodos Privados

- `ApplyPrefixVariant(Transform root, string prefix, string keep)` — recorre hijos, desactiva si comienzan con `prefix` y nombre ≠ keep
- `GraftEggPart(Transform root, GameObject partMesh, string prefix)` — desactiva todos con `prefix`, instancia partMesh bajo Body, resetea transform
- `FindChildByName(Transform root, string name) → Transform` — busca recursivamente por componente Transform exacto

## Vinculado a

- [[Index/10 - Visualization]]
- [[Index/02 - Genetics & Breeding]] (partes genéticas)

## Conexiones

- [[MonchiVisualizer]] (llamador: `Build()` al cambiar a Form.Egg)
- [[MonchiVisualBankSO]] (banco de modelos y partes)
- [[CreatureDNA]] (DNA.BodyShapeID, DNA.BackID)
- [[MonchiSlimeBody]] (análogo para slime)
- [[MonchiForm]] (Enum)
