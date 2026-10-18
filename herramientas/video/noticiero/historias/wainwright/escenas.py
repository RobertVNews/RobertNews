"""Historia: explosión e incendio en la base CFB Wainwright (Alberta, Canadá), 17 oct 2026. Noticia de última hora y tono sobrio.

Verificado con Global News (y búsqueda: CBC, CNN, Globe and Mail): hubo muertos y heridos (confirmado por el ministro de Defensa,
David McGuinty, sin cifras); "al menos siete muertos y decenas de heridos" según fuentes militares anónimas; varios hospitales de Alberta
en código naranja; causa NO confirmada (fuentes militares: ejercicio de tiro real contra una línea/pozo de gas); el fuego cruzó la cerca
de la base y hacia medianoche estaba contenido (municipio). Cifras mayores que circulan ("decenas de muertos, cientos de heridos")
NO están verificadas y el Short lo dice. Las imágenes (enviadas por el usuario) son ilustraciones de IA y se rotulan como tales.
Escenas: foto · cita del ministro (panel) · confirmado/sin confirmar (panel) · código naranja (panel) · foto (causa) · foto (incendio) · aviso (panel) · cierre.
"""
import math
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec, photo_bleed, caption

C = None
HERE_S = os.path.dirname(os.path.abspath(__file__))
ORANGE = (255, 140, 30)
GREEN = (90, 220, 150)

yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([8, 6, 10], "float32") + v * np.array([22, 8, 6], "float32")
for cx_, cy_, rad_, col_, k_ in ((540, 1100, 900, (230, 90, 20), 0.34), (300, 300, 600, (60, 70, 120), 0.25)):
    d_ = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2) / rad_
    bg += (np.clip(1 - d_, 0, 1) ** 2)[..., None] * np.array(col_, "float32") * k_
bg *= np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)) ** 2.2, 0.3, 1)[..., None]
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
DUST = [glow_dot((255, 140, 60), 6), glow_dot((200, 120, 90), 5)]
_rg = random.Random(3)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H), _rg.uniform(30, 90), _rg.uniform(0, 6.28), _rg.choice([0, 1])) for _ in range(50)]

T_DEF = title_sprite("MINISTRO DE DEFENSA DE CANADÁ")
T_CON = title_sprite("¿QUÉ ESTÁ CONFIRMADO?")
T_COD = title_sprite("HOSPITALES DE ALBERTA")
T_IA = title_sprite("AVISO")
S_NAME = S("DAVID McGUINTY", B7, 54, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))
S_NOCIF = S("SIN DAR CIFRAS", B7, 50, fill=AMBER, shadow=(0, 4, 3, 0.9))
S_FALTA = S("NADIE HA VERIFICADO CIFRAS MAYORES", B7, 46, fill=AMBER, shadow=(0, 4, 3, 0.9))
S_QUOTE = [S("«UNA SITUACIÓN", ANTON, 100, fill=(255, 255, 255), shadow=(0, 8, 6, 0.85)),
           S("MUY ACTIVA", ANTON, 100, fill=(255, 255, 255), shadow=(0, 8, 6, 0.85)),
           S("Y DELICADA»", ANTON, 100, fill=(255, 255, 255), shadow=(0, 8, 6, 0.85))]
STAMP_IA = make_stamp("ILUSTRACIONES CON IA", RED, 78)
STAMP_ORA, _, _ = rtext("CÓDIGO NARANJA", ANTON, 130, fill=ORANGE, stroke=5, stroke_col=(60, 20, 0), glow=((255, 130, 20), 20, 0.7), shadow=(0, 8, 6, 0.8))
S_VICT = S("PROTOCOLO PARA VÍCTIMAS MASIVAS", B7, 50, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))


def block(title, body, col, h=250):
    sp = rrect(860, h, (14, 22, 36), (8, 14, 24), 22)
    ImageDraw.Draw(sp).rounded_rectangle((0, 0, 859, h - 1), radius=22, outline=col + (255,), width=5)
    t = S(title, B7, 46, fill=col, shadow=(0, 3, 2, 0.6))
    sp.alpha_composite(t, (34, 20))
    for i, line in enumerate(body):
        b = S(line, B7, 58, fill=(255, 255, 255), shadow=(0, 3, 2, 0.6))
        if b.width > 800:
            b = b.resize((800, round(b.height * 800 / b.width)), Image.LANCZOS)
        sp.alpha_composite(b, (34, 88 + 66 * i))
    return sp


BLK_OFI = block("CONFIRMADO OFICIALMENTE", ["HAY MUERTOS Y HERIDOS", "(SIN CIFRAS)"], GREEN)
BLK_ANO = block("FUENTES MILITARES ANÓNIMAS", ["AL MENOS 7 MUERTOS", "DECENAS DE HERIDOS"], AMBER)


def background(t, dim):
    cv = BG.copy()
    for x0, y0, sp, ph, c in PARTS:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(ph + t * 0.8)
        a = 0.2 + 0.25 * math.sin(ph * 3 + t * 2.4)
        s = DUST[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * max(a, 0))))
    return cv


def ministro(cv, t):
    a, ain = C.sw(t, 1)
    if a <= 0:
        return
    panel(cv, a, T_DEF)
    t0 = C.wd(1, "situación")
    for i, sp in enumerate(S_QUOTE):
        p = e_out(prog(t, t0 + 0.25 * i - 0.1, t0 + 0.25 * i + 0.4))
        blit(cv, sp, 540, 540 + 125 * i + 24 * (1 - p), alpha=a * p)
    pn = e_out(prog(t, C.wd(1, "ministro"), C.wd(1, "ministro") + 0.4))
    blit(cv, S_NAME, 540, 930, alpha=a * pn)
    pc = e_out(prog(t, C.wd(1, "cifras"), C.wd(1, "cifras") + 0.4))
    blit(cv, S_NOCIF, 540, 1040, alpha=a * pc)


def confirmado(cv, t):
    a, ain = C.sw(t, 2)
    if a <= 0:
        return
    panel(cv, a, T_CON)
    t1 = C.wd(2, "fuentes")
    p1 = e_back(prog(t, C.l0(2) + 0.1, C.l0(2) + 0.6), 1.3)
    blit(cv, BLK_OFI, 540 - 160 * (1 - clamp(p1)), 520, alpha=a * clamp(p1 * 2))
    p2 = e_back(prog(t, t1 - 0.1, t1 + 0.4), 1.3)
    blit(cv, BLK_ANO, 540 - 160 * (1 - clamp(p2)), 830, alpha=a * clamp(p2 * 2))


def codigo(cv, t):
    a, ain = C.sw(t, 3)
    if a <= 0:
        return
    panel(cv, a, T_COD)
    tc = C.wd(3, "código")
    p = e_back(prog(t, tc - 0.1, tc + 0.45), 1.8)
    pulse = 1 + 0.03 * math.sin((t - tc) * 6) * (t > tc + 0.5)
    blit(cv, STAMP_ORA, 540, 600, scale=(0.7 + 0.3 * clamp(p)) * pulse, alpha=a * clamp(p * 2))
    tp = C.wd(3, "protocolo")
    pp = e_out(prog(t, tp, tp + 0.4))
    blit(cv, S_VICT, 540, 860, alpha=a * pp)


def aviso(cv, t):
    a, ain = C.sw(t, 6)
    if a <= 0:
        return
    panel(cv, a, T_IA)
    ts = C.wd(6, "ilustraciones")
    p = e_back(prog(t, ts - 0.1, ts + 0.4), 1.9)
    if p > 0:
        sx, sy = shake(t, ts + 0.1, 8, 9)
        blit(cv, STAMP_IA, 540 + sx, 640 + sy, scale=0.7 + 0.3 * clamp(p), rot=-4, alpha=a * clamp(p * 2))
    tf = C.wd(6, "circulan")
    pf = e_out(prog(t, tf, tf + 0.4))
    blit(cv, S_FALTA, 540, 960, alpha=a * pf)


def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0
    A = f"{HERE_S}/assets"
    SC = ctx.SC_T
    IA = "ILUSTRACIÓN CON IA · NO ES UNA FOTO DEL INCIDENTE"

    def sfx(sput, ctx):
        sput(whoosh(0.5, True, 2), 0.25, 0.4)
        sput(hit(60, 1.2, 0.5), 0.3, 0.6)
        for i in range(1, 8):
            sput(whoosh(0.45, True, 10 + i), SC[i][0] - 0.1, 0.35)
        sput(blip(900, 0.12), wd(1, "situación"), 0.4)
        sput(thump(0.8), wd(2, "siete") - 0.1, 0.7)
        sput(ping(), wd(3, "código") + 0.1, 0.6)
        sput(hit(60, 1.0, 0.5), wd(4, "causa") + 0.1, 0.6)
        sput(rumble(2.0), wd(5, "vientos") - 0.1, 0.5)
        sput(hit(60, 1.0, 0.5), wd(6, "ilustraciones") + 0.1, 0.6)
        sput(ping(), wd(7, "síguenos") + 0.35, 0.7)

    bleed = [
        photo_bleed(f"{A}/fuego2.webp", 0.0, SC[0][1] + 0.1, z0=1.0, z1=1.2, fx=0.5, fy=0.45, tag=IA),
        caption("BASE WAINWRIGHT, ALBERTA", wd(0, "wainwright"), SC[0][1], y=960, col=AMBER),
        caption("EXPLOSIÓN E INCENDIO", wd(0, "explosión"), SC[0][1], y=1065),
        photo_bleed(f"{A}/fuego1.webp", SC[4][0] + 0.05, SC[4][1] + 0.1, z0=1.0, z1=1.25, fx=0.5, fy=0.6, tag=IA),
        caption("CAUSA: SIN CONFIRMAR", wd(4, "causa"), SC[4][1], y=960, col=AMBER),
        caption("¿UN POZO DE GAS?", wd(4, "pozo"), SC[4][1], y=1065),
        photo_bleed(f"{A}/fuego2.webp", SC[5][0] + 0.05, SC[5][1] + 0.1, z0=1.25, z1=1.0, fx=0.5, fy=0.3, tag=IA),
        caption("VIENTOS FUERTES", wd(5, "vientos"), SC[5][1], y=960, col=AMBER),
        caption("CONTENIDO A MEDIANOCHE", wd(5, "medianoche"), SC[5][1], y=1065),
        photo_bleed(f"{A}/fuego1.webp", SC[7][0] + 0.05, ctx.DUR + 1, z0=1.1, z1=1.0, fx=0.5, fy=0.55, tag=IA),
        caption("SEGUIREMOS INFORMANDO", wd(7, "seguiremos"), ctx.DUR + 1, y=1000, col=AMBER),
    ]
    impacts = [0.30, wd(2, "siete") + 0.1, wd(3, "código") + 0.1, wd(4, "causa") + 0.1, wd(6, "ilustraciones") + 0.1]
    return Spec(background, [ministro, confirmado, codigo, aviso], impacts=impacts, flashes=[(0.27, 0.5)], sfx=sfx, bleed=bleed)
