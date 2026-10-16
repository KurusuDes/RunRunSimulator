---
tags: [index, arte, vegetacion, pasto]
---

# 36 - Pasto y vegetación (referencias)

> Referentes de paleta y forma de vegetación (Juan, S162): **Genshin Impact** e **Immortals Fenyx Rising**.

## Qué hacen bien los referentes

| Rasgo | Genshin Impact | Immortals Fenyx Rising | Nosotros (S162) |
|---|---|---|---|
| Forma de brizna | Ancha, larga, pocas por m²; se lee como forma limpia | Matas gordas, pinceladas grandes | Agujas finas (2-4 cm × 14-34 cm), muchas por m²: se lee como "pelo" o alfombra |
| Altura vs. personaje | Hasta la rodilla | Rodilla en praderas | Tobillo: parece césped cortado |
| Luz | Normales de terreno: el campo se ilumina como una sola superficie | Ídem, con sombras grandes de nubes y relieve | Normales al 85 % de terreno, pero cada brizna recibe sombra propia + banda toon + brillo de punta → moteado de alta frecuencia |
| Color | Verde esmeralda frío, poca variación entre briznas; la variación va en manchas grandes | Amarillo-verde cálido al sol, verde azulado a la sombra; parches grandes | Verde lima saturado uniforme; la variación está en cada brizna (ruido) y no en el campo |
| Suelo | Nunca se ve | Casi nunca | Se ve el plano verde en claros y bordes |
| Lejanía | Perspectiva aérea fuerte: el verde se aclara y se azula hacia el horizonte | Bruma cálida y bloom | Sin niebla en la tienda: el verde lejano es igual al cercano |
| Acentos | Flores blancas grandes y sueltas, matas más altas | Arbustos con flores fucsia, piedras | Flores diminutas (5-8 cm de cabeza) que se pierden |

## Por qué el suyo se ve mejor (regla)

**Detalle grande y luz simple.** El ojo lee primero formas y manchas de valor grandes; el detalle fino solo se ve de cerca. Ellos ponen la variación en manchas de metros (nubes, parches de color, relieve) y simplifican cada brizna; nosotros hacemos lo contrario: cada brizna aporta ruido (sombra propia, punta brillante, tono aleatorio) y el campo entero queda plano.

## Técnicas públicas que respaldan esto

- **Ghost of Tsushima (GDC 2021, Eric Wohllaib):** briznas generadas en GPU, agrupadas en matas por ruido celular (comparten giro, altura y curva), normales curvadas en el fragment para que la brizna se vea redonda, ensanchamiento en espacio de vista cuando la brizna está de canto, color de base a punta y AO falso por altura.
- **Comunidad (Godot, Unity, recreaciones de BotW/Genshin):** iluminar con la normal del terreno, color de la raíz = color del suelo (el pasto "sale" del piso), manchas de color por ruido de escala grande, sin sombras propias en la brizna, flores y matas como acentos de escala distinta.

## Pendientes

- **Fundido por distancia (Juan, S163)**: como en Genshin, el pasto tiene una distancia de dibujado: de lejos las briznas se desvanecen (encogen o bajan densidad) y aparecen al acercarse, así se ve bien de lejos y de cerca. Idea: en `ArenaGrass.shader` escalar la altura de la brizna a 0 entre dos distancias a cámara (`_FadeStart` / `_FadeEnd`, por ejemplo 35 y 60 m) con dither por brizna para que no se vea una línea; de lejos el suelo verde con la misma rampa de color sostiene la lectura. Además baja el costo (S163: 5 M vértices tras replicar el pasto del patio en toda la escena).

## Fuentes
- [GDC Vault: Procedural Grass in Ghost of Tsushima](https://gdcvault.com/play/1027214/Advanced-Graphics-Summit-Procedural-Grass)
- [2Retr0/GodotGrass (implementación basada en la charla)](https://github.com/2Retr0/GodotGrass)
- [Godot Shaders: Stylized Cartoon Grass](https://godotshaders.com/shader/stylized-cartoon-grass/)
- [Unity Discussions: Genshin Impact grass rendering](https://discussions.unity.com/threads/genshin-impact-grass-rendering-how.984026/)
- [Unity Discussions: grass normals](https://discussions.unity.com/t/grass-normals-shader-graph/1723731/5)
- [Cinevva: grass and occlusion (BotW)](https://app.cinevva.com/blog/2026-05-14-open-world-browser-part-28-grass-and-occlusion)
- [PixelAnt: millions of grass blades](https://pixelantgames.com/blog/rendering-millions-of-grass-blades-using-ue-and-niagara/)
- [Technicolor Games: Immortals Fenyx Rising (Miyazaki/Kazuo Oga)](https://games.technicolor.com/blog/technicolor-games-team-rises-challenge-immortals-fenyx-rising)
- [Hands on Immortals Fenyx Rising (pasto cel-shaded)](https://nintendoeverything.com/hands-on-with-immortals-fenyx-rising-formerly-known-as-gods-monsters/)

Nota: no hay charla oficial de Genshin sobre su pasto; lo de Genshin sale de observación y recreaciones de la comunidad.
