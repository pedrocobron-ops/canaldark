---
name: editor-video
description: Monta shorts verticais (1080x1920, 30 fps) de humor absurdo a partir de um script.json, com narração neural local, legenda colorida palavra-chave, zoom/tremida nas imagens, círculo e seta vermelhos, X vermelho, ícones de app, prints falsos de chat, trilha de suspense e cartão final. Use quando o Pedro pedir para editar, montar, renderizar, refazer ou ajustar um vídeo do canal.
---

# Editor de vídeo do canal

Conversa com o Pedro em português. Nunca usar travessão em nada.

O editor é o pacote `editor/` deste repositório. Ele lê `projects/<slug>/script.json`, gera a voz, sincroniza legendas e imagens e exporta `projects/<slug>/out/video.mp4`.

## Preparar o ambiente (uma vez por sessão)

```bash
bash setup.sh
```

Instala `kokoro-onnx` e `soundfile` e baixa o modelo de voz (cerca de 120 MB) em `models/`. Precisa de acesso ao GitHub e ao PyPI. Já vem com ffmpeg, Pillow e numpy.

## Comandos

```bash
python -m editor.make projects/<slug> --preview      # 540x960, cerca de 1,5 min, para conferir
python -m editor.make projects/<slug>                # final 1080x1920
python -m editor.make projects/<slug> --keep-audio   # reaproveita a narração já gerada (só mudou imagem/efeito)
```

Saídas em `out/`: `video.mp4`, `narration.wav`, `music.wav`, `mix.wav`, `timeline.json`, `thumb.jpg`.

## Formato do script.json

```json
{
  "title": "Why is X refusing to ...?",
  "voice": "am_onyx",          // am_onyx (grave), am_michael, am_fenrir, am_adam
  "speed": 0.9,                // 0.9 dá cerca de 2,6 palavras/s
  "music_volume": 0.16,
  "post": "legenda do post + hashtags",
  "style_suffix": "sufixo de estilo para os prompts de cartoon",
  "beats": [
    {
      "say": "Why is {y:Squidward} | refusing to work | on the new {b:iMessage 2}?",
      "tts": "opcional: texto alternativo só para a pronúncia",
      "shots": [
        {"img": "01.png", "n": 2, "fit": "contain", "fx": "zoom_in", "prompt": "..."},
        {"img": "@icon:2:#1E7BFF", "n": 1, "fx": "pop"}
      ]
    }
  ],
  "outro": {"seconds": 3.5}
}
```

- **beat** é uma frase narrada de uma vez (a prosódia fica natural). `|` separa as legendas, de 1 a 4 palavras cada.
- **Palavra-chave colorida:** `{y:...}` amarelo (destaque), `{r:...}` vermelho (perigo), `{g:...}` verde, `{b:...}` azul (apps), `{o:...}` laranja, `{p:...}` rosa. Uma por legenda, no máximo.
- **shots:** cada imagem cobre `n` legendas seguidas da frase. A soma dos `n` deve ser igual ao número de legendas.
- **img:**
  - `NN.png` fica em `projects/<slug>/images/`. Aceita qualquer extensão com o mesmo nome. Se faltar, o editor põe um placeholder com o prompt.
  - `@icon:<rótulo>:<#cor>` desenha o ícone de app com o número em neon (`@icon::#34C759` sai sem número).
  - `@chat:family` e `@chat:squidward` desenham prints falsos de grupo da família. Para criar outros, adicione em `CHATS`, no arquivo `editor/assets.py`.
- **fit:** `cover` (padrão, preenche a tela) ou `contain` (imagem inteira sobre fundo branco, para personagem recortado e boneco 3D).
- **fx:** `zoom_in` (padrão), `zoom_out`, `pop` (impacto), `shake` (tremida, para alarme, susto e raiva), `pan_left`, `pan_right`, `static`.
- **overlay:** `{"circle": [x, y, raio], "arrow": true}` com coordenadas de 0 a 1 da tela, para a "prova" com círculo e seta vermelhos. `{"x": true}` põe um X vermelho gigante.

Canal, marca d'água e redes do cartão final ficam em `channel.json`, na raiz.

## Regras de edição (tiradas dos vídeos de referência do "Você Sabo?")
- Entre 60 e 75 s no total. Medir com o `timeline.json` e ajustar `speed` ou o texto.
- A legenda troca a cada 0,5 a 1,2 s. A imagem troca a cada 2 a 4 legendas, e nunca fica mais de 4 s parada.
- O personagem aparece no primeiro quadro, e o tema (evento, app) no segundo shot.
- Alternar as fontes de imagem: cartoon do personagem, foto realista, banco de imagem, boneco 3D branco, print de celular, ícone.
- Nunca usar trecho real do desenho (Content ID). Só imagem gerada.
- A legenda fica a 63% da altura, em Luckiest Guy branca com contorno preto.

## Controle de qualidade antes de entregar
1. Renderizar com `--preview` e montar uma folha de contato:
   `ffmpeg -i out/preview.mp4 -vf "fps=1/3,scale=200:-1,tile=8x3" -frames:v 1 folha.jpg`
2. Olhar a folha (Read na imagem). Conferir se tem placeholder ("FALTA:"), se a legenda está cortada, se a legenda cobre o rosto do personagem (se cobrir, ajustar com `fit: contain` ou trocar o shot) e se a duração está entre 60 e 75 s.
3. Renderizar o final e entregar o `video.mp4` com `SendUserFile`, mais o texto do post.

## Imagens vindas do Google Drive
O Pedro gera as imagens com os prompts do `PROMPTS.md` e sobe numa pasta do Drive com o nome do slug. Busque a pasta com `mcp__Google_Drive__search_files`, liste os arquivos, baixe cada um com `mcp__Google_Drive__download_file_content` e salve em `projects/<slug>/images/` com o nome exato (`01.png`, `02.png`...).
