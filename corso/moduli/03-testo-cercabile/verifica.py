#!/usr/bin/env python3
"""Verifica del laboratorio 3. Non chiama nessun modello: gratis.

    python moduli/03-testo-cercabile/verifica.py
"""

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
    print("Laboratorio 3 superato.")
    print("Prossimo: moduli/04-dal-recupero-al-grafo/LEZIONE.md")
    sys.exit(0)


print("== i file ==")
presenti = True
for nome in ["pezzi.py", "lessicale.py", "semantica.py", "ibrida.py"]:
    presenti &= controlla(f"memoria/{nome}", (RADICE / "memoria" / nome).exists(),
                          f"cp moduli/03-testo-cercabile/starter/{nome} memoria/")
if not presenti:
    finisci()

print("\n== spezzare ==")
try:
    from pezzi import carica_pezzi, spezza_alla_cieca, spezza_per_titoli
    manuale = (RADICE / "progetto-finale" / "corpus" / "manuali"
               / "termovex-tx24.md").read_text(encoding="utf-8")

    ciechi = spezza_alla_cieca(manuale)
    controlla(f"spezza_alla_cieca() -> {len(ciechi)} pezzi", len(ciechi) == 6,
              "attesi 6 pezzi da 800 caratteri con 120 di sovrapposizione")
    controlla("i pezzi si sovrappongono davvero",
              len(ciechi) > 1 and ciechi[0][-120:] == ciechi[1][:120],
              "il pezzo successivo deve ripartire 120 caratteri prima della fine")

    strutturati = spezza_per_titoli(manuale)
    controlla(f"spezza_per_titoli() -> {len(strutturati)} pezzi", len(strutturati) == 8,
              "atteso un pezzo per sezione: 8")
    tabella = [p for p in strutturati if "E4" in p and "E9" in p]
    controlla("la tabella dei codici di errore resta intera", bool(tabella),
              "un pezzo solo deve contenere sia E4 sia E9")

    pezzi = carica_pezzi(per_titoli=True)
    controlla(f"carica_pezzi() -> {len(pezzi)} pezzi", len(pezzi) == 48,
              "attesi 48 pezzi da 12 documenti")
    controlla("ogni pezzo ha id, nome e testo",
              all({"id", "nome", "testo"} <= set(p) for p in pezzi))
except NotImplementedError as errore:
    controlla("pezzi.py e' completo", False, str(errore))
    finisci()
except Exception as errore:
    controlla("pezzi.py gira", False, f"{type(errore).__name__}: {errore}")
    finisci()

print("\n== BM25 ==")
try:
    from lessicale import Bm25
    motore = Bm25(pezzi)
    raro, comune = motore.idf("bpr6es"), motore.idf("il")
    controlla(f"l'IDF premia le parole rare ({raro:.2f} contro {comune:.2f})",
              raro > comune * 2,
              "stai contando le occorrenze invece dei documenti?")
    risultati = motore.cerca("Con che coppia si stringe il bullone della lama?")
    controlla("trova il manuale del rasaerba sulla coppia della lama",
              bool(risultati) and "greencut" in risultati[0]["nome"],
              f"primo risultato: {risultati[0]['nome'] if risultati else 'nessuno'}")
    controlla("i punteggi sono positivi e decrescenti",
              all(r["punteggio"] > 0 for r in risultati)
              and risultati == sorted(risultati, key=lambda r: -r["punteggio"]))
except NotImplementedError as errore:
    controlla("lessicale.py e' completo", False, str(errore))
    finisci()
except Exception as errore:
    controlla("lessicale.py gira", False, f"{type(errore).__name__}: {errore}")
    finisci()

print("\n== semantica ==")
print("    (la prima volta scarica 220 MB, abbi pazienza)")
try:
    from semantica import Semantica, similitudine_coseno, vettori
    prova = vettori(["il rasaerba non parte", "il tagliaerba non si avvia",
                     "la caldaia va in errore E4"])
    vicini = float(similitudine_coseno(prova[0], prova[1:2])[0])
    lontani = float(similitudine_coseno(prova[0], prova[2:3])[0])
    controlla(f"capisce i sinonimi ({vicini:.2f} contro {lontani:.2f})",
              vicini > lontani + 0.15,
              "due frasi senza parole in comune ma di pari significato "
              "devono stare piu' vicine")
    motore_semantico = Semantica(pezzi)
    risultati = motore_semantico.cerca("Il tagliaerba non si accende", quanti=3)
    controlla("trova il rasaerba partendo da 'tagliaerba'",
              any("greencut" in r["nome"] for r in risultati),
              f"ha trovato: {[r['nome'] for r in risultati]}")
except NotImplementedError as errore:
    controlla("semantica.py e' completo", False, str(errore))
    finisci()
except Exception as errore:
    controlla("semantica.py gira", False, f"{type(errore).__name__}: {errore}")
    finisci()

print("\n== fusione ==")
try:
    from ibrida import fondi
    per_parole = motore.cerca("Cosa vuol dire il codice F03?", quanti=8)
    per_significato = motore_semantico.cerca("Cosa vuol dire il codice F03?", quanti=8)
    insieme = fondi([per_parole, per_significato], quanti=5)
    controlla("fondi() restituisce qualcosa", bool(insieme))
    controlla("fondi() non duplica lo stesso pezzo",
              len({r["id"] for r in insieme}) == len(insieme),
              "usa pezzo['id'] come identita'")
    controlla("fondi() ordina per punteggio decrescente",
              insieme == sorted(insieme, key=lambda r: -r["punteggio"]))
    controlla("la fusione trova il manuale della lavatrice",
              any("lavanor" in r["nome"] for r in insieme),
              f"ha trovato: {[r['nome'] for r in insieme]}")
except NotImplementedError as errore:
    controlla("ibrida.py e' completo", False, str(errore))
except Exception as errore:
    controlla("ibrida.py gira", False, f"{type(errore).__name__}: {errore}")

finisci()
