# RAG Chatbot Tutorial: build an AI memory with Python, cognee and free LLM APIs

**English** · [Italiano](README.it.md)

**Free RAG course: build a chatbot that remembers your documents, step by step, at zero cost.**

A hands-on 20-hour RAG chatbot tutorial (course language: Italian) that takes you from zero to a
personal knowledge base that organizes itself: you pour documents and voice
notes into it, and it links, updates and answers questions about them.
Topics: retrieval-augmented generation (RAG), embeddings, knowledge graphs
with [cognee](https://github.com/topoteretes/cognee), an
[LiteLLM](https://github.com/BerriAI/litellm) gateway over free LLM APIs
(Groq, Google AI Studio, OpenRouter), memory maintenance and evaluation.
Total cost: zero. A fully local path with Ollama is available.

**Live course:** https://corso-rag.giuseppebosi.com

## Quick start (macOS or Linux; Windows via WSL2)

```bash
git clone https://github.com/JoeBosi/rag-chatbot-course.git
cd rag-chatbot-course/corso
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # then add your free API keys, see CHIAVI.md
python moduli/01-perche-serve-una-memoria/verifica.py
```

Build the website locally (MkDocs Material):

```bash
python3 -m venv .venv && .venv/bin/pip install mkdocs-material
.venv/bin/python tools/build_sito.py   # output in site/
```

The build copies only an allow-list of files and stops if it finds an API key.

## Structure

| Path | Content |
|---|---|
| `corso/` | the course: setup, 8 modules (`LEZIONE.md` lesson, `LAB.md` lab, `starter/`, `soluzione/`, `verifica.py` checker), final project with a sample corpus |
| `corso/memoria/` | the reusable Python package built step by step |
| `tools/` | site build script, SEO files (robots.txt, llms.txt) |
| `overrides/` | MkDocs Material theme overrides (header, footer, metadata) |
| `mkdocs.yml` | site configuration |

The sample corpus (appliance manuals, repair notes, synthetic voice notes) is invented for the course.

## License

- Course texts: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Code: MIT (see [LICENSE](LICENSE))

## Author

Giuseppe Bosi · [www.giuseppebosi.com](https://www.giuseppebosi.com) · [LinkedIn](https://www.linkedin.com/in/giuseppebosi)
