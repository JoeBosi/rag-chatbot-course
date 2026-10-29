#!/usr/bin/env python3
"""Costruisce il sito del corso in site/ a partire da corso/.

Non da' in pasto a MkDocs la cartella corso/ cosi' com'e': dentro ci
sono .env con le chiavi vere, i dati di cognee e i PDF generati. Copia
invece in una cartella di lavoro SOLO quello che deve finire online,
scegliendolo con una lista di ammessi, non con una lista di esclusi.

Alla fine controlla che nessuna chiave sia finita in site/ e si ferma
se ne trova una.
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CORSO = RADICE / "corso"
LAVORO = RADICE / "build" / "docs"
SITO = RADICE / "site"

# Estensioni che possono finire online. Tutto il resto viene ignorato.
AMMESSE = {".md", ".py", ".yaml", ".yml", ".txt", ".toml", ".cfg", ".png",
           ".jpg", ".jpeg", ".svg", ".ico", ".css", ".js"}

# Cartelle che non escono mai, qualunque cosa contengano.
VIETATE = {"dati", ".venv", ".venv-gateway", "__pycache__", ".git",
           "site", "build", ".pytest_cache"}

# File vietati per nome: il .env vero non deve uscire, il .env.example si'.
def vietato(percorso: Path) -> bool:
    nome = percorso.name
    if nome == ".env" or nome.startswith(".env.") and nome != ".env.example":
        return True
    return nome.endswith((".pdf", ".m4a", ".mp3", ".wav", ".db", ".sqlite"))


def copia() -> int:
    if LAVORO.exists():
        shutil.rmtree(LAVORO)
    LAVORO.mkdir(parents=True)

    copiati = 0
    for sorgente in CORSO.rglob("*"):
        relativo = sorgente.relative_to(CORSO)
        if any(parte in VIETATE for parte in relativo.parts):
            continue
        if sorgente.is_dir():
            continue
        if sorgente.suffix.lower() not in AMMESSE or vietato(sorgente):
            continue
        destinazione = LAVORO / relativo
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(sorgente, destinazione)
        copiati += 1

    # MkDocs vuole una index.md: e' il README del corso.
    if (LAVORO / "README.md").is_file():
        shutil.copy2(LAVORO / "README.md", LAVORO / "index.md")
        (LAVORO / "README.md").unlink()

    return copiati


# Forme delle chiavi dei fornitori usati nel corso.
IMPRONTE = [
    ("Groq",       re.compile(r"gsk_[A-Za-z0-9]{20,}")),
    ("OpenRouter", re.compile(r"sk-or-v1-[A-Za-z0-9]{20,}")),
    ("OpenAI",     re.compile(r"sk-proj-[A-Za-z0-9_\-]{20,}")),
    ("Google",     re.compile(r"AIza[A-Za-z0-9_\-]{30,}")),
    ("IONOS",      re.compile(r"[a-f0-9]{32}\.[A-Za-z0-9_\-]{40,}")),
]


def controlla_chiavi(cartella: Path) -> list[str]:
    """Nessuna chiave deve essere finita nel sito pubblicato."""
    trovate = []
    for file in cartella.rglob("*"):
        if not file.is_file():
            continue
        try:
            testo = file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for fornitore, impronta in IMPRONTE:
            for riscontro in impronta.findall(testo):
                trovate.append(
                    f"{fornitore} in {file.relative_to(cartella)}: "
                    f"{riscontro[:12]}..."
                )
    return trovate


def controlla_env_incorporato() -> None:
    """SETUP.md contiene una copia di .env.example, per chi legge online.

    Due copie della stessa cosa divergono sempre. Qui il build si ferma
    se e' successo, invece di pubblicare istruzioni sbagliate.
    """
    esempio = (CORSO / ".env.example").read_text(encoding="utf-8").rstrip("\n")
    setup = (CORSO / "SETUP.md").read_text(encoding="utf-8")
    if esempio not in setup:
        print("FERMO: il blocco .env.example dentro SETUP.md non coincide")
        print("       piu' con corso/.env.example. Riallineali.")
        sys.exit(1)
    print("   SETUP.md e .env.example coincidono")


def main() -> None:
    print("== controlli di coerenza ==")
    controlla_env_incorporato()

    print("\n== copia dei file pubblicabili ==")
    copiati = copia()
    print(f"   {copiati} file in {LAVORO.relative_to(RADICE)}")

    sys.path.insert(0, str(RADICE / "tools"))
    import visibilita
    n = visibilita.applica(LAVORO, RADICE / "mkdocs.yml")
    print(f"   descrizioni per {n} pagine, robots.txt, llms.txt, llms-full.txt")

    perdite = controlla_chiavi(LAVORO)
    if perdite:
        print("\nFERMO: una chiave sarebbe finita nel sito.")
        for perdita in perdite:
            print("  -", perdita)
        sys.exit(1)
    print("   nessuna chiave nei file copiati")

    print("\n== mkdocs build ==")
    esito = subprocess.run(
        [str(RADICE / ".venv" / "bin" / "mkdocs"), "build",
         "--strict", "--clean"],
        cwd=RADICE,
    )
    if esito.returncode != 0:
        sys.exit(esito.returncode)

    print("\n== controllo finale su site/ ==")
    perdite = controlla_chiavi(SITO)
    if perdite:
        print("FERMO: una chiave e' nel sito costruito.")
        for perdita in perdite:
            print("  -", perdita)
        shutil.rmtree(SITO)
        print("site/ cancellato per sicurezza.")
        sys.exit(1)

    pagine = len(list(SITO.rglob("*.html")))
    peso = sum(f.stat().st_size for f in SITO.rglob("*") if f.is_file())
    print(f"   {pagine} pagine, {peso / 1024 / 1024:.1f} MB, nessuna chiave")
    print(f"\nsito pronto in {SITO}")


if __name__ == "__main__":
    main()
