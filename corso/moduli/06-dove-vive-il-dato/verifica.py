#!/usr/bin/env python3
"""Verifica del laboratorio 6. Nessuna chiamata al modello.

    python moduli/06-dove-vive-il-dato/verifica.py
"""

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
    print("Laboratorio 6 superato.")
    print("Prossimo: moduli/07-manutenzione-della-memoria/LEZIONE.md")
    sys.exit(0)


print("== configurazione ==")
controlla("DB_PROVIDER = postgres", os.getenv("DB_PROVIDER") == "postgres",
          f"adesso vale {os.getenv('DB_PROVIDER')!r}: vedi LAB.md passo 4")
controlla("VECTOR_DB_PROVIDER = pgvector",
          os.getenv("VECTOR_DB_PROVIDER") == "pgvector",
          f"adesso vale {os.getenv('VECTOR_DB_PROVIDER')!r}")
controlla("GRAPH_DATASET_DATABASE_HANDLER = kuzu",
          os.getenv("GRAPH_DATASET_DATABASE_HANDLER") == "kuzu",
          "senza, i grafi finiscono in file .pkl invece che in Kuzu")
controlla("memoria/docker-compose.yml esiste",
          (RADICE / "memoria" / "docker-compose.yml").exists(),
          "cp moduli/06-dove-vive-il-dato/starter/docker-compose.yml memoria/")
controlla("memoria/ispeziona.py esiste",
          (RADICE / "memoria" / "ispeziona.py").exists(),
          "cp moduli/06-dove-vive-il-dato/starter/ispeziona.py memoria/")

print("\n== PostgreSQL ==")
try:
    import psycopg2
    connessione = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"), port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "cognee_db"),
        user=os.getenv("DB_USERNAME", "cognee"),
        password=os.getenv("DB_PASSWORD", "cognee"), connect_timeout=10)
    cursore = connessione.cursor()
    controlla("il database risponde", True)

    cursore.execute("SELECT extversion FROM pg_extension WHERE extname='vector'")
    versione = cursore.fetchone()
    controlla(f"pgvector installato ({versione[0] if versione else '-'})",
              bool(versione),
              "CREATE EXTENSION vector; nel database")

    cursore.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
    tabelle = [r[0] for r in cursore.fetchall()]
    controlla(f"cognee ha creato le sue tabelle ({len(tabelle)})",
              len(tabelle) >= 10,
              "python memoria/quaderno.py aggiungi && ... digerisci")
    controlla("la tabella dei documenti ha delle righe",
              "data" in tabelle and
              (cursore.execute('SELECT count(*) FROM data') or
               cursore.fetchone()[0]) > 0,
              "l'archivio e' vuoto: rifai aggiungi e digerisci")
    connessione.close()
except ImportError:
    controlla("psycopg2 installato", False,
              'pip install "cognee[postgres-binary]==1.6.0"')
except Exception as errore:
    controlla("il database risponde", False,
              f"{type(errore).__name__}: {str(errore)[:150]}\n"
              "         docker compose -f memoria/docker-compose.yml up -d")

print("\n== il grafo Kuzu ==")
try:
    import ispeziona
    percorso = ispeziona.trova_kuzu()
    if controlla(f"il grafo Kuzu esiste ({percorso.name if percorso else '-'})",
                 percorso is not None,
                 "metti GRAPH_DATASET_DATABASE_HANDLER=kuzu e ricostruisci"):
        import kuzu
        connessione = kuzu.Connection(kuzu.Database(str(percorso)))
        risultato = connessione.execute("MATCH (n) RETURN count(*)")
        quanti = risultato.get_next()[0] if risultato.has_next() else 0
        controlla(f"il grafo ha dei nodi ({quanti})", quanti > 20,
                  "cognify non e' arrivato in fondo")
        risultato = connessione.execute("MATCH ()-[r]->() RETURN count(*)")
        archi = risultato.get_next()[0] if risultato.has_next() else 0
        controlla(f"il grafo ha degli archi ({archi})", archi > 20)
except Exception as errore:
    controlla("il grafo si apre", False, f"{type(errore).__name__}: {str(errore)[:150]}")

print("\n== ispeziona.py ==")
try:
    import ispeziona
    controlla("relazionale_postgres() e' scritta",
              "NotImplementedError" not in
              (RADICE / "memoria" / "ispeziona.py").read_text().split(
                  "def relazionale_postgres")[1].split("def ")[0],
              "TODO 1")
    controlla("grafo() e' scritta",
              "NotImplementedError" not in
              (RADICE / "memoria" / "ispeziona.py").read_text().split(
                  "\ndef grafo")[1].split("\ndef ")[0],
              "TODO 2")
except Exception as errore:
    controlla("ispeziona.py si legge", False, str(errore)[:150])

finisci()
