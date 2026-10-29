# Lab 7 — Keep the memory alive {#laboratorio-7-tenere-viva-la-memoria}

**Duration: 78 minutes.**

You need the knowledge base from module 5 or 6 already digested, and the
gateway running.

Already digested means **all of it**. Before you start:

```bash
python moduli/05-la-pipeline-di-cognee/verifica.py
```

must pass. The reason is the quota. If the `digerisci` of module 5
stopped halfway, the first `aggiungi` of this lab does not digest only
the new note: `cognify` picks up every document left behind. That is the
right behavior (it resumes where it stopped, it does not redo what is
already there), but it costs as much as a whole corpus, about 50,000
tokens, not the 5,000 of one note. If it happens at the end of the day,
you find the quota used up and the lab stops there.

---

## Exercise 1 — Reproduce the failure (8 minutes) {#esercizio-1-riprodurre-il-fallimento-8-minuti}

```bash
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia Termovex?"
```

(The question means: "At what pressure should I keep the Termovex boiler
system?")

Write the answer on a sheet of paper. Then look at what the system had
in hand:

```bash
python memoria/quaderno.py chiedi "pressione impianto Termovex" --tipo pezzi
```

Two questions to answer before you go on:

1. among the retrieved chunks, is the August 30 note there?
2. if it is **not**, the problem is retrieval. If it **is** and the
   answer stays 1.2 bar, the problem is the model, which did not
   understand which of the two values applies.

They are two different faults and you fix them in two different ways.
Knowing which one you have is half the work.

## Exercise 2 — Add without redoing everything (15 minutes) {#esercizio-2-aggiungere-senza-rifare-tutto-15-minuti}

The folder `progetto-finale/corpus/note/` holds the August 30 note. Let
us simulate the arrival of a new note.

Create `dati/nota-nuova.md`:

```markdown
# Intervento del 15 settembre 2026 — Caldaia Termovex TX-24, via Mazzini 8

Controllo stagionale. Pressione a freddo trovata a 1,35 bar, dentro
tolleranza, non toccata. Pulito lo scambiatore. Sostituito il ricambio
7832-VE8 (vaso di espansione) perche' la precarica era scesa a 0,6 bar.
Tempo: 2,5 ore.
```

(A job on September 15, 2026: seasonal check, cold pressure 1.35 bar,
within tolerance; heat exchanger cleaned; part 7832-VE8, the expansion
vessel, replaced because its pre-charge had dropped to 0.6 bar; 2.5
hours.)

Open `starter/manutenzione.py`. **TODO 1** is the `aggiungi()` function:

```python
await cognee.add(percorso, dataset_name=DATASET)
await cognee.cognify(datasets=[DATASET])
```

Time it:

```bash
time python memoria/manutenzione.py aggiungi dati/nota-nuova.md
```

**Compare** it with the minutes the full `digerisci` of module 5 took.
It should be a fraction: that proves `cognify` is incremental. If
instead it takes the same time, something in the configuration makes it
restart from scratch. Note it down and move on.

Then check that it went in:

```bash
python memoria/quaderno.py chiedi "Quando ho sostituito il vaso di espansione della Termovex?"
```

(The question means: "When did I replace the expansion vessel of the
Termovex?")

## Exercise 3 — List what is inside (10 minutes) {#esercizio-3-elencare-quello-che-ce-dentro-10-minuti}

**TODO 2**, the `elenca()` function. It tells you what the knowledge
base contains and gets you the identifiers you need to update and
delete.

```python
datasets = await cognee.datasets.list_datasets()
for d in datasets:
    documenti = await cognee.datasets.list_data(dataset_id=d.id)
    for doc in documenti:
        print(doc.id, doc.name)
```

```bash
python memoria/manutenzione.py elenca
```

You must see your documents with their identifiers. Keep them handy:
you need them in the next two exercises.

## Exercise 4 — Resolve the contradiction (20 minutes) {#esercizio-4-risolvere-la-contraddizione-20-minuti}

Now let us fix the fault from exercise 1, with the method that works:
the **correction note**.

Create `dati/rettifica-pressione.md`:

```markdown
# Rettifica del 30 agosto 2026 — Caldaia Termovex TX-24

Questa nota SUPERA il valore del libretto e le mie note precedenti.

Pressione di esercizio a freddo: 1,4 bar.
  Valore precedente, non piu' valido: 1,2 bar (libretto e nota di marzo).
Precarica del vaso di espansione: 1,2 bar.
  Valore precedente, non piu' valido: 1,0 bar.

Motivo: impianto su tre piani, con 1,2 bar i radiatori dell'ultimo piano
non scaldavano.
```

(The note OVERRIDES the manual and earlier notes: cold operating
pressure 1.4 bar, previous value 1.2 no longer valid; expansion vessel
pre-charge 1.2 bar, previous 1.0 no longer valid. Reason: a three-floor
system, and at 1.2 bar the top-floor radiators did not heat.)

Add it and digest again:

```bash
python memoria/manutenzione.py aggiungi dati/rettifica-pressione.md
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia Termovex?"
```

Now it must say **1.4 bar**. If it says so and also mentions the old
value, even better: that is exactly what you want from a notebook.

**Question to answer in the module's `RISPOSTE.md`:** why is this note
retrieved and the August 30 one is not, given that they say the same
thing? Look at the words they contain.

## Exercise 5 — Forget (10 minutes) {#esercizio-5-dimenticare-10-minuti}

**TODO 3**, the `dimentica()` function:

```python
await cognee.datasets.delete_data(dataset_id=..., data_id=..., mode="soft")
```

Delete `dati/nota-nuova.md` using the identifier from exercise 3. Then
ask again:

```bash
python memoria/quaderno.py chiedi "Quando ho sostituito il vaso di espansione della Termovex?"
```

It must no longer know. Then check that the rest survived:

```bash
python memoria/quaderno.py chiedi "Cosa vuol dire l'errore E4?"
```

(The question means: "What does error E4 mean?")

This one must still answer. If it is gone too, you used `mode="hard"`
and took away the shared nodes.

Also try throwing away only what was understood, keeping the documents:

```python
await cognee.forget(dataset=DATASET, memory_only=True)
```

Do not do it now on the good knowledge base. Do it when you want to
change the extraction model without reloading the files.

## Exercise 6 — The graph health report (10 minutes) {#esercizio-6-la-relazione-sulla-salute-del-grafo-10-minuti}

**TODO 4**, the `relazione()` function:

```python
await cognee.report(datasets=DATASET, output_path="dati/relazione.md")
```

Open it and look for the **hub nodes** section. Write the top three in
`RISPOSTE.md` and answer: are they real entities (an appliance, a spare
part) or units of measure and generic words?

Also run:

```python
await cognee.validate(dataset=DATASET)
```

and report whether graph and vectors agree.

## Exercise 7 — The backup, and the proof that it works (5 minutes) {#esercizio-7-il-backup-e-la-prova-che-funziona-5-minuti}

```bash
python memoria/manutenzione.py salva dati/backup
```

**TODO 5**: the `salva()` function must do three things, not one:

1. `cognee.export(dataset=DATASET, format="cogx", destination=...)`, plus
   a copy in `format="json"` so you can read it
2. copy the folder of original documents
3. if you are on module 6 with PostgreSQL: `pg_dump`

```bash
docker compose exec -T postgres pg_dump -U cognee cognee > dati/backup/registro.sql
```

Check that the three pieces exist and are not empty:

```bash
ls -la dati/backup/
```

A 0-byte backup is the most common way to find out, six months later,
that you had no backup.

---

## Check {#verifica}

```bash
python moduli/07-manutenzione-della-memoria/verifica.py
```

It checks that `manutenzione.py` has the five functions, that the
correction note is in the corpus, and that the knowledge base answers
1.4 bar.

**Hand in:** the complete `manutenzione.py` and `RISPOSTE.md` with the
answers to exercises 4 and 6.

Running total: **16.5 / 20 hours.** Next: [module 8](../08-valutare-il-sistema/LEZIONE.md).
