---
description: A free, hands-on 20-hour RAG chatbot course in Python. Build a personal AI memory with cognee, knowledge graphs and free LLM APIs, at zero cost.
---

# Build your own AI memory

A hands-on 20-hour course. You start from zero and end up with a personal
knowledge base that organizes itself: you pour documents into it, you tell
it things by voice, and it links, updates and answers.

At the end you will have **The workshop notebook**: the manuals of your
appliances and tools, plus your notes on what you found while repairing
them, all searchable together.

An example of a question the system answers at the end of the course:

> "Error E4 on the boiler: what does the manual say, and what did I find
> last time?"

!!! note "About the language of the examples"
    The course was written in Italian. The text is translated, but the
    sample corpus (manuals and repair notes) and the questions in the
    commands stay in Italian, exactly as the code expects them. Every time
    an Italian word matters, the lesson explains it.

## Who it is for

You can install a program, open a terminal, and you have seen some Python
code without writing it every day. You know nothing about artificial
intelligence: that's fine. Every term is explained the first time it
appears, and the [glossary](GLOSSARIO.md) collects them all, one line each.

## What you need

| What | Details |
|---|---|
| Operating system | macOS or Linux. **Windows is not supported**: use WSL2 (Ubuntu), explained in [SETUP.md](SETUP.md) |
| Python | 3.11 or 3.12 |
| Disk | 3 GB free |
| RAM | 4 GB (8 GB if you want to try the local path with Ollama) |
| Money | **zero**. No credit card, at any step |
| Free accounts | Groq, Google AI Studio, OpenRouter — instructions in [CHIAVI.md](CHIAVI.md) |

## Data warning: read it now

Free tiers of model providers are paid for with your data: almost all of
them reserve the right to use what you send to train their models. For
toaster manuals and for learning, that's fine. **Do not put customer
data, other people's personal data, confidential documents or passwords
in it.** If your material is sensitive, the course has an alternative
path that sends nothing outside your computer: Ollama, marked in every
module by the "Local path" box.

## How the course works

Eight modules, plus the final project. Every module starts with something
you run and see working in the first five minutes; the explanation comes
afterwards, to give a name to what you just saw. Every module ends with a
working piece of the program that you keep and reuse in the next module:
the course builds **one single thing**, step by step.

Three times the course makes you build a deliberately wrong version, has
you break it on your own data, and only then gives you the right one. It
is not wasted time: it is the only way to understand why the good
solution is built the way it is.

### Hours

| # | Module | Hours | of which lab | Running total |
|---|---|---:|---:|---:|
| 1 | [Why you need a memory](moduli/01-perche-serve-una-memoria/LEZIONE.md) | 2.0 | 1.0 | 2.0 |
| 2 | [Keys, gateway and quotas](moduli/02-chiavi-gateway-e-quote/LEZIONE.md) | 2.0 | 1.3 | 4.0 |
| 3 | [How a text becomes searchable](moduli/03-testo-cercabile/LEZIONE.md) | 3.0 | 2.0 | 7.0 |
| 4 | [From retrieval to the graph](moduli/04-dal-recupero-al-grafo/LEZIONE.md) | 2.5 | 1.7 | 9.5 |
| 5 | [The cognee pipeline](moduli/05-la-pipeline-di-cognee/LEZIONE.md) | 3.0 | 2.0 | 12.5 |
| 6 | [Where the data lives](moduli/06-dove-vive-il-dato/LEZIONE.md) | 2.0 | 1.4 | 14.5 |
| 7 | [Memory maintenance](moduli/07-manutenzione-della-memoria/LEZIONE.md) | 2.0 | 1.3 | 16.5 |
| 8 | [Evaluating your system](moduli/08-valutare-il-sistema/LEZIONE.md) | 2.0 | 1.4 | 18.5 |
| — | [Final project: the workshop notebook](progetto-finale/BRIEF.md) | 1.5 | 1.5 | **20.0** |

Lab time: **13.6 hours out of 20**.

## How to use this repository

```bash
git clone <indirizzo-del-repo> memoria-ai
cd memoria-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # poi riempi .env seguendo CHIAVI.md
```

The repository is on GitHub:
[JoeBosi/rag-chatbot-course](https://github.com/JoeBosi/rag-chatbot-course)
(the course files are in its `corso/` folder).

All paths in the course are **relative to the root of the repository**.
If a command starts with `python moduli/03-...`, run it from that folder.

Structure of each module:

| File | What it is for |
|---|---|
| `LEZIONE.md` | the lesson. You read it |
| `LAB.md` | the lab. You do it |
| `starter/` | incomplete code: your starting point |
| `soluzione/` | the complete, commented version. Look at it **after** you have tried |
| `verifica.py` | tells you whether the lab worked. Run it on its own |

At the end of every lab:

```bash
python moduli/01-perche-serve-una-memoria/verifica.py
```

The script prints `OK` line by line, or tells you exactly what is missing.

## Suggested reading order

1. [SETUP.md](SETUP.md) — installation, 30 minutes the first time
2. [CHIAVI.md](CHIAVI.md) — the free keys, 20 minutes
3. Module 1, then the others in order
4. [Final project](progetto-finale/BRIEF.md)

If you want to run the knowledge base on a server instead of your laptop:
[SETUP-VPS.md](SETUP-VPS.md).

If you have to **teach** the course, [DOCENTE.md](DOCENTE.md) explains why
it is built this way, which choices were made among the many possible,
and what breaks first.

## License

The **texts** are under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
the **code** under the MIT license: you can reuse and modify them, also
for teaching, as long as you credit the author. Details, libraries and
models used are on the [Credits](CREDITI.md) page; what the site collects
(nothing) is on the [Privacy](PRIVACY.md) page.
