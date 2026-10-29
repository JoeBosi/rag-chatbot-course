# Laboratorio 6 — Aprire la scatola e cambiare il motore

**Durata: 84 minuti.**

Alla fine avrai l'archivio su PostgreSQL con pgvector, il grafo in Kuzu
davvero ispezionabile, e uno strumento per guardarci dentro.

**Serve Docker.** Se non ce l'hai:
<https://docs.docker.com/engine/install/> (Linux) oppure Docker Desktop
(macOS). Verifica con `docker run --rm hello-world`.

---

## Passo 1 — Guarda cosa c'è adesso (15 minuti)

```bash
cp moduli/06-dove-vive-il-dato/starter/ispeziona.py memoria/
python memoria/ispeziona.py relazionale
python memoria/ispeziona.py vettori
```

La parte SQLite è già scritta. Guarda le tabelle: `data` ha una riga per
documento, `datasets` una per archivio, `pipeline_runs` una per
esecuzione. Confronta il numero di righe di `data` con i documenti che
hai caricato: devono coincidere.

Poi:

```bash
python memoria/ispeziona.py grafo
```

Guarda cosa c'è nella cartella:

```bash
ls -la dati/cognee/sistema/databases/*/
```

Trovi un `cognee_db` (SQLite), una cartella `....lance.db` (i vettori), e
un file che si chiama **`<id-archivio>.pkl`**, con accanto un
`.pkl.wal`.

Il `.pkl` sembra un file Python serializzato. **Non lo è.** Aprilo:

```bash
python -c "
import kuzu, pathlib
p = next(pathlib.Path('dati/cognee/sistema/databases').rglob('*.pkl'))
c = kuzu.Connection(kuzu.Database(str(p)))
r = c.execute('MATCH (n) RETURN count(*)')
print(p.name, '->', r.get_next()[0], 'nodi')
"
```

Risponde. **Quel `.pkl` è un database Kuzu**: cognee 1.6 dà quel nome al
file del grafo qualunque motore ci sia sotto, e il `.pkl.wal` accanto è
il registro delle scritture, che è una cosa da Kuzu, non da pickle.

È la lezione più utile di tutto il modulo, e vale ben oltre cognee:

> **Il suffisso di un file è un'opinione di chi l'ha scritto. Per sapere
> cosa c'è dentro, lo apri.**

Per questo `trova_kuzu()` in `ispeziona.py` non cerca per nome: prova ad
aprire ogni candidato e tiene il primo che risponde in Cypher.

Nel `.env` la riga che governa il motore dei grafi per-dataset è:

```bash
GRAPH_DATASET_DATABASE_HANDLER=kuzu
```

Con `GRAPH_DATABASE_PROVIDER=kuzu` cognee 1.6 la imposta già da sola, ma
scriverla esplicitamente ti risparmia una sorpresa il giorno che cambi
motore.

## Passo 2 — Accendi PostgreSQL (10 minuti)

```bash
cp moduli/06-dove-vive-il-dato/starter/docker-compose.yml memoria/
docker compose -f memoria/docker-compose.yml up -d
```

Controlla che sia vivo e che pgvector ci sia:

```bash
docker exec memoria-postgres psql -U cognee -d cognee_db \
  -c "CREATE EXTENSION IF NOT EXISTS vector; \
      SELECT extversion FROM pg_extension WHERE extname='vector';"
```

Deve stampare un numero di versione (0.8.x o superiore).

| Sintomo | Causa | Rimedio |
|---|---|---|
| `port is already allocated` | hai già un Postgres sulla 5432 | cambia in `127.0.0.1:5433:5432` e metti `DB_PORT=5433` in `.env` |
| `permission denied` su docker | non sei nel gruppo docker | `sudo usermod -aG docker $USER`, poi esci e rientra |
| `Cannot connect to the Docker daemon` | Docker non è avviato | avvialo |

## Passo 3 — Prova pgvector a mano (15 minuti)

Prima di farlo fare a cognee, fallo tu: tre minuti che chiariscono cosa
sia un database vettoriale.

```bash
docker exec -i memoria-postgres psql -U cognee -d cognee_db <<'SQL'
CREATE TABLE prova (id serial primary key, testo text, punto vector(3));
INSERT INTO prova (testo, punto) VALUES
  ('rasaerba',  '[1.0, 0.1, 0.0]'),
  ('tagliaerba','[0.9, 0.2, 0.0]'),
  ('caldaia',   '[0.0, 0.1, 1.0]');

-- i piu' vicini a "rasaerba", per distanza coseno
SELECT testo, round((punto <=> '[1.0, 0.1, 0.0]')::numeric, 4) AS distanza
FROM prova ORDER BY punto <=> '[1.0, 0.1, 0.0]';
SQL
```

«tagliaerba» deve risultare vicinissimo e «caldaia» lontano. Sono i
vettori del modulo 3, in tre dimensioni invece di 384, dentro una query
SQL normale.

Ora la cosa che un database vettoriale separato non sa fare:

```bash
docker exec -i memoria-postgres psql -U cognee -d cognee_db <<'SQL'
SELECT testo FROM prova
WHERE testo LIKE '%erba%'
ORDER BY punto <=> '[0.0, 0.1, 1.0]'
LIMIT 1;
SQL
```

Filtro esatto e ordinamento per somiglianza, insieme. Poi pulisci:

```bash
docker exec memoria-postgres psql -U cognee -d cognee_db -c "DROP TABLE prova;"
```

## Passo 4 — Migra l'archivio (25 minuti, quasi tutti di attesa)

In `.env`:

```bash
DB_PROVIDER=postgres
DB_NAME=cognee_db
DB_HOST=localhost
DB_PORT=5432
DB_USERNAME=cognee
DB_PASSWORD=cognee
VECTOR_DB_PROVIDER=pgvector
GRAPH_DATASET_DATABASE_HANDLER=kuzu
```

Installa le librerie che servono per parlare con Postgres:

```bash
pip install "cognee[postgres-binary]==1.6.0"
```

**I dati non si spostano da soli.** Il database nuovo è vuoto: bisogna
rifare tutto, e rispendere la quota.

```bash
python memoria/quaderno.py azzera
python memoria/quaderno.py aggiungi
python memoria/quaderno.py digerisci
```

Mentre aspetti, rifletti su questo: se avessi avuto dieci anni di note
invece di dodici file, questa riga ti sarebbe costata giorni di quota.
**La scelta del database va fatta prima di riempirlo.** Scrivilo in
`note-lab6.md`.

## Passo 5 — Guarda dentro, adesso davvero (15 minuti)

Scrivi `relazionale_postgres()` (TODO 1) e `grafo()` (TODO 2) in
`memoria/ispeziona.py`.

```bash
python memoria/ispeziona.py relazionale
```

Le stesse tabelle di prima, più quelle dei vettori. Cerca le tabelle che
contengono `vector` nel nome.

```bash
python memoria/ispeziona.py grafo
```

Tre query Cypher. Guarda la seconda, «i nodi più collegati»: se in cima
trovi un nodo che è un'unità di misura («bar», «ore») o una parola
generica, l'estrazione ha creato un nodo spazzatura e ci ha attaccato
mezzo archivio. Annota quali sono: **è il primo lavoro del modulo 7.**

Verifica anche direttamente sul database che i vettori ci siano:

```bash
docker exec memoria-postgres psql -U cognee -d cognee_db \
  -c "\dt" | head -20
```

## Passo 6 — Il backup (4 minuti)

Ora che i metadati e i vettori stanno nello stesso posto:

```bash
docker exec memoria-postgres pg_dump -U cognee cognee_db > dati/backup.sql
ls -lh dati/backup.sql
```

Un file solo. Il grafo Kuzu però **non** è lì dentro: è una cartella a
parte, e va salvata a parte. Salvarlo è l'argomento del modulo 7.

## Passo 7 — Verifica

```bash
python moduli/06-dove-vive-il-dato/verifica.py
```

---

## Se vuoi tornare indietro

Rimetti in `.env`:

```bash
DB_PROVIDER=sqlite
VECTOR_DB_PROVIDER=lancedb
```

e rifai `azzera / aggiungi / digerisci`. I dati su Postgres restano dove
sono: `docker compose -f memoria/docker-compose.yml down` ferma il
servizio senza cancellarli.

## Artefatti di questo modulo

`memoria/docker-compose.yml`, `memoria/ispeziona.py`, l'archivio su
PostgreSQL + pgvector e il grafo in Kuzu.
