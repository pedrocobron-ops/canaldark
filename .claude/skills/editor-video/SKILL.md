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
  "voice": "am_adam",          // padrão do canal (escolhida pelo Pedro). Outras: am_onyx, am_michael, am_fenrir
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
  "outro": {}                // sem cartão final (regra do canal)
}
```

- **beat** é uma frase narrada de uma vez (a prosódia fica natural). `|` separa as legendas, de 1 a 4 palavras cada.
- **Palavra-chave colorida:** `{y:...}` amarelo (destaque), `{r:...}` vermelho (perigo), `{g:...}` verde, `{b:...}` azul (apps), `{o:...}` laranja, `{p:...}` rosa. Uma por legenda, no máximo.
- **shots:** cada imagem cobre `n` legendas seguidas da frase. A soma dos `n` deve ser igual ao número de legendas.
- **img:**
  - `NN.png` fica em `projects/<slug>/images/`. Aceita qualquer extensão com o mesmo nome. Se faltar, o editor põe um placeholder com o prompt.
  - `@icon:<rótulo>:<#cor>` desenha o ícone de app com o número em neon (`@icon::#34C759` sai sem número).
  - `@chat:family` e `@chat:squidward` desenham prints falsos de grupo da família. Para criar outros, adicione em `CHATS`, no arquivo `editor/assets.py`.
- **fit:** `cover` (padrão, preenche a tela), `contain` (imagem inteira sobre fundo branco, para personagem recortado e boneco 3D) ou `blurfill` (foto horizontal inteira no centro, com ela mesma desfocada no fundo; use `cap_y: 0.24`).
- **fx:** `zoom_in` (padrão), `zoom_out`, `pop` (impacto), `shake` (tremida, para alarme, susto e raiva), `pan_left`, `pan_right`, `static`.
- **tr:** transição de entrada do shot: `whip` (chicote lateral com desfoque), `zoom` (zoom através), `punch` (entra grande e assenta), `fade` (passa pelo escuro), `cut` (seco). Sem `tr`, o editor alterna sozinho seguindo `CYCLE` em `editor/transitions.py`. Use `punch` para impacto e revelação, e `whip` para mudança de assunto.
- **sfx:** efeitos sonoros extras no início do shot: `alarm`, `ding`, `pop`, `impact`, `thud`, `whoosh`, `swish`. Os whooshes das transições e o impacto do punch entram sozinhos. Volume geral em `sfx_volume` (padrão 0.8).
- **anim** (só para `@chat:*`): `reveal` faz as mensagens aparecerem uma por uma com "ding"; `reveal_strike` revela e depois risca cada áudio com X vermelho e batida. Prefira isso a um chat parado.
- **@phone:<rótulo>:<#cor>** desenha um celular com o ícone do app, sobre o fundo desfocado de `phone_bg` (uma imagem do projeto). Para virar um ícone em outro: `"flip_to": "@phone:2:#FF8A00", "flip_cap": 3` (gira na 4ª legenda do shot, com swish). Prefira isso à tela preta com ícone.
- **inset:** cola outra imagem dentro de uma área oval, por exemplo na nuvem de pensamento do boneco 3D: `{"img": "12.png", "box": [x0, y0, x1, y1], "center": [0.5, 0.35]}`, com coordenadas de 0 a 1 da imagem.
- **cap_y:** altura da legenda naquele shot (0 a 1; padrão 0.63). Use 0.24 quando os personagens estiverem no meio ou embaixo da imagem. Sempre confira na folha de contato por shot se a legenda cobre algum rosto ou personagem.
- **bg_img** (só para telas desenhadas `@...`): põe a tela sobre uma imagem do projeto desfocada e escurecida, no lugar do fundo liso. **Use sempre**, escolhendo a cena daquele trecho, para as telas não ficarem todas iguais. Ajustes: `bg_dark` (0 a 1, padrão 0.5), `bg_blur` (padrão 22), `key_tol` (tolerância do recorte do fundo; aumente em telas com brilho em volta, como `@award`). **tilt** inclina o cartão em graus (-4 a 4) com sombra: use em objetos (ficha, cupom, prêmio, calendário), não em placar nem estatística.
- **overlay:** `{"circle": [x, y, raio], "arrow": true}` com coordenadas de 0 a 1 da tela, para a "prova" com círculo e seta vermelhos. `{"x": true}` põe um X vermelho gigante.

Canal, marca d'água e redes do cartão final ficam em `channel.json`, na raiz.

## Regras de edição (tiradas dos vídeos de referência do "Você Sabo?")
- **Todo vídeo passa de 1 minuto: mínimo de 61 s, ideal entre 62 e 75 s.** O editor avisa e desacelera a voz se ficar curto, mas o certo é acrescentar uma frase ao roteiro (de 175 a 190 palavras em speed 0.9).
- **REGRA: nenhuma imagem fica mais de 4 s seguidos na tela** (cenas seguidas da mesma imagem contam juntas). Meta: média de 2 a 2,5 s por imagem, como nas referências. O editor avisa com "IMAGEM PARADA MAIS DE 4s"; não entregar vídeo com esse aviso. Para quebrar trechos longos, use elementos desenhados que reforcem a piada (tábua, documento, cartão de estatística, guia de TV) ou peça mais uma imagem.
- **Nunca deixar mais de 4 s parado no mesmo visual sem animação.** Chat tem que revelar ou riscar, ícone tem que girar ou estar no celular.
- **Fotos realistas sempre com o personagem escondido** (atrás de algo, no reflexo, na sombra, só a mão ou a garra), **sem círculo nem seta** (o Pedro prefere que o público ache sozinho). Foto realista "pura" deixa o meio do vídeo chato. Nos prompts, peça "2D cartoon character inserted into the real photo" e anexe no Gemini a imagem de corpo inteiro do personagem como referência.
- **Foto de fantasia do personagem em festa infantil** (como nos vídeos de referência) é ótima para quebrar repetição no meio do vídeo. Se for horizontal, use `fit: blurfill`.
- **Boneco 3D branco: no máximo um por vídeo, e nunca no final** (o painel de espectadores achou que ele quebra o clima de desenho). Nada de foto de banco de imagem genérica (gente de escritório) para "witnesses": use testemunhas no estilo do vídeo.
- **Final = punchline + loop.** O vídeo termina na última piada, com o personagem na tela; a pergunta para o público vai no texto do post, não na narração. Se o personagem tem bordão famoso, use pelo menos um.
- **Efeitos sonoros em toda transição e nos objetos que fazem barulho** (alarme, notificação).
- **Sem cartão final de redes. O final é em loop:** a última imagem passa com whip para a primeira (o editor faz sozinho; `"loop": false` desliga). Assim o replay emenda sem quebra.
- **Marca d'água = mascote (`assets/brand/logo.png`) + @didyouknew, a 80% de opacidade, só nos cantos de cima** (configurada em `channel.json`), porque o TikTok e o Reels cobrem a parte de baixo.
- **Áudio:** a voz passa por EQ, de-esser e compressor, a trilha abaixa sozinha quando a voz fala (ducking) e o mix final é normalizado em -14 LUFS, igual às referências. A sincronia das legendas usa a duração real de cada trecho falado, encaixada nas pausas.
- **Capa:** o render final gera `out/cover.jpg`. Configure em `"cover": {"img": "10.png", "text": "...", "y": 0.66}`, usando a imagem mais expressiva do personagem e a pergunta-gancho. O vídeo termina na última fala, segurando a imagem por 0,7 s.
- **Transições entre quase todos os shots** (chicote, zoom, punch, escurecer), com poucos cortes secos. Cada uma dura de 0,2 a 0,36 s.
- A legenda troca a cada 0,5 a 1,2 s. A imagem troca a cada 2 a 4 legendas, e nunca fica mais de 4 s parada.
- O personagem aparece no primeiro quadro, já com a primeira legenda (o editor mostra a legenda desde 0 s), e o tema (evento, app) no segundo shot.
- **Antes de entregar, rode a skill `analise-tiktok`** (painel de espectadores).
- Alternar as fontes de imagem: cartoon do personagem, foto realista, banco de imagem, boneco 3D branco, print de celular, ícone.
- Nunca usar trecho real do desenho (Content ID). Só imagem gerada.
- A legenda fica a 63% da altura, em Luckiest Guy branca com contorno preto.

## Controle de qualidade antes de entregar
1. Renderizar com `--preview` e montar uma folha de contato:
   `ffmpeg -i out/preview.mp4 -vf "fps=1/3,scale=200:-1,tile=8x3" -frames:v 1 folha.jpg`
2. Olhar a folha (Read na imagem). Conferir se tem placeholder ("FALTA:"), se a legenda está cortada, se a legenda cobre o rosto do personagem (se cobrir, ajustar com `fit: contain` ou trocar o shot) e se a duração está entre 60 e 75 s.
3. Renderizar o final e entregar o `video.mp4` com `SendUserFile`, mais o texto do post.

## Imagens vindas do Google Drive
O Pedro gera as imagens com os prompts do `PROMPTS.md` e sobe numa pasta do Drive. **O conector do Drive só aguenta arquivos abaixo de cerca de 6 MB**: acima disso a conexão cai. Peça sempre as imagens em JPG. Se alguma passar do limite, peça que ele mande aquela imagem direto no chat ou reenvie em JPG. Baixe uma imagem por vez, nunca em paralelo. Normalmente ele manda o link da pasta. Os arquivos podem vir com nomes descritivos, e não `01.png`.

1. Liste a pasta com `mcp__Google_Drive__search_files`, usando a query `parentId = '<id da pasta>'` e `excludeContentSnippets: true`. Pagine até acabar.
2. Relacione cada arquivo ao shot pelo título e pelo prompt, e salve o mapa em `projects/<slug>/drive_map.json` no formato `{"<fileId>": "01.png"}`.
3. Chame `mcp__Google_Drive__download_file_content` para cada fileId (pode ser em paralelo). O resultado é grande demais e é salvo automaticamente em `tool-results/`. Não leia esse arquivo.
4. Converta tudo de uma vez com `python tools/drive_import.py projects/<slug> projects/<slug>/drive_map.json /root/.claude/projects`.
5. Monte uma folha de contato das imagens e confira se cada uma bate com a cena. Ajuste as coordenadas de `circle` olhando a imagem real.
