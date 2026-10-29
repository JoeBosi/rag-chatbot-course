# Modulo 6 — Dove vive il dato

**Durata: 2 ore** (36 minuti di lezione, 84 di laboratorio).
Totale progressivo: 14,5 / 20 ore.

Fin qui l'archivio è stato una scatola nera con tre file dentro. Adesso
apri la scatola: tre modi diversi di conservare i dati, perché ce ne
vogliono tre, e come si passa da quelli usa-e-getta a quelli veri.

---

## 1. Primi cinque minuti: guarda cosa c'è

```bash
python memoria/quaderno.py stato
ls -la dati/cognee/sistema/databases/
```

Tre cose diverse, non una:

```text
cognee_db              un file SQLite
cognee.kuzu/           una cartella: il grafo
<id-dataset>/          i vettori (LanceDB)
```

Apri il primo con lo strumento più semplice che c'è:

```bash
python -c "
import sqlite3, glob
db = glob.glob('dati/cognee/sistema/databases/cognee_db')[0]
for (nome,) in sqlite3.connect(db).execute(
        \"select name from sqlite_master where type='table' order by name\"):
    print(nome)
"
```

Vedrai una ventina di tabelle: `data`, `datasets`, `pipeline_runs`,
`users`, `acls`. Nessuna contiene i tuoi vettori, e nessuna contiene il
grafo. Perché?

## 2. Tre modelli di dato, tre mestieri

| | Relazionale | Vettoriale | Grafo |
|---|---|---|---|
| Unità | riga in una tabella | vettore con un'etichetta | nodo e arco |
| Domanda tipica | «quali documenti ho caricato il 3 marzo?» | «cosa somiglia a questo?» | «cosa è collegato a questo?» |
| Linguaggio | SQL | nessuno standard | Cypher, Gremlin |
| Costo di una ricerca | indice su colonna: immediato | confronto con tutti i vettori (o indice approssimato) | percorrere archi |
| Nel tuo archivio | SQLite / PostgreSQL | LanceDB / pgvector | Kuzu |

Le tre domande sono davvero diverse, e nessuno dei tre sa rispondere bene
alle domande degli altri.

### Il relazionale: la contabilità

Qui sta il **registro**: quali file hai aggiunto, quando, con che
impronta, in quale dataset, chi può vederli, quali esecuzioni della
pipeline sono andate a buon fine. Non i contenuti: la contabilità dei
contenuti.

Serve perché la domanda «ho già caricato questo file?» si risponde con
un `SELECT`, non con una ricerca semantica.

### Il vettoriale: la somiglianza

Un pezzo di testo sono 384 numeri (modulo 3). Cercare vuol dire trovare
i vettori più vicini a quello della domanda.

Con 48 pezzi puoi confrontarli tutti: sono 48 moltiplicazioni, un
millisecondo. Con 48.000 pezzi diventano 48.000, e con dieci ricerche al
secondo il conto non torna più. Per questo esistono gli **indici
approssimati** (*ANN*, *approximate nearest neighbour*): strutture che
trovano «quasi sempre i più vicini» guardandone una frazione. Il più
diffuso si chiama **HNSW** (*hierarchical navigable small world*): una
rete di collegamenti a più livelli, in cui si scende saltando.

Approssimato vuol dire che ogni tanto ti perdi un risultato. In cambio
la ricerca resta immediata quando i pezzi diventano milioni.

### Il grafo: i collegamenti

Il modulo 4 te l'ha già spiegato. La cosa che un database a grafo fa e
gli altri no è **seguire un arco senza fare una join**. In SQL, «i vicini
dei vicini» è un `JOIN` su se stessa; a tre salti diventa impraticabile.
In Cypher è una riga:

```cypher
MATCH (a)-[*1..2]-(b) WHERE a.name = 'Caldaia Termovex TX-24' RETURN b
```

**Kuzu** è un database a grafo *embedded*: non è un server, è una
cartella di file che la tua applicazione apre direttamente, come SQLite.
Nessun servizio da avviare, nessuna porta, nessuna password.
Documentazione: <https://docs.kuzudb.com/>.

## 3. Perché SQLite non basta più

SQLite è perfetto per cominciare: nessuna installazione, un file solo,
si copia con `cp`. Il corso lo usa fino a qui apposta.

Smette di bastare quando:

| Problema | Cosa succede con SQLite |
|---|---|
| due programmi scrivono insieme | «database is locked»: SQLite ha **uno** scrittore per volta |
| l'archivio vive su un server | il file è sulla macchina, i client no |
| i vettori sono tanti | LanceDB è un secondo sistema da gestire e da salvare a parte |
| vuoi un backup coerente | tre tecnologie, tre modi di salvare |

Il terzo punto è quello che si sente di più: con SQLite hai i metadati in
un posto e i vettori in un altro. Con PostgreSQL + pgvector stanno nello
stesso database, e un `pg_dump` se li porta via tutti e due.

## 4. PostgreSQL e pgvector

**PostgreSQL** è un database relazionale, un servizio vero, con utenti,
connessioni contemporanee, transazioni, backup.

**pgvector** è un'estensione che gli aggiunge un tipo di dato nuovo:
`vector(384)`, e gli operatori per confrontarli.

```sql
CREATE EXTENSION vector;

CREATE TABLE pezzi (
    id     bigserial PRIMARY KEY,
    testo  text,
    punto  vector(384)
);

-- i 5 pezzi piu' vicini a un vettore dato
SELECT testo FROM pezzi ORDER BY punto <-> '[0.1, 0.2, ...]' LIMIT 5;
```

L'operatore **`<->`** è la distanza euclidea; **`<=>`** è la distanza
coseno, quella che abbiamo usato nel modulo 3; **`<#>`** è il prodotto
scalare negato. Sono operatori SQL normali: puoi metterli in una query
con `WHERE`, `JOIN`, `ORDER BY`, tutto.

Questo è il vantaggio vero, e vale la pena vederlo scritto:

```sql
SELECT testo FROM pezzi
WHERE apparecchio = 'Caldaia Termovex TX-24'
  AND data > '2026-06-01'
ORDER BY punto <=> :domanda
LIMIT 5;
```

**Filtro esatto e ricerca per somiglianza nella stessa query.** Con un
database vettoriale separato dovresti fare due ricerche e incrociarle a
mano.

Senza indice, pgvector confronta tutti i vettori. Si aggiunge così:

```sql
CREATE INDEX ON pezzi USING hnsw (punto vector_cosine_ops);
```

Documentazione: <https://github.com/pgvector/pgvector>.

### Docker, in quattro righe

Installare PostgreSQL con pgvector a mano significa compilare
un'estensione. Con Docker è un file di configurazione e un comando,
perché esiste un'immagine già pronta (`pgvector/pgvector:pg17`).

Un **contenitore** è un programma impacchettato con tutto quello che gli
serve. Non è una macchina virtuale: condivide il sistema operativo, e
parte in un secondo. Per il corso serve sapere tre comandi: `up -d` per
avviare, `logs` per guardare, `down` per fermare.

I dati stanno in un **volume**, che sopravvive al contenitore. Fermare
Postgres non cancella niente; `down -v` sì.

## 5. Cosa cambia nel tuo `.env`

Questo è tutto quello che serve per migrare:

```bash
DB_PROVIDER=postgres
DB_NAME=cognee_db
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=cognee
DB_PASSWORD=cognee
VECTOR_DB_PROVIDER=pgvector
```

Sei righe. Il codice di `quaderno.py` non cambia di una virgola: è lo
stesso disaccoppiamento del gateway, applicato ai database.

**Quello che i sei righe non fanno: migrare i dati.** I documenti già
digeriti restano in SQLite; il nuovo database è vuoto. Bisogna rifare
`add` e `cognify`, e quindi rispendere la quota. Sul corpus del corso
sono quattro minuti; su un archivio vero è una decisione da prendere
prima, non dopo. **Se pensi che finirai su PostgreSQL, comincia da
PostgreSQL.**

## 6. Guardare dentro al grafo

Kuzu si interroga in **Cypher**, il linguaggio dei database a grafo. Tre
query che userai sempre:

```cypher
// quanti nodi ci sono, per tipo
MATCH (n) RETURN labels(n) AS tipo, count(*) AS quanti ORDER BY quanti DESC;

// i vicini di un nodo
MATCH (a)-[r]-(b) WHERE a.name CONTAINS 'Termovex' RETURN a.name, type(r), b.name;

// i nodi piu' collegati: sono quelli che contano
MATCH (n)-[r]-() RETURN n.name, count(r) AS grado ORDER BY grado DESC LIMIT 10;
```

L'ultima è diagnostica: se in cima trovi un nodo generico come «bar» o
«ore», vuol dire che l'estrazione ha creato un nodo per un'unità di
misura e ci ha attaccato mezzo archivio. È esattamente il tipo di difetto
che si vede solo guardando.

Puoi anche chiederlo a cognee con `SearchType.CYPHER`, senza aprire Kuzu
a mano.

## 7. Quanto occupa

Sul corpus del corso, dopo `cognify`:

| Pezzo | Dimensione tipica |
|---|---|
| documenti copiati | quanto gli originali |
| SQLite (metadati) | poche centinaia di KB |
| Kuzu (grafo) | pochi MB |
| LanceDB (vettori) | ~1,5 KB per pezzo (384 numeri a 4 byte, più l'indice) |

La regola da portarsi via: **i vettori occupano quasi quanto il testo**,
e il grafo occupa poco. Un archivio di diecimila pezzi sta in qualche
decina di MB. Non è il disco il tuo problema: è la quota.

**Adesso: [LAB.md](LAB.md).**
