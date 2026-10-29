#!/usr/bin/env python3
"""Il giro completo di cognee su una nota sola. Completo, si esegue.

    python moduli/05-la-pipeline-di-cognee/starter/primo_giro.py

Costa poche chiamate al modello e ci mette uno o due minuti. Serve a
vedere funzionare add -> cognify -> search prima di sapere cosa sono.

ATTENZIONE: azzera l'archivio prima di cominciare. Se hai gia' dei dati
dentro cognee, li perdi.
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv


def trova_radice() -> Path:
    for candidata in Path(__file__).resolve().parents:
        if (candidata / "progetto-finale" / "corpus").is_dir():
            return candidata
    raise SystemExit("lancia il comando dalla cartella del corso")


RADICE = trova_radice()
load_dotenv(RADICE / ".env")

import cognee                                                  # noqa: E402
from cognee.modules.search.types.SearchType import SearchType   # noqa: E402

cognee.config.system_root_directory(str(RADICE / "dati" / "cognee" / "sistema"))
cognee.config.data_root_directory(str(RADICE / "dati" / "cognee" / "documenti"))

CORPUS = RADICE / "progetto-finale" / "corpus"
DOCUMENTI = [
    str(CORPUS / "manuali" / "termovex-tx24.md"),
    str(CORPUS / "note" / "2026-03-12-caldaia-e4.md"),
]
DOMANDA = "L'errore E4 sulla caldaia: cosa dice il libretto e cosa ho trovato io?"


async def main():
    print("1. azzero l'archivio")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)

    print("2. add: metto dentro il manuale e una nota (non costa quota)")
    await cognee.add(DOCUMENTI, dataset_name="primo_giro")

    print("3. cognify: costruisco il grafo (qui si spende, abbi pazienza)")
    await cognee.cognify(datasets=["primo_giro"])

    print(f"\n4. search: {DOMANDA}\n")
    risultati = await cognee.search(
        query_text=DOMANDA,
        query_type=SearchType.GRAPH_COMPLETION,
        datasets=["primo_giro"],
    )
    for risultato in risultati:
        if isinstance(risultato, dict) and "search_result" in risultato:
            for voce in risultato["search_result"]:
                print(voce)
        else:
            print(risultato)

    print("\nSei righe di codice hanno fatto il lavoro dei moduli 3 e 4.")


if __name__ == "__main__":
    asyncio.run(main())
