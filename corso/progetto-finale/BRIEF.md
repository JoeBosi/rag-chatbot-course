# Progetto finale — Il quaderno di officina

**Durata: 1,5 ore** (tutto laboratorio).
Totale progressivo: 20,0 / 20 ore.

---

## La situazione

Fai manutenzione. Caldaie, elettrodomestici, utensili, biciclette: cose
che hanno un libretto e che si rompono in modi che sul libretto non ci
sono.

Hai due tipi di sapere, e stanno in due posti diversi.

Il **libretto** dice cosa significa l'errore E4. È scritto bene, è
preciso, ed è uguale per tutti quelli che hanno quella caldaia.

Il **tuo quaderno** dice che l'ultima volta che hai visto l'E4 su quella
caldaia in via Mazzini non era la pressione, era il vaso di espansione
sgonfio, e che ci hai messo un'ora e mezza. Questo non c'è su nessun
libretto e non ce l'ha nessun altro. È la parte che vale.

Fra sei mesi l'E4 torna. Il libretto ce l'hai ancora. Del tuo quaderno
ti ricordi il 20 %.

**Il progetto è costruire il quaderno che si ricorda al posto tuo.**

---

## Cosa deve fare

Sette requisiti. I primi quattro sono obbligatori, gli altri tre alzano
il voto.

### R1 — Ingerire i manuali, compresi quelli scansionati

Nel corpus ci sono cinque manuali in PDF. Quattro sono PDF nativi e si
leggono. Il quinto, `greencut-rm46.pdf`, è la fotografia di un libretto
di carta: per il tuo sistema, oggi, è una pagina bianca.

```bash
python -c "import pypdf; print(len(pypdf.PdfReader('progetto-finale/corpus/manuali/greencut-rm46.pdf').pages[0].extract_text()))"
```

Stampa `0`. Nessun aggiustamento del prompt risolve un documento vuoto:
va letto prima. Hai due strade, e vanno bene tutte e due.

| Strada | Come | Costo | Privacy |
|---|---|---|---|
| modello multimodale | `memoria-occhi` nel gateway (Gemini) | quota gratuita | le pagine escono di casa |
| OCR in locale | `pip install "cognee[rapidocr]==1.6.0"` | zero | non esce niente |

Se scegli la prima, rileggi l'avvertenza in fondo a questa pagina prima
di mandare fuori una scansione.

**Prova che è fatto:** la domanda D05 (`BPR6ES`, `0,7`) passa.

### R2 — Accettare le note a fine lavoro, scritte o dettate

Scritte è facile: un file Markdown in una cartella, `add` + `cognify`.

Dettate è il punto. In `corpus/audio/` ci sono due note vocali `.m4a`,
quelle che si registrano in macchina tornando dal lavoro, quando
scrivere non si può. Vanno **trascritte da sole** e finire nell'archivio
come le altre.

Nel gateway c'è già `memoria-orecchie` (Whisper su Groq, gratuito).
Quota: 20 trascrizioni al minuto, 2.000 al giorno. Non è un problema.

```python
with open(percorso, "rb") as audio:
    trascrizione = await client.audio.transcriptions.create(
        model="memoria-orecchie", file=audio, language="it")
```

La trascrizione va salvata come file di testo **prima** di darla in
pasto a `add`, per un motivo pratico: Whisper sbaglia i codici ricambio,
e tu devi poter aprire il file e correggere `7845 NTC` in `7845-NTC`
senza rifare la trascrizione.

**Prova che è fatto:** la domanda D12 passa con `5,5` ore. Prima di
ingerire la nota vocale del 12/09 la risposta giusta è `3,5`: se il tuo
sistema dice ancora 3,5, l'audio non è entrato.

### R3 — Rispondere a domande che incrociano libretto ed esperienza

È la ragione per cui esiste il progetto.

> «L'errore E4 sulla caldaia: cosa dice il libretto e cosa ho trovato io
> l'ultima volta?»

Una risposta buona ha **due parti dichiarate come tali**: cosa dice il
manuale, cosa dicono le tue note. Una risposta che le mescola in un
paragrafo unico senza dire da dove viene cosa è una risposta peggiore,
anche quando i fatti sono giusti — perché in officina tu devi sapere se
ti stai fidando del costruttore o di te stesso di sei mesi fa.

**Prova che è fatto:** le quattro domande `incrocio` (D03, D04, D06,
D09) passano, e la risposta a D03 distingue le due fonti.

### R4 — Dire «non lo so»

D10 chiede la pressione dei pneumatici della bici. Non è scritta da
nessuna parte.

Un sistema che tira fuori un numero plausibile ha fallito il progetto, a
prescindere da come sono andate le altre undici domande. In officina una
risposta inventata e sicura di sé ti fa gonfiare una gomma a 6 bar.

**Prova che è fatto:** D10 passa con `verifica` del modulo 8.

### R5 — Aggiornarsi senza cancellare a mano

La pressione della caldaia è passata da 1,2 a 1,4 bar. Il libretto dice
ancora 1,2, e continuerà a dirlo.

Il sistema deve rispondere **1,4** senza che tu abbia cancellato niente.
Il modulo 7 ti ha dato il modo: la nota di rettifica.

**Prova che è fatto:** D02 passa, e non contiene il valore vecchio.

### R6 — Le foto

In `corpus/foto/` ci sono quattro immagini. In officina si fotografa la
targhetta, il pezzo rotto, il display con il codice errore: è il modo
più veloce di prendere una nota.

Vanno descritte da un modello multimodale (`memoria-occhi`) e la
descrizione va collegata all'apparecchio giusto. Una foto con la
descrizione «un display che mostra E4» e nessun legame con la Termovex
non serve a niente.

**Prova che è fatto:** chiedi al sistema «che foto ho della caldaia?» e
ti risponde.

### R7 — Non ripartire da zero ogni volta

Il sistema deve reggere l'uso vero: una nota nuova ogni sera, senza
ridigerire tutto l'archivio. È il modulo 7, esercizio 2.

**Prova che è fatto:** aggiungere una nota impiega una frazione del
tempo di un `digerisci` completo, e il tempo lo hai misurato.

---

## Cosa consegni

```
quaderno/
  ingerisci.py        R1, R2, R6: manuali, audio, foto
  quaderno.py         l'interrogazione (dal modulo 5)
  manutenzione.py     R5, R7 (dal modulo 7)
  valuta.py           il metro (dal modulo 8)
  dati/
    valutazioni/      almeno due giri, prima e dopo un cambiamento
    trascrizioni/     le note vocali in testo, correggibili a mano
  RELAZIONE.md
```

La `RELAZIONE.md` è due pagine, non di più, e risponde a cinque domande:

1. quale strada hai scelto per i PDF scansionati, e perché;
2. il risultato del **primo** giro di valutazione, per tipo;
3. cosa hai cambiato dopo averlo letto;
4. il risultato dell'**ultimo** giro, per tipo;
5. **una cosa che il sistema sbaglia ancora**, e cosa ci vorrebbe per
   aggiustarla.

Il punto 5 non è una formalità. Un sistema di cui sai elencare i difetti
è un sistema che hai capito. Una relazione che dice «funziona tutto» è
una relazione che vale meno di una che dice «le domande con due salti le
sbaglia se la parola chiave non compare nella prima nota».

---

## Da dove parti

Il corpus è pronto in `progetto-finale/corpus/`:

| Cartella | Contenuto |
|---|---|
| `manuali/` | 5 apparecchi, in Markdown e in PDF (uno scansionato) |
| `note/` | 7 note di intervento, con una contraddizione voluta |
| `audio/` | 2 note vocali in italiano |
| `foto/` | 4 immagini |

Gli apparecchi sono inventati ma verosimili: caldaia Termovex TX-24,
lavatrice Lavanor WM-700, avvitatore Ferrex ID-18, bici Velomonte Trail
275, rasaerba Greencut RM-46.

Le domande di valutazione sono in `progetto-finale/domande.yaml`.

---

## Come ti valuti

La griglia è in [RUBRICA.md](RUBRICA.md). Leggila **prima** di
cominciare: è scritta per dirti cosa conta, non per giudicarti alla
fine.

---

## Avvertenza, la seconda volta

L'hai già letta in [SETUP.md](../SETUP.md). Va ripetuta qui, perché è
adesso che diventa concreta.

**I piani gratuiti si ripagano con quello che ci mandi dentro.** Groq,
Google AI Studio e OpenRouter, nei loro piani senza carta di credito, si
riservano di usare le tue richieste per migliorare i loro modelli. Non è
una scorrettezza nascosta, è scritto nelle loro condizioni.

Per il corpus di questo corso è irrilevante: sono manuali di
elettrodomestici inventati.

Per il tuo quaderno vero **non lo è**. Le note di intervento contengono
indirizzi di clienti, nomi, a volte numeri di telefono. Le foto delle
targhette contengono numeri di matricola. Le note vocali contengono la
tua voce.

Tre regole, in ordine di forza:

1. **Non versarci dentro dati di clienti.** Nessuna eccezione, nessuna
   scorciatoia «tanto è solo una prova».
2. Se ti serve il tuo quaderno vero, **passa a Ollama**: nel `.env`
   cambi due righe, il modulo 2 spiega quali, e da quel momento non esce
   più niente dal tuo computer. Il sistema diventa più lento e le
   risposte un po' peggiori. È un prezzo onesto.
3. Se devi per forza usare le API gratuite su dati veri, **togli prima
   quello che identifica le persone**: indirizzi, nomi, telefoni.
   Manualmente, o con uno script che scrivi tu. Non delegando la cosa al
   modello a cui stai mandando i dati.

Questa è una delle poche cose in tutto il corso su cui non c'è un
compromesso ragionevole. Il resto si aggiusta dopo; questo no.
