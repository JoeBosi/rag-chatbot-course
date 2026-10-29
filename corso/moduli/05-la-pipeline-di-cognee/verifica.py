#!/usr/bin/env python3
"""Verifica del laboratorio 5.

    python moduli/05-la-pipeline-di-cognee/verifica.py

Fa due domande all'archivio: poche chiamate, poca quota.
L'archivio deve essere gia' costruito (aggiungi + digerisci).
"""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "memoria"))
load_dotenv(RADICE / ".env")
errori = []


def controlla(descrizione, condizione, aiuto=""):
    print(("OK  " if condizione else "NO  ") + descrizione)
    if not condizione:
        errori.append(f"{descrizione}\n      -> {aiuto}" if aiuto else descrizione)
    return condizione


def finisci():
    print()
    if errori:
        print("=" * 60)
        print("Mancano ancora:\n")
        for errore in errori:
            print("  -", errore)
        sys.exit(1)
    print("=" * 60)
    print("Laboratorio 5 superato.")
    print("Prossimo: moduli/06-dove-vive-il-dato/LEZIONE.md")
    sys.exit(0)


print("== configurazione ==")
controlla("memoria/quaderno.py esiste", (RADICE / "memoria" / "quaderno.py").exists(),
          "cp moduli/05-la-pipeline-di-cognee/starter/quaderno.py memoria/")
modello = os.getenv("LLM_MODEL", "")
controlla(f"LLM_MODEL ha il prefisso del fornitore ({modello})",
          "/" in modello,
          "cognee vuole openai/memoria-veloce, non memoria-veloce")

if not (RADICE / "memoria" / "quaderno.py").exists():
    finisci()

print("\n== dove stanno i dati ==")
try:
    import quaderno
    dentro_venv = ".venv" in str(quaderno.DATI)
    controlla(f"l'archivio e' in {quaderno.DATI.relative_to(RADICE) if not dentro_venv else quaderno.DATI}",
              not dentro_venv,
              "rimetti le righe cognee.config.system_root_directory / data_root_directory")
    controlla("la cartella dell'archivio esiste", quaderno.DATI.exists(),
              "python memoria/quaderno.py aggiungi")
except Exception as errore:
    controlla("quaderno.py si importa", False, f"{type(errore).__name__}: {errore}")
    finisci()

print("\n== i tre database ==")
databases = quaderno.DATI / "sistema" / "databases"
if databases.exists():
    contenuto = [p.name for p in databases.rglob("*")]
    controlla("c'e' il database relazionale (SQLite)",
              any("cognee_db" in nome for nome in contenuto))
    # Il file del grafo si chiama <id>.pkl anche quando dentro c'e' Kuzu:
    # per sapere cosa contiene un file lo si apre, non si guarda il nome.
    def e_un_grafo_kuzu():
        import kuzu
        for candidato in databases.rglob("*.pkl"):
            try:
                kuzu.Connection(kuzu.Database(str(candidato))).execute(
                    "MATCH (n) RETURN count(*)")
                return True
            except Exception:
                continue
        return False

    controlla("c'e' il grafo (Kuzu, nel file che si chiama .pkl)",
              e_un_grafo_kuzu(),
              "GRAPH_DATABASE_PROVIDER=kuzu in .env, poi ricostruisci")
    controlla("ci sono i vettori (LanceDB)",
              any("lance" in nome.lower() for nome in contenuto))
else:
    controlla("la cartella dei database esiste", False,
              "python memoria/quaderno.py aggiungi && python memoria/quaderno.py digerisci")
    finisci()

print("\n== le risposte ==")


async def prova():
    import cognee
    from cognee.modules.search.types.SearchType import SearchType

    def testo_di(risultati):
        pezzi = []
        for risultato in risultati:
            if isinstance(risultato, dict) and "search_result" in risultato:
                pezzi += [str(v) for v in risultato["search_result"]]
            else:
                pezzi.append(str(risultato))
        return " ".join(pezzi)

    diretta = testo_di(await cognee.search(
        query_text="Cosa significa l'errore E4 sulla caldaia Termovex?",
        query_type=SearchType.GRAPH_COMPLETION, datasets=[quaderno.ARCHIVIO]))
    print(f"    {' '.join(diretta.split())[:150]}")
    controlla("risponde a una domanda diretta (pressione)",
              "pression" in diretta.lower(),
              "l'archivio e' vuoto o cognify non e' arrivato in fondo")

    # Il manuale del rasaerba e' una scansione: nell'archivio non c'e'.
    # Questo controllo verifica che il muro ci SIA, perche' e' il punto
    # di partenza del progetto finale.
    muro = testo_di(await cognee.search(
        query_text="Che candela monta il rasaerba Greencut?",
        query_type=SearchType.GRAPH_COMPLETION, datasets=[quaderno.ARCHIVIO]))
    controlla("il manuale scansionato NON e' entrato (e' voluto)",
              "bpr6es" not in muro.lower(),
              "se risponde BPR6ES stai ingerendo i sorgenti .md invece "
              "dei PDF: vedi documenti_del_corpus() in quaderno.py")

    pezzi = await cognee.search(
        query_text="errore E4 caldaia", query_type=SearchType.CHUNKS,
        datasets=[quaderno.ARCHIVIO])
    controlla(f"la ricerca CHUNKS restituisce dei pezzi ({len(pezzi)})", bool(pezzi),
              "serve a capire se sbaglia il recupero o il modello")


try:
    asyncio.run(prova())
except Exception as errore:
    controlla("le ricerche girano", False, f"{type(errore).__name__}: {str(errore)[:200]}")

finisci()
