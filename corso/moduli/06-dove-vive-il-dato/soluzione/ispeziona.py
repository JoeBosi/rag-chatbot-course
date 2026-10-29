#!/usr/bin/env python3
"""Guarda dentro ai tre database dell'archivio. Versione completa.

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
    """Le stesse tabelle, ma su PostgreSQL."""
    import os

    import psycopg2

    connessione = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "cognee_db"),
        user=os.getenv("DB_USERNAME", "cognee"),
        password=os.getenv("DB_PASSWORD", "cognee"),
    )
    cursore = connessione.cursor()

    cursore.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
    versione = cursore.fetchone()
    print(f"PostgreSQL su {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}")
    print(f"pgvector: {versione[0] if versione else 'NON INSTALLATO'}\n")

    cursore.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' "
                    "ORDER BY tablename")
    tabelle = [riga[0] for riga in cursore.fetchall()]
    for tabella in tabelle:
        cursore.execute(f'SELECT count(*) FROM "{tabella}"')
        print(f"  {tabella:<40} {cursore.fetchone()[0]:>6} righe")
    print(f"\n{len(tabelle)} tabelle")
    connessione.close()


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
    """Tre domande al grafo, in Cypher."""
    import kuzu

    percorso = trova_kuzu()
    if not percorso:
        print("non trovo il grafo Kuzu.")
        print("Serve GRAPH_DATABASE_PROVIDER=kuzu in .env, e poi")
        print("ricostruire l'archivio. Se c'e' un .pkl che non si apre")
        print("con kuzu, allora e' davvero un altro motore.")
        return

    # Kuzu qui e' un file solo, piu' il suo registro .wal accanto.
    peso = percorso.stat().st_size
    wal = percorso.with_suffix(percorso.suffix + ".wal")
    if wal.exists():
        peso += wal.stat().st_size
    print(f"Kuzu: {percorso.name}  ({peso / 1024:.0f} KB, .wal compreso)\n")

    database = kuzu.Database(str(percorso))
    connessione = kuzu.Connection(database)

    for titolo, query in QUERY.items():
        print(f"--- {titolo} ---")
        try:
            risultato = connessione.execute(query)
        except Exception as errore:
            print(f"    query non eseguibile: {str(errore)[:120]}")
            print()
            continue
        colonne = risultato.get_column_names()
        righe = 0
        while risultato.has_next():
            valori = risultato.get_next()
            print("    " + "  |  ".join(
                f"{nome}={valore}" for nome, valore in zip(colonne, valori)))
            righe += 1
        if not righe:
            print("    (nessun risultato)")
        print()


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
