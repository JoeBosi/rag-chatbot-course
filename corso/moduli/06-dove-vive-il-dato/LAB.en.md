# Lab 6 — Open the box and change the engine {#laboratorio-6-aprire-la-scatola-e-cambiare-il-motore}

**Duration: 84 minutes.**

By the end you will have the knowledge base on PostgreSQL with pgvector,
the graph in Kuzu that you can really inspect, and a tool to look inside.

**You need Docker.** If you do not have it:
<https://docs.docker.com/engine/install/> (Linux) or Docker Desktop
(macOS). Check with `docker run --rm hello-world`.

---

## Step 1 — Look at what is there now (15 minutes) {#passo-1-guarda-cosa-ce-adesso-15-minuti}

```bash
cp moduli/06-dove-vive-il-dato/starter/ispeziona.py memoria/
python memoria/ispeziona.py relazionale
python memoria/ispeziona.py vettori
```

The SQLite part is already written. Look at the tables: `data` has one row
per document, `datasets` one per knowledge base, `pipeline_runs` one per
run. Compare the number of rows in `data` with the documents you loaded:
they must match.

Then:

```bash
python memoria/ispeziona.py grafo
```

Look at what is in the folder:

```bash
ls -la dati/cognee/sistema/databases/*/
```

You find a `cognee_db` (SQLite), a `....lance.db` folder (the vectors),
and a file called **`<id-archivio>.pkl`**, with a `.pkl.wal` next to it.

The `.pkl` looks like a serialized Python file. **It is not.** Open it:

```bash
python -c "
import kuzu, pathlib
p = next(pathlib.Path('dati/cognee/sistema/databases').rglob('*.pkl'))
c = kuzu.Connection(kuzu.Database(str(p)))
r = c.execute('MATCH (n) RETURN count(*)')
print(p.name, '->', r.get_next()[0], 'nodi')
"
```

It answers. **That `.pkl` is a Kuzu database**: cognee 1.6 gives the
graph file that name whatever engine is underneath, and the `.pkl.wal`
next to it is the write-ahead log, which is a Kuzu thing, not a pickle
thing.

It is the most useful lesson of the whole module, and it goes well
beyond cognee:

> **A file's suffix is the opinion of whoever wrote it. To know what is
> inside, you open it.**

That is why `trova_kuzu()` in `ispeziona.py` does not search by name: it
tries to open each candidate and keeps the first one that answers in
Cypher.

In `.env` the line that controls the per-dataset graph engine is:

```bash
GRAPH_DATASET_DATABASE_HANDLER=kuzu
```

With `GRAPH_DATABASE_PROVIDER=kuzu` cognee 1.6 already sets it on its
own, but writing it explicitly saves you a surprise the day you change
engine.

## Step 2 — Start PostgreSQL (10 minutes) {#passo-2-accendi-postgresql-10-minuti}

```bash
cp moduli/06-dove-vive-il-dato/starter/docker-compose.yml memoria/
docker compose -f memoria/docker-compose.yml up -d
```

Check that it is alive and that pgvector is there:

```bash
docker exec memoria-postgres psql -U cognee -d cognee_db \
  -c "CREATE EXTENSION IF NOT EXISTS vector; \
      SELECT extversion FROM pg_extension WHERE extname='vector';"
```

It must print a version number (0.8.x or higher).

| Symptom | Cause | Fix |
|---|---|---|
| `port is already allocated` | you already have a Postgres on 5432 | change it to `127.0.0.1:5433:5432` and set `DB_PORT=5433` in `.env` |
| `permission denied` on docker | you are not in the docker group | `sudo usermod -aG docker $USER`, then log out and back in |
| `Cannot connect to the Docker daemon` | Docker is not running | start it |

## Step 3 — Try pgvector by hand (15 minutes) {#passo-3-prova-pgvector-a-mano-15-minuti}

Before letting cognee do it, do it yourself: three minutes that make
clear what a vector database is.

```bash
docker exec -i memoria-postgres psql -U cognee -d cognee_db <<'SQL'
CREATE TABLE prova (id serial primary key, testo text, punto vector(3));
INSERT INTO prova (testo, punto) VALUES
  ('rasaerba',  '[1.0, 0.1, 0.0]'),
  ('tagliaerba','[0.9, 0.2, 0.0]'),
  ('caldaia',   '[0.0, 0.1, 1.0]');

-- i piu' vicini a "rasaerba", per distanza coseno
SELECT testo, round((punto <=> '[1.0, 0.1, 0.0]')::numeric, 4) AS distanza
FROM prova ORDER BY punto <=> '[1.0, 0.1, 0.0]';
SQL
```

(The comment means: the closest to "rasaerba", by cosine distance.)

«tagliaerba» (lawn mower) must come out very close and «caldaia»
(boiler) far away. These are the vectors of module 3, in three
dimensions instead of 384, inside a normal SQL query.

Now the thing a separate vector database cannot do:

```bash
docker exec -i memoria-postgres psql -U cognee -d cognee_db <<'SQL'
SELECT testo FROM prova
WHERE testo LIKE '%erba%'
ORDER BY punto <=> '[0.0, 0.1, 1.0]'
LIMIT 1;
SQL
```

Exact filter and similarity ordering, together. Then clean up:

```bash
docker exec memoria-postgres psql -U cognee -d cognee_db -c "DROP TABLE prova;"
```

## Step 4 — Migrate the knowledge base (25 minutes, mostly waiting) {#passo-4-migra-larchivio-25-minuti-quasi-tutti-di-attesa}

In `.env`:

```bash
DB_PROVIDER=postgres
DB_NAME=cognee_db
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=cognee
DB_PASSWORD=cognee
VECTOR_DB_PROVIDER=pgvector
GRAPH_DATASET_DATABASE_HANDLER=kuzu
```

Install the libraries you need to talk to Postgres:

```bash
pip install "cognee[postgres-binary]==1.6.0"
```

**The data does not move by itself.** The new database is empty: you
have to redo everything, and spend the quota again.

```bash
python memoria/quaderno.py azzera
python memoria/quaderno.py aggiungi
python memoria/quaderno.py digerisci
```

While you wait, think about this: if you had ten years of notes instead
of twelve files, this line would have cost you days of quota. **Choose
the database before you fill it.** Write it in `note-lab6.md`.

## Step 5 — Look inside, for real this time (15 minutes) {#passo-5-guarda-dentro-adesso-davvero-15-minuti}

Write `relazionale_postgres()` (TODO 1) and `grafo()` (TODO 2) in
`memoria/ispeziona.py`.

```bash
python memoria/ispeziona.py relazionale
```

The same tables as before, plus the vector ones. Look for the tables
with `vector` in the name.

```bash
python memoria/ispeziona.py grafo
```

Three Cypher queries. Look at the second one, "the most connected
nodes": if at the top you find a node that is a unit of measure («bar»,
«ore», hours) or a generic word, the extraction created a junk node and
attached half the knowledge base to it. Write down which ones they are:
**it is the first job of module 7.**

Also check directly on the database that the vectors are there:

```bash
docker exec memoria-postgres psql -U cognee -d cognee_db \
  -c "\dt" | head -20
```

## Step 6 — The backup (4 minutes) {#passo-6-il-backup-4-minuti}

Now that metadata and vectors live in the same place:

```bash
docker exec memoria-postgres pg_dump -U cognee cognee_db > dati/backup.sql
ls -lh dati/backup.sql
```

One file. The Kuzu graph, however, is **not** in there: it is a separate
folder, and you back it up separately. Backing it up is the topic of
module 7.

## Step 7 — Check {#passo-7-verifica}

```bash
python moduli/06-dove-vive-il-dato/verifica.py
```

---

## If you want to go back {#se-vuoi-tornare-indietro}

Put this back in `.env`:

```bash
DB_PROVIDER=sqlite
VECTOR_DB_PROVIDER=lancedb
```

and redo `azzera / aggiungi / digerisci`. The data on Postgres stays
where it is: `docker compose -f memoria/docker-compose.yml down` stops
the service without deleting it.

## What you keep from this module {#artefatti-di-questo-modulo}

`memoria/docker-compose.yml`, `memoria/ispeziona.py`, the knowledge base
on PostgreSQL + pgvector and the graph in Kuzu.
