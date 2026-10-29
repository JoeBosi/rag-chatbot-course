#!/usr/bin/env python3
"""Verifica del laboratorio 1. Si lancia dalla radice del repository:

    python moduli/01-perche-serve-una-memoria/verifica.py

Fa due chiamate vere al modello: consuma pochissima quota.
"""

import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "memoria"))

errori = []


def controlla(descrizione, condizione, aiuto=""):
    stato = "OK  " if condizione else "NO  "
    print(f"{stato}{descrizione}")
    if not condizione:
        errori.append(f"{descrizione}\n      -> {aiuto}" if aiuto else descrizione)
    return condizione


print("== ambiente ==")
controlla("Python 3.11 o 3.12",
          sys.version_info[:2] in [(3, 11), (3, 12)],
          f"hai {sys.version_info.major}.{sys.version_info.minor}: vedi SETUP.md")

try:
    import openai, dotenv  # noqa: F401
    librerie = True
except ImportError as errore:
    librerie = False
controlla("librerie installate", librerie,
          "attiva l'ambiente: source .venv/bin/activate && pip install -r requirements.txt")

env = RADICE / ".env"
controlla(".env esiste", env.exists(), "cp .env.example .env, poi riempilo (CHIAVI.md)")

if env.exists():
    from dotenv import load_dotenv
    import os
    load_dotenv(env)
    fornitore = os.getenv("LLM_PROVIDER", "groq")
    if fornitore == "groq":
        controlla("GROQ_API_KEY presente", bool(os.getenv("GROQ_API_KEY")),
                  "prendila su https://console.groq.com/keys (CHIAVI.md)")
    else:
        controlla(f"LLM_PROVIDER = {fornitore}", True)

print("\n== il tuo codice ==")
controlla("memoria/llm.py esiste", (RADICE / "memoria" / "llm.py").exists(),
          "cp moduli/01-perche-serve-una-memoria/starter/llm.py memoria/")
controlla("memoria/memoria_minima.py esiste",
          (RADICE / "memoria" / "memoria_minima.py").exists(),
          "cp moduli/01-perche-serve-una-memoria/starter/memoria_minima.py memoria/")

if errori:
    print("\n" + "=" * 60)
    print("Sistema questi punti, poi rilancia:\n")
    for errore in errori:
        print("  -", errore)
    sys.exit(1)

print("\n== funziona? ==")
try:
    from llm import chiedi
    risposta = chiedi("Rispondi solo con la parola: pronto")
    controlla("il modello risponde", "pront" in risposta.lower(),
              f"ha risposto: {risposta[:80]!r}")
except Exception as errore:
    controlla("il modello risponde", False, str(errore)[:200])

try:
    from memoria_minima import carica_documenti, cerca, costruisci_contesto, rispondi

    documenti = carica_documenti()
    controlla(f"il corpus si legge ({len(documenti)} documenti)", len(documenti) >= 10,
              "controlla che progetto-finale/corpus/ ci sia ancora")

    trovati = cerca("Che candela monta il rasaerba?", documenti)
    controlla("cerca() restituisce qualcosa", bool(trovati), "TODO 1 non fatto?")
    controlla("cerca() mette il punteggio",
              bool(trovati) and "punteggio" in trovati[0],
              "ogni risultato deve avere la chiave 'punteggio'")
    controlla("cerca() trova il manuale del rasaerba",
              any("greencut" in d["nome"] for d in trovati),
              f"ha trovato: {[d['nome'] for d in trovati]}")

    contesto = costruisci_contesto(trovati)
    controlla("costruisci_contesto() cita i nomi dei file",
              "[documento:" in contesto and "greencut" in contesto,
              "ogni blocco deve cominciare con [documento: nome]")

    risposta = rispondi("Che candela monta il rasaerba e con che distanza elettrodi?",
                        mostra_fonti=False)
    controlla("risponde con il dato giusto (BPR6ES)",
              "bpr6es" in risposta.lower(),
              f"ha risposto: {risposta[:150]!r}")
    controlla("risponde con la distanza elettrodi (0,7)",
              "0,7" in risposta or "0.7" in risposta,
              f"ha risposto: {risposta[:150]!r}")
except NotImplementedError as errore:
    controlla("le funzioni del laboratorio sono scritte", False, str(errore))
except Exception as errore:
    controlla("memoria_minima.py gira senza errori", False,
              f"{type(errore).__name__}: {errore}")

print()
if errori:
    print("=" * 60)
    print("Mancano ancora:\n")
    for errore in errori:
        print("  -", errore)
    sys.exit(1)

print("=" * 60)
print("Laboratorio 1 superato. Artefatti: memoria/llm.py, memoria/memoria_minima.py")
print("Prossimo: moduli/02-chiavi-gateway-e-quote/LEZIONE.md")
