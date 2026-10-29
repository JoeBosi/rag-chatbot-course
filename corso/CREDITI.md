# Crediti

Questo corso sta in piedi sul lavoro di altri. Qui c'è chi, con la sua
licenza e il link al progetto, perché chi vuole andare a fondo sappia
dove guardare.

## Le librerie che il corso installa

| Libreria | A cosa serve nel corso | Licenza |
|---|---|---|
| [cognee](https://github.com/topoteretes/cognee) | il motore di memoria dei moduli 5-8: spezza, estrae entità, costruisce il grafo, risponde | Apache 2.0 |
| [LiteLLM](https://github.com/BerriAI/litellm) | il gateway del modulo 2: un solo indirizzo davanti a più fornitori, con la catena di riserve | MIT |
| [Kuzu](https://github.com/kuzudb/kuzu) | il database a grafo dove vivono entità e relazioni | MIT |
| [LanceDB](https://github.com/lancedb/lancedb) | l'archivio dei vettori, di partenza | Apache 2.0 |
| [pgvector](https://github.com/pgvector/pgvector) | l'alternativa del modulo 6: vettori dentro PostgreSQL | PostgreSQL License |
| [fastembed](https://github.com/qdrant/fastembed) | calcola gli embedding sul tuo computer, senza chiamate a pagamento | Apache 2.0 |
| [transformers](https://github.com/huggingface/transformers) | il tokenizzatore con cui si contano i token del modello di embedding (modulo 3) | Apache 2.0 |
| [pypdf](https://github.com/py-pdf/pypdf) | legge i PDF del corpus e mostra quando un PDF non ha testo da leggere | BSD 3-Clause |
| [httpx](https://github.com/encode/httpx) | le chiamate HTTP delle verifiche | BSD 3-Clause |
| [PyYAML](https://github.com/yaml/pyyaml) | legge la configurazione del gateway e l'insieme di domande del modulo 8 | MIT |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | carica il file `.env` con le chiavi | BSD 3-Clause |
| [Ollama](https://github.com/ollama/ollama) | la «strada locale»: modelli sul proprio computer, niente esce da casa | MIT |

Il sito è costruito con [MkDocs](https://github.com/mkdocs/mkdocs)
(licenza BSD 2-Clause) e il tema
[Material for MkDocs](https://github.com/squidfunk/mkdocs-material)
(licenza MIT).

## I modelli citati

| Modello | Dove si usa | Chi lo fa |
|---|---|---|
| `openai/gpt-oss-120b` | il modello che risponde ed estrae le entità, servito sul piano gratuito di [Groq](https://groq.com/) | OpenAI, pesi aperti (Apache 2.0) |
| `paraphrase-multilingual-MiniLM-L12-v2` | gli embedding, calcolati in locale | [Sentence-Transformers](https://www.sbert.net/), Apache 2.0 |
| `whisper-large-v3-turbo` | trascrive le note vocali del progetto finale | OpenAI, MIT |
| `gemini-3.5-flash` | riserva del gateway, testi lunghi, lettura di foto e scansioni, su [Google AI Studio](https://aistudio.google.com/) | Google |
| `qwen3:4b-instruct` | la strada locale con Ollama | Alibaba Cloud, Apache 2.0 |

I piani gratuiti e i loro limiti cambiano. Le pagine ufficiali restano
l'unica fonte aggiornata:
[limiti di Groq](https://console.groq.com/docs/rate-limits),
[limiti di Google AI Studio](https://ai.google.dev/gemini-api/docs/rate-limits),
[limiti di OpenRouter](https://openrouter.ai/docs/limits).

## Le fonti

- la documentazione di [cognee](https://docs.cognee.ai/) per la pipeline,
  le operazioni di memoria e l'esportazione dell'archivio;
- la documentazione di [LiteLLM](https://docs.litellm.ai/) per il proxy,
  le riserve e i tentativi;
- [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) e
  [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
  per la parte di recupero del modulo 3.

## Il corpus del corso è inventato

I cinque manuali (caldaia, lavatrice, avvitatore, bici, rasaerba) e le
note di riparazione sono scritti per il corso: nessun apparecchio
esistente, nessun manuale vero. Un manuale reale è coperto da copyright e
non si può distribuire, ed è anche troppo lungo per le ore che ci sono.

## Licenze di questo corso

I **testi** (lezioni, laboratori, brief, rubrica, corpus) sono sotto
[Creative Commons Attribuzione 4.0](https://creativecommons.org/licenses/by/4.0/deed.it):
si possono usare, modificare e ridistribuire, anche per insegnare, anche
a pagamento, citando l'autore.

Il **codice** (starter, soluzioni, verifiche, strumenti) è sotto licenza
MIT:

```text
Copyright (c) 2026 Giuseppe Bosi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

I nomi dei prodotti e dei servizi citati appartengono ai rispettivi
proprietari.
