# Put the notebook on a server {#mettere-il-quaderno-su-un-server}

This page is **optional**. The whole course works on your own
computer. You need it if you want your notebook to be reachable when your
laptop is closed: from another computer, or from your phone while you are
in the workshop.

It assumes you have finished at least module 6.

---

## 1. What machine you need {#1-che-macchina-serve}

| Resource | Minimum | Why |
|---|---|---|
| RAM | 2 GB | 4 if you want PostgreSQL in the same place |
| disk | 5 GB | the embedding model takes 0.22 GB, the rest is data |
| CPU | 1 core | inference happens elsewhere, here you only do coordination |
| graphics card | **none** | the model does not run here |

These are the requirements of a VPS (*Virtual Private Server*, a rented
computer that is always on) for a few euros a month, or of an old
laptop, or of a Raspberry Pi 4 with 4 GB.

**You do not need a machine with a graphics card.** That is the point of the
whole course architecture: the model runs at the provider, and here only
coordination and searches run. If you choose the Ollama path instead,
everything changes and you need a real machine.

The operating system is Linux. Debian 12 or Ubuntu 24.04 are fine.

---

## 2. What goes on the server and what does not {#2-cosa-va-sul-server-e-cosa-no}

Not the whole course. The server hosts **three things**:

1. the LiteLLM **gateway**, because it is the only place where the keys live;
2. the **data**: PostgreSQL with pgvector, Kuzu, the documents;
3. a **way to ask questions**: the command line over SSH is enough, but
   you will probably want something for your phone.

The keys live **only** on the server, in a `.env` file with the right
permissions. Your laptop talks to the gateway, not to the providers.

```bash
chmod 600 .env
```

This is not a formality: `600` means no other user on the machine
can read it. On a shared server it is the only thing that separates your keys
from everyone else.

---

## 3. Installation {#3-installazione}

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

(`<il tuo repo>` means your repository; `metti le chiavi` means "put your keys here".)

From here on it is the same as what you did on your laptop.

---

## 4. The gateway as a service {#4-il-gateway-come-servizio}

So far you started the gateway by hand, and it stops when you close the
terminal. On a server it must restart on its own, even after a reboot.

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

Two lines are worth a closer look.

**`User=quaderno`**: the gateway does not run as root. If LiteLLM has a
hole tomorrow, whoever gets in ends up with the permissions of a user who can
read one folder and nothing else.

**`EnvironmentFile`**: the keys come from the file, not from the command
line. Variables written in `ExecStart` show up in `ps`, so anyone on the
machine can read them. The file with `chmod 600` cannot be read.

---

## 5. The gateway does not face the internet {#5-il-gateway-non-si-affaccia-su-internet}

**This is the point you must not get wrong.**

LiteLLM has its own key (`GATEWAY_KEY`), but it is not a service designed
to be exposed. If you open port 4000 to the world, you are handing your
free quotas to anyone who finds them. And they do find them: scanners
sweep the common ports all the time.

The gateway listens on `localhost` and nothing else: that is what `--host
127.0.0.1` does in the service above. **Without that option LiteLLM listens
on `0.0.0.0`**, and then the only thing protecting you is the
firewall. Check:

```bash
ss -lptn 'sport = :4000'
```

It must say `127.0.0.1:4000`. If it says `0.0.0.0:4000` or `*:4000`, fix it
before you do anything else. To reach it from outside:

```bash
ssh -L 4000:localhost:4000 quaderno@tuo-server
```

From then on, on your laptop, `http://localhost:4000` **is** the
server's gateway. No open ports, and the traffic travels inside SSH.

If you want a web interface you can reach from your phone, the rule
still holds: you expose **the interface**, behind a reverse proxy with HTTPS and
a password. Never the gateway.

---

## 6. Backups, which become mandatory here {#6-il-backup-che-qui-diventa-obbligatorio}

On your laptop a backup is prudence. On a server it is the only thing that
separates you from losing everything: cheap VPSs break, and whoever
rents you one owes you nothing.

Module 7 gave you the three pieces. Here you put them in a file and
run them automatically.

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

(The comment means "keep the last 14 days".)

```bash
chmod +x ~/quaderno/backup.sh
crontab -e
```

```cron
30 3 * * * /home/quaderno/quaderno/backup.sh >> /home/quaderno/backup.log 2>&1
```

**Then, once, try restoring it into another folder.** A
backup you never restored is not a backup, it is a file. That is the line from
module 7, and it matters even more here, where you expect failures.

---

## 7. If the machine is yours and you want to take the internet out of the loop {#7-se-la-macchina-e-tua-e-vuoi-togliere-internet-dal-giro}

With 8 GB of RAM you can put Ollama on the server and send nothing
outside:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen3:4b-instruct
```

In `.env` you change the two lines you know from module 2. The gateway stays
where it is: only the provider behind it changes.

Answers get a bit worse and response times get longer. In exchange, your
customers' notes never leave the room. Reread the
[project brief](progetto-finale/BRIEF.md) on why that can matter
more than quality.
