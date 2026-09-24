# Guía: emisora en vivo (host gratis) + esta web

Esta web (`player/index.html`) es el **reproductor** que ven los oyentes. Reproduce
**cualquier** URL de stream (Icecast/Shoutcast), así que sirve con el servicio de radio
que elijas. El **audio** (transmitir, hablar en vivo, biblioteca de canciones) lo pone
un **host de radio**.

## Servicios de radio con plan GRATIS (auto-DJ + en vivo)
> Los planes gratis cambian y suelen tener límites (oyentes máx., bitrate, espacio, o
> algo de publicidad). Confirma los límites al registrarte.

- **Caster.fm** — plan *Free*: servidor Icecast ~400 oyentes, 96 kbps, AutoDJ, DJ en vivo,
  playlists y web de la radio. Buena opción para un colegio. (caster.fm)
- **Primcast** — hosting de radio gratis, oyentes ilimitados según su oferta, sin anuncios,
  AutoDJ, SSL. (primcast.com)
- **1Server.fr** — SHOUTcast/Icecast gratis con AutoDJ, SSL, analíticas, en vivo. (1server.fr)
- **FreeSHOUTcast** — servidor SHOUTcast gratis, setup instantáneo, AutoDJ, en vivo.

> **Nota honesta:** un stream de radio consume ancho de banda, así que "gratis de verdad"
> siempre trae algún límite. Para algo estable y sin límites, un plan pago barato (o un
> VPS ~5 USD/mes con **AzuraCast**, software gratis) es lo más sólido. Para el colegio, el
> plan gratis de Caster.fm suele alcanzar.

## Paso 1 — Crear la estación (lo haces tú, ~10 min)
1. Regístrate en el servicio que elijas (recomendado: **caster.fm**, plan Free).
2. Crea la estación con nombre **SALVADOR ENTREGAS**.

## Paso 2 — Copiar la URL del stream y pasármela
1. En el panel del servicio busca el **Stream URL** (formato MP3, algo como
   `http://servidor:puerto/stream` o una URL https que ellos den).
2. Pégalo en `player/index.html`:
   ```js
   var STREAM_URL = "PEGA_AQUI_TU_STREAM_URL";
   ```
   (O pásamelo y lo pego yo.)

## Paso 3 — Subir canciones (AutoDJ)
En el panel del servicio → sección **AutoDJ / Media / Playlists**: sube tus MP3 y arma la
lista. Suena solo cuando **no** estás en vivo.

## Paso 4 — Hablar en vivo (tu micrófono al aire)
El audio en vivo entra por un **encoder** (app en tu PC):
1. En el panel del servicio anota **servidor, puerto, contraseña y mountpoint** (empieza con `/`).
2. Instala **BUTT** (gratis, Windows/Mac) o **Mixxx**.
3. Crea un servidor tipo **Icecast/SHOUTcast** con esos datos, elige tu micrófono y pulsa
   **Broadcast**. Al detener, vuelve el AutoDJ.

## Paso 5 — Publicar la web (GitHub Pages, gratis, sin Vercel)
1. Repo **RobertNews** → **Settings → Pages**.
2. *Source*: **Deploy from a branch** → rama `claude/que-puedo-hacer-7kaw1g` → carpeta **/ (root)** → *Save*.
3. Queda en: `https://robertvnews.github.io/RobertNews/salvador-radio/player/`

## Opcionales (dímelo y lo activo)
- **"Ahora suena"** automático (si el servicio da endpoint de metadata) → `NOWPLAYING_URL`.
- **Pedir canción por WhatsApp** → pásame el número → `REQUEST_WHATSAPP`.
- **Logo real** → reemplaza `salvador-radio/emisora/assets/escudo-colegio-sm.jpg`.
