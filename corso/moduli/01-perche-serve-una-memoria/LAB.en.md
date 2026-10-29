# Lab 1 — RAG in thirty lines

**Duration: 60 minutes.**

At the end you will have, in the `memoria/` folder of the repository,
two files you will use for the whole course: `llm.py` (the only place
that talks to the model) and `memoria_minima.py` (search, then ask).

---

## Step 0 — The folder of your system (2 minutes)

```bash
mkdir -p memoria
cp moduli/01-perche-serve-una-memoria/starter/llm.py memoria/llm.py
cp moduli/01-perche-serve-una-memoria/starter/memoria_minima.py memoria/
```

**`memoria/` is your system.** It grows with every module. The `starter/`
folders are starting points to copy, the `soluzione/` folders are the
safety net.

Check that the connection to the model works:

```bash
python memoria/llm.py
```

It must print `pronto` (ready). If it prints an error, the diagnosis is
in [CHIAVI.md](../../CHIAVI.md#6-controlla-che-le-chiavi-funzionino).

## Step 1 — Measure the problem (8 minutes)

```bash
python moduli/01-perche-serve-una-memoria/starter/conta_token.py \
  progetto-finale/corpus/manuali/*.md progetto-finale/corpus/note/*.md
```

Note the total. **Write it down somewhere**: in module 3 you will compare
it with how many tokens the system uses once it has learned to search. On
the course corpus it is about 4,400 tokens.

## Step 2 — `cerca()` (25 minutes)

Open `memoria/memoria_minima.py` and write the `cerca()` (search)
function, where TODO 1 is.

It must:

1. reduce the question to a set of words with `normalizza()`;
2. for each document, count how many of those words appear in it;
3. drop the documents with a score of zero;
4. return the first `quanti` (how many), sorted, each with the key
   `"punteggio"` (score).

Try it without spending quota, that is, without calling the model:

```bash
python -c "
import sys; sys.path.insert(0, 'memoria')
from memoria_minima import carica_documenti, cerca
for d in cerca('Che candela monta il rasaerba?', carica_documenti()):
    print(d['punteggio'], d['nome'])
"
```

(The question means: "Which spark plug does the lawn mower take?")

Expected result: `manuali/greencut-rm46.md` and
`note/2026-07-21-rasaerba-non-parte.md`, both with 2 points.

If you get an empty list, you normalized the question but not the
documents (or the other way round).

## Step 3 — `costruisci_contesto()` (10 minutes)

TODO 2. You need a single string, with one block per document:

```text
[documento: manuali/greencut-rm46.md]
# GREENCUT RM-46 ...

[documento: note/2026-07-21-rasaerba-non-parte.md]
# Intervento del 21 luglio ...
```

The file name in front of the text is not a whim: it is what allows the
model to cite the source, and you to check it.

## Step 4 — Try it (5 minutes)

```bash
python memoria/memoria_minima.py "Cosa significa l'errore E4 sulla caldaia Termovex?"
```

You should first see the list of documents used, then an answer that
mentions 0.8 bar, the reset to 1.2 bar and, if retrieval worked well,
also the March 12 note about the expansion vessel.

## Step 5 — Break it (10 minutes)

Now the useful part. Run these three questions and **look at the list of
documents used**, not at the answer:

```bash
python memoria/memoria_minima.py "Quanto devo stringere la vite che tiene la lama?"
python memoria/memoria_minima.py "Perche' il trapano avvitatore si scarica subito?"
python memoria/memoria_minima.py "Il tagliaerba non si accende, cosa devo controllare?"
```

(In English: "How tight should I screw the bolt that holds the blade?",
"Why does the drill driver run flat so fast?", "The lawn mower won't
start, what should I check?")

What you should observe on the course corpus:

| Question | What happens |
|---|---|
| the blade bolt | in first place comes the **note about the bike brakes** (2 points, for «vite» (screw) and «stringere» (tighten)). The lawn mower manual, which contains the answer, 45 Nm, comes second with 1 point |
| the drill running flat | ahead of the right note about the battery, a **note about the washing machine** sneaks in, because it contains the word «scarica» (here: water drain) |
| the lawn mower | three documents **with the same score**: a drill driver, a lawn mower and a washing machine. The winner is decided by alphabetical order, not by relevance. And «tagliaerba» appears in no document: the corpus says «rasaerba» (both mean lawn mower) |

Three different failures with a single root: **we are comparing strings,
not meanings.**

- «scarica» (the battery runs flat) and «scarica» (the water drains) are
  the same string and two different things;
- «tagliaerba» and «rasaerba» are two strings and the same thing;
- a rare word like «45» counts as much as a trivial word like «vite».

In a file of your own, `note-lab1.md`, write in your own words which of
the three seems to you the most serious problem. You will pick it up
again in module 3, where the first two are solved with semantic search
and the third with BM25.

## Step 6 — Check

```bash
python moduli/01-perche-serve-una-memoria/verifica.py
```

It makes two real calls to the model (little quota). It must print `OK`
on every line.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'llm'` | you run the script from another folder | move to the root of the repository |
| `ModuleNotFoundError: No module named 'dotenv'` | virtual environment not active | `source .venv/bin/activate` |
| `NotImplementedError: TODO 1` | you have not written `cerca()` yet | step 2 |
| the list of documents is always empty | `normalizza()` applied only on one side | compare sets of words, not strings |
| `429` | you used up the tokens for the minute | wait 60 seconds. Module 2 |

## What you keep from this module

`memoria/llm.py` and `memoria/memoria_minima.py`, working. Do not delete
them: module 3 starts from here.
