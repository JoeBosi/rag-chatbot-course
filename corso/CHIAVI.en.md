# Free API keys, provider by provider {#le-chiavi-gratuite-fornitore-per-fornitore}

**Limits checked on September 20, 2026.** Providers change them without
notice: the official page linked in each box always has the last word.
That is exactly why in [module 2](moduli/02-chiavi-gateway-e-quote/LEZIONE.md)
we put a gateway in front of all of them: if one changes the rules, the
course keeps working with the others.

## One rule for all {#regola-che-vale-per-tutti}

**No provider in this course asks for a credit card.** If a screen asks
you for one, you are on the wrong page or you clicked a paid plan: go
back. The only exception is flagged below (Cerebras), and for that reason
the course does **not** use it.

**An API key is a password.** It goes in `.env`, never in the code, never
in a commit. `.env` is already in `.gitignore`. If a key ends up on GitHub
by mistake, revoke it and make a new one: deleting the commit is not
enough.

## How many you really need {#quante-ne-servono-davvero}

| Key | Used for | Required? |
|---|---|---|
| Groq | the reasoning model + voice-note transcription | **yes**, from module 1 |
| Google AI Studio | long contexts, photo descriptions, OCR of scanned PDFs | **yes**, from the final project |
| OpenRouter | comparing different models, third safety net | recommended, from module 2 |
| Mistral | fallback | no |
| Cloudflare Workers AI | fallback | no |

You can do the first two modules with the Groq key alone.

---

## 1. Groq {#1-groq}

The fastest of the three. No card; sign up with email or a Google
account.

1. Go to <https://console.groq.com/keys> and sign in.
2. `Create API Key`, give it a name (`corso-memoria`), copy the key.
3. **You see the key only once.** If you lose it, make another one.
4. Paste it into `.env`:

```bash
GROQ_API_KEY=gsk_...
```

### Free tier limits {#limiti-del-piano-gratuito}

| Model | Requests/minute | Requests/day | Tokens/minute | Tokens/day |
|---|---:|---:|---:|---:|
| `openai/gpt-oss-120b` | 30 | 1,000 | 8,000 | 200,000 |
| `openai/gpt-oss-20b` | 30 | 1,000 | 8,000 | 200,000 |
| `qwen/qwen3.8-27b` | 30 | 1,000 | 8,000 | 200,000 |
| `whisper-large-v3` | 20 | 2,000 | — | — |
| `whisper-large-v3-turbo` | 20 | 2,000 | — | — |

The limits apply **per account**, not per key: making five keys does
nothing. Up-to-date table: <https://console.groq.com/docs/rate-limits>.

**Look at the last column, not the second.** The number that counts is
`200.000 token al giorno` (200,000 tokens per day), and almost nobody
notices it in time.

Measured on this course's corpus: one extraction call weighs between
**900 and 4,300 tokens**, median about **2,100**, because besides the text
it carries the instructions and the JSON schema of the answer. Do the
math:

```
200.000 token al giorno / ~2.500 token a chiamata = ~80 chiamate al giorno
```

(200,000 tokens per day / ~2,500 tokens per call = ~80 calls per day.)

**Eighty calls.** Not a thousand. You will never see the 1,000 requests
per day limit: you will run out of tokens long before.

What it means in practice:

| Operation | Calls | Tokens | How many times a day |
|---|---:|---:|---|
| one question to the knowledge base | 1-3 | ~5,000 | as many as you like |
| ingesting a new note | 3-6 | ~10,000 | as many as you like |
| ingesting the course corpus from scratch | ~24 | ~50,000 | three or four |

Three or four times a day is comfortable. But there is a trap, and it is
the reason this page insists so much:

> **Every retry after a 429 resends the whole prompt, and it is counted
> again.**

It isn't the useful work that eats your day: it's the wasted attempts. A
badly configured `cognify` that gets thirty 429s and repeats them costs
**more than twice** as much as a well-configured one, for the same
result. With the module 5 configuration the 429s drop to two or three;
without it, I counted thirty-one on the exact same job.

Moral: the rate limiter isn't there to be polite to the provider. It is
there so you don't throw away your quota.

**And if you really run out?** The message changes: it says `tokens per day
(TPD)` instead of `per minute`, and no short wait is enough. It doesn't
reset at midnight: it is a **24-hour window**, and it reopens as
yesterday's usage leaves the window. In practice: the day is over, and
work resumes the next day, in the hours when you had used it up. Good
news: requests **rejected** with `per day` are not counted, so retrying
costs time, not quota.

Free tier limits change without notice: the values here are from
September 2026, and the always up-to-date page is
[console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits).

Better to know this before you spend the evening watching a terminal that
retries.

The **8,000 tokens per minute** are the second constraint: they slow you
down, they don't stop you. In module 2 you learn to count before you
launch, and in module 5 to set the right rate limiter.

### Which model to use {#quale-modello-usare}

| Model | When |
|---|---|
| `openai/gpt-oss-120b` | **course default.** It handles entity extraction in JSON |
| `openai/gpt-oss-20b` | faster, but gets structured JSON wrong: we show you in module 5 |
| `whisper-large-v3-turbo` | voice-note transcription: fast and good enough |
| `whisper-large-v3` | more accurate transcription, if turbo mishears |

---

## 2. Google AI Studio (Gemini) {#2-google-ai-studio-gemini}

The best for long texts and the only free one that looks at **images**:
in the final project it describes photos of parts and reads scanned PDFs.

1. Go to <https://aistudio.google.com/apikey> with a Google account.
2. `Create API key` → choose or create a project.
3. Copy the key (it starts with `AIza`) into `.env`:

```bash
GEMINI_API_KEY=AIza...
```

### Free tier limits {#limiti-del-piano-gratuito_1}

Google **no longer publishes a fixed table**: the limits depend on the
model and the project, and you see them on your dashboard:
<https://aistudio.google.com/rate-limit>. The figures you find around for
the `flash` models — about 10 requests per minute and a few hundred per
day — are indicative, not official.

Free models as of September 2026 (always up-to-date source:
<https://ai.google.dev/gemini-api/docs/pricing>):

| Model | Use in the course |
|---|---|
| `gemini-3.5-flash` | photo descriptions, OCR, long contexts |
| `gemini-3.5-flash-lite` | low-cost summaries |
| `gemini-2.5-flash` | alternative if the 3.x models aren't available in your region |
| `gemini-embedding-2` | embeddings via API, if you don't want to compute them on your computer |

### Specific warning {#avvertenza-specifica}

Google's pricing page, for the free tier, says literally that content
**is used to improve their products**; for the paid tier it says the
opposite. In plain words: what you send to Gemini with the free key can
end up in training. The same goes for the others. Appliance manuals: no
problem. Contracts, medical reports, customer data: never.

---

## 3. OpenRouter {#3-openrouter}

One key for about twenty free models from different providers. In the
course you use it to **compare** models without opening other accounts,
and as a third safety net when Groq and Google have used up their quota.

1. <https://openrouter.ai/keys>, sign in, `Create Key`.
2. Copy it (it starts with `sk-or-v1-`) into `.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

### Limits of the `:free` models {#limiti-dei-modelli-free}

| Situation | Requests/minute | Requests/day |
|---|---:|---:|
| Never bought credits | 20 | **50** |
| After buying at least $10 once | 20 | 1,000 |

Source: <https://openrouter.ai/docs/api-reference/limits>.

**In the course you buy nothing**: 50 requests a day is not much, so
OpenRouter stays the last link in the fallback chain, not the first. The
current list of free models is at
<https://openrouter.ai/models?q=free>: they all have the `:free` suffix.

You check how many you have left today like this:

```bash
curl -s https://openrouter.ai/api/v1/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

---

## 4. Optional fallbacks {#4-riserve-facoltative}

### Mistral {#mistral}

Free "Experiment" plan at <https://console.mistral.ai/>: no card, but you
need a phone number for verification. The limits are not published: you
read them in Admin → Limits. An honest fallback, but don't count on it.

### Cloudflare Workers AI {#cloudflare-workers-ai}

10,000 free "Neurons" per day on any Workers account
(<https://developers.cloudflare.com/workers-ai/platform/pricing/>). A
Neuron is their unit of compute: for small text models it is enough for a
few hundred answers. Some large models require the paid plan.

### Cerebras — warning, **not part of the course** {#cerebras-attenzione-fuori-dal-corso}

Cerebras was the most generous fallback (1 million tokens per day). As of
September 2026 their documentation says that to activate the API and
Playground **you need a verified payment method**
(<https://inference-docs.cerebras.ai/support/rate-limits>): $5 of free
credit, but you must add the card. The course promises zero cost with no
card, so Cerebras is **not** part of the chain. If you already have it
active, adding it to the gateway is one line: you can work it out
yourself in module 2.

---

## 5. No keys: the local path {#5-nessuna-chiave-la-strada-locale}

If the material you want to store cannot leave your computer, skip this
whole page and use Ollama: models that run on your machine, zero keys,
zero quotas, zero data sent. It is slower and answers worse, but the
course works the same from start to finish. Instructions in
[SETUP.md](SETUP.md#strada-locale-ollama), and in every module you find
the "Local path" box with the differences.

---

## 6. Check that your keys work {#6-controlla-che-le-chiavi-funzionino}

When you have filled in `.env`:

```bash
python moduli/02-chiavi-gateway-e-quote/starter/controlla_chiavi.py
```

For each key present it makes a real, tiny call, and prints whether it
answers, with which model and how much quota you have left. Missing keys:
it skips them and tells you. It is the script you will run again every
time "nothing works anymore": nine times out of ten it's a used-up quota.
