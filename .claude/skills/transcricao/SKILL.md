---
name: transcricao
description: Transcreve localmente (Whisper, grátis, sem internet depois do modelo baixado) o vídeo bruto do YouTube que está na pasta bruto/, em português, e salva em trabalho/ o texto com o horário de início e fim de cada frase (JSON, TXT e legenda SRT). Use sempre que o usuário pedir para transcrever, legendar, "tirar o texto" ou "passar para texto" um vídeo/áudio, quando quiser saber o que foi dito em que momento, ou como primeiro passo antes de montar um plano de edição — mesmo que ele não diga "Whisper" ou "transcrição".
---

# Transcrição de vídeo bruto

Esta skill é o primeiro passo do fluxo de edição: bruto/ → **trabalho/ (transcrição)** → plano-de-edicao → final/.
A transcrição com o tempo de cada frase (e de cada palavra) é o que permite depois achar pausas, repetições e o lugar exato dos letreiros, por isso o tempo importa tanto quanto o texto.

## Passos

1. **Escolha o arquivo.** Liste `bruto/` (vídeos e áudios: .mp4 .mov .mkv .webm .m4a .mp3 .wav).
   - Se houver só um, use-o.
   - Se houver vários e o usuário não disse qual, pergunte (mostre nome, tamanho e data) — transcrever o errado custa muitos minutos.
   - Se a pasta estiver vazia, peça para ele colocar o vídeo em `bruto/` e pare.

2. **Ache o Python que tem o Whisper.** Teste nesta ordem e use o primeiro que funcionar:
   `~/whisper-env/bin/python -c "import whisper"` → `python3 -c "import whisper"` → `python -c "import whisper"`.
   Se nenhum funcionar, explique que o Whisper não está instalado e pergunte se pode instalar (`pip install openai-whisper`, que precisa do FFmpeg). Não instale sem permissão.

3. **Escolha o modelo.** Padrão: `small` (bom equilíbrio para português em computador sem placa de vídeo).
   Para vídeos longos (> 30 min) avise que pode demorar e ofereça `base` (mais rápido). Se o usuário pedir mais qualidade, use `medium` ou `turbo`.
   Na primeira vez, o modelo é baixado da internet (centenas de MB).

4. **Rode o script** a partir da raiz da pasta do projeto:
   ```bash
   <python> .claude/skills/transcricao/scripts/transcrever.py "bruto/<arquivo>" --modelo small --saida trabalho
   ```
   Rode em segundo plano se o vídeo for longo e acompanhe a saída.

5. **Confira e mostre.** Abra `trabalho/<nome>.transcricao.txt` e mostre ao usuário as primeiras ~15 linhas, a duração total e quantas frases saíram. Aponte palavras que parecem mal transcritas (nomes próprios, termos técnicos) e pergunte se ele quer corrigir alguma — correções vão no `.json` (campo `texto`) e no `.txt`.

## O que fica em trabalho/

| Arquivo | Para quê |
|---|---|
| `<nome>.transcricao.json` | Usado pela skill plano-de-edicao. Cada frase tem `id`, `inicio`, `fim` (segundos), `texto` e `palavras` com tempo. |
| `<nome>.transcricao.txt` | Para ler: `[00:01:23.4 -> 00:01:27.9] frase` |
| `<nome>.srt` | Legenda pronta para subir no YouTube (do vídeo bruto — depois dos cortes, os tempos mudam). |

No fim, sugira o próximo passo: "Quer que eu monte o plano de edição?" (skill plano-de-edicao).
