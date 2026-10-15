# ROBERT NEWS · Vídeos narrados

> **Shorts de noticiero (45 s, gráficos animados, voz explosiva):** ver [`noticiero/README.md`](noticiero/README.md) y la skill `/short-noticiero`. Este documento cubre los especiales largos (30–90 min).

Convierte una noticia en un especial narrado (30–90 min) con voz neural gratuita, portada y capítulos para YouTube.

## Flujo completo

1. **Revisa la noticia publicada** (detecta restos de IA como instrucciones de imagen o "Título alternativo"):

   ```bash
   python3 herramientas/video/robertnews_video.py revisar https://robertnews.vercel.app/noticia/... --guardar salida/noticia.txt
   ```

2. **Escribe el guion.** En Claude Code basta con:

   ```
   /video-noticia https://robertnews.vercel.app/noticia/...
   ```

   Claude verifica la fuente original, escribe el guion por capítulos y genera el vídeo. Si lo escribes tú, usa el formato de abajo.

3. **Genera audio y vídeo:**

   ```bash
   python3 herramientas/video/robertnews_video.py salida/guion.txt \
     --titulo "CREATINA" \
     --subtitulo "¿Músculo y memoria sin ir al gimnasio?" \
     --bajada "Lo que dice (y lo que no dice) el nuevo estudio" \
     --duracion 90 \
     --salida salida/creatina
   ```

   Resultado en `salida/creatina/`: `video_youtube.mp4`, `audio.mp3`, `portada.png`, `capitulos_youtube.txt`, `guion.txt`.

## Formato del guion

Texto plano. Cada capítulo empieza con `## Título`; los párrafos van separados por una línea en blanco.

```
## Introducción

Bienvenidos a Robert News...

## La noticia

Un estudio publicado...
```

- La voz anuncia "Capítulo uno. La noticia." automáticamente (desactívalo con `--sin-anunciar`). La introducción no se anuncia.
- Escribe los números y siglas como se pronuncian ("diez gramos", "Texas A y M").
- Ejemplo completo: `ejemplos/creatina.txt` (13.200 palabras ≈ 90 min).

## Duración

Unas **150 palabras = 1 minuto** de audio final. 90 min ≈ 13.000 palabras.
`--duracion 90` ajusta la velocidad de la voz (entre −20 % y +15 %) y avisa si faltan o sobran palabras.

## Opciones

| Opción | Para qué |
|---|---|
| `--voz es-CO-SalomeNeural` | Voz femenina colombiana. Otras: `es-ES-AlvaroNeural`, `es-MX-JorgeNeural`. |
| `--velocidad -10%` | Velocidad fija (ignora `--duracion`). |
| `--muestra 2` | Prueba rápida: 2 párrafos de 2 capítulos. Úsala antes del render largo. |
| `--conservar-fragmentos` | Guarda los fragmentos para regenerar solo lo que cambie. |

Si se corta la conexión, vuelve a ejecutar el mismo comando con `--conservar-fragmentos`: reutiliza lo ya generado.

## Instalación

```bash
pip install -r herramientas/video/requirements.txt
# y ffmpeg: https://ffmpeg.org  (Windows: winget install ffmpeg · Mac: brew install ffmpeg)
```

Detrás de un proxy con certificado propio: `export SSL_CERT_FILE=/ruta/al/ca.crt`.

## Antes de publicar en YouTube

- Escucha el inicio y un par de puntos al azar: la voz puede pronunciar mal nombres propios.
- Activa "contenido alterado o sintético" en YouTube Studio solo si el vídeo muestra personas o hechos realistas generados por IA; una narración con voz sintética sobre hechos reales no lo exige, pero menciónalo en la descripción por transparencia.
- Para que YouTube no lo trate como contenido "no auténtico", cada vídeo debe aportar análisis propio (contexto, lectura crítica, fuentes), no solo leer la noticia.
- `salida/` está en `.gitignore`: los vídeos no se suben al repo ni a Vercel.
