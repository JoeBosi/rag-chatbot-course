# Glossario

Ogni sigla del corso è sciolta la prima volta che compare, nel modulo in
cui serve. Questa pagina serve dopo, quando la incontri di nuovo e non
ti ricordi.

In ordine alfabetico. La colonna «modulo» dice dove se ne parla davvero.

---

## Sigle

| Sigla | Per esteso | In parole | Modulo |
|---|---|---|---|
| **ANN** | *Approximate Nearest Neighbors*, vicini più prossimi approssimati | Cercare i vettori simili senza confrontarli tutti. Sbaglia qualche volta, ed è mille volte più veloce | 3 |
| **API** | *Application Programming Interface*, interfaccia di programmazione | Il modo in cui un programma parla con un altro. Qui: come il tuo codice parla con il modello | 1 |
| **BM25** | *Best Matching 25* | La formula che decide quanto un documento c'entra con le parole che hai cercato. Il 25 è il numero della versione, non vuol dire niente | 3 |
| **CSV** | *Comma-Separated Values*, valori separati da virgola | Un foglio di calcolo in formato testo | 8 |
| **ECL** | *Extract, Cognify, Load*, estrai, capisci, carica | Le tre fasi di cognee. È la sua parola per la pipeline | 5 |
| **HNSW** | *Hierarchical Navigable Small World* | L'algoritmo che pgvector usa per trovare i vettori simili in fretta. Il nome descrive la struttura: strati di scorciatoie | 6 |
| **HTTP** | *HyperText Transfer Protocol* | Il protocollo con cui i programmi si parlano su internet. Quando leggi «429», è un codice HTTP | 2 |
| **IDF** | *Inverse Document Frequency*, frequenza inversa nei documenti | Quanto è rara una parola. «BPR6ES» è rara e pesa; «il» c'è ovunque e non pesa | 3 |
| **JSON** | *JavaScript Object Notation* | Un modo di scrivere dati strutturati che i programmi leggono senza sbagliare | 2 |
| **LLM** | *Large Language Model*, modello linguistico grande | Il modello che scrive le risposte. «Grande» si riferisce al numero di parametri, non alla qualità | 1 |
| **OCR** | *Optical Character Recognition*, riconoscimento ottico dei caratteri | Leggere il testo dentro un'immagine. Serve per i PDF scansionati | progetto |
| **RAG** | *Retrieval-Augmented Generation*, generazione aumentata dal recupero | Cerca prima, rispondi poi. Il modello non risponde a memoria: risponde su documenti che gli hai messo davanti | 1 |
| **RPD** | *Requests Per Day*, richieste al giorno | Quante volte puoi chiamare il modello in 24 ore | 2 |
| **RPM** | *Requests Per Minute*, richieste al minuto | Quante volte puoi chiamarlo in un minuto | 2 |
| **RRF** | *Reciprocal Rank Fusion*, fusione per rango reciproco | Il modo di mettere insieme due classifiche diverse guardando la posizione, non il punteggio | 3 |
| **SQL** | *Structured Query Language* | La lingua con cui si interrogano i database a tabelle | 6 |
| **TF** | *Term Frequency*, frequenza del termine | Quante volte la parola compare nel documento | 3 |
| **TPD / TPM** | *Tokens Per Day / Per Minute* | Quanti token puoi consumare al giorno / al minuto. **Su Groq è il TPM il limite che colpisci per primo**, non l'RPM | 2, 5 |
| **URL** | *Uniform Resource Locator* | Un indirizzo web | 2 |
| **VPS** | *Virtual Private Server*, server privato virtuale | Un computer in affitto da qualche parte, che sta sempre acceso | SETUP-VPS |
| **YAML** | *YAML Ain't Markup Language* | Un formato di configurazione leggibile a occhio. Si scrive con l'indentazione, e l'indentazione conta | 2 |

---

## Parole

**Archivio / dataset.** Un insieme di documenti con un nome. In questo
corso è sempre `officina`. Servono per tenere separate cose che non
devono mescolarsi, per esempio due clienti.

**Backoff esponenziale.** Aspettare sempre di più fra un tentativo e il
successivo: 1 secondo, poi 2, poi 4. Serve a non peggiorare la
situazione quando un servizio è in affanno. *Modulo 4.*

**Chunk / pezzo.** Un documento spezzato in parti abbastanza piccole da
stare nel contesto del modello. Come lo spezzi cambia tutto: il modulo 3
lo dimostra tagliando a metà una tabella. *Modulo 3.*

**Contesto / finestra di contesto.** Quanto testo il modello riesce a
tenere sott'occhio in una volta. Grande non vuol dire che lo legge bene:
vedi *lost in the middle*. *Modulo 1.*

**Coseno / similarità del coseno.** Quanto due vettori puntano nella
stessa direzione, da -1 a 1. È il modo standard di dire «questi due
testi parlano della stessa cosa». *Modulo 3.*

**Cypher.** La lingua per interrogare i grafi, come SQL lo è per le
tabelle. *Modulo 6.*

**Embedding / vettore.** Un elenco di numeri che rappresenta il
significato di un testo. Testi che vogliono dire cose simili hanno
vettori vicini. Nel corso ne usiamo da 384 numeri, calcolati sul tuo
computer. *Modulo 3.*

**Entità.** Una cosa di cui l'archivio sa qualcosa: un apparecchio, un
ricambio, una data. Nel grafo è un nodo. *Modulo 4.*

**Fallback / riserva.** Il fornitore di scorta, a cui il gateway passa
quando il primo non risponde. *Modulo 2.*

**Gateway.** Il pezzo in mezzo fra il tuo codice e i fornitori. Il tuo
codice conosce un indirizzo solo; dietro, il gateway sceglie, alterna e
ripiega. Qui è LiteLLM. *Modulo 2.*

**Grafo.** Entità collegate da relazioni. Serve a rispondere alle
domande che chiedono di mettere in fila due passaggi. *Modulo 4.*

**Hub / nodo-mozzo.** Un nodo collegato a tutto. Sembra ricchezza ed è
un difetto: se «bar» è collegato a mezzo archivio, il recupero a due
salti smette di selezionare. *Modulo 7.*

**Ibrida (ricerca).** Cercare con le parole **e** con il significato, e
unire le due classifiche. Nel corso non vince sempre, e il modulo 3
mostra i numeri veri. *Modulo 3.*

**Lost in the middle.** Il fatto misurato che i modelli ricordano bene
l'inizio e la fine di un testo lungo, e male il centro. È il motivo per
cui «metti tutto nel contesto» non funziona. *Modulo 1.*

**Multi-hop / a più salti.** Una domanda la cui risposta non sta scritta
da nessuna parte e va ricostruita mettendo insieme due o tre documenti.
«Quante ore ho passato in tutto sulla caldaia?» *Modulo 4.*

**pgvector.** L'estensione che insegna a PostgreSQL a cercare per
somiglianza. *Modulo 6.*

**Prompt.** Quello che mandi al modello: istruzioni più contesto più
domanda. *Modulo 1.*

**Quantizzazione.** Rimpicciolire un modello arrotondando i suoi numeri,
per farlo stare in meno memoria. È il motivo per cui un modello da 4
miliardi di parametri gira su un portatile. *Modulo 2, Ollama.*

**Relazione / arco.** Il collegamento fra due entità: «la Termovex TX-24
**monta** il vaso 7832-VE8». *Modulo 4.*

**Recupero.** La prima metà di ogni RAG: trovare i pezzi giusti. Se
sbaglia qui, nessun modello aggiusta dopo. *Modulo 3.*

**Rate limit / limite di velocità.** Quanto puoi chiedere a un fornitore
prima che ti dica di aspettare. Quando ti dice di aspettare, risponde
`429`. *Modulo 2.*

**Structured output / uscita strutturata.** Obbligare il modello a
rispondere in un formato fisso, descritto con uno schema, invece che in
prosa. Se il modello è piccolo, a volte non ce la fa: il modulo 2 lo
mostra dal vivo. *Modulo 2.*

**Token.** Il pezzo di testo che il modello conta: circa quattro
caratteri, o tre quarti di parola. Le quote si misurano in token.
*Modulo 1.*

**Tripla.** Soggetto-verbo-oggetto, la forma in cui si scrive un fatto
in un grafo. *Modulo 4.*

**Whisper.** Il modello che trascrive l'audio. Su Groq è gratuito.
*Progetto finale.*
