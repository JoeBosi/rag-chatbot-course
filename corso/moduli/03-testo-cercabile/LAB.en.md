# Lab 3 — Chunk, search, measure {#laboratorio-3-spezzare-cercare-misurare}

**Duration: 120 minutes.**

At the end you will have four new pieces of your system: `pezzi.py`,
`lessicale.py`, `semantica.py`, `ibrida.py` — and, above all, a way to
know whether a change makes things better or worse.

You do not need the module 2 gateway in this lab: **the model is not
called even once**. Searching uses no quota. Keep this in mind: the
expensive part of the system is the answer, not the search.

---

## Step 1 — Chunking (25 minutes) {#passo-1-spezzare-25-minuti}

```bash
cp moduli/03-testo-cercabile/starter/pezzi.py memoria/
```

Write `spezza_alla_cieca()` (TODO 1) and `spezza_per_titoli()` (TODO 2).

Checks, one at a time:

```bash
python memoria/pezzi.py progetto-finale/corpus/manuali/termovex-tx24.md --cieco
```
must give **6 chunks**, and in chunk 2 the E4 table row is cut.

```bash
python memoria/pezzi.py progetto-finale/corpus/manuali/termovex-tx24.md
```
must give **8 chunks**, one per section, with the error code table
entirely inside a single chunk.

```bash
python memoria/pezzi.py
```
must say `48 pezzi da 12 documenti` (48 chunks from 12 documents).

| If you get | Look at |
|---|---|
| 7 chunks instead of 6 | you are not discarding whitespace-only chunks |
| 9 chunks instead of 8 | you open a new chunk on the first heading too, when the current chunk is empty |
| a number other than 48 | one of the two, or you are including `LEGGIMI.md` |

## Step 2 — BM25 (30 minutes) {#passo-2-bm25-30-minuti}

```bash
cp moduli/03-testo-cercabile/starter/lessicale.py memoria/
```

Two functions: `idf()` (TODO 1) and `punteggio()` (TODO 2). The formulas
are in the lesson, §3, and repeated in the comments.

Try it:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pezzi import carica_pezzi
from lessicale import Bm25
motore = Bm25(carica_pezzi())
for p in motore.cerca('Con che coppia si stringe il bullone della lama?'):
    print(round(p['punteggio'],2), p['id'])
"
```

(The question means: "What torque do you tighten the blade bolt to?")

The first result must come from `manuali/greencut-rm46.md`. **This is
the question the module 1 system got wrong**: there, the note on the
bike brakes came first, because «vite» (screw) and «stringe» (tighten)
counted as much as everything else. Now «lama» (blade) and «45» are rare
and carry weight.

Check that the formula is right and not just plausible:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pezzi import carica_pezzi
from lessicale import Bm25
motore = Bm25(carica_pezzi())
print('idf di una parola rara (bpr6es):', round(motore.idf('bpr6es'), 3))
print('idf di una parola comune (il):  ', round(motore.idf('il'), 3))
"
```

(It prints the idf of a rare word and of a common word.)

The first must be much larger than the second. If they are equal, you
are counting total occurrences instead of the number of documents the
word appears in.

## Step 3 — Embeddings and cosine (30 minutes) {#passo-3-embedding-e-coseno-30-minuti}

```bash
cp moduli/03-testo-cercabile/starter/semantica.py memoria/
```

TODO 1 is the cosine, TODO 2 is the search.

**The first run downloads 220 MB** of model and takes a couple of
minutes. It happens only once; the model stays in the `fastembed`
cache.

Before you write `cerca()`, get a feel for what you have:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from semantica import vettori, similitudine_coseno
v = vettori(['il rasaerba non parte',
             'il tagliaerba non si avvia',
             'la caldaia va in errore E4'])
print('rasaerba vs tagliaerba:', round(float(similitudine_coseno(v[0], v[1:2])[0]), 3))
print('rasaerba vs caldaia:   ', round(float(similitudine_coseno(v[0], v[2:3])[0]), 3))
"
```

(The sentences mean: "the lawn mower won't start", "the lawn mower won't
start" with different words, "the boiler shows error E4".)

Two sentences with **no words in common** (apart from «non») must come
out much more similar to each other than to the third. If the two
numbers are almost the same, the cosine is wrong: you probably forgot to
divide by the lengths.

Then the search:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pezzi import carica_pezzi
from semantica import Semantica
for p in Semantica(carica_pezzi()).cerca('Il tagliaerba non si accende'):
    print(round(p['punteggio'],3), p['id'])
"
```

(The question means: "The lawn mower won't turn on".)

The lawn mower manual must appear near the top, **even though the word
«tagliaerba» is not written anywhere in the corpus**. This is the module
1 failure, fixed.

## Step 4 — Merging (15 minutes) {#passo-4-fondere-15-minuti}

```bash
cp moduli/03-testo-cercabile/starter/ibrida.py memoria/
```

A single function, `fondi()`. Watch out for two things: a chunk's
identity is `pezzo["id"]` (not the text, not the file name), and the
final score replaces the scores of the two original systems.

## Step 5 — Measuring (15 minutes) {#passo-5-misurare-15-minuti}

This is the step the whole module is worth.

```bash
python moduli/03-testo-cercabile/starter/confronta.py
```

You must get exactly these numbers (the corpus is fixed, the model is
deterministic):

```text
metodo        primi 1  primi 3  primi 5
BM25            4/10     8/10    10/10
semantica       5/10     7/10     8/10
ibrida          4/10     8/10    10/10
-- unione       7/10    10/10    10/10
```

If they do not match, you got something wrong in the previous steps: the
comparison is also a test.

Now answer these questions by looking at the table, not your gut:

1. Which method gets "What does code F03 mean?" wrong, and why?
2. Does hybrid, in the top 3, do better than BM25 alone? (No.) So why
   does the course make you write it?
3. The "union" row says 10/10 in the top 3. What does that mean,
   exactly, for the work that remains to be done?

The answers are in the lesson, §5 and §6. Write them in your own words
in `note-lab3.md`: you will need them in module 8.

## Step 6 — Free experiment (5 minutes) {#passo-6-esperimento-libero-5-minuti}

Change `K` in `memoria/ibrida.py` from 60 to 1, run `confronta.py` again.
Change `MISURA_PEZZO` in `memoria/pezzi.py` from 800 to 400, run it again.
Set `per_titoli=False` in `confronta.py`, run it again.

Note what happens. It is the first taste of module 8: **you do not tune
the knobs by feel, you measure**.

## Step 7 — Check {#passo-7-verifica}

```bash
python moduli/03-testo-cercabile/verifica.py
```

---

## Troubleshooting {#se-qualcosa-non-va}

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: fastembed` | wrong environment | `source .venv/bin/activate` |
| the model download hangs | slow network or proxy | run it again: it resumes where it stopped |
| `ValueError: la sovrapposizione deve essere minore del pezzo` | you swapped the parameters | `misura > sovrapposizione` |
| all cosines are 1 | you are comparing a vector with itself | check the indexes |
| BM25 gives negative scores | the `+1` inside the IDF logarithm is missing | reread the formula |

## What you keep from this module {#artefatti-di-questo-modulo}

`memoria/pezzi.py`, `memoria/lessicale.py`, `memoria/semantica.py`,
`memoria/ibrida.py`. In module 5 cognee will do all of this by itself:
but now you know what it does, and you could do it again.
