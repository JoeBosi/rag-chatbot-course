#!/usr/bin/env python3
"""Fa una domanda al modello. Con o senza un documento allegato.

    python moduli/01-perche-serve-una-memoria/starter/chiedi.py "la tua domanda"
    python .../chiedi.py --con-manuale percorso/al/file.md "la tua domanda"

Legge da .env quale fornitore usare (LLM_PROVIDER) e quale modello
(LLM_MODEL). Non c'e' niente di magico: e' una chiamata HTTP.
"""

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# .env sta nella radice del repository, due livelli sopra questo file.
RADICE = Path(__file__).resolve().parents[3]
load_dotenv(RADICE / ".env")

# Ogni fornitore gratuito espone un endpoint "compatibile OpenAI": stessa
# forma di richiesta, stessa forma di risposta. Cambia solo l'indirizzo e
# la chiave. E' quello che rende possibile il gateway del modulo 2.
FORNITORI = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY", "openai/gpt-oss-120b"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai/",
               "GEMINI_API_KEY", "gemini-3.5-flash"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY",
                   "meta-llama/llama-3.3-70b-instruct:free"),
    "ollama": ("http://localhost:11434/v1", None, "qwen3:4b-instruct"),
    "custom": (None, "LLM_API_KEY", None),   # il gateway del modulo 2
}


def apri_collegamento():
    """Restituisce (client, nome_modello) secondo quello che dice .env."""
    fornitore = os.getenv("LLM_PROVIDER", "groq").lower()
    if fornitore not in FORNITORI:
        sys.exit(f"LLM_PROVIDER='{fornitore}' non lo conosco. "
                 f"Valori ammessi: {', '.join(FORNITORI)}")

    indirizzo, nome_chiave, modello_di_default = FORNITORI[fornitore]
    indirizzo = os.getenv("LLM_ENDPOINT") or indirizzo
    modello = os.getenv("LLM_MODEL") or modello_di_default
    chiave = os.getenv(nome_chiave, "") if nome_chiave else "ollama"

    if not indirizzo:
        sys.exit("Con LLM_PROVIDER=custom devi mettere anche LLM_ENDPOINT in .env")
    if not chiave:
        sys.exit(f"Manca {nome_chiave} in .env. Vedi CHIAVI.md.")

    return OpenAI(base_url=indirizzo, api_key=chiave, timeout=120), modello


def chiedi(domanda: str, contesto: str | None = None) -> str:
    client, modello = apri_collegamento()

    if contesto:
        sistema = (
            "Rispondi alla domanda usando SOLO il documento qui sotto. "
            "Se il documento non contiene la risposta, di' che non lo sai. "
            "Cita i valori numerici esattamente come sono scritti.\n\n"
            "--- DOCUMENTO ---\n" + contesto + "\n--- FINE DOCUMENTO ---"
        )
    else:
        sistema = "Rispondi in italiano, in modo conciso e pratico."

    risposta = client.chat.completions.create(
        model=modello,
        messages=[{"role": "system", "content": sistema},
                  {"role": "user", "content": domanda}],
        temperature=0,
    )
    return risposta.choices[0].message.content.strip()


def main():
    parser = argparse.ArgumentParser(description="Una domanda al modello.")
    parser.add_argument("domanda")
    parser.add_argument("--con-manuale", metavar="FILE",
                        help="file di testo da allegare alla domanda")
    argomenti = parser.parse_args()

    contesto = None
    if argomenti.con_manuale:
        percorso = Path(argomenti.con_manuale)
        if not percorso.exists():
            sys.exit(f"File non trovato: {percorso}")
        contesto = percorso.read_text(encoding="utf-8")
        print(f"[allegato {percorso.name}: {len(contesto)} caratteri]\n")

    try:
        print(chiedi(argomenti.domanda, contesto))
    except Exception as errore:
        sys.exit(spiega_errore(errore))


def spiega_errore(errore: Exception) -> str:
    """Traduce gli errori piu' frequenti in qualcosa di azionabile."""
    testo = str(errore)
    if "401" in testo or "invalid_api_key" in testo:
        return "Chiave rifiutata. Controlla GROQ_API_KEY in .env (CHIAVI.md)."
    if "429" in testo:
        return ("Quota esaurita o troppe richieste al minuto. Aspetta un minuto. "
                "Nel modulo 2 impari a non finirci dentro.")
    if "Connection" in testo or "connect" in testo.lower():
        return ("Nessuna risposta dall'indirizzo. Se usi Ollama, e' acceso? "
                "Se usi il gateway del modulo 2, l'hai avviato?")
    return f"Errore: {testo}"


if __name__ == "__main__":
    main()
