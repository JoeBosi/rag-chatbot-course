# Modulo 5 — La pipeline di cognee

**Durata: 3 ore** (60 minuti di lezione, 120 di laboratorio).
Totale progressivo: 12,5 / 20 ore.

Nei moduli 3 e 4 hai costruito a mano: chunking, BM25, embedding,
estrazione di entità, visita del grafo. Adesso butti via tutto e usi un
motore che fa quelle cose meglio di te.

Non era tempo perso: senza quei quattro moduli, quello che segue sarebbe
magia. Con quei quattro moduli, è software.

---

## 1. Primi cinque minuti: il giro completo

```bash
python moduli/05-la-pipeline-di-cognee/starter/primo_giro.py
```

Prende **una** nota di intervento, la digerisce e risponde a una domanda.
Ci mette un minuto o due. Alla fine hai un grafo, dei vettori e una
risposta che incrocia il manuale e la tua esperienza, scritti con **sei
righe di codice vero**:

```python
await cognee.add(testo, dataset_name="officina")
await cognee.cognify(datasets=["officina"])
risultati = await cognee.search(query_text="...",
                                query_type=SearchType.GRAPH_COMPLETION,
                                datasets=["officina"])
```

Tutto il modulo 4 sta dentro la seconda riga.

## 2. Cos'è cognee

Un **motore di memoria**: prende documenti, ne ricava un grafo di entità
e relazioni più un indice vettoriale, e risponde a domande usando tutti e
due. Codice aperto, si installa con `pip`, gira sul tuo computer.

Il modello che ha in testa si chiama **ECL**: *Extract, Cognify, Load* —
estrai, elabora, carica. È la parafrasi di ETL (*Extract, Transform,
Load*), il modo in cui da trent'anni si spostano i dati nei magazzini
aziendali; la parola in mezzo cambia perché al posto di una
trasformazione meccanica c'è un modello che capisce il testo.

Documentazione: <https://docs.cognee.ai/>.

## 3. Le quattro operazioni

### `add` — metti dentro

```python
await cognee.add(["percorso/al/file.md", "..."], dataset_name="officina")
```

Cosa fa: copia i file in una cartella sua, riconosce il formato (ne
gestisce una quarantina: testo, PDF, DOCX, immagini, audio), ne estrae il
testo grezzo, registra ogni documento in una tabella con un identificativo
e un'impronta del contenuto.

Cosa **non** fa: non chiama il modello, non costruisce niente. È veloce e
**non consuma quota**. Se rilanci `add` sullo stesso file, l'impronta è
la stessa e cognee non lo duplica.

Il **dataset** è il nome dell'archivio. Puoi averne più d'uno — `casa`,
`lavoro`, `bici` — e interrogarne uno solo o tutti insieme.

### `cognify` — capisci

```python
await cognee.cognify(datasets=["officina"])
```

Questo è il comando che costa. In ordine:

| Fase | Cosa succede | Chiama il modello? |
|---|---|---|
| 1. classificazione | che tipo di documento è | sì, una volta per documento |
| 2. permessi | chi può vedere cosa | no |
| 3. spezzatura | il testo diventa pezzi | no |
| 4. estrazione | entità e relazioni da ogni pezzo | **sì, una per pezzo** |
| 5. riassunto | un riassunto per pezzo | **sì, una per pezzo** |
| 6. embedding | ogni pezzo diventa 384 numeri | no (girano da te) |
| 7. scrittura | nodi e archi nel grafo, vettori nell'indice | no |

Le fasi 4 e 5 sono le due chiamate per pezzo di cui parlava il modulo 2.
Il conto che hai imparato a fare lì vale esattamente qui.

### `memify` — riordina

```python
await cognee.memify(dataset="officina")
```

Passa **sul grafo già costruito** e lo migliora: fonde nodi che sono la
stessa cosa, rinforza i collegamenti usati spesso, ricava fatti nuovi da
quelli che ci sono, toglie nodi che non servono più.

È la differenza fra un archivio e una **memoria**: un archivio contiene
quello che ci hai messo, una memoria si riorganizza. È anche la ragione
per cui il titolo di questo corso dice «memoria» e non «ricerca».

`memify` richiede che `cognify` sia già passato: non ingerisce niente di
nuovo.

### `search` — chiedi

```python
await cognee.search(query_text="...", query_type=SearchType.GRAPH_COMPLETION,
                    datasets=["officina"])
```

cognee ha **venti** tipi di ricerca. Questi sono quelli che userai:

| Tipo | Cosa fa | Quando serve |
|---|---|---|
| `GRAPH_COMPLETION` | risponde seguendo il grafo | domande a più salti: «quante ore in tutto» |
| `RAG_COMPLETION` | risponde usando solo i pezzi di testo | domande dirette: «che candela monta» |
| `HYBRID_COMPLETION` | tutti e due (è il predefinito) | quando non sai |
| `CHUNKS` | ti dà i pezzi grezzi, senza risposta | per **capire cosa ha recuperato** |
| `CHUNKS_LEXICAL` | come sopra, ma ricerca per parole | codici e sigle esatte |
| `SUMMARIES` | i riassunti dei pezzi | scorrere un archivio grande |
| `CYPHER` | esegui una query sul grafo | ispezione (modulo 6) |
| `TEMPORAL` | domande con dentro il tempo | «cosa ho fatto a settembre» |

`CHUNKS` è il più importante quando qualcosa non va: separa «il recupero
ha sbagliato» da «il modello ha sbagliato». Sono due problemi diversi con
due cure diverse.

## 4. Dove finiscono i dati

**Attenzione, perché la risposta predefinita è sbagliata.** Se non gliela
cambi, cognee scrive dentro la cartella della libreria, in
`.venv/lib/python3.12/site-packages/cognee/.cognee_system/`. Cioè: i tuoi
dati vivono in un posto che sparisce con un `pip uninstall` o con un
`rm -rf .venv`.

Due righe, all'inizio del programma, sistemano la cosa:

```python
cognee.config.system_root_directory("dati/cognee/sistema")
cognee.config.data_root_directory("dati/cognee/documenti")
```

Cosa trovi lì dentro:

| Cartella | Contenuto | Tecnologia |
|---|---|---|
| `documenti/` | i file originali, copiati | filesystem |
| `sistema/databases/cognee_db` | tabelle: documenti, dataset, esecuzioni | SQLite |
| `sistema/databases/cognee.kuzu` | il grafo: nodi e archi | Kuzu |
| `sistema/databases/cognee.lancedb` | i vettori | LanceDB |

Tre database diversi perché servono tre cose diverse. Il modulo 6 è
dedicato a questo.

## 5. Il fallimento da vedere: il modello che non ce la fa

Adesso la parte utile. Metti in `.env` il modello piccolo:

```bash
LLM_MODEL=openai/gpt-oss-20b
```

e rilancia `cognify`. Con ogni probabilità ottieni questo:

```text
CognifyFailedError: Cognify failed for dataset '['officina']':
BadRequestError: GroqException - {"error":{"message":"Failed to validate
JSON. Please adjust your prompt. See 'failed_generation' for more
details.","type":"invalid_request_error","code":"json_validate_failed"}}
```

Non è un errore tuo e non si aggiusta cambiando il prompt, nonostante sia
quello che il messaggio suggerisce. Sta succedendo questo:

- per costruire il grafo, cognee chiede al modello un JSON annidato:
  un elenco di nodi, ognuno con un elenco di archi, ognuno con tipi
  vincolati;
- `gpt-oss-20b` con uno schema di quattro campi ci riesce (l'hai visto
  nel modulo 2), con questo no;
- il fornitore valida la risposta contro lo schema, la trova sbagliata e
  restituisce 422 invece di darti spazzatura.

**Che il fornitore si accorga dell'errore è una fortuna.** Senza
validazione stretta ti ritroveresti un grafo silenziosamente monco, e lo
scopriresti fra tre mesi da una risposta sbagliata.

La cura è una sola: **un modello più capace per l'estrazione**. Rimetti
`openai/gpt-oss-120b` e riparte.

> Nota per chi usa Ollama o un endpoint compatibile: in quel caso cognee
> non usa lo schema stretto ma chiede «un oggetto JSON» e si corregge da
> sola se la risposta non torna. È più tollerante e più lento, e sbaglia
> in silenzio più spesso. Con un modello locale da 4 miliardi di
> parametri aspettati un grafo più povero.

## 6. Quanto ci mette, davvero

Sul corpus del corso — 12 documenti, 14.775 caratteri estraibili (5
manuali in PDF, di cui uno scansionato che ne dà zero, più 7 note) — con
il piano gratuito di Groq e il freno configurato come sopra:

| Comando | Chiamate al modello | Tempo misurato |
|---|---|---|
| `add` | 0 | 90 secondi |
| `cognify` | ~24 | **decine di minuti**, quasi tutti di attesa |
| `memify` | poche | meno di un minuto |
| `search` | 1-3 | pochi secondi |

**E adesso il numero che conta davvero.** Quelle ~24 chiamate, a circa
2.100 token l'una, fanno **~50.000 token**: un quarto della quota
giornaliera di Groq, che è di **200.000 token al giorno**. Puoi
digerire questo corpus tre o quattro volte in una giornata.

Se non sprechi niente.

Perché c'è una trappola, ed è il motivo per cui il freno di poco fa non
è un dettaglio:

> **Ogni ritentativo dopo un 429 rimanda il prompt per intero, e ti
> viene riconteggiato.**

Il lavoro utile non cambia; i tentativi buttati sì. Sullo stesso
identico `cognify` ho contato **trentuno** errori 429 con il freno
scritto male (`2 richieste ogni 60 secondi`) e **tre** con quello
scritto bene (`1 ogni 30`). Trentuno ritentativi da 2.100 token sono
**65.000 token buttati**: più di quanto costi l'intero lavoro.

E quando la quota giornaliera finisce davvero, il messaggio è diverso da
quello che hai già visto:

```text
Rate limit reached ... on tokens per day (TPD): Limit 200000, Used 199852
```

`per day`, non `per minute`. Lì aspettare non serve: devi aspettare
domani. Se ci arrivi, quasi sempre non è perché hai digerito troppo, è
perché hai ritentato troppo.

Due cose da tenere a mente, quindi:

| | |
|---|---|
| **il freno** | non è educazione verso il fornitore, è la tua quota che difendi |
| **`cognify` è incrementale** | se un giro si interrompe, il successivo riprende, non ricomincia |

Se vuoi provare e riprovare senza pensarci — o se hai in mano un corpus
molto più grande di questo — `quaderno.py aggiungi --ridotto` ingerisce
solo due apparecchi invece di cinque. Serve a iterare in fretta, non a
finire il corso: il corpus intero ci sta comodamente.

Il rapporto è quello che conta: **digerire è caro, chiedere è quasi
gratis**. Si digerisce una volta e si chiede mille volte. È il motivo per
cui vale la pena costruire una memoria invece di incollare i documenti
nel prompt ogni volta.

## 7. Cosa hai guadagnato rispetto al modulo 4

| | Grafo fatto a mano | cognee |
|---|---|---|
| Spezzatura | la tua, 30 righe | consapevole del tipo di documento |
| Estrazione | uno schema tuo | schema più ricco, con riassunti |
| Nomi doppi | «Lavatrice LAVANOR» e «Lavatrice Lavanor» | `memify` li fonde |
| Aggiunta di un documento | ricostruisci tutto | incrementale |
| Recupero | grafo **oppure** vettori | tutti e due insieme |
| Formati | solo `.md` | una quarantina, PDF e immagini compresi |
| Cancellazione selettiva | no | sì (modulo 7) |

E cosa **non** hai guadagnato: la certezza. cognee sbaglia come
sbagliavi tu, solo in modo più difficile da vedere. Il modulo 8 esiste
per questo.

**Adesso: [LAB.md](LAB.md).**
