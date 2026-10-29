# Glossary {#glossario}

Every acronym in the course is spelled out the first time it appears, in
the module where you need it. This page is for later, when you meet it
again and don't remember.

In alphabetical order. The "module" column says where it is really
discussed.

---

## Acronyms {#sigle}

| Acronym | Spelled out | In plain words | Module |
|---|---|---|---|
| **ANN** | *Approximate Nearest Neighbors* | Finding similar vectors without comparing them all. It is wrong now and then, and a thousand times faster | 3 |
| **API** | *Application Programming Interface* | The way one program talks to another. Here: how your code talks to the model | 1 |
| **BM25** | *Best Matching 25* | The formula that decides how relevant a document is to the words you searched for. The 25 is the version number, it means nothing | 3 |
| **CSV** | *Comma-Separated Values* | A spreadsheet in text format | 8 |
| **ECL** | *Extract, Cognify, Load* | The three phases of cognee. It is cognee's word for the pipeline | 5 |
| **HNSW** | *Hierarchical Navigable Small World* | The algorithm pgvector uses to find similar vectors quickly. The name describes the structure: layers of shortcuts | 6 |
| **HTTP** | *HyperText Transfer Protocol* | The protocol programs use to talk to each other on the internet. When you read "429", it is an HTTP code | 2 |
| **IDF** | *Inverse Document Frequency* | How rare a word is. "BPR6ES" is rare and weighs a lot; «il» ("the") is everywhere and weighs nothing | 3 |
| **JSON** | *JavaScript Object Notation* | A way to write structured data that programs read without mistakes | 2 |
| **LLM** | *Large Language Model* | The model that writes the answers. "Large" refers to the number of parameters, not to quality | 1 |
| **OCR** | *Optical Character Recognition* | Reading the text inside an image. You need it for scanned PDFs | project |
| **RAG** | *Retrieval-Augmented Generation* | Search first, answer second. The model doesn't answer from memory: it answers from documents you put in front of it | 1 |
| **RPD** | *Requests Per Day* | How many times you can call the model in 24 hours | 2 |
| **RPM** | *Requests Per Minute* | How many times you can call it in one minute | 2 |
| **RRF** | *Reciprocal Rank Fusion* | The way to merge two different rankings by looking at position, not score | 3 |
| **SQL** | *Structured Query Language* | The language you use to query table databases | 6 |
| **TF** | *Term Frequency* | How many times the word appears in the document | 3 |
| **TPD / TPM** | *Tokens Per Day / Per Minute* | How many tokens you can use per day / per minute. **On Groq, TPM is the limit you hit first**, not RPM | 2, 5 |
| **URL** | *Uniform Resource Locator* | A web address | 2 |
| **VPS** | *Virtual Private Server* | A rented computer somewhere, always on | SETUP-VPS |
| **YAML** | *YAML Ain't Markup Language* | A configuration format you can read by eye. You write it with indentation, and indentation matters | 2 |

---

## Terms {#parole}

**Knowledge base / dataset.** A named set of documents. In this course it
is always `officina`. They keep apart things that must not mix, for
example two customers.

**Exponential backoff.** Waiting longer and longer between one attempt
and the next: 1 second, then 2, then 4. It keeps you from making things
worse when a service is struggling. *Module 4.*

**Chunk.** A document split into parts small enough to fit in the
model's context. How you split it changes everything: module 3 proves it
by cutting a table in half. *Module 3.*

**Context / context window.** How much text the model can keep in view
at once. Big doesn't mean it reads it well: see *lost in the middle*.
*Module 1.*

**Cosine / cosine similarity.** How much two vectors point in the same
direction, from -1 to 1. It is the standard way to say "these two texts
talk about the same thing". *Module 3.*

**Cypher.** The language for querying graphs, as SQL is for tables.
*Module 6.*

**Embedding / vector.** A list of numbers that represents the meaning of
a text. Texts that mean similar things have nearby vectors. In the course
we use 384-number ones, computed on your computer. *Module 3.*

**Entity.** A thing the knowledge base knows something about: an
appliance, a spare part, a date. In the graph it is a node. *Module 4.*

**Fallback.** The backup provider the gateway switches to when the first
one doesn't answer. *Module 2.*

**Gateway.** The piece in between your code and the providers. Your code
knows one address only; behind it, the gateway chooses, alternates and
falls back. Here it is LiteLLM. *Module 2.*

**Graph.** Entities linked by relationships. It answers questions that
require chaining two steps. *Module 4.*

**Hub.** A node linked to everything. It looks like richness and it is a
flaw: if «bar» is linked to half the knowledge base, two-hop retrieval
stops being selective. *Module 7.*

**Hybrid (search).** Searching with words **and** with meaning, and
merging the two rankings. In the course it doesn't always win, and
module 3 shows the real numbers. *Module 3.*

**Lost in the middle.** The measured fact that models remember the
beginning and end of a long text well, and the middle badly. It is why
"put everything in the context" doesn't work. *Module 1.*

**Multi-hop.** A question whose answer isn't written anywhere and must be
rebuilt by putting together two or three documents. "How many hours have
I spent on the boiler in total?" *Module 4.*

**pgvector.** The extension that teaches PostgreSQL to search by
similarity. *Module 6.*

**Prompt.** What you send to the model: instructions plus context plus
question. *Module 1.*

**Quantization.** Shrinking a model by rounding its numbers, so it fits
in less memory. It is why a 4-billion-parameter model runs on a laptop.
*Module 2, Ollama.*

**Relationship / edge.** The link between two entities: "the Termovex
TX-24 **fits** the 7832-VE8 expansion tank". *Module 4.*

**Retrieval.** The first half of every RAG: finding the right chunks. If
it goes wrong here, no model fixes it later. *Module 3.*

**Rate limit.** How much you can ask a provider before it tells you to
wait. When it tells you to wait, it answers `429`. *Module 2.*

**Structured output.** Forcing the model to answer in a fixed format,
described with a schema, instead of prose. If the model is small,
sometimes it can't: module 2 shows it live. *Module 2.*

**Token.** The piece of text the model counts: about four characters, or
three quarters of a word. Quotas are measured in tokens. *Module 1.*

**Triple.** Subject-verb-object, the form in which you write a fact in a
graph. *Module 4.*

**Whisper.** The model that transcribes audio. On Groq it is free.
*Final project.*
