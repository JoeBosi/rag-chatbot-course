# Costruisci la tua memoria AI

Corso pratico di 20 ore. Si parte da zero e si arriva a un archivio di
conoscenza personale che si riorganizza da solo: ci si versano documenti,
gli si raccontano cose parlando, e lui collega, aggiorna e risponde.

Alla fine avrai **Il quaderno di officina**: i manuali dei tuoi
elettrodomestici e dei tuoi attrezzi, più le note di quello che hai
scoperto riparandoli, interrogabili insieme.

Esempio di domanda a cui il sistema risponde alla fine del corso:

> «L'errore E4 sulla caldaia: cosa dice il libretto e cosa ho trovato io
> l'ultima volta?»

## A chi si rivolge

Sai installare un programma, sai aprire un terminale, hai visto del codice
Python ma non lo scrivi tutti i giorni. Di intelligenza artificiale non sai
niente: va benissimo. Ogni termine viene sciolto e spiegato la prima volta
che compare, e il [glossario](GLOSSARIO.md) raccoglie tutto in una riga
per voce.

## Cosa ti serve

| Cosa | Dettaglio |
|---|---|
| Sistema operativo | macOS o Linux. **Windows non è supportato**: usa WSL2 (Ubuntu), spiegato in [SETUP.md](SETUP.md) |
| Python | 3.11 o 3.12 |
| Disco | 3 GB liberi |
| RAM | 4 GB (8 GB se vuoi provare la strada locale con Ollama) |
| Soldi | **zero**. Nessuna carta di credito, in nessun passaggio |
| Account gratuiti | Groq, Google AI Studio, OpenRouter — istruzioni in [CHIAVI.md](CHIAVI.md) |

## Avvertenza sui dati: leggila adesso

I piani gratuiti dei fornitori di modelli si pagano con i tuoi dati: quasi
tutti si riservano di usare quello che invii per addestrare i loro modelli.
Per i manuali del tostapane e per imparare va benissimo. **Non metterci
dati di clienti, dati personali di terzi, documenti riservati o
password.** Se il materiale è sensibile, il corso ha una strada
alternativa che non manda niente fuori dal tuo computer: Ollama, segnalata
in ogni modulo dal riquadro «Strada locale».

## Com'è fatto il corso

Otto moduli, più il progetto finale. Ogni modulo comincia con qualcosa che
esegui e vedi funzionare nei primi cinque minuti; la spiegazione arriva
dopo, per dare un nome a quello che hai appena visto. Ogni modulo finisce
con un pezzo di programma funzionante che ti tieni e riusi nel modulo
dopo: il corso costruisce **una cosa sola**, per aggiunte successive.

Tre volte il corso ti fa costruire una versione sbagliata di proposito,
te la fa rompere sui tuoi dati, e solo dopo ti dà quella giusta. Non è
tempo perso: è l'unico modo per capire perché la soluzione buona è fatta
così.

### Ripartizione delle ore

| # | Modulo | Ore | di cui laboratorio | Totale progressivo |
|---|---|---:|---:|---:|
| 1 | [Perché serve una memoria](moduli/01-perche-serve-una-memoria/LEZIONE.md) | 2,0 | 1,0 | 2,0 |
| 2 | [Chiavi, gateway e quote](moduli/02-chiavi-gateway-e-quote/LEZIONE.md) | 2,0 | 1,3 | 4,0 |
| 3 | [Come un testo diventa cercabile](moduli/03-testo-cercabile/LEZIONE.md) | 3,0 | 2,0 | 7,0 |
| 4 | [Dal recupero al grafo](moduli/04-dal-recupero-al-grafo/LEZIONE.md) | 2,5 | 1,7 | 9,5 |
| 5 | [La pipeline di cognee](moduli/05-la-pipeline-di-cognee/LEZIONE.md) | 3,0 | 2,0 | 12,5 |
| 6 | [Dove vive il dato](moduli/06-dove-vive-il-dato/LEZIONE.md) | 2,0 | 1,4 | 14,5 |
| 7 | [Manutenzione della memoria](moduli/07-manutenzione-della-memoria/LEZIONE.md) | 2,0 | 1,3 | 16,5 |
| 8 | [Valutare il proprio sistema](moduli/08-valutare-il-sistema/LEZIONE.md) | 2,0 | 1,4 | 18,5 |
| — | [Progetto finale: il quaderno di officina](progetto-finale/BRIEF.md) | 1,5 | 1,5 | **20,0** |

Laboratorio: **13,6 ore su 20**.

## Come si usa questo repository

```bash
git clone <indirizzo-del-repo> memoria-ai
cd memoria-ai
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # poi riempi .env seguendo CHIAVI.md
```

Tutti i percorsi scritti nel corso sono **relativi alla radice del
repository**. Se un comando comincia con `python moduli/03-...`, va
lanciato da questa cartella.

Struttura di ogni modulo:

| File | A cosa serve |
|---|---|
| `LEZIONE.md` | la spiegazione. Si legge |
| `LAB.md` | il laboratorio. Si esegue |
| `starter/` | codice incompleto: è il punto di partenza |
| `soluzione/` | la versione completa e commentata. Guardala **dopo** aver provato |
| `verifica.py` | ti dice se il laboratorio è riuscito. Si lancia da solo |

Alla fine di ogni laboratorio:

```bash
python moduli/01-perche-serve-una-memoria/verifica.py
```

Lo script stampa `OK` riga per riga, oppure ti dice esattamente cosa manca.

## Ordine di lettura consigliato

1. [SETUP.md](SETUP.md) — installazione, 30 minuti la prima volta
2. [CHIAVI.md](CHIAVI.md) — le chiavi gratuite, 20 minuti
3. Modulo 1, poi gli altri in ordine
4. [Progetto finale](progetto-finale/BRIEF.md)

Se vuoi far girare l'archivio su un server invece che sul portatile:
[SETUP-VPS.md](SETUP-VPS.md).

Se il corso lo devi **insegnare**, [DOCENTE.md](DOCENTE.md) dice perché è
fatto così, quali scelte sono state prese fra le tante possibili, e cosa
si rompe per primo.

## Licenza

I **testi** sono sotto [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.it),
il **codice** sotto licenza MIT: puoi riusarli e modificarli, anche per
insegnare, citando l'autore. Dettagli, librerie e modelli usati nella
pagina [Crediti](CREDITI.md); cosa raccoglie il sito (niente) in
[Privacy](PRIVACY.md).
