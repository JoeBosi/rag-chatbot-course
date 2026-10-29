#!/usr/bin/env python3
"""Il quaderno di officina, con cognee al posto del codice fatto a mano.

    python memoria/quaderno.py azzera         # butta via tutto e riparte
    python memoria/quaderno.py aggiungi       # ingerisce il corpus intero
    python memoria/quaderno.py aggiungi --ridotto   # solo caldaia e lavatrice
    python memoria/quaderno.py digerisci      # costruisce il grafo (cognify)
    python memoria/quaderno.py arricchisci    # memify
    python memoria/quaderno.py chiedi "..."   # domanda
    python memoria/quaderno.py stato          # cosa c'e' dentro e dove sta

I quattro comandi del mezzo sono le quattro operazioni di cognee, nello
stesso ordine in cui vanno eseguite.
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def trova_radice() -> Path:
    for candidata in Path(__file__).resolve().parents:
        if (candidata / "progetto-finale" / "corpus").is_dir():
            return candidata
    raise SystemExit("lancia il comando dalla cartella del corso")


RADICE = trova_radice()
CORPUS = RADICE / "progetto-finale" / "corpus"
DATI = RADICE / "dati" / "cognee"
ARCHIVIO = "officina"

load_dotenv(RADICE / ".env")

import cognee                                          # noqa: E402
from cognee.modules.search.types.SearchType import SearchType   # noqa: E402

# DOVE cognee scrive. Senza queste due righe scrive dentro la cartella
# della libreria, in .venv: i tuoi dati finirebbero in un posto che
# cancelli con un "pip uninstall". Non farlo mai.
cognee.config.system_root_directory(str(DATI / "sistema"))
cognee.config.data_root_directory(str(DATI / "documenti"))


# I tipi di ricerca che useremo. Ce ne sono venti: questi sono i quattro
# che servono. L'elenco completo e' nella lezione.
TIPI_DI_RICERCA = {
    "grafo": SearchType.GRAPH_COMPLETION,      # risposta usando il grafo
    "testo": SearchType.RAG_COMPLETION,        # risposta usando solo i pezzi
    "misto": SearchType.HYBRID_COMPLETION,     # tutti e due
    "pezzi": SearchType.CHUNKS,                # i pezzi grezzi, senza risposta
}


async def azzera():
    """Cancella dati e memoria: si riparte da zero."""
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    print("archivio svuotato")


async def aggiungi(percorsi: list[Path]):
    """Mette i documenti dentro l'archivio, senza ancora capirli.

    `add` non chiama il modello: copia, riconosce il formato, estrae il
    testo e registra il documento. E' veloce e non consuma quota.
    """
    await cognee.add([str(p) for p in percorsi], dataset_name=ARCHIVIO)
    print(f"{len(percorsi)} documenti aggiunti all'archivio '{ARCHIVIO}'")


async def digerisci():
    """Costruisce il grafo: e' il passaggio lungo e costoso.

    Qui il modello viene chiamato due volte per ogni pezzo di testo. Sul
    corpus del corso sono una quarantina di chiamate: con il piano
    gratuito di Groq, vari minuti, buona parte dei quali ad aspettare che
    il contatore dei token si azzeri.
    """
    print("costruisco il grafo: decine di chiamate al modello, abbi pazienza.")
    print("(con python memoria/stima_quota.py sai in anticipo quanto dura)")
    await cognee.cognify(datasets=[ARCHIVIO])
    print("grafo costruito")


async def arricchisci():
    """Passa sul grafo gia' costruito e lo migliora (memify)."""
    await cognee.memify(dataset=ARCHIVIO)
    print("grafo arricchito")


async def chiedi(domanda: str, tipo: str = "grafo"):
    """Fa una domanda all'archivio."""
    risultati = await cognee.search(
        query_text=domanda,
        query_type=TIPI_DI_RICERCA[tipo],
        datasets=[ARCHIVIO],
    )
    if not risultati:
        print("nessun risultato")
        return
    for risultato in risultati:
        # search restituisce oggetti diversi a seconda del tipo di
        # ricerca: a volte un dizionario con "search_result", a volte
        # direttamente il testo.
        if isinstance(risultato, dict) and "search_result" in risultato:
            for voce in risultato["search_result"]:
                print(voce)
        else:
            print(risultato)


async def stato():
    """Dove stanno i dati e quanto pesano."""
    print(f"archivio:     {ARCHIVIO}")
    print(f"cartella:     {DATI}")
    print(f"modello:      {os.getenv('LLM_MODEL')} "
          f"via {os.getenv('LLM_PROVIDER')}")
    print(f"embedding:    {os.getenv('EMBEDDING_MODEL')} "
          f"({os.getenv('EMBEDDING_PROVIDER')})")
    print(f"grafo:        {os.getenv('GRAPH_DATABASE_PROVIDER', 'kuzu')}")
    print(f"vettori:      {os.getenv('VECTOR_DB_PROVIDER', 'lancedb')}")
    print(f"relazionale:  {os.getenv('DB_PROVIDER', 'sqlite')}")
    print()
    if not DATI.exists():
        print("(la cartella non esiste ancora: non hai ancora aggiunto niente)")
        return
    for cartella in sorted(DATI.rglob("*")):
        if cartella.is_dir() and not any(c.is_dir() for c in cartella.iterdir()):
            peso = sum(f.stat().st_size for f in cartella.rglob("*") if f.is_file())
            print(f"  {cartella.relative_to(DATI)}  {peso / 1024:.0f} KB")


def documenti_del_corpus() -> list[Path]:
    """Il corpus come ti arriva davvero: i manuali in PDF, le note scritte.

    I manuali li ingeriamo in PDF, non nei sorgenti Markdown da cui sono
    stati generati, perche' e' la forma in cui ti arrivano nella vita.
    Uno dei cinque, greencut-rm46.pdf, e' la fotografia di un libretto
    di carta: cognee ci estrae zero caratteri, e da qui in poi quel
    rasaerba nel tuo archivio non c'e'. Non e' un guasto, e' il muro che
    apri nel progetto finale (requisito R1).

    Provalo tu:
        python -c "import pypdf; print(len(pypdf.PdfReader(
            'progetto-finale/corpus/manuali/greencut-rm46.pdf'
            ).pages[0].extract_text()))"
    """
    manuali = sorted((CORPUS / "manuali").glob("*.pdf"))
    note = sorted((CORPUS / "note").glob("*.md"))
    return manuali + note


# Il corpus ridotto del modulo 5: due apparecchi e le loro note.
# Non e' pigrizia, e' aritmetica. Digerire tutti e 12 i documenti costa
# circa 250.000 token, e il piano gratuito Groq ne da' 200.000 AL
# GIORNO: non ci sta, e se ci provi resti senza quota anche per i
# moduli 7 e 8. Vedi la lezione, sezione 6.
RIDOTTO = ("termovex-tx24", "lavanor-wm700", "caldaia", "lavatrice")


def documenti_ridotti() -> list[Path]:
    """Solo caldaia e lavatrice: 2 manuali + 4 note, circa 6 documenti."""
    return [p for p in documenti_del_corpus()
            if any(chiave in p.stem for chiave in RIDOTTO)]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    comando = sys.argv[1]

    if comando == "azzera":
        asyncio.run(azzera())
    elif comando == "aggiungi":
        ridotto = "--ridotto" in sys.argv
        elenco = documenti_ridotti() if ridotto else documenti_del_corpus()
        if ridotto:
            print(f"corpus ridotto: {len(elenco)} documenti su "
                  f"{len(documenti_del_corpus())} (vedi lezione 5, par. 6)")
        asyncio.run(aggiungi(elenco))
    elif comando == "digerisci":
        asyncio.run(digerisci())
    elif comando == "arricchisci":
        asyncio.run(arricchisci())
    elif comando == "chiedi":
        tipo = "grafo"
        argomenti = sys.argv[2:]
        if argomenti and argomenti[0].startswith("--"):
            tipo = argomenti.pop(0)[2:]
        if tipo not in TIPI_DI_RICERCA:
            sys.exit(f"tipo sconosciuto. Usa: {', '.join(TIPI_DI_RICERCA)}")
        asyncio.run(chiedi(" ".join(argomenti), tipo))
    elif comando == "stato":
        asyncio.run(stato())
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
