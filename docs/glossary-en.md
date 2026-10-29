# Italian → English glossary for the course translation

Use these terms every time. Code, commands, output, file and folder names,
function names and the Italian sample corpus stay **identical**: only prose
is translated. When a command contains an Italian question, keep it and add
a short English gloss in prose if the meaning matters.

## Course and structure

| Italian | English |
|---|---|
| Costruisci la tua memoria AI | Build your own AI memory |
| corso | course |
| modulo | module |
| lezione (LEZIONE.md) | lesson |
| laboratorio (LAB.md) | lab |
| starter | starter |
| soluzione | solution |
| verifica (verifica.py) | checker / check script |
| progetto finale | final project |
| brief | brief |
| rubrica | rubric |
| Il quaderno di officina | The workshop notebook |
| nota (di officina) | (workshop) note |
| note vocali | voice notes |
| corpus di partenza | starter corpus |
| Strada locale | Local path |
| Riquadro | Box |
| Approfondimenti | Further reading |
| Note per chi insegna | Notes for teachers |
| Prima di cominciare | Before you start |
| Preparare il computer | Set up your computer |
| Prendere le chiavi | Get your API keys |
| Glossario | Glossary |
| Crediti | Credits |
| Totale progressivo | Running total |
| Durata | Duration |
| Prerequisiti | Prerequisites |
| Artefatto di questo modulo | What you keep from this module |
| Se qualcosa non va | Troubleshooting |
| Sintomo / Causa / Rimedio | Symptom / Cause / Fix |
| Passo | Step |

## Technical terms

| Italian | English |
|---|---|
| memoria | memory |
| archivio | knowledge base (archive when it means the dataset) |
| recupero | retrieval |
| generazione aumentata dal recupero | retrieval-augmented generation |
| contesto / finestra di contesto | context / context window |
| allucinazione | hallucination |
| pezzo / chunk | chunk |
| spezzare (in pezzi) | chunk / split |
| ricerca semantica | semantic search |
| ricerca ibrida | hybrid search |
| grafo di conoscenza | knowledge graph |
| nodo / arco / relazione | node / edge / relationship |
| entità | entity |
| embedding / vettore | embedding / vector |
| similarità del coseno | cosine similarity |
| quota / limite | quota / rate limit |
| chiave (API) | API key |
| piano gratuito | free tier |
| fornitore | provider |
| gateway | gateway |
| ritentativo | retry |
| backoff esponenziale | exponential backoff |
| manutenzione della memoria | memory maintenance |
| rettifica | correction |
| valutare / valutazione | evaluate / evaluation |
| domande di prova | test questions |
| giudice (LLM) | (LLM) judge |
| trascrizione | transcription |
| caldaia | boiler |
| lavatrice | washing machine |
| avvitatore | impact driver / drill driver |
| rasaerba / tagliaerba | lawn mower (Italian: two different words for the same thing) |
| bici | bike |

## Author

| Italian | English |
|---|---|
| Prof. Giuseppe Bosi (firma) | by Prof. Giuseppe Bosi |
| Dottore in Ingegneria Elettronica (V.O.) | Master's-level degree in Electronic Engineering (5-year Italian Laurea, pre-reform, EQF level 7) |
| Professore di Scienze e Tecnologie Informatiche | Teacher of Computer Science and Technology |
| sito dell'autore | https://www.giuseppebosi.com/en/ |

Never: M.Sc., licensed engineer, Ing., "Professor" as a job title.

## Style

- Second person, short sentences, plain US English, same tone as the Italian.
- Numbers: keep the measured values; use a decimal point (0.8 bar) in English prose.
- Keep Italian words that appear in the corpus or in commands in quotes, with
  the English meaning in parentheses the first time: «rasaerba» (lawn mower).
- Links: keep the same relative links to `.md` files; the site resolves them to the English page.
- Headings: other pages link to Italian anchors (e.g. `CHIAVI.md#1-groq`). Every
  translated heading keeps the Italian anchor with an explicit id:
  `## 1. Groq {#1-groq}`. The id is the anchor MkDocs generates from the Italian
  heading (lowercase, accents removed, spaces → hyphens, punctuation dropped).
