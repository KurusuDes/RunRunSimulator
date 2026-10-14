# Props de la tienda (S153) - hoja de ruta y brief para agentes modeladores

Objetivo (Index/34 D6 + E11): reemplazar los cubos de ProBuilder del equipamiento por modelos en la linea de **KayKit** (toony, chunky, colores planos pastel) que encajen con los MoriMonchis (dragones regordetes SD).

## Pipeline
- Cada prop = `Tools/Blender/props/<Nombre>.py`, que importa los helpers:
  ```python
  import sys
  sys.path.insert(0, r"C:\Users\Docente\Desktop\UnityProyects\RunRunSimulator\Tools\Blender\props")
  from props_common import *
  out, flags = cli()
  begin()
  # ... construir partes con finish(nombre, bmesh, "SH_Color") ...
  ob = join_all("<Nombre>")
  report(ob)
  export(ob, flags)          # -> Assets/RunRunSimulator/Resources/Models/Shop/<Nombre>.fbx
  preview(ob, out, dragon_loc=(x, y, 0))   # hoja de contacto <out>/<Nombre>_sheet.png (6 vistas)
  ```
- Correr (PowerShell): `& "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b -P <script> -- <out_dir> [noexport]`
- `props_common.py` NO se edita. Helpers: `lathe_bm`, `ellipsoid_bm`, `tube_bm(points, radii, sides)`, `torus_bm`, `rbox_bm(center,size,r)`, `soft_box(center,size,rc,R)`, `loft`/`rbox_rings`/`rrect`, `rslab`-like via loft, `catmull`, `xf(bm, matrix)`. Si necesitas otro helper, va en tu script.
- **Materiales**: solo los de `PALETTE` (`SH_*`); Unity los remapea por nombre a materiales Toon compartidos. Maximo 4-5 materiales por prop.
- **Ejes**: Blender Z arriba, **frente = -Y** (la vista `front` mira desde -Y). Origen en el centro de la huella, **base en z = 0**.
- **Escala**: metros reales de juego. `preview` pone un MoriMochi de referencia a escala de juego (0,99 m de alto) donde digas con `dragon_loc` (al lado, sin tocar el prop).
- Estilo de referencia ya aprobado: `shop_corral.py`, `shop_pc.py`, `shop_incubator.py` (ojo: su dragon de referencia esta a escala 1.0, el de `preview` esta a 0.7, el correcto).

## Vara de calidad (KayKit)
- Volumenes gordos y redondeados: biseles generosos (2-6 cm), nada de piezas finas (< 3 cm de grosor) ni palitos.
- 2-4 colores planos por prop, uno dominante; sin texturas. Contraste claro entre partes (madera clara vs oscura, crema vs acento).
- Proporciones exageradas y amables (patas cortas y gruesas, tapas abombadas, bordes rebordeados), un detalle con encanto (estrella, corazon, huellita, tornillos gordos) pero sin recargar.
- Silueta legible desde arriba-en-diagonal (la camara del juego es tercera persona alta): juzgar con la vista `iso` y `34`.
- Presupuesto: props chicos < 2500 tris, grandes < 6000 tris.
- Sin huecos ni piezas flotando: las uniones se hunden unos mm.
- **Bucle obligatorio**: render -> abrir tu `_sheet.png` con Read -> corregir -> repetir hasta que se vea al nivel de `shop_corral`/`shop_pc` y bien proporcionado al lado del MoriMochi. Minimo 2 iteraciones.

## Lista de props
Huella = lo que ocupa en el suelo (X x Y), Alto = Z. Los numeros vienen de los colliders/obstaculos de la escena.

| # | Nombre | Que es en el juego | Huella / alto | Idea |
|---|--------|--------------------|---------------|------|
| A1 | `ShopFeeder` | Comedero (estacion de comida, se rellena) | <= 0.8 x 0.8 / 0.5-0.7 | tolva de grano con ventanita de nivel sobre un plato ancho; coral + crema + paja |
| A2 | `ShopWater` | Bebedero (estacion de agua) | <= 0.8 x 0.8 / 0.6-0.8 | garrafon invertido sobre base con plato de agua; cielo/agua + crema |
| A3 | `ShopBed` | Cama (descanso) | <= 0.95 x 0.95 / 0.3-0.4 | cama redonda acolchada con borde inflado y mantita; lila + durazno + crema |
| A4 | `ShopPlayStation` | Estacion de juego (Sala de juegos) | <= 0.8 x 0.8 / 0.8-1.1 | torre de juego chiquita: plataforma, rampa/tobogan corto, pelota; menta + coral + paja |
| B1 | `ShopRegister` | Caja registradora (los clientes pagan) | 1.0 x 0.8 / ~1.3 | mostradorcito de madera con caja registradora retro 80s encima (teclas gordas, cajon, cartel "$"); frente = lado del cliente (-Y) |
| B2 | `ShopShowcase` | Vitrina: zona 3 x 3 donde los MoriMonchis esperan comprador | 3.0 x 3.0 / tarima 0.12, baranda <= 0.5, cartel <= 1.6 | tarima baja con alfombra, baranda baja de vidrio/madera con hueco de entrada al frente, cartel colgante con estrella y etiqueta de precio |
| B3 | `ShopLockedSign` | Cartel de zona bloqueada (expansion por comprar) | tablero 2.4 x 0.1 x 1.1 centrado a 1.1 de alto | tablero de madera sobre dos postes gordos, candado grande arriba al centro, cinta de "obra" en diagonal; sin texto |
| C1 | `ShopEggShelf` | Repisa de huevos (E9): va detras de la incubadora | 1.6 x 0.45 / ~1.5 | estante de pie de 2 niveles con 6 nidos de paja (3+3) para huevos, copete con huevito tallado |
| C2 | `ShopDecorPedestal` | Pedestal de ranura de decoracion (3 por corral) | diametro 0.6 / 0.25 (la deco se apoya a 0.3) | plinto redondo con borde rebordeado y estrella en el frente |
| C3 | `ShopCorkBoard` | Panel de crianza (en la pared, cerca de la incubadora) | 0.7 x 0.08 / 0.55 (colgado) | tablero de corcho con marco gordo, fichas/fotos de arbol genealogico con hilo, chinches de color; origen en el centro del tablero (no en la base) |
| D1 | `ShopLedger` | Panel "Criaturas" (fichero) sobre mesa | 0.45 x 0.35 / 0.35 | tarjetero rolodex retro con fichas y separadores de color |
| D2 | `ShopRadio` | Panel "Bajada" (expedicion) sobre mesa | 0.45 x 0.3 / 0.45 | radio/walkie de expedicion 80s con antena gorda, dial, foco rojo |
| D3 | `ShopCrate` | Panel "Almacen" sobre mesa | 0.45 x 0.45 / 0.4 | baul/caja de madera con herrajes gordos y tapa entreabierta |
| D4 | `ShopMop` | Trapeador (prop que los MoriMonchis roban) | largo 1.2 tumbado o parado | palo gordo + cabeza de mechas en mechones gruesos; recto, origen en la base de las mechas |
| D5 | `ShopSnack` | Snack Monchi (bolsa de comida) | 0.3 x 0.2 / 0.3 | bolsa de papas inflada con cierre dentado y huellita |

Ya hechos (S152), solo se colocan: `ShopPC` + `ShopPC_Desk` (panel Tienda), `ShopIncubator`, `ShopCorral` (corral 2.8 en zona 3 x 3).

Fuera de esta tanda: juguetes (arte provisional aceptado), clientes (pack comprado H6), paredes/pisos de zonas.

## Colocacion en Unity (la hace el orquestador)
1. Materiales Toon compartidos `Materials/Shop/SH_*` con `Shader Graphs/CartoonShader` y remapeo por nombre en cada FBX.
2. El cubo/plano viejo se apaga (no se borra) y el modelo entra como hijo `Model` con la misma huella; colliders, obstaculos y puntos de interaccion no cambian.
3. Verificacion: Play, consola 0 errores, NavMesh y puntos de interaccion alcanzables.

---

# Tanda 2 (S153): diseño de la tienda (edificio y entorno)

Juan pidio tambien "los diseños de la tienda": vestir el edificio y su entorno, hoy de ProBuilder gris, con el mismo estilo KayKit.

## Fuente de verdad geometrica
- `scratchpad/shop_env/shop_env.obj`: geometria actual en **coordenadas Blender** (ya convertidas: X=-unityX, Y=-unityZ, Z=unityY). Objetos: `ENVIROMENT__PetShop` (edificio), `ENVIROMENT__Parque` (patio/cuarto trasero), `ENVIROMENT__Street`, `ENVIROMENT__BaseFloor`, `EXPANSIONS__ZONE_*__Open__Floor/Wall_*` (Criadero y Sala de juegos).
- `scratchpad/shop_env/markers.csv`: centro y tamaño de cada mueble y de cada sala (`ROOM_*` = superficies NavMesh) en coordenadas Blender, para saber que es cada cuarto.
- Importar el OBJ en Blender con `bpy.ops.wm.obj_import(filepath=..., forward_axis='Y', up_axis='Z')` (ya esta en ejes Blender; verificar con un render cenital que los markers caen dentro de las salas).

## Regla de oro: la colision NO cambia
- En Unity se apagan los renderers de ProBuilder y se **conservan sus colliders y el NavMesh**. Tu malla es solo visual y se coloca en el origen del mundo (posicion 0, rotacion 0), asi que **exporta en coordenadas de mundo** (no recentres; `export(ob, flags)` de `props_common` ya respeta la posicion de los vertices).
- Las caras que se pisan (pisos) deben quedar a la MISMA altura que el OBJ (+-1 cm). Las caras internas de las paredes a +-3 cm del plano original; los adornos (zocalo, molduras, marcos) pueden sobresalir hasta 5 cm hacia el cuarto, nunca tapar huecos de puertas.
- Respetar los huecos (puertas, ventanas, aberturas) que ya tiene la geometria original.
- La camara del juego es tercera persona alta: si el edificio no tiene techo, NO le pongas techo (solo remate superior grueso de la pared).

## Kit de paredes (comun a todos los agentes de la tanda 2)
- Pared interior: zocalo `SH_WoodDark` 0.12 alto · friso (wainscot) hasta 0.9 m en el color de la sala · moldura de silla `SH_Wood` · parte alta `SH_Cream` · remate superior grueso y redondeado `SH_WoodDark`.
- Esquinas con pilar redondeado `SH_Wood`; marcos de puertas/ventanas gordos `SH_Wood` con biseles.
- Colores de friso por sala: tienda (FrontDesk) `SH_MintSoft` · cuarto trasero (BackRoom) `SH_Peach` · deposito (StorageRoom) `SH_Sky` · Criadero `SH_Straw` (aire de granero, tablas verticales) · Sala de juegos `SH_Lilac` (lunares o estrellas grandes en la parte alta).
- Exterior de la fachada: `SH_Coral` con molduras `SH_Cream`.
- Pisos: tienda = damero grande (0.75 m) `SH_Cream`/`SH_Peach` con junta hundida · cuarto trasero = tablones `SH_Wood`/`SH_WoodDark` alternados · deposito = baldosas `SH_Beige` · Criadero = tablones `SH_WoodDark` con paja suelta · Sala de juegos = goma de colores en cuadros `SH_Mint`/`SH_Lilac`/`SH_Straw` · patio = cesped (agregar `SH_Mint` como pasto, o el verde que haga falta via un material nuevo `SH_Grass` definido en tu script) · vereda = losetas `SH_Beige` con cordon `SH_Chrome` · calle = `SH_Dark` con lineas `SH_Straw`.
- Presupuesto: edificio completo < 40k tris; cada zona < 15k; props exteriores < 3k cada uno.

## Piezas
| # | Nombre FBX | Que cubre |
|---|------------|-----------|
| E1 | `ShopBuilding` | Vestido de `ENVIROMENT__PetShop`: paredes (kit), pisos por sala, marcos de puertas/ventanas, fachada exterior |
| E2 | `ShopYard` | Vestido de `ENVIROMENT__Parque`: muros/cerca del patio, piso de cesped/caminitos |
| E3 | `ShopStreet` | Vestido de `ENVIROMENT__Street` y `ENVIROMENT__BaseFloor`: calle, vereda con cordon, suelo exterior |
| E4 | `ShopZoneCriadero`, `ShopZoneSalaJuegos` | Vestido de pisos y paredes de cada expansion (solo lo de `Open`) |
| E5 | `ShopSignMain`, `ShopAwning`, `ShopStreetLamp`, `ShopBench`, `ShopPlanter`, `ShopMailbox` | Letrero grande "MoriMonchis" con letras 3D gordas (fuente de Blender extruida y biselada) + un MoriMochi de silueta; toldo a rayas coral/crema sobre la entrada/vitrinas; farol, banca, macetero con flores, buzon |

---

# Tanda 3 (S153): estetica de la tienda v2 (feedback de Juan)

Juan: "me encanta el diseño y los props; el look debe parecer una **tienda de mascotas**; hay **mucho rojo**; quiero una paleta con **mas tonos de madera, fantasia**; no me gusta el **patron del piso** (damero)". Los props de la tanda 1 y la fachada E5 NO se tocan.

## Direccion: tienda de mascotas de cuento, hecha de madera
- Estructura de **entramado de madera** (vigas vistas tipo cabaña de cuento): postes y vigas `SH_Timber`/`SH_Walnut`, paneles de revoque `SH_Parchment`, friso bajo de tablas `SH_Honey`/`SH_Oak`, zocalo `SH_Walnut`. Base exterior de **piedra** redondeada (`SH_Stone`/`SH_StoneDark`).
- Acento de cada sala SOLO en una franja fina (moldura o guarda pintada), no en todo el friso: tienda `SH_Sage`, cuarto trasero `SH_Teal`, deposito `SH_Gold`, Criadero `SH_Moss`, Sala de juegos `SH_Plum`.
- **Cero coral/rojo** en arquitectura. Nada de pastel saturado.
- **Pisos**: tablones anchos con vetas/clavitos (tienda `SH_Oak`+`SH_Honey` alternados suave; cuarto trasero `SH_Honey`/`SH_Walnut`; deposito losas de piedra irregulares `SH_Stone`; Criadero tablones `SH_Walnut` + paja; Sala de juegos madera clara `SH_Oak` con una alfombra redonda tejida en tonos `SH_Plum`/`SH_Gold`/`SH_Sage` apagados). Nada de damero ni cuadricula de colores.
- **Fantasia** (con mesura, 2-3 recursos repetidos): vigas con extremos redondeados/tallados, faroles colgantes `SH_Gold` en las esquinas, guirnalda de hojas/hiedra `SH_Leaf`/`SH_Moss` en el remate superior, algun hongo o raiz tallada en las esquinas exteriores, marcos de ventana con arco tallado (decorativo, sin tapar el hueco).
- **Que se lea tienda de mascotas**: repisas de pared con bolsas de comida, frascos de golosinas con hueso, collares/correas colgados de ganchos, carteles tallados con huella/hueso/pez, una pecera de pared. Todo **pegado a la pared, por encima de 1.0 m y con maximo 0.30 m de saliente** (la colision no cambia).
- Exterior: fachada de tablas `SH_Honey`/`SH_Oak` con entramado `SH_Timber`, base de piedra, aleros de madera; patio con cerca de madera rustica (no muros coral), pasto `SH_Grass`/`SH_Leaf`, caminos de piedra.
- Paleta nueva ya disponible en `props_common.PALETTE` (`SH_Honey`, `SH_Oak`, `SH_Walnut`, `SH_Timber`, `SH_Parchment`, `SH_Stone`, `SH_StoneDark`, `SH_Sage`, `SH_Moss`, `SH_Teal`, `SH_Plum`, `SH_Gold`, `SH_Leaf`).
- Mismas reglas de colision, coordenadas de mundo y presupuesto que la tanda 2 (edificio < 50k tris con los adornos).

---

# Tandas 4-6 (S154): arte de las etapas (Index/35 Parte 1.5)

Mismo pipeline, misma vara KayKit y misma paleta de madera de cuento de la tanda 3. Juan: "los props de la ultima sesion fueron muy buenos" -> ese es el nivel minimo. **Cero `SH_Coral`** en piezas nuevas (acentos: `SH_Sage`, `SH_Teal`, `SH_Plum`, `SH_Gold`, `SH_Moss`, `SH_Sky`, `SH_Lilac`, `SH_Straw`, `SH_Peach` con mesura).
Referencias aprobadas para copiar lenguaje: `ShopShowcase.py`, `ShopFeeder.py`, `ShopBed.py`, `ShopEggShelf.py`, `shop_incubator.py`, `ShopZoneCriadero.py` + `env_kit_e2.py` (arquitectura).
Salida de hojas de contacto: `<scratchpad>/props_t4/`. Cada agente escribe SOLO sus scripts y sus FBX.

## Tanda 4 · kit modular + piezas por nivel de zonas existentes
| # | Nombre | Que es | Huella / alto | Idea |
|---|--------|--------|---------------|------|
| K1 | `ZoneKitFloor` | Baldosa de piso de lote 3 x 3 m | 3.0 x 3.0, cara de arriba en z = 0, grosor 0.15 hacia abajo | tablones anchos `SH_Oak`/`SH_Honey` con junta hundida y clavitos; bordes que encajan sin costura con la vecina |
| K2 | `ZoneKitWall` | Pared lisa de 3 m | 3.0 (eje X) x 0.3 x 2.7, origen centro de la base, cara interior = -Y | entramado como `env_kit_e2` tanda 3: zocalo `SH_Walnut`, friso de tablas `SH_Honey`, franja de acento (parte aparte en `SH_Sage`, se recolorea por sala en Unity), revoque `SH_Parchment`, postes/vigas `SH_Timber`; exterior tablas `SH_Honey` + base de piedra |
| K3 | `ZoneKitWallWindow` | Pared con ventana | igual que K2 | ventana con marco gordo y arco tallado, vidrio `SH_Glass`, maceterito |
| K4 | `ZoneKitWallDoor` | Pared con puerta abierta | igual que K2, hueco 1.6 ancho x 2.2 alto centrado | marco tallado, sin hoja (paso libre) |
| K5 | `ZoneKitCorner` | Pilar de esquina | 0.4 x 0.4 x 2.85 | poste `SH_Timber` con capitel y base de piedra, extremos redondeados |
| K6 | `ZoneKitTrimIvy` | Remate superior con hiedra | 3.0 x 0.4 x ~0.2, se apoya en z = 2.7 | viga redondeada `SH_Walnut` + guirnalda `SH_Leaf`/`SH_Moss` |
| N1 | `ShopShowcaseL2` | Vitrina nivel 2 (5 lugares) | 4.0 x 3.0 | misma familia que `ShopShowcase` (alfombra NO coral: `SH_Sage`/`SH_Gold`) |
| N2 | `ShopShowcaseL3` | Vitrina nivel 3 (8 lugares) | 5.0 x 3.6 | idem, mas lujosa: escalon y cartel doble |
| N3 | `ShopCounterExt` | Tramo extra de mostrador (2.º y 3.er cliente) | 1.0 x 0.8 / ~1.0 | mostrador como el de `ShopRegister` sin maquina: campanita, frasco de propinas |
| N4 | `ShopFeederDouble` | Comedero doble (cuidado N2) | <= 1.4 x 0.8 / 0.5-0.7 | dos tolvas en una base comun |
| N5 | `ShopWaterDouble` | Bebedero doble (cuidado N2) | <= 1.4 x 0.8 / 0.6-0.8 | dos garrafones en una base comun |
| N6 | `ShopBedCanopy` | 2.ª cama, de lujo (cuidado N3) | 1.0 x 1.0 / ~1.4 | cama redonda con dosel de tela en arco y estrellitas |
| N7 | `ShopOrderBoard` | Pizarra de pedidos (oficina N2/N3) | 1.0 x 0.08 x 0.7 colgada, origen centro del tablero | 5 ganchos con fichas, campanita dorada de "pedido especial" |
| N8 | `ShopSandbox` | Arenero (patio N2) | 2.0 x 2.0 / 0.35 | marco de troncos, arena `SH_Straw`, palita y balde |
| N9 | `ShopHoseReel` | Manguera fija (patio N3) | 0.6 x 0.4 / 0.8 | poste con grifo y carrete con manguera gorda enroscada `SH_Moss` |
| N10 | `ShopPuddle` | Charco (patio N3) | 1.2 x 0.8 / 0.02 | forma organica plana `SH_Water` con borde claro |
| N11 | `ShopPlayMat` | Area grande de juego (sala N2) | 3.0 x 3.0 / 0.08 | alfombra acolchada redonda tejida + 2 cojines gordos |
| R1 | `ShopRegister`, `ShopSignMain`, `ShopLockedSign` | Recolor sin coral (decision S154) | sin cambios de forma | coral -> `SH_Gold`/`SH_Plum`/`SH_Sage` segun la pieza |

## Tanda 5 · equipamiento de la etapa 3
| Zona | Props (huella / alto aprox.) |
|------|------------------------------|
| Guarderia | `ShopCrib` cuna 1.0 x 0.7 / 0.8 con movil de estrellas · `ShopRockingChair` mecedora 0.7 x 0.9 / 1.0 · `ShopToyChest` baul de juguetes 0.7 x 0.45 / 0.5 · `ShopNightLamp` lampara-hongo 0.3 / 0.6 |
| Bano y peluqueria | `ShopBathtub` banera con patas 1.4 x 0.8 / 0.7 con burbujas · `ShopDryer` secador de casco de pie 0.6 / 1.4 · `ShopGroomTable` mesa de peluqueria con espejo 1.0 x 0.6 / 1.5 · `ShopTowelRack` toallero 0.8 x 0.3 / 1.0 |
| Cocina de snacks | `ShopStove` horno de lena 1.0 x 0.7 / 1.1 · `ShopKitchenCounter` mesada con tabla y bowls 1.6 x 0.7 / 0.95 · `ShopRecipeShelf` estante de frascos de recetas 1.2 x 0.35 / 1.6 |
| Almacen | `ShopStorageShelf` estanteria con cajas y sacos 2.0 x 0.6 / 2.0 · `ShopSackPile` pila de sacos 1.0 x 0.8 / 0.6 · `ShopBarrel` barril 0.6 / 0.8 · `ShopHandTruck` carretilla 0.6 x 0.6 / 1.2 |

## Tanda 6 · equipamiento de la etapa 4 (se corta si falta tiempo)
Escenario (tarima con telon, focos, banderines) · Gimnasio (pesas gordas, cinta, colchoneta, saco) · Clinica (camilla, botiquin, biombo, bascula) · Sala del linaje (arbol genealogico tallado, pedestales de retrato, vitrina de trofeos).

### Tanda 6 · detalle (S154)
| Zona | Props (huella / alto aprox.) |
|------|------------------------------|
| Escenario | `ShopStage` tarima con telon en arco 3.0 x 2.0 / tarima 0.4, arco 3.2 · `ShopSpotlight` foco de pie 0.5 / 1.6 · `ShopJudgeTable` mesa del jurado con campanita y cartelitos 1.6 x 0.6 / 0.8 · `ShopPrizePodium` podio 1-2-3 1.5 x 0.6 / 0.6 |
| Gimnasio | `ShopDumbbellRack` rack con pesas gordas 1.2 x 0.5 / 0.8 · `ShopRunWheel` rueda para correr 1.4 diametro x 0.8 · `ShopGymMat` colchoneta 2.0 x 1.2 / 0.12 · `ShopPunchBag` saco colgado de poste 0.8 x 0.8 / 1.8 |
| Clinica | `ShopExamTable` camilla 1.4 x 0.7 / 0.8 · `ShopMedCabinet` botiquin-armario con cruz (cruz `SH_Sage`/`SH_Teal`, nunca roja) 0.9 x 0.4 / 1.6 · `ShopFolderScreen` biombo 1.4 x 0.3 / 1.5 · `ShopScale` bascula 0.6 x 0.6 / 1.2 |
| Sala del linaje | `ShopFamilyTree` arbol genealogico tallado de pie con medallones 2.4 x 0.5 / 2.6 · `ShopPortraitPedestal` pedestal con retrato enmarcado 0.5 x 0.5 / 1.3 · `ShopTrophyCase` vitrina de trofeos 1.4 x 0.5 / 1.8 · `ShopLineageBook` atril con libro abierto 0.6 x 0.5 / 1.1 |
