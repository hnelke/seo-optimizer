#!/bin/bash
# --- SEO-OPTIMIZER Automatisches Deployment-Skript ---

echo "=== Starte Deployment von SEO-Optimizer auf Port 8001 ==="

# 1. Neuesten Code aus GitHub abrufen
echo "Rufe neuesten Code ab..."
git pull origin main

# 2. Prüfen, ob eine .env Datei existiert. Falls nicht, Vorlage kopieren
if [ ! -f .env ] && [ -f .env.example ]; then
    echo "Erstelle .env aus Vorlage .env.example..."
    cp .env.example .env
elif [ -f .env ]; then
    grep -q "^ADMIN_USERNAME=" .env || printf "\n# Admin Login Zugangsdaten\nADMIN_USERNAME=hnelke@gmail.com\nADMIN_PASSWORD=\n" >> .env
    grep -q "^GEMINI_MODEL=" .env || printf "GEMINI_MODEL=gemini-2.5-flash\n" >> .env
fi

# 3. Python Virtual Environment einrichten
echo "Richte Python Virtual Environment ein..."
if [ -d ".venv" ]; then
    VENV_DIR=".venv"
else
    VENV_DIR="venv"
fi

if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "Installiere/Aktualisiere Python-Abhängigkeiten..."
pip install --upgrade pip
pip install -r requirements.txt

# 4. Prüfen, ob der systemd-Dienst aktiv/installiert ist
if command -v systemctl &> /dev/null && systemctl list-unit-files 2>/dev/null | grep -q "seo-optimizer.service"; then
    echo "Starte systemd-Dienst 'seo-optimizer' neu..."
    sudo systemctl restart seo-optimizer
    sleep 2
    sudo systemctl status seo-optimizer --no-pager
else
    echo "Kein systemd-Dienst aktiv. Verwende Standard-Start..."
    echo "Stoppe alte Instanz auf Port 8001..."
    pkill -f 'uvicorn main:app.*8001' || true
    fuser -k 8001/tcp || true
    sleep 1

    echo "Starte Uvicorn-Server auf Port 8001..."
    export PYTHONUNBUFFERED=1
    nohup "$VENV_DIR/bin/python" -u -m uvicorn main:app --host 127.0.0.1 --port 8001 > app.log 2>&1 &
fi

echo "=== Deployment erfolgreich abgeschlossen! ==="
echo "Die App läuft nun auf Port 8001."
