#!/usr/bin/env python3
"""Il RAG piu' stupido che funziona. Da completare: cerca i TODO.

Uso, quando l'avrai finito:

    python memoria/memoria_minima.py "Cosa significa l'errore E4?"

Cosa deve fare, in ordine:
  1. leggere tutti i documenti del corpus (manuali .md + note .md);
  2. dare un punteggio a ogni documento in base a quante parole della
     domanda contiene;
  3. mettere i 3 migliori nel prompt e farci rispondere il modello.
"""

import sys
from pathlib import Path

# La cartella del repository: questo file sta in memoria/, quindi la
# radice e' il genitore.
RADICE = Path(__file__).resolve().parents[1]
CORPUS = RADICE / "progetto-finale" / "corpus"

# Cosi' funziona sia lanciandolo a mano sia quando lo importa verifica.py.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm import chiedi                  # noqa: E402

# Parole cosi' comuni da non dire niente su nessun documento.
# Nel modulo 3 scoprirai che questo elenco fatto a mano ha un nome e una
# alternativa calcolata: IDF.
PAROLE_VUOTE = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da",
    "in", "con", "su", "per", "tra", "fra", "e", "o", "ma", "che", "chi",
    "cosa", "come", "quando", "dove", "perche", "quale", "quali", "quanto",
    "quanta", "quanti", "quante", "del", "della", "dei", "delle", "dello",
    "degli", "al", "allo", "alla", "ai", "agli", "alle", "dal", "dalla",
    "nel", "nella", "nei", "sul", "sulla", "si", "non", "piu", "mi", "ho",
    "ha", "hai", "sono", "e'", "essere", "fare", "va", "vanno", "devo",
}


def normalizza(testo: str) -> list[str]:
    """Testo -> elenco di parole minuscole, senza punteggiatura."""
    pulito = "".join(carattere.lower() if carattere.isalnum() else " "
                     for carattere in testo)
    return [parola for parola in pulito.split()
            if parola not in PAROLE_VUOTE and len(parola) > 1]


def carica_documenti() -> list[dict]:
    """Legge il corpus. Ogni documento e' {"nome": ..., "testo": ...}."""
    documenti = []
    for percorso in sorted(CORPUS.rglob("*.md")):
        if percorso.name == "LEGGIMI.md":
            continue
        documenti.append({
            "nome": str(percorso.relative_to(CORPUS)),
            "testo": percorso.read_text(encoding="utf-8"),
        })
    return documenti


def cerca(domanda: str, documenti: list[dict], quanti: int = 3) -> list[dict]:
    """I `quanti` documenti che contengono piu' parole della domanda.

    TODO 1 --------------------------------------------------------------
    - normalizza la domanda con normalizza()
    - per ogni documento, normalizza il testo e conta quante parole della
      domanda ci compaiono (suggerimento: un `set` rende il conto veloce)
    - scarta i documenti con punteggio 0
    - ordina dal punteggio piu' alto e restituisci i primi `quanti`
    Ogni documento restituito deve avere anche la chiave "punteggio".
    ---------------------------------------------------------------------
    """
    raise NotImplementedError("TODO 1: scrivi cerca()")


def costruisci_contesto(trovati: list[dict]) -> str:
    """Impacchetta i documenti trovati in un unico blocco di testo.

    TODO 2 --------------------------------------------------------------
    Restituisci una stringa fatta cosi', un blocco per documento:

        [documento: note/2026-03-12-caldaia-e4.md]
        ...testo intero...

    Separa i blocchi con una riga vuota. Il nome del file serve: e' quello
    che permette allo studente (e a te) di verificare da dove arriva la
    risposta.
    ---------------------------------------------------------------------
    """
    raise NotImplementedError("TODO 2: scrivi costruisci_contesto()")


def rispondi(domanda: str, mostra_fonti: bool = True) -> str:
    documenti = carica_documenti()
    trovati = cerca(domanda, documenti)

    if not trovati:
        return "Non lo so: nel corpus non c'e' niente che riguardi la domanda."

    if mostra_fonti:
        print("[documenti usati]")
        for documento in trovati:
            print(f"  {documento['punteggio']:>3} punti  {documento['nome']}")
        print()

    sistema = (
        "Rispondi alla domanda usando SOLO i documenti qui sotto.\n"
        "Se la risposta non c'e', scrivi esattamente: non lo so.\n"
        "Cita i valori numerici come sono scritti e di' da quale documento "
        "viene ogni informazione.\n\n" + costruisci_contesto(trovati)
    )
    return chiedi(domanda, sistema=sistema)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Uso: python memoria/memoria_minima.py "la tua domanda"')
    print(rispondi(" ".join(sys.argv[1:])))
