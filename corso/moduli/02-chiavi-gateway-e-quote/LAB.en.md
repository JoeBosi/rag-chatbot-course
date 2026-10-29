# Lab 2 — The gateway and counting tokens {#laboratorio-2-il-gateway-e-il-conto-dei-token}

**Duration: 78 minutes.**

At the end you will have a gateway running on your computer, your system
going through it without knowing, and a script that tells you how much a
job costs before you launch it.

---

## Step 1 — Install and start the gateway (18 minutes) {#passo-1-installa-e-avvia-il-gateway-18-minuti}

A virtual environment of its own (the reason is in the lesson, §3):

```bash
python3.12 -m venv .venv-gateway
.venv-gateway/bin/pip install -r requirements-gateway.txt
```

Copy the configuration into your system:

```bash
mkdir -p memoria/gateway
cp moduli/02-chiavi-gateway-e-quote/starter/config.yaml memoria/gateway/
```

Open it and read it: it is forty lines, and after the lesson you
understand all of them.

Start the gateway. **Leave this terminal open**: the gateway stays on as
long as you keep it there. Open a second terminal for the rest of the
lab.

```bash
set -a; source .env; set +a
.venv-gateway/bin/litellm --config memoria/gateway/config.yaml \
    --host 127.0.0.1 --port 4000
```

The line `set -a; source .env; set +a` puts the keys in the environment:
that is how `os.environ/GROQ_API_KEY` in the YAML file finds something.

**Do not remove `--host 127.0.0.1`.** Without it, LiteLLM listens on
`0.0.0.0`, that is, on every network card of the computer: anyone on
your same network — the Wi-Fi at the café, the hotel, the office — can
use your keys through your gateway. With `127.0.0.1` it answers only
your own computer.

Wait for the line `Uvicorn running on http://127.0.0.1:4000`. If it says
`0.0.0.0`, you forgot `--host`. Then, **from the second terminal**:

```bash
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-memoria-locale" \
  -H "Content-Type: application/json" \
  -d '{"model":"memoria-veloce",
       "messages":[{"role":"user","content":"Rispondi solo: pronto"}],
       "max_tokens":200}' | head -c 400
```

("Rispondi solo: pronto" means "Answer only: ready".)

You must get back a JSON with `"content":"pronto"` or similar.

> **Why `max_tokens: 200` and not 5.** The `gpt-oss` models reason
> before answering, and the reasoning uses up the budget. With
> `max_tokens: 5` you get an **empty** answer with
> `"finish_reason":"length"`. It is not broken: it ran out of room.

| Symptom | Cause | Fix |
|---|---|---|
| `Connection refused` | the gateway did not start | look at the first terminal |
| `401 Invalid proxy key` | `GATEWAY_KEY` differs from the one you pass | they must match |
| `os.environ/GROQ_API_KEY` not resolved | you skipped `set -a; source .env` | run it again in the gateway terminal |

## Step 2 — Route your system through the gateway (10 minutes) {#passo-2-fai-passare-il-tuo-sistema-dal-gateway-10-minuti}

In `.env`, comment out the module 1 lines and uncomment the gateway
ones:

```bash
# LLM_PROVIDER=groq
# LLM_MODEL=openai/gpt-oss-120b
LLM_PROVIDER=custom
LLM_ENDPOINT=http://localhost:4000/v1
LLM_MODEL=memoria-veloce
LLM_API_KEY=sk-memoria-locale
```

Now run the module 1 system again:

```bash
python memoria/memoria_minima.py "Cosa significa l'errore E4 sulla caldaia Termovex?"
```

(The question means: "What does error E4 on the Termovex boiler mean?")

**It works exactly the same, and you did not touch a line of code.** That
is the point of the exercise: your program no longer knows who answers
it, and it does not care. In the gateway terminal you see the request go
through.

## Step 3 — Watch the fallback kick in (15 minutes) {#passo-3-guarda-il-fallback-scattare-15-minuti}

With a single key you cannot really run out of quota, but you can break
the first link. Stop the gateway (`Ctrl-C`) and restart it with the test
configuration:

```bash
set -a; source .env; set +a
.venv-gateway/bin/litellm \
  --config moduli/02-chiavi-gateway-e-quote/starter/config-prova-fallback.yaml \
  --host 127.0.0.1 --port 4000
```

In there, `memoria-veloce` points to `groq/questo-modello-non-esiste`
("this model does not exist"), and the fallback is a real model. From the
second terminal:

```bash
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-memoria-locale" \
  -H "Content-Type: application/json" \
  -d '{"model":"memoria-veloce",
       "messages":[{"role":"user","content":"Rispondi solo: ok"}],
       "max_tokens":200}' | python -c "import sys,json; d=json.load(sys.stdin); print('ha risposto il modello:', d['model'])"
```

You asked for `memoria-veloce`, which is broken. The answer comes from
`openai/gpt-oss-20b`. **The `model` field of the response always says who
really answered**: that is how you notice you are running on the
fallback.

When you are done, put the good `config.yaml` back.

## Step 4 — `stima()` (20 minutes) {#passo-4-stima-20-minuti}

```bash
cp moduli/02-chiavi-gateway-e-quote/starter/stima_quota.py memoria/
```

Write the `stima()` function where the TODO is. The whole calculation is
in the comment. Two traps:

- tokens must be counted **twice**, because every chunk is sent to the
  model twice (extraction and summary);
- the minimum time is not the sum of the two limits but **the larger of
  the two**: they run in parallel.

Try it:

```bash
python memoria/stima_quota.py progetto-finale/corpus/manuali/*.md \
                              progetto-finale/corpus/note/*.md
```

On the course corpus you must get exactly:

```text
documenti                    12
caratteri                 17036
pezzi da 1000 caratteri         22
chiamate al modello          44
token (stima)             17036

limite token:    2.1 minuti
limite chiamate: 1.5 minuti
=> tempo minimo: 2.1 minuti (comanda il limite piu' stretto)
```

Keep this number handy: in module 5 you will run the real `cognify` and
compare the estimate with the actual time.

## Step 5 — Structured output (15 minutes) {#passo-5-output-strutturato-15-minuti}

```bash
python moduli/02-chiavi-gateway-e-quote/starter/estrai_json.py \
  progetto-finale/corpus/note/2026-08-30-caldaia-manutenzione.md
```

You get back a JSON with appliance, component, action, date and the list
of values. The model did not decide to answer this way: the schema
forced it to.

Now two experiments:

1. Change `LLM_MODEL` in `.env` to a smaller model (add a
   `model_name: memoria-piccola` with `groq/openai/gpt-oss-20b` to
   `config.yaml`) and run it again. With this simple schema it
   holds up. **Note how it writes numbers**: `1,4 bar` or `1.4 bar`?
2. Add to `SCHEMA` a required field that is not in the note — for
   example `"costo_ricambi"` (spare parts cost) — and run it again. Look at
   what the model makes up just to fill it. That is why in module 7
   there will be very few required fields.

## Step 6 — Check {#passo-6-verifica}

```bash
python moduli/02-chiavi-gateway-e-quote/verifica.py
```

The gateway must be running, otherwise the first line is already red.

---

## What you keep from this module {#artefatti-di-questo-modulo}

- `memoria/gateway/config.yaml` — your provider chain
- `memoria/stima_quota.py` — the count before you spend
- `.env` pointing to the gateway

You **did not touch** `memoria/llm.py`. Remember it: it is the proof that
the decoupling works.
