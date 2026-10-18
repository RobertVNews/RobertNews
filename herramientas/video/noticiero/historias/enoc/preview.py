"""Vista previa del Short "Enoc" (estilo línea blanca sobre azul liso). Uso: python3 historias/enoc/preview.py [--hasta N]
Genera build/storyboard.png (todas las escenas) y build/preview.mp4 (las primeras N escenas con voz)."""
import sys, os, json, subprocess, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from lib import *

D = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(f"{D}/build/linea_tiempos.json", encoding="utf-8"))
LN = TL["lineas"]
END = TL["fin_voz"] + 0.6
TEXTOS = ["ENOC NUNCA MURIÓ", "CAMINÓ CON DIOS Y DESAPARECIÓ", "FUE TRASLADADO, NO MUERTO", "HA OBSERVADO TODAS LAS ÉPOCAS",
          "LA HUMANIDAD LO OLVIDÓ", "AÚN GUARDA LO QUE ESCRIBIÓ", "¿CAMINA ENTRE NOSOTROS?", "¿ESPERA EL MOMENTO?", "¿ENOC AÚN ESTÁ VIVO?"]
IMGS = {0: "escena1", 1: "escena2", 2: "escena3", 3: "escena4", 4: "escena5", 5: "escena6", 7: "escena8", 8: "escena9"}  # 7 (índice 6) pendiente
STARTS = [0.0] + [LN[i]["t0"] - 0.2 for i in range(1, 9)]
ENDS = STARTS[1:] + [END]
BLUE = (1, 35, 157)
DISC = S("RELATO BÍBLICO Y TRADICIONES · NO SON HECHOS VERIFICADOS", B6, 32, fill=(210, 220, 245))
_cache = {}


def img(i):
    if i not in IMGS:
        return None
    p = f"{D}/assets/{IMGS[i]}.webp"
    if not os.path.exists(p):
        return None
    if i not in _cache:
        _cache[i] = Image.open(p).convert("RGB").resize((1080, 1080), Image.LANCZOS)
    return _cache[i]


FEATHER = Image.fromarray((np.clip(np.minimum(np.minimum(np.arange(1080)[:, None], 1079 - np.arange(1080)[:, None]),
                                           np.minimum(np.arange(1080)[None, :], 1079 - np.arange(1080)[None, :])) / 40.0, 0, 1) * 255).astype("uint8"))


def text_sprite(txt):
    sp = S(txt, B7, 128, fill=(255, 255, 255))
    if sp.width <= 960:
        return [sp]
    w = txt.split()
    best = min(range(1, len(w)), key=lambda k: abs(len(" ".join(w[:k])) - len(" ".join(w[k:]))))
    return [S(" ".join(w[:best]), B7, 120, fill=(255, 255, 255)), S(" ".join(w[best:]), B7, 120, fill=(255, 255, 255))]


TXT = [text_sprite(t) for t in TEXTOS]


def end_card(cv, t):
    cv.paste((8, 8, 14), (0, 0, W, H))
    e = Image.open(f"{HERE}/assets/marca/emblema_rojo.png").convert("RGBA")
    e = e.resize((560, round(560 * e.height / e.width)), Image.LANCZOS)
    blit(cv, soft_glow(520, 520, (255, 20, 40), 60, 0.5), 540, 760)
    blit(cv, e, 540, 760, alpha=e_out(prog(t, 0, 0.5)))
    blit(cv, S("SÍGUENOS  @robertnews_", B7, 84, fill=(255, 255, 255), glow=((255, 20, 40), 16, 0.8)), 540, 1160, alpha=e_out(prog(t, 0.3, 0.8)))
    blit(cv, S("MÁS HISTORIA Y MISTERIOS CADA DÍA", B6, 46, fill=(255, 120, 130)), 540, 1260, alpha=e_out(prog(t, 0.5, 1.0)))


def frame(t):
    if t >= END:
        cv = Image.new("RGB", (W, H), (8, 8, 14))
        end_card(cv, t - END)
        return cv
    i = max(k for k in range(9) if STARTS[k] <= t + 1e-6)
    ts = t - STARTS[i]
    cv = Image.new("RGB", (W, H), BLUE)
    im = img(i)
    if im is not None:
        z = 1.0 + 0.07 * ts / max(ENDS[i] - STARTS[i], 1)
        sz = round(1080 * z)
        r = im.resize((sz, sz), Image.BILINEAR)
        m = FEATHER.resize((sz, sz), Image.BILINEAR)
        cv.paste(r, (540 - sz // 2, round(1010 - sz / 2 - 14 * ts / 7)), m)
    else:
        d = ImageDraw.Draw(cv)
        d.rectangle((120, 540, 960, 1480), outline=(255, 255, 255), width=3)
        blit(cv, S("IMAGEN PENDIENTE", B7, 70, fill=(255, 255, 255)), 540, 1010)
    sp = TXT[i]
    a = e_out(prog(ts, 0.15, 0.6))
    y0 = 250 if len(sp) == 1 else 215
    for k, s in enumerate(sp):
        blit(cv, s, 540, y0 + 128 * k + 14 * (1 - a), alpha=a)
    blit(cv, DISC, 540, 1690, alpha=0.8)
    return cv


if __name__ == "__main__":
    hasta = 9
    if "--hasta" in sys.argv:
        hasta = int(sys.argv[sys.argv.index("--hasta") + 1])
    # storyboard
    tiles = []
    for i in range(9):
        tiles.append(frame(STARTS[i] + 1.5).resize((324, 576), Image.LANCZOS))
    tiles.append(frame(END + 1.2).resize((324, 576), Image.LANCZOS))
    sheet = Image.new("RGB", (324 * 5 + 40, 576 * 2 + 10), (30, 30, 30))
    for k, tl in enumerate(tiles):
        sheet.paste(tl, ((k % 5) * 334, (k // 5) * 586))
    sheet.save(f"{D}/build/storyboard.png")
    t_end = ENDS[hasta - 1] if hasta < 9 else END + 3.0
    nf = int(t_end * FPS)
    out = f"{D}/build/preview.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", f"{D}/build/voz.wav", "-t", f"{t_end:.2f}", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11", "-c:v", "libx264", "-preset", "fast",
                          "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", out], stdin=subprocess.PIPE)
    for k in range(nf):
        p.stdin.write(frame(k / FPS).tobytes())
    p.stdin.close()
    p.wait()
    print("listo", out, f"{t_end:.1f}s")
