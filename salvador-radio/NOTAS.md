# Diagnóstico de errores (análisis del código)

> Etiquetas: [Seguro] verificado en el código · [Probable] causa muy factible ·
> [Suposición] hay que confirmarlo probando en el sitio real.

## 0. Seguridad (lo más grave) — [Seguro] · CORREGIDO en este repo
La clave `123456` venía en `config.js`, un archivo **público**, y la verificación era
solo en el navegador. Cualquiera podía entrar al panel y controlar la emisora, o escribir
directo a `/api/sync` y `/api/live` sin clave. **Arreglo:** validación en el servidor con
`ADMIN_PASSCODE`; los oyentes solo leen / piden canciones.

## 1. No suena / no arranca el audio
- [Seguro] Política de autoplay: el navegador **exige un gesto** (clic en “Entrar/Escuchar”)
  antes de reproducir. Sin ese clic, no hay sonido. El código ya intenta `muted→play→unmute`.
- [Probable] Si la estación está **fuera del aire** (`nowPlaying: null`, como ahora), no hay
  nada que reproducir: es lo esperado, no un fallo.
- [Suposición] En iPhone/Safari los segmentos webm/opus del mic-HTTP **no** se reproducen
  (Safari no soporta webm). Para iOS conviene la ruta PeerJS, no el mic-HTTP.

## 2. El panel del DJ falla
- [Probable] **Raíz común con el #3:** el backend usa **jsonblob.com**, un servicio gratis y
  compartido, con límites y latencia. Cuando falla una escritura, `sync.js` reintenta y cae a
  caché local → los clics del DJ “no hacen nada” o se revierten. **Recomendación fuerte:**
  cambiar el almacén a **Vercel KV / Upstash Redis** (rápido y fiable). Es el cambio de mayor
  impacto para estabilidad.

## 3. No se sincroniza (lo del DJ no llega a oyentes)
- [Probable] Mismo origen: fiabilidad de jsonblob + polling por intervalo. Con Vercel KV se
  va casi en tiempo real.
- [Seguro] Emisora y dashboard ahora son dominios distintos pero comparten el **mismo**
  `STATION_SYNC_ID`, así que el estado se comparte igual. Verifica que ambos proyectos tengan
  ese mismo id en `config.js`.

## 4. YouTube / Spotify no cargan
- [Probable] **YouTube:** `/api/youtube` probablemente devolvía error. La versión reescrita
  resuelve el enlace por **oEmbed** (sin API key) y devuelve `videoId/title/cover`. Ojo:
  videos con **embed deshabilitado** por su dueño no se pueden reproducir.
- [Seguro] **Spotify:** `SPOTIFY_REDIRECT_URI` debe coincidir **exacto** con el registrado en
  el panel de Spotify. El original apuntaba a `salvador-entregas.vercel.app/admin`; si el panel
  queda en otro dominio, el login **rompe**. Actualiza ambos (Spotify Dashboard + `config.js`).
- [Suposición] Reproducir canciones completas por Spotify Web Playback requiere cuenta
  **Premium**; sin Premium solo hay previews de 30s.

## Siguiente paso de mayor impacto
Migrar `/api/sync` (y `/api/live`) de **jsonblob** a **Vercel KV**. Resuelve de raíz los
errores #2 y #3. Puedo hacerlo cuando conecte este repo a tu cuenta de Vercel.
