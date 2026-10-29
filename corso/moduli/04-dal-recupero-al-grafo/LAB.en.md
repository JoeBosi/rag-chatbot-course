# Lab 4 — Build a graph by hand {#laboratorio-4-costruisci-un-grafo-a-mano}

**Duration: 102 minutes.**

By the end you will have a graph of entities and relationships built from
your documents, and you will answer the question that was impossible in
module 3.

**Quota cost:** about 30,000 tokens, that is four or five minutes of real
work plus the waits. Run it when your quota is fresh; if you are already
halfway through the day, `python memoria/stima_quota.py` tells you whether
you will make it.

---

## Step 1 — See the failure (12 minutes) {#passo-1-vedi-il-fallimento-12-minuti}

```bash
python moduli/04-dal-recupero-al-grafo/starter/prova_multihop.py
```

Look at **which chunks** it retrieves, not at the answer. Not one of them
is about the boiler. Write in `note-lab4.md` why, in your view, the search
picked exactly those five.

## Step 2 — Patience (5 minutes) {#passo-2-la-pazienza-5-minuti}

```bash
cp moduli/04-dal-recupero-al-grafo/starter/pazienza.py memoria/
```

Read it: it is forty lines and there is nothing to write. Two functions:
one reads from the error message how many seconds to wait, the other
retries.

Try it dry:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pazienza import secondi_da_aspettare
class Finto(Exception): pass
print(secondi_da_aspettare(Finto('Rate limit reached. Please try again in 1.875s'), 0))
print(secondi_da_aspettare(Finto('errore generico'), 3))
"
```

It must print `2.375` and `8`. The first is the time stated by the
provider plus half a second of margin; the second is the exponential
backoff when nothing is stated.

## Step 3 — Extraction (35 minutes) {#passo-3-lestrazione-35-minuti}

```bash
cp moduli/04-dal-recupero-al-grafo/starter/grafo.py memoria/
```

Write `costruisci()` (TODO 1). Before running it on the whole corpus, try
extraction on **a single document**, which costs one call:

```bash
python -c "
import sys, json; sys.path.insert(0,'memoria')
from grafo import estrai
from pathlib import Path
t = Path('progetto-finale/corpus/note/2026-03-12-caldaia-e4.md').read_text()
print(json.dumps(estrai(t), indent=2, ensure_ascii=False))
"
```

You must see entities with `nome` and `tipo`, and relationships
`da / relazione / a`. Check three things:

1. is there an entity of type `intervento` with a date in its name?
2. is there a `riguarda` relationship linking it to the boiler?
3. is there a relationship pointing to «1,5 ore» (1.5 hours) or similar?

If the third is missing, the model did not see «Tempo impiegato: 1 ora e
mezza» (time spent: an hour and a half) as a duration. Change
`ISTRUZIONI` to tell it more clearly, and try again: **this is the
craft**, not writing the code.

Then build everything:

```bash
python memoria/grafo.py costruisci
```

It prints one line per document and, when the quota runs out, lines like
`quota esaurita, aspetto 1.9s` (quota exhausted, waiting 1.9s). They are
the sign that `pazienza.py` works. At the end it writes `dati/grafo.json`.

## Step 4 — The traversal (25 minutes) {#passo-4-la-visita-25-minuti}

Write `vicini()` (TODO 2). It is a breadth-first traversal: see the
comment in the file.

```bash
python memoria/grafo.py mostra "caldaia"
```

You must see the relationships that start from the boiler or reach it:
the repairs, the components, the error codes.

With two hops:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from grafo import carica, vicini, trova_nodo
g = carica()
n = trova_nodo(g, 'caldaia termovex')
for s in (1, 2, 3):
    print(s, 'salti ->', len(vicini(g, n, salti=s)), 'relazioni')
"
```

The number must **grow** from 1 to 2 hops and grow little or not at all
from 2 to 3: you have already reached almost all of the subgraph you care
about. That is why two hops is the right choice.

## Step 5 — The impossible answer (15 minutes) {#passo-5-la-risposta-impossibile-15-minuti}

```bash
python memoria/grafo.py chiedi "Quante ore ho passato in tutto sulla caldaia?"
```

Now it must answer **3,5 ore** (3.5 hours), and show the addends: 1.5 on
March 12, 2 on August 30.

If it gets the sum wrong but has the right facts in front of it, the
problem is the model, not the graph: try again with a higher
`max_tokens`, or with a bigger model. If it does not have the facts, the
problem is extraction: go back to step 3.

Try these too:

```bash
python memoria/grafo.py chiedi "Quali ricambi ho usato sulla bici?"
python memoria/grafo.py chiedi "Su quali apparecchi ho lavorato a settembre?"
```

("Which spare parts did I use on the bike?" and "Which appliances did I
work on in September?")

And one that must fail:

```bash
python memoria/grafo.py chiedi "Che pressione hanno le gomme della bici?"
```

("What pressure are the bike tires at?") It is not in the corpus. If the
system makes up a number, write it down: that is the problem of module 8.

## Step 6 — Break the graph on purpose (10 minutes) {#passo-6-rompi-il-grafo-apposta-10-minuti}

Search the graph for all the nodes that name the same appliance:

```bash
python -c "
import json
g = json.load(open('dati/grafo.json'))
for parola in ['caldaia', 'lavatrice', 'rasaerba', 'bici']:
    trovati = [e['nome'] for e in g['entita'] if parola in e['nome'].lower()]
    print(parola, '->', trovati)
"
```

On the course corpus, the boiler usually merges well: a single node, with
three documents as sources. The washing machine almost never does:

```text
lavatrice -> ['Lavatrice LAVANOR WM-700', 'Lavatrice Lavanor WM-700']
```

**Two nodes, because of a difference in capitalization.** They are two
pieces of memory that do not talk to each other: a question that starts
from one does not reach the facts of the other. Your result may differ
from ours (the model is not deterministic on this), but you will
certainly find some duplicates.

Write in `note-lab4.md` how many you found and which ones. You will need
them in module 7, where the problem is tackled for real: normalizing names
by hand fixes capitalization and does not fix «Termovex TX-24» versus «la
caldaia del bagno» (the bathroom boiler).

## Step 7 — Check {#passo-7-verifica}

```bash
python moduli/04-dal-recupero-al-grafo/verifica.py
```

---

## Troubleshooting {#se-qualcosa-non-va}

| Symptom | Cause | Fix |
|---|---|---|
| `json_validate_failed` | model too small for the schema | use `openai/gpt-oss-120b` |
| extraction runs but there are zero relationships | the model did not understand what you want | strengthen `ISTRUZIONI` with an example |
| `429` that never goes away | daily quota exhausted, not the per-minute one | wait until tomorrow or add a provider |
| `vicini()` returns the whole graph | you compare strings without `lower()`, or you do not stop the traversal | check the loop |
| "I don't know" even with the graph | `trova_nodo()` did not catch anything | try naming the appliance in full |

## What you keep from this module {#artefatti-di-questo-modulo}

`memoria/pazienza.py`, `memoria/grafo.py`, `dati/grafo.json`.

From here on you will not build graphs by hand anymore: in module 5
cognee does it. But when cognee gives a strange result, you will know
what to look at.
