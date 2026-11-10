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
    sc = min(1.2, 980 / DH, 1000 / DW)          # o maior possível acima da legenda
    dev = dev.resize((int(DW * sc), int(DH * sc)), Image.LANCZOS)
    DW, DH = dev.size
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ox, oy = (W - DW) // 2, max(140, (1150 - DH) // 2 + 40)
    ImageDraw.Draw(sh).rounded_rectangle((ox + 30, oy + 50, ox + DW + 30, oy + DH + 50), 70, fill=(0, 0, 0, 170))
    sh = sh.filter(ImageFilter.GaussianBlur(30))
    base.paste(sh, (0, 0), sh)
    base.paste(dev, (ox, oy), dev)
    if c.get("label"):
        ImageDraw.Draw(base).text((W / 2, oy - 2), c["label"], font=font(FONT_CAPTION, 70), fill=c["label_color"],
                                  anchor="mb", stroke_width=6, stroke_fill="black")
    return base


RECEIPTS = {
    "spongebob": [("KRUSTY KRAB", "big"), ("EMPLOYEE TIP REPORT", "bold"), ("", ""),
                  ("Employee:", "SpongeBob S."), ("Years worked:", "25"), ("Shifts:", "9,125"),
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
    "pew72": {"num": "72%", "text": ["of Americans say tipping", "is expected in more places", "than 5 years ago"],
              "src": "Source: Pew Research Center, 2023"},
}


def stat(name):
    """Cartão de estatística com a fonte (o fato verdadeiro do vídeo)."""
    c = STATS[name]
    bg = Image.new("RGB", (W, H), (14, 18, 30))
    d = ImageDraw.Draw(bg)
    d.text((W / 2, 520), c["num"], font=font(FONT_CAPTION, 380), fill=(255, 214, 0), anchor="mm",
           stroke_width=10, stroke_fill="black")
    y = 800
    for line in c["text"]:
        d.text((W / 2, y), line, font=font(FONT_UI_BOLD, 60), fill="white", anchor="mm")
        y += 80
    d.text((W / 2, y + 40), c["src"], font=font(FONT_UI, 36), fill=(150, 160, 180), anchor="mm")
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
