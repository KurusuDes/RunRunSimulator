---
tags: [script, dev, testing, autoplayer]
---

# AutoPlayer.cs

**Ruta:** `Systems/Dev/AutoPlayer.cs`

**Responsabilidad:** Bot de testing automatizado (dev) ejecutor de 17 pasos: onboarding (compra caja, apertura) + 3 eclosiones + expedición arena + ciclo de cría/venta/mejora. Singleton `DontDestroyOnLoad`. Refactorizado S138: delegó pasos 1-10 a `AutoPlayerOpeningSteps`, pasos 11-17 a `AutoPlayerLoopSteps`. Orquestador delgado.

**S138:** División en colaboradores; carga pasos internos en `Sequence()` vía `new AutoPlayerOpeningSteps(this)` + `new AutoPlayerLoopSteps(this)`.

## Singleton + Lifecycle

- `Instance { get; private set; }` — singleton persistente
- `DontDestroyOnLoad` en Awake
- `Status { get; set; }` — string con estado actual (pub escritura interna; lectura pública para dev/UI)

## Campos Serializados

- `arenaTimeScale` (float, default 4) — aceleración de tiempo durante combate (arena)
- `stepTimeout` (float, default 60) — timeout por paso en segundos

## Estado Interno (acceso `internal` para colaboradores)

- `CurrentStep` — paso actual
- `Failed` — flag de falla
- `EggIds`, `SlimeIds` — listas de IDs spawneados
- `LastExpeditionReturn`, `LastRunMaterial`, `LastRunLost`, `TotalExpeditions`, `LostExpeditions` — resulados de expedición
- `LastChild`, `LastSoldDna`, `LastSalePrice` — resultados de cría y venta

## Ciclo de 17 Pasos (vía Colaboradores)

### Pasos 1-10: AutoPlayerOpeningSteps
- Step 1: Arrival — CloudSync ready + TutorialStep >= 1
- Step 2: BuyEggBox — compra caja Form.Egg (precio 0)
- Step 3: OpenBox — abre caja, verifica 5 huevos
- Step 4: PlaceIncubator — coloca incubadora en espiral
- Step 5: EggsIntoIncubator — lanza 5 huevos hacia incubadora
- Step 6: HatchThree — eclosiona 3 (verifica 3 slimes, 2 huevos)
- Step 7-9: Expedition — inicia bajada, corre arena, valida retorno
- Step 10: HatchRemaining — eclosiona los 2 restantes

### Pasos 11-17: AutoPlayerLoopSteps
- Step 11: BuyBreedingRoom — compra corral de cría
- Step 12: ExpeditionsUntilPair — bajadas hasta pareja adulta criable
- Step 13: Breed — lanza padres, espera hijo (Form=Slime), eclosiona
- Step 14: Showcase — coloca vitrina, lanza criatura vendible
- Step 15: Sale — espera cliente, cierra venta, valida dinero
- Step 16: Upgrade — compra mejora disponible en catálogo
- Step 17: Fin — marca fin (Status="FIN tanda 2 · stats")

## Métodos Públicos

- `Run()` — inicia secuencia si no está corriendo
- `Status { get; set; }` — acceso al string de estado

## Métodos Privados

- `Sequence() → IEnumerator` — orquestador maestro; instancia colaboradores, ejecuta pasos en orden
- `WaitFor(Func<bool> condition, float timeout, string what) → IEnumerator` — loop until condition o timeout; si falla: Fail()
- `Fail(string reason)` — asigna `failed=true`, Status="FALLA paso X · reason", Debug.Break()
- `Ok(string name, string data)` — Status="OK paso X · name · data", Debug.Log()
- `ExpeditionsUntil(Func<bool> condition, int max, string why, List<string> occupyIds=null) → IEnumerator` — itera expediciones hasta lograr condición
- `PlayExpedition(List<string> teamIds) → IEnumerator` — lanza expedición, espera resultado

## Suscripciones

- `OnEnable()` suscribe: `GameEvents.OnExpeditionReturned`, `GameEvents.OnBreedingCompleted`, `GameEvents.OnCustomerSold`
- `OnDisable()` desuscribe

## Invariantes

- **Singleton + Persistent:** una sola instancia, persiste entre escenas
- **Falla en Debug.Break():** desarrollo interactivo
- **Status público:** lectura de progreso en vivo
- **ResumeFromStep static:** permite reiniciar desde paso N (hardcodeado)
- **Colaboradores internos:** `AutoPlayerOpeningSteps` + `AutoPlayerLoopSteps` no son singletons, se instancian por ciclo

## Vinculado a

- [[Index/23 - Arena Sandbox y Expedicion]]
- [[Index/28 - Currency & Monetization]] (mejoras)

**Conexiones:** [[AutoPlayerOpeningSteps]], [[AutoPlayerLoopSteps]], [[AutoPlayerQuery]], [[GameEvents]], [[GameManager]], [[Wallet]], [[BreedingController]], [[StoreManager]], [[MoriMochiSpawner]], [[CloudSyncService]]
