"""Gera projects/<slug>/PROMPTS.md a partir do script.json.
Uso: python tools/prompts.py projects/<slug>"""
import json
import sys
from pathlib import Path

proj = Path(sys.argv[1])
d = json.loads((proj / "script.json").read_text())
suffix = d.get("style_suffix", "2D cartoon illustration, bold outlines, vertical 9:16")
out = [f"# Imagens para gerar: {proj.name}", "",
       "Gere cada imagem na vertical 9:16 (ou o maior tamanho possível) e salve com o nome exato indicado.",
       f"Suba todas numa pasta do Google Drive chamada `{proj.name}`.", "",
       "Dica: Gemini (Nano Banana) e ChatGPT costumam aceitar personagens reais. Se um recusar, tente o outro.", ""]
seen = set()
for b in d["beats"]:
    for sh in b["shots"]:
        if "prompt" not in sh or sh["img"] in seen:
            continue
        seen.add(sh["img"])
        p = sh["prompt"]
        low = p.lower()
        if sh.get("style") == "photo" or low.startswith("realistic") or "photograph" in low.split(" of ")[0]:
            p += ", vertical 9:16" if "photograph" in low else ", photorealistic, vertical 9:16"
        elif any(k in low.split(" of ")[0] for k in ("painting", "engraving", "woodcut", "print")) \
                or "inserted into" in low or "3d powerpoint" in low or "3d stick" in low:
            p += ", vertical 9:16"     # pintura ou boneco 3D: nunca recebe o estilo cartoon
        else:
            p += ", " + suffix
        out += [f"## {sh['img']}", "", "```", p, "```", ""]
(proj / "PROMPTS.md").write_text("\n".join(out))
print(f"{len(seen)} prompts em {proj / 'PROMPTS.md'}")
