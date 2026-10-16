"""Historia: amuleto de plata de Fráncfort, "evidencia cristiana más antigua al norte de los Alpes".

Short de ~49 s. Todo sale de la nota de Robert News, que se apoya en publicaciones en redes (X) y un artículo de AOL;
no cita el estudio científico, así que el guion lo dice ("según los arqueólogos", "conviene contrastarla").
Imagen de apertura/cierre (ChatGPT) y clips (Gemini) son ilustrativos y se rotulan. La línea de tiempo es esquemática.
Escenas: foto de gancho · clip del amuleto · clip excavación + TC · clip TC (inscripción) · foto (frases) ·
línea de tiempo (panel) · fuentes (panel) · cierre con foto y emblema.
"""
import math
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec, photo_bleed, video_bleed, caption

C = None
HERE_S = os.path.dirname(os.path.abspath(__file__))
SILVER = (205, 215, 230)

# ------------------------------------------------------------------ fondo (solo se ve en los paneles)
yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([6, 9, 18], "float32") + v * np.array([14, 10, 8], "float32")
for cx_, cy_, rad_, col_, k_ in ((540, 760, 820, (200, 140, 50), 0.32), (900, 300, 600, (60, 90, 160), 0.30)):
    d_ = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2) / rad_
    bg += (np.clip(1 - d_, 0, 1) ** 2)[..., None] * np.array(col_, "float32") * k_
bg *= np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)) ** 2.2, 0.3, 1)[..., None]
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
DUST = [glow_dot((255, 205, 120), 6), glow_dot((230, 170, 90), 5)]
_rg = random.Random(8)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H), _rg.uniform(30, 90), _rg.uniform(0, 6.28), _rg.choice([0, 1])) for _ in range(50)]

EMBLEMA = Image.open(f"{HERE}/assets/marca/emblema_rojo.png").convert("RGBA")
EMBLEMA = EMBLEMA.resize((520, round(520 * EMBLEMA.height / EMBLEMA.width)), Image.LANCZOS)
EMB_G = glow_dot((255, 40, 50), 130)

T_TIME = title_sprite("LÍNEA DE TIEMPO · ESQUEMÁTICA")
T_SRC = title_sprite("¿DE DÓNDE SALE LA NOTICIA?")
S_ILU = S("ESQUEMA ILUSTRATIVO", B7, 32, fill=(210, 220, 235), shadow=(0, 3, 2, 0.9))
S_EVI = S("EVIDENCIA CRISTIANA MÁS ANTIGUA", B7, 58, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))
S_ALP = S("AL NORTE DE LOS ALPES", B7, 54, fill=AMBER, shadow=(0, 4, 3, 0.9))
S_RANGO, _, _ = rtext("230–270 d. C.", ANTON, 130, grad=GOLD, stroke=6, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.7))
S_ANIOS = {}


def pill(txt, col=SILVER):
    sp = rrect(840, 118, (14, 34, 58), (8, 20, 36), 22)
    ImageDraw.Draw(sp).rounded_rectangle((0, 0, 839, 117), radius=22, outline=col + (255,), width=4)
    t = S(txt, B7, 52, fill=(255, 255, 255), shadow=(0, 3, 2, 0.6))
    if t.width > 780:
        t = t.resize((780, round(t.height * 780 / t.width)), Image.LANCZOS)
    sp.alpha_composite(t, (30, (118 - t.height) // 2))
    return sp


PILL_X, PILL_AOL = pill("PUBLICACIONES EN REDES (X)"), pill("ARTÍCULO DE AOL")
S_FALTA = S("FALTA: EL ESTUDIO CIENTÍFICO COMPLETO", B7, 46, fill=AMBER, shadow=(0, 4, 3, 0.9))
STAMP_PC = make_stamp("POR CONTRASTAR", RED, 92)


def background(t, dim):
    cv = BG.copy()
    for x0, y0, sp, ph, c in PARTS:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(ph + t * 0.8)
        a = 0.2 + 0.25 * math.sin(ph * 3 + t * 2.4)
        s = DUST[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * max(a, 0))))
    return cv


# ------------------------------------------------------------------ escenas con panel (5 y 6)
def timeline(cv, t):
    a, ain = C.sw(t, 5)
    if a <= 0:
        return
    panel(cv, a, T_TIME)
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    x0, x1, ya = 140, 940, 740
    xs = lambda yr: x0 + (x1 - x0) * yr / 2026
    p_ax = e_out(prog(t, C.SC_T[5][0] + 0.2, C.SC_T[5][0] + 1.0))
    d.line((x0, ya, x0 + (x1 - x0) * p_ax, ya), fill=SILVER + (255,), width=8)
    for yr in (0, 500, 1000, 1500, 2000):
        d.line((xs(yr), ya - 16, xs(yr), ya + 16), fill=SILVER + (int(255 * p_ax),), width=5)
    t_a = C.wd(5, "doscientos")
    t_b = C.wd(5, "setenta")
    pm = e_back(prog(t, t_a, t_a + 0.45), 1.7)
    if pm > 0:
        wseg = max(18, xs(270) - xs(230))
        grow = e_out(prog(t, t_a, t_b + 0.2))
        d.rounded_rectangle((xs(230) - 6, ya - 30, xs(230) + wseg * (0.4 + 0.6 * grow) + 6, ya + 30), radius=10, fill=AMBER + (255,))
        d.line((xs(250), ya - 34, xs(250), ya - 130 * clamp(pm)), fill=AMBER + (255,), width=6)
    comp(cv, lay, a)
    for yr, lab in ((0, "AÑO 0"), (2000, "HOY")):
        sp = S(lab, B6, 40, fill=(190, 205, 225))
        blit(cv, sp, xs(yr) if yr else xs(yr) + 40, ya + 62, alpha=a * p_ax)
    blit(cv, S_ILU, 540, 1170, alpha=a * 0.8)
    pe = e_back(prog(t, C.wd(5, "evidencia"), C.wd(5, "evidencia") + 0.4), 1.5)
    blit(cv, S_EVI, 540, 400, scale=0.9 + 0.1 * clamp(pe), alpha=a * clamp(pe * 2))
    pa = e_back(prog(t, C.wd(5, "alpes"), C.wd(5, "alpes") + 0.4), 1.5)
    blit(cv, S_ALP, 540, 480, scale=0.9 + 0.1 * clamp(pa), alpha=a * clamp(pa * 2))
    pr = e_back(prog(t, t_a + 0.1, t_a + 0.6), 1.7)
    blit(cv, S_RANGO, 540, 580, scale=0.85 + 0.15 * clamp(pr), alpha=a * clamp(pr * 2))
    ps = e_back(prog(t, t_b + 0.3, t_b + 0.8), 1.6)
    if ps > 0:
        yrs = round(1756 * e_out(prog(t, t_b + 0.3, t_b + 1.4)) / 100) * 100
        sp = S(f"+{yrs:,}".replace(",", ".") + " AÑOS", ANTON, 120, fill=(255, 255, 255), shadow=(0, 8, 6, 0.8))
        blit(cv, sp, 540, 930, scale=0.9 + 0.1 * clamp(ps), alpha=a * clamp(ps * 2))


def fuentes(cv, t):
    a, ain = C.sw(t, 6)
    if a <= 0:
        return
    panel(cv, a, T_SRC)
    for sp, word, y in ((PILL_X, "redes", 470), (PILL_AOL, "medios", 620)):
        tw = C.wd(6, word)
        p = e_back(prog(t, tw, tw + 0.4), 1.4)
        if p > 0:
            blit(cv, sp, 540 - 160 * (1 - clamp(p)), y, scale=1.0, alpha=a * clamp(p * 2))
    tc = C.wd(6, "contrastarla")
    p = e_back(prog(t, tc, tc + 0.4), 2.0)
    if p > 0:
        sx, sy = shake(t, tc + 0.1, 10, 9)
        blit(cv, STAMP_PC, 540 + sx, 860 + sy, scale=0.7 + 0.3 * clamp(p), rot=-5, alpha=a * clamp(p * 2))
    tp = C.wd(6, "publicación")
    pf = e_out(prog(t, tp, tp + 0.4))
    blit(cv, S_FALTA, 540, 1080, alpha=a * pf)


# ------------------------------------------------------------------ cierre: emblema sobre la foto
def emblema(t_in, t_out):
    def f(cv, t):
        p = e_back(prog(t, t_in, t_in + 0.5), 1.8)
        a = clamp(p * 2) * (1 - e_out(prog(t, t_out - 0.15, t_out)))
        if a > 0.01:
            beat = 1 + 0.02 * math.sin((t - t_in) * 5)
            blit(cv, EMB_G, 540, 600, scale=3.4 * beat * clamp(p), alpha=0.6 * a)
            blit(cv, EMBLEMA, 540, 600, scale=beat * (0.6 + 0.4 * clamp(p)), alpha=a)
    return f


def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0
    A = f"{HERE_S}/assets"
    SC = ctx.SC_T
    ILU = "IMAGEN ILUSTRATIVA"
    CT = "REPRESENTACIÓN ILUSTRATIVA · LOS SIGNOS NO SON LA INSCRIPCIÓN REAL"

    def sfx(sput, ctx):
        sput(riser(0.3), 0.0, 0.5)
        sput(hit(70, 1.2, 0.8), 0.27, 1.0)
        sput(whoosh(0.5, True, 2), 0.25, 0.5)
        for i in range(1, 8):
            sput(whoosh(0.45, True, 10 + i), SC[i][0] - 0.1, 0.45)
            sput(hit(100, 0.5, 0.3), SC[i][0] + 0.12, 0.45)
        sput(hit(80, 0.9, 0.8), wd(0, "setecientos") + 0.1, 0.9)
        sput(blip(1300), wd(1, "fráncfort"), 0.5)
        sput(ping(), wd(1, "dos") + 0.3, 0.6)
        sput(sweep(3.0), wd(2, "tomografía") - 0.1, 0.5)
        sput(hit(70, 0.9, 0.9), wd(3, "dieciocho") + 0.1, 1.0)
        sput(blip(1100, 0.12), wd(3, "latín"), 0.6)
        sput(thump(0.9), wd(4, "santo") - 0.2, 0.7)
        sput(hit(75, 0.9, 0.7), wd(4, "doblad") + 0.1, 0.8)
        sput(riser(1.0), wd(5, "doscientos") - 1.0, 0.45)
        sput(hit(70, 1.0, 0.9), wd(5, "setenta") + 0.3, 1.0)
        sput(hit(65, 1.0, 0.8), wd(6, "contrastarla") + 0.1, 0.9)
        sput(riser(1.0), wd(7, "diecisiete") - 1.0, 0.5)
        sput(hit(70, 1.0, 0.9), wd(7, "diecisiete") + 0.2, 1.0)
        sput(ping(), wd(7, "síguenos") + 0.35, 0.9)

    t_asi, t_esc = wd(2, "así") - 0.1, wd(3, "escrita") - 0.15
    bleed = [
        # 0 · gancho
        photo_bleed(f"{A}/portada.webp", 0.0, SC[0][1] + 0.1, z0=1.02, z1=1.2, fx=0.42, fy=0.45, tag=ILU),
        caption("AMULETO DE PLATA", wd(0, "amuleto"), SC[0][1], y=980, col=AMBER),
        caption("MÁS DE 1.700 AÑOS", wd(0, "mil"), SC[0][1], y=1085),
        # 1 · clip del amuleto sobre la tierra
        video_bleed(f"{A}/clip_gemini.mp4", SC[1][0] + 0.05, SC[1][1] + 0.1, 0.0, pan=(0.35, 0.6), tag=ILU),
        caption("FRÁNCFORT, ALEMANIA", wd(1, "fráncfort"), SC[1][1], y=930, col=AMBER),
        caption("ANTIGUO CEMENTERIO ROMANO", wd(1, "antiguo"), SC[1][1], y=1025),
        caption("AÑO 2018", wd(1, "dos"), SC[1][1], y=1125, col=AMBER),
        # 2 · excavación y tomografía
        video_bleed(f"{A}/clip_gemini.mp4", SC[2][0] + 0.05, t_asi, 5.0, pan=(0.3, 0.5), tag=ILU),
        video_bleed(f"{A}/clip_gemini.mp4", t_asi, SC[2][1] + 0.1, 9.0, pan=(0.4, 0.6), tag=CT),
        caption("TAN FRÁGIL...", wd(2, "frágil"), t_asi + 0.15, y=1000, col=AMBER),
        caption("TOMOGRAFÍA (TC)", wd(2, "tomografía"), SC[2][1], y=1000, col=AMBER),
        # 3 · la inscripción
        video_bleed(f"{A}/clip_gemini.mp4", SC[3][0] + 0.05, t_esc, 15.0, pan=(0.4, 0.55), tag=CT),
        video_bleed(f"{A}/clip_gemini.mp4", t_esc, SC[3][1] + 0.1, 3.0, pan=(0.4, 0.6), tag=CT),
        caption("18 LÍNEAS", wd(3, "dieciocho"), SC[3][1], y=980, col=AMBER),
        caption("EN LATÍN", wd(3, "latín"), SC[3][1], y=1090),
        # 4 · las frases
        photo_bleed(f"{A}/portada.webp", SC[4][0] + 0.05, SC[4][1] + 0.1, z0=1.25, z1=1.05, fx=0.35, fy=0.5, tag=ILU),
        caption("«SANTO, SANTO, SANTO»", wd(4, "santo"), SC[4][1], y=980, col=AMBER),
        caption("«DOBLAD VUESTRAS RODILLAS»", wd(4, "doblad"), SC[4][1], y=1085),
        # 7 · cierre
        photo_bleed(f"{A}/portada.webp", SC[7][0] + 0.05, ctx.DUR + 1, z0=1.1, z1=1.0, fx=0.5, fy=0.55, tag=ILU),
        caption("MÁS DE 17 SIGLOS", wd(7, "diecisiete"), ctx.DUR + 1, y=1000, col=AMBER),
        emblema(wd(7, "síguenos") - 0.25, ctx.DUR + 1),
    ]
    impacts = [0.30, wd(0, "setecientos") + 0.1, wd(3, "dieciocho") + 0.1, wd(4, "doblad") + 0.1, wd(5, "setenta") + 0.3, wd(6, "contrastarla") + 0.1, wd(7, "diecisiete") + 0.2]
    flashes = [(0.27, 0.9), (wd(3, "dieciocho") + 0.1, 0.25)]
    return Spec(background, [timeline, fuentes], impacts=impacts, flashes=flashes, sfx=sfx, bleed=bleed)
