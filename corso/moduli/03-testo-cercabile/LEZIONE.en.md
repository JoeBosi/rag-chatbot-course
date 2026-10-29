# Module 3 — How a text becomes searchable {#modulo-3-come-un-testo-diventa-cercabile}

**Duration: 3 hours** (60 minutes of lesson, 120 of lab).
Running total: 7.0 / 20 hours.

In module 1 the search counted shared words and got things wrong in three
different ways. Here you build something that gets far fewer things
wrong, and — more important — you learn to **measure** by how much.

---

## 1. First five minutes: watch a manual break {#1-primi-cinque-minuti-guarda-come-si-rompe-un-manuale}

```bash
python moduli/03-testo-cercabile/soluzione/pezzi.py \
  progetto-finale/corpus/manuali/termovex-tx24.md --cieco
```

(Yes, you are running the solution. Watching it work now is the point;
writing it is the lab.)

The manual is cut every 800 characters. Look at **chunk 2**:

```text
--- pezzo 2 (800 caratteri) ---
one impianto insufficiente** | **Pressione scesa sotto 0,8 bar** |
**Riportare la pressione a 1,2 bar con il rubinetto di riempimento** |
| E5 | Sonda mandata guasta | ...
```

The row for error E4 was **cut in half**: the code «E4» stayed in the
previous chunk, the explanation ended up in this one. Neither chunk, on
its own, answers the question "what does E4 mean".

This is the second failure of the course, and it is not an edge case:
tables, numbered lists and step-by-step procedures are exactly the
content worth storing, and that is what blind cutting ruins.

Now look at the difference:

```bash
python moduli/03-testo-cercabile/soluzione/pezzi.py \
  progetto-finale/corpus/manuali/termovex-tx24.md
```

Eight chunks instead of six, each one a whole section. The error code
table fits entirely inside a single chunk.

## 2. Chunking: why, and how {#2-spezzare-perche-e-come}

### Why {#perche}

You do not index whole documents but **chunks**, for three reasons:

1. **retrieval precision**: if the manual is one single block, searching
   for «E4» returns all of it, including the 40 lines on winter
   storage;
2. **quota**: you send the model 800 characters instead of 4,000;
3. **the model reads better**: less noise around the useful information
   (the *lost in the middle* of module 1).

### How {#come}

| Method | How it works | When it works well |
|---|---|---|
| blind | cuts every N characters | text with no structure, transcriptions |
| with overlap | as above, but repeats the last N characters at the start of the next chunk | softens cuts in the middle of a sentence |
| **by structure** | cuts on headings, paragraphs, blank lines | **documents written by humans: manuals, notes, articles** |

**Overlap** is the band-aid for blind cutting: if you repeat 120
characters, a broken sentence shows up whole in at least one of the two
chunks. It costs space (each chunk contains a bit of the previous one)
and it does not fix the table case.

Cutting **by structure** costs five more lines of code and fixes the
problem at the root: the author of the document already decided where a
topic ends, by putting a heading there. Throwing that information away
and then trying to guess it is a waste.

**Course rule of thumb:** chunks of 600-1,200 characters, cut on
structure when there is one, with 15% overlap when there is not.
Smaller chunks retrieve better but lose context; bigger ones do the
opposite.

## 3. Searching by words, done right: BM25 {#3-cercare-per-parole-fatto-bene-bm25}

The count in module 1 treated all words the same. «45» was worth as much
as «vite» (screw). **BM25** — *Best Match 25*, the twenty-fifth
experiment in a family of formulas from the 1990s, and still the
reference today — fixes three things.

**TF** (*term frequency*). If «pressione» (pressure) appears five times
in a chunk, that chunk is more about pressure than one where it appears
once. But not five times more: the contribution flattens out after the
first occurrences. The knob that sets how fast it flattens is called `k1`
and is 1.5.

**IDF** (*inverse document frequency*). A word that appears in every
document distinguishes nothing: «manutenzione» (maintenance) is
everywhere in our corpus, «BPR6ES» in one place only. The second must
weigh much more. The formula:

```text
idf(parola) = log( (N - n + 0,5) / (n + 0,5) + 1 )
```

where `N` is the number of chunks and `n` how many chunks contain the
word. This is what fixes the module 1 failure on the lawn mower «vite»:
«vite» is common, «lama» (blade) less so, «45» is rare.

**Length.** A long chunk contains more words by chance. BM25 penalizes
it in proportion to how much it exceeds the average length. The knob is
called `b` and is 0.75.

Put together, for each word of the question present in the chunk:

```text
idf(parola) * ( f * (k1+1) ) / ( f + k1 * (1 - b + b * lunghezza/media) )
```

(`parola` = word, `lunghezza/media` = length/average.)

It looks worse than it is: in the lab it is eight lines of Python.

**What BM25 still does not know:** that «tagliaerba» and «rasaerba» are
the same thing (lawn mower). It compares strings. No formula on
frequencies can know that.

## 4. Searching by meaning: embeddings {#4-cercare-per-significato-gli-embedding}

An **embedding** (in the sense of embedding a text in a numeric space) is
a list of numbers that represents the meaning of a piece of text. Our
model produces **384** of them per chunk.

The idea is simple and surprising: a model trained on enough text learns
to put texts that mean similar things close together, even with no
words in common. «Il tagliaerba non parte» and «il motore del rasaerba
non si avvia» (both: "the lawn mower won't start") end up close because
their contexts of use, in the text the model has seen, look alike.

**How close?** You measure it with the **cosine** between the two lists
of numbers, seen as arrows starting from the origin:

```text
coseno = (a · b) / (|a| · |b|)
```

It is 1 if they point in the same direction, 0 if they are
perpendicular. What counts is the **direction**, not the length: a long
text and a short one that say the same thing have a high cosine.

### The model runs on your computer {#il-modello-gira-sul-tuo-computer}

The course uses **fastembed** with
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`: 220 MB,
multilingual (it understands Italian), no GPU, no key.

This is a choice, and it is worth explaining. You can also get
embeddings from Google or OpenAI, and on Gemini it is free. But:

| | Local embeddings | Embeddings via API |
|---|---|---|
| Quota used | **zero** | one call for every chunk, every time |
| Data sent out | **none** | the whole corpus, chunk by chunk |
| Works offline | yes | no |
| Quality on Italian | good | better |
| Speed on 48 chunks | ~2 seconds | depends on network and quota |

In module 5 you will build the graph, and there embeddings are computed
for every chunk. Doing it via API would mean burning the daily quota and
then having nothing left for questions. That is why they are local, and
why they stay local on the "local path" with Ollama too: they are local
already.

If you prefer Google embeddings, in `.env`:

```bash
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIMENSIONS=768
```

### A chunk cannot be longer than 512 tokens {#il-pezzo-non-puo-essere-piu-lungo-di-512-token}

This model has a window of **512 tokens**, about 380 words. A longer
chunk does not raise an error: it gets **truncated**, and the extra part
simply does not end up in the vector. Silently.

That is why the course `.env` contains this line, which would otherwise
look like red tape:

```bash
HUGGINGFACE_TOKENIZER=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

It is there to count tokens **with the same tokenizer as the model**.
Without it, cognee falls back to TikToken, which is from OpenAI and
splits words differently: the count is wrong, chunks come out longer
than you think, and whatever goes over disappears. A failure you never
see happen, and that shows up only as "it never finds this sentence".

If you see `Falling back to TikToken` in the logs, you are missing the
`transformers` package: it is in `requirements.txt` and installs without
PyTorch.

**What embeddings still do not know:** that «E4» and «F03» are two
different codes. To the model they are two short strings, with no
context, almost identical. It is the mirror-image flaw of BM25.

## 5. Numbers, not opinions {#5-i-numeri-non-le-opinioni}

This is why the course has you write both. These are the ten questions
in `domande-ricerca.yaml` measured on the course corpus (48 chunks),
looking at the top 3 results:

| Question | BM25 | semantic |
|---|:---:|:---:|
| Which spark plug does the lawn mower («rasaerba») use? | yes | yes |
| The lawn mower («**tagliaerba**») won't turn on | **NO** | yes |
| The washer («**lavabiancheria**») leaves water | yes | yes |
| What does code **F03** mean? | yes | **NO** |
| What does code E4 mean? | yes | yes |
| What torque do you tighten the blade bolt to? | yes | yes |
| Why does the drill run down («**si scarica**») so fast? | yes | **NO** |
| When did I bleed («**spurgato**») the brakes? | yes | **NO** |
| What pressure should the system be at? | yes | yes |
| I found coins **in the appliance** («nell'elettrodomestico») | **NO** | yes |

And the count at different depths:

| method | top 1 | top 3 | top 5 |
|---|:---:|:---:|:---:|
| BM25 | 4/10 | 8/10 | 10/10 |
| semantic | 5/10 | 7/10 | 8/10 |
| hybrid (RRF) | 4/10 | 8/10 | 10/10 |
| *union* | *7/10* | *10/10* | *10/10* |

Read it carefully, because it contradicts what you read around:

1. **They get different things wrong.** BM25 fails on synonyms, semantic
   search on codes and technical words («spurgato»). It is not a race:
   they are two tools.
2. **The union gets 10/10 in the top 3.** That is: between the two, the
   right answer is **always** there. The problem is not finding it, it
   is putting it on top.
3. **Hybrid does not win on this corpus: it ties with BM25.** 8/10
   against 8/10. Merging two rankings has a cost, and that cost eats the
   gain.

Whoever tells you hybrid search is always better has not measured it on
your corpus. **Now you know how to measure it.**

## 6. Merging the two: RRF {#6-unire-le-due-rrf}

You cannot add up the scores: BM25 gives numbers from 0 to 20, cosine
from -1 to 1. You merge the **positions** in the ranking.

**RRF** = *Reciprocal Rank Fusion*. Each system votes: first place gets
`1/(K+1)`, second `1/(K+2)`, and so on. The votes add up.

```text
punteggio(pezzo) = somma su ogni classifica di  1 / (K + posizione + 1)
```

(score(chunk) = sum over each ranking of 1 / (K + position + 1).)

`K` (usually 60) softens the advantage of the top places. With a small
`K` the first place dominates; with a large `K` widespread placements
count more. On our corpus, changing `K` from 1 to 60 moves the results of
one question in ten: on small corpora it is an overrated knob, and in
the lab you check it.

**The flaw of RRF**, which you see at work in the table above: a chunk
found **by only one system, in first place**, gets a single vote and is
overtaken by mediocre chunks found by both. That is why hybrid loses
"the lawn mower won't turn on", which semantic search ranked first.

### So why do we use it {#allora-perche-la-usiamo}

Because the right question is not "which one wins on the course corpus"
but "which one does the least damage on my corpus, which I do not know
yet". BM25 collapses on a corpus of badly written notes, with synonyms
and abbreviations. Semantic search collapses on code catalogs. Hybrid is
never the best and never a disaster. On a real corpus, bigger and
messier than this one, the advantage shows.

And anyway: **measure it again on yours**. It takes twenty minutes and
you have the script.

## 7. What it does NOT do yet {#7-cosa-non-fa-ancora}

Back to the module 1 question: "how many hours have I spent on the
boiler in total?". None of these three searches can answer it: the
number is not written in any chunk, it has to be rebuilt by putting
together three different notes. You need something that knows those
three notes **talk about the same object**.

That is module 4.

**Now: [LAB.md](LAB.md).**
