# Modulo 1 — Perché serve una memoria

**Durata: 2 ore** (45 minuti di lezione, 60 di laboratorio, 15 di
installazione delle chiavi). Totale progressivo: 2,0 / 20 ore.

Prerequisiti: [SETUP.md](../../SETUP.md) fatto, chiave Groq presa come
spiegato in [CHIAVI.md](../../CHIAVI.md#1-groq).

---

## 1. Primi cinque minuti: fallo adesso

Non c'è niente da capire, per ora. Esegui:

```bash
python moduli/01-perche-serve-una-memoria/starter/chiedi.py \
  "Cosa significa l'errore E4 sulla caldaia Termovex TX-24 e come si risolve?"
```

Leggi la risposta. Arriva in due secondi, è scritta bene, è
circostanziata. E, quasi sicuramente, **è inventata**.

La caldaia Termovex TX-24 non esiste: l'abbiamo inventata noi per questo
corso. Il modello non lo dice. Ti dà una procedura plausibile, con numeri
plausibili, perché il suo mestiere è produrre testo plausibile.

Adesso confronta con il manuale vero, che sta in
`progetto-finale/corpus/manuali/termovex-tx24.md`, paragrafo 2.1. Di
solito il modello azzecca il concetto generale (la pressione) e sbaglia
tutto il resto: il valore di ripristino, il nome del componente, la
procedura.

**Questo è il problema che il corso risolve.**

## 2. Cos'è successo, con i nomi giusti

**LLM** sta per *Large Language Model*, modello linguistico di grandi
dimensioni. È un programma addestrato a prevedere la parola successiva su
una quantità enorme di testo. Non ha un archivio da cui pesca: ha dei
pesi numerici che riassumono le regolarità del linguaggio che ha visto.

**Token.** Il modello non lavora con le lettere ma con i *token*, pezzi di
parola. «caldaia» è un token, «Termovex» ne occupa tre o quattro perché è
una parola che non ha mai visto. Ti serve saperlo per due motivi: le
quote gratuite si contano in token, e i limiti di lunghezza pure.

**Allucinazione.** Quando il modello produce un'affermazione falsa con lo
stesso tono sicuro di una vera. Non è un malfunzionamento: è il
funzionamento normale applicato a qualcosa che non sa. Un modello non ha
modo di distinguere «ricordo» da «ho appena inventato», perché non
ricorda niente: genera.

**Prompt.** Il testo che gli mandi. Tutto quello che il modello sa della
tua domanda, in quel momento, sta lì dentro.

## 3. Secondo giro: dagli il manuale

```bash
python moduli/01-perche-serve-una-memoria/starter/chiedi.py \
  --con-manuale progetto-finale/corpus/manuali/termovex-tx24.md \
  "Cosa significa l'errore E4 sulla caldaia Termovex TX-24 e come si risolve?"
```

Adesso la risposta è giusta: 0,8 bar, rubinetto blu, ripristino a 1,2 bar,
e l'avvertenza che se torna spesso la causa è un'altra.

Non è cambiato il modello. È cambiato il **contesto**: il manuale è finito
dentro il prompt, e il modello ha potuto leggerlo invece di inventarlo.

> **Riquadro — Strada locale**
> Con Ollama è identico: `chiedi.py` legge `LLM_PROVIDER` da `.env` e
> parla con il modello locale senza che tu cambi una riga. La risposta
> arriva più lenta e più sciatta, ma il ragionamento del modulo regge
> uguale. Vedi [SETUP.md](../../SETUP.md#strada-locale-ollama).

## 4. Perché non finisce qui

Se la soluzione fosse «incolla tutto nel prompt», il corso finirebbe a
pagina uno. Non funziona, per quattro motivi che puoi misurare tu.

### 4.1 Non ci sta

Ogni modello ha una **finestra di contesto**: il numero massimo di token
che può leggere in una volta. Il nostro manuale sta comodo. Cinque manuali
di cinquanta pagine, più due anni di note, no.

### 4.2 Costa quota, e la quota è finita

Il piano gratuito di Groq dà **8.000 token al minuto**. Il manuale
Termovex, da solo, ne occupa circa 890. I cinque manuali del corpus
insieme fanno circa 3.200 token: il 40 % della quota di un minuto per
**una sola domanda**, cioè due domande di fila e sei fermo ad aspettare.
E questi sono cinque manualetti di due pagine, non venti manuali veri.
Misuralo tu:

```bash
python moduli/01-perche-serve-una-memoria/starter/conta_token.py \
  progetto-finale/corpus/manuali/*.md
```

### 4.3 Più contesto, peggiori risposte

È controintuitivo ma è documentato: quando il materiale utile sta in mezzo
a molto materiale inutile, i modelli lo trovano meno. Il fenomeno si
chiama *lost in the middle* — «perso nel mezzo» — ed è descritto in
<https://arxiv.org/abs/2307.03172>. Nel laboratorio lo vedi succedere.

### 4.4 È lento

Il modello deve leggere tutto ogni volta. Trentamila token di manuali
significano qualche secondo di attesa per ogni singola domanda, ogni
volta, anche per chiedere che candela monta il rasaerba.

## 5. L'idea: cercare prima, chiedere dopo

Invece di dargli tutto, gli diamo **solo il pezzo che serve**:

1. arriva la domanda;
2. un programma cerca, tra i documenti, i pezzi che c'entrano;
3. quei pezzi finiscono nel prompt, insieme alla domanda;
4. il modello risponde usando quelli.

Questo schema ha un nome: **RAG**, *Retrieval-Augmented Generation*,
«generazione aumentata dal recupero». Recupero perché prima si recupera,
aumentata perché il prompt viene arricchito, generazione perché alla fine
è il modello che scrive la risposta.

Tre proprietà che guadagni subito:

| | Senza RAG | Con RAG |
|---|---|---|
| Fonte della risposta | i pesi del modello | i tuoi documenti |
| Verificabile? | no | sì: sai quali pezzi ha letto |
| Aggiornabile? | solo riaddestrando | cambi il documento |

E una che **non** guadagni: il RAG non elimina le allucinazioni, le rende
*controllabili*. Se il recupero porta il pezzo sbagliato, il modello
risponde sbagliato con la stessa sicurezza di prima. Per questo il modulo
8 è dedicato a misurare, non a fidarsi.

## 6. Le trenta righe

Nel laboratorio scrivi la versione più stupida possibile di un RAG:

- i documenti sono i file Markdown del corpus;
- la ricerca conta quante parole della domanda compaiono in ogni
  documento;
- i tre documenti col punteggio più alto finiscono nel prompt.

Funziona. Su alcune domande è già utile. Su altre fa una figuraccia — e
quella figuraccia è il modulo 3.

## 7. Cosa NON fa ancora, e in che modulo lo sistemiamo

| Problema che vedrai nel laboratorio | Si risolve nel |
|---|---|
| Se chiedi «perde acqua» non trova «trafilamento»: cerca parole, non significati | modulo 3 |
| Prende il documento intero, anche se serve un paragrafo | modulo 3 |
| Non risponde a «quante ore ho passato sulla caldaia?»: deve mettere insieme più note | modulo 4 |
| Se due note si contraddicono, usa quella che capita | modulo 7 |
| Non sai se risponde bene: lo giudichi a naso | modulo 8 |

## 8. Prima di passare al laboratorio

Tre parole che useremo da qui in avanti:

| Parola | Significato in una riga |
|---|---|
| Corpus | l'insieme dei documenti che il sistema conosce |
| Recupero (*retrieval*) | scegliere quali pezzi del corpus mandare al modello |
| Contesto | il materiale che finisce nel prompt insieme alla domanda |

Tutte le altre sono in [GLOSSARIO.md](../../GLOSSARIO.md).

**Adesso: [LAB.md](LAB.md).**
