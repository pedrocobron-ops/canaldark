"""Converte downloads do conector Google Drive (JSON base64 salvo em tool-results)
em arquivos de imagem do projeto.
Uso: python tools/drive_import.py projects/<slug> mapa.json [pasta_tool_results]
mapa.json: {"<fileId>": "01.png", ...}"""
import base64, glob, json, sys
from pathlib import Path

proj, mapa = Path(sys.argv[1]), json.load(open(sys.argv[2]))
src = sys.argv[3] if len(sys.argv) > 3 else str(Path.home() / ".claude/projects")
(proj / "images").mkdir(parents=True, exist_ok=True)
done = set()
for f in sorted(glob.glob(f"{src}/**/mcp-Google_Drive-download_file_content-*.txt", recursive=True)):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    fid = d.get("id")
    if fid in mapa and fid not in done:
        ext = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}.get(d.get("mimeType"), ".png")
        out = proj / "images" / (Path(mapa[fid]).stem + ext)
        out.write_bytes(base64.b64decode(d["content"]))
        done.add(fid)
        print(f"{mapa[fid]:8s} <- {d.get('title')}")
falta = [v for k, v in mapa.items() if k not in done]
print("faltando:", falta or "nada")
