"""Historia: un agricultor halla una estatua gigante de Ramsés II en Egipto (Behbeit El Hagar, Gharbia).

Short de ~45 s. Todo sale de la nota de Robert News (fuentes citadas: Egyptian Gazette, Heritage Daily, New York Post).
La imagen de portada es una ilustración y se rotula "IMAGEN ILUSTRATIVA". Las siluetas de la comparación de tamaños,
el mapa y los jeroglíficos del bloque son esquemáticos (no reproducen el hallazgo real).
Escenas (una por línea): gancho con la imagen · Ramsés II · mapa · excavación · cabeza y doble corona ·
altura de la estatua · segunda estatua · bloque de granito · cierre.
"""
import math
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec

C = None  # contexto de la historia (tiempos de la voz); lo asigna setup()
HERE = os.path.dirname(os.path.abspath(__file__))
SAND = (232, 190, 120)
GOLDC = (255, 196, 70)

# ------------------------------------------------------------------ fondo: noche en el desierto
yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([8, 5, 4], "float32") + v * np.array([20, 11, 5], "float32")
for cx_, cy_, rad_, col_, k_ in ((540, 700, 820, (190, 120, 40), 0.40), (150, 1500, 700, (160, 70, 20), 0.30), (950, 400, 600, (120, 80, 40), 0.25)):
    d_ = np.sqrt((xx - cx_) ** 2 + (yy - cy_) ** 2) / rad_
    bg += (np.clip(1 - d_, 0, 1) ** 2)[..., None] * np.array(col_, "float32") * k_
bg *= np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.65)) ** 2)) ** 2.2, 0.3, 1)[..., None]
_r = np.random.default_rng(11)
for _ in range(120):
    sx, sy = int(_r.uniform(0, W)), int(_r.uniform(0, 700))
    bg[sy:sy + 2, sx:sx + 2] += _r.uniform(30, 120)
bg[::6] *= 0.94
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
SANDS = [glow_dot((255, 205, 120), 6), glow_dot((230, 160, 80), 5), glow_dot((255, 240, 200), 4)]
_rg = random.Random(6)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H), _rg.uniform(40, 120), _rg.uniform(0, 6.28), _rg.choice([0, 1, 2])) for _ in range(60)]

# ------------------------------------------------------------------ tu imagen
cover = Image.open(f"{HERE}/assets/portada.webp").convert("RGB")
KX, KY = cover.width / 1142, cover.height / 1377
_patch = cover.crop((round(62 * KX), round(1022 * KY), round(96 * KX), round(1062 * KY)))
cover.paste(_patch, (round(18 * KX), round(1022 * KY)))
HERO = (0, 620, 1142, 1360)
HERO_MASK = Image.fromarray((np.clip(np.minimum(np.arange(700)[:, None] / 45, (699 - np.arange(700))[:, None] / 45), 0, 1) *
                             np.clip(np.minimum(np.arange(1080)[None, :] / 30, (1079 - np.arange(1080))[None, :] / 30), 0, 1) * 255).astype("uint8"))


def hero_view(cv, cxs, cys, z, alpha=1.0, y_dest=250):
    """Recorte con zoom y paneo de la imagen; devuelve la función que pasa coordenadas de la imagen a pantalla."""
    w, h = 1142 / z, 740 / z
    x0, y0 = clamp(cxs - w / 2, 0, 1142 - w), clamp(cys - h / 2, 620, 1360 - h)
    im = cover.crop((round(x0 * KX), round(y0 * KY), round((x0 + w) * KX), round((y0 + h) * KY))).resize((1080, 700), Image.LANCZOS)
    m = HERO_MASK if alpha >= 1 else HERO_MASK.point(lambda q: int(q * alpha))
    cv.paste(im, (0, y_dest), m)
    return lambda sx, sy: ((sx - x0) * 1080 / w, y_dest + (sy - y0) * 700 / h)


def tile(box, w, h, border=GOLDC):
    x0, y0, x1, y1 = box
    im = cover.crop((round(x0 * KX), round(y0 * KY), round(x1 * KX), round(y1 * KY))).resize((w, h), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=26, fill=255)
    im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=26, outline=border + (255,), width=6)
    return im


TILE_HEAD_S = tile((470, 598, 1142, 1180), 470, 407)
TILE_HEAD = tile((470, 598, 1142, 1180), 660, 572)
TILE_FARM = tile((0, 680, 600, 1160), 800, 640)
TILE_GLOW = soft_glow(660, 572, (255, 170, 40), 40, 0.8, 26)

# ------------------------------------------------------------------ sprites de texto
S_T1, w_t1, _ = rtext("FARAÓN", ANTON, 260, grad=WHITE, stroke=7, stroke_col=(20, 8, 2), glow=((255, 170, 50), 22, 0.5), shadow=(0, 12, 9, 0.7))
S_T2, w_t2, _ = rtext("GIGANTE", ANTON, 210, grad=GOLD, stroke=7, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 12, 9, 0.7))
S_ILU = S("IMAGEN ILUSTRATIVA", B7, 34, fill=(255, 220, 160), shadow=(0, 3, 2, 0.9))
S_AGR = S("AGRICULTOR", B7, 50, fill=(255, 245, 220), shadow=(0, 4, 3, 0.9))
S_RAM = S("RAMSÉS II", B7, 54, fill=GOLDC, shadow=(0, 4, 3, 0.9))
T_RAMSES = title_sprite("RAMSÉS II")
T_MAPA = title_sprite("EGIPTO · DELTA DEL NILO")
T_EXC = title_sprite("EXCAVACIÓN EN CURSO")
T_CAB = title_sprite("LA CABEZA")
T_ALT = title_sprite("¿CUÁNTO MEDÍA?")
T_SEG = title_sprite("UNA SEGUNDA ESTATUA")
T_BLO = title_sprite("BLOQUE DE GRANITO ROSA")
S_PODER = S("uno de los reyes más poderosos", B7, 50, fill=(240, 232, 215), shadow=(0, 4, 3, 0.8))
S_PODER2 = S("del antiguo Egipto", B7, 50, fill=(240, 232, 215), shadow=(0, 4, 3, 0.8))
S_NACE = S("NACE EN 1303 a. C.", B7, 44, fill=GOLDC, shadow=(0, 4, 3, 0.8))
S_IMP = S("IMPERIO NUEVO · 1570 – 1069 a. C.", B7, 46, fill=(235, 225, 205), shadow=(0, 4, 3, 0.8))
S_Y1570 = S("1570", B6, 36, fill=(180, 165, 140))
S_Y1069 = S("1069", B6, 36, fill=(180, 165, 140))
S_EGIPTO = S("EGIPTO", ANTON, 70, fill=(255, 235, 200), shadow=(0, 5, 4, 0.8))
S_DELTA = S("DELTA DEL NILO", B7, 44, fill=(120, 215, 235), shadow=(0, 4, 3, 0.9))
S_BEH = S("BEHBEIT EL HAGAR", B7, 50, fill=GOLDC, shadow=(0, 4, 3, 0.9))
S_GHA = S("provincia de Gharbia · según medios egipcios", B6, 38, fill=(220, 210, 190), shadow=(0, 4, 3, 0.9))
S_CSA = S("CONSEJO SUPREMO DE ANTIGÜEDADES", B7, 48, fill=(255, 255, 255), shadow=(0, 3, 2, 0.5))
S_AVISO = S("avisó a las autoridades locales", B6, 44, fill=(225, 215, 195), shadow=(0, 4, 3, 0.8))
S_DOBLE = S("DOBLE CORONA", ANTON, 70, grad=GOLD, glow=GLOW_A, shadow=(0, 5, 4, 0.8))
S_DOBLE2 = S("Alto y Bajo Egipto", B7, 44, fill=(240, 232, 215), shadow=(0, 4, 3, 0.8))
S_METRO = S("+1,5 m", ANTON, 90, grad=WHITE, stroke=4, stroke_col=(20, 8, 2), glow=((255, 170, 50), 14, 0.5), shadow=(0, 6, 5, 0.8))
S_H8, w_h8, _ = rtext("MÁS DE 8 m", ANTON, 130, grad=GOLD, stroke=5, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.7))
S_ALTURA = S("altura calculada de la estatua completa", B6, 42, fill=(220, 210, 190), shadow=(0, 4, 3, 0.8))
S_PERSONA = S("persona 1,7 m", B7, 40, fill=(225, 235, 245), shadow=(0, 4, 3, 0.9))
S_CABEZA = S("cabeza +1,5 m", B7, 40, fill=GOLDC, shadow=(0, 4, 3, 0.9))
S_2E, w_2e, _ = rtext("CASI 2,4 m", ANTON, 120, grad=((255, 250, 235), (200, 170, 110)), stroke=5, stroke_col=(60, 30, 5), glow=GLOW_A, shadow=(0, 8, 6, 0.7))
S_2E2 = S("sin piernas ni base · rostro visible", B6, 42, fill=(225, 215, 195), shadow=(0, 4, 3, 0.8))
S_NEMES = S("NEMES · tocado real a rayas", B7, 44, fill=GOLDC, shadow=(0, 4, 3, 0.9))
S_GR = S("~1,2 m de altura", B7, 44, fill=(255, 215, 215), shadow=(0, 4, 3, 0.9))
S_REY = S("REY DEL ALTO Y BAJO EGIPTO", B7, 50, fill=(255, 245, 220), shadow=(0, 4, 3, 0.9))
S_HIJO = S("HIJO DE RA", ANTON, 100, grad=GOLD, stroke=4, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 6, 5, 0.8))
S_INS = S("inscripción ilustrativa", B6, 36, fill=(255, 170, 140))
S_QM1, w_q1, _ = rtext("¿QUÉ MÁS HAY", ANTON, 190, grad=WHITE, stroke=7, stroke_col=(20, 8, 2), glow=((255, 170, 50), 22, 0.5), shadow=(0, 12, 9, 0.7))
S_QM2, w_q2, _ = rtext("BAJO LA ARENA?", ANTON, 190, grad=GOLD, stroke=7, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 12, 9, 0.7))
S_FIN = S("Esperan que los hallazgos ayuden a entender mejor la región", B6, 40, fill=(225, 215, 195), shadow=(0, 4, 3, 0.9))

# ------------------------------------------------------------------ gráficos
EGIPTO = [(25.0, 31.6), (29.9, 31.2), (30.4, 31.5), (31.8, 31.45), (32.3, 31.3), (34.25, 31.25), (34.9, 29.5), (34.5, 28.5), (34.25, 27.75),
          (33.6, 28.2), (32.8, 29.6), (32.55, 29.97), (32.85, 29.4), (33.1, 28.4), (33.8, 27.2), (34.9, 25.1), (35.5, 23.9), (36.9, 22.0), (25.0, 22.0)]
NILO = [(32.9, 22.0), (32.9, 24.1), (32.65, 25.7), (31.9, 26.5), (31.2, 27.2), (31.1, 28.5), (31.2, 30.05), (31.1, 30.7)]
RAMA_ROSETA = [(31.1, 30.7), (30.7, 31.1), (30.2, 31.45)]
RAMA_DAMIETA = [(31.1, 30.7), (31.5, 31.0), (31.8, 31.4)]
BEH = (31.28, 30.95)
MAP_X0, MAP_Y0, MAP_W, MAP_H = 110, 340, 860, 790


def mp(lon, lat):
    return (MAP_X0 + (lon - 24.5) / (37.4 - 24.5) * MAP_W, MAP_Y0 + (31.9 - lat) / (31.9 - 21.8) * MAP_H)


def statue_pts(h, cx, ground):
    right = [(0.45, 0), (0.45, 0.06), (0.28, 0.06), (0.26, 0.60), (0.40, 0.66), (0.40, 0.72), (0.10, 0.74), (0.10, 0.77), (0.24, 0.80), (0.27, 0.92), (0.10, 1.0)]
    left = [(-x, y) for x, y in reversed(right)]
    return [(cx + x * 0.40 * h, ground - y * h) for x, y in right + left]


def draw_statue(lay, d, h, cx, ground, col=(236, 186, 80), stripes=False):
    pts = statue_pts(h, cx, ground)
    d.polygon(pts, fill=col + (255,), outline=(255, 240, 190, 255))
    if stripes:
        for k in range(5):
            yy_ = ground - (0.78 + 0.028 * k) * h
            d.line((cx - 0.24 * 0.4 * h, yy_, cx + 0.24 * 0.4 * h, yy_), fill=(120, 70, 10, 255), width=4)


def person(d, cx, ground, h, col=(205, 220, 238)):
    hr = h * 0.075
    d.ellipse((cx - hr, ground - h, cx + hr, ground - h + 2 * hr), fill=col + (255,))
    d.polygon([(cx - h * 0.16, ground - h + 2.2 * hr), (cx + h * 0.16, ground - h + 2.2 * hr), (cx + h * 0.12, ground - h * 0.42), (cx - h * 0.12, ground - h * 0.42)], fill=col + (255,))
    d.rectangle((cx - h * 0.11, ground - h * 0.42, cx - h * 0.02, ground), fill=col + (255,))
    d.rectangle((cx + h * 0.02, ground - h * 0.42, cx + h * 0.11, ground), fill=col + (255,))


def block_sprite():
    w, h = 560, 440
    r = np.random.default_rng(14)
    img = np.zeros((h, w, 3), "float32")
    img[:] = (196, 128, 126)
    img += r.normal(0, 16, img.shape)
    for _ in range(900):
        x, y = int(r.uniform(0, w)), int(r.uniform(0, h))
        img[y:y + 3, x:x + 3] = r.choice([60, 230, 150], size=3) if r.random() < 0.5 else (70, 40, 40)
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.8)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=20, fill=255)
    im.putalpha(m)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=20, outline=(255, 220, 220, 255), width=5)
    return im


BLOCK = block_sprite()
BLOCK_G = soft_glow(560, 440, (255, 150, 120), 30, 0.6, 20)


def glyph(d, kind, cx, cy, s, col=(70, 20, 18, 255)):
    w = max(4, int(s * 0.09))
    if kind == 0:    # ojo
        d.ellipse((cx - s * .5, cy - s * .25, cx + s * .5, cy + s * .25), outline=col, width=w)
        d.ellipse((cx - s * .14, cy - s * .14, cx + s * .14, cy + s * .14), fill=col)
    elif kind == 1:  # ankh
        d.ellipse((cx - s * .22, cy - s * .5, cx + s * .22, cy - s * .06), outline=col, width=w)
        d.line((cx, cy - s * .06, cx, cy + s * .5), fill=col, width=w)
        d.line((cx - s * .3, cy + s * .12, cx + s * .3, cy + s * .12), fill=col, width=w)
    elif kind == 2:  # disco solar
        d.ellipse((cx - s * .3, cy - s * .3, cx + s * .3, cy + s * .3), outline=col, width=w)
        d.ellipse((cx - s * .09, cy - s * .09, cx + s * .09, cy + s * .09), fill=col)
        for k in range(8):
            a = k * math.pi / 4
            d.line((cx + s * .36 * math.cos(a), cy + s * .36 * math.sin(a), cx + s * .5 * math.cos(a), cy + s * .5 * math.sin(a)), fill=col, width=w)
    elif kind == 3:  # agua
        for k in range(3):
            y = cy - s * .3 + k * s * .3
            pts = [(cx - s * .5 + i * s / 12, y + math.sin(i * 1.3) * s * .08) for i in range(13)]
            d.line(pts, fill=col, width=w)
    elif kind == 4:  # pájaro
        d.polygon([(cx - s * .5, cy + s * .1), (cx - s * .1, cy - s * .3), (cx + s * .35, cy - s * .2), (cx + s * .5, cy - s * .35), (cx + s * .3, cy), (cx + s * .1, cy + s * .35), (cx - s * .2, cy + s * .3)], outline=col, width=w)
    else:            # caña
        d.line((cx, cy + s * .5, cx, cy - s * .4), fill=col, width=w)
        d.line((cx, cy - s * .1, cx - s * .3, cy - s * .35), fill=col, width=w)
        d.line((cx, cy - s * .1, cx + s * .3, cy - s * .35), fill=col, width=w)


# ------------------------------------------------------------------ escenas
def background(t, dim):
    cv = BG.copy()
    for x0, y0, sp, ph, c in PARTS:
        x = (x0 + sp * t) % (W + 200) - 100
        y = y0 + 25 * math.sin(ph + t * 0.9)
        a = 0.30 + 0.35 * math.sin(ph * 3 + t * 2.4)
        s = SANDS[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * a)))
    return cv


def hook(cv, t):
    s1 = C.SC_T[0][1]
    out = e_inout(prog(t, s1 - 0.4, s1 + 0.1))
    ta, tf = C.wd(0, "agricultor"), C.wd(0, "faraón")
    pin = e_out(prog(t, 0.0, 0.6))
    p = e_inout(prog(t, ta + 0.1, tf + 0.3))
    z = 1.9 - 0.65 * p
    to = hero_view(cv, 250 + 560 * p, 930 - 40 * p, z, alpha=pin * (1 - out), y_dest=250 - round(500 * out))
    if out < 0.5:
        lay = new_layer()
        d = ImageDraw.Draw(lay)
        # retícula sobre el agricultor y luego sobre la cabeza
        pa = e_out(prog(t, ta - 0.1, ta + 0.35)) * (1 - e_out(prog(t, tf - 0.5, tf - 0.2)))
        if pa > 0:
            sx, sy = to(310, 850)
            r = 150 * (0.7 + 0.3 * pa)
            d.ellipse((sx - r, sy - r, sx + r, sy + r), outline=(255, 245, 220, int(255 * pa)), width=6)
        pf = e_out(prog(t, tf - 0.2, tf + 0.3))
        if pf > 0:
            sx, sy = to(800, 880)
            r = 330 * z * 0.946 * 0.55 * (0.8 + 0.2 * pf)
            for k in range(14):
                a0 = k * 25.7 + t * 90
                d.arc((sx - r, sy - r, sx + r, sy + r), a0, a0 + 14, fill=GOLDC + (int(255 * pf),), width=8)
        comp(cv, lay, 1 - out * 2)
        if pa > 0.2:
            sx, sy = to(310, 850)
            blit(cv, S_AGR, sx + 40, sy - 190, alpha=pa * (1 - out))
        if pf > 0.2:
            sx, sy = to(800, 880)
            blit(cv, S_RAM, sx, sy - 330 * z * 0.946 * 0.55 - 36, alpha=pf * (1 - out))
    blit(cv, S_ILU, 230, 925, alpha=0.9 * pin * (1 - out))
    p1 = e_back(prog(t, 0.40, 0.80))
    dx, dy = shake(t, 0.62, 22, 8)
    blit(cv, S_T1, 540 + dx, 1020 + dy - 800 * out, scale=0.9 * min(960 / w_t1, 1) * (1 + 1.1 * (1 - p1)), alpha=e_out(prog(t, 0.40, 0.55)) * (1 - out))
    p2 = e_back(prog(t, 0.75, 1.15))
    dx2, dy2 = shake(t, 0.95, 20, 8)
    blit(cv, S_T2, 540 + dx2, 1228 + dy2 - 800 * out, scale=min(940 / w_t2, 1) * (1 + 1.0 * (1 - p2)), alpha=e_out(prog(t, 0.75, 0.9)) * (1 - out))


def ramses(cv, t):
    a, ain = C.sw(t, 1)
    if a <= 0.01:
        return
    panel(cv, a, T_RAMSES, 0.96 + 0.04 * ain)
    s0 = C.SC_T[1][0]
    p = e_back(prog(t, s0 + 0.1, s0 + 0.6))
    blit(cv, TILE_GLOW, 300, 640, scale=0.72 * p, alpha=a * 0.8 * clamp(p * 2))
    blit(cv, TILE_HEAD_S, 300, 640, scale=1.0 * p, alpha=a * clamp(p * 2))
    tp = C.wd(1, "reyes")
    pr = e_back(prog(t, tp - 0.1, tp + 0.4))
    blit(cv, S_PODER, 745, 590, scale=min(380 / S_PODER.width, 1) * pr, alpha=a * clamp(pr * 2))
    blit(cv, S_PODER2, 745, 650, scale=min(380 / S_PODER2.width, 1) * pr, alpha=a * clamp(pr * 2))
    # línea de tiempo del Imperio Nuevo
    tl = C.wd(1, "ramsés")
    pt = e_out(prog(t, s0 + 0.9, s0 + 1.5))
    blit(cv, S_IMP, 540, 925, alpha=a * pt)
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    x0_, x1_, yb_ = 120, 960, 1030
    d.line((x0_, yb_, x0_ + (x1_ - x0_) * pt, yb_), fill=SAND + (255,), width=14)
    d.ellipse((x0_ - 10, yb_ - 10, x0_ + 10, yb_ + 10), fill=SAND + (255,))
    d.ellipse((x1_ - 10, yb_ - 10, x1_ + 10, yb_ + 10), fill=SAND + (255,))
    mx = x0_ + (x1_ - x0_) * (1570 - 1303) / (1570 - 1069)
    pm = e_back(prog(t, s0 + 1.8, s0 + 2.3))
    if pm > 0:
        d.polygon([(mx, yb_ + 8), (mx - 20, yb_ + 52 * pm), (mx + 20, yb_ + 52 * pm)], fill=GOLDC + (255,))
    comp(cv, lay, a)
    blit(cv, S_Y1570, x0_ + 5, yb_ + 38, alpha=a * pt)
    blit(cv, S_Y1069, x1_ - 5, yb_ + 38, alpha=a * pt)
    blit(cv, S_NACE, mx, yb_ + 100, alpha=a * clamp(pm * 2))


def mapa(cv, t):
    a, ain = C.sw(t, 2)
    if a <= 0.01:
        return
    panel(cv, a, T_MAPA, 0.96 + 0.04 * ain)
    s0 = C.SC_T[2][0]
    pm = e_out(prog(t, s0 + 0.1, s0 + 0.8))
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    pts = [mp(*q) for q in EGIPTO]
    d.polygon(pts, fill=(58, 40, 18, 255), outline=SAND + (255,), width=5)
    for seg, w_, col in ((NILO, 9, (80, 190, 225)), (RAMA_ROSETA, 7, (80, 190, 225)), (RAMA_DAMIETA, 7, (80, 190, 225))):
        d.line([mp(*q) for q in seg], fill=col + (255,), width=w_, joint="curve")
    comp(cv, lay, a * pm)
    blit(cv, S_EGIPTO, mp(28.2, 26.3)[0], mp(28.2, 26.3)[1], alpha=a * pm * 0.9)
    tn = C.wd(2, "delta")
    pd_ = e_out(prog(t, tn - 0.1, tn + 0.4))
    blit(cv, S_DELTA, mp(34.0, 29.6)[0] - 40, mp(34.0, 29.6)[1] + 80, alpha=a * pd_)
    tb = C.wd(2, "behbeit")
    pb = e_back(prog(t, tb - 0.1, tb + 0.4))
    bx, by = mp(*BEH)
    if pb > 0:
        ring = prog((t - tb) % 1.4, 0, 1.4)
        lay = new_layer()
        d = ImageDraw.Draw(lay)
        r = 24 + 120 * ring
        d.ellipse((bx - r, by - r, bx + r, by + r), outline=GOLDC + (int(230 * (1 - ring)),), width=5)
        d.ellipse((bx - 14, by - 14, bx + 14, by + 14), fill=GOLDC + (255,), outline=(255, 255, 255, 255), width=3)
        comp(cv, lay, a * clamp(pb))
        blit(cv, S_BEH, bx + 40 + S_BEH.width / 2 - 20, by + 130, scale=pb, alpha=a * clamp(pb * 2))
        blit(cv, S_GHA, 540, 1160, alpha=a * prog(t, tb + 0.2, tb + 0.7))


def excavacion(cv, t):
    a, ain = C.sw(t, 3)
    if a <= 0.01:
        return
    panel(cv, a, T_EXC, 0.96 + 0.04 * ain)
    s0 = C.SC_T[3][0]
    p = e_back(prog(t, s0 + 0.1, s0 + 0.6), 1.3)
    z = 1.0 + 0.05 * prog(t, s0, C.SC_T[3][1])
    blit(cv, TILE_FARM, 540, 640, scale=0.96 * p * z, alpha=a * clamp(p * 2))
    ta = C.wd(3, "autoridades")
    pa = e_out(prog(t, ta - 0.1, ta + 0.4))
    blit(cv, S_AVISO, 540, 1010, alpha=a * pa)
    tc = C.wd(3, "consejo")
    pc = e_back(prog(t, tc - 0.1, tc + 0.4))
    badge = rrect(880, 100, (160, 30, 30), (110, 10, 10), 20)
    badge.alpha_composite(S_CSA if S_CSA.width <= 840 else S_CSA.resize((840, round(S_CSA.height * 840 / S_CSA.width))), (20, (100 - S_CSA.height) // 2))
    blit(cv, badge, 540, 1110, scale=pc, alpha=a * clamp(pc * 2))


def cabeza(cv, t):
    a, ain = C.sw(t, 4)
    if a <= 0.01:
        return
    panel(cv, a, T_CAB, 0.96 + 0.04 * ain)
    s0 = C.SC_T[4][0]
    p = e_back(prog(t, s0 + 0.1, s0 + 0.6), 1.3)
    cx, cy = 480, 660
    blit(cv, TILE_GLOW, cx, cy, alpha=a * 0.7 * clamp(p * 2))
    blit(cv, TILE_HEAD, cx, cy, scale=0.92 * p, alpha=a * clamp(p * 2))
    tm = C.wd(4, "metro")
    pm = e_out(prog(t, tm - 0.3, tm + 0.5))
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    if pm > 0:
        x = 815
        d.line((x, 400, x, 400 + 520 * pm), fill=(255, 245, 220, 255), width=7)
        d.line((x - 22, 400, x + 22, 400), fill=(255, 245, 220, 255), width=7)
        if pm > 0.95:
            d.line((x - 22, 920, x + 22, 920), fill=(255, 245, 220, 255), width=7)
    td = C.wd(4, "doble")
    pd_ = e_out(prog(t, td - 0.1, td + 0.4))
    if pd_ > 0:
        d.line((600, 395, 600 + 200 * pd_, 395 - 20 * pd_), fill=GOLDC + (255,), width=6)
        d.ellipse((590, 385, 610, 405), fill=GOLDC + (255,))
    comp(cv, lay, a)
    blit(cv, S_METRO, 915, 660, alpha=a * clamp(pm * 2))
    blit(cv, S_DOBLE, 540, 1010, scale=min(560 / S_DOBLE.width, 1) * e_back(pd_), alpha=a * clamp(pd_ * 2))
    blit(cv, S_DOBLE2, 540, 1090, alpha=a * pd_)


def escala(cv, t, i, second):
    a, ain = C.sw(t, i)
    if a <= 0.01:
        return
    panel(cv, a, T_SEG if second else T_ALT, 0.96 + 0.04 * ain)
    s0 = C.SC_T[i][0]
    ground = 1150
    H8, H2, HP = 8.2 * 70, 2.4 * 70, 1.7 * 70
    if second:
        g = 1.0
    else:
        g = e_out(prog(t, C.wd(i, "completa") - 0.2, C.wd(i, "ocho") + 0.6))
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    d.line((120, ground, 960, ground), fill=SAND + (255,), width=6)
    draw_statue(lay, d, H8 * g, 740, ground, stripes=True)
    person(d, 230, ground, HP)
    pm = e_out(prog(t, s0 + 0.2, s0 + 0.7))
    if not second:
        tt = C.wd(i, "ocho")
        pr = e_out(prog(t, tt - 0.2, tt + 0.5))
        if pr > 0:
            d.line((905, ground, 905, ground - H8 * pr), fill=(255, 245, 220, 255), width=6)
            d.line((885, ground - H8 * pr, 925, ground - H8 * pr), fill=(255, 245, 220, 255), width=6)
        # cabeza = 1,5 m dentro de la estatua
        ph = e_out(prog(t, s0 + 1.2, s0 + 1.8))
        if ph > 0:
            top, bot = ground - H8 * 0.93, ground - H8 * 0.76
            d.rectangle((650, top, 830, bot), outline=GOLDC + (int(255 * ph),), width=5)
    else:
        ts = C.wd(i, "segunda")
        p2 = e_back(prog(t, ts - 0.1, ts + 0.4))
        draw_statue(lay, d, H2 * clamp(p2), 430, ground, col=(250, 235, 200), stripes=True)
        tr = C.wd(i, "tocado")
        pn = e_out(prog(t, tr - 0.1, tr + 0.4))
        if pn > 0:
            d.line((470, ground - H2 * 0.88, 560, ground - H2 * 0.88 - 140 * pn), fill=GOLDC + (255,), width=5)
    comp(cv, lay, a * pm)
    blit(cv, S_PERSONA, 230, ground + 40, alpha=a * pm)
    if not second:
        tt = C.wd(i, "ocho")
        ph8 = e_back(prog(t, tt - 0.1, tt + 0.35))
        dx, dy = shake(t, tt + 0.3, 14, 9)
        blit(cv, S_H8, 540 + dx - 100, 470 + dy, scale=min(520 / w_h8, 1) * ph8, alpha=a * clamp(ph8 * 2))
        blit(cv, S_ALTURA, 540 - 100, 555, alpha=a * prog(t, tt + 0.3, tt + 0.7))
        blit(cv, S_CABEZA, 540 - 20, 1195, alpha=a * prog(t, s0 + 1.4, s0 + 1.9))
    else:
        tr = C.wd(i, "dos")
        p2e = e_back(prog(t, tr - 0.1, tr + 0.35))
        blit(cv, S_2E, 530, 470, scale=min(520 / w_2e, 1) * p2e, alpha=a * clamp(p2e * 2))
        blit(cv, S_2E2, 530, 550, alpha=a * prog(t, tr + 0.2, tr + 0.6))
        tn = C.wd(i, "rayas")
        blit(cv, S_NEMES, 600, 1195, alpha=a * e_out(prog(t, tn - 0.5, tn)))


def bloque(cv, t):
    a, ain = C.sw(t, 7)
    if a <= 0.01:
        return
    panel(cv, a, T_BLO, 0.96 + 0.04 * ain)
    s0 = C.SC_T[7][0]
    tb = C.wd(7, "bloque")
    p = e_back(prog(t, tb - 0.1, tb + 0.5), 1.3)
    cx, cy = 540, 640
    blit(cv, BLOCK_G, cx, cy, scale=p, alpha=a * 0.7 * clamp(p * 2))
    blit(cv, BLOCK, cx, cy, scale=p, alpha=a * clamp(p * 2))
    tj = C.wd(7, "jeroglíficos")
    lay = new_layer()
    d = ImageDraw.Draw(lay)
    k = 0
    for r in range(3):
        for c in range(4):
            gx, gy = cx - 195 + c * 130, cy - 130 + r * 130
            pg = e_out(prog(t, tj + 0.07 * (k), tj + 0.07 * k + 0.35))
            if pg > 0:
                glyph(d, k % 6, gx, gy, 90 * pg)
            k += 1
    comp(cv, lay, a * clamp(p))
    blit(cv, S_GR, cx, cy + 250, alpha=a * clamp(p * 2))
    blit(cv, S_INS, cx, cy + 300, alpha=a * prog(t, tj + 0.5, tj + 0.9))
    tp = C.wd(7, "proclaman")
    pr = e_out(prog(t, tp - 0.1, tp + 0.4))
    blit(cv, S_REY, 540, 1010, scale=min(900 / S_REY.width, 1) * pr, alpha=a * pr)
    th = C.wd(7, "hijo")
    ph = e_back(prog(t, th - 0.05, th + 0.35))
    dx, dy = shake(t, th + 0.3, 16, 9)
    blit(cv, S_HIJO, 540 + dx, 1110 + dy, scale=ph, alpha=a * clamp(ph * 2))


def cierre(cv, t):
    s0 = C.SC_T[8][0]
    a = e_out(prog(t, s0, s0 + 0.4))
    if a <= 0.01:
        return
    beat = 1 + 0.03 * (abs(math.sin((t - s0) * 3.2)) ** 6)
    hero_view(cv, 700, 900, 1.1 * beat, alpha=a, y_dest=240)
    blit(cv, S_ILU, 230, 915, alpha=0.9 * a)
    tp = C.wd(8, "esperan")
    p1 = e_back(prog(t, tp - 0.05, tp + 0.45))
    dx, dy = shake(t, tp + 0.4, 16, 9)
    blit(cv, S_QM1, 540 + dx, 1005 + dy, scale=0.92 * min(960 / w_q1, 1) * p1, alpha=a * clamp(p1 * 2))
    td = C.wd(8, "delta")
    p2 = e_back(prog(t, td - 0.4, td + 0.2))
    dx, dy = shake(t, td + 0.15, 20, 8)
    blit(cv, S_QM2, 540 + dx, 1190 + dy, scale=0.92 * min(960 / w_q2, 1) * p2, alpha=a * clamp(p2 * 2))


def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0
    scenes = [hook, ramses, mapa, excavacion, cabeza, lambda cv, t: escala(cv, t, 5, False), lambda cv, t: escala(cv, t, 6, True), bloque, cierre]

    def dim(t):
        return 0.0 if t < ctx.SC_T[1][0] - 0.2 else 0.7

    def sfx(sput, ctx):
        SC_T = ctx.SC_T
        sput(rumble(2.0, 6), 0.0, 0.7)
        sput(hit(70, 1.2, 0.8), 0.45, 0.8)
        sput(whoosh(0.4, True, 3), 0.40, 0.4)
        sput(blip(1100), wd(0, "agricultor"), 0.5)
        sput(riser(0.9), wd(0, "faraón") - 0.8, 0.5)
        sput(hit(60, 1.4, 0.9), wd(0, "faraón") + 0.2, 1.0)
        sput(hit(85, 0.9, 0.7), wd(0, "gigante") + 0.3, 0.8)
        for i in range(1, 9):
            sput(whoosh(0.45, True, 10 + i), SC_T[i][0] - 0.1, 0.45)
            sput(hit(100, 0.5, 0.3), SC_T[i][0] + 0.12, 0.45)
        sput(blip(1300), wd(1, "reyes"), 0.5)
        sput(ping(), wd(2, "behbeit") + 0.2, 0.6)
        sput(whoosh(0.5, False, 5), wd(3, "avisó"), 0.3)
        sput(whoosh(0.4, True, 6), wd(3, "arqueólogos"), 0.3)
        sput(hit(90, 0.6, 0.5), wd(3, "consejo"), 0.7)
        sput(hit(70, 0.9, 0.8), wd(4, "doble"), 0.9)
        sput(blip(900), wd(4, "metro"), 0.5)
        sput(riser(1.4), wd(5, "completa") - 0.2, 0.55)
        sput(hit(60, 1.2, 0.9), wd(5, "ocho"), 1.0)
        sput(hit(90, 0.7, 0.5), wd(6, "segunda"), 0.8)
        sput(blip(1200), wd(6, "tocado"), 0.5)
        sput(whoosh(0.5, True, 7), wd(7, "jeroglíficos") - 0.1, 0.35)
        sput(hit(70, 1.0, 0.8), wd(7, "hijo"), 0.9)
        sput(thump(1.0), wd(8, "esperan"), 0.8)
        sput(hit(70, 1.0, 0.9), wd(8, "delta") + 0.15, 1.0)
        sput(ping(), wd(8, "síguenos") + 0.35, 0.9)

    impacts = [0.45, wd(0, "faraón") + 0.2, wd(0, "gigante") + 0.3, wd(4, "doble"), wd(5, "ocho") + 0.3, wd(6, "segunda"), wd(7, "hijo") + 0.3, wd(8, "delta") + 0.15]
    flashes = [(0.42, 0.5), (wd(0, "faraón") + 0.2, 0.5), (wd(5, "ocho"), 0.3)]
    return Spec(background, scenes, impacts=impacts, flashes=flashes, sfx=sfx, dim=dim, pad=(55, 73.4, 98, 123.5))
