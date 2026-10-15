"""Historia: Científicos perforan la formación Durupınar (Turquía) en busca del Arca de Noé.

Short de ~45 s. Fuentes: Fox News, Popular Mechanics, Newsweek. Todo lo dudoso va atribuido a los investigadores.
Escenas (una por línea del guion): gancho · lugar · perforación · roca vs tierra · georradar · materia orgánica · geólogos · carbono 14.
"""
import math, random
from lib import *  # utilidades, paleta, panel, sellos, sonido, Spec

C = None  # contexto de la historia (tiempos de la voz); lo asigna setup()

# ------------------------------------------------------------------ paisaje
LW, LH = 1500, 760


def ridge(width, base, amp, rough, seed, octaves=6):
    rng = np.random.default_rng(seed)
    h = np.zeros(width)
    for o in range(octaves):
        n = 2 ** (o + 2)
        pts = rng.uniform(-1, 1, n + 1)
        h += np.interp(np.linspace(0, n, width), np.arange(n + 1), pts) * (rough ** o)
    h = (h - h.min()) / (h.max() - h.min())
    return base + amp * h


def cone(width, c, peak, half, p=1.25, seed=3):
    x = np.arange(width)
    rng = np.random.default_rng(seed)
    noise = np.interp(x, np.linspace(0, width, 60), rng.uniform(-1, 1, 60)) * 10
    base = np.clip(1 - np.abs(x - c) / half, 0, None)
    return np.clip(peak * base ** p + noise * (np.abs(x - c) < half) * (base > 0.02), 0, None)


def layer_poly(heights, c1, c2):
    top = LH - heights.max()
    im = vgrad(LW, LH, c1, c2).convert("RGBA")
    m = Image.new("L", (LW, LH), 0)
    pts = [(0, LH)] + [(x, LH - heights[x]) for x in range(LW)] + [(LW - 1, LH)]
    ImageDraw.Draw(m).polygon(pts, fill=255)
    im.putalpha(m)
    return im, m


far_h = np.maximum.reduce([ridge(LW, 120, 90, 0.55, 11), cone(LW, 560, 560, 620), cone(LW, 1120, 360, 360, seed=5)])
LAND = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
far, far_mask = layer_poly(far_h, (74, 108, 138), (20, 40, 58))
# nieve en las cumbres
snow_thr = 380
sm = np.zeros((LH, LW), "uint8")
for x in range(LW):
    if far_h[x] > snow_thr:
        y_top, y_thr = int(LH - far_h[x]), int(LH - snow_thr)
        sm[y_top:y_thr, x] = 255
snow_mask = Image.fromarray(sm).filter(ImageFilter.GaussianBlur(2))
snow = Image.new("RGBA", (LW, LH), (214, 232, 246, 0))
snow.putalpha(ImageChops.multiply(snow_mask, far_mask).point(lambda v: int(v * 0.92)))
far = Image.alpha_composite(far, snow)
rim = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
ImageDraw.Draw(rim).line([(x, LH - far_h[x]) for x in range(LW)], fill=(130, 215, 240, 190), width=3)
rim_glow = rim.filter(ImageFilter.GaussianBlur(5))
far = Image.alpha_composite(Image.alpha_composite(far, rim_glow), rim)
mid, _ = layer_poly(ridge(LW, 70, 150, 0.6, 21), (22, 50, 70), (8, 24, 38))
near, _ = layer_poly(ridge(LW, 20, 110, 0.62, 31), (8, 20, 30), (4, 10, 18))
LAND = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(LAND, far), mid), near)
LAND_Y = 1262  # borde inferior del paisaje

# casco del "arca"


def make_hull(w=800, h=250, col=AMBER, lw=7, fill=None):
    pts = [(20, 100), (640, 100), (790, 158), (640, 226), (110, 226), (20, 176)]
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.polygon(pts, outline=col + (255,), width=lw)
    d.rectangle((170, 40, 520, 100), outline=col + (255,), width=lw - 1)
    for yy in (138, 172, 206):
        d.line((60, yy, 610 + (yy - 138) // 2, yy), fill=col + (150,), width=3)
    g = lay.filter(ImageFilter.GaussianBlur(10))
    g2 = lay.filter(ImageFilter.GaussianBlur(24))
    out = Image.alpha_composite(Image.alpha_composite(g2, g), lay)
    return out


HULL = make_hull()
HULL_FILL = Image.new("L", HULL.size, 0)
ImageDraw.Draw(HULL_FILL).polygon([(20, 100), (640, 100), (790, 158), (640, 226), (110, 226), (20, 176)], fill=255)
ImageDraw.Draw(HULL_FILL).rectangle((170, 40, 520, 100), fill=255)

# niebla (tileable en horizontal)
_rng = np.random.default_rng(5)
_b = _rng.random((40, 54)).astype("float32")
_t3 = np.tile(_b, (1, 3))
_img = Image.fromarray((_t3 * 255).astype("uint8")).resize((3240, 620), Image.BICUBIC).filter(ImageFilter.GaussianBlur(70))
_a = np.asarray(_img, "float32")
_a = (_a - _a.min()) / (_a.max() - _a.min())
_a = np.clip((_a - 0.35) * 1.8, 0, 1)[:, 1080:2160]
FOG = Image.new("RGBA", (1080, 620), (150, 190, 210, 0))
FOG.putalpha(Image.fromarray((_a * 120).astype("uint8")))

# fondo
yy, xx = np.mgrid[0:H, 0:W].astype("float32")
v = (yy / H)[..., None]
bg = (1 - v) * np.array([3, 6, 14], "float32") + v * np.array([4, 10, 18], "float32")
for cx, cy, rad, col, k in ((820, 380, 780, (30, 110, 140), 0.50), (300, 1120, 600, (150, 80, 10), 0.20), (540, 1700, 700, (10, 40, 60), 0.35)):
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) / rad
    bg += (np.clip(1 - d, 0, 1) ** 2)[..., None] * np.array(col, "float32") * k
vig = np.clip(1 - (np.sqrt(((xx - W / 2) / (W * 0.78)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)) ** 2.2, 0.3, 1)
bg *= vig[..., None]
_r = np.random.default_rng(9)
for _ in range(150):
    sx, sy = int(_r.uniform(0, W)), int(_r.uniform(0, 900))
    bg[sy:sy + 2, sx:sx + 2] += _r.uniform(40, 150)
bg[::6] *= 0.94
BG = Image.fromarray(np.clip(bg, 0, 255).astype("uint8"))
MOON = Image.new("RGBA", (260, 260), (0, 0, 0, 0))
_mm = Image.new("L", (260, 260), 0)
ImageDraw.Draw(_mm).ellipse((80, 80, 180, 180), fill=255)
MOON = Image.merge("RGBA", (Image.new("L", (260, 260), 200), Image.new("L", (260, 260), 235), Image.new("L", (260, 260), 245), _mm.filter(ImageFilter.GaussianBlur(5))))
MOON_G = Image.merge("RGBA", (Image.new("L", (260, 260), 120), Image.new("L", (260, 260), 200), Image.new("L", (260, 260), 230), _mm.filter(ImageFilter.GaussianBlur(40)).point(lambda v: int(v * 0.8))))


def glow_dot(col, size):
    im = Image.new("RGBA", (size * 4, size * 4), col + (0,))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse((size * 1.5, size * 1.5, size * 2.5, size * 2.5), fill=255)
    im.putalpha(m.filter(ImageFilter.GaussianBlur(size * 0.9)))
    return im


EMB = [glow_dot((255, 170, 40), 7), glow_dot((255, 210, 120), 5), glow_dot((110, 210, 235), 6)]
_rg = random.Random(3)
PARTS = [(_rg.uniform(0, W), _rg.uniform(0, H + 200), _rg.uniform(25, 90), _rg.uniform(0, 6.28), _rg.choice([0, 0, 1, 2])) for _ in range(55)]

# ------------------------------------------------------------------ sprites de texto
S_Q1, wq1, hq1 = rtext("¿EL ARCA", ANTON, 330, grad=WHITE, stroke=7, stroke_col=(4, 10, 20), glow=((120, 200, 255), 22, 0.6), shadow=(0, 12, 9, 0.7))
S_Q2, wq2, hq2 = rtext("DE NOÉ?", ANTON, 330, grad=GOLD, stroke=7, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 12, 9, 0.7))
S_SUB1, _, _ = rtext("PERFORARON LA FORMACIÓN", B7, 62, fill=(255, 200, 60), shadow=(0, 4, 3, 0.7))
S_TURK, _, _ = rtext("ESTE DE TURQUÍA", ANTON, 84, grad=WHITE, stroke=4, stroke_col=(4, 10, 20), glow=((120, 200, 255), 14, 0.5), shadow=(0, 8, 6, 0.7))
S_ARARAT, _, _ = rtext("MONTE ARARAT · 5.137 m", B7, 48, fill=(210, 235, 250), shadow=(0, 4, 3, 0.8))
S_DURU, _, _ = rtext("FORMACIÓN DURUPINAR", B7, 50, fill=(255, 200, 60), shadow=(0, 4, 3, 0.8))
S_BARCO, _, _ = rtext("COLINA CON FORMA DE BARCO", B6, 42, fill=(230, 238, 248), shadow=(0, 4, 3, 0.8))

T_PERF = S("PERFORACIÓN PROFUNDA", B7, 62, fill=AMBER, shadow=(0, 4, 3, 0.7))
T_FIND = S("¿QUÉ HAY BAJO LA FORMACIÓN?", B7, 60, fill=AMBER, shadow=(0, 4, 3, 0.7))
T_RADAR = S("GEORRADAR · ANOMALÍAS", B7, 62, fill=AMBER, shadow=(0, 4, 3, 0.7))
T_ORG = S("MATERIA ORGÁNICA", B7, 62, fill=AMBER, shadow=(0, 4, 3, 0.7))
T_GEO = S("LOS GEÓLOGOS DUDAN", B7, 62, fill=AMBER, shadow=(0, 4, 3, 0.7))
T_C14 = S("DATACIÓN POR RADIOCARBONO", B7, 54, fill=TEAL, shadow=(0, 4, 3, 0.7))
LBL = lambda s, c=(200, 212, 228), z=40: S(s, B6, z, fill=c)
T_DEPTH = S("PROFUNDIDAD", B7, 44, fill=(160, 180, 205))
T_SAMP = S("MUESTRAS DE SUELO", B7, 44, fill=(160, 180, 205))
T_SEGUN = S("Según uno de los investigadores", B6, 42, fill=(170, 186, 208))
T_ROCA = S("ROCA SÓLIDA", ANTON, 66, grad=((235, 240, 250), (150, 160, 180)), shadow=(0, 5, 4, 0.7))
T_ROCA2 = S("lo que esperaban los geólogos", B6, 38, fill=(170, 186, 208))
T_TIERRA = S("CAPAS DE TIERRA", ANTON, 66, grad=GOLD, shadow=(0, 5, 4, 0.7), glow=((255, 170, 0), 14, 0.6))
T_TIERRA2 = S("lo que sacaron las sondas", B6, 38, fill=(170, 186, 208))
T_NOENC, _, _ = rtext("NO ENCONTRADA", B7, 52, fill=(255, 90, 90))
T_NOENC = T_NOENC
T_MENOS = S("MÁS CARBONO Y MATERIA ORGÁNICA DENTRO", B7, 50, fill=(255, 205, 110), shadow=(0, 4, 3, 0.7))
T_MAD = S("¿MADERA DEL ARCA?", ANTON, 118, grad=WHITE, stroke=5, stroke_col=(4, 10, 20), glow=((255, 170, 0), 18, 0.7), shadow=(0, 8, 6, 0.7))
_tl = S("No son fotos: son lecturas de radar", B7, 50, fill=(255, 190, 150))
T_LIN = Image.new("RGBA", (_tl.width + 70, _tl.height + 40), (0, 0, 0, 0))
ImageDraw.Draw(T_LIN).rounded_rectangle((4, 4, T_LIN.width - 5, T_LIN.height - 5), radius=22, fill=(60, 10, 10, 235), outline=(255, 120, 90, 255), width=5)
T_LIN.alpha_composite(_tl, (35, 20))
T_N = [S(f"NIVEL {i}", B7, 46, fill=AMBER, shadow=(0, 3, 2, 0.8)) for i in (1, 2, 3)]
T_CAV = S("CAVIDADES", B7, 40, fill=TEAL, shadow=(0, 3, 2, 0.8))
T_REC = S("LÍNEAS RECTAS", B7, 40, fill=TEAL, shadow=(0, 3, 2, 0.8))
T_CAMB, _, _ = rtext("CAMBIOS EN LA TIERRA", B7, 56, fill=(210, 224, 240))
T_NOPR, wnopr, _ = rtext("NO PRUEBAN", ANTON, 130, grad=GOLD, stroke=5, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.7))
T_UNB, wunb, _ = rtext("UN BARCO", ANTON, 130, grad=WHITE, stroke=5, stroke_col=(4, 10, 20), glow=((120, 200, 255), 16, 0.5), shadow=(0, 8, 6, 0.7))
T_C14B = S("CARBONO 14", ANTON, 120, grad=WHITE, stroke=5, stroke_col=(4, 10, 20), glow=((90, 220, 230), 20, 0.7), shadow=(0, 8, 6, 0.7))
T_LEY, wley, _ = rtext("¿LEYENDA?", ANTON, 140, grad=WHITE, stroke=5, stroke_col=(4, 10, 20), glow=((120, 200, 255), 16, 0.5), shadow=(0, 8, 6, 0.7))
T_DES, wdes, _ = rtext("¿DESCUBRIMIENTO?", ANTON, 108, grad=GOLD, stroke=5, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.7))


ST_SINCONF = make_stamp("SIN CONFIRMAR", (255, 70, 70))
ST_NATURAL = make_stamp("FORMACIÓN NATURAL", (110, 230, 215), 80, (0, 30, 34, 225))

# ------------------------------------------------------------------ gráficos específicos
# georradar
RW, RH = 880, 640
_rr = np.random.default_rng(12)
rad = _rr.normal(0, 0.10, (RH, RW)).astype("float32")
rad += 0.10 * np.sin(np.arange(RH)[:, None] * 0.045)
xs = np.arange(RW)
for yb, amp, inten in ((120, 6, 0.35), (170, 7, 0.9), (310, 8, 0.9), (450, 7, 0.9), (560, 5, 0.3)):
    wob = yb + amp * np.sin(xs * 0.011 + yb) + 3 * np.sin(xs * 0.05)
    for x in range(RW):
        y = int(wob[x])
        rad[max(0, y - 3):y + 4, x] += inten * np.exp(-((np.arange(max(0, y - 3), y + 4) - wob[x]) ** 2) / 4)
for x0, y0 in ((250, 230), (560, 380), (700, 240), (400, 520), (140, 400)):
    y = y0 + 0.32 * (np.sqrt((xs - x0) ** 2 + 45 ** 2) - 45)
    for x in range(RW):
        yi = int(y[x])
        if yi < RH - 4:
            rad[yi - 2:yi + 3, x] += 0.55 * np.exp(-abs(x - x0) / 260)
rad *= np.exp(-np.arange(RH)[:, None] / 900)
rad = np.clip(rad, 0, 1.2) / 1.2
rad = np.clip(rad ** 0.6 * 1.25, 0, 1)
cm = np.zeros((RH, RW, 3), "float32")
lo, mi, hi = np.array([3, 10, 20.0]), np.array([26, 150, 172.0]), np.array([255, 226, 140.0])
a1 = np.clip(rad / 0.35, 0, 1)[..., None]
a2 = np.clip((rad - 0.55) / 0.40, 0, 1)[..., None]
cm = lo * (1 - a1) + mi * a1
cm = cm * (1 - a2) + hi * a2
cm[::3] *= 0.9
RADAR = Image.fromarray(np.clip(cm, 0, 255).astype("uint8"))
RADAR_X0, RADAR_Y0 = 100, 330


def strata_img(w, h, seed, kind="soil"):
    r = np.random.default_rng(seed)
    img = np.zeros((h, w, 3), "float32")
    y = 0
    cols = [(96, 68, 46), (124, 90, 60), (80, 58, 40), (112, 82, 54), (88, 64, 46), (132, 98, 64)]
    i = 0
    while y < h:
        bh = int(r.uniform(34, 70))
        c = np.array(cols[i % len(cols)], "float32")
        img[y:y + bh] = c
        i += 1
        y += bh
    img += r.normal(0, 7, img.shape)
    wav = (np.sin(np.arange(w)[None, :] * 0.04 + np.arange(h)[:, None] * 0.02) * 6)[..., None]
    img += wav
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8"))


def rock_img(w, h, seed):
    r = np.random.default_rng(seed)
    img = np.full((h, w, 3), (118, 124, 134), "float32")
    img += r.normal(0, 9, img.shape)
    im = Image.fromarray(np.clip(img, 0, 255).astype("uint8"))
    d = ImageDraw.Draw(im)
    for yy_ in range(0, h, 70):
        d.line((0, yy_, w, yy_), fill=(70, 74, 84), width=3)
        off = 0 if (yy_ // 70) % 2 == 0 else 60
        for xx_ in range(off, w, 120):
            d.line((xx_, yy_, xx_, yy_ + 70), fill=(70, 74, 84), width=3)
    return im


def core_sprite(img, border):
    w, h = img.size
    spr = img.convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=34, fill=255)
    spr.putalpha(m)
    d = ImageDraw.Draw(spr)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=34, outline=border + (255,), width=6)
    shade = Image.new("L", (w, h), 0)
    ImageDraw.Draw(shade).rectangle((0, 0, int(w * 0.22), h), fill=70)
    ImageDraw.Draw(shade).rectangle((int(w * 0.80), 0, w, h), fill=90)
    shade = shade.filter(ImageFilter.GaussianBlur(24))
    dark = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dark.putalpha(ImageChops.multiply(shade, m))
    return Image.alpha_composite(spr, dark)


CORE_ROCK = core_sprite(rock_img(330, 560, 4), (190, 200, 215))
CORE_SOIL = core_sprite(strata_img(330, 560, 6), AMBER)
CORE_SOIL_G = soft_glow(330, 560, (255, 170, 0), 30, 0.8, 34)
STRIP = strata_img(330, 720, 8)


def vial(col):
    s = Image.new("RGBA", (26, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.rounded_rectangle((3, 12, 22, 66), radius=9, fill=col + (255,), outline=(235, 240, 250, 255), width=3)
    d.rectangle((1, 4, 24, 14), fill=(235, 240, 250, 255))
    return s


VIALS = [vial((150, 104, 64)), vial((190, 136, 74)), vial((110, 80, 52))]

# documento 1996
DOC = Image.new("RGBA", (400, 520), (0, 0, 0, 0))
_dd = ImageDraw.Draw(DOC)
_dd.rounded_rectangle((8, 8, 392, 512), radius=14, fill=(238, 240, 244, 255), outline=(150, 160, 175, 255), width=4)
_dd.rectangle((40, 50, 360, 64), fill=(60, 70, 90, 255))
for yy_ in range(100, 470, 34):
    _dd.line((40, yy_, 360 - (yy_ % 3) * 30, yy_), fill=(160, 168, 182, 255), width=7)
_t, _, _ = rtext("1996", ANTON, 110, fill=(40, 50, 70))
DOC.alpha_composite(_t, ((400 - _t.width) // 2, 135))
DOC_G = soft_glow(400, 520, (110, 230, 215), 22, 0.45, 14)
T_COL = S("COLLINS Y FASOLD", B7, 46, fill=(200, 215, 232), shadow=(0, 4, 3, 0.7))


def background(t, dim):
    cv = BG.copy()
    blit(cv, MOON_G, 830, 380, scale=2.2, alpha=0.7)
    blit(cv, MOON, 830, 380, scale=1.3)
    # paisaje con paralaje
    ls = 1.25 + 0.05 * t / C.DUR
    blit(cv, LAND, 540 - 18 * (t / 10) + 30, LAND_Y - LH * ls / 2 + 0, scale=ls, alpha=1.0 - dim * 0.62)
    # niebla
    sh1, sh2 = (t * 26) % 1080, (t * 52) % 1080
    for sh, y, a in ((sh1, 1010, 0.55), (sh2, 1130, 0.75)):
        for k in (-1, 0, 1):
            x = round(sh + 1080 * k)
            if -1080 < x < 1080:
                al = FOG.getchannel("A").point(lambda q, a=a: int(q * a * (1 - dim * 0.4)))
                cv.paste(FOG.convert("RGB"), (x, y), al)
    for x0, y0, sp, ph, c in PARTS:
        y = (y0 - sp * t) % (H + 200) - 100
        x = x0 + 30 * math.sin(ph + t * 0.8)
        a = 0.30 + 0.35 * math.sin(ph * 3 + t * 2.4)
        s = EMB[c]
        cv.paste(s.convert("RGB"), (round(x - s.width / 2), round(y - s.height / 2)), s.getchannel("A").point(lambda q, a=a: int(q * a)))
    return cv
def hook(cv, t):
    s0, s1 = C.SC_T[0]
    out = e_inout(prog(t, s1 - 0.45, s1 + 0.1))
    p1 = prog(t, 0.28, 0.62)
    dx, dy = shake(t, 0.30, 26, 8)
    blit(cv, S_Q1, 540 + dx, 560 + dy - 700 * out, scale=min(960 / wq1, 1) * (1 + 1.4 * (1 - e_back(p1))), alpha=e_out(prog(t, 0.28, 0.4)) * (1 - out))
    p2 = e_back(prog(t, 0.62, 0.95))
    dx2, dy2 = shake(t, 0.78, 22, 8)
    blit(cv, S_Q2, 540 + dx2, 830 + dy2 - 700 * out, scale=min(960 / wq2, 1) * (1 + 1.2 * (1 - p2)), alpha=e_out(prog(t, 0.62, 0.74)) * (1 - out))
    ts = C.wd(0, "perforar")
    p3 = e_out(prog(t, ts - 0.25, ts + 0.15))
    blit(cv, S_SUB1, 540 + 900 * (1 - p3) + 900 * out, 1030, alpha=clamp(p3 * 2) * (1 - out))
    d = ImageDraw.Draw(cv)
    d.rectangle((540 - 360 * p3, 1085, 540 + 360 * p3, 1090), fill=(255, 176, 0)) if out < 0.5 else None


def place(cv, t):
    a, ain = C.sw(t, 1)
    if a <= 0.01:
        return
    tt = C.wd(1, "turquía")
    blit(cv, S_TURK, 540, 318 - 40 * (1 - e_out(prog(t, tt - 0.1, tt + 0.3))), alpha=a * e_out(prog(t, tt - 0.1, tt + 0.25)))
    # etiqueta del monte Ararat: sigue a la cumbre del paisaje
    ta = C.wd(1, "ararat")
    p = e_out(prog(t, ta - 0.1, ta + 0.4))
    ls = 1.25 + 0.05 * t / C.DUR
    peak_x, peak_y = 540 - 1.8 * t + 30 + (560 - 750) * ls, LAND_Y - 560 * ls
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.line((peak_x + 8, peak_y - 4, peak_x + 8 + 130 * p, peak_y - 4 - 70 * p), fill=(210, 235, 250, 235), width=4)
    d.ellipse((peak_x - 4, peak_y - 16, peak_x + 20, peak_y + 8), fill=(210, 235, 250, 255))
    comp(cv, lay, a * p)
    blit(cv, S_ARARAT, peak_x + 150 + S_ARARAT.width / 2, peak_y - 76, alpha=a * p)
    # el casco del arca se dibuja sobre la colina
    tb = C.wd(1, "colina")
    hp = prog(t, tb - 0.05, tb + 1.1)
    if hp > 0:
        pulse = 0.85 + 0.15 * math.sin(t * 6)
        hx, hy = 600, 1075
        blit(cv, HULL, hx, hy, scale=0.95, alpha=a * clamp(hp * 1.5) * pulse)
        ring = prog((t - tb) % 1.4, 0, 1.4)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        r = 90 + 230 * ring
        d.ellipse((hx - r, hy + 20 - r * 0.42, hx + r, hy + 20 + r * 0.42), outline=(255, 176, 0, int(230 * (1 - ring))), width=5)
        comp(cv, lay, a * clamp(hp * 2))
        blit(cv, S_DURU, hx, hy - 150, alpha=a * clamp(hp * 2))
        blit(cv, S_BARCO, hx, hy + 150, alpha=a * clamp(hp * 2))


def drilling(cv, t):
    a, ain = C.sw(t, 2)
    if a <= 0.01:
        return
    s0 = C.SC_T[2][0]
    panel(cv, a, T_PERF, 0.96 + 0.04 * ain)
    gy0, scale_m = 430, 36  # superficie y píxeles por metro
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    # corte del suelo
    lay.paste(STRIP.convert("RGBA"), (230, gy0))
    d.rectangle((230, gy0 - 8, 560, gy0 + 2), fill=(70, 150, 80, 255))
    # escala de profundidad
    d.line((205, gy0, 205, gy0 + 20 * scale_m), fill=(170, 190, 215, 255), width=3)
    for m in (0, 5, 10, 15, 20):
        y = gy0 + m * scale_m
        d.line((190, y, 220, y), fill=(170, 190, 215, 255), width=4)
    dp = e_inout(prog(t, C.l0(2) + 0.15, C.l0(2) + 2.7))
    depth = 20 * dp
    yb = gy0 + depth * scale_m
    # torre
    for k, (x0, x1) in enumerate(((345, 445),)):
        d.polygon([(x0 + 10, gy0 - 8), (x1 - 10, gy0 - 8), (395, gy0 - 120)], outline=(200, 205, 215, 255), width=5)
        d.line((x0 + 30, gy0 - 8, 395 + (x0 - 345) * 0, gy0 - 70), fill=(200, 205, 215, 200), width=3)
        d.line((x1 - 30, gy0 - 8, 395, gy0 - 70), fill=(200, 205, 215, 200), width=3)
    d.rectangle((386, gy0 - 120, 404, gy0 - 8), fill=(255, 176, 0, 255))
    d.rectangle((388, gy0 - 8, 402, yb), fill=(255, 214, 90, 255))  # barra
    d.rectangle((380, gy0 + 2, 410, max(yb, gy0 + 3)), fill=(8, 12, 18, 230))
    d.rectangle((389, gy0 - 8, 401, yb), fill=(255, 214, 90, 255))
    comp(cv, lay, a)
    blit(cv, soft_glow(40, 40, (255, 190, 0), 22, 1.0, 20), 395, yb, alpha=a * 0.9 * (1 if depth > 0.2 else 0))
    for m in (0, 5, 10, 15, 20):
        blit(cv, LBL(f"{m} m", (170, 190, 215), 36), 150, gy0 + m * scale_m, alpha=a)
    # lecturas a la derecha
    blit(cv, T_DEPTH, 790, 470, alpha=a)
    dtxt = f"{depth:.1f}".replace(".", ",") + (" m" if dp < 0.995 else " m")
    num, _, _ = rtext(("~20 m" if dp >= 0.995 else dtxt), ANTON, 150, grad=GOLD, stroke=5, stroke_col=(110, 50, 0), glow=GLOW_A, shadow=(0, 8, 6, 0.7))
    blit(cv, num, 790, 585, alpha=a)
    blit(cv, T_SAMP, 790, 745, alpha=a)
    sp = e_out(prog(t, C.wd(2, "sacó") - 0.1, C.wd(2, "sacó") + 1.3))
    n = int(300 * sp)
    snum, _, _ = rtext(("300+" if sp >= 0.995 else str(n)), ANTON, 170, grad=WHITE, stroke=5, stroke_col=(4, 10, 20), glow=((120, 200, 255), 14, 0.5), shadow=(0, 8, 6, 0.7))
    blit(cv, snum, 790, 865, alpha=a)
    # viales
    for i in range(30):
        r_, c_ = divmod(i, 10)
        p = e_back(prog(t, C.wd(2, "sacó") - 0.1 + 0.035 * i, C.wd(2, "sacó") + 0.2 + 0.035 * i))
        blit(cv, VIALS[i % 3], 600 + c_ * 40, 995 + r_ * 70, scale=0.85 * p, alpha=a * clamp(p * 2))


def finding(cv, t):
    a, ain = C.sw(t, 3)
    if a <= 0.01:
        return
    panel(cv, a, T_FIND, 0.96 + 0.04 * ain)
    blit(cv, T_SEGUN, 540, 355, alpha=a)
    pl = e_back(prog(t, C.SC_T[3][0] + 0.1, C.SC_T[3][0] + 0.6))
    blit(cv, CORE_ROCK, 300, 680, scale=pl, alpha=a * clamp(pl * 2))
    pr = e_back(prog(t, C.wd(3, "solo") - 0.05, C.wd(3, "solo") + 0.45))
    glow = 0.7 + 0.3 * math.sin(t * 5)
    blit(cv, CORE_SOIL_G, 780, 680, scale=pr, alpha=a * clamp(pr * 2) * glow)
    blit(cv, CORE_SOIL, 780, 680, scale=pr, alpha=a * clamp(pr * 2))
    blit(cv, T_ROCA, 300, 1020, alpha=a * clamp(pl * 2))
    blit(cv, T_ROCA2, 300, 1080, alpha=a * clamp(pl * 2))
    blit(cv, T_TIERRA, 780, 1020, alpha=a * clamp(pr * 2))
    blit(cv, T_TIERRA2, 780, 1080, alpha=a * clamp(pr * 2))
    # tachón rojo sobre la roca
    tx = C.wd(3, "roca")
    ps = prog(t, tx - 0.05, tx + 0.28)
    if ps > 0:
        dx, dy = shake(t, tx + 0.25, 14, 9)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        c = (300 + dx, 680 + dy)
        q = min(ps * 2, 1)
        d.line((c[0] - 140, c[1] - 220, c[0] - 140 + 280 * q, c[1] - 220 + 440 * q), fill=(255, 50, 60, 255), width=26)
        if ps > 0.5:
            q2 = (ps - 0.5) * 2
            d.line((c[0] + 140, c[1] - 220, c[0] + 140 - 280 * q2, c[1] - 220 + 440 * q2), fill=(255, 50, 60, 255), width=26)
        comp(cv, lay, a)
        if ps >= 1:
            blit(cv, T_NOENC, 300, 1135, alpha=a)


def radar(cv, t):
    a, ain = C.sw(t, 4)
    if a <= 0.01:
        return
    panel(cv, a, T_RADAR, 0.96 + 0.04 * ain)
    tg = C.wd(4, "georradar")
    sp = prog(t, tg, tg + 3.0)
    cols = int(RW * sp)
    box = Image.new("RGBA", (RW + 16, RH + 16), (0, 0, 0, 0))
    ImageDraw.Draw(box).rounded_rectangle((0, 0, RW + 15, RH + 15), radius=12, fill=(3, 8, 14, 255), outline=TEAL + (255,), width=3)
    blit(cv, box, 540, 650, alpha=a)
    # posición real del radar (esquina sup-izq)
    rx, ry = 92, 322
    if cols > 2:
        part = RADAR.crop((0, 0, cols, RH))
        cv.paste(part, (rx + 8, ry + 8), Image.new("L", part.size, int(255 * a)))
        sx = rx + 8 + cols
        d = ImageDraw.Draw(cv)
        if sp < 1:
            d.rectangle((sx - 3, ry + 8, sx + 3, ry + 8 + RH), fill=(200, 255, 255))
    # marcas
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tl = C.wd(4, "líneas")
    pl = e_out(prog(t, tl, tl + 0.4))
    if pl > 0:
        d.line((rx + 40, ry + 8 + 120, rx + 40 + 300 * pl, ry + 8 + 120), fill=TEAL + (255,), width=5)
        blit(cv, T_REC, rx + 205, ry + 8 + 96, alpha=a * pl)
    tc = C.wd(4, "cavidades")
    pc = e_out(prog(t, tc, tc + 0.4))
    if pc > 0:
        for (cx_, cy_) in ((250, 230), (700, 240)):
            r = 46 * pc
            d.ellipse((rx + 8 + cx_ - r, ry + 8 + cy_ - r * 0.7, rx + 8 + cx_ + r, ry + 8 + cy_ + r * 0.7), outline=TEAL + (255,), width=5)
        blit(cv, T_CAV, rx + 8 + 250, ry + 8 + 270, alpha=a * pc)
    tn = C.wd(4, "niveles")
    for k, yb in enumerate((170, 310, 450)):
        pk = e_out(prog(t, tn - 0.55 + 0.28 * k, tn - 0.15 + 0.28 * k))
        if pk > 0:
            d.rectangle((rx + 8 + 10, ry + 8 + yb - 14, rx + 8 + 10 + 860 * pk, ry + 8 + yb + 14), outline=AMBER + (255,), width=4)
            blit(cv, T_N[k], rx + 8 + 810, ry + 8 + yb - 30, alpha=a * pk)
    comp(cv, lay, a)
    tf = C.wd(4, "fotos")
    pf = e_back(prog(t, tf - 0.7, tf - 0.2))
    blit(cv, T_LIN, 540, 1112, scale=pf, alpha=a * clamp(pf * 2))


def organic(cv, t):
    a, ain = C.sw(t, 5)
    if a <= 0.01:
        return
    panel(cv, a, T_ORG, 0.96 + 0.04 * ain)
    tt = C.SC_T[5][0]
    pulse = 0.75 + 0.25 * math.sin((t - tt) * 5)
    p = e_out(prog(t, tt + 0.1, tt + 0.7))
    sc = 1.12 * (0.9 + 0.1 * p)
    warm = vgrad(HULL.width, HULL.height, (255, 214, 70), (225, 70, 10)).convert("RGBA")
    warm.putalpha(HULL_FILL.point(lambda q: int(q * 0.95 * pulse * p)))
    blit(cv, soft_glow(640, 120, (255, 140, 20), 40, 0.9, 30), 540, 575, scale=sc * 1.1, alpha=a * p * pulse * 0.8)
    blit(cv, warm, 540, 560, scale=sc, alpha=a)
    blit(cv, HULL, 540, 560, scale=sc, alpha=a * p)
    blit(cv, T_MENOS, 540, 770, alpha=a * e_out(prog(t, tt + 0.5, tt + 0.9)))
    tm = C.wd(5, "madera")
    pm = e_back(prog(t, tm - 0.05, tm + 0.35))
    dx, dy = shake(t, tm + 0.3, 16, 9)
    blit(cv, T_MAD, 540 + dx, 900 + dy, scale=min(940 / T_MAD.width, 1) * pm, alpha=a * clamp(pm * 2))
    tc = C.wd(5, "todavía")
    ps = prog(t, tc - 0.05, tc + 0.18)
    if ps > 0:
        dx, dy = shake(t, tc + 0.14, 24, 8)
        blit(cv, ST_SINCONF, 540 + dx, 1090 + dy, scale=0.95 * (1 + 1.6 * (1 - e_out(ps))), rot=-5, alpha=a * clamp(ps * 2.5))


def skeptics(cv, t):
    a, ain = C.sw(t, 6)
    if a <= 0.01:
        return
    panel(cv, a, T_GEO, 0.96 + 0.04 * ain)
    tt = C.SC_T[6][0]
    p = e_back(prog(t, tt + 0.1, tt + 0.6))
    bob = 6 * math.sin((t - tt) * 2)
    blit(cv, DOC_G, 320, 700 + bob, scale=0.9 * p, alpha=a * 0.8 * clamp(p * 2))
    blit(cv, DOC, 320, 700 + bob, scale=0.9 * p, rot=-4, alpha=a * clamp(p * 2))
    blit(cv, T_COL, 320, 1010, alpha=a * clamp(p * 2))
    tn = C.wd(6, "natural")
    ps = prog(t, tn - 0.1, tn + 0.18)
    if ps > 0:
        dx, dy = shake(t, tn + 0.14, 20, 8)
        blit(cv, ST_NATURAL, 325 + dx, 770 + dy, scale=0.64 * (1 + 1.3 * (1 - e_out(ps))), rot=-9, alpha=a * clamp(ps * 2.5))
    tc = C.wd(6, "cambios")
    pc = e_out(prog(t, tc - 0.05, tc + 0.35))
    blit(cv, T_CAMB, 765 + 80 * (1 - pc), 560, scale=0.74, alpha=a * pc)
    tb = C.wd(6, "prueban")
    p1 = e_back(prog(t, tb - 0.1, tb + 0.35))
    blit(cv, T_NOPR, 765, 700, scale=min(450 / wnopr, 1) * p1, alpha=a * clamp(p1 * 2))
    tb2 = C.wd(6, "barco")
    p2 = e_back(prog(t, tb2 - 0.1, tb2 + 0.35))
    dx, dy = shake(t, tb2 + 0.3, 14, 9)
    blit(cv, T_UNB, 765 + dx, 850 + dy, scale=min(450 / wunb, 1) * p2, alpha=a * clamp(p2 * 2))


def atom(lay, cx, cy, t, a):
    d = ImageDraw.Draw(lay)
    for k in range(3):
        ang = math.radians(60 * k) + t * 0.6
        pts = []
        for j in range(80):
            th = j / 80 * 2 * math.pi
            x, y = 190 * math.cos(th), 62 * math.sin(th)
            pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
        d.line(pts + [pts[0]], fill=TEAL + (200,), width=4)
        th = t * 2.6 + k * 2.1
        x, y = 190 * math.cos(th), 62 * math.sin(th)
        ex, ey = cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)
        d.ellipse((ex - 11, ey - 11, ex + 11, ey + 11), fill=(190, 250, 255, 255))
    d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(255, 190, 40, 255))


def finale(cv, t):
    a, ain = C.sw(t, 7)
    if a <= 0.01 and t < C.SC_T[7][0]:
        return
    a = ain
    tt = C.SC_T[7][0]
    panel(cv, a, T_C14, 0.96 + 0.04 * ain)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    atom(lay, 540, 520, t, a)
    blit(cv, soft_glow(60, 60, (255, 170, 0), 40, 1.0, 30), 540, 520, scale=1.4, alpha=a * (0.6 + 0.3 * math.sin(t * 6)))
    comp(cv, lay, a)
    tc = C.wd(7, "carbono")
    pc = e_back(prog(t, tc - 0.05, tc + 0.35))
    blit(cv, T_C14B, 540, 750, scale=pc, alpha=a * clamp(pc * 2))
    tl = C.wd(7, "leyenda")
    p1 = e_back(prog(t, tl - 0.05, tl + 0.35))
    dx, dy = shake(t, tl + 0.3, 16, 9)
    blit(cv, T_LEY, 540 + dx, 905 + dy, scale=min(900 / wley, 1) * p1, alpha=a * clamp(p1 * 2))
    td = C.wd(7, "descubrimiento")
    p2 = e_back(prog(t, td - 0.05, td + 0.4))
    dx, dy = shake(t, td + 0.35, 20, 8)
    blit(cv, T_DES, 540 + dx, 1045 + dy, scale=min(940 / wdes, 1) * p2, alpha=a * clamp(p2 * 2))



def setup(ctx):
    global C
    C = ctx
    wd, l0 = ctx.wd, ctx.l0

    def dim(t):
        d = max(ctx.sw(t, i)[0] for i in range(2, 8)) if t > ctx.SC_T[2][0] - 0.2 else 0.0
        return 1.0 if t > ctx.SC_T[7][0] else d

    def sfx(sput, ctx):
        SC_T = ctx.SC_T
        sput(riser(0.3), 0.0, 0.5)
        sput(hit(70, 1.2, 0.8), 0.27, 1.0)
        sput(whoosh(0.5, True, 2), 0.25, 0.5)
        sput(hit(85), 0.78, 0.8)
        sput(whoosh(0.4, True, 3), 0.62, 0.35)
        sput(drill(1.6), wd(0, "perforar") - 0.1, 0.5)
        sput(blip(1100), 0.6, 0.4)
        for i in range(1, 8):
            sput(whoosh(0.45, True, 10 + i), SC_T[i][0] - 0.1, 0.45)
            sput(hit(100, 0.5, 0.3), SC_T[i][0] + 0.12, 0.45)
        sput(blip(1300), wd(1, "ararat"), 0.5)
        sput(ping(), wd(1, "colina") + 0.2, 0.6)
        sput(drill(2.8), l0(2) + 0.1, 0.55)
        sput(riser(1.3), wd(2, "sacó") - 0.1, 0.5)
        sput(hit(110, 0.5, 0.3), wd(2, "sacó") + 1.3, 0.5)
        sput(hit(70, 0.9, 0.9), wd(3, "roca") + 0.28, 1.0)
        sput(sweep(3.0), wd(4, "georradar"), 0.55)
        for k in range(3):
            sput(blip(900 + 200 * k, 0.12), wd(4, "niveles") - 0.5 + 0.28 * k, 0.55)
        sput(thump(0.9), wd(5, "todavía") - 0.8, 0.8)
        sput(hit(70, 0.9, 0.9), wd(5, "todavía") + 0.14, 1.0)
        sput(hit(75, 0.9, 0.7), wd(6, "natural") + 0.14, 0.9)
        sput(hit(65, 1.0, 0.8), wd(6, "barco") + 0.3, 0.9)
        sput(riser(1.0), wd(7, "leyenda") - 1.0, 0.5)
        sput(hit(70, 1.0, 0.9), wd(7, "descubrimiento") + 0.35, 1.0)
        sput(ping(), wd(7, "síguenos") + 0.35, 0.9)

    impacts = [0.30, 0.78, wd(3, "roca") + 0.28, wd(5, "todavía") + 0.14, wd(6, "natural") + 0.14, wd(6, "barco") + 0.3, wd(7, "descubrimiento") + 0.35]
    flashes = [(0.27, 0.9), (0.55, 0.4), (wd(5, "todavía") + 0.14, 0.25)]
    return Spec(background, [hook, place, drilling, finding, radar, organic, skeptics, finale],
                impacts=impacts, flashes=flashes, sfx=sfx, dim=dim)
