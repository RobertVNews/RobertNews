#!/usr/bin/env python3
"""ROBERT NEWS · Generador de vídeos narrados.

Convierte un guion (texto plano con capítulos "## ") en:
  - audio narrado con voz neural gratuita (Edge TTS)
  - portada 1920x1080
  - vídeo MP4 listo para YouTube
  - marcas de tiempo de capítulos para la descripción

Uso:
  python3 herramientas/video/robertnews_video.py guion.txt \
      --titulo "CREATINA" --subtitulo "¿Músculo sin gimnasio?" \
      --duracion 90 --salida salida/creatina

  python3 herramientas/video/robertnews_video.py revisar URL_DE_LA_NOTICIA
"""
import argparse
import asyncio
import html
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import urllib.request
from pathlib import Path

VOZ_POR_DEFECTO = "es-CO-GonzaloNeural"
# Palabras por minuto efectivas de es-CO-GonzaloNeural (medido en un guion de 13.000 palabras).
PPM_BASE = 171
PAUSA_PARRAFO = 0.9
PAUSA_CAPITULO = 2.5
LIMITE_ENVIO_MB = 30

NUMEROS = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho",
           "nueve", "diez", "once", "doce", "trece", "catorce", "quince", "dieciséis",
           "diecisiete", "dieciocho", "diecinueve", "veinte"]

# Restos de generación automática que no deben llegar a una noticia publicada.
FUGAS = [
    (r"Imagen realista[^.\n]*", "instrucción de imagen visible en el texto"),
    (r"T[íi]tulo alternativo\s*:", "título alternativo visible en el texto"),
    (r"estilo fotogr[áa]fico|sin texto en la imagen", "instrucción de imagen visible en el texto"),
    (r"\bComo (?:modelo de lenguaje|IA)\b", "frase de asistente de IA"),
    (r"\[(?:insertar|completar|fuente)[^\]]*\]", "marcador sin completar"),
]


def ssl_context():
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    if ca:
        return ssl.create_default_context(cafile=ca)
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def ffprobe_duracion(ruta):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "csv=p=0", str(ruta)])
    return float(out)


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *args], check=True)


# ---------------------------------------------------------------- guion

def leer_guion(ruta, anunciar):
    """Devuelve [(titulo, [parrafos])]. Los capítulos se marcan con líneas '## Título'."""
    texto = Path(ruta).read_text(encoding="utf-8")
    capitulos, actual = [], None
    for bloque in re.split(r"\n\s*\n", texto):
        bloque = bloque.strip()
        if not bloque or bloque.startswith("<!--"):
            continue
        m = re.match(r"^##\s+(.+?)\s*(?:\n|$)", bloque)
        if m:
            actual = (m.group(1).strip(), [])
            capitulos.append(actual)
            bloque = bloque[m.end():].strip()
            if not bloque:
                continue
        if actual is None:
            actual = ("Introducción", [])
            capitulos.append(actual)
        actual[1].append(re.sub(r"\s*\n\s*", " ", bloque))
    if not capitulos:
        sys.exit("El guion está vacío.")
    if anunciar:
        n = 0
        for titulo, parrafos in capitulos:
            if titulo.lower().startswith("introducci"):
                continue
            n += 1
            nombre = NUMEROS[n] if n < len(NUMEROS) else str(n)
            parrafos.insert(0, f"Capítulo {nombre}. {titulo.rstrip('.')}.")
    return capitulos


def calcular_velocidad(palabras, n_parrafos, n_capitulos, minutos):
    pausas = (n_parrafos * PAUSA_PARRAFO + n_capitulos * PAUSA_CAPITULO) / 60
    minutos_voz = max(minutos - pausas, 1)
    factor = palabras / (PPM_BASE * minutos_voz)
    pct = round((factor - 1) * 100)
    acotado = max(-20, min(15, pct))
    if acotado != pct:
        ppm_min = PPM_BASE * (1 + acotado / 100)
        estimado = palabras / ppm_min + pausas
        falta = int((minutos - estimado) * PPM_BASE * 0.8)
        aviso = (f"faltan unas {falta} palabras" if falta > 0 else f"sobran unas {-falta} palabras")
        print(f"  Aviso: para {minutos} min habría que usar {pct:+d}%; uso {acotado:+d}% "
              f"(≈{estimado:.0f} min). Para clavar la duración, {aviso}.")
    return f"{acotado:+d}%"


# ---------------------------------------------------------------- voz

async def sintetizar(trabajos, voz, velocidad, concurrencia=4):
    import edge_tts.communicate as comm
    comm._SSL_CTX = ssl_context()
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    sem = asyncio.Semaphore(concurrencia)
    hechos = [0]

    async def uno(ruta, texto):
        if ruta.exists() and ruta.stat().st_size > 0:
            hechos[0] += 1
            return
        async with sem:
            for intento in range(5):
                try:
                    tmp = ruta.with_suffix(".part")
                    await comm.Communicate(texto, voz, rate=velocidad, proxy=proxy).save(str(tmp))
                    tmp.rename(ruta)
                    break
                except Exception as e:  # red inestable: reintento con espera exponencial
                    if intento == 4:
                        raise SystemExit(f"No se pudo generar {ruta.name}: {e}")
                    await asyncio.sleep(2 ** intento)
        hechos[0] += 1
        print(f"\r  Voz: {hechos[0]}/{len(trabajos)} fragmentos", end="", flush=True)

    await asyncio.gather(*(uno(r, t) for r, t in trabajos))
    print()


# ---------------------------------------------------------------- montaje

def hms(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"


def montar_audio(capitulos, seg, salida):
    for nombre, dur in (("corta", PAUSA_PARRAFO), ("larga", PAUSA_CAPITULO)):
        ffmpeg("-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", str(dur),
               "-c:a", "libmp3lame", "-b:a", "48k", str(seg / f"pausa_{nombre}.mp3"))
    lista, marcas, t = [], [], 0.0
    for ci, (titulo, parrafos) in enumerate(capitulos):
        if ci:
            lista.append("file 'pausa_larga.mp3'")
            t += PAUSA_CAPITULO
        marcas.append((t, titulo.rstrip(".")))
        for pi in range(len(parrafos)):
            if pi:
                lista.append("file 'pausa_corta.mp3'")
                t += PAUSA_PARRAFO
            f = seg / f"{ci:02d}_{pi:03d}.mp3"
            lista.append(f"file '{f.name}'")
            t += ffprobe_duracion(f)
    (seg / "lista.txt").write_text("\n".join(lista), encoding="utf-8")
    audio = salida / "audio.mp3"
    ffmpeg("-f", "concat", "-safe", "0", "-i", str(seg / "lista.txt"),
           "-c:a", "libmp3lame", "-b:a", "64k", "-ar", "24000", "-ac", "1", str(audio))
    if marcas and marcas[0][0] != 0:
        marcas[0] = (0.0, marcas[0][1])
    (salida / "capitulos_youtube.txt").write_text(
        "\n".join(f"{hms(s)} {titulo}" for s, titulo in marcas) + "\n", encoding="utf-8")
    return audio


def fuente(negrita):
    for f in (["DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf", "Arial Bold.ttf"] if negrita
              else ["DejaVuSans.ttf", "LiberationSans-Regular.ttf", "Arial.ttf"]):
        for base in ("/usr/share/fonts", "/Library/Fonts", "/System/Library/Fonts", "C:/Windows/Fonts"):
            for p in Path(base).rglob(f) if Path(base).exists() else []:
                return str(p)
    return None


def crear_portada(salida, titulo, subtitulo, bajada):
    b, r = fuente(True), fuente(False)
    if not b:
        print("  Aviso: no encontré fuentes; la portada saldrá sin texto.")
    textos = []
    capas = ["drawbox=x=0:y=0:w=1920:h=12:color=0xe63946:t=fill",
             "drawbox=x=120:y=800:w=500:h=6:color=0xe63946:t=fill"]
    for i, (txt, f, tam, color, y) in enumerate([
            ("ROBERT NEWS · ESPECIAL", b, 44, "0xe63946", 200),
            (titulo.upper(), b, 200 if len(titulo) <= 11 else 120, "white", 290),
            (subtitulo, b, 72 if len(subtitulo) <= 40 else 56, "0xf1c40f", 560),
            (bajada, r, 52, "0xdfe6ee", 680)]):
        if not txt or not f:
            continue
        p = salida / f".texto{i}.txt"
        p.write_text(txt, encoding="utf-8")
        textos.append(p)
        capas.append(f"drawtext=fontfile='{f}':textfile='{p}':fontsize={tam}:fontcolor={color}:x=120:y={y}")
    portada = salida / "portada.png"
    ffmpeg("-f", "lavfi", "-i", "color=c=0x0b1f33:s=1920x1080", "-frames:v", "1",
           "-vf", ",".join(capas), str(portada))
    for p in textos:
        p.unlink()
    return portada


def crear_video(portada, audio, destino, kbps):
    ffmpeg("-loop", "1", "-framerate", "1", "-i", str(portada), "-i", str(audio),
           "-c:v", "libx264", "-tune", "stillimage", "-preset", "veryfast", "-pix_fmt", "yuv420p",
           "-r", "1", "-c:a", "aac", "-b:a", f"{kbps}k", "-ac", "1", "-shortest", str(destino))


# ---------------------------------------------------------------- comandos

def cmd_generar(a):
    for exe in ("ffmpeg", "ffprobe"):
        if not shutil.which(exe):
            sys.exit(f"Falta {exe}. Instálalo (https://ffmpeg.org) y vuelve a intentar.")
    salida = Path(a.salida)
    seg = salida / "fragmentos"
    seg.mkdir(parents=True, exist_ok=True)

    capitulos = leer_guion(a.guion, not a.sin_anunciar)
    if a.muestra:
        capitulos = [(t, p[:a.muestra]) for t, p in capitulos[:2]]
    parrafos = sum(len(p) for _, p in capitulos)
    palabras = sum(len(x.split()) for _, p in capitulos for x in p)
    print(f"Guion: {len(capitulos)} capítulos, {parrafos} párrafos, {palabras} palabras.")

    velocidad = a.velocidad or (calcular_velocidad(palabras, parrafos, len(capitulos), a.duracion)
                                if a.duracion else "+0%")
    print(f"Voz: {a.voz} · velocidad {velocidad}")

    # Los fragmentos se reutilizan si el texto, la voz y la velocidad no cambiaron.
    firma = seg / "firma.json"
    actual = {"voz": a.voz, "velocidad": velocidad,
              "capitulos": [[t, p] for t, p in capitulos]}
    if firma.exists() and json.loads(firma.read_text(encoding="utf-8")) != actual:
        for f in seg.glob("*.mp3"):
            f.unlink()
    firma.write_text(json.dumps(actual, ensure_ascii=False), encoding="utf-8")

    trabajos = [(seg / f"{ci:02d}_{pi:03d}.mp3", texto)
                for ci, (_, ps) in enumerate(capitulos) for pi, texto in enumerate(ps)]
    asyncio.run(sintetizar(trabajos, a.voz, velocidad))

    audio = montar_audio(capitulos, seg, salida)
    minutos = ffprobe_duracion(audio) / 60
    print(f"Audio: {minutos:.1f} min")

    portada = crear_portada(salida, a.titulo or Path(a.guion).stem, a.subtitulo, a.bajada)
    video = salida / "video_youtube.mp4"
    # Bitrate de audio que deja el vídeo por debajo del límite de envío.
    kbps = max(24, min(96, int(LIMITE_ENVIO_MB * 8 * 1024 * 0.92 / (minutos * 60))))
    crear_video(portada, audio, video, kbps)
    shutil.copy(a.guion, salida / "guion.txt")
    if not a.conservar_fragmentos and not a.muestra:
        shutil.rmtree(seg)

    print(f"\nListo en {salida}/")
    for f in sorted(salida.iterdir()):
        if f.is_file():
            print(f"  {f.name:24s} {f.stat().st_size / 1e6:6.1f} MB")
    print("\nPega capitulos_youtube.txt en la descripción de YouTube.")


def extraer_noticia(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 RobertNewsVideo"})
    with urllib.request.urlopen(req, context=ssl_context(), timeout=30) as r:
        crudo = r.read().decode("utf-8", "replace")
    crudo = re.sub(r"<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", crudo, flags=re.S | re.I)
    titulo = re.search(r"<h1[^>]*>(.*?)</h1>", crudo, re.S | re.I)
    titulo = html.unescape(re.sub(r"<[^>]+>", "", titulo.group(1))).strip() if titulo else ""
    cuerpo = re.search(r"<article[^>]*>(.*?)</article>", crudo, re.S | re.I)
    cuerpo = cuerpo.group(1) if cuerpo else crudo
    cuerpo = re.sub(r"</(p|h\d|li|div)>|<br\s*/?>", "\n", cuerpo, flags=re.I)
    cuerpo = html.unescape(re.sub(r"<[^>]+>", " ", cuerpo))
    lineas = [re.sub(r"\s+", " ", l).strip() for l in cuerpo.splitlines()]
    return titulo, "\n".join(l for l in lineas if len(l) > 2)


def cmd_revisar(a):
    titulo, cuerpo = extraer_noticia(a.url)
    print(f"Título: {titulo or '(no encontrado)'}")
    print(f"Palabras en la página: {len(cuerpo.split())}\n")
    problemas = []
    for patron, motivo in FUGAS:
        for m in re.finditer(patron, cuerpo, re.I):
            fragmento = re.sub(r"\s+", " ", cuerpo[m.start():m.start() + 90]).strip()
            problemas.append(f"  · {motivo}: «{fragmento}…»")
    if problemas:
        print("PROBLEMAS EN LA NOTICIA PUBLICADA (corrígelos antes de hacer el vídeo):")
        print("\n".join(dict.fromkeys(problemas)))
    else:
        print("Sin restos de generación automática detectados.")
    if a.guardar:
        Path(a.guardar).write_text(f"{titulo}\n\n{cuerpo}\n", encoding="utf-8")
        print(f"\nTexto guardado en {a.guardar}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "revisar":
        p = argparse.ArgumentParser(prog="robertnews_video.py revisar",
                                    description="Revisa una noticia publicada y extrae su texto.")
        p.add_argument("url")
        p.add_argument("--guardar", help="archivo donde guardar el texto extraído")
        cmd_revisar(p.parse_args(sys.argv[2:]))
        return
    p = argparse.ArgumentParser(description="Convierte un guion en audio y vídeo narrado.")
    p.add_argument("guion", help="archivo .txt con capítulos marcados con '## Título'")
    p.add_argument("--salida", default="salida/video", help="carpeta de salida")
    p.add_argument("--titulo", help="texto grande de la portada")
    p.add_argument("--subtitulo", default="", help="pregunta o gancho de la portada")
    p.add_argument("--bajada", default="", help="línea pequeña de la portada")
    p.add_argument("--voz", default=VOZ_POR_DEFECTO,
                   help="voz de Edge TTS (es-CO-SalomeNeural, es-ES-AlvaroNeural…)")
    p.add_argument("--duracion", type=float, help="minutos objetivo; ajusta la velocidad")
    p.add_argument("--velocidad", help="velocidad fija, p. ej. -10%% (ignora --duracion)")
    p.add_argument("--sin-anunciar", action="store_true", help="no leer 'Capítulo uno…'")
    p.add_argument("--muestra", type=int, help="prueba rápida: solo N párrafos de 2 capítulos")
    p.add_argument("--conservar-fragmentos", action="store_true")
    cmd_generar(p.parse_args())


if __name__ == "__main__":
    main()
