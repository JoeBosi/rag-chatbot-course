# Module 5 — The cognee pipeline {#modulo-5-la-pipeline-di-cognee}

**Duration: 3 hours** (60 minutes of lesson, 120 of lab).
Running total: 12.5 / 20 hours.

In modules 3 and 4 you built things by hand: chunking, BM25, embeddings,
entity extraction, graph traversal. Now you throw it all away and use an
engine that does those things better than you.

It was not wasted time: without those four modules, what follows would
be magic. With those four modules, it is software.

---

## 1. The first five minutes: the full round {#1-primi-cinque-minuti-il-giro-completo}

```bash
python moduli/05-la-pipeline-di-cognee/starter/primo_giro.py
```

It takes **one** repair note, digests it and answers a question. It takes
a minute or two. At the end you have a graph, vectors and an answer that
combines the manual and your experience, written with **six lines of real
code**:

```python
await cognee.add(testo, dataset_name="officina")
await cognee.cognify(datasets=["officina"])
risultati = await cognee.search(query_text="...",
                                query_type=SearchType.GRAPH_COMPLETION,
                                datasets=["officina"])
```

All of module 4 fits inside the second line.

## 2. What cognee is {#2-cose-cognee}

A **memory engine**: it takes documents, derives a graph of entities and
relationships plus a vector index, and answers questions using both. Open
source, installed with `pip`, runs on your computer.

The model it has in mind is called **ECL**: *Extract, Cognify, Load*. It
paraphrases ETL (*Extract, Transform, Load*), the way data has been moved
into company data warehouses for thirty years; the middle word changes
because instead of a mechanical transformation there is a model that
understands the text.

Documentation: <https://docs.cognee.ai/>.

## 3. The four operations {#3-le-quattro-operazioni}

### `add` — put it in {#add-metti-dentro}

```python
await cognee.add(["percorso/al/file.md", "..."], dataset_name="officina")
```

What it does: copies the files into its own folder, recognizes the format
(it handles about forty: text, PDF, DOCX, images, audio), extracts the raw
text, and registers each document in a table with an identifier and a
fingerprint of the content.

What it does **not** do: it does not call the model, it does not build
anything. It is fast and **uses no quota**. If you run `add` again on the
same file, the fingerprint is the same and cognee does not duplicate it.

The **dataset** is the name of the knowledge base. You can have more than
one (`casa`, `lavoro`, `bici`) and query one or all of them together.

### `cognify` — understand {#cognify-capisci}

```python
await cognee.cognify(datasets=["officina"])
```

This is the command that costs. In order:

| Phase | What happens | Calls the model? |
|---|---|---|
| 1. classification | what kind of document it is | yes, once per document |
| 2. permissions | who can see what | no |
| 3. chunking | the text becomes chunks | no |
| 4. extraction | entities and relationships from each chunk | **yes, one per chunk** |
| 5. summary | one summary per chunk | **yes, one per chunk** |
| 6. embedding | each chunk becomes 384 numbers | no (runs on your machine) |
| 7. writing | nodes and edges in the graph, vectors in the index | no |

Phases 4 and 5 are the two calls per chunk that module 2 talked about.
The math you learned to do there applies exactly here.

### `memify` — tidy up {#memify-riordina}

```python
await cognee.memify(dataset="officina")
```

It passes **over the graph already built** and improves it: it merges
nodes that are the same thing, strengthens links used often, derives new
facts from the existing ones, removes nodes that are no longer needed.

It is the difference between an archive and a **memory**: an archive
holds what you put in it, a memory reorganizes itself. It is also the
reason the title of this course says "memory" and not "search".

`memify` requires `cognify` to have run already: it does not ingest
anything new.

### `search` — ask {#search-chiedi}

```python
await cognee.search(query_text="...", query_type=SearchType.GRAPH_COMPLETION,
                    datasets=["officina"])
```

cognee has **twenty** search types. These are the ones you will use:

| Type | What it does | When you need it |
|---|---|---|
| `GRAPH_COMPLETION` | answers by following the graph | multi-hop questions: "how many hours in total" |
| `RAG_COMPLETION` | answers using only the text chunks | direct questions: "which spark plug does it take" |
| `HYBRID_COMPLETION` | both (it is the default) | when you do not know |
| `CHUNKS` | gives you the raw chunks, no answer | to **understand what it retrieved** |
| `CHUNKS_LEXICAL` | as above, but word-based search | exact codes and abbreviations |
| `SUMMARIES` | the chunk summaries | skimming a large knowledge base |
| `CYPHER` | runs a query on the graph | inspection (module 6) |
| `TEMPORAL` | questions involving time | "what did I do in September" |

`CHUNKS` is the most important when something goes wrong: it separates
"retrieval got it wrong" from "the model got it wrong". They are two
different problems with two different cures.

## 4. Where the data ends up {#4-dove-finiscono-i-dati}

**Watch out, because the default answer is wrong.** Unless you change it,
cognee writes inside the library folder, in
`.venv/lib/python3.12/site-packages/cognee/.cognee_system/`. That means
your data lives in a place that disappears with a `pip uninstall` or an
`rm -rf .venv`.

Two lines at the top of the program fix it:

```python
cognee.config.system_root_directory("dati/cognee/sistema")
cognee.config.data_root_directory("dati/cognee/documenti")
```

What you find in there:

| Folder | Contents | Technology |
|---|---|---|
| `documenti/` | the original files, copied | filesystem |
| `sistema/databases/cognee_db` | tables: documents, datasets, runs | SQLite |
| `sistema/databases/cognee.kuzu` | the graph: nodes and edges | Kuzu |
| `sistema/databases/cognee.lancedb` | the vectors | LanceDB |

Three different databases because they serve three different purposes.
Module 6 is devoted to this.

## 5. The failure to see: the model that cannot cope {#5-il-fallimento-da-vedere-il-modello-che-non-ce-la-fa}

Now the useful part. Put the small model in `.env`:

```bash
LLM_MODEL=openai/gpt-oss-20b
```

and run `cognify` again. In all likelihood you get this:

```text
CognifyFailedError: Cognify failed for dataset '['officina']':
BadRequestError: GroqException - {"error":{"message":"Failed to validate
JSON. Please adjust your prompt. See 'failed_generation' for more
details.","type":"invalid_request_error","code":"json_validate_failed"}}
```

It is not your mistake, and changing the prompt does not fix it, even
though that is what the message suggests. This is what is happening:

- to build the graph, cognee asks the model for nested JSON: a list of
  nodes, each with a list of edges, each with constrained types;
- `gpt-oss-20b` manages with a four-field schema (you saw it in module 2),
  but not with this one;
- the provider validates the response against the schema, finds it wrong
  and returns 422 instead of handing you garbage.

**It is lucky that the provider catches the error.** Without strict
validation you would end up with a silently incomplete graph, and you
would find out three months later from a wrong answer.

There is only one cure: **a more capable model for extraction**. Put
`openai/gpt-oss-120b` back and it starts again.

> Note for Ollama or a compatible endpoint: in that case cognee does not
> use the strict schema but asks for "a JSON object" and corrects itself
> if the answer does not fit. It is more tolerant and slower, and it fails
> silently more often. With a local 4-billion-parameter model, expect a
> poorer graph.

## 6. How long it really takes {#6-quanto-ci-mette-davvero}

On the course corpus (12 documents, 14,775 extractable characters: 5
manuals in PDF, one of them scanned and yielding zero, plus 7 notes),
with the Groq free tier and the throttle configured as above:

| Command | Model calls | Measured time |
|---|---|---|
| `add` | 0 | 90 seconds |
| `cognify` | ~24 | **tens of minutes**, almost all waiting |
| `memify` | a few | under a minute |
| `search` | 1-3 | a few seconds |

**And now the number that really matters.** Those ~24 calls, at about
2,100 tokens each, add up to **~50,000 tokens**: a quarter of Groq's daily
quota, which is **200,000 tokens a day**. You can digest this corpus
three or four times in a day.

If you waste nothing.

Because there is a trap, and it is why the throttle above is not a
detail:

> **Every retry after a 429 resends the whole prompt, and it is counted
> again.**

The useful work does not change; the wasted attempts do. On the very
same `cognify` I counted **thirty-one** 429 errors with the throttle
written badly (`2 richieste ogni 60 secondi`, 2 requests every 60
seconds) and **three** with it written well (`1 ogni 30`, 1 every 30).
Thirty-one retries at 2,100 tokens are **65,000 wasted tokens**: more than
the whole job costs.

And when the daily quota really runs out, the message differs from the
one you have already seen:

```text
Rate limit reached ... on tokens per day (TPD): Limit 200000, Used 199852
```

`per day`, not `per minute`. Waiting does not help there: you have to
wait until tomorrow. If you get there, it is almost never because you
digested too much; it is because you retried too much.

So, two things to keep in mind:

| | |
|---|---|
| **the throttle** | it is not politeness toward the provider, it is your quota you are defending |
| **`cognify` is incremental** | if a run stops, the next one picks up, it does not start over |

If you want to try again and again without thinking about it, or if you
have a corpus much larger than this one, `quaderno.py aggiungi --ridotto`
ingests only two appliances instead of five. It is for iterating fast,
not for finishing the course: the full corpus fits comfortably.

The ratio is what counts: **digesting is expensive, asking is almost
free**. You digest once and ask a thousand times. That is why it is
worth building a memory instead of pasting the documents into the prompt
every time.

## 7. What you gained compared with module 4 {#7-cosa-hai-guadagnato-rispetto-al-modulo-4}

| | Hand-made graph | cognee |
|---|---|---|
| Chunking | yours, 30 lines | aware of the document type |
| Extraction | your own schema | richer schema, with summaries |
| Duplicate names | «Lavatrice LAVANOR» and «Lavatrice Lavanor» | `memify` merges them |
| Adding a document | rebuild everything | incremental |
| Retrieval | graph **or** vectors | both together |
| Formats | only `.md` | about forty, PDF and images included |
| Selective deletion | no | yes (module 7) |

And what you did **not** gain: certainty. cognee makes mistakes the way
you did, only in ways that are harder to see. That is what module 8 is
for.

**Now: [LAB.md](LAB.md).**
