# Final project rubric {#rubrica-del-progetto-finale}

Four levels. Read it before you start: it tells you what matters.

You reach a level when **all** its rows are met, not most of them. A
system that does brilliant things and makes up answers is not at
level 3: it is below level 1.

---

## Level 0 — Not yet {#livello-0-non-ancora}

Any one of these, and one is enough:

- it makes up an answer to D10 (the question with no answer);
- it cannot ingest the corpus without errors;
- it gives the old value (1.2 bar) to D02 after you have done module 7.

The first is the most important, and it is worth saying clearly: **a
system that makes things up is not a weaker system, it is an unusable
one**, because you have to check all its output, and if you have to
check everything you might as well read the manuals.

---

## Level 1 — It works {#livello-1-funziona}

| Requirement | How it is measured |
|---|---|
| it ingests the 4 native manuals and the 7 notes | `manutenzione.py elenca` lists them |
| it answers the factual questions | D01, D07, D11 pass |
| it says "I don't know" to D10 | `verifica.py` from module 8 |
| there is a written evaluation run | a file in `dati/valutazioni/` |
| `RELAZIONE.md` exists and answers the 5 points | |

Typical result: **6-7 out of 12.** OCR, audio and some cross-source
questions are missing.

This level is already a system you would use. It is not a consolation
prize: it queries your manuals in Italian, at zero cost, on your
machine. Six months ago there was no simple way to do that.

---

## Level 2 — It combines sources {#livello-2-incrocia-le-fonti}

All of level 1, plus:

| Requirement | How it is measured |
|---|---|
| the `incrocio` (cross-source) questions pass | D03, D04, D06, D09: at least 3 out of 4 |
| D03 **separates** the two sources | the answer says what comes from the manual and what from the notes |
| D02 gives 1.4 bar with no manual deletions | R5 |
| the summary by type is there, not just the total | |
| adding a note does **not** re-digest everything | R7, with the time measured |

Typical result: **9-10 out of 12.** OCR is missing.

This is the level that shows you understood the course: memory is not
a bigger archive, it is an archive that **puts together** things
written by different people at different times.

---

## Level 3 — It reads everything and listens {#livello-3-legge-tutto-e-ascolta}

All of level 2, plus:

| Requirement | How it is measured |
|---|---|
| the scanned manual got in | D05 and D08 pass (`BPR6ES`, `0,7`, `SAE 30`) |
| the voice notes are transcribed and ingested | D12 gives `5,5` hours |
| the transcriptions are saved and editable | `dati/trascrizioni/` exists |
| the photos are described and linked | "what photos do I have of the boiler?" gets an answer |
| **two** evaluation runs, before and after a change | |
| the report says what the system still gets wrong | point 5 |

Typical result: **11-12 out of 12.**

The last row counts as much as the others. A 12 out of 12 with a report
that says "everything works" is a level 2. You built the yardstick
yourself, and you know it has flaws: snippet matching produces false
positives, twelve questions are few, and the corpus is small and
written for the course, so it is kinder than what you will meet in
real life.

A system whose limits you can list is a system you understand.

---

## What is NOT graded {#cosa-non-viene-valutato}

Because people waste time on it and it does not help.

- **how elegant the code is.** If it runs and is readable a month from now, it is fine.
- **how nice the answers are.** Terse answers are fine too.
- **the interface.** The command line is perfect. If you want a web
  interface, it is an extension, not a requirement.
- **speed.** With free quotas the rate limit is in charge, not your
  code.

---

## Extensions, if you got hooked {#estensioni-se-hai-preso-gusto}

In order of what you learn compared with what it costs.

**1. The voice note that arrives on its own** (1-2 hours)
A watched folder: you drop the `.m4a` in, and a minute later it is
transcribed, corrected, ingested and linked. `watchdog`, twenty lines.
This is the extension that turns an exercise into a tool you use.

**2. The graph, looked at** (30 minutes)
`cognee.visualize_graph()` spits out an HTML file. Open it. Seeing your
knowledge base as a network changes how you think about it, and the
hub nodes from module 7 stand out at a glance.

**3. Mandatory citations** (1 hour)
Ask the model to put the name of the source file next to every
statement. It changes how you use the system: from "I trust it" to
"I check it in two seconds".

**4. Local Whisper** (1 hour)
`faster-whisper`, `small` model, runs in 4 GB without a graphics card.
The voice notes, which hold your voice and your customers' names, no
longer leave home. On Italian the quality is close to Groq's.

**5. The second provider, for real** (1 hour)
Add a Google AI Studio key and put **two deployments with the same
`model_name`** in the gateway. LiteLLM alternates them, and the token
quota doubles: `digerisci` on the corpus drops from half an hour to ten
minutes. It is the real fix for the slowness of module 5.

**6. A second workshop** (2 hours)
Two separate `dataset`s, one per customer, with
`add(dataset_name=...)`. It teaches you data isolation, the first thing
people ask about when more than one person uses a system like this.

**7. The notebook that talks** (2 hours)
Answers read aloud, with `piper` running locally. In the workshop, with
dirty hands, it is the difference between using it and not using it.

---

If you finish one of these, the course worked.
