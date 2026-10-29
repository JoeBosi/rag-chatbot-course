# Le chiavi gratuite, fornitore per fornitore

**Limiti verificati il 20 settembre 2026.** I fornitori li cambiano senza
preavviso: l'ultima parola ce l'ha sempre la pagina ufficiale linkata in
ogni riquadro. È esattamente il motivo per cui nel [modulo 2](moduli/02-chiavi-gateway-e-quote/LEZIONE.md)
mettiamo un gateway davanti a tutti: se uno cambia le regole, il corso
continua a funzionare con gli altri.

## Regola che vale per tutti

**Nessun fornitore di questo corso chiede una carta di credito.** Se una
schermata te la chiede, hai sbagliato pagina o hai cliccato su un piano a
pagamento: torna indietro. L'unica eccezione è segnalata più sotto
(Cerebras) e per questo motivo il corso **non** la usa.

**Una chiave è una password.** Va in `.env`, mai dentro il codice, mai in
un commit. `.env` è già in `.gitignore`. Se una chiave finisce per sbaglio
su GitHub, revocala e rifalla: non basta cancellare il commit.

## Quante ne servono davvero

| Chiave | Serve per | Obbligatoria? |
|---|---|---|
| Groq | il modello che ragiona + la trascrizione delle note vocali | **sì**, dal modulo 1 |
| Google AI Studio | contesti lunghi, descrizione delle foto, OCR dei PDF scansionati | **sì**, dal progetto finale |
| OpenRouter | confrontare modelli diversi, terza rete di sicurezza | consigliata, dal modulo 2 |
| Mistral | riserva | no |
| Cloudflare Workers AI | riserva | no |

Puoi fare i primi due moduli con la sola chiave Groq.

---

## 1. Groq

Il più veloce dei tre. Nessuna carta, registrazione con email o account
Google.

1. Vai su <https://console.groq.com/keys> e accedi.
2. `Create API Key`, dai un nome (`corso-memoria`), copia la chiave.
3. **La chiave si vede una volta sola.** Se la perdi, ne fai un'altra.
4. Incollala in `.env`:

```bash
GROQ_API_KEY=gsk_...
```

### Limiti del piano gratuito

| Modello | Richieste/minuto | Richieste/giorno | Token/minuto | Token/giorno |
|---|---:|---:|---:|---:|
| `openai/gpt-oss-120b` | 30 | 1.000 | 8.000 | 200.000 |
| `openai/gpt-oss-20b` | 30 | 1.000 | 8.000 | 200.000 |
| `qwen/qwen3.8-27b` | 30 | 1.000 | 8.000 | 200.000 |
| `whisper-large-v3` | 20 | 2.000 | — | — |
| `whisper-large-v3-turbo` | 20 | 2.000 | — | — |

I limiti valgono **per account**, non per chiave: farne cinque non serve a
niente. Tabella aggiornata: <https://console.groq.com/docs/rate-limits>.

**Guarda l'ultima colonna, non la seconda.** Il numero che conta è
`200.000 token al giorno`, e quasi nessuno se ne accorge in tempo.

Misurato sul corpus di questo corso: una chiamata di estrazione pesa fra
**900 e 4.300 token**, mediana circa **2.100**, perché oltre al testo
porta le istruzioni e lo schema JSON della risposta. Fai il conto:

```
200.000 token al giorno / ~2.500 token a chiamata = ~80 chiamate al giorno
```

**Ottanta chiamate.** Non mille. Il limite da 1.000 richieste al giorno
non lo vedrai mai: finirai i token molto prima.

Cosa vuol dire in pratica:

| Operazione | Chiamate | Token | Quante volte al giorno |
|---|---:|---:|---|
| una domanda all'archivio | 1-3 | ~5.000 | quante vuoi |
| digerire una nota nuova | 3-6 | ~10.000 | quante vuoi |
| digerire il corpus del corso da zero | ~24 | ~50.000 | tre o quattro |

Tre o quattro volte al giorno è comodo. Ma c'è una trappola, ed è la
ragione per cui questa pagina insiste tanto:

> **Ogni ritentativo dopo un 429 rimanda il prompt per intero, e ti
> viene riconteggiato.**

Non è il lavoro utile a consumare la giornata: sono i tentativi
sprecati. Un `cognify` configurato male, che si prende trenta 429 e li
ripete, costa **più del doppio** di uno configurato bene, a parità di
risultato. Con la configurazione del modulo 5 i 429 scendono a due o
tre; senza, ne ho contati trentuno sullo stesso identico lavoro.

Morale: il freno non serve a essere educati con il fornitore, serve a
non buttare via la tua quota.

**E se la finisci davvero?** Il messaggio cambia: dice `tokens per day
(TPD)` invece di `per minute`, e lì non c'è attesa breve che basti. Non
si azzera a mezzanotte: è una **finestra di 24 ore**, e si riapre quando
escono dalla finestra i consumi di ieri. In pratica: la giornata è
finita, e il lavoro riprende il giorno dopo, nella fascia oraria in cui
avevi consumato. Una buona notizia: le richieste **respinte** con `per
day` non vengono conteggiate, quindi riprovare costa tempo e non quota.

I limiti dei piani gratuiti cambiano senza preavviso: i valori qui sono
di settembre 2026, la pagina sempre aggiornata è
[console.groq.com/docs/rate-limits](https://console.groq.com/docs/rate-limits).

Conviene saperlo prima di passare la serata a guardare un terminale che
ritenta.

Gli **8.000 token al minuto** sono il secondo vincolo: rallentano, non
fermano. Nel modulo 2 impari a contare prima di lanciare, e nel modulo 5
a mettere il freno giusto.

### Quale modello usare

| Modello | Quando |
|---|---|
| `openai/gpt-oss-120b` | **predefinito del corso.** L'estrazione di entità in JSON gli riesce |
| `openai/gpt-oss-20b` | più veloce, ma sbaglia il JSON strutturato: te lo facciamo vedere nel modulo 5 |
| `whisper-large-v3-turbo` | trascrizione delle note vocali: veloce e sufficiente |
| `whisper-large-v3` | trascrizione più accurata, se il turbo capisce male |

---

## 2. Google AI Studio (Gemini)

Il migliore per i testi lunghi e l'unico gratuito che guarda le
**immagini**: nel progetto finale descrive le foto dei pezzi e legge i PDF
scansionati.

1. Vai su <https://aistudio.google.com/apikey> con un account Google.
2. `Create API key` → scegli o crea un progetto.
3. Copia la chiave (inizia per `AIza`) in `.env`:

```bash
GEMINI_API_KEY=AIza...
```

### Limiti del piano gratuito

Google **non pubblica più una tabella fissa**: i limiti dipendono dal
modello e dal progetto, e li vedi sulla tua dashboard:
<https://aistudio.google.com/rate-limit>. Quelli che trovi in giro per i
modelli `flash` — circa 10 richieste al minuto e qualche centinaio al
giorno — sono indicativi, non ufficiali.

Modelli gratuiti a settembre 2026 (fonte sempre aggiornata:
<https://ai.google.dev/gemini-api/docs/pricing>):

| Modello | Uso nel corso |
|---|---|
| `gemini-3.5-flash` | descrizione delle foto, OCR, contesti lunghi |
| `gemini-3.5-flash-lite` | riassunti a basso costo |
| `gemini-2.5-flash` | alternativa se i 3.x non sono disponibili nella tua area |
| `gemini-embedding-2` | embedding via API, se non vuoi calcolarli sul tuo computer |

### Avvertenza specifica

La pagina dei prezzi di Google, per il piano gratuito, dice testualmente
che i contenuti **vengono usati per migliorare i loro prodotti**; sul piano
a pagamento dice il contrario. Tradotto: quello che mandi a Gemini con la
chiave gratuita può finire nell'addestramento. Vale lo stesso per gli
altri. Manuali di elettrodomestici: nessun problema. Contratti, referti,
dati di clienti: mai.

---

## 3. OpenRouter

Una chiave sola per una ventina di modelli gratuiti di fornitori diversi.
Nel corso serve per **confrontare** modelli senza aprire altri account, e
come terza rete di sicurezza quando Groq e Google hanno finito la quota.

1. <https://openrouter.ai/keys>, accedi, `Create Key`.
2. Copia (inizia per `sk-or-v1-`) in `.env`:

```bash
OPENROUTER_API_KEY=sk-or-v1-...
```

### Limiti dei modelli `:free`

| Situazione | Richieste/minuto | Richieste/giorno |
|---|---:|---:|
| Senza aver mai comprato crediti | 20 | **50** |
| Dopo aver comprato almeno 10 $ una volta | 20 | 1.000 |

Fonte: <https://openrouter.ai/docs/api-reference/limits>.

**Nel corso non compri niente**: 50 richieste al giorno sono poche, quindi
OpenRouter resta l'ultimo anello della catena di riserve, non il primo.
L'elenco dei modelli gratuiti del momento è su
<https://openrouter.ai/models?q=free>: hanno tutti il suffisso `:free`.

Quante te ne restano oggi lo chiedi così:

```bash
curl -s https://openrouter.ai/api/v1/key \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

---

## 4. Riserve facoltative

### Mistral

Piano gratuito «Experiment» su <https://console.mistral.ai/>: niente carta,
serve un numero di telefono per la verifica. I limiti non sono pubblicati:
li leggi in Admin → Limits. Riserva onesta, ma non contarci.

### Cloudflare Workers AI

10.000 «Neuron» al giorno gratis su qualunque account Workers
(<https://developers.cloudflare.com/workers-ai/platform/pricing/>). Un
Neuron è la loro unità di calcolo: per i modelli piccoli di testo bastano
per qualche centinaio di risposte. Alcuni modelli grossi richiedono il
piano a pagamento.

### Cerebras — attenzione, **fuori dal corso**

Cerebras era la riserva più generosa (1 milione di token al giorno). Al
settembre 2026 la loro documentazione dice che per attivare API e Playground
**serve un metodo di pagamento verificato**
(<https://inference-docs.cerebras.ai/support/rate-limits>): 5 $ di credito
omaggio, ma la carta la devi mettere. Il corso promette costo zero senza
carta, quindi Cerebras **non** fa parte della catena. Se ce l'hai già
attiva, aggiungerla al gateway è una riga: te lo spieghi da solo nel
modulo 2.

---

## 5. Nessuna chiave: la strada locale

Se il materiale che vuoi archiviare non può uscire dal tuo computer, salti
tutta questa pagina e usi Ollama: modelli che girano da te, zero chiavi,
zero quote, zero dati inviati. È più lento e risponde peggio, ma il corso
funziona lo stesso dall'inizio alla fine. Istruzioni in
[SETUP.md](SETUP.md#strada-locale-ollama), e in ogni modulo trovi il
riquadro «Strada locale» con le differenze.

---

## 6. Controlla che le chiavi funzionino

Quando hai riempito `.env`:

```bash
python moduli/02-chiavi-gateway-e-quote/starter/controlla_chiavi.py
```

Per ogni chiave presente fa una chiamata vera, minuscola, e stampa se
risponde, con che modello e quanta quota ti resta. Chiavi assenti: le
salta e te lo dice. È lo script che rilancerai ogni volta che «non
funziona più niente»: nove volte su dieci è una quota finita.
