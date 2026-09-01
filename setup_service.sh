#!/bin/bash
# --- SEO-OPTIMIZER Systemd Service Setup Script ---

set -e

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CURRENT_USER="$(whoami)"

echo "=== Richte systemd Service für SEO-Optimizer ein ==="
echo "Arbeitsverzeichnis: $APP_DIR"
echo "Benutzer: $CURRENT_USER"

SERVICE_FILE="/etc/systemd/system/seo-optimizer.service"

# Virtual Environment ermitteln
VENV_DIR="$APP_DIR/venv"
if [ ! -d "$VENV_DIR" ] && [ -d "$APP_DIR/.venv" ]; then
    VENV_DIR="$APP_DIR/.venv"
fi

sudo bash -c "cat > $SERVICE_FILE <<EOF
[Unit]
Description=SEO & KI-Readiness Analyzer FastAPI Application
After=network.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$APP_DIR
Environment=PYTHONUNBUFFERED=1
ExecStart=$VENV_DIR/bin/python -u -m uvicorn main:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=5
StandardOutput=append:$APP_DIR/app.log
StandardError=append:$APP_DIR/app.log

[Install]
WantedBy=multi-user.target
EOF"

echo "Aktualisiere systemd..."
sudo systemctl daemon-reload
echo "Aktiviere Autostart für seo-optimizer..."
sudo systemctl enable seo-optimizer
echo "Starte Dienst neu..."
sudo systemctl restart seo-optimizer

echo "=== Status des Dienstes ==="
sudo systemctl status seo-optimizer --no-pager

echo "=== Einrichtung erfolgreich abgeschlossen! ==="
