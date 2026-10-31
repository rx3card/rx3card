# Validación

Estado al 31 de octubre de 2026. Solo figura aquí lo que se ejecutó de verdad. Nada se ha publicado: no hubo push ni cambios en la cuenta.

## Resultado

| Comprobación | Resultado |
|---|---|
| Pruebas automáticas | 30 de 30 pasan |
| Pruebas sobre archivos reales a publicar | Pasan, incluidas en las 30 |
| Pasos del workflow simulados en local con datos reales | Pasan; sin cambios, no habría commit |
| Pruebas de mutación | 4 de 4 fallos introducidos se detectan |
| API de Markdown de GitHub | Conserva 13 `<picture>`, sus `media`, 13 `alt` y 4 `<details>`; sin scripts ni estilos |
| `impeccable detect` sobre la vista previa | Sin hallazgos; no analiza por dentro los SVG |
| `lint.mjs` de Taste | 0 FAIL, 0 WARN |
| `inspect.mjs` de Taste | 5 FAIL, 4 WARN; ver abajo |
| Enlaces públicos | 4 repositorios, verificados en la consulta a GitHub |
| Peso | 1,2 MB en 26 SVG; el mayor pesa 110 KB |

## Privacidad

- Un repositorio privado sintético, con URL e identificador, no aparece en `stats.json`, en la salida ni en los errores.
- Mutaciones detectadas: volcar nombres de repositorios al JSON, poner la ruta en un error, incluir forks, y mezclar privados en PUBLIC.
- Una revisión independiente de `collect.py` no encontró ninguna vía para que un nombre, identificador o URL privados salieran.
- `PROFILE_STATS_TOKEN` solo existe en el paso Collect.
- El calendario publicado coincide con el anónimo: 1.296 contribuciones y 371 días, comprobado contra la página pública sin sesión.

Corrección hecha durante el trabajo: el calendario se pedía con el token de acceso privado. Hoy no filtraba nada, porque tu perfil ya muestra esas cifras, pero lo habría hecho si desactivaras esa opción. Ahora usa siempre `GITHUB_TOKEN`.

## Por qué siguen 5 FAIL en el inspector de Taste

Son límites del medidor en este formato, no defectos ocultos. El inspector mide el HTML, y aquí todo vive dentro de `<img>`:

| Regla | Motivo |
|---|---|
| `no-title`, `late-title` | El título está en el SVG. GitHub no da otra forma de ponerlo con esta tipografía |
| `few-pictures` | No ve las fotos incrustadas en los SVG |
| `still-page` | No ve las animaciones internas del SVG |
| `body-size` | Mide el texto de GitHub y la línea de créditos |

Las advertencias de botón, vídeo, medida y titular tienen el mismo origen. El README no tiene un botón de acción a propósito, y GitHub no reproduce vídeo con autoplay. El criterio de "0 FAIL" de Taste no se cumple y no se fingió: la verificación real se hizo con capturas.

## Inspección visual

Capturas reales en Brave 156, cada SVG dentro de un `<img>`:

- Todas las piezas a 830 y 350 px de ancho.
- Página completa a 1280 y 390 px sobre la versión final. El fondo claro se revisó antes de las últimas correcciones.
- La animación del calendario a 2,3 s y 5,2 s.
- Movimiento reducido: el contenido sigue visible.
- Temporadas Halloween, DARK y una temporada futura sintética, sin tocar la lógica.

## Crítica de Impeccable

Hubo dos evaluaciones aisladas, tal como pide `/impeccable critique`.

| Dimensión | Puntuación |
|---|---|
| Diseño, heurísticas | 22 de 36 antes de las correcciones |
| Especificidad | Fuerte: no se puede reutilizar para otro perfil |
| Accesibilidad | 3 de 4 |
| Rendimiento | 3 de 4 |
| Temas | 3 de 4 |
| Responsive | 2 de 4 antes del cambio de corte |
| Antipatrones | 4 de 4 |

No repetí la puntuación tras los cambios, así que estas cifras describen la versión anterior.

### Los cinco elementos más débiles

1. **Mensaje cifrado.** Era Markdown gris, y en móvil no se podía leer completo. Corregido: ahora es una pieza impresa, con versión móvil.
2. **Portada en móvil.** Perdía la punta del plato y a la persona. Corregido: se ve el plato entero.
3. **Tira de proyectos.** Paneles parecidos y la captura de CFetch recordaba al banner rechazado. Corregido en parte: cada uno tiene su propio material, con los tiempos de CFetch a escala y una flecha de enlace.
4. **Paneles de lenguajes.** Se repiten y los colores de Linguist rompen la paleta. Mantenido a propósito: pediste todos los lenguajes con color identificable. Quedan plegados, salvo el global. La barra de Contribuciones, que exageraba 6 líneas, se quitó.
5. **Ancho intermedio.** Entre 641 y 900 px el arte de escritorio dejaba texto de unos 10 px. Corregido: el arte estrecho se usa hasta 1100 px, porque la barra lateral de GitHub reduce la columna.

### Otras correcciones

- Los días en cero subieron de contraste a 3:1 o más.
- La lámpara de la portada estaba en el cielo; ahora está en el foco de la antena.
- El pad de portada se eliminó: reducido era una mancha gris.
- Una ejecución parcial ya no publica si existe una completa.
- Texto alternativo más completo en todas las imágenes.

### Rechazado de la crítica

- Limitar los lenguajes a 8 filas: contradice lo que pediste.
- Barra marrón en mayo: es el barrido de la animación, capturado a mitad.
- Nota de vista previa: solo existe en `previews/`, no en el README.
- Quitar el nombre de la tarjeta: la tarjeta QSL existe para llevar ese indicativo.

### Lo que sigue débil

- Sigue siendo una serie larga de paneles oscuros: GitHub no permite más composición que apilar imágenes.
- En móvil el calendario no tiene marcas de mes.
- Las cifras en cero tienen contraste de 3:1, por debajo de AA para texto. Es intencionado: son el ruido de fondo, y el recuento real está en el `alt`.
- Los paneles dejan una franja entre imágenes, blanca en tema claro. Se leen como láminas separadas.

## Taste Skill

Scripts ejecutados de verdad:

- `draw.mjs`: 6 direcciones repartidas, hoja completa de `editorial-report`, semilla 2083712076.
- `assets.mjs`: búsquedas en Wikimedia Commons; Openverse no respondió en 30 s. También NASA para vídeo.
- `lint.mjs` e `inspect.mjs`.
- `scenes.mjs` no se ejecutó: no hay escenas de scroll, y el repositorio oficial no incluye esa biblioteca.

Excepciones justificadas en `DESIGN.md`. La paleta repartida, "Candy chapters", se rechazó porque tu paleta está fijada. Esa decisión debió pasarse con `--keep palette,type`.

## Impeccable

- Ejecutado: `context`, `concept-seed`, `init` (PRODUCT.md), `surface-brief`, `critique`, `audit`, `hooks` y `detect`, más el documentador oficial para `DESIGN.md`.
- `init` y `shape` piden una entrevista. No la hice porque tu encargo ya respondía esas preguntas y pedía no detenerse. Tampoco presenté la ronda de direcciones para que eligieras.
- La ruta fue guiada por código: no hay herramienta de imágenes en esta sesión.
- `finish-reviewer` no se ejecutó, y la crítica no se repitió sobre la versión final.

## Sin verificar

- **Nada se ha visto en github.com.** El HTML viene de su API, pero las animaciones se probaron en Brave. Safari y la app móvil de GitHub no se probaron.
- **El corte de 1100 px** se dedujo del diseño de GitHub, no de una medición sobre tu perfil.
- **Token de grano fino.** Las pruebas reales usaron tu sesión de `gh`. El permiso `Metadata: Read-only` no se probó.
- **Workflow real.** Sus pasos corrieron en local y su YAML se analizó sin errores, pero nunca corrió en Actions.
- **Avatar y estado.** Son propuestas; no se aplicó nada.
