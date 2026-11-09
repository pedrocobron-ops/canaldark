"""Monta um short vertical a partir de projects/<nome>/script.json.

Uso:
    python -m editor.make projects/001-squidward-imessage
    python -m editor.make projects/001-squidward-imessage --preview   # 540x960, rápido

Saída: projects/<nome>/out/video.mp4 (+ narration.wav, timeline.json, thumb.jpg)
"""
import argparse
import json
import math
import random
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from . import assets
from .common import COLORS, FONT_CAPTION, FONT_UI_BOLD, FPS, H, ROOT, W

TOKEN = re.compile(r"\{(\w):([^}]*)\}")
GAP = 0.18          # silêncio entre frases
LEAD = 0.15         # silêncio no começo


# ---------------------------------------------------------------- texto
def parse_chunk(chunk):
    """'on the new {b:iMessage 2}?' -> [('ON THE NEW ', None), ('IMESSAGE 2', 'b'), ('?', None)]"""
    out, pos = [], 0
    for m in TOKEN.finditer(chunk):
        if m.start() > pos:
            out.append((chunk[pos:m.start()], None))
        out.append((m.group(2), m.group(1)))
        pos = m.end()
    if pos < len(chunk):
        out.append((chunk[pos:], None))
    return [(t.upper(), c) for t, c in out if t]


def plain(s):
    return TOKEN.sub(r"\2", s).replace("|", " ")


def chunks_of(beat):
    return [c.strip() for c in beat["say"].split("|") if c.strip()]


# ---------------------------------------------------------------- voz
def synth(script, out_dir):
    import soundfile as sf
    from kokoro_onnx import Kokoro

    from .common import KOKORO_MODEL, KOKORO_VOICES

    k = Kokoro(str(KOKORO_MODEL), str(KOKORO_VOICES))
    sr = 24000
    voice, speed = script.get("voice", "am_onyx"), script.get("speed", 1.0)
    audio = [np.zeros(int(LEAD * sr), dtype=np.float32)]
    t = LEAD
    timeline = []
    for bi, beat in enumerate(script["beats"]):
        text = re.sub(r"\s+", " ", plain(beat["say"])).strip()
        text = beat.get("tts", text)          # pronúncia alternativa opcional
        samples, sr = k.create(text, voice=voice, speed=speed, lang="en-us")
        samples = trim(samples, sr)
        dur = len(samples) / sr
        chunks = chunks_of(beat)
        # tempo de cada legenda proporcional ao tamanho falado
        weights = [len(plain(c)) + 4 for c in chunks]
        tot = sum(weights)
        acc = t
        caps = []
        for c, w in zip(chunks, weights):
            d = dur * w / tot
            caps.append({"text": c, "start": acc, "end": acc + d})
            acc += d
        timeline.append({"beat": bi, "start": t, "end": t + dur, "captions": caps})
        audio += [samples.astype(np.float32), np.zeros(int(GAP * sr), dtype=np.float32)]
        t += dur + GAP
        print(f"  voz {bi + 1}/{len(script['beats'])}: {dur:.1f}s", flush=True)
    wav = np.concatenate(audio)
    sf.write(out_dir / "narration.wav", wav, sr)
    return timeline, len(wav) / sr


def trim(x, sr, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] - int(0.03 * sr))
    b = min(len(x), idx[-1] + int(0.08 * sr))
    return x[a:b]


# ---------------------------------------------------------------- trilha
def music(seconds, path, sr=44100, seed=7):
    """Trilha de suspense sintetizada (sem direitos autorais)."""
    import soundfile as sf
    rnd = np.random.default_rng(seed)
    t = np.arange(int(seconds * sr)) / sr
    root = 55.0
    pad = np.zeros_like(t)
    for f, a in [(root, 0.5), (root * 1.5, 0.25), (root * 2, 0.2), (root * 2.38, 0.12)]:
        lfo = 0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t + f)
        pad += a * lfo * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.2 * t))
    # pulso grave a 80 bpm
    beat = 60 / 80
    pulse = np.zeros_like(t)
    env_len = int(0.35 * sr)
    env = np.exp(-np.linspace(0, 8, env_len))
    kick = env * np.sin(2 * np.pi * 48 * np.arange(env_len) / sr)
    for s in np.arange(0, seconds, beat):
        i = int(s * sr)
        j = min(len(t), i + env_len)
        pulse[i:j] += kick[: j - i] * 0.8
    # tique agudo tipo relógio
    tick = np.zeros_like(t)
    tl = int(0.02 * sr)
    tenv = np.exp(-np.linspace(0, 10, tl)) * rnd.normal(0, 1, tl)
    for s in np.arange(beat / 2, seconds, beat):
        i = int(s * sr)
        j = min(len(t), i + tl)
        tick[i:j] += tenv[: j - i] * 0.12
    mix = pad * 0.5 + pulse + tick
    fade = np.minimum(1, np.minimum(t / 1.5, (seconds - t) / 2))
    mix = mix * fade
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.9
    sf.write(path, np.stack([mix, mix], 1).astype(np.float32), sr)


# ---------------------------------------------------------------- legenda
class Captioner:
    def __init__(self, scale):
        self.s = scale
        self.font = ImageFont.truetype(str(FONT_CAPTION), int(96 * scale))
        self.stroke = max(2, int(10 * scale))
        self.cache = {}

    def render(self, chunk):
        if chunk in self.cache:
            return self.cache[chunk]
        parts = parse_chunk(chunk)
        # palavras = listas de segmentos (texto, cor); pontuação colada fica na mesma palavra
        words, glue = [], False
        for txt, col in parts:
            for tok in re.findall(r"\S+|\s+", txt):
                if tok.isspace():
                    glue = False
                    continue
                if glue and words:
                    words[-1].append((tok, col))
                else:
                    words.append([(tok, col)])
                glue = True
        d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        maxw = int(940 * self.s)
        lines, cur, curw = [], [], 0
        space = d.textlength(" ", font=self.font)
        for segs in words:
            ww = sum(d.textlength(t, font=self.font) for t, _ in segs)
            if cur and curw + space + ww > maxw:
                lines.append(cur)
                cur, curw = [], 0
            cur.append((segs, ww))
            curw += (space if len(cur) > 1 else 0) + ww
        if cur:
            lines.append(cur)
        asc, desc = self.font.getmetrics()
        lh = asc + desc
        pad = self.stroke * 2 + 8
        widths = [sum(x[1] for x in ln) + space * (len(ln) - 1) for ln in lines]
        im = Image.new("RGBA", (int(max(widths)) + pad * 2, lh * len(lines) + pad * 2), (0, 0, 0, 0))
        dr = ImageDraw.Draw(im)
        for li, ln in enumerate(lines):
            x = pad + (max(widths) - widths[li]) / 2
            y = pad + li * lh
            for segs, ww in ln:
                for w, col in segs:
                    fill = COLORS.get(col, (255, 255, 255)) if col else (255, 255, 255)
                    dr.text((x + 4 * self.s, y + 6 * self.s), w, font=self.font, fill=(0, 0, 0, 160),
                            stroke_width=self.stroke, stroke_fill=(0, 0, 0, 160))
                    dr.text((x, y), w, font=self.font, fill=fill, stroke_width=self.stroke, stroke_fill="black")
                    x += dr.textlength(w, font=self.font)
                x += space
        self.cache[chunk] = im
        return im


# ---------------------------------------------------------------- imagens
def load_shot_image(proj, shot, size, handles):
    w, h = size
    ref = shot["img"]
    if ref.startswith("@"):
        im = assets.make(ref, handles)
    else:
        p = proj / "images" / ref
        if not p.exists():
            alt = list((proj / "images").glob(Path(ref).stem + ".*"))
            p = alt[0] if alt else p
        if p.exists():
            im = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        else:
            print(f"  ! faltando {ref}, usando placeholder")
            im = assets.placeholder(ref, shot.get("prompt"))
    # base com folga de 18% para zoom e tremida
    bw, bh = int(w * 1.18), int(h * 1.18)
    if shot.get("fit") == "contain":
        canvas = Image.new("RGB", (bw, bh), shot.get("bg", "white"))
        c = ImageOps.contain(im, (int(bw / 1.18), int(bh / 1.18)), Image.LANCZOS)  # inteira no zoom 1.0
        canvas.paste(c, ((bw - c.width) // 2, (bh - c.height) // 2))
        return canvas
    return ImageOps.fit(im, (bw, bh), Image.LANCZOS)


def zoom_for(fx, p, f):
    """Devolve (zoom, dx, dy) em função do progresso p (0..1) e frame f."""
    if fx == "zoom_out":
        return 1.14 - 0.12 * p, 0, 0
    if fx == "pop":
        z = 1.0 + 0.10 * math.exp(-p * 12) + 0.03 * p
        return z, 0, 0
    if fx == "shake":
        rnd = random.Random(f)
        a = 14 * (1 - p) + 4
        return 1.08 + 0.04 * p, rnd.uniform(-a, a), rnd.uniform(-a, a)
    if fx == "pan_left":
        return 1.1, 60 * (0.5 - p), 0
    if fx == "pan_right":
        return 1.1, -60 * (0.5 - p), 0
    if fx == "static":
        return 1.0, 0, 0
    return 1.0 + 0.12 * p, 0, 0   # zoom_in


def frame_from(base, size, z, dx, dy):
    w, h = size
    bw, bh = base.size
    cw, ch = bw / 1.18 / z, bh / 1.18 / z
    cx, cy = bw / 2 + dx, bh / 2 + dy
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return base.resize((w, h), Image.BILINEAR, box=box)


def draw_overlay(img, ov, s, p):
    if not ov:
        return img
    d = ImageDraw.Draw(img)
    w, h = img.size
    red = (235, 20, 20)
    if "circle" in ov:
        cx, cy, r = ov["circle"]
        cx, cy, r = cx * w, cy * h, r * w
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=red, width=int(14 * s))
        if ov.get("arrow"):
            ax, ay = cx + r * 1.05, cy - r * 1.05
            bx, by = ax + r * 0.9, ay - r * 0.9
            d.line((bx, by, ax, ay), fill=red, width=int(26 * s))
            hd = r * 0.38
            d.polygon([(ax - 4 * s, ay + 4 * s), (ax + hd, ay + hd * 0.05), (ax - hd * 0.05, ay - hd)], fill=red)
    if ov.get("x") and p > 0.08:
        m = 0.14
        x0, x1, y0, y1 = w * m, w * (1 - m), h * 0.22, h * 0.72
        d.line((x0, y0, x1, y1), fill=red, width=int(70 * s))
        d.line((x1, y0, x0, y1), fill=red, width=int(70 * s))
    return img


# ---------------------------------------------------------------- montagem
def build_shots(script, timeline, total, outro_s):
    shots = []
    for beat, tl in zip(script["beats"], timeline):
        caps = tl["captions"]
        i = 0
        for k, sh in enumerate(beat["shots"]):
            n = sh.get("n", 1)
            start = tl["start"] if k == 0 else caps[min(i, len(caps) - 1)]["start"]
            shots.append(dict(sh, start=start))
            i += n
    if shots:
        shots[0]["start"] = 0
    for a, b in zip(shots, shots[1:]):
        a["end"] = b["start"]
    shots[-1]["end"] = total
    shots.append({"img": "@outro", "start": total, "end": total + outro_s, "fx": "static", "outro": True})
    return shots


def render(proj, preview=False, keep_audio=False):
    proj = Path(proj).resolve()
    script = json.loads((proj / "script.json").read_text())
    channel = json.loads((ROOT / "channel.json").read_text())
    handles = [(h["label"], h["handle"]) for h in channel.get("socials", [])]
    out = proj / "out"
    out.mkdir(exist_ok=True)
    scale = 0.5 if preview else 1.0
    size = (int(W * scale) // 2 * 2, int(H * scale) // 2 * 2)

    tl_path = out / "timeline.json"
    if keep_audio and tl_path.exists() and (out / "narration.wav").exists():
        data = json.loads(tl_path.read_text())
        timeline, total = data["timeline"], data["total"]
    else:
        print("narração...")
        timeline, total = synth(script, out)
        tl_path.write_text(json.dumps({"timeline": timeline, "total": total}, indent=1))
    outro_s = script.get("outro", {}).get("seconds", 3.5)
    full = total + outro_s
    print(f"duração: {full:.1f}s")

    print("trilha...")
    music(full, out / "music.wav")
    mix = out / "mix.wav"
    vol = script.get("music_volume", 0.16)
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", str(out / "narration.wav"), "-i", str(out / "music.wav"),
        "-filter_complex",
        f"[0:a]aresample=44100,apad=pad_dur={outro_s},volume=1.6[v];[1:a]volume={vol}[m];"
        f"[v][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]",
        "-map", "[a]", "-t", f"{full:.3f}", str(mix)], check=True)

    shots = build_shots(script, timeline, total, outro_s)
    caps = [c for tl in timeline for c in tl["captions"]]
    capper = Captioner(scale)
    wm_font = ImageFont.truetype(str(FONT_UI_BOLD), int(34 * scale))
    handle = channel.get("watermark", "")

    video = out / ("preview.mp4" if preview else "video.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{size[0]}x{size[1]}", "-r", str(FPS), "-i", "-", "-i", str(mix),
           "-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
           "-crf", "26" if preview else "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", str(video)]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)

    nframes = int(math.ceil(full * FPS))
    cur_shot, base, ci = -1, None, 0
    corners = ["tl", "tr", "bl"]
    print(f"renderizando {nframes} frames...")
    for f in range(nframes):
        t = f / FPS
        si = cur_shot if cur_shot >= 0 else 0
        while si + 1 < len(shots) and shots[si + 1]["start"] <= t:
            si += 1
        if si != cur_shot:
            cur_shot = si
            base = load_shot_image(proj, shots[si], size, handles)
        sh = shots[si]
        p = (t - sh["start"]) / max(0.01, sh["end"] - sh["start"])
        z, dx, dy = zoom_for(sh.get("fx", "zoom_in"), min(1, max(0, p)), f)
        img = frame_from(base, size, z, dx * scale, dy * scale)
        img = draw_overlay(img, sh.get("overlay"), scale, p)

        if not sh.get("outro"):
            while ci < len(caps) and caps[ci]["end"] <= t:
                ci += 1
            if ci < len(caps) and caps[ci]["start"] <= t:
                c = caps[ci]
                cim = capper.render(c["text"])
                age = t - c["start"]
                k = 1.0 if age > 0.1 else 0.86 + 1.4 * age
                if k != 1.0:
                    cim = cim.resize((max(1, int(cim.width * k)), max(1, int(cim.height * k))), Image.BILINEAR)
                cx = (size[0] - cim.width) // 2
                cy = int(size[1] * 0.63) - cim.height // 2
                img.paste(cim, (cx, cy), cim)
            if handle:
                d = ImageDraw.Draw(img, "RGBA")
                corner = corners[si % 3]
                tw = d.textlength(handle, font=wm_font)
                m = int(40 * scale)
                x = m if corner in ("tl", "bl") else size[0] - m - tw
                y = int(90 * scale) if corner in ("tl", "tr") else int(size[1] * 0.80)
                d.text((x, y), handle, font=wm_font, fill=(255, 255, 255, 150),
                       stroke_width=max(1, int(3 * scale)), stroke_fill=(0, 0, 0, 120))
        ff.stdin.write(img.tobytes())
        if f == int(2.0 * FPS):
            img.save(out / "thumb.jpg", quality=90)
        if f % 300 == 0:
            print(f"  {f}/{nframes}", flush=True)
    ff.stdin.close()
    ff.wait()
    if ff.returncode:
        sys.exit("ffmpeg falhou")
    print(f"pronto: {video}")
    return video


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--preview", action="store_true", help="540x960 rápido")
    ap.add_argument("--keep-audio", action="store_true", help="reusa a narração já gerada")
    a = ap.parse_args()
    render(a.project, a.preview, a.keep_audio)


if __name__ == "__main__":
    main()
