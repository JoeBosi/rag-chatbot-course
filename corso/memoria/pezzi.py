#!/usr/bin/env python3
"""Spezza i documenti in pezzi cercabili. Versione completa.

    python memoria/pezzi.py progetto-finale/corpus/manuali/termovex-tx24.md

Due modi di spezzare:
  spezza_alla_cieca()   ogni N caratteri, senza guardare cosa c'e' dentro
  spezza_per_titoli()   seguendo i titoli del documento
Il laboratorio ti fa vedere la differenza su una tabella di codici errore.
"""

import sys
from pathlib import Path

def trova_radice() -> Path:
    """Risale le cartelle finche' trova quella del repository.

    Serve perche' questo file gira sia da memoria/ sia da
    moduli/NN/soluzione/, e il corpus va trovato in tutti e due i casi.
    """
    cartella = Path(__file__).resolve()
    for candidata in cartella.parents:
        if (candidata / "progetto-finale" / "corpus").is_dir():
            return candidata
    raise SystemExit("non trovo la radice del repository: lancia i comandi "
                     "dalla cartella del corso")


RADICE = trova_radice()
CORPUS = RADICE / "progetto-finale" / "corpus"

MISURA_PEZZO = 800          # caratteri
SOVRAPPOSIZIONE = 120       # caratteri ripetuti fra un pezzo e il successivo


def spezza_alla_cieca(testo: str, misura: int = MISURA_PEZZO,
                      sovrapposizione: int = SOVRAPPOSIZIONE) -> list[str]:
    """Taglia ogni `misura` caratteri, ripetendone `sovrapposizione`.

    E' il metodo piu' semplice e il piu' sbagliato: non sa cosa sta
    tagliando. La sovrapposizione serve a limitare i danni, non a
    evitarli: una tabella lunga viene spezzata lo stesso.
    """
    if misura <= sovrapposizione:
        raise ValueError("la sovrapposizione deve essere minore del pezzo")
    passo = misura - sovrapposizione
    pezzi = [testo[inizio:inizio + misura]
             for inizio in range(0, len(testo), passo)]
    return [pezzo for pezzo in pezzi if pezzo.strip()]


def spezza_per_titoli(testo: str, misura_massima: int = 1800) -> list[str]:
    """Taglia sui titoli Markdown: un pezzo per sezione.

    Costa cinque righe in piu' della versione cieca e cambia tutto: la
    tabella dei codici di errore resta intera, perche' sta dentro una
    sezione sola. La struttura che l'autore ha messo nel documento e'
    un'informazione: buttarla via e' uno spreco.
    """
    sezioni, corrente = [], []
    for riga in testo.splitlines():
        if riga.startswith("#") and corrente:
            sezioni.append("\n".join(corrente))
            corrente = [riga]
        else:
            corrente.append(riga)
    if corrente:
        sezioni.append("\n".join(corrente))

    pezzi = []
    for sezione in sezioni:
        if not sezione.strip():
            continue
        if len(sezione) > misura_massima:
            # Una sezione enorme resta ingestibile: la si taglia lo stesso,
            # ma e' un caso raro invece che la regola.
            pezzi.extend(spezza_alla_cieca(sezione))
        else:
            pezzi.append(sezione)
    return pezzi


def carica_pezzi(per_titoli: bool = True) -> list[dict]:
    """Tutto il corpus, gia' spezzato.

    Ogni pezzo e' {"id": ..., "nome": ..., "testo": ...}.
    L'id serve a ritrovare lo stesso pezzo con metodi di ricerca diversi.
    """
    pezzi = []
    for percorso in sorted(CORPUS.rglob("*.md")):
        if percorso.name == "LEGGIMI.md":
            continue
        testo = percorso.read_text(encoding="utf-8")
        nome = str(percorso.relative_to(CORPUS))
        frammenti = spezza_per_titoli(testo) if per_titoli else spezza_alla_cieca(testo)
        for numero, frammento in enumerate(frammenti):
            pezzi.append({"id": f"{nome}#{numero}", "nome": nome, "testo": frammento})
    return pezzi


if __name__ == "__main__":
    if len(sys.argv) > 1:
        testo = Path(sys.argv[1]).read_text(encoding="utf-8")
        modo = "--cieco" not in sys.argv
        frammenti = spezza_per_titoli(testo) if modo else spezza_alla_cieca(testo)
        print(f"{len(frammenti)} pezzi "
              f"({'per titoli' if modo else 'alla cieca'})\n")
        for numero, frammento in enumerate(frammenti):
            print(f"--- pezzo {numero} ({len(frammento)} caratteri) ---")
            print(frammento[:200].strip().replace("\n", " ") + " ...")
            print()
    else:
        pezzi = carica_pezzi()
        print(f"{len(pezzi)} pezzi da {len(set(p['nome'] for p in pezzi))} documenti")
