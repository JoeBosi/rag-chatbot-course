# Risposte del laboratorio 8 (riferimento per chi insegna)

## Esercizio 6 — Quale tipo peggiora di piu' senza il grafo?

**`multi-hop`**, e non di poco: di solito passa da 1/1 a 0/1.

D12 chiede quante ore in tutto sulla caldaia. Il numero (5,5) non e'
scritto in nessun documento: va ricostruito sommando tre interventi
descritti in tre note diverse. `RAG_COMPLETION` recupera i pezzi piu'
simili alla domanda, e i tre pezzi che servono non si somigliano fra
loro: somigliano alla domanda uno per volta, e nessuno dei tre la
contiene. Con il grafo, i tre interventi sono collegati allo stesso nodo
"Caldaia Termovex TX-24" e si raggiungono insieme.

Peggiorano anche gli `incrocio`, ma meno: li' i due pezzi che servono
(manuale e nota) contengono spesso le stesse parole, quindi il recupero
per somiglianza a volte li prende tutti e due per caso.

## Esercizio 6 — Puo' qualche tipo MIGLIORARE senza il grafo?

Si', i `fattuale`, e succede davvero.

La risposta a D01 ("cosa significa l'errore E4") sta scritta per intero
in una riga di tabella del manuale. `RAG_COMPLETION` mette davanti al
modello quella riga e poco altro. `GRAPH_COMPLETION` gli mette davanti
il nodo E4, i suoi vicini, le note di intervento collegate, e le ore
lavorate: il modello ha piu' materiale, e a volte risponde con la storia
dell'intervento invece che con la definizione secca.

**La lezione:** piu' contesto non e' sempre meglio. Il grafo serve
quando la risposta va costruita; quando e' gia' scritta da qualche
parte, aggiunge rumore.

E' anche il motivo per cui `quaderno.py` ha l'opzione `--tipo`: non
esiste una modalita' giusta per tutte le domande.
