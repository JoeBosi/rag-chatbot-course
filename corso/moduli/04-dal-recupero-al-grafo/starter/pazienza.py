#!/usr/bin/env python3
"""Aspettare quando il fornitore dice 429. Nessun TODO: questo e' un regalo.

Il gateway del modulo 2 cambia fornitore quando il primo esaurisce la
quota. Ma se hai una chiave sola, non c'e' nessun posto dove cadere: la
catena di riserve e' decorativa. Allora l'unica cosa sensata e'
**aspettare**, e aspettare la quantita' giusta.

Il fornitore te la dice: nel messaggio di errore c'e' "Please try again
in 1.875s", e spesso c'e' l'header `retry-after`.
"""

import re
import time


def secondi_da_aspettare(errore: Exception, tentativo: int) -> float:
    """Quanto aspettare prima di riprovare.

    Prima cerca il tempo che il fornitore ha dichiarato. Se non lo trova,
    raddoppia a ogni tentativo (2, 4, 8, 16 secondi): si chiama
    "attesa esponenziale" e serve a non martellare un servizio in
    difficolta'.
    """
    testo = str(errore)
    dichiarato = re.search(r"try again in ([0-9.]+)s", testo)
    if dichiarato:
        return float(dichiarato.group(1)) + 0.5
    dichiarato = re.search(r"retry-after[\"']?\s*[:=]\s*[\"']?(\d+)", testo, re.I)
    if dichiarato:
        return float(dichiarato.group(1)) + 0.5
    return min(2 ** tentativo, 60)


def con_pazienza(funzione, *argomenti, tentativi: int = 6, **parametri):
    """Esegue `funzione`, e se il fornitore dice 429 aspetta e riprova.

    Qualunque altro errore lo rilancia subito: un 401 non migliora
    aspettando.
    """
    for tentativo in range(tentativi):
        try:
            return funzione(*argomenti, **parametri)
        except Exception as errore:
            if "429" not in str(errore) and "rate_limit" not in str(errore).lower():
                raise
            if tentativo == tentativi - 1:
                raise
            attesa = secondi_da_aspettare(errore, tentativo)
            print(f"    quota esaurita, aspetto {attesa:.1f}s "
                  f"(tentativo {tentativo + 1}/{tentativi})", flush=True)
            time.sleep(attesa)
    raise RuntimeError("non dovremmo arrivare qui")
