# Credits {#crediti}

This course stands on other people's work. Here they are, with their
license and a link to the project, so anyone who wants to dig deeper
knows where to look.

## The libraries the course installs {#le-librerie-che-il-corso-installa}

| Library | What it does in the course | License |
|---|---|---|
| [cognee](https://github.com/topoteretes/cognee) | the memory engine of modules 5-8: it chunks, extracts entities, builds the graph, answers | Apache 2.0 |
| [LiteLLM](https://github.com/BerriAI/litellm) | the gateway of module 2: one address in front of several providers, with the fallback chain | MIT |
| [Kuzu](https://github.com/kuzudb/kuzu) | the graph database where entities and relationships live | MIT |
| [LanceDB](https://github.com/lancedb/lancedb) | the default vector store | Apache 2.0 |
| [pgvector](https://github.com/pgvector/pgvector) | the alternative in module 6: vectors inside PostgreSQL | PostgreSQL License |
| [fastembed](https://github.com/qdrant/fastembed) | computes embeddings on your computer, with no paid calls | Apache 2.0 |
| [transformers](https://github.com/huggingface/transformers) | the tokenizer used to count the embedding model's tokens (module 3) | Apache 2.0 |
| [pypdf](https://github.com/py-pdf/pypdf) | reads the corpus PDFs and shows when a PDF has no text to read | BSD 3-Clause |
| [httpx](https://github.com/encode/httpx) | the HTTP calls of the check scripts | BSD 3-Clause |
| [PyYAML](https://github.com/yaml/pyyaml) | reads the gateway configuration and the question set of module 8 | MIT |
| [python-dotenv](https://github.com/theskumar/python-dotenv) | loads the `.env` file with the keys | BSD 3-Clause |
| [Ollama](https://github.com/ollama/ollama) | the "local path": models on your own computer, nothing leaves home | MIT |

The site is built with [MkDocs](https://github.com/mkdocs/mkdocs)
(BSD 2-Clause license) and the
[Material for MkDocs](https://github.com/squidfunk/mkdocs-material)
theme (MIT license).

## The models mentioned {#i-modelli-citati}

| Model | Where it is used | Who makes it |
|---|---|---|
| `openai/gpt-oss-120b` | the model that answers and extracts entities, served on the free tier of [Groq](https://groq.com/) | OpenAI, open weights (Apache 2.0) |
| `paraphrase-multilingual-MiniLM-L12-v2` | the embeddings, computed locally | [Sentence-Transformers](https://www.sbert.net/), Apache 2.0 |
| `whisper-large-v3-turbo` | transcribes the voice notes of the final project | OpenAI, MIT |
| `gemini-3.5-flash` | gateway fallback, long texts, reading photos and scans, on [Google AI Studio](https://aistudio.google.com/) | Google |
| `qwen3:4b-instruct` | the local path with Ollama | Alibaba Cloud, Apache 2.0 |

Free tiers and their limits change. The official pages are the only
up-to-date source:
[Groq rate limits](https://console.groq.com/docs/rate-limits),
[Google AI Studio rate limits](https://ai.google.dev/gemini-api/docs/rate-limits),
[OpenRouter limits](https://openrouter.ai/docs/limits).

## Sources {#le-fonti}

- the [cognee](https://docs.cognee.ai/) documentation for the pipeline,
  the memory operations and exporting the knowledge base;
- the [LiteLLM](https://docs.litellm.ai/) documentation for the proxy,
  fallbacks and retries;
- [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) and
  [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
  for the retrieval part of module 3.

## The course corpus is made up {#il-corpus-del-corso-e-inventato}

The five manuals (boiler, washing machine, impact driver, bike, lawn
mower) and the repair notes were written for the course: no real
appliance, no real manual. A real manual is under copyright and cannot
be distributed, and it is also too long for the hours available.

## Licenses of this course {#licenze-di-questo-corso}

The **texts** (lessons, labs, brief, rubric, corpus) are under
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/deed.it):
you can use, modify and redistribute them, also for teaching, also for
a fee, as long as you credit the author.

The **code** (starters, solutions, check scripts, tools) is under the
MIT license:

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

The names of the products and services mentioned belong to their
respective owners.
