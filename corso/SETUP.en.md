# Installation {#installazione}

Time: **30 minutes** the first time. You do this only once, before
module 1.

At the end of this page you have: a working Python, the course
repository on your disk, the libraries installed and a `.env` file ready
to fill in.

## Supported systems {#sistemi-supportati}

| System | Support |
|---|---|
| macOS 13 or newer (Intel or Apple Silicon) | yes |
| Linux (Ubuntu 22.04/24.04, Debian 12, Fedora 40+) | yes |
| Windows | **no, not directly** — see below |

### If you are on Windows {#se-sei-su-windows}

The course uses Kuzu and cognee, which cause build and path problems on
native Windows. We won't make you waste two hours fighting them: you use
**WSL2**, which is a real Ubuntu inside Windows. From PowerShell as
administrator:

```powershell
wsl --install -d Ubuntu-24.04
```

Restart, open "Ubuntu" from the Start menu, and **from then on follow the
Linux instructions of this course**. Keep the repository inside the Linux
side (`/home/tuonome/...`), not on `/mnt/c/...`: on the mounted Windows
disk it is three to ten times slower.

Official documentation: <https://learn.microsoft.com/windows/wsl/install>.

---

## 1. Python 3.11 or 3.12 {#1-python-311-o-312}

Check what you have:

```bash
python3 --version
```

If it prints `Python 3.11.x` or `Python 3.12.x` you are fine: skip to step 2.

> **3.13 and later do not work**: some course libraries don't have
> prebuilt packages yet. Install 3.12 next to the one you have, not
> instead of it: they don't get in each other's way.

**macOS** (with [Homebrew](https://brew.sh)):

```bash
brew install python@3.12
```

**Ubuntu / Debian:**

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3-pip git
```

**Fedora:**

```bash
sudo dnf install -y python3.12 git
```

How you know it went wrong: `python3.12 --version` answers
`command not found`. On older Ubuntu (22.04), 3.12 is not in the standard
packages; in that case 3.11 is fine too
(`sudo apt install python3.11 python3.11-venv`).

## 2. The repository {#2-il-repository}

```bash
git clone <indirizzo-del-repo> memoria-ai
cd memoria-ai
```

From here on, **you run every course command from this folder**. If a
command says `python moduli/01-.../verifica.py`, you are in `memoria-ai`.

## 3. The isolated environment {#3-lambiente-isolato}

A "virtual environment" is a folder that holds a copy of Python and the
libraries of this project only. It keeps the system Python clean, and you
can throw everything away with an `rm -rf`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

The terminal prompt now starts with `(.venv)`. **Every time you open a new
terminal you must run `source .venv/bin/activate` again**: it is the
number one cause of `ModuleNotFoundError` errors during the course.

## 4. The libraries {#4-le-librerie}

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

It takes 3 to 10 minutes and downloads about 1.5 GB. It also downloads
`onnxruntime`, which computes embeddings on your computer (module 3).

**How you know it went well:**

```bash
python -c "import cognee; print(cognee.get_cognee_version())"
```

It must print `1.6.0`. The first colored log lines you see are normal:
cognee always announces itself.

**If it fails:**

| Message | Cause | Fix |
|---|---|---|
| `error: externally-managed-environment` | you didn't activate the venv | `source .venv/bin/activate` |
| `No matching distribution found for cognee` | Python 3.13 or too old | use 3.11 or 3.12 |
| `Failed building wheel for ...` | the build tools are missing | Ubuntu: `sudo apt install build-essential python3.12-dev`; macOS: `xcode-select --install` |
| it hangs at `Resolving dependencies` for minutes | that's normal, `pip` is trying combinations | wait |

## 4-bis. The gateway environment {#4-bis-lambiente-del-gateway}

From module 2 on you will use a **gateway**: a small server that runs on
your computer, in front of the providers. It goes in its own virtual
environment, separate from the first one.

```bash
python3.12 -m venv .venv-gateway
.venv-gateway/bin/pip install -r requirements-gateway.txt
```

You don't need to activate it: you will always launch it with the full
path (`.venv-gateway/bin/litellm`).

Why separate: cognee demands an old version of `litellm`, whose proxy
server won't start with current web libraries. Instead of crippling one of
the two, we keep them in two environments. It is also the right practice
anyway: a service that runs on its own doesn't share dependencies with
your application.

Check:

```bash
.venv-gateway/bin/litellm --version
```

## 5. The keys file {#5-il-file-delle-chiavi}

```bash
cp .env.example .env
```

Now open `.env` with a text editor and fill it in following
[CHIAVI.md](CHIAVI.md). To start, `GROQ_API_KEY` is enough.

If you are reading the course on the website and don't have the file at
hand, this is the full `.env.example`. The comments inside matter as much
as the lines: they explain what changes and when.

<details>
<summary>The contents of <code>.env.example</code></summary>

```bash
# Copia questo file in .env e riempilo.  .env NON va su Git: e' gia' in .gitignore.
# Come si ottiene ogni chiave: CHIAVI.md

# =============================================================
# 1. CHIAVI DEI FORNITORI  (tutte gratuite, nessuna carta)
# =============================================================
# Groq      -> https://console.groq.com/keys        (inizia per gsk_)
GROQ_API_KEY=
# Google AI Studio -> https://aistudio.google.com/apikey   (inizia per AIza)
GEMINI_API_KEY=
# OpenRouter -> https://openrouter.ai/keys          (inizia per sk-or-v1-)
OPENROUTER_API_KEY=
# Riserve, facoltative
CEREBRAS_API_KEY=
MISTRAL_API_KEY=

# =============================================================
# 2. IL GATEWAY  (modulo 2 in poi)
# =============================================================
# Indirizzo del proxy LiteLLM che avvii tu sul tuo computer.
GATEWAY_URL=http://localhost:4000/v1
# Password finta che il proxy si aspetta: serve solo a impedire che altri
# programmi sul tuo computer usino il tuo gateway. Inventala.
GATEWAY_KEY=sk-memoria-locale

# =============================================================
# 3. COME COGNEE PARLA COL MODELLO
# =============================================================
# MODULO 1: si parla diritti con Groq, senza gateway.
LLM_PROVIDER=groq
LLM_MODEL=openai/gpt-oss-120b
LLM_MAX_COMPLETION_TOKENS=4096

# DAL MODULO 2 IN POI: commenta le tre righe sopra e togli il commento a
# queste quattro. "custom" vuol dire "endpoint compatibile OpenAI", cioe'
# il gateway LiteLLM che avvii tu.
# LLM_PROVIDER=custom
# LLM_ENDPOINT=http://localhost:4000/v1
# LLM_MODEL=openai/memoria-veloce
# LLM_API_KEY=sk-memoria-locale

# --- Il freno (modulo 5) ---------------------------------------------
# cognee digerisce in parallelo e senza freno prende 429, aspetta molto
# piu' del dovuto, riprova: un lavoro da venti minuti ne impiega
# quaranta. Queste tre righe gli dicono di restare sotto quota da solo.
#
# ATTENZIONE, e' il punto che inganna tutti: il freno di cognee 1.6.0
# conta le RICHIESTE, non i token. Ma il limite che colpisci per primo
# su Groq e' quello a TOKEN (8.000 al minuto), perche' ogni chiamata di
# estrazione pesa circa 3.000 token fra istruzioni e testo.
# Quindi il budget va convertito:  8.000 / 3.000 = 2 richieste al minuto.
# Mettere 25 qui non frena niente. Vedi il modulo 5.
#
# E si scrive 1 ogni 30 secondi, non 2 ogni 60: il freno e' a secchiello,
# e con 2/60 le due chiamate possono partire insieme. Due chiamate
# insieme fanno 6-8.000 token in due secondi, cioe' esattamente il 429
# che stavi cercando di evitare. Stessa velocita' media, nessuna raffica.
LLM_RATE_LIMIT_ENABLED=true
LLM_RATE_LIMIT_REQUESTS=1
LLM_RATE_LIMIT_INTERVAL=30

# =============================================================
# 4. EMBEDDING  (vedi modulo 3: qui restano sul tuo computer)
# =============================================================
EMBEDDING_PROVIDER=fastembed
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_DIMENSIONS=384
# Il tokenizzatore con cui contare i token PER QUESTO modello. Senza,
# cognee ripiega su TikToken (che e' di OpenAI) e sbaglia a dimensionare
# i pezzi: il modello qui sopra regge 512 token, e quello che sfora
# viene troncato senza un avviso. Richiede il pacchetto transformers.
HUGGINGFACE_TOKENIZER=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

# =============================================================
# 5. DOVE VIVONO I DATI  (modulo 6)
# =============================================================
# Di partenza: tutto in file locali, niente da installare.
DB_PROVIDER=sqlite
DB_NAME=cognee_db
VECTOR_DB_PROVIDER=lancedb
GRAPH_DATABASE_PROVIDER=kuzu
# cognee tiene un grafo per ogni dataset, e per quelli usa un motore
# che si imposta a parte. Con GRAPH_DATABASE_PROVIDER=kuzu qui sopra
# cognee 1.6 la imposta da sola, ma scriverla esplicitamente ti risparmia
# una sorpresa se un giorno cambi il provider.
#
# NON farti ingannare dal nome del file: cognee chiama il grafo
# <id-archivio>.pkl qualunque motore ci sia sotto. Quel .pkl e' un vero
# database Kuzu, e accanto ci trovi il suo .pkl.wal. Per sapere cosa c'e'
# dentro un file si apre, non si guarda il suffisso: vedi il modulo 6.
GRAPH_DATASET_DATABASE_HANDLER=kuzu

# Dal modulo 6 in poi, PostgreSQL + pgvector:
# DB_PROVIDER=postgres
# DB_NAME=cognee_db
# DB_HOST=localhost
# DB_PORT=5432
# DB_USERNAME=cognee
# DB_PASSWORD=cognee
# VECTOR_DB_PROVIDER=pgvector

# =============================================================
# 6. TRASCRIZIONE DELLE NOTE VOCALI  (progetto finale)
# =============================================================
WHISPER_MODEL=whisper-large-v3-turbo

# =============================================================
# 7. STRADA LOCALE CON OLLAMA  (niente esce dal tuo computer)
# =============================================================
# Per passare in locale: commenta il blocco 3 e togli il commento a queste.
# LLM_PROVIDER=ollama
# LLM_ENDPOINT=http://localhost:11434/v1
# LLM_MODEL=qwen3:4b-instruct
# LLM_API_KEY=ollama
```

</details>

The comments in the file are in Italian. The key points: block 1 holds the
provider keys (all free, no card); block 2 is the gateway; block 3 says how
cognee talks to the model (direct to Groq in module 1, through the gateway
from module 2 on); the rate limiter counts requests, not tokens, so it is
set to 1 request every 30 seconds (see module 5); block 4 keeps embeddings
on your computer; block 5 is where the data lives (the graph file ends in
`.pkl` but is a real Kuzu database); blocks 6 and 7 cover voice-note
transcription and the local path with Ollama.

`.env` **must never end up on Git**: it is already listed in `.gitignore`.
Check that it really is:

```bash
git check-ignore -v .env
```

It must answer `.gitignore:1:.env	.env`. If it answers nothing, something
is out of place: stop and fix it before you go on.

## 6. Dress rehearsal {#6-prova-generale}

```bash
python moduli/01-perche-serve-una-memoria/verifica.py
```

It tells you which pieces are in place and which aren't. At this point it
is normal for it to flag the labs you haven't done yet: what matters is
that the first lines (Python, libraries, `.env`) are `OK`.

---

## Local path: Ollama {#strada-locale-ollama}

Do this **only** if you don't want to send anything outside your
computer. It needs more RAM (8 GB) and the course gets slower: a
`cognify` that takes one minute with Groq takes ten here.

1. Install Ollama: <https://ollama.com/download> (macOS: `.dmg` file;
   Linux: `curl -fsSL https://ollama.com/install.sh | sh`).
2. Download a small model that can do structured output:

```bash
ollama pull qwen3:4b-instruct
```

3. Check that it answers:

```bash
ollama run qwen3:4b-instruct "Rispondi solo: pronto"
```

(The prompt means "Just answer: ready".)

4. In `.env`, comment out block 3 and uncomment the last lines:

```bash
LLM_PROVIDER=ollama
LLM_ENDPOINT=http://localhost:11434/v1
LLM_MODEL=qwen3:4b-instruct
LLM_API_KEY=ollama
```

The embeddings stay those of block 4: they are already local, nothing
changes.

**What you lose**, and you'd better know it right away:

| | With the free APIs | With Ollama locally |
|---|---|---|
| Speed of a `cognify` on 10 pages | ~1 minute | ~10 minutes |
| Quality of entity extraction | good | fair, with more errors |
| Photo descriptions | yes (Gemini) | only if you install a multimodal model (`ollama pull qwen2.5vl:3b`) |
| Voice-note transcription | yes (Groq Whisper) | needs `whisper.cpp` separately |
| Data sent to third parties | yes | **none** |

Every module has a "Local path" box with the practical differences.

---

## Uninstall everything {#disinstallare-tutto}

```bash
deactivate            # esce dall'ambiente virtuale
cd ..
rm -rf memoria-ai     # via il repository, i dati e le librerie
```

Ollama, if you installed it, is removed separately:
<https://github.com/ollama/ollama/blob/main/docs/faq.md>.
