# Recursos para generar con ChatGPT

El perfil ya está completo sin imágenes generadas. Las fotografías reales y los datos son su fuerza, y rechazaste antes lo que parecía IA. Por eso solo propongo dos recursos, y solo el primero importa de verdad.

Descarté banner, escena ambiental, recurso de estadísticas, transición y cierre: la portada usa una foto real, las estadísticas deben salir de datos y el cierre ya funciona solo con tipografía.

Para que ninguna imagen falsee datos, no pidas nunca cifras, gráficos ni texto.

## Prioridad 1. Avatar

- **Nombre:** avatar-receiver
- **Propósito:** identidad reconocible en perfil, comentarios y commits
- **Posición:** foto de perfil de GitHub, no va en el README
- **Relación de aspecto:** 1:1
- **Resolución:** 1024 × 1024
- **Ruta:** `assets/avatar/avatar-receiver.png`
- **Composición:** plato parabólico en silueta, mirando hacia arriba y a la derecha, con el centro óptico en el centro exacto de la imagen. Ocupa el 58 % del ancho.
- **Dirección visual:** silueta casi negra sobre negro, separada solo por un filo tenue de luz. El único color es un punto ámbar en el foco.
- **Zona segura:** todo el motivo dentro del círculo central del 76 %. Las esquinas son negro puro.
- **Tratamiento posterior:** exportar también a 400 × 400; comprobar a 40 y 32 px en círculo.

Prompt:

```text
A square image, 1024 by 1024 pixels, for a circular profile picture.
Subject: the silhouette of one parabolic radio telescope dish on a short pedestal, seen from slightly below, tilted up and to the right. The dish is a clean, solid shape, with its feed arm and a single point at the focus.
Composition: the dish is centred. It fills 58 percent of the image width. Everything important stays inside a central circle covering 76 percent of the width. The four corners are pure empty black.
Lighting: night. The dish is nearly black against a black ground, separated only by a very thin rim of cold grey light along its upper edge. No other light source. No stars, no clouds, no landscape, no horizon.
Colour: pure black #050507 ground, charcoal #0B0B10 for the dish, and exactly one small, sharp amber point #FF6A00 at the focus. The point is soft at its very edge but has no large glow, no rays and no lens flare.
Material: the matte, grainy look of a real night photograph printed on black paper. Slight fine film grain. Not a 3D render, not a vector logo, not glossy.
Avoid: text, letters, numbers, logos, faces, people, eclipses, planets, rings, nebulae, galaxies, pumpkins, bats, neon outlines, gradients in the sky, orange glow around the dish, symmetrical icon styling.
The image must still read as a dish at 32 pixels wide.
```

**Criterios de aceptación:**
- A 32 px se reconoce como un plato o, al menos, como una forma con un punto de luz.
- No hay texto ni halo naranja.
- El motivo sobrevive al recorte circular.
- No parece un icono de stock ni un render 3D.

**Elementos prohibidos:** texto, eclipse, anillos, brillo extendido, cualquier elemento de Halloween.

## Prioridad 2. Portada para redes, opcional

- **Nombre:** social-preview
- **Propósito:** imagen que se ve al compartir el enlace del repositorio
- **Posición:** Settings del repositorio, "Social preview", no va en el README
- **Relación de aspecto:** 2:1
- **Resolución:** 1280 × 640
- **Ruta:** `assets/avatar/social-preview.png`
- **Composición:** horizonte bajo, en el 22 % inferior. Una sola luz ámbar diminuta a la altura de la cuarta parte derecha. El resto, cielo vacío.
- **Dirección visual:** la misma noche del avatar, sin plato protagonista. Solo una antena lejana muy pequeña, casi perdida en el horizonte.
- **Zona segura:** deja libre la mitad izquierda; puedes añadir `rx3card` después con la portada real como referencia.
- **Tratamiento posterior:** añadir el nombre con tipografía real, nunca dentro de la generación.

Prompt:

```text
A wide image, 1280 by 640 pixels, a real-looking night photograph.
Composition: a very low, dark horizon of forest in the bottom 22 percent of the frame. Above it, an enormous empty sky. On the horizon at about three quarters of the width stands a single distant radio mast, very small, about 6 percent of the image height. At its top, one tiny amber light #FF6A00.
Lighting: the last light after dusk, nearly gone. The sky is a very dark, uneven charcoal #0B0B10 with faint cloud texture and no stars. The forest is pure black #050507.
Depth: the mast is far away and slightly softened by air. Nothing is close to the camera.
Material: fine film grain, slight unevenness of a real long exposure. Not a digital painting, not a 3D render.
Negative space: the left half of the sky stays completely empty for later typography.
Avoid: text, letters, numbers, moons, eclipses, stars, planets, aurora, fog machines, people, bats, pumpkins, orange sky, purple sky, glowing edges, lens flare, dramatic rays.
```

**Criterios de aceptación:**
- Parece una fotografía, no una ilustración.
- El punto ámbar es la única nota de color.
- Sin texto ni objetos de Halloween.

**Elementos prohibidos:** texto, cielo naranja o violeta, luna, eclipse.

## Cómo integrarlos

1. Genera la imagen y guárdala en la ruta indicada.
2. Revísala a su tamaño real antes de aceptarla.
3. Súbela en GitHub. El README no necesita cambios.
4. Anota la fecha y la herramienta en `ASSET_SOURCES.md`, para que quede claro que no es material de archivo.
