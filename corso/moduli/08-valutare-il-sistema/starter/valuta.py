#!/usr/bin/env python3
"""STARTER — Il metro: fa all'archivio le domande di domande.yaml e conta.

    python memoria/valuta.py                 # ricerca sul grafo
    python memoria/valuta.py --tipo testo    # solo recupero, per confronto
    python memoria/valuta.py --pausa 0       # se hai una quota generosa

Scrive il risultato in dati/valutazioni/, con in testa la configurazione
usata: un giro che non lasci scritto e' un giro buttato.
"""

import argparse
import asyncio
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv


def trova_radice() -> Path:
    for candidata in Path(__file__).resolve().parents:
        if (candidata / "progetto-finale" / "corpus").is_dir():
            return candidata
    raise SystemExit("lancia il comando dalla cartella del corso")


RADICE = trova_radice()
DOMANDE = RADICE / "progetto-finale" / "domande.yaml"
DATI = RADICE / "dati" / "cognee"
ARCHIVIO = "officina"

# 2 chiamate al minuto e' il budget del modulo 5: 8.000 token al minuto
# diviso i circa 3.000 token di una chiamata.
PAUSA = 30

load_dotenv(RADICE / ".env")

import cognee                                                    # noqa: E402
from cognee.modules.search.types.SearchType import SearchType     # noqa: E402

cognee.config.system_root_directory(str(DATI / "sistema"))
cognee.config.data_root_directory(str(DATI / "documenti"))

TIPI_DI_RICERCA = {
    "grafo": SearchType.GRAPH_COMPLETION,
    "testo": SearchType.RAG_COMPLETION,
    "misto": SearchType.HYBRID_COMPLETION,
}

# Modi di ammettere che non si sa. Il modello ne usa uno a caso.
AMMISSIONI = (
    "non lo so", "non trovo", "non e' presente", "non e' specificat",
    "non e' indicat", "non risulta", "non compare", "non ho trovato",
    "nessuna informazione", "non viene specificat", "non e' riportat",
    "non sono disponibili", "non ci sono informazioni",
)

# Un numero seguito da un'unita' di misura: se c'e', il modello ha
# tirato fuori un valore, comunque abbia girato la frase.
NUMERO_CON_UNITA = re.compile(
    r"\d+[.,]?\d*\s*(bar|psi|atm|kpa|nm|ml|litri|l\b)"
)


def normalizza(testo: str) -> str:
    """Minuscolo, spazi compattati, virgola e punto decimale resi uguali.

    Il modello scrive "1.4" o "1,4" a seconda dell'umore, e gli accenti
    a volte li mangia. Non e' quello che stai misurando.
    """
    testo = testo.lower()
    testo = testo.replace("à", "a'").replace("è", "e'").replace("é", "e'")
    testo = testo.replace("ì", "i'").replace("ò", "o'").replace("ù", "u'")
    testo = re.sub(r"(\d)[.,](\d)", r"\1,\2", testo)
    return re.sub(r"\s+", " ", testo)


# --- TODO 2 ----------------------------------------------------------
def giudica_assente(testo: str) -> tuple[bool, str]:
    """La regola speciale per le domande senza risposta.

    Due condizioni, tutte e due necessarie: c'e' un'ammissione di
    ignoranza, e non c'e' un numero con unita' di misura.
    """
    # TODO 2: due condizioni, tutte e due necessarie.
    #   - il testo contiene una delle AMMISSIONI
    #   - il testo NON contiene un NUMERO_CON_UNITA
    # Restituisci (True, "") oppure (False, "motivo").
    raise NotImplementedError("TODO 2")


# --- TODO 1 ----------------------------------------------------------
def giudica(risposta: str, domanda: dict) -> tuple[bool, str]:
    """Passa o non passa, e perche'."""
    testo = normalizza(risposta)

    # TODO 1:
    #   - se domanda["tipo"] e' "assente", delega a giudica_assente
    #   - tutte le "attese" devono comparire in testo (normalizzate!)
    #   - nessuna delle "vietate" deve comparire
    # Il secondo controllo e' quello che manca nelle valutazioni fatte
    # male: "1,2 bar, poi portata a 1,4" contiene la parola giusta ed e'
    # una risposta che in officina ti fa sbagliare il lavoro.
    raise NotImplementedError("TODO 1")


async def interroga(testo: str, tipo: str) -> str:
    risultati = await cognee.search(
        query_text=testo,
        query_type=TIPI_DI_RICERCA[tipo],
        datasets=[ARCHIVIO],
    )
    pezzi = []
    for risultato in risultati or []:
        if isinstance(risultato, dict) and "search_result" in risultato:
            pezzi.extend(str(v) for v in risultato["search_result"])
        else:
            pezzi.append(str(risultato))
    return "\n".join(pezzi)


# --- TODO 3 + TODO 4 -------------------------------------------------
async def giro(tipo: str, pausa: int) -> list[dict]:
    domande = yaml.safe_load(DOMANDE.read_text(encoding="utf-8"))

    # TODO 3: per ogni domanda
    #   risposta = await interroga(domanda["domanda"], tipo)
    #   passata, motivo = giudica(risposta, domanda)
    #   stampa, accumula in una lista di dizionari con le chiavi
    #     id, tipo, domanda, passata, motivo, risposta
    #   e await asyncio.sleep(pausa) fra una e l'altra.
    # La pausa non e' prudenza: senza, le prime domande partono a
    # raffica, prendi 429 e il giro dura di piu'.
    raise NotImplementedError("TODO 3")


def riassumi(esiti: list[dict]) -> list[tuple[str, int, int]]:
    """Una riga per tipo. Una media unica nasconde tutto."""
    # TODO 4: raggruppa per esito["tipo"] e restituisci una lista di
    # tuple (tipo, passate, totale). Una media unica nasconde tutto:
    # da 8/12 a 9/12 non impari niente, da "0/2 ocr" a "2/2 ocr" si'.
    raise NotImplementedError("TODO 4")


def stampa_riassunto(esiti: list[dict]) -> None:
    print("\ntipo          passate")
    for tipo, passate, totale in riassumi(esiti):
        print(f"{tipo:<14}{passate:>3}/{totale}")
    print("-" * 20)
    passate = sum(e["passata"] for e in esiti)
    print(f"{'totale':<14}{passate:>3}/{len(esiti)}")


# --- TODO 5 ----------------------------------------------------------
def scrivi(esiti: list[dict], tipo: str) -> Path:
    """Senza la configurazione in testa, fra un mese hai un numero
    e nessun modo di sapere a cosa si riferiva."""
    adesso = datetime.now()
    cartella = RADICE / "dati" / "valutazioni"
    cartella.mkdir(parents=True, exist_ok=True)
    file = cartella / f"{adesso:%Y-%m-%d-%H%M}.md"

    # TODO 5: scrivi in `file` un Markdown con, IN TESTA, la
    # configurazione usata (LLM_MODEL, EMBEDDING_MODEL, tipo di
    # ricerca), poi il riassunto per tipo, poi la tabella domanda per
    # domanda. Senza la configurazione in testa, fra un mese hai un
    # numero e nessun modo di sapere a cosa si riferiva.
    raise NotImplementedError("TODO 5")


def main() -> None:
    lettore = argparse.ArgumentParser()
    lettore.add_argument("--tipo", default="grafo", choices=list(TIPI_DI_RICERCA))
    lettore.add_argument("--pausa", type=int, default=PAUSA,
                         help="secondi fra una domanda e l'altra")
    argomenti = lettore.parse_args()

    if not DOMANDE.is_file():
        raise SystemExit(f"non trovo {DOMANDE}")

    print(f"ricerca: {argomenti.tipo}, pausa {argomenti.pausa}s\n")
    esiti = asyncio.run(giro(argomenti.tipo, argomenti.pausa))
    stampa_riassunto(esiti)
    print(f"\nscritto in {scrivi(esiti, argomenti.tipo)}")


if __name__ == "__main__":
    main()
