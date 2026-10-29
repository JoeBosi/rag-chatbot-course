#!/usr/bin/env python3
"""Verifica del laboratorio 4.

    python moduli/04-dal-recupero-al-grafo/verifica.py

Fa una chiamata al modello alla fine. Il grafo deve essere gia' costruito.
"""

import json
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "memoria"))
errori = []


def controlla(descrizione, condizione, aiuto=""):
    print(("OK  " if condizione else "NO  ") + descrizione)
    if not condizione:
        errori.append(f"{descrizione}\n      -> {aiuto}" if aiuto else descrizione)
    return condizione


def finisci():
    print()
    if errori:
        print("=" * 60)
        print("Mancano ancora:\n")
        for errore in errori:
            print("  -", errore)
        sys.exit(1)
    print("=" * 60)
    print("Laboratorio 4 superato.")
    print("Prossimo: moduli/05-la-pipeline-di-cognee/LEZIONE.md")
    sys.exit(0)


print("== i file ==")
ok = controlla("memoria/pazienza.py", (RADICE / "memoria" / "pazienza.py").exists(),
               "cp moduli/04-dal-recupero-al-grafo/starter/pazienza.py memoria/")
ok &= controlla("memoria/grafo.py", (RADICE / "memoria" / "grafo.py").exists(),
                "cp moduli/04-dal-recupero-al-grafo/starter/grafo.py memoria/")
if not ok:
    finisci()

print("\n== la pazienza ==")
try:
    from pazienza import con_pazienza, secondi_da_aspettare

    class Finto(Exception):
        pass

    dichiarato = secondi_da_aspettare(
        Finto("Rate limit reached. Please try again in 1.875s"), 0)
    controlla(f"legge il tempo dichiarato dal fornitore ({dichiarato})",
              abs(dichiarato - 2.375) < 0.01,
              "atteso 1.875 + 0.5 di margine")
    esponenziale = secondi_da_aspettare(Finto("errore generico"), 3)
    controlla(f"attesa esponenziale quando non c'e' ({esponenziale})",
              esponenziale == 8, "2 elevato al numero del tentativo")

    tentativi = {"n": 0}

    def fallisce_due_volte():
        tentativi["n"] += 1
        if tentativi["n"] < 3:
            raise Finto("Error code: 429 - rate_limit_exceeded. "
                        "Please try again in 0.01s")
        return "fatto"

    controlla("con_pazienza() riprova e alla fine passa",
              con_pazienza(fallisce_due_volte) == "fatto")

    def fallisce_per_altro():
        raise Finto("401 invalid api key")

    try:
        con_pazienza(fallisce_per_altro)
        rilanciato = False
    except Finto:
        rilanciato = True
    controlla("con_pazienza() NON riprova su errori diversi dal 429", rilanciato,
              "un 401 non migliora aspettando")
except Exception as errore:
    controlla("pazienza.py gira", False, f"{type(errore).__name__}: {errore}")
    finisci()

print("\n== il grafo ==")
percorso_grafo = RADICE / "dati" / "grafo.json"
if not controlla("dati/grafo.json esiste", percorso_grafo.exists(),
                 "python memoria/grafo.py costruisci"):
    finisci()

grafo = json.loads(percorso_grafo.read_text(encoding="utf-8"))
controlla(f"ha delle entita' ({len(grafo.get('entita', []))})",
          len(grafo.get("entita", [])) >= 30,
          "attese almeno 30 entita' dal corpus del corso")
controlla(f"ha delle relazioni ({len(grafo.get('relazioni', []))})",
          len(grafo.get("relazioni", [])) >= 40,
          "attese almeno 40 relazioni")
controlla("ogni entita' ha nome, tipo e fonti",
          all({"nome", "tipo", "fonti"} <= set(e) for e in grafo["entita"]),
          "manca la fusione per nome: vedi TODO 1")
controlla("ogni relazione sa da quale documento viene",
          all("fonte" in r for r in grafo["relazioni"]),
          "serve a poter verificare le risposte")

caldaia = [e for e in grafo["entita"] if "termovex" in e["nome"].lower()]
controlla(f"la caldaia e' nel grafo ({len(caldaia)} nodi che la nominano)",
          bool(caldaia))
interventi = [e for e in grafo["entita"] if e["tipo"] == "intervento"]
controlla(f"ha riconosciuto gli interventi ({len(interventi)})",
          len(interventi) >= 5,
          "attesi almeno 5 interventi: sono 7 note nel corpus")

print("\n== la visita ==")
try:
    from grafo import trova_nodo, vicini
    nodo = trova_nodo(grafo, "caldaia termovex")
    controlla(f"trova_nodo() aggancia la caldaia ({nodo})", bool(nodo))
    uno = vicini(grafo, nodo, salti=1)
    due = vicini(grafo, nodo, salti=2)
    controlla(f"1 salto -> {len(uno)} relazioni", len(uno) > 0)
    controlla(f"2 salti -> {len(due)} relazioni, di piu'", len(due) > len(uno),
              "la visita in ampiezza non sta allargando")
    controlla("non restituisce relazioni doppie",
              len({(r["da"], r["relazione"], r["a"], r["fonte"]) for r in due})
              == len(due))
except NotImplementedError as errore:
    controlla("vicini() e' scritta", False, str(errore))
    finisci()
except Exception as errore:
    controlla("vicini() gira", False, f"{type(errore).__name__}: {errore}")
    finisci()

print("\n== la domanda impossibile ==")
try:
    from grafo import chiedi_al_grafo
    risposta = chiedi_al_grafo("Quante ore ho passato in tutto sulla caldaia?")
    print(f"    risposta: {' '.join(risposta.split())[:160]}")
    controlla("risponde con la somma giusta (3,5 ore)",
              "3,5" in risposta or "3.5" in risposta,
              "il grafo ha i fatti ma la somma non torna: alza max_tokens "
              "o usa un modello piu' grande")
except Exception as errore:
    controlla("chiedi_al_grafo() gira", False, f"{type(errore).__name__}: {errore}")

finisci()
