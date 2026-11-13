#!/usr/bin/env python3
"""Lista pausas longas e possíveis repetições/retomadas numa transcrição.

Uso: python analisar_pausas.py trabalho/<nome>.transcricao.json [--pausa 1.2]

Imprime JSON com:
  pausas:     silêncios entre palavras maiores que --pausa segundos
  repeticoes: frases vizinhas muito parecidas (a primeira costuma ser o "erro")
  vicios:     ocorrências de "né", "tipo", "éé", "hum" etc. com tempo
É só um ponto de partida: quem decide o corte é a leitura do conteúdo.
"""
import argparse, difflib, json, re

VICIOS = {"né", "tipo", "hum", "hmm", "éé", "ééé", "ahn", "ah", "eh", "é...", "então..."}


def norm(t):
    return re.sub(r"[^\wà-ú ]", "", t.lower()).strip()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("transcricao")
    p.add_argument("--pausa", type=float, default=1.2)
    a = p.parse_args()
    d = json.load(open(a.transcricao, encoding="utf-8"))
    frases = d["frases"]

    palavras = [w for f in frases for w in f.get("palavras", [])]
    pausas = []
    for w1, w2 in zip(palavras, palavras[1:]):
        gap = w2["inicio"] - w1["fim"]
        if gap >= a.pausa:
            pausas.append({"inicio": w1["fim"], "fim": w2["inicio"], "duracao": round(gap, 2),
                           "depois_de": w1["p"], "antes_de": w2["p"]})
    if not palavras:  # sem tempo por palavra: usa intervalo entre frases
        for f1, f2 in zip(frases, frases[1:]):
            gap = f2["inicio"] - f1["fim"]
            if gap >= a.pausa:
                pausas.append({"inicio": f1["fim"], "fim": f2["inicio"], "duracao": round(gap, 2)})

    repeticoes = []
    for i, f1 in enumerate(frases):
        for f2 in frases[i + 1:i + 4]:
            n1, n2 = norm(f1["texto"]), norm(f2["texto"])
            if not n1 or not n2:
                continue
            curto = min(n1, n2, key=len)
            longo = n2 if curto is n1 else n1
            sim = difflib.SequenceMatcher(None, n1, n2).ratio()
            if sim >= 0.6 or (len(curto) > 12 and longo.startswith(curto[: int(len(curto) * .7)])):
                repeticoes.append({"frase_descartavel": f1["id"], "frase_boa": f2["id"],
                                   "inicio": f1["inicio"], "fim": f1["fim"],
                                   "similaridade": round(sim, 2),
                                   "texto_1": f1["texto"], "texto_2": f2["texto"]})

    vicios = [{"palavra": w["p"], "inicio": w["inicio"], "fim": w["fim"]}
              for w in palavras if norm(w["p"]) in VICIOS]

    print(json.dumps({"duracao": d.get("duracao"), "pausas": pausas,
                      "repeticoes": repeticoes, "vicios": vicios},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
