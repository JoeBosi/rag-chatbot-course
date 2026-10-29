# Risposte del laboratorio 7 (riferimento per chi insegna)

## Esercizio 4 — Perche' la nota di rettifica viene recuperata e quella
## del 30 agosto no, se dicono la stessa cosa?

Perche' contiene le parole della domanda.

La nota del 30 agosto e' un verbale di intervento: parla di pulizia
dello scambiatore, di ore lavorate, e da qualche parte in mezzo dice che
ha alzato la pressione. Le parole "pressione", "esercizio" e "bar"
compaiono una volta, in mezzo ad altro.

La nota di rettifica non parla d'altro. Ha "pressione" tre volte,
"Termovex TX-24" nel titolo, "bar" quattro volte. Per BM25 e' un
documento corto e densissimo di termini della domanda: e' esattamente il
caso in cui la normalizzazione per lunghezza premia.

La lezione generale: **se vuoi che un fatto venga recuperato, scrivilo
in un documento che parla solo di quello.** Non e' un trucco, e' come
funziona il recupero.

## Esercizio 6 — I primi tre nodi-mozzo

Dipende dal giro, ma i candidati tipici sul corpus del corso sono:

1. `Caldaia Termovex TX-24` — entita' vera, ed e' giusto che sia un
   mozzo: e' l'apparecchio su cui ci sono piu' note.
2. `bar` — **difetto**. E' un'unita' di misura, non una cosa. Il
   modello l'ha promossa a entita' perche' compare in molte frasi, e
   adesso collega la caldaia alla bici passando per "bar".
3. `ore` — **stesso difetto**, per lo stesso motivo.

Il rimedio e' togliere `misura` dall'elenco dei tipi di entita' che si
danno al modello, oppure dirgli esplicitamente che le unita' di misura
sono attributi e non entita'. Poi si ridigerisce.

`validate` deve dire che grafo e vettori sono d'accordo. Se segnala nodi
presenti in uno e non nell'altro, quasi sempre c'e' stato un `cognify`
interrotto a meta' da un 429.
