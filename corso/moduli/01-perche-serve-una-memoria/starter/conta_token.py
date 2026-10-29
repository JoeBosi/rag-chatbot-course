#!/usr/bin/env python3
"""Quanti token occupano questi file? E quanta quota consumano?

    python moduli/01-perche-serve-una-memoria/starter/conta_token.py file1 file2 ...

Il conteggio e' una stima: ogni fornitore ha il suo modo di spezzare il
testo in token. La regola pratica che useremo in tutto il corso e'
**1 token ogni 4 caratteri** per l'italiano, che sbaglia di poco (dal 5
al 15 per cento) e non richiede di installare niente.
"""

import sys
from pathlib import Path

# Piano gratuito di Groq, verificato il 20/09/2026.
# Fonte: https://console.groq.com/docs/rate-limits
TOKEN_AL_MINUTO = 8000
TOKEN_AL_GIORNO = 200000


def stima_token(testo: str) -> int:
    return max(1, round(len(testo) / 4))


def main():
    percorsi = [Path(p) for p in sys.argv[1:]]
    if not percorsi:
        sys.exit("Uso: conta_token.py FILE [FILE ...]")

    totale = 0
    print(f"{'file':<40} {'caratteri':>10} {'token (stima)':>14}")
    print("-" * 66)
    for percorso in percorsi:
        if not percorso.exists():
            print(f"{percorso.name:<40} {'non trovato':>25}")
            continue
        testo = percorso.read_text(encoding="utf-8", errors="ignore")
        token = stima_token(testo)
        totale += token
        print(f"{percorso.name:<40} {len(testo):>10} {token:>14}")

    print("-" * 66)
    print(f"{'TOTALE':<40} {'':>10} {totale:>14}\n")
    print(f"Quota Groq gratuita: {TOKEN_AL_MINUTO} token/minuto, "
          f"{TOKEN_AL_GIORNO} token/giorno.")
    print(f"Mandare tutto questo in un prompt solo consuma il "
          f"{totale / TOKEN_AL_MINUTO:.0%} della quota di un minuto")
    print(f"e ti concede {TOKEN_AL_GIORNO // max(totale, 1)} domande al giorno.")
    if totale > TOKEN_AL_MINUTO:
        print("\n>>> Non ci sta. Ecco perche' serve cercare prima di chiedere.")


if __name__ == "__main__":
    main()
