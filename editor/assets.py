"""Imagens desenhadas pelo próprio editor: ícones de app, prints de chat,
cartão final e placeholders. Tudo em 1080x1920."""
import math
import random
import textwrap

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from .common import FONT_CAPTION, FONT_EMOJI, FONT_UI, FONT_UI_BOLD, H, W


def font(path, size):
    return ImageFont.truetype(str(path), size)


def emoji(ch, size):
    """Emoji colorido (Noto Color Emoji só existe no tamanho 109)."""
    f = ImageFont.truetype(str(FONT_EMOJI), 109)
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def bubble_icon(color, size=420):
    """Ícone quadrado arredondado com balão de fala branco."""
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.22), fill=color)
    cx, cy = size / 2, size * 0.47
    rx, ry = size * 0.33, size * 0.27
    d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill="white")
    d.polygon([(cx - rx * 0.55, cy + ry * 0.6), (cx - rx * 0.95, cy + ry * 1.45),
               (cx - rx * 0.05, cy + ry * 0.85)], fill="white")
    return im


def glow_text(text, fnt, color, pad=60):
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=fnt)
    im = Image.new("RGBA", (r - l + pad * 2, b - t + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((pad - l, pad - t), text, font=fnt, fill=color)
    glow = im.filter(ImageFilter.GaussianBlur(22))
    out = Image.alpha_composite(glow, glow)
    out = Image.alpha_composite(out, im)
    return out


def app_icon(label, color):
    """Tela preta com o ícone do app e um número em neon, como 'WhatsApp 2'."""
    bg = Image.new("RGB", (W, H), (8, 8, 12))
    icon = bubble_icon(color)
    if label:
        num = glow_text(label, font(FONT_CAPTION, 520), color)
        total = icon.width + num.width - 80
        x0 = (W - total) // 2
        bg.paste(icon, (x0, (H - icon.height) // 2 - 120), icon)
        bg.paste(num, (x0 + icon.width - 80, (H - num.height) // 2 - 120), num)
    else:
        bg.paste(icon, ((W - icon.width) // 2, (H - icon.height) // 2 - 120), icon)
    return bg


def _wave(d, x, y, w, h, color, seed):
    rnd = random.Random(seed)
    n = 34
    step = w / n
    for i in range(n):
        a = h * (0.2 + 0.8 * abs(math.sin(i * 0.7 + rnd.random() * 2)) * rnd.uniform(0.4, 1))
        xx = x + i * step
        d.rounded_rectangle((xx, y + (h - a) / 2, xx + step * 0.55, y + (h + a) / 2), radius=3, fill=color)


CHATS = {
    "family": {
        "title": "Family Group",
        "sub": "Mom, Aunt Linda, Uncle Bob, Grandma, +9",
        "msgs": [
            ("Aunt Linda", "voice", "9:12", False),
            ("Uncle Bob", "voice", "4:37", False),
            ("Mom", "voice", "6:05", False),
            ("Grandma", "voice", "3:48", False),
            ("Aunt Linda", "voice", "11:26", False),
        ],
    },
    "squidward": {
        "title": "Family Group",
        "sub": "Today 6:00 AM",
        "msgs": [
            ("Squidward", "voice", "7:43", True),
            ("Mom", "text", "honey it's 6am", False),
            ("Uncle Bob", "text", "please stop", False),
            ("Squidward", "voice", "8:02", True),
        ],
    },
}


def chat(name, visible=None, struck=0):
    """visible: quantas mensagens aparecem; struck: quantas levam X vermelho."""
    spec = CHATS[name]
    msgs = spec["msgs"] if visible is None else spec["msgs"][:visible]
    bg = Image.new("RGB", (W, H), (242, 242, 247))
    d = ImageDraw.Draw(bg)
    # barra superior
    d.rectangle((0, 0, W, 300), fill=(248, 248, 250))
    d.line((0, 300, W, 300), fill=(210, 210, 215), width=2)
    d.text((60, 70), "9:41", font=font(FONT_UI_BOLD, 44), fill="black")
    d.ellipse((W / 2 - 55, 105, W / 2 + 55, 215), fill=(150, 160, 175))
    fam = emoji("👨‍👩‍👧‍👦", 70)
    bg.paste(fam, (int(W / 2 - fam.width / 2), int(160 - fam.height / 2)), fam)
    f_t = font(FONT_UI_BOLD, 40)
    tw = d.textlength(spec["title"], font=f_t)
    d.text(((W - tw) / 2, 228), spec["title"], font=f_t, fill="black")
    f_s = font(FONT_UI, 28)
    sw = d.textlength(spec["sub"], font=f_s)
    d.text(((W - sw) / 2, 268), spec["sub"], font=f_s, fill=(120, 120, 128))

    y = 360
    f_name = font(FONT_UI, 30)
    f_msg = font(FONT_UI, 46)
    for i, (who, kind, val, mine) in enumerate(msgs):
        bw = 700 if kind == "voice" else int(d.textlength(val, font=f_msg)) + 80
        bh = 140 if kind == "voice" else 110
        if mine:
            x = W - 50 - bw
            fill, fg = (10, 132, 255), "white"
        else:
            x = 120
            fill, fg = (229, 229, 234), (30, 30, 30)
            d.text((x + 24, y), who, font=f_name, fill=(120, 120, 128))
            y += 42
            d.ellipse((30, y + bh - 76, 100, y + bh - 6), fill=(170, 175, 190))
            ini = who[0]
            d.text((65 - d.textlength(ini, font=f_name) / 2, y + bh - 60), ini, font=f_name, fill="white")
        d.rounded_rectangle((x, y, x + bw, y + bh), radius=48, fill=fill)
        if kind == "voice":
            cx, cy = x + 70, y + bh / 2
            d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=fg)
            d.polygon([(cx - 10, cy - 18), (cx - 10, cy + 18), (cx + 18, cy)], fill=fill)
            _wave(d, x + 125, y + 35, bw - 290, bh - 70, fg, i * 7 + len(val))
            d.text((x + bw - 140, y + bh / 2 - 24), val, font=font(FONT_UI_BOLD, 42), fill=fg)
        else:
            d.text((x + 40, y + 26), val, font=f_msg, fill=fg)
        if i < struck:
            red, m = (235, 20, 20), 18
            d.line((x - m, y - m, x + bw + m, y + bh + m), fill=red, width=26)
            d.line((x + bw + m, y - m, x - m, y + bh + m), fill=red, width=26)
        y += bh + 46
    # barra de digitar
    d.rectangle((0, H - 170, W, H), fill=(248, 248, 250))
    d.rounded_rectangle((120, H - 140, W - 60, H - 60), radius=40, outline=(200, 200, 205), width=3, fill="white")
    d.text((160, H - 122), "iMessage", font=font(FONT_UI, 38), fill=(170, 170, 175))
    return bg


def phone(label, color, bg=None, sx=1.0):
    """Celular na mão do espectador: fundo desfocado + aparelho + ícone do app.
    sx: escala horizontal do ícone (para o flip)."""
    if bg is not None:
        base = ImageOps.fit(bg, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(28))
        base = Image.blend(base, Image.new("RGB", (W, H), (0, 0, 0)), 0.45)
    else:
        base = Image.new("RGB", (W, H), (12, 12, 18))
    d = ImageDraw.Draw(base)
    pw, ph = 640, 1300
    x0, y0 = (W - pw) // 2, (H - ph) // 2 - 140
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0 + 20, y0 + 40, x0 + pw + 20, y0 + ph + 40), 90, fill=(0, 0, 0, 150))
    base.paste(shadow.filter(ImageFilter.GaussianBlur(30)), (0, 0), shadow.filter(ImageFilter.GaussianBlur(30)))
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), 90, fill=(25, 25, 30), outline=(90, 90, 100), width=6)
    d.rounded_rectangle((x0 + 22, y0 + 22, x0 + pw - 22, y0 + ph - 22), 72, fill=(245, 245, 250))
    d.rounded_rectangle((x0 + pw / 2 - 90, y0 + 42, x0 + pw / 2 + 90, y0 + 92), 25, fill=(25, 25, 30))
    icon = bubble_icon(color, 300)
    if label:
        num = glow_text(label, font(FONT_CAPTION, 300), color, pad=40)
        num = num.resize((int(num.width * 0.9), int(num.height * 0.9)))
        group = Image.new("RGBA", (icon.width + num.width - 30, max(icon.height, num.height)), (0, 0, 0, 0))
        group.paste(icon, (0, (group.height - icon.height) // 2), icon)
        group.paste(num, (icon.width - 30, (group.height - num.height) // 2), num)
    else:
        group = icon
    if group.width > pw - 80:
        r = (pw - 80) / group.width
        group = group.resize((int(group.width * r), int(group.height * r)), Image.LANCZOS)
    gw = max(1, int(group.width * abs(sx)))
    group = group.resize((gw, group.height), Image.BILINEAR)
    base.paste(group, (W // 2 - gw // 2, y0 + ph // 2 - group.height // 2 - 60), group)
    name = "iMessage" + (f" {label}" if label else "")
    f = font(FONT_UI_BOLD, 54)
    d.text((W / 2 - d.textlength(name, font=f) / 2, y0 + ph // 2 + 170), name, font=f, fill=(30, 30, 35))
    return base


LOCKS = {
    "wilma": {
        "time": "1:07", "date": "Tuesday, August 24",
        "notifs": [
            ("Phone", "Wilma ❤️", "Missed call"),
            ("Phone", "Wilma ❤️", "Missed call (12)"),
            ("Messages", "Wilma ❤️", "FRED THE MOUNTAIN IS ON FIRE"),
            ("Phone", "Wilma ❤️", "Missed call (31)"),
            ("Messages", "Wilma ❤️", "PICK UP"),
            ("Phone", "Wilma ❤️", "47 missed calls"),
        ],
    },
}


def lock(name, visible=None, struck=0):
    """Tela de bloqueio com notificações empilhando (ligações perdidas)."""
    spec = LOCKS[name]
    notifs = spec["notifs"] if visible is None else spec["notifs"][:visible]
    bg = Image.new("RGB", (W, H))
    # papel de parede: degradê escuro
    top, bot = (35, 25, 70), (190, 70, 40)
    for y in range(H):
        k = y / H
        ImageDraw.Draw(bg).line((0, y, W, y), fill=tuple(int(top[i] + (bot[i] - top[i]) * k) for i in range(3)))
    d = ImageDraw.Draw(bg)
    fd = font(FONT_UI_BOLD, 44)
    d.text((W / 2 - d.textlength(spec["date"], font=fd) / 2, 210), spec["date"], font=fd, fill=(255, 255, 255))
    ft = font(FONT_UI_BOLD, 230)
    d.text((W / 2 - d.textlength(spec["time"], font=ft) / 2, 250), spec["time"], font=ft, fill=(255, 255, 255))
    y = 620
    fa, fb, fc = font(FONT_UI, 30), font(FONT_UI_BOLD, 40), font(FONT_UI, 38)
    for i, (app, who, txt) in enumerate(reversed(notifs)):
        card = Image.new("RGBA", (W - 100, 170), (0, 0, 0, 0))
        cd = ImageDraw.Draw(card)
        cd.rounded_rectangle((0, 0, card.width - 1, 169), 40, fill=(245, 245, 250, 225))
        icon_c = (52, 199, 89) if app != "Messages" else (52, 199, 89)
        cd.rounded_rectangle((28, 40, 118, 130), 22, fill=icon_c)
        glyph = emoji("📞" if app == "Phone" else "💬", 52)
        card.paste(glyph, (73 - glyph.width // 2, 85 - glyph.height // 2), glyph)
        cd.text((145, 28), app.upper(), font=fa, fill=(110, 110, 120))
        cd.text((card.width - 120, 28), "now", font=fa, fill=(110, 110, 120))
        cd.text((145, 66), who, font=fb, fill=(20, 20, 25), embedded_color=True)
        red = "missed" in txt.lower() or txt.isupper()
        cd.text((145, 116), txt, font=fc, fill=(215, 30, 30) if red else (40, 40, 45))
        bg.paste(card, (50, y), card)
        y += 190
    return bg


CALS = {
    "sunday": {"month": "APRIL 1912", "num": "14", "day": "SUNDAY", "time": "11:40 PM", "color": (200, 30, 40)},
    "monday": {"month": "APRIL 1912", "num": "15", "day": "MONDAY", "time": "12:00 AM", "color": (200, 30, 40)},
    "monday_sink": {"month": "APRIL 1912", "num": "15", "day": "MONDAY", "time": "2:20 AM", "color": (200, 30, 40)},
}


def calendar(name):
    """Folhinha de calendário antiga com dia, nome do dia e hora."""
    c = CALS[name]
    bg = Image.new("RGB", (W, H), (28, 24, 22))
    d = ImageDraw.Draw(bg)
    for i in range(0, H, 6):
        d.line((0, i, W, i), fill=(34, 29, 26))
    x0, y0, x1, y1 = 170, 250, W - 170, 1140     # acima da legenda (63% da altura)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0 + 25, y0 + 35, x1 + 25, y1 + 35), 30, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(25))
    bg.paste(sh, (0, 0), sh)
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(246, 240, 226))
    d.rounded_rectangle((x0, y0, x1, y0 + 200), 30, fill=c["color"])
    d.rectangle((x0, y0 + 150, x1, y0 + 200), fill=c["color"])
    for rx in (x0 + 160, x1 - 160):
        d.ellipse((rx - 28, y0 - 40, rx + 28, y0 + 16), fill=(70, 70, 75))
    d.text((W / 2, y0 + 104), c["month"], font=font(FONT_CAPTION, 100), fill="white", anchor="mm")
    d.text((W / 2, y0 + 430), c["num"], font=font(FONT_CAPTION, 360), fill=(30, 30, 30), anchor="mm")
    d.text((W / 2, y0 + 700), c["day"], font=font(FONT_CAPTION, 140), fill=c["color"], anchor="mm")
    d.text((W / 2, y0 + 812), c["time"], font=font(FONT_UI_BOLD, 66), fill=(90, 80, 70), anchor="mm")
    return bg


FB = {
    "garfield": {"name": "Garfield", "when": "April 14, 1912 at 11:41 PM", "text": "I hate Mondays 😩",
                 "likes": "1.2K", "comments": "312 comments", "avatar": (245, 140, 20)},
}


def facebook(name):
    """Post falso do Facebook (anacronismo)."""
    f = FB[name]
    bg = Image.new("RGB", (W, H), (240, 242, 245))
    d = ImageDraw.Draw(bg)
    d.rectangle((0, 0, W, 170), fill=(255, 255, 255))
    d.text((50, 85), "facebook", font=font(FONT_UI_BOLD, 76), fill=(24, 119, 242), anchor="lm")
    x0, y0, x1 = 30, 420, W - 30
    d.rounded_rectangle((x0, y0, x1, y0 + 820), 30, fill="white")
    d.ellipse((x0 + 40, y0 + 40, x0 + 180, y0 + 180), fill=f["avatar"])
    d.text((x0 + 110, y0 + 110), f["name"][0], font=font(FONT_UI_BOLD, 80), fill="white", anchor="mm")
    d.text((x0 + 210, y0 + 75), f["name"], font=font(FONT_UI_BOLD, 54), fill=(5, 5, 5), anchor="lm")
    d.text((x0 + 210, y0 + 145), f["when"], font=font(FONT_UI, 36), fill=(101, 103, 107),
           anchor="lm", embedded_color=True)
    tf = font(FONT_UI, 88)
    tx = x0 + 50
    for part in f["text"].split(" "):
        if any(ord(ch) > 0x2600 for ch in part):
            e = emoji(part, 92)
            bg.paste(e, (int(tx), y0 + 300), e)
            tx += e.width + 20
        else:
            d.text((tx, y0 + 300), part, font=tf, fill=(5, 5, 5))
            tx += d.textlength(part + " ", font=tf)
    re_ = [emoji("😆", 60), emoji("😢", 60), emoji("👍", 60)]
    rx = x0 + 50
    for e in re_:
        bg.paste(e, (rx, y0 + 560), e)
        rx += 55
    d.text((rx + 20, y0 + 590), f["likes"], font=font(FONT_UI, 40), fill=(101, 103, 107), anchor="lm")
    d.text((x1 - 50, y0 + 590), f["comments"], font=font(FONT_UI, 40), fill=(101, 103, 107), anchor="rm")
    d.line((x0 + 40, y0 + 660, x1 - 40, y0 + 660), fill=(220, 222, 226), width=3)
    for i, lab in enumerate(["Like", "Comment", "Share"]):
        cx = x0 + (x1 - x0) * (i * 2 + 1) / 6
        d.text((cx, y0 + 740), lab, font=font(FONT_UI_BOLD, 42), fill=(101, 103, 107), anchor="mm")
    return bg


def anim_count(ref):
    """Quantos itens um asset animado revela (mensagens ou notificações)."""
    kind, _, name = ref[1:].partition(":")
    if kind == "chat":
        return len(CHATS[name]["msgs"])
    if kind == "lock":
        return len(LOCKS[name]["notifs"])
    return 0


def outro(handles, accent=(245, 168, 0)):
    """Cartão final: fundo amarelo com interrogações, joinha e as redes."""
    bg = Image.new("RGB", (W, H), accent)
    d = ImageDraw.Draw(bg)
    fq = font(FONT_CAPTION, 420)
    rnd = random.Random(3)
    for gy in range(-200, H, 380):
        for gx in range(-150, W, 360):
            d.text((gx + rnd.randint(-40, 40), gy + rnd.randint(-40, 40)), "?", font=fq, fill=(18, 22, 48))
    thumb = emoji("👍", 260)
    bg.paste(thumb, ((W - thumb.width) // 2, 430), thumb)
    f = font(FONT_CAPTION, 74)
    y = 780
    for label, handle in handles:
        txt = f"{label}  {handle}".upper()
        tw = d.textlength(txt, font=f)
        d.text(((W - tw) / 2, y), txt, font=f, fill="white", stroke_width=9, stroke_fill="black")
        y += 120
    return bg


def placeholder(name, prompt):
    bg = Image.new("RGB", (W, H), (60, 60, 70))
    d = ImageDraw.Draw(bg)
    d.text((80, 700), f"FALTA: {name}", font=font(FONT_CAPTION, 90), fill=(255, 220, 0))
    y = 860
    for line in textwrap.wrap(prompt or "", 38):
        d.text((80, y), line, font=font(FONT_UI, 44), fill="white")
        y += 58
    return bg


def make(ref, handles=None):
    """Resolve '@icon:2:#hex', '@chat:family', '@outro'."""
    kind, _, rest = ref[1:].partition(":")
    if kind == "icon":
        label, _, color = rest.partition(":")
        return app_icon(label, color or "#34C759")
    if kind == "chat":
        return chat(rest)
    if kind == "lock":
        return lock(rest)
    if kind == "cal":
        return calendar(rest)
    if kind == "fb":
        return facebook(rest)
    if kind == "phone":
        label, _, color = rest.partition(":")
        return phone(label, color or "#34C759", None)
    if kind == "outro":
        return outro(handles or [])
    raise ValueError(f"asset desconhecido: {ref}")
