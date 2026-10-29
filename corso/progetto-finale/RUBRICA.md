# Rubrica del progetto finale

Quattro livelli. Leggila prima di cominciare: serve a dirti cosa conta.

Un livello si raggiunge quando **tutte** le sue righe sono soddisfatte,
non la maggioranza. Un sistema che fa cose brillanti e inventa le
risposte non sta al livello 3: sta sotto il livello 1.

---

## Livello 0 — Non ancora

Una di queste, e basta una:

- inventa una risposta a D10 (la domanda senza risposta);
- non riesce a ingerire il corpus senza errori;
- dà il valore vecchio (1,2 bar) a D02 dopo che hai fatto il modulo 7.

La prima è la più importante e vale la pena dirlo chiaro: **un sistema
che inventa non è un sistema meno buono, è un sistema inutilizzabile**,
perché il suo output va verificato tutto, e se devi verificare tutto
tanto vale leggere i manuali.

---

## Livello 1 — Funziona

| Requisito | Come si misura |
|---|---|
| ingerisce i 4 manuali nativi e le 7 note | `manutenzione.py elenca` li mostra |
| risponde alle domande fattuali | D01, D07, D11 passano |
| dice «non lo so» a D10 | `verifica.py` del modulo 8 |
| c'è un giro di valutazione scritto | un file in `dati/valutazioni/` |
| la `RELAZIONE.md` c'è e risponde ai 5 punti | |

Risultato tipico: **6-7 su 12.** Mancano OCR, audio e qualche incrocio.

Questo livello è già un sistema che useresti. Non è un consolation
prize: interroga i tuoi manuali in italiano, a costo zero, sulla tua
macchina. Sei mesi fa non esisteva un modo semplice di farlo.

---

## Livello 2 — Incrocia le fonti

Tutto il livello 1, più:

| Requisito | Come si misura |
|---|---|
| le domande `incrocio` passano | D03, D04, D06, D09: almeno 3 su 4 |
| D03 **distingue** le due fonti | la risposta dice cosa viene dal libretto e cosa dalle note |
| D02 dà 1,4 bar senza cancellazioni a mano | R5 |
| il riassunto per tipo c'è, non solo il totale | |
| aggiungere una nota **non** ridigerisce tutto | R7, con il tempo misurato |

Risultato tipico: **9-10 su 12.** Manca l'OCR.

È il livello che dimostra di aver capito il corso: la memoria non è un
archivio più grande, è un archivio che **mette insieme** cose scritte da
persone diverse in momenti diversi.

---

## Livello 3 — Legge tutto e ascolta

Tutto il livello 2, più:

| Requisito | Come si misura |
|---|---|
| il manuale scansionato è entrato | D05 e D08 passano (`BPR6ES`, `0,7`, `SAE 30`) |
| le note vocali sono trascritte e ingerite | D12 dà `5,5` ore |
| le trascrizioni sono salvate e correggibili | `dati/trascrizioni/` esiste |
| le foto sono descritte e collegate | «che foto ho della caldaia?» risponde |
| **due** giri di valutazione, prima e dopo un cambiamento | |
| la relazione dice cosa il sistema sbaglia ancora | punto 5 |

Risultato tipico: **11-12 su 12.**

L'ultima riga vale quanto le altre. Un 12 su 12 con una relazione che
dice «funziona tutto» è un livello 2. Il metro l'hai costruito tu, e sai
che ha i suoi difetti: il confronto di frammenti prende falsi positivi,
dodici domande sono poche, e il corpus è piccolo e scritto per il corso,
quindi più gentile di quello che troverai nella vita.

Un sistema di cui sai elencare i limiti è un sistema che hai capito.

---

## Cosa NON viene valutato

Perché ci si perde tempo e non serve.

- **quanto è elegante il codice.** Se gira ed è leggibile fra un mese, va bene.
- **quanto sono belle le risposte.** Vanno bene anche secche.
- **l'interfaccia.** La riga di comando è perfetta. Se vuoi
  un'interfaccia web, è un'estensione, non un requisito.
- **la velocità.** Con le quote gratuite comanda il limite di velocità,
  non il tuo codice.

---

## Estensioni, se hai preso gusto

In ordine di rapporto fra quello che impari e quello che costa.

**1. La nota vocale che arriva da sola** (1-2 ore)
Una cartella sorvegliata: ci butti dentro l'`.m4a`, e dopo un minuto è
trascritto, corretto, ingerito e collegato. `watchdog`, venti righe. È
l'estensione che trasforma un esercizio in uno strumento che usi.

**2. Il grafo, guardato** (30 minuti)
`cognee.visualize_graph()` sputa un HTML. Aprilo. Vedere il proprio
archivio come una rete cambia il modo in cui ci pensi, e i nodi-mozzo
del modulo 7 si riconoscono a colpo d'occhio.

**3. Le citazioni obbligatorie** (1 ora)
Chiedi al modello di mettere accanto a ogni affermazione il nome del
file da cui viene. Cambia l'uso del sistema: da «mi fido» a «controllo
in due secondi».

**4. Whisper in locale** (1 ora)
`faster-whisper`, modello `small`, gira su 4 GB senza scheda grafica. Le
note vocali, che sono la tua voce e i nomi dei tuoi clienti, non escono
più di casa. La qualità è vicina a quella di Groq sull'italiano.

**5. Il secondo fornitore, per davvero** (1 ora)
Aggiungi una chiave Google AI Studio e metti **due deployment con lo
stesso `model_name`** nel gateway. LiteLLM li alterna, e la quota a
token raddoppia: il `digerisci` del corpus scende dalla mezz'ora a
dieci minuti. È il vero rimedio alla lentezza del modulo 5.

**6. Una seconda officina** (2 ore)
Due `dataset` separati, uno per cliente, con `add(dataset_name=...)`.
Serve a capire l'isolamento dei dati, che è la prima cosa che chiedono
quando un sistema del genere lo usa più di una persona.

**7. Il quaderno che parla** (2 ore)
Risposte lette ad alta voce, con `piper` in locale. In officina, con le
mani sporche, è la differenza fra usarlo e non usarlo.

---

Se arrivi in fondo a una di queste, il corso ha funzionato.
