# SALVADOR ENTREGAS — Radio del colegio

Código recuperado del sitio en vivo (`salvador-entregas.vercel.app`) y **separado en dos apps**
para que la emisora (oyentes) sea liviana y el panel de control (locutor) vaya aparte.

```
emisora/     -> lo que abren los OYENTES  (página en vivo, liviana)
dashboard/   -> el PANEL del LOCUTOR/DJ   (control, pesado: ~240 KB)
```

Cada carpeta es un **proyecto de Vercel independiente** (dos dominios, un solo repo).
Comparten el mismo estado porque ambos hablan con el mismo canal (`STATION_SYNC_ID`) vía `/api/sync`.

---

## 1) Desplegar en Vercel (dos proyectos, misma cuenta)

Para cada carpeta crea un proyecto en Vercel:

| Proyecto        | Root Directory | Dominio sugerido                |
|-----------------|----------------|---------------------------------|
| Emisora oyentes | `emisora`      | `salvador-entregas.vercel.app`  |
| Panel del DJ    | `dashboard`    | `salvador-dj.vercel.app`        |

Vercel → **Add New Project** → importa este repo → en *Root Directory* elige `emisora`
(y repite creando otro proyecto con `dashboard`). Framework: **Other**.

## 2) Variables de entorno (en AMBOS proyectos)

| Variable          | Para qué sirve                                                        | Obligatoria |
|-------------------|----------------------------------------------------------------------|-------------|
| `ADMIN_PASSCODE`  | Clave del locutor. El **servidor** la valida en cada cambio.         | Sí (seguridad) |
| `STATION_LIVE_ID` | Blob de jsonblob para el micrófono-HTTP (ver abajo).                 | Opcional    |

> Si `ADMIN_PASSCODE` **no** se define, cualquiera puede controlar la emisora (comportamiento
> viejo). Defínela para cerrar el hueco. Ya **no** hay ninguna clave en `config.js`.

## 3) Micrófono en vivo por HTTP (opcional)

`/api/live` guarda los segmentos de voz en un blob de [jsonblob.com](https://jsonblob.com):
1. En jsonblob.com crea un blob con contenido `{"chunks":[]}` y copia su id.
2. Ponlo en la variable `STATION_LIVE_ID` de ambos proyectos.

Si no lo configuras, el mic-HTTP queda **desactivado de forma segura** (no rompe nada).
La voz en vivo por **PeerJS** (`live-stream.js`) funciona sin backend y no necesita esto.

## 4) Spotify

En [developer.spotify.com](https://developer.spotify.com) → tu app → *Redirect URIs*, pon
**exactamente** el dominio del **dashboard** (sin `/` final), y ajústalo en `dashboard/config.js`
(`SPOTIFY_REDIRECT_URI`).

## 5) Logo

`assets/escudo-colegio-sm.jpg` es un **placeholder** (1×1). Reemplázalo por el escudo real
en `emisora/assets/` y `dashboard/assets/`.

---

## Qué se cambió respecto al original

- **Seguridad:** la clave `123456` ya **no** viaja en `config.js` (era pública y legible por
  cualquiera). Ahora se valida en el servidor (`ADMIN_PASSCODE`). Los oyentes solo pueden
  **leer** y mandar **peticiones de canciones**; no pueden controlar la emisora.
- **Separación** emisora / dashboard (este repo).

## Qué es fiel y qué es reconstruido

- **Fiel (idéntico al vivo):** `index.html` (oyentes y panel), `sync.js`, `http-live.js`,
  `live-stream.js`, `mp3-library.js`, `config.js`. (A `sync.js`/`http-live.js` solo se les
  añadió el envío de la clave por cabecera; a `config.js` se le quitó la clave.)
- **Reconstruido (el backend no era descargable):** `api/sync.js`, `api/live.js`,
  `api/youtube.js`. Respetan el mismo contrato que espera el cliente, pero conviene
  probarlos contra el sitio real.

## Errores reportados — diagnóstico

Ver el análisis y las causas probables en `NOTAS.md`.
