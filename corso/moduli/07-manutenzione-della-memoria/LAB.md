# Laboratorio 7 — Tenere viva la memoria

**Durata: 78 minuti.**

Ti serve l'archivio del modulo 5 o 6 già digerito, e il gateway acceso.

Già digerito vuol dire **tutto**. Prima di cominciare:

```bash
python moduli/05-la-pipeline-di-cognee/verifica.py
```

deve passare. Il motivo è la quota. Se il `digerisci` del modulo 5 si era
fermato a metà, il primo `aggiungi` di questo laboratorio non digerisce
solo la nota nuova: `cognify` riprende tutti i documenti rimasti indietro.
È il comportamento giusto (riparte da dove si era fermato, non rifà
quello che c'è già), ma costa quanto un corpus intero, circa 50.000
token, non i 5.000 di una nota. Se succede a fine giornata trovi la quota
esaurita e il laboratorio si ferma lì.

---

## Esercizio 1 — Riprodurre il fallimento (8 minuti)

```bash
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia Termovex?"
```

Scrivi su un foglio la risposta. Poi guarda cosa aveva in mano il sistema:

```bash
python memoria/quaderno.py chiedi "pressione impianto Termovex" --tipo pezzi
```

Due domande a cui rispondere prima di andare avanti:

1. fra i pezzi recuperati c'è la nota del 30 agosto?
2. se **non** c'è, il problema è il recupero. Se **c'è** e la risposta
   resta 1,2 bar, il problema è il modello che non ha capito quale dei
   due valori vale.

Sono due guasti diversi e si curano in due modi diversi. Sapere quale dei
due hai è metà del lavoro.

## Esercizio 2 — Aggiungere senza rifare tutto (15 minuti)

Nella cartella `progetto-finale/corpus/note/` c'è la nota del 30 agosto.
Simuliamo l'arrivo di una nota nuova.

Crea `dati/nota-nuova.md`:

```markdown
# Intervento del 15 settembre 2026 — Caldaia Termovex TX-24, via Mazzini 8

Controllo stagionale. Pressione a freddo trovata a 1,35 bar, dentro
tolleranza, non toccata. Pulito lo scambiatore. Sostituito il ricambio
7832-VE8 (vaso di espansione) perche' la precarica era scesa a 0,6 bar.
Tempo: 2,5 ore.
```

Apri `starter/manutenzione.py`. Il **TODO 1** è la funzione `aggiungi()`:

```python
await cognee.add(percorso, dataset_name=DATASET)
await cognee.cognify(datasets=[DATASET])
```

Cronometra:

```bash
time python memoria/manutenzione.py aggiungi dati/nota-nuova.md
```

**Confronta** con i minuti che ha impiegato il `digerisci` completo del
modulo 5. Dovrebbe essere una frazione: è la dimostrazione che `cognify`
è incrementale. Se invece ci mette lo stesso tempo, qualcosa nella
configurazione fa ripartire tutto da zero — segnalo e vai avanti.

Poi verifica che sia entrata:

```bash
python memoria/quaderno.py chiedi "Quando ho sostituito il vaso di espansione della Termovex?"
```

## Esercizio 3 — Elencare quello che c'è dentro (10 minuti)

**TODO 2**, la funzione `elenca()`. Serve a sapere cosa contiene
l'archivio e a recuperare gli identificativi che servono per aggiornare e
cancellare.

```python
datasets = await cognee.datasets.list_datasets()
for d in datasets:
    documenti = await cognee.datasets.list_data(dataset_id=d.id)
    for doc in documenti:
        print(doc.id, doc.name)
```

```bash
python memoria/manutenzione.py elenca
```

Devi vedere i tuoi documenti con il loro identificativo. Tienilo da
parte: serve nei due esercizi seguenti.

## Esercizio 4 — Risolvere la contraddizione (20 minuti)

Adesso curiamo il guasto dell'esercizio 1, con il metodo che funziona:
la **nota di rettifica**.

Crea `dati/rettifica-pressione.md`:

```markdown
# Rettifica del 30 agosto 2026 — Caldaia Termovex TX-24

Questa nota SUPERA il valore del libretto e le mie note precedenti.

Pressione di esercizio a freddo: 1,4 bar.
  Valore precedente, non piu' valido: 1,2 bar (libretto e nota di marzo).
Precarica del vaso di espansione: 1,2 bar.
  Valore precedente, non piu' valido: 1,0 bar.

Motivo: impianto su tre piani, con 1,2 bar i radiatori dell'ultimo piano
non scaldavano.
```

Aggiungila e ridigerisci:

```bash
python memoria/manutenzione.py aggiungi dati/rettifica-pressione.md
python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia Termovex?"
```

Adesso deve dire **1,4 bar**. Se lo dice menzionando anche il valore
vecchio, meglio ancora: è esattamente quello che vuoi da un quaderno.

**Domanda a cui rispondere nel `RISPOSTE.md` del modulo:** perché questa
nota viene recuperata e quella del 30 agosto no, visto che dicono la
stessa cosa? Guarda le parole che contengono.

## Esercizio 5 — Dimenticare (10 minuti)

**TODO 3**, la funzione `dimentica()`:

```python
await cognee.datasets.delete_data(dataset_id=..., data_id=..., mode="soft")
```

Cancella `dati/nota-nuova.md` usando l'identificativo dell'esercizio 3.
Poi richiedi:

```bash
python memoria/quaderno.py chiedi "Quando ho sostituito il vaso di espansione della Termovex?"
```

Non deve più saperlo. Poi controlla che il resto sia sopravvissuto:

```bash
python memoria/quaderno.py chiedi "Cosa vuol dire l'errore E4?"
```

Questo deve rispondere ancora. Se è sparito anche lui, hai usato
`mode="hard"` e hai portato via i nodi condivisi.

Prova anche a buttare via solo il capito, tenendo i documenti:

```python
await cognee.forget(dataset=DATASET, memory_only=True)
```

Non farlo adesso sull'archivio buono. Fallo quando vorrai cambiare
modello di estrazione senza ricaricare i file.

## Esercizio 6 — La relazione sulla salute del grafo (10 minuti)

**TODO 4**, la funzione `relazione()`:

```python
await cognee.report(datasets=DATASET, output_path="dati/relazione.md")
```

Aprila e cerca la sezione dei **nodi-mozzo**. Scrivi nel `RISPOSTE.md` i
primi tre e rispondi: sono entità vere (un apparecchio, un ricambio) o
sono unità di misura e parole generiche?

Lancia anche:

```python
await cognee.validate(dataset=DATASET)
```

e riporta se grafo e vettori sono d'accordo.

## Esercizio 7 — Il backup, e la prova che funziona (5 minuti)

```bash
python memoria/manutenzione.py salva dati/backup
```

**TODO 5**: la funzione `salva()` deve fare tre cose, non una:

1. `cognee.export(dataset=DATASET, format="cogx", destination=...)` — e una
   copia in `format="json"` per poterla leggere
2. copiare la cartella dei documenti originali
3. se sei sul modulo 6 con PostgreSQL: `pg_dump`

```bash
docker compose exec -T postgres pg_dump -U cognee cognee > dati/backup/registro.sql
```

Controlla che i tre pezzi esistano e non siano vuoti:

```bash
ls -la dati/backup/
```

Un backup di 0 byte è il modo più comune di scoprire, sei mesi dopo, che
non avevi un backup.

---

## Verifica

```bash
python moduli/07-manutenzione-della-memoria/verifica.py
```

Controlla che `manutenzione.py` abbia le cinque funzioni, che la nota di
rettifica sia nel corpus e che l'archivio risponda 1,4 bar.

**Consegna:** `manutenzione.py` completo e `RISPOSTE.md` con le risposte
agli esercizi 4 e 6.

Totale progressivo: **16,5 / 20 ore.** Prossimo: [modulo 8](../08-valutare-il-sistema/LEZIONE.md).
