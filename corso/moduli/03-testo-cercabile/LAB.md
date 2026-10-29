# Laboratorio 3 — Spezzare, cercare, misurare

**Durata: 120 minuti.**

Alla fine avrai quattro pezzi nuovi del tuo sistema: `pezzi.py`,
`lessicale.py`, `semantica.py`, `ibrida.py` — e, soprattutto, un modo per
sapere se una modifica migliora le cose o le peggiora.

Il gateway del modulo 2 non serve in questo laboratorio: **non si chiama
il modello nemmeno una volta**. Cercare non costa quota. È un fatto da
tenere a mente: il pezzo costoso del sistema è la risposta, non la
ricerca.

---

## Passo 1 — Spezzare (25 minuti)

```bash
cp moduli/03-testo-cercabile/starter/pezzi.py memoria/
```

Scrivi `spezza_alla_cieca()` (TODO 1) e `spezza_per_titoli()` (TODO 2).

Controlli, uno per volta:

```bash
python memoria/pezzi.py progetto-finale/corpus/manuali/termovex-tx24.md --cieco
```
deve dare **6 pezzi**, e nel pezzo 2 la riga della tabella E4 è tagliata.

```bash
python memoria/pezzi.py progetto-finale/corpus/manuali/termovex-tx24.md
```
deve dare **8 pezzi**, uno per sezione, con la tabella dei codici di
errore tutta dentro un pezzo solo.

```bash
python memoria/pezzi.py
```
deve dire `48 pezzi da 12 documenti`.

| Se ottieni | Guarda |
|---|---|
| 7 pezzi invece di 6 | non stai scartando i pezzi di soli spazi |
| 9 pezzi invece di 8 | stai aprendo un pezzo nuovo anche sul primo titolo, quando il pezzo corrente è vuoto |
| un numero diverso da 48 | uno dei due, oppure stai includendo `LEGGIMI.md` |

## Passo 2 — BM25 (30 minuti)

```bash
cp moduli/03-testo-cercabile/starter/lessicale.py memoria/
```

Due funzioni: `idf()` (TODO 1) e `punteggio()` (TODO 2). Le formule sono
nella lezione, §3, e ripetute nei commenti.

Prova:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pezzi import carica_pezzi
from lessicale import Bm25
motore = Bm25(carica_pezzi())
for p in motore.cerca('Con che coppia si stringe il bullone della lama?'):
    print(round(p['punteggio'],2), p['id'])
"
```

Il primo risultato deve venire da `manuali/greencut-rm46.md`. **Questa è
la domanda che il sistema del modulo 1 sbagliava**: lì al primo posto
finiva la nota sui freni della bici, perché «vite» e «stringe» contavano
quanto tutto il resto. Adesso «lama» e «45» sono rare e pesano.

Controllo che la formula sia giusta e non solo plausibile:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pezzi import carica_pezzi
from lessicale import Bm25
motore = Bm25(carica_pezzi())
print('idf di una parola rara (bpr6es):', round(motore.idf('bpr6es'), 3))
print('idf di una parola comune (il):  ', round(motore.idf('il'), 3))
"
```

La prima deve essere molto più grande della seconda. Se sono uguali, stai
contando le occorrenze totali invece del numero di documenti in cui la
parola compare.

## Passo 3 — Embedding e coseno (30 minuti)

```bash
cp moduli/03-testo-cercabile/starter/semantica.py memoria/
```

TODO 1 è il coseno, TODO 2 è la ricerca.

**La prima esecuzione scarica 220 MB** di modello e ci mette un paio di
minuti. Succede una volta sola; il modello resta nella cache di
`fastembed`.

Prima di scrivere `cerca()`, fatti un'idea di cosa hai in mano:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from semantica import vettori, similitudine_coseno
v = vettori(['il rasaerba non parte',
             'il tagliaerba non si avvia',
             'la caldaia va in errore E4'])
print('rasaerba vs tagliaerba:', round(float(similitudine_coseno(v[0], v[1:2])[0]), 3))
print('rasaerba vs caldaia:   ', round(float(similitudine_coseno(v[0], v[2:3])[0]), 3))
"
```

Due frasi senza **nessuna parola in comune** (a parte «non») devono
risultare molto più simili fra loro che alla terza. Se i due numeri sono
quasi uguali, il coseno è sbagliato: probabilmente hai dimenticato di
dividere per le lunghezze.

Poi la ricerca:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pezzi import carica_pezzi
from semantica import Semantica
for p in Semantica(carica_pezzi()).cerca('Il tagliaerba non si accende'):
    print(round(p['punteggio'],3), p['id'])
"
```

Il manuale del rasaerba deve comparire fra i primi, **anche se la parola
«tagliaerba» non è scritta da nessuna parte nel corpus**. Questo è il
fallimento del modulo 1 risolto.

## Passo 4 — Fondere (15 minuti)

```bash
cp moduli/03-testo-cercabile/starter/ibrida.py memoria/
```

Una funzione sola, `fondi()`. Attento a due cose: l'identità di un pezzo
è `pezzo["id"]` (non il testo, non il nome del file), e il punteggio
finale sostituisce quelli dei due sistemi di partenza.

## Passo 5 — Misurare (15 minuti)

Questo è il passo che vale il modulo.

```bash
python moduli/03-testo-cercabile/starter/confronta.py
```

Devi ottenere esattamente questi numeri (il corpus è fisso, il modello è
deterministico):

```text
metodo        primi 1  primi 3  primi 5
BM25            4/10     8/10    10/10
semantica       5/10     7/10     8/10
ibrida          4/10     8/10    10/10
-- unione       7/10    10/10    10/10
```

Se non tornano, hai sbagliato qualcosa nei passi precedenti: il confronto
è anche un collaudo.

Adesso rispondi a queste domande guardando la tabella, non l'istinto:

1. Quale metodo sbaglia «Cosa vuol dire il codice F03?» e perché?
2. L'ibrida, nei primi 3, fa meglio di BM25 da solo? (No.) Allora perché
   il corso te la fa scrivere?
3. La riga «unione» dice 10/10 nei primi 3. Cosa significa, esattamente,
   rispetto al lavoro che resta da fare?

Le risposte sono nella lezione, §5 e §6. Scrivile con parole tue in
`note-lab3.md`: nel modulo 8 ti serviranno.

## Passo 6 — Esperimento libero (5 minuti)

Cambia `K` in `memoria/ibrida.py` da 60 a 1, rilancia `confronta.py`.
Cambia `MISURA_PEZZO` in `memoria/pezzi.py` da 800 a 400, rilancia.
Metti `per_titoli=False` in `confronta.py`, rilancia.

Segnati cosa succede. È il primo assaggio del modulo 8: **non si
regolano le manopole a sentimento, si misura**.

## Passo 7 — Verifica

```bash
python moduli/03-testo-cercabile/verifica.py
```

---

## Se qualcosa non va

| Sintomo | Causa | Rimedio |
|---|---|---|
| `ModuleNotFoundError: fastembed` | ambiente sbagliato | `source .venv/bin/activate` |
| il download del modello si blocca | rete lenta o proxy | rilancia: riprende da dove era |
| `ValueError: la sovrapposizione deve essere minore del pezzo` | hai invertito i parametri | `misura > sovrapposizione` |
| tutti i coseni valgono 1 | stai confrontando un vettore con se stesso | controlla gli indici |
| BM25 dà punteggi negativi | manca il `+1` dentro il logaritmo dell'IDF | rileggi la formula |

## Artefatti di questo modulo

`memoria/pezzi.py`, `memoria/lessicale.py`, `memoria/semantica.py`,
`memoria/ibrida.py`. Nel modulo 5 cognee farà tutto questo da solo: ma
adesso sai che cosa fa, e sapresti rifarlo.
