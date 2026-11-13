---
name: plano-de-edicao
description: Monta o plano de edição de um vídeo do YouTube a partir da transcrição em trabalho/ e do guia estilo/ESTILO.md — entende o assunto, sugere cortes (pausas longas, repetições, retomadas, vícios de fala) e marca onde entram letreiros, gráficos, listas e zooms, com início, fim e descrição — e salva em trabalho/plano.json, sempre mostrando o plano para aprovação antes de criar qualquer coisa. Use sempre que o usuário pedir plano de edição, roteiro de cortes, "o que cortar", "onde colocar letreiro/gráfico/zoom", "decupagem", ou quiser começar a editar um vídeo já transcrito.
---

# Plano de edição

Segundo passo do fluxo: bruto/ → trabalho/ (transcrição) → **trabalho/plano.json** → final/.
O plano é uma proposta: o usuário é o editor. Nada de renderizar, cortar arquivo ou criar animação até ele aprovar — refazer um vídeo por causa de um corte errado custa muito mais do que ler uma tabela.

## 1. Reúna o material

- Transcrição: `trabalho/*.transcricao.json`. Se não houver, ofereça rodar a skill **transcricao** primeiro. Se houver várias, pergunte qual.
- Estilo: `estilo/ESTILO.md`. Ele manda nas decisões (ritmo, tom, cores, fontes, quantos letreiros, tamanho de pausa aceitável, o que nunca cortar). Se não existir, avise, siga os padrões abaixo e ofereça criar um a partir do modelo `estilo/ESTILO.md` deste projeto.
- Leia a transcrição inteira antes de propor qualquer coisa: você precisa entender o assunto, a estrutura (abertura, pontos principais, chamada final) e o que é essencial.

## 2. Ache os candidatos a corte (mecânico)

```bash
python3 .claude/skills/plano-de-edicao/scripts/analisar_pausas.py trabalho/<nome>.transcricao.json --pausa 1.2
```
Use o limite de pausa do ESTILO.md se houver. O script devolve pausas, frases vizinhas parecidas (retomadas/repetições) e vícios ("né", "tipo", "éé"). É ponto de partida: confirme cada um lendo o contexto. Uma pausa dramática antes de uma revelação pode ficar; uma repetição em que a segunda versão é a boa deve cortar a primeira.

Ao cortar pausas, deixe ~0,2–0,3 s de respiro em cada lado para a fala não ficar "picotada".

## 3. Decida os elementos visuais (interpretação)

Com base no conteúdo e no ESTILO.md:
- **letreiro**: nome de pessoa/ferramenta citada pela 1ª vez, título de seção, frase de impacto.
- **grafico**: quando há números, comparação, evolução no tempo.
- **lista**: quando a fala enumera ("três coisas", "primeiro… segundo…").
- **zoom**: ênfase, piada, ponto-chave — com moderação (padrão: no máximo 1 a cada ~30 s).
Cada item precisa de um motivo ligado ao que está sendo dito.

## 4. Salve trabalho/plano.json

Tempos em segundos do vídeo **bruto** (antes dos cortes), com 2 casas decimais.

```json
{
  "video": "bruto/aula-01.mp4",
  "transcricao": "trabalho/aula-01.transcricao.json",
  "assunto": "Resumo em 1-2 frases do que o vídeo trata",
  "status": "aguardando_aprovacao",
  "duracao_original": 754.2,
  "duracao_estimada_final": 642.0,
  "cortes": [
    {"id": "C1", "inicio": 12.40, "fim": 15.10, "tipo": "pausa|repeticao|retomada|vicio|fora_do_assunto",
     "descricao": "Pausa de 2,7 s antes de 'vamos começar'", "confianca": "alta|media|baixa"}
  ],
  "elementos": [
    {"id": "E1", "tipo": "letreiro|grafico|lista|zoom", "inicio": 20.00, "fim": 24.50,
     "descricao": "Letreiro com o título 'O que é HyperFrames'",
     "conteudo": "texto, itens da lista ou dados do gráfico",
     "motivo": "Início da primeira seção"}
  ],
  "observacoes": ["Dúvidas ou sugestões para o editor"]
}
```

## 5. Mostre e peça aprovação (sempre)

Mostre no chat, em linguagem simples:
1. Assunto entendido e duração original → estimada.
2. Tabela de cortes: id, de–até (mm:ss), tipo, o que é dito/acontece, confiança.
3. Tabela de elementos: id, de–até, tipo, descrição.
4. Observações e dúvidas.

Termine perguntando: aprova tudo, quer mudar algum item (pelo id), ou remover/adicionar algo? Aplique as mudanças no plano.json e mostre de novo o que mudou. Só quando ele aprovar explicitamente, troque `status` para `"aprovado"` — e só então siga para cortar/montar (por exemplo com FFmpeg e as skills HyperFrames), salvando o resultado em `final/`.
