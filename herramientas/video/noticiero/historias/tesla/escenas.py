"""Historia: el Tesla Roadster "vuela" sobre una fila de vehículos en su presentación (15 oct 2026, Texas).

Short de ~48 s. La nota de Robert News se apoya solo en un post de Polymarket en X; los datos del guion se contrastaron con
CNN, TechCrunch y Fox Business (salto sobre Model 3/Y, Cybertruck, Cybercab y Semi; propulsores de aire comprimido; sin conductor;
0-60 mph en 0,81 s según un medio; producción en 2028; versión voladora sin homologar).
Fotos: imagen de la presentación enviada por el usuario. Clip: generado con IA (se rotula "ILUSTRATIVO").
Escenas: foto de gancho · lista de vehículos (panel) · foto de la vuelta · clip de propulsores · foto sin conductor ·
cifras (panel) · "ojo" (panel) · cierre con foto lateral.
"""
import math
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec, photo_bleed, video_bleed, caption

C = None
HERE_S = os.path.dirname(os.path.abspath(__file__))
SILVER = (205, 215, 230)
CYAN = (90, 200, 255)

yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([6, 8, 18], "float32") + v * np.array([16, 8, 12], "float32")
for cx_, cy_, rad_, col_, k_ in ((540, 760, 820, (200, 40, 50), 0.28), (200, 300, 600, (50, 90, 190), 0.32)):
    d_ = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2) / rad_
    bg += (np.clip(1 - d_, 0, 1) ** 2)[..., None] * np.array(col_, "float32") * k_
bg *= np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)) ** 2.2, 0.3, 1)[..., None]
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
DUST = [glow_dot((255, 120, 120), 6), glow_dot((120, 180, 255), 5)]
_rg = random.Random(5)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H), _rg.uniform(30, 90), _rg.uniform(0, 6.28), _rg.choice([0, 1])) for _ in range(50)]

T_SALTO = title_sprite("SOBRE QUÉ SALTÓ")
T_CIF = title_sprite("LAS CIFRAS (SEGÚN MEDIOS)")
T_OJO = title_sprite("OJO")
S_TX = S("PRESENTACIÓN EN TEXAS · 15 OCT 2026", B7, 40, fill=(190, 205, 225), shadow=(0, 3, 2, 0.8))
S_060 = S("DE 0 A 60 MILLAS POR HORA", B7, 54, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))
S_PROD = S("PRODUCCIÓN PREVISTA", B7, 54, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))
S_NOTA = S("Cifras reportadas por medios; sin verificación independiente", B6, 34, fill=(170, 185, 205), shadow=(0, 3, 2, 0.8))
S_FALTA = S("FALTA VER SI VUELA PARA LOS DUEÑOS", B7, 50, fill=AMBER, shadow=(0, 4, 3, 0.9))
STAMP_NA = make_stamp("NO APROBADO PARA LA CALLE", RED, 80)


def pill(txt, col=CYAN):
    sp = rrect(840, 110, (14, 30, 56), (8, 18, 34), 22)
    ImageDraw.Draw(sp).rounded_rectangle((0, 0, 839, 109), radius=22, outline=col + (255,), width=4)
    t = S(txt, B7, 56, fill=(255, 255, 255), shadow=(0, 3, 2, 0.6))
    sp.alpha_composite(t, (34, (110 - t.height) // 2))
    return sp


PILLS = [pill(x) for x in ("MODEL 3", "MODEL Y", "CYBERTRUCK", "CYBERCAB")] + [pill("CAMIÓN SEMI")]


def background(t, dim):
    cv = BG.copy()
    for x0, y0, sp, ph, c in PARTS:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(ph + t * 0.8)
        a = 0.2 + 0.25 * math.sin(ph * 3 + t * 2.4)
        s = DUST[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * max(a, 0))))
    return cv


def vehiculos(cv, t):
    a, ain = C.sw(t, 1)
    if a <= 0:
        return
    panel(cv, a, T_SALTO)
    ts = [C.wd(1, "model"), None, C.wd(1, "cybertruck"), C.wd(1, "cybercab"), C.wd(1, "semi")]
    ts[1] = (ts[0] + ts[2]) / 2
    for i, (sp, tw) in enumerate(zip(PILLS, ts)):
        p = e_back(prog(t, tw - 0.1, tw + 0.35), 1.4)
        if p > 0:
            blit(cv, sp, 540 - 180 * (1 - clamp(p)), 430 + 130 * i, alpha=a * clamp(p * 2))
    pt = e_out(prog(t, C.wd(1, "texas"), C.wd(1, "texas") + 0.4))
    blit(cv, S_TX, 540, 1130, alpha=a * pt)


def cifras(cv, t):
    a, ain = C.sw(t, 5)
    if a <= 0:
        return
    panel(cv, a, T_CIF)
    t1 = C.wd(5, "sesenta")
    p1 = e_out(prog(t, t1 - 0.2, t1 + 0.3))
    blit(cv, S_060, 540, 420, alpha=a * p1)
    t2 = C.wd(5, "ochenta")
    val = 0.81 * e_out(prog(t, t2 - 0.9, t2 + 0.5))
    n = S(f"{val:.2f}".replace(".", ",") + " s", ANTON, 250, fill=(255, 220, 90), shadow=(0, 10, 8, 0.85))
    pn = e_back(prog(t, t1, t1 + 0.5), 1.4)
    blit(cv, n, 540, 600, scale=0.85 + 0.15 * clamp(pn), alpha=a * clamp(pn * 2))
    t3 = C.wd(5, "producirá")
    p3 = e_out(prog(t, t3 - 0.2, t3 + 0.3))
    blit(cv, S_PROD, 540, 850, alpha=a * p3)
    t4 = C.wd(5, "veintiocho")
    p4 = e_back(prog(t, t4 - 0.1, t4 + 0.4), 1.6)
    n2 = S("2028", ANTON, 230, fill=(255, 255, 255), shadow=(0, 10, 8, 0.85))
    blit(cv, n2, 540, 1010, scale=0.85 + 0.15 * clamp(p4), alpha=a * clamp(p4 * 2))
    blit(cv, S_NOTA, 540, 1160, alpha=a * 0.9)


def ojo(cv, t):
    a, ain = C.sw(t, 6)
    if a <= 0:
        return
    panel(cv, a, T_OJO)
    ts = C.wd(6, "aprobada")
    p = e_back(prog(t, ts - 0.2, ts + 0.3), 2.0)
    if p > 0:
        sx, sy = shake(t, ts + 0.1, 10, 9)
        blit(cv, STAMP_NA, 540 + sx, 640 + sy, scale=0.7 + 0.3 * clamp(p), rot=-4, alpha=a * clamp(p * 2))
    tf = C.wd(6, "falta")
    pf = e_out(prog(t, tf, tf + 0.4))
    blit(cv, S_FALTA, 540, 960, alpha=a * pf)


def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0
    A = f"{HERE_S}/assets"
    SC = ctx.SC_T
    REF = "IMAGEN DE REFERENCIA"
    ILU = "CLIP ILUSTRATIVO (IA): NO ES EL VEHÍCULO REAL"

    def sfx(sput, ctx):
        sput(riser(0.3), 0.0, 0.5)
        sput(hit(70, 1.2, 0.8), 0.27, 1.0)
        sput(whoosh(0.5, True, 2), 0.25, 0.5)
        for i in range(1, 8):
            sput(whoosh(0.45, True, 10 + i), SC[i][0] - 0.1, 0.45)
            sput(hit(100, 0.5, 0.3), SC[i][0] + 0.12, 0.45)
        sput(hit(80, 0.9, 0.8), wd(0, "vuela") + 0.1, 0.9)
        sput(riser(0.9), wd(0, "saltó") - 0.8, 0.5)
        for w in ("model", "cybertruck", "cybercab", "semi"):
            sput(blip(1100 + 150 * ("model cybertruck cybercab semi".split().index(w)), 0.1), wd(1, w), 0.5)
        sput(whoosh(0.8, True, 5), wd(2, "vuelta") - 0.1, 0.6)
        sput(hit(70, 0.9, 0.9), wd(2, "aterrizar") + 0.1, 0.8)
        sput(rumble(2.0), wd(3, "propulsores") - 0.1, 0.6)
        sput(hit(75, 0.9, 0.8), wd(4, "nadie") + 0.1, 0.9)
        sput(thump(0.9), wd(5, "sesenta") - 0.2, 0.7)
        sput(hit(70, 1.0, 0.9), wd(5, "ochenta") + 0.3, 1.0)
        sput(hit(65, 1.0, 0.8), wd(6, "aprobada") + 0.1, 0.9)
        sput(riser(1.0), wd(7, "futuro") - 0.6, 0.5)
        sput(hit(70, 1.0, 0.9), wd(7, "espectáculo") + 0.2, 1.0)
        sput(ping(), wd(7, "síguenos") + 0.35, 0.9)

    s1, s2, s3, s4, s7 = SC[1], SC[2], SC[3], SC[4], SC[7]
    bleed = [
        photo_bleed(f"{A}/vuelo.jpg", 0.0, SC[0][1] + 0.1, z0=1.0, z1=1.25, fx=0.58, fy=0.3, tag=REF),
        caption("¿UN AUTO QUE VUELA?", wd(0, "vuela"), SC[0][1], y=960, col=AMBER),
        caption("EN VIVO", wd(0, "vivo"), SC[0][1], y=1065),
        photo_bleed(f"{A}/vuelo.jpg", s2[0] + 0.05, s2[1] + 0.1, z0=1.3, z1=1.0, fx=0.6, fy=0.28, tag=REF),
        caption("UNA VUELTA EN EL AIRE", wd(2, "vuelta"), s2[1], y=1010, col=AMBER),
        photo_bleed(f"{A}/vuelo.jpg", s3[0] + 0.05, s3[1] + 0.1, z0=1.0, z1=1.3, fx=0.3, fy=0.42, tag=REF),
        caption("PROPULSORES DE AIRE COMPRIMIDO", wd(3, "propulsores"), s3[1], y=1010, col=AMBER),
        photo_bleed(f"{A}/lateral.jpg", s4[0] + 0.05, s4[1] + 0.1, z0=1.0, z1=1.45, fx=0.62, fy=0.55, tag=REF),
        caption("SIN CONDUCTOR", wd(4, "nadie"), s4[1], y=1010, col=AMBER),
        photo_bleed(f"{A}/lateral.jpg", s7[0] + 0.05, ctx.DUR + 1, z0=1.25, z1=1.02, fx=0.6, fy=0.55, tag=REF),
        caption("¿FUTURO O ESPECTÁCULO?", wd(7, "futuro"), ctx.DUR + 1, y=1000, col=AMBER),
    ]
    impacts = [0.30, wd(0, "vuela") + 0.1, wd(2, "aterrizar") + 0.1, wd(4, "nadie") + 0.1, wd(5, "ochenta") + 0.3, wd(6, "aprobada") + 0.1, wd(7, "espectáculo") + 0.2]
    flashes = [(0.27, 0.9), (wd(2, "vuelta") + 0.0, 0.25)]
    return Spec(background, [vehiculos, cifras, ojo], impacts=impacts, flashes=flashes, sfx=sfx, bleed=bleed)
