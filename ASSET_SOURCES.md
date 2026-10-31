# Fuentes de los recursos

Nada de este perfil usa imágenes generadas por IA. Las licencias se verificaron en la página de cada archivo el 31 de octubre de 2026, mediante `scripts/assets.mjs` de Taste Skill.

## Fotografías usadas

### Plato de radiotelescopio, 1960

- **Título:** A radio telescope
- **Autor:** Gar Lunney
- **URL:** https://commons.wikimedia.org/wiki/File:A_radio_telescope_Un_radiot%C3%A9lescope_(46720461475).jpg
- **Licencia:** dominio público
- **Atribución:** no obligatoria; se incluye al pie del README
- **Modificaciones:** recorte, escala de grises, oscurecido a anochecer, extensión del cielo por espejo, duotono, velo oscuro bajo el título
- **Rutas:** `assets/plates/dish-*.jpg`

### Antena Duga

- **Título:** DUGA Radar Array near Chernobyl, Ukraine 2014
- **Autor:** Ingmar Runge
- **URL:** https://commons.wikimedia.org/wiki/File:DUGA_Radar_Array_near_Chernobyl,_Ukraine_2014.jpg
- **Licencia:** CC BY 3.0, https://creativecommons.org/licenses/by/3.0
- **Atribución:** obligatoria; aparece al pie del README
- **Modificaciones:** recorte, negativo, niveles, duotono, máscara inferior
- **Rutas:** `assets/plates/array-*.jpg`

## Tipografías

| Fuente | Licencia | Uso |
|---|---|---|
| Bodoni Moda | SIL OFL 1.1 | Convertida a trazados en `data/glyphs.json` |
| Jost | SIL OFL 1.1 | Convertida a trazados en `data/glyphs.json` |

Las licencias están en `assets/fonts-license/`. Fuente: https://github.com/google/fonts. Se usan como trazados vectoriales porque un SVG dentro de `<img>` no puede cargar fuentes externas.

## Iconos y datos

| Recurso | Licencia | Ruta |
|---|---|---|
| Iconos de lenguajes, Simple Icons 16.36.0 | CC0 1.0 | `data/icons.json` |
| Colores de lenguajes, GitHub Linguist | MIT | `data/lang_colors.json` |

Los logotipos siguen siendo marcas de sus dueños y aquí solo identifican el lenguaje. Los lenguajes sin icono usan sus iniciales.

## Investigados y descartados

| Recurso | Licencia | Por qué no |
|---|---|---|
| One-Time Pads, CIA | Dominio público | Probado en portada; a tamaño pequeño era una mancha gris |
| Field Station Berlin, Teufelsberg | CC BY-SA | Compartir igual obligaría a licenciar los derivados igual, sin ganancia visual |
| QSL XU6GRL, 1947 | Dominio público | Ornamento ajeno. La forma de la tarjeta sí inspiró la tarjeta propia |
| Captura de CFetch | Tuya | Reducida parecía el banner de terminal que ya rechazaste. Ahora se muestran sus tiempos a escala |
| John Reinartz, 1925 | Dominio público | Es una persona real; no debe parecer el protagonista |
| Vídeos de NASA | Dominio público | GitHub no reproduce vídeo en README con autoplay, y un GIF pesado no aportaba más que las cifras animadas |

## Para reconstruir las placas

Descarga los originales en una carpeta con estos nombres y ejecuta `scripts/build_plates.sh <carpeta>`:

- `a-radio-telescope.jpg`
- `duga-radar-array-near-chernobyl-ukraine-2014.jpg`
