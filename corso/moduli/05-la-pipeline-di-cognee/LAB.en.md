# Lab 5 — The notebook, with cognee underneath {#laboratorio-5-il-quaderno-con-cognee-sotto}

**Duration: 120 minutes**, a good part of them spent waiting: bring
something to read, or start `digerisci` and go get a coffee.

By the end you will have `memoria/quaderno.py`: a single program holding
your whole system, and the knowledge base built on the full corpus.

**Before you start**, check three things:

```bash
python memoria/stima_quota.py progetto-finale/corpus/manuali/*.md \
                              progetto-finale/corpus/note/*.md
python moduli/02-chiavi-gateway-e-quote/starter/controlla_chiavi.py
```

If you have fewer than 100,000 tokens left for today, put it off:
`cognify` eats them.

The gateway must be running, and in `.env` you need **`LLM_MODEL` with
the `openai/` prefix**:

```bash
LLM_PROVIDER=custom
LLM_ENDPOINT=http://localhost:4000/v1
LLM_MODEL=openai/memoria-veloce
LLM_API_KEY=sk-memoria-locale
```

The `openai/` prefix tells cognee "this is an OpenAI-compatible
endpoint". Without it, cognee does not know who it is talking to and
stops.

---

## Step 1 — The round on a single note (15 minutes) {#passo-1-il-giro-su-una-nota-sola-15-minuti}

```bash
python moduli/05-la-pipeline-di-cognee/starter/primo_giro.py
```

Two documents, one question. Watch the logs scroll by: you will recognize
the names of the phases from the lesson (`classify_documents`,
`extract_chunks`, `extract_graph`, `summarize_text`).

If it ends with an answer that cites **both** the 0.8 bar from the
manual **and** the expansion vessel from your note, the pipeline works.

## Step 2 — Your program (35 minutes) {#passo-2-il-tuo-programma-35-minuti}

```bash
cp moduli/05-la-pipeline-di-cognee/starter/quaderno.py memoria/
```

Three TODOs, one per operation: `aggiungi()`, `digerisci()`, `chiedi()`.
They are three calls to cognee: the hard part is not writing them, it is
knowing what they do.

Before running, look at where the data will end up:

```bash
python memoria/quaderno.py stato
```

It must say `dati/cognee`, **not** a folder inside `.venv`. If it says
`.venv`, you deleted the two `cognee.config` lines: put them back.

## Step 3 — Digest the whole corpus (30 minutes, almost all waiting) {#passo-3-digerisci-tutto-il-corpus-30-minuti-quasi-tutti-di-attesa}

```bash
python memoria/quaderno.py azzera
python memoria/quaderno.py aggiungi
python memoria/quaderno.py digerisci
```

`aggiungi` finishes in a minute. `digerisci` does not.

It costs about **50,000 tokens**, a quarter of the daily quota: you can
afford it three or four times a day. But only if you do not retry in
vain; the lesson, section 6, explains why 429s cost more than the real
work.

If you want to iterate fast without using up quota, there is
`python memoria/quaderno.py aggiungi --ridotto`: it ingests only the
boiler and the washing machine, 6 documents instead of 12. You do not
need it to finish the module, and for module 8 you will need the full
corpus anyway.

**Look at what you just poured in.** From here on the manuals go in as
**PDF**, not as the Markdown sources I generated them from: that is the
form they reach you in real life. And one of the five does not go in at
all:

```bash
python -c "import pypdf; print(len(pypdf.PdfReader(
    'progetto-finale/corpus/manuali/greencut-rm46.pdf'
    ).pages[0].extract_text()))"
```

It prints `0`. `greencut-rm46.pdf` is a photo of a paper manual, and to
your system it is a blank page. From now on, the lawn mower is not in
your knowledge base.

Do not fix it now. It is the wall you break open in the final project,
and it is also why in module 8 you will see an `ocr 0/2` line in the
summary: it is there to show you that **no prompt change fixes an empty
document**.

While it runs, read the logs. You will see this line appear on its own:

```text
Potential RPM issues detected (RateLimitError) — slowing down processing
to accommodate: enabling the RPM limiter (60 requests per 60s)
```

That is cognee noticing the 429s and **slowing down on its own**. It is
the same thing you wrote by hand in `pazienza.py` in module 4, done by
the engine.

Then:

```bash
python memoria/quaderno.py arricchisci
```

## Step 4 — Ask (20 minutes) {#passo-4-chiedi-20-minuti}

The same course questions, now to cognee:

```bash
python memoria/quaderno.py chiedi "Cosa significa l'errore E4 sulla caldaia?"
python memoria/quaderno.py chiedi "Quante ore ho passato in tutto sulla caldaia?"
python memoria/quaderno.py chiedi "Che candela monta il rasaerba?"
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto?"
```

("What does error E4 on the boiler mean?", "How many hours did I spend on
the boiler in total?", "Which spark plug does the lawn mower take?",
"What pressure should I keep the system at?")

The last one is the one that counts: the manual says 1.2 bar, the August
30 note says 1.4. **See which of the two answers you.** If it gives you
1.2, it is not a bug: it is the problem you will tackle in module 7.

Now compare the search types on the same question:

```bash
python memoria/quaderno.py chiedi --testo "Quante ore ho passato sulla caldaia?"
python memoria/quaderno.py chiedi --grafo "Quante ore ho passato sulla caldaia?"
python memoria/quaderno.py chiedi --pezzi "Quante ore ho passato sulla caldaia?"
```

The third command does not answer: it shows you **what it retrieved**. It
is the tool you will use every time an answer looks wrong, to find out
whether retrieval or the model got it wrong.

Write in `note-lab5.md` which of the three types answers best, and why.

## Step 5 — Break the pipeline (15 minutes) {#passo-5-rompi-la-pipeline-15-minuti}

Put in `.env`:

```bash
LLM_MODEL=openai/memoria-piccola
```

after adding to the gateway's `config.yaml`:

```yaml
  - model_name: memoria-piccola
    litellm_params:
      model: groq/openai/gpt-oss-20b
      api_key: os.environ/GROQ_API_KEY
```

Restart the gateway, then:

```bash
python memoria/quaderno.py azzera
python memoria/quaderno.py aggiungi
python memoria/quaderno.py digerisci
```

Most likely it stops with `json_validate_failed`. Copy the error message
into `note-lab5.md` and write next to it, in your own words, why
**changing the prompt does not help** even though the error suggests it.

Then put `openai/memoria-veloce` back and rebuild: you need it for
module 6.

## Step 6 — See where your knowledge base lives (5 minutes) {#passo-6-guarda-dove-abita-il-tuo-archivio-5-minuti}

```bash
python memoria/quaderno.py stato
ls -la dati/cognee/sistema/databases/
```

Three databases, three technologies: SQLite, Kuzu, LanceDB. That is the
topic of module 6.

## Step 7 — Check {#passo-7-verifica}

```bash
python moduli/05-la-pipeline-di-cognee/verifica.py
```

---

## Troubleshooting {#se-qualcosa-non-va}

| Symptom | Cause | Fix |
|---|---|---|
| `ProviderNotDeducibleError` | `LLM_MODEL` without `openai/` in front | `LLM_MODEL=openai/memoria-veloce` |
| `json_validate_failed` | model too small | `openai/gpt-oss-120b` |
| `Could not load a matching tokenizer ... falling back to TikToken` | `transformers` is missing, or `HUGGINGFACE_TOKENIZER` is missing from `.env` | `pip install -r requirements.txt` and check `.env`: with TikToken the chunks are sized wrong and the embedding model cuts off their tail without warning (module 3) |
| `LLM connection test timed out after 30s` | the gateway is running but cannot get the model to answer | `curl localhost:4000/health/liveliness` only tells you the gateway is alive, not that the model answers. Try `python memoria/llm.py`, which must print `pronto`: if that hangs too, stop the gateway and start it again |
| `cognify` stops halfway with 429 | daily quota exhausted | tomorrow, or add a provider to the gateway |
| `No deployments available for selected model, Try again in N seconds` | it is not a provider limit: it is the **gateway** that benched all its providers after the 429s | wait the seconds it says. That number is not your `cooldown_time`: when a provider answers 429, LiteLLM uses the time the provider itself stated, which on the free tier can be half an hour |
| the data ends up in `.venv` | the `cognee.config` lines are missing | put them back at the top of `quaderno.py` |
| `search` returns an empty list | `cognify` never got to the end | run `digerisci` again |
| everything is very slow | it is normal on the free tier | `cognify` once, `chiedi` as often as you like |

## What you keep from this module {#artefatti-di-questo-modulo}

`memoria/quaderno.py` and the `dati/cognee/` folder with the knowledge
base you built. From here on the course works on this.
