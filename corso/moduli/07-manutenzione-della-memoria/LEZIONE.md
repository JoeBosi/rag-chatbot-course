# Modulo 7 — Manutenzione della memoria

**Durata: 2 ore** (42 minuti di lezione, 78 di laboratorio).
Totale progressivo: 16,5 / 20 ore.

Fin qui hai costruito. Adesso il problema è **tenerlo vivo**: aggiungere
senza rifare tutto, aggiornare i fatti che cambiano, togliere quello che
non deve restare, e poterlo salvare.

È la parte che nei corsi non si fa mai, ed è quella che decide se fra sei
mesi l'archivio lo usi ancora o l'hai abbandonato.

---

## 1. Primi cinque minuti: la memoria che ti dà l'informazione vecchia

```bash
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia?"
```

Nel corpus ci sono due risposte:

- il **libretto** dice: riportare la pressione a **1,2 bar**;
- la **nota del 30 agosto 2026** dice che il tecnico ha alzato
  l'esercizio a **1,4 bar**, e che quella di marzo «non vale più».

Il sistema, quasi sempre, ti dà 1,2. Non perché sia rotto: perché il
manuale ripete quel numero in tre punti, e la nota lo dice una volta
sola. Il recupero premia la ridondanza, non la data.

**Questo è il quarto fallimento del corso**, e a differenza degli altri
tre non c'è un algoritmo che lo risolve da solo: è un problema di
**governo dei fatti**, e va affrontato di petto.

## 2. Quattro operazioni di manutenzione

| Operazione | Quando serve | Comando cognee |
|---|---|---|
| **aggiungere** | è arrivata una nota nuova | `add` + `cognify` (incrementale) |
| **aggiornare** | un documento è cambiato | `update` |
| **dimenticare** | un documento non deve restare | `forget` |
| **controllare** | «è ancora tutto coerente?» | `validate`, `report` |

### 2.1 Aggiungere senza rifare tutto

```python
await cognee.add("nuova-nota.md", dataset_name="officina")
await cognee.cognify(datasets=["officina"])      # incremental_loading=True
```

`cognify` è **incrementale**: riconosce dall'impronta i documenti già
digeriti e lavora solo sui nuovi. Costa la quota del documento nuovo, non
di tutto l'archivio. È il motivo per cui ha senso versarci dentro una
nota ogni volta che si finisce un lavoro.

### 2.2 Aggiornare un documento

```python
await cognee.update(data_id=..., data="testo nuovo", dataset_id=...)
```

Non è la stessa cosa di cancellare e riaggiungere. `update` **tiene lo
stesso identificativo** del documento e confronta il testo vecchio con
quello nuovo pezzo per pezzo, rifacendo solo i pezzi cambiati. Costa
meno, e soprattutto non spezza i collegamenti del grafo che puntavano a
quel documento.

Per farlo servono `data_id` e `dataset_id`, che si leggono così:

```python
datasets = await cognee.datasets.list_datasets()
documenti = await cognee.datasets.list_data(dataset_id=datasets[0].id)
```

### 2.3 Dimenticare

```python
await cognee.forget(data_id=...,  dataset="officina")   # un documento
await cognee.forget(dataset="officina", memory_only=True)  # il grafo, non i file
await cognee.forget(everything=True)                     # tutto
```

`memory_only=True` è la più interessante: butta via quello che il modello
ha capito, ma tiene i documenti. È quello che fai quando cambi modello o
quando ti accorgi che l'estrazione ha prodotto spazzatura: non devi
ricaricare niente, solo ridigerire.

Esiste anche `cognee.datasets.delete_data(dataset_id, data_id, mode=...)`
con due modi:

| `mode` | Cosa fa |
|---|---|
| `soft` | toglie il documento, lascia le entità che altri documenti condividono |
| `hard` | toglie anche le entità rimaste orfane |

`soft` è il predefinito ed è quasi sempre quello giusto: con `hard`
rischi di cancellare un nodo «Caldaia Termovex TX-24» che serviva anche
alle altre cinque note.

## 3. I fatti che si contraddicono

Questo è il problema serio, e vale la pena capirlo bene prima di provare
a risolverlo.

Un archivio di documenti non ha un concetto di **verità corrente**. Ha
documenti, ognuno vero nel momento in cui è stato scritto. «La pressione
va tenuta a 1,2 bar» era vero a marzo ed è falso da agosto, ma il
documento di marzo è ancora lì e dice ancora quella cosa.

Tre modi di affrontarlo, dal più debole al più forte.

### 3.1 Dare al sistema la data, e dirgli di usarla

Il più semplice: mettere la data nel testo (non solo nel nome del file) e
istruire il modello a preferire il fatto più recente quando due si
contraddicono.

```text
Se due informazioni si contraddicono, usa quella con la data piu'
recente e di' esplicitamente che c'era un valore precedente.
```

Funziona spesso. Non funziona quando il recupero non porta il documento
recente, perché non puoi preferire un fatto che non hai sott'occhio.

### 3.2 Scrivere una nota di rettifica

Il modo **manuale e affidabile**: quando un fatto cambia, aggiungere un
documento che lo dice esplicitamente.

```markdown
# Rettifica del 30 agosto 2026 — Caldaia Termovex TX-24

SUPERA il valore del libretto e le mie note precedenti.
Pressione di esercizio a freddo: 1,4 bar (prima: 1,2 bar).
Precarica vaso di espansione: 1,2 bar (prima: 1,0 bar).
```

È rozzo e funziona, per due motivi: il documento contiene le parole della
domanda («pressione», «esercizio», «bar») quindi viene recuperato, e dice
in modo non ambiguo quale valore vale.

È anche quello che farebbe un manutentore serio con un quaderno di carta:
non cancella, annota la rettifica.

### 3.3 Lasciarlo fare a `memify`

```python
await cognee.memify(dataset="officina")
```

`memify` passa sul grafo e prova a fondere i nodi che sono la stessa
cosa, a pesare i collegamenti, a ricavare fatti nuovi. Sui duplicati di
nome («Lavatrice LAVANOR» e «Lavatrice Lavanor») funziona bene. Sulle
contraddizioni di valore funziona a volte.

**Non fidarti di `memify` per i fatti che contano.** Per la pressione
della caldaia usa il metodo 3.2 e dormi tranquillo.

## 4. Controllare che sia ancora tutto a posto

cognee ha due strumenti di diagnosi che vale la pena conoscere.

```python
report = await cognee.validate(dataset="officina")
```

Confronta il grafo e l'indice vettoriale e dice se sono **d'accordo**:
nodi presenti nel grafo e non nei vettori, o viceversa. Succede quando un
`cognify` si interrompe a metà — cosa che, con le quote gratuite,
succede.

```python
await cognee.report(datasets="officina", output_path="dati/relazione.md")
```

Scrive una relazione in Markdown con:

- i **nodi-mozzo** (*hub*, o «nodi dio»): quelli collegati a tutto.
  Se in cima trovi «bar» o «ore», l'estrazione ha creato un nodo per
  un'unità di misura e ci ha attaccato mezzo archivio;
- i collegamenti inattesi fra parti diverse dell'archivio;
- la provenienza degli archi: da quale documento viene ogni collegamento.

I nodi-mozzo sono il difetto più comune e il più dannoso: rendono tutto
raggiungibile da tutto, e il recupero a due salti smette di selezionare.
Si curano togliendo il tipo di entità che li genera dall'elenco che dai
al modello, e ridigerendo.

## 5. Il backup

Tre tecnologie, tre modi di salvare. Va fatto un elenco e va rispettato.

| Pezzo | Dove | Come si salva |
|---|---|---|
| documenti originali | `dati/cognee/documenti/` | copia della cartella |
| registro | PostgreSQL (o SQLite) | `pg_dump` (o copia del file) |
| vettori | pgvector, dentro Postgres | è nel `pg_dump` |
| grafo | Kuzu, cartella | copia della cartella, **a macchina ferma** |

**Copiare Kuzu mentre il sistema scrive produce un backup rotto.** Come
per SQLite: o fermi il programma, o usi l'esportazione.

Esportazione, che è la via pulita. `cognee.export` ha quattro formati
e **non fanno la stessa cosa**:

| `format` | Cosa ti dà | A cosa serve |
|---|---|---|
| `cogx` | una cartella-archivio | **ripristinare**: `cognee.remember(COGXArchiveSource(percorso))` |
| `json` | un file leggibile | guardarci dentro, versionarlo con git |
| `graphml` | formato standard per grafi | aprirlo in Gephi o simili |
| `cypher` | istruzioni di inserimento | portarlo su Neo4j |

```python
await cognee.export(dataset="officina", format="cogx",
                    destination="dati/backup/archivio")
```

Quello del backup è **`cogx`**: è l'unico che si rimette dentro. `json`
è utile per leggere e per tenere traccia dei cambiamenti, ma non è un
ripristino.

In tutti i casi, un'esportazione batte la copia della cartella: è
indipendente dal motore, e non si rompe se il programma sta scrivendo.

**La regola:** il backup buono è quello che hai provato a ripristinare.
Un backup mai ripristinato non è un backup, è un file.

## 6. Quanto spesso

| Operazione | Ogni quanto |
|---|---|
| `add` + `cognify` della nota nuova | dopo ogni intervento |
| `memify` | ogni dieci-venti documenti nuovi |
| `validate` | dopo ogni `cognify` interrotto |
| `report` | una volta al mese, per guardare i nodi-mozzo |
| backup | prima di ogni esperimento, e comunque una volta al mese |

**Adesso: [LAB.md](LAB.md).**
