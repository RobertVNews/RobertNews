# Shorts estilo noticiero · ROBERT NEWS

Convierte una noticia en un Short vertical de ~45 s (1080×1920): voz en off en español con entonación por frase, gráficos animados que caen justo cuando se dice cada palabra, banner de noticiero con cinta, efectos de sonido sintetizados y cierre con botón. Sin personas y sin depender de generadores de vídeo con IA: todo se dibuja con código, así los textos y las cifras salen exactos.

## Requisitos

```bash
pip install pillow numpy edge-tts
# y ffmpeg + ffprobe en el PATH
```

Detrás de un proxy con certificado propio: `export SSL_CERT_FILE=/ruta/al/ca.crt`. Las fuentes (Anton y Barlow Condensed, licencia OFL) y el logo ya están en `fonts/` y `assets/`.

## Estructura

```
noticiero/
  lib.py        motor: animación, texto, banner, paneles, sellos, cámara, sonido, render
  voz.py        voz con tiempos por palabra  ->  build/voz.wav + build/linea_tiempos.json
  render.py     test (PNG + hoja de contacto) y render (build/short.mp4)
  historias/<nombre>/
    guion.json  líneas del guion, entonación y datos de marca
    escenas.py  una escena por línea; setup(ctx) devuelve el Spec
    assets/     imágenes de la historia (p. ej. la foto que envía el usuario)
    build/      generado (no se sube al repo)
```

Historias de ejemplo: `arca` (Arca de Noé, 8 escenas) y `nucleo` (núcleo terrestre, 9 escenas).

## El método, paso a paso

1. **Leer la noticia.** `curl` de la URL de Robert News o el texto que pegue el usuario. Por instrucción del usuario (2026-10-18) no se contrasta con fuentes externas ni se corrigen datos salvo que lo pida.
2. **Escribir el guion: 8–9 líneas, unas 120–130 palabras** para 45 s. Una idea por línea: gancho → contexto → dato → mecanismo → matiz o contra-argumento → cierre con "Síguenos en Robert News". Números y años en palabras. Todo lo no verificado se atribuye ("según uno de sus líderes", "algunos creen").
3. **`guion.json`:** voz (`es-MX-JorgeNeural` por defecto: la más neutra), `boost` global de velocidad, `lineas` con `vel`/`tono`/`vol` por frase (explosivas en los golpes de efecto, graves en el misterio), `marca` (etiqueta, titular del banner, cinta, palabra del cierre) y `escenas_en_linea`.
4. **Voz:** `python3 voz.py historias/<nombre>`. Ajusta `--boost` hasta que diga "vídeo ≈ 45 s".
5. **Escenas** (`escenas.py`): una función `f(cv, t)` por línea. Sincroniza con `ctx.wd(linea, "palabra")` (instante en que se dice) y usa `ctx.sw(t, i)` para entrada/salida. Gráficos con `panel`, `rtext`/`S`, `blit`, `comp` + `ImageDraw`, `make_stamp`, `shake`. `setup(ctx)` devuelve `Spec(background, scenes, impacts, flashes, sfx, dim)`.
6. **Prueba visual antes de renderizar:** `python3 render.py historias/<nombre> test 1.0 6.5 12 ...` y abre `build/contacto.png`. Mira solapes, texto cortado y zona segura. Incluye siempre el instante justo en que empieza cada animación.
7. **Render:** `python3 render.py historias/<nombre> render` → `build/short.mp4` (unos 5 min). Comprueba duración, volumen (≈ −14 LUFS) y peso (< 30 MB para poder enviarlo).
8. **Publicación:** título (el gancho va en los primeros 40 caracteres), descripción con fuentes y aviso, 3–5 hashtags, comentario fijado con una pregunta. En YouTube Studio marca "contenido sintético: Sí".

## Lecciones aprendidas

- **Rótulos a mitad de pantalla:** apagados por defecto (`RN_ROTULOS=1` los activa). Solo quedan logo arriba y banner abajo.
- **Zona segura de Shorts:** la interfaz tapa el 15 % superior y buena parte de la inferior. Contenido entre y=215 y y=1235. Por preferencia del usuario el banner va abajo: barra en y≈1420 (Shorts) o y≈1330 (TikTok); se cambia con `DY` en `lib.py` (sube el banner restando píxeles si la interfaz lo tapa).
- **Caracteres:** las fuentes latinas de Anton/Barlow no incluyen "≈", "→" ni "≠". Evítalos (o dibuja la flecha con líneas, como hace el botón final).
- **Gráficos de escala:** si no son datos reales, rotúlalos "ILUSTRATIVO". Las cifras reales salen de la fuente primaria.
- **Fuentes:** si GitHub bloquea la descarga (403), `npm pack @fontsource/anton @fontsource/barlow-condensed` entrega los `.woff`.
- **Errores típicos:** rectángulos con altura negativa al inicio de una animación (usa `max(...)`); texto más ancho que su caja (reescala el sprite); sellos que tapan otro texto.
- **Audio:** no se oye hasta que lo escuchas. El motor mide el volumen, no el resultado artístico: escucha el vídeo antes de publicar.
- **Voz sintética:** se declara siempre en la descripción y en el ajuste de Studio.

## Comandos de la historia del núcleo (ejemplo completo)

```bash
python3 voz.py historias/nucleo            # voz + tiempos
python3 render.py historias/nucleo test 1.0 6.5 12 20 28 36 43
python3 render.py historias/nucleo render  # build/short.mp4
```
