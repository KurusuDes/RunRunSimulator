# Propuesta de assets Synty para MoriMonchis (S162)

> Fuente: bóveda `E:\GitHub\AssetVaultFinder` (solo lectura). Cada asset listado aparece en `Packs/<ID>/CONTENTS.txt` (verificado con `Find-Asset.ps1` y grep). Los MB salen de `Install-Pack.ps1 -DryRun -Project 'E:\GitHub\RunRunSimulator'` (tamaño en disco de lo que se importaría, con dependencias; `PolygonGeneric` ya existe y se salta). **No se importó nada.**
> Proyecto: Unity 6000.3.9f1 · URP · POLYGON + toon propio · NPCs siempre Sidekick.

**Estilo elegido:** POLYGON + Sidekick. SIMPLE descartado (fauna SIMPLE no entra: rompería el estilo).

## Punto de partida (lo que hay hoy en `Assets/Synty`)

| Carpeta | Qué hay de verdad |
|---|---|
| `SidekickCharacters` (225 MB) | Tool 1.2.7 + **solo el Starter**: piezas `SK_FANT_KNGT_17_*` (un único set de caballero), `SK_SCFI_CIVL_*` y `SK_HORR_VILN_*`. **El pack Fantasy Knights completo no está instalado.** La base de datos (`Side_Kick_Data.db`) ya conoce las piezas `FANT_VILL_*` y demás: falta importar las mallas. |
| `PolygonNature` (80 MB), `PolygonGeneric` (156 MB) | Bosque de la tienda (238 árboles) y librería compartida. |
| INTERFACE (Fantasy Menus / Screens / Warrior HUD) | En esta PC no hay carpeta en `Assets/Synty`; la UI usa los sprites copiados a `UI Toolkit/Skin/Synty` (versionados). Los `.unitypackage` sí están en la caché del instalador. |
| Animaciones humanoides | Caseras (`HumanoidClipBaker`): Human_Idle/Walk/Talk y FP_*. |

Clientes actuales: 5 caballeros `Human_Knight_01..05` armados con `HumanBodyAssembler` (`Outfits/Starter/SK_FANT_KNGT_17_`). Arquetipos de cliente: Artista, Coleccionista, Fan de los roles, Ahorrador, Familia. Vecinos propuestos en `Index/35` §2.2: tío, veterinaria, panadera, coleccionista, niña del barrio, vendedor de genes.

---

## Prioridad (a) · Sidekicks de los personajes que faltan

Regla: los NPCs se arman **por piezas** con `HumanBodyAssembler` (`SidekickRuntime.CreateCharacter`), así que lo que hay que importar son las **mallas de outfit** (`Resources/Meshes/Outfits/<Pack>/`); los presets sirven de referencia de combinación y para leer el género.

| Pack | Qué cubre del GDD | `-Include` (listo) | MB | Masc / Fem |
|---|---|---|---|---|
| **SIDEKICK_FantasyVillagers** (núcleo) | Vecinos del Outer World (tío, veterinaria, panadera, coleccionista) y 4 de los 5 arquetipos de cliente (Artista, Coleccionista, Ahorrador, Familia); ropa civil de fantasía para el protagonista y mangas para los brazos FP. 83 piezas en 10 sets: pelo 6, barba 3, torso 7, brazos 3, cadera 6, piernas 3, pies 2, gorros 10, cara 3, espalda 6. | `'*/Resources/Meshes/Outfits/FantasyVillagers/*'` | **380,1** | Presets 01, 03, 05 → `Masculine` (con barba) · 02, 04 → `Feminine` |
| ↳ presets (opcional) | Referencia ya combinada de los 5 aldeanos + bases `HumanSpecies_01-04`. | `'*/Characters/FantasyVillagers/*'` | 50,9 | ídem |
| **SIDEKICK_FantasyKnights** | Variedad real para el arquetipo **Fan de los roles** / aventureros que hoy usan un solo set (KNGT_17). 119 piezas en 15 sets, 13 cascos, 15 capas. | `'*/Resources/Meshes/Outfits/FantasyKnights/*'` | **34,0** | Presets 01-05 → `Masculine` · 06 → `Feminine` |
| **SIDEKICK_FantasySorcerers** | **Vendedor de genes del mercado** (personaje místico) y toques para el Artista: sombreros de bruja, túnicas, capuchas (131 piezas, 10 sets). Usar piezas sueltas: el pack es de tono oscuro, no vestir a nadie entero de nigromante. | `'*/Resources/Meshes/Outfits/FantasySorcerers/*'` | **76,0** | 01, 03, 05 (intermedio −51), 06 → `Masculine` · 02, 04 → `Feminine` |
| ↳ presets 02-05 (alternativa) | Si solo se quiere la bruja/el hechicero listos. | `'*/Characters/FantasySorcerers/FantasySorcerers_0[2-5]/*'` (o los 4 por nombre) | 58,3 | 02, 04 F · 03, 05 M |

**Reparto sugerido** (punto de partida; las piezas finales se eligen en el Tool):

| Rol | Base | Carpeta de animación |
|---|---|---|
| El tío (historia, tutoriales de etapa) | FantasyVillagers_01 (barba) | `Masculine` |
| Veterinaria | FantasyVillagers_02 o _04 | `Feminine` |
| Panadera | FantasyVillagers_04 (o _02) | `Feminine` |
| Coleccionista (vecino y cliente) | FantasyVillagers_05 + accesorio de cara | `Masculine` |
| Vendedor/a de genes | FantasySorcerers_02/_04 (bruja) o _03 | `Feminine` / `Masculine` |
| Cliente Artista | Villagers fem. + sombrero Sorcerers | `Feminine` |
| Cliente Ahorrador | FantasyVillagers_03 | `Masculine` |
| Cliente Fan de los roles | FantasyKnights_01-05 / _06 | `Masculine` / `Feminine` |
| Cliente Familia | adulto Villagers (**sin niño**, ver huecos) | según el adulto |
| Protagonista (cuerpo y brazos FP) | `HumanSpecies` + torso/brazos Villagers | según Body Type elegido |

**Regla de género:** decide `BlendShapes.BodyTypeValue` del `.sk` (−100 masc, +100 fem); si se cambia el Body Type en el Tool, manda ese valor.

**Huecos (sin Sidekick en la bóveda):**
- **Niños** (la niña del barrio, el hijo del arquetipo Familia): ningún pack Sidekick trae niños. Opciones: posponer la niña, que la Familia sea una pareja adulta, o `POLYGON_Kids` como excepción (estilo POLYGON clásico; choca al lado de Sidekick).
- Vecinos animales antropomórficos: solo en `POLYGON_FantasyVillage` (gato, zorro, cerdo, conejo, ratón, mapache, rana, pájaro). Excepción a la regla Sidekick: **no recomendado** salvo decisión de Juan.

---

## Prioridad (b) · Animaciones (reemplazar las caseras)

Usar siempre `Animations/Sidekick/{Masculine|Feminine}` (clips `A_MOD_*`; los `A_POLY_*` son del rig POLYGON). Los packs no traen controller utilizable para nuestro caso: se arma uno propio (como `HumanNpc`) con estos clips.

| Pack | Qué cubre | `-Include` (listo) | MB |
|---|---|---|---|
| **ANIMATION_BaseLocomotion** (recorte) | Cliente que camina por la calle y la tienda (NavMesh: avance + giros), parar/arrancar, agacharse a la altura de un MoriMochi (`Stand_ToCrouch` → `BL_Idle_Crouching` → `Crouch_ToStand`), correr (niña/emergencia). | `'*/Animations/Sidekick/*/Locomotion/Walk/A_MOD_BL_Walk_F_*','*/Animations/Sidekick/*/Locomotion/Run/A_MOD_BL_Run_F_*','*/Animations/Sidekick/*/Locomotion/Turn/*','*/Animations/Sidekick/*/Idles/*','*/Animations/Sidekick/*/Transitions/Idle_ToWalk/*','*/Animations/Sidekick/*/Transitions/Walk_ToIdle/*','*/Animations/Sidekick/*/Transitions/Stand_ToCrouch/*','*/Animations/Sidekick/*/Transitions/Crouch_ToStand/*'` | **49,2** |
| ↳ todo Sidekick (alternativa) | + strafes, sprint, salto, crouch walk y los 174 controllers (traen 7 GUID que no están en el paquete). | `'*/Animations/Sidekick/*'` | 342,6 |
| **ANIMATION_Idles** (recorte) | Esperar en la caja/fila (`Bored_FootTap`, `WeightShift`, `ArmsFolded_Casual`, `Yawn`), mirar la vitrina (`Thoughtful_*`, `Look_*`, `Inspect_Hands`, `PointHand_Index_F`), negociar (`HeadNod_*`, `HeadShake_Small/Disappointed`, `Plead_F`, `HandsOnHips_Base`), saludar (`Wave_Small`), vecinos en rutina (`Lean_B_Base`, `Eat_Small`, `Drink_Sip`, `Stretch_Arms`), **acariciar a ras del suelo** (`Pray_Kneeling` Enter/Loop/Exit como arrodillarse). | `'A_MOD_IDL_Base_*.fbx','A_MOD_IDL_ArmsFolded_Casual_*.fbx','A_MOD_IDL_Bored_FootTap_*.fbx','A_MOD_IDL_Bored_SwingArms_*.fbx','A_MOD_IDL_HandsOnHips_Base_*.fbx','A_MOD_IDL_HeadNod_*.fbx','A_MOD_IDL_HeadShake_Small_*.fbx','A_MOD_IDL_HeadShake_Disappointed_*.fbx','A_MOD_IDL_Thoughtful_*.fbx','A_MOD_IDL_PointHand_Index_F_*.fbx','A_MOD_IDL_Wave_Small_*.fbx','A_MOD_IDL_Look_L_*.fbx','A_MOD_IDL_Look_R_*.fbx','A_MOD_IDL_Look_Down_*.fbx','A_MOD_IDL_Lean_B_Base_*.fbx','A_MOD_IDL_Pray_Kneeling_*.fbx','A_MOD_IDL_Eat_Small_*.fbx','A_MOD_IDL_Drink_Sip_*.fbx','A_MOD_IDL_Inspect_Hands_*.fbx','A_MOD_IDL_Plead_F_*.fbx','A_MOD_IDL_WeightShift_*.fbx','A_MOD_IDL_Yawn_*.fbx','A_MOD_IDL_Stretch_Arms_*.fbx'` | **84,9** |
| ↳ todo Sidekick sin móvil | Todas las posturas/acciones menos UsePhone/CheckWatch/PickNose. | `-Include '*/Animations/Sidekick/*' -Exclude '*/UsePhone/*','*/CheckWatch/*','*/PickNose/*'` | 227,5 |
| **ANIMATION_EmotesAndTaunts** (recorte) | Reacción del cliente en la venta (Moonlighter): contento (`Happy_*`, `Celebrate_Clapping_Polite`, `Affection_HeartHands`, `Celebrate_HandOnHeart`), duda/rechazo (`Sad_Shrug`, `Sad_Facepalm`, `Reproach_WaveAway`, `Reproach_ShakeFinger`, `Angry_ShakeFist`), cansado de esperar (`Sad_Tired`), saludo de vecinos (`Greet_Wave`, `Greet_WaveOver`, `Greet_Bow`, `Greet_Curtsy`), **lanzar** (`Sporty_Baseball`, gesto de lanzamiento). | `'A_MOD_EMOT_Greet_Wave_*.fbx','A_MOD_EMOT_Greet_WaveOver_*.fbx','A_MOD_EMOT_Greet_Bow_M*.fbx','A_MOD_EMOT_Greet_Bow_F*.fbx','A_MOD_EMOT_Greet_Curtsy_*.fbx','A_MOD_EMOT_Happy_*.fbx','A_MOD_EMOT_Celebrate_Clapping_Polite_*.fbx','A_MOD_EMOT_Celebrate_HandOnHeart_*.fbx','A_MOD_EMOT_Affection_HeartHands_*.fbx','A_MOD_EMOT_Sad_Shrug_*.fbx','A_MOD_EMOT_Sad_Facepalm_*.fbx','A_MOD_EMOT_Sad_Tired_*.fbx','A_MOD_EMOT_Reproach_WaveAway_*.fbx','A_MOD_EMOT_Reproach_ShakeFinger_*.fbx','A_MOD_EMOT_Angry_ShakeFist_*.fbx','A_MOD_EMOT_Sporty_Baseball_*.fbx','A_MOD_EMOT_Base_Idle_*.fbx'` | **103,1** |

Packs descartados: `SwordCombat`, `BowCombat`, `GoblinLocomotion` (no hay combate humano; el Brawl es de MoriMonchis).

**Huecos de animación (no están en la bóveda):**
- **Primera persona del jugador** (agarrar, acariciar, lanzar, sostener, interactuar): no hay clips FPV de interacción (solo los de arco). `FPArms` y `FP_*` caseros se quedan.
- NPC **agarrar/recibir/entregar** un MoriMochi o pagar en la caja, cargar en brazos, sentarse en bancos, trabajar (hornear, curar en camilla): sin clips. Aproximaciones: `PointHand`, `Inspect_Hands`, `Pray_Kneeling`, crouch.
- Animación facial / lip-sync: no viene (las caras vivas siguen dependiendo de los blendshapes de Sidekick, pendiente S156).

---

## Prioridad (c) · Flora y fauna más pulida

Biomas por zona (FLORA_FAUNA.md: bosque templado = **Meadow**, mágico/noche = **Enchanted**, nieve = **Alpine**). El pasto lo sigue haciendo nuestro shader (`ShopGrassField`/`ArenaGrass`): de Synty se toman árboles, arbustos, flores en mata, setas, rocas, setos, enredaderas y **fauna ambiental en partículas**.

| Pack | Zona del GDD | Assets concretos | `-Include` (listo) | MB |
|---|---|---|---|---|
| **POLYGON_FantasyVillage** (entorno + FX) | Exterior de la tienda y barrio (madera de cuento, colores otoñales) · paleta **Otoño** del Brawl · remate con hiedra del kit de zonas | `SM_Env_Tree_01-05`, `SM_Env_Wild_Flower_*` (+grupos), `SM_Env_Hedge_01-03`, `SM_Env_Vine_*` (+Creeping/Large), `SM_Env_Stepping_Stone_*`, `SM_Env_Flowers_01-03`, `SM_Env_Grass_Blob_*`, `SM_Env_Lillypads_*`; fauna FX: `FX_Bee_Large_01`, `FX_BumbleBees_01`, `FX_Honeybees_01`, `FX_Ladybugs_01`, `FX_Dandelion_Blowing_01`, `FX_Birds_01/02`, `FX_Butterflies_01`, `FX_Frogs_01`, `FX_Fish_01`, `FX_Fireflies_01`, `FX_Wisps_01`, `FX_Chimney_Smoke_01` | `'SM_Env_Tree_0*.prefab','SM_Env_Wild_Flower_*.prefab','SM_Env_Hedge_*.prefab','SM_Env_Vine_*.prefab','SM_Env_Stepping_Stone_*.prefab','SM_Env_Flowers_0*.prefab','SM_Env_Grass_Blob_*.prefab','SM_Env_Lillypads_*.prefab','FX_Bee_Large_01.prefab','FX_BumbleBees_01.prefab','FX_Honeybees_01.prefab','FX_Ladybugs_01.prefab','FX_Dandelion_Blowing_01.prefab','FX_Birds_0*.prefab','FX_Butterflies_01.prefab','FX_Frogs_01.prefab','FX_Fish_01.prefab','FX_Fireflies_01.prefab','FX_Wisps_01.prefab','FX_Chimney_Smoke_01.prefab'` | **52,1** |
| **POLYGON_MeadowForestBiome** | Pradera de afuera y Outer World · paleta **Pradera** | `SM_Env_Tree_Birch_*`, `SM_Env_Tree_Fruit_*`, `SM_Env_Tree_Meadow_*`, `SM_Env_Wildflowers_01-03`, `SM_Env_Flowers_Flat_*`, `SM_Env_Bush_*`, `SM_Env_Grass_Bush_*`, `SM_Env_Sunflower_*`, `SM_Prop_Mushroom_*` (grupos/sparse), `SM_Prop_Leaves_*`, rocas pequeñas, `SM_Prop_Birdhouse_*`, `SM_Prop_Meadow_Fence*`; FX `FX_Butterflies_Blue/Cabbage/Lunar/Monarch`, `FX_Petals_*`, `FX_Leaves_*`, `FX_Dust_Spots` | `'SM_Env_Tree_Birch_*.prefab','SM_Env_Tree_Fruit_*.prefab','SM_Env_Tree_Meadow_*.prefab','SM_Env_Wildflowers_0*.prefab','SM_Env_Flowers_Flat_*.prefab','SM_Env_Bush_*.prefab','SM_Env_Grass_Bush_*.prefab','SM_Env_Sunflower_*.prefab','SM_Prop_Mushroom_*.prefab','SM_Prop_Leaves_*.prefab','SM_Env_Rock_Pile_*.prefab','SM_Env_Rock_Small*.prefab','SM_Prop_Birdhouse_*.prefab','SM_Prop_Meadow_Fence*.prefab','FX_Butterflies_*.prefab','FX_Petals_*.prefab','FX_Leaves_*.prefab','FX_Dust_Spots_*.prefab'` | **157,0** (sin `Wildflowers_Patch_*` ni `Lillies`: 52 + 16 MB de FBX/texturas; con ellos 228) |
| **POLYGON_EnchantedForestBiome** | Salas de bosque del Brawl · paleta **Crepúsculo** (noche con luciérnagas) · sala de **minerales** · entrada a la bajada | `SM_Env_Fern*`, `SM_Env_Undergrowth_Fern_*`, `SM_Env_Mushroom*` (cap/small/grupos), `SM_Env_Moss_Lumps_*`, `SM_Env_Roots*`, `SM_Env_Tree_Small/Medium/Large_*`, `SM_Env_Log_*`, `SM_Env_Vines_*`, `SM_Env_Branch_*`, **`SM_Prop_Crystal_01-08`, `SM_Prop_Geode_*`** (Minerita); FX `FX_Fireflies`, `FX_Fireflies_Large`, `FX_Wisps`, `FX_Sparkles`, `FX_Sparkle_Static`, `FX_Birds_Fantail`, `FX_Weta` | `'SM_Env_Fern*.prefab','SM_Env_Undergrowth_Fern_*.prefab','SM_Env_Mushroom*.prefab','SM_Env_Moss_Lumps_*.prefab','SM_Env_Roots*.prefab','SM_Env_Tree_Small_*.prefab','SM_Env_Tree_Medium_*.prefab','SM_Env_Tree_Large_*.prefab','SM_Env_Log_*.prefab','SM_Env_Vines_*.prefab','SM_Env_Branch_*.prefab','SM_Prop_Crystal_*.prefab','SM_Prop_Geode_*.prefab','FX_Fireflies*.prefab','FX_Wisps_*.prefab','FX_Sparkles_*.prefab','FX_Sparkle_Static_*.prefab','FX_Birds_Fantail_*.prefab','FX_Weta_*.prefab'` | **111,3** |
| **POLYGON_AlpineMountainBiome** | Paleta **Nevado** del Brawl | `SM_Env_Pine_01-05`, `SM_Env_Pine_Stump_01`, `SM_Env_Snow_Mound_01-04`, `SM_Env_Ice_Sheet_01-06`, `SM_Env_Bush_Flower_01`, `SM_Env_Rock_Cliff_01-07`, `SM_Env_Stalactite_01-08`; FX `FX_Snow_Dust_01`, `FX_Hawk_01`, `FX_Aurora_Mesh_01/02` | `'SM_Env_Pine_0*.prefab','SM_Env_Pine_Stump_*.prefab','SM_Env_Snow_Mound_*.prefab','SM_Env_Ice_Sheet_*.prefab','SM_Env_Bush_Flower_*.prefab','SM_Env_Rock_Cliff_0*.prefab','SM_Env_Stalactite_*.prefab','FX_Snow_Dust_01.prefab','FX_Hawk_01.prefab','FX_Aurora_Mesh_0*.prefab'` | **53,7** |
| **POLYGON_Dungeon** (solo cueva) | Paleta de **cueva** pedida en `Index/33` P1 #17: bordes de sala | `SM_Env_Cave_01/02`, `_Curved`, `_Large`, `_Background*`, `_Roof_01` (+ `_DoubleSided`) | `'SM_Env_Cave_*.prefab'` | **1,1** |
| **POLYGON_DungeonRealms** (solo cristales) | Cueva y sala de minerales | `SM_Env_Crystals_Cluster_Large_01-04`, `SM_Env_Ore_Pile_*`; FX `FX_Gold_Sparkle`, `FX_FallingDust(_Small)`, `FX_Big_Sparkle` | `'SM_Env_Crystals_Cluster_*.prefab','SM_Env_Ore_Pile_*.prefab','FX_Gold_Sparkle_*.prefab','FX_FallingDust*.prefab','FX_Big_Sparkle_*.prefab'` | **2,3** |

**Fauna animada:** en POLYGON solo hay cánidos (`POLYGON_Dog`). Para el barrio (perro de un vecino, zorro en la pradera): `SK_Dog_Shiba_Collar_01`, `SK_Dog_GoldenRetrieve_Collar_01`, `SK_Dog_Fox_01` → `-Include 'SK_Dog_Shiba_Collar_01.prefab','SK_Dog_GoldenRetrieve_Collar_01.prefab','SK_Dog_Fox_01.prefab'`, **15 MB** (opcional; 1 GUID sin resolver en el zorro). Ciervos, conejos, aves en tierra, gatos y granja: **hueco** (solo SIMPLE, excluido por estilo). La fauna ambiental queda cubierta por las partículas de los biomas (abejas, mariquitas, mariposas, pájaros, ranas, peces, luciérnagas, fuegos fatuos, halcón).

---

## Prioridad (d) · Otros paquetes útiles

| Pack | Para qué | `-Include` (listo) | MB |
|---|---|---|---|
| **POLYGON_FantasyVillage** (props; importar junto con (c)) | Plaza del barrio y tienda: `SM_Prop_Fountain_01-03` + `FX_Fountain_Water_01`, `SM_Prop_Lantern_01-03`, `SM_Prop_Bench_01/02`, `SM_Prop_Picnic_Bench_01`, `SM_Prop_Sign_*` (28), `SM_Prop_Plushie_01` (juguete), `SM_Prop_Bowl_*` y `SM_Prop_Food_Bowl_Insert_*` (cocina de snacks), `SM_Prop_Shelves_*` (almacén), `SM_Prop_Bunting_*` (escenario/concursos) | `'SM_Prop_Fountain_0*.prefab','FX_Fountain_Water_01.prefab','SM_Prop_Lantern_0*.prefab','SM_Prop_Bench_0*.prefab','SM_Prop_Picnic_Bench_01.prefab','SM_Prop_Sign_*.prefab','SM_Prop_Plushie_01.prefab','SM_Prop_Bowl_0*.prefab','SM_Prop_Food_Bowl_*.prefab','SM_Prop_Shelves_*.prefab','SM_Prop_Bunting_*.prefab'` | **14,9** |
| **POLYGON_FantasyKingdom** (recorte) | **Tablero de misiones** del Outer World (`SM_Prop_Quest_Board_01` + `_Posters_01`), puestos del mercado del vendedor de genes (`SM_Prop_Market_Stall_01-03`, `SM_Prop_Market_Label_*`), fuente, carteles de dirección, bancos, jaulas | `'SM_Prop_Quest_Board_*.prefab','SM_Prop_Market_Stall_*.prefab','SM_Prop_Market_Label_*.prefab','SM_Env_Fountain_01.prefab','FX_Fountain_01.prefab','SM_Prop_Direction_Sign_*.prefab','SM_Prop_Bench_Seat_*.prefab','SM_Prop_Cage_0*.prefab'` | **7,0** |
| **POLYGON_Dog** (solo props) | Tienda de mascotas: comederos/bebederos (`SM_Prop_Bowl_Food/Water/Metal/Blue/Green_01`), cama, casita, transportín (`SM_Prop_Carrier_01`), cepillos (baño y peluquería), juguetes (`SM_Prop_Toy_Chicken/Duck/RubberBone_01`, pelotas, lanzapelotas), bolsa de comida, chapitas, **aparatos de agility** (`SM_Prop_Obstacle_*`: gimnasio, etapa 4) | `'SM_Prop_Bowl_*.prefab','SM_Prop_Bed_01.prefab','SM_Prop_House_01.prefab','SM_Prop_Carrier_01.prefab','SM_Prop_Brush_*.prefab','SM_Prop_Toy_*.prefab','SM_Prop_Ball_0*.prefab','SM_Prop_Bone_01.prefab','SM_Prop_FoodBag_01.prefab','SM_Prop_Obstacle_*.prefab','SM_Prop_Tag_*.prefab'` | **1,4** |
| **POLYGON_ParticleFX** (recorte) | Feel del loop (`Index/33` P0.8): venta (`FX_Money_Coins*`, `FX_Confetti_*`), evolución (`FX_LevelUp_01`, `FX_ExperienceGain_01`), eclosión/afecto (`FX_Pickup_Heart_01`, `FX_Sparkles_*`, `FX_Sparkle_Orbit_*`, `FX_RainbowSparkle_01`, `FX_RainbowGlow_*`), baño (`FX_Bubble_01`, `FX_Bubbles_Float_01`), curación en el Brawl (`FX_Heal_01/02`, `FX_Healing_Cirle_01/02`), aturdido (`FX_StarStunned_01/02`), pasos y saltos cartoon (`FX_Cartoony_*`), polvo e impacto suaves, `FX_Fairy_01`, `FX_Swirl_*` | `'FX_Cartoony_*.prefab','FX_Confetti_*.prefab','FX_Money_Coins*.prefab','FX_Heal_0*.prefab','FX_Healing_Cirle_*.prefab','FX_LevelUp_01.prefab','FX_ExperienceGain_01.prefab','FX_Pickup_Heart_01.prefab','FX_StarStunned_0*.prefab','FX_Sparkles_*.prefab','FX_Sparkle_Orbit_*.prefab','FX_RainbowSparkle_01.prefab','FX_RainbowGlow_0*.prefab','FX_Bubble_01.prefab','FX_Bubbles_Float_01.prefab','FX_Impact_Small_01.prefab','FX_Impact_Dirt_01.prefab','FX_Dust_Small_01.prefab','FX_Dust_Big_01.prefab','FX_Swirl_0*.prefab','FX_Fairy_01.prefab','FX_Smoke_White_Small_01.prefab','FX_Steam_01.prefab','FX_Leaves_Blossom_01.prefab'` | **7,8** |
| **POLYGON_Icons** (recorte) | Marcadores 3D sobre vecinos con misión (`SM_Icon_ExclamationMark_*`, `SM_Icon_QuestionMark_*`) y fuente para íconos renderizados del hotbar/encargos: corazón, monedas, gema (Minerita), ADN, comida, regalo, estrella, medalla, trofeo, reloj de arena, cuencos, cama, poción, cofre, fondos | `'SM_Icon_Heart_*.prefab','SM_Icon_Coin*.prefab','SM_Icon_Gem_*.prefab','SM_Icon_DNA_*.prefab','SM_Icon_Food_*.prefab','SM_Icon_Present_*.prefab','SM_Icon_ExclamationMark_*.prefab','SM_Icon_QuestionMark_*.prefab','SM_Icon_Star_*.prefab','SM_Icon_Medal_*.prefab','SM_Icon_Trophy_*.prefab','SM_Icon_Hourglass_*.prefab','SM_Icon_Bowls_*.prefab','SM_Icon_Bed_*.prefab','SM_Icon_Crafting_Feather_*.prefab','SM_Icon_Crafting_Mushroom_*.prefab','SM_Icon_Potion_*.prefab','SM_Icon_Chest_*.prefab','SM_Icon_Backing_*.prefab'` | **3,5** |

Alternativas consideradas y no elegidas: `POLYGON_Shops` (moderno, choca con madera de cuento), `POLYGON_Farm` (granja moderna), `SIMPLE_*` (estilo), `POLYGON_SwampMarshlandBiome` (solo si aparece una paleta de pantano: trae ranas, murciélagos, libélulas y grullas en FX).

---

## Totales (dry-run)

| Prioridad | MB |
|---|---|
| (a) Sidekick: Villagers 380,1 + Knights 34,0 + Sorcerers 76,0 | 490,1 |
| (b) Animaciones: Locomotion 49,2 + Idles 84,9 + Emotes 103,1 | 237,2 |
| (c) Flora: FantasyVillage 52,1 + Meadow 157,0 + Enchanted 111,3 + Alpine 53,7 + cueva 1,1 + cristales 2,3 | 377,5 |
| (d) Props/FX/íconos: Village props 14,9 + Kingdom 7,0 + Dog 1,4 + ParticleFX 7,8 + Icons 3,5 | 34,6 |
| **Total recomendado** | **≈ 1.139 MB (1,14 GB)** |
| Opcionales: presets Villagers 50,9 · perros/zorro 15,0 | + 65,9 |

Notas del total: lo compartido entre biomas (`PNB_Core`, `WeatherControl`) se cuenta en cada llamada pero se importa una vez (pocos MB). Las mallas de outfit de Villagers pesan ~4,5 MB cada una (blendshapes); Knights ~0,3 MB. Ningún paquete supera 500 MB.

---

## Riesgos

1. **Licencia / git:** `/Assets/Synty/` y `/Assets/DownloadCache/` ya están en `.gitignore`; todo lo de arriba cae bajo `Assets/Synty/` (las animaciones van a `Assets/Synty/Animation*`). Cada PC tiene que importar lo mismo (las dos PCs): conviene una lista de comandos única. `Install-Pack` crea/actualiza `SYNTY_ASSETS.md` en la raíz del proyecto: decidir si se versiona (sirve de receta para la otra PC). Nada de prefabs propios que referencien Synty puede funcionar en una PC sin el import.
2. **Mutación de assets:** importar = mutar el proyecto → **requiere OK de Juan** (CLAUDE.md, paso 8). Con el editor abierto `Install-Pack` devuelve `editor-open` y la línea `AssetDatabase.ImportPackage(...)` para correr por MCP/CLI (el MCP estuvo caído en S161).
3. **Shaders / URP:** Sidekick usa `Sidekick_ShaderGraph`, ya presente por el Tool (GUID `db6285…`). Los biomas traen shaders `PNB_Core` (Shader Graph, URP OK); no reciben nuestro toon: aplicar el mismo criterio de S156 (`_RampInfluence`) o materiales propios y comparar con capturas. GUID sin resolver: `FantasyVillage_Wind_01.mat` (1) y `FX_Fireflies_01` de FantasyVillage (3) → revisar que no salgan rosas; los controllers `AC_Sidekick_*` de BaseLocomotion referencian 7 GUID ausentes → **no importarlos** (el recorte ya los excluye). Las texturas de máscara Sidekick faltan siempre (esperado, se ve bien sin ellas).
4. **Animaciones en nuestro rig:** los clips Sidekick vienen para `SidekickSyntyCharacter` (se importa ~1 MB de malla de referencia). Comprobar que importen como **Humanoid** y retargeteen sobre los cuerpos de `HumanBodyAssembler`; el nombre del clip interno no siempre coincide con el FBX (p. ej. `A_MOD_IDL_Base_Masc.fbx` → clip `A_MOD_IDL_Idle_Base_Masc`).
5. **Código:** `HumanBodyAssembler` tiene las rutas fijas a `Outfits/Starter/…`; usar Villagers/Knights/Sorcerers pide sumar prefijos `Outfits/FantasyVillagers/`, etc. y un catálogo por rol (trabajo de `morimonchi-coder`, fuera de esta propuesta).
6. **Rutas largas:** el proyecto está en `E:\GitHub\RunRunSimulator` (25 caracteres): sin riesgo. Ojo si se abre desde la junction `C:\Users\USUARIO\Documents\GitHub\RunRunSimulator` (50): sigue bajo el umbral de ~120.
7. **Estilo:** no mezclar los personajes POLYGON de FantasyVillage (animales y humanos `SM_Chr_*`) con los Sidekick en la misma escena; los recortes de arriba no los incluyen.
8. **Peso:** ~1,1 GB más en `Assets` (y su `Library`). Se recortaron los FBX más pesados de Meadow (`Wildflowers_Patch_*`, `Lillies`) porque las flores ya las hace `ShopGrassField`.

---

## Orden de importación sugerido

1. **ANIMATION_BaseLocomotion + Idles + Emotes** (recortes, 237 MB): mejora visible inmediata sobre los 5 caballeros actuales sin tocar personajes; permite retirar `HumanoidClipBaker` para NPCs.
2. **SIDEKICK_FantasyVillagers** outfits (380 MB) → actualizar `HumanBodyAssembler` y armar clientes civiles + el tío.
3. **SIDEKICK_FantasyKnights** y **FantasySorcerers** outfits (110 MB) → variedad de clientes y vendedor de genes.
4. **POLYGON_FantasyVillage** entorno + FX + props en **una sola llamada** (67 MB) → exterior de la tienda y barrio.
5. **POLYGON_MeadowForestBiome** (157 MB) → pradera exterior y paleta Pradera.
6. **POLYGON_EnchantedForestBiome + Dungeon (cueva) + DungeonRealms (cristales)** (115 MB) → Crepúsculo, cueva y minerales del Brawl.
7. **POLYGON_AlpineMountainBiome** (54 MB) → Nevado.
8. **FantasyKingdom, Dog props, ParticleFX, Icons** (20 MB) → plaza/misiones y feel; con el Outer World decidido.

Comando tipo (desde Bash): `powershell -NoProfile -ExecutionPolicy Bypass -Command "& 'E:\GitHub\AssetVaultFinder\tools\Install-Pack.ps1' -Pack <ID> -Project 'E:\GitHub\RunRunSimulator' -Include <patrones de la tabla> -DryRun"` y repetir sin `-DryRun` tras el OK.
