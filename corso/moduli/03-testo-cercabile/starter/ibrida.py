#!/usr/bin/env python3
"""Ricerca ibrida: unisce lessicale e semantica. Da completare.

Le due ricerche sbagliano in modi diversi:
  - la lessicale non sa che "tagliaerba" e "rasaerba" sono la stessa cosa;
  - la semantica non sa che "E4" e "F03" sono due codici diversi, perche'
    per lei sono due stringhe corte e simili.

Unirle non vuol dire sommare i punteggi: BM25 da' numeri fra 0 e 20,
il coseno fra -1 e 1, non sono confrontabili. Si uniscono le POSIZIONI in
classifica, con una formula che si chiama RRF.

  RRF = Reciprocal Rank Fusion, "fusione dei ranghi reciproci".
  Ogni sistema vota: un pezzo che arriva primo vale 1/(K+1), secondo
  1/(K+2), e cosi' via. I voti si sommano. Un pezzo che entrambi mettono
  a meta' classifica batte un pezzo che uno solo mette primo.
"""

K = 60      # valore classico: ammorbidisce il vantaggio dei primi posti


def fondi(classifiche: list[list[dict]], quanti: int = 5) -> list[dict]:
    """Unisce piu' classifiche in una sola con RRF.

    TODO ------------------------------------------------------------------
    - per ogni classifica, scorri i risultati con la loro posizione
      (0, 1, 2, ...);
    - a ogni pezzo somma 1 / (K + posizione + 1), usando pezzo["id"] come
      identita';
    - tieni da parte il pezzo intero, per poterlo restituire;
    - ordina per punteggio RRF decrescente e restituisci i primi `quanti`,
      ognuno con la chiave "punteggio" uguale al punteggio RRF arrotondato
      a 4 decimali.
    -----------------------------------------------------------------------
    """
    raise NotImplementedError("TODO: fondi()")
