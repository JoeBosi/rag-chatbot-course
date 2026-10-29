#!/usr/bin/env python3
"""Verifica del laboratorio 8. Nessuna chiamata al modello.

    python moduli/08-valutare-il-sistema/verifica.py

Mette alla prova il tuo giudice con risposte finte, di cui si sa gia'
l'esito. Se il tuo giudica() da' un punto a "la pressione e' 1,2 bar,
poi portata a 1,4", te lo dice.
"""

import sys
from pathlib import Path

import yaml

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
    print("Laboratorio 8 superato.")
    print("Hai finito gli otto moduli: 18,5 ore su 20.")
    print("Prossimo e ultimo: progetto-finale/BRIEF.md")
    sys.exit(0)


print("== l'insieme di valutazione ==")

percorso_domande = RADICE / "progetto-finale" / "domande.yaml"
if not controlla("progetto-finale/domande.yaml esiste", percorso_domande.is_file()):
    finisci()

domande = yaml.safe_load(percorso_domande.read_text(encoding="utf-8"))
controlla("contiene 12 domande", len(domande) == 12, f"ne ho contate {len(domande)}")
tipi = {d.get("tipo") for d in domande}
controlla("c'e' almeno una domanda senza risposta (tipo: assente)",
          "assente" in tipi)
controlla("c'e' almeno una domanda con fatti vietati",
          any(d.get("vietate") for d in domande))

print("\n== il tuo script ==")

script = RADICE / "memoria" / "valuta.py"
if not controlla("memoria/valuta.py esiste", script.is_file(),
                 "copia moduli/08-.../starter/valuta.py in memoria/"):
    finisci()

try:
    import valuta
except Exception as errore:
    controlla("memoria/valuta.py si importa", False, str(errore))
    finisci()

for nome in ("giudica", "giudica_assente", "giro", "riassumi", "scrivi"):
    controlla(f"la funzione {nome}() c'e'",
              callable(getattr(valuta, nome, None)))

print("\n== il giudice, su risposte di cui si sa l'esito ==")

# (risposta finta, domanda, esito atteso, perche')
PROVE = [
    ("La pressione di esercizio a freddo e' 1,4 bar.",
     {"tipo": "aggiornato", "attese": ["1,4"], "vietate": ["1,2 bar a freddo"]},
     True, "risposta giusta e pulita"),

    ("Il libretto dice 1,2 bar a freddo.",
     {"tipo": "aggiornato", "attese": ["1,4"], "vietate": ["1,2 bar a freddo"]},
     False, "manca il valore nuovo"),

    ("La pressione e' 1,2 bar a freddo, poi portata a 1,4 bar.",
     {"tipo": "aggiornato", "attese": ["1,4"], "vietate": ["1,2 bar a freddo"]},
     False, "ha la parola giusta E il fatto vecchio: non deve passare"),

    ("La pressione di esercizio e' 1.4 bar.",
     {"tipo": "aggiornato", "attese": ["1,4"]},
     True, "1.4 e 1,4 sono lo stesso numero: normalizza() se ne occupa"),

    ("La candela e' una NGK BPR6ES con distanza elettrodi 0,7 mm.",
     {"tipo": "ocr", "attese": ["BPR6ES", "0,7"]},
     True, "maiuscole e minuscole non contano"),

    ("Non trovo questa informazione nei documenti.",
     {"tipo": "assente", "attese": ["non"]},
     True, "ammette di non sapere, senza inventare numeri"),

    ("La pressione consigliata e' di 4 bar.",
     {"tipo": "assente", "attese": ["non"]},
     False, "ha inventato un valore"),

    ("La pressione non deve superare i 4 bar.",
     {"tipo": "assente", "attese": ["non"]},
     False, "c'e' la parola 'non' ma c'e' anche un numero inventato: "
            "e' il trabocchetto del modulo"),

    ("Nei manuali caricati questa informazione non e' presente.",
     {"tipo": "assente", "attese": ["non"]},
     True, "altro modo di dire non lo so"),
]

for risposta, domanda, atteso, perche in PROVE:
    try:
        ottenuto, motivo = valuta.giudica(risposta, domanda)
    except NotImplementedError:
        controlla("giudica() non e' piu' un TODO", False,
                  "hai lasciato il raise dello starter")
        finisci()
    except Exception as errore:
        controlla(f'giudica("{risposta[:40]}...")', False, str(errore))
        continue

    etichetta = f'"{risposta[:46]}..." -> {"passa" if atteso else "non passa"}'
    controlla(etichetta, ottenuto == atteso, perche)

print("\n== il riassunto per tipo ==")

ESITI = [
    {"tipo": "fattuale", "passata": True},
    {"tipo": "fattuale", "passata": True},
    {"tipo": "ocr", "passata": False},
    {"tipo": "ocr", "passata": False},
]
try:
    riassunto = dict((t, (p, n)) for t, p, n in valuta.riassumi(ESITI))
    controlla("riassumi() separa i tipi", set(riassunto) == {"fattuale", "ocr"})
    controlla("riassumi() conta 2/2 sui fattuali",
              riassunto.get("fattuale") == (2, 2))
    controlla("riassumi() conta 0/2 sugli ocr",
              riassunto.get("ocr") == (0, 2))
except NotImplementedError:
    controlla("riassumi() non e' piu' un TODO", False,
              "hai lasciato il raise dello starter")
except Exception as errore:
    controlla("riassumi() funziona", False, str(errore))

print("\n== la traccia scritta ==")

cartella = RADICE / "dati" / "valutazioni"
giri = sorted(cartella.glob("*.md")) if cartella.is_dir() else []
if controlla("hai lasciato almeno un giro in dati/valutazioni/", bool(giri),
             "esercizio 5: lancia python memoria/valuta.py"):
    testo = giri[-1].read_text(encoding="utf-8").lower()
    controlla("  il file dice che modello hai usato",
              "gpt-oss" in testo or "modello" in testo)
    controlla("  il file dice che tipo di ricerca hai usato",
              "grafo" in testo or "completion" in testo)
    controlla("  il file ha il riassunto per tipo",
              "fattuale" in testo and "ocr" in testo)

finisci()
