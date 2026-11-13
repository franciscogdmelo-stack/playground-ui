#!/usr/bin/env python3
"""Transcreve um vídeo/áudio com o Whisper (local) em português.

Uso: python transcrever.py <arquivo> [--modelo small] [--saida trabalho]

Gera em <saida>/:
  <nome>.transcricao.json  - frases com início/fim (segundos) e palavras com tempo
  <nome>.transcricao.txt   - texto legível: [00:01:23.4 -> 00:01:27.9] frase
  <nome>.srt               - legenda pronta para o YouTube
"""
import argparse, json, os, sys


def hms(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:04.1f}"


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("arquivo")
    p.add_argument("--modelo", default="small",
                   help="tiny, base, small, medium, large-v3, turbo (maior = melhor e mais lento)")
    p.add_argument("--saida", default="trabalho")
    a = p.parse_args()

    try:
        import whisper
    except ImportError:
        sys.exit("Whisper não encontrado neste Python. Rode com o Python onde ele foi instalado "
                 "(ex.: ~/whisper-env/bin/python) ou instale com: pip install openai-whisper")

    os.makedirs(a.saida, exist_ok=True)
    nome = os.path.splitext(os.path.basename(a.arquivo))[0]
    print(f"Carregando modelo '{a.modelo}'...", flush=True)
    modelo = whisper.load_model(a.modelo)
    print(f"Transcrevendo {a.arquivo} (pode demorar)...", flush=True)
    r = modelo.transcribe(a.arquivo, language="pt", word_timestamps=True,
                          verbose=False, fp16=False)

    frases = []
    for i, s in enumerate(r["segments"], 1):
        frases.append({
            "id": i,
            "inicio": round(s["start"], 2),
            "fim": round(s["end"], 2),
            "texto": s["text"].strip(),
            "palavras": [{"p": w["word"].strip(), "inicio": round(w["start"], 2),
                          "fim": round(w["end"], 2)} for w in s.get("words", [])],
        })
    duracao = frases[-1]["fim"] if frases else 0.0
    dados = {"arquivo": os.path.abspath(a.arquivo), "idioma": "pt", "modelo": a.modelo,
             "duracao": duracao, "frases": frases}

    base = os.path.join(a.saida, nome)
    with open(base + ".transcricao.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    with open(base + ".transcricao.txt", "w", encoding="utf-8") as f:
        for fr in frases:
            f.write(f"[{hms(fr['inicio'])} -> {hms(fr['fim'])}] {fr['texto']}\n")
    with open(base + ".srt", "w", encoding="utf-8") as f:
        for fr in frases:
            f.write(f"{fr['id']}\n{srt_time(fr['inicio'])} --> {srt_time(fr['fim'])}\n{fr['texto']}\n\n")

    print(f"Pronto: {len(frases)} frases, {hms(duracao)} de fala.")
    for ext in (".transcricao.json", ".transcricao.txt", ".srt"):
        print("  " + base + ext)


if __name__ == "__main__":
    main()
