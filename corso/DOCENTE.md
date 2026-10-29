# Note per chi insegna

Questa pagina non è per gli studenti. Dice **perché** il corso è fatto
così, quali scelte sono state prese fra le tante possibili, e cosa si
rompe per primo.

---

## 1. Le scelte prese, e perché

Ogni volta che c'era più di una strada, il corso prende quella più
semplice per lo studente. Qui sono elencate tutte, con il motivo: se in
aula si decide di cambiarne una, conviene sapere cosa si tocca.

### 1.1 Gli embedding si calcolano in locale, non via API

**Scelta:** `EMBEDDING_PROVIDER=fastembed`, modello
`paraphrase-multilingual-MiniLM-L12-v2`, 384 dimensioni, 0,22 GB.

**Perché:** un `cognify` del corpus fa qualche centinaio di chiamate di
embedding. Farle via API brucia la quota giornaliera del modulo 5 prima
di arrivare al modulo 8. In locale sono gratis, non hanno limite di
velocità, e girano su CPU in pochi secondi.

**Effetto collaterale utile:** gli embedding sono l'unica parte del
sistema che lo studente vede funzionare senza internet. È la
dimostrazione concreta che «RAG» non vuol dire «tutto in cloud».

**Prezzo:** un modello a 384 dimensioni è più debole di
`text-embedding-3-large`. Sul corpus del corso non si nota; su un
corpus grosso sì.

### 1.2 Cerebras è stato tolto dai fornitori

Cerebras sarebbe una riserva naturale, veloce e con un piano gratuito.
A settembre 2026 però chiede un metodo di pagamento anche per quel
piano. Il vincolo «zero costi,
nessuna carta di credito» è più forte dell'elenco dei fornitori, quindi
è fuori. Restano Groq (principale), Google AI Studio e OpenRouter
(riserve), Mistral e Cloudflare citati come opzionali in `CHIAVI.md`.

### 1.3 Niente Windows

`SETUP.md` copre macOS e Linux. Per Windows rimanda a WSL2 in due righe
e non lo collauda.

Non è pigrizia: Docker Desktop, i percorsi dei file e i permessi di Kuzu
su Windows nativo sono tre fonti di problemi che non insegnano niente
sull'argomento del corso.

### 1.4 Il gateway ha un ambiente Python separato

`litellm[proxy]` e `cognee` non stanno nello stesso ambiente: cognee
richiede `litellm<1.97`, e il server proxy di quella versione vuole una
FastAPI più nuova di quella che cognee accetta.

Due ambienti — `.venv` e `.venv-gateway` — è la soluzione corretta, non
un ripiego: il gateway **è** un servizio separato, che nella vita vera
gira su un'altra macchina. Vederlo installato a parte fin da subito
insegna la cosa giusta.

È spiegato in `SETUP.md` §4-bis. Se uno studente prova a installare
tutto insieme, `pip` glielo rifiuta con un messaggio chiaro.

### 1.5 Il grafo Kuzu si chiama `.pkl`, e non è un pickle

Il trabocchetto del modulo 6, e ci sono cascato io per primo mentre
scrivevo il corso.

cognee 1.6 salva il grafo di ogni dataset in un file chiamato
`<id-archivio>.pkl`, **qualunque motore ci sia sotto**. Con
`GRAPH_DATABASE_PROVIDER=kuzu` quel file è un database Kuzu a tutti gli
effetti — accanto c'è il suo `.pkl.wal`, che è il registro delle
scritture di Kuzu — ma il nome dice un'altra cosa.

Conseguenza: qualunque controllo che cerchi «kuzu» nel nome del file
fallisce, e ti convinci di avere un problema di configurazione che non
hai. `trova_kuzu()` in `ispeziona.py` quindi **apre** i candidati invece
di guardarne il nome, e il laboratorio fa fare allo studente la stessa
scoperta in prima persona.

La lezione generale che ci si porta via vale ben oltre cognee: il
suffisso di un file è un'opinione di chi l'ha scritto.

Nota su `GRAPH_DATASET_DATABASE_HANDLER=kuzu`: con
`GRAPH_DATABASE_PROVIDER=kuzu` cognee 1.6 la imposta già da sola (c'è un
validatore che lo fa). Resta nel `.env` esplicita, con il commento che
spiega perché, così chi cambia motore domani non si trova il grafo
altrove senza capire perché.

### 1.6 Il freno di cognee si misura in richieste, non in token

Il punto che ha richiesto più tempo da capire, ed è finito nel modulo 5
perché è il più utile di tutto il corso.

Su Groq gratuito il limite che si colpisce per primo **non** è quello
sulle richieste (30 al minuto) ma quello sui token (8.000 al minuto),
perché ogni chiamata di estrazione pesa circa 3.000 token fra
istruzioni, schema JSON e testo.

Il limitatore interno di cognee 1.6.0 (`LLM_RATE_LIMIT_*`) conta **solo
le richieste**: `LLM_RATE_LIMIT_TOKENS` è dichiarato nella
configurazione ma non usato dal percorso di codice attivo. Quindi il
budget va convertito a mano:

```
8.000 token al minuto / 3.000 token a chiamata = 2 richieste al minuto
LLM_RATE_LIMIT_REQUESTS=1
LLM_RATE_LIMIT_INTERVAL=30
```

Con `25` (che sembra prudente, visto che il limite è 30) non frena
niente e si prendono 429 a raffica.

**E si scrive `1 / 30`, non `2 / 60`.** Il limitatore di cognee è un
secchiello (`aiolimiter.AsyncLimiter`): con `2 / 60` le due chiamate
possono partire nello stesso istante, e due chiamate insieme fanno
6-8.000 token in due secondi — cioè esattamente il 429 che si voleva
evitare. La velocità media è la stessa, la raffica no.

**Conseguenza da dire in aula:** un `cognify` del corpus completo
impiega mezz'ora abbondante sul piano gratuito Groq, e sono quasi tutti
minuti di attesa. Non è il codice lento, è la quota. Il rimedio vero è
l'estensione 5 della rubrica: due fornitori con lo stesso `model_name`
nel gateway, e il tempo si dimezza.

**In aula:** fai lanciare il `digerisci` **prima** della pausa, non
dopo. Oppure distribuisci un archivio già digerito (vedi §4).

### 1.7 La quota giornaliera, e chi se la mangia davvero

Il limite di cui nessuno parla è il tetto **giornaliero** di token:
**200.000** sul piano gratuito Groq. Non i 30 messaggi al minuto, non
gli 8.000 token al minuto.

Misurato: una chiamata di estrazione pesa fra 900 e 4.300 token
(mediana ~2.100), perché porta le istruzioni e lo schema JSON oltre al
testo. Il corpus del corso si spezza in ~12 pezzi, due chiamate a pezzo:
**~24 chiamate, ~50.000 token**. Cioè un quarto della giornata. Il
corpus ci sta comodamente, tre o quattro volte.

**Quello che mangia la quota sono i ritentativi.** Ogni 429 fa rimandare
il prompt per intero, e viene riconteggiato. Sullo stesso identico
`cognify` ho contato:

| Configurazione | Errori 429 | Token buttati |
|---|---:|---:|
| `rpm`/`tpm` impostati nel gateway con un solo fornitore | 66 | ~140.000 |
| freno `2 richieste / 60 s` (a raffica) | 31 | ~65.000 |
| freno `1 richiesta / 30 s` | 3 | ~6.000 |

Il punto da portare in aula è questo: **il freno non è educazione verso
il fornitore, è la quota che difendi.** Senza freno i 429 arrivano
comunque, e ogni ritentativo rimanda il prompt per intero: la quota
finisce prima del lavoro.

In aula: se un gruppo esaurisce i 200.000 token, il messaggio cambia da
`per minute` a `per day` e non c'è attesa che tenga. Serve l'archivio
già digerito da distribuire (§4), o una seconda chiave.

Due cose da sapere sulla quota giornaliera, misurate su un account
esaurito (settembre 2026):

- le richieste **respinte** con `per day` non vengono conteggiate: il
  contatore `Used` è rimasto fermo a 199.926 mentre ne rifiutava 62. Cioè
  ritentare costa tempo, non quota, e `cognify` è incrementale: riprende
  dai documenti che mancano. Un ciclo "riprova più tardi" non spreca niente;
- non è una finestra che si ricarica di continuo. Ho ritentato ogni ora
  per ventiquattro ore e l'ho sempre trovata chiusa, poi si è riaperta
  tutta insieme. Quindi non promettere alla classe che "fra un'ora si
  sblocca": a quota finita, quella giornata è finita.

**La seconda chiave, come si aggiunge davvero.** Non serve un secondo
fornitore: bastano due conti gratuiti dello stesso, elencati due volte
sotto lo **stesso** `model_name`. LiteLLM li tratta come due sportelli
dello stesso sportello e alterna fra i due:

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

Non è nel `config.yaml` del corso perché la seconda chiave non ce l'hanno
tutti, e una riserva senza chiave fa più danno che bene (§ regola nel
file). In aula però è la mossa che sblocca una giornata: due conti su due
docenti, e la quota raddoppia. Qui è servita esattamente a questo, per
verificare i moduli 5, 7 e 8 quando il primo conto era esaurito.

**Nota su `--ridotto`.** `quaderno.py aggiungi --ridotto` ingerisce solo
caldaia e lavatrice (6 documenti). Non serve per fare il corso — il
corpus intero ci sta — ma è comodo quando si vuole provare e riprovare,
o se in aula si è già consumato molto.

### 1.8 La panchina del gateway è corta

`cooldown_time: 10` e `allowed_fails: 3`, non `60` e `1`.

Con un solo fornitore configurato — che è la situazione di chi ha solo
la chiave Groq — `allowed_fails: 1` significa che al primo 429 LiteLLM
risponde «nessun deployment disponibile» per un minuto intero, e cognee
ci mette sopra il suo backoff. Il risultato è un lavoro da venti minuti
che ne impiega quaranta.

Con due o più fornitori veri, i valori alti tornano ad avere senso: è
spiegato nel commento dentro `config.yaml`.

### 1.9 La valutazione confronta frammenti, non usa un modello giudice

Un secondo modello come giudice sarebbe più fine. Confrontare frammenti
costa zero quota, dà sempre lo stesso risultato, e su risposte con
dentro un numero o un codice ricambio ci prende quasi sempre.

I suoi due difetti (falsi negativi su «un bar e quattro», falsi positivi
su «1,4» dentro una frase che dice il contrario) sono scritti nella
lezione 8 invece che nascosti, ed è per questo che le `attese` sono
sempre numeri e codici, mai frasi.

Il tipo `assente` ha una regola sua, perché il confronto di frammenti lì
non funziona: vedi lezione 8 §3.

### 1.10 Moduli 1-4 sui Markdown, moduli 5-8 sui PDF

Una differenza voluta che un docente attento nota subito.

Gli script fatti a mano dei moduli 1-4 (`pezzi.py`, `lessicale.py`,
`semantica.py`, `grafo.py`) leggono i **sorgenti Markdown** dei manuali.
Da `quaderno.py` in poi, cioè dai moduli 5-8 e dal progetto, si
ingeriscono i **PDF**.

Non è una svista. Nei primi quattro moduli si studia come funziona il
recupero, e mettere di mezzo l'estrazione del testo dai PDF aggiunge una
variabile che non c'entra. Dal modulo 5, invece, il corpus è quello vero
— ed è lì che `greencut-rm46.pdf`, la scansione, diventa un muro.

**Conseguenza concreta:** nel modulo 3 il rasaerba risponde, dal modulo 5
non risponde più. È dichiarato nel laboratorio 5 e ricompare come
`ocr 0/2` nel riassunto del modulo 8. Se in aula qualcuno chiede «ma
prima funzionava», la risposta è: prima leggevi il sorgente, adesso
leggi il documento.

Se questa differenza dà fastidio, si allinea in una riga: in
`quaderno.py`, `documenti_del_corpus()` torna a `CORPUS.rglob("*.md")`.
Ma allora il modulo 8 non mostra più il fallimento OCR, e il requisito
R1 del progetto perde il suo motivo.

### 1.11 `transformers` serve, anche senza PyTorch

Un problema che si manifesta solo come un avviso in mezzo ai log, e che
degrada in silenzio la qualità:

```text
Could not load a matching tokenizer for fastembed model
'...paraphrase-multilingual-MiniLM-L12-v2' (No module named 'transformers').
Falling back to TikToken, so token counts are approximate.
```

TikToken è il tokenizzatore di OpenAI e non c'entra niente con il
modello di embedding che usiamo. Il conteggio dei token decide **quanto
lunghi fare i pezzi**, e il modello di embedding regge **512 token**:
contarli male vuol dire produrre pezzi che sforano, e il testo in
eccesso viene troncato dall'embedder senza che nessuno lo dica.

Rimedio, già nel corso: `transformers==4.57.1` in `requirements.txt` e
`HUGGINGFACE_TOKENIZER=...` nel `.env`. Si installa **senza PyTorch**
(servono solo i tokenizzatori, non i modelli), quindi sono una decina di
megabyte, non un gigabyte.

Verifica che sia a posto:

```bash
python -c "
from dotenv import load_dotenv; load_dotenv('.env')
from cognee.infrastructure.llm.tokenizer.resolver import resolve_embedding_tokenizer
t = resolve_embedding_tokenizer(provider='fastembed',
    model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
print(type(t).__name__)
"
```

Deve stampare `HuggingFaceTokenizer`. Se stampa qualcosa con `TikToken`
dentro, manca il pacchetto.

### 1.12 Il corpus è inventato

Cinque apparecchi verosimili e nessuno vero. Motivo: un manuale vero è
coperto da copyright e non si può distribuire con un corso, e un manuale
vero è anche troppo lungo per il tempo che c'è.

I PDF si rigenerano con `tools/genera_corpus.py`, che li costruisce dai
sorgenti Markdown in `progetto-finale/corpus/manuali/`.

### 1.13 Un solo nome di modello nel `.env`, due lettori diversi

Dal modulo 2 il `.env` dice `LLM_MODEL=openai/memoria-veloce`. Lo leggono
in due: cognee, che passa per la libreria litellm e ha bisogno di quel
`openai/` per capire che deve parlare con un indirizzo compatibile
OpenAI; e `memoria/llm.py`, che usa il client OpenAI diretto e manderebbe
il nome così com'è. Il gateway conosce solo `memoria-veloce` e risponde
`400 Invalid model name passed in model=openai/memoria-veloce`.

Si poteva tenere due variabili separate. Si è scelto di lasciarne una
sola e far togliere il prefisso a `llm.py` quando parla col gateway
(`LLM_PROVIDER=custom`): una variabile in meno da sbagliare. Se uno
studente ha una versione vecchia di `llm.py` presa dal modulo 1 e la
verifica del modulo 2 fallisce con quel 400, la causa è questa.

---

## 2. I quattro fallimenti, e perché sono lì

Un sistema che funziona subito non insegna perché è fatto così. Il
corso fa costruire quattro versioni sbagliate più una, le fa rompere sui
dati dello studente, e solo dopo dà quella giusta.

| # | Dove | Cosa fallisce | Cosa insegna |
|---|---|---|---|
| 1 | modulo 1 | il modello inventa la risposta su un apparecchio che non conosce | perché serve il recupero |
| 2 | modulo 3 | il taglio cieco spezza in due la tabella dell'errore E4 | perché il chunking non è un dettaglio |
| 3 | modulo 4 | «quante ore in tutto?»: il recupero porta pezzi giusti e la risposta è sbagliata | perché serve il grafo |
| 4 | modulo 7 | la memoria dà il valore vecchio (1,2 bar) | che i fatti invecchiano, e nessun algoritmo lo risolve da solo |
| bonus | modulo 2 | `gpt-oss-20b` si rompe sullo schema JSON annidato (`json_validate_failed`) | che «modello più piccolo» ha un costo concreto e misurabile |

**Il quarto è il più importante e il più facile da saltare in aula**,
perché non ha una soluzione tecnica elegante: si risolve scrivendo una
nota di rettifica, cioè facendo quello che farebbe un manutentore con un
quaderno di carta. Vale la pena fermarsi lì cinque minuti.

Il bonus del modulo 2 è tenuto apposta: è un errore vero, incontrato
scrivendo il corso, e riprodurlo mostra che l'errore non era del codice.

---

## 3. Le ore

| # | Modulo | Ore | di cui lab |
|---|---|---|---|
| 1 | Perché serve una memoria | 2,0 | 1,0 |
| 2 | Chiavi, gateway e quote | 2,0 | 1,3 |
| 3 | Come un testo diventa cercabile | 3,0 | 2,0 |
| 4 | Dal recupero al grafo | 2,5 | 1,7 |
| 5 | La pipeline di cognee | 3,0 | 2,0 |
| 6 | Dove vive il dato | 2,0 | 1,4 |
| 7 | Manutenzione della memoria | 2,0 | 1,3 |
| 8 | Valutare il proprio sistema | 2,0 | 1,4 |
| — | Progetto finale | 1,5 | 1,5 |
| | **totale** | **20,0** | **13,6** |

13,6 ore di laboratorio su 20: più di due terzi del tempo si passa a
scrivere e lanciare codice, non ad ascoltare.

**Le ore non contano l'attesa delle quote.** Il `digerisci` del modulo 5
e il giro di valutazione del modulo 8 sono minuti in cui non si fa
niente. In aula vanno lanciati prima di una pausa.

---

## 4. Come portarlo in aula

**Il giorno prima.** Fai fare a tutti `SETUP.md` fino alla fine, con la
chiave Groq già presa. Il download del modello di embedding (0,22 GB)
su venti macchine contemporaneamente è l'unico momento in cui la rete
dell'aula conta.

**Porta un archivio già digerito.** Una copia di `dati/cognee/` fatta da
te, da distribuire a chi rimane indietro sul modulo 5. Sono 30-40
minuti di attesa che non insegnano niente a chi li ha già visti una
volta.

**Il modulo 6 richiede Docker.** Se in aula non c'è, il modulo funziona
lo stesso su SQLite e LanceDB: si perde la parte su PostgreSQL e
pgvector, che è la metà. Meglio verificarlo prima.

**Dividi in due giornate**, se puoi: moduli 1-4 e moduli 5-8 più il
progetto. Il modulo 4 chiude un discorso (perché il recupero da solo non
basta) e il 5 ne apre un altro (una libreria che lo fa per te).

---

## 5. Cosa si rompe per primo

In ordine di probabilità.

1. **Le quote gratuite cambiano.** I numeri in `CHIAVI.md` sono
   di settembre 2026 e sono la cosa che invecchia prima: le pagine
   ufficiali dei limiti, linkate in `CREDITI.md`, restano la fonte buona.
   Controllali prima di ogni edizione.
2. **cognee cambia API.** È a versione 1.6 e si muove in fretta. Le
   versioni in `requirements.txt` sono bloccate apposta: se le sblocchi,
   metti in conto di rifare i moduli 5, 6 e 7.
3. **Un fornitore toglie il piano gratuito.** È successo a Cerebras
   mentre scrivevo. Il gateway serve anche a questo: si cambia una
   sezione di `config.yaml` e il codice dello studente non se ne accorge.
4. **I modelli cambiano nome.** `openai/gpt-oss-120b` su Groq oggi.
   Quando sparirà, si cambia in `config.yaml` e in `.env.example`, in due
   punti.

---

## 6. Dove sono le soluzioni

Ogni modulo ha `starter/` (con i TODO) e `soluzione/` (completa). Gli
studenti copiano da `starter/` in `memoria/` e lavorano lì; `verifica.py`
guarda dentro `memoria/`.

`verifica.py` distingue lo starter dalla soluzione: cerca il
`NotImplementedError` e lo segnala. Non è aggirabile cancellando la riga
senza scrivere il codice, perché i controlli successivi provano le
funzioni su casi di cui si sa già l'esito.

Nessun `verifica.py` chiama il modello, tranne l'ultimo controllo del
modulo 7: se il gateway è spento lo salta e lo dice.

**Le risposte alle domande aperte** dei laboratori (quelle che finiscono
in `RISPOSTE.md`) stanno in `soluzione/RISPOSTE.md` dentro il modulo che
le pone: moduli 7 e 8. Non sono in nessun menu del sito, si aprono
sapendo il percorso. Nel modulo 7 c'è anche
`soluzione/rettifica-pressione.md`, cioè la nota di rettifica già
scritta, da usare se in aula il tempo stringe.
