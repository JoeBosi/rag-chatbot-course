# Modulo 4 — Dal recupero alla memoria: il grafo

**Durata: 2 ore e 30** (48 minuti di lezione, 102 di laboratorio).
Totale progressivo: 9,5 / 20 ore.

Il modulo 3 ha costruito un sistema di ricerca che funziona. Questo
modulo ti fa vedere la classe di domande che quel sistema **non può**
risolvere, per come è fatto, e cosa serve al suo posto.

---

## 1. Primi cinque minuti: la domanda che rompe tutto

Con il sistema del modulo 3 già in mano:

```bash
python moduli/04-dal-recupero-al-grafo/starter/prova_multihop.py
```

Chiede: **«Quante ore ho passato in tutto sulla caldaia?»**

Guarda cosa recupera:

```text
pezzi recuperati:
   manuali/greencut-rm46.md#5
   note/2026-09-05-lavatrice-cinghia.md#0
   note/2026-05-18-avvitatore-batteria.md#0
   note/2026-06-07-bici-freno-spugnoso.md#0
   note/2026-07-21-rasaerba-non-parte.md#0

RISPOSTA: Non lo so.
```

**Nessuno dei cinque pezzi parla della caldaia.** Eppure nel corpus ci
sono due note di intervento sulla caldaia, e tutte e due dicono quanto
tempo è stato impiegato.

Questo è il terzo fallimento del corso, e il più istruttivo, perché non
si aggiusta con una manopola.

## 2. Perché è successo

La ricerca — lessicale o semantica, non cambia — fa una cosa sola:
prende la domanda e cerca il pezzo di testo **che le somiglia di più**.

La domanda «quante ore ho passato in tutto sulla caldaia» somiglia a
tutte le note di intervento: dicono tutte «Tempo impiegato: ... ore».
Somiglia anche al manuale del rasaerba, che parla di «ogni 50 ore». La
parola che discrimina — «caldaia» — è una su otto, e pesa poco.

E anche se il recupero fosse perfetto, resterebbe il problema vero:

> **La risposta non è scritta in nessun pezzo.**
> Va costruita: trovare quali interventi riguardano la caldaia, prendere
> la durata di ciascuno, sommarle.

Questo si chiama **multi-hop**, «a più salti»: per rispondere bisogna
seguire più di un collegamento.

```text
    "caldaia"  ──riguarda──  Intervento del 12 marzo  ──è durato──  1,5 ore
               ──riguarda──  Intervento del 30 agosto ──è durato──  2 ore
                                                                    ──────
                                                                    3,5 ore
```

Due salti. Il RAG classico ne fa **zero**: pesca un pezzo e lo dà in
pasto al modello. Non c'è niente, nella similitudine fra vettori, che
somigli a «segui il collegamento».

### Le domande multi-hop non sono un caso di scuola

Sono la metà delle domande che uno fa al proprio archivio:

| Domanda | Salti |
|---|---|
| Quante ore ho passato sulla caldaia? | intervento → durata |
| Quale ricambio ho usato l'ultima volta sulla bici? | apparecchio → intervento più recente → ricambio |
| Ho già avuto questo problema su un altro apparecchio? | sintomo → interventi → apparecchi |
| Cosa ho cambiato dopo l'ultima manutenzione? | data → interventi successivi |

## 3. Cosa serve: entità e relazioni

Finora il sistema vedeva **testo**. Da adesso vede **cose e collegamenti
fra cose**.

- **Entità** (o **nodo**): una cosa che ha un nome. «Caldaia Termovex
  TX-24», «vaso di espansione», «Intervento del 12 marzo 2026», «1,5 ore».
- **Relazione** (o **arco**): un collegamento orientato fra due entità,
  con un nome. «*Intervento del 12 marzo* **riguarda** *Caldaia Termovex
  TX-24*».
- **Tripla**: la coppia di entità più la relazione. `(da, relazione, a)`.
  È l'unità di informazione di un grafo.
- **Grafo di conoscenza** (*knowledge graph*): l'insieme di tutte le
  triple.

Il valore non è in nessuna tripla presa da sola: è nel fatto che sono
**collegate**. Due note scritte a cinque mesi di distanza, da cui hai
estratto lo stesso nodo «Caldaia Termovex TX-24», adesso sanno l'una
dell'altra.

## 4. Chi costruisce il grafo

Le triple qualcuno le deve tirare fuori dal testo. Fino a pochi anni fa
si faceva con regole scritte a mano, e funzionava male. Oggi lo fa il
modello, con l'**output strutturato** del modulo 2: gli si dà uno schema
JSON con «entità» e «relazioni», e lui riempie.

Il pezzo delicato è uno solo, e vale la pena dirlo prima che ti ci
scontri: **il modello deve chiamare la stessa cosa sempre nello stesso
modo**. Se in un documento estrae «Caldaia Termovex TX-24» e in un altro
«la caldaia», hai due nodi scollegati invece di uno, e il multi-hop non
funziona lo stesso.

Tre modi di limitare il danno, tutti nel laboratorio:

1. **dire al modello quali tipi di entità vuoi** (`apparecchio`,
   `componente`, `intervento`, `ricambio`, `sintomo`, `misura`) invece di
   lasciarlo inventare;
2. **chiedergli il nome completo**, non quello che compare nel testo;
3. **fondere per nome** a fine estrazione.

Il punto 3 è rozzo e lo sai: «Caldaia Termovex TX-24» e «Termovex TX-24»
restano due nodi. Aggiustarlo è il mestiere di cognee (modulo 5) e la
manutenzione è il modulo 7.

## 5. Interrogare un grafo

Con un grafo la domanda non è più «quale testo somiglia?» ma «da quale
nodo parto, e fin dove mi spingo?».

```text
1. trova il nodo di partenza   ("caldaia" -> Caldaia Termovex TX-24)
2. raccogli tutte le relazioni entro N salti
3. dai quelle relazioni al modello, come fatti
4. il modello risponde, e se serve fa la somma
```

Il passo 2 è una **visita in ampiezza** (*breadth-first*): parti da un
nodo, prendi tutti i suoi vicini, poi i vicini dei vicini. Quindici righe
di Python.

**Quanti salti?** Uno serve a poco, tre portano dentro mezzo grafo.
Due è quasi sempre la risposta giusta, ed è il valore che useremo.

## 6. Grafo e vettori non sono alternativi

Il grafo è bravissimo a seguire collegamenti e pessimo a trovare il punto
di partenza: «il coso che perde acqua sotto» non corrisponde a nessun
nodo. La ricerca semantica fa l'opposto.

Un sistema serio usa tutti e due:

| Passaggio | Chi lo fa |
|---|---|
| trovare da dove partire | ricerca ibrida (modulo 3) |
| seguire i collegamenti | grafo (questo modulo) |
| scrivere la risposta | il modello |

È esattamente l'architettura di cognee, che vedrai nel modulo 5. Adesso
la costruisci a mano, in piccolo, per sapere cosa c'è dentro.

## 7. Cosa costa

Il grafo non è gratis: ogni documento va letto dal modello.

Sul corpus del corso, 12 documenti, una chiamata ciascuno, 2.000-3.000
token a chiamata: **circa 30.000 token**, che con gli 8.000 token al
minuto del piano gratuito fanno **almeno quattro minuti** di lavoro, buona
parte dei quali passati ad aspettare.

E qui scoprirai una cosa che il modulo 2 ti ha promesso e non ti ha
ancora fatto vedere: **con una chiave sola, la catena di riserve è
decorativa**. Quando Groq dice 429, il gateway prova Gemini, che senza
chiave risponde 401, poi OpenRouter, idem, e alla fine l'errore torna a
te. Non c'è magia: se non hai un secondo fornitore, non hai un secondo
fornitore.

L'unica cosa sensata, allora, è **aspettare il tempo giusto**. Il
fornitore te lo dice dentro il messaggio di errore:

```text
Rate limit reached ... Please try again in 1.875s
```

Nel laboratorio ti diamo `pazienza.py`, quindici righe che leggono quel
numero e aspettano. È il pezzo di impianto che rende possibile qualunque
lavoro lungo su un piano gratuito, e da qui in poi lo userai sempre.

**Adesso: [LAB.md](LAB.md).**
