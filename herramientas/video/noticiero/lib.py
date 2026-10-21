"""Motor de Shorts estilo noticiero de ROBERT NEWS (1080x1920, vertical).

Piezas reutilizables: animación (easing, sacudidas), texto con degradado/resplandor,
banner de tercio inferior con cinta, logo, paneles, sellos, cámara, destellos,
efectos de sonido sintetizados y la tubería de render (fotogramas -> ffmpeg).

Cada historia vive en historias/<nombre>/ con guion.json y escenas.py (ver README).
"""
import importlib.util, json, math, os, random, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
ANTON, B7, B6 = (f"{HERE}/fonts/{n}" for n in ("Anton.woff", "BarlowCond700.woff", "BarlowCond600.woff"))

# variante TikTok (RN_TIKTOK=1): la interfaz de TikTok tapa más la parte baja (~480-660 px) y la alta (~240 px).
# Se encoge el contenido (escenas) y se sube el banner; el logo baja un poco. Ver README.
TT = os.environ.get("RN_TIKTOK") == "1"
TT_S, TT_TOP = 0.86, 290          # escala del contenido y la y a la que queda su borde superior (y=215 de origen)
DY = 68 if TT else 158        # banner y botón final más abajo (pedido del usuario): barra en y=1420 (Shorts) o y=1330 (TikTok)
LOGO_Y = 205 if TT else 120

# paleta de la marca
AMBER, TEAL, RED = (255, 176, 0), (90, 220, 230), (232, 30, 45)
GOLD = ((255, 240, 70), (255, 168, 0))
WHITE = ((255, 255, 255), (178, 190, 205))
GLOW_A = ((255, 170, 0), 24, 0.9)

# ------------------------------------------------------------------ animación
clamp = lambda x, a=0.0, b=1.0: max(a, min(b, x))
prog = lambda t, a, b: clamp((t - a) / (b - a))


def e_out(x):
    return 1 - (1 - clamp(x)) ** 3


def e_inout(x):
    x = clamp(x)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def e_back(x, s=1.9):
    x = clamp(x)
    return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2


def shake(t, t0, amp=16.0, decay=9.0):
    """Sacudida amortiguada tras un impacto en t0."""
    if t < t0:
        return 0.0, 0.0
    k = amp * math.exp(-decay * (t - t0))
    return k * math.sin(71 * (t - t0)), k * math.cos(83 * (t - t0))


# ------------------------------------------------------------------ gráficos
def vgrad(w, h, c1, c2):
    a = np.linspace(0, 1, h)[:, None, None]
    arr = (1 - a) * np.array(c1, float) + a * np.array(c2, float)
    return Image.fromarray(np.broadcast_to(arr, (h, w, 3)).astype("uint8"))


def rtext(txt, fpath, size, fill=(255, 255, 255), grad=None, stroke=0, stroke_col=(0, 0, 0), glow=None, shadow=None):
    """Sprite RGBA de texto con degradado, contorno, resplandor y sombra. -> (sprite, ancho_tinta, alto_tinta)."""
    f = ImageFont.truetype(fpath, size)
    l, t, r, b = f.getbbox(txt, stroke_width=stroke)
    pad = 12 + stroke + (int(glow[1] * 3) if glow else 0) + (int(shadow[2] * 3) + 20 if shadow else 0)
    w, h = r - l + 2 * pad, b - t + 2 * pad

    def mask(sw):
        m = Image.new("L", (w, h), 0)
        ImageDraw.Draw(m).text((pad - l, pad - t), txt, font=f, fill=255, stroke_width=sw, stroke_fill=255)
        return m

    inner = mask(0)
    outer = mask(stroke) if stroke else inner
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        dx, dy, bl, al = shadow
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        sh.putalpha(ImageChops.offset(outer, dx, dy).filter(ImageFilter.GaussianBlur(bl)).point(lambda v: int(v * al)))
        out = Image.alpha_composite(out, sh)
    if glow:
        col, rad, gain = glow
        g = Image.new("RGBA", (w, h), col + (0,))
        g.putalpha(outer.filter(ImageFilter.GaussianBlur(rad)).point(lambda v: min(255, int(v * gain))))
        out = Image.alpha_composite(out, g)
    if stroke:
        s = Image.new("RGBA", (w, h), stroke_col + (0,))
        s.putalpha(outer)
        out = Image.alpha_composite(out, s)
    if grad:
        fl = Image.new("RGB", (w, h))
        fl.paste(vgrad(w, h - 2 * pad, grad[0], grad[1]), (0, pad))
        fl.paste(Image.new("RGB", (w, pad), grad[0]), (0, 0))
        fl.paste(Image.new("RGB", (w, pad), grad[1]), (0, h - pad))
        fl = fl.convert("RGBA")
    else:
        fl = Image.new("RGBA", (w, h), fill + (255,))
    fl.putalpha(inner)
    return Image.alpha_composite(out, fl), r - l, b - t


def S(txt, font, size, **kw):
    """Atajo: solo el sprite de texto."""
    return rtext(txt, font, size, **kw)[0]


def blit(cv, spr, cx, cy, scale=1.0, rot=0.0, alpha=1.0, sx=1.0):
    """Pega un sprite RGBA centrado en (cx, cy) con escala, rotación y opacidad."""
    if alpha <= 0.003 or scale <= 0.001:
        return
    s = spr
    nw, nh = max(1, round(s.width * scale * sx)), max(1, round(s.height * scale))
    if (nw, nh) != s.size:
        s = s.resize((nw, nh), Image.BILINEAR)
    if rot:
        s = s.rotate(rot, resample=Image.BICUBIC, expand=True)
    a = s.getchannel("A")
    if alpha < 1:
        a = a.point(lambda v: int(v * alpha))
    cv.paste(s.convert("RGB"), (round(cx - s.width / 2), round(cy - s.height / 2)), a)


def comp(cv, lay, a=1.0):
    """Compone una capa RGBA del tamaño del lienzo (para dibujar primitivas con ImageDraw)."""
    al = lay.getchannel("A")
    if a < 1:
        al = al.point(lambda v: int(v * a))
    cv.paste(lay.convert("RGB"), (0, 0), al)


def new_layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def rrect(w, h, c1, c2, radius=16):
    im = vgrad(w, h, c1, c2).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=255)
    im.putalpha(m)
    return im


def soft_glow(w, h, col, rad, alpha=0.8, radius=18):
    g = Image.new("RGBA", (w + 4 * rad, h + 4 * rad), col + (0,))
    m = Image.new("L", g.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((2 * rad, 2 * rad, 2 * rad + w, 2 * rad + h), radius=radius, fill=int(255 * alpha))
    g.putalpha(m.filter(ImageFilter.GaussianBlur(rad)))
    return g


def glow_dot(col, size):
    im = Image.new("RGBA", (size * 4, size * 4), col + (0,))
    m = Image.new("L", im.size, 0)
    ImageDraw.Draw(m).ellipse((size * 1.5, size * 1.5, size * 2.5, size * 2.5), fill=255)
    im.putalpha(m.filter(ImageFilter.GaussianBlur(size * 0.9)))
    return im


def make_stamp(text, col, size=104, fillc=(40, 0, 8, 215)):
    t, _, _ = rtext(text, ANTON, size, fill=col, stroke=3, stroke_col=(20, 0, 5), glow=(col, 14, 0.8))
    st = Image.new("RGBA", (t.width + 80, t.height + 50), (0, 0, 0, 0))
    ImageDraw.Draw(st).rounded_rectangle((6, 6, st.width - 7, st.height - 7), radius=18, fill=fillc, outline=col + (255,), width=9)
    st.alpha_composite(t, ((st.width - t.width) // 2, (st.height - t.height) // 2))
    return st


# ------------------------------------------------------------------ marca
_LOGO_IMG = Image.open(f"{HERE}/assets/logo.png").convert("RGBA")
if os.path.exists(f"{HERE}/assets/marca/robertnews_texto.webp"):
    _LOGO_IMG = Image.open(f"{HERE}/assets/marca/robertnews_texto.webp").convert("RGBA")
    _LOGO_IMG = _LOGO_IMG.crop(_LOGO_IMG.getbbox())
if os.path.exists(f"{HERE}/assets/marca/robertnews_texto.webp"):
    # sombra paralela siguiendo la silueta del logotipo (el logotipo nuevo es transparente)
    _a = Image.new("L", (_LOGO_IMG.width + 120, _LOGO_IMG.height + 120), 0)
    _a.paste(_LOGO_IMG.getchannel("A"), (60, 60))
    _a = _a.filter(ImageFilter.GaussianBlur(18)).point(lambda v: min(255, int(v * 1.6)))
    _LOGO_GLOW = Image.new("RGBA", _a.size, (0, 0, 0, 0))
    _LOGO_GLOW.putalpha(_a)
    _LOGO_GLOW = Image.merge("RGBA", (*Image.new("RGB", _a.size, (0, 0, 0)).split(), _a.point(lambda v: int(v * 0.85))))
else:
    _LOGO_GLOW = soft_glow(_LOGO_IMG.width, _LOGO_IMG.height, (255, 20, 40), 26, 0.45)

PANEL = Image.new("RGBA", (1020, 1080), (0, 0, 0, 0))
_pd = ImageDraw.Draw(PANEL)
_pd.rounded_rectangle((20, 30, 1000, 1050), radius=30, fill=(4, 10, 18, 214), outline=AMBER + (210,), width=3)
for _cx, _cy, _sx, _sy in ((20, 30, 1, 1), (1000, 30, -1, 1), (20, 1050, 1, -1), (1000, 1050, -1, -1)):
    _pd.line((_cx, _cy + 60 * _sy, _cx, _cy, _cx + 60 * _sx, _cy), fill=AMBER + (255,), width=8)
PANEL_G = soft_glow(980, 1020, AMBER, 20, 0.28, 30)


def panel(cv, a, title, scale=1.0):
    """Panel tipo HUD (x 50-1030, y 215-1235) con título en su cabecera. La zona segura de Shorts llega a y=1440."""
    blit(cv, PANEL_G, 540, 725, scale=scale, alpha=a * 0.9)
    blit(cv, PANEL, 540, 725, scale=scale, alpha=a)
    blit(cv, title, 540, 290, alpha=a)


def title_sprite(txt, col=AMBER, size=62):
    return S(txt, B7, size, fill=col, shadow=(0, 4, 3, 0.7))


class Ctx:
    """Tiempos de la voz + configuración de marca de una historia."""

    def __init__(self, story_dir, tail=0.95):
        self.dir = os.path.abspath(story_dir)
        self.build = os.path.join(self.dir, "build")
        os.makedirs(self.build, exist_ok=True)
        self.cfg = json.load(open(f"{self.dir}/guion.json", encoding="utf-8"))
        tl = json.load(open(f"{self.build}/linea_tiempos.json", encoding="utf-8"))
        self.LN = tl["lineas"]
        self.DUR = tl["fin_voz"] + tail
        self.NF = int(self.DUR * FPS)
        first = self.cfg.get("escenas_en_linea", list(range(len(self.LN))))
        starts = [0.0] + [self.l0(k) - 0.05 for k in first[1:]]
        self.SC_T = [(starts[i], starts[i + 1] if i + 1 < len(starts) else self.DUR) for i in range(len(starts))]
        m = self.cfg["marca"]
        self.marca = m
        self.cta_line = m.get("cta_linea", len(self.LN) - 1)
        self.lt_in = self.l0(m.get("banner_desde_linea", 1)) + 0.1
        self._brand_sprites(m)

    # -- tiempos
    def l0(self, i):
        return self.LN[i]["t0"]

    def l1(self, i):
        return self.LN[i]["t1"]

    def wd(self, i, start):
        """Instante (s) de la primera palabra de la línea i que empieza por `start`."""
        for w in self.LN[i]["words"]:
            if w["w"].lower().strip("¡!¿?.,…:;").startswith(start):
                return w["t"]
        raise KeyError(f"línea {i}: no hay palabra que empiece por '{start}': " + " ".join(w["w"] for w in self.LN[i]["words"]))

    def sw(self, t, i):
        """(visibilidad con entrada y salida, solo entrada) de la escena i en el instante t."""
        s0, s1 = self.SC_T[i]
        a_in = e_out(prog(t, s0, s0 + 0.35))
        a_out = 1 - e_inout(prog(t, s1 - 0.18, s1 + 0.12))
        return a_in * a_out, a_in

    # -- sprites del banner (dependen del texto de cada historia)
    def _brand_sprites(self, m):
        self.TAG = rrect(262, 110, (232, 22, 38), (176, 8, 22), 10)
        s = S(m["etiqueta"], ANTON, 42, fill=(255, 255, 255), shadow=(0, 3, 2, 0.5))
        if s.width > 230:
            s = s.resize((230, round(s.height * 230 / s.width)), Image.LANCZOS)
        self.TAG.alpha_composite(s, ((self.TAG.width - s.width) // 2, (self.TAG.height - s.height) // 2))
        self.BAR = rrect(738, 110, (16, 40, 62), (8, 22, 36), 10)
        s = S(m["titular"], B7, 58, fill=(255, 255, 255), shadow=(0, 3, 2, 0.5))
        if s.width > 690:
            s = s.resize((690, round(s.height * 690 / s.width)), Image.LANCZOS)
        self.BAR.alpha_composite(s, (22, (self.BAR.height - s.height) // 2))
        ticker = m["cinta"] + "  •  robert-news-latest.onrender.com  •  "
        self.TICK = S(ticker * 3, B6, 34, fill=(255, 255, 255))
        self.TICK_W = S(ticker, B6, 34, fill=(255, 255, 255)).width - 24
        self.TICK_BG = rrect(1000, 48, (150, 8, 20), (120, 6, 16), 6)
        self.BTN = rrect(900, 130, (236, 22, 38), (184, 8, 22), 22)
        txt = m.get("cta_texto_tiktok", "SÍGUENOS  @robertnews_") if TT else m.get("cta_texto", "SÍGUENOS EN ROBERT NEWS")
        bt = S(txt, B7, 66, fill=(255, 255, 255), shadow=(0, 3, 2, 0.5))
        emb = f"{HERE}/assets/marca/emblema_rojo.png"
        oy = 0
        self.URL_DY = 0
        if m.get("cta_emblema") and os.path.exists(emb):
            # botón con el emblema RN a la izquierda (sobresale de la barra)
            bar = self.BTN
            self.BTN = Image.new("RGBA", (900, 176), (0, 0, 0, 0))
            self.BTN.alpha_composite(bar, (0, 23))
            e = Image.open(emb).convert("RGBA")
            e = e.resize((round(e.width * 176 / e.height), 176), Image.LANCZOS)
            if bt.width > 560:
                bt = bt.resize((560, round(bt.height * 560 / bt.width)), Image.LANCZOS)
            self.BTN.alpha_composite(bt, (210, (176 - bt.height) // 2))
            self.BTN.alpha_composite(e, (14, 0))
            oy = 23
            self.URL_DY = 26
        else:
            if bt.width > 730:
                bt = bt.resize((730, round(bt.height * 730 / bt.width)), Image.LANCZOS)
            self.BTN.alpha_composite(bt, (60, (130 - bt.height) // 2))
        d = ImageDraw.Draw(self.BTN)
        ax, ay = 818, 65 + oy
        for xy in ((ax - 34, ay, ax + 30, ay), (ax + 6, ay - 24, ax + 34, ay), (ax + 6, ay + 24, ax + 34, ay)):
            d.line(xy, fill=(255, 255, 255, 255), width=10)
        self.BTN_G = soft_glow(900, self.BTN.height, (255, 30, 50), 26, 0.8)
        self.URL = S("robert-news-latest.onrender.com", B6, 54, fill=(135, 205, 255), shadow=(0, 4, 3, 0.6))


# ------------------------------------------------------------------ elementos comunes de cada fotograma
def top_logo(cv, t):
    p = e_back(prog(t, 0.55, 1.1), 1.4)
    y = LOGO_Y - 220 * (1 - p)
    sc = 760 / _LOGO_IMG.width * (1 + 0.012 * math.sin(t * 3.2))
    blit(cv, _LOGO_GLOW, 540, y, scale=sc, alpha=prog(t, 0.55, 0.85))
    blit(cv, _LOGO_IMG, 540, y, scale=sc, alpha=prog(t, 0.55, 0.75))


def lower_third(ctx, cv, t):
    """Etiqueta + titular + cinta (y 1262-1428). Sale cuando entra el botón final."""
    p = e_out(prog(t, ctx.lt_in, ctx.lt_in + 0.55))
    tc = ctx.wd(ctx.cta_line, ctx.marca.get("cta_palabra", "síguenos"))
    out = e_inout(prog(t, tc - 0.2, tc + 0.3))
    if p <= 0:
        return
    off = -1100 * (1 - p) + 1100 * out
    ptick = e_out(prog(t, ctx.lt_in + 0.25, ctx.lt_in + 0.75))
    y0 = 1262 + DY
    glow = soft_glow(1000, 110, (0, 90, 220), 22, 0.35)
    cv.paste(glow.convert("RGB"), (round(40 - 44 + off), y0 - 44), glow.getchannel("A"))
    cv.paste(ctx.TAG.convert("RGB"), (round(40 + off), y0), ctx.TAG.getchannel("A"))
    cv.paste(ctx.BAR.convert("RGB"), (round(302 + off), y0), ctx.BAR.getchannel("A"))
    cv.paste(ctx.TICK_BG.convert("RGB"), (round(40 + off), 1380 + DY + round(40 * (1 - ptick))), ctx.TICK_BG.getchannel("A"))
    if ptick > 0.4:
        shift = (t * 150) % ctx.TICK_W
        strip = ctx.TICK.crop((round(shift), 0, round(shift) + 960, ctx.TICK.height))
        cv.paste(strip.convert("RGB"), (round(60 + off), 1380 + DY + (48 - strip.height) // 2 + 1), strip.getchannel("A"))


def cta(ctx, cv, t):
    """Botón rojo final + URL (y 1330-1420, por encima de la zona de interfaz de Shorts)."""
    tc = ctx.wd(ctx.cta_line, ctx.marca.get("cta_palabra", "síguenos"))
    pb = e_back(prog(t, tc - 0.1, tc + 0.4))
    if pb <= 0:
        return
    beat = 1 + 0.035 * math.sin((t - tc) * 7) * (t > tc + 0.5)
    blit(cv, ctx.BTN_G, 540, 1330 + DY, scale=beat * pb, alpha=0.9 * clamp(pb))
    blit(cv, ctx.BTN, 540, 1330 + DY, scale=beat * pb, alpha=clamp(pb * 2))
    blit(cv, ctx.URL, 540, 1420 + DY + ctx.URL_DY, alpha=prog(t, tc + 0.2, tc + 0.6))


def camera(cv, t, dur, impacts):
    """Zoom lento + empujón tras cada impacto."""
    z = 1.0 + 0.03 * t / dur + 0.035 * sum(math.exp(-11 * (t - t0)) for t0 in impacts if t >= t0)
    if z <= 1.0005:
        return cv
    cw, chh = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - chh) / 2
    return cv.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + chh))


class Spec:
    """Lo que una historia entrega al motor."""

    def __init__(self, background, scenes, impacts=(), flashes=(), sfx=None, dim=None, pad=(55, 65.4, 98, 130.8), bleed=()):
        self.background, self.scenes, self.bleed = background, scenes, list(bleed)
        self.impacts, self.flashes, self.sfx = list(impacts), list(flashes), sfx
        self.dim = dim or (lambda t: 0.0)
        self.pad = pad


_TT_MASK = None


def photo_bleed(path, t0, t1, z0=1.04, z1=1.18, fx=0.5, fy=0.5, tag=None, tag_xy=(60, 330)):
    """Foto a pantalla completa (1080x1920, recorte tipo 'cover') entre t0 y t1, con zoom lento y degradados arriba y abajo
    para que se lean el logo y el banner. `tag`: rótulo de transparencia (p. ej. 'IMAGEN ILUSTRATIVA'). Devuelve f(cv, t)."""
    img = Image.open(path).convert("RGB")
    s0 = max(W / img.width, H / img.height) * z1
    base = img.resize((math.ceil(img.width * s0), math.ceil(img.height * s0)), Image.LANCZOS)
    ov = np.zeros((H, W, 4), "uint8")
    ya = np.arange(H)[:, None]
    top = np.clip(1 - ya / 380.0, 0, 1) ** 1.5 * 175
    bot = np.clip((ya - 980) / 940.0, 0, 1) ** 1.3 * 215
    ov[..., 3] = np.broadcast_to(np.maximum(top, bot), (H, W)).astype("uint8")
    OV = Image.fromarray(ov, "RGBA")
    TAG = None
    if tag:
        t_s = S(tag, B7, 34, fill=(255, 255, 255), shadow=(0, 2, 2, 0.6))
        TAG = Image.new("RGBA", (t_s.width + 40, t_s.height + 22), (0, 0, 0, 150))
        TAG.alpha_composite(t_s, (20, 11))

    def f(cv, t):
        a = e_out(prog(t, t0, t0 + 0.2)) * (1 - e_out(prog(t, t1 - 0.2, t1)))
        if a <= 0.003:
            return
        z = z0 + (z1 - z0) * prog(t, t0, t1)
        cw, ch = W * z1 / z, H * z1 / z
        cx = clamp(fx * base.width, cw / 2, base.width - cw / 2)
        cy = clamp(fy * base.height, ch / 2, base.height - ch / 2)
        fr = base.resize((W, H), Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))
        fr = fr.convert("RGBA")
        fr.alpha_composite(OV)
        if TAG is not None:
            fr.alpha_composite(TAG, tag_xy)
        cv.paste(Image.blend(cv, fr.convert("RGB"), a))

    return f


def video_bleed(path, t0, t1, src0, pan=(0.3, 0.7), tag=None, tag_xy=(60, 330)):
    """Clip de vídeo (aunque sea horizontal) a pantalla completa 1080x1920: se escala a la altura y se recorta con un paneo
    lento de `pan[0]` a `pan[1]` (fracción del ancho). Se lee del segundo `src0` del clip a velocidad normal entre t0 y t1.
    Decodifica en streaming con ffmpeg (los fotogramas se piden en orden). Devuelve f(cv, t)."""
    ov = np.zeros((H, W, 4), "uint8")
    ya = np.arange(H)[:, None]
    ov[..., 3] = np.broadcast_to(np.maximum(np.clip(1 - ya / 380.0, 0, 1) ** 1.5 * 175, np.clip((ya - 980) / 940.0, 0, 1) ** 1.3 * 215), (H, W)).astype("uint8")
    OV = Image.fromarray(ov, "RGBA")
    TAG = None
    if tag:
        t_s = S(tag, B7, 34, fill=(255, 255, 255), shadow=(0, 2, 2, 0.6))
        TAG = Image.new("RGBA", (t_s.width + 40, t_s.height + 22), (0, 0, 0, 150))
        TAG.alpha_composite(t_s, (20, 11))
    st = {"p": None, "n": -1, "last": None}
    D = max(t1 - t0, 0.1)

    def start(n):
        if st["p"] is not None:
            st["p"].kill()
        off = n / FPS
        x = f"(iw-ow)*({pan[0]}+({pan[1]}-{pan[0]})*min(1,(t+{off:.3f})/{D:.3f}))"
        vf = f"fps={FPS},scale=-2:{H}:flags=lanczos,crop=w={W}:h={H}:x='{x}':y=0,unsharp=5:5:0.7"
        st["p"] = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{src0 + off:.3f}", "-i", path, "-vf", vf, "-an", "-f", "rawvideo",
                                    "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=W * H * 6)
        st["n"] = n

    def get(n):
        if st["p"] is None or n != st["n"]:
            start(n)
        buf = st["p"].stdout.read(W * H * 3)
        st["n"] = n + 1
        if len(buf) < W * H * 3:
            return st["last"] or Image.new("RGB", (W, H))
        st["last"] = Image.frombytes("RGB", (W, H), buf)
        return st["last"]

    def f(cv, t):
        a = e_out(prog(t, t0, t0 + 0.2)) * (1 - e_out(prog(t, t1 - 0.2, t1)))
        if a <= 0.003:
            return
        fr = get(max(0, round((t - t0) * FPS))).convert("RGBA")
        fr.alpha_composite(OV)
        if TAG is not None:
            fr.alpha_composite(TAG, tag_xy)
        cv.paste(Image.blend(cv, fr.convert("RGB"), a))

    return f


# Rótulos grandes a mitad de pantalla: apagados por defecto (pedido del usuario, 2026-10-21). RN_ROTULOS=1 los vuelve a activar.
ROTULOS = os.environ.get("RN_ROTULOS") == "1"


def caption(txt, t_in, t_out, y=1010, col=(255, 255, 255), size=84):
    """Rótulo grande que entra con rebote en t_in y sale en t_out. Devuelve f(cv, t). Desactivado salvo RN_ROTULOS=1."""
    if not ROTULOS:
        return lambda cv, t: None
    sp = S(txt, ANTON, size, fill=col, shadow=(0, 5, 4, 0.85))
    if sp.width > 960:
        sp = sp.resize((960, round(sp.height * 960 / sp.width)), Image.LANCZOS)

    def f(cv, t):
        p = e_back(prog(t, t_in, t_in + 0.3), 1.6)
        a = clamp(p * 2) * (1 - e_out(prog(t, t_out - 0.15, t_out)))
        if a > 0.01:
            blit(cv, sp, 540, y + 30 * (1 - clamp(p)), scale=0.85 + 0.15 * clamp(p), alpha=a)

    return f


def tt_squeeze(cv):
    """Encoge las escenas (con borde difuminado sobre un fondo borroso) para dejar sitio a la interfaz de TikTok."""
    global _TT_MASK
    sw, sh = round(W * TT_S), round(H * TT_S)
    if _TT_MASK is None:
        m = Image.new("L", (sw, sh), 0)
        ImageDraw.Draw(m).rectangle((46, 46, sw - 46, sh - 46), fill=255)
        _TT_MASK = m.filter(ImageFilter.GaussianBlur(22))
    base = cv.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR)
    base = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), base, 0.7)
    base.paste(cv.resize((sw, sh), Image.LANCZOS), ((W - sw) // 2, round(TT_TOP - 215 * TT_S)), _TT_MASK)
    return base


def make_frame(ctx, spec):
    def frame(t):
        cv = spec.background(t, clamp(spec.dim(t)))
        for sc in spec.scenes:
            sc(cv, t)
        if TT:
            cv = tt_squeeze(cv)
        for b in spec.bleed:      # fotos a pantalla completa (no se encogen en la variante TikTok)
            b(cv, t)
        top_logo(cv, t)
        cv = camera(cv, t, ctx.DUR, spec.impacts)
        lower_third(ctx, cv, t)
        cta(ctx, cv, t)
        for t0, k in spec.flashes:
            f = math.exp(-14 * (t - t0)) if t >= t0 else 0.0
            if f > 0.02:
                cv = Image.blend(cv, Image.new("RGB", (W, H), (230, 240, 255)), min(1, f * k))
        fade = prog(t, 0.0, 0.18)
        if fade < 1:
            cv = Image.blend(Image.new("RGB", (W, H), (0, 0, 0)), cv, fade)
        return cv

    return frame


# ------------------------------------------------------------------ sonido sintetizado
def lp_noise(n, a0, a1, seed=1):
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype("float32")
    y = np.zeros(n, "float32")
    a = np.linspace(a0, a1, n)
    p = 0.0
    for i in range(n):
        p += a[i] * (x[i] - p)
        y[i] = p
    return y / (np.abs(y).max() + 1e-9)


def whoosh(dur=0.5, up=True, seed=1):
    n = int(dur * SR)
    y = lp_noise(n, 0.01, 0.25, seed) if up else lp_noise(n, 0.25, 0.01, seed)
    return y * np.sin(np.linspace(0, np.pi, n)) ** 1.6 * 0.9


def hit(f0=90, dur=0.8, noise=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * np.cumsum(f0 * np.exp(-6 * t) + 36) / SR) * np.exp(-5 * t)
    y += noise * lp_noise(n, 0.3, 0.02, 3) * np.exp(-26 * t)
    return y.astype("float32")


def riser(dur=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 200 * (1 + 4 * (t / dur) ** 2)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 2 * 0.5
    y += lp_noise(n, 0.02, 0.3, 5) * (t / dur) ** 2 * 0.4
    return y.astype("float32")


def blip(freq=1500, dur=0.08):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * freq * t) * np.exp(-40 * t) * 0.6).astype("float32")


def ping():
    n = SR
    t = np.arange(n) / SR
    return ((np.sin(2 * np.pi * 1568 * t) + 0.5 * np.sin(2 * np.pi * 2093 * t)) * np.exp(-5 * t) * 0.35).astype("float32")


def drill(dur=2.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = (np.sign(np.sin(2 * np.pi * 48 * t)) * 0.3 + lp_noise(n, 0.15, 0.2, 8) * 0.7) * np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.3)
    return y.astype("float32") * 0.8


def sweep(dur=3.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 700 + 500 * ((t * 1.6) % 1)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 * np.minimum(1, t / 0.2) * np.minimum(1, (dur - t) / 0.3)).astype("float32")


def thump(g=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 55 * t) * np.exp(-14 * t) * g).astype("float32")


def rumble(dur=2.0, seed=4):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (lp_noise(n, 0.004, 0.012, seed) * 1.4 * np.minimum(1, t / 0.4) * np.minimum(1, (dur - t) / 0.5)).astype("float32")


def build_audio(ctx, spec, path):
    """Voz + efectos (spec.sfx(sput, ctx)) + bordón oscuro + viento, normalizado luego por ffmpeg."""
    n = int(ctx.DUR * SR)
    sfx = np.zeros(n, "float32")

    def sput(sig, t0, g):
        i = int(t0 * SR)
        if 0 <= i < n:
            seg = sig[: n - i] * g
            sfx[i:i + len(seg)] += seg

    if spec.sfx:
        spec.sfx(sput, ctx)
    with wave.open(f"{ctx.build}/voz.wav", "rb") as w:
        voice = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype("float32") / 32768
    mix = np.zeros(n, "float32")
    mix[: min(n, len(voice))] += voice[:n]
    mix += sfx * 0.55
    t = np.arange(n) / SR
    pad = sum(np.sin(2 * np.pi * f * t + p) for p, f in enumerate(spec.pad)) / len(spec.pad)
    pad *= 0.07 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.18 * t)) * np.minimum(1, t / 0.8) * np.minimum(1, (ctx.DUR - t) / 1.0)
    wind = lp_noise(n, 0.004, 0.02, 21) * 0.07 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * t))
    mix += pad.astype("float32") + wind.astype("float32")
    mix = np.clip(mix, -1, 1)
    st = np.stack([mix, mix], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())


# ------------------------------------------------------------------ ejecución
def load_story(story_dir):
    ctx = Ctx(story_dir)
    spath = os.path.join(ctx.dir, "escenas.py")
    sp = importlib.util.spec_from_file_location("escenas_" + os.path.basename(ctx.dir), spath)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return ctx, mod.setup(ctx)


def run(story_dir, mode, times=()):
    ctx, spec = load_story(story_dir)
    frame = make_frame(ctx, spec)
    print(f"duración {ctx.DUR:.2f}s · {ctx.NF} fotogramas")
    if mode == "test":
        ims = []
        for t in times:
            im = frame(t)
            im.save(f"{ctx.build}/test{'_tt' if TT else ''}_{t:05.2f}.png")
            ims.append(im.resize((324, 576), Image.LANCZOS))
        sheet = Image.new("RGB", (324 * len(ims), 576))
        for i, im in enumerate(ims):
            sheet.paste(im, (324 * i, 0))
        sheet.save(f"{ctx.build}/contacto{'_tt' if TT else ''}.png")
        print(f"hoja de contacto: {ctx.build}/contacto.png")
        return
    build_audio(ctx, spec, f"{ctx.build}/mezcla{'_tt' if TT else ''}.wav")
    out = f"{ctx.build}/short{'_tiktok' if TT else ''}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", f"{ctx.build}/mezcla{'_tt' if TT else ''}.wav", "-af", "loudnorm=I=-14:TP=-1.0:LRA=11",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-movflags", "+faststart", "-shortest", out], stdin=subprocess.PIPE)
    for i in range(ctx.NF):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % 90 == 0:
            print("fotograma", i, "/", ctx.NF, flush=True)
    p.stdin.close()
    p.wait()
    print("listo", out)
