#!/usr/bin/env python3
"""Output strutturato: dal testo libero a dati che il programma puo' usare.

    python moduli/02-chiavi-gateway-e-quote/starter/estrai_json.py \
        progetto-finale/corpus/note/2026-08-30-caldaia-manutenzione.md

Chiede al modello di rispondere in una forma decisa da noi (JSON Schema)
invece che in prosa. Passa dal gateway, quindi funziona con qualunque
fornitore ci sia dietro.
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

RADICE = Path(__file__).resolve().parents[3]
load_dotenv(RADICE / ".env")

# La forma esatta che vogliamo indietro. "strict": True dice al fornitore
# di imporla al modello, non di sperarci.
SCHEMA = {
    "type": "object",
    "properties": {
        "apparecchio": {"type": "string",
                        "description": "nome e modello dell'apparecchio"},
        "componente": {"type": "string",
                       "description": "il pezzo su cui si e' intervenuto"},
        "azione": {"type": "string",
                   "description": "cosa e' stato fatto, in poche parole"},
        "data": {"type": "string", "description": "data in formato AAAA-MM-GG"},
        "valori": {
            "type": "array",
            "description": "ogni misura o taratura citata",
            "items": {
                "type": "object",
                "properties": {
                    "grandezza": {"type": "string"},
                    "valore": {"type": "string"},
                },
                "required": ["grandezza", "valore"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["apparecchio", "componente", "azione", "data", "valori"],
    "additionalProperties": False,
}


def estrai(testo: str) -> dict:
    client = OpenAI(
        base_url=os.getenv("LLM_ENDPOINT", "http://localhost:4000/v1"),
        api_key=os.getenv("LLM_API_KEY", os.getenv("GATEWAY_KEY", "sk-memoria-locale")),
        timeout=120,
    )
    risposta = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "memoria-veloce"),
        messages=[
            {"role": "system",
             "content": "Estrai i fatti da questa nota di intervento. "
                        "Non inventare: se un campo non c'e', lascialo vuoto."},
            {"role": "user", "content": testo},
        ],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "intervento", "strict": True,
                                         "schema": SCHEMA}},
        temperature=0,
        max_tokens=1500,
    )
    return json.loads(risposta.choices[0].message.content)


def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: estrai_json.py FILE.md")
    percorso = Path(sys.argv[1])
    if not percorso.exists():
        sys.exit(f"File non trovato: {percorso}")

    try:
        dati = estrai(percorso.read_text(encoding="utf-8"))
    except Exception as errore:
        testo = str(errore)
        if "json_validate_failed" in testo:
            sys.exit("Il modello non e' riuscito a rispettare lo schema.\n"
                     "Non e' colpa tua: prova un modello piu' grande "
                     "(openai/gpt-oss-120b invece di 20b).")
        raise

    print(json.dumps(dati, indent=2, ensure_ascii=False))
    print()
    print("Nota: guarda come sono scritti i numeri. Alcuni modelli")
    print("rispondono '1,4 bar', altri '1.4 bar'. Se il tuo codice cerca")
    print("la stringa esatta, meta' delle volte non la trova.")


if __name__ == "__main__":
    main()
