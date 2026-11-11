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
    "fyre": {"month": "APRIL 2017", "num": "27", "day": "THURSDAY", "time": "ARRIVAL DAY", "color": (230, 90, 20)},
    "apollo": {"month": "APRIL 1970", "num": "13", "day": "MONDAY", "time": "9:08 PM CST", "color": (20, 60, 140)},
    "oscars": {"month": "FEBRUARY 2017", "num": "26", "day": "SUNDAY", "time": "9:05 PM", "color": (170, 20, 30)},
    "suez": {"month": "MARCH 2021", "num": "23", "day": "TUESDAY", "time": "7:40 AM", "color": (20, 90, 160)},
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


TIPS = {
    "classic": {
        "bezel": (22, 22, 24), "merchant": "Self-Checkout  ·  no staff on duty",
        "lines": [("Dasani Water 16.9 oz", "$2.49")], "total": "$2.49",
        "ask": "Would you like to add a tip?",
        "tiles": [("20%", "$0.50"), ("25%", "$0.62"), ("30%", "$0.75")],
        "custom": "Custom amount", "no": "No tip", "no_size": 24, "label": None, "label_color": None},
    "gold": {
        "bezel": (205, 160, 40), "merchant": "Self-Checkout",
        "lines": [("Dasani Water 16.9 oz", "$2.49")], "total": "$2.49",
        "ask": "No tip screen.", "sub": "Just pay and go.", "tiles": [],
        "custom": None, "no": None, "label": "TIP SCREEN 2", "label_color": (255, 205, 60)},
    "krabs": {
        "bezel": (22, 22, 24), "merchant": "THE KRUSTY KRAB",
        "lines": [("Krabby Patty", "$3.99"), ("Service fee (18%)", "$0.72"),
                  ("Kitchen appreciation fee", "$0.50"), ("Breathing fee", "$0.25")], "total": "$5.46",
        "ask": "Add a tip for SpongeBob?",
        "tiles": [("45%", "$2.46"), ("60%", "$3.28"), ("75%", "$4.10")],
        "custom": "Custom: your soul", "no": "No tip (SpongeBob will be fired)", "no_size": 20,
        "label": None, "label_color": None},
    "three_order": {
        "bezel": (190, 20, 30), "merchant": "THE KRUSTY KRAB",
        "lines": [("Your order", "not started")], "total": "$0.00",
        "ask": "Tip first. Order later.",
        "tiles": [("25%", "of ?"), ("35%", "of ?"), ("50%", "of ?")],
        "custom": None, "no": None, "label": "TIP SCREEN 3", "label_color": (255, 70, 70)},
    "three_walk": {
        "bezel": (190, 20, 30), "merchant": "📍 You walked past the Krusty Krab",
        "lines": [("Distance", "30 ft"), ("Time near entrance", "4 sec")], "total": None,
        "ask": "Add a tip for walking by?",
        "tiles": [("$5", ""), ("$10", ""), ("$20", "")],
        "custom": None, "no": None, "label": "TIP SCREEN 3", "label_color": (255, 70, 70)},
}


def _txt(d, im, xy, text, fnt, fill, anchor="la", esize=None):
    """Texto com emoji colorido no começo (ex.: 📍)."""
    if text and ord(text[0]) > 0x2600:
        ch, rest = text.split(" ", 1)
        e = emoji(ch, esize or int(fnt.size * 1.1))
        x, y = xy
        if anchor[0] == "m":
            tw = d.textlength(rest, font=fnt) + e.width + 12
            x = x - tw / 2
        im.paste(e, (int(x), int(y - e.height / 2)), e)
        d.text((x + e.width + 12, y), rest, font=fnt, fill=fill, anchor="lm")
    else:
        d.text(xy, text, font=fnt, fill=fill, anchor=anchor)


def tipscreen(name, bg=None):
    """Terminal de pagamento de balcão (estilo iPad/Square, modo escuro), levemente
    inclinado, sobre o fundo desfocado de uma foto do projeto."""
    c = TIPS[name]
    if bg is not None:
        base = ImageOps.fit(bg, (W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(22))
        base = Image.blend(base, Image.new("RGB", (W, H), (0, 0, 0)), 0.35)
    else:
        base = Image.new("RGB", (W, H), (40, 34, 30))
    # conteúdo da tela desenhado numa camada alta; depois a moldura é feita no tamanho exato
    DW = 860
    SW = DW - 88
    scr = Image.new("RGBA", (SW, 1400), (14, 14, 16, 255))
    d = ImageDraw.Draw(scr)
    sx0, sy0, sx1 = 0, 0, SW
    cx = SW / 2
    # barra de status
    fs = font(FONT_UI_BOLD, 24)
    d.text((sx0 + 34, sy0 + 26), "9:41", font=fs, fill=(200, 200, 205))
    d.rounded_rectangle((sx1 - 80, sy0 + 28, sx1 - 36, sy0 + 46), 5, outline=(200, 200, 205), width=2)
    d.rectangle((sx1 - 76, sy0 + 32, sx1 - 50, sy0 + 42), fill=(200, 200, 205))
    y = sy0 + 90
    _txt(d, scr, (cx, y), c["merchant"], font(FONT_UI_BOLD, 34), (235, 235, 240), anchor="mm")
    y += 50
    d.line((sx0 + 40, y, sx1 - 40, y), fill=(50, 50, 56), width=2)
    y += 26
    fl = font(FONT_UI, 30)
    for a, b in c["lines"]:
        d.text((sx0 + 50, y), a, font=fl, fill=(170, 170, 178))
        d.text((sx1 - 50, y), b, font=fl, fill=(170, 170, 178), anchor="ra")
        y += 44
    if c.get("total"):
        d.text((sx0 + 50, y + 6), "Total", font=font(FONT_UI_BOLD, 34), fill="white")
        d.text((sx1 - 50, y + 6), c["total"], font=font(FONT_UI_BOLD, 34), fill="white", anchor="ra")
        y += 60
    y += 20
    d.text((cx, y + 30), c["ask"], font=font(FONT_UI_BOLD, 50), fill="white", anchor="mm")
    y += 90
    if c.get("sub"):
        d.text((cx, y + 10), c["sub"], font=font(FONT_UI, 40), fill=(170, 170, 178), anchor="mm")
        ck = Image.new("RGBA", (220, 220), (0, 0, 0, 0))
        ImageDraw.Draw(ck).ellipse((0, 0, 219, 219), fill=(52, 199, 89))
        ImageDraw.Draw(ck).line([(60, 115), (98, 152), (165, 75)], fill="white", width=22, joint="curve")
        scr.paste(ck, (int(cx - 110), int(y + 90)), ck)
        y += 330
    tiles = c["tiles"]
    if tiles:
        n = len(tiles)
        gap = 22
        tw = (sx1 - sx0 - 80 - gap * (n - 1)) / n
        th = 210
        for i, (big, small) in enumerate(tiles):
            x = sx0 + 40 + i * (tw + gap)
            d.rounded_rectangle((x, y, x + tw, y + th), 26, fill=(245, 245, 247))
            d.text((x + tw / 2, y + (78 if small else th / 2)), big, font=font(FONT_UI_BOLD, 64),
                   fill=(14, 14, 16), anchor="mm")
            if small:
                d.text((x + tw / 2, y + 150), small, font=font(FONT_UI, 34), fill=(90, 90, 96), anchor="mm")
        y += th + 24
    if c.get("custom"):
        d.rounded_rectangle((sx0 + 40, y, sx1 - 40, y + 90), 22, fill=(38, 38, 42))
        d.text((cx, y + 45), c["custom"], font=font(FONT_UI_BOLD, 36), fill="white", anchor="mm")
        y += 110
    if c.get("no"):
        d.text((cx, y + 22), c["no"], font=font(FONT_UI, c.get("no_size", 24)), fill=(95, 95, 100), anchor="mm")
    y_end = int(y + 60)
    scr = scr.crop((0, 0, SW, y_end))
    mask = Image.new("L", scr.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, scr.width - 1, scr.height - 1), 36, fill=255)
    DH = y_end + 104
    dev = Image.new("RGBA", (DW, DH), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dev)
    dd.rounded_rectangle((0, 0, DW - 1, DH - 1), 70, fill=c["bezel"] + (255,))
    dd.rounded_rectangle((8, 8, DW - 9, DH - 9), 64, outline=tuple(min(255, v + 40) for v in c["bezel"]) + (255,), width=4)
    dd.ellipse((DW / 2 - 9, 22, DW / 2 + 9, 40), fill=(10, 10, 12))
    dev.paste(scr, (44, 60), mask)
    # inclinação leve (perspectiva) e sombra
    k = 0.035
    quad = (DW * k, 0, 0, DH, DW, DH, DW * (1 - k), 0)
    dev = dev.transform((DW, DH), Image.QUAD, quad, Image.BICUBIC)
    sc = min(1.15, 860 / DH, 940 / DW)          # o maior possível acima da legenda
    dev = dev.resize((int(DW * sc), int(DH * sc)), Image.LANCZOS)
    DW, DH = dev.size
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = (W - DW) // 2, max(270, 1130 - DH)
    ImageDraw.Draw(sh).rounded_rectangle((ox + 30, oy + 50, ox + DW + 30, oy + DH + 50), 70, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base.paste(sh, (0, 0), sh)
    base.paste(dev, (ox, oy), dev)
    if c.get("label"):
        ImageDraw.Draw(base).text((W / 2, oy - 2), c["label"], font=font(FONT_CAPTION, 70), fill=c["label_color"],
                                  anchor="mb", stroke_width=6, stroke_fill="black")
    return base


RECEIPTS = {
    "fyre": [("FYRE CATERING", "big"), ("ORDER #0001 · VIP", "bold"), ("", ""),
             ("Lobster:", "300"), ("Sushi:", "1,200 pcs"), ("Champagne:", "400"),
             ("Eaten by:", "TAZ"), ("Time:", "4 seconds"), ("", ""),
             ("LEFT FOR GUESTS", "1 sandwich")],
    "spongebob": [("KRUSTY KRAB", "big"), ("EMPLOYEE TIP REPORT", "bold"), ("", ""),
                  ("Employee:", "SpongeBob S."), ("Since:", "1999"), ("Shifts:", "9,862"),
                  ("Guests tipped:", "$48,912.40"), ("Mr. Krabs kept:", "$48,911.78"), ("", ""),
                  ("TOTAL TIPS RECEIVED", "$0.62")],
}


def receipt(name):
    """Recibo térmico (acima da área da legenda)."""
    rows = RECEIPTS[name]
    bg = Image.new("RGB", (W, H), (28, 30, 34))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 200, 250, W - 200, 1150
    paper = Image.new("RGBA", (x1 - x0, y1 - y0), (250, 248, 240, 255))
    pd = ImageDraw.Draw(paper)
    # serrilha embaixo
    for i in range(0, paper.width, 30):
        pd.polygon([(i, paper.height), (i + 15, paper.height - 18), (i + 30, paper.height)], fill=(28, 30, 34, 255))
    mono_b = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 40)
    mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 36)
    big = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 72)
    y = 60
    for a, b in rows:
        if b == "big":
            pd.text((paper.width / 2, y + 30), a, font=big, fill=(20, 20, 20), anchor="mm"); y += 100
        elif b == "bold":
            pd.text((paper.width / 2, y + 20), a, font=mono_b, fill=(20, 20, 20), anchor="mm"); y += 70
        elif not a:
            pd.text((40, y), "-" * 30, font=mono, fill=(120, 120, 120)); y += 60
        elif a.startswith("TOTAL"):
            pd.text((40, y), a, font=mono_b, fill=(20, 20, 20))
            pd.text((paper.width - 40, y + 60), b, font=big, fill=(200, 20, 30), anchor="ra"); y += 160
        else:
            pd.text((40, y), a, font=mono, fill=(40, 40, 40))
            pd.text((paper.width - 40, y), b, font=mono, fill=(40, 40, 40), anchor="ra"); y += 60
    for i in range(40):
        w = 4 if i % 3 else 8
        pd.rectangle((80 + i * 16, y + 10, 80 + i * 16 + w, y + 70), fill=(20, 20, 20))
    paper = paper.rotate(-2.5, resample=Image.BICUBIC, expand=True, fillcolor=(0, 0, 0, 0))
    bg.paste(paper, (x0 - 20, y0), paper)
    return bg


STATS = {
    "fyre250k": {"num": "$250K", "text": ["for ONE Instagram post", "promoting the festival"], "src": "Fyre Festival, 2017"},
    "dropped": {"num": "1968", "text": ["Oxygen tank No. 2 was", "dropped 2 inches at the factory,", "18 months before launch"],
                "src": "Source: Apollo 13 Review Board, NASA, 1970"},
    "evergiven": {"num": "400 m", "text": ["longer than the Eiffel", "Tower is tall"], "src": "Ever Given · 1,312 ft"},
    "suez96": {"num": "$9.6B", "text": ["of trade blocked", "every single day"], "src": "Source: Lloyd's List, March 2021"},
    "rockodds": {"num": "99%", "text": ["of the fish bet", "on Patrick"], "src": "Under-A-Rock Championship 2021"},
    "extinct75": {"num": "75%", "text": ["of all species on Earth", "went extinct"], "src": "Chicxulub impact, 66 million years ago"},
    "pew72": {"num": "72%", "text": ["of Americans say tipping", "is expected in more places", "than 5 years ago"],
              "src": "Source: Pew Research Center, 2023"},
}


def stat(name):
    """Cartão de estatística com a fonte (o fato verdadeiro do vídeo)."""
    c = STATS[name]
    bg = Image.new("RGB", (W, H), (14, 18, 30))
    d = ImageDraw.Draw(bg)
    d.text((W / 2, 520), c["num"], font=font(FONT_CAPTION, 380 if len(c["num"]) <= 3 else 280), fill=(255, 214, 0), anchor="mm",
           stroke_width=10, stroke_fill="black")
    y = 800
    for line in c["text"]:
        d.text((W / 2, y), line, font=font(FONT_UI_BOLD, 60), fill="white", anchor="mm")
        y += 80
    d.text((W / 2, y + 40), c["src"], font=font(FONT_UI, 36), fill=(150, 160, 180), anchor="mm")
    return bg


DOCS = {
    "decree": {"title": "Decree", "sub": "City Council of Strasbourg · July 1518",
               "lines": ["The dancing sickness shall be", "cured with MORE MUSIC.", "",
                         "Musicians shall be hired.", "A wooden stage shall be built."],
               "sign": "By order of the Council", "seal": (150, 20, 25)},
    "contract": {"title": "Contract", "sub": "Strasbourg · Anno Domini 1518",
                 "lines": ["The Backyardigans shall play", "for the dancers of the city.", "",
                           "Duration: TWO MONTHS", "Payment: one basket of", "pretzels per song.",
                           "UNLIMITED PRETZELS."],
                 "sign": "Tasha", "seal": (150, 20, 25), "signature": True},
    "program": {"title": "Program", "sub": "Weekly music of the Dancing Plague",
                "lines": ["Week I ......... Tango", "Week II ......... Disco", "Week III ...... Bollywood",
                          "Week IV ........ Opera", "Week V ...... Hip-Hop"],
                "sign": "The Backyardigans", "seal": (40, 70, 140)},
    "paracelsus": {"title": "Paracelsus", "sub": "On the dancing of Frau Troffea",
                   "lines": ["She began to dance only", "to annoy her husband,", "and would not stop,",
                             "so that he would", "look like a fool."],
                   "sign": "Theophrastus Paracelsus", "seal": None},
}


def parchment(name):
    """Documento de 1518 em pergaminho (acima da área da legenda)."""
    from .common import ROOT
    c = DOCS[name]
    goth = lambda sz: ImageFont.truetype(str(ROOT / "assets/fonts/UnifrakturMaguntia-Book.ttf"), sz)
    fell = lambda sz: ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENrm28P.ttf"), sz)
    fell_i = lambda sz: ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENit28P.ttf"), sz)
    bg = Image.new("RGB", (W, H), (32, 24, 18))
    rnd = random.Random(hash(name) % 1000)
    # mesa de madeira escura
    d0 = ImageDraw.Draw(bg)
    for y in range(0, H, 3):
        v = 30 + int(8 * math.sin(y / 37.0)) + rnd.randint(-3, 3)
        d0.line((0, y, W, y), fill=(v + 8, v, v - 8))
    PW, PH = 860, 960
    pap = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pap)
    # borda irregular
    pts = []
    for i in range(0, PW, 20):
        pts.append((i, rnd.randint(0, 14)))
    for i in range(0, PH, 20):
        pts.append((PW - rnd.randint(0, 14), i))
    for i in range(PW, 0, -20):
        pts.append((i, PH - rnd.randint(0, 14)))
    for i in range(PH, 0, -20):
        pts.append((rnd.randint(0, 14), i))
    pd.polygon(pts, fill=(232, 214, 172, 255))
    # manchas de idade
    stains = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stains)
    for _ in range(40):
        x, y, r = rnd.randint(0, PW), rnd.randint(0, PH), rnd.randint(20, 120)
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(150, 110, 60, rnd.randint(8, 22)))
    stains = stains.filter(ImageFilter.GaussianBlur(25))
    mask = pap.getchannel("A")
    pap = Image.alpha_composite(pap, Image.composite(stains, Image.new("RGBA", (PW, PH)), mask))
    pd = ImageDraw.Draw(pap)
    ink = (52, 32, 18)
    pd.text((PW / 2, 120), c["title"], font=goth(118), fill=ink, anchor="mm")
    pd.text((PW / 2, 215), c["sub"], font=fell_i(36), fill=(95, 65, 40), anchor="mm")
    pd.line((120, 260, PW - 120, 260), fill=(120, 85, 50), width=3)
    y = 320
    for line in c["lines"]:
        if line:
            big = line.isupper() or "MORE MUSIC" in line or "TWO MONTHS" in line
            f = fell(54 if big else 46)
            pd.text((PW / 2, y), line, font=f, fill=(140, 20, 20) if big else ink, anchor="mm")
        y += 66
    y += 20
    if c.get("signature"):
        pd.text((PW / 2 - 60, y + 30), c["sign"], font=fell_i(76), fill=(30, 40, 110), anchor="mm")
        pd.line((PW / 2 - 230, y + 75, PW / 2 + 110, y + 75), fill=ink, width=2)
    else:
        pd.text((PW / 2 - 60, y + 30), c["sign"], font=fell_i(42), fill=ink, anchor="mm")
    if c.get("seal"):
        sx, sy = PW - 150, PH - 95
        col = c["seal"]
        for k in range(10):
            ang = k * 36 * math.pi / 180
            rx, ry = sx + 58 * math.cos(ang), sy + 58 * math.sin(ang)
            pd.ellipse((rx - 22, ry - 22, rx + 22, ry + 22), fill=col)
        pd.ellipse((sx - 62, sy - 62, sx + 62, sy + 62), fill=col)
        pd.ellipse((sx - 44, sy - 44, sx + 44, sy + 44), outline=tuple(min(255, v + 50) for v in col), width=5)
        pd.text((sx, sy + 4), "S", font=goth(70), fill=tuple(min(255, v + 60) for v in col), anchor="mm")
    pap = pap.rotate(rnd.uniform(-3, 3), resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = (W - pap.width) // 2, 200
    ImageDraw.Draw(sh).rectangle((ox + 30, oy + 40, ox + pap.width + 30, oy + pap.height + 30), fill=(0, 0, 0, 160))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    bg.paste(sh, (0, 0), sh)
    bg.paste(pap, (ox, oy), pap)
    return bg


def old_map(name):
    """Mapa antigo: Estrasburgo -> Santuário de São Vito (Saverne), com trilha de dança."""
    from .common import ROOT
    goth = lambda sz: ImageFont.truetype(str(ROOT / "assets/fonts/UnifrakturMaguntia-Book.ttf"), sz)
    fell = lambda sz: ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENrm28P.ttf"), sz)
    fell_i = lambda sz: ImageFont.truetype(str(ROOT / "assets/fonts/IMFeENit28P.ttf"), sz)
    rnd = random.Random(7)
    bg = Image.new("RGB", (W, H), (32, 24, 18))
    d0 = ImageDraw.Draw(bg)
    for y in range(0, H, 3):
        v = 30 + int(8 * math.sin(y / 37.0)) + rnd.randint(-3, 3)
        d0.line((0, y, W, y), fill=(v + 8, v, v - 8))
    PW, PH = 960, 960
    pap = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    pts = [(i, rnd.randint(0, 14)) for i in range(0, PW, 20)] + [(PW - rnd.randint(0, 14), i) for i in range(0, PH, 20)] \
        + [(i, PH - rnd.randint(0, 14)) for i in range(PW, 0, -20)] + [(rnd.randint(0, 14), i) for i in range(PH, 0, -20)]
    ImageDraw.Draw(pap).polygon(pts, fill=(228, 208, 165, 255))
    st = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    for _ in range(45):
        x, y, r = rnd.randint(0, PW), rnd.randint(0, PH), rnd.randint(20, 130)
        sd.ellipse((x - r, y - r, x + r, y + r), fill=(140, 100, 55, rnd.randint(8, 24)))
    st = st.filter(ImageFilter.GaussianBlur(28))
    pap = Image.alpha_composite(pap, Image.composite(st, Image.new("RGBA", (PW, PH)), pap.getchannel("A")))
    d = ImageDraw.Draw(pap)
    ink, red = (60, 38, 20), (150, 25, 25)
    d.text((PW / 2, 85), "The Road to the Shrine", font=goth(78), fill=ink, anchor="mm")
    d.text((PW / 2, 150), "Anno Domini 1518", font=fell_i(34), fill=(100, 70, 40), anchor="mm")
    # rio Reno (direita)
    rv = [(PW - 120 + 30 * math.sin(y / 70.0), y) for y in range(200, PH - 40, 10)]
    d.line(rv, fill=(90, 120, 150), width=10, joint="curve")
    d.text((PW - 175, 600), "Rhine", font=fell_i(32), fill=(70, 95, 125), anchor="mm")
    # montanhas (Vosges, esquerda/cima)
    for mx, my, ms in [(150, 330, 70), (240, 300, 85), (330, 340, 65), (110, 430, 55), (200, 420, 75), (420, 290, 55)]:
        d.polygon([(mx - ms, my + ms * 0.6), (mx, my - ms * 0.7), (mx + ms, my + ms * 0.6)], fill=(205, 180, 135), outline=ink)
        d.line([(mx, my - ms * 0.7), (mx + ms * 0.35, my - ms * 0.2)], fill=ink, width=2)
    d.text((270, 500), "Vosges Mountains", font=fell_i(30), fill=(100, 70, 40), anchor="mm")
    # santuário (capela) no alto à esquerda
    cx, cy = 230, 235
    d.rectangle((cx - 35, cy - 10, cx + 35, cy + 40), fill=(240, 230, 205), outline=ink, width=3)
    d.polygon([(cx - 45, cy - 10), (cx, cy - 55), (cx + 45, cy - 10)], fill=(170, 60, 50), outline=ink)
    d.line([(cx, cy - 90), (cx, cy - 55)], fill=ink, width=4)
    d.line([(cx - 14, cy - 76), (cx + 14, cy - 76)], fill=ink, width=4)
    d.text((cx + 140, cy - 30), "Shrine of", font=fell(34), fill=ink, anchor="mm")
    d.text((cx + 140, cy + 10), "Saint Vitus", font=fell(40), fill=red, anchor="mm")
    # Estrasburgo (embaixo à direita): casinhas + catedral
    sx, sy = 640, 760
    for k, (hx, hh) in enumerate([(-90, 40), (-45, 55), (45, 50), (90, 38)]):
        d.rectangle((sx + hx - 20, sy - hh, sx + hx + 20, sy), fill=(240, 228, 200), outline=ink, width=2)
        d.polygon([(sx + hx - 24, sy - hh), (sx + hx, sy - hh - 22), (sx + hx + 24, sy - hh)], fill=(150, 70, 50), outline=ink)
    d.rectangle((sx - 14, sy - 120, sx + 14, sy), fill=(215, 150, 140), outline=ink, width=2)
    d.polygon([(sx - 14, sy - 120), (sx, sy - 175), (sx + 14, sy - 120)], fill=(200, 130, 120), outline=ink)
    d.text((sx, sy + 40), "Strasbourg", font=fell(46), fill=ink, anchor="mm")
    # pretzel desenhado ao lado da cidade
    px, py = sx + 150, sy - 70
    for a0 in (0, 1):
        d.arc((px - 40 + a0 * 30, py - 30, px + 10 + a0 * 30, py + 20), 0, 360, fill=(150, 90, 40), width=8)
    d.arc((px - 30, py - 5, px + 40, py + 45), 180, 360, fill=(150, 90, 40), width=8)
    d.text((px + 5, py + 60), "pretzels", font=fell_i(26), fill=(120, 70, 30), anchor="mm")
    # trilha pontilhada da cidade ao santuário
    path = []
    for i in range(0, 101):
        t = i / 100
        x = sx - 60 + (cx + 40 - (sx - 60)) * t + 70 * math.sin(t * math.pi * 2.2)
        y = sy - 30 + (cy + 60 - (sy - 30)) * t
        path.append((x, y))
    for i in range(0, len(path) - 1, 4):
        d.line([path[i], path[i + 2]], fill=red, width=6)
    # pegadas de dança ao longo da trilha
    for i in range(8, 95, 14):
        x, y = path[i]
        side = 14 if (i // 14) % 2 else -14
        d.ellipse((x + side - 7, y - 11, x + side + 7, y + 11), fill=ink)
    d.text((path[50][0] + 120, path[50][1]), "the dancers", font=fell_i(30), fill=red, anchor="mm")
    # rosa dos ventos
    rx, ry = 110, PH - 120
    d.polygon([(rx, ry - 60), (rx + 12, ry), (rx, ry + 60), (rx - 12, ry)], fill=ink)
    d.polygon([(rx - 60, ry), (rx, ry - 12), (rx + 60, ry), (rx, ry + 12)], fill=(150, 120, 80))
    d.text((rx, ry - 80), "N", font=fell(30), fill=ink, anchor="mm")
    pap = pap.rotate(-2, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = (W - pap.width) // 2, 200
    ImageDraw.Draw(sh).rectangle((ox + 30, oy + 40, ox + pap.width + 30, oy + pap.height + 30), fill=(0, 0, 0, 160))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    bg.paste(sh, (0, 0), sh)
    bg.paste(pap, (ox, oy), pap)
    return bg


STONES = {
    "records": {"title": "Official Records", "lines": ["66,000,000 B.C.", "", "Barney warned", "everyone.", "", "(in a song)"]},
    "rules": {"title": "Barney's Rules", "lines": ["Rule #1:", "Never say", "anything sad.", "", "Rule #2:", "Hug everyone."]},
    "rockrules": {"title": "Official Rules", "flat": True, "lines": ["Rule 1:", "Get under a rock.", "Rule 2:", "Stay there.", "Rule 3:", "No snacks."]},
    "song": {"title": "Barney's Song", "lines": ["There's a big rock", "in the sky,", "it's coming", "to say hi!", "", "la la la ♪"]},
}


def stone(name):
    """Tábua de pedra com texto entalhado (pré-histórico)."""
    c = STONES[name]
    rnd = random.Random(11)
    bg = Image.new("RGB", (W, H), (20, 50, 60) if c.get("flat") else (70, 110, 60))
    d0 = ImageDraw.Draw(bg)
    for y in range(0 if not c.get("flat") else H, H):   # céu pré-histórico em degradê
        k = y / H
        d0.line((0, y, W, y), fill=(int(240 - 120 * k), int(150 - 60 * k), int(90 - 30 * k)))
    PW, PH = 820, 960
    tab = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    td = ImageDraw.Draw(tab)
    td.rounded_rectangle((0, 0, PW - 1, PH - 1), 120, fill=(140, 132, 120, 255))
    tex = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    xd = ImageDraw.Draw(tex)
    for _ in range(900):
        x, y, r = rnd.randint(0, PW), rnd.randint(0, PH), rnd.randint(2, 9)
        v = rnd.randint(-35, 35)
        xd.ellipse((x - r, y - r, x + r, y + r), fill=(140 + v, 132 + v, 120 + v, 120))
    tex = tex.filter(ImageFilter.GaussianBlur(2))
    tab = Image.alpha_composite(tab, Image.composite(tex, Image.new("RGBA", (PW, PH)), tab.getchannel("A")))
    td = ImageDraw.Draw(tab)
    td.rounded_rectangle((24, 24, PW - 25, PH - 25), 100, outline=(95, 88, 78, 255), width=8)
    def carve(xy, text, f):
        x, y = xy
        td.text((x + 3, y + 3), text, font=f, fill=(210, 205, 195), anchor="mm")
        td.text((x, y), text, font=f, fill=(70, 62, 55), anchor="mm")
    carve((PW / 2, 130), c["title"], font(FONT_CAPTION, 74))
    td.line((140, 190, PW - 140, 190), fill=(95, 88, 78), width=5)
    y = 290
    for line in c["lines"]:
        if line:
            carve((PW / 2, y), line, font(FONT_CAPTION, 76 if "♪" not in line else 60))
        y += 105
    # notas musicais coloridas (só na tábua da música)
    for nx, ny in ([(110, 330), (PW - 110, 480), (120, 700)] if name == "song" else []):
        e = emoji("🎵", 80)
        tab.paste(e, (nx - 40, ny - 40), e)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = (W - PW) // 2, 190
    ImageDraw.Draw(sh).rounded_rectangle((ox + 30, oy + 40, ox + PW + 30, oy + PH + 30), 120, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(28))
    bg.paste(sh, (0, 0), sh)
    bg.paste(tab, (ox, oy), tab)
    return bg


def timeline(name):
    """Linha do tempo: Estegossauro -> T. rex -> você (o fato real em forma visual)."""
    bg = Image.new("RGB", (W, H), (14, 18, 30))
    d = ImageDraw.Draw(bg)
    d.text((W / 2, 240), "MILLIONS OF YEARS AGO", font=font(FONT_CAPTION, 62), fill=(255, 214, 0), anchor="mm")
    x0, x1, y = 220, W - 190, 640
    d.line((x0, y, x1, y), fill="white", width=10)
    pts = [(150, "Stegosaurus", "🦕", (90, 200, 120)), (67, "T. rex", "🦖", (255, 80, 80)), (0, "You", "🧍", (90, 170, 255))]
    def X(m): return x1 - (x1 - x0) * m / 150
    for m, lab, em, col in pts:
        x = X(m)
        d.ellipse((x - 18, y - 18, x + 18, y + 18), fill=col)
        e = emoji(em, 130)
        bg.paste(e, (int(x - e.width / 2), y - 70 - e.height), e)
        d.text((x, y + 60), lab, font=font(FONT_UI_BOLD, 40), fill="white", anchor="mm")
        d.text((x, y + 110), f"{m}M" if m else "today", font=font(FONT_UI, 34), fill=(170, 175, 190), anchor="mm")
    # chaves com as distâncias
    def brace(a, b, txt, col, yy):
        xa, xb = X(a), X(b)
        d.line((xa, yy, xb, yy), fill=col, width=6)
        d.line((xa, yy - 18, xa, yy + 18), fill=col, width=6)
        d.line((xb, yy - 18, xb, yy + 18), fill=col, width=6)
        d.text(((xa + xb) / 2, yy + 50), txt, font=font(FONT_CAPTION, 48), fill=col, anchor="mm")
    brace(150, 67, "83 million years", (90, 200, 120), 860)
    brace(67, 0, "67 million years", (90, 170, 255), 990)
    return bg


def tvguide(name):
    """Anúncio de guia de TV retrô (1992)."""
    bg = Image.new("RGB", (W, H), (25, 22, 30))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 140, 230, W - 140, 1120
    d.rectangle((x0, y0, x1, y1), fill=(250, 245, 230))
    d.rectangle((x0, y0, x1, y0 + 150), fill=(200, 30, 40))
    d.text((W / 2, y0 + 78), "TV GUIDE", font=font(FONT_CAPTION, 110), fill="white", anchor="mm")
    d.text((W / 2, y0 + 210), "APRIL 1992", font=font(FONT_UI_BOLD, 46), fill=(60, 60, 70), anchor="mm")
    d.line((x0 + 50, y0 + 260, x1 - 50, y0 + 260), fill=(60, 60, 70), width=3)
    d.text((W / 2, y0 + 350), "NEW SERIES!", font=font(FONT_CAPTION, 70), fill=(200, 30, 40), anchor="mm")
    d.text((W / 2, y0 + 460), "Barney & Friends", font=font(FONT_CAPTION, 92), fill=(140, 60, 200), anchor="mm")
    e = emoji("🦖", 200)
    bg.paste(e, (int(W / 2 - e.width / 2), y0 + 530), e)
    d.text((W / 2, y0 + 790), "A purple dinosaur who", font=font(FONT_UI, 40), fill=(60, 60, 70), anchor="mm")
    d.text((W / 2, y0 + 840), "\"definitely warned everyone.\"", font=font(FONT_UI_BOLD, 40), fill=(60, 60, 70), anchor="mm")
    return bg


BADGES = {
    "johnny": {"photo": "projects/007-johnny-bravo-vmas/images/01.jpg", "crop": [0.28, 0.15, 0.72],
               "event": "VMA 2009", "sub": "MTV VIDEO MUSIC AWARDS", "name": "JOHNNY BRAVO",
               "role": "HEAD OF SECURITY", "id": "SEC-0001", "date": "SEPT 13, 2009 · RADIO CITY"},
    "shrek": {"photo": "projects/011-shrek-fyre/images/01.jpg", "crop": [0.22, 0.06, 0.78],
              "event": "FYRE FESTIVAL", "sub": "GREAT EXUMA · BAHAMAS", "name": "SHREK",
              "role": "LUXURY VILLAS", "id": "OGRE-001", "date": "APRIL 2017 · VIP AREA",
              "access": ["VIP", "SWAMP"], "top": (230, 90, 20)},
    "bugs": {"photo": "projects/010-bugs-apollo13/images/01.jpg", "crop": [0.25, 0.08, 0.75],
             "event": "APOLLO 13", "sub": "NASA · MANNED SPACECRAFT CENTER", "name": "BUGS BUNNY",
             "role": "TANK INSPECTOR", "id": "O2-0002", "date": "APRIL 1970 · TANK No. 2",
             "access": ["TANK", "ACCESS"], "top": (20, 40, 110)},
    "scooby": {"photo": "projects/009-scooby-oscars/images/01.jpg", "crop": [0.12, 0.16, 0.50],
               "event": "OSCARS 2017", "sub": "ENVELOPE SECURITY · BACKSTAGE", "name": "SCOOBY-DOO",
               "role": "BRIEFCASE GUARD", "id": "SNACK-01", "date": "FEB 26, 2017 · LOS ANGELES",
               "access": ["ALL", "SNACKS"], "top": (90, 20, 20)},
    "patrick": {"photo": "projects/008-patrick-suez/images/03.jpg", "crop": [0.22, 0.45, 0.78],
                "event": "SUEZ CANAL", "sub": "SUEZ CANAL AUTHORITY · EGYPT", "name": "PATRICK STAR",
                "role": "OFFICIAL SHIP GUIDE", "id": "FLAG-0002", "date": "MARCH 2021 · KM 151",
                "access": ["FLAG", "DUTY"], "top": (10, 60, 110)},
}


def badge(name):
    """Credencial de segurança realista com a foto do personagem, cordão e plástico."""
    from .common import ROOT
    import random
    c = BADGES[name]
    bg = Image.new("RGB", (W, H), (18, 16, 24))
    d = ImageDraw.Draw(bg)
    for i in range(0, H, 4):
        d.line((0, i, W, i), fill=(22 + (i // 4) % 3, 20, 30))
    bw, bh = 700, 1080
    card = Image.new("RGBA", (bw + 60, bh + 60), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    ox, oy = 30, 30
    cd.rounded_rectangle((ox, oy, ox + bw, oy + bh), 34, fill=(250, 250, 252))
    # faixa do topo com degradê
    top = Image.new("RGB", (bw, 230))
    for y in range(230):
        t = y / 230
        r0, g0, b0 = c.get("top", (20, 10, 40))
        ImageDraw.Draw(top).line((0, y, bw, y), fill=(int(r0 + 10 * t), int(g0 + 5 * t), int(b0 + 30 * t)))
    m = Image.new("L", (bw, 230), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, bw, 290), 34, fill=255)
    card.paste(top, (ox, oy), m)
    cd.rounded_rectangle((ox + bw / 2 - 70, oy + 26, ox + bw / 2 + 70, oy + 56), 15, fill=(250, 250, 252))
    cd.text((ox + bw / 2, oy + 125), c["event"], font=font(FONT_CAPTION, 100), fill=(255, 214, 0), anchor="mm")
    cd.text((ox + bw / 2, oy + 195), c["sub"], font=font(FONT_UI_BOLD, 30), fill=(200, 200, 225), anchor="mm")
    # foto
    ph_path = ROOT / c["photo"]
    im = Image.open(ph_path).convert("RGB") if ph_path.exists() else Image.new("RGB", (800, 1400), (200, 200, 210))
    w, h = im.size
    x0f, y0f, x1f = c["crop"]
    side = int((x1f - x0f) * w)
    face = im.crop((int(x0f * w), int(y0f * h), int(x0f * w) + side, int(y0f * h) + int(side * 1.2)))
    pw, ph = 330, 396
    face = face.resize((pw, ph), Image.LANCZOS)
    back = Image.new("RGB", (pw, ph))
    for y in range(ph):
        ImageDraw.Draw(back).line((0, y, pw, y), fill=(int(120 + 60 * y / ph), int(170 + 40 * y / ph), 235))
    import numpy as np
    arr = np.asarray(face).astype(int)
    white = ((arr[..., 0] > 235) & (arr[..., 1] > 235) & (arr[..., 2] > 235)).astype("uint8") * 255
    face = Image.composite(back, face, Image.fromarray(white).convert("L"))
    px, py = ox + 50, oy + 280
    cd.rectangle((px - 6, py - 6, px + pw + 6, py + ph + 6), fill=(30, 30, 40))
    card.paste(face, (px, py))
    # dados ao lado da foto
    tx = px + pw + 40
    a1, a2 = c.get("access", ["ALL", "ACCESS"])
    cd.text((tx, py + 10), a1, font=font(FONT_CAPTION, 92), fill=(220, 30, 45), anchor="la")
    cd.text((tx, py + 105), a2, font=font(FONT_CAPTION, 70), fill=(220, 30, 45), anchor="la")
    cd.text((tx, py + 215), "ID", font=font(FONT_UI, 28), fill=(120, 120, 135), anchor="la")
    cd.text((tx, py + 248), c["id"], font=font(FONT_UI_BOLD, 38), fill=(30, 30, 40), anchor="la")
    # holograma
    for i in range(70):
        hue = [(255, 120, 200), (120, 220, 255), (255, 240, 120), (160, 255, 170)][i // 18 % 4]
        cd.line((tx + i * 3, py + 320, tx + i * 3 + 40, py + 390), fill=hue + (150,), width=3)
    cd.text((ox + bw / 2, py + ph + 85), c["name"], font=font(FONT_CAPTION, 84), fill=(20, 20, 28), anchor="mm")
    ry = py + ph + 145
    cd.rounded_rectangle((ox + 50, ry, ox + bw - 50, ry + 92), 18, fill=(215, 30, 45))
    cd.text((ox + bw / 2, ry + 46), c["role"], font=font(FONT_UI_BOLD, 52), fill="white", anchor="mm")
    cd.text((ox + bw / 2, ry + 130), c["date"], font=font(FONT_UI_BOLD, 28), fill=(110, 110, 125), anchor="mm")
    rnd = random.Random(7)
    bx, by = ox + 120, ry + 165
    x = bx
    while x < ox + bw - 120:
        wbar = rnd.choice([2, 3, 5, 7])
        cd.rectangle((x, by, x + wbar, by + 50), fill=(20, 20, 25))
        x += wbar + rnd.choice([3, 4, 6])
    # brilho do plástico
    gl = Image.new("RGBA", card.size, (0, 0, 0, 0))
    ImageDraw.Draw(gl).polygon([(ox + 80, oy), (ox + 330, oy), (ox + 80, oy + 520), (ox, oy + 520), (ox, oy + 160)],
                                fill=(255, 255, 255, 38))
    card = Image.alpha_composite(card, gl)
    card = card.rotate(-4, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    sh.putalpha(card.split()[3].point(lambda v: v * 0.55))
    from PIL import ImageFilter
    sh = sh.filter(ImageFilter.GaussianBlur(22))
    cx, cy = (W - card.width) // 2, 220
    # cordão
    d.polygon([(W / 2 - 150, 0), (W / 2 - 80, 0), (cx + card.width / 2 - 20, cy + 70), (cx + card.width / 2 - 60, cy + 70)],
              fill=(215, 30, 45))
    d.polygon([(W / 2 + 80, 0), (W / 2 + 150, 0), (cx + card.width / 2 + 40, cy + 70), (cx + card.width / 2, cy + 70)],
              fill=(190, 25, 38))
    bg.paste(sh, (cx + 18, cy + 30), sh)
    bg.paste(card, (cx, cy), card)
    d = ImageDraw.Draw(bg)
    d.rounded_rectangle((W / 2 - 22, cy + 10, W / 2 + 22, cy + 80), 10, fill=(170, 170, 180), outline=(90, 90, 100), width=3)
    return bg


QUOTES = {
    "taz": {"text": ["\"Blrrbl grrr", "wubba wubba", "rrraaah!\""], "who": "Taz · official statement · April 2017 · (translation below)"},
    "apollo": {"text": ["\"Okay, Houston,", "we've had", "a problem here.\""], "who": "Apollo 13 · April 13, 1970 · 55 hours into the mission"},
    "horowitz": {"text": ["\"Moonlight,", "you guys won.", "This is", "not a joke.\""], "who": "Jordan Horowitz · La La Land producer · Feb 26, 2017"},
    "patrick": {"text": ["\"I waved.", "It didn't", "wave back.\""], "who": "Patrick Star · official statement · March 2021"},
    "call": {"text": ["\"Hello, is this", "the ship guide?\""], "who": "Suez Canal Authority · phone call · March 23, 2021"},
    "kanye": {"text": ["\"Yo Taylor, I'm really", "happy for you,", "I'mma let you finish,", "but Beyoncé had one", "of the best videos", "of all time!\""],
              "who": "MTV Video Music Awards · Sept 13, 2009"},
}


def quote(name):
    """Cartão com uma frase real e famosa."""
    c = QUOTES[name]
    bg = Image.new("RGB", (W, H), (12, 12, 16))
    d = ImageDraw.Draw(bg)
    d.text((140, 430), "\u201c", font=font(FONT_CAPTION, 300), fill=(255, 214, 0), anchor="lm")
    y = 620
    for line in c["text"]:
        d.text((W / 2, y), line, font=font(FONT_CAPTION, 76), fill="white", anchor="mm")
        y += 105
    d.text((W / 2, y + 40), c["who"], font=font(FONT_UI, 34), fill=(150, 155, 170), anchor="mm")
    return bg


AWARDS = {
    "patrick": {"cat": "DOING NOTHING", "winner": "PATRICK STAR", "work": "Longer than anyone else",
                "event": "BIKINI BOTTOM AWARDS"},
    "beyonce": {"cat": "VIDEO OF THE YEAR", "winner": "BEYONCÉ", "work": "\"Single Ladies\"",
                "event": "MTV VIDEO MUSIC AWARDS 2009"},
    "taylor": {"cat": "BEST FEMALE VIDEO", "winner": "TAYLOR SWIFT", "work": "\"You Belong With Me\"",
               "event": "MTV VIDEO MUSIC AWARDS 2009"},
}


def award(name):
    """Cartão de vencedor da premiação (envelope dourado)."""
    c = AWARDS[name]
    bg = Image.new("RGB", (W, H), (12, 8, 20))
    d = ImageDraw.Draw(bg)
    for r in range(900, 0, -12):
        k = r / 900
        d.ellipse((W / 2 - r, 650 - r, W / 2 + r, 650 + r), fill=(int(12 + 70 * (1 - k)), int(8 + 50 * (1 - k)), int(20 + 20 * (1 - k))))
    x0, y0, x1, y1 = 110, 280, W - 110, 1020
    d.rounded_rectangle((x0 + 14, y0 + 18, x1 + 14, y1 + 18), 26, fill=(5, 3, 8))
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(212, 175, 55))
    d.rounded_rectangle((x0 + 26, y0 + 26, x1 - 26, y1 - 26), 18, fill=(250, 244, 225), outline=(170, 135, 40), width=5)
    d.text((W / 2, y0 + 110), "AND THE WINNER IS...", font=font(FONT_UI_BOLD, 44), fill=(150, 115, 30), anchor="mm")
    d.line((x0 + 120, y0 + 170, x1 - 120, y0 + 170), fill=(212, 175, 55), width=4)
    d.text((W / 2, y0 + 250), c["cat"], font=font(FONT_CAPTION, 64), fill=(40, 30, 20), anchor="mm")
    d.text((W / 2, y0 + 400), c["winner"], font=font(FONT_CAPTION, 112), fill=(200, 30, 60), anchor="mm")
    d.text((W / 2, y0 + 520), c["work"], font=font(FONT_UI_BOLD, 50), fill=(60, 50, 40), anchor="mm")
    d.text((W / 2, y0 + 640), c["event"], font=font(FONT_UI, 32), fill=(150, 115, 30), anchor="mm")
    for (sx, sy, sr) in [(180, 200, 14), (900, 170, 18), (960, 1080, 12), (140, 1100, 16), (540, 1150, 10)]:
        d.polygon([(sx, sy - sr * 2), (sx + sr / 2, sy - sr / 2), (sx + sr * 2, sy), (sx + sr / 2, sy + sr / 2),
                   (sx, sy + sr * 2), (sx - sr / 2, sy + sr / 2), (sx - sr * 2, sy), (sx - sr / 2, sy - sr / 2)], fill=(255, 225, 120))
    return bg


SONGS = {
    "innocent": {"title": "Innocent", "artist": "Taylor Swift", "album": "Speak Now · 2010",
                 "pos": "2:41", "len": "2:21", "colors": [(120, 40, 140), (230, 120, 170)]},
}


def song(name):
    """Tela de player de música tocando a faixa."""
    c = SONGS[name]
    a, b = c["colors"]
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        t = y / H
        d.line((0, y, W, y), fill=tuple(int(a[i] * (1 - t) * 0.6 + 10) for i in range(3)))
    cs = 720
    cx0, cy0 = (W - cs) // 2, 190
    d.rounded_rectangle((cx0 + 10, cy0 + 20, cx0 + cs + 10, cy0 + cs + 20), 30, fill=(10, 5, 15))
    art = Image.new("RGB", (cs, cs))
    ad = ImageDraw.Draw(art)
    for y in range(cs):
        t = y / cs
        ad.line((0, y, cs, y), fill=tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)))
    ad.text((cs / 2, cs / 2 - 40), c["title"].upper(), font=font(FONT_CAPTION, 120), fill=(255, 245, 250), anchor="mm")
    ad.text((cs / 2, cs / 2 + 70), c["artist"].upper(), font=font(FONT_UI_BOLD, 40), fill=(255, 230, 240), anchor="mm")
    m = Image.new("L", (cs, cs), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, cs, cs), 30, fill=255)
    bg.paste(art, (cx0, cy0), m)
    y = cy0 + cs + 70
    d.text((cx0, y), c["title"], font=font(FONT_UI_BOLD, 62), fill="white", anchor="la")
    d.text((cx0, y + 80), c["artist"] + " · " + c["album"], font=font(FONT_UI, 38), fill=(220, 210, 225), anchor="la")
    d.text((cx0 + cs, y + 20), "\u2665", font=font(FONT_UI_BOLD, 60), fill=(255, 80, 120), anchor="ra")
    by = y + 170
    d.rounded_rectangle((cx0, by, cx0 + cs, by + 10), 5, fill=(255, 255, 255, 80))
    d.rounded_rectangle((cx0, by, cx0 + int(cs * 0.53), by + 10), 5, fill="white")
    d.ellipse((cx0 + int(cs * 0.53) - 14, by - 9, cx0 + int(cs * 0.53) + 14, by + 19), fill="white")
    d.text((cx0, by + 30), c["pos"], font=font(FONT_UI, 30), fill=(210, 200, 215), anchor="la")
    d.text((cx0 + cs, by + 30), "-" + c["len"], font=font(FONT_UI, 30), fill=(210, 200, 215), anchor="ra")
    return bg


COUPONS = {
    "icecream": {"title": "FREE SCOOP", "sub": "Good for ONE scoop of ice cream", "small": "1 per customer · No cash value",
                 "exp": "EXPIRES 03/31/2021"},
    "icecream_expired": {"title": "FREE SCOOP", "sub": "Good for ONE scoop of ice cream", "small": "1 per customer · No cash value",
                         "exp": "EXPIRES 03/31/2021", "stamp": "EXPIRED"},
}


def coupon(name):
    """Cupom de papel recortável com sorvete desenhado."""
    c = COUPONS[name]
    bg = Image.new("RGB", (W, H), (255, 200, 225))
    d = ImageDraw.Draw(bg)
    for i in range(-H, W, 70):
        d.line((i, 0, i + H, H), fill=(255, 210, 232), width=24)
    x0, y0, x1, y1 = 100, 330, W - 100, 1090
    d.rounded_rectangle((x0 + 14, y0 + 18, x1 + 14, y1 + 18), 24, fill=(200, 120, 160))
    d.rounded_rectangle((x0, y0, x1, y1), 24, fill=(255, 251, 238))
    for x in range(x0 + 20, x1 - 20, 34):
        d.line((x, y0 + 22, x + 18, y0 + 22), fill=(230, 80, 130), width=5)
        d.line((x, y1 - 22, x + 18, y1 - 22), fill=(230, 80, 130), width=5)
    for y in range(y0 + 20, y1 - 20, 34):
        d.line((x0 + 22, y, x0 + 22, y + 18), fill=(230, 80, 130), width=5)
        d.line((x1 - 22, y, x1 - 22, y + 18), fill=(230, 80, 130), width=5)
    cx, cy = x0 + 190, y0 + 380
    d.polygon([(cx - 70, cy), (cx + 70, cy), (cx, cy + 230)], fill=(222, 170, 90), outline=(150, 100, 40))
    for k in range(-60, 70, 28):
        d.line((cx + k, cy, cx + k / 2, cy + 110), fill=(170, 120, 50), width=3)
    d.ellipse((cx - 95, cy - 150, cx + 95, cy + 30), fill=(255, 150, 190), outline=(210, 90, 140), width=4)
    d.ellipse((cx - 25, cy - 200, cx + 15, cy - 160), fill=(220, 30, 50))
    tx = x0 + 520
    d.text((tx, y0 + 230), c["title"], font=font(FONT_CAPTION, 104), fill=(230, 60, 120), anchor="mm")
    lines = ["Good for ONE scoop", "of ice cream"]
    for i, ln in enumerate(lines):
        d.text((tx, y0 + 340 + i * 56), ln, font=font(FONT_UI_BOLD, 42), fill=(60, 50, 60), anchor="mm")
    d.text((tx, y0 + 480), c["small"], font=font(FONT_UI, 30), fill=(130, 120, 130), anchor="mm")
    d.rounded_rectangle((tx - 230, y0 + 540, tx + 230, y0 + 620), 14, fill=(230, 60, 120))
    d.text((tx, y0 + 580), c["exp"], font=font(FONT_UI_BOLD, 38), fill="white", anchor="mm")
    if c.get("stamp"):
        st = Image.new("RGBA", (720, 200), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rounded_rectangle((8, 8, 712, 192), 20, outline=(210, 20, 40, 235), width=14)
        sd.text((360, 100), c["stamp"], font=font(FONT_CAPTION, 130), fill=(210, 20, 40, 235), anchor="mm")
        st = st.rotate(-14, resample=Image.BICUBIC, expand=True)
        bg.paste(st, (W // 2 - st.width // 2, (y0 + y1) // 2 - st.height // 2), st)
    return bg


SITES = {
    "stuck": {"url": "istheshipstillstuck.com", "q": "Is the ship still stuck?", "a": "YES.", "foot": "Day 4 · updated 2 minutes ago"},
}


def site(name):
    """Print de site meme de uma pergunta só, numa janela de navegador."""
    c = SITES[name]
    bg = Image.new("RGB", (W, H), (30, 32, 38))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 60, 260, W - 60, 1180
    d.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y1 + 14), 28, fill=(10, 10, 14))
    d.rounded_rectangle((x0, y0, x1, y1), 28, fill="white")
    d.rounded_rectangle((x0, y0, x1, y0 + 130), 28, fill=(225, 228, 234))
    d.rectangle((x0, y0 + 100, x1, y0 + 130), fill=(225, 228, 234))
    for i, col in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((x0 + 34 + i * 46, y0 + 30, x0 + 64 + i * 46, y0 + 60), fill=col)
    d.rounded_rectangle((x0 + 40, y0 + 76, x1 - 40, y0 + 120), 20, fill="white")
    d.text((x0 + 70, y0 + 98), "\U0001F512 " if False else c["url"], font=font(FONT_UI, 30), fill=(70, 70, 80), anchor="lm")
    d.text((W / 2, y0 + 300), c["q"], font=font(FONT_UI_BOLD, 56), fill=(30, 30, 36), anchor="mm")
    d.text((W / 2, y0 + 560), c["a"], font=font(FONT_CAPTION, 330), fill=(220, 30, 40), anchor="mm")
    d.text((W / 2, y1 - 70), c["foot"], font=font(FONT_UI, 30), fill=(140, 140, 150), anchor="mm")
    return bg


REPORTS = {
    "jobbugs": {"title": "JOB DESCRIPTION", "sub": "NASA · Manned Spacecraft Center · 1970",
                "rows": [("Position", "Tank inspector"), ("Duty", "Look inside tanks"), ("Must find", "Nothing"),
                         ("Lunch", "12:00 sharp"), ("Carrots", "Not allowed"), ("Hired", "Bugs Bunny")],
                "stamp": "HIRED"},
    "job": {"title": "JOB DESCRIPTION", "sub": "Suez Canal Authority · Position #0002",
            "rows": [("Position", "Official ship guide"), ("Duty 1", "Wave flag (left)"), ("Duty 2", "Wave flag (right)"),
                     ("Other duties", "None"), ("Hours", "When awake"), ("Hired", "Patrick Star")],
            "stamp": "HIRED"},
    "rules": {"title": "OFFICIAL RULES", "sub": "Under-A-Rock Championship 2021",
              "rows": [("Rule 1", "Get under a rock"), ("Rule 2", "Stay there"), ("Rule 3", "Last one out wins"),
                       ("Snacks", "Not allowed"), ("Time limit", "None"), ("Judge", "A fish")],
              "stamp": "OFFICIAL"},
    "vma": {"title": "INCIDENT REPORT", "sub": "MTV VMAs · Radio City · Sept 13, 2009",
            "rows": [("Incident", "Man on stage"), ("Hair", "Very tall, blonde"), ("Said", "\"Whoa, mama\""),
                     ("Called", "Head of Security"), ("Responded", "Johnny Bravo"), ("Suspect", "Johnny Bravo")],
            "stamp": "CASE CLOSED"},
}


def report(name, stage=1):
    """Relatório de ocorrência. stage=0 esconde as 2 últimas linhas e o carimbo (revela com a fala)."""
    c = dict(REPORTS[name])
    if stage == 0:
        c["rows"] = c["rows"][:-2]
        c["stamp"] = None
    bg = Image.new("RGB", (W, H), (30, 34, 44))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 90, 200, W - 90, 1300
    d.rounded_rectangle((x0 + 12, y0 + 16, x1 + 12, y1 + 16), 30, fill=(12, 14, 20))
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(150, 105, 60))
    d.rectangle((x0 + 40, y0 + 70, x1 - 40, y1 - 40), fill=(252, 251, 246))
    d.rounded_rectangle((W / 2 - 150, y0 - 20, W / 2 + 150, y0 + 80), 18, fill=(170, 172, 180), outline=(90, 90, 100), width=4)
    d.text((W / 2, y0 + 150), c["title"], font=font(FONT_CAPTION, 80), fill=(20, 20, 28), anchor="mm")
    d.text((W / 2, y0 + 220), c["sub"], font=font(FONT_UI, 32), fill=(110, 110, 120), anchor="mm")
    y = y0 + 300
    for k, v in c["rows"]:
        if k:
            d.line((x0 + 80, y - 18, x1 - 80, y - 18), fill=(220, 220, 225), width=2)
        d.text((x0 + 90, y), (k + ":") if k else "", font=font(FONT_UI_BOLD, 38), fill=(90, 90, 100), anchor="la")
        last = k == "Suspect"
        d.text((x0 + 370, y), v, font=font(FONT_UI_BOLD if last else FONT_UI, 44),
               fill=(200, 30, 45) if last else (25, 25, 35), anchor="la")
        y += 82
    if not c["stamp"]:
        return bg
    st = Image.new("RGBA", (560, 150), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((6, 6, 554, 144), 16, outline=(205, 30, 45, 230), width=10)
    sd.text((280, 75), c["stamp"], font=font(FONT_CAPTION, 76), fill=(205, 30, 45, 230), anchor="mm")
    st = st.rotate(12, resample=Image.BICUBIC, expand=True)
    bg.paste(st, (int(W / 2 - st.width / 2 + 40), y1 - 260), st)
    return bg


DEPARTURES = {
    "suez": {"title": "SUEZ CANAL · NORTHBOUND", "rows": [("EVER GIVEN", "STUCK"), ("OCEAN QUEEN", "WAITING"),
             ("CAPE HOPE", "WAITING"), ("BLUE WHALE II", "WAITING"), ("PACIFIC STAR", "WAITING"),
             ("SEA BISCUIT", "WAITING"), ("NORDIC ROSE", "WAITING")],
             "count_label": "SHIPS IN LINE", "count": 369, "days": "DAY 6"},
}


def departures(name, val=None):
    """Painel de chegadas estilo aeroporto (letras amarelas em placas pretas)."""
    c = DEPARTURES[name]
    bg = Image.new("RGB", (W, H), (40, 44, 52))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 50, 200, W - 50, 1240
    d.rounded_rectangle((x0, y0, x1, y1), 18, fill=(18, 18, 20), outline=(90, 90, 96), width=6)
    d.rectangle((x0 + 6, y0 + 6, x1 - 6, y0 + 110), fill=(250, 200, 30))
    d.text((W / 2, y0 + 58), c["title"], font=font(FONT_UI_BOLD, 50), fill=(20, 20, 20), anchor="mm")
    d.text((x0 + 50, y0 + 150), "SHIP", font=font(FONT_UI_BOLD, 30), fill=(150, 150, 150), anchor="lm")
    d.text((x1 - 50, y0 + 150), "STATUS", font=font(FONT_UI_BOLD, 30), fill=(150, 150, 150), anchor="rm")
    y = y0 + 200
    f = font(FONT_UI_BOLD, 44)
    for ship, st in c["rows"]:
        cx = x0 + 40
        for ch in ship:
            d.rounded_rectangle((cx, y, cx + 38, y + 60), 5, fill=(34, 34, 38))
            d.line((cx, y + 30, cx + 38, y + 30), fill=(10, 10, 12), width=2)
            d.text((cx + 19, y + 31), ch, font=f, fill=(255, 214, 60), anchor="mm")
            cx += 42
        col = (255, 60, 60) if st == "STUCK" else (255, 214, 60)
        d.text((x1 - 50, y + 31), st, font=font(FONT_UI_BOLD, 40), fill=col, anchor="rm")
        y += 78
    d.line((x0 + 30, y + 10, x1 - 30, y + 10), fill=(70, 70, 76), width=3)
    v = str(c["count"] if val is None else val)
    d.text((x0 + 50, y + 85), c["count_label"], font=font(FONT_UI_BOLD, 44), fill=(200, 200, 200), anchor="lm")
    d.text((x1 - 50, y + 85), v, font=font(FONT_CAPTION, 110), fill=(255, 70, 60), anchor="rm")
    d.text((W / 2, y1 - 40), c["days"], font=font(FONT_UI_BOLD, 34), fill=(150, 150, 150), anchor="mm")
    return bg


SIGNS = {
    "rock": {"lines": ["UNDER-A-ROCK", "CHAMPIONSHIP"], "sub": ["DAY 1  ·  48 COMPETITORS", "NO SNACKS. NO PEEKING."]},
}


def woodsign(name):
    """Placa de madeira pintada à mão, pendurada por cordas."""
    import random
    c = SIGNS[name]
    bg = Image.new("RGB", (W, H), (20, 60, 80))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 90, 420, W - 90, 1120
    d.line((x0 + 120, 0, x0 + 150, y0 + 20), fill=(190, 160, 110), width=12)
    d.line((x1 - 120, 0, x1 - 150, y0 + 20), fill=(190, 160, 110), width=12)
    rnd = random.Random(3)
    for k, (a, b) in enumerate([(y0, y0 + 230), (y0 + 236, y0 + 466), (y0 + 472, y1)]):
        base = (150 + rnd.randint(-10, 10), 98 + rnd.randint(-8, 8), 52)
        d.rounded_rectangle((x0, a, x1, b), 14, fill=base, outline=(90, 55, 25), width=6)
        for g in range(6):
            gy = rnd.randint(a + 20, b - 20)
            d.line((x0 + 20, gy, x1 - 20, gy + rnd.randint(-6, 6)), fill=(125, 80, 40), width=3)
        for nx in (x0 + 30, x1 - 30):
            d.ellipse((nx - 9, (a + b) / 2 - 9, nx + 9, (a + b) / 2 + 9), fill=(80, 80, 85))
    d.text((W / 2, y0 + 120), c["lines"][0], font=font(FONT_CAPTION, 112), fill=(255, 245, 225), anchor="mm",
           stroke_width=8, stroke_fill=(70, 35, 15))
    d.text((W / 2, y0 + 350), c["lines"][1], font=font(FONT_CAPTION, 112), fill=(255, 215, 80), anchor="mm",
           stroke_width=8, stroke_fill=(70, 35, 15))
    for i, ln in enumerate(c["sub"]):
        d.text((W / 2, y0 + 545 + i * 62), ln, font=font(FONT_UI_BOLD, 42), fill=(255, 245, 225), anchor="mm")
    d.ellipse((x1 - 190, y0 - 60, x1 - 40, y0 + 40), fill=(120, 110, 100), outline=(70, 60, 55), width=6)
    return bg


PODIUMS = {
    "rock": {"title": "FINAL RESULTS", "sub": "Time spent under a rock",
             "places": [("PATRICK", "6 DAYS"), ("A CLAM", "2 DAYS"), ("A SNAIL", "1 DAY")]},
}


def podium(name):
    """Pódio com 1º, 2º e 3º lugar e medalhas."""
    c = PODIUMS[name]
    bg = Image.new("RGB", (W, H), (16, 24, 48))
    d = ImageDraw.Draw(bg)
    d.text((W / 2, 300), c["title"], font=font(FONT_CAPTION, 110), fill=(255, 214, 0), anchor="mm",
           stroke_width=8, stroke_fill="black")
    d.text((W / 2, 400), c["sub"], font=font(FONT_UI_BOLD, 44), fill="white", anchor="mm")
    base = 1180
    spec = [(1, W / 2, 470, (245, 196, 40)), (2, W / 2 - 320, 330, (200, 205, 215)), (3, W / 2 + 320, 230, (205, 130, 70))]
    for rank, cx, hgt, col in spec:
        who, val = c["places"][rank - 1]
        top = base - hgt
        d.rectangle((cx - 150, top, cx + 150, base), fill=col, outline=(0, 0, 0), width=6)
        d.text((cx, top + 90), str(rank), font=font(FONT_CAPTION, 150), fill="white", anchor="mm",
               stroke_width=8, stroke_fill=(0, 0, 0))
        d.ellipse((cx - 55, top - 250, cx + 55, top - 140), fill=col, outline=(0, 0, 0), width=5)
        d.text((cx, top - 195), str(rank), font=font(FONT_CAPTION, 70), fill="white", anchor="mm")
        d.text((cx, top - 95), who, font=font(FONT_CAPTION, 56 if rank == 1 else 46), fill="white", anchor="mm",
               stroke_width=5, stroke_fill="black")
        d.text((cx, top - 40), val, font=font(FONT_UI_BOLD, 40 if rank == 1 else 34), fill=(255, 230, 120), anchor="mm")
    return bg


CALLS = {
    "houston": {"caller": "Houston Mission Control", "sub": "NASA · Texas", "note": "We've had a problem."},
    "suez": {"caller": "Suez Canal Authority", "sub": "Egypt · mobile", "note": "Is this the ship guide?"},
}


def call(name):
    """Celular recebendo uma ligação (tela de chamada)."""
    c = CALLS[name]
    bg = Image.new("RGB", (W, H), (25, 25, 30))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 230, 130, W - 230, 1250
    d.rounded_rectangle((x0 - 18, y0 - 18, x1 + 18, y1 + 18), 90, fill=(15, 15, 18), outline=(120, 120, 128), width=6)
    scr = Image.new("RGB", (x1 - x0, y1 - y0))
    sd = ImageDraw.Draw(scr)
    for y in range(scr.height):
        t = y / scr.height
        sd.line((0, y, scr.width, y), fill=(int(20 + 40 * t), int(60 + 50 * t), int(90 + 40 * t)))
    m = Image.new("L", scr.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, scr.width, scr.height), 74, fill=255)
    bg.paste(scr, (x0, y0), m)
    d = ImageDraw.Draw(bg)
    cx = W / 2
    d.rounded_rectangle((cx - 90, y0 + 22, cx + 90, y0 + 58), 18, fill=(0, 0, 0))
    d.text((cx, y0 + 150), "incoming call", font=font(FONT_UI, 34), fill=(210, 225, 235), anchor="mm")
    d.ellipse((cx - 110, y0 + 220, cx + 110, y0 + 440), fill=(230, 160, 40))
    d.polygon([(cx - 60, y0 + 380), (cx + 60, y0 + 380), (cx, y0 + 270)], fill=(255, 245, 220))
    d.text((cx, y0 + 520), c["caller"], font=font(FONT_UI_BOLD, 46), fill="white", anchor="mm")
    d.text((cx, y0 + 575), c["sub"], font=font(FONT_UI, 32), fill=(190, 205, 215), anchor="mm")
    d.rounded_rectangle((x0 + 40, y0 + 650, x1 - 40, y0 + 790), 26, fill=(255, 255, 255))
    d.text((x0 + 70, y0 + 690), "Message", font=font(FONT_UI_BOLD, 26), fill=(120, 120, 130), anchor="lm")
    d.text((x0 + 70, y0 + 745), c["note"], font=font(FONT_UI_BOLD, 34), fill=(25, 25, 30), anchor="lm")
    for bx, col, lab in [(cx - 170, (235, 60, 60), "Decline"), (cx + 170, (50, 200, 90), "Accept")]:
        d.ellipse((bx - 70, y1 - 260, bx + 70, y1 - 120), fill=col)
        d.text((bx, y1 - 80), lab, font=font(FONT_UI, 30), fill="white", anchor="mm")
    for k in range(3):   # tremida de vibração
        r = 40 + k * 26
        d.arc((x0 - 120 - r, (y0 + y1) / 2 - r, x0 - 120 + r, (y0 + y1) / 2 + r), 140, 220, fill=(200, 200, 210), width=6)
        d.arc((x1 + 120 - r, (y0 + y1) / 2 - r, x1 + 120 + r, (y0 + y1) / 2 + r), -40, 40, fill=(200, 200, 210), width=6)
    return bg


BETS = {
    "rock": {"book": "BIKINI BOTTOM SPORTSBOOK", "event": "Under-A-Rock Championship 2021",
             "rows": [("Patrick Star", "1.01"), ("A Clam", "50.00"), ("A Snail", "99.00")],
             "note": "99% of all bets placed on Patrick", "stamp": "FAVORITE"},
}


def bet(name):
    """Bilhete de aposta de papel térmico com odds e carimbo."""
    c = BETS[name]
    bg = Image.new("RGB", (W, H), (35, 40, 50))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 170, 220, W - 170, 1180
    zig = [(x0, y0)]
    for i, x in enumerate(range(x0, x1 + 1, 30)):
        zig.append((x, y0 + (0 if i % 2 else 16)))
    pts = zig + [(x1, y1)] + [(x, y1 - (0 if i % 2 else 16)) for i, x in enumerate(range(x1, x0 - 1, -30))]
    d.polygon(pts, fill=(250, 248, 240))
    mono = font(FONT_UI_BOLD, 36)
    d.text((W / 2, y0 + 90), c["book"], font=font(FONT_UI_BOLD, 40), fill=(20, 20, 20), anchor="mm")
    d.text((W / 2, y0 + 150), c["event"], font=font(FONT_UI, 32), fill=(80, 80, 80), anchor="mm")
    for xx in range(x0 + 40, x1 - 40, 22):
        d.line((xx, y0 + 200, xx + 10, y0 + 200), fill=(120, 120, 120), width=3)
    y = y0 + 270
    d.text((x0 + 60, y), "PICK", font=font(FONT_UI, 28), fill=(110, 110, 110), anchor="lm")
    d.text((x1 - 60, y), "ODDS", font=font(FONT_UI, 28), fill=(110, 110, 110), anchor="rm")
    y += 70
    for i, (who, odd) in enumerate(c["rows"]):
        if i == 0:
            d.rectangle((x0 + 40, y - 34, x1 - 40, y + 34), fill=(255, 230, 120))
        d.text((x0 + 60, y), who, font=mono, fill=(20, 20, 20), anchor="lm")
        d.text((x1 - 60, y), odd, font=mono, fill=(20, 20, 20), anchor="rm")
        y += 85
    for xx in range(x0 + 40, x1 - 40, 22):
        d.line((xx, y, xx + 10, y), fill=(120, 120, 120), width=3)
    d.text((W / 2, y + 70), c["note"], font=font(FONT_UI_BOLD, 32), fill=(20, 20, 20), anchor="mm")
    import random
    rnd = random.Random(5)
    bx = x0 + 110
    while bx < x1 - 110:
        wv = rnd.choice([3, 4, 6, 8])
        d.rectangle((bx, y1 - 170, bx + wv, y1 - 90), fill=(20, 20, 20))
        bx += wv + rnd.choice([3, 5, 7])
    st = Image.new("RGBA", (520, 150), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((6, 6, 514, 144), 16, outline=(30, 120, 60, 230), width=10)
    sd.text((260, 75), c["stamp"], font=font(FONT_CAPTION, 80), fill=(30, 120, 60, 230), anchor="mm")
    st = st.rotate(14, resample=Image.BICUBIC, expand=True)
    bg.paste(st, (x1 - st.width + 40, y1 - 250), st)
    return bg


ENVELOPES = {
    "actress": {"cat": "Actress in a", "cat2": "Leading Role", "name": "Emma Stone", "film": "\"La La Land\""},
}


def envelope(name):
    """Envelope vermelho de premiação aberto, com o cartão do vencedor e mancha de mostarda."""
    c = ENVELOPES[name]
    bg = Image.new("RGB", (W, H), (25, 20, 22))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 120, 520, W - 120, 1220
    d.rounded_rectangle((x0, y0, x1, y1), 16, fill=(170, 20, 35), outline=(120, 10, 20), width=6)
    d.polygon([(x0, y0 + 8), (W / 2, y0 + 300), (x1, y0 + 8)], fill=(150, 15, 30), outline=(110, 10, 20))
    cx0, cy0, cx1, cy1 = x0 + 70, 170, x1 - 70, y0 + 330
    d.rounded_rectangle((cx0 + 10, cy0 + 14, cx1 + 10, cy1 + 14), 10, fill=(10, 8, 8))
    d.rounded_rectangle((cx0, cy0, cx1, cy1), 10, fill=(250, 246, 236))
    d.rectangle((cx0 + 24, cy0 + 24, cx1 - 24, cy1 - 24), outline=(200, 160, 60), width=4)
    d.text((W / 2, cy0 + 120), c["cat"], font=font(FONT_UI_BOLD, 50), fill=(60, 50, 40), anchor="mm")
    d.text((W / 2, cy0 + 185), c["cat2"], font=font(FONT_UI_BOLD, 50), fill=(60, 50, 40), anchor="mm")
    d.line((W / 2 - 160, cy0 + 245, W / 2 + 160, cy0 + 245), fill=(200, 160, 60), width=4)
    d.text((W / 2, cy0 + 345), c["name"], font=font(FONT_CAPTION, 104), fill=(30, 25, 25), anchor="mm")
    d.text((W / 2, cy0 + 450), c["film"], font=font(FONT_UI_BOLD, 56), fill=(170, 20, 35), anchor="mm")
    import random
    rnd = random.Random(9)
    stain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stain)
    mx, my = cx1 - 170, cy1 - 120
    for _ in range(14):
        r = rnd.randint(18, 52)
        ox, oy = rnd.randint(-70, 70), rnd.randint(-40, 40)
        sd.ellipse((mx + ox - r, my + oy - r, mx + ox + r, my + oy + r), fill=(225, 175, 20, 170))
    stain = stain.filter(ImageFilter.GaussianBlur(3))
    bg.paste(stain, (0, 0), stain)
    return bg


THERMOS = {
    "lox": {"value": "-297°F", "label": "OXYGEN TANK No. 2", "sub": "Cryogenic oxygen", "level": 0.06},
}


def thermo(name):
    """Termômetro gigante de laboratório, congelado, marcando a temperatura."""
    c = THERMOS[name]
    bg = Image.new("RGB", (W, H), (14, 30, 48))
    d = ImageDraw.Draw(bg)
    cx, top, bot = W / 2 - 170, 230, 1150
    d.rounded_rectangle((cx - 70, top, cx + 70, bot), 70, fill=(235, 245, 255), outline=(150, 190, 220), width=8)
    d.ellipse((cx - 120, bot - 130, cx + 120, bot + 110), fill=(60, 140, 230), outline=(150, 190, 220), width=8)
    lv = bot - 40 - (bot - top - 120) * c["level"]
    d.rectangle((cx - 32, lv, cx + 32, bot), fill=(60, 140, 230))
    for k in range(11):
        y = top + 60 + k * (bot - top - 160) / 10
        d.line((cx + 70, y, cx + 120, y), fill=(200, 220, 240), width=5)
    import random
    rnd = random.Random(4)
    for _ in range(60):   # gelo
        x, y, r = rnd.randint(int(cx - 140), int(cx + 140)), rnd.randint(top, bot + 80), rnd.randint(4, 14)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(220, 240, 255))
    tx = W / 2 + 190
    d.text((tx, 560), c["value"], font=font(FONT_CAPTION, 150), fill=(120, 200, 255), anchor="mm", stroke_width=8, stroke_fill=(10, 20, 40))
    d.text((tx, 700), c["label"], font=font(FONT_UI_BOLD, 40), fill="white", anchor="mm")
    d.text((tx, 760), c["sub"], font=font(FONT_UI, 30), fill=(170, 200, 230), anchor="mm")
    return bg


TICKETS = {
    "fyre": {"title": "FYRE FESTIVAL", "sub": "Great Exuma · Bahamas · 2017", "tier": "LUXURY VILLA PACKAGE",
             "price": "$12,000", "perks": ["Private island", "Gourmet meals", "Luxury villa"]},
}


def ticket(name):
    """Pulseira/ingresso VIP de festival."""
    c = TICKETS[name]
    bg = Image.new("RGB", (W, H), (20, 40, 60))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 110, 330, W - 110, 1130
    d.rounded_rectangle((x0 + 14, y0 + 18, x1 + 14, y1 + 18), 34, fill=(8, 14, 22))
    grad = Image.new("RGB", (x1 - x0, y1 - y0))
    gd = ImageDraw.Draw(grad)
    for y in range(y1 - y0):
        t = y / (y1 - y0)
        gd.line((0, y, x1 - x0, y), fill=(int(255 - 40 * t), int(120 + 60 * t), int(40 + 120 * t)))
    m = Image.new("L", grad.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, grad.width, grad.height), 34, fill=255)
    bg.paste(grad, (x0, y0), m)
    d = ImageDraw.Draw(bg)
    d.text((W / 2, y0 + 110), c["title"], font=font(FONT_CAPTION, 110), fill="white", anchor="mm", stroke_width=6, stroke_fill=(120, 40, 10))
    d.text((W / 2, y0 + 195), c["sub"], font=font(FONT_UI_BOLD, 36), fill=(255, 245, 230), anchor="mm")
    d.line((x0 + 50, y0 + 260, x1 - 50, y0 + 260), fill=(255, 255, 255), width=4)
    d.text((W / 2, y0 + 330), c["tier"], font=font(FONT_UI_BOLD, 44), fill="white", anchor="mm")
    d.text((W / 2, y0 + 460), c["price"], font=font(FONT_CAPTION, 170), fill=(255, 240, 120), anchor="mm", stroke_width=8, stroke_fill=(90, 30, 10))
    for i, p in enumerate(c["perks"]):
        d.text((W / 2, y0 + 600 + i * 56), "\u2713  " + p, font=font(FONT_UI_BOLD, 40), fill="white", anchor="mm")
    for x in range(x0 + 30, x1 - 30, 36):
        d.ellipse((x, y0 + 252, x + 14, y0 + 266), fill=(20, 40, 60))
    return bg


NAMETAGS = {
    "taz": {"name": "TAZ", "role": "Luxury Villas Manager", "note": "do not feed", "color": (230, 40, 40)},
}


def nametag(name):
    """Adesivo de crachá "HELLO my name is" escrito à mão com canetão."""
    import random
    c = NAMETAGS[name]
    bg = Image.new("RGB", (W, H), (30, 30, 34))
    st = Image.new("RGBA", (900, 640), (0, 0, 0, 0))
    d = ImageDraw.Draw(st)
    d.rounded_rectangle((0, 0, 899, 639), 46, fill=c["color"] + (255,))
    d.text((450, 95), "HELLO", font=font(FONT_CAPTION, 120), fill="white", anchor="mm")
    d.text((450, 175), "my name is", font=font(FONT_UI_BOLD, 46), fill="white", anchor="mm")
    d.rectangle((26, 230, 873, 570), fill=(255, 255, 255, 255))
    marker = font(FONT_CAPTION, 150)
    d.text((450, 345), c["name"], font=marker, fill=(25, 25, 35), anchor="mm")
    d.text((450, 460), c["role"], font=font(FONT_UI_BOLD, 42), fill=(25, 25, 35), anchor="mm")
    d.text((450, 525), "(" + c["note"] + ")", font=font(FONT_UI, 34), fill=(90, 90, 100), anchor="mm")
    rnd = random.Random(2)
    for cx, cy in ((800, 270), (90, 545)):   # duas marcas de dedo de lama
        for _ in range(6):
            x, y, r = cx + rnd.randint(-22, 22), cy + rnd.randint(-16, 16), rnd.randint(14, 26)
            d.ellipse((x - r, y - r, x + r, y + r), fill=(95, 120, 50, 90))
    st = st.rotate(-6, resample=Image.BICUBIC, expand=True)
    bg.paste(st, ((W - st.width) // 2, 330), st)
    return bg


BOARDS = {
    "armwrestle": {"title": "ARM WRESTLING", "sub": "Backstage · Radio City Music Hall",
                   "left": "JOHNNY", "right": "ROCKETTES", "l": "0", "r": "35"},
    "onions": {"title": "ONION PEELING", "sub": "Catering tent · Fyre Festival · 2017",
               "left": "SHREK", "right": "DONKEY", "l": "2", "r": "100"},
    "carrots": {"title": "JUDGE'S SCORE", "sub": "Carrot Cake Bake-Off · NASA cafeteria · 1968",
                "left": "WABBIT", "right": "EVERYONE ELSE", "l": "0", "r": "10"},
    "hotdogs": {"title": "HOT DOG CHALLENGE", "sub": "Backstage catering · Oscars 2017",
                "left": "SCOOBY & SHAGGY", "right": "WAITER", "l": "84", "r": "85"},
    "rock": {"title": "UNDER-A-ROCK", "sub": "Championship 2021 · Bottom of the Suez Canal",
             "left": "DAY", "right": "PLAYERS", "l": "1", "r": "48"},
    "rockfinal": {"title": "TIME UNDER A ROCK", "sub": "Final results · Under-A-Rock Championship 2021",
                  "left": "PATRICK", "right": "2ND PLACE", "l": "6d", "r": "2d"},
    "suez": {"title": "SUEZ CANAL", "sub": "Traffic report · March 2021",
             "left": "DAYS", "right": "SHIPS", "l": "6", "r": "369"},
    "armwrestle_win": {"title": "FINAL SCORE", "sub": "Backstage · Radio City Music Hall",
                       "left": "JOHNNY", "right": "ROCKETTES", "l": "1", "r": "35"},
}


def board(name, r_val=None):
    """Placar esportivo. r_val anima o placar da direita (anim: count)."""
    c = dict(BOARDS[name])
    if r_val is not None:
        c["r"] = str(r_val)
    bg = Image.new("RGB", (W, H), (10, 10, 14))
    d = ImageDraw.Draw(bg)
    x0, y0, x1, y1 = 90, 300, W - 90, 1100
    d.rounded_rectangle((x0, y0, x1, y1), 30, fill=(25, 25, 32), outline=(255, 214, 0), width=8)
    d.text((W / 2, y0 + 90), c["title"], font=font(FONT_CAPTION, 84), fill=(255, 214, 0), anchor="mm")
    d.text((W / 2, y0 + 170), c["sub"], font=font(FONT_UI, 34), fill=(170, 175, 190), anchor="mm")
    for i, (lab, val, col) in enumerate([(c["left"], c["l"], (90, 170, 255)), (c["right"], c["r"], (255, 70, 70))]):
        cx = W / 2 + (-1 if i == 0 else 1) * 225
        d.text((cx, y0 + 290), lab, font=font(FONT_CAPTION, 60 if len(lab) <= 10 else 38), fill=col, anchor="mm")
        d.rounded_rectangle((cx - 170, y0 + 350, cx + 170, y0 + 640), 20, fill=(0, 0, 0))
        d.text((cx, y0 + 495), val, font=font(FONT_CAPTION, 230 if len(val) <= 2 else 160), fill=(255, 120, 40), anchor="mm")
    d.text((W / 2, y0 + 495), ":", font=font(FONT_CAPTION, 160), fill="white", anchor="mm")
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
    if kind == "badge":
        return badge(rest)
    if kind == "report":
        return report(rest)
    if kind == "nametag":
        return nametag(rest)
    if kind == "ticket":
        return ticket(rest)
    if kind == "thermo":
        return thermo(rest)
    if kind == "envelope":
        return envelope(rest)
    if kind == "call":
        return call(rest)
    if kind == "bet":
        return bet(rest)
    if kind == "departures":
        return departures(rest)
    if kind == "sign":
        return woodsign(rest)
    if kind == "podium":
        return podium(rest)
    if kind == "site":
        return site(rest)
    if kind == "coupon":
        return coupon(rest)
    if kind == "award":
        return award(rest)
    if kind == "song":
        return song(rest)
    if kind == "quote":
        return quote(rest)
    if kind == "board":
        return board(rest)
    if kind == "tv":
        return tvguide(rest)
    if kind == "stone":
        return stone(rest)
    if kind == "timeline":
        return timeline(rest)
    if kind == "map":
        return old_map(rest)
    if kind == "doc":
        return parchment(rest)
    if kind == "stat":
        return stat(rest)
    if kind == "tip":
        return tipscreen(rest)
    if kind == "receipt":
        return receipt(rest)
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
