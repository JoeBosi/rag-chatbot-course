#!/usr/bin/env python3
"""Verifica del laboratorio 7.

    python moduli/07-manutenzione-della-memoria/verifica.py

Controlla il codice e i file. L'ultimo controllo interroga l'archivio e
consuma una chiamata al modello: se il gateway e' spento, lo salta e te
lo dice.
"""

import asyncio
import inspect
import sys
from pathlib import Path

from dotenv import load_dotenv

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "memoria"))
load_dotenv(RADICE / ".env")
errori = []


def controlla(descrizione, condizione, aiuto=""):
    print(("OK  " if condizione else "NO  ") + descrizione)
    if not condizione:
        errori.append(f"{descrizione}\n      -> {aiuto}" if aiuto else descrizione)
    return condizione


saltati = []


def finisci():
    print()
    if errori:
        print("=" * 60)
        print("Mancano ancora:\n")
        for errore in errori:
            print("  -", errore)
        sys.exit(1)
    print("=" * 60)
    if saltati:
        print("Laboratorio 7 superato PER META'.")
        print("Il codice va bene, ma non ho potuto provare la cosa che")
        print("conta davvero, cioe' che l'archivio risponda 1,4 bar:\n")
        for saltato in saltati:
            print("  -", saltato)
        print("\nRimedia e rilancia prima di passare al modulo 8.")
        sys.exit(2)
    print("Laboratorio 7 superato.")
    print("Prossimo: moduli/08-valutare-il-sistema/LEZIONE.md")
    sys.exit(0)


print("== il tuo script ==")

script = RADICE / "memoria" / "manutenzione.py"
if not controlla("memoria/manutenzione.py esiste", script.is_file(),
                 "copia moduli/07-.../starter/manutenzione.py in memoria/"):
    finisci()

import manutenzione  # noqa: E402

for nome in ("aggiungi", "elenca", "dimentica", "relazione", "salva"):
    funzione = getattr(manutenzione, nome, None)
    controlla(f"la funzione {nome}() c'e'", callable(funzione))
    if callable(funzione):
        controlla(f"  {nome}() e' asincrona",
                  inspect.iscoroutinefunction(funzione),
                  "deve iniziare con 'async def'")
        sorgente = inspect.getsource(funzione)
        controlla(f"  {nome}() non e' piu' un TODO",
                  "NotImplementedError" not in sorgente,
                  "hai lasciato il raise dello starter")

testo = script.read_text()
controlla("dimentica() usa delete_data", "delete_data" in testo)
controlla("dimentica() usa il modo soft",
          '"soft"' in testo or "'soft'" in testo,
          "mode='hard' porta via i nodi condivisi da altri documenti")
controlla("salva() esporta in cogx", "cogx" in testo,
          "e' l'unico formato che si puo' rimettere dentro")
controlla("relazione() chiama report e validate",
          "report" in testo and "validate" in testo)

print("\n== la nota di rettifica ==")

rettifiche = list((RADICE / "dati").glob("*rettific*.md")) if (RADICE / "dati").is_dir() else []
if controlla("hai scritto una nota di rettifica in dati/", bool(rettifiche),
             "esercizio 4: dati/rettifica-pressione.md"):
    corpo = rettifiche[0].read_text().lower()
    controlla("  dice 1,4 bar", "1,4" in corpo or "1.4" in corpo)
    controlla("  dichiara che supera il valore precedente",
              any(p in corpo for p in ("supera", "non piu' valido",
                                       "non più valido", "sostituisce")),
              "il modello deve capire quale dei due valori vale")
    controlla("  contiene le parole della domanda",
              "pressione" in corpo and "termovex" in corpo,
              "se non le contiene, il recupero non la trova mai")

print("\n== risposte ==")
risposte = RADICE / "RISPOSTE.md"
if risposte.is_file():
    corpo = risposte.read_text().lower()
    controlla("RISPOSTE.md parla dei nodi-mozzo",
              "mozzo" in corpo or "hub" in corpo, "esercizio 6")
else:
    controlla("RISPOSTE.md esiste", False,
              "scrivi le risposte agli esercizi 4 e 6")

print("\n== l'archivio risponde il valore aggiornato ==")

try:
    import httpx

    import os

    base = os.getenv("GATEWAY_URL", "http://localhost:4000").rstrip("/")
    base = base[:-3] if base.endswith("/v1") else base
    httpx.get(base + "/health/liveliness", timeout=5)
    gateway_acceso = True
except Exception:
    gateway_acceso = False

if not gateway_acceso:
    print("--  gateway spento: salto la domanda all'archivio.")
    saltati.append("il gateway e' spento: accendilo e rilancia")
else:
    try:
        sys.path.insert(0, str(RADICE / "memoria"))
        import quaderno

        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            asyncio.run(
                quaderno.chiedi("A che pressione devo tenere l'impianto "
                                "della caldaia Termovex?")
            )
        testo_risposta = buffer.getvalue().lower()
        print("    risposta dell'archivio:",
              " ".join(testo_risposta.split())[:200])
        controlla("l'archivio risponde 1,4 bar",
                  "1,4" in testo_risposta or "1.4" in testo_risposta,
                  "aggiungi la nota di rettifica e ridigerisci "
                  "(esercizio 4)")
    except Exception as errore:
        print(f"--  non sono riuscito a interrogare l'archivio: {errore}")
        saltati.append(f"l'archivio non risponde: {str(errore)[:120]}")

finisci()
