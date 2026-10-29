# Module 7 — Memory maintenance {#modulo-7-manutenzione-della-memoria}

**Duration: 2 hours** (42 minutes of lesson, 78 of lab).
Running total: 16.5 / 20 hours.

So far you have built. Now the problem is **keeping it alive**: adding
without redoing everything, updating facts that change, removing what
must not stay, and being able to back it up.

It is the part courses never cover, and it is the part that decides
whether six months from now you still use the knowledge base or have
abandoned it.

---

## 1. The first five minutes: the memory that gives you old information {#1-primi-cinque-minuti-la-memoria-che-ti-da-linformazione-vecchia}

```bash
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia?"
```

(The question means: "At what pressure should I keep the boiler
system?")

The corpus has two answers:

- the **manual** says: bring the pressure back to **1.2 bar**;
- the **note of August 30, 2026** says the technician raised the
  operating pressure to **1.4 bar**, and that the March value "no longer
  applies".

The system almost always gives you 1.2. Not because it is broken:
because the manual repeats that number in three places, and the note
says it only once. Retrieval rewards redundancy, not dates.

**This is the fourth failure of the course**, and unlike the other three
no algorithm solves it on its own: it is a problem of **governing the
facts**, and you have to face it head on.

## 2. Four maintenance operations {#2-quattro-operazioni-di-manutenzione}

| Operation | When you need it | cognee command |
|---|---|---|
| **add** | a new note has arrived | `add` + `cognify` (incremental) |
| **update** | a document has changed | `update` |
| **forget** | a document must not stay | `forget` |
| **check** | "is everything still consistent?" | `validate`, `report` |

### 2.1 Adding without redoing everything {#21-aggiungere-senza-rifare-tutto}

```python
await cognee.add("nuova-nota.md", dataset_name="officina")
await cognee.cognify(datasets=["officina"])      # incremental_loading=True
```

`cognify` is **incremental**: it recognizes already digested documents
by their fingerprint and works only on the new ones. It costs the quota
of the new document, not of the whole knowledge base. That is why it
makes sense to pour in a note every time you finish a job.

### 2.2 Updating a document {#22-aggiornare-un-documento}

```python
await cognee.update(data_id=..., data="testo nuovo", dataset_id=...)
```

It is not the same as deleting and adding again. `update` **keeps the
same identifier** for the document and compares the old text with the
new one chunk by chunk, redoing only the chunks that changed. It costs
less, and above all it does not break the graph links that pointed to
that document.

To do it you need `data_id` and `dataset_id`, which you read like this:

```python
datasets = await cognee.datasets.list_datasets()
documenti = await cognee.datasets.list_data(dataset_id=datasets[0].id)
```

### 2.3 Forgetting {#23-dimenticare}

```python
await cognee.forget(data_id=...,  dataset="officina")   # un documento
await cognee.forget(dataset="officina", memory_only=True)  # il grafo, non i file
await cognee.forget(everything=True)                     # tutto
```

(The comments mean: one document; the graph, not the files; everything.)

`memory_only=True` is the most interesting one: it throws away what the
model understood, but keeps the documents. It is what you do when you
change model or when you notice that the extraction produced junk: you
do not have to reload anything, only digest again.

There is also `cognee.datasets.delete_data(dataset_id, data_id, mode=...)`
with two modes:

| `mode` | What it does |
|---|---|
| `soft` | removes the document, leaves the entities other documents share |
| `hard` | also removes the entities left orphaned |

`soft` is the default and almost always the right one: with `hard` you
risk deleting a «Caldaia Termovex TX-24» node that the other five notes
also needed.

## 3. Facts that contradict each other {#3-i-fatti-che-si-contraddicono}

This is the serious problem, and it is worth understanding it well
before you try to solve it.

A knowledge base of documents has no concept of **current truth**. It
has documents, each one true at the moment it was written. "Keep the
pressure at 1.2 bar" was true in March and has been false since August,
but the March document is still there and still says that.

Three ways to deal with it, from weakest to strongest.

### 3.1 Give the system the date, and tell it to use it {#31-dare-al-sistema-la-data-e-dirgli-di-usarla}

The simplest: put the date in the text (not just in the file name) and
instruct the model to prefer the most recent fact when two contradict
each other.

```text
Se due informazioni si contraddicono, usa quella con la data piu'
recente e di' esplicitamente che c'era un valore precedente.
```

(It means: "If two pieces of information contradict each other, use the
one with the most recent date and say explicitly that there was an
earlier value.")

It often works. It does not work when retrieval does not bring in the
recent document, because you cannot prefer a fact you do not have in
front of you.

### 3.2 Write a correction note {#32-scrivere-una-nota-di-rettifica}

The **manual and reliable** way: when a fact changes, add a document
that says so explicitly.

```markdown
# Rettifica del 30 agosto 2026 — Caldaia Termovex TX-24

SUPERA il valore del libretto e le mie note precedenti.
Pressione di esercizio a freddo: 1,4 bar (prima: 1,2 bar).
Precarica vaso di espansione: 1,2 bar (prima: 1,0 bar).
```

(A correction dated August 30, 2026: it OVERRIDES the manual and the
earlier notes; cold operating pressure 1.4 bar, was 1.2; expansion
vessel pre-charge 1.2 bar, was 1.0.)

It is crude and it works, for two reasons: the document contains the
words of the question («pressione», «esercizio», «bar») so it gets
retrieved, and it says unambiguously which value applies.

It is also what a serious maintenance technician would do with a paper
notebook: do not erase, write down the correction.

### 3.3 Let `memify` do it {#33-lasciarlo-fare-a-memify}

```python
await cognee.memify(dataset="officina")
```

`memify` goes over the graph and tries to merge the nodes that are the
same thing, weigh the links, and derive new facts. On name duplicates
(«Lavatrice LAVANOR» and «Lavatrice Lavanor») it works well. On value
contradictions it works sometimes.

**Do not trust `memify` for the facts that matter.** For the boiler
pressure, use method 3.2 and sleep soundly.

## 4. Checking that everything is still in order {#4-controllare-che-sia-ancora-tutto-a-posto}

cognee has two diagnostic tools worth knowing.

```python
report = await cognee.validate(dataset="officina")
```

It compares the graph and the vector index and tells you whether they
**agree**: nodes present in the graph and not in the vectors, or the
other way around. This happens when a `cognify` stops halfway, which,
with free quotas, does happen.

```python
await cognee.report(datasets="officina", output_path="dati/relazione.md")
```

It writes a Markdown report with:

- the **hub nodes** (*hubs*, or "god nodes"): the ones linked to
  everything. If at the top you find «bar» or «ore» (hours), the
  extraction created a node for a unit of measure and attached half the
  knowledge base to it;
- unexpected links between different parts of the knowledge base;
- the provenance of the edges: which document each link comes from.

Hub nodes are the most common defect and the most harmful: they make
everything reachable from everything, and two-hop retrieval stops
selecting. You fix them by removing the entity type that creates them
from the list you give the model, and digesting again.

## 5. The backup {#5-il-backup}

Three technologies, three ways to back up. Make a list and stick to it.

| Piece | Where | How you back it up |
|---|---|---|
| original documents | `dati/cognee/documenti/` | copy the folder |
| register | PostgreSQL (or SQLite) | `pg_dump` (or copy the file) |
| vectors | pgvector, inside Postgres | it is in the `pg_dump` |
| graph | Kuzu, folder | copy the folder, **with the system stopped** |

**Copying Kuzu while the system is writing produces a broken backup.**
As with SQLite: either you stop the program, or you use the export.

Export is the clean way. `cognee.export` has four formats and **they do
not do the same thing**:

| `format` | What you get | What it is for |
|---|---|---|
| `cogx` | an archive folder | **restoring**: `cognee.remember(COGXArchiveSource(percorso))` |
| `json` | a readable file | looking inside, versioning it with git |
| `graphml` | standard graph format | opening it in Gephi or similar |
| `cypher` | insert statements | moving it to Neo4j |

```python
await cognee.export(dataset="officina", format="cogx",
                    destination="dati/backup/archivio")
```

The one for backups is **`cogx`**: it is the only one you can put back
in. `json` is useful for reading and for tracking changes, but it is not
a restore.

In every case, an export beats copying the folder: it is independent of
the engine, and it does not break if the program is writing.

**The rule:** a good backup is one you have tried to restore. A backup
never restored is not a backup, it is a file.

## 6. How often {#6-quanto-spesso}

| Operation | How often |
|---|---|
| `add` + `cognify` of the new note | after every job |
| `memify` | every ten to twenty new documents |
| `validate` | after every interrupted `cognify` |
| `report` | once a month, to look at the hub nodes |
| backup | before every experiment, and in any case once a month |

**Now: [LAB.md](LAB.md).**
