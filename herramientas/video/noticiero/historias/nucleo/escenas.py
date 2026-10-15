"""Historia: el núcleo interno de la Tierra modifica la duración de los días (Nature, Universidad de Alberta).

Short de ~45 s. Fuentes: artículo de Nature (Zhang y Dumberry, 2026), comunicado de la Universidad de Alberta, ScienceDaily.
Escenas (una por línea del guion): gancho con la imagen · estudio · milisegundos · capas de la Tierra · gravedad ·
tres fuerzas · deformación viscosa · misterios · cierre.
Los gráficos de escala (curva de milisegundos, tamaños de fuerzas) son ilustrativos y así se rotulan.
"""
import math
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec

C = None  # contexto de la historia (tiempos de la voz); lo asigna setup()
HERE = os.path.dirname(os.path.abspath(__file__))
PURPLE = (190, 130, 255)
CX, CY, R = 540, 655, 300  # esquema de capas de la Tierra

# ------------------------------------------------------------------ fondo: espacio profundo
yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([3, 5, 14], "float32") + v * np.array([8, 5, 14], "float32")
for cx_, cy_, rad_, col_, k_ in ((200, 420, 760, (70, 40, 140), 0.45), (900, 1100, 700, (20, 70, 150), 0.35), (540, 1750, 800, (170, 70, 10), 0.30)):
    d_ = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2) / rad_
    bg += (np.clip(1 - d_, 0, 1) ** 2)[..., None] * np.array(col_, "float32") * k_
bg *= np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)) ** 2.2, 0.3, 1)[..., None]
_r = np.random.default_rng(9)
for _ in range(260):
    sx, sy = int(_r.uniform(0, W)), int(_r.uniform(0, H))
    bg[sy:sy + 2, sx:sx + 2] += _r.uniform(30, 160)
bg[::6] *= 0.94
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
STARS = [(_r.uniform(0, W), _r.uniform(0, H), _r.uniform(0, 6.28)) for _ in range(70)]
STAR_S = glow_dot((220, 235, 255), 4)
EMB = [glow_dot((255, 170, 40), 7), glow_dot((255, 215, 130), 5), glow_dot((150, 190, 255), 6)]
_rg = random.Random(4)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H + 200), _rg.uniform(20, 70), _rg.uniform(0, 6.28), _rg.choice([0, 1, 2])) for _ in range(40)]

# ------------------------------------------------------------------ tu imagen de la Tierra
earth_img = Image.open(f"{HERE}/assets/tierra.webp").convert("RGB")


def feather(im, px):
    w, h = im.size
    m = np.ones((h, w), float)
    ramp = np.linspace(0, 1, px)
    m[:px] *= ramp[:, None]
    m[-px:] *= ramp[::-1][:, None]
    m[:, :px] *= ramp[None, :]
    m[:, -px:] *= ramp[::-1][None, :]
    a = im.convert("RGBA")
    a.putalpha(Image.fromarray((m * 255).astype("uint8")))
    return a


EARTH_S = feather(earth_img.resize((1080, round(earth_img.height * 1080 / earth_img.width)), Image.LANCZOS), 110)
_core = earth_img.crop((330, 100, 590, 360)).resize((900, 900), Image.LANCZOS).filter(ImageFilter.UnsharpMask(4, 130, 2))
_yy, _xx = np.mgrid[0:900, 0:900]
_rr = np.sqrt((_xx - 450) ** 2 + (_yy - 450) ** 2) / 450
CORE_S = _core.convert("RGBA")
CORE_S.putalpha(Image.fromarray((np.clip((1 - _rr) / 0.35, 0, 1) * 255).astype("uint8")))
CORE_G = soft_glow(500, 500, (255, 150, 20), 60, 0.9, 250)

# ------------------------------------------------------------------ esquema de capas (supermuestreado)


def build_earth_x():
    size = 2 * R + 60
    ss = 2
    n = size * ss
    c = n / 2
    Y, X = np.mgrid[0:n, 0:n].astype("float32")
    r = np.sqrt((X - c) ** 2 + (Y - c) ** 2) / (R * ss)
    rng = np.random.default_rng(2)
    nz = np.asarray(Image.fromarray((rng.random((50, 50)) * 255).astype("uint8")).resize((n, n), Image.BICUBIC).filter(ImageFilter.GaussianBlur(18)), "float32")
    nz = (nz - nz.min()) / (nz.max() - nz.min()) - 0.5
    img = np.zeros((n, n, 3), "float32")
    t = np.clip((r - 0.545) / 0.44, 0, 1)[..., None]
    mantle = (1 - t) * np.array([236, 92, 28], "float32") + t * np.array([150, 30, 14], "float32") + nz[..., None] * 46
    t = np.clip((r - 0.192) / 0.353, 0, 1)[..., None]
    outer = (1 - t) * np.array([255, 222, 100], "float32") + t * np.array([255, 135, 22], "float32") + nz[..., None] * 40
    t = np.clip(r / 0.192, 0, 1)[..., None]
    inner = (1 - t) * np.array([255, 252, 225], "float32") + t * np.array([255, 208, 100], "float32")
    img = np.where((r < 0.192)[..., None], inner, np.where((r < 0.545)[..., None], outer, np.where((r < 0.985)[..., None], mantle, np.array([104, 72, 48], "float32"))))
    for b_ in (0.192, 0.545, 0.985):
        img *= (1 - 0.55 * np.clip(1 - np.abs(r - b_) / 0.006, 0, 1))[..., None]
    alpha = np.clip((1.0 - r) * R * ss / 1.6, 0, 1)
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8")).convert("RGBA")
    im.putalpha(Image.fromarray((alpha * 255).astype("uint8")))
    return im.resize((size, size), Image.LANCZOS)


EARTH_X = build_earth_x()
EARTH_HALO = soft_glow(2 * R, 2 * R, (255, 120, 30), 50, 0.8, R)


def pol(cx, cy, r, ang):
    return cx + r * math.cos(ang), cy + r * math.sin(ang)


def arrow(d, p0, p1, col, w=10, head=36):
    d.line((p0[0], p0[1], p1[0], p1[1]), fill=col, width=w)
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    pts = [p1, (p1[0] - head * math.cos(ang - 0.45), p1[1] - head * math.sin(ang - 0.45)), (p1[0] - head * math.cos(ang + 0.45), p1[1] - head * math.sin(ang + 0.45))]
    d.polygon(pts, fill=col)


def dashed(d, p0, p1, col, w=8, dash=26, gap=16, off=0.0):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    s = -((off) % (dash + gap))
    while s < L:
        a0, a1 = max(0, s), min(L, s + dash)
        if a1 > a0:
            d.line((p0[0] + ux * a0, p0[1] + uy * a0, p0[0] + ux * a1, p0[1] + uy * a1), fill=col, width=w)
        s += dash + gap


def earth_diagram(cv, t, a, grow=1.0, blobs=0.0, arrows=0.0, markers=0.0, cy=CY):
    blit(cv, EARTH_HALO, CX, cy, scale=grow, alpha=a * 0.6 * clamp(grow))
    blit(cv, EARTH_X, CX, cy, scale=grow, alpha=a * clamp(grow * 1.5))
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    if blobs > 0:
        for k, ang in enumerate((math.radians(-35), math.radians(150))):
            bx, by = pol(CX, cy, 0.77 * R, ang)
            pr = 1 + 0.1 * math.sin(t * 4 + k)
            rx, ry = 70 * pr * blobs, 44 * pr * blobs
            d.ellipse((bx - rx, by - ry, bx + rx, by + ry), fill=(70, 8, 8, 215), outline=(255, 190, 60, 255), width=5)
    if arrows > 0:
        for k, ang in enumerate((math.radians(-35), math.radians(150))):
            p0 = pol(CX, cy, 0.22 * R, ang)
            p1 = pol(CX, cy, (0.22 + 0.34 * arrows) * R, ang)
            dashed(d, p0, p1, (255, 245, 170, 255), w=10, dash=22, gap=14, off=t * 90)
            if arrows > 0.95:
                arrow(d, pol(CX, cy, 0.52 * R, ang), pol(CX, cy, 0.60 * R, ang), (255, 245, 170, 255), w=10, head=34)
    if markers > 0:
        phi = t * 1.5   # núcleo interno: gira un poco más rápido que el manto
        psi = t * 0.9
        pa, pb = pol(CX, cy, 0.02 * R, phi), pol(CX, cy, 0.19 * R, phi)
        d.line((pa[0], pa[1], pb[0], pb[1]), fill=(40, 20, 0, 255), width=9)
        pc, pd_ = pol(CX, cy, 0.60 * R, psi), pol(CX, cy, 0.98 * R, psi)
        d.line((pc[0], pc[1], pd_[0], pd_[1]), fill=TEAL + (255,), width=9)
        pe = pol(CX, cy, 1.0 * R, psi)
        d.ellipse((pe[0] - 14, pe[1] - 14, pe[0] + 14, pe[1] + 14), fill=TEAL + (255,))
    comp(cv, lay, a)


# ------------------------------------------------------------------ sprites de texto
S_NUC1, w_n1, _ = rtext("EL NÚCLEO", ANTON, 250, grad=WHITE, stroke=7, stroke_col=(4, 10, 20), glow=((255, 160, 40), 22, 0.5), shadow=(0, 12, 9, 0.7))
S_NUC2, w_n2, _ = rtext("DE LA TIERRA", ANTON, 190, grad=GOLD, stroke=7, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 12, 9, 0.7))
S_NUC3 = S("CAMBIA LA DURACIÓN DEL DÍA", B7, 62, fill=(255, 200, 80), shadow=(0, 4, 3, 0.7))
T_NAT = title_sprite("PUBLICADO EN NATURE")
T_MS = title_sprite("UNOS POCOS MILISEGUNDOS")
T_BAT = title_sprite("UNA BATALLA DE FUERZAS")
T_GRAV = title_sprite("ACOPLAMIENTO GRAVITACIONAL")
T_TRES = title_sprite("TRES FUERZAS COMPITEN")
T_VISC = title_sprite("DEFORMACIÓN VISCOSA", TEAL)
T_MIST = title_sprite("AÚN HAY MISTERIOS")
S_MSBIG, w_msb, _ = rtext("MILISEGUNDOS", ANTON, 150, grad=GOLD, stroke=5, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.7))
S_MS1 = S("1 milisegundo = 0,001 segundos", B6, 46, fill=(190, 206, 228))
S_ILU = S("ILUSTRATIVO", B7, 34, fill=(255, 150, 120))
S_REV = S("estudio revisado por otros científicos", B6, 44, fill=(170, 190, 215))
S_DEC = S("DÉCADAS", B7, 36, fill=(160, 180, 205))
S_MSAX = S("ms", B7, 40, fill=(160, 180, 205))
S_PROF = S("MÁS DE 5.000 km", ANTON, 78, grad=GOLD, stroke=4, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 6, 5, 0.7))
LEG = [("MANTO", (220, 80, 26)), ("NÚCLEO EXTERNO · líquido", (255, 180, 50)), ("NÚCLEO INTERNO · sólido", (255, 240, 190))]
S_LEG = [S(t_, B7, 44, fill=(225, 234, 246), shadow=(0, 3, 2, 0.8)) for t_, _ in LEG]
S_GRAV = S("el más fuerte de los tres", B6, 48, fill=(255, 215, 120), shadow=(0, 4, 3, 0.8))
S_ACE = S("ACELERA", ANTON, 84, grad=((140, 255, 240), (60, 200, 200)), glow=((90, 220, 230), 16, 0.7), shadow=(0, 6, 5, 0.7))
S_FRE = S("FRENA", ANTON, 84, grad=((255, 160, 150), (230, 60, 60)), glow=((255, 60, 60), 16, 0.7), shadow=(0, 6, 5, 0.7))
S_NUCLEO_L = S("núcleo interno", B7, 38, fill=(40, 20, 0))
FORCES = [("GRAVITACIONAL", AMBER, 800, "la más fuerte"), ("ELECTROMAGNÉTICA", TEAL, 470, ""), ("TOPOGRÁFICA", PURPLE, 340, "")]
S_FORCE = [S(n_, B7, 50, fill=(235, 242, 250), shadow=(0, 4, 3, 0.8)) for n_, _, _, _ in FORCES]
S_AMORT = S("AMORTIGUADORES", ANTON, 90, grad=GOLD, stroke=4, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 6, 5, 0.7))
S_ILU2 = S("tamaños ilustrativos, sin escala", B6, 38, fill=(255, 160, 130))
S_10, w10, _ = rtext("~10 AÑOS", ANTON, 190, grad=WHITE, stroke=6, stroke_col=(4, 10, 20), glow=((90, 220, 230), 20, 0.7), shadow=(0, 8, 6, 0.7))
S_VISC = S("el núcleo sólido se deforma como una masa espesa", B6, 44, fill=(190, 230, 240), shadow=(0, 4, 3, 0.8))
S_Q = S("?", ANTON, 330, grad=GOLD, stroke=6, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.7))
S_CEN, w_cen, _ = rtext("EL CENTRO", ANTON, 205, grad=WHITE, stroke=7, stroke_col=(4, 10, 20), glow=((255, 160, 40), 22, 0.5), shadow=(0, 12, 9, 0.7))
S_MAN, w_man, _ = rtext("MANDA", ANTON, 250, grad=GOLD, stroke=7, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 12, 9, 0.7))
ST_PUB = make_stamp("PUBLICADO", (110, 230, 215), 78, (0, 30, 34, 225))


def card(w, h, head, lines_, foot, accent=AMBER):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, w - 7, h - 7), radius=24, fill=(8, 18, 30, 235), outline=accent + (255,), width=5)
    hs = S(head, B7, 46, fill=accent)
    im.alpha_composite(hs, (36, 30))
    y = 120
    for ln in lines_:
        s = S(ln, B6, 44, fill=(225, 234, 246))
        im.alpha_composite(s, (36, y))
        y += 66
    fs = S(foot, B6, 38, fill=(150, 168, 196))
    im.alpha_composite(fs, (36, h - 80))
    return im


CARD_A = card(450, 520, "OTRAS VARIACIONES", ["Algunos cambios más", "rápidos del día aún", "no tienen una", "explicación completa."], "sin resolver", AMBER)
CARD_B = card(450, 520, "EL DEBATE", ["No todos los", "sismólogos coinciden", "en cómo gira", "el núcleo interno."], "discusión abierta", TEAL)

# tarjeta del artículo
NAT = Image.new("RGBA", (880, 640), (0, 0, 0, 0))
_d = ImageDraw.Draw(NAT)
_d.rounded_rectangle((8, 8, 872, 632), radius=22, fill=(240, 243, 248, 255), outline=(150, 160, 178, 255), width=5)
_d.rectangle((8, 8, 872, 96), fill=(14, 30, 52, 255))
NAT.alpha_composite(S("NATURE", ANTON, 66, fill=(255, 255, 255)), (40, 8))
NAT.alpha_composite(S("2026 · REVISIÓN POR PARES", B7, 36, fill=(255, 200, 80)), (520, 28))
for i_, ln_ in enumerate(("Gravitational torque drives", "multidecadal variations", "in length of day")):
    NAT.alpha_composite(S(ln_, B7, 66, fill=(18, 36, 64)), (40, 130 + i_ * 82))
NAT.alpha_composite(S("Huifeng Zhang  ·  Mathieu Dumberry", B6, 46, fill=(70, 84, 108)), (40, 400))
_d.rounded_rectangle((40, 480, 700, 560), radius=14, fill=(200, 20, 36, 255))
NAT.alpha_composite(S("UNIVERSIDAD DE ALBERTA · CANADÁ", B7, 40, fill=(255, 255, 255)), (62, 496))
NAT_G = soft_glow(880, 640, (110, 200, 255), 24, 0.35, 22)


# ------------------------------------------------------------------ escenas
def background(t, dim):
    cv = BG.copy()
    for x, y, ph in STARS:
        a = 0.25 + 0.5 * (0.5 + 0.5 * math.sin(ph + t * 2.2))
        cv.paste(STAR_S.convert("RGB"), (round(x - STAR_S.width / 2), round(y - STAR_S.height / 2)), STAR_S.getchannel("A").point(lambda q, a=a: int(q * a * (1 - dim * 0.5))))
    for x0, y0, sp, ph, c in PARTS:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(ph + t * 0.8)
        a = 0.25 + 0.3 * math.sin(ph * 3 + t * 2.4)
        s = EMB[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * a)))
    return cv


def hook(cv, t):
    s1 = C.SC_T[0][1]
    out = e_inout(prog(t, s1 - 0.4, s1 + 0.1))
    pin = e_out(prog(t, 0.0, 0.7))
    te = C.wd(0, "centro")
    zoom = 1.0 + 0.10 * prog(t, 0, te + 0.4)
    to_core = e_out(prog(t, te - 0.1, te + 0.3))
    blit(cv, EARTH_S, 540, 600 - 400 * out, scale=zoom * (0.88 + 0.12 * pin), alpha=pin * (1 - out) * (1 - 0.9 * to_core))
    pc = e_back(prog(t, te - 0.1, te + 0.35))
    if pc > 0:
        pulse = 1 + 0.03 * math.sin(t * 7)
        blit(cv, CORE_G, 540, 600 - 400 * out, scale=(0.6 + 0.7 * pc) * pulse, alpha=clamp(pc * 2) * (1 - out) * 0.9)
        blit(cv, CORE_S, 540, 600 - 400 * out, scale=(0.55 + 0.55 * pc) * pulse * 1.0, alpha=clamp(pc * 2) * (1 - out))
    p1 = e_back(prog(t, 0.45, 0.85))
    dx, dy = shake(t, 0.62, 22, 8)
    blit(cv, S_NUC1, 540 + dx, 930 + dy - 700 * out, scale=min(960 / w_n1, 1) * (1 + 1.2 * (1 - p1)), alpha=e_out(prog(t, 0.45, 0.6)) * (1 - out))
    p2 = e_back(prog(t, 0.75, 1.1))
    dx2, dy2 = shake(t, 0.9, 20, 8)
    blit(cv, S_NUC2, 540 + dx2, 1185 + dy2 - 700 * out, scale=min(940 / w_n2, 1) * (1 + 1.1 * (1 - p2)), alpha=e_out(prog(t, 0.75, 0.9)) * (1 - out))
    tc = C.wd(0, "cambiando")
    p3 = e_out(prog(t, tc - 0.1, tc + 0.35))
    blit(cv, S_NUC3, 540 - 700 * (1 - p3) + 800 * out, 1305, alpha=clamp(p3 * 2) * (1 - out))


def nature(cv, t):
    a, ain = C.sw(t, 1)
    if a <= 0.01:
        return
    panel(cv, a, T_NAT, 0.96 + 0.04 * ain)
    s0 = C.SC_T[1][0]
    p = e_back(prog(t, s0 + 0.1, s0 + 0.6))
    bob = 5 * math.sin((t - s0) * 2)
    blit(cv, NAT_G, 540, 700 + bob, scale=0.98 * p, alpha=a * 0.8 * clamp(p * 2))
    blit(cv, NAT, 540, 700 + bob, scale=0.98 * p, rot=-2, alpha=a * clamp(p * 2))
    tn = C.wd(1, "nature")
    ps = prog(t, tn - 0.05, tn + 0.18)
    if ps > 0:
        dx, dy = shake(t, tn + 0.14, 20, 8)
        blit(cv, ST_PUB, 690 + dx, 1085 + dy, scale=0.82 * (1 + 1.4 * (1 - e_out(ps))), rot=-7, alpha=a * clamp(ps * 2.5))
    ta = C.wd(1, "alberta")
    blit(cv, S_REV, 540, 1195, alpha=a * prog(t, ta, ta + 0.4))


def curve_y(u):
    return 0.55 * math.sin(2 * math.pi * u / 0.55 + 0.4) + 0.30 * math.sin(2 * math.pi * u / 0.23 + 1.3) + 0.15 * math.sin(2 * math.pi * u / 0.11 + 0.2)


def milis(cv, t):
    a, ain = C.sw(t, 2)
    if a <= 0.01:
        return
    panel(cv, a, T_MS, 0.96 + 0.04 * ain)
    s0 = C.SC_T[2][0]
    x0, x1, yb, amp = 130, 950, 640, 150
    tm = C.wd(2, "milisegundos")
    td = C.wd(2, "décadas")
    pr = e_inout(prog(t, s0 + 0.2, td + 0.9))
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    d.rectangle((x0 - 10, 380, x1 + 10, 900), outline=(60, 90, 130, 255), width=3)
    for gy in range(420, 900, 60):
        d.line((x0 - 10, gy, x1 + 10, gy), fill=(30, 50, 80, 255), width=1)
    d.line((x0, yb, x1, yb), fill=(170, 190, 215, 255), width=3)
    d.line((x0, 380, x0, 900), fill=(170, 190, 215, 255), width=3)
    pts = [(x0 + (x1 - x0) * u / 200, yb - amp * curve_y(u / 200)) for u in range(int(200 * pr) + 1)]
    if len(pts) > 1:
        d.line(pts, fill=(255, 190, 40, 255), width=8, joint="curve")
        d.ellipse((pts[-1][0] - 14, pts[-1][1] - 14, pts[-1][0] + 14, pts[-1][1] + 14), fill=(255, 245, 190, 255))
    comp(cv, lay, a)
    if len(pts) > 1:
        blit(cv, soft_glow(30, 30, (255, 170, 0), 24, 1.0, 14), pts[-1][0], pts[-1][1], alpha=a * 0.9)
    blit(cv, S_MSAX, x0 + 40, 410, alpha=a)
    blit(cv, S_DEC, x1 - 70, 870, alpha=a)
    blit(cv, S_ILU, x1 - 60, 408, alpha=a)
    pm = e_back(prog(t, tm - 0.05, tm + 0.35))
    dx, dy = shake(t, tm + 0.3, 14, 9)
    blit(cv, S_MSBIG, 540 + dx, 1010 + dy, scale=min(940 / w_msb, 1) * pm, alpha=a * clamp(pm * 2))
    blit(cv, S_MS1, 540, 1135, alpha=a * prog(t, tm + 0.3, tm + 0.7))


def capas(cv, t):
    a, ain = C.sw(t, 3)
    if a <= 0.01:
        return
    panel(cv, a, T_BAT, 0.96 + 0.04 * ain)
    s0 = C.SC_T[3][0]
    grow = e_back(prog(t, s0 + 0.1, s0 + 0.7), 1.3)
    earth_diagram(cv, t, a, grow=grow, markers=prog(t, s0 + 0.8, s0 + 1.2))
    tm = C.wd(3, "miles")
    pr = e_out(prog(t, tm - 0.1, tm + 0.7))
    if pr > 0:
        lay = new_layer()
        d = ImageDraw.Draw(lay)
        top, bot = CY - R, CY - 0.192 * R
        x = CX + R + 10
        d.line((x, top, x, top + (bot - top) * pr), fill=(255, 245, 190, 255), width=8)
        d.line((x - 22, top, x + 22, top), fill=(255, 245, 190, 255), width=8)
        if pr > 0.95:
            d.line((x - 22, bot, x + 22, bot), fill=(255, 245, 190, 255), width=8)
        comp(cv, lay, a)
        blit(cv, S_PROF, 540, 1012, scale=pr, alpha=a * clamp(pr * 2))
    for k, (s_, (_, col)) in enumerate(zip(S_LEG, LEG)):
        pk = e_out(prog(t, s0 + 0.9 + 0.2 * k, s0 + 1.3 + 0.2 * k))
        lay = new_layer()
        ImageDraw.Draw(lay).ellipse((150, 1105 + k * 50 - 14, 178, 1105 + k * 50 + 14), fill=col + (255,))
        comp(cv, lay, a * pk)
        blit(cv, s_, 200 + s_.width / 2, 1105 + k * 50, alpha=a * pk)


def gravedad(cv, t):
    a, ain = C.sw(t, 4)
    if a <= 0.01:
        return
    panel(cv, a, T_GRAV, 0.96 + 0.04 * ain)
    s0 = C.SC_T[4][0]
    tz = C.wd(4, "zonas")
    tt = C.wd(4, "tira")
    earth_diagram(cv, t, a, grow=1.0, blobs=e_back(prog(t, tz - 0.1, tz + 0.4)), arrows=e_out(prog(t, tt - 0.05, tt + 0.5)), markers=1.0)
    blit(cv, S_GRAV, 540, 1215, alpha=a * prog(t, s0 + 0.2, s0 + 0.6))
    ta, tf = C.wd(4, "acelera"), C.wd(4, "frena")
    pa = e_back(prog(t, ta - 0.05, ta + 0.3))
    pf = e_back(prog(t, tf - 0.05, tf + 0.3))
    blit(cv, S_ACE, 250, 1105, scale=pa, alpha=a * clamp(pa * 2))
    blit(cv, S_FRE, 840, 1105, scale=pf, alpha=a * clamp(pf * 2))


def fuerzas(cv, t):
    a, ain = C.sw(t, 5)
    if a <= 0.01:
        return
    panel(cv, a, T_TRES, 0.96 + 0.04 * ain)
    s0 = C.SC_T[5][0]
    starts = [s0 + 0.15, C.wd(5, "electromagnética") - 0.1, C.wd(5, "topográfica") - 0.1]
    ta = C.wd(5, "amortiguador")
    for k, (n_, col, wbar, _) in enumerate(FORCES):
        y = 440 + k * 190
        g = e_out(prog(t, starts[k], starts[k] + 0.6))
        blit(cv, S_FORCE[k], 110 + S_FORCE[k].width / 2, y - 62, alpha=a * g)
        bar = rrect(max(8, round(wbar * g)), 78, col, tuple(int(c * 0.6) for c in col), 16)
        glow = soft_glow(max(8, round(wbar * g)), 78, col, 26, 0.6, 16)
        pulse = 1.0
        if k > 0 and t > ta - 0.2:
            pulse = 0.75 + 0.25 * math.sin((t - ta) * 8 + k)
        blit(cv, glow, 110 + max(8, round(wbar * g)) / 2, y + 10, alpha=a * g * pulse)
        blit(cv, bar, 110 + max(8, round(wbar * g)) / 2, y + 10, alpha=a * clamp(g * 2))
    pa = e_back(prog(t, ta - 0.1, ta + 0.35))
    if pa > 0:
        blit(cv, S_AMORT, 540, 1040, scale=min(900 / S_AMORT.width, 1) * pa, alpha=a * clamp(pa * 2))
        # muelle animado entre dos placas
        lay = new_layer()
        d = ImageDraw.Draw(lay)
        for sx_ in (330, 750):
            top_ = 1105 + 6 * math.sin((t - ta) * 9)
            d.rectangle((sx_ - 50, top_, sx_ + 50, top_ + 14), fill=(255, 200, 80, 255))
            d.rectangle((sx_ - 50, 1190, sx_ + 50, 1204), fill=(255, 200, 80, 255))
            pts = [(sx_, top_ + 14)]
            n = 7
            for i in range(1, n + 1):
                yy_ = top_ + 14 + (1190 - top_ - 14) * i / (n + 1)
                pts.append((sx_ + (28 if i % 2 else -28), yy_))
            pts.append((sx_, 1190))
            d.line(pts, fill=(255, 235, 170, 255), width=7, joint="curve")
        comp(cv, lay, a * clamp(pa))
    blit(cv, S_ILU2, 540, 1228, alpha=a * 0.9 * prog(t, s0 + 1.0, s0 + 1.4))


def viscosa(cv, t):
    a, ain = C.sw(t, 6)
    if a <= 0.01:
        return
    panel(cv, a, T_VISC, 0.96 + 0.04 * ain)
    s0 = C.SC_T[6][0]
    td = C.wd(6, "deformarse")
    amp = 0.20 * e_out(prog(t, td - 0.1, td + 1.0))
    cx, cy = 540, 640
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    for i in range(10):  # reloj de diez años
        ang = -math.pi / 2 + i * 2 * math.pi / 10
        p0, p1 = pol(cx, cy, 285, ang), pol(cx, cy, 315, ang)
        d.line((p0[0], p0[1], p1[0], p1[1]), fill=(120, 160, 190, 255), width=6)
    t10 = C.wd(6, "diez")
    sweep_ = prog(t, t10, t10 + 1.6)
    if sweep_ > 0:
        d.arc((cx - 300, cy - 300, cx + 300, cy + 300), -90, -90 + 360 * sweep_, fill=TEAL + (255,), width=12)
    pts = []
    for j in range(121):
        th = j / 120 * 2 * math.pi
        r_ = 150 * (1 + amp * math.sin(3 * th + t * 2.6) + 0.6 * amp * math.sin(5 * th - t * 1.9))
        pts.append(pol(cx, cy, r_, th))
    d.polygon(pts, fill=(255, 214, 110, 255), outline=(255, 250, 220, 255))
    comp(cv, lay, a)
    blit(cv, soft_glow(260, 260, (255, 160, 30), 50, 0.9, 120), cx, cy, scale=1.0 + 0.1 * math.sin(t * 4), alpha=a * 0.8)
    blit(cv, S_NUCLEO_L, cx, cy, alpha=a * 0.9)
    pm = e_back(prog(t, t10 - 0.05, t10 + 0.4))
    dx, dy = shake(t, t10 + 0.3, 14, 9)
    blit(cv, S_10, 540 + dx, 1030 + dy, scale=min(800 / w10, 1) * pm, alpha=a * clamp(pm * 2))
    blit(cv, S_VISC, 540, 1165, alpha=a * prog(t, td, td + 0.5))


def misterios(cv, t):
    a, ain = C.sw(t, 7)
    if a <= 0.01:
        return
    panel(cv, a, T_MIST, 0.96 + 0.04 * ain)
    tm, tc = C.wd(7, "misterios"), C.wd(7, "coinciden")
    for k, (spr, cx, tt) in enumerate(((CARD_A, 290, tm), (CARD_B, 790, tc))):
        p = e_back(prog(t, tt - 0.1, tt + 0.45))
        bob = 6 * math.sin(t * 2 + k)
        blit(cv, spr, cx, 640 + bob, scale=p, alpha=a * clamp(p * 2))
        pq = e_back(prog(t, tt + 0.2, tt + 0.7))
        blit(cv, S_Q, cx, 1065 + bob, scale=0.55 * pq * (1 + 0.04 * math.sin(t * 5 + k)), alpha=a * clamp(pq * 2))


def cierre(cv, t):
    s0 = C.SC_T[8][0]
    a = e_out(prog(t, s0, s0 + 0.4))
    if a <= 0.01:
        return
    beat = 1 + 0.03 * (abs(math.sin((t - s0) * 3.2)) ** 6)
    blit(cv, EARTH_HALO, 540, 560, scale=1.5 * beat, alpha=a * 0.6)
    blit(cv, EARTH_S, 540, 560, scale=0.95 * beat, alpha=a * 0.9)
    tc, tm = C.wd(8, "centro"), C.wd(8, "manda")
    p1 = e_back(prog(t, tc - 0.05, tc + 0.4))
    dx, dy = shake(t, tc + 0.3, 16, 9)
    blit(cv, S_CEN, 540 + dx, 925 + dy, scale=min(960 / w_cen, 1) * p1, alpha=a * clamp(p1 * 2))
    p2 = e_back(prog(t, tm - 0.05, tm + 0.4))
    dx, dy = shake(t, tm + 0.3, 20, 8)
    blit(cv, S_MAN, 540 + dx, 1128 + dy, scale=min(900 / w_man, 1) * p2, alpha=a * clamp(p2 * 2))


def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0
    scenes = [hook, nature, milis, capas, gravedad, fuerzas, viscosa, misterios, cierre]

    def dim(t):
        if t < ctx.SC_T[1][0] - 0.2:
            return 0.0
        return 0.7

    def sfx(sput, ctx):
        SC_T = ctx.SC_T
        sput(rumble(2.0), 0.0, 0.8)
        sput(hit(70, 1.2, 0.8), 0.45, 0.9)
        sput(hit(85), 0.75, 0.8)
        sput(whoosh(0.4, True, 3), 0.40, 0.4)
        sput(riser(0.9), wd(0, "centro") - 0.8, 0.5)
        sput(hit(60, 1.4, 0.9), wd(0, "centro") - 0.1, 1.0)
        sput(whoosh(0.5, True, 4), wd(0, "centro") - 0.1, 0.5)
        for i in range(1, 9):
            sput(whoosh(0.45, True, 10 + i), SC_T[i][0] - 0.1, 0.45)
            sput(hit(100, 0.5, 0.3), SC_T[i][0] + 0.12, 0.45)
        sput(hit(70, 0.9, 0.9), wd(1, "nature") + 0.14, 0.9)
        sput(ping(), wd(1, "alberta"), 0.5)
        sput(sweep(2.8), l0(2) + 0.2, 0.35)
        sput(hit(110, 0.5, 0.3), wd(2, "milisegundos") + 0.3, 0.7)
        sput(riser(1.2), wd(3, "batalla") - 1.0, 0.5)
        sput(hit(70, 1.0, 0.9), wd(3, "batalla"), 0.9)
        sput(blip(1200), wd(3, "miles"), 0.5)
        sput(thump(1.0), wd(4, "tira"), 0.8)
        sput(thump(1.0), wd(4, "tira") + 0.5, 0.7)
        sput(hit(95, 0.6, 0.5), wd(4, "acelera"), 0.7)
        sput(hit(75, 0.6, 0.5), wd(4, "frena"), 0.7)
        for k, w in enumerate(("otras", "electromagnética", "topográfica")):
            sput(blip(900 + 250 * k, 0.12), wd(5, w), 0.6)
        sput(hit(100, 0.7, 0.6), wd(5, "amortiguador"), 0.9)
        sput(riser(1.0), wd(6, "diez") - 1.0, 0.5)
        sput(hit(70, 0.9, 0.8), wd(6, "diez"), 0.9)
        sput(blip(1000), wd(7, "misterios"), 0.5)
        sput(blip(1300), wd(7, "coinciden"), 0.5)
        sput(thump(1.0), wd(8, "centro"), 0.8)
        sput(hit(70, 1.0, 0.9), wd(8, "manda"), 1.0)
        sput(ping(), wd(8, "síguenos") + 0.35, 0.9)

    impacts = [0.45, 0.75, wd(1, "nature") + 0.14, wd(2, "milisegundos") + 0.3, wd(3, "batalla"), wd(4, "tira"), wd(5, "amortiguador"), wd(6, "diez") + 0.3, wd(8, "manda") + 0.3]
    flashes = [(0.42, 0.5), (wd(0, "centro") - 0.1, 0.7), (wd(3, "batalla"), 0.3)]
    return Spec(background, scenes, impacts=impacts, flashes=flashes, sfx=sfx, dim=dim, pad=(49, 73.4, 110, 146.8))
