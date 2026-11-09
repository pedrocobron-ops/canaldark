---
name: novo-video
description: Produz um vídeo do canal do zero, da pauta ao MP4 pronto. Use quando o Pedro pedir um vídeo novo, um episódio, uma continuação de série ou disser "faz o próximo".
---

# Novo vídeo: da pauta ao MP4

Conversa em português, roteiro em inglês, nunca travessão.

## Passo a passo

1. **Pauta.** Se o Pedro não deu tema, propor 3 combinações (personagem com função + alvo + motivo mesquinho) seguindo a skill `roteiro-shorts-absurdo`, se ela estiver disponível, e escolher a melhor. Personagem **real** (o Pedro quer o personagem conhecido, não um genérico). Evitar Disney e Nintendo.

2. **Pasta do projeto.** `projects/NNN-<slug>/`, numerando a partir do último existente.

3. **Roteiro (`script.json`).** Seguir as batidas do formato A ou B e o formato descrito na skill `editor-video`. Use `projects/001-squidward-imessage/script.json` como modelo.
   - Narração entre 175 e 190 palavras: o vídeo tem que passar de 1 minuto (mínimo de 61 s). Sem cartão final.
   - Legendas de 1 a 4 palavras, uma palavra-chave colorida por legenda.
   - Tudo que for app, print ou ícone sai como asset desenhado (`@icon`, `@chat`), para poupar imagem do Pedro.
   - De 16 a 22 imagens geradas por vídeo. Cada shot com imagem gerada tem um `prompt` em inglês. Prompt de personagem começa pelo nome completo e pela obra ("Squidward Tentacles from SpongeBob SquarePants ...").

4. **Prompts para o Pedro.** Gerar o `PROMPTS.md` a partir do JSON (o script em `tools/prompts.py` faz isso) e mandar com `SendUserFile`. Pedir que ele suba tudo numa pasta do Drive com o nome do slug.

5. **Prévia enquanto espera.** Rodar `python -m editor.make projects/<slug> --preview` com os placeholders, para validar duração e ritmo. Ajustar o texto se ficar abaixo de 61 s ou acima de 75 s.

6. **Imagens.** Quando o Pedro avisar, baixar do Drive para `projects/<slug>/images/` (ver `editor-video`).

7. **Render final**, controle de qualidade pela folha de contato e entrega do `video.mp4` com o texto do post e a ideia de continuação.

8. **Git.** Commitar o `script.json`, o `PROMPTS.md` e as imagens. O `out/` não vai para o git.
