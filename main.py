import os
import json
import hmac
import time
import secrets
import hashlib
import datetime
import urllib.parse
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Paths configuration
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
reports_file = os.path.join(current_dir, "reports.json")
dotenv_file = os.path.join(current_dir, ".env")

# Load environment variables from .env file if it exists
def load_dotenv(dotenv_path=dotenv_file):
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            key, val = parts
                            # Strip quotes
                            val_clean = val.strip().strip("'").strip('"')
                            os.environ[key.strip()] = val_clean
        except Exception as e:
            print(f"[WARNING] Fehler beim Laden der .env Datei: {e}")

def update_dotenv_values(updates: dict, dotenv_path=dotenv_file):
    """Updates or adds key-value pairs in the .env file while preserving comments and other keys."""
    lines = []
    if os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"[WARNING] Fehler beim Lesen der .env Datei: {e}")

    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.split("=", 1)[0].strip()
            if key in updates:
                new_lines.append(f"{key}={updates[key]}\n")
                updated_keys.add(key)
                os.environ[key] = str(updates[key])
                continue
        new_lines.append(line if line.endswith("\n") else line + "\n")

    for key, val in updates.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={val}\n")
            os.environ[key] = str(val)

    with open(dotenv_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

DEFAULT_GEMINI_MODELS = [
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash (Standard – Empfohlen)",
        "description": "Optimales Verhältnis aus Geschwindigkeit, Kosten und semantischer Textanalyse."
    },
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro (Deep Reasoning & Analyse)",
        "description": "Maximale sprachliche und analytische Tiefe für komplexe Webseitentexte."
    },
    {
        "id": "gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash-Lite (Ultra-Schnell)",
        "description": "Besonders schnelle und ressourcenschonende KI-Auswertung."
    },
    {
        "id": "gemini-3-flash-preview",
        "name": "Gemini 3 Flash Preview (Next-Gen Flash)",
        "description": "Vorschau auf die neueste Gemini 3 Flash Generation."
    },
    {
        "id": "gemini-3.1-pro-preview",
        "name": "Gemini 3.1 Pro Preview (Next-Gen Flaggschiff)",
        "description": "Neueste Gemini 3.1 Pro Generation für höchste Ansprüche."
    },
    {
        "id": "gemini-2.0-flash",
        "name": "Gemini 2.0 Flash",
        "description": "Bewährtes und schnelles multimodales Modell."
    }
]

def ensure_dotenv_exists(dotenv_path=dotenv_file):
    """Creates .env with default keys if it does not exist yet, or appends missing admin/model keys."""
    if not os.path.exists(dotenv_path):
        try:
            default_content = (
                "# Google Gemini API Einstellungen (über Admin-Panel verwaltbar)\n"
                "GEMINI_API_KEY=\n"
                "GEMINI_MODEL=gemini-2.5-flash\n\n"
                "# Admin Login Zugangsdaten\n"
                "ADMIN_USERNAME=hnelke@gmail.com\n"
                "ADMIN_PASSWORD=\n"
            )
            with open(dotenv_path, "w", encoding="utf-8") as f:
                f.write(default_content)
        except Exception as e:
            print(f"[WARNING] Konnte .env nicht automatisch anlegen: {e}")
    else:
        try:
            with open(dotenv_path, "r", encoding="utf-8") as f:
                content = f.read()
            additions = []
            if "GEMINI_MODEL=" not in content:
                additions.append("GEMINI_MODEL=gemini-2.5-flash")
            if "ADMIN_USERNAME=" not in content:
                additions.append("\n# Admin Login Zugangsdaten\nADMIN_USERNAME=hnelke@gmail.com")
            if "ADMIN_PASSWORD=" not in content:
                additions.append("ADMIN_PASSWORD=")
            if additions:
                with open(dotenv_path, "a", encoding="utf-8") as f:
                    if not content.endswith("\n"):
                        f.write("\n")
                    f.write("\n".join(additions) + "\n")
        except Exception as e:
            print(f"[WARNING] Fehler beim Ergänzen der .env Datei: {e}")

ensure_dotenv_exists()
load_dotenv()

from analyzer import fetch_and_analyze

app = FastAPI(
    title="SEO & KI-Readiness Analyzer",
    description="Ein Tool zur Auditierung von Webseiten auf traditionelles SEO und Google AI Overviews Bereitschaft mit Historie.",
    version="2.0.0"
)

# Admin Authentication Helpers
revoked_tokens = set()
TOKEN_TTL_SECONDS = 86400  # 24 Stunden

def get_admin_credentials():
    load_dotenv()
    admin_user = os.environ.get("ADMIN_USERNAME", "hnelke@gmail.com").strip()
    admin_pass = os.environ.get("ADMIN_PASSWORD", "").strip()
    return admin_user, admin_pass

def create_admin_token(username: str, password: str) -> str:
    expires = int(time.time()) + TOKEN_TTL_SECONDS
    nonce = secrets.token_hex(16)
    payload = f"{username.lower()}:{expires}:{nonce}"
    secret_key = f"seo-optimizer-admin:{password}".encode("utf-8")
    sig = hmac.new(secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{expires}.{nonce}.{sig}"

def verify_admin_token(token: str) -> str:
    if not token or token in revoked_tokens:
        raise HTTPException(status_code=401, detail="Nicht autorisiert. Bitte als Admin anmelden.")
    admin_user, admin_pass = get_admin_credentials()
    if not admin_pass:
        raise HTTPException(status_code=401, detail="Admin-Zugang ist auf dem Server noch nicht konfiguriert.")
    parts = token.split(".")
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Ungültiges Sitzungs-Token.")
    expires_str, nonce, sig = parts
    try:
        expires = int(expires_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Ungültiges Sitzungs-Token.")
    if time.time() > expires:
        raise HTTPException(status_code=401, detail="Sitzung abgelaufen. Bitte erneut anmelden.")
    payload = f"{admin_user.lower()}:{expires}:{nonce}"
    secret_key = f"seo-optimizer-admin:{admin_pass}".encode("utf-8")
    expected_sig = hmac.new(secret_key, payload.encode("utf-8"), hashlib.sha256).hexdigest()
    if not secrets.compare_digest(sig, expected_sig):
        raise HTTPException(status_code=401, detail="Ungültiges oder abgelaufenes Sitzungs-Token.")
    return admin_user

async def require_admin(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Nicht autorisiert. Nur Administratoren dürfen diese Aktion ausführen.")
    token = authorization[7:].strip()
    return verify_admin_token(token)


def normalize_reports_db():
    if not os.path.exists(reports_file):
        return
    try:
        modified = False
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
        
        if "domains" in db:
            new_domains = {}
            for domain, reports in db["domains"].items():
                lower_domain = domain.lower()
                if lower_domain != domain:
                    modified = True
                
                normalized_reports = []
                for r in reports:
                    if "url" in r:
                        lower_url = r["url"].lower()
                        if r["url"] != lower_url:
                            r["url"] = lower_url
                            modified = True
                    normalized_reports.append(r)
                
                if lower_domain in new_domains:
                    new_domains[lower_domain].extend(normalized_reports)
                    modified = True
                else:
                    new_domains[lower_domain] = normalized_reports
            
            # Sort reports in each domain by timestamp to keep them chronological
            for domain in new_domains:
                new_domains[domain].sort(key=lambda x: x.get("timestamp", ""))
                
            db["domains"] = new_domains
            
        if modified:
            with open(reports_file, "w", encoding="utf-8") as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            print("[INFO] reports.json erfolgreich auf Kleinbuchstaben normalisiert.")
    except Exception as e:
        print(f"[WARNING] Fehler bei der Normalisierung von reports.json: {e}")

normalize_reports_db()

if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Mount the static directory
app.mount("/static", StaticFiles(directory=static_dir), name="static")

class AnalyzeRequest(BaseModel):
    url: str
    gemini_api_key: Optional[str] = None

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class BulkDeleteItem(BaseModel):
    domain: str
    timestamp: str

class BulkDeleteRequest(BaseModel):
    items: List[BulkDeleteItem]

class AdminSettingsRequest(BaseModel):
    gemini_api_key: Optional[str] = ""
    gemini_model: Optional[str] = "gemini-2.5-flash"

class AdminModelsRequest(BaseModel):
    gemini_api_key: Optional[str] = None


def save_report(report: dict) -> dict:
    """Helper to save report inside reports.json grouped by domain."""
    url = report["url"].lower()
    report["url"] = url
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc.lower() if parsed_url.netloc else "unknown-domain"
    
    # Add timestamp
    timestamp = datetime.datetime.now().isoformat()
    report["timestamp"] = timestamp
    
    # Load database
    db = {"domains": {}}
    if os.path.exists(reports_file):
        try:
            with open(reports_file, "r", encoding="utf-8") as f:
                db = json.load(f)
        except Exception:
            pass # fallback to empty if corrupted
            
    if "domains" not in db:
        db["domains"] = {}
        
    if domain not in db["domains"]:
        db["domains"][domain] = []
        
    # Append new report to this domain's history
    db["domains"][domain].append(report)
    
    # Save back
    with open(reports_file, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
        
    return report

@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(
        content="<h1>SEO & KI-Readiness Analyzer</h1><p>index.html fehlt im static-Ordner.</p>",
        status_code=200
    )

@app.get("/glossar", response_class=HTMLResponse)
async def read_glossary():
    glossary_path = os.path.join(static_dir, "glossary.html")
    if os.path.exists(glossary_path):
        return FileResponse(glossary_path)
    return HTMLResponse(
        content="<h1>SEO & KI-Readiness Analyzer - Glossar</h1><p>glossary.html fehlt im static-Ordner.</p>",
        status_code=404
    )

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(static_dir, "favicon.ico"))


@app.post("/api/analyze")
async def api_analyze(request: AnalyzeRequest):
    url = request.url.strip().lower()
    if not url:
        raise HTTPException(status_code=400, detail="Die URL darf nicht leer sein.")
    
    if not url.startswith(("http://", "https://")) and "." not in url:
        raise HTTPException(status_code=400, detail="Bitte gib eine gültige Domain oder URL ein (z. B. wikipedia.org).")
        
    try:
        load_dotenv()
        # Pass the api key to fetch_and_analyze if provided in request
        report = await fetch_and_analyze(url, gemini_api_key=request.gemini_api_key)
        # Save report to reports.json
        saved = save_report(report)
        return saved
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/history")
async def api_history():
    """Returns a list of all analyzed domains and their runs (without full details to keep payload small)."""
    if not os.path.exists(reports_file):
        return {"domains": {}}
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        slim_history = {}
        for domain, reports in db.get("domains", {}).items():
            slim_history[domain] = []
            for r in reports:
                slim_history[domain].append({
                    "timestamp": r.get("timestamp"),
                    "url": r.get("url"),
                    "overall_score": r.get("overall_score"),
                    "scores": r.get("scores")
                })
        return {"domains": slim_history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Historie: {str(e)}")

@app.get("/api/report")
async def api_report(domain: str, timestamp: str):
    """Fetches a specific full report from the database."""
    domain = domain.lower()
    if not os.path.exists(reports_file):
        raise HTTPException(status_code=404, detail="Keine Berichte vorhanden.")
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        reports = db.get("domains", {}).get(domain, [])
        for r in reports:
            if r.get("timestamp") == timestamp:
                return r
                
        raise HTTPException(status_code=404, detail="Bericht zu diesem Zeitstempel nicht gefunden.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/login")
async def api_admin_login(request: AdminLoginRequest):
    """Authenticates the admin user against credentials in .env."""
    admin_user, admin_pass = get_admin_credentials()
    if not admin_pass or admin_pass == "your_admin_password_here":
        raise HTTPException(
            status_code=500,
            detail="Admin-Passwort (ADMIN_PASSWORD) ist in der .env Datei auf dem Server noch nicht hinterlegt."
        )
    
    input_user = request.username.strip().lower()
    expected_user = admin_user.strip().lower()
    input_pass = request.password
    
    user_ok = (
        secrets.compare_digest(input_user.encode("utf-8"), expected_user.encode("utf-8"))
        or input_user == "admin"
    )
    pass_ok = (
        secrets.compare_digest(input_pass.encode("utf-8"), admin_pass.encode("utf-8"))
        or secrets.compare_digest(input_pass.strip().encode("utf-8"), admin_pass.encode("utf-8"))
    )
    
    if not (user_ok and pass_ok):
        print(f"[AUTH] Admin-Login fehlgeschlagen: user='{input_user}' (user_ok={user_ok}, pass_ok={pass_ok}, input_pass_len={len(input_pass)}, expected_pass_len={len(admin_pass)})")
        raise HTTPException(status_code=401, detail="Ungültiger Benutzername oder Passwort.")
        
    token = create_admin_token(admin_user, admin_pass)
    return {
        "status": "success",
        "token": token,
        "username": admin_user
    }

@app.get("/api/admin/verify")
async def api_admin_verify(admin_user: str = Depends(require_admin)):
    """Verifies whether the current admin session token is valid."""
    return {"authenticated": True, "username": admin_user}

@app.post("/api/admin/logout")
async def api_admin_logout(authorization: Optional[str] = Header(None)):
    """Revokes the current admin session token."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:].strip()
        if token:
            revoked_tokens.add(token)
    return {"status": "success", "message": "Erfolgreich abgemeldet."}

@app.get("/api/admin/settings")
async def api_get_admin_settings(_admin: str = Depends(require_admin)):
    """Returns the current Google Gemini API Key and LLM model configured on the server."""
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if api_key == "your_gemini_api_key_here":
        api_key = ""
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
    if model.startswith("models/"):
        model = model[len("models/"):]
    return {
        "gemini_api_key": api_key,
        "has_api_key": bool(api_key),
        "gemini_model": model,
        "available_models": DEFAULT_GEMINI_MODELS
    }

@app.put("/api/admin/settings")
async def api_save_admin_settings(request: AdminSettingsRequest, _admin: str = Depends(require_admin)):
    """Saves the Google Gemini API Key and selected LLM model to .env on the server."""
    api_key = (request.gemini_api_key or "").strip()
    model = (request.gemini_model or "gemini-2.5-flash").strip()
    if model.startswith("models/"):
        model = model[len("models/"):]
    if not model:
        model = "gemini-2.5-flash"

    try:
        update_dotenv_values({
            "GEMINI_API_KEY": api_key,
            "GEMINI_MODEL": model
        })
        return {
            "status": "success",
            "message": "Google API-Key und LLM-Modell erfolgreich in der .env gespeichert.",
            "has_api_key": bool(api_key),
            "gemini_model": model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern in .env: {str(e)}")

@app.post("/api/admin/models")
async def api_fetch_gemini_models(request: AdminModelsRequest, _admin: str = Depends(require_admin)):
    """Fetches live available Gemini models from the Google Generative Language API."""
    import httpx
    load_dotenv()
    api_key = (request.gemini_api_key if request.gemini_api_key is not None else os.environ.get("GEMINI_API_KEY", "")).strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(status_code=400, detail="Bitte gib zuerst einen gültigen Google Gemini API-Key ein, um Modelle live abzurufen.")

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                err_msg = "Ungültiger API-Key oder Google API Fehler."
                try:
                    err_json = resp.json()
                    err_msg = err_json.get("error", {}).get("message", err_msg)
                except Exception:
                    pass
                raise HTTPException(status_code=400, detail=f"Google API Fehler: {err_msg}")
            data = resp.json()

        live_models = []
        seen_ids = set()
        excluded_keywords = ("embedding", "imagen", "veo", "aqa", "tts", "audio", "robotics", "computer-use", "learnlm")

        for m in data.get("models", []):
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" not in methods:
                continue
            raw_name = m.get("name", "")
            model_id = raw_name[len("models/"):] if raw_name.startswith("models/") else raw_name
            if not model_id.startswith("gemini-"):
                continue
            if any(kw in model_id.lower() for kw in excluded_keywords):
                continue
            seen_ids.add(model_id)
            display_name = m.get("displayName") or model_id
            desc = m.get("description") or "Google Gemini Sprachmodell"
            live_models.append({
                "id": model_id,
                "name": f"{display_name} ({model_id})" if model_id not in display_name.lower() else display_name,
                "description": desc[:140]
            })

        # Sort so newest/recommended (2.5, 3, 2.0) appear at the top
        def model_sort_key(item):
            mid = item["id"]
            if mid == "gemini-2.5-flash":
                return (0, mid)
            if mid.startswith("gemini-2.5"):
                return (1, mid)
            if mid.startswith("gemini-3"):
                return (2, mid)
            if mid.startswith("gemini-2.0"):
                return (3, mid)
            return (4, mid)

        live_models.sort(key=model_sort_key)

        if not live_models:
            live_models = DEFAULT_GEMINI_MODELS

        return {
            "status": "success",
            "models": live_models,
            "count": len(live_models)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Modelle: {str(e)}")

@app.delete("/api/report")
async def api_delete_report(domain: str, timestamp: str, _admin: str = Depends(require_admin)):
    """Deletes a specific report run from the database (Admin only)."""
    domain = domain.lower()
    if not os.path.exists(reports_file):
        raise HTTPException(status_code=404, detail="Keine Berichte vorhanden.")
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        reports = db.get("domains", {}).get(domain, [])
        new_reports = [r for r in reports if r.get("timestamp") != timestamp]
        
        if len(new_reports) == len(reports):
            raise HTTPException(status_code=404, detail="Bericht zum angegebenen Zeitstempel nicht gefunden.")
            
        if not new_reports:
            # Delete domain key entirely if no runs left
            del db["domains"][domain]
        else:
            db["domains"][domain] = new_reports
            
        with open(reports_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "message": "Bericht gelöscht."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/domain")
async def api_delete_domain(domain: str, _admin: str = Depends(require_admin)):
    """Deletes an entire domain and all its reports from the database (Admin only)."""
    domain = domain.lower()
    if not os.path.exists(reports_file):
        raise HTTPException(status_code=404, detail="Keine Berichte vorhanden.")
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        if domain not in db.get("domains", {}):
            raise HTTPException(status_code=404, detail="Domain nicht gefunden.")
            
        del db["domains"][domain]
        
        with open(reports_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "message": f"Domain {domain} komplett gelöscht."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/delete-bulk")
async def api_delete_bulk(request: BulkDeleteRequest, _admin: str = Depends(require_admin)):
    """Deletes multiple selected report runs at once (Admin only)."""
    if not os.path.exists(reports_file):
        raise HTTPException(status_code=404, detail="Keine Berichte vorhanden.")
        
    try:
        with open(reports_file, "r", encoding="utf-8") as f:
            db = json.load(f)
            
        domains_db = db.get("domains", {})
        targets_by_domain = {}
        for item in request.items:
            d = item.domain.lower()
            targets_by_domain.setdefault(d, set()).add(item.timestamp)
            
        deleted_count = 0
        for d, ts_set in targets_by_domain.items():
            if d in domains_db:
                before_len = len(domains_db[d])
                new_list = [r for r in domains_db[d] if r.get("timestamp") not in ts_set]
                deleted_count += (before_len - len(new_list))
                if not new_list:
                    del domains_db[d]
                else:
                    domains_db[d] = new_list
                    
        with open(reports_file, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2, ensure_ascii=False)
            
        return {"status": "success", "deleted_count": deleted_count, "message": f"{deleted_count} Analyse(n) gelöscht."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time

    def open_browser():
        time.sleep(1.5)
        webbrowser.open("http://localhost:8000")

    print("Starte SEO & KI-Readiness Analyzer auf http://localhost:8000 ...")
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
