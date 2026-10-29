# Module 2 — Keys, gateway and quotas {#modulo-2-chiavi-gateway-e-quote}

**Duration: 2 hours** (42 minutes of lesson, 78 of lab).
Running total: 4.0 / 20 hours.

In module 1 you called Groq directly. It works until it stops working:
quota used up, provider under maintenance, model retired. Here you build
the piece of plumbing that protects you from all of this, and you learn to
count before you spend.

---

## 1. First five minutes: look at your quota {#1-primi-cinque-minuti-guarda-la-tua-quota}

```bash
python moduli/02-chiavi-gateway-e-quote/starter/controlla_chiavi.py
```

For every key you put in `.env` it makes a tiny call and prints what the
provider returns in the **headers**, the metadata of the HTTP response.
On Groq you see something like this:

```text
  Groq                 OK  modello openai/gpt-oss-20b
       x-ratelimit-remaining-requests: 999
       x-ratelimit-remaining-tokens: 7921
       x-ratelimit-reset-requests: 1m26.4s
       x-ratelimit-reset-tokens: 592ms
```

Those four numbers are your bank balance. `remaining-tokens: 7921`
means you have 7,921 tokens left this minute; `reset-tokens:
592ms` means the counter restarts in half a second.

**This script is the first place to look when something stops
working.** Nine times out of ten it is not your code: it is a quota.

## 2. How quotas really work {#2-come-funzionano-davvero-le-quote}

Three limits at the same time, and you must respect all of them:

| Acronym | Spelled out | What it limits |
|---|---|---|
| RPM | *requests per minute* | how many calls per minute |
| TPM | *tokens per minute* | how many tokens per minute, question + answer |
| RPD | *requests per day* | how many calls per day |

On the Groq free tier (values from September 2026; the official
rate limits page is <https://console.groq.com/docs/rate-limits>):
30 RPM, 8,000 TPM,
1,000 RPD for text models. The limit that stops you is almost always
the **TPM**: a manual in the prompt is a thousand tokens, and after eight
prompts like that you are stuck for a minute.

The limits apply **per account**, not per key. Getting five keys doubles
nothing.

### The 429 {#il-429}

When you go over, the provider does not send the answer: it sends the
HTTP code **429 Too Many Requests**, usually with a `retry-after`
header that says how many seconds to wait before trying again.

Three ways to react, from worst to best:

| Reaction | What happens |
|---|---|
| ignore it and retry right away | you get another 429, and some providers make the penalty longer |
| wait for `retry-after` and retry | it works, but your program sits idle |
| **switch to another provider** | you do not stop. This is what the gateway does |

## 3. The gateway {#3-il-gateway}

A **gateway** is a program in the middle: your code talks to it, it
talks to the providers.

```text
  il tuo codice  ──►  gateway  ──┬──►  Groq          (primo tentativo)
                   localhost:4000 ├──►  Gemini        (se Groq dice 429)
                                  └──►  OpenRouter    (se anche Gemini è giù)
```

(Your code → gateway → Groq first, Gemini if Groq says 429, OpenRouter if
Gemini is down too.)

What you gain:

| Without a gateway | With a gateway |
|---|---|
| every program knows the keys | only the gateway knows the keys |
| changing provider = changing code | changing provider = changing one line of configuration |
| a 429 stops everything | a 429 triggers the fallback, your code does not notice |
| model names are scattered through the code | models have your own names: `memoria-veloce`, `memoria-occhi` |
| you do not know how much you used | the gateway keeps count |

We use **LiteLLM** (<https://docs.litellm.ai/>), which is two things with
the same name: a Python library and a proxy server. We need the
server.

### Why in a separate virtual environment {#perche-in-un-ambiente-virtuale-separato}

The LiteLLM server and the library that cognee pulls in want different
versions of the same web libraries. Instead of sacrificing one, they
live in two separate virtual environments: `.venv` for the course,
`.venv-gateway` for the server. It is good practice anyway: a service
that runs on its own does not share dependencies with the application
that uses it.

### The configuration {#la-configurazione}

Everything is in a YAML file. The parts that matter:

```yaml
model_list:
  - model_name: memoria-veloce          # il nome che usi TU
    litellm_params:
      model: groq/openai/gpt-oss-120b   # il nome vero, dal fornitore
      api_key: os.environ/GROQ_API_KEY  # la chiave, letta dall'ambiente
      rpm: 28
      tpm: 7500

router_settings:
  fallbacks:
    - memoria-veloce: ["riserva-1", "riserva-2"]
```

(The comments say: the name YOU use; the real name, from the provider;
the key, read from the environment.)

Three things to notice:

1. **`os.environ/GROQ_API_KEY`** means "take it from the environment". The
   keys are not in the file: this file can go on Git.
2. **`rpm` and `tpm`** are set lower than the real limit: the gateway
   stops first and switches to the fallback, instead of getting a 429.
3. **`fallbacks`** is the chain. In order. Your code always asks for
   `memoria-veloce` and knows nothing else.

The names we use for the whole course:

| Name | Who answers | What it is for |
|---|---|---|
| `memoria-veloce` | Groq gpt-oss-120b | questions and extraction: the everyday work |
| `memoria-lunga` | Gemini flash | a whole manual in one go |
| `memoria-occhi` | Gemini flash | photos and scanned PDFs (module 8 and project) |
| `memoria-orecchie` | Groq Whisper | voice notes (final project) |

## 4. Count before you spend {#4-contare-prima-di-spendere}

The question you must ask yourself before you launch a long command is:
**how many calls will it make, and how many tokens?**

Rule of thumb for Italian: **1 token every 4 characters**. It is off by
about 10%, and you do not need to install anything.

From this you can estimate everything. A `cognify` — the module 5
command that builds the graph — makes, for every chunk of text:

| Step | Calls per chunk |
|---|---|
| entity and relationship extraction | 1 |
| chunk summary | 1 |
| embedding (local, uses no quota) | 0 |

So: **2 calls per chunk of text**, plus the length of the chunk in
tokens, twice. The course corpus (17,036 characters) split into
1,000-character chunks makes **22 chunks, 44 calls, about 17,000
tokens**. On the Groq free tier that is **2.1 minutes of forced
waiting**, not two seconds. In the lab you compute it with a script
instead of in your head — and the number it prints is exactly that one.

## 5. Structured output: JSON Schema {#5-output-strutturato-il-json-schema}

So far we asked the model to write text. From module 4 on we will ask it
for **data**: "read this note and give me the appliance, the component,
the action and the numeric values". An answer in prose is no use: you
need something the program can use.

That is what **JSON Schema** is for: you describe the exact shape of the
answer, the provider forces it on the model, and what comes back is
always in the right shape.

```python
response_format={"type": "json_schema", "json_schema": {
    "name": "fatto", "strict": True, "schema": SCHEMA}}
```

It works, with two warnings that will save you an afternoon:

**Small models break on complex schemas.** With a four-field schema,
`gpt-oss-20b` and `gpt-oss-120b` do equally well. With the nested schema
cognee uses to build the graph, the 20b fails and the provider
answers:

```text
{"error":{"message":"Failed to validate JSON. Please adjust your prompt.",
"code":"json_validate_failed"}}
```

It is not your mistake. The model cannot handle it. The cure is to change
the model, not the prompt: you will see it live in module 5.

**Numbers come back the way the model writes them.** On the same note,
the 20b answered `"1,4 bar"` and the 120b `"1.4 bar"`. If your code looks
for the exact string, you lose one of the two cases. Always normalize.

## 6. The local path, in two lines {#6-la-strada-locale-in-due-righe}

> **Box — Local path**
> To move the whole course to Ollama, in `.env`:
> ```bash
> LLM_PROVIDER=ollama
> LLM_ENDPOINT=http://localhost:11434/v1
> LLM_MODEL=qwen3:4b-instruct
> ```
> Nothing else. `memoria/llm.py` checks `LLM_PROVIDER` and changes
> destination. You can keep the gateway or drop it: if you keep it,
> add an `ollama/qwen3:4b-instruct` model to `config.yaml` and
> put it at the end of the fallback chain. That way, when you run out of
> quota, the system keeps working locally instead of stopping.

## 7. Keys and security, once and for all {#7-le-chiavi-e-la-sicurezza-una-volta-sola}

- A key is a password. Whoever has it uses your quota.
- It lives in `.env`. `.env` is in `.gitignore`. Never in the code, never
  in a comment, never in a screenshot.
- If one leaks onto GitHub: **revoke it right away**. Deleting the
  commit is not enough: the history stays, and the bots that scan GitHub
  find it in minutes.
- The gateway's `config.yaml` contains `os.environ/NOME`, not the keys:
  you can put that under version control.
- The gateway has its own password (`GATEWAY_KEY`), otherwise any
  program on your computer can use your quotas.

**Now: [LAB.md](LAB.md).**
