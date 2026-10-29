# Mettere il quaderno su un server

Questa pagina è **facoltativa**. Il corso funziona per intero sul tuo
computer. Serve se vuoi che il tuo quaderno sia raggiungibile quando il
portatile è chiuso: da un altro computer, o dal telefono mentre sei in
officina.

Presuppone che tu abbia finito almeno il modulo 6.

---

## 1. Che macchina serve

| Risorsa | Minimo | Perché |
|---|---|---|
| RAM | 2 GB | 4 se vuoi PostgreSQL nello stesso posto |
| disco | 5 GB | il modello di embedding pesa 0,22 GB, il resto sono dati |
| CPU | 1 core | l'inferenza è altrove, qui si fa solo il coordinamento |
| scheda grafica | **nessuna** | il modello non gira qui |

Sono i requisiti di un VPS (*Virtual Private Server*, un computer in
affitto che sta sempre acceso) da pochi euro al mese, o di un vecchio
portatile, o di un Raspberry Pi 4 con 4 GB.

**Non serve una macchina con la scheda grafica.** È il punto di tutta
l'architettura del corso: il modello gira dal fornitore, qui gira solo
il coordinamento e le ricerche. Se invece scegli la strada Ollama,
cambia tutto e ti serve una macchina vera.

Il sistema operativo è Linux. Debian 12 o Ubuntu 24.04 vanno bene.

---

## 2. Cosa va sul server e cosa no

Non tutto il corso. Il server ospita **tre cose**:

1. il **gateway** LiteLLM, perché è l'unico posto dove stanno le chiavi;
2. i **dati**: PostgreSQL con pgvector, Kuzu, i documenti;
3. un **modo di interrogare**: la riga di comando via SSH basta, ma
   probabilmente vorrai qualcosa da telefono.

Le chiavi stanno **solo** sul server, in un file `.env` con i permessi
giusti. Il tuo portatile parla col gateway, non coi fornitori.

```bash
chmod 600 .env
```

Non è formalismo: `600` vuol dire che nessun altro utente della macchina
lo legge. Su un server condiviso è l'unica cosa che separa le tue chiavi
dagli altri.

---

## 3. Installazione

```bash
sudo apt update
sudo apt install -y python3.12-venv git docker.io docker-compose-plugin

git clone <il tuo repo> ~/quaderno
cd ~/quaderno

python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt

python3.12 -m venv .venv-gateway
.venv-gateway/bin/pip install -r requirements-gateway.txt

cp .env.example .env
nano .env          # metti le chiavi
chmod 600 .env

docker compose -f memoria/docker-compose.yml up -d
```

Da qui in poi è identico a quello che hai fatto sul portatile.

---

## 4. Il gateway come servizio

Finora il gateway l'hai avviato a mano e si spegne quando chiudi il
terminale. Su un server deve ripartire da solo, anche dopo un riavvio.

`/etc/systemd/system/gateway-memoria.service`:

```ini
[Unit]
Description=Gateway LiteLLM del quaderno di officina
After=network-online.target docker.service
Wants=network-online.target

[Service]
Type=simple
User=quaderno
WorkingDirectory=/home/quaderno/quaderno
EnvironmentFile=/home/quaderno/quaderno/.env
ExecStart=/home/quaderno/quaderno/.venv-gateway/bin/litellm \
    --config memoria/gateway/config.yaml --host 127.0.0.1 --port 4000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gateway-memoria
sudo systemctl status gateway-memoria
curl -s http://localhost:4000/health/liveliness
```

Due righe su cui vale la pena fermarsi.

**`User=quaderno`**: il gateway non gira come root. Se domani LiteLLM ha
un buco, chi entra si ritrova con i permessi di un utente che può
leggere una cartella e basta.

**`EnvironmentFile`**: le chiavi arrivano dal file, non dalla riga di
comando. Le variabili scritte in `ExecStart` si vedono in `ps`, cioè
sono leggibili da chiunque sia sulla macchina. Il file con `chmod 600`
no.

---

## 5. Il gateway non si affaccia su internet

**Questo è il punto da non sbagliare.**

LiteLLM ha una chiave sua (`GATEWAY_KEY`), ma non è un servizio pensato
per stare esposto. Se apri la porta 4000 al mondo, stai mettendo le tue
quote gratuite a disposizione di chiunque le trovi — e le trovano, i
motori di scansione girano sulle porte comuni in continuazione.

Il gateway ascolta su `localhost` e basta: è quello che fa `--host
127.0.0.1` nel servizio qui sopra. **Senza quell'opzione LiteLLM ascolta
su `0.0.0.0`**, e a quel punto l'unica cosa che ti protegge è il
firewall. Controlla:

```bash
ss -lptn 'sport = :4000'
```

Deve dire `127.0.0.1:4000`. Se dice `0.0.0.0:4000` o `*:4000`, correggi
prima di fare qualunque altra cosa. Per arrivarci da fuori:

```bash
ssh -L 4000:localhost:4000 quaderno@tuo-server
```

Da quel momento, sul tuo portatile, `http://localhost:4000` **è** il
gateway del server. Niente porte aperte, e il traffico passa dentro SSH.

Se invece vuoi un'interfaccia web raggiungibile da telefono, la regola
resta: si espone **l'interfaccia**, dietro un reverse proxy con HTTPS e
una password. Mai il gateway.

---

## 6. Il backup, che qui diventa obbligatorio

Sul portatile il backup è prudenza. Su un server è l'unica cosa che ti
separa dalla perdita totale: i VPS economici si guastano, e chi te lo
affitta non ti deve niente.

Il modulo 7 ti ha dato i tre pezzi. Qui si mettono in un file e si
lanciano da soli.

`~/quaderno/backup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
cd /home/quaderno/quaderno
GIORNO=$(date +%F)
DESTINAZIONE=/home/quaderno/backup/$GIORNO
mkdir -p "$DESTINAZIONE"

.venv/bin/python memoria/manutenzione.py salva "$DESTINAZIONE"

docker compose -f memoria/docker-compose.yml exec -T postgres \
    pg_dump -U cognee cognee > "$DESTINAZIONE/registro.sql"

# tiene gli ultimi 14 giorni
find /home/quaderno/backup -maxdepth 1 -type d -mtime +14 -exec rm -rf {} +
```

```bash
chmod +x ~/quaderno/backup.sh
crontab -e
```

```cron
30 3 * * * /home/quaderno/quaderno/backup.sh >> /home/quaderno/backup.log 2>&1
```

**E poi, una volta, prova a ripristinarlo su un'altra cartella.** Un
backup mai ripristinato non è un backup, è un file. È la frase del
modulo 7 e vale ancora di più qui, dove il guasto te lo aspetti.

---

## 7. Se la macchina è tua e vuoi togliere internet dal giro

Con 8 GB di RAM puoi mettere Ollama sul server e non mandare fuori
niente:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b-instruct
```

Nel `.env` cambi le due righe che conosci dal modulo 2. Il gateway resta
dov'è: cambia solo quale fornitore ha dietro.

Le risposte peggiorano un po' e i tempi si allungano. In cambio, le note
dei tuoi clienti non escono dalla stanza. Rileggi il
[brief del progetto](progetto-finale/BRIEF.md) sul perché può contare
più della qualità.
