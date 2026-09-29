---
tags: [script, dev, autoplayer, steps, opening]
---

# AutoPlayerOpeningSteps.cs

**Ruta:** `Systems/Dev/AutoPlayerOpeningSteps.cs`

**Responsabilidad:** Pasos 1–10 del loop de AutoPlayer: tutorial inicial (llegada, compra caja de huevos, apertura, incubadora), eclosión, primera expedición de 3 slimes, eclosión de los 2 restantes. Colaborador interno para desacoplamiento.

**S138:** Nuevo colaborador; extrae pasos 1-10 (onboarding + cría inicial) de AutoPlayer.

## Métodos Principales (IEnumerator)

- `Step1_Arrival()` — Espera sync de nube, TutorialStep >= 1, verifica Minerita suficiente
- `Step2_BuyEggBox()` — Compra caja de huevos en tienda (precio 0)
- `Step3_OpenBox()` — Abre caja, verifica 5 huevos spawneados
- `Step4_PlaceIncubator()` — Coloca incubadora en espiral libre
- `Step5_EggsIntoIncubator()` — Lanza 5 huevos a incubadora con delay
- `Step6_HatchThree()` — Eclosiona 3 de los 5, verifica count (3 slimes, 2 huevos)
- `Step7to9_Expedition()` — Juega expedición con los 3 slimes, verifica regreso + explorations++
- `Step10_HatchRemaining()` — Eclosiona los 2 huevos restantes (0 quedan)

## Constantes

- Timeout estándar por step (configurable en AutoPlayer)
- Hatch cost por defecto en BreedingController

## Vinculado a

- [[AutoPlayer]] (orquestador)
- [[Index/04 - Breeding System]]
- [[Index/13 - Expedition & Arena]]

**Conexiones:** [[DeliveryBox]], [[IncubatorContainer]], [[CloudSyncService]], [[MoriMochiSpawner]], [[AutoPlayerQuery]], [[Wallet]], [[BreedingController]]
