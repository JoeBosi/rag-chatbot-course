#!/usr/bin/env python3
"""Prova tutte le chiavi che trova in .env e dice quanta quota resta.

    python moduli/02-chiavi-gateway-e-quote/starter/controlla_chiavi.py

Per ogni fornitore fa UNA chiamata minuscola (meno di 20 token) e legge
gli header della risposta. Le chiavi assenti le salta.

E' lo script da rilanciare ogni volta che "non funziona piu' niente":
nove volte su dieci e' una quota finita, non il tuo codice.
"""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

RADICE = Path(__file__).resolve().parents[3]
load_dotenv(RADICE / ".env")

# nome, indirizzo, variabile con la chiave, modello da provare
FORNITORI = [
    ("Groq", "https://api.groq.com/openai/v1", "GROQ_API_KEY",
     "openai/gpt-oss-20b"),
    ("Google AI Studio", "https://generativelanguage.googleapis.com/v1beta/openai",
     "GEMINI_API_KEY", "gemini-3.5-flash"),
    ("OpenRouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
     "meta-llama/llama-3.3-70b-instruct:free"),
    ("Mistral", "https://api.mistral.ai/v1", "MISTRAL_API_KEY",
     "mistral-small-latest"),
]

# Gli header di quota non hanno un nome standard: ogni fornitore usa i
# suoi. Questi sono quelli che incontrerai piu' spesso.
HEADER_QUOTA = [
    "x-ratelimit-remaining-requests",
    "x-ratelimit-remaining-tokens",
    "x-ratelimit-reset-requests",
    "x-ratelimit-reset-tokens",
    "retry-after",
]


def prova(nome, indirizzo, variabile, modello):
    chiave = os.getenv(variabile, "").strip()
    if not chiave:
        print(f"  {nome:<20} chiave assente, saltato")
        return

    try:
        risposta = httpx.post(
            f"{indirizzo}/chat/completions",
            headers={"Authorization": f"Bearer {chiave}",
                     "Content-Type": "application/json"},
            json={"model": modello,
                  "messages": [{"role": "user", "content": "di': ok"}],
                  "max_tokens": 5, "temperature": 0},
            timeout=45,
        )
    except httpx.HTTPError as errore:
        print(f"  {nome:<20} NON RAGGIUNGIBILE ({type(errore).__name__})")
        return

    if risposta.status_code == 200:
        print(f"  {nome:<20} OK  modello {modello}")
    elif risposta.status_code == 401:
        print(f"  {nome:<20} CHIAVE RIFIUTATA (401): rigenerala")
    elif risposta.status_code == 429:
        print(f"  {nome:<20} QUOTA ESAURITA (429)")
    elif risposta.status_code == 404:
        print(f"  {nome:<20} modello {modello} non disponibile (404)")
    else:
        messaggio = risposta.text[:110].replace("\n", " ")
        print(f"  {nome:<20} errore {risposta.status_code}: {messaggio}")

    quota = {chiave_header: valore for chiave_header, valore in risposta.headers.items()
             if chiave_header.lower() in HEADER_QUOTA}
    for chiave_header, valore in sorted(quota.items()):
        print(f"       {chiave_header}: {valore}")
    if not quota:
        print("       (questo fornitore non dichiara la quota negli header)")


def main():
    print(f"Chiavi lette da {RADICE / '.env'}\n")
    for fornitore in FORNITORI:
        prova(*fornitore)
    print("\nSe sono tutte 'chiave assente': hai copiato .env.example in .env?")


if __name__ == "__main__":
    main()
