# Modulo 8 — Valutare il proprio sistema

**Durata: 2 ore** (36 minuti di lezione, 84 di laboratorio).
Totale progressivo: 18,5 / 20 ore.

Fin qui, ogni volta che hai cambiato qualcosa, hai giudicato il risultato
guardandolo. Hai fatto una domanda, hai letto la risposta, ti è sembrata
buona o cattiva.

Non regge. Non perché sia poco scientifico, ma per un motivo pratico: fra
due settimane cambierai il modello, o la dimensione dei pezzi, e non avrai
modo di sapere se hai migliorato o peggiorato. Te ne accorgerai per caso,
su una domanda a cui tieni, tre settimane dopo.

Serve un metro. Questo modulo costruisce il metro.

---

## 1. Un insieme di valutazione è un elenco di domande con la risposta

Niente di più. Un file con, per ogni domanda:

- la **domanda**, scritta come la scriveresti davvero;
- cosa **deve** comparire nella risposta;
- cosa **non deve** comparire;
- dove sta la risposta, e di che **tipo** di domanda si tratta.

Il file te l'ho preparato: `progetto-finale/domande.yaml`, dodici
domande. Aprilo adesso e leggilo, perché è il cuore di questo modulo.

```yaml
- id: D02
  domanda: "A che pressione devo tenere l'impianto della caldaia?"
  fonte: note
  tipo: aggiornato
  attese: ["1,4"]
  vietate: ["1,2 bar a freddo"]
```

Il campo `vietate` è quello che manca nelle valutazioni fatte male. Una
risposta può contenere la parola giusta **e** essere sbagliata, perché
contiene anche quella vecchia. «La pressione è 1,2 bar, poi portata a
1,4» prende il punto se guardi solo le attese, ed è una risposta che in
officina ti fa sbagliare il lavoro.

## 2. Perché le domande sono divise per tipo

I sei tipi di `domande.yaml` non sono una catalogazione ordinata: sono
**sei modi diversi in cui il sistema può rompersi**, e vanno misurati
separatamente perché si curano in modo diverso.

| Tipo | Cosa mette alla prova | Se sbaglia, guarda |
|---|---|---|
| `fattuale` | il recupero di base | i pezzi, la dimensione dei pezzi |
| `aggiornato` | i fatti superati | il modulo 7, la nota di rettifica |
| `incrocio` | manuale + nota insieme | quanti pezzi recuperi, il grafo |
| `multi-hop` | mettere in fila due passaggi | il grafo, i collegamenti |
| `ocr` | la lettura dei PDF scansionati | l'ingestione, non il modello |
| `assente` | dire «non lo so» | l'istruzione al modello |

Una media unica su dodici domande nasconde tutto questo. Se passi da
8/12 a 9/12 non sai niente. Se passi da «3/3 fattuali, 0/2 ocr» a «3/3
fattuali, 2/2 ocr» sai esattamente cosa hai aggiustato.

## 3. Il tipo `assente`, e perché conta più degli altri

Nel file c'è una domanda che **non ha risposta nel corpus**: riguarda un
apparecchio che non c'è.

```yaml
- id: D10
  domanda: "Qual e' la pressione di gonfiaggio dei pneumatici della bici?"
  fonte: nessuna
  tipo: assente
```

Questa domanda **non si può valutare a frammenti**, e vale la pena capire
perché prima di scrivere il codice. Se cerchi la parola «non», la prende
anche una risposta inventata come «la pressione **non** deve superare i
4 bar». Se cerchi «non lo so», la perdi quando il sistema risponde «nei
documenti non trovo questa informazione», che è una risposta giusta.

Per questo tipo lo script usa una regola sua, in due parti:

1. la risposta contiene uno dei modi di ammettere l'ignoranza
   («non lo so», «non trovo», «non è presente», «non risulta»…);
2. e **non contiene un numero seguito da un'unità di misura**.

La seconda parte è quella che conta: un sistema che tira fuori un numero
ha inventato, comunque abbia girato la frase.

Un sistema che a questa domanda risponde qualcosa di plausibile è
**peggio** di uno che sbaglia le altre undici, perché non ti dà modo di
accorgertene. Le risposte sbagliate palesi le controlli; le risposte
inventate e sicure di sé no.

Nel progetto finale questo è un criterio di bocciatura, non un punto in
meno.

## 4. Come si assegna il punto, senza un altro modello

Il modo elegante di valutare è usare un secondo modello come giudice. Il
modo che usiamo qui è il **confronto di frammenti**: la risposta contiene
la stringa attesa, e non contiene quelle vietate.

È grezzo. Ha due difetti veri, e devi conoscerli:

1. **falsi negativi**: il sistema risponde «un bar e quattro» e tu cerchi
   «1,4». Risposta giusta, punto perso.
2. **falsi positivi**: la risposta contiene «1,4» dentro una frase che
   dice il contrario.

È comunque il metodo giusto per iniziare, per tre motivi: costa zero
quota, dà sempre lo stesso risultato sullo stesso testo, e su risposte
con dentro un numero o un codice ricambio ci prende quasi sempre.

Le attese vanno scelte di conseguenza: **numeri e codici, non frasi.**
`"1,4"` e `"BPR6ES"` funzionano. `"devi portare la pressione a"` no.

## 5. La regola che rende utile tutto questo

**Si misura prima di cambiare, e si rimisura dopo.**

Il numero da solo non vuol dire niente: 9/12 è buono o cattivo? Non si
sa. 9/12 dopo che ieri era 7/12, e l'unica cosa cambiata è la dimensione
dei pezzi, vuol dire qualcosa.

Per questo lo script del laboratorio scrive ogni giro in un file con la
data e la configurazione usata. Un giro di valutazione che non lasci
scritto è un giro buttato.

## 6. Quanto costa misurare

Dodici domande sono dodici chiamate al modello (più il recupero, che è
gratis perché gli embedding stanno sul tuo computer). Sul piano gratuito
Groq, con 1.000 messaggi al giorno, puoi permetterti circa **ottanta giri
di valutazione al giorno**.

Non è un vincolo. È un permesso: misura ogni volta che tocchi qualcosa.

Un giro completo impiega uno-due minuti, quasi tutti passati ad aspettare
il limite di velocità. Lo script mette una pausa fra una domanda e
l'altra apposta: senza, le prime tre domande partono insieme, prendi 429,
e stai fermo di più.

**Adesso: [LAB.md](LAB.md).**
