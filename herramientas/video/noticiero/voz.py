#!/usr/bin/env python3
"""Voz en off con entonación por frase y tiempos por palabra (Edge TTS, gratuito).

  python3 voz.py historias/<nombre> [--boost 11] [--voz es-MX-JorgeNeural]

Lee historias/<nombre>/guion.json y escribe en build/: voz.wav y linea_tiempos.json
(inicio/fin de cada línea y de cada palabra, que las escenas usan para sincronizar).
Si la red pasa por un proxy con certificado propio, exporta SSL_CERT_FILE con el CA.
"""
import argparse, asyncio, json, os, ssl, subprocess, sys, wave
import numpy as np
import edge_tts.communicate as comm

SR, GAP, LEAD = 44100, 0.26, 0.15


async def sintetizar(lineas, voz, boost, proxy):
    out = []
    for i, ln in enumerate(lineas):
        for intento in range(5):
            try:
                c = comm.Communicate(ln["texto"], voz, rate=f"{ln.get('vel', 0) + boost:+d}%", pitch=f"{ln.get('tono', 0):+d}Hz",
                                     volume=f"{ln.get('vol', 0):+d}%", boundary="WordBoundary", proxy=proxy)
                audio, words = bytearray(), []
                async for ch in c.stream():
                    if ch["type"] == "audio":
                        audio += ch["data"]
                    elif ch["type"] == "WordBoundary":
                        words.append({"t": ch["offset"] / 1e7, "d": ch["duration"] / 1e7, "w": ch["text"]})
                break
            except Exception:
                if intento == 4:
                    raise
                await asyncio.sleep(2 ** intento)
        out.append((bytes(audio), words))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("historia")
    ap.add_argument("--boost", type=int, help="ajuste global de velocidad en %% (por defecto el de guion.json)")
    ap.add_argument("--voz", help="voz de Edge TTS (por defecto la de guion.json)")
    a = ap.parse_args()
    d = os.path.abspath(a.historia)
    cfg = json.load(open(f"{d}/guion.json", encoding="utf-8"))
    voz = a.voz or cfg.get("voz", "es-MX-JorgeNeural")
    boost = cfg.get("boost", 0) if a.boost is None else a.boost
    build = f"{d}/build"
    os.makedirs(build, exist_ok=True)
    ca = os.environ.get("SSL_CERT_FILE")
    if ca:
        comm._SSL_CTX = ssl.create_default_context(cafile=ca)
    proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
    res = asyncio.run(sintetizar(cfg["lineas"], voz, boost, proxy))

    t, timeline, chunks = LEAD, [], []
    for i, (audio, words) in enumerate(res):
        open(f"{build}/l{i}.mp3", "wb").write(audio)
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", f"{build}/l{i}.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
        sig = np.frombuffer(raw, "float32")
        nz = np.where(np.abs(sig) > 0.012)[0]
        lo, hi = (max(0, nz[0] - int(0.03 * SR)), min(len(sig), nz[-1] + int(0.05 * SR))) if len(nz) else (0, len(sig))
        seg = sig[lo:hi]
        dur = len(seg) / SR
        timeline.append({"i": i, "t0": t, "t1": t + dur,
                         "words": [{"w": w["w"], "t": t + w["t"] - lo / SR, "d": w["d"]} for w in words]})
        chunks.append((t, seg))
        t += dur + GAP
    fin = timeline[-1]["t1"]
    n = int((fin + 2.0) * SR)
    mix = np.zeros(n, "float32")
    for t0, seg in chunks:
        k = int(t0 * SR)
        mix[k:k + len(seg)] += seg
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.88
    with wave.open(f"{build}/voz.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    json.dump({"voz": voz, "boost": boost, "fin_voz": fin, "lineas": timeline}, open(f"{build}/linea_tiempos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"voz {voz} · boost {boost:+d}% · la voz termina en {fin:.2f}s (vídeo ≈ {fin + 0.95:.1f}s)")
    for l in timeline:
        print(l["i"], f"{l['t0']:.2f}-{l['t1']:.2f}", " ".join(w["w"] for w in l["words"])[:70])


if __name__ == "__main__":
    main()
