# Laboratorio 2 — Il gateway e il conto dei token

**Durata: 78 minuti.**

Alla fine avrai un gateway che gira sul tuo computer, il tuo sistema che
ci passa attraverso senza saperlo, e uno script che ti dice quanto costa
un lavoro prima di lanciarlo.

---

## Passo 1 — Installa e avvia il gateway (18 minuti)

Un ambiente virtuale tutto suo (il perché è nella lezione, §3):

```bash
python3.12 -m venv .venv-gateway
.venv-gateway/bin/pip install -r requirements-gateway.txt
```

Copia la configurazione nel tuo sistema:

```bash
mkdir -p memoria/gateway
cp moduli/02-chiavi-gateway-e-quote/starter/config.yaml memoria/gateway/
```

Aprila e leggila: sono quaranta righe, le capisci tutte dopo la lezione.

Avvia il gateway. **Lascia questo terminale aperto**: il gateway resta
acceso finché lo tieni lì. Apri un secondo terminale per il resto del
laboratorio.

```bash
set -a; source .env; set +a
.venv-gateway/bin/litellm --config memoria/gateway/config.yaml \
    --host 127.0.0.1 --port 4000
```

La riga `set -a; source .env; set +a` mette le chiavi nell'ambiente: è
così che `os.environ/GROQ_API_KEY` nel file YAML trova qualcosa.

**Non togliere `--host 127.0.0.1`.** Senza, LiteLLM ascolta su
`0.0.0.0`, cioè su tutte le schede di rete del computer: chiunque sia
sulla tua stessa rete — il Wi-Fi del bar, dell'albergo, dell'ufficio —
può usare le tue chiavi attraverso il tuo gateway. Con `127.0.0.1`
risponde solo al tuo computer.

Aspetta la riga `Uvicorn running on http://127.0.0.1:4000`. Se dice
`0.0.0.0`, hai dimenticato `--host`. Poi, **dal secondo terminale**:

```bash
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-memoria-locale" \
  -H "Content-Type: application/json" \
  -d '{"model":"memoria-veloce",
       "messages":[{"role":"user","content":"Rispondi solo: pronto"}],
       "max_tokens":200}' | head -c 400
```

Deve tornare un JSON con `"content":"pronto"` o simile.

> **Perché `max_tokens: 200` e non 5.** I modelli `gpt-oss` ragionano
> prima di rispondere, e il ragionamento consuma il budget. Con
> `max_tokens: 5` ti torna una risposta **vuota** con
> `"finish_reason":"length"`. Non è rotto: è finito lo spazio.

| Sintomo | Causa | Rimedio |
|---|---|---|
| `Connection refused` | il gateway non è partito | guarda il primo terminale |
| `401 Invalid proxy key` | `GATEWAY_KEY` diverso da quello che passi | devono coincidere |
| `os.environ/GROQ_API_KEY` non risolta | hai saltato `set -a; source .env` | rifallo nel terminale del gateway |

## Passo 2 — Fai passare il tuo sistema dal gateway (10 minuti)

In `.env`, commenta le righe del modulo 1 e togli il commento a quelle
del gateway:

```bash
# LLM_PROVIDER=groq
# LLM_MODEL=openai/gpt-oss-120b
LLM_PROVIDER=custom
LLM_ENDPOINT=http://localhost:4000/v1
LLM_MODEL=memoria-veloce
LLM_API_KEY=sk-memoria-locale
```

Adesso rilancia il sistema del modulo 1:

```bash
python memoria/memoria_minima.py "Cosa significa l'errore E4 sulla caldaia Termovex?"
```

**Funziona identico, e non hai toccato una riga di codice.** Questo è il
punto dell'esercizio: il tuo programma non sa più chi gli risponde, e non
gliene importa. Nel terminale del gateway vedi passare la richiesta.

## Passo 3 — Guarda il fallback scattare (15 minuti)

Con una chiave sola non puoi far finire la quota per davvero, ma puoi
rompere il primo anello. Ferma il gateway (`Ctrl-C`) e riavvialo con la
configurazione di prova:

```bash
set -a; source .env; set +a
.venv-gateway/bin/litellm \
  --config moduli/02-chiavi-gateway-e-quote/starter/config-prova-fallback.yaml \
  --host 127.0.0.1 --port 4000
```

Lì dentro `memoria-veloce` punta a `groq/questo-modello-non-esiste`, e la
riserva è un modello vero. Dal secondo terminale:

```bash
curl -s http://localhost:4000/v1/chat/completions \
  -H "Authorization: Bearer sk-memoria-locale" \
  -H "Content-Type: application/json" \
  -d '{"model":"memoria-veloce",
       "messages":[{"role":"user","content":"Rispondi solo: ok"}],
       "max_tokens":200}' | python -c "import sys,json; d=json.load(sys.stdin); print('ha risposto il modello:', d['model'])"
```

Hai chiesto `memoria-veloce`, che è rotto. Ti risponde
`openai/gpt-oss-20b`. **Il campo `model` della risposta dice sempre chi
ha risposto davvero**: è il modo per accorgersi che stai viaggiando sulla
riserva.

Quando hai finito, rimetti il `config.yaml` buono.

## Passo 4 — `stima()` (20 minuti)

```bash
cp moduli/02-chiavi-gateway-e-quote/starter/stima_quota.py memoria/
```

Scrivi la funzione `stima()` dove c'è il TODO. Il conto è tutto nel
commento. Due trappole:

- i token vanno contati **due volte**, perché ogni pezzo viene mandato al
  modello due volte (estrazione e riassunto);
- il tempo minimo non è la somma dei due limiti ma **il più grande dei
  due**: scattano in parallelo.

Provala:

```bash
python memoria/stima_quota.py progetto-finale/corpus/manuali/*.md \
                              progetto-finale/corpus/note/*.md
```

Sul corpus del corso devi ottenere esattamente:

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

Tieni questo numero da parte: nel modulo 5 lancerai il `cognify` vero e
confronterai la stima con il tempo effettivo.

## Passo 5 — Output strutturato (15 minuti)

```bash
python moduli/02-chiavi-gateway-e-quote/starter/estrai_json.py \
  progetto-finale/corpus/note/2026-08-30-caldaia-manutenzione.md
```

Ti torna un JSON con apparecchio, componente, azione, data e l'elenco dei
valori. Non è il modello che ha deciso di rispondere così: è lo schema
che gliel'ha imposto.

Adesso due prove:

1. Cambia `LLM_MODEL` in `.env` mettendo un modello più piccolo (aggiungi
   al `config.yaml` un `model_name: memoria-piccola` con
   `groq/openai/gpt-oss-20b`) e rilancia. Con questo schema semplice
   regge. **Segnati come scrive i numeri**: `1,4 bar` o `1.4 bar`?
2. Aggiungi allo `SCHEMA` un campo obbligatorio che nella nota non c'è —
   per esempio `"costo_ricambi"` — e rilancia. Guarda cosa si inventa il
   modello pur di riempirlo. È la ragione per cui nel modulo 7 i campi
   obbligatori saranno pochissimi.

## Passo 6 — Verifica

```bash
python moduli/02-chiavi-gateway-e-quote/verifica.py
```

Il gateway deve essere acceso, altrimenti la prima riga è già rossa.

---

## Artefatti di questo modulo

- `memoria/gateway/config.yaml` — la tua catena di fornitori
- `memoria/stima_quota.py` — il conto prima di spendere
- `.env` che punta al gateway

`memoria/llm.py` **non l'hai toccato**. Ricordatelo: è la prova che il
disaccoppiamento funziona.
