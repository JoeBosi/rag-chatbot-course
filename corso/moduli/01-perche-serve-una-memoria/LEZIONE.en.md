# Module 1 — Why you need a memory

**Duration: 2 hours** (45 minutes of lesson, 60 of lab, 15 to set up the
keys). Running total: 2.0 / 20 hours.

Prerequisites: [SETUP.md](../../SETUP.md) done, Groq key obtained as
explained in [CHIAVI.md](../../CHIAVI.md#1-groq).

---

## 1. The first five minutes: do it now

There is nothing to understand yet. Run:

```bash
python moduli/01-perche-serve-una-memoria/starter/chiedi.py \
  "Cosa significa l'errore E4 sulla caldaia Termovex TX-24 e come si risolve?"
```

(The question means: "What does error E4 on the Termovex TX-24 boiler
mean, and how do you fix it?")

Read the answer. It arrives in two seconds, it is well written, it is
detailed. And it is almost certainly **made up**.

The Termovex TX-24 boiler does not exist: we invented it for this
course. The model does not say so. It gives you a plausible procedure,
with plausible numbers, because its job is to produce plausible text.

Now compare it with the real manual, in
`progetto-finale/corpus/manuali/termovex-tx24.md`, section 2.1. Usually
the model gets the general idea right (the pressure) and everything else
wrong: the reset value, the name of the part, the procedure.

**This is the problem the course solves.**

## 2. What happened, with the right names

**LLM** stands for *Large Language Model*. It is a program trained to
predict the next word on a huge amount of text. It has no archive to
pick from: it has numeric weights that summarize the regularities of the
language it has seen.

**Token.** The model does not work with letters but with *tokens*, pieces
of words. «caldaia» (boiler) is one token, «Termovex» takes three or four
because it is a word the model has never seen. You need to know this for
two reasons: free quotas are counted in tokens, and so are length limits.

**Hallucination.** When the model produces a false statement in the same
confident tone as a true one. It is not a malfunction: it is the normal
functioning applied to something it does not know. A model has no way to
tell "I remember" from "I just made it up", because it remembers nothing:
it generates.

**Prompt.** The text you send it. Everything the model knows about your
question, at that moment, is in there.

## 3. Second round: give it the manual

```bash
python moduli/01-perche-serve-una-memoria/starter/chiedi.py \
  --con-manuale progetto-finale/corpus/manuali/termovex-tx24.md \
  "Cosa significa l'errore E4 sulla caldaia Termovex TX-24 e come si risolve?"
```

Now the answer is right: 0.8 bar, blue tap, reset to 1.2 bar, and the
warning that if it keeps coming back the cause is something else.

The model did not change. The **context** did: the manual ended up
inside the prompt, and the model could read it instead of inventing it.

> **Box — Local path**
> With Ollama it is the same: `chiedi.py` reads `LLM_PROVIDER` from `.env`
> and talks to the local model without you changing a line. The answer
> comes slower and sloppier, but the reasoning of the module holds just
> the same. See [SETUP.md](../../SETUP.md#strada-locale-ollama).

## 4. Why it does not end here

If the solution were "paste everything into the prompt", the course would
end on page one. It does not work, for four reasons you can measure
yourself.

### 4.1 It does not fit

Every model has a **context window**: the maximum number of tokens it can
read at once. Our manual fits easily. Five fifty-page manuals, plus two
years of notes, do not.

### 4.2 It costs quota, and quota runs out

The Groq free tier gives **8,000 tokens per minute**. The Termovex manual
alone takes about 890. The five manuals of the corpus together are about
3,200 tokens: 40% of one minute's quota for **a single question**, which
means two questions in a row and you are stuck waiting. And these are
five little two-page manuals, not twenty real ones. Measure it yourself:

```bash
python moduli/01-perche-serve-una-memoria/starter/conta_token.py \
  progetto-finale/corpus/manuali/*.md
```

### 4.3 More context, worse answers

It is counterintuitive but documented: when the useful material sits in
the middle of a lot of useless material, models find it less often. The
phenomenon is called *lost in the middle*, and it is described in
<https://arxiv.org/abs/2307.03172>. In the lab you will see it happen.

### 4.4 It is slow

The model has to read everything every time. Thirty thousand tokens of
manuals mean a few seconds of waiting for every single question, every
time, even to ask which spark plug the lawn mower takes.

## 5. The idea: search first, ask afterwards

Instead of giving it everything, we give it **only the piece it needs**:

1. the question arrives;
2. a program searches the documents for the pieces that are relevant;
3. those pieces go into the prompt, together with the question;
4. the model answers using them.

This pattern has a name: **RAG**, *Retrieval-Augmented Generation*.
Retrieval because you retrieve first, augmented because the prompt is
enriched, generation because in the end it is the model that writes the
answer.

Three properties you gain right away:

| | Without RAG | With RAG |
|---|---|---|
| Source of the answer | the model's weights | your documents |
| Verifiable? | no | yes: you know which pieces it read |
| Updatable? | only by retraining | you change the document |

And one you do **not** gain: RAG does not eliminate hallucinations, it
makes them *controllable*. If retrieval brings the wrong piece, the model
answers wrong with the same confidence as before. That is why module 8 is
about measuring, not trusting.

## 6. The thirty lines

In the lab you write the dumbest possible version of a RAG:

- the documents are the Markdown files of the corpus;
- the search counts how many words of the question appear in each
  document;
- the three documents with the highest score go into the prompt.

It works. On some questions it is already useful. On others it fails
badly, and that failure is module 3.

## 7. What it does NOT do yet, and in which module we fix it

| Problem you will see in the lab | Fixed in |
|---|---|
| If you ask «perde acqua» (it leaks water) it does not find «trafilamento» (seepage): it searches words, not meanings | module 3 |
| It takes the whole document, even when one paragraph is enough | module 3 |
| It cannot answer "how many hours have I spent on the boiler?": it has to combine several notes | module 4 |
| If two notes contradict each other, it uses whichever comes up | module 7 |
| You do not know whether it answers well: you judge by gut feeling | module 8 |

## 8. Before moving on to the lab

Three words we will use from now on:

| Word | Meaning in one line |
|---|---|
| Corpus | the set of documents the system knows |
| Retrieval | choosing which pieces of the corpus to send to the model |
| Context | the material that goes into the prompt together with the question |

All the others are in the [glossary](../../GLOSSARIO.md).

**Now: [LAB.md](LAB.md).**
