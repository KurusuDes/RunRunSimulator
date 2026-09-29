---
tags: [script, genetics, gameplay]
---

# CreatureGrowth.cs

**Ruta:** `Systems/Creatures/CreatureGrowth.cs`

**Responsabilidad:** Clase estatica que maneja transiciones de forma en el ciclo de vida: Egg → Slime → Adult. `Lay()` marca un DNA como huevo (Form=Egg, Explorations=0). `Hatch()` lo pasa a slime (Form=Slime, Explorations=0). `RecordExploration()` incrementa contador de exploraciones; devuelve true cuando alcanza el threshold `toEvolve`, evolucionando a Adult. Solo opera si el DNA no está muerto y su forma es válida. Entry point del gameplay desde breeding.

## Métodos Públicos

- `Lay(CreatureDNA dna)` — asigna Form=Egg, Explorations=0 (incubable, no vivo)
- `Hatch(CreatureDNA dna)` — asigna Form=Slime, Explorations=0 (recién eclosionado, listo a explorar)
- `RecordExploration(CreatureDNA dna, int toEvolve) → bool` — incrementa `dna.Explorations++`. Si alcanza `toEvolve`, asigna Form=Adult y devuelve true. Retorna false si DNA es null, está muerto o no es Slime.

## Ciclo de Vida (S137)

1. **Lay()**: Breeding → DNA como Egg (el huevo entra al registro)
2. **Hatch()**: BreedingController.TryHatchEgg() → DNA como Slime (spawn en incubadora, sale como slime)
3. **RecordExploration()**: ExpeditionReturn → cada slime que vuelve vivo suma 1 exploración
4. **Adult**: Cuando Explorations >= `CreatureAvailability.ExplorationSteps` (default 3), pasa a Adult (visual adulta, puede reproducirse)

## Vinculado a

- [[Index/02 - Genetics & Breeding]]
- [[Index/09 - Active Context]] (S137: ciclo de vida)

## Conexiones

- [[CreatureDNA]] (DNA.Form, DNA.Explorations, DNA.IsDead)
- [[BreedingController]] (genera Lay/Hatch)
- [[ExpeditionBridge]] (genera RecordExploration)
- [[MonchiForm]] (Enum: Egg, Slime, Adult)
