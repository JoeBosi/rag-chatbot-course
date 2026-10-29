#!/usr/bin/env python3
"""Ricerca ibrida: unisce lessicale e semantica. Versione completa.

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

    Si sommano le posizioni, non i punteggi: cosi' non serve sapere che
    scala usa ciascun sistema, e nessuno dei due puo' dominare l'altro
    solo perche' produce numeri piu' grandi.
    """
    voti: dict[str, float] = {}
    oggetti: dict[str, dict] = {}
    for classifica in classifiche:
        for posizione, pezzo in enumerate(classifica):
            identita = pezzo["id"]
            voti[identita] = voti.get(identita, 0.0) + 1 / (K + posizione + 1)
            oggetti.setdefault(identita, pezzo)
    ordinati = sorted(voti.items(), key=lambda coppia: coppia[1], reverse=True)
    return [dict(oggetti[identita], punteggio=round(voto, 4))
            for identita, voto in ordinati[:quanti]]
