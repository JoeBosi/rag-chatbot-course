# Final project — The workshop notebook {#progetto-finale-il-quaderno-di-officina}

**Duration: 1.5 hours** (all lab).
Running total: 20.0 / 20 hours.

---

## The situation {#la-situazione}

You do maintenance. Boilers, appliances, tools, bikes: things that
come with a manual and that break in ways the manual does not cover.

You have two kinds of knowledge, and they live in two different places.

The **manual** says what error E4 means. It is well written, precise,
and the same for everyone who owns that boiler.

**Your notebook** says that the last time you saw E4 on that boiler on
Via Mazzini it was not the pressure, it was a deflated expansion
vessel, and that it took you an hour and a half. That is in no manual
and nobody else has it. It is the part that is worth something.

Six months from now E4 comes back. You still have the manual. You
remember 20 % of your notebook.

**The project is to build the notebook that remembers for you.**

---

## What it must do {#cosa-deve-fare}

Seven requirements. The first four are mandatory, the other three
raise your grade.

### R1 — Ingest the manuals, scanned ones included {#r1-ingerire-i-manuali-compresi-quelli-scansionati}

The corpus has five PDF manuals. Four are native PDFs and can be read.
The fifth, `greencut-rm46.pdf`, is a photo of a paper booklet: for your
system, today, it is a blank page.

```bash
python -c "import pypdf; print(len(pypdf.PdfReader('progetto-finale/corpus/manuali/greencut-rm46.pdf').pages[0].extract_text()))"
```

It prints `0`. No prompt tweak fixes an empty document: it has to be
read first. You have two paths, and both are fine.

| Path | How | Cost | Privacy |
|---|---|---|---|
| multimodal model | `memoria-occhi` in the gateway (Gemini) | free quota | the pages leave home |
| local OCR | `pip install "cognee[rapidocr]==1.6.0"` | zero | nothing leaves |

If you pick the first, reread the warning at the bottom of this page
before you send out a scan.

**Proof it is done:** question D05 (`BPR6ES`, `0,7`) passes.

### R2 — Accept end-of-job notes, written or dictated {#r2-accettare-le-note-a-fine-lavoro-scritte-o-dettate}

Written is easy: a Markdown file in a folder, `add` + `cognify`.

Dictated is the point. In `corpus/audio/` there are two `.m4a` voice
notes, the kind you record in the car on the way back from a job, when
you cannot write. They must be **transcribed automatically** and end up
in the knowledge base like the others.

The gateway already has `memoria-orecchie` (Whisper on Groq, free).
Quota: 20 transcriptions per minute, 2,000 per day. That is not a
problem.

```python
with open(percorso, "rb") as audio:
    trascrizione = await client.audio.transcriptions.create(
        model="memoria-orecchie", file=audio, language="it")
```

Save the transcription as a text file **before** you feed it to `add`,
for a practical reason: Whisper gets spare part codes wrong, and you
must be able to open the file and fix `7845 NTC` into `7845-NTC`
without transcribing again.

**Proof it is done:** question D12 passes with `5,5` hours. Before you
ingest the voice note of 12/09 the right answer is `3,5`: if your
system still says 3.5, the audio did not get in.

### R3 — Answer questions that combine manual and experience {#r3-rispondere-a-domande-che-incrociano-libretto-ed-esperienza}

This is why the project exists.

> «L'errore E4 sulla caldaia: cosa dice il libretto e cosa ho trovato io
> l'ultima volta?»

(Error E4 on the boiler: what does the manual say, and what did I find
last time?)

A good answer has **two parts, labeled as such**: what the manual says,
what your notes say. An answer that blends them into one paragraph
without saying where each thing comes from is a worse answer, even
when the facts are right — because in the workshop you need to know
whether you are trusting the manufacturer or yourself six months ago.

**Proof it is done:** the four `incrocio` (cross-source) questions
(D03, D04, D06, D09) pass, and the answer to D03 separates the two
sources.

### R4 — Say "I don't know" {#r4-dire-non-lo-so}

D10 asks for the bike's tire pressure. It is not written anywhere.

A system that comes up with a plausible number has failed the project,
no matter how the other eleven questions went. In the workshop a
made-up, confident answer has you inflate a tire to 6 bar.

**Proof it is done:** D10 passes with `verifica` from module 8.

### R5 — Update without deleting by hand {#r5-aggiornarsi-senza-cancellare-a-mano}

The boiler pressure went from 1.2 to 1.4 bar. The manual still says
1.2, and it will keep saying so.

The system must answer **1.4** without you deleting anything. Module 7
gave you the way: the correction note.

**Proof it is done:** D02 passes, and does not contain the old value.

### R6 — Photos {#r6-le-foto}

In `corpus/foto/` there are four images. In the workshop you take
photos of the rating plate, the broken part, the display with the
error code: it is the fastest way to take a note.

They must be described by a multimodal model (`memoria-occhi`) and the
description must be linked to the right appliance. A photo described
as "a display showing E4" with no link to the Termovex is useless.

**Proof it is done:** ask the system «che foto ho della caldaia?»
(what photos do I have of the boiler?) and it answers.

### R7 — Don't start from scratch every time {#r7-non-ripartire-da-zero-ogni-volta}

The system must handle real use: a new note every evening, without
re-digesting the whole knowledge base. That is module 7, exercise 2.

**Proof it is done:** adding a note takes a fraction of the time of a
full `digerisci`, and you measured that time.

---

## What you hand in {#cosa-consegni}

```
quaderno/
  ingerisci.py        R1, R2, R6: manuali, audio, foto
  quaderno.py         l'interrogazione (dal modulo 5)
  manutenzione.py     R5, R7 (dal modulo 7)
  valuta.py           il metro (dal modulo 8)
  dati/
    valutazioni/      almeno due giri, prima e dopo un cambiamento
    trascrizioni/     le note vocali in testo, correggibili a mano
  RELAZIONE.md
```

`RELAZIONE.md` (the report) is two pages, no more, and answers five
questions:

1. which path you chose for the scanned PDFs, and why;
2. the result of the **first** evaluation run, by type;
3. what you changed after reading it;
4. the result of the **last** run, by type;
5. **one thing the system still gets wrong**, and what it would take
   to fix it.

Point 5 is not a formality. A system whose flaws you can list is a
system you understand. A report that says "everything works" is worth
less than one that says "it gets two-hop questions wrong if the keyword
does not appear in the first note".

---

## Where you start {#da-dove-parti}

The corpus is ready in `progetto-finale/corpus/`:

| Folder | Contents |
|---|---|
| `manuali/` | 5 appliances, in Markdown and PDF (one scanned) |
| `note/` | 7 job notes, with a deliberate contradiction |
| `audio/` | 2 voice notes in Italian |
| `foto/` | 4 images |

The appliances are made up but realistic: Termovex TX-24 boiler,
Lavanor WM-700 washing machine, Ferrex ID-18 impact driver, Velomonte
Trail 275 bike, Greencut RM-46 lawn mower.

The evaluation questions are in `progetto-finale/domande.yaml`.

---

## How you grade yourself {#come-ti-valuti}

The grid is in [RUBRICA.md](RUBRICA.md). Read it **before** you start:
it is written to tell you what matters, not to judge you at the end.

---

## Warning, the second time {#avvertenza-la-seconda-volta}

You already read it in [SETUP.md](../SETUP.md). It is worth repeating
here, because this is when it becomes concrete.

**Free tiers are paid for with what you send into them.** Groq,
Google AI Studio and OpenRouter, on their plans without a credit card,
reserve the right to use your requests to improve their models. It is
not a hidden trick, it is written in their terms.

For this course's corpus it does not matter: they are manuals of
made-up appliances.

For your real notebook **it does**. Job notes contain customer
addresses, names, sometimes phone numbers. Photos of rating plates
contain serial numbers. Voice notes contain your voice.

Three rules, in order of strength:

1. **Don't pour customer data into it.** No exceptions, no "it's just
   a test anyway" shortcuts.
2. If you need your real notebook, **switch to Ollama**: you change two
   lines in `.env`, module 2 explains which, and from then on nothing
   leaves your computer. The system gets slower and the answers a bit
   worse. It is a fair price.
3. If you really must use the free APIs on real data, **first remove
   what identifies people**: addresses, names, phone numbers. By hand,
   or with a script you write yourself. Not by handing the job to the
   model you are sending the data to.

This is one of the few things in the whole course where there is no
reasonable compromise. Everything else can be fixed later; this
cannot.
