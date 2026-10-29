# Laboratorio 1 — Il RAG in trenta righe

**Durata: 60 minuti.**

Alla fine avrai, nella cartella `memoria/` del repository, due file che
userai per tutto il corso: `llm.py` (l'unico punto da cui si parla col
modello) e `memoria_minima.py` (cerca, poi chiede).

---

## Passo 0 — La cartella del tuo sistema (2 minuti)

```bash
mkdir -p memoria
cp moduli/01-perche-serve-una-memoria/starter/llm.py memoria/llm.py
cp moduli/01-perche-serve-una-memoria/starter/memoria_minima.py memoria/
```

**`memoria/` è il tuo sistema.** Cresce a ogni modulo. Gli `starter/` sono
punti di partenza da copiare, le `soluzione/` sono la rete di sicurezza.

Controlla che il collegamento col modello funzioni:

```bash
python memoria/llm.py
```

Deve stampare `pronto`. Se stampa un errore, la diagnosi è in
[CHIAVI.md](../../CHIAVI.md#6-controlla-che-le-chiavi-funzionino).

## Passo 1 — Misura il problema (8 minuti)

```bash
python moduli/01-perche-serve-una-memoria/starter/conta_token.py \
  progetto-finale/corpus/manuali/*.md progetto-finale/corpus/note/*.md
```

Annota il totale. **Scrivilo da qualche parte**: nel modulo 3 lo
confronterai con quanti token consuma il sistema dopo aver imparato a
cercare. Sul corpus del corso sono circa 4.400 token.

## Passo 2 — `cerca()` (25 minuti)

Apri `memoria/memoria_minima.py` e scrivi la funzione `cerca()`, dove c'è
il TODO 1.

Deve:

1. ridurre la domanda a un insieme di parole con `normalizza()`;
2. per ogni documento, contare quante di quelle parole ci compaiono;
3. buttare via i documenti con punteggio zero;
4. restituire i primi `quanti`, ordinati, ciascuno con la chiave
   `"punteggio"`.

Provala senza spendere quota, cioè senza chiamare il modello:

```bash
python -c "
import sys; sys.path.insert(0, 'memoria')
from memoria_minima import carica_documenti, cerca
for d in cerca('Che candela monta il rasaerba?', carica_documenti()):
    print(d['punteggio'], d['nome'])
"
```

Risultato atteso: `manuali/greencut-rm46.md` e
`note/2026-07-21-rasaerba-non-parte.md`, entrambi con 2 punti.

Se ottieni una lista vuota, hai normalizzato la domanda ma non i
documenti (o viceversa).

## Passo 3 — `costruisci_contesto()` (10 minuti)

TODO 2. Serve una stringa sola, con un blocco per documento:

```text
[documento: manuali/greencut-rm46.md]
# GREENCUT RM-46 ...

[documento: note/2026-07-21-rasaerba-non-parte.md]
# Intervento del 21 luglio ...
```

Il nome del file davanti al testo non è un vezzo: è quello che permette
al modello di citare la fonte, e a te di controllare.

## Passo 4 — Provalo (5 minuti)

```bash
python memoria/memoria_minima.py "Cosa significa l'errore E4 sulla caldaia Termovex?"
```

Devi vedere prima l'elenco dei documenti usati, poi una risposta che cita
0,8 bar, il ripristino a 1,2 bar e — se il recupero ha funzionato bene —
anche la nota del 12 marzo sul vaso di espansione.

## Passo 5 — Rompilo (10 minuti)

Adesso la parte utile. Lancia queste tre domande e **guarda l'elenco dei
documenti usati**, non la risposta:

```bash
python memoria/memoria_minima.py "Quanto devo stringere la vite che tiene la lama?"
python memoria/memoria_minima.py "Perche' il trapano avvitatore si scarica subito?"
python memoria/memoria_minima.py "Il tagliaerba non si accende, cosa devo controllare?"
```

Cosa dovresti osservare, sul corpus del corso:

| Domanda | Cosa succede |
|---|---|
| la vite della lama | al primo posto finisce la **nota sui freni della bici** (2 punti, per «vite» e «stringere»). Il manuale del rasaerba, che contiene la risposta — 45 Nm — arriva secondo con 1 punto |
| il trapano che si scarica | davanti alla nota giusta sulla batteria si infila una **nota sulla lavatrice**, perché contiene la parola «scarica» (di scarico dell'acqua) |
| il tagliaerba | tre documenti **a pari punteggio**: un avvitatore, un rasaerba e una lavatrice. Chi vince lo decide l'ordine alfabetico, non la pertinenza. E «tagliaerba» non compare in nessun documento: il corpus dice «rasaerba» |

Sono tre fallimenti diversi con una radice sola: **stiamo confrontando
stringhe, non significati.**

- «scarica» (batteria) e «scarica» (acqua) sono la stessa stringa e due
  cose diverse;
- «tagliaerba» e «rasaerba» sono due stringhe e la stessa cosa;
- una parola rara come «45» conta quanto una parola banale come «vite».

Scrivi in un file `note-lab1.md` tuo, con parole tue, quale dei tre ti
sembra il problema più grave. Lo riprenderai nel modulo 3, dove i primi
due si risolvono con la ricerca semantica e il terzo con BM25.

## Passo 6 — Verifica

```bash
python moduli/01-perche-serve-una-memoria/verifica.py
```

Fa due chiamate vere al modello (poca quota). Deve stampare `OK` su tutte
le righe.

---

## Se qualcosa non va

| Sintomo | Causa | Rimedio |
|---|---|---|
| `ModuleNotFoundError: No module named 'llm'` | lanci lo script da un'altra cartella | mettiti nella radice del repository |
| `ModuleNotFoundError: No module named 'dotenv'` | ambiente virtuale non attivo | `source .venv/bin/activate` |
| `NotImplementedError: TODO 1` | non hai ancora scritto `cerca()` | passo 2 |
| la lista dei documenti è sempre vuota | `normalizza()` applicata solo da un lato | confronta insiemi di parole, non stringhe |
| `429` | hai finito i token del minuto | aspetta 60 secondi. Modulo 2 |

## Artefatto di questo modulo

`memoria/llm.py` e `memoria/memoria_minima.py` funzionanti. Non
cancellarli: il modulo 3 parte da qui.
