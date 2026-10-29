#!/usr/bin/env python3
"""Misura i tre modi di cercare sullo stesso insieme di domande.

    python moduli/03-testo-cercabile/starter/confronta.py

Non ti chiede di crederci: conta quante domande ciascun metodo azzecca e
ti fa vedere quali sbaglia. E' completo, non c'e' niente da scrivere:
serve a decidere sui numeri invece che sulle impressioni.
"""

import sys
from pathlib import Path

import yaml

RADICE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RADICE / "memoria"))

from ibrida import fondi              # noqa: E402
from lessicale import Bm25            # noqa: E402
from pezzi import carica_pezzi        # noqa: E402
from semantica import Semantica       # noqa: E402

DOMANDE = Path(__file__).resolve().parents[1] / "domande-ricerca.yaml"
POSIZIONI = (1, 3, 5)      # "azzeccata" = il documento giusto sta nei primi N
QUANTI_RECUPERO = 8        # quanti risultati chiede ogni metodo


def azzecca(risultati, atteso, quanti):
    return any(risultato["nome"] == atteso for risultato in risultati[:quanti])


def main():
    domande = yaml.safe_load(DOMANDE.read_text(encoding="utf-8"))
    pezzi = carica_pezzi(per_titoli=True)
    print(f"{len(pezzi)} pezzi da {len(set(p['nome'] for p in pezzi))} documenti")
    print("carico il modello di embedding (la prima volta lo scarica)...\n")

    lessicale = Bm25(pezzi)
    semantica = Semantica(pezzi)

    metodi = ["BM25", "semantica", "ibrida"]
    esiti = []
    for voce in domande:
        per_parole = lessicale.cerca(voce["domanda"], quanti=QUANTI_RECUPERO)
        per_significato = semantica.cerca(voce["domanda"], quanti=QUANTI_RECUPERO)
        insieme = fondi([per_parole, per_significato], quanti=QUANTI_RECUPERO)
        esiti.append({
            "domanda": voce["domanda"],
            "atteso": voce["atteso"],
            "BM25": per_parole,
            "semantica": per_significato,
            "ibrida": insieme,
        })

    # --- chi sbaglia cosa, guardando i primi 3 ---
    larghezza = max(len(e["domanda"]) for e in esiti)
    print(f"{'domanda (primi 3 risultati)':<{larghezza}}  BM25  sem.  ibr.")
    print("-" * (larghezza + 20))
    for esito in esiti:
        segni = "  ".join(
            " si " if azzecca(esito[metodo], esito["atteso"], 3) else " NO "
            for metodo in metodi)
        print(f"{esito['domanda']:<{larghezza}}  {segni}")
    print("-" * (larghezza + 20))

    # --- il conto, a diverse profondita' ---
    totale = len(esiti)
    print(f"\n{'metodo':<12}" + "".join(f"  primi {n}" for n in POSIZIONI))
    for metodo in metodi:
        riga = f"{metodo:<12}"
        for quanti in POSIZIONI:
            giuste = sum(azzecca(e[metodo], e["atteso"], quanti) for e in esiti)
            riga += f"  {giuste:>2}/{totale} "
        print(riga)

    # --- il tetto massimo: quante ne prenderebbe una fusione perfetta ---
    riga = f"{'-- unione':<12}"
    for quanti in POSIZIONI:
        giuste = sum(azzecca(e["BM25"], e["atteso"], quanti)
                     or azzecca(e["semantica"], e["atteso"], quanti)
                     for e in esiti)
        riga += f"  {giuste:>2}/{totale} "
    print(riga)
    print("\n'unione' e' quante ne prenderebbe una fusione perfetta, cioe' il")
    print("massimo a cui l'ibrida puo' ambire. La distanza fra 'ibrida' e")
    print("'unione' e' quanto ti costa il modo in cui fondi le classifiche.")


if __name__ == "__main__":
    main()
