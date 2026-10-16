---
tags: [shader, shop, materiales]
---

# CartoonGlass.shader

**Ruta:** `Shaders/CartoonGlass.shader`

**Responsabilidad:** Shader URP transparente del vidrio cartoon de las ventanas de la tienda. Pinta un degradado vertical entre dos colores, dos reflejos diagonales en bandas (uno ancho y uno fino, separados por un hueco), y un borde fresnel. La luz principal solo modula el tono base. Sin soporte de sombras ni de iluminación adicional.

**Vinculado a:** tienda (material `Materials/Shop/FV/M_CartoonGlass`)

**Conexiones:** ninguna en código. Lo usa el material `M_CartoonGlass` asignado a las ventanas de la tienda.

## Nombre del shader

`MoriMonchi/CartoonGlass`

## Propiedades

| Propiedad | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `_Color` | Color | (0.62, 0.82, 0.95, 0.38) | Color base en la parte baja del degradado (alfa = opacidad base) |
| `_TopColor` | Color | (0.85, 0.95, 1, 0.5) | Color de la parte alta del degradado |
| `_StreakColor` | Color | (1, 1, 1, 0.75) | Color y opacidad de los reflejos |
| `_StreakScale` | Float | 1.4 | Densidad de las bandas |
| `_StreakWidth` | Range 0–0.5 | 0.16 | Ancho de la banda ancha |
| `_StreakThin` | Range 0–0.2 | 0.05 | Ancho de la banda fina |
| `_StreakGap` | Range 0–1 | 0.28 | Separación entre la banda ancha y la fina |
| `_Slant` | Float | 1.0 | Inclinación de las bandas respecto a la altura |
| `_FresnelColor` | Color | (1, 1, 1, 0.35) | Color y opacidad del borde fresnel |
| `_FresnelPower` | Float | 3 | Exponente del fresnel (más alto = borde más fino) |
| `_GradientHeight` | Float | 1.2 | Altura en espacio objeto del ciclo del degradado |

## Render

- Tags: `Transparent` / `Transparent`, URP.
- `Blend SrcAlpha OneMinusSrcAlpha`, `ZWrite Off`, `Cull Back`.
- Un solo pase `ForwardLit`. No tiene `ShadowCaster`: el vidrio no proyecta sombra.

## Cálculo

- Las bandas se calculan en espacio objeto con un vector tangente derivado de la normal (`cross` con el eje Y). Se mueven con el objeto, no con la cámara.
- El degradado usa `frac(y / _GradientHeight)`: se repite cada `_GradientHeight` unidades.
- El antialias de las bandas usa `fwidth` del parámetro de bandas.
- La luz principal (`GetMainLight`) solo oscurece el tono base entre 0.85 y 1.0. No recibe sombras.

## Quirks ⚠️

- **Sin sombras:** no tiene `ShadowCaster` y no samplea sombras. Si se quiere sombra en el vidrio, hay que agregar el pase.
- **Sin cara trasera:** `Cull Back` y `ZWrite Off` hacen que solo se vea la cara frontal. Un plano sin volumen se ve de un lado.
- **Orden:** al ser transparente sin `ZWrite`, el orden entre varios vidrios depende de la cola de render.
- **Espacio objeto:** si el mesh tiene escala no uniforme, las bandas se deforman con la escala.
