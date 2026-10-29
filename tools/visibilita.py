"""File per i motori di ricerca e per i modelli linguistici.

Lavora sulla cartella di build, prima di mkdocs:
- aggiunge a ogni pagina una descrizione (meta description e Open
  Graph), presa dal primo paragrafo del testo;
- scrive robots.txt, llms.txt (formato llmstxt.org) e llms-full.txt,
  con tutto il testo del corso in un solo file.
La sitemap.xml e l'URL canonico li genera gia' MkDocs da site_url.
"""

import re
from pathlib import Path

import yaml

SITO = "https://corso-rag.giuseppebosi.com"
AUTORE = "https://www.giuseppebosi.com"
ALTRI_CORSI = [
    ("Corso pratico di llama.cpp", "https://corso-llamacpp.giuseppebosi.com/"),
    ("Corso JSON & API", "https://corso-api-json.giuseppebosi.com/"),
]
CRAWLER_IA = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot",
              "Claude-SearchBot", "anthropic-ai", "PerplexityBot",
              "Google-Extended", "Applebot-Extended", "CCBot"]


def url_di(percorso: str, lingua: str = "it") -> str:
    base = SITO + ("/en" if lingua == "en" else "")
    if percorso == "index.md":
        return base + "/"
    return f"{base}/{percorso[:-3]}/"


def inglese(file: str) -> str:
    """Nome della versione inglese di una pagina: pagina.en.md."""
    return file[:-3] + ".en.md"


def pulisci(testo: str) -> str:
    testo = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", testo)
    testo = re.sub(r"[*_`]", "", testo)
    return re.sub(r"\s+", " ", testo).strip()


def descrizione(md: str, massimo: int = 158) -> str:
    """Il primo paragrafo di prosa dopo il titolo, accorciato."""
    for blocco in re.split(r"\n\s*\n", md):
        blocco = blocco.strip()
        if not blocco or blocco[0] in "#|`!><-*:{" or re.match(r"\d+\.", blocco):
            continue
        frase = pulisci(blocco)
        if len(frase) < 40:
            continue
        if len(frase) > massimo:
            frase = frase[:massimo].rsplit(" ", 1)[0].rstrip(",;:") + "…"
        return frase
    return ""


def pagine_nav(voci, sezione=None):
    """(sezione di primo livello, titolo, file) in ordine di menu."""
    for voce in voci:
        for titolo, valore in voce.items():
            if isinstance(valore, str):
                yield sezione, titolo, valore
            else:
                yield from pagine_nav(valore, sezione or titolo)


def applica(lavoro: Path, config: Path) -> int:
    cfg = yaml.load(config.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    pagine = list(pagine_nav(cfg["nav"]))

    descrizioni = {}
    nomi = [file for _, _, file in pagine]
    nomi += [inglese(f) for f in nomi if (lavoro / inglese(f)).is_file()]
    for file in nomi:
        pagina = lavoro / file
        testo = pagina.read_text(encoding="utf-8")
        descr = cfg["site_description"] if file == "index.md" else descrizione(testo)
        descrizioni[file] = descr
        if descr and not testo.startswith("---\n"):
            fm = "---\ndescription: " + yaml.safe_dump(descr, allow_unicode=True,
                                                       width=1000).split("\n")[0]
            pagina.write_text(fm + "\n---\n\n" + testo, encoding="utf-8")
        elif testo.startswith("---\n"):
            trovata = re.search(r"^description: (.*)$", testo, re.M)
            if trovata:
                descrizioni[file] = yaml.safe_load(trovata.group(1))

    robots = ["User-agent: *", "Allow: /", ""]
    for bot in CRAWLER_IA:
        robots += [f"User-agent: {bot}", "Allow: /", ""]
    robots.append(f"Sitemap: {SITO}/sitemap.xml")
    (lavoro / "robots.txt").write_text("\n".join(robots) + "\n", encoding="utf-8")

    testa = [
        f"# {cfg['site_name']}", "",
        f"> {cfg['site_description']}", "",
        "Corso in italiano, gratuito e senza registrazione, di Prof. Giuseppe "
        f"Bosi ({AUTORE}). Testi CC BY 4.0, codice MIT. Il codice del corso "
        "e' in Python; si usano cognee, LiteLLM e i piani gratuiti di Groq, "
        "Google AI Studio e OpenRouter, con l'alternativa locale Ollama.", "",
    ]
    corto, sezione_corrente = list(testa), None
    for sezione, titolo, file in pagine:
        gruppo = sezione or "Il corso"
        if gruppo != sezione_corrente:
            corto += ["", f"## {gruppo}", ""]
            sezione_corrente = gruppo
        riga = f"- [{titolo}]({url_di(file)})"
        if descrizioni[file]:
            riga += f": {descrizioni[file]}"
        corto.append(riga)
    corto += ["", "## Optional", "",
              f"- [Testo completo del corso]({SITO}/llms-full.txt): tutte le "
              "pagine in un solo file Markdown",
              f"- [Giuseppe Bosi]({AUTORE}): sito dell'autore",
              "- [LinkedIn di Giuseppe Bosi](https://www.linkedin.com/in/giuseppebosi): profilo dell'autore"]
    corto += [f"- [{nome}]({url}): altro corso dello stesso autore"
              for nome, url in ALTRI_CORSI]

    tradotte = [(t, f) for _, t, f in pagine if inglese(f) in descrizioni]
    if tradotte:
        lingua_en = next(l for l in cfg["plugins"][1]["i18n"]["languages"]
                         if l["locale"] == "en")
        traduci = lingua_en.get("nav_translations", {})
        corto += ["", "## English version", "",
                  f"The same course in English, under {SITO}/en/. "
                  "The sample corpus and the questions in the commands stay in Italian.", ""]
        for titolo, file in tradotte:
            riga = f"- [{traduci.get(titolo, titolo)}]({url_di(file, 'en')})"
            if descrizioni[inglese(file)]:
                riga += f": {descrizioni[inglese(file)]}"
            corto.append(riga)
        corto.append(f"- [Full English text]({SITO}/llms-full-en.txt): all translated pages in one Markdown file")
    (lavoro / "llms.txt").write_text("\n".join(corto) + "\n", encoding="utf-8")

    pieno_en = [f"# {cfg['site_name']} (English)", ""]
    for titolo, file in tradotte:
        testo = (lavoro / inglese(file)).read_text(encoding="utf-8")
        testo = re.sub(r"\A---\n.*?\n---\n\n", "", testo, flags=re.S)
        pieno_en += ["", "---", "", f"Page: {url_di(file, 'en')}", "", testo.strip()]
    if tradotte:
        (lavoro / "llms-full-en.txt").write_text("\n".join(pieno_en) + "\n", encoding="utf-8")

    pieno = list(testa)
    for _, titolo, file in pagine:
        testo = (lavoro / file).read_text(encoding="utf-8")
        testo = re.sub(r"\A---\n.*?\n---\n\n", "", testo, flags=re.S)
        pieno += ["", "---", "", f"Pagina: {url_di(file)}", "", testo.strip()]
    (lavoro / "llms-full.txt").write_text("\n".join(pieno) + "\n", encoding="utf-8")
    return len(pagine)
