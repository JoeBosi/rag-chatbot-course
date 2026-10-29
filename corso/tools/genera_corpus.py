#!/usr/bin/env python3
"""Genera il corpus del progetto finale a partire dai sorgenti Markdown.

Produce, dentro progetto-finale/corpus/:
  manuali/*.pdf        quattro manuali "nativi" (testo estraibile) + uno
                       scansionato (solo immagini: serve l'OCR)
  foto/*.png           immagini segnaposto di targhette e componenti
  audio/*.m4a          due note vocali in italiano (voce sintetica)

Lo studente NON deve lanciare questo script: il corpus e' gia' nel
repository. Serve al docente per rigenerarlo o per aggiungere apparecchi.

Dipendenze aggiuntive:  pip install fpdf2 pillow
Per l'audio serve anche:  espeak-ng  e  ffmpeg  (solo Linux/macOS con brew)

Uso:  python tools/genera_corpus.py [--solo pdf|foto|audio]
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
CORPUS = RADICE / "progetto-finale" / "corpus"
MANUALI = CORPUS / "manuali"
FOTO = CORPUS / "foto"
AUDIO = CORPUS / "audio"

# Il manuale del rasaerba diventa un PDF "scansionato": pagine come
# immagini, testo non selezionabile. Serve a far fallire pypdf nel
# progetto finale e a giustificare l'OCR.
SCANSIONATO = "greencut-rm46"


# --------------------------------------------------------------------------
# font
# --------------------------------------------------------------------------
def trova_font(grassetto=False, mono=False):
    """Primo font TrueType disponibile sul sistema. None se non ne trova."""
    candidati = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-{}.ttf",
        "/System/Library/Fonts/Supplemental/Arial{}.ttf",
        "/Library/Fonts/Arial{}.ttf",
    ]
    if mono:
        candidati = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono{}.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        ]
    for modello in candidati:
        for suffisso in (["-Bold", "Bold"] if grassetto else ["", "-Regular", ""]):
            percorso = Path(modello.format(suffisso))
            if percorso.exists():
                return str(percorso)
    return None


# --------------------------------------------------------------------------
# markdown -> righe tipografiche
# --------------------------------------------------------------------------
def leggi_markdown(percorso: Path):
    """Traduce il Markdown in una lista di (stile, testo).

    Stili: 'h1', 'h2', 'h3', 'p', 'li', 'tab', 'hr', 'vuoto'.
    Le tabelle diventano righe 'tab' gia' allineate a colonne fisse.
    """
    righe = []
    blocco_tabella = []

    def scarica_tabella():
        if not blocco_tabella:
            return
        celle = [[c.strip() for c in r.strip().strip("|").split("|")] for r in blocco_tabella]
        celle = [r for r in celle if not all(set(c) <= set("-: ") for c in r)]
        if not celle:
            blocco_tabella.clear()
            return
        colonne = max(len(r) for r in celle)
        larghezze = [0] * colonne
        for r in celle:
            for i, c in enumerate(r):
                larghezze[i] = max(larghezze[i], len(pulisci(c)))
        for r in celle:
            pezzi = [pulisci(c).ljust(larghezze[i]) for i, c in enumerate(r)]
            righe.append(("tab", "  ".join(pezzi).rstrip()))
        righe.append(("vuoto", ""))
        blocco_tabella.clear()

    for riga in percorso.read_text(encoding="utf-8").splitlines():
        if riga.lstrip().startswith("|"):
            blocco_tabella.append(riga)
            continue
        scarica_tabella()
        nudo = riga.strip()
        if not nudo:
            righe.append(("vuoto", ""))
        elif nudo.startswith("### "):
            righe.append(("h3", pulisci(nudo[4:])))
        elif nudo.startswith("## "):
            righe.append(("h2", pulisci(nudo[3:])))
        elif nudo.startswith("# "):
            righe.append(("h1", pulisci(nudo[2:])))
        elif nudo.startswith("---"):
            righe.append(("hr", ""))
        elif nudo.startswith(("- ", "* ")):
            righe.append(("li", pulisci(nudo[2:])))
        elif re.match(r"^\d+\.\s", nudo):
            righe.append(("li", pulisci(nudo)))
        elif nudo.startswith("> "):
            righe.append(("p", pulisci(nudo[2:])))
        else:
            righe.append(("p", pulisci(nudo)))
    scarica_tabella()
    return righe


def pulisci(testo: str) -> str:
    """Toglie la sintassi Markdown e i caratteri fuori dal latin-1."""
    testo = re.sub(r"\*\*(.+?)\*\*", r"\1", testo)
    testo = re.sub(r"`(.+?)`", r"\1", testo)
    testo = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", testo)
    return (testo.replace("’", "'").replace("‘", "'")
                 .replace("“", '"').replace("”", '"')
                 .replace("—", "-").replace("–", "-")
                 .replace(" ", " ").replace(" ", " "))


# --------------------------------------------------------------------------
# PDF nativi
# --------------------------------------------------------------------------
def pdf_nativo(sorgente: Path, destinazione: Path):
    from fpdf import FPDF

    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(20, 18, 20)
    pdf.add_page()
    for stile, testo in leggi_markdown(sorgente):
        if stile == "vuoto":
            pdf.ln(3)
        elif stile == "hr":
            pdf.ln(2)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(3)
        elif stile == "h1":
            pdf.set_font("helvetica", "B", 17)
            pdf.multi_cell(0, 8, testo, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
        elif stile == "h2":
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 13)
            pdf.multi_cell(0, 7, testo, new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        elif stile == "h3":
            pdf.set_font("helvetica", "B", 11)
            pdf.multi_cell(0, 6, testo, new_x="LMARGIN", new_y="NEXT")
        elif stile == "tab":
            # Courier: ogni carattere e' largo 0,6 volte il corpo. Scelgo il
            # corpo piu' grande che fa stare la riga nei 170 mm di testo.
            larghezza_mm = 170
            corpo = min(8.5, larghezza_mm * 2.834 / (0.6 * max(len(testo), 1)))
            pdf.set_font("courier", "", max(corpo, 4.5))
            pdf.multi_cell(0, max(corpo, 4.5) * 0.52, testo, new_x="LMARGIN", new_y="NEXT")
        elif stile == "li":
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(0, 5, "  " + testo, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(0, 5, testo, new_x="LMARGIN", new_y="NEXT")
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(destinazione))


# --------------------------------------------------------------------------
# PDF scansionato (pagine come immagini, con un po' di sporco)
# --------------------------------------------------------------------------
def pdf_scansionato(sorgente: Path, destinazione: Path):
    import random
    from fpdf import FPDF
    from PIL import Image, ImageDraw, ImageFont

    random.seed(46)
    larghezza, altezza = 1240, 1754          # A4 a 150 dpi
    percorso_font = trova_font() or ""
    def font(dimensione, grassetto=False):
        scelto = trova_font(grassetto=grassetto) or percorso_font
        if not scelto:
            return ImageFont.load_default()
        return ImageFont.truetype(scelto, dimensione)

    pagine, corrente = [], None
    y = 0
    margine = 110

    def nuova_pagina():
        nonlocal corrente, y
        corrente = Image.new("L", (larghezza, altezza), 244)
        y = margine
        return corrente

    nuova_pagina()
    for stile, testo in leggi_markdown(sorgente):
        if stile == "vuoto":
            y += 14
            continue
        if stile == "hr":
            ImageDraw.Draw(corrente).line((margine, y, larghezza - margine, y), fill=120)
            y += 20
            continue
        dimensione, grassetto = {"h1": (44, True), "h2": (32, True), "h3": (26, True)}.get(
            stile, (22, False))
        tipo = font(dimensione, grassetto)
        prefisso = "  - " if stile == "li" else ""
        disegna = ImageDraw.Draw(corrente)
        for pezzo in spezza(prefisso + testo, tipo, larghezza - 2 * margine, disegna):
            if y > altezza - margine:
                pagine.append(corrente)
                nuova_pagina()
                disegna = ImageDraw.Draw(corrente)
            disegna.text((margine + random.randint(-2, 2), y), pezzo,
                         font=tipo, fill=random.randint(25, 60))
            y += int(dimensione * 1.45)
        y += 6
    pagine.append(corrente)

    finite = []
    for pagina in pagine:
        disegna = ImageDraw.Draw(pagina)
        for _ in range(1600):                 # granulosita' della scansione
            disegna.point((random.randint(0, larghezza - 1),
                           random.randint(0, altezza - 1)),
                          fill=random.randint(150, 215))
        finite.append(pagina.rotate(random.uniform(-0.4, 0.4),
                                    resample=Image.BILINEAR, fillcolor=244))

    temporanei = []
    for numero, pagina in enumerate(finite):
        temporaneo = destinazione.parent / f".scan-{numero}.jpg"
        pagina.convert("RGB").save(temporaneo, "JPEG", quality=72)
        temporanei.append(temporaneo)

    pdf = FPDF(format="A4", unit="mm")
    for temporaneo in temporanei:
        pdf.add_page()
        pdf.image(str(temporaneo), x=0, y=0, w=210, h=297)
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(destinazione))
    for temporaneo in temporanei:
        temporaneo.unlink()


def spezza(testo, tipo, larghezza_massima, disegna):
    parole, righe, corrente = testo.split(), [], ""
    for parola in parole:
        prova = (corrente + " " + parola).strip()
        if disegna.textlength(prova, font=tipo) <= larghezza_massima:
            corrente = prova
        else:
            if corrente:
                righe.append(corrente)
            corrente = parola
    if corrente:
        righe.append(corrente)
    return righe or [""]


# --------------------------------------------------------------------------
# foto segnaposto
# --------------------------------------------------------------------------
FOTOGRAFIE = [
    ("targhetta-termovex-tx24.png", "TARGHETTA DATI", [
        "TERMOVEX  TX-24", "Cod. prodotto 0010-TX24", "Matricola  TX24-2019-004471",
        "Portata termica 24,0 kW", "Pressione max 3 bar", "230V ~ 50Hz",
        "Anno 2019"], (196, 198, 200)),
    ("vaso-espansione-caldaia.png", "VASO DI ESPANSIONE", [
        "8 litri - precarica 1,0 bar", "codice ricambio 7832-VE8",
        "valvola di gonfiaggio sul retro"], (150, 158, 168)),
    ("cinghia-lavatrice-1201j5.png", "CINGHIA POLI-V", [
        "stampigliatura: 1201 J5", "5 gole - lunghezza 1201 mm",
        "spezzata sul lato interno"], (70, 70, 74)),
    ("pastiglie-freno-vm-bp21.png", "PASTIGLIE FRENO", [
        "VM-BP21 organiche", "materiale d'attrito 0,4 mm",
        "tracce di olio minerale"], (120, 124, 130)),
]


def genera_foto():
    from PIL import Image, ImageDraw, ImageFont
    FOTO.mkdir(parents=True, exist_ok=True)
    for nome, titolo, righe, colore in FOTOGRAFIE:
        immagine = Image.new("RGB", (900, 600), colore)
        disegna = ImageDraw.Draw(immagine)
        percorso = trova_font(grassetto=True)
        grande = ImageFont.truetype(percorso, 40) if percorso else ImageFont.load_default()
        percorso_n = trova_font()
        piccolo = ImageFont.truetype(percorso_n, 28) if percorso_n else ImageFont.load_default()
        disegna.rectangle((40, 40, 860, 560), outline=(30, 30, 30), width=4)
        disegna.rectangle((60, 70, 840, 150), fill=(250, 250, 245))
        disegna.text((80, 90), titolo, font=grande, fill=(20, 20, 20))
        y = 200
        for riga in righe:
            disegna.text((80, y), riga, font=piccolo, fill=(250, 250, 245))
            y += 46
        minuscolo = ImageFont.truetype(percorso_n, 19) if percorso_n else ImageFont.load_default()
        disegna.text((80, 532), "immagine segnaposto del corso - non e' una foto reale",
                     font=minuscolo, fill=(245, 245, 240))
        immagine.save(FOTO / nome)
        print(f"  foto   {nome}")


# --------------------------------------------------------------------------
# note vocali
# --------------------------------------------------------------------------
NOTE_VOCALI = [
    ("nota-2026-09-12-caldaia.m4a",
     "Dodici settembre. Caldaia Termovex. E' tornato l'errore E quattro. "
     "Ho controllato il manometro: la pressione era uno virgola quattro bar, "
     "quindi la pressione non c'entrava. Ho smontato il mantello e lo "
     "scambiatore primario era pieno di calcare. L'ho pulito con la spazzola "
     "di nylon, ho lavato il sifone della condensa e ho rimesso tutto a posto. "
     "Ci ho messo due ore. Nessun ricambio."),
    ("nota-2026-09-14-rasaerba.m4a",
     "Quattordici settembre. Rasaerba GreenCut. Ho affilato la lama con la "
     "smerigliatrice e l'ho riequilibrata sul cacciavite. Bullone della lama "
     "stretto a quarantacinque newton metro con la chiave dinamometrica. "
     "Ho anche cambiato l'olio del motore da caldo, sei decimi di litro di "
     "SAE trenta. La prossima volta ricordarsi di staccare la candela prima "
     "di ribaltare il rasaerba."),
]


def genera_audio():
    if not shutil.which("espeak-ng") or not shutil.which("ffmpeg"):
        print("  audio  SALTATO: servono espeak-ng e ffmpeg")
        return
    AUDIO.mkdir(parents=True, exist_ok=True)
    for nome, testo in NOTE_VOCALI:
        grezzo = AUDIO / (nome.replace(".m4a", ".wav"))
        subprocess.run(["espeak-ng", "-v", "it", "-s", "145", "-p", "35",
                        "-w", str(grezzo), testo], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(grezzo),
                        "-ar", "16000", "-ac", "1", "-c:a", "aac", "-b:a", "64k",
                        str(AUDIO / nome)], check=True)
        grezzo.unlink()
        print(f"  audio  {nome}")
    (AUDIO / "LEGGIMI.md").write_text(
        "# Note vocali del corpus\n\n"
        "Sono generate con una voce sintetica (espeak-ng): suonano robotiche\n"
        "di proposito. Servono a far girare il laboratorio anche a chi non ha\n"
        "un microfono a portata di mano.\n\n"
        "La trascrizione di una voce sintetica e' piu' difficile di quella di\n"
        "una voce vera: se Whisper sbaglia qualche numero, e' normale ed e'\n"
        "parte dell'esercizio (vedi il modulo 7: i fatti trascritti male vanno\n"
        "corretti, non lasciati in memoria).\n\n"
        "Registra le tue: qualunque registratore del telefono, formato m4a,\n"
        "wav o mp3, e mettile in questa cartella.\n",
        encoding="utf-8")


# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--solo", choices=["pdf", "foto", "audio"])
    argomenti = parser.parse_args()

    if argomenti.solo in (None, "pdf"):
        sorgenti = sorted(MANUALI.glob("*.md"))
        if not sorgenti:
            sys.exit(f"nessun sorgente .md in {MANUALI}")
        for sorgente in sorgenti:
            destinazione = sorgente.with_suffix(".pdf")
            if sorgente.stem == SCANSIONATO:
                pdf_scansionato(sorgente, destinazione)
                print(f"  pdf    {destinazione.name}  (scansionato, senza testo)")
            else:
                pdf_nativo(sorgente, destinazione)
                print(f"  pdf    {destinazione.name}")
    if argomenti.solo in (None, "foto"):
        genera_foto()
    if argomenti.solo in (None, "audio"):
        genera_audio()
    print("corpus pronto in", CORPUS)


if __name__ == "__main__":
    main()
