#!/usr/bin/env python3
"""Guarda dentro ai tre database dell'archivio. Da completare.

    python memoria/ispeziona.py relazionale
    python memoria/ispeziona.py grafo
    python memoria/ispeziona.py vettori
    python memoria/ispeziona.py tutto

Nessuna chiamata al modello: apre i file e legge.
"""

import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv


def trova_radice() -> Path:
    for candidata in Path(__file__).resolve().parents:
        if (candidata / "progetto-finale" / "corpus").is_dir():
            return candidata
    raise SystemExit("lancia il comando dalla cartella del corso")


RADICE = trova_radice()
DATABASES = RADICE / "dati" / "cognee" / "sistema" / "databases"
load_dotenv(RADICE / ".env")


# --------------------------------------------------------------------
def relazionale():
    """Le tabelle del registro: SQLite oppure PostgreSQL."""
    import os
    if os.getenv("DB_PROVIDER", "sqlite") == "postgres":
        relazionale_postgres()
    else:
        relazionale_sqlite()


def relazionale_sqlite():
    percorso = DATABASES / "cognee_db"
    if not percorso.exists():
        sys.exit(f"non trovo {percorso}: hai gia' fatto 'aggiungi'?")
    connessione = sqlite3.connect(percorso)
    print(f"SQLite: {percorso}  ({percorso.stat().st_size / 1024:.0f} KB)\n")
    tabelle = [r[0] for r in connessione.execute(
        "select name from sqlite_master where type='table' order by name")]
    for tabella in tabelle:
        quante = connessione.execute(f'select count(*) from "{tabella}"').fetchone()[0]
        print(f"  {tabella:<32} {quante:>6} righe")
    print(f"\n{len(tabelle)} tabelle")


def relazionale_postgres():
    """Le stesse tabelle, ma su PostgreSQL.

    TODO 1 ------------------------------------------------------------
    Usa psycopg2 per collegarti leggendo DB_HOST, DB_PORT, DB_NAME,
    DB_USERNAME, DB_PASSWORD da .env, e stampa nome e numero di righe
    di ogni tabella dello schema "public".

    La query che elenca le tabelle:
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
        ORDER BY tablename

    Stampa anche se l'estensione pgvector e' installata:
        SELECT extversion FROM pg_extension WHERE extname = 'vector'
    -------------------------------------------------------------------
    """
    raise NotImplementedError("TODO 1: relazionale_postgres()")


# --------------------------------------------------------------------
def trova_kuzu() -> Path | None:
    """Il grafo Kuzu dentro l'archivio.

    Attenzione al nome: cognee 1.6 chiama il file del grafo
    `<id-archivio>.pkl`, qualunque motore ci sia sotto. Il suffisso e'
    una convenzione ereditata, non il formato: quel .pkl E' un database
    Kuzu, e accanto ci trovi il suo `.pkl.wal`, che e' il registro delle
    scritture tipico di Kuzu.

    Quindi non si cerca per nome, si cerca **aprendolo**: e' l'unico
    modo onesto di sapere cosa c'e' dentro un file.
    """
    import kuzu

    for candidato in sorted(DATABASES.rglob("*.pkl")):
        try:
            kuzu.Connection(kuzu.Database(str(candidato))).execute(
                "MATCH (n) RETURN count(*)")
            return candidato
        except Exception:
            continue
    return None


def grafo():
    """Tre domande al grafo, in Cypher.

    TODO 2 ------------------------------------------------------------
    - apri il database con  kuzu.Database(str(percorso))  e
      kuzu.Connection(database)
    - esegui le tre query qui sotto e stampa i risultati in modo
      leggibile; il risultato si scorre con  mentre risultato.has_next():
      riga = risultato.get_next()
    -------------------------------------------------------------------
    """
    raise NotImplementedError("TODO 2: grafo()")


QUERY = {
    "quanti nodi per tipo":
        "MATCH (n) RETURN label(n) AS tipo, count(*) AS quanti "
        "ORDER BY quanti DESC LIMIT 15",
    "i nodi piu' collegati":
        "MATCH (n)-[r]-() RETURN n.name AS nome, count(r) AS grado "
        "ORDER BY grado DESC LIMIT 10",
    "i vicini della caldaia":
        "MATCH (a)-[r]-(b) WHERE a.name CONTAINS 'Termovex' "
        "RETURN a.name AS da, b.name AS a LIMIT 15",
}


# --------------------------------------------------------------------
def vettori():
    """Quanti vettori ci sono e quanto occupano."""
    lance = [p for p in DATABASES.rglob("*.lance.db") if p.is_dir()]
    if not lance:
        print("nessun indice LanceDB: stai usando pgvector?")
        return
    for cartella in lance:
        peso = sum(f.stat().st_size for f in cartella.rglob("*") if f.is_file())
        tabelle = [p.name for p in cartella.iterdir() if p.is_dir()]
        print(f"LanceDB: {cartella.name}  ({peso / 1024:.0f} KB)")
        for tabella in sorted(tabelle):
            print(f"  {tabella}")


def main():
    comando = sys.argv[1] if len(sys.argv) > 1 else "tutto"
    if comando in ("relazionale", "tutto"):
        print("=" * 60, "\nREGISTRO\n" + "=" * 60)
        relazionale()
    if comando in ("grafo", "tutto"):
        print("\n" + "=" * 60, "\nGRAFO\n" + "=" * 60)
        grafo()
    if comando in ("vettori", "tutto"):
        print("\n" + "=" * 60, "\nVETTORI\n" + "=" * 60)
        vettori()


if __name__ == "__main__":
    main()
