# Alinear la tienda al estilo POLYGON Fantasy Village (S163)

Referencia: imagen de Juan + demo `Assets/Synty/PolygonFantasyVillage/Scenes/Demo.unity` (capturas en `ref/`). Comparación: `lamina_nosotros_vs_fv.png`. Piloto: `piloto/sala_antes_despues.png`.

## Regla
Nuestra geometría, colliders y NavMesh se quedan; la silueta y la piel de las estructuras salen del kit FV (techo, frontón, zócalo, aberturas, remates) y el exterior se llena con props FV.

## Qué define el estilo FV
- **Techos de paja** gruesos y curvos, con alero que cae y borde deshilachado; cumbrera con celosía de madera; tejas solo en torres.
- **Muros**: yeso crema entre entramado de madera; **zócalo alto de piedra** (cantos rodados); frontones de piedra o yeso.
- **Aberturas**: ventanas redondas o en arco con vidrio azul y parteluces orgánicos; buhardillas; postigos.
- **Remates**: espirales talladas, veletas, chimeneas de piedra, faroles en torre con techo rojo.
- **Vegetación sobre la arquitectura**: hiedra y glicina en techos y muros, maceteros en ventanas.
- **Suelo**: empedrado y losas; nada de asfalto.
- **Relleno**: banderines cruzando la calle, puestos de mercado, carteles, barriles, cajones, bancos, macetas, tablón de misiones.
- **Color**: madera miel/naranja, crema, acentos teal y rojo frambuesa.

## Veredicto por elemento

| Elemento | Hoy | Veredicto | Cómo |
|---|---|---|---|
| Planta, colliders, NavMesh | ok | **Rescatar** | No se toca |
| Entramado de madera de las fachadas | ok | **Rescatar** | Ya es el lenguaje FV |
| Fachada (toldos, cartel, faroles, bancas, macetas) | ok | **Rescatar** | Sumar maceteros FV en ventanas |
| Props interiores (KayKit) | ok | **Rescatar** | Juan los aprobó; no son estructura |
| Techos de teja recta (todas las alas) | rígidos, mismo naranja | **Reemplazar** | Techo de paja FV (`Roof_Thatch_Preset_*`) encima, techo nuestro apagado (los techos no tienen collider). Piloto hecho en la Sala de Juegos con `Preset_04` |
| Tablones lisos en todo el muro | monótono | **Modificar** | Paneles altos del entramado en yeso crema (cambio de material en el FBX o `Wall_*` FV encima) |
| Zócalo de piedra fino | casi no se ve | **Modificar** | Zócalo FV más alto (`Base_*`, `Stone_Edge`) a lo largo de los muros |
| Ventanas cuadradas | genéricas | **Modificar** | Postigos FV (`Window_Shutter_*`) y una ventana redonda por frontón (`Window_Large_*`) |
| Remates | no hay | **Agregar** | 1 chimenea por bloque grande, veleta en la cumbrera principal, ornamentos en espiral |
| Hiedra en techos/muros | pocas hojas sueltas | **Agregar** | `SM_Env_Vine_*` (ya importados) en aleros y esquinas |
| Calle de asfalto con cebra y vereda rosa | moderna, choca | **Reemplazar** | Empedrado y losas FV; faroles en torre |
| Exterior vacío | — | **Agregar** | Banderines, puesto de mercado, tablón de misiones, barriles, cajones, macetas |

## Cómo (orden)
1. **Techos** ala por ala con presets de paja ajustados al footprint; el techo principal (15 m de luz) se arma con dos presets o con piezas sueltas. Material: shader Synty original (como el bosque FV); si choca con nuestro toon, `SyntyToonConverter`.
2. **Muros**: yeso en paneles + zócalo alto.
3. **Aberturas y remates**.
4. **Calle**: empedrado (decisión de Juan: la calle moderna es la única pieza que contradice el estilo).
5. **Relleno exterior** por zona.

## Hecho (S163)
- **Techos**: `SM_Bld_Roof_Thatch_Preset_04` en 11 alas (`FV_Techo_*` / `FV_Restyle_SalaJuegos`); techos viejos apagados (sin collider). El techo viejo encendido asoma entre la paja: dejarlo apagado.
- **Muros**: copias de malla `*_FV` en `Resources/Models/Shop/FVRestyle/` (ShopBuilding, ShopZoneCriadero, ShopZoneSalaJuegos, ZoneKitWall, ZoneKitWallWindow): caras verticales de miel/roble → `SH_Parchment_Env`. Los FBX originales no se tocaron.
- **Zócalo**: `FV_Zocalo` por edificio con `SM_Bld_Base_Wall_Half_01` + material `Stone_Half_Wall_01` (cantos rodados, ~0,95 m sobre el suelo real); sin piezas en la rampa de entrada.
- **Remates**: `FV_Remates` (verde en techos, hiedra colgante, 3 chimeneas) y `FV_RematesMuro` (hiedra trepadora, 46 postigos en 23 ventanas).
- **Calle**: `ShopStreet_FV` con UV planos en metros: calzada `FV_Calle_Empedrado`, vereda `FV_Vereda_Losas` (`Materials/Shop/FV/`); sin líneas, cebra ni alcantarillas.
- **Relleno**: `ENVIROMENT/FV_Relleno` (3 banderines con postes, 2 campanarios, tablón de misiones, carreta de mercado, barriles, cajones, paja, pozo, carretilla, macetas).
- **Pasto**: receta del patio en toda la escena + área `FrenteTienda` (exclusión de la rampa) y franja sur hasta el cordón.

## Quirks encontrados
- **El MCP reintenta `execute_code` largos**: el zócalo quedó triplicado una vez. Todo script que crea objetos debe borrar primero lo que ya creó (idempotente).
- El triplanar de Synty (`Synty/PolygonShader`) promedia la textura del camino y la deja lisa: usar UV planos + `Generic_Basic`.
- Postigos: la normal del vidrio puede salir de una cara lateral; usar el eje fino del cristal y apoyar con rayo sobre la cara exterior del muro.
- **Otra PC**: necesita POLYGON_FantasyVillage completo (sin personajes) en `Assets/Synty`, o pierde techos, zócalo, remates, calle y relleno.
- `SM_Bld_Roof_Thatch_Preset_Wide_01` trae una sola caída, no sirve como techo entero.
- Los módulos sueltos `Roof_Thatch_01` se ven bien solo de a pares y con la escala original; escalarlos fuerte deja huecos.
- Medidas de la grilla FV: módulos de 2,5 m.
