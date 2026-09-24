# Guía: emisora en vivo con Zeno.fm + esta web

Esta web (`player/index.html`) es el **reproductor** que ven los oyentes. El **audio**
(transmitir, hablar en vivo, biblioteca de canciones) lo pone **Zeno.fm** (gratis).

## Paso 1 — Crear la estación en Zeno.fm  (lo haces tú, 10 min)
1. Entra a **https://zeno.fm** → *Sign up* (cuenta gratis).
2. Crea una estación (nombre: **SALVADOR ENTREGAS**).
3. En el panel de Zeno (**Zeno Tools**) busca tu estación.

## Paso 2 — Sacar la URL del stream
1. En Zeno Tools → tu estación → copia el **Stream URL** (algo como
   `https://stream.zeno.fm/xxxxxxxx`).
2. Pégalo en `player/index.html`, en la línea:
   ```js
   var STREAM_URL = "PEGA_AQUI_TU_STREAM_URL_DE_ZENO";
   ```
   (Dímelo y lo pego yo por ti.)

## Paso 3 — Subir canciones (biblioteca / auto-DJ)
1. En Zeno Tools → tu estación → sección de **Automation / Media**.
2. Sube tus MP3 y arma la lista. Zeno los reproduce solo cuando **no** estás en vivo.

## Paso 4 — Hablar en vivo (tu micrófono al aire)
Zeno recibe la voz por un **encoder** (una app en tu PC). El más fácil:
1. En Zeno Tools → tu estación → **Broadcast Settings**: anota **servidor, puerto,
   mountpoint y contraseña** (el mountpoint empieza con `/`).
2. Instala **BUTT** (Broadcast Using This Tool, gratis, Windows/Mac) o **Mixxx**.
3. En la app, crea un servidor tipo **Icecast** con esos datos y elige tu micrófono.
4. Pulsa **Broadcast/Play** → estás al aire. Al detener, Zeno vuelve al auto-DJ.

> Desde el celular también hay apps de broadcast Icecast, pero desde PC con BUTT es lo
> más estable para el colegio.

## Paso 5 — Publicar la web (GitHub Pages, gratis, sin Vercel)
1. En GitHub, repo **RobertNews** → **Settings → Pages**.
2. *Build and deployment* → *Source*: **Deploy from a branch**.
3. Branch: la rama donde está esto (`claude/que-puedo-hacer-7kaw1g`) → carpeta **/ (root)** → *Save*.
4. En 1–2 min tu player queda en:
   `https://robertvnews.github.io/RobertNews/salvador-radio/player/`

## Opcionales (dímelo y lo dejo listo)
- **"Ahora suena"** automático: si Zeno te da un endpoint de metadata, lo conecto en
  `NOWPLAYING_URL`.
- **Pedir canción por WhatsApp**: pásame el número y activo el botón (`REQUEST_WHATSAPP`).
- **Logo real**: reemplaza `salvador-radio/emisora/assets/escudo-colegio-sm.jpg` por el escudo.

---

### ¿Y todo lo otro que reconstruí antes?
La carpeta `salvador-radio/emisora` y `salvador-radio/dashboard` es la versión con
**servidor propio** (panel de DJ completo, PeerJS, etc.). Queda guardada por si algún día
quieres esa vía con una cuenta de hosting. Para una emisora **estable y sencilla**, el
camino Zeno + este player es el recomendado.
