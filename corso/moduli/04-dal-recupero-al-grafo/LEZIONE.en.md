# Module 4 — From retrieval to memory: the graph {#modulo-4-dal-recupero-alla-memoria-il-grafo}

**Duration: 2 hours 30** (48 minutes of lesson, 102 of lab).
Running total: 9.5 / 20 hours.

Module 3 built a search system that works. This module shows you the
class of questions that system **cannot** answer, by design, and what you
need instead.

---

## 1. The first five minutes: the question that breaks everything {#1-primi-cinque-minuti-la-domanda-che-rompe-tutto}

With the module 3 system already in hand:

```bash
python moduli/04-dal-recupero-al-grafo/starter/prova_multihop.py
```

It asks: **«Quante ore ho passato in tutto sulla caldaia?»** ("How many
hours did I spend on the boiler in total?")

Look at what it retrieves:

```text
pezzi recuperati:
   manuali/greencut-rm46.md#5
   note/2026-09-05-lavatrice-cinghia.md#0
   note/2026-05-18-avvitatore-batteria.md#0
   note/2026-06-07-bici-freno-spugnoso.md#0
   note/2026-07-21-rasaerba-non-parte.md#0

RISPOSTA: Non lo so.
```

**None of the five chunks is about the boiler.** Yet the corpus holds two
repair notes on the boiler, and both say how much time the job took.

This is the third failure of the course, and the most instructive one,
because no knob fixes it.

## 2. Why it happened {#2-perche-e-successo}

Search, lexical or semantic, it makes no difference, does one thing only:
it takes the question and looks for the chunk of text **that resembles it
most**.

The question «quante ore ho passato in tutto sulla caldaia» resembles all
the repair notes: they all say «Tempo impiegato: ... ore» (time spent: ...
hours). It also resembles the lawn mower manual, which talks about «ogni
50 ore» (every 50 hours). The word that discriminates, «caldaia»
(boiler), is one out of eight, and it carries little weight.

And even if retrieval were perfect, the real problem would remain:

> **The answer is not written in any chunk.**
> It has to be built: find which repairs concern the boiler, take the
> duration of each, add them up.

This is called **multi-hop**: to answer, you have to follow more than one
link.

```text
    "caldaia"  ──riguarda──  Intervento del 12 marzo  ──è durato──  1,5 ore
               ──riguarda──  Intervento del 30 agosto ──è durato──  2 ore
                                                                    ──────
                                                                    3,5 ore
```

Two hops. Classic RAG does **zero**: it grabs a chunk and feeds it to the
model. Nothing in vector similarity resembles "follow the link".

### Multi-hop questions are not a textbook case {#le-domande-multi-hop-non-sono-un-caso-di-scuola}

They are half the questions people ask their own knowledge base:

| Question | Hops |
|---|---|
| How many hours did I spend on the boiler? | repair → duration |
| Which spare part did I use last time on the bike? | appliance → most recent repair → spare part |
| Have I had this problem on another appliance before? | symptom → repairs → appliances |
| What did I change after the last service? | date → later repairs |

## 3. What you need: entities and relationships {#3-cosa-serve-entita-e-relazioni}

Until now the system saw **text**. From now on it sees **things and links
between things**.

- **Entity** (or **node**): a thing with a name. «Caldaia Termovex
  TX-24», «vaso di espansione» (expansion vessel), «Intervento del 12
  marzo 2026» (repair of March 12, 2026), «1,5 ore».
- **Relationship** (or **edge**): a directed link between two entities,
  with a name. «*Intervento del 12 marzo* **riguarda** *Caldaia Termovex
  TX-24*» (the repair *concerns* the boiler).
- **Triple**: the pair of entities plus the relationship. `(da, relazione, a)`.
  It is the unit of information of a graph.
- **Knowledge graph**: the set of all the triples.

The value is not in any single triple: it is in the fact that they are
**connected**. Two notes written five months apart, from which you
extracted the same node «Caldaia Termovex TX-24», now know about each
other.

## 4. Who builds the graph {#4-chi-costruisce-il-grafo}

Someone has to pull the triples out of the text. Until a few years ago
this was done with hand-written rules, and it worked badly. Today the
model does it, with the **structured output** from module 2: you give it
a JSON schema with "entities" and "relationships", and it fills it in.

There is only one delicate part, and it is worth saying before you run
into it: **the model must always call the same thing the same way**. If
in one document it extracts «Caldaia Termovex TX-24» and in another «la
caldaia» (the boiler), you get two disconnected nodes instead of one, and
multi-hop still fails.

Three ways to limit the damage, all in the lab:

1. **tell the model which entity types you want** (`apparecchio`,
   `componente`, `intervento`, `ricambio`, `sintomo`, `misura`) instead of
   letting it invent them;
2. **ask it for the full name**, not the one that appears in the text;
3. **merge by name** at the end of extraction.

Point 3 is crude, and you know it: «Caldaia Termovex TX-24» and «Termovex
TX-24» stay two nodes. Fixing that is cognee's job (module 5), and
maintenance is module 7.

## 5. Querying a graph {#5-interrogare-un-grafo}

With a graph the question is no longer "which text is similar?" but
"which node do I start from, and how far do I go?".

```text
1. trova il nodo di partenza   ("caldaia" -> Caldaia Termovex TX-24)
2. raccogli tutte le relazioni entro N salti
3. dai quelle relazioni al modello, come fatti
4. il modello risponde, e se serve fa la somma
```

(1. find the start node; 2. collect all relationships within N hops;
3. give them to the model as facts; 4. the model answers, adding up if
needed.)

Step 2 is a **breadth-first** traversal: start from a node, take all its
neighbors, then the neighbors' neighbors. Fifteen lines of Python.

**How many hops?** One is of little use, three drag in half the graph.
Two is almost always the right answer, and it is the value we will use.

## 6. Graph and vectors are not alternatives {#6-grafo-e-vettori-non-sono-alternativi}

The graph is great at following links and terrible at finding the
starting point: «il coso che perde acqua sotto» (the thingy leaking water
underneath) matches no node. Semantic search does the opposite.

A serious system uses both:

| Step | Who does it |
|---|---|
| find where to start | hybrid search (module 3) |
| follow the links | graph (this module) |
| write the answer | the model |

This is exactly cognee's architecture, which you will see in module 5.
Now you build it by hand, small, so you know what is inside.

## 7. What it costs {#7-cosa-costa}

The graph is not free: the model has to read every document.

On the course corpus, 12 documents, one call each, 2,000-3,000 tokens per
call: **about 30,000 tokens**, which at the free tier's 8,000 tokens per
minute means **at least four minutes** of work, much of it spent waiting.

And here you will find out something module 2 promised and has not shown
you yet: **with only one key, the fallback chain is decorative**. When
Groq says 429, the gateway tries Gemini, which without a key answers 401,
then OpenRouter, same thing, and in the end the error comes back to you.
There is no magic: if you do not have a second provider, you do not have a
second provider.

So the only sensible thing is to **wait the right amount of time**. The
provider tells you inside the error message:

```text
Rate limit reached ... Please try again in 1.875s
```

In the lab we give you `pazienza.py`, fifteen lines that read that number
and wait. It is the piece of plumbing that makes any long job possible on
a free tier, and from here on you will always use it.

**Now: [LAB.md](LAB.md).**
