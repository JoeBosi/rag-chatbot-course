#!/usr/bin/env python3
"""STARTER — Manutenzione dell'archivio: aggiungere, elencare, dimenticare, salvare.

    python memoria/manutenzione.py aggiungi dati/nota-nuova.md
    python memoria/manutenzione.py elenca
    python memoria/manutenzione.py dimentica <data_id>
    python memoria/manutenzione.py relazione
    python memoria/manutenzione.py salva dati/backup

Sono le operazioni che servono dopo, quando l'archivio e' gia' in piedi
e va tenuto in vita.
"""

import asyncio
import shutil
import sys
from pathlib import Path

from dotenv import load_dotenv


def trova_radice() -> Path:
    for candidata in Path(__file__).resolve().parents:
        if (candidata / "progetto-finale" / "corpus").is_dir():
            return candidata
    raise SystemExit("lancia il comando dalla cartella del corso")


RADICE = trova_radice()
DATI = RADICE / "dati" / "cognee"
ARCHIVIO = "officina"

load_dotenv(RADICE / ".env")

import cognee                                          # noqa: E402

cognee.config.system_root_directory(str(DATI / "sistema"))
cognee.config.data_root_directory(str(DATI / "documenti"))


# --- TODO 1 ----------------------------------------------------------
async def aggiungi(percorso: str) -> None:
    """Versa un documento nuovo e ridigerisce SOLO quello.

    cognify e' incrementale: riconosce dall'impronta i documenti gia'
    digeriti e li salta. Costa la quota del documento nuovo, non quella
    di tutto l'archivio.
    """
    file = Path(percorso).resolve()
    if not file.is_file():
        raise SystemExit(f"non trovo {file}")

    # TODO 1: due righe.
    #   await cognee.add(str(file), dataset_name=ARCHIVIO)
    #   await cognee.cognify(datasets=[ARCHIVIO])
    # Poi cronometra e confronta col digerisci completo del modulo 5.
    raise NotImplementedError("TODO 1")


# --- TODO 2 ----------------------------------------------------------
async def elenca() -> None:
    """Cosa c'e' dentro, con gli identificativi che servono per cancellare."""
    # TODO 2: scorri gli archivi e i loro documenti, stampa id e nome.
    #   archivi = await cognee.datasets.list_datasets()
    #   documenti = await cognee.datasets.list_data(dataset_id=archivio.id)
    # Gli identificativi che stampi qui servono nell'esercizio 5.
    raise NotImplementedError("TODO 2")


# --- TODO 3 ----------------------------------------------------------
async def dimentica(data_id: str, duro: bool = False) -> None:
    """Toglie un documento.

    mode="soft" lascia in piedi le entita' che altri documenti
    condividono. E' il predefinito ed e' quasi sempre quello giusto:
    con "hard" rischi di portarti via il nodo "Caldaia Termovex TX-24"
    che serviva anche alle altre cinque note.
    """
    # TODO 3: trova l'archivio che contiene data_id e cancellalo con
    #   await cognee.datasets.delete_data(dataset_id=..., data_id=...,
    #                                     mode="soft")
    # Attenzione a mode="hard": porta via anche i nodi rimasti orfani,
    # e alcuni di quei nodi li usavano altri documenti.
    raise NotImplementedError("TODO 3")


# --- TODO 4 ----------------------------------------------------------
async def relazione() -> None:
    """Le due diagnosi: coerenza fra grafo e vettori, e nodi-mozzo."""
    destinazione = RADICE / "dati" / "relazione.md"
    destinazione.parent.mkdir(parents=True, exist_ok=True)

    # TODO 4: due chiamate.
    #   await cognee.validate(dataset=ARCHIVIO)
    #   await cognee.report(datasets=ARCHIVIO, output_path=str(destinazione))
    raise NotImplementedError("TODO 4")


# --- TODO 5 ----------------------------------------------------------
async def salva(cartella: str) -> None:
    """Il backup: tre pezzi, non uno.

    1. il grafo, in formato cogx (ripristinabile) e json (leggibile)
    2. i documenti originali
    3. il registro (con PostgreSQL: pg_dump, vedi LAB.md)
    """
    destinazione = Path(cartella).resolve()
    destinazione.mkdir(parents=True, exist_ok=True)

    # TODO 5: tre pezzi, non uno.
    #   1. await cognee.export(dataset=ARCHIVIO, format="cogx",
    #                          destination=str(destinazione / "archivio"))
    #   2. copia DATI / "documenti" con shutil.copytree
    #   3. il registro: stampa il comando pg_dump (vedi LAB.md)
    raise NotImplementedError("TODO 5")


COMANDI = {
    "aggiungi": aggiungi,
    "elenca": elenca,
    "dimentica": dimentica,
    "relazione": relazione,
    "salva": salva,
}


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] not in COMANDI:
        raise SystemExit(f"comandi: {' | '.join(COMANDI)}")

    comando = sys.argv[1]
    argomenti = [a for a in sys.argv[2:] if not a.startswith("--")]

    if comando == "dimentica":
        if not argomenti:
            raise SystemExit("serve l'identificativo: vedi 'elenca'")
        asyncio.run(dimentica(argomenti[0], duro="--hard" in sys.argv))
    elif comando in ("aggiungi", "salva"):
        if not argomenti:
            raise SystemExit(f"'{comando}' vuole un percorso")
        asyncio.run(COMANDI[comando](argomenti[0]))
    else:
        asyncio.run(COMANDI[comando]())


if __name__ == "__main__":
    main()
