# Installazione

Tempo: **30 minuti** la prima volta. Da fare una volta sola, prima del
modulo 1.

Alla fine di questa pagina hai: Python funzionante, il repository del
corso sul disco, le librerie installate e un file `.env` pronto da
riempire.

## Sistemi supportati

| Sistema | Supporto |
|---|---|
| macOS 13 o più recente (Intel o Apple Silicon) | sì |
| Linux (Ubuntu 22.04/24.04, Debian 12, Fedora 40+) | sì |
| Windows | **no, non direttamente** — vedi sotto |

### Se sei su Windows

Il corso usa Kuzu e cognee, che su Windows nativo danno problemi di
compilazione e di percorsi. Non ti facciamo perdere due ore a combatterci:
si usa **WSL2**, cioè una Ubuntu vera dentro Windows. Da PowerShell come
amministratore:

```powershell
wsl --install -d Ubuntu-24.04
```

Riavvia, apri «Ubuntu» dal menu Start, e **da lì in poi segui le
istruzioni Linux di questo corso**. Tieni il repository dentro la parte
Linux (`/home/tuonome/...`), non su `/mnt/c/...`: sul disco Windows
montato è da tre a dieci volte più lento.

Documentazione ufficiale: <https://learn.microsoft.com/windows/wsl/install>.

---

## 1. Python 3.11 o 3.12

Controlla cosa hai:

```bash
python3 --version
```

Se stampa `Python 3.11.x` o `Python 3.12.x` sei a posto, salta al punto 2.

> **3.13 e successivi non vanno**: alcune librerie del corso non hanno
> ancora i pacchetti compilati. Installa la 3.12 accanto a quella che hai,
> non al posto: non si disturbano.

**macOS** (con [Homebrew](https://brew.sh)):

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

Come riconosci che è andata male: `python3.12 --version` risponde
`command not found`. Su Ubuntu vecchie (22.04) la 3.12 non c'è nei
pacchetti standard; in quel caso va bene anche la 3.11
(`sudo apt install python3.11 python3.11-venv`).

## 2. Il repository

```bash
git clone <indirizzo-del-repo> memoria-ai
cd memoria-ai
```

Da qui in avanti, **tutti i comandi del corso si lanciano da questa
cartella**. Se un comando dice `python moduli/01-.../verifica.py`, tu sei
in `memoria-ai`.

## 3. L'ambiente isolato

Un «ambiente virtuale» è una cartella che contiene una copia di Python e
le librerie di questo progetto soltanto. Serve a non sporcare il Python
del sistema e a poter buttare via tutto con un `rm -rf`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Il prompt del terminale ora comincia con `(.venv)`. **Ogni volta che apri
un terminale nuovo devi rifare `source .venv/bin/activate`**: è la causa
numero uno degli errori `ModuleNotFoundError` durante il corso.

## 4. Le librerie

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Ci mette da 3 a 10 minuti e scarica circa 1,5 GB. Scarica anche
`onnxruntime`, che serve a calcolare gli embedding sul tuo computer
(modulo 3).

**Come riconosci che è andata bene:**

```bash
python -c "import cognee; print(cognee.get_cognee_version())"
```

Deve stampare `1.6.0`. Le prime righe di log colorate che vedi sono
normali: cognee si annuncia sempre.

**Se fallisce:**

| Messaggio | Causa | Rimedio |
|---|---|---|
| `error: externally-managed-environment` | non hai attivato il venv | `source .venv/bin/activate` |
| `No matching distribution found for cognee` | Python 3.13 o troppo vecchio | usa 3.11 o 3.12 |
| `Failed building wheel for ...` | mancano gli strumenti di compilazione | Ubuntu: `sudo apt install build-essential python3.12-dev`; macOS: `xcode-select --install` |
| si blocca a `Resolving dependencies` per minuti | è normale, `pip` sta provando combinazioni | aspetta |

## 4-bis. L'ambiente del gateway

Dal modulo 2 in poi userai un **gateway**: un piccolo server che sta sul
tuo computer, davanti ai fornitori. Va in un ambiente virtuale suo,
separato dal primo.

```bash
python3.12 -m venv .venv-gateway
.venv-gateway/bin/pip install -r requirements-gateway.txt
```

Non serve attivarlo: lo lancerai sempre con il percorso completo
(`.venv-gateway/bin/litellm`).

Perché separato: cognee pretende una versione di `litellm` vecchia, il
cui server proxy non parte con le librerie web attuali. Invece di
azzoppare uno dei due, li teniamo in due ambienti. È anche la pratica
corretta a prescindere: un servizio che gira per conto suo non condivide
le dipendenze con la tua applicazione.

Controlla:

```bash
.venv-gateway/bin/litellm --version
```

## 5. Il file delle chiavi

```bash
cp .env.example .env
```

Adesso apri `.env` con un editor di testo e riempilo seguendo
[CHIAVI.md](CHIAVI.md). Per cominciare basta `GROQ_API_KEY`.

Se stai leggendo il corso sul sito e non hai il file sotto mano, questo
è `.env.example` per intero. I commenti dentro contano quanto le righe:
spiegano cosa cambia e quando.

<details>
<summary>Il contenuto di <code>.env.example</code></summary>

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

`.env` **non deve mai finire su Git**: è già elencato in `.gitignore`.
Verifica che sia davvero così:

```bash
git check-ignore -v .env
```

Deve rispondere `.gitignore:1:.env	.env`. Se non risponde niente,
qualcosa è fuori posto: fermati e sistemalo prima di andare avanti.

## 6. Prova generale

```bash
python moduli/01-perche-serve-una-memoria/verifica.py
```

Ti dirà quali pezzi sono a posto e quali no. A questo punto è normale che
segnali i laboratori non ancora fatti: quello che conta è che le prime
righe (Python, librerie, `.env`) siano `OK`.

---

## Strada locale: Ollama

Da fare **solo** se non vuoi mandare niente fuori dal tuo computer. Serve
più RAM (8 GB) e il corso diventa più lento: un `cognify` che con Groq
dura un minuto qui ne dura dieci.

1. Installa Ollama: <https://ollama.com/download> (macOS: file `.dmg`;
   Linux: `curl -fsSL https://ollama.com/install.sh | sh`).
2. Scarica un modello piccolo che sa fare l'output strutturato:

```bash
ollama pull qwen3:4b-instruct
```

3. Controlla che risponda:

```bash
ollama run qwen3:4b-instruct "Rispondi solo: pronto"
```

4. In `.env`, commenta il blocco 3 e togli il commento alle ultime righe:

```bash
LLM_PROVIDER=ollama
LLM_ENDPOINT=http://localhost:11434/v1
LLM_MODEL=qwen3:4b-instruct
LLM_API_KEY=ollama
```

Gli embedding restano quelli del blocco 4: sono già locali, non cambia
niente.

**Cosa perdi**, e ti conviene saperlo subito:

| | Con le API gratuite | Con Ollama in locale |
|---|---|---|
| Velocità di un `cognify` su 10 pagine | ~1 minuto | ~10 minuti |
| Qualità dell'estrazione di entità | buona | discreta, con più errori |
| Descrizione delle foto | sì (Gemini) | solo se installi un modello multimodale (`ollama pull qwen2.5vl:3b`) |
| Trascrizione delle note vocali | sì (Groq Whisper) | serve `whisper.cpp` a parte |
| Dati inviati a terzi | sì | **nessuno** |

Ogni modulo ha un riquadro «Strada locale» con le differenze pratiche.

---

## Disinstallare tutto

```bash
deactivate            # esce dall'ambiente virtuale
cd ..
rm -rf memoria-ai     # via il repository, i dati e le librerie
```

Ollama, se l'hai installato, si toglie a parte:
<https://github.com/ollama/ollama/blob/main/docs/faq.md>.
