#!/usr/bin/env python3
"""Genera i notebook Google Colab dei laboratori in corso/notebooks/.

    python tools/crea_notebook.py

Un notebook per laboratorio, con le spiegazioni in italiano e in inglese
nella stessa cella. Il codice delle celle e' lo stesso comando che il
laboratorio fa lanciare da terminale, preceduto da "!".

La chiave del fornitore non sta mai nel notebook: si legge dai Segreti di
Colab (google.colab.userdata) e, se non ci sono, si chiede con getpass.
"""

import json
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
USCITA = RADICE / "corso" / "notebooks"
REPO = "https://github.com/JoeBosi/rag-chatbot-course.git"

_contatore = [0]


def _id():
    _contatore[0] += 1
    return f"c{_contatore[0]:03d}"


def md(it, en):
    testo = it.strip() + "\n\n---\n\n" + en.strip()
    return {"cell_type": "markdown", "id": _id(), "metadata": {},
            "source": testo.splitlines(keepends=True)}


def codice(src):
    return {"cell_type": "code", "id": _id(), "metadata": {},
            "execution_count": None, "outputs": [],
            "source": src.strip().splitlines(keepends=True)}


SETUP = '''
# Prepara l'ambiente / Set up the environment (about 1 minute)
import os, sys, subprocess
if sys.version_info[:2] not in [(3, 11), (3, 12)]:
    print("ATTENZIONE: questo corso e' provato con Python 3.11 o 3.12; hai "
          f"{sys.version_info.major}.{sys.version_info.minor}. "
          "WARNING: the course is tested on Python 3.11 or 3.12.")
BASE = "/content" if os.path.isdir("/content") else os.getcwd()
REPO_DIR = os.path.join(BASE, "rag-chatbot-course")
if not os.path.isdir(REPO_DIR):
    subprocess.run(["git", "clone", "--depth", "1", "%(repo)s", REPO_DIR], check=True)
os.chdir(os.path.join(REPO_DIR, "corso"))
%(pip)s
print("Cartella di lavoro / working folder:", os.getcwd())
'''

CHIAVE = '''
# La chiave Groq / The Groq key. Mai scritta nel notebook / never written in the notebook.
import os
from getpass import getpass

def leggi_chiave(nome="GROQ_API_KEY"):
    if os.environ.get(nome):
        return os.environ[nome]
    try:
        from google.colab import userdata          # Colab: icona della chiave, a sinistra
        return userdata.get(nome)
    except Exception:
        pass
    try:
        return getpass(f"Incolla {nome} / paste {nome}: ")
    except Exception:
        return ""

chiave = leggi_chiave()
if chiave:
    os.environ["GROQ_API_KEY"] = chiave
    os.environ["LLM_PROVIDER"] = "groq"
    print("Chiave caricata (non viene mostrata) / key loaded (not displayed).")
else:
    print("Nessuna chiave. I passaggi che chiamano il modello si fermeranno con "
          "il messaggio 'Manca GROQ_API_KEY'. Vedi la cella sopra.\\n"
          "No key. Steps that call the model will stop with 'Manca GROQ_API_KEY'. See the cell above.")
![ -f .env ] || cp .env.example .env
'''

TESTA_CHIAVE = ("""
## La chiave gratuita / The free key

Questo laboratorio chiama un modello: serve una chiave **Groq**, gratuita e senza carta di credito
([CHIAVI.md](https://corso-rag.giuseppebosi.com/CHIAVI/) spiega come ottenerla in due minuti).
Poi in Colab: icona della **chiave** nella barra a sinistra, **Aggiungi nuovo segreto**, nome
`GROQ_API_KEY`, valore la tua chiave, e attiva **Accesso da notebook**. Se non la imposti, la cella
te la chiede al momento. La chiave non finisce mai nel notebook.
""", """
This lab calls a model, so you need a free **Groq** key, no credit card
([CHIAVI.md](https://corso-rag.giuseppebosi.com/en/CHIAVI/) shows how to get one in two minutes).
Then in Colab: the **key** icon in the left bar, **Add new secret**, name `GROQ_API_KEY`, value your
key, and switch on **Notebook access**. If you skip this, the cell asks for the key when you run it.
The key is never saved in the notebook.
""")

SENZA_CHIAVE = ("""
Le celle con un'etichetta **[serve la chiave]** chiamano il modello. Senza chiave si fermano con
`Manca GROQ_API_KEY in .env`: non e' un guasto, inserisci la chiave come spiegato sopra e rilancia.
Le altre celle funzionano anche senza.
""", """
Cells labelled **[needs the key]** call the model. Without a key they stop with
`Manca GROQ_API_KEY in .env` (the message is Italian): this is not a fault, add the key as explained
above and run the cell again. The other cells work without it.
""")

INTESTAZIONE = ("""
**Come si usa.** Esegui le celle dall'alto in basso (Maiusc+Invio). Serve un account Google gratuito
per usare Colab. Il testo completo del laboratorio e' sul sito: {url_it}
""", """
**How to use it.** Run the cells from top to bottom (Shift+Enter). Colab needs a free Google account.
The full text of the lab is on the site: {url_en}
""")

SOLUZIONE = ("""
## Starter o soluzione? / Starter or solution?

Nel laboratorio scrivi tu alcune funzioni (i TODO). Qui sotto scegli:
`USA_SOLUZIONE = True` copia la soluzione, cosi' tutte le celle girano subito;
`USA_SOLUZIONE = False` copia lo **starter** con i TODO: apri il file nel pannello **File** a sinistra
(cartella `rag-chatbot-course/corso/memoria`), scrivi la funzione, salva e rilancia le celle.
""", """
In the lab you write some functions yourself (the TODOs). Choose below:
`USA_SOLUZIONE = True` copies the solution so every cell runs straight away;
`USA_SOLUZIONE = False` copies the **starter** with the TODOs: open the file in the **Files** panel on
the left (folder `rag-chatbot-course/corso/memoria`), write the function, save, and run the cells again.
""")


def copia_file(modulo, nomi):
    righe = ["USA_SOLUZIONE = True   # False = parti dallo starter e scrivi tu i TODO",
             f'MOD = "moduli/{modulo}"',
             'ORIGINE = "soluzione" if USA_SOLUZIONE else "starter"',
             "!mkdir -p memoria"]
    for n in nomi:
        righe.append(f"!cp $MOD/$ORIGINE/{n} memoria/")
    return "\n".join(righe)


def scrivi(nome, celle):
    USCITA.mkdir(parents=True, exist_ok=True)
    quaderno = {
        "cells": celle,
        "metadata": {
            "colab": {"provenance": [], "name": nome},
            "kernelspec": {"display_name": "Python 3", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }
    (USCITA / nome).write_text(
        json.dumps(quaderno, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("scritto", nome, len(celle), "celle")


def cella_setup(pip):
    return codice(SETUP % {"repo": REPO, "pip": pip})


def pagina(slug, num):
    base = "https://corso-rag.giuseppebosi.com"
    return (f"{base}/moduli/{slug}/LAB/", f"{base}/en/moduli/{slug}/LAB/")


def inizio(num, slug, titolo_it, titolo_en, pip, chiave=True):
    u_it, u_en = pagina(slug, num)
    celle = [md(f"# Laboratorio {num}: {titolo_it}", f"# Lab {num}: {titolo_en}"),
             md(INTESTAZIONE[0].format(url_it=u_it, url_en=u_en),
                INTESTAZIONE[1].format(url_it=u_it, url_en=u_en)),
             cella_setup(pip)]
    if chiave:
        celle += [md(*TESTA_CHIAVE), codice(CHIAVE), md(*SENZA_CHIAVE)]
    return celle


GW_INSTALL = """
!python -m venv .venv-gateway
!.venv-gateway/bin/pip install -q -r requirements-gateway.txt
!mkdir -p memoria/gateway
!cp moduli/02-chiavi-gateway-e-quote/starter/config.yaml memoria/gateway/
"""

GW_AVVIO = """
import subprocess, time, os
GATEWAY = subprocess.Popen(
    [".venv-gateway/bin/litellm", "--config", "memoria/gateway/config.yaml",
     "--host", "127.0.0.1", "--port", "4000"],
    stdout=open("gateway.log", "w"), stderr=subprocess.STDOUT, env=dict(os.environ))
for _ in range(180):
    time.sleep(2)
    if "Uvicorn running on http://127.0.0.1:4000" in open("gateway.log").read():
        print("Gateway acceso su http://127.0.0.1:4000 / gateway is up")
        break
else:
    print(open("gateway.log").read()[-1500:])
"""

ENV_GATEWAY = """
# Come nel laboratorio 5: cognee parla col gateway locale / as in lab 5: cognee talks to the local gateway
os.environ.update(
    LLM_PROVIDER="custom", LLM_ENDPOINT="http://localhost:4000/v1",
    LLM_MODEL="openai/memoria-veloce", LLM_API_KEY="sk-memoria-locale")
"""


def celle_gateway():
    return [
        md("## Il gateway\n\nCome nel laboratorio 2, il gateway gira come processo di sfondo, in un ambiente virtuale suo, sul solo indirizzo "
           "`127.0.0.1`. L'installazione richiede un paio di minuti.",
           "## The gateway\n\nAs in lab 2, the gateway runs as a background process in its own virtual environment, on "
           "`127.0.0.1` only. Installing takes a couple of minutes."),
        codice(GW_INSTALL), codice(GW_AVVIO), codice(ENV_GATEWAY),
    ]


PIP_LEGGERO = "!pip install -q openai python-dotenv httpx PyYAML pypdf"
PIP_RICERCA = "!pip install -q openai python-dotenv httpx PyYAML pypdf fastembed numpy transformers"
PIP_COGNEE = "!pip install -q -r requirements.txt"

C = "progetto-finale/corpus"
TUTTI = f"{C}/manuali/*.md {C}/note/*.md"


def lab1():
    m = "01-perche-serve-una-memoria"
    c = inizio(1, m, "Il RAG in trenta righe", "RAG in thirty lines", PIP_LEGGERO)
    c += [
        md("## Passo 0: la cartella del tuo sistema", "## Step 0: the folder of your system"),
        md(*SOLUZIONE),
        codice(copia_file(m, ["llm.py", "memoria_minima.py"])),
        md("Controlla il collegamento col modello **[serve la chiave]**. Deve stampare `pronto`.",
           "Check the link to the model **[needs the key]**. It must print `pronto`."),
        codice("!python memoria/llm.py"),
        md("## Passo 1: misura il problema\n\nSul corpus del corso sono circa 4.400 token.",
           "## Step 1: measure the problem\n\nOn the course corpus it is about 4,400 tokens."),
        codice(f"!python moduli/{m}/starter/conta_token.py {TUTTI}"),
        md("## Passo 2: `cerca()`\n\nSenza chiamare il modello. Risultato atteso: `manuali/greencut-rm46.md` e "
           "`note/2026-07-21-rasaerba-non-parte.md`, entrambi con 2 punti.",
           "## Step 2: `cerca()`\n\nWithout calling the model. Expected: `manuali/greencut-rm46.md` and "
           "`note/2026-07-21-rasaerba-non-parte.md`, both with 2 points."),
        codice('''
import sys; sys.path.insert(0, "memoria")
from memoria_minima import carica_documenti, cerca
for d in cerca("Che candela monta il rasaerba?", carica_documenti()):
    print(d["punteggio"], d["nome"])
'''),
        md("## Passo 4: provalo **[serve la chiave]**\n\nPrima l'elenco dei documenti usati, poi una risposta che cita 0,8 bar "
           "e il ripristino a 1,2 bar.",
           "## Step 4: try it **[needs the key]**\n\nFirst the list of documents used, then an answer that cites 0.8 bar "
           "and the reset to 1.2 bar."),
        codice('!python memoria/memoria_minima.py "Cosa significa l\'errore E4 sulla caldaia Termovex?"'),
        md("## Passo 5: rompilo\n\nGuarda l'**elenco dei documenti usati**, non la risposta. La prima domanda mette al primo "
           "posto la nota sui freni della bici, la seconda una nota sulla lavatrice, la terza tre documenti a pari punteggio.",
           "## Step 5: break it\n\nLook at the **list of documents used**, not the answer. The first question ranks the bike-brake "
           "note first, the second a washing-machine note, the third three documents with equal scores."),
        codice('''
!python memoria/memoria_minima.py "Quanto devo stringere la vite che tiene la lama?"
!python memoria/memoria_minima.py "Perche' il trapano avvitatore si scarica subito?"
!python memoria/memoria_minima.py "Il tagliaerba non si accende, cosa devo controllare?"
'''),
        md("## Passo 6: verifica **[serve la chiave]**\n\nDeve stampare `OK` su tutte le righe.",
           "## Step 6: check **[needs the key]**\n\nIt must print `OK` on every line."),
        codice(f"!python moduli/{m}/verifica.py"),
    ]
    scrivi("lab01-rag-in-trenta-righe.ipynb", c)


def lab2():
    m = "02-chiavi-gateway-e-quote"
    c = inizio(2, m, "Il gateway e il conto dei token", "The gateway and the token count", PIP_LEGGERO)
    c += [
        md("## Passo 1: installa e avvia il gateway\n\nIn Colab il gateway gira in un processo di sfondo, "
           "in un ambiente virtuale suo (come spiega la lezione). L'installazione richiede un paio di minuti.",
           "## Step 1: install and start the gateway\n\nIn Colab the gateway runs as a background process in "
           "its own virtual environment (as the lesson explains). Installing takes a couple of minutes."),
        codice(GW_INSTALL),
        md("Avvio del gateway sul solo indirizzo `127.0.0.1` (non togliere `--host`). Il processo resta acceso "
           "finche' non lo fermi con l'ultima cella.",
           "Start the gateway on `127.0.0.1` only (do not drop `--host`). The process stays on until you stop it "
           "in the last cell."),
        codice(GW_AVVIO),
        md("Prova **[serve la chiave]**: deve tornare un JSON con `\"content\":\"pronto\"` o simile. Con `max_tokens` a 200 e non a 5: "
           "i modelli `gpt-oss` ragionano prima di rispondere.",
           "Try it **[needs the key]**: it must return JSON with `\"content\":\"pronto\"` or similar. `max_tokens` is 200, not 5: "
           "`gpt-oss` models reason before answering."),
        codice('''
!curl -s http://localhost:4000/v1/chat/completions \\
  -H "Authorization: Bearer sk-memoria-locale" \\
  -H "Content-Type: application/json" \\
  -d '{"model":"memoria-veloce","messages":[{"role":"user","content":"Rispondi solo: pronto"}],"max_tokens":200}' | head -c 400
'''),
        md("## Passo 2: fai passare il tuo sistema dal gateway\n\nIn Colab non serve modificare `.env`: si impostano le variabili "
           "d'ambiente. Poi si rilancia il sistema del modulo 1, senza toccare il codice.",
           "## Step 2: send your system through the gateway\n\nIn Colab you do not need to edit `.env`: set the environment "
           "variables. Then rerun the module 1 system without changing any code."),
        codice('''
os.environ.update(LLM_PROVIDER="custom", LLM_ENDPOINT="http://localhost:4000/v1",
                  LLM_MODEL="memoria-veloce", LLM_API_KEY="sk-memoria-locale")
!python memoria/memoria_minima.py "Cosa significa l'errore E4 sulla caldaia Termovex?"
'''),
        md("## Passo 4: `stima()`\n\nSul corpus del corso deve dare esattamente 12 documenti, 17036 caratteri, 22 pezzi, 44 chiamate, "
           "tempo minimo 2.1 minuti. Non chiama il modello.",
           "## Step 4: `stima()`\n\nOn the course corpus it must give exactly 12 documents, 17036 characters, 22 chunks, 44 calls, "
           "minimum time 2.1 minutes. It does not call the model."),
        md(*SOLUZIONE),
        codice(copia_file(m, ["stima_quota.py"])),
        codice(f"!python memoria/stima_quota.py {TUTTI}"),
        md("## Passo 5: output strutturato **[serve la chiave]**\n\nUn JSON con apparecchio, componente, azione, data e i valori.",
           "## Step 5: structured output **[needs the key]**\n\nJSON with appliance, component, action, date and values."),
        codice(f"!python moduli/{m}/starter/estrai_json.py {C}/note/2026-08-30-caldaia-manutenzione.md"),
        md("## Controlla le chiavi **[serve la chiave]**\n\nProva ogni chiave presente e mostra la quota che resta.",
           "## Check the keys **[needs the key]**\n\nTries every key present and shows the remaining quota."),
        codice(f"!python moduli/{m}/starter/controlla_chiavi.py"),
        md("## Passo 6: verifica\n\nIl gateway deve essere acceso (la cella di avvio sopra).",
           "## Step 6: check\n\nThe gateway must be running (the start cell above)."),
        codice(f"!python moduli/{m}/verifica.py"),
        md("## Fine: ferma il gateway", "## Done: stop the gateway"),
        codice("GATEWAY.terminate(); print('gateway fermato / gateway stopped')"),
    ]
    scrivi("lab02-gateway-e-token.ipynb", c)


def lab3():
    m = "03-testo-cercabile"
    c = inizio(3, m, "Spezzare, cercare, misurare", "Split, search, measure", PIP_RICERCA, chiave=False)
    c += [
        md("Questo laboratorio **non chiama mai il modello**: non serve nessuna chiave. La prima esecuzione della ricerca "
           "semantica scarica circa 220 MB di modello (un paio di minuti, una volta sola).",
           "This lab **never calls the model**: no key needed. The first run of semantic search downloads about 220 MB "
           "of model (a couple of minutes, once)."),
        md(*SOLUZIONE),
        codice(copia_file(m, ["pezzi.py", "lessicale.py", "semantica.py", "ibrida.py"])),
        md("## Passo 1: spezzare\n\nDeve dare 6 pezzi alla cieca, 8 per titoli, e `48 pezzi da 12 documenti`.",
           "## Step 1: splitting\n\nIt must give 6 chunks blind, 8 by headings, and `48 pezzi da 12 documenti`."),
        codice(f'''
!python memoria/pezzi.py {C}/manuali/termovex-tx24.md --cieco
!python memoria/pezzi.py {C}/manuali/termovex-tx24.md
!python memoria/pezzi.py
'''),
        md("## Passo 2: BM25\n\nIl primo risultato deve venire da `manuali/greencut-rm46.md`. L'idf di `bpr6es` deve essere molto piu' grande di quello di `il`.",
           "## Step 2: BM25\n\nThe first result must come from `manuali/greencut-rm46.md`. The idf of `bpr6es` must be much larger than that of `il`."),
        codice('''
import sys; sys.path.insert(0, "memoria")
from pezzi import carica_pezzi
from lessicale import Bm25
motore = Bm25(carica_pezzi())
for p in motore.cerca("Con che coppia si stringe il bullone della lama?"):
    print(round(p["punteggio"], 2), p["id"])
print("idf bpr6es:", round(motore.idf("bpr6es"), 3), " idf il:", round(motore.idf("il"), 3))
'''),
        md("## Passo 3: embedding e coseno\n\nLe due frasi senza parole in comune devono risultare molto piu' simili fra loro che alla terza.",
           "## Step 3: embeddings and cosine\n\nThe two sentences with no words in common must be far more similar to each other than to the third."),
        codice('''
from semantica import vettori, similitudine_coseno
v = vettori(["il rasaerba non parte", "il tagliaerba non si avvia", "la caldaia va in errore E4"])
print("rasaerba vs tagliaerba:", round(float(similitudine_coseno(v[0], v[1:2])[0]), 3))
print("rasaerba vs caldaia:   ", round(float(similitudine_coseno(v[0], v[2:3])[0]), 3))
'''),
        codice('''
from semantica import Semantica
for p in Semantica(carica_pezzi()).cerca("Il tagliaerba non si accende"):
    print(round(p["punteggio"], 3), p["id"])
'''),
        md("## Passo 5: misurare\n\nQuesta e' la tabella da ottenere esattamente:\n\n"
           "```text\nmetodo        primi 1  primi 3  primi 5\nBM25            4/10     8/10    10/10\n"
           "semantica       5/10     7/10     8/10\nibrida          4/10     8/10    10/10\n-- unione       7/10    10/10    10/10\n```",
           "## Step 5: measure\n\nThis is the table you must get exactly:\n\n"
           "```text\nmetodo        primi 1  primi 3  primi 5\nBM25            4/10     8/10    10/10\n"
           "semantica       5/10     7/10     8/10\nibrida          4/10     8/10    10/10\n-- unione       7/10    10/10    10/10\n```"),
        codice(f"!python moduli/{m}/starter/confronta.py"),
        md("## Passo 7: verifica", "## Step 7: check"),
        codice(f"!python moduli/{m}/verifica.py"),
    ]
    scrivi("lab03-spezzare-cercare-misurare.ipynb", c)


def lab4():
    m = "04-dal-recupero-al-grafo"
    c = inizio(4, m, "Costruisci un grafo a mano", "Build a graph by hand", PIP_RICERCA)
    c += [
        md("Costo in quota: circa 30.000 token per costruire tutto il grafo, cioe' quattro o cinque minuti di lavoro "
           "piu' le attese. La cella di costruzione e' l'unica costosa.",
           "Quota cost: about 30,000 tokens to build the whole graph, i.e. four or five minutes of work plus waiting. "
           "The build cell is the only expensive one."),
        md(*SOLUZIONE),
        md("## Passo 1: vedi il fallimento **[serve la chiave]**\n\nGuarda quali pezzi recupera: nessuno parla della caldaia.",
           "## Step 1: see the failure **[needs the key]**\n\nLook at which chunks it retrieves: none mentions the boiler."),
        codice("""
USA_SOLUZIONE = True
MOD = "moduli/04-dal-recupero-al-grafo"
ORIGINE = "soluzione" if USA_SOLUZIONE else "starter"
!python $MOD/starter/prova_multihop.py
"""),
        md("## Passo 2: la pazienza\n\nDeve stampare `2.375` e `8`.",
           "## Step 2: patience\n\nIt must print `2.375` and `8`."),
        codice("!cp $MOD/$ORIGINE/pazienza.py memoria/\n!cp $MOD/$ORIGINE/grafo.py memoria/"),
        codice('''
import sys; sys.path.insert(0, "memoria")
from pazienza import secondi_da_aspettare
class Finto(Exception): pass
print(secondi_da_aspettare(Finto("Rate limit reached. Please try again in 1.875s"), 0))
print(secondi_da_aspettare(Finto("errore generico"), 3))
'''),
        md("## Passo 3: l'estrazione **[serve la chiave]**\n\nPrima su un solo documento (una chiamata): entita' con `nome` e `tipo`, relazioni `da / relazione / a`.",
           "## Step 3: extraction **[needs the key]**\n\nFirst on a single document (one call): entities with `nome` and `tipo`, relations `da / relazione / a`."),
        codice('''
import json
from grafo import estrai
from pathlib import Path
t = Path("progetto-finale/corpus/note/2026-03-12-caldaia-e4.md").read_text()
print(json.dumps(estrai(t), indent=2, ensure_ascii=False))
'''),
        md("Poi tutto il corpus **[serve la chiave]**: una riga per documento, e `quota esaurita, aspetto ...` quando serve. Scrive `dati/grafo.json`.",
           "Then the whole corpus **[needs the key]**: one line per document, and `quota esaurita, aspetto ...` when needed. Writes `dati/grafo.json`."),
        codice("!python memoria/grafo.py costruisci"),
        md("## Passo 4: la visita\n\nIl numero di relazioni deve crescere da 1 a 2 salti e poco da 2 a 3.",
           "## Step 4: the traversal\n\nThe number of relations must grow from 1 to 2 hops and barely from 2 to 3."),
        codice('''
!python memoria/grafo.py mostra "caldaia"
from grafo import carica, vicini, trova_nodo
g = carica()
n = trova_nodo(g, "caldaia termovex")
for s in (1, 2, 3):
    print(s, "salti ->", len(vicini(g, n, salti=s)), "relazioni")
'''),
        md("## Passo 5: la risposta impossibile **[serve la chiave]**\n\nDeve rispondere **3,5 ore**, con gli addendi 1,5 e 2.",
           "## Step 5: the impossible answer **[needs the key]**\n\nIt must answer **3.5 hours**, showing the addends 1.5 and 2."),
        codice('''
!python memoria/grafo.py chiedi "Quante ore ho passato in tutto sulla caldaia?"
!python memoria/grafo.py chiedi "Che pressione hanno le gomme della bici?"
'''),
        md("## Passo 6: rompi il grafo apposta\n\nCerca i nodi duplicati. Il tuo risultato puo' essere diverso dal nostro, ma qualche duplicato lo trovi.",
           "## Step 6: break the graph on purpose\n\nLook for duplicate nodes. Your result may differ from ours, but you will find some duplicates."),
        codice('''
g = json.load(open("dati/grafo.json"))
for parola in ["caldaia", "lavatrice", "rasaerba", "bici"]:
    print(parola, "->", [e["nome"] for e in g["entita"] if parola in e["nome"].lower()])
'''),
        md("## Passo 7: verifica", "## Step 7: check"),
        codice("!python $MOD/verifica.py"),
    ]
    scrivi("lab04-grafo-a-mano.ipynb", c)


def lab5():
    m = "05-la-pipeline-di-cognee"
    c = inizio(5, m, "Il quaderno, con cognee sotto", "The notebook, with cognee underneath", PIP_COGNEE)
    c += [
        md("**Avvertenza onesta.** Questo laboratorio installa cognee (circa 1,5 GB) e `cognify` consuma circa 50.000 token. "
           "In Colab il gateway del modulo 2 gira come processo di sfondo (celle qui sotto). Con il solo piano gratuito Groq "
           "il `digerisci` completo e' lento e puo' fermarsi per la quota del minuto: e' normale, vedi la lezione. "
           "Il PDF scansionato del rasaerba resta una pagina bianca: e' voluto.",
           "**A fair warning.** This lab installs cognee (about 1.5 GB) and `cognify` uses about 50,000 tokens. In Colab it "
           "runs **without the gateway**: the module 2 gateway runs as a background process (cells below). On the free Groq plan the full "
           "`digerisci` (digest) step is slow and can stop on the per-minute quota: that is normal, see the lesson. "
           "The scanned lawn-mower PDF stays a blank page on purpose."),
        *celle_gateway(),
        codice("!python -c \"import cognee; print('cognee', cognee.get_cognee_version())\""),
        md("## Passo 1: il giro su una nota sola **[serve la chiave]**\n\nSe finisce con una risposta che cita sia 0,8 bar sia il vaso di espansione, la pipeline funziona.",
           "## Step 1: one note end to end **[needs the key]**\n\nIf it ends with an answer citing both 0.8 bar and the expansion vessel, the pipeline works."),
        codice(f"!python moduli/{m}/starter/primo_giro.py"),
        md(*SOLUZIONE),
        codice(copia_file(m, ["quaderno.py"])),
        md("## Passo 2: dove finiranno i dati\n\nDeve dire `dati/cognee`, non una cartella dentro `.venv`.",
           "## Step 2: where the data will go\n\nIt must say `dati/cognee`, not a folder inside `.venv`."),
        codice("!python memoria/quaderno.py stato"),
        md("## Passo 3: digerisci il corpus **[serve la chiave]**\n\nPuo' richiedere decine di minuti. Con `--ridotto` ingerisci solo caldaia e lavatrice (6 documenti).",
           "## Step 3: digest the corpus **[needs the key]**\n\nIt can take tens of minutes. With `--ridotto` it ingests only the boiler and washer (6 documents)."),
        codice('''
!python memoria/quaderno.py azzera
!python memoria/quaderno.py aggiungi --ridotto
!python memoria/quaderno.py digerisci
'''),
        md("Il PDF scansionato non ha testo: deve stampare `0`.", "The scanned PDF has no text: it must print `0`."),
        codice('''
import pypdf
print(len(pypdf.PdfReader("progetto-finale/corpus/manuali/greencut-rm46.pdf").pages[0].extract_text()))
'''),
        md("## Passo 4: chiedi **[serve la chiave]**", "## Step 4: ask **[needs the key]**"),
        codice('''
!python memoria/quaderno.py chiedi "Cosa significa l'errore E4 sulla caldaia?"
!python memoria/quaderno.py chiedi --pezzi "Quante ore ho passato sulla caldaia?"
'''),
        md("## Passo 6: dove abita l'archivio\n\nTre database, tre tecnologie: SQLite, Kuzu, LanceDB.",
           "## Step 6: where the archive lives\n\nThree databases, three technologies: SQLite, Kuzu, LanceDB."),
        codice("!python memoria/quaderno.py stato\n!ls -la dati/cognee/sistema/databases/"),
    ]
    scrivi("lab05-quaderno-cognee.ipynb", c)


def lab6():
    m = "06-dove-vive-il-dato"
    c = inizio(6, m, "Aprire la scatola e cambiare il motore", "Open the box and swap the engine", PIP_COGNEE)
    c += [
        md("**Cosa si puo' fare in Colab.** Colab non ha Docker, quindi i passi 2, 3, 4 e 6 (PostgreSQL con pgvector in un "
           "contenitore) si fanno sul tuo computer, come descrive il laboratorio. Qui provi la parte che non richiede Docker: "
           "ispezionare SQLite, i vettori e il grafo Kuzu (passo 1) e il trucco del file `.pkl` che e' in realta' un database Kuzu. "
           "Serve l'archivio del modulo 5: se non l'hai fatto in questa sessione, la cella di preparazione lo costruisce in formato ridotto **[serve la chiave]**.",
           "**What you can do in Colab.** Colab has no Docker, so steps 2, 3, 4 and 6 (PostgreSQL with pgvector in a container) "
           "are done on your own computer, as the lab describes. Here you try the part that needs no Docker: inspecting SQLite, "
           "the vectors and the Kuzu graph (step 1), and the trick of the `.pkl` file that is really a Kuzu database. "
           "It needs the module 5 archive: if you have not built it in this session, the preparation cell builds a reduced one **[needs the key]**."),
        *celle_gateway(),
        codice('''
!mkdir -p dati
if not os.path.isdir("dati/cognee"):
    !python memoria/quaderno.py aggiungi --ridotto
    !python memoria/quaderno.py digerisci
'''),
        md(*SOLUZIONE),
        codice(copia_file(m, ["ispeziona.py"])),
        md("## Passo 1: guarda cosa c'e' adesso\n\nLe tabelle di SQLite (`data` ha una riga per documento), i vettori, il grafo.",
           "## Step 1: look at what is there now\n\nThe SQLite tables (`data` has one row per document), the vectors, the graph."),
        codice('''
!python memoria/ispeziona.py relazionale
!python memoria/ispeziona.py vettori
!python memoria/ispeziona.py grafo
!ls -la dati/cognee/sistema/databases/*/
'''),
        md("Il `.pkl` sembra un file Python serializzato, ma e' un database Kuzu: aprilo.",
           "The `.pkl` looks like a serialized Python file, but it is a Kuzu database: open it."),
        codice('''
import kuzu, pathlib
p = next(pathlib.Path("dati/cognee/sistema/databases").rglob("*.pkl"))
c = kuzu.Connection(kuzu.Database(str(p)))
r = c.execute("MATCH (n) RETURN count(*)")
print(p.name, "->", r.get_next()[0], "nodi")
'''),
        md("## Passi 2-7 sul tuo computer\n\nPostgreSQL con pgvector, la migrazione, il backup con `pg_dump` e la verifica richiedono Docker: "
           "segui il [laboratorio 6](https://corso-rag.giuseppebosi.com/moduli/06-dove-vive-il-dato/LAB/) dal tuo computer.",
           "## Steps 2-7 on your own computer\n\nPostgreSQL with pgvector, the migration, the `pg_dump` backup and the check need Docker: "
           "follow [lab 6](https://corso-rag.giuseppebosi.com/en/moduli/06-dove-vive-il-dato/LAB/) on your own computer."),
    ]
    scrivi("lab06-dove-vive-il-dato.ipynb", c)


def lab7():
    m = "07-manutenzione-della-memoria"
    c = inizio(7, m, "Tenere viva la memoria", "Keeping the memory alive", PIP_COGNEE)
    c += [
        md("Serve l'archivio digerito del modulo 5. Se non l'hai in questa sessione, la cella di preparazione ne costruisce uno ridotto "
           "**[serve la chiave]**.",
           "It needs the digested module 5 archive. If you do not have it in this session, the preparation cell builds a reduced one "
           "**[needs the key]**."),
        *celle_gateway(),
        codice('''
!mkdir -p dati
if not os.path.isdir("dati/cognee"):
    !python memoria/quaderno.py aggiungi
    !python memoria/quaderno.py digerisci
'''),
        md(*SOLUZIONE),
        codice(copia_file(m, ["manutenzione.py"])),
        md("## Esercizio 1: riproduci il fallimento **[serve la chiave]**\n\nIl libretto dice 1,2 bar, la nota del 30 agosto 1,4.",
           "## Exercise 1: reproduce the failure **[needs the key]**\n\nThe manual says 1.2 bar, the 30 August note says 1.4."),
        codice('''
!python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia Termovex?"
!python memoria/quaderno.py chiedi --pezzi "pressione impianto Termovex"
'''),
        md("## Esercizio 2: aggiungere senza rifare tutto **[serve la chiave]**",
           "## Exercise 2: add without redoing everything **[needs the key]**"),
        codice('''
nota = """# Intervento del 15 settembre 2026 — Caldaia Termovex TX-24, via Mazzini 8

Controllo stagionale. Pressione a freddo trovata a 1,35 bar, dentro
tolleranza, non toccata. Pulito lo scambiatore. Sostituito il ricambio
7832-VE8 (vaso di espansione) perche' la precarica era scesa a 0,6 bar.
Tempo: 2,5 ore.
"""
open("dati/nota-nuova.md", "w", encoding="utf-8").write(nota)
!time python memoria/manutenzione.py aggiungi dati/nota-nuova.md
!python memoria/quaderno.py chiedi "Quando ho sostituito il vaso di espansione della Termovex?"
'''),
        md("## Esercizio 3: elencare quello che c'e' dentro\n\nI documenti con il loro identificativo.",
           "## Exercise 3: list what is inside\n\nThe documents with their identifiers."),
        codice("!python memoria/manutenzione.py elenca"),
        md("## Esercizio 4: la nota di rettifica **[serve la chiave]**\n\nAdesso deve dire **1,4 bar**.",
           "## Exercise 4: the correction note **[needs the key]**\n\nNow it must say **1.4 bar**."),
        codice('''
!cp moduli/07-manutenzione-della-memoria/soluzione/rettifica-pressione.md dati/
!python memoria/manutenzione.py aggiungi dati/rettifica-pressione.md
!python memoria/quaderno.py chiedi "A che pressione devo tenere l'impianto della caldaia Termovex?"
'''),
        md("## Esercizi 5, 6, 7: dimenticare, relazione, backup",
           "## Exercises 5, 6, 7: forget, report, backup"),
        codice('''
!python memoria/manutenzione.py relazione
!python memoria/manutenzione.py salva dati/backup
!ls -la dati/backup/
'''),
        md("Per `dimentica` serve l'identificativo mostrato da `elenca`: `!python memoria/manutenzione.py dimentica ID_DEL_DOCUMENTO`.",
           "`dimentica` needs the identifier shown by `elenca`: `!python memoria/manutenzione.py dimentica DOCUMENT_ID`."),
        md("## Verifica", "## Check"),
        codice("!python moduli/07-manutenzione-della-memoria/verifica.py"),
    ]
    scrivi("lab07-manutenzione.ipynb", c)


def lab8():
    m = "08-valutare-il-sistema"
    c = inizio(8, m, "Costruire il metro", "Building the yardstick", PIP_COGNEE)
    c += [
        md("Serve l'archivio **completo** (12 documenti). Il giro di 12 domande con la pausa di 30 secondi dura sei-sette minuti. "
           "Il gateway del modulo 2 gira come processo di sfondo (celle qui sotto).",
           "It needs the **complete** archive (12 documents). The round of 12 questions with the 30 s pause takes six or seven minutes. "
           "The module 2 gateway runs as a background process (cells below)."),
        *celle_gateway(),
        codice('''
!mkdir -p dati
if not os.path.isdir("dati/cognee"):
    !python memoria/quaderno.py aggiungi
    !python memoria/quaderno.py digerisci
'''),
        md(*SOLUZIONE),
        codice(copia_file(m, ["valuta.py"])),
        md("## Esercizio 1: l'insieme di valutazione\n\nDodici domande. Prima di lanciare, scrivi la tua previsione: passa o non passa?",
           "## Exercise 1: the evaluation set\n\nTwelve questions. Before running, write your prediction: pass or fail?"),
        codice("!cat progetto-finale/domande.yaml"),
        md("## Esercizi 2-5: il giro completo **[serve la chiave]**\n\nAlla fine un riassunto per tipo di domanda e un file in `dati/valutazioni/`.",
           "## Exercises 2-5: the full round **[needs the key]**\n\nAt the end a summary by question type and a file in `dati/valutazioni/`."),
        codice("!python memoria/valuta.py"),
        md("Il manuale del rasaerba e' un PDF scansionato: senza OCR non contiene caratteri leggibili. Deve stampare `0`.",
           "The lawn-mower manual is a scanned PDF: without OCR it holds no readable characters. It must print `0`."),
        codice('''
import pypdf
print(len(pypdf.PdfReader("progetto-finale/corpus/manuali/greencut-rm46.pdf").pages[0].extract_text()))
'''),
        md("## Esercizio 6: misurare un cambiamento **[serve la chiave]**\n\nSolo recupero, senza grafo: confronta i due riassunti per tipo.",
           "## Exercise 6: measure a change **[needs the key]**\n\nRetrieval only, no graph: compare the two summaries by type."),
        codice("!python memoria/valuta.py --tipo testo"),
        md("## Verifica\n\nNon interroga il modello: giudica risposte finte.",
           "## Check\n\nIt does not call the model: it grades fake answers."),
        codice(f"!python moduli/{m}/verifica.py"),
    ]
    scrivi("lab08-valutare-il-sistema.ipynb", c)


if __name__ == "__main__":
    for f in (lab1, lab2, lab3, lab4, lab5, lab6, lab7, lab8):
        f()
