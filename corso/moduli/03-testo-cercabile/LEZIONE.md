# Modulo 3 — Come un testo diventa cercabile

**Durata: 3 ore** (60 minuti di lezione, 120 di laboratorio).
Totale progressivo: 7,0 / 20 ore.

Nel modulo 1 la ricerca contava le parole in comune e sbagliava in tre
modi diversi. Qui costruisci qualcosa che sbaglia molto meno, e — più
importante — impari a **misurare** di quanto.

---

## 1. Primi cinque minuti: guarda come si rompe un manuale

```bash
python moduli/03-testo-cercabile/soluzione/pezzi.py \
  progetto-finale/corpus/manuali/termovex-tx24.md --cieco
```

(Sì, stai lanciando la soluzione. Guardarla funzionare adesso è il punto;
scriverla è il laboratorio.)

Il manuale viene tagliato ogni 800 caratteri. Guarda il **pezzo 2**:

```text
--- pezzo 2 (800 caratteri) ---
one impianto insufficiente** | **Pressione scesa sotto 0,8 bar** |
**Riportare la pressione a 1,2 bar con il rubinetto di riempimento** |
| E5 | Sonda mandata guasta | ...
```

La riga dell'errore E4 è stata **tagliata a metà**: il codice «E4» è
rimasto nel pezzo precedente, la spiegazione è finita in questo. Nessuno
dei due pezzi, da solo, risponde alla domanda «cosa vuol dire E4».

Questo è il secondo fallimento del corso, e non è un caso limite: le
tabelle, gli elenchi numerati e le procedure passo-passo sono
esattamente il contenuto che vale la pena archiviare, ed è quello che il
taglio cieco rovina.

Ora guarda la differenza:

```bash
python moduli/03-testo-cercabile/soluzione/pezzi.py \
  progetto-finale/corpus/manuali/termovex-tx24.md
```

Otto pezzi invece di sei, ognuno una sezione intera. La tabella dei
codici di errore sta tutta dentro un pezzo solo.

## 2. Spezzare: perché, e come

### Perché

Non si indicizzano documenti interi ma **pezzi** (in inglese *chunk*),
per tre motivi:

1. **precisione del recupero**: se il manuale è un blocco unico, cercare
   «E4» te lo restituisce tutto, comprese le 40 righe sul rimessaggio
   invernale;
2. **quota**: al modello mandi 800 caratteri invece di 4.000;
3. **il modello legge meglio**: meno rumore intorno all'informazione
   utile (il *lost in the middle* del modulo 1).

### Come

| Modo | Come funziona | Quando va bene |
|---|---|---|
| alla cieca | taglia ogni N caratteri | testo senza struttura, trascrizioni |
| con sovrapposizione | come sopra, ma ripete gli ultimi N caratteri all'inizio del pezzo dopo | attenua i tagli a metà frase |
| **per struttura** | taglia sui titoli, sui paragrafi, sulle righe vuote | **documenti scritti da esseri umani: manuali, note, articoli** |

La **sovrapposizione** (*overlap*) è il cerotto del taglio cieco: se
ripeti 120 caratteri, una frase spezzata compare intera almeno in uno dei
due pezzi. Costa spazio (ogni pezzo contiene un po' del precedente) e non
risolve il caso della tabella.

Il taglio **per struttura** costa cinque righe di codice in più e risolve
il problema alla radice: l'autore del documento ha già deciso lui dove
finisce un argomento, mettendoci un titolo. Buttare via quell'informazione
per poi cercare di indovinarla è uno spreco.

**Regola pratica del corso:** pezzi di 600-1.200 caratteri, tagliati
sulla struttura quando c'è, con sovrapposizione del 15 % quando non c'è.
Pezzi più piccoli recuperano meglio ma perdono il contesto; più grandi
fanno il contrario.

## 3. Cercare per parole, fatto bene: BM25

Il conteggio del modulo 1 trattava tutte le parole allo stesso modo.
«45» valeva quanto «vite». **BM25** — *Best Match 25*, il venticinquesimo
esperimento di una famiglia di formule degli anni Novanta, e ancora oggi
il riferimento — sistema tre cose.

**TF** (*term frequency*, frequenza del termine). Se «pressione» compare
cinque volte in un pezzo, quel pezzo parla di pressione più di uno dove
compare una volta. Ma non cinque volte tanto: il contributo si appiattisce
dopo le prime occorrenze. Il bottone che regola la velocità con cui si
appiattisce si chiama `k1` e vale 1,5.

**IDF** (*inverse document frequency*, frequenza inversa nei documenti).
Una parola che compare in tutti i documenti non distingue niente:
«manutenzione» sta ovunque nel nostro corpus, «BPR6ES» in un punto solo.
La seconda deve pesare molto di più. La formula:

```text
idf(parola) = log( (N - n + 0,5) / (n + 0,5) + 1 )
```

dove `N` è il numero di pezzi e `n` in quanti pezzi compare la parola. È
questo che risolve il fallimento del modulo 1 sulla «vite» del rasaerba:
«vite» è comune, «lama» meno, «45» è raro.

**Lunghezza.** Un pezzo lungo contiene più parole per caso. BM25 lo
penalizza in proporzione a quanto supera la lunghezza media. Il bottone
si chiama `b` e vale 0,75.

Messe insieme, per ogni parola della domanda presente nel pezzo:

```text
idf(parola) * ( f * (k1+1) ) / ( f + k1 * (1 - b + b * lunghezza/media) )
```

Sembra peggio di quello che è: nel laboratorio sono otto righe di Python.

**Cosa BM25 continua a non sapere:** che «tagliaerba» e «rasaerba» sono
la stessa cosa. Confronta stringhe. Nessuna formula sulle frequenze può
saperlo.

## 4. Cercare per significato: gli embedding

Un **embedding** («immersione», nel senso di immergere un testo in uno
spazio numerico) è un elenco di numeri che rappresenta il significato di
un pezzo di testo. Il nostro modello ne produce **384** per pezzo.

L'idea è semplice e sorprendente: un modello addestrato su abbastanza
testo impara a mettere vicini i testi che vogliono dire cose simili,
anche senza parole in comune. «Il tagliaerba non parte» e «il motore del
rasaerba non si avvia» finiscono vicini perché i loro contesti d'uso, nel
testo che il modello ha visto, si somigliano.

**Vicini quanto?** Si misura con il **coseno** fra i due elenchi di
numeri, visti come frecce che partono dall'origine:

```text
coseno = (a · b) / (|a| · |b|)
```

Vale 1 se puntano nella stessa direzione, 0 se sono perpendicolari.
Conta la **direzione**, non la lunghezza: un testo lungo e uno corto che
dicono la stessa cosa hanno coseno alto.

### Il modello gira sul tuo computer

Il corso usa **fastembed** con
`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`: 220 MB,
multilingue (capisce l'italiano), nessuna GPU, nessuna chiave.

Questa è una scelta, e vale la pena spiegarla. Gli embedding si possono
anche chiedere a Google o a OpenAI, ed è gratis su Gemini. Ma:

| | Embedding locali | Embedding via API |
|---|---|---|
| Quota consumata | **zero** | una chiamata per ogni pezzo, ogni volta |
| Dati inviati fuori | **nessuno** | tutto il corpus, pezzo per pezzo |
| Funziona senza rete | sì | no |
| Qualità sull'italiano | buona | migliore |
| Velocità su 48 pezzi | ~2 secondi | dipende dalla rete e dalla quota |

Nel modulo 5 costruirai il grafo, e lì gli embedding si calcolano su ogni
pezzo. Farlo via API significherebbe bruciare la quota giornaliera per
poi non avere più niente per le domande. Per questo stanno in locale, e
per questo restano in locale anche sulla «strada locale» con Ollama:
sono già locali di loro.

Se preferisci gli embedding di Google, in `.env`:

```bash
EMBEDDING_PROVIDER=gemini
EMBEDDING_MODEL=gemini-embedding-2
EMBEDDING_DIMENSIONS=768
```

### Il pezzo non può essere più lungo di 512 token

Questo modello ha una finestra di **512 token**, circa 380 parole. Un
pezzo più lungo non dà errore: viene **troncato**, e la parte in eccesso
semplicemente non finisce nel vettore. Silenziosamente.

È il motivo per cui il `.env` del corso contiene questa riga, che
altrimenti sembrerebbe una noia burocratica:

```bash
HUGGINGFACE_TOKENIZER=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

Serve a contare i token **con lo stesso tokenizzatore del modello**.
Senza, cognee ripiega su TikToken, che è di OpenAI e spezza le parole in
modo diverso: il conteggio sbaglia, i pezzi escono più lunghi di quanto
si crede, e quello che sfora sparisce. Un guasto che non vedi mai
succedere, e che si manifesta solo come «questa frase non la trova mai».

Se nei log vedi `Falling back to TikToken`, ti manca il pacchetto
`transformers`: è in `requirements.txt` e si installa senza PyTorch.

**Cosa gli embedding continuano a non sapere:** che «E4» e «F03» sono due
codici diversi. Per il modello sono due stringhe corte, senza contesto,
quasi identiche. È il difetto speculare di BM25.

## 5. I numeri, non le opinioni

Ecco perché il corso ti fa scrivere tutti e due. Queste sono le dieci
domande di `domande-ricerca.yaml` misurate sul corpus del corso (48
pezzi), guardando i primi 3 risultati:

| Domanda | BM25 | semantica |
|---|:---:|:---:|
| Che candela monta il rasaerba? | sì | sì |
| Il **tagliaerba** non si accende | **NO** | sì |
| La **lavabiancheria** lascia l'acqua | sì | sì |
| Cosa vuol dire il codice **F03**? | sì | **NO** |
| Cosa vuol dire il codice E4? | sì | sì |
| Con che coppia si stringe il bullone della lama? | sì | sì |
| Perché il trapano **si scarica** subito? | sì | **NO** |
| Quando ho **spurgato** i freni? | sì | **NO** |
| A che pressione tengo l'impianto? | sì | sì |
| Ho trovato delle monete **nell'elettrodomestico** | **NO** | sì |

E il conto a diverse profondità:

| metodo | primi 1 | primi 3 | primi 5 |
|---|:---:|:---:|:---:|
| BM25 | 4/10 | 8/10 | 10/10 |
| semantica | 5/10 | 7/10 | 8/10 |
| ibrida (RRF) | 4/10 | 8/10 | 10/10 |
| *unione* | *7/10* | *10/10* | *10/10* |

Leggilo con attenzione, perché contraddice quello che si legge in giro:

1. **Sbagliano cose diverse.** BM25 cade sui sinonimi, la semantica sui
   codici e sulle parole tecniche («spurgato»). Non è una gara: sono due
   attrezzi.
2. **L'unione fa 10/10 nei primi 3.** Cioè: fra i due, la risposta giusta
   c'è **sempre**. Il problema non è trovarla, è metterla in cima.
3. **L'ibrida su questo corpus non vince: pareggia con BM25.** 8/10
   contro 8/10. Fondere due classifiche costa qualcosa, e quel costo si
   mangia il guadagno.

Chi ti dice che la ricerca ibrida è sempre meglio non l'ha misurata sul
tuo corpus. **Tu adesso sai misurarla.**

## 6. Unire le due: RRF

Sommare i punteggi non si può: BM25 dà numeri da 0 a 20, il coseno da -1
a 1. Si uniscono le **posizioni** in classifica.

**RRF** = *Reciprocal Rank Fusion*, fusione dei ranghi reciproci. Ogni
sistema vota: il primo classificato prende `1/(K+1)`, il secondo
`1/(K+2)`, e così via. I voti si sommano.

```text
punteggio(pezzo) = somma su ogni classifica di  1 / (K + posizione + 1)
```

`K` (di solito 60) ammorbidisce il vantaggio dei primi posti. Con `K`
piccolo il primo classificato domina; con `K` grande contano di più i
piazzamenti diffusi. Sul nostro corpus, cambiare `K` da 1 a 60 sposta i
risultati di una domanda su dieci: su corpus piccoli è una manopola
sopravvalutata, e nel laboratorio lo verifichi.

**Il difetto di RRF**, che nella tabella sopra vedi in azione: un pezzo
trovato **da un solo sistema, al primo posto**, prende un voto solo e
viene scavalcato da pezzi mediocri trovati da entrambi. È il motivo per
cui l'ibrida perde «il tagliaerba non si accende», che la semantica
metteva prima.

### Allora perché la usiamo

Perché la domanda giusta non è «quale vince sul corpus del corso» ma
«quale mi fa meno danni sul mio corpus, che non conosco ancora». BM25
crolla su un corpus di note scritte male, con sinonimi e abbreviazioni.
La semantica crolla su cataloghi di codici. L'ibrida non è mai la
migliore e non è mai un disastro. Su un corpus vero, più grande e più
disordinato di questo, il vantaggio si vede.

E comunque: **rimisurala sul tuo**. Ti servono venti minuti e lo script
ce l'hai.

## 7. Cosa NON fa ancora

Torna la domanda del modulo 1: «quante ore ho passato in tutto sulla
caldaia?». Nessuna di queste tre ricerche può rispondere: il numero non
sta scritto in nessun pezzo, va ricostruito mettendo insieme tre note
diverse. Serve qualcosa che sappia che quelle tre note **parlano dello
stesso oggetto**.

È il modulo 4.

**Adesso: [LAB.md](LAB.md).**
