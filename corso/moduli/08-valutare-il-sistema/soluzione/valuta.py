#!/usr/bin/env python3
"""Il metro: fa all'archivio le domande di domande.yaml e conta.

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
    ammette = any(a in testo for a in AMMISSIONI)
    inventa = NUMERO_CON_UNITA.search(testo)

    if inventa:
        return False, f"ha inventato un valore: '{inventa.group(0)}'"
    if not ammette:
        return False, "non ammette di non sapere"
    return True, ""


# --- TODO 1 ----------------------------------------------------------
def giudica(risposta: str, domanda: dict) -> tuple[bool, str]:
    """Passa o non passa, e perche'."""
    testo = normalizza(risposta)

    if domanda.get("tipo") == "assente":
        return giudica_assente(testo)

    mancanti = [a for a in domanda.get("attese", [])
                if normalizza(a) not in testo]
    if mancanti:
        return False, "manca: " + ", ".join(mancanti)

    presenti = [v for v in domanda.get("vietate", [])
                if normalizza(v) in testo]
    if presenti:
        return False, "contiene il fatto vecchio: " + ", ".join(presenti)

    return True, ""


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
    esiti = []

    for indice, domanda in enumerate(domande):
        try:
            risposta = await interroga(domanda["domanda"], tipo)
        except Exception as errore:
            risposta = ""
            print(f"  {domanda['id']}: errore interrogando -> {errore}")

        passata, motivo = giudica(risposta, domanda)
        esiti.append({
            "id": domanda["id"],
            "tipo": domanda.get("tipo", "?"),
            "domanda": domanda["domanda"],
            "passata": passata,
            "motivo": motivo,
            "risposta": " ".join(risposta.split())[:300],
        })
        print(f"{'OK ' if passata else 'NO '} {domanda['id']} "
              f"[{domanda.get('tipo', '?')}] {domanda['domanda']}")
        if motivo:
            print(f"        {motivo}")

        if pausa and indice < len(domande) - 1:
            await asyncio.sleep(pausa)

    return esiti


def riassumi(esiti: list[dict]) -> list[tuple[str, int, int]]:
    """Una riga per tipo. Una media unica nasconde tutto."""
    tipi = {}
    for esito in esiti:
        passate, totale = tipi.get(esito["tipo"], (0, 0))
        tipi[esito["tipo"]] = (passate + int(esito["passata"]), totale + 1)
    return [(tipo, p, t) for tipo, (p, t) in tipi.items()]


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

    righe = [
        f"# Valutazione del {adesso:%Y-%m-%d %H:%M}",
        "",
        f"- modello:    {os.getenv('LLM_MODEL')} via {os.getenv('LLM_PROVIDER')}",
        f"- embedding:  {os.getenv('EMBEDDING_MODEL')} "
        f"({os.getenv('EMBEDDING_DIMENSIONS')})",
        f"- ricerca:    {tipo} ({TIPI_DI_RICERCA[tipo].name})",
        f"- archivio:   {ARCHIVIO}",
        "",
        "## Riassunto per tipo",
        "",
        "| tipo | passate |",
        "|---|---|",
    ]
    for nome, passate, totale in riassumi(esiti):
        righe.append(f"| {nome} | {passate}/{totale} |")
    passate = sum(e["passata"] for e in esiti)
    righe += [f"| **totale** | **{passate}/{len(esiti)}** |", "",
              "## Domanda per domanda", "",
              "| id | tipo | esito | motivo |", "|---|---|---|---|"]
    for esito in esiti:
        righe.append(f"| {esito['id']} | {esito['tipo']} | "
                     f"{'OK' if esito['passata'] else 'NO'} | "
                     f"{esito['motivo']} |")

    file.write_text("\n".join(righe) + "\n", encoding="utf-8")
    return file


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
