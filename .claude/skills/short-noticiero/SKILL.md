---
name: short-noticiero
description: Crea un Short vertical de ~45 s estilo noticiero (voz en off, gráficos animados, banner de ROBERT NEWS) a partir de una noticia. Úsalo cuando el usuario pida "un short de esta noticia", "hazme el short" o invoque /short-noticiero con una URL de robertnews.vercel.app.
---

# Short de noticiero a partir de una noticia

Todo el método, la estructura y las lecciones están en `herramientas/video/noticiero/README.md`. Léelo antes de empezar. Resumen operativo:

## 1. Leer la nota (sin verificar por tu cuenta)
- `curl -sSL -A "Mozilla/5.0" <URL>` y extrae el texto del `<article>`, o usa el texto que pegue el usuario.
- **Regla del usuario (2026-10-18): no contrastar las noticias con fuentes externas, no corregir cifras ni datos, no cambiar su texto "porque no sea verdad".** Haz el guion con lo que dice la nota o el texto del usuario, conservando sus matices ("supuestamente", "según fuentes", etc.).
- Solo busca en la web si el usuario lo pide expresamente.
- No inventes datos que no estén en la nota ni conviertas lo atribuido en hecho.

## 2. Crear la historia
- Carpeta `herramientas/video/noticiero/historias/<slug>/` con `guion.json`, `escenas.py` y `assets/` (la imagen que envíe el usuario, convertida a `.webp`/`.png`).
- Guion de 8–9 líneas y ~120–130 palabras; una escena por línea. Atribuye todo lo dudoso. Números en palabras.
- Copia la estructura de `historias/nucleo` o `historias/arca` y cambia sprites, escenas y efectos. Los gráficos de escala que no sean datos reales llevan el rótulo "ILUSTRATIVO".

## 3. Voz, prueba y render
```bash
cd herramientas/video/noticiero
SSL_CERT_FILE=<ca-del-proxy> python3 voz.py historias/<slug>        # ajusta --boost para ~45 s
python3 render.py historias/<slug> test <tiempos clave...>           # revisar build/contacto.png
python3 render.py historias/<slug> render                            # build/short.mp4, en segundo plano
```
Revisa solapes y texto cortado en la hoja de contacto, incluyendo el instante en que empieza cada animación, antes del render completo. Tras el render comprueba con ffprobe duración, y con `ebur128` el volumen (≈ −14 LUFS).

## 4. Entregar
- Envía `short.mp4` (menos de 30 MB) y un `.txt` con título (gancho en los primeros 40 caracteres), descripción con fuentes y aviso, hashtags, comentario fijado y ajustes de Studio ("contenido sintético: Sí").
- Di qué no verificaste: nunca has escuchado el audio, solo medido su volumen.
- No subas `build/` al repo (está en `.gitignore`).
