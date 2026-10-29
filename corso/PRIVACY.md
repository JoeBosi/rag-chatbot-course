# Privacy

Pagina breve perché c'è poco da dire.

## Questo sito

Sono pagine statiche: testo, immagini e fogli di stile, tutti ospitati
qui. Il sito **non raccoglie niente**.

- **Nessun cookie**, nessuna pubblicità, nessuna analitica (niente Google
  Analytics o simili).
- **Nessuna richiesta a server di terzi**: font, fogli di stile e script
  del tema stanno su questo sito, quindi aprendo una pagina non si
  contatta nessun altro servizio. Gli unici indirizzi esterni sono i
  **link** che si trovano nei testi: valgono solo se si decide di
  cliccarli.
- **Nessun modulo da compilare**: non c'è niente da iscriversi, nessuna
  mail da lasciare. La ricerca interna del sito funziona dentro il
  browser, senza mandare fuori quello che si cerca.
- **Nessun registro degli accessi**: il server che serve queste pagine
  non tiene un log delle visite. Annota solo i propri eventi tecnici
  (rinnovo dei certificati, errori), che restano sul server.

## Quando fai il corso, invece

Il corso ti fa usare i piani gratuiti dei fornitori di modelli (Groq,
Google AI Studio, OpenRouter). Lì vale la loro informativa, non questa: i
testi che invii escono dal tuo computer e **quasi tutti i piani gratuiti
si riservano di usarli per migliorare i loro modelli**.

Conseguenza pratica, la stessa che trovi in home e nel progetto finale:
nel tuo archivio metti i manuali del tostapane e le tue note di
officina, **non** dati di clienti, dati personali di altre persone,
documenti riservati o password.

Se il materiale è sensibile, il corso tiene aperta dal primo modulo la
**strada locale** con [Ollama](SETUP.md#strada-locale-ollama): modelli che
girano sul tuo computer, nessun dato che esce. È più lenta e chiede più
memoria, ma è completa: ogni modulo funziona anche così.

Gli embedding, cioè la parte che trasforma i testi in numeri, si
calcolano **sempre in locale**, anche quando il resto passa dai
fornitori: quella parte del tuo materiale non esce mai, per come è
costruito il corso.

## Le tue chiavi

Le chiavi dei fornitori stanno nel file `.env` sul tuo computer, e il
corso insegna a non scriverle mai nel codice, nelle configurazioni o nei
repository. Il gateway del modulo 2 si avvia in ascolto solo su
`127.0.0.1` proprio per questo: nessuno sulla tua rete può usare le tue
chiavi.
