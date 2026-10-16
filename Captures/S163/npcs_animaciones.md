# NPCs Sidekick y animaciones (S163)

> Solo lectura de `Assets/`. Todo lo nuevo vive en `Tools/Blender/anims/`. Sin Unity MCP.
> Prefijos de ruta: **BL** = `Assets/Synty/AnimationBaseLocomotion/Animations/Sidekick/{Masculine|Feminine}/`, **IDL** = `Assets/Synty/AnimationIdles/Animations/Sidekick/{G}/`, **EMOT** = `Assets/Synty/AnimationEmotesAndTaunts/Animations/Sidekick/{G}/`. Sufijo `_Masc` / `_Femn`.

## 1. Roles y piezas

Regla: cada rol parte de un preset de Synty (`.sk` leído del `.unitypackage` de la bóveda) y cambia solo cabeza, pelo o accesorios. Todas las piezas existen en `SidekickCharacters/Resources/Meshes/{Outfits/<Pack>|Species/Humans}` (verificado parte por parte). Las piezas de cara que no se nombran son `SK_HUMN_BASE_01_*` (cabeza, ojos, cejas, orejas, nariz, manos).

- Receta completa (lista de 20-28 piezas por rol + BodyType/BodySize/Muscle): `Tools/Blender/anims/npc_roles.json`.
- Lineup en T-pose (silueta, colores por tipo de pieza, no los del Tool): `Tools/Blender/anims/npc_roles_r1.png`, `_r2.png`, `_r3.png`.

| Rol | Body Type (anim) | Base | Cambios sobre el preset | Lectura visual |
|---|---|---|---|---|
| Protagonista | Masculine (BT −100) — **decide Juan** | sin preset | `VILL_03_10TORS`, `VILL_02_11/12 AUP*`, `VILL_01_13/14 ALW*` (mangas para FPArms), `VILL_04_17HIPS`, `VILL_01_18/19 LEG*`, `VILL_01_20/21 FOT*`, pelo `HUMN_BASE_08_02HAIR` | Camisa y pantalón civiles limpios, sin accesorios |
| Tío | Masculine (BT −100, talla 57) | `FantasyVillagers_01` | ninguno | Barbudo con gorro, delantal, bolsa y **un bichito en el hombro** (`VILL_01_30ASHR`): perfecto para la tienda de mascotas |
| Veterinaria | Feminine (BT 100) | `FantasyVillagers_02` | sin capucha `22AHED`, pelo `VILL_06_02HAIR`, sin `27AHPL`/`28AHPR` (colgaban un ave muerta) | Corsé con lazos, falda y delantal |
| Panadera | Feminine (BT 100, talla 35) | `FantasyVillagers_04` | talla −60 → 35 (más redonda) | Pelo largo, mochila con panes, jarra de leche |
| Coleccionista (vecino) | Masculine | `FantasyVillagers_05` | gafas `VILL_01_23AFAC` en vez de pipa, `VILL_10_22AHED` | Overol con herramientas y gafas redondas |
| Vendedora de genes | Feminine (BT 100) | `FantasySorcerers_04` | ninguno | Sombrero blando grande, familiar en el hombro, falda bordada. Cálida, nada oscura |
| Cliente Artista | Feminine | `FantasyVillagers_02` | boina `VILL_02_22AHED`, pelo `VILL_02_02HAIR`, torso `VILL_06_10TORS`, espalda `VILL_06_24ABAC`, sin `27/28AHP*` | Boina, chaqueta cruzada, falda en capas |
| Cliente Coleccionista | Masculine (talla 42) | `FantasySorcerers_06` | ninguno | Erudito barbudo con gorro de gnomo y lechuzas |
| Cliente Fan de los roles | Masculine / Feminine | `FantasyKnights_05` / `FantasyKnights_06` | ninguno | Armadura ligera; la F con yelmo de penacho |
| Cliente Ahorrador | Masculine (talla −35) | `FantasyVillagers_03` | `VILL_08_22AHED` en vez de la boina (la usa el Artista) | Flaco, cacerolas y herramientas colgando |
| Cliente Familia | Feminine + Masculine (pareja) | F sin preset · M `FantasyVillagers_01` | F: `VILL_05_10TORS`, `VILL_03` brazos, `VILL_02` cadera/piernas/pies, `VILL_01_24ABAC`, pelo `HUMN_BASE_10_02HAIR`. M: tío sin gorro ni bichito, pelo `VILL_03_02HAIR`, barba `HUMN_BASE_06_09FCHR` | Pareja adulta (no hay niños Sidekick) |

Descartados por tono o por piezas faltantes: `FantasySorcerers_02` (cuernos y máscara de calavera), `_05` (manos fantasma en la espalda), `FantasyKnights_01-04` (piden `SK_APOC_OUTL_*` / `SK_VIKG_WARR_*`, packs no instalados).

## 2. Acciones y clips

| Acción | Clip | Estado |
|---|---|---|
| Caminar | BL `Locomotion/Walk/A_MOD_BL_Walk_F` (+ `_RM` con root motion) | Existe M/F |
| Correr (emergencia) | BL `Locomotion/Run/A_MOD_BL_Run_F` | Existe M/F |
| Girar en el lugar | BL `Locomotion/Turn/A_MOD_BL_Turn_Standing_90L/90R/180L/180R` | Existe M/F |
| Arrancar / frenar | BL `Transitions/Idle_ToWalk/*`, `Walk_ToIdle/A_MOD_BL_Walk_ToIdleF_{L,R}Foot` (2 clips internos cada uno: `…Passing` / `…Extend`) | **Solo Masculine** |
| Parado base | IDL `Base/Stances/A_MOD_IDL_Base` (clip interno `A_MOD_IDL_Idle_Base_*`), BL `Idles/A_MOD_BL_Idle_Standing` | Existe M/F |
| Esperar en fila | IDL `Bored/Actions/A_MOD_IDL_Bored_FootTap`, `Bored_SwingArms`, `WeightShift/A_MOD_IDL_WeightShift_L/R`, `ArmsFolded/Stances/A_MOD_IDL_ArmsFolded_Casual_Enter/Loop/Exit`, `Yawn`; EMOT `Sad/A_MOD_EMOT_Sad_Tired` (harto) | Existe M/F |
| Mirar vitrina | IDL `Thoughtful/Stances/A_MOD_IDL_Thoughtful_{L,R}_Enter/Loop/Exit`, `Thoughtful/Actions/…ChinScratch`, `Look/Actions/A_MOD_IDL_Look_{L,R,Down}`, `Inspect/Actions/A_MOD_IDL_Inspect_Hands`, `PointHand/Actions/A_MOD_IDL_PointHand_Index_F(_Small)` | Existe M/F |
| Negociar | IDL `HeadNod/Actions/A_MOD_IDL_HeadNod_{Small,Large,Thanks}`, `HeadShake/Actions/A_MOD_IDL_HeadShake_{Small,Disappointed}`, `Plead/Actions/A_MOD_IDL_Plead_F`, `HandsOnHips/Stances/…Base_Enter/Loop/Exit`; EMOT `Sad/A_MOD_EMOT_Sad_Shrug` | Existe M/F |
| Contento al comprar | EMOT `Happy/A_MOD_EMOT_Happy_{ThumbsUp,TwoThumbs_Mild,Nodding_Confident,ArmsRaised,FistPump}`, `Celebrate/A_MOD_EMOT_Celebrate_{Clapping_Polite,HandOnHeart}`, `Affection/A_MOD_EMOT_Affection_HeartHands` | Existe M/F |
| Descontento | EMOT `Reproach/A_MOD_EMOT_Reproach_{WaveAway,ShakeFinger}`, `Sad/A_MOD_EMOT_Sad_Facepalm`, `Angry/A_MOD_EMOT_Angry_ShakeFist` (solo enojo fuerte) | Existe M/F |
| Saludar | IDL `Wave/Stances/A_MOD_IDL_Wave_Small_Enter/Loop/Exit`, `HeadNod/Actions/A_MOD_IDL_HeadNod_Greet`; EMOT `Greet/A_MOD_EMOT_Greet_{Wave,WaveOver,Bow,Curtsy}` (clips internos `Greeting_Bow_Femn` y `Greeting_Curtsy_Masc`) | Existe M/F |
| Agacharse a ver un MoriMochi | BL `Transitions/Stand_ToCrouch` → `Idles/A_MOD_BL_Idle_Crouching` → `Transitions/Crouch_ToStand`; alternativa de rodillas IDL `Pray/Stances/A_MOD_IDL_Pray_Kneeling_Enter/Loop/Exit` | Idle agachado M/F; **transiciones solo Masculine** |
| Agarrar un MoriMochi del suelo | `Tools/Blender/anims/A_MM_PickUp_Floor_{Masc,Femn}.fbx` (1,6 s) | **Nuevo** |
| Recibir un MoriMochi del mostrador | `Tools/Blender/anims/A_MM_Receive_{Masc,Femn}.fbx` (1,2 s, termina en pose de cargar) | **Nuevo** |
| Cargar en brazos | `Tools/Blender/anims/A_MM_Carry_Loop_{Masc,Femn}.fbx` (2,0 s, loop) | **Nuevo** |
| Entregar / dejar en el mostrador | `Tools/Blender/anims/A_MM_HandOver_{Masc,Femn}.fbx` (1,2 s, de cargar a idle) | **Nuevo** |
| Pagar en la caja | `Tools/Blender/anims/A_MM_Pay_{Masc,Femn}.fbx` (1,0 s, mano derecha palma arriba) | **Nuevo** |
| Sentarse en banco | `Tools/Blender/anims/A_MM_Sit_Enter / Sit_Loop / Sit_Exit_{Masc,Femn}.fbx` (1,2 s / 2,0 s loop / 1,2 s) | **Nuevo** (no hay sit en ningún pack Sidekick de la bóveda) |
| Rutinas de vecinos | IDL `Lean/Stances/Base/A_MOD_IDL_Lean_B_Base_Enter/Loop/Exit` (apoyado en pared), `Eat_Small`, `Drink_Sip`, `Stretch_Arms`; sentarse = clips nuevos; trabajar (hornear, curar) = combinar `Inspect_Hands`/`Carry_Loop` | Existe M/F + nuevos |
| Sostener taza/comida en loop (opcional) | `A_MOD_IDL_Drink_Hold_*` y `Eat_Hold_*` están en la bóveda pero **no importados** | Falta importar |

Cobertura: 16 de 20 acciones salen de clips existentes; 4 (agarrar, cargar, entregar/pagar, sentarse) se crearon: 8 clips × 2 cuerpos = **16 FBX nuevos**.

## 3. Clips nuevos (cómo se hicieron)

- Generador: `Tools/Blender/anims/make_npc_anims.py` (`blender -b --python make_npc_anims.py -- <Masc|Femn> <carpeta> [clips]`). Parte, fotograma a fotograma, del idle real del pack (`A_MOD_IDL_Base_<G>.fbx`, misma respiración y misma postura), le suma inclinación de columna/cabeza en ejes de mundo, mueve la pelvis cuando hace falta, resuelve brazos y piernas con un IK analítico de dos huesos (codo afuera-abajo, rodilla adelante, pies plantados con la orientación original) y aplica pronación/supinación de muñeca y cierre de dedos.
- Mismo esqueleto: el armature sale del FBX del idle (91 huesos, mismos nombres). Export: FBX 7.4, `UnitScaleFactor 1`, Y-up, 30 fps, todos los huesos con curva por fotograma, take = nombre del clip (`A_MM_Receive_Masc`, …).
- `.blend` de trabajo: `A_MM_NpcAnims_Masc.blend`, `A_MM_NpcAnims_Femn.blend`.
- Verificación: `render_check.py` reimporta cada FBX exportado (no la escena de trabajo) y lo maneja sobre el `SK_BaseModel` con shape key `masculineFeminine` según el cuerpo, con mostrador, banco y una esfera de MoriMochi. Hojas `A_MM_<Clip>_<G>_check.png` (arriba 3/4 frontal, abajo perfil; 4 fotogramas, 2 en `Sit_Loop`). Revisé 13 de las 16 hojas (sin brazos que atraviesen el cuerpo ni rotaciones raras). Las 3 que no miré (`Carry_Loop_Femn`, `Sit_Loop_Femn`, `Sit_Exit_Masc`) comparten parámetros con su pareja ya revisada. La primera versión usaba el IK de Blender y rompía los brazos porque las colas de los huesos Sidekick no apuntan al hijo. Se cambió por el IK propio.
- Medidas que asumen los clips (mundo, raíz en el origen, mirando a −Z en Unity): mostrador con tapa a ~0,88 m y MoriMochi a 0,40 m delante; banco con asiento a ~0,39 m, de 0,12 a 0,52 m detrás de la raíz; MoriMochi del suelo a 0,34 m delante. `Receive` termina en la pose de `Carry_Loop`, y `HandOver` y `PickUp_Floor` empiezan o terminan en ella. La fase de respiración difiere: conviene un crossfade de 0,1-0,15 s.

## 4. Qué falta en código (sin escribirlo)

1. **`HumanBodyAssembler`**: reemplazar las 5 `Recipes` fijas a `Outfits/Starter/SK_FANT_KNGT_17_*` por recetas por rol (las de `npc_roles.json`: nombre de pieza completo, ya que el prefijo de pack cambia por pieza) que busquen en `Outfits/FantasyVillagers|FantasyKnights|FantasySorcerers|Starter` y `Species/Humans`. Debe aplicar BodyType/BodySize/Muscle (`BlendShapes` de Sidekick) y guardar en el catálogo el **Body Type** de cada cuerpo, porque elige el set de clips.
2. **`HumanBodyCatalogSO`**: entradas por rol/arquetipo (y no solo una lista plana), con un flag Masc/Fem o un `AnimatorOverrideController` por cuerpo. `NpcBody` hoy elige al azar: pasaría a elegir según `CustomerArchetypeSO` (cliente) o `NeighborSO` (vecino).
3. **Controller nuevo** (reemplaza `HumanNpc` de `HumanoidClipBaker`): un controller base con locomoción en blend tree (Idle / Walk / Run por `Speed`, turns opcionales) y estados `Browse` (Thoughtful/Look), `Queue` (Bored/WeightShift aleatorio), `Negotiate` (HeadNod/Shake/Plead), `React` (Happy o Reproach por trigger según el resultado), `Receive → Carry` (la capa superior con máscara de brazos permite caminar cargando), `Pay`, `HandOver`, `Crouch`, `Sit`. Dos `AnimatorOverrideController` (Masc y Fem) cambian solo los clips. Parámetros nuevos: `Mood`/trigger `Happy`/`Upset`, `Carrying` (bool), triggers `Pay`, `Receive`, `HandOver`, `Sit`.
4. **`NpcBody`**: traducir más estados de `NpcAgent` (InspectingDisplay → Browse, Queueing → Queue, compra aceptada/rechazada → React, Purchased → Receive + Carry al irse). Anclar el MoriMochi vendido al hueso `prop_r` o al punto medio de las manos mientras `Carrying`.
5. **Import en Unity** (lo hace quien tenga el editor): copiar los FBX `A_MM_*` a una carpeta del proyecto, Rig Humanoid → *Copy From Other Avatar* con el avatar de `SidekickSyntyCharacter` (igual que los `A_MOD_*`, `avatarSetup: 2`) o *Create From This Model*; marcar `Loop Time` en `Carry_Loop` y `Sit_Loop`; *Bake Into Pose* en root Y/XZ.

## 5. Riesgos

- **Nodo extra `Armature`**: el exportador de Blender agrega un nodo raíz `Armature` (los `A_MOD_*` empiezan en `root`). Los músculos humanoides no se ven afectados. Los huesos no humanoides (`prop_r`, `*Attach`) quedan con otra ruta y no animan. Hay que verificarlo al importar; si *Copy From Other Avatar* falla por jerarquía, usar *Create From This Model*.
- **Transiciones Feminine faltantes**: el recorte importado de BaseLocomotion trae `Idle_ToWalk`, `Walk_ToIdle`, `Stand_ToCrouch` y `Crouch_ToStand` solo para Masculine. Hay que importar las Feminine o usar crossfades.
- **Flags de loop inconsistentes en los metas de Synty**: `Turn_*` Masc con `loopTime 1`, Fem con 0; `Wave_Small_Loop` y `Pray_Kneeling_Loop` con 0; `Thoughtful_L_ChinScratch_Masc` con 0 y el Fem con 1. Hay que revisarlos al armar el controller.
- **Nombres internos ≠ FBX**: `A_MOD_IDL_Base_*` → `A_MOD_IDL_Idle_Base_*`, `Greet_Bow_Femn` → `Greeting_Bow_Femn`, `Greet_Curtsy_Masc` → `Greeting_Curtsy_Masc`, `Walk_ToIdleF_*` trae 2 clips.
- **Clips nuevos a ojo**: las poses se calibraron con renders del modelo base, no con los outfits. Delantales largos (Panadera, Veterinaria) y la falda de la Vendedora pueden clipear al sentarse o agacharse. Hay que verificarlo en Play con capturas.
- **Escala de cuerpo**: BodySize ±60 cambia el largo de brazos muy poco (el esqueleto es fijo). Con el retarget humanoide las manos pueden no cerrar exacto sobre el MoriMochi en cuerpos gruesos. Se puede corregir con IK de Unity (`OnAnimatorIK`) si molesta.
- **Colores**: los lineups son siluetas; los colores cálidos estilo Fantasy Village salen del ColorSet en `BuildPresetMaterials`. Hoy se usan los grupos de "Fantasy Knights NN" y hace falta mapear los de Villagers/Sorcerers.
- **Git**: `Tools/Blender/anims/` pesa ~14 MB de FBX + PNG. Los FBX son derivados de clips Synty (esqueleto e idle base): ojo con la licencia si el repo se hace público.
