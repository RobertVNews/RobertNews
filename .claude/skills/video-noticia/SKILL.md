---
name: video-noticia
description: Convierte una noticia de ROBERT NEWS (URL o tema) en un especial narrado de 30–90 min para YouTube, con guion investigado, voz neural, portada y capítulos. Úsalo cuando el usuario pida "hazme un vídeo/especial/audio de esta noticia" o invoque /video-noticia.
---

# Especial narrado a partir de una noticia

Argumentos: URL de la noticia (o tema) y, opcional, duración en minutos (por defecto 90) y voz.

## 1. Revisar la noticia publicada

```bash
python3 herramientas/video/robertnews_video.py revisar <URL> --guardar salida/<slug>/noticia.txt
```

Si reporta problemas (instrucciones de imagen, "Título alternativo", marcadores), díselo al usuario en la primera línea: la web los está mostrando a los lectores.

## 2. Verificar contra la fuente primaria

La noticia no es la fuente. Busca el estudio, comunicado o documento original (WebSearch; descarga el PDF si existe) y extrae: autores, fecha, diseño, tamaño de muestra por grupo, resultados con cifras, limitaciones declaradas, financiación y conflictos de interés. Anota cualquier diferencia entre la noticia y la fuente. Nunca inventes cifras: si un dato no está verificado, no va o se presenta como incierto.

## 3. Escribir el guion

Guárdalo en `salida/<slug>/guion.txt` con el formato de `herramientas/video/README.md` (capítulos `## Título`). Objetivo: unas 150 palabras por minuto (90 min ≈ 13.000 palabras). Estructura que funciona (ver `herramientas/video/ejemplos/creatina.txt`):

1. Introducción: gancho, qué se va a cubrir, aviso si es salud/finanzas/legal.
2. La noticia: qué se publicó, quién, cómo, resultados principales.
3. Contexto histórico.
4. Cómo funciona (explicación sencilla del mecanismo).
5. Los datos por dentro: cifras, grupos, qué salió y qué no.
6. Lectura crítica: limitaciones, conflictos de interés, titular justo.
7–9. Ángulos amplios: impacto en Colombia y Latinoamérica, evidencia relacionada, mitos.
10. Guía práctica / qué significa para el oyente.
11. Preguntas frecuentes.
12. Conclusiones + cierre "Esto fue Robert News".

Reglas de escritura para voz: español neutro-colombiano, trato de "usted"; números, años y siglas escritos como se pronuncian; sin listas, tablas ni markdown dentro de los párrafos; párrafos de 60–180 palabras. Sin relleno: cada capítulo aporta información nueva, porque YouTube desmonetiza el contenido repetitivo o "no auténtico".

## 4. Generar

Primero una muestra (`--muestra 2`) para comprobar la voz; luego el render completo en segundo plano:

```bash
python3 herramientas/video/robertnews_video.py salida/<slug>/guion.txt \
  --titulo "<1–2 palabras>" --subtitulo "<pregunta gancho>" --bajada "<línea corta>" \
  --duracion <min> --salida salida/<slug> --conservar-fragmentos
```

En un contenedor con proxy TLS exporta antes `SSL_CERT_FILE` con el CA del proxy.

## 5. Entregar

Envía `video_youtube.mp4` (viene por debajo de 30 MB), `capitulos_youtube.txt`, `guion.txt` y `portada.png`. Incluye un título y una descripción propuestos para YouTube con las fuentes. No subas nada de `salida/` al repositorio.
