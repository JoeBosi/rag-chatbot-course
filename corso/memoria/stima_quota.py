#!/usr/bin/env python3
"""Quanto costa, in quota, digerire questi documenti? Versione completa.

    python moduli/02-chiavi-gateway-e-quote/starter/stima_quota.py \
        progetto-finale/corpus/manuali/*.md progetto-finale/corpus/note/*.md

Serve a rispondere alla domanda giusta PRIMA di lanciare un comando
lungo: "quante chiamate fara', quanti token, e quanto dovro' aspettare?"
"""

import sys
from pathlib import Path

# --- piano gratuito di Groq, verificato il 20/09/2026 -------------------
# https://console.groq.com/docs/rate-limits
RICHIESTE_AL_MINUTO = 30
TOKEN_AL_MINUTO = 8000
RICHIESTE_AL_GIORNO = 1000

# --- come cognee digerisce un documento (modulo 5) ---------------------
# Il testo viene spezzato in pezzi, e per ogni pezzo il modello viene
# chiamato due volte: una per estrarre entita' e relazioni, una per
# riassumere.
CARATTERI_PER_PEZZO = 1000
CHIAMATE_PER_PEZZO = 2
# La risposta occupa spazio quanto la domanda, all'incirca.
FATTORE_RISPOSTA = 1.0

CARATTERI_PER_TOKEN = 4


def stima_token(testo: str) -> int:
    return max(1, round(len(testo) / CARATTERI_PER_TOKEN))


def pezzi(testo: str) -> int:
    """Quanti pezzi esce da questo testo."""
    return max(1, -(-len(testo) // CARATTERI_PER_PEZZO))   # divisione per eccesso


def stima(percorsi: list[Path]) -> dict:
    """Restituisce un dizionario con la stima.

    Il conto e' questo, e vale per qualunque pipeline che passi il testo
    a un modello: quanti pezzi, per quante chiamate a pezzo, per quanti
    token a chiamata. Il tempo minimo non e' la somma dei due limiti: e'
    il piu' grande dei due, perche' scattano in parallelo.
    """
    caratteri = 0
    totale_pezzi = 0
    documenti = 0

    for percorso in percorsi:
        testo = percorso.read_text(encoding="utf-8", errors="ignore")
        documenti += 1
        caratteri += len(testo)
        totale_pezzi += pezzi(testo)

    chiamate = totale_pezzi * CHIAMATE_PER_PEZZO
    # Ogni pezzo viene mandato CHIAMATE_PER_PEZZO volte, e ogni volta
    # torna indietro una risposta che occupa spazio anche lei.
    token = round(caratteri / CARATTERI_PER_TOKEN
                  * CHIAMATE_PER_PEZZO * (1 + FATTORE_RISPOSTA))

    minuti_per_token = token / TOKEN_AL_MINUTO
    minuti_per_chiamate = chiamate / RICHIESTE_AL_MINUTO

    return {
        "documenti": documenti,
        "caratteri": caratteri,
        "pezzi": totale_pezzi,
        "chiamate": chiamate,
        "token": token,
        "minuti_per_token": minuti_per_token,
        "minuti_per_chiamate": minuti_per_chiamate,
        "minuti": max(minuti_per_token, minuti_per_chiamate),
    }


def main():
    percorsi = [Path(p) for p in sys.argv[1:] if Path(p).is_file()]
    if not percorsi:
        sys.exit("Uso: stima_quota.py FILE [FILE ...]")

    risultato = stima(percorsi)

    print(f"documenti            {risultato['documenti']:>10}")
    print(f"caratteri            {risultato['caratteri']:>10}")
    print(f"pezzi da {CARATTERI_PER_PEZZO} caratteri {risultato['pezzi']:>10}")
    print(f"chiamate al modello  {risultato['chiamate']:>10}")
    print(f"token (stima)        {risultato['token']:>10}")
    print()
    print(f"limite token:    {risultato['minuti_per_token']:.1f} minuti")
    print(f"limite chiamate: {risultato['minuti_per_chiamate']:.1f} minuti")
    print(f"=> tempo minimo: {risultato['minuti']:.1f} minuti "
          f"(comanda il limite piu' stretto)")

    if risultato["chiamate"] > RICHIESTE_AL_GIORNO:
        print(f"\n>>> ATTENZIONE: {risultato['chiamate']} chiamate superano le "
              f"{RICHIESTE_AL_GIORNO} al giorno del piano gratuito.")
        print("    Digerisci il materiale a pezzi, in giorni diversi,")
        print("    oppure aggiungi una riserva al gateway.")


if __name__ == "__main__":
    main()
