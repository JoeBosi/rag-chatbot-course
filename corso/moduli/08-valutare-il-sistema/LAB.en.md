# Lab 8 — Build the measuring stick {#laboratorio-8-costruire-il-metro}

**Duration: 84 minutes.**

You need the gateway running and the **complete** knowledge base, all
twelve documents. If in module 5 you used `--ridotto`, fix it now:

```bash
python memoria/quaderno.py aggiungi      # senza --ridotto
python memoria/quaderno.py digerisci
```

(The comment means: without `--ridotto`.)

`cognify` is incremental: it recognizes the documents already digested
and works only on the new ones.

You need the whole corpus because the twelve questions cover all five
appliances: with only the boiler and the washing machine you would fail
half of them for the wrong reason, that is, because the document is not
there, not because the system gets it wrong.

---

## Exercise 1 — Read the evaluation set (10 minutes) {#esercizio-1-leggere-linsieme-di-valutazione-10-minuti}

```bash
cat progetto-finale/domande.yaml
```

Twelve questions. For each one, before you run anything, write your
prediction on a sheet of paper: **pass or fail?**

This step looks useless and it is not. In twenty minutes you will
compare your prediction with the result, and the questions where you
were wrong are the ones you learn something from. If the result confirms
everything, you learned nothing.

Count how many you predict right. Write down the number.

## Exercise 2 — Ask a question and judge it (20 minutes) {#esercizio-2-fare-una-domanda-e-giudicarla-20-minuti}

Open `starter/valuta.py`.

**TODO 1** is the `giudica(risposta, domanda)` function, the heart of it
all:

```python
def giudica(risposta: str, domanda: dict) -> tuple[bool, str]:
    testo = normalizza(risposta)

    if domanda.get("tipo") == "assente":
        return giudica_assente(testo)

    mancanti = [a for a in domanda.get("attese", [])
                if normalizza(a) not in testo]
    if mancanti:
        return False, f"manca: {', '.join(mancanti)}"

    presenti = [v for v in domanda.get("vietate", [])
                if normalizza(v) in testo]
    if presenti:
        return False, f"contiene il fatto vecchio: {', '.join(presenti)}"

    return True, ""
```

(The messages mean "missing: ..." and "contains the old fact: ...".)

Look at `normalizza()`, which is already written: lowercase, spaces
collapsed, decimal comma and decimal point made the same. You need it
because the model writes «1.4» or «1,4» depending on its mood, and that
is not what you are measuring.

**TODO 2** is `giudica_assente(testo)`, the special rule explained in the
lesson:

```python
AMMISSIONI = ("non lo so", "non trovo", "non e' presente", "non risulta",
              "non compare", "nessuna informazione", "non ho trovato",
              "non viene specificato", "non e' indicato")
NUMERO_CON_UNITA = re.compile(r"\d+[.,]?\d*\s*(bar|psi|atm|kpa)")
```

(`AMMISSIONI` are the Italian ways of admitting "I don't know", "I can't
find it", "it is not there", "no information", and so on.)

Two conditions, both required: there is an admission **and** there is no
number with a unit of measure.

## Exercise 3 — The full run (20 minutes) {#esercizio-3-il-giro-completo-20-minuti}

**TODO 3** is `giro()`: for each question, query the knowledge base,
judge, print, **wait**.

```python
for domanda in domande:
    risposta = await interroga(domanda["domanda"])
    passata, motivo = giudica(risposta, domanda)
    ...
    await asyncio.sleep(PAUSA)
```

`PAUSA` is set to 30 seconds and it is not excessive caution: it is the
budget from module 5 (2 calls per minute). Without it, the first
questions go out in a burst, you get a 429, and the run takes longer.

```bash
python memoria/valuta.py
```

That is twelve questions with the pause: allow **six to seven minutes**.
Go get a coffee. It is not your time, it is the rate limit's time.

When it finishes, compare with your prediction from exercise 1.

## Exercise 4 — The summary by type (15 minutes) {#esercizio-4-il-riassunto-per-tipo-15-minuti}

**TODO 4**: at the end of the run, besides the total, print one line for
each question type.

```
tipo          passate
fattuale         3/3
aggiornato       1/1
incrocio         2/4
ocr              0/2
multi-hop        1/1
assente          1/1
--------------------
totale           8/12
```

Look at your `ocr`. If it is `0/2`, the lawn mower did not get in: its
manual is a scanned PDF and without OCR it does not contain a single
readable character. Check:

```bash
python -c "import pypdf; print(len(pypdf.PdfReader('progetto-finale/corpus/manuali/greencut-rm46.pdf').pages[0].extract_text()))"
```

If it prints `0`, it is not the model getting it wrong: for your system,
that document is a blank page. **No prompt change fixes an empty
document.** The fix is in the final project.

This is the most important lesson of the module: the summary by type
tells you **where to look**, and it stops you from wasting an afternoon
polishing the prompt when the problem is in ingestion.

## Exercise 5 — Leave a record (10 minutes) {#esercizio-5-lasciare-traccia-10-minuti}

**TODO 5**: write the result to `dati/valutazioni/AAAA-MM-GG-HHMM.md`,
with the configuration used at the top:

```markdown
# Valutazione del 2026-09-20 18:42

modello:     openai/gpt-oss-120b via gateway
embedding:   paraphrase-multilingual-MiniLM-L12-v2 (384)
ricerca:     grafo (GRAPH_COMPLETION)
archivio:    12 documenti

| id | tipo | esito | motivo |
|---|---|---|---|
| D01 | fattuale | OK | |
| D05 | ocr | NO | manca: BPR6ES, 0,7 |
```

Without the configuration at the top, in a month you will have a file
with "8/12" and no way to know what it referred to.

## Exercise 6 — Measure a change (9 minutes) {#esercizio-6-misurare-un-cambiamento-9-minuti}

Now the measuring stick is good for something. Change **one thing
only**:

```bash
python memoria/valuta.py --tipo testo
```

Use `RAG_COMPLETION` (retrieval only, no graph) instead of
`GRAPH_COMPLETION`. Compare the two summaries by type.

In `RISPOSTE.md` write:

1. which question type gets worst without the graph;
2. whether any type **improves** without the graph, and why that can
   happen.

The second is not a trick question. The graph adds context, and extra
context can confuse a plain factual question.

---

## Check {#verifica}

```bash
python moduli/08-valutare-il-sistema/verifica.py
```

It does not query the model: it checks your code by judging fake
answers whose outcome is already known. If your `giudica()` gives a
point to «la pressione è 1,2 bar, poi portata a 1,4» (the pressure is
1.2 bar, then raised to 1.4), the check tells you.

**Hand in:** the complete `valuta.py`, a file in `dati/valutazioni/` and
the `RISPOSTE.md` for exercise 6.

Running total: **18.5 / 20 hours.** Next: [the final
project](../../progetto-finale/BRIEF.md).
