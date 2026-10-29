#!/usr/bin/env python3
"""Verifica del laboratorio 2.

    python moduli/02-chiavi-gateway-e-quote/verifica.py

Il gateway deve essere acceso su localhost:4000.
"""

import os
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RADICE / "memoria"))

from dotenv import load_dotenv        # noqa: E402

load_dotenv(RADICE / ".env")
errori = []


def controlla(descrizione, condizione, aiuto=""):
    print(("OK  " if condizione else "NO  ") + descrizione)
    if not condizione:
        errori.append(f"{descrizione}\n      -> {aiuto}" if aiuto else descrizione)
    return condizione


print("== il gateway ==")
indirizzo = os.getenv("LLM_ENDPOINT", "http://localhost:4000/v1")
chiave = os.getenv("LLM_API_KEY") or os.getenv("GATEWAY_KEY", "sk-memoria-locale")

try:
    import httpx
    risposta = httpx.get(indirizzo.replace("/v1", "") + "/health/liveliness", timeout=10)
    acceso = risposta.status_code == 200
except Exception:
    acceso = False
controlla(f"il gateway risponde su {indirizzo}", acceso,
          "avvialo: .venv-gateway/bin/litellm --config memoria/gateway/config.yaml --host 127.0.0.1 --port 4000")


def ascolta_solo_in_locale(porta: int = 4000) -> bool:
    """Prova a raggiungere il gateway dall'indirizzo di rete del computer.

    Se risponde anche li', sta ascoltando su 0.0.0.0: chiunque sulla tua
    stessa rete puo' usare le tue chiavi. Funziona uguale su macOS e Linux.
    """
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("10.255.255.255", 1))     # non manda niente
            indirizzo_di_rete = s.getsockname()[0]
    except OSError:
        return True                               # nessuna rete: niente da esporre
    if indirizzo_di_rete.startswith("127."):
        return True
    try:
        with socket.create_connection((indirizzo_di_rete, porta), timeout=2):
            return False                          # risponde da fuori: esposto
    except OSError:
        return True


if acceso:
    controlla("il gateway ascolta SOLO sul tuo computer", ascolta_solo_in_locale(),
              "hai dimenticato --host 127.0.0.1: chi e' sulla tua rete "
              "puo' usare le tue chiavi. Fermalo e rilancialo con --host")

controlla("memoria/gateway/config.yaml esiste",
          (RADICE / "memoria" / "gateway" / "config.yaml").exists(),
          "cp moduli/02-chiavi-gateway-e-quote/starter/config.yaml memoria/gateway/")

if (RADICE / "memoria" / "gateway" / "config.yaml").exists():
    testo = (RADICE / "memoria" / "gateway" / "config.yaml").read_text()
    controlla("la configurazione ha una catena di riserve", "fallbacks" in testo,
              "manca la sezione router_settings: fallbacks")
    controlla("le chiavi NON sono scritte dentro al config",
              "gsk_" not in testo and "sk-or-v1" not in testo and "AIza" not in testo,
              "usa os.environ/NOME_VARIABILE, mai la chiave in chiaro")

print("\n== .env punta al gateway ==")
controlla("LLM_PROVIDER = custom", os.getenv("LLM_PROVIDER") == "custom",
          f"adesso vale {os.getenv('LLM_PROVIDER')!r}: vedi LAB.md passo 2")
controlla("LLM_ENDPOINT impostato", bool(os.getenv("LLM_ENDPOINT")),
          "LLM_ENDPOINT=http://localhost:4000/v1")

print("\n== stima_quota.py ==")
percorso_stima = RADICE / "memoria" / "stima_quota.py"
if controlla("memoria/stima_quota.py esiste", percorso_stima.exists(),
             "cp moduli/02-chiavi-gateway-e-quote/starter/stima_quota.py memoria/"):
    try:
        from stima_quota import stima
        corpus = sorted((RADICE / "progetto-finale" / "corpus").rglob("*.md"))
        corpus = [p for p in corpus if p.name != "LEGGIMI.md"]
        risultato = stima(corpus)
        controlla(f"conta i documenti ({risultato['documenti']})",
                  risultato["documenti"] == 12,
                  "attesi 12 documenti nel corpus")
        controlla(f"conta i pezzi ({risultato['pezzi']})", risultato["pezzi"] == 22,
                  "attesi 22 pezzi: usa la divisione per eccesso, documento per documento")
        controlla(f"conta le chiamate ({risultato['chiamate']})",
                  risultato["chiamate"] == 44, "pezzi * 2")
        controlla(f"il tempo minimo e' il limite piu' stretto "
                  f"({risultato['minuti']:.1f} min)",
                  abs(risultato["minuti"] - max(risultato["minuti_per_token"],
                                                risultato["minuti_per_chiamate"])) < 0.01,
                  "minuti = max(dei due limiti), non la somma")
    except NotImplementedError:
        controlla("stima() e' scritta", False, "TODO nel file")
    except Exception as errore:
        controlla("stima() gira", False, f"{type(errore).__name__}: {errore}")

print("\n== il sistema passa dal gateway ==")
if acceso:
    try:
        from llm import chiedi
        risposta = chiedi("Rispondi solo con la parola: pronto")
        controlla("memoria/llm.py risponde attraverso il gateway",
                  "pront" in risposta.lower(), f"ha risposto: {risposta[:80]!r}")
    except Exception as errore:
        controlla("memoria/llm.py risponde attraverso il gateway", False,
                  str(errore)[:200])

print()
if errori:
    print("=" * 60)
    print("Mancano ancora:\n")
    for errore in errori:
        print("  -", errore)
    sys.exit(1)

print("=" * 60)
print("Laboratorio 2 superato.")
print("Prossimo: moduli/03-testo-cercabile/LEZIONE.md")
