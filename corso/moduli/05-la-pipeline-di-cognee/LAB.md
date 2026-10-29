# Laboratorio 5 — Il quaderno, con cognee sotto

**Durata: 120 minuti**, dei quali una buona parte passata ad aspettare:
portati qualcosa da leggere, o lancia `digerisci` e vai a prendere un
caffè.

Alla fine avrai `memoria/quaderno.py`: un solo programma con dentro tutto
il tuo sistema, e l'archivio costruito sul corpus intero.

**Prima di cominciare**, controlla tre cose:

```bash
python memoria/stima_quota.py progetto-finale/corpus/manuali/*.md \
                              progetto-finale/corpus/note/*.md
python moduli/02-chiavi-gateway-e-quote/starter/controlla_chiavi.py
```

Se ti restano meno di 100.000 token per oggi, rimanda: `cognify` li
mangia.

Il gateway deve essere acceso, e in `.env` serve **`LLM_MODEL` con il
prefisso `openai/`**:

```bash
LLM_PROVIDER=custom
LLM_ENDPOINT=http://localhost:4000/v1
LLM_MODEL=openai/memoria-veloce
LLM_API_KEY=sk-memoria-locale
```

Il prefisso `openai/` dice a cognee «questo è un endpoint compatibile
OpenAI». Senza, non capisce con chi sta parlando e si ferma.

---

## Passo 1 — Il giro su una nota sola (15 minuti)

```bash
python moduli/05-la-pipeline-di-cognee/starter/primo_giro.py
```

Due documenti, una domanda. Guarda i log che scorrono: riconoscerai i
nomi delle fasi della lezione (`classify_documents`, `extract_chunks`,
`extract_graph`, `summarize_text`).

Se finisce con una risposta che cita **sia** i 0,8 bar del libretto
**sia** il vaso di espansione della tua nota, la pipeline funziona.

## Passo 2 — Il tuo programma (35 minuti)

```bash
cp moduli/05-la-pipeline-di-cognee/starter/quaderno.py memoria/
```

Tre TODO, uno per operazione: `aggiungi()`, `digerisci()`, `chiedi()`.
Sono tre chiamate a cognee: la difficoltà non è scriverle, è sapere cosa
fanno.

Prima di lanciare, guarda dove finiranno i dati:

```bash
python memoria/quaderno.py stato
```

Deve dire `dati/cognee`, **non** una cartella dentro `.venv`. Se dice
`.venv`, hai cancellato le due righe di `cognee.config`: rimettile.

## Passo 3 — Digerisci tutto il corpus (30 minuti, quasi tutti di attesa)

```bash
python memoria/quaderno.py azzera
python memoria/quaderno.py aggiungi
python memoria/quaderno.py digerisci
```

`aggiungi` finisce in un minuto. `digerisci` no.

Costa circa **50.000 token**, un quarto della quota giornaliera: puoi
permettertelo tre o quattro volte al giorno. Ma solo se non ritenti a
vuoto — la lezione, paragrafo 6, spiega perché i 429 costano più del
lavoro vero.

Se vuoi iterare in fretta senza consumare, esiste
`python memoria/quaderno.py aggiungi --ridotto`: ingerisce solo caldaia
e lavatrice, 6 documenti invece di 12. Per fare il modulo fino in fondo
non serve, e per il modulo 8 ti servirà comunque il corpus intero.

**Guarda cosa hai appena versato dentro.** Da qui in poi i manuali
entrano come **PDF**, non come i sorgenti Markdown da cui li ho
generati: è la forma in cui ti arrivano nella vita. E uno dei cinque
non entra affatto:

```bash
python -c "import pypdf; print(len(pypdf.PdfReader(
    'progetto-finale/corpus/manuali/greencut-rm46.pdf'
    ).pages[0].extract_text()))"
```

Stampa `0`. `greencut-rm46.pdf` è la fotografia di un libretto di carta,
e per il tuo sistema è una pagina bianca. Il rasaerba, da adesso, nel
tuo archivio non c'è.

Non aggiustarlo adesso. È il muro che apri nel progetto finale, ed è
anche il motivo per cui nel modulo 8 vedrai una riga `ocr 0/2` nel
riassunto: serve a mostrarti che **nessuna modifica al prompt risolve un
documento vuoto**.

Mentre gira, leggi i log. Vedrai comparire da sola questa riga:

```text
Potential RPM issues detected (RateLimitError) — slowing down processing
to accommodate: enabling the RPM limiter (60 requests per 60s)
```

È cognee che si accorge dei 429 e **rallenta da sola**. È la stessa cosa
che hai scritto a mano in `pazienza.py` nel modulo 4, fatta dal motore.

Poi:

```bash
python memoria/quaderno.py arricchisci
```

## Passo 4 — Chiedi (20 minuti)

Le stesse domande del corso, adesso a cognee:

```bash
python memoria/quaderno.py chiedi "Cosa significa l'errore E4 sulla caldaia?"
python memoria/quaderno.py chiedi "Quante ore ho passato in tutto sulla caldaia?"
python memoria/quaderno.py chiedi "Che candela monta il rasaerba?"
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto?"
```

L'ultima è quella che conta: il libretto dice 1,2 bar, la nota del 30
agosto dice 1,4. **Guarda quale delle due ti risponde.** Se ti dà 1,2,
non è un bug: è il problema che affronterai nel modulo 7.

Adesso confronta i tipi di ricerca sulla stessa domanda:

```bash
python memoria/quaderno.py chiedi --testo "Quante ore ho passato sulla caldaia?"
python memoria/quaderno.py chiedi --grafo "Quante ore ho passato sulla caldaia?"
python memoria/quaderno.py chiedi --pezzi "Quante ore ho passato sulla caldaia?"
```

Il terzo comando non risponde: ti fa vedere **cosa ha recuperato**. È lo
strumento che userai ogni volta che una risposta ti sembra sbagliata,
per capire se ha sbagliato il recupero o il modello.

Scrivi in `note-lab5.md` quale dei tre tipi risponde meglio, e perché.

## Passo 5 — Rompi la pipeline (15 minuti)

Metti in `.env`:

```bash
LLM_MODEL=openai/memoria-piccola
```

dopo aver aggiunto al `config.yaml` del gateway:

```yaml
  - model_name: memoria-piccola
    litellm_params:
      model: groq/openai/gpt-oss-20b
      api_key: os.environ/GROQ_API_KEY
```

Riavvia il gateway, poi:

```bash
python memoria/quaderno.py azzera
python memoria/quaderno.py aggiungi
python memoria/quaderno.py digerisci
```

Molto probabilmente si ferma con `json_validate_failed`. Copia il
messaggio di errore in `note-lab5.md` e scrivici accanto, con parole tue,
perché **cambiare il prompt non serve** anche se l'errore lo suggerisce.

Poi rimetti `openai/memoria-veloce` e ricostruisci: ti serve per il
modulo 6.

## Passo 6 — Guarda dove abita il tuo archivio (5 minuti)

```bash
python memoria/quaderno.py stato
ls -la dati/cognee/sistema/databases/
```

Tre database, tre tecnologie: SQLite, Kuzu, LanceDB. È l'argomento del
modulo 6.

## Passo 7 — Verifica

```bash
python moduli/05-la-pipeline-di-cognee/verifica.py
```

---

## Se qualcosa non va

| Sintomo | Causa | Rimedio |
|---|---|---|
| `ProviderNotDeducibleError` | `LLM_MODEL` senza `openai/` davanti | `LLM_MODEL=openai/memoria-veloce` |
| `json_validate_failed` | modello troppo piccolo | `openai/gpt-oss-120b` |
| `Could not load a matching tokenizer ... falling back to TikToken` | manca `transformers`, o manca `HUGGINGFACE_TOKENIZER` nel `.env` | `pip install -r requirements.txt` e controlla il `.env`: con TikToken i pezzi vengono dimensionati male e il modello di embedding ne tronca la coda senza avvisare (modulo 3) |
| `LLM connection test timed out after 30s` | il gateway è acceso ma non riesce a far rispondere il modello | `curl localhost:4000/health/liveliness` dice solo che il gateway è vivo, non che il modello risponde. Prova `python memoria/llm.py`, che deve stampare `pronto`: se si blocca anche quello, ferma il gateway e rilancialo |
| `cognify` si ferma a metà con 429 | quota giornaliera finita | domani, oppure aggiungi un fornitore al gateway |
| `No deployments available for selected model, Try again in N seconds` | non è un limite del fornitore: è il **gateway** che ha messo in panchina tutti i suoi fornitori dopo i 429 | aspetta i secondi che dice. Quel numero non è il tuo `cooldown_time`: quando un fornitore risponde 429, LiteLLM usa il tempo che il fornitore stesso ha indicato, che sul piano gratuito può essere mezz'ora |
| i dati finiscono in `.venv` | mancano le righe `cognee.config` | rimettile in cima a `quaderno.py` |
| `search` restituisce lista vuota | `cognify` non è mai arrivato in fondo | rilancia `digerisci` |
| tutto è lentissimo | è normale sul piano gratuito | `cognify` una volta, `chiedi` quante vuoi |

## Artefatti di questo modulo

`memoria/quaderno.py` e la cartella `dati/cognee/` con l'archivio
costruito. Da qui in poi il corso lavora su questo.
