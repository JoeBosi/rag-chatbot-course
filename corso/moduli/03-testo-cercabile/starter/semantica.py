#!/usr/bin/env python3
"""Ricerca semantica: cerca per significato, non per parole. Da completare.

Un **embedding** e' un elenco di numeri che rappresenta il significato di
un pezzo di testo. Testi che vogliono dire cose simili finiscono vicini,
anche se non hanno una parola in comune.

Il modello che usiamo gira SUL TUO COMPUTER (libreria fastembed): non
consuma quota, non manda niente fuori, funziona anche senza internet dopo
il primo scaricamento. E' multilingue, quindi capisce l'italiano.
"""

import numpy as np
from fastembed import TextEmbedding

# 384 numeri per pezzo di testo, circa 220 MB di modello, nessuna GPU.
MODELLO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_modello = None


def modello() -> TextEmbedding:
    """Carica il modello una volta sola (la prima volta lo scarica)."""
    global _modello
    if _modello is None:
        _modello = TextEmbedding(model_name=MODELLO)
    return _modello


def vettori(testi: list[str]) -> np.ndarray:
    """Testi -> matrice (quanti_testi x 384)."""
    return np.array(list(modello().embed(testi)), dtype=np.float32)


def similitudine_coseno(uno: np.ndarray, molti: np.ndarray) -> np.ndarray:
    """Quanto `uno` somiglia a ciascuna riga di `molti`. Da -1 a 1.

    TODO 1 ----------------------------------------------------------------
    Il coseno fra due vettori e' il loro prodotto scalare diviso per il
    prodotto delle lunghezze:

        coseno = (a . b) / (|a| * |b|)

    Vale 1 se puntano nella stessa direzione, 0 se sono perpendicolari.
    Con numpy: `molti @ uno` fa tutti i prodotti scalari in un colpo, e
    `np.linalg.norm(..., axis=1)` da' le lunghezze.
    Aggiungi 1e-10 ai denominatori per non dividere per zero.
    -----------------------------------------------------------------------
    """
    raise NotImplementedError("TODO 1: similitudine_coseno()")


class Semantica:
    def __init__(self, pezzi: list[dict]):
        self.pezzi = pezzi
        # Questo e' il passaggio lento: si fa una volta sola, all'avvio.
        self.matrice = vettori([pezzo["testo"] for pezzo in pezzi])

    def cerca(self, domanda: str, quanti: int = 5) -> list[dict]:
        """I `quanti` pezzi semanticamente piu' vicini alla domanda.

        TODO 2 ------------------------------------------------------------
        - calcola il vettore della domanda con vettori([domanda])[0]
        - confrontalo con self.matrice usando similitudine_coseno()
        - prendi gli indici dei `quanti` punteggi piu' alti
          (suggerimento: np.argsort(punteggi)[::-1][:quanti])
        - restituisci i pezzi corrispondenti, ognuno con
          punteggio=round(float(...), 3)
        -------------------------------------------------------------------
        """
        raise NotImplementedError("TODO 2: cerca()")
