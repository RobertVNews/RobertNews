"""Short temático con el vídeo del usuario (nefilim2.mp4, vertical 10 s, generado con IA): se ralentiza ×2,14 (interpolado) para
cubrir la narración y se reproduce al revés la cola para no congelar. Rótulos sobre el vídeo a pantalla completa; sin escenas de panel.
Todo atribuido al texto bíblico (Números 13:33, Génesis 6) o a la tradición (Libro de Enoc); no se afirma que existieran."""
from lib import *  # utilidades, paleta, Spec, video_bleed, caption

C = None
HERE_S = os.path.dirname(os.path.abspath(__file__))
yy, xx = np.mgrid[0:H, 0:W].astype("float32")
BG = Image.new("RGB", (W, H), (8, 6, 8))


def background(t, dim):
    return BG.copy()


def setup(ctx):
    global C
    C = ctx
    wd = ctx.wd
    SC = ctx.SC_T
    A = f"{HERE_S}/assets"
    TAG = "CLIP ILUSTRATIVO (IA)"

    def sfx(sput, ctx):
        sput(rumble(3.0), 0.0, 0.9)
        sput(riser(0.5), 0.0, 0.4)
        sput(hit(55, 1.4, 0.7), 0.6, 0.9)
        for i in range(1, 6):
            sput(whoosh(0.45, True, 10 + i), SC[i][0] - 0.1, 0.35)
        sput(thump(0.9), wd(1, "aterrados") - 0.1, 0.8)
        sput(hit(60, 1.0, 0.6), wd(2, "langostas") + 0.05, 0.9)
        sput(rumble(3.0), wd(3, "ángeles") - 0.2, 0.8)
        sput(rumble(3.0), wd(4, "diluvio") - 0.2, 0.9)
        sput(riser(1.0), wd(5, "historia") - 1.0, 0.5)
        sput(hit(70, 1.0, 0.9), wd(5, "historia") + 0.1, 1.0)
        sput(ping(), wd(5, "síguenos") + 0.35, 0.9)

    bleed = [
        video_bleed(f"{A}/clip_lento.mp4", 0.0, ctx.DUR + 1, 0.0, pan=(0.5, 0.5), tag=TAG),
        caption("¿GIGANTES REALES?", wd(0, "gigantes"), SC[1][0], y=980, col=AMBER),
        caption("NEFILIM", wd(0, "nefilim"), SC[1][0], y=1085),
        caption("ESPÍAS EN CANAÁN", wd(1, "espías"), SC[2][0], y=980, col=AMBER),
        caption("NÚMEROS 13", wd(1, "aterrados"), SC[2][0], y=1085),
        caption("«ÉRAMOS COMO LANGOSTAS»", wd(2, "langostas") - 0.8, SC[3][0], y=1010, col=AMBER),
        caption("¿ÁNGELES CAÍDOS?", wd(3, "ángeles"), SC[4][0], y=980, col=AMBER),
        caption("LIBRO DE ENOC", wd(3, "enoc"), SC[4][0], y=1085),
        caption("EL DILUVIO", wd(4, "diluvio"), wd(4, "otros"), y=1010, col=AMBER),
        caption("¿O SOLO UN SÍMBOLO?", wd(4, "símbolo"), SC[5][0], y=1010),
        caption("¿MITO, SÍMBOLO O HISTORIA?", wd(5, "mito"), ctx.DUR + 1, y=1000, col=AMBER),
    ]
    impacts = [0.6, wd(1, "aterrados"), wd(2, "langostas"), wd(5, "historia") + 0.1]
    return Spec(background, [], impacts=impacts, flashes=[(0.6, 0.5)], sfx=sfx, bleed=bleed)
