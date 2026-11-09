"""Transições curtas entre shots, copiadas dos vídeos de referência.

Cada transição dura cerca de 0,27 s e fica centrada no ponto de troca.
  whip   chicote lateral: A sai pela esquerda, B entra pela direita, desfoque de movimento
  zoom   zoom através: A amplia com desfoque, B nasce ampliada e assenta
  punch  corte seco, mas B entra grande e encolhe até o normal
  fade   passa pelo escuro
  cut    corte seco
"""
import math

import numpy as np
from PIL import Image

DUR = {"whip": 0.27, "zoom": 0.30, "punch": 0.22, "fade": 0.36, "cut": 0.0}

# alternância automática quando o shot não define "tr"
CYCLE = ["whip", "punch", "zoom", "whip", "cut", "punch", "fade", "zoom", "whip", "punch", "cut"]


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def motion_blur_h(img, strength):
    """Desfoque horizontal: média de cópias deslocadas."""
    n = int(strength)
    if n < 2:
        return img
    a = np.asarray(img, dtype=np.float32)
    acc = np.zeros_like(a)
    steps = 7
    for i in range(steps):
        off = int((i / (steps - 1) - 0.5) * n)
        acc += np.roll(a, off, axis=1)
    return Image.fromarray((acc / steps).astype(np.uint8))


def zoom_blur(img, z, strength):
    """Zoom centrado com desfoque radial aproximado (média de escalas)."""
    w, h = img.size
    copies = 4 if strength > 0.02 else 1
    acc = None
    for i in range(copies):
        zz = z * (1 + strength * i / max(1, copies - 1))
        cw, ch = w / zz, h / zz
        box = ((w - cw) / 2, (h - ch) / 2, (w + cw) / 2, (h + ch) / 2)
        fr = np.asarray(img.resize((w, h), Image.BILINEAR, box=box), dtype=np.float32)
        acc = fr if acc is None else acc + fr
    return Image.fromarray((acc / copies).astype(np.uint8))


def blend(kind, a, b, q, size):
    """a, b: frames (PIL) do shot que sai e do que entra. q: 0..1 dentro da transição."""
    w, h = size
    if kind == "whip":
        e = ease(q)
        off = int(e * w)
        canvas = Image.new("RGB", size)
        canvas.paste(a, (-off, 0))
        canvas.paste(b, (w - off, 0))
        return motion_blur_h(canvas, 0.22 * w * math.sin(math.pi * q))
    if kind == "zoom":
        if q < 0.5:
            k = ease(q * 2)
            return zoom_blur(a, 1 + 0.9 * k, 0.25 * k)
        k = 1 - ease((q - 0.5) * 2)
        return zoom_blur(b, 1 + 0.6 * k, 0.2 * k)
    if kind == "punch":
        k = 1 - ease(q)
        return zoom_blur(b, 1 + 0.35 * k, 0.12 * k)
    if kind == "fade":
        if q < 0.5:
            return Image.blend(a, Image.new("RGB", size), ease(q * 2))
        return Image.blend(Image.new("RGB", size), b, ease((q - 0.5) * 2))
    return b if q >= 0.5 else a


def window(kind, t_cut):
    """Intervalo [início, fim] da transição em segundos."""
    d = DUR.get(kind, 0)
    if kind == "punch":       # só depois do corte
        return t_cut, t_cut + d
    return t_cut - d / 2, t_cut + d / 2
