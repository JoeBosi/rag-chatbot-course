#!/usr/bin/env python3
"""Un grafo di entita' e relazioni, costruito a mano. Da completare.

    python memoria/grafo.py costruisci      # legge il corpus, chiama il
                                            # modello, scrive dati/grafo.json
    python memoria/grafo.py mostra "Caldaia Termovex TX-24"
    python memoria/grafo.py chiedi "Quante ore ho passato sulla caldaia?"

Nel modulo 5 tutto questo lo fara' cognee. Farlo una volta a mano serve a
sapere cosa c'e' dentro quando smettera' di funzionare.
"""

import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pazienza import con_pazienza      # noqa: E402


def trova_radice() -> Path:
    for candidata in Path(__file__).resolve().parents:
        if (candidata / "progetto-finale" / "corpus").is_dir():
            return candidata
    raise SystemExit("lancia il comando dalla cartella del corso")


RADICE = trova_radice()
CORPUS = RADICE / "progetto-finale" / "corpus"
GRAFO = RADICE / "dati" / "grafo.json"
load_dotenv(RADICE / ".env")

# I tipi di entita' che ci interessano. Elencarli serve: senza un elenco
# il modello inventa una tassonomia diversa per ogni documento, e il
# grafo non si collega piu'.
TIPI = ["apparecchio", "componente", "intervento", "ricambio",
        "sintomo", "misura", "persona", "data"]

SCHEMA = {
    "type": "object",
    "properties": {
        "entita": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string",
                             "description": "nome proprio e completo, "
                                            "sempre scritto allo stesso modo"},
                    "tipo": {"type": "string", "enum": TIPI},
                },
                "required": ["nome", "tipo"],
                "additionalProperties": False,
            },
        },
        "relazioni": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "da": {"type": "string"},
                    "relazione": {"type": "string",
                                  "description": "un verbo o poco piu': "
                                                 "riguarda, ha_componente, "
                                                 "e_durato, ha_sostituito, "
                                                 "ha_valore, avvenuto_il"},
                    "a": {"type": "string"},
                },
                "required": ["da", "relazione", "a"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["entita", "relazioni"],
    "additionalProperties": False,
}

ISTRUZIONI = """Estrai da questo documento le entita' e le relazioni.

Regole:
- usa sempre lo stesso nome per la stessa cosa (se il documento dice
  "la caldaia", scrivi "Caldaia Termovex TX-24");
- ogni intervento e' un'entita' di tipo "intervento", chiamata
  "Intervento del GG mese AAAA";
- collega ogni intervento all'apparecchio con la relazione "riguarda";
- se il documento dice quanto tempo e' stato impiegato, aggiungi una
  relazione "e_durato" verso una misura tipo "1,5 ore";
- non inventare: se una cosa non c'e' nel testo, non metterla."""


def cliente() -> OpenAI:
    return OpenAI(
        base_url=os.getenv("LLM_ENDPOINT", "https://api.groq.com/openai/v1"),
        api_key=os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY", ""),
        timeout=180,
    )


def estrai(testo: str) -> dict:
    """Chiede al modello entita' e relazioni, nella forma di SCHEMA.

    Passa da con_pazienza(): questo e' il primo comando del corso che fa
    una dozzina di chiamate di fila, ed e' matematicamente certo che
    prima o poi sbatta contro gli 8.000 token al minuto del piano
    gratuito.
    """
    risposta = con_pazienza(
        cliente().chat.completions.create,
        model=os.getenv("LLM_MODEL", "memoria-veloce"),
        messages=[{"role": "system", "content": ISTRUZIONI},
                  {"role": "user", "content": testo}],
        response_format={"type": "json_schema",
                         "json_schema": {"name": "grafo", "strict": True,
                                         "schema": SCHEMA}},
        temperature=0,
        max_tokens=3000,
    )
    return json.loads(risposta.choices[0].message.content)


def costruisci() -> dict:
    """Legge tutto il corpus e mette insieme un grafo solo.

    TODO 1 ----------------------------------------------------------------
    - scorri i .md del corpus (salta LEGGIMI.md);
    - per ognuno chiama estrai();
    - accumula le entita' in un dizionario nome -> {"nome", "tipo", "fonti"}
      (se la stessa entita' torna in piu' documenti, aggiungi la fonte);
    - accumula le relazioni in una lista di dizionari
      {"da", "relazione", "a", "fonte"};
    - stampa una riga per documento, cosi' si vede che sta lavorando;
    - restituisci {"entita": [...], "relazioni": [...]}.
    -----------------------------------------------------------------------
    """
    raise NotImplementedError("TODO 1: costruisci()")


def carica() -> dict:
    if not GRAFO.exists():
        sys.exit("Il grafo non c'e'. Prima: python memoria/grafo.py costruisci")
    return json.loads(GRAFO.read_text(encoding="utf-8"))


def vicini(grafo: dict, partenza: str, salti: int = 2) -> list[dict]:
    """Tutte le relazioni raggiungibili da `partenza` entro `salti` passi.

    TODO 2 ----------------------------------------------------------------
    E' una visita in ampiezza. Parti da un insieme che contiene solo
    `partenza`; a ogni salto, prendi tutte le relazioni che toccano un
    nodo gia' raggiunto (come "da" oppure come "a"), aggiungile al
    risultato, e aggiungi ai nodi raggiunti l'altro capo.
    Il confronto fra nomi va fatto senza distinguere maiuscole e
    minuscole. Non restituire due volte la stessa relazione.
    -----------------------------------------------------------------------
    """
    raise NotImplementedError("TODO 2: vicini()")


def trova_nodo(grafo: dict, testo: str) -> str | None:
    """Il nodo del grafo che somiglia di piu' a quello che ha scritto l'utente.

    Aggancio rozzo per parole. La punteggiatura va tolta: senza questa
    riga, "caldaia?" non corrisponde a "Caldaia Termovex TX-24" e il
    sistema risponde "non lo so" pur avendo il fatto in casa.
    """
    ripulito = re.sub(r"[^\w\s]", " ", testo.lower())
    parole = {parola for parola in ripulito.split() if len(parola) > 3}
    migliore, punteggio_migliore = None, 0
    for entita in grafo["entita"]:
        nome = entita["nome"].lower()
        punteggio = sum(1 for parola in parole if parola in nome)
        if punteggio > punteggio_migliore:
            migliore, punteggio_migliore = entita["nome"], punteggio
    return migliore


def chiedi_al_grafo(domanda: str) -> str:
    """Risponde usando il sottografo intorno all'entita' nominata."""
    grafo = carica()
    nodo = trova_nodo(grafo, domanda)
    if not nodo:
        return "Non lo so: nel grafo non c'e' niente che somigli alla domanda."

    relazioni = vicini(grafo, nodo, salti=2)
    print(f"[nodo di partenza: {nodo}]")
    print(f"[{len(relazioni)} relazioni entro 2 salti]\n")

    fatti = "\n".join(f"{r['da']} --{r['relazione']}--> {r['a']}  (da {r['fonte']})"
                      for r in relazioni)
    risposta = cliente().chat.completions.create(
        model=os.getenv("LLM_MODEL", "memoria-veloce"),
        messages=[
            {"role": "system",
             "content": "Rispondi alla domanda usando solo questi fatti "
                        "estratti dai documenti. Se devi fare una somma, "
                        "falla e mostra gli addendi. Se i fatti non "
                        "bastano, dillo.\n\n" + fatti},
            {"role": "user", "content": domanda},
        ],
        temperature=0,
        max_tokens=1200,
    )
    return risposta.choices[0].message.content.strip()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    comando = sys.argv[1]

    if comando == "costruisci":
        grafo = costruisci()
        GRAFO.parent.mkdir(parents=True, exist_ok=True)
        GRAFO.write_text(json.dumps(grafo, indent=2, ensure_ascii=False),
                         encoding="utf-8")
        print(f"\n{len(grafo['entita'])} entita', "
              f"{len(grafo['relazioni'])} relazioni -> {GRAFO}")

    elif comando == "mostra":
        grafo = carica()
        nodo = trova_nodo(grafo, " ".join(sys.argv[2:]))
        if not nodo:
            sys.exit("nodo non trovato")
        print(f"{nodo}\n")
        for relazione in vicini(grafo, nodo, salti=1):
            print(f"  {relazione['da']} --{relazione['relazione']}--> "
                  f"{relazione['a']}")

    elif comando == "chiedi":
        print(chiedi_al_grafo(" ".join(sys.argv[2:])))

    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
