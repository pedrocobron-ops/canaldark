---
name: analise-tiktok
description: Analisa um vídeo pronto do canal com um painel de agentes que se comportam como pessoas rolando o feed do TikTok (cada um com um perfil), e junta tudo num veredito com correções. Use quando o Pedro perguntar "ficou perfeito?", pedir análise, revisão ou opinião sobre um vídeo renderizado.
---

# Painel de espectadores do TikTok

Conversa em português, nunca travessão. A análise tem que ser honesta: o objetivo é achar o que faz a pessoa rolar o feed, não elogiar.

## 1. Pacote de revisão

```bash
python tools/review_pack.py projects/<slug>
```

Gera em `projects/<slug>/out/review/`: `hook.jpg` (0 a 3,5 s), `sheet_NN.jpg` (um quadro a cada 0,5 s, 12 s por folha) e `roteiro.md` (falas com tempo, cada imagem com duração e prompt, números gerais e texto do post). Os agentes não ouvem o áudio: a narração está no `roteiro.md`, e a legenda aparece nos quadros.

## 2. Painel (5 agentes em paralelo, `subagent_type: general-purpose`)

Mande todos na mesma mensagem. Cada um recebe: o caminho da pasta `review`, o seu perfil (abaixo), o formato do canal (narração séria de documentário sobre algo absurdo, com um personagem de desenho famoso no meio de um fato real) e as instruções da seção 3. Não conte a eles o que você acha do vídeo.

| # | Perfil | Foco |
|---|---|---|
| 1 | **Rolador**: 19 anos, EUA, rola o feed rápido no ônibus, decide em 1 a 2 s | Gancho, primeiro quadro, momento em que rolaria para o próximo |
| 2 | **Fã do tema**: conhece bem o fato real e as pessoas reais do vídeo (no vídeo 7, swiftie) | Fato real certo ou errado, algo que ofende o fandom, vontade de comentar e marcar alguém |
| 3 | **Nostálgico do desenho**: 30 a 35 anos, cresceu vendo o personagem | Personagem fiel (cabelo, roupa, jeito), piada combina com a personalidade dele |
| 4 | **Fã de humor absurdo**: segue contas tipo "Você Sabo?" e meme de documentário falso | Lógica interna da história, escalada do absurdo, prêmio mundano, punchline, final em loop |
| 5 | **Estrategista de TikTok**: editor que vive de retenção | Ritmo, legenda cobrindo rosto, imagem parada, transições, capa, texto do post, hashtags, riscos (IA com pessoa real, direitos) |

## 3. Instruções para cada agente

- Leia `roteiro.md`, depois `hook.jpg`, depois as folhas em ordem, como se estivesse assistindo.
- Fique no personagem: reaja como aquela pessoa reagiria no feed, não como um crítico educado.
- Responda em português, sem travessão, neste formato:
  1. **Parei de rolar?** (sim ou não, e por quê, olhando só os primeiros 2 s)
  2. **Até onde assisti:** segundo em que sairia, ou "até o fim / reassisti"
  3. **Melhor momento** (segundo e motivo)
  4. **Pior momento** (segundo e motivo)
  5. **Curtir, comentar, compartilhar, seguir?** (cada um sim ou não; se comentar, escreva o comentário que deixaria)
  6. **Problemas concretos** (segundo, o que está errado, como corrigir), no máximo 5, do mais grave ao menos grave
  7. **Nota de 0 a 10**
- Não invente problemas para preencher a lista. Se algo está bom, diga.

## 4. Veredito

Junte os 5 relatórios numa tabela (perfil, parou?, saiu em, nota) e depois:
- **Problemas confirmados**: os que aparecem em 2 ou mais agentes, ou que você conferir no quadro. Confira cada um olhando a folha antes de aceitar.
- **Opiniões isoladas**: as de um agente só, com a sua avaliação (aceitar ou não).
- **Correções propostas** em ordem de impacto na retenção, separando o que o editor resolve sozinho do que precisa de imagem nova do Pedro.
- Nota média e resposta direta a "ficou perfeito?".

Não aplique as correções sem o Pedro aprovar, a não ser erros óbvios (legenda cortada, placeholder).
