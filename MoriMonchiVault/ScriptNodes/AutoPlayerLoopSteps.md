---
tags: [script, dev, autoplayer, steps]
---

# AutoPlayerLoopSteps.cs

**Ruta:** `Systems/Dev/AutoPlayerLoopSteps.cs`

**Responsabilidad:** Pasos 11–17 del loop de AutoPlayer: comprar incubadora de cría, criar pareja, exponer a vitrina, vender, comprar mejoras. Colaborador interno que desacopla la orquestación de AutoPlayer.

**S138:** Nuevo colaborador; extrae los pasos 11-17 (ciclo de cría + venta) de AutoPlayer para mejorar legibilidad.

## Métodos Principales (IEnumerator)

- `Step11_BuyBreedingRoom()` — Compra `BreedingContainer` si no existe; verifica precio en Minerita
- `Step12_ExpeditionsUntilPair()` — Corre expediciones hasta conseguir pareja adulta criable
- `Step13_Breed()` — Lanza padres a incubadora, espera a que inicien cría, avanza bloques, eclosiona hijo
- `Step14_Showcase()` — Coloca vitrina (`StoreContainer`); valida accesibilidad desde caja registradora
- `Step15_Sale()` — Espera cliente, realiza venta, verifica dinero + estado IsSold
- `Step16_Upgrade()` — Compra primera mejora disponible en el catálogo
- `Step17_Fin()` — Marca fin de la tanda 2; reporta estadísticas

## Constantes

- `MaxExpeditions = 15` — Límite de bajadas antes de fallar
- `MaxClockAdvances = 4` — Bloques máximos a avanzar
- `LongTimeout = 180f` — Timeout largo en segundos

## Vinculado a

- [[AutoPlayer]] (orquestador)
- [[Index/04 - Breeding System]]
- [[Index/05 - UI System]] (tiendas)

**Conexiones:** [[BreedingController]], [[StoreManager]], [[MoriMochiSpawner]], [[FurnitureService]], [[AutoPlayerQuery]], [[GameEvents]], [[Wallet]], [[GameClock]]
