#!/usr/bin/env python3
"""L'unico punto del programma da cui si parla con un modello.

Tutto il resto del corso importa `chiedi` da qui. Quando nel modulo 2
metterai davanti un gateway, cambierai questo file e basta: nessun altro
pezzo del sistema se ne accorgera'.
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

RADICE = Path(__file__).resolve().parents[1]
load_dotenv(RADICE / ".env")

# indirizzo compatibile OpenAI, nome della variabile con la chiave, modello
FORNITORI = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-120b"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/",
               "GEMINI_API_KEY", "gemini-3.5-flash"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
                   "meta-llama/llama-3.3-70b-instruct:free"),
    "ollama": ("http://localhost:11434/v1", None, "qwen3:4b-instruct"),
    "custom": (None, "LLM_API_KEY", None),
}


def apri_collegamento():
    fornitore = os.getenv("LLM_PROVIDER", "groq").lower()
    if fornitore not in FORNITORI:
        sys.exit(f"LLM_PROVIDER='{fornitore}' sconosciuto. "
                 f"Ammessi: {', '.join(FORNITORI)}")
    indirizzo, nome_chiave, modello_default = FORNITORI[fornitore]
    indirizzo = os.getenv("LLM_ENDPOINT") or indirizzo
    modello = os.getenv("LLM_MODEL") or modello_default
    # Con il gateway, nel .env il modello si scrive "openai/memoria-veloce":
    # quel "openai/" serve a cognee, che passa per la libreria litellm e
    # lo usa per capire che deve parlare con un indirizzo compatibile
    # OpenAI, poi lo toglie. Qui invece parliamo col gateway direttamente,
    # e il gateway conosce solo "memoria-veloce": il prefisso va tolto.
    if fornitore == "custom" and modello and modello.startswith("openai/"):
        modello = modello.removeprefix("openai/")
    chiave = os.getenv(nome_chiave, "") if nome_chiave else "ollama"
    if not indirizzo:
        sys.exit("Con LLM_PROVIDER=custom serve anche LLM_ENDPOINT in .env")
    if not chiave:
        sys.exit(f"Manca {nome_chiave} in .env. Vedi CHIAVI.md.")
    return OpenAI(base_url=indirizzo, api_key=chiave, timeout=120), modello


def chiedi(domanda: str, sistema: str | None = None, temperatura: float = 0.0) -> str:
    """Manda una domanda al modello e restituisce il testo della risposta."""
    client, modello = apri_collegamento()
    messaggi = []
    if sistema:
        messaggi.append({"role": "system", "content": sistema})
    messaggi.append({"role": "user", "content": domanda})
    risposta = client.chat.completions.create(
        model=modello, messages=messaggi, temperature=temperatura,
    )
    return (risposta.choices[0].message.content or "").strip()


if __name__ == "__main__":
    print(chiedi("Rispondi solo con la parola: pronto"))
