---
name: rx3card
description: Perfil de GitHub como tarjeta de recepción y transmisión de números, en papel negro con una sola luz.
colors:
  ground: "#050507"
  field: "#0B0B10"
  ink: "#ECECF2"
  ink-2-dark: "#A8A8B6"
  ink-2-halloween: "#B0A69C"
  accent-dark: "#C9C9D6"
  accent-halloween: "#FF6A00"
  card-dark: "#ECECF2"
  card-halloween: "#FF6A00"
  card-ink: "#050507"
  dim-dark: "#3A3A44"
  dim-halloween: "#46321F"
  zero-dark: "#6A6A76"
  zero-halloween: "#7A6450"
typography:
  display:
    fontFamily: "Bodoni Moda (ajuste display, trazados)"
    fontSize: "124"
    fontWeight: 400
  headline:
    fontFamily: "Bodoni Moda (ajuste medio, trazados)"
    fontSize: "50"
    fontWeight: 400
  figure:
    fontFamily: "Bodoni Moda (ajuste texto, trazados)"
    fontSize: "29"
    fontWeight: 400
  body:
    fontFamily: "Jost 400 (trazados)"
    fontSize: "25"
    fontWeight: 400
  strong:
    fontFamily: "Jost 500 (trazados)"
    fontSize: "26"
    fontWeight: 500
spacing:
  margin: "56"
  margin-narrow: "36"
  axis: "538"
components:
  reception-card:
    backgroundColor: "{colors.card-halloween}"
    textColor: "{colors.card-ink}"
    width: "420"
    height: "244"
---

# Design System: rx3card

Los tamaños sin unidad son unidades del viewBox del SVG (1280 de ancho en escritorio, 720 en estrecho), no píxeles CSS.

## Overview

**Estrella del norte: "El receptor que alguien dejó encendido"**

## Concepto

Todo es una hoja impresa de radioafición: tarjeta QSL, bloc de cifrado, bitácora de estación. Papel negro, una sola luz (ámbar en Halloween, gris pálido en el estado permanente), hueso como tinta. Un año de contribuciones reales llega como cifras, una por día. No hay tarjetas repetidas ni mono de terminal: las cifras son Bodoni.

Todo el texto está convertido a trazados en `data/glyphs.json`, así que el arte no depende de las fuentes del visitante. Cada imagen es un SVG generado por `scripts/render.py` desde datos reales; nada se dibuja a mano ni se inventa.

## Colors

Una luz, tinta de hueso, dos negros. El acento marca lo que importa: el conteo alto (9 o más), la lámpara, el pico del arreglo, la barra de barrido.

### Primary
- **Ámbar de transmisión** (accent-halloween): luz única de la temporada HALLOWEEN (1 oct a 2 nov); también el papel de la tarjeta.
- **Plata de espera** (accent-dark): equivalente del estado DARK permanente; la tarjeta pasa a papel hueso.

### Neutral
- **Papel negro** (ground) y **campo** (field): fondo de aperturas y barras; campo para las secciones de lectura (transmisión, mensaje, ranking global).
- **Hueso** (ink): texto principal y cifras de 4 a 8.
- **Tinta secundaria** (ink-2-*): notas, cifras de 1 a 3, etiquetas; cálida en Halloween.
- **Tenue** (dim-*): líneas de suelo, mástiles sin protagonismo, barras no destacadas.
- **Cero** (zero-*): días sin actividad.

### Named Rules
**La Regla de la Única Luz.** El acento aparece solo donde hay un dato fuerte o un punto vivo. Nada brilla por decoración.

**La Regla de la Temporada.** Los colores salen de `profile.config.json`; la temporada cambia tokens, no composición. Las estadísticas no dependen de la temporada. Los colores de lenguaje (Linguist) se aclaran hasta 4.5:1 sobre el fondo (3:1 en la barra apilada).

## Typography

**Display:** Bodoni Moda, tres ajustes ópticos como trazados: display (`bd`, opsz 96, peso 500, wordmark final), medio (`bm`, opsz 26, peso 600, títulos y tarjeta) y texto (`bt`, opsz 18, peso 500, cifras y porcentajes). **Cuerpo:** Jost 400 (`j4`) y 500 (`j5`, valores y nombres).

**Carácter:** Didone de alto contraste para lo que se lee como dato; geométrica sobria para lo que explica. Sin mono.

### Hierarchy
Escala de render real: columna de unos 830 px en escritorio (factor 0.65 sobre 1280) y unos 340 px en teléfono (factor 0.47 sobre 720).
- **Wordmark** (`bd`, ancho de página): "rx3card" de cierre, ocupa todo el ancho útil.
- **Título de apertura** (`bm`, 124 escritorio, 118 estrecho): unos 80 px y 56 px reales.
- **Título de sección** (`bm`, 50 escritorio, 62 estrecho): unos 32 px y 29 px reales.
- **Título de proyecto** (`bm`, 44 / 54): unos 29 px y 25 px reales.
- **Cifra** (`bt`, 29 transmisión, 26 a 30 rankings): unos 19 px reales en escritorio; 27 en estrecho, unos 13 px.
- **Cuerpo y nota** (Jost 400, 25 a 30 escritorio, 26 a 34 estrecho): unos 16 a 19 px y 12 a 16 px reales.
- **Valor** (Jost 500, 26 a 30): nombres de lenguaje y datos de la tarjeta.

### Named Rules
**La Regla de las Cifras.** Todo número es Bodoni de ajuste texto; todo texto corrido es Jost. No se mezclan.

**La Regla de la Letra Mínima.** El texto más pequeño usa 23 unidades (unos 15 px reales en escritorio). En teléfono nada baja de 25 unidades (unos 12 px).

## Layout

Un eje fijo en x=538 de 1280 que ancla los títulos de sección y las líneas de proyecto; las notas pequeñas se alinean a la izquierda en el margen de 56. Márgenes laterales de 56 en escritorio y 36 en estrecho. Cada sección es un SVG de ancho completo, apilado, sin tarjetas.

Dos artes por pieza, `nombre.svg` (1280) y `nombre-phone.svg` (720), seleccionados con `<picture>` en el punto de quiebre de 1100 px (la barra lateral de GitHub encoge la columna). El arte estrecho no es una versión reducida: reordena. Los títulos se parten en dos líneas, el calendario pasa de 53 columnas a grupos de 4 semanas por fila, los rankings a una columna, y la tarjeta de recepción baja bajo el título.

Recorrido: tarjeta, transmisión, arreglo, bandas, proyectos, despedida. El mensaje y los rankings secundarios van dentro de `<details>`.

## Elevation & Depth

Plano. La profundidad viene de dos placas de archivo en duotono (antena, arreglo de mástiles) y de la perspectiva de los mástiles (altura = raíz cuadrada del conteo). No hay sombras de caja.

### Named Rules
**La Regla del Velo.** Bajo el título de la apertura hay un único degradado neutro de scrim, solo para asegurar contraste AA sobre la foto. Ningún otro degradado.

## Shapes

Esquinas rectas, sin radios. Rectángulos para barras, tarjeta y mosaicos de lenguaje. Las únicas líneas finas son las que pertenecen al objeto: el marco interior de la tarjeta QSL (trazo 1.6 a escala 400) y las líneas de suelo de los mástiles. Flecha de enlace de dos trazos al final de cada línea de proyecto, en acento.

## Components

### Tarjeta de recepción
Papel del color de `card`, tinta `card-ink`, marco fino, "Confirming reception", "RX3CARD" en `bm` 66, y tres filas Fecha / Oído / Más fuerte con datos reales. 420 x 244 en escritorio (abajo a la izquierda, x=56, y=432); 648 x 376 en estrecho.

### Transmisión del calendario
Una cifra por día (0 a 9, 9 significa 9 o más), una columna por semana, 36 unidades de fila. Color por conteo: cero, tinta secundaria, tinta, acento (9 o más). Barrido ámbar sobre la columna activa.

### Mástiles
Siete filas en perspectiva, tres bandas de color por conteo (1 a 3, 4 a 14, 15 o más). El día pico lleva un punto de acento.

### Bandas de lenguaje
Barra apilada, filas de rango (cifra, icono o iniciales, nombre, porcentaje, barra). Dos columnas en escritorio, una en estrecho. Los números de rango se mantienen porque son datos reales.

### Marcas de proyecto
Cada proyecto se muestra con su propio material: minimapa del archivo fuente, carrera de milisegundos a escala, manifiesto de archivos, token cifrado. No hay tarjeta común.

### Mensaje cifrado
Cifras de cinco dígitos sobre su pad y el tablero de damas (checkerboard) impreso debajo; descifrable a mano.

### Animaciones
- **Barrido de transmisión:** ciclo de 18 s; cada semana (`.w`) se enciende de opacidad .14 a 1 con un retardo de 0.12 s entre semanas, y una barra de acento recorre las columnas en pasos.
- **Lámpara:** parpadeo de 5 s (opacidad .18 a 1 entre 62 % y 78 % del ciclo) en la antena de la apertura y, con .25, en el pico del arreglo.
- **Crepúsculo:** capa del color de fondo sobre la placa, opacidad 0 a .5 y vuelta en 48 s.
- **Movimiento reducido:** cada SVG animado incluye su propia regla `prefers-reduced-motion` que apaga toda animación, y una prueba lo exige. Sin animar, todo queda visible a opacidad 1. Los tres ciclos son lentos y no hay destellos de más de uno por 5 s.

## Identidad

El nombre es `rx3card`, en minúsculas, nunca el nombre real. La frase firma es "is still receiving"; el cierre es "73", saludo de radioaficionado. El diseño habla; no explica quién es el dueño. Sin cargos, sin "bienvenido", sin llamadas a seguir o dar estrellas. Créditos de placas en `ASSET_SOURCES.md`.

## Criterios de calidad

- Todo número es verdadero y viene de `data/stats.json`; si una actualización falla, queda el último resultado válido.
- Contraste AA dentro de las imágenes; `alt` significativo en cada imagen, con los datos completos.
- Legible en el tema claro y oscuro de GitHub: cada SVG pinta su propio fondo.
- Nada privado sale: solo porcentajes agregados.
- Prueba de una frase: si un elemento puede quitarse sin que el conjunto pierda, se quita.

## Do's and Don'ts

### Do:
- **Do** generar todo desde `render.py` y `profile.config.json`; añadir una temporada es añadir un bloque de tokens.
- **Do** mantener un solo acento por temporada y el eje en x=538.
- **Do** dar a cada pieza su arte estrecho propio.

### Don't:
- **Don't** repetir tarjetas idénticas ni muros de insignias.
- **Don't** usar calabazas, fantasmas sonrientes, brillo general ni imágenes de apariencia IA.
- **Don't** mezclar contribuciones con los rankings de bytes.
- **Don't** usar texto vivo: siempre trazados.

## Dirección alternativa, no construida: "El tablero"

Repositorios y calendario como un tablero de salidas de paletas giratorias (split-flap): paletas negras con una sola fila ámbar retrasada. Fue el retador más fuerte que repartió la semilla de concepto de Impeccable. No se eligió porque el giro por carácter exige muchos fotogramas, pesa más y repite una cuadrícula que ya usan las cifras.

## Excepciones a Taste Skill, justificadas

- Paleta repartida "Candy chapters" rechazada: la paleta del dueño está fijada.
- El violeta del dueño #6E27A8 queda sin usar: Taste prohíbe el violeta y el mundo funciona con un solo color encendido.
- El plano del héroe coloca la tarjeta de recepción abajo a la izquierda, en lugar de dos tarjetas abajo a la derecha.
- Un degradado neutro de scrim bajo el título es el único degradado permitido.
- Los números de ranking se mantienen: son datos reales, no numeración de secciones.
- El marco de la tarjeta QSL y las líneas de suelo de los mástiles son filetes finos que se mantienen porque pertenecen al objeto representado.
- Los FAIL del Inspector por falta de h1, imágenes y movimiento son límites de un medidor que no ve dentro de `img`.
