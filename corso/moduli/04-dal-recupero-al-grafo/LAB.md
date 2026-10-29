# Laboratorio 4 — Costruisci un grafo a mano

**Durata: 102 minuti.**

Alla fine avrai un grafo di entità e relazioni costruito dai tuoi
documenti, e risponderai alla domanda che nel modulo 3 era impossibile.

**Costo in quota:** circa 30.000 token, cioè quattro o cinque minuti di
lavoro vero più le attese. Lancialo quando hai la quota fresca; se sei
già a metà giornata, `python memoria/stima_quota.py` ti dice se ce la fai.

---

## Passo 1 — Vedi il fallimento (12 minuti)

```bash
python moduli/04-dal-recupero-al-grafo/starter/prova_multihop.py
```

Guarda **quali pezzi** recupera, non la risposta. Non ce n'è uno che
parli della caldaia. Scrivi in `note-lab4.md` perché, secondo te, la
ricerca ha pescato proprio quei cinque.

## Passo 2 — La pazienza (5 minuti)

```bash
cp moduli/04-dal-recupero-al-grafo/starter/pazienza.py memoria/
```

Leggilo: sono quaranta righe e non c'è niente da scrivere. Due funzioni:
una legge dal messaggio di errore quanti secondi aspettare, l'altra
riprova.

Provala a vuoto:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from pazienza import secondi_da_aspettare
class Finto(Exception): pass
print(secondi_da_aspettare(Finto('Rate limit reached. Please try again in 1.875s'), 0))
print(secondi_da_aspettare(Finto('errore generico'), 3))
"
```

Deve stampare `2.375` e `8`. Il primo è il tempo dichiarato dal
fornitore più mezzo secondo di margine; il secondo è l'attesa
esponenziale quando non c'è niente di dichiarato.

## Passo 3 — L'estrazione (35 minuti)

```bash
cp moduli/04-dal-recupero-al-grafo/starter/grafo.py memoria/
```

Scrivi `costruisci()` (TODO 1). Prima di lanciarlo su tutto il corpus,
prova l'estrazione su **un solo documento**, che costa una chiamata:

```bash
python -c "
import sys, json; sys.path.insert(0,'memoria')
from grafo import estrai
from pathlib import Path
t = Path('progetto-finale/corpus/note/2026-03-12-caldaia-e4.md').read_text()
print(json.dumps(estrai(t), indent=2, ensure_ascii=False))
"
```

Devi vedere entità con `nome` e `tipo`, e relazioni `da / relazione / a`.
Controlla tre cose:

1. c'è un'entità di tipo `intervento` con una data nel nome?
2. c'è una relazione `riguarda` che la collega alla caldaia?
3. c'è una relazione verso «1,5 ore» o simili?

Se manca la terza, il modello non ha visto «Tempo impiegato: 1 ora e
mezza» come una durata. Modifica `ISTRUZIONI` per dirglielo più
chiaramente, e riprova: **è questo il mestiere**, non scrivere il codice.

Poi costruisci tutto:

```bash
python memoria/grafo.py costruisci
```

Stampa una riga per documento e, quando la quota finisce, le righe
`quota esaurita, aspetto 1.9s`. Sono il segno che `pazienza.py`
funziona. Alla fine scrive `dati/grafo.json`.

## Passo 4 — La visita (25 minuti)

Scrivi `vicini()` (TODO 2). È una visita in ampiezza: guarda il commento
nel file.

```bash
python memoria/grafo.py mostra "caldaia"
```

Devi vedere le relazioni che partono dalla caldaia o ci arrivano: gli
interventi, i componenti, i codici di errore.

Con due salti:

```bash
python -c "
import sys; sys.path.insert(0,'memoria')
from grafo import carica, vicini, trova_nodo
g = carica()
n = trova_nodo(g, 'caldaia termovex')
for s in (1, 2, 3):
    print(s, 'salti ->', len(vicini(g, n, salti=s)), 'relazioni')
"
```

Il numero deve **crescere** da 1 a 2 salti e crescere poco o niente da 2
a 3: hai già raggiunto quasi tutto il sottografo che ti riguarda. È il
motivo per cui due salti è la scelta giusta.

## Passo 5 — La risposta impossibile (15 minuti)

```bash
python memoria/grafo.py chiedi "Quante ore ho passato in tutto sulla caldaia?"
```

Adesso deve rispondere **3,5 ore**, e mostrare gli addendi: 1,5 del 12
marzo, 2 del 30 agosto.

Se sbaglia la somma ma ha i fatti giusti sotto gli occhi, il problema è
il modello, non il grafo: riprova con `max_tokens` più alto, o con un
modello più grande. Se non ha i fatti, il problema è l'estrazione: torna
al passo 3.

Prova anche queste:

```bash
python memoria/grafo.py chiedi "Quali ricambi ho usato sulla bici?"
python memoria/grafo.py chiedi "Su quali apparecchi ho lavorato a settembre?"
```

E una che deve fallire:

```bash
python memoria/grafo.py chiedi "Che pressione hanno le gomme della bici?"
```

Nel corpus non c'è. Se il sistema si inventa un numero, segnatelo: è il
problema del modulo 8.

## Passo 6 — Rompi il grafo apposta (10 minuti)

Cerca nel grafo tutti i nodi che nominano lo stesso apparecchio:

```bash
python -c "
import json
g = json.load(open('dati/grafo.json'))
for parola in ['caldaia', 'lavatrice', 'rasaerba', 'bici']:
    trovati = [e['nome'] for e in g['entita'] if parola in e['nome'].lower()]
    print(parola, '->', trovati)
"
```

Sul corpus del corso, la caldaia di solito si fonde bene: un nodo solo,
con tre documenti come fonte. La lavatrice quasi sempre no:

```text
lavatrice -> ['Lavatrice LAVANOR WM-700', 'Lavatrice Lavanor WM-700']
```

**Due nodi, per una differenza di maiuscole.** Sono due pezzi di memoria
che non si parlano: una domanda che parte dall'uno non raggiunge i fatti
dell'altro. Il tuo risultato può essere diverso dal nostro — il modello
non è deterministico su questo — ma qualche duplicato lo trovi di sicuro.

Scrivi in `note-lab4.md` quanti ne hai trovati e quali. Ti servono nel
modulo 7, dove si affronta il problema per davvero: normalizzare i nomi
a mano risolve le maiuscole e non risolve «Termovex TX-24» contro
«la caldaia del bagno».

## Passo 7 — Verifica

```bash
python moduli/04-dal-recupero-al-grafo/verifica.py
```

---

## Se qualcosa non va

| Sintomo | Causa | Rimedio |
|---|---|---|
| `json_validate_failed` | modello troppo piccolo per lo schema | usa `openai/gpt-oss-120b` |
| l'estrazione gira ma le relazioni sono zero | il modello non ha capito cosa vuoi | irrobustisci `ISTRUZIONI` con un esempio |
| `429` che non passa mai | quota giornaliera finita, non quella al minuto | aspetta domani o aggiungi un fornitore |
| `vicini()` restituisce tutto il grafo | confronti stringhe senza `lower()`, o non fermi la visita | controlla il ciclo |
| «non lo so» anche col grafo | `trova_nodo()` non ha agganciato niente | prova a nominare l'apparecchio per esteso |

## Artefatti di questo modulo

`memoria/pazienza.py`, `memoria/grafo.py`, `dati/grafo.json`.

Da qui in poi non costruirai più grafi a mano: nel modulo 5 lo fa cognee.
Ma quando cognee darà un risultato strano, saprai cosa guardare.
