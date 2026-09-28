---
tags: [script, world, creature, animation]
---

# EggIdleShuffler.cs

**Ruta:** `World/Creatures/EggIdleShuffler.cs`

**Responsabilidad:** Automatizador de animaciones idle de huevos. **S136 NUEVO.** MonoBehaviour que rotea variantes de animación idle (Wobble, Hop, Jingle) en intervalos aleatorios con crossfade suave. Usado en EggLabBuilder para dar vida a los huevos en el laboratorio.

## Campos Serializados

| Campo | Tipo | Default | Descripción |
|-------|------|---------|-------------|
| `animator` | `Animator` | null | Animator del huevo; auto-detectado si nulo |
| `variants` | `string[]` | { "Wobble", "Hop", "Jingle" } | Nombres de estados de animación a rotar |
| `gapSeconds` | `Vector2` | (2.5, 7) | Rango de segundos entre cambios; Random.Range(min, max) |
| `crossFade` | `float` | 0.12 | Duración crossfade en segundos |

## Métodos Públicos

**Ninguno.** MonoBehaviour puro (OnEnable, OnDisable, corrutina interna).

## Ciclo de Vida

| Evento | Acción |
|--------|--------|
| `Awake()` | Si `animator` es null, obtiene del primer Animator en hijos: `GetComponentInChildren<Animator>()` |
| `OnEnable()` | Inicia corrutina ShuffleRoutine |
| `OnDisable()` | Detiene corrutina si existe; limpia referencia |

## Corrutina ShuffleRoutine()

**Flujo:**
1. **Inicialización:** `animator.Play("Idle", 0, Random.value)` — comienza en estado Idle con offset de frame aleatorio (evita sincronía entre huevos)
2. **Loop:**
   - Espera `Random.Range(gapSeconds.x, gapSeconds.y)` segundos
   - Elige índice aleatorio en `variants[]`
   - Si hay >1 variante: reitera hasta elegir una diferente al último (evita repetir)
   - Almacena índice en `lastIndex`
   - Ejecuta crossfade: `animator.CrossFadeInFixedTime(variants[index], crossFade)`
   - Vuelve a esperar

**Pseudocódigo:**
```csharp
IEnumerator ShuffleRoutine()
{
    animator.Play("Idle", 0, Random.value);
    int lastIndex = -1;
    
    while (true)
    {
        yield return new WaitForSeconds(Random.Range(gapSeconds.x, gapSeconds.y));
        
        int index = Random.Range(0, variants.Length);
        // Evita repetición consecutiva
        if (variants.Length > 1)
        {
            while (index == lastIndex)
                index = Random.Range(0, variants.Length);
        }
        lastIndex = index;
        
        animator.CrossFadeInFixedTime(variants[index], crossFade);
    }
}
```

## Cambios S136

**Nuevo script para laboratorio de huevos:**
- EggLabBuilder instancia huevos con componente EggIdleShuffler
- Anima huevos sin input del jugador (automatizado)
- Variantes por huevo-modelo (Wobble = bamboleo, Hop = salto, Jingle = tintineo)

## Notas S136

- No requiere CreatureDNA ni datos genéticos; solo animaciones idle
- auto-encuentra Animator si no seteado en inspector
- Soporta N variantes (flexible, no hardcodeado)
- crossfade suave evita transiciones abruptas
- Offset de frame inicial (Random.value) desincroniza huevos visualmente
- No se desuscribe de eventos; MonoBehaviour simple lifecycle

## Invariantes

- ShuffleRoutine se ejecuta en bucle infinito mientras el GameObject esté activo
- OnDisable siempre frena la corrutina (clean lifecycle)
- No hay state externo (variables son locales/privadas)
- Diferencia de animación es puramente visual (sin lógica de gameplay)

## Vinculado a

- [[Index/31 - EggLab & Incubadora]]
- [[EggLabBuilder]] — instancia con este componente

## Conexiones

**Entrada:**
- Animator del huevo (auto-detected o seteado)
- Animator states: Idle, Wobble, Hop, Jingle (debe existir en el RuntimeAnimatorController)

**Salida:**
- Transiciones suaves entre animaciones idle
- Sin eventos ni callbacks
