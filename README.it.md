# Corso RAG e Chatbot: costruisci la tua memoria AI

[English](README.md) · **Italiano**

Corso pratico e gratuito di 20 ore: si parte da zero e si arriva a un
archivio di conoscenza personale che si riorganizza da solo. Ci si versano
documenti e note vocali, e lui collega, aggiorna e risponde. Argomenti: RAG,
embedding, grafi di conoscenza con cognee, gateway LiteLLM sui modelli
gratuiti (Groq, Google AI Studio, OpenRouter), manutenzione e valutazione
della memoria. Costo: zero. C'è anche la strada tutta locale con Ollama.

**Corso online:** https://corso-rag.giuseppebosi.com

## Avvio rapido (macOS o Linux; Windows con WSL2)

```bash
git clone https://github.com/JoeBosi/rag-chatbot-course.git
cd rag-chatbot-course/corso
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # poi le chiavi gratuite, vedi CHIAVI.md
python moduli/01-perche-serve-una-memoria/verifica.py
```

Per costruire il sito: `.venv/bin/python tools/build_sito.py` (MkDocs
Material). Lo script copia solo i file ammessi e si ferma se trova una chiave.

## Struttura

- `corso/`: il corso (preparazione, 8 moduli con lezione, laboratorio,
  starter, soluzione e verifica, progetto finale con corpus di esempio)
- `corso/memoria/`: il pacchetto Python costruito modulo dopo modulo
- `tools/`: costruzione del sito, robots.txt e llms.txt
- `overrides/`: personalizzazioni del tema
- `mkdocs.yml`: configurazione del sito

Il corpus di esempio (manuali, note di riparazione, note vocali sintetiche) è inventato per il corso.

## Licenza

Testi [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.it), codice MIT (testo in `corso/CREDITI.md`).

## Autore

Giuseppe Bosi · [www.giuseppebosi.com](https://www.giuseppebosi.com) · [LinkedIn](https://www.linkedin.com/in/giuseppebosi)
