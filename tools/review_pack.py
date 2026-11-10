"""Monta o pacote de revisão de um vídeo para os agentes-espectadores.

Uso: python tools/review_pack.py projects/<slug>

Gera em projects/<slug>/out/review/:
  hook.jpg        quadros de 0 a 3 s (o que decide se a pessoa para de rolar)
  sheet_NN.jpg    1 quadro a cada 0,5 s, em folhas de 24 quadros (12 s cada)
  roteiro.md      falas com tempo, shots com duração, números gerais
"""
import json
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"


def frame(video, t, w=270):
    out = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1",
                          "-vf", f"scale={w}:-1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(out)).convert("RGB")


def tile(frames, labels, cols, path):
    w, h = frames[0].size
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 34)), (0, 0, 0))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(FONT, 24)
    for i, (im, lab) in enumerate(zip(frames, labels)):
        x, y = (i % cols) * w, (i // cols) * (h + 34)
        sheet.paste(im, (x, y + 34))
        d.text((x + 8, y + 4), lab, font=f, fill=(255, 220, 0))
    sheet.save(path, quality=88)


def clean(t):
    return re.sub(r"\{\w:([^}]*)\}", r"\1", t)


def main(proj):
    proj = Path(proj)
    out = proj / "out"
    video = out / "video.mp4"
    rv = out / "review"
    rv.mkdir(exist_ok=True)
    script = json.load(open(proj / "script.json"))
    tl = json.load(open(out / "timeline.json"))
    total = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                  str(video)], capture_output=True, text=True).stdout)

    hook_t = [0.1, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    tile([frame(video, t) for t in hook_t], [f"{t:.1f}s" for t in hook_t], 4, rv / "hook.jpg")

    ts = [i * 0.5 + 0.1 for i in range(int(total / 0.5))]
    sheets = []
    for k in range(0, len(ts), 24):
        chunk = ts[k:k + 24]
        p = rv / f"sheet_{k // 24 + 1:02d}.jpg"
        tile([frame(video, t, 200) for t in chunk], [f"{t:.1f}s" for t in chunk], 8, p)
        sheets.append(p.name)

    lines = [f"# {script.get('title', '')}", "", f"Duração: {total:.1f} s", ""]
    shots_all = []
    lines.append("## Falas e imagens (com tempo)")
    for b, beat in zip(script["beats"], tl["timeline"]):
        caps = beat["captions"]
        lines.append(f"\n**{beat['start']:.1f}s** {clean(b['say']).replace(' | ', ' ')}")
        i = 0
        for sh in b["shots"]:
            seg = caps[i:i + sh["n"]]
            i += sh["n"]
            if not seg:
                continue
            st, en = seg[0]["start"], seg[-1]["end"]
            shots_all.append(en - st)
            desc = sh.get("prompt", "")[:140] or sh["img"]
            lines.append(f"- {st:.1f}-{en:.1f}s ({en - st:.1f}s) `{sh['img']}`: {desc}")
    n = len(shots_all)
    lines += ["", "## Números",
              f"- Trocas de imagem: {n}, média {sum(shots_all) / n:.1f} s, maior {max(shots_all):.1f} s",
              f"- Palavras narradas: {sum(len(clean(b['say']).replace('|', ' ').split()) for b in script['beats'])}",
              f"- Folhas: hook.jpg, {', '.join(sheets)}"]
    if script.get("post"):
        lines += ["", "## Texto do post", script["post"]]
    (rv / "roteiro.md").write_text("\n".join(lines))
    print(rv)


if __name__ == "__main__":
    main(sys.argv[1])
