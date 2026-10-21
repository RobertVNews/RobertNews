"""Short temático: los nefilim (Génesis 6:1-4, Números 13:33, Libro de Enoc). Sin noticia ni fotos: gráficos propios (siluetas ILUSTRATIVAS).
Todo se atribuye al texto bíblico o a la tradición; no se afirma que existieran.
Escenas: gancho con silueta gigante · versículo (panel) · significado de la palabra (panel) · espías y langostas (panel) ·
tres interpretaciones (panel) · diluvio (panel) · cierre."""
import math
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec

C = None
RED2 = (255, 90, 70)
yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([14, 4, 14], "float32") + v * np.array([40, 10, 8], "float32")
for cx_, cy_, rad_, col_, k_ in ((540, 1000, 900, (230, 70, 30), 0.38), (540, 400, 700, (110, 40, 130), 0.30)):
    d_ = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2) / rad_
    bg += (np.clip(1 - d_, 0, 1) ** 2)[..., None] * np.array(col_, "float32") * k_
bg *= np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)) ** 2.2, 0.3, 1)[..., None]
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
EMB = [glow_dot((255, 120, 60), 6), glow_dot((220, 90, 160), 5)]
_rg = random.Random(21)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H), _rg.uniform(30, 90), _rg.uniform(0, 6.28), _rg.choice([0, 1])) for _ in range(50)]


def figure(d, cx, by, h, col):
    """Silueta humanoide simple (cabeza, torso, brazos, piernas) con base en (cx, by) y altura h."""
    r = 0.065 * h
    d.ellipse((cx - r, by - 0.98 * h, cx + r, by - 0.98 * h + 2 * r), fill=col)
    d.polygon([(cx - 0.14 * h, by - 0.84 * h), (cx + 0.14 * h, by - 0.84 * h), (cx + 0.09 * h, by - 0.48 * h), (cx - 0.09 * h, by - 0.48 * h)], fill=col)
    d.polygon([(cx - 0.14 * h, by - 0.84 * h), (cx - 0.2 * h, by - 0.5 * h), (cx - 0.16 * h, by - 0.49 * h), (cx - 0.1 * h, by - 0.78 * h)], fill=col)
    d.polygon([(cx + 0.14 * h, by - 0.84 * h), (cx + 0.2 * h, by - 0.5 * h), (cx + 0.16 * h, by - 0.49 * h), (cx + 0.1 * h, by - 0.78 * h)], fill=col)
    d.polygon([(cx - 0.09 * h, by - 0.48 * h), (cx - 0.005 * h, by - 0.48 * h), (cx - 0.03 * h, by), (cx - 0.1 * h, by)], fill=col)
    d.polygon([(cx + 0.09 * h, by - 0.48 * h), (cx + 0.005 * h, by - 0.48 * h), (cx + 0.03 * h, by), (cx + 0.1 * h, by)], fill=col)
    d.ellipse((cx - 0.03 * h, by - 0.955 * h, cx - 0.008 * h, by - 0.94 * h), fill=(255, 200, 80, 255))
    d.ellipse((cx + 0.008 * h, by - 0.955 * h, cx + 0.03 * h, by - 0.94 * h), fill=(255, 200, 80, 255))


def mountains(d, by, col):
    pts = [(0, by)]
    for k in range(0, 1081, 60):
        pts.append((k, by - 80 - 90 * abs(math.sin(k * 0.011 + 1.3)) - 60 * abs(math.sin(k * 0.027))))
    pts.append((1080, by))
    d.polygon(pts, fill=col)


T_VERSO = title_sprite("GÉNESIS 6:4")
T_PAL = title_sprite("¿QUÉ SIGNIFICA «NEFILIM»?")
T_ESP = title_sprite("NÚMEROS 13:33")
T_INT = title_sprite("¿QUIÉNES ERAN?")
T_DIL = title_sprite("DESPUÉS: EL DILUVIO")
S_ILU = S("ILUSTRACIÓN ESQUEMÁTICA", B7, 32, fill=(220, 200, 210), shadow=(0, 3, 2, 0.9))
S_HOOK1, _, _ = rtext("¿GIGANTES", ANTON, 190, grad=WHITE, stroke=6, stroke_col=(40, 0, 10), glow=((255, 90, 60), 22, 0.6), shadow=(0, 10, 8, 0.8))
S_HOOK2, _, _ = rtext("EN LA BIBLIA?", ANTON, 190, grad=GOLD, stroke=6, stroke_col=(110, 40, 0), glow=GLOW_A, shadow=(0, 10, 8, 0.8))
S_NEF, _, _ = rtext("NEFILIM", ANTON, 230, grad=GOLD, stroke=7, stroke_col=(110, 40, 0), glow=GLOW_A, shadow=(0, 12, 9, 0.8))
VERSO = ["«HABÍA GIGANTES", "EN LA TIERRA", "EN AQUELLOS DÍAS»"]
S_VERSO = [S(t, ANTON, 96, fill=(255, 255, 255), shadow=(0, 8, 6, 0.85)) for t in VERSO]
S_REF = S("Reina-Valera 1960", B6, 36, fill=(200, 190, 210), shadow=(0, 3, 2, 0.8))
S_GIG = S("GIGANTES", ANTON, 120, fill=(255, 255, 255), shadow=(0, 8, 6, 0.85))
S_CAI = S("CAÍDOS", ANTON, 120, fill=AMBER, shadow=(0, 8, 6, 0.85))
S_DISC = S("SU SIGNIFICADO EXACTO SE DISCUTE", B7, 46, fill=(220, 200, 210), shadow=(0, 4, 3, 0.9))
S_LANG = S("«ÉRAMOS COMO LANGOSTAS»", ANTON, 84, fill=AMBER, shadow=(0, 8, 6, 0.85))
S_CAN = S("LOS ESPÍAS EN CANAÁN", B7, 52, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))


def card(txt, sub, col):
    sp = rrect(860, 190, (30, 14, 28), (18, 8, 18), 22)
    ImageDraw.Draw(sp).rounded_rectangle((0, 0, 859, 189), radius=22, outline=col + (255,), width=5)
    t = S(txt, B7, 60, fill=(255, 255, 255), shadow=(0, 3, 2, 0.6))
    if t.width > 800:
        t = t.resize((800, round(t.height * 800 / t.width)), Image.LANCZOS)
    sp.alpha_composite(t, (30, 28))
    s = S(sub, B6, 40, fill=col, shadow=(0, 3, 2, 0.6))
    sp.alpha_composite(s, (30, 112))
    return sp


CARDS = [card("ÁNGELES CAÍDOS", "SEGÚN EL LIBRO DE ENOC", RED2), card("DESCENDIENTES DE SET", "OTRA INTERPRETACIÓN", AMBER), card("REYES Y GUERREROS", "OTRA INTERPRETACIÓN", TEAL)]
S_DIL = S("LA BIBLIA HABLA DE LA MALDAD DE LOS HOMBRES", B7, 50, fill=(255, 255, 255), shadow=(0, 4, 3, 0.9))
S_Q = [S("¿MITO,", ANTON, 170, fill=(255, 255, 255), shadow=(0, 10, 8, 0.85)), S("SÍMBOLO", ANTON, 170, fill=AMBER, shadow=(0, 10, 8, 0.85)),
       S("O HISTORIA?", ANTON, 170, fill=(255, 255, 255), shadow=(0, 10, 8, 0.85))]


def background(t, dim):
    cv = BG.copy()
    for x0, y0, sp, ph, c in PARTS:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(ph + t * 0.8)
        a = 0.2 + 0.25 * math.sin(ph * 3 + t * 2.4)
        s = EMB[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * max(a, 0))))
    return cv


GLOW_BG = glow_dot((255, 110, 50), 120)


def hook(cv, t, full=False, texts=True):
    a, ain = C.sw(t, 0) if not full else (1.0, 1.0)
    if a <= 0:
        return
    rise = e_out(prog(t, 0.3, 2.2))
    blit(cv, GLOW_BG, 540, 880, scale=3.2 + 0.2 * math.sin(t * 2), alpha=0.55 * a)
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    mountains(d, 1130, (30, 10, 26, 255))
    figure(d, 540, 1130 + 240 * (1 - rise), 520, (12, 3, 14, 255))
    mountains(d, 1230, (14, 5, 14, 255))
    for k, x in enumerate((180, 380, 720, 880)):
        figure(d, x, 1235, 120, (6, 2, 8, 255))
    comp(cv, lay, a)
    if texts:
        p1 = e_back(prog(t, 0.2, 0.8), 1.5)
        blit(cv, S_HOOK1, 540, 330, scale=0.85 + 0.15 * clamp(p1), alpha=a * clamp(p1 * 2))
        p2 = e_back(prog(t, C.wd(0, "biblia") - 0.3, C.wd(0, "biblia") + 0.3), 1.5)
        blit(cv, S_HOOK2, 540, 500, scale=0.85 + 0.15 * clamp(p2), alpha=a * clamp(p2 * 2))
    blit(cv, S_ILU, 540, 1190, alpha=a * 0.8)


def verso(cv, t):
    a, ain = C.sw(t, 1)
    if a <= 0:
        return
    panel(cv, a, T_VERSO)
    t0 = C.wd(1, "gigantes")
    for i, sp in enumerate(S_VERSO):
        p = e_out(prog(t, t0 + 0.3 * i - 0.1, t0 + 0.3 * i + 0.45))
        blit(cv, sp, 540, 520 + 130 * i + 20 * (1 - p), alpha=a * p)
    blit(cv, S_REF, 540, 960, alpha=a * e_out(prog(t, t0 + 1.2, t0 + 1.7)))
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    d.line((250, 1010, 830, 1010), fill=AMBER + (160,), width=3)
    figure(d, 420, 1170, 220, (255, 200, 150, 255))
    figure(d, 640, 1170, 220, (255, 200, 150, 255))
    comp(cv, lay, a * e_out(prog(t, C.wd(1, "hijos"), C.wd(1, "hijos") + 0.5)))


def palabra(cv, t):
    a, ain = C.sw(t, 2)
    if a <= 0:
        return
    panel(cv, a, T_PAL)
    p = e_back(prog(t, C.l0(2) + 0.1, C.l0(2) + 0.6), 1.5)
    blit(cv, S_NEF, 540, 480, scale=0.85 + 0.15 * clamp(p), alpha=a * clamp(p * 2))
    for sp, word, y in ((S_GIG, "gigantes", 720), (S_CAI, "caídos", 880)):
        tw = C.wd(2, word)
        pk = e_back(prog(t, tw - 0.1, tw + 0.4), 1.6)
        blit(cv, sp, 540, y, scale=0.85 + 0.15 * clamp(pk), alpha=a * clamp(pk * 2))
    pd = e_out(prog(t, C.wd(2, "discute"), C.wd(2, "discute") + 0.4))
    blit(cv, S_DISC, 540, 1080, alpha=a * pd)


def espias(cv, t):
    a, ain = C.sw(t, 3)
    if a <= 0:
        return
    panel(cv, a, T_ESP)
    tg = C.wd(3, "gigantes")
    pg = e_out(prog(t, tg - 0.2, tg + 0.6))
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    d.line((100, 1060, 980, 1060), fill=(255, 200, 150, 120), width=3)
    figure(d, 680, 1060 + 120 * (1 - pg), 640, (255, 140, 90, 255))
    pt = e_out(prog(t, C.wd(3, "espías"), C.wd(3, "espías") + 0.6))
    for k, x in enumerate((250, 330, 410)):
        figure(d, x, 1060, 70, (255, 235, 210, int(255 * pt)))
    comp(cv, lay, a)
    blit(cv, S_CAN, 540, 440, alpha=a * pt)
    pl = e_back(prog(t, C.wd(3, "langostas") - 0.2, C.wd(3, "langostas") + 0.4), 1.6)
    blit(cv, S_LANG, 540, 570, scale=0.85 + 0.15 * clamp(pl), alpha=a * clamp(pl * 2))


def interpretaciones(cv, t):
    a, ain = C.sw(t, 4)
    if a <= 0:
        return
    panel(cv, a, T_INT)
    for sp, word, y in ((CARDS[0], "ángeles", 470), (CARDS[1], "descendientes", 700), (CARDS[2], "reyes", 930)):
        tw = C.wd(4, word)
        p = e_back(prog(t, tw - 0.1, tw + 0.4), 1.4)
        if p > 0:
            blit(cv, sp, 540 - 180 * (1 - clamp(p)), y, alpha=a * clamp(p * 2))


def diluvio(cv, t):
    a, ain = C.sw(t, 5)
    if a <= 0:
        return
    panel(cv, a, T_DIL)
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    rise = e_out(prog(t, C.wd(5, "diluvio") - 0.2, C.wd(5, "diluvio") + 2.0))
    for k in range(6):
        y0 = 1000 - 360 * rise + 36 * k
        pts = [(x, y0 + 14 * math.sin(x * 0.02 + t * 3 + k)) for x in range(110, 971, 20)]
        pts += [(970, 1190), (110, 1190)]
        d.polygon(pts, fill=(90 + 10 * k, 160 + 8 * k, 230, 70))
    comp(cv, lay, a)
    pm = e_out(prog(t, C.wd(5, "maldad"), C.wd(5, "maldad") + 0.5))
    blit(cv, S_DIL, 540, 500, alpha=a * pm)


def cierre(cv, t):
    a, ain = C.sw(t, 6)
    if a <= 0:
        return
    hook(cv, t, full=True, texts=False)
    for i, sp in enumerate(S_Q):
        tw = (C.wd(6, "mito"), C.wd(6, "símbolo"), C.wd(6, "historia"))[i]
        p = e_back(prog(t, tw - 0.1, tw + 0.4), 1.6)
        blit(cv, sp, 540, 330 + 160 * i, scale=0.85 + 0.15 * clamp(p), alpha=a * clamp(p * 2))


def setup(ctx):
    global C
    C = ctx
    wd = ctx.wd
    SC = ctx.SC_T

    def sfx(sput, ctx):
        sput(riser(0.3), 0.0, 0.5)
        sput(hit(60, 1.4, 0.8), 0.9, 1.0)
        sput(rumble(2.2), 0.3, 0.7)
        sput(whoosh(0.5, True, 2), 0.25, 0.5)
        for i in range(1, 7):
            sput(whoosh(0.45, True, 10 + i), SC[i][0] - 0.1, 0.4)
            sput(hit(100, 0.5, 0.3), SC[i][0] + 0.12, 0.4)
        sput(hit(70, 0.9, 0.8), wd(1, "gigantes") + 0.1, 0.9)
        sput(ping(), wd(2, "nefilim") + 0.1, 0.6)
        sput(thump(0.9), wd(3, "langostas") - 0.2, 0.8)
        for w in ("ángeles", "descendientes", "reyes"):
            sput(blip(900 + 150 * ("ángeles descendientes reyes".split().index(w)), 0.12), wd(4, w), 0.5)
        sput(rumble(2.5), wd(5, "diluvio") - 0.2, 0.7)
        sput(riser(1.0), wd(6, "historia") - 1.0, 0.5)
        sput(hit(70, 1.0, 0.9), wd(6, "historia") + 0.1, 1.0)
        sput(ping(), wd(6, "síguenos") + 0.35, 0.9)

    impacts = [0.9, wd(1, "gigantes") + 0.1, wd(3, "langostas") + 0.1, wd(6, "historia") + 0.1]
    return Spec(background, [hook, verso, palabra, espias, interpretaciones, diluvio, cierre], impacts=impacts, flashes=[(0.9, 0.6)], sfx=sfx)
