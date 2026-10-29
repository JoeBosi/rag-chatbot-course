#!/usr/bin/env python3
"""La domanda che il sistema del modulo 3 non sa risolvere.

    python moduli/04-dal-recupero-al-grafo/starter/prova_multihop.py

Completo, niente da scrivere: serve a vedere il fallimento prima di
sentirselo spiegare.
"""

import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RADICE / "memoria"))

from ibrida import fondi              # noqa: E402
from lessicale import Bm25            # noqa: E402
from llm import chiedi                # noqa: E402
from pezzi import carica_pezzi        # noqa: E402
from semantica import Semantica       # noqa: E402

DOMANDA = "Quante ore ho passato in tutto sulla caldaia?"

pezzi = carica_pezzi()
lessicale = Bm25(pezzi)
semantica = Semantica(pezzi)

trovati = fondi([lessicale.cerca(DOMANDA, 8), semantica.cerca(DOMANDA, 8)], quanti=5)

print(f"domanda: {DOMANDA}\n")
print("pezzi recuperati:")
for pezzo in trovati:
    print("  ", pezzo["id"])

contesto = "\n\n".join(f"[{p['id']}]\n{p['testo']}" for p in trovati)
print("\nRISPOSTA:")
print(chiedi(DOMANDA,
             sistema="Rispondi usando solo questi documenti. "
                     "Se non puoi, di' che non lo sai.\n\n" + contesto))
print()
print("La risposta giusta sarebbe 3,5 ore: 1,5 il 12 marzo piu' 2 il 30 agosto.")
print("Il numero non e' scritto in nessun documento: va costruito.")
