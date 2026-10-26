"""Short temático: Roswell 1947 con el clip del usuario (generado con IA, vertical, 20 s; ralentizado ×1,28 sin audio original).
Tono amarillista pedido por el usuario; la voz atribuye todo a "testigos aseguran" y el vídeo se rotula como ilustración (IA).
Sin rótulos a mitad de pantalla (apagados por defecto): solo logo arriba y banner abajo. Un solo archivo para TikTok y YouTube
(se renderiza con RN_TIKTOK=1: banner a y=1330)."""
from lib import *  # utilidades, paleta, Spec, video_bleed

C = None
HERE_S = os.path.dirname(os.path.abspath(__file__))
BG = Image.new("RGB", (W, H), (6, 8, 6))


def background(t, dim):
    return BG.copy()


def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0
    SC = ctx.SC_T
    A = f"{HERE_S}/assets"

    def sfx(sput, ctx):
        sput(rumble(3.0), 0.0, 0.9)
        sput(riser(0.9), 1.6, 0.5)
        sput(hit(50, 1.6, 0.9), 3.2, 1.0)
        sput(whoosh(0.5, True, 3), 0.3, 0.4)
        for i in range(1, 5):
            sput(whoosh(0.45, True, 10 + i), SC[i][0] - 0.1, 0.35)
        sput(thump(1.0), wd(1, "cuerpos"), 0.9)
        sput(rumble(2.5), wd(1, "cuerpos") - 0.2, 0.8)
        sput(blip(700, 0.15), wd(2, "hangar"), 0.5)
        sput(hit(60, 1.0, 0.6), wd(3, "globo") + 0.05, 0.8)
        sput(riser(1.2), wd(4, "prueba") - 0.6, 0.5)
        sput(hit(55, 1.4, 0.9), wd(4, "vieras") + 0.15, 1.0)
        sput(ping(), wd(5, "síguenos") + 0.35, 0.9)

    bleed = [video_bleed(f"{A}/clip_lento.mp4", 0.0, ctx.DUR + 1, 0.0, pan=(0.5, 0.5), tag="ILUSTRACIÓN CON IA · NO ES MATERIAL REAL")]
    impacts = [3.2, wd(1, "cuerpos"), wd(3, "globo") + 0.05, wd(4, "vieras") + 0.15]
    return Spec(background, [], impacts=impacts, flashes=[(3.2, 0.7)], sfx=sfx, bleed=bleed)
