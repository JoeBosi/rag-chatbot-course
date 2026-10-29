# Laboratorio 8 — Costruire il metro

**Durata: 84 minuti.**

Ti serve il gateway acceso e l'archivio **completo**, tutti e dodici i
documenti. Se al modulo 5 avevi usato `--ridotto`, rimedia adesso:

```bash
python memoria/quaderno.py aggiungi      # senza --ridotto
python memoria/quaderno.py digerisci
```

`cognify` è incrementale: riconosce quelli già digeriti e lavora solo
sui nuovi.

Serve il corpus intero perché le dodici domande parlano di tutti e
cinque gli apparecchi: con solo caldaia e lavatrice ne falliresti la
metà per il motivo sbagliato, cioè perché il documento non c'è, non
perché il sistema sbaglia.

---

## Esercizio 1 — Leggere l'insieme di valutazione (10 minuti)

```bash
cat progetto-finale/domande.yaml
```

Dodici domande. Per ognuna, prima di lanciare qualunque cosa, scrivi su
un foglio la tua previsione: **passa o non passa?**

Questo passaggio sembra inutile e non lo è. Fra venti minuti confronterai
la tua previsione con il risultato, e le domande su cui ti sei sbagliato
sono quelle da cui impari qualcosa. Se il risultato ti conferma tutto,
non hai imparato niente.

Conta quante ne prevedi giuste. Segna il numero.

## Esercizio 2 — Fare una domanda e giudicarla (20 minuti)

Apri `starter/valuta.py`.

**TODO 1** è la funzione `giudica(risposta, domanda)`, il cuore di tutto:

```python
def giudica(risposta: str, domanda: dict) -> tuple[bool, str]:
    testo = normalizza(risposta)

    if domanda.get("tipo") == "assente":
        return giudica_assente(testo)

    mancanti = [a for a in domanda.get("attese", [])
                if normalizza(a) not in testo]
    if mancanti:
        return False, f"manca: {', '.join(mancanti)}"

    presenti = [v for v in domanda.get("vietate", [])
                if normalizza(v) in testo]
    if presenti:
        return False, f"contiene il fatto vecchio: {', '.join(presenti)}"

    return True, ""
```

Guarda `normalizza()`, che è già scritta: minuscolo, spazi compattati,
virgola decimale e punto decimale resi uguali. Serve perché il modello
scrive «1.4» o «1,4» a seconda dell'umore, e non è quello che stai
misurando.

**TODO 2** è `giudica_assente(testo)`, la regola speciale spiegata nella
lezione:

```python
AMMISSIONI = ("non lo so", "non trovo", "non e' presente", "non risulta",
              "non compare", "nessuna informazione", "non ho trovato",
              "non viene specificato", "non e' indicato")
NUMERO_CON_UNITA = re.compile(r"\d+[.,]?\d*\s*(bar|psi|atm|kpa)")
```

Due condizioni, tutte e due necessarie: c'è un'ammissione **e** non c'è
un numero con unità di misura.

## Esercizio 3 — Il giro completo (20 minuti)

**TODO 3** è `giro()`: per ogni domanda, interroga l'archivio, giudica,
stampa, **aspetta**.

```python
for domanda in domande:
    risposta = await interroga(domanda["domanda"])
    passata, motivo = giudica(risposta, domanda)
    ...
    await asyncio.sleep(PAUSA)
```

`PAUSA` è a 30 secondi e non è prudenza eccessiva: è il budget del
modulo 5 (2 chiamate al minuto). Senza, le prime domande partono a
raffica, prendi 429, e il giro dura di più.

```bash
python memoria/valuta.py
```

Sono dodici domande con la pausa: mettici **sei-sette minuti**. Vai a
prendere un caffè, non è tempo tuo, è tempo del limite di velocità.

Quando finisce, confronta con la tua previsione dell'esercizio 1.

## Esercizio 4 — Il riassunto per tipo (15 minuti)

**TODO 4**: alla fine del giro, oltre al totale, stampa una riga per
ogni tipo di domanda.

```
tipo          passate
fattuale         3/3
aggiornato       1/1
incrocio         2/4
ocr              0/2
multi-hop        1/1
assente          1/1
--------------------
totale           8/12
```

Guarda il tuo `ocr`. Se è `0/2`, il rasaerba non è entrato: il suo
manuale è un PDF scansionato e senza OCR non contiene neanche un
carattere leggibile. Verifica:

```bash
python -c "import pypdf; print(len(pypdf.PdfReader('progetto-finale/corpus/manuali/greencut-rm46.pdf').pages[0].extract_text()))"
```

Se stampa `0`, non è il modello che sbaglia: è che quel documento, per
il tuo sistema, è una pagina bianca. **Nessuna modifica al prompt
risolve un documento vuoto.** Il rimedio è nel progetto finale.

Questa è la lezione più importante del modulo: il riassunto per tipo ti
dice **dove guardare**, e ti impedisce di perdere un pomeriggio a
limare il prompt quando il problema è nell'ingestione.

## Esercizio 5 — Lasciare traccia (10 minuti)

**TODO 5**: scrivi il risultato in `dati/valutazioni/AAAA-MM-GG-HHMM.md`,
con in testa la configurazione usata:

```markdown
# Valutazione del 2026-09-20 18:42

modello:     openai/gpt-oss-120b via gateway
embedding:   paraphrase-multilingual-MiniLM-L12-v2 (384)
ricerca:     grafo (GRAPH_COMPLETION)
archivio:    12 documenti

| id | tipo | esito | motivo |
|---|---|---|---|
| D01 | fattuale | OK | |
| D05 | ocr | NO | manca: BPR6ES, 0,7 |
```

Senza la configurazione in testa, fra un mese avrai un file con «8/12» e
nessun modo di sapere a cosa si riferiva.

## Esercizio 6 — Misurare un cambiamento (9 minuti)

Adesso il metro serve a qualcosa. Cambia **una cosa sola**:

```bash
python memoria/valuta.py --tipo testo
```

Usa `RAG_COMPLETION` (solo recupero, niente grafo) al posto di
`GRAPH_COMPLETION`. Confronta i due riassunti per tipo.

Nel `RISPOSTE.md` scrivi:

1. quale tipo di domanda peggiora di più senza il grafo;
2. se qualche tipo **migliora** senza il grafo, e perché può succedere.

La seconda non è una domanda trabocchetto. Il grafo aggiunge contesto, e
il contesto in più può confondere su una domanda fattuale secca.

---

## Verifica

```bash
python moduli/08-valutare-il-sistema/verifica.py
```

Non interroga il modello: controlla il tuo codice giudicando risposte
finte, di cui si sa già l'esito. Se il tuo `giudica()` dà un punto a
«la pressione è 1,2 bar, poi portata a 1,4», la verifica te lo dice.

**Consegna:** `valuta.py` completo, un file in `dati/valutazioni/` e il
`RISPOSTE.md` dell'esercizio 6.

Totale progressivo: **18,5 / 20 ore.** Prossimo: [il progetto
finale](../../progetto-finale/BRIEF.md).
