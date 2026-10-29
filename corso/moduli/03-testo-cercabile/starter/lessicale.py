#!/usr/bin/env python3
"""Ricerca lessicale con BM25. Da completare.

BM25 ("Best Match 25", il venticinquesimo tentativo di una famiglia di
formule degli anni Novanta) e' ancora oggi il modo migliore di cercare
per parole. Migliora il conteggio grezzo del modulo 1 in tre modi:

  TF  (term frequency, frequenza del termine)
      una parola che compare 5 volte conta piu' di una che compare 1
      volta, ma non 5 volte tanto: il contributo si appiattisce.
  IDF (inverse document frequency, frequenza inversa nei documenti)
      una parola che sta in tutti i documenti non distingue niente e
      conta poco; una parola rara vale molto.
  Lunghezza
      un documento lungo ha piu' parole per caso: viene normalizzato.
"""

import math
import re
from collections import Counter

# I due bottoni di BM25. Questi valori sono quelli classici e vanno bene
# quasi sempre: k1 quanto in fretta si appiattisce il contributo della
# frequenza, b quanto pesa la lunghezza del documento.
K1 = 1.5
B = 0.75


def parole(testo: str) -> list[str]:
    """Testo -> elenco di parole minuscole. Numeri e codici restano interi."""
    return re.findall(r"[a-zA-ZàèéìòùÀÈÉÌÒÙ0-9]+", testo.lower())


class Bm25:
    def __init__(self, pezzi: list[dict]):
        self.pezzi = pezzi
        self.documenti = [parole(pezzo["testo"]) for pezzo in pezzi]
        self.frequenze = [Counter(documento) for documento in self.documenti]
        self.lunghezze = [len(documento) for documento in self.documenti]
        self.lunghezza_media = sum(self.lunghezze) / max(len(self.lunghezze), 1)
        self.in_quanti_documenti = Counter()
        for frequenza in self.frequenze:
            self.in_quanti_documenti.update(frequenza.keys())

    def idf(self, parola: str) -> float:
        """Quanto e' rara questa parola nel corpus.

        TODO 1 ------------------------------------------------------------
        Formula BM25 classica, con N = numero di documenti e
        n = in quanti documenti compare la parola:

            idf = log( (N - n + 0.5) / (n + 0.5) + 1 )

        Il "+1" finale evita che una parola presente in tutti i documenti
        finisca con peso negativo.
        -------------------------------------------------------------------
        """
        raise NotImplementedError("TODO 1: idf()")

    def punteggio(self, parole_domanda: list[str], indice: int) -> float:
        """Quanto il documento `indice` risponde a questa domanda.

        TODO 2 ------------------------------------------------------------
        Per ogni parola della domanda presente nel documento, somma:

            idf(parola) * ( f * (K1 + 1) ) /
                          ( f + K1 * (1 - B + B * lunghezza / media) )

        dove f e' quante volte la parola compare in quel documento.
        -------------------------------------------------------------------
        """
        raise NotImplementedError("TODO 2: punteggio()")

    def cerca(self, domanda: str, quanti: int = 5) -> list[dict]:
        """I `quanti` pezzi col punteggio piu' alto."""
        parole_domanda = parole(domanda)
        punteggi = [(self.punteggio(parole_domanda, indice), indice)
                    for indice in range(len(self.pezzi))]
        punteggi.sort(reverse=True)
        return [dict(self.pezzi[indice], punteggio=round(punteggio, 3))
                for punteggio, indice in punteggi[:quanti] if punteggio > 0]
