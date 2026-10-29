#!/usr/bin/env python3
"""Manutenzione dell'archivio: aggiungere, elencare, dimenticare, salvare.

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

    await cognee.add(str(file), dataset_name=ARCHIVIO)
    print(f"aggiunto: {file.name}")

    await cognee.cognify(datasets=[ARCHIVIO])
    print("digerito (solo la parte nuova)")


# --- TODO 2 ----------------------------------------------------------
async def elenca() -> None:
    """Cosa c'e' dentro, con gli identificativi che servono per cancellare."""
    archivi = await cognee.datasets.list_datasets()
    if not archivi:
        print("l'archivio e' vuoto")
        return

    for archivio in archivi:
        print(f"\narchivio: {archivio.name}  [{archivio.id}]")
        documenti = await cognee.datasets.list_data(dataset_id=archivio.id)
        for doc in documenti:
            nome = getattr(doc, "name", "?")
            tipo = getattr(doc, "extension", "") or getattr(doc, "mime_type", "")
            print(f"  {doc.id}  {nome}  ({tipo})")
        print(f"  totale: {len(documenti)} documenti")


# --- TODO 3 ----------------------------------------------------------
async def dimentica(data_id: str, duro: bool = False) -> None:
    """Toglie un documento.

    mode="soft" lascia in piedi le entita' che altri documenti
    condividono. E' il predefinito ed e' quasi sempre quello giusto:
    con "hard" rischi di portarti via il nodo "Caldaia Termovex TX-24"
    che serviva anche alle altre cinque note.
    """
    archivi = await cognee.datasets.list_datasets()
    if not archivi:
        raise SystemExit("l'archivio e' vuoto")

    from uuid import UUID
    bersaglio = UUID(str(data_id))

    for archivio in archivi:
        documenti = await cognee.datasets.list_data(dataset_id=archivio.id)
        if any(doc.id == bersaglio for doc in documenti):
            await cognee.datasets.delete_data(
                dataset_id=archivio.id,
                data_id=bersaglio,
                mode="hard" if duro else "soft",
            )
            print(f"dimenticato {data_id} da {archivio.name}"
                  f" (modo {'hard' if duro else 'soft'})")
            return

    raise SystemExit(f"nessun documento con identificativo {data_id}")


# --- TODO 4 ----------------------------------------------------------
async def relazione() -> None:
    """Le due diagnosi: coerenza fra grafo e vettori, e nodi-mozzo."""
    destinazione = RADICE / "dati" / "relazione.md"
    destinazione.parent.mkdir(parents=True, exist_ok=True)

    esito = await cognee.validate(dataset=ARCHIVIO)
    print("validate:", esito)

    await cognee.report(datasets=ARCHIVIO, output_path=str(destinazione))
    print(f"relazione scritta in {destinazione}")
    print("cerca la sezione dei nodi-mozzo: se in cima trovi 'bar' o "
          "'ore', l'estrazione ha fatto un nodo per un'unita' di misura.")


# --- TODO 5 ----------------------------------------------------------
async def salva(cartella: str) -> None:
    """Il backup: tre pezzi, non uno.

    1. il grafo, in formato cogx (ripristinabile) e json (leggibile)
    2. i documenti originali
    3. il registro (con PostgreSQL: pg_dump, vedi LAB.md)
    """
    destinazione = Path(cartella).resolve()
    destinazione.mkdir(parents=True, exist_ok=True)

    # cogx: l'unico formato che si rimette dentro, con
    # cognee.remember(COGXArchiveSource(percorso)). "json" serve per
    # leggere, non per ripristinare.
    await cognee.export(
        dataset=ARCHIVIO,
        format="cogx",
        destination=str(destinazione / "archivio"),
    )
    print(f"grafo esportato in {destinazione / 'archivio'}")

    await cognee.export(
        dataset=ARCHIVIO,
        format="json",
        destination=str(destinazione / "grafo.json"),
    )
    print(f"copia leggibile in {destinazione / 'grafo.json'}")

    documenti = DATI / "documenti"
    if documenti.is_dir():
        copia = destinazione / "documenti"
        if copia.exists():
            shutil.rmtree(copia)
        shutil.copytree(documenti, copia)
        print(f"documenti copiati in {copia}")

    print("\nManca il registro. Con SQLite e' un file, copialo a programma")
    print("fermo. Con PostgreSQL (modulo 6):")
    print(f"  docker compose exec -T postgres pg_dump -U cognee cognee"
          f" > {destinazione / 'registro.sql'}")
    print("\nUn backup mai ripristinato non e' un backup, e' un file.")


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
