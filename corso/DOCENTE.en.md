# Notes for teachers {#note-per-chi-insegna}

This page is not for students. It explains **why** the course is built
this way, which choices were made among the many possible ones, and what
breaks first.

---

## 1. The choices made, and why {#1-le-scelte-prese-e-perche}

Every time there was more than one path, the course takes the simplest
one for the student. They are all listed here, with the reason: if you
decide in class to change one, it helps to know what you are touching.

### 1.1 Embeddings are computed locally, not through an API {#11-gli-embedding-si-calcolano-in-locale-non-via-api}

**Choice:** `EMBEDDING_PROVIDER=fastembed`, model
`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensions, 0.22 GB.

**Why:** one `cognify` of the corpus makes a few hundred embedding
calls. Making them through an API burns the daily quota in module 5 before
you reach module 8. Locally they are free, have no rate limit,
and run on a CPU in a few seconds.

**Useful side effect:** embeddings are the only part of the
system the student sees working without internet. It is the
concrete proof that "RAG" does not mean "everything in the cloud".

**Price:** a 384-dimension model is weaker than
`text-embedding-3-large`. On the course corpus you do not notice; on a
large corpus you do.

### 1.2 Cerebras was removed from the providers {#12-cerebras-e-stato-tolto-dai-fornitori}

Cerebras would be a natural fallback, fast and with a free tier.
As of September 2026, though, it asks for a payment method even for that
tier. The "zero cost, no credit card" constraint is stronger than the list
of providers, so it is out. What remains: Groq (main), Google AI Studio and
OpenRouter (fallbacks), with Mistral and Cloudflare mentioned as optional
in `CHIAVI.md`.

### 1.3 No Windows {#13-niente-windows}

`SETUP.md` covers macOS and Linux. For Windows it points to WSL2 in two lines
and does not test it.

This is not laziness: Docker Desktop, file paths and Kuzu permissions
on native Windows are three sources of trouble that teach nothing
about the topic of the course.

### 1.4 The gateway has a separate Python environment {#14-il-gateway-ha-un-ambiente-python-separato}

`litellm[proxy]` and `cognee` do not live in the same environment: cognee
requires `litellm<1.97`, and the proxy server of that version wants a
newer FastAPI than cognee accepts.

Two environments, `.venv` and `.venv-gateway`, are the correct solution, not
a workaround: the gateway **is** a separate service, which in real life
runs on another machine. Seeing it installed separately from the start
teaches the right thing.

It is explained in `SETUP.md` §4-bis. If a student tries to install
everything together, `pip` refuses with a clear message.

### 1.5 The Kuzu graph is called `.pkl`, and it is not a pickle {#15-il-grafo-kuzu-si-chiama-pkl-e-non-e-un-pickle}

The trap of module 6, and I fell into it first myself while
writing the course.

cognee 1.6 saves the graph of each dataset in a file called
`<id-archivio>.pkl`, **whatever engine is underneath**. With
`GRAPH_DATABASE_PROVIDER=kuzu` that file is a full Kuzu database.
Next to it sits its `.pkl.wal`, which is Kuzu's write-ahead log.
But the name says something else.

Consequence: any check that looks for "kuzu" in the file name
fails, and you convince yourself you have a configuration problem you do not
have. So `trova_kuzu()` in `ispeziona.py` **opens** the candidates instead
of looking at their names, and the lab has the student make the same
discovery firsthand.

The general lesson goes well beyond cognee: a file's
extension is the opinion of whoever wrote it.

Note on `GRAPH_DATASET_DATABASE_HANDLER=kuzu`: with
`GRAPH_DATABASE_PROVIDER=kuzu`, cognee 1.6 already sets it on its own (a
validator does it). It stays explicit in `.env`, with a comment that
explains why, so whoever changes engine tomorrow does not find the graph
elsewhere without understanding why.

### 1.6 cognee's throttle is measured in requests, not tokens {#16-il-freno-di-cognee-si-misura-in-richieste-non-in-token}

The point that took the longest to understand. It ended up in module 5
because it is the most useful one in the whole course.

On free Groq, the limit you hit first is **not** the one
on requests (30 per minute) but the one on tokens (8,000 per minute),
because each extraction call weighs about 3,000 tokens between
instructions, JSON schema and text.

The internal limiter of cognee 1.6.0 (`LLM_RATE_LIMIT_*`) counts **only
requests**: `LLM_RATE_LIMIT_TOKENS` is declared in the
configuration but not used by the active code path. So you have to convert
the budget by hand:

```
8.000 token al minuto / 3.000 token a chiamata = 2 richieste al minuto
LLM_RATE_LIMIT_REQUESTS=1
LLM_RATE_LIMIT_INTERVAL=30
```

(8,000 tokens per minute / 3,000 tokens per call = 2 requests per minute.)

With `25` (which looks cautious, since the limit is 30) it throttles
nothing and you get a burst of 429s.

**And you write `1 / 30`, not `2 / 60`.** cognee's limiter is a
leaky bucket (`aiolimiter.AsyncLimiter`): with `2 / 60` both calls
can start at the same instant, and two calls together make
6,000-8,000 tokens in two seconds. That is exactly the 429 you wanted
to avoid. The average speed is the same, the burst is not.

**Consequence to say in class:** a `cognify` of the full corpus
takes a good half hour on the Groq free tier, and almost all of it is
minutes of waiting. It is not slow code, it is the quota. The real fix is
extension 5 of the rubric: two providers with the same `model_name`
in the gateway, and the time halves.

**In class:** have students launch `digerisci` **before** the break, not
after. Or hand out an already-digested knowledge base (see §4).

### 1.7 The daily quota, and who really eats it {#17-la-quota-giornaliera-e-chi-se-la-mangia-davvero}

The limit nobody talks about is the **daily** token cap:
**200,000** on the Groq free tier. Not the 30 messages per minute, not
the 8,000 tokens per minute.

Measured: an extraction call weighs between 900 and 4,300 tokens
(median ~2,100), because it carries the instructions and the JSON schema
besides the text. The course corpus splits into ~12 chunks, two calls per chunk:
**~24 calls, ~50,000 tokens**. That is a quarter of the day. The
corpus fits comfortably, three or four times.

**What eats the quota is retries.** Every 429 makes the client resend
the whole prompt, and it is counted again. On the exact same
`cognify` I counted:

| Configuration | 429 errors | Tokens wasted |
|---|---:|---:|
| `rpm`/`tpm` set in the gateway with a single provider | 66 | ~140,000 |
| throttle `2 richieste / 60 s` (bursty) | 31 | ~65,000 |
| throttle `1 richiesta / 30 s` | 3 | ~6,000 |

The point to bring to class is this: **the throttle is not politeness
toward the provider, it is the quota you defend.** Without a throttle the 429s
come anyway, and each retry resends the whole prompt: the quota
runs out before the work does.

In class: if a group exhausts the 200,000 tokens, the message changes from
`per minute` to `per day` and no amount of waiting helps. You need the
already-digested knowledge base to hand out (§4), or a second key.

Two things to know about the daily quota, measured on an exhausted
account (September 2026):

- requests **rejected** with `per day` are not counted: the
  `Used` counter stayed at 199,926 while it rejected 62 of them. So
  retrying costs time, not quota, and `cognify` is incremental: it resumes
  from the missing documents. A "try again later" loop wastes nothing;
- it is not a window that refills continuously. I retried every hour
  for twenty-four hours and always found it closed, then it reopened
  all at once. So do not promise the class that "it unlocks in an hour":
  once the quota is gone, that day is over.

**The second key, how you actually add it.** You do not need a second
provider: two free accounts with the same one are enough, listed twice
under the **same** `model_name`. LiteLLM treats them as two counters
at the same desk and alternates between them:

```yaml
  - model_name: memoria-veloce
    litellm_params:
      model: groq/openai/gpt-oss-120b
      api_key: os.environ/GROQ_API_KEY
  - model_name: memoria-veloce
    litellm_params:
      model: groq/openai/gpt-oss-120b
      api_key: os.environ/GROQ_API_KEY_2
```

It is not in the course `config.yaml` because not everyone has the second key,
and a fallback without a key does more harm than good (§ rule in the
file). In class, though, it is the move that saves a day: two accounts from two
teachers, and the quota doubles. Here it served exactly that purpose, to
verify modules 5, 7 and 8 when the first account was exhausted.

**Note on `--ridotto`.** `quaderno.py aggiungi --ridotto` ingests only
the boiler and the washing machine (6 documents). You do not need it to do the course,
since the whole corpus fits, but it is handy when you want to try again and again,
or if a lot has already been used up in class.

### 1.8 The gateway's bench is short {#18-la-panchina-del-gateway-e-corta}

`cooldown_time: 10` and `allowed_fails: 3`, not `60` and `1`.

With a single provider configured, which is the situation of anyone who has only
the Groq key, `allowed_fails: 1` means that at the first 429 LiteLLM
answers "no deployment available" for a whole minute, and cognee
adds its own backoff on top. The result is a twenty-minute job
that takes forty.

With two or more real providers, the high values make sense again: it is
explained in the comment inside `config.yaml`.

### 1.9 Evaluation compares fragments, it does not use a judge model {#19-la-valutazione-confronta-frammenti-non-usa-un-modello-giudice}

A second model as a judge would be more refined. Comparing fragments
costs zero quota, always gives the same result, and on answers that
contain a number or a spare part code it is almost always right.

Its two flaws (false negatives on «un bar e quattro» (one bar and four tenths), false positives
on «1,4» inside a sentence that says the opposite) are written in
lesson 8 instead of hidden, and that is why the `attese` (expected values) are
always numbers and codes, never sentences.

The `assente` (absent) type has its own rule, because fragment comparison
does not work there: see lesson 8 §3.

### 1.10 Modules 1-4 on Markdown, modules 5-8 on PDF {#110-moduli-1-4-sui-markdown-moduli-5-8-sui-pdf}

A deliberate difference that a careful teacher notices right away.

The handmade scripts of modules 1-4 (`pezzi.py`, `lessicale.py`,
`semantica.py`, `grafo.py`) read the **Markdown sources** of the manuals.
From `quaderno.py` on, that is from modules 5-8 and the project, you
ingest the **PDFs**.

It is not an oversight. In the first four modules you study how
retrieval works, and adding text extraction from PDFs adds a
variable that has nothing to do with it. From module 5, instead, the corpus is the real one,
and that is where `greencut-rm46.pdf`, the scan, becomes a wall.

**Concrete consequence:** in module 3 the lawn mower answers, from module 5
it no longer does. This is stated in lab 5 and shows up again as
`ocr 0/2` in the module 8 summary. If someone in class asks "but
it worked before", the answer is: before you read the source, now you
read the document.

If this difference bothers you, you can align it in one line: in
`quaderno.py`, `documenti_del_corpus()` goes back to `CORPUS.rglob("*.md")`.
But then module 8 no longer shows the OCR failure, and requirement
R1 of the project loses its reason.

### 1.11 `transformers` is needed, even without PyTorch {#111-transformers-serve-anche-senza-pytorch}

A problem that shows up only as a warning in the middle of the logs, and that
silently degrades quality:

```text
Could not load a matching tokenizer for fastembed model
'...paraphrase-multilingual-MiniLM-L12-v2' (No module named 'transformers').
Falling back to TikToken, so token counts are approximate.
```

TikToken is OpenAI's tokenizer and has nothing to do with the
embedding model we use. The token count decides **how
long to make the chunks**, and the embedding model handles **512 tokens**:
counting them wrong means producing chunks that overflow, and the excess
text gets truncated by the embedder without anyone saying so.

Fix, already in the course: `transformers==4.57.1` in `requirements.txt` and
`HUGGINGFACE_TOKENIZER=...` in `.env`. It installs **without PyTorch**
(you only need the tokenizers, not the models), so it is about ten
megabytes, not a gigabyte.

Check that it is in place:

```bash
python -c "
from dotenv import load_dotenv; load_dotenv('.env')
from cognee.infrastructure.llm.tokenizer.resolver import resolve_embedding_tokenizer
t = resolve_embedding_tokenizer(provider='fastembed',
    model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
print(type(t).__name__)
"
```

It must print `HuggingFaceTokenizer`. If it prints something with `TikToken`
in it, the package is missing.

### 1.12 The corpus is made up {#112-il-corpus-e-inventato}

Five plausible appliances and none of them real. Reason: a real manual is
covered by copyright and cannot be distributed with a course, and a real
manual is also too long for the time available.

The PDFs are regenerated with `tools/genera_corpus.py`, which builds them from
the Markdown sources in `progetto-finale/corpus/manuali/`.

### 1.13 One model name in `.env`, two different readers {#113-un-solo-nome-di-modello-nel-env-due-lettori-diversi}

From module 2 the `.env` says `LLM_MODEL=openai/memoria-veloce`. Two
readers use it: cognee, which goes through the litellm library and needs that
`openai/` to understand it must talk to an OpenAI-compatible
address; and `memoria/llm.py`, which uses the OpenAI client directly and would send
the name as is. The gateway knows only `memoria-veloce` and answers
`400 Invalid model name passed in model=openai/memoria-veloce`.

You could keep two separate variables. The choice was to leave just
one and have `llm.py` strip the prefix when it talks to the gateway
(`LLM_PROVIDER=custom`): one less variable to get wrong. If a
student has an old version of `llm.py` taken from module 1 and the
module 2 check fails with that 400, this is the cause.

---

## 2. The four failures, and why they are there {#2-i-quattro-fallimenti-e-perche-sono-li}

A system that works right away does not teach why it is built that way. The
course has students build four wrong versions plus one, breaks them on the
student's data, and only then gives the right one.

| # | Where | What fails | What it teaches |
|---|---|---|---|
| 1 | module 1 | the model invents the answer about an appliance it does not know | why you need retrieval |
| 2 | module 3 | blind splitting cuts the E4 error table in two | why chunking is not a detail |
| 3 | module 4 | "how many hours in total?": retrieval brings the right chunks and the answer is wrong | why you need the graph |
| 4 | module 7 | the memory gives the old value (1.2 bar) | that facts age, and no algorithm fixes that on its own |
| bonus | module 2 | `gpt-oss-20b` breaks on the nested JSON schema (`json_validate_failed`) | that "smaller model" has a concrete, measurable cost |

**The fourth is the most important and the easiest to skip in class**,
because it has no elegant technical solution: you fix it by writing a
correction note, that is by doing what a repair technician would do with a
paper notebook. It is worth stopping there for five minutes.

The module 2 bonus is kept on purpose: it is a real error, met
while writing the course, and reproducing it shows that the error was not in the code.

---

## 3. The hours {#3-le-ore}

| # | Module | Hours | of which lab |
|---|---|---|---|
| 1 | Why you need a memory | 2.0 | 1.0 |
| 2 | Keys, gateway and quotas | 2.0 | 1.3 |
| 3 | How a text becomes searchable | 3.0 | 2.0 |
| 4 | From retrieval to the graph | 2.5 | 1.7 |
| 5 | The cognee pipeline | 3.0 | 2.0 |
| 6 | Where the data lives | 2.0 | 1.4 |
| 7 | Memory maintenance | 2.0 | 1.3 |
| 8 | Evaluate your own system | 2.0 | 1.4 |
| — | Final project | 1.5 | 1.5 |
| | **total** | **20.0** | **13.6** |

13.6 lab hours out of 20: more than two thirds of the time goes to
writing and running code, not to listening.

**The hours do not count waiting for quotas.** The module 5 `digerisci`
and the module 8 evaluation run are minutes when nothing happens.
In class, launch them before a break.

---

## 4. How to bring it to class {#4-come-portarlo-in-aula}

**The day before.** Have everyone complete `SETUP.md` to the end, with the
Groq key already in hand. Downloading the embedding model (0.22 GB)
on twenty machines at once is the only moment when the classroom
network matters.

**Bring an already-digested knowledge base.** A copy of `dati/cognee/` made by
you, to hand out to anyone who falls behind in module 5. That is 30-40
minutes of waiting that teach nothing to someone who has already seen them
once.

**Module 6 requires Docker.** If the classroom does not have it, the module works
anyway on SQLite and LanceDB: you lose the PostgreSQL and
pgvector part, which is half of it. Better to check beforehand.

**Split it into two days**, if you can: modules 1-4, and modules 5-8 plus the
project. Module 4 closes one topic (why retrieval alone is not
enough) and module 5 opens another (a library that does it for you).

---

## 5. What breaks first {#5-cosa-si-rompe-per-primo}

In order of likelihood.

1. **Free quotas change.** The numbers in `CHIAVI.md` are
   from September 2026 and are the first thing to age: the official
   limits pages, linked in `CREDITI.md`, remain the reliable source.
   Check them before every edition.
2. **cognee changes its API.** It is at version 1.6 and moves fast. The
   versions in `requirements.txt` are pinned on purpose: if you unpin them,
   plan to redo modules 5, 6 and 7.
3. **A provider drops its free tier.** It happened to Cerebras
   while I was writing. The gateway is there for this too: you change one
   section of `config.yaml` and the student's code does not notice.
4. **Models change names.** `openai/gpt-oss-120b` on Groq today.
   When it disappears, you change it in `config.yaml` and in `.env.example`, in two
   places.

---

## 6. Where the solutions are {#6-dove-sono-le-soluzioni}

Every module has `starter/` (with the TODOs) and `soluzione/` (complete). The
students copy from `starter/` into `memoria/` and work there; `verifica.py`
looks inside `memoria/`.

`verifica.py` tells the starter from the solution: it looks for the
`NotImplementedError` and reports it. You cannot get around it by deleting the line
without writing the code, because the following checks test the
functions on cases whose outcome is already known.

No `verifica.py` calls the model, except the last check of
module 7: if the gateway is off, it skips it and says so.

**The answers to the open questions** in the labs (the ones that end up
in `RISPOSTE.md`) are in `soluzione/RISPOSTE.md` inside the module that
asks them: modules 7 and 8. They are not in any site menu; you open them
by knowing the path. Module 7 also has
`soluzione/rettifica-pressione.md`, the correction note already
written, to use if time is short in class.
