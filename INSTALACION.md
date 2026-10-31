# Instalación y publicación

Ya está publicado. Esta guía queda para repetir o renovar la instalación.

## 1. Revisa la vista previa

Abre `previews/index.html` en tu navegador. La generé con el HTML que devuelve la API de Markdown de GitHub, así que refleja lo que su sanitizador deja pasar. Las animaciones funcionan ahí igual que dentro de un `<img>`.

Para ver el perfil como lo verá GitHub, puedes publicar primero en una rama y abrirla en la web.

## 2. Crea el token

El `GITHUB_TOKEN` estándar no ve tus repositorios privados, así que necesitas un token aparte. Nunca lo pegues en un chat, en el código ni en un commit.

1. Ve a **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.
2. **Resource owner:** `rx3card`.
3. **Expiration:** la que prefieras, por ejemplo 1 año. Cuando venza, el workflow fallará sin tocar lo publicado.
4. **Repository access:** elige **All repositories** para que los repositorios nuevos entren solos. Con **Only select repositories** deberás añadir cada repositorio nuevo.
5. **Repository permissions → Metadata: Read-only.** Es el mínimo y GitHub lo marca solo.
6. No concedas ningún otro permiso. En especial, nada de escritura.

Este permiso bastó en la ejecución real: `Metadata: Read-only` entrega los lenguajes de los repositorios privados.

## 3. Guarda el token como secreto

1. En `rx3card/rx3card`, ve a **Settings → Secrets and variables → Actions → New repository secret**.
2. **Name:** `PROFILE_STATS_TOKEN`
3. **Secret:** el token.

## 4. Publica

Revisa primero `git status`. El `.gitignore` excluye `archive/`, `.taste-skill/`, `.impeccable/`, el ZIP y la carpeta del kit anterior.

```bash
git add -A
```

```bash
git status
```

```bash
git commit -m "Receiving"
```

```bash
git push origin main
```

## 5. Primera ejecución

1. Ve a **Actions → Refresh profile → Run workflow**.
2. Comprueba que los pasos Test, Collect, Render y "Check what will be published" pasen.
3. Abre `github.com/rx3card`.

Desde entonces corre cada día. GitHub suspende los workflows programados tras 60 días sin actividad en el repositorio; si pasa, actívalo desde Actions.

Si el commit falla por permisos, ve a **Settings → Actions → General → Workflow permissions** y elige **Read and write permissions**.

## 6. Identidad del perfil

Aplica lo que quieras de `PROFILE_IDENTITY.md`: bio, estado, repositorios fijados y avatar. Es manual a propósito.

## Temporadas

`profile.config.json` decide la temporada:

- `"season": "auto"` usa el calendario. Halloween va del 1 de octubre al 2 de noviembre; el resto del año, `dark`.
- `"season": "dark"` fija una temporada.

Para añadir una temporada nueva, copia un bloque dentro de `seasons`, y cambia colores, textos y fechas. Admite fechas que cruzan el año, como `"from": "12-20", "to": "01-05"`. No hace falta tocar los scripts. La temporada cambia sola en la ejecución diaria.

Las fotos tienen dos tratamientos, `halloween` y `dark`, indicados en el campo `plate`. Para otro color, añádelo a `scripts/build_plates.sh`.

## Trabajo local

Regenerar el arte con los datos actuales, sin red ni tokens:

```bash
python3 scripts/render.py
```

Pruebas:

```bash
python3 -m unittest discover -s tests
```

Recoger datos reales en local (usa tu propia sesión de `gh`, con la que el calendario podría incluir lo que solo tú ves):

```bash
PROFILE_STATS_TOKEN=$(gh auth token) GITHUB_TOKEN=$(gh auth token) python3 scripts/collect.py
```

## Deshacer

La versión anterior publicada sigue en el historial de git. El kit V2 quedó en `archive/v2/` y solo existe en tu equipo.
