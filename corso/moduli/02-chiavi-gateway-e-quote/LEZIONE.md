# Modulo 2 — Chiavi, gateway e quote

**Durata: 2 ore** (42 minuti di lezione, 78 di laboratorio).
Totale progressivo: 4,0 / 20 ore.

Nel modulo 1 hai chiamato Groq direttamente. Funziona finché non smette:
quota finita, fornitore in manutenzione, modello ritirato. Qui costruisci
il pezzo di impianto che ti protegge da tutto questo, e impari a contare
prima di spendere.

---

## 1. Primi cinque minuti: guarda la tua quota

```bash
python moduli/02-chiavi-gateway-e-quote/starter/controlla_chiavi.py
```

Per ogni chiave che hai messo in `.env` fa una chiamata piccolissima e
stampa quello che il fornitore risponde negli **header**, cioè nei
metadati della risposta HTTP. Su Groq vedi qualcosa del genere:

```text
  Groq                 OK  modello openai/gpt-oss-20b
       x-ratelimit-remaining-requests: 999
       x-ratelimit-remaining-tokens: 7921
       x-ratelimit-reset-requests: 1m26.4s
       x-ratelimit-reset-tokens: 592ms
```

Quei quattro numeri sono il tuo conto in banca. `remaining-tokens: 7921`
vuol dire che in questo minuto ti restano 7.921 token; `reset-tokens:
592ms` vuol dire che tra mezzo secondo il contatore riparte.

**Questo script è il primo posto dove guardare quando qualcosa smette di
funzionare.** Nove volte su dieci non è il tuo codice: è una quota.

## 2. Come funzionano davvero le quote

Tre limiti contemporaneamente, tutti da rispettare:

| Sigla | Sciolta | Cosa limita |
|---|---|---|
| RPM | *requests per minute* | quante chiamate al minuto |
| TPM | *tokens per minute* | quanti token al minuto, domanda + risposta |
| RPD | *requests per day* | quante chiamate al giorno |

Sul piano gratuito di Groq (valori di settembre 2026; la pagina
ufficiale dei limiti e' <https://console.groq.com/docs/rate-limits>):
30 RPM, 8.000 TPM,
1.000 RPD per i modelli di testo. Il limite che ti fermerà è quasi sempre
il **TPM**: un manuale nel prompt sono mille token, e dopo otto prompt
così sei fermo per un minuto.

I limiti valgono **per account**, non per chiave. Farsi cinque chiavi non
raddoppia niente.

### Il 429

Quando sfori, il fornitore non risponde con la risposta: risponde con il
codice HTTP **429 Too Many Requests**, e di solito un header
`retry-after` che dice fra quanti secondi riprovare.

Tre modi di reagire, dal peggiore al migliore:

| Reazione | Cosa succede |
|---|---|
| ignorarlo e ritentare subito | ti becchi un altro 429, e alcuni fornitori allungano la punizione |
| aspettare `retry-after` e ritentare | funziona, ma il tuo programma sta fermo |
| **passare a un altro fornitore** | non ti fermi. È quello che fa il gateway |

## 3. Il gateway

Un **gateway** è un programma che sta in mezzo: il tuo codice parla con
lui, lui parla con i fornitori.

```text
  il tuo codice  ──►  gateway  ──┬──►  Groq          (primo tentativo)
                   localhost:4000 ├──►  Gemini        (se Groq dice 429)
                                  └──►  OpenRouter    (se anche Gemini è giù)
```

Cosa ci guadagni:

| Senza gateway | Con gateway |
|---|---|
| ogni programma conosce le chiavi | le chiavi le conosce solo il gateway |
| cambiare fornitore = cambiare codice | cambiare fornitore = cambiare una riga di configurazione |
| un 429 ferma tutto | un 429 fa scattare la riserva, il codice non se ne accorge |
| i nomi dei modelli sono sparsi nel codice | i modelli hanno nomi tuoi: `memoria-veloce`, `memoria-occhi` |
| non sai quanto hai consumato | il gateway tiene il conto |

Noi usiamo **LiteLLM** (<https://docs.litellm.ai/>), che è due cose con lo
stesso nome: una libreria Python e un server proxy. A noi serve il
server.

### Perché in un ambiente virtuale separato

Il server di LiteLLM e la libreria che cognee si porta dentro vogliono
versioni diverse delle stesse librerie web. Invece di sacrificarne uno,
stanno in due ambienti virtuali distinti: `.venv` per il corso,
`.venv-gateway` per il server. È anche la pratica giusta a prescindere:
un servizio che gira per conto suo non condivide le dipendenze con
l'applicazione che lo usa.

### La configurazione

Tutto sta in un file YAML. Le parti che contano:

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

Tre cose da notare:

1. **`os.environ/GROQ_API_KEY`** significa «prendila dall'ambiente». Le
   chiavi non stanno nel file: questo file può finire su Git.
2. **`rpm` e `tpm`** dichiarati più bassi del limite vero: il gateway si
   ferma prima e passa alla riserva, invece di prendersi il 429.
3. **`fallbacks`** è la catena. In ordine. Il tuo codice chiede sempre
   `memoria-veloce` e non sa nient'altro.

I nomi che useremo per tutto il corso:

| Nome | Chi risponde | A cosa serve |
|---|---|---|
| `memoria-veloce` | Groq gpt-oss-120b | domande e estrazione: il lavoro di tutti i giorni |
| `memoria-lunga` | Gemini flash | un manuale intero in un colpo |
| `memoria-occhi` | Gemini flash | foto e PDF scansionati (modulo 8 e progetto) |
| `memoria-orecchie` | Groq Whisper | note vocali (progetto finale) |

## 4. Contare prima di spendere

La domanda che devi saperti fare prima di lanciare un comando lungo è:
**quante chiamate farà, e quanti token?**

Regola pratica per l'italiano: **1 token ogni 4 caratteri**. Sbaglia del
10 % circa, e non richiede di installare niente.

Da qui si stima tutto. Un `cognify` — il comando del modulo 5 che
costruisce il grafo — fa, per ogni pezzo di testo:

| Passaggio | Chiamate per pezzo |
|---|---|
| estrazione di entità e relazioni | 1 |
| riassunto del pezzo | 1 |
| embedding (locale, non consuma quota) | 0 |

Quindi: **2 chiamate ogni pezzo di testo**, più la lunghezza del pezzo in
token, due volte. Il corpus del corso (17.036 caratteri) spezzato in
pezzi da 1.000 caratteri fa **22 pezzi, 44 chiamate, circa 17.000
token**. Sul piano gratuito di Groq sono **2,1 minuti di attesa
forzata**, non due secondi. Nel laboratorio lo calcoli con uno script
invece che a mente — e il numero che ti stampa è quello lì.

## 5. Output strutturato: il JSON Schema

Fin qui abbiamo chiesto al modello di scrivere testo. Dal modulo 4 in poi
gli chiederemo **dati**: «leggi questa nota e dammi l'apparecchio, il
componente, l'azione e i valori numerici». Una risposta in prosa non
serve: serve qualcosa che il programma possa usare.

Per questo esiste il **JSON Schema**: descrivi la forma esatta della
risposta, il fornitore la impone al modello, e quello che torna è per
forza della forma giusta.

```python
response_format={"type": "json_schema", "json_schema": {
    "name": "fatto", "strict": True, "schema": SCHEMA}}
```

Funziona, ma con due avvertenze che ti risparmieranno un pomeriggio:

**I modelli piccoli si rompono sugli schemi complicati.** Con uno schema
di quattro campi, `gpt-oss-20b` e `gpt-oss-120b` se la cavano uguale. Con
lo schema annidato che cognee usa per costruire il grafo, il 20b fallisce
e il fornitore risponde:

```text
{"error":{"message":"Failed to validate JSON. Please adjust your prompt.",
"code":"json_validate_failed"}}
```

Non è un errore tuo. È il modello che non ce la fa. La cura è cambiare
modello, non cambiare prompt: lo rivedrai dal vivo nel modulo 5.

**I numeri tornano come li scrive il modello.** Sulla stessa nota, il 20b
ha risposto `"1,4 bar"` e il 120b `"1.4 bar"`. Se il tuo codice cerca la
stringa esatta, uno dei due casi lo perdi. Normalizza sempre.

## 6. La strada locale, in due righe

> **Riquadro — Strada locale**
> Per passare tutto il corso su Ollama, in `.env`:
> ```bash
> LLM_PROVIDER=ollama
> LLM_ENDPOINT=http://localhost:11434/v1
> LLM_MODEL=qwen3:4b-instruct
> ```
> Nient'altro. `memoria/llm.py` guarda `LLM_PROVIDER` e cambia
> destinazione. Il gateway puoi tenerlo o toglierlo: se lo tieni,
> aggiungi al `config.yaml` un modello `ollama/qwen3:4b-instruct` e
> mettilo in fondo alla catena delle riserve. Così, quando finisci le
> quote, il sistema continua a funzionare in locale invece di fermarsi.

## 7. Le chiavi e la sicurezza, una volta sola

- Una chiave è una password. Chi ce l'ha consuma la tua quota.
- Sta in `.env`. `.env` sta in `.gitignore`. Mai nel codice, mai in un
  commento, mai in uno screenshot.
- Se te ne scappa una su GitHub: **revocala subito**. Cancellare il
  commit non basta, la cronologia resta e i robot che scandagliano GitHub
  la trovano in minuti.
- Il `config.yaml` del gateway contiene `os.environ/NOME`, non le chiavi:
  quello puoi versionarlo.
- Il gateway ha una sua password (`GATEWAY_KEY`), altrimenti qualunque
  programma sul tuo computer può usare le tue quote.

**Adesso: [LAB.md](LAB.md).**
