# Metodología de datos

Cada cifra del perfil sale de `data/stats.json`, escrito por `scripts/collect.py`. Ninguna se dibuja a mano ni la genera un modelo de imágenes.

## Lenguajes de repositorios propios

Fuente: `GET /repos/{owner}/{repo}/languages`, que entrega bytes detectados por GitHub Linguist en la rama predeterminada.

```text
porcentaje = bytes_del_lenguaje / suma_de_bytes_del_grupo × 100
```

Se suman bytes y luego se calcula el porcentaje. Nunca se promedian porcentajes por repositorio, porque un repositorio diminuto pesaría igual que uno grande.

| Grupo | Incluye |
|---|---|
| GLOBAL | Públicos y privados propios |
| PUBLIC | Solo públicos propios |
| PRIVATE | Solo privados propios a los que llega el token |

### Casos especiales

| Caso | Tratamiento |
|---|---|
| Forks | Excluidos: su código es en su mayoría ajeno. `dwm` queda fuera por esto |
| Este repositorio | Excluido: sus generadores inflarían Python y SVG |
| Repositorios vacíos | Excluidos: GitHub no reporta lenguajes |
| Archivados | Incluidos: el código sigue siendo tuyo |
| Eliminados | Desaparecen del listado y salen del cálculo en la siguiente ejecución |
| Nuevos | Entran en la ejecución siguiente a que GitHub calcule su tamaño |
| Acceso revocado durante la ejecución | La ejecución falla, sin nombrar el repositorio, y conserva los datos anteriores |
| Sin acceso a ningún privado | La ejecución falla y conserva los datos anteriores |
| Código generado y dependencias | Linguist los excluye con sus reglas; se puede ajustar con `.gitattributes` en cada repositorio |
| Lenguajes no identificados | Linguist no los cuenta |

### Limitaciones de Linguist

- Mide bytes, no tiempo, habilidad ni autoría. Un archivo de datos grande pesa más que meses de trabajo.
- Clasifica por extensión y heurísticas, y puede equivocarse. `Papyrus`, con 7,2 % en público, parece un error de este tipo o archivos de un repositorio concreto. No lo corregí a mano: la solución correcta es un `.gitattributes` en el repositorio de origen.
- Solo mira la rama predeterminada.

## Contribuciones

Es un grupo aparte porque usa otra métrica: **líneas cambiadas, no bytes**. Nunca se mezcla con los otros tres.

Mide solo lo que puede atribuirse a la cuenta en repositorios públicos ajenos:
- Archivos de pull requests fusionados de la cuenta.
- Commits de la cuenta encontrados por búsqueda, sin contar los commits de merge.

Nunca usa los lenguajes del repositorio anfitrión, porque eso te atribuiría código que no escribiste. El lenguaje se deduce por la extensión de cada archivo tocado. Se ignoran archivos de bloqueo, minificados y extensiones sin correspondencia.

Resultado actual: 6 líneas, 1 pull request fusionado, 2 commits directos, 3 repositorios. El 100 % de Astro es real, pero la muestra es mínima y el perfil lo dice debajo del gráfico.

Limitaciones:
- La búsqueda de commits solo ve lo indexado por GitHub.
- Pull requests cerrados sin fusionar no cuentan: uno de 383 líneas añadidas en `midudev/bigibai` quedó fuera por eso.
- Los commits fusionados con squash cuentan por los archivos del pull request.
- Un fallo aquí no detiene el resto: el panel dice que no pudo medirse.

## Calendario de contribuciones

Fuente: GraphQL `contributionCalendar`, consultado siempre con el `GITHUB_TOKEN` del workflow y nunca con el token de acceso privado. Así el perfil no puede mostrar más que lo que ve cualquier visitante.

| Visualización | Regla |
|---|---|
| Cifras | Cada día es su recuento; desde 9 se muestra 9 y va en acento |
| Mástiles | Altura proporcional a la raíz cuadrada del recuento |
| Colores de mástil | Gris menos de 4, claro de 4 a 14, acento desde 15 |

La raíz cuadrada evita que el pico de 45 aplaste los días de 1 y 2. El gráfico lo declara.

## Mensaje cifrado

El mensaje oculto es un cifrado de un solo uso real con tablero de sustitución. El texto incluye las contribuciones de los últimos siete días, escritas con palabras. El pad se deriva con SHA-256 del texto y la fecha, y se publica junto al mensaje porque es un juego, no un secreto. Una prueba confirma que se descifra.

## Privacidad

Solo salen de `collect.py`:
- Nombres de lenguajes con posición y porcentaje.
- Calendario público.
- Metadatos de los cuatro proyectos públicos listados en `profile.config.json`.
- Cobertura de contribuciones y un indicador `complete`.

No salen nombres, enlaces, rutas, descripciones ni identificadores de repositorios privados, ni bytes en bruto, ni el número de repositorios privados.

Controles:
- Los registros de repositorios solo existen en memoria durante la ejecución.
- Los errores usan mensajes fijos, sin URL ni nombre.
- El workflow no publica artefactos ni archivos de diagnóstico.
- `tests/test_profile.py` usa un repositorio sintético secreto y comprueba que no aparezca.
- `tests/test_published.py` revisa los archivos reales antes de cada commit.

**Información residual que sí queda pública.** Comparando GLOBAL, PUBLIC y PRIVATE se puede estimar qué proporción de tu código total es privada. También se ve qué lenguajes usas en privado. Es una consecuencia inevitable de publicar agregados, y es lo que autorizaste.

## Actualización

- Una ejecución diaria a las 05:23 UTC, más ejecución manual. GitHub puede retrasar las programadas.
- Reintentos ante errores 5xx y límites de API, con paginación acotada.
- Solo se hace commit si cambian lenguajes, cobertura, proyectos o el total del calendario, o si cambia la semana. Por eso una cuenta quieta produce como máximo un commit semanal.
- Si algo falla, el workflow termina en error y no toca lo publicado.
- La fecha real aparece en el perfil como última cifra y última recepción.
