# Module 6 — Where the data lives {#modulo-6-dove-vive-il-dato}

**Duration: 2 hours** (36 minutes of lesson, 84 of lab).
Running total: 14.5 / 20 hours.

So far the knowledge base has been a black box with three files inside. Now
you open the box: three different ways to store data, why you need all
three, and how you move from the throwaway ones to the real ones.

---

## 1. The first five minutes: look at what is there {#1-primi-cinque-minuti-guarda-cosa-ce}

```bash
python memoria/quaderno.py stato
ls -la dati/cognee/sistema/databases/
```

Three different things, not one:

```text
cognee_db              un file SQLite
cognee.kuzu/           una cartella: il grafo
<id-dataset>/          i vettori (LanceDB)
```

(An SQLite file; a folder holding the graph; the vectors in LanceDB.)

Open the first one with the simplest tool there is:

```bash
python -c "
import sqlite3, glob
db = glob.glob('dati/cognee/sistema/databases/cognee_db')[0]
for (nome,) in sqlite3.connect(db).execute(
        \"select name from sqlite_master where type='table' order by name\"):
    print(nome)
"
```

You will see about twenty tables: `data`, `datasets`, `pipeline_runs`,
`users`, `acls`. None of them holds your vectors, and none holds the
graph. Why?

## 2. Three data models, three jobs {#2-tre-modelli-di-dato-tre-mestieri}

| | Relational | Vector | Graph |
|---|---|---|---|
| Unit | row in a table | vector with a label | node and edge |
| Typical question | "which documents did I load on March 3?" | "what is similar to this?" | "what is connected to this?" |
| Language | SQL | no standard | Cypher, Gremlin |
| Cost of a search | index on a column: instant | compare with every vector (or approximate index) | walk the edges |
| In your knowledge base | SQLite / PostgreSQL | LanceDB / pgvector | Kuzu |

The three questions really are different, and none of the three systems
answers the others' questions well.

### Relational: the bookkeeping {#il-relazionale-la-contabilita}

This is where the **register** lives: which files you added, when, with
which fingerprint, in which dataset, who can see them, which pipeline
runs succeeded. Not the contents: the bookkeeping of the contents.

You need it because the question "did I already load this file?" is
answered with a `SELECT`, not with a semantic search.

### Vector: similarity {#il-vettoriale-la-somiglianza}

A chunk of text is 384 numbers (module 3). Searching means finding the
vectors closest to the question's vector.

With 48 chunks you can compare them all: 48 multiplications, one
millisecond. With 48,000 chunks it becomes 48,000, and at ten searches
per second the math no longer works. That is why **approximate indexes**
exist (*ANN*, *approximate nearest neighbour*): structures that find
"almost always the closest ones" by looking at a fraction of them. The
most common is **HNSW** (*hierarchical navigable small world*): a network
of links on several levels, where you go down by jumping.

Approximate means that now and then you miss a result. In exchange, the
search stays instant when the chunks become millions.

### Graph: the links {#il-grafo-i-collegamenti}

Module 4 already explained it. What a graph database does and the others
do not is **follow an edge without a join**. In SQL, "the neighbors of
the neighbors" is a self `JOIN`; at three hops it becomes impractical.
In Cypher it is one line:

```cypher
MATCH (a)-[*1..2]-(b) WHERE a.name = 'Caldaia Termovex TX-24' RETURN b
```

**Kuzu** is an *embedded* graph database: it is not a server, it is a
folder of files that your application opens directly, like SQLite. No
service to start, no port, no password.
Documentation: <https://docs.kuzudb.com/>.

## 3. Why SQLite is no longer enough {#3-perche-sqlite-non-basta-piu}

SQLite is perfect to start with: no installation, a single file, you
copy it with `cp`. The course uses it up to here on purpose.

It stops being enough when:

| Problem | What happens with SQLite |
|---|---|
| two programs write at the same time | "database is locked": SQLite has **one** writer at a time |
| the knowledge base lives on a server | the file is on the machine, the clients are not |
| there are many vectors | LanceDB is a second system to manage and back up separately |
| you want a consistent backup | three technologies, three ways to save |

The third point is the one you feel most: with SQLite you have the
metadata in one place and the vectors in another. With PostgreSQL +
pgvector they live in the same database, and one `pg_dump` takes both.

## 4. PostgreSQL and pgvector {#4-postgresql-e-pgvector}

**PostgreSQL** is a relational database, a real service, with users,
concurrent connections, transactions, backups.

**pgvector** is an extension that adds a new data type to it:
`vector(384)`, and the operators to compare them.

```sql
CREATE EXTENSION vector;

CREATE TABLE pezzi (
    id     bigserial PRIMARY KEY,
    testo  text,
    punto  vector(384)
);

-- i 5 pezzi piu' vicini a un vettore dato
SELECT testo FROM pezzi ORDER BY punto <-> '[0.1, 0.2, ...]' LIMIT 5;
```

(The comment means: the 5 chunks closest to a given vector.)

The **`<->`** operator is the Euclidean distance; **`<=>`** is the cosine
distance, the one we used in module 3; **`<#>`** is the negated inner
product. They are normal SQL operators: you can put them in a query with
`WHERE`, `JOIN`, `ORDER BY`, everything.

This is the real advantage, and it is worth seeing it written out:

```sql
SELECT testo FROM pezzi
WHERE apparecchio = 'Caldaia Termovex TX-24'
  AND data > '2026-06-01'
ORDER BY punto <=> :domanda
LIMIT 5;
```

**Exact filter and similarity search in the same query.** With a
separate vector database you would have to run two searches and cross
them by hand.

Without an index, pgvector compares every vector. You add one like this:

```sql
CREATE INDEX ON pezzi USING hnsw (punto vector_cosine_ops);
```

Documentation: <https://github.com/pgvector/pgvector>.

### Docker, in four lines {#docker-in-quattro-righe}

Installing PostgreSQL with pgvector by hand means compiling an
extension. With Docker it is one configuration file and one command,
because a ready-made image exists (`pgvector/pgvector:pg17`).

A **container** is a program packaged with everything it needs. It is
not a virtual machine: it shares the operating system, and it starts in
a second. For the course you need three commands: `up -d` to start,
`logs` to look, `down` to stop.

The data lives in a **volume**, which outlives the container. Stopping
Postgres deletes nothing; `down -v` does.

## 5. What changes in your `.env` {#5-cosa-cambia-nel-tuo-env}

This is all you need to migrate:

```bash
DB_PROVIDER=postgres
DB_NAME=cognee_db
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=cognee
DB_PASSWORD=cognee
VECTOR_DB_PROVIDER=pgvector
```

Six lines. The code of `quaderno.py` does not change at all: it is the
same decoupling as the gateway, applied to databases.

**What those six lines do not do: migrate the data.** The documents
already digested stay in SQLite; the new database is empty. You have to
redo `add` and `cognify`, and so spend the quota again. On the course
corpus it takes four minutes; on a real knowledge base it is a decision
to make before, not after. **If you think you will end up on PostgreSQL,
start with PostgreSQL.**

## 6. Looking inside the graph {#6-guardare-dentro-al-grafo}

You query Kuzu in **Cypher**, the language of graph databases. Three
queries you will use all the time:

```cypher
// quanti nodi ci sono, per tipo
MATCH (n) RETURN labels(n) AS tipo, count(*) AS quanti ORDER BY quanti DESC;

// i vicini di un nodo
MATCH (a)-[r]-(b) WHERE a.name CONTAINS 'Termovex' RETURN a.name, type(r), b.name;

// i nodi piu' collegati: sono quelli che contano
MATCH (n)-[r]-() RETURN n.name, count(r) AS grado ORDER BY grado DESC LIMIT 10;
```

(The comments mean: how many nodes there are, by type; the neighbors of
a node; the most connected nodes, the ones that matter.)

The last one is a diagnostic: if at the top you find a generic node like
«bar» or «ore» (hours), it means the extraction created a node for a unit
of measure and attached half the knowledge base to it. It is exactly the
kind of defect you only see by looking.

You can also ask cognee for it with `SearchType.CYPHER`, without opening
Kuzu by hand.

## 7. How much space it takes {#7-quanto-occupa}

On the course corpus, after `cognify`:

| Piece | Typical size |
|---|---|
| copied documents | as much as the originals |
| SQLite (metadata) | a few hundred KB |
| Kuzu (graph) | a few MB |
| LanceDB (vectors) | ~1.5 KB per chunk (384 numbers at 4 bytes, plus the index) |

The rule to take away: **vectors take almost as much space as the text**,
and the graph takes little. A knowledge base of ten thousand chunks fits
in a few tens of MB. Disk is not your problem: the quota is.

**Now: [LAB.md](LAB.md).**
