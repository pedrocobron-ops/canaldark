# canaldark

Fábrica de shorts verticais de humor absurdo (formato "Você Sabo?"), em inglês.

- `editor/`: montador de vídeo. Lê o `script.json`, gera a narração (Kokoro, local), as legendas coloridas, os zooms, os overlays, a trilha e o cartão final, e exporta MP4 em 1080x1920 a 30 fps.
- `projects/NNN-slug/`: um vídeo por pasta, com `script.json`, `PROMPTS.md`, `images/` e `out/` (fora do git).
- `.claude/skills/`: skills do Claude (`novo-video`, `editor-video` e `roteiro-shorts-absurdo`).
- `channel.json`: nome, marca d'água e redes do cartão final.

## Uso rápido

```bash
bash setup.sh
python -m editor.make projects/001-squidward-imessage --preview
python -m editor.make projects/001-squidward-imessage
```
