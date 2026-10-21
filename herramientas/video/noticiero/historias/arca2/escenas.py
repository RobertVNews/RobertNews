"""Historia: Arca de Noé, parte 2 (lo que marcó el georradar). Usa el texto de la nota de Robert News sin contrastar (instrucción del usuario).
Fotos del usuario (aérea de Durupınar, equipo con muestras) y una imagen ilustrativa de laboratorio, a pantalla completa.
Escenas: foto aérea · foto de muestras · panel "sin roca" · radar (panel) · foto lab · sin confirmar (panel) · cierre."""
import math
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec, photo_bleed, caption

C = None
HERE_S = os.path.dirname(os.path.abspath(__file__))
SOIL = (190, 140, 80)

yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([8, 7, 5], "float32") + v * np.array([22, 12, 6], "float32")
for cx_, cy_, rad_, col_, k_ in ((540, 760, 820, (200, 140, 50), 0.34), (900, 300, 600, (90, 120, 80), 0.25)):
    d_ = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2) / rad_
    bg += (np.clip(1 - d_, 0, 1) ** 2)[..., None] * np.array(col_, "float32") * k_
bg *= np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)) ** 2.2, 0.3, 1)[..., None]
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
DUST = [glow_dot((255, 205, 120), 6), glow_dot((230, 170, 90), 5)]
_rg = random.Random(12)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H), _rg.uniform(30, 90), _rg.uniform(0, 6.28), _rg.choice([0, 1])) for _ in range(50)]

T_SUELO = title_sprite("QUÉ DIJO UNO DE SUS LÍDERES")
T_RADAR = title_sprite("LO QUE MARCÓ EL GEORRADAR")
T_CONF = title_sprite("¿ESTÁ CONFIRMADO?")
S_NOROCA, _, _ = rtext("NO HAY ROCA SÓLIDA", ANTON, 120, grad=WHITE, stroke=5, stroke_col=(40, 20, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.8))
S_SOLO = S("SOLO CAPAS DE TIERRA", B7, 66, fill=AMBER, shadow=(0, 4, 3, 0.9))
S_NOTA = S("LECTURAS DE RADAR, NO FOTOS", B7, 40, fill=(210, 220, 235), shadow=(0, 3, 2, 0.8))
S_REC = S("LÍNEAS RECTAS", B7, 56, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))
S_CAV = S("CAVIDADES", B7, 56, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))
S_NIV = [S(f"NIVEL {k}", B7, 50, fill=AMBER, shadow=(0, 4, 3, 0.9)) for k in (1, 2, 3)]
STAMP_SC = make_stamp("SIN CONFIRMAR", RED, 100)
S_BARCO = S("CAMBIOS EN LA TIERRA ≠ UN BARCO".replace("≠", "NO PRUEBAN"), B7, 52, fill=AMBER, shadow=(0, 4, 3, 0.9))


def background(t, dim):
    cv = BG.copy()
    for x0, y0, sp, ph, c in PARTS:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(ph + t * 0.8)
        a = 0.2 + 0.25 * math.sin(ph * 3 + t * 2.4)
        s = DUST[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * max(a, 0))))
    return cv


def sinroca(cv, t):
    a, ain = C.sw(t, 2)
    if a <= 0:
        return
    panel(cv, a, T_SUELO)
    t0 = C.wd(2, "roca")
    p = e_back(prog(t, t0 - 0.2, t0 + 0.4), 1.6)
    blit(cv, S_NOROCA, 540, 560, scale=0.8 + 0.2 * clamp(p), alpha=a * clamp(p * 2))
    # capas de tierra
    t1 = C.wd(2, "capas")
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    for k in range(6):
        pk = e_out(prog(t, t1 - 0.2 + 0.12 * k, t1 + 0.35 + 0.12 * k))
        y = 760 + 55 * k
        col = (int(SOIL[0] - 12 * k), int(SOIL[1] - 12 * k), int(SOIL[2] - 8 * k), int(255 * pk))
        d.rounded_rectangle((150, y, 150 + 780 * pk, y + 46), radius=10, fill=col)
    comp(cv, lay, a)
    ps = e_out(prog(t, t1, t1 + 0.4))
    blit(cv, S_SOLO, 540, 1130, alpha=a * ps)


def radar(cv, t):
    a, ain = C.sw(t, 3)
    if a <= 0:
        return
    panel(cv, a, T_RADAR)
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((120, 400, 960, 1000), radius=18, outline=SOIL + (255,), width=4, fill=(40, 28, 16, 200))
    tl = C.wd(3, "líneas")
    for k, (wname, yy_) in enumerate((("líneas", 520), ("cavidades", 700), ("tres", 880))):
        tw = C.wd(3, wname)
        pk = e_out(prog(t, tw - 0.1, tw + 0.5))
        x1 = 160 + 760 * pk
        d.line((160, yy_, x1, yy_), fill=AMBER + (255,), width=7)
        if k == 1:
            for cx in (330, 560, 770):
                if pk > 0.8:
                    d.ellipse((cx - 38, yy_ + 24 - 18, cx + 38, yy_ + 24 + 18), outline=(255, 255, 255, 255), width=5)
    comp(cv, lay, a)
    for k, wname in enumerate(("líneas", "cavidades", "niveles")):
        tw = C.wd(3, wname)
        pk = e_out(prog(t, tw, tw + 0.35))
        sp = (S_REC, S_CAV, S_NIV[2])[k]
        blit(cv, sp, 540, (470, 650, 830)[k] - 0, alpha=a * pk)
    blit(cv, S_NOTA, 540, 1100, alpha=a * 0.9)


def confirmado(cv, t):
    a, ain = C.sw(t, 5)
    if a <= 0:
        return
    panel(cv, a, T_CONF)
    ts = C.wd(5, "confirmado")
    p = e_back(prog(t, ts - 0.1, ts + 0.45), 1.9)
    if p > 0:
        sx, sy = shake(t, ts + 0.1, 10, 9)
        blit(cv, STAMP_SC, 540 + sx, 620 + sy, scale=0.7 + 0.3 * clamp(p), rot=-4, alpha=a * clamp(p * 2))
    tg = C.wd(5, "geólogos")
    pg = e_out(prog(t, tg, tg + 0.4))
    blit(cv, S_BARCO, 540, 940, alpha=a * pg)


def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0
    A = f"{HERE_S}/assets"
    SC = ctx.SC_T
    REF, ILU = "IMAGEN DE REFERENCIA", "IMAGEN ILUSTRATIVA"

    def sfx(sput, ctx):
        sput(riser(0.3), 0.0, 0.5)
        sput(hit(70, 1.2, 0.8), 0.27, 1.0)
        sput(whoosh(0.5, True, 2), 0.25, 0.5)
        for i in range(1, 7):
            sput(whoosh(0.45, True, 10 + i), SC[i][0] - 0.1, 0.45)
            sput(hit(100, 0.5, 0.3), SC[i][0] + 0.12, 0.45)
        sput(drill(1.8), l0(1) + 0.1, 0.5)
        sput(hit(70, 0.9, 0.9), wd(2, "roca") + 0.2, 1.0)
        sput(sweep(3.0), wd(3, "georradar"), 0.5)
        for k in range(3):
            sput(blip(900 + 200 * k, 0.12), wd(3, "líneas") + 0.5 * k, 0.55)
        sput(thump(0.9), wd(4, "madera") - 0.5, 0.8)
        sput(hit(70, 0.9, 0.9), wd(5, "confirmado") + 0.1, 0.9)
        sput(riser(1.0), wd(6, "leyenda") - 1.0, 0.5)
        sput(hit(70, 1.0, 0.9), wd(6, "descubrimiento") + 0.3, 1.0)
        sput(ping(), wd(6, "síguenos") + 0.35, 0.9)

    bleed = [
        photo_bleed(f"{A}/durupinar_aerea.jpg", 0.0, SC[0][1] + 0.1, z0=1.02, z1=1.2, fx=0.5, fy=0.5, tag=REF),
        caption("¿QUÉ HAY BAJO LA COLINA?", wd(0, "georradar"), SC[0][1], y=980, col=AMBER),
        photo_bleed(f"{A}/equipo_muestras.jpg", SC[1][0] + 0.05, SC[1][1] + 0.1, z0=1.0, z1=1.18, fx=0.5, fy=0.55, tag=REF),
        caption("CASI 20 METROS", wd(1, "veinte"), SC[1][1], y=960, col=AMBER),
        caption("+300 MUESTRAS", wd(1, "trescientas"), SC[1][1], y=1065),
        photo_bleed(f"{A}/laboratorio_ilustrativo.jpg", SC[4][0] + 0.05, SC[4][1] + 0.1, z0=1.0, z1=1.18, fx=0.45, fy=0.5, tag=ILU),
        caption("MÁS MATERIA ORGÁNICA", wd(4, "materia"), SC[4][1], y=960, col=AMBER),
        caption("¿MADERA DEL ARCA?", wd(4, "madera"), SC[4][1], y=1065),
        photo_bleed(f"{A}/durupinar_aerea.jpg", SC[6][0] + 0.05, ctx.DUR + 1, z0=1.2, z1=1.0, fx=0.5, fy=0.5, tag=REF),
        caption("¿LEYENDA O DESCUBRIMIENTO?", wd(6, "leyenda"), ctx.DUR + 1, y=1000, col=AMBER),
    ]
    impacts = [0.30, wd(2, "roca") + 0.2, wd(5, "confirmado") + 0.1, wd(6, "descubrimiento") + 0.3]
    return Spec(background, [sinroca, radar, confirmado], impacts=impacts, flashes=[(0.27, 0.9)], sfx=sfx, bleed=bleed)
