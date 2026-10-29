# Module 8 — Evaluate your own system {#modulo-8-valutare-il-proprio-sistema}

**Duration: 2 hours** (36 minutes of lesson, 84 of lab).
Running total: 18.5 / 20 hours.

So far, every time you changed something, you judged the result by
looking at it. You asked a question, you read the answer, it seemed good
or bad to you.

That does not hold up. Not because it is unscientific, but for a
practical reason: two weeks from now you will change the model, or the
chunk size, and you will have no way to know whether you made it better
or worse. You will notice by chance, on a question you care about, three
weeks later.

You need a measuring stick. This module builds it.

---

## 1. An evaluation set is a list of questions with their answers {#1-un-insieme-di-valutazione-e-un-elenco-di-domande-con-la-risposta}

Nothing more. A file with, for each question:

- the **question**, written the way you would really write it;
- what **must** appear in the answer;
- what **must not** appear;
- where the answer is, and what **type** of question it is.

I have prepared the file for you: `progetto-finale/domande.yaml`, twelve
questions. Open it now and read it, because it is the heart of this
module.

```yaml
- id: D02
  domanda: "A che pressione devo tenere l'impianto della caldaia?"
  fonte: note
  tipo: aggiornato
  attese: ["1,4"]
  vietate: ["1,2 bar a freddo"]
```

(The question means: "At what pressure should I keep the boiler
system?" The forbidden string means "1.2 bar cold". The expected values
keep the Italian decimal comma, because they are matched against Italian
answers.)

The `vietate` (forbidden) field is what poorly made evaluations lack. An
answer can contain the right word **and** be wrong, because it also
contains the old one. "The pressure is 1.2 bar, then raised to 1.4" gets
the point if you only look at the expected values, and it is an answer
that makes you do the job wrong in the workshop.

## 2. Why the questions are split by type {#2-perche-le-domande-sono-divise-per-tipo}

The six types in `domande.yaml` are not a tidy catalog: they are **six
different ways the system can break**, and you measure them separately
because you fix them differently.

| Type | What it tests | If it fails, look at |
|---|---|---|
| `fattuale` | basic retrieval | the chunks, the chunk size |
| `aggiornato` | superseded facts | module 7, the correction note |
| `incrocio` | manual + note together | how many chunks you retrieve, the graph |
| `multi-hop` | chaining two steps | the graph, the links |
| `ocr` | reading scanned PDFs | ingestion, not the model |
| `assente` | saying "I don't know" | the instruction to the model |

(The type names mean: factual, updated, cross-check, multi-hop, OCR,
absent.)

A single average over twelve questions hides all this. If you go from
8/12 to 9/12 you learn nothing. If you go from "3/3 factual, 0/2 ocr" to
"3/3 factual, 2/2 ocr" you know exactly what you fixed.

## 3. The `assente` type, and why it matters more than the others {#3-il-tipo-assente-e-perche-conta-piu-degli-altri}

The file has one question that **has no answer in the corpus**: it is
about an appliance that is not there.

```yaml
- id: D10
  domanda: "Qual e' la pressione di gonfiaggio dei pneumatici della bici?"
  fonte: nessuna
  tipo: assente
```

(The question means: "What is the tire pressure for the bike?")

This question **cannot be scored by fragments**, and it is worth
understanding why before you write the code. If you look for the word
«non» (not), you also accept a made-up answer like "the pressure must
**not** exceed 4 bar". If you look for «non lo so» (I don't know), you
miss it when the system answers "I cannot find this information in the
documents", which is a correct answer.

For this type the script uses its own rule, in two parts:

1. the answer contains one of the ways of admitting ignorance
   («non lo so», «non trovo», «non è presente», «non risulta»…: I don't
   know, I can't find it, it is not there, it does not appear);
2. and it **does not contain a number followed by a unit of measure**.

The second part is the one that matters: a system that comes up with a
number has made it up, however it phrased the sentence.

A system that answers this question with something plausible is
**worse** than one that gets the other eleven wrong, because it gives
you no way to notice. Obvious wrong answers you can check; confident
made-up answers you cannot.

In the final project this is a fail criterion, not one point less.

## 4. How you award the point, without another model {#4-come-si-assegna-il-punto-senza-un-altro-modello}

The elegant way to evaluate is to use a second model as a judge. The way
we use here is **fragment matching**: the answer contains the expected
string, and does not contain the forbidden ones.

It is crude. It has two real flaws, and you need to know them:

1. **false negatives**: the system answers "one point four bar" and you
   look for «1,4». Right answer, point lost.
2. **false positives**: the answer contains «1,4» inside a sentence that
   says the opposite.

It is still the right method to start with, for three reasons: it costs
zero quota, it always gives the same result on the same text, and on
answers that contain a number or a spare part code it is almost always
right.

Choose the expected values accordingly: **numbers and codes, not
sentences.** `"1,4"` and `"BPR6ES"` work. `"devi portare la pressione a"`
(you must bring the pressure to) does not.

## 5. The rule that makes all this useful {#5-la-regola-che-rende-utile-tutto-questo}

**Measure before you change, and measure again after.**

The number alone means nothing: is 9/12 good or bad? Nobody knows. 9/12
when yesterday it was 7/12, and the only thing that changed is the chunk
size, means something.

That is why the lab script writes every run to a file with the date and
the configuration used. An evaluation run you do not write down is a run
thrown away.

## 6. How much measuring costs {#6-quanto-costa-misurare}

Twelve questions are twelve calls to the model (plus retrieval, which is
free because the embeddings live on your computer). On the Groq free
tier, with 1,000 messages a day, you can afford about **eighty
evaluation runs a day**.

It is not a constraint. It is a license: measure every time you touch
something.

A full run takes one to two minutes, almost all spent waiting for the
rate limit. The script puts a pause between one question and the next
on purpose: without it, the first three questions go out together, you
get a 429, and you wait longer.

**Now: [LAB.md](LAB.md).**
